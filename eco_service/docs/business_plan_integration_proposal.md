# AUROVILLE ECO-SERVICE ERP
## Open Source Architecture & Development Transfer Proposal

**Initiative Sponsor / Technical Developer:** Dmitry Lab  
**Target Recipient:** Auroville Eco-Service  
**Document Status:** Revised Proposal — Open Source, No-Obligation Framework  
**Document Purpose:** Free-of-charge transfer of the current development to Auroville Eco-Service for independent review, use, and further adaptation.

---

## EXECUTIVE SUMMARY

This proposal accompanies the free-of-charge transfer of the current Dmitry Lab development related to a waste-management and resource-accounting ERP concept for Auroville Eco-Service. The contribution brings together an architectural design, an implemented database structure, selected software components, technical documentation, and a synthetic-data utility.

The purpose is practical: to place the existing engineering work at the organisation's disposal so that its team can inspect the structure, evaluate its relevance, reuse suitable parts, or adapt the work independently. The proposal does not assume that Eco-Service will adopt the system or proceed with implementation.

* **Essential Project Principle & Open Source Availability:** Dmitry Lab develops the digital system architecture and provides the codebase. Auroville Eco-Service implements and operates it at its sole discretion, with consultative and expert support from Dmitry Lab if desired.
* **No Payment / No Procurement Obligation:** The current development is offered without charge. Auroville Eco-Service remains free to use the materials to the extent permitted by applicable project and third-party licences, modify or extend them, select only useful components, or decide not to proceed.
* **No Implementation Obligation:** There is no requirement to purchase services, procure specified equipment, implement the system, accept a prescribed technical configuration, or maintain an ongoing relationship with Dmitry Lab.

---

## TABLE OF CONTENTS
1. [Project Background & Value Proposition](#1-project-background--value-proposition)
2. [Current Development: Scope, Status & DDL](#2-current-development-scope-status--ddl)
3. [Operational Process Model](#3-operational-process-model)
4. [Technical Architecture & Client Touchpoints](#4-technical-architecture--client-touchpoints)
5. [Software Test Data (Not Field Data)](#5-software-test-data-not-field-data)
6. [Proposed ERP Field Pilot & Implementation Roadmap](#6-proposed-erp-field-pilot--implementation-roadmap)
7. [Progressive Automation & Economic Cost Profile](#7-progressive-automation--economic-cost-profile)
8. [Data Governance, Sovereignty & Software Licensing](#8-data-governance-sovereignty--software-licensing)
9. [Terms of the Contribution & Unresolved Decisions](#9-terms-of-the-contribution--unresolved-decisions)
10. [Conclusion](#10-conclusion)

---

## 1. PROJECT BACKGROUND & VALUE PROPOSITION

### 1.1 Practical Operational Challenges & Background
Managing municipal waste streams in a decentralized community like Auroville requires structured accounting between initial receipt at community collection yards, transport logistics, and central sorting facility processing. The Eco-Service has been managing these flows since 1992, and any accounting system—whether on paper or digital—is inherently an evolving ERP system reflecting organizational maturity.

**Model Validation Background:**
This digital architecture and operational model have been rigorously verified through independent household management and waste accounting for a single residential unit, utilizing minimal software (a lightweight interface connected directly to a SQL database) alongside accessible consumer scales (e.g., DEXP BM-10 or DEXP KG-30W). Experience confirms that regular weighings and a robust core database schema provide a complete, realistic picture of waste dynamics with minimal operational overhead, easily integrating into daily routines as a background habit.

Without unified accounting across fractions:
* Material throughput and balance across sorted fractions cannot be verified in real time.
* Volume variations create scheduling bottlenecks at processing hubs.
* Physical accountability between collection, transport, and sorting relies on paper or verbal reporting, increasing administrative overhead.

### 1.2 Proposed ERP Value
The proposed ERP digitizes or structures material flows from intake to recovery:
* **Material Balance Accountability:** Verification of gross intake weights against sorted fraction yields across established Auroville categories (`ORGANIC`, `PLASTIC`, `GLASS_UNBROKEN`, `GLASS_BROKEN`, `PAPER`, `CARDBOARD`, `METAL`, `TETRAPACK`, `THERMOCOL`, `TEXTILE`, `BATTERIES`, `TYRES`, `SANITARY`, `NON_RECYCLABLE_KITCHEN`).
* **Operational Efficiency:** Simplified field data collection using accessible tools (web panels, PWAs, or messaging interfaces) with offline caching capability to ensure uninterrupted field operation.
* **Data-Driven Oversight & Community Engagement:** Real-time dashboards enable Eco-Service leadership to optimize collection routes and staffing. Real-time report generation boosts user retention (RR) and community awareness by demonstrating tangible recycling outcomes and showcasing exemplary household practices.

---

## 2. CURRENT DEVELOPMENT: SCOPE, STATUS & DDL

The present contribution is an engineering base with components at different maturity levels.

| Area | Current State |
| :--- | :--- |
| **Architecture and Data Model** | Designed structure for operational entities, relationships, and event-based records. |
| **Database Structure** | Implemented relational schema definitions (`dicts`) for core entities and operational records. |
| **Backend Components** | Selected Python components, including asynchronous database access (`asyncpg`) and data-validation models (`Pydantic`). |
| **Application Layer** | Selected Reflex-based components and web interface specifications for administrative management. |
| **Testing Utility** | `environment_initializer.py` for generating synthetic records in a controlled test environment. |
| **Deployment Materials** | Docker-related materials, README, and technical setup guidance. |

### Core Database Schema DDL Definitions
To ensure absolute technical clarity, the relational foundation rests upon structured dictionaries in the `dicts` schema:

```sql
CREATE TABLE dicts.bag_event_types (event_type_id uuid NOT NULL, code character varying(50) NOT NULL, name character varying(100) NOT NULL, description text, created_at timestamp without time zone NOT NULL);
CREATE TABLE dicts.bag_statuses (status_id uuid NOT NULL, code character varying(30) NOT NULL, name character varying(100) NOT NULL, description text, created_at timestamp without time zone NOT NULL);
CREATE TABLE dicts.bag_types (type_id uuid NOT NULL, code character varying(30) NOT NULL, name character varying(100) NOT NULL, description text, created_at timestamp without time zone NOT NULL);
CREATE TABLE dicts.categories (category_id uuid NOT NULL, code character varying(30) NOT NULL, name character varying(100) NOT NULL, created_at timestamp without time zone NOT NULL);
CREATE TABLE dicts.households (household_id uuid NOT NULL, user_id uuid NOT NULL, yard_id uuid NOT NULL, family_size integer NOT NULL, created_at timestamp without time zone NOT NULL);
CREATE TABLE dicts.operators (operator_id uuid NOT NULL, username character varying(50) NOT NULL, full_name character varying(150) NOT NULL, role character varying(30) NOT NULL, access_level integer NOT NULL, is_active boolean NOT NULL, created_at timestamp without time zone NOT NULL, updated_at timestamp without time zone NOT NULL);
CREATE TABLE dicts.organizations (organization_id uuid NOT NULL, name character varying(150) NOT NULL, business_type character varying(50) NOT NULL, address text, is_active boolean NOT NULL, created_at timestamp without time zone NOT NULL);
CREATE TABLE dicts.spatial_ref_sys (srid integer NOT NULL, auth_name character varying(256), auth_srid integer, srtext character varying(2048), proj4text character varying(2048));
CREATE TABLE dicts.yards (yard_id uuid NOT NULL, name character varying(150) NOT NULL, address text, location USER-DEFINED, is_active boolean NOT NULL, created_at timestamp without time zone NOT NULL, updated_at timestamp without time zone NOT NULL);
```

### IMPORTANT STATUS LIMIT
The current work is not a full production ERP installation. No live operational deployment or field validation at Auroville Eco-Service is claimed.

---

## 3. OPERATIONAL PROCESS MODEL

The system concept is organised around recording operational events and associating them with identifiable operational objects.

```
+────────────────────+     +──────────────────+     +──────────────────+     +──────────────────+     +────────────────────+     +───────────────────+
| COLLECTION/        | --> | ARRIVAL /        | --> | WEIGHING         | --> | SORTING          | --> | STORAGE/           | --> | FINAL             |
| SUBMISSION         |     | RECEIPT          |     |                  |     |                  |     | TRANSFER           |     | DESTINATION       |
+────────────────────+     +──────────────────+     +──────────────────+     +──────────────────+     +────────────────────+     +───────────────────+
```

### 3.1 Event History
Rather than relying on a single overwritten status, an event-based approach preserves an immutable sequence of recorded state changes:
* **SUBMITTED:** A collection, load, or material record is entered into the system.
* **ARRIVED:** The relevant load or item is recorded as having reached a receiving point.
* **WEIGHED:** A weight measurement is associated with the relevant record and context.
* **SORTED:** A sorting action or resulting material fraction is recorded.

### 3.2 Material Accounting & Data Integrity
A structured record supports reconciliation between incoming material, sorted fractions, residuals, transfers, and stock changes.

*Data Integrity is Not the Same as Operational Accuracy:* The software can enforce structure and validation rules, but it cannot independently guarantee that a recorded weight or classification is accurate. These depend on physical instruments, procedures, and operator practice. Operator errors, time constraints, or initial resistance are realistic factors that supply executive leadership with valuable feedback to refine workflows.

---

## 4. TECHNICAL ARCHITECTURE & CLIENT TOUCHPOINTS

| Layer | Technology / Approach | Role |
| :--- | :--- | :--- |
| **Database** | PostgreSQL; PostGIS where spatial data is required | Relational data foundation and optional spatial capability for yard geometries. |
| **Data Access** | Python; `asyncpg` | Asynchronous application-to-database access. |
| **Validation** | `Pydantic` | Structured validation of incoming application payloads. |
| **Application UI** | Reflex components | Administrative interface components for web browser access. |
| **Field / Mobile Direction** | Progressive Web Apps (PWA) | Browser-based mobile concept with offline data caching and Web Bluetooth printing support. |
| **Messaging Interface** | General Messenger Integration | Optional interaction channel for query/status submission. |
| **Deployment** | Docker-related materials | Reproducible environment setup scripts. |

---

## 5. SOFTWARE TEST DATA (NOT FIELD DATA)

The project includes `environment_initializer.py` and modular simulation configurations (e.g., `model_config.py`), which model household baseline waste profiles (~56.6 kg/month) and distinct commercial profiles (Restaurants, Offices, Factories, Guesthouses, Educational Facilities).

* **Illustrative Time Window:** 1 September 2026, 07:00 UTC – 31 October 2026, 21:00 UTC
* **Generated Records:** Approximately 580–760 synthetic entries
* **Synthetic Material Volume:** Approximately 4.8–6.4 metric tonnes

### SYNTHETIC DATA ONLY
These figures are artificially generated test data. They are not measurements, forecasts, or operational statistics from Auroville Eco-Service and must not be used as a baseline for procurement, staffing, or financial planning.

The Flow Simulator serves as a strategic modeling utility for leadership: once a pilot is executed across a small subset of locations (e.g., 10 sites), real operational data can be fed into the simulator to forecast system behavior and resource demands across 50 to 100 scaled facilities.

---

## 6. PROPOSED ERP FIELD PILOT & IMPLEMENTATION ROADMAP

Should Eco-Service choose to test this architecture live, implementation should be driven purely by available team resources rather than software complexity.

```
+───────────────────────────────────────────────────────────────────────────────────+
| PHASE 1: Digital System Development & Technical Validation (Dmitry Lab)           |
| Deliver software repository, database DDL, Reflex web app, and simulation tests.  |
+───────────────────────────────────────────────────────────────────────────────────+
                                          │
                                          ▼
+───────────────────────────────────────────────────────────────────────────────────+
| PHASE 2: Operational Preparation & 10-Site Pilot Setup (Eco-Service + Support)     |
| Populate dicts, verify permissions, configure 10 diverse pilot sites (2 months).  |
+───────────────────────────────────────────────────────────────────────────────────+
                                          │
                                          ▼
+───────────────────────────────────────────────────────────────────────────────────+
| PHASE 3: Strategic Pause & Pilot Evaluation (Eco-Service)                         |
| Pause for 1 month: analyze captured data, audit friction points, refine workflows.|
+───────────────────────────────────────────────────────────────────────────────────+
                                          │
                                          ▼
+───────────────────────────────────────────────────────────────────────────────────+
| PHASE 4: Strategic Scaling Decision (Eco-Service)                                 |
| Utilize simulator with real pilot metrics to project scaling across 50-100 sites. |
+───────────────────────────────────────────────────────────────────────────────────+
```

### Pilot Guidance
1. **Diverse Site Selection:** Pilot sites must span varied categories (residential, restaurant, office, factory, guesthouse) to accurately model future waste streams.
2. **Minimal Operational Friction:** Initial intake can focus purely on gross weights and load arrivals without mandatory individual bag tracking or complex tagging.
3. **User Onboarding:** Software interfaces should feature direct technical support feedback forms on every page to capture immediate field feedback.

---

## 7. PROGRESSIVE AUTOMATION & ECONOMIC COST PROFILE

Automation can be introduced incrementally based on budget and operational readiness.

| Level | Configuration | Relative Cost Profile | Operational Effort |
| :---: | :--- | :--- | :--- |
| **1** | **Manual Data Entry** | Minimal additional CAPEX (utilizes existing PC/phones; option for local server hosting) | Manual numeric entry at processing hubs or paper register logs. |
| **2** | **Stationary Placards** | Very low CAPEX (pre-printed placards/codes on collection bins) | Operators scan or enter fixed location codes. |
| **3** | **Container QR Identification** | Low to moderate CAPEX (reusable QR tags + optional Bluetooth thermal printers) | Mobile scanning of container tags at intake. |
| **4** | **Individual Bag QR Tracking** | Moderate CAPEX + regular OPEX (synthetic weather-resistant labels for every bag) | Unique label generated per bag handover. |
| **5** | **Automated IoT Infrastructure** | High CAPEX + specialized OPEX (load-cell scales, RFID bins, resident smart cards) | Automatic weighing and logging upon RFID tap. |

### IMPORTANT — Preliminary Rough Order of Magnitude (ROM) Only
The financial figures and cost profiles above are intentionally provided as a preliminary, non-binding Rough Order of Magnitude (ROM) for initial optioneering only. Detailed cost research for each level prior to defining actual operational capabilities and constraints has no practical sense. These estimates serve solely to:
1. Illustrate the order of difference between automation levels.
2. Enable a strategic decision on which pilot configuration is feasible to evaluate.
3. Provide a baseline for the Flow Simulator to calculate accurate Auroville-wide deployment costs.

Final detailed economic modeling is only possible after the selection of the implementation strategy. This modeling can be performed both before and after the pilot, once the strategy is defined.

### Extreme Budget Flexibility
In budget-constrained environments, hosting costs can be minimized: an existing office PC connected to the local network can replace dedicated cloud VPS servers, existing domain names can be reused, and local connections can be utilized prior to deploying commercial SSL certificates.

---

## 8. DATA GOVERNANCE, SOVEREIGNTY & SOFTWARE LICENSING

Operational data generated by Auroville Eco-Service remains under the sole ownership and governance of Auroville Eco-Service.

1. **Data Sovereignty:** Eco-Service controls all user roles, access credentials, export policies, backup routines, and historical corrections.
2. **Open Source Licensing:** All code developed by Dmitry Lab is provided under Open Source terms ([GitHub Repository](https://github.com/dmitry-lab-git/projects/tree/main/eco_service)). Eco-Service holds an irrevocable, non-exclusive right to use, modify, extend, or fork the codebase independently.
3. **Information Security:** System security measures should scale with data value. True peace of mind and data protection become essential when the operational processes run smoothly and autonomously.

---

## 9. TERMS OF THE CONTRIBUTION & UNRESOLVED DECISIONS

### Free-of-Charge Transfer of Development
Dmitry Lab transfers these materials without fee or commercial obligation. Auroville Eco-Service retains full discretion to:
* Inspect, test, or adapt the architecture.
* Integrate selected components or proceed independently with alternative software or paper workflows.
* Invite Dmitry Lab for expert consultation or decline further engagement.

### Decisions Reserved for Auroville Eco-Service
No pre-conditions are imposed. Prior to any operational launch, Eco-Service independently determines:
* [ ] Selection and approval of pilot locations (if desired).
* [ ] Target baseline automation level (Level 1 to 5).
* [ ] Hosting strategy (local office hardware vs. VPS hosting).
* [ ] Personnel allocation for field coordination and system administration.

---

## 10. CONCLUSION

This proposal represents a technical contribution—an Open Source engineering foundation—offered to Auroville Eco-Service to support its long-standing mission in waste management and resource recovery. 

**THE DECISION REMAINS WITH AUROVILLE ECO-SERVICE**  
The organization retains complete authority over whether to review, adopt, modify, or ignore these materials.

---
*End of Proposal Document.*