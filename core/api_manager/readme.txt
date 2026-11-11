# API Manager — Resilient LLM Gateway, Quota Gatekeeper & Audit Proxy

**Module Location:** `core/api_manager`  
**Primary Entry Point:** `api_manager.service.secure_api_call`  
**Database Schema:** `processing` (`api_requests_log`, `api_request_blobs_cache`, `api_blocked_models`, `source_extractions`)  
**Core Dependencies:** `google-genai`, `google-api-core`, `psycopg2`, `rich`, `python-dotenv`, `core.db_utils`

---

## 1. Purpose & Architectural Role

`api_manager` is a centralized, database-synchronized **AI Gateway and Rate-Limit Proxy** engineered to govern all LLM interactions across the ecosystem (`doc_ingress_hub`, `receipts_processor`, interactive interfaces, and analytical background workers).

Rather than allowing decoupled scripts to invoke the Gemini API independently—which leads to `429 Too Many Requests` bans, uncoordinated token consumption, and silent data loss—`api_manager` enforces:
* **Sliding-Window Rate Limiting (`RPM` / `TPM` / `RPD`)** synchronized against PostgreSQL `clock_timestamp()` and Pacific Time (`America/Los_Angeles`) daily quota resets.
* **Multi-Layer Defense (`api_defend.py`)** combining in-memory storm detection, historical anomaly analysis, database load protection, and automated circuit breaking.
* **Media Path Security (`media_manager.py`)** restricting binary file reads strictly to a whitelisted set of directories (`ALLOWED_DIRS`) and enforcing a 20 MB payload cap.
* **Full Lifecycle Auditing (`db_utils.py`)** persisting prompt weights, token consumption, latency (`duration_ms`), binary caches, and normalized error states in PostgreSQL.

---

## 2. Three-Stage Execution Pipeline (`service.py`)

Every call routed through `secure_api_call(...)` executes a deterministic three-stage lifecycle (preceded by a once-per-session `CLEANUP_OLD_BLOBS` cache sweep and a live `reload_config()` refresh):

### Stage 1: System Validation & Media Guard (`_stage_validation`)
Executed via `validate_system_state(...)` in `api_utils/api_defend.py`:
1. **Pre-Flight Token Counting:** Queries `client.models.count_tokens` separately for text and attached media (`types.Part`) to calculate exact `input_tokens` and enforce `DEFAULT_MAX_PROMPT_WEIGHT`.
2. **Media Security Check:** Validates file existence, read permissions, size (`<= 20 MB`), MIME type (`.jpg`, `.png`, `.webp`, `.pdf`, `.csv`, `.txt`), and directory containment against `ALLOWED_DIRS`.
3. **Storm & Overload Sensors:** Checks both the in-memory `SystemHealthMonitor` (max 10 events / 60s) and database-wide request volume (`CHECK_LOAD`, `CHECK_REQUEST_COUNT`).
4. **Historical Health & Circuit Breaker:** Scans `processing.api_requests_log` over the past hour (`GET_HEALTH_STATS`) for quota breach signatures and checks `processing.api_blocked_models` for active bans.
5. **Zombie Request Cleanup:** Transitions stale `PENDING` requests to `TIMEOUT` (after 10 min) or `ABANDONED` (after 24 hours).
6. **Internal & External Quota Gatekeeping:** Computes real-time global and per-model usage via `GET_METRICS_REPORT` using `clock_timestamp()` and puts the worker to sleep for the exact remaining sliding-window duration (`global_rpm_wait_sec + 1s`) when limits are reached.
7. **Live Diagnostic Panel:** Renders a Rich terminal dashboard (`display_report`) showing pass/fail states and percentage utilization across all limits.

### Stage 2: Model Selection & Rotation (`_stage_rotation`)
* Supports pinned execution (`USE_STATIC_MODEL = True`, defaulting to `gemini-3.1-flash-lite`) or dynamic priority-based fallback (`check_actual_model` / `model_rotation`) across `ALLOWED_MODELS` (`gemini-3.5-flash`, `gemini-3.1-flash-lite`, `gemini-2.5-flash-lite`, `gemini-2.5-flash`, `gemma-4-31b`) when daily quotas (`RPD`) are exhausted or a model is circuit-broken.

### Stage 3: Audited Execution & Retry Engine (`_stage_execution`)
1. Registers the parent extraction target (`ENSURE_SOURCE_EXTRACTION`) and inserts a `PENDING` audit row into `processing.api_requests_log` (`LOG_START`), returning `request_id`.
2. Persists the binary attachment into `processing.api_request_blobs_cache` (`INSERT_BLOB`, retained for 3 days).
3. Executes `client.models.generate_content` inside `execute_with_retry(...)`:
   * On success: extracts `candidates_token_count`, computes `duration_ms`, commits `FINISHED` status via `LOG_FINISH` (halting via `SystemExit` if DB persistence fails to prevent silent data loss), and applies `PACING_DELAY` via a Rich progress timer.
   * On error: delegates to `ExceptionHandler.handle(...)` to determine retryability, sleep backoff, and database status mapping.

---

## 3. Domain Exception Hierarchy (`exceptions.py`)

Raw `google.api_core.exceptions` and Python network errors are normalized into typed `SecureAPIError` subclasses mapped to `dicts.dict_statuses` (`entity_type = 'api_requests'`):

| Exception Class | Upstream Error / Condition | Retryable | DB `status_key` |
| :--- | :--- | :---: | :--- |
| `ClientValidationError` | Invalid arguments or `ALLOWED_DIRS` security violation | No | `ABANDONED` |
| `RateLimitError` | `TooManyRequests` (429) or transient per-minute `ResourceExhausted` | Yes | `ERROR_RETRY` |
| `QuotaExhaustedError` | `ResourceExhausted` with daily (`RPD`) quota markers | No | `ERROR_QUOTA` |
| `ContentPolicyViolationError` | `InvalidArgument` (400) with safety/policy block markers | No | `ERROR_SAFETY` |
| `SecureAPIError` (Timeout) | `DeadlineExceeded` (504), `GatewayTimeout`, or Python `TimeoutError` | Yes | `TIMEOUT` |
| `ProviderError` | `InternalServerError` (500) or `ServiceUnavailable` (503) | Yes | `ERROR_GENERIC` |

---

## 4. Database Schema Integration (`processing`)

`api_manager` relies on four tables inside the `processing` schema:

* **`processing.source_extractions`:** Parent registry linking external `source_uuid` entities (e.g., `source_files.id`) to a `target_name` (`doc_triage`, `receipts`, `technical`).
* **`processing.api_requests_log`:** Full audit ledger storing `source_id`, `model_family`, `model_version`, `prompt_text`, `file_meta` (`jsonb`), `input_tokens`, `output_tokens`, `response_text`, `duration_ms`, `status_id`, and `error_message`.
* **`processing.api_request_blobs_cache`:** Temporary binary store (`request_id`, `file_data bytea`) automatically purged after 3 days (`CLEANUP_OLD_BLOBS`).
* **`processing.api_blocked_models`:** Circuit-breaker state table storing `model_name` and `blocked_until` timestamps.

---

## 5. Configuration & Hot Reloading

* **`settings.txt` (Hot-Reloaded on Every Call):** Controls `GLOBAL_RPM_LIMIT`, `GLOBAL_RPD_LIMIT`, `GLOBAL_TPM_LIMIT`, `PACING_DELAY`, `DEFAULT_MAX_PROMPT_WEIGHT`, and `DEFAULT_MAX_RETRIES`. Changes take effect immediately without restarting active pipelines.
* **`models_config.json`:** Defines `ALLOWED_MODELS` and per-model rate caps (`max_rpm`, `max_tpm`, `max_rpd`, `priority`).
* **Secrets (`.env`):** Loaded externally from `secure_folder/api_manager/.env` (`GEMINI_API_KEY`), isolated from Git tracking.
* **Media Whitelist (`api_utils/media_manager.py`):** Explicitly restricts file ingestion to `/home/fujitsu-u745/Projects/{data,uploads,Ledger}`, `core/photo_processor/ai_input`, `/mnt/c/Personal/Projects/Ingress`, and `/mnt/c/Personal/Projects/Archive_Buffer`.

---

## 6. Module Structure

```text
core/api_manager/
├── __init__.py
├── config.py                  # Secret loader, Rich traceback setup & hot-reload hooks
├── service.py                 # Entry point (secure_api_call) & 3-stage pipeline
├── exceptions.py              # Domain exceptions & Google SDK error mapper
├── models_config.json         # Model whitelist & RPM/TPM/RPD rate definitions
├── settings.txt               # Live-tunable global pacing & retry thresholds
├── api_utils/
│   ├── api_defend.py          # Multi-layer validation, quota gatekeeper & Rich report
│   ├── api_utils.py           # Retry engine, countdown UI, PT reset clock & rotation
│   └── media_manager.py       # Path security guard (ALLOWED_DIRS) & Part builder
├── db_utils/
│   ├── db_queries.py          # Parameterized SQL queries (clock_timestamp sliding windows)
│   └── db_utils.py            # Request logging, BLOB caching & health metric queries
├── registry/                  # Internal registries
└── README.md                  # Module documentation
```

---

## 7. Usage Example

```python
from google import genai
from api_manager.service import secure_api_call
from core.db_utils.db_access import get_db_connection

client = genai.Client(api_key="YOUR_GEMINI_API_KEY")
conn = get_db_connection()

response_text = secure_api_call(
    client=client,
    prompt_text="Analyze this document and return structured JSON.",
    conn=conn,
    source_uuid="16bb8b7f-ef83-4eef-b4d2-0ecda4ae6f8d",
    model_name="gemini-3.1-flash-lite",
    target_name="doc_triage",
    file_path="/mnt/c/Personal/Projects/Archive_Buffer/2026-11-11/sample.jpg"
)
```
