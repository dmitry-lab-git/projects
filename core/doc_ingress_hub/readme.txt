# Doc Ingress Hub — Universal Document Ingestion, BLOB Archiver & AI Router

**Module Location:** `core/doc_ingress_hub`  
**Database Schema:** `processing` (`source_files`, `source_file_blobs`)  
**Core Integrations:** `core.api_manager` (Gemini API), `core.db_utils` (PostgreSQL), `core.receipts_processor` (Downstream Worker)

## 1. Purpose & Architectural Role

`doc_ingress_hub` is the centralized ingestion and triage gateway for all incoming documents placed into the Windows host directory (`C:\Personal\Projects\Ingress`). 

Rather than hardcoding file-discovery and archival logic inside domain-specific parsers (such as `receipts_processor`), `doc_ingress_hub` decouples **file intake** from **domain extraction**:
1. **Stage 1 — Ingestion, Deduplication & BLOB Archiving:** Every incoming file is hashed (SHA-256), compressed into an OCR-readable JPEG/WebP binary, and persisted into PostgreSQL (`processing.source_file_blobs`) linked via UUID. This eliminates Git repository bloat and guarantees zero data loss.
2. **Stage 2 — AI Triage & Classification:** Utilizing available Gemini API quota via `secure_api_call`, the hub runs a lightweight classification prompt to identify the document type (e.g., `RECEIPT`, `INVOICE`, `CONTRACT`, `SCREENSHOT`, or `UNKNOWN`), generates a normalized title, and tags the record for the appropriate downstream processor.

## 2. Directory & Routing Logic

The hub monitors `/mnt/c/Personal/Projects/Ingress` (mapped from Windows `C:\Personal\Projects\Ingress`) to keep the ingress queue clean and auditable:

* **`Ingress/` (Root & Uncategorized Subfolders):** Any file dropped here is ingested, archived as a BLOB, and routed through AI Triage. Unidentifiable files are indexed under the title `UNKNOWN` with a corresponding review status.
* **`Ingress/receipts_income/`:** Pre-hinted as a receipt candidate, verified via AI Triage, and dispatched to the `receipts_processor` queue.
* **`Ingress/receipts_income/Important/`:** Marked with `is_important = TRUE` and `is_protected = TRUE` in the BLOB registry. Original files in this directory are **never moved or deleted** automatically and are exempt from 30-day retention cleanup.

*Note: Standard files are moved out of `Ingress` into a 30-day local retention buffer after successful database commit, ensuring `Ingress` remains empty when idle.*

## 3. Database Integration

The module manages two core tables in the `processing` schema:

* **`processing.source_files`:** Stores file metadata, SHA-256 hash (`UNIQUE` constraint preventing duplicate ingestion), `ingress_zone`, `is_important` flag, AI-classified `doc_type`, AI-assigned `doc_title`, and workflow `status_id`.
* **`processing.source_file_blobs`:** Dedicated 1-to-1 binary registry (`source_file_id` FK with `ON DELETE RESTRICT`) storing compressed `bytea` payloads, original vs. compressed byte sizes, compression ratios, and protection flags.

## 4. Ecosystem & Downstream Pipeline

```text
[Windows Ingress Folder: C:\Personal\Projects\Ingress]
                       │
                       ▼ (1. SHA-256 Check & Image Compression)
[PostgreSQL: source_files + source_file_blobs] ──► (Retain if Important / Move to 30d Buffer)
                       │
                       ▼ (2. Stage 1 AI Call via api_manager.secure_api_call)
     [doc_ingress_hub: AI Triage & Classification]
                       │
                       ├──► doc_type == RECEIPT  ──► [core/receipts_processor] ──► processing.receipts
                       ├──► doc_type == INVOICE  ──► [Future Downstream Workers]
                       └──► doc_type == UNKNOWN  ──► Indexed as `UNKNOWN` + BLOB Preserved
```

## 5. Module Structure

```text
core/doc_ingress_hub/
├── __init__.py
├── config.py           # Ingress/Archive paths, compression settings (max width, JPEG quality)
├── compressor.py       # Pillow-based image resizing & optimization for BLOB storage
├── classifier.py       # Lightweight Gemini API triage execution & JSON parser
├── ingestor.py         # Directory scanner, SHA-256 deduplicator, DB writer & file mover
├── pipeline.py         # Main entry point orchestrating ingestion + AI triage
├── prompts/
│   └── triage.txt      # System prompt for initial document classification & titling
└── README.md           # Module documentation
```

## 6. Operational Guarantees

* **Zero Data Loss Policy:** Binary payloads are committed to `processing.source_file_blobs` *before* any file is relocated out of `Ingress`.
* **Quota Optimization:** Uses fast, low-token classification prompts (`gemini-3.1-flash-lite`) to filter out non-receipt documents before expensive domain extraction prompts run.
* **Idempotency & Extensibility:** Re-running the hub is safe due to SHA-256 deduplication, and adding new document types only requires plugging in a new downstream worker without touching ingestion logic.
