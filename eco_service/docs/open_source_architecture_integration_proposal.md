# AUROVILLE ECO-SERVICE ERP

## Open Source Architecture & Development Transfer Proposal

**Initiative Sponsor / Technical Developer:** Dmitry Lab  
**Target Recipient:** Auroville Eco-Service  
**Document Status:** Revised Proposal — Open Source, No-Obligation Framework  
**Document Purpose:** Free-of-charge transfer of the current development to Auroville Eco-Service for independent review, use, and further adaptation.  

---

## EXECUTIVE SUMMARY

This proposal accompanies the free-of-charge transfer of the current Dmitry Lab development related to a waste-management and resource-accounting ERP concept for Auroville Eco-Service. The contribution brings together an architectural design, an implemented database structure, selected software components, technical documentation, and a synthetic-data utility.

**Development Status & Nature of Contribution:**  
The contribution represents an Open Source architectural and engineering framework — a construction model for a potential future ERP system, rather than a complete or production-ready ERP installation. It provides a technical foundation that Eco-Service may independently review, develop, implement, or adapt according to its operational requirements.

The purpose is practical: to place the existing engineering work at the organisation's disposal so that its team can inspect the structure, evaluate its relevance, reuse suitable parts, or adapt the work independently. The proposal does not assume that Eco-Service will adopt the system or proceed with implementation.

* **Essential Project Principle:** Dmitry Lab develops the digital system architecture and provides the codebase. Auroville Eco-Service implements and operates it at its sole discretion, with consultative and expert support from Dmitry Lab if desired.
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
This digital architecture and operational approach have been tested through independent household management and waste accounting for a single residential unit, using a lightweight software interface connected directly to an SQL database and accessible consumer scales (e.g., DEXP BM-10 or DEXP KG-30W). Experience confirms that regular weighings and a robust core database schema provide a complete, realistic picture of waste dynamics with minimal operational overhead, easily integrating into daily routines as a background habit.

Without unified accounting across fractions:
* Material throughput and balance across sorted fractions cannot be verified in real time.
* Volume variations create scheduling bottlenecks at processing hubs.
* Physical accountability between collection, transport, and sorting relies on paper or verbal reporting, increasing administrative overhead.

### 1.2 Proposed ERP Value

The proposed ERP digitizes or structures material flows from intake to recovery:
* **Material Balance Accountability:** Verification of gross intake weights against sorted fraction yields across established Auroville categories (`ORGANIC`, `PLASTIC`, `GLASS_UNBROKEN`, `GLASS_BROKEN`, `PAPER`, `CARDBOARD`, `METAL`, `TETRAPACK`, `THERMOCOL`, `TEXTILE`, `BATTERIES`, `TYRES`, `SANITARY`, `NON_RECYCLABLE_KITCHEN`).
* **Operational Efficiency:** Simplified field data collection using accessible tools (web panels, PWAs, or messaging interfaces) with offline caching capability to ensure uninterrupted field operation.
* **Data-Driven Oversight & Visibility:** Structured reporting can improve operational transparency and community awareness by demonstrating measurable recycling outcomes and providing visibility into material recovery performance.

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

The following definitions illustrate the core relational structure. They are presented as a structural reference and do not constitute a complete standalone deployment script:

```sql
CREATE TABLE dicts.bag_event_types (event_type_id uuid NOT NULL, code character varying(50) NOT NULL, name character varying(100) NOT NULL, description text, created_at timestamp without time zone NOT NULL);
CREATE TABLE dicts.bag_statuses (status_id uuid NOT NULL, code character varying(30) NOT NULL, name character varying(100) NOT NULL, description text, created_at timestamp without time zone NOT NULL);
CREATE TABLE dicts.bag_types (type_id uuid NOT NULL, code character varying(30) NOT NULL, name character varying(100) NOT NULL, description text, created_at timestamp without time zone NOT NULL);
CREATE TABLE dicts.categories (category_id uuid NOT NULL, code character varying(30) NOT NULL, name character varying(100) NOT NULL, created_at timestamp without time zone NOT NULL);
CREATE TABLE dicts.households (household_id uuid NOT NULL, user_id uuid NOT NULL, yard_id uuid NOT NULL, family_size integer NOT NULL, created_at timestamp without time zone NOT NULL);
CREATE TABLE dicts.operators (operator_id uuid NOT NULL, username character varying(50) NOT NULL, full_name character varying(150) NOT NULL, role character varying(30) NOT NULL, access_level integer NOT NULL, is_active boolean NOT NULL, created_at timestamp without time zone NOT NULL, updated_at timestamp without time zone NOT NULL);
CREATE TABLE dicts.organizations (organization_id uuid NOT NULL, name character varying(150) NOT NULL, business_type character varying(50) NOT NULL, address text, is_active boolean NOT NULL, created_at timestamp without time zone NOT NULL);
CREATE TABLE dicts.spatial_ref_sys (srid integer NOT NULL, auth_name character varying(256), auth_srid integer, srtext character varying(2048), proj4text character varying(2048));
CREATE TABLE dicts.yards (yard_id uuid NOT NULL, name character varying(150) NOT NULL, address text, location geometry(Point, 4326), is_active boolean NOT NULL, created_at timestamp without time zone NOT NULL, updated_at timestamp without time zone NOT NULL);
```

### IMPORTANT STATUS LIMIT

**The current work is not a full production ERP installation. No live operational deployment or field validation at Auroville Eco-Service is claimed.**

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

Rather than relying on a single overwritten status, an event-based approach preserves a sequence of recorded state changes:
* **SUBMITTED:** A collection, load, or material record is entered into the system.
* **ARRIVED:** The relevant load or item is recorded as having reached a receiving point.
* **WEIGHED:** A weight measurement is associated with the relevant record and context.
* **SORTED:** A sorting action or resulting material fraction is recorded.

Historical events are intended to remain append-only. Corrections to previously recorded information should be represented through additional corrective events rather than silent overwriting of the original event history.

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

The Flow Simulator is intended to serve as a strategic modeling utility. Following a successful field pilot, actual operational data may be used to calibrate simulation parameters and develop indicative scenarios for potential scaling across 50 to 100 facilities. Such projections would require validation against actual operational conditions and should not be interpreted as guaranteed forecasts.

---

## 6. PROPOSED ERP FIELD PILOT & IMPLEMENTATION ROADMAP

Should Eco-Service choose to test this architecture live, implementation should be driven purely by available team resources rather than software complexity.

```
+───────────────────────────────────────────────────────────────────────────────────+
| PHASE 1: Existing Development & Technical Materials Transfer (Dmitry Lab)         |
| Provide existing software repository, DDL, Reflex components, simulator & docs.   |
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

### Implementation Status Clarification

The roadmap describes a possible implementation sequence, not an approved or scheduled project. No field pilot has been authorized or commenced by Auroville Eco-Service. Any operational pilot remains subject to the organisation's independent decision, resource availability, and internal approval procedures.

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
| **4** | **Individual Bag QR Tracking** | Moderate CAPEX + regular OPEX (durable weather-resistant labels for every bag) | Unique label generated per bag handover. |
| **5** | **Automated IoT Infrastructure** | High CAPEX + specialized OPEX (load-cell scales, RFID bins, resident smart cards) | Automatic weighing and logging upon RFID tap. |

### IMPORTANT — Preliminary Rough Order of Magnitude (ROM) Only

The financial figures and cost profiles above are intentionally provided as a preliminary, non-binding Rough Order of Magnitude (ROM) for initial optioneering only. Detailed cost research for each level prior to defining actual operational capabilities and constraints has no practical sense. These estimates serve solely to:
1. Illustrate the order of difference between automation levels.
2. Enable a strategic decision on which pilot configuration is feasible to evaluate.
3. Provide a baseline for the Flow Simulator to calculate accurate Auroville-wide deployment costs.

Final detailed economic modeling is only possible after the selection of the implementation strategy. This modeling can be performed both before and after the pilot, once the strategy is defined.

### Extreme Budget Flexibility

Existing office hardware and local network infrastructure may reduce initial hosting costs. However, access to the system beyond a trusted local environment should use appropriate authentication, encrypted connections, and other security measures suitable for the deployment context.

---

## 8. DATA GOVERNANCE, SOVEREIGNTY & SOFTWARE LICENSING

Operational data generated by Auroville Eco-Service remains under the sole ownership and governance of Auroville Eco-Service.

1. **Data Sovereignty:** Eco-Service controls all user roles, access credentials, export policies, backup routines, and historical corrections.
2. **Open Source Licensing:**  
   The software developed by Dmitry Lab is released under the **MIT License (Copyright © 2026 Dmitry Lab)**, provided in the root directory of the project repository ([LICENSE File](https://github.com/dmitry-lab-git/projects/blob/main/eco_service/LICENSE)).  
   The MIT License grants Auroville Eco-Service and other recipients broad permission to use, copy, modify, merge, publish, distribute, sublicense, and sell copies of the software, subject to the conditions stated in the licence.  
   The contribution is provided free of charge. No payment, royalty, procurement, or commercial engagement with Dmitry Lab is required for the use of the released materials.  
   The licence applies to the software and associated materials covered by it. Third-party components remain subject to their respective licences.
3. **Information Security:** Security and data protection measures should be considered from the initial deployment stage and developed in proportion to the sensitivity of the data, operational risks, and system complexity. Appropriate access control, authentication, backup procedures, and secure communications should form part of the implementation strategy.

---

## 9. TERMS OF THE CONTRIBUTION & UNRESOLVED DECISIONS

### Free-of-Charge Transfer of Development

Dmitry Lab transfers these materials without fee or commercial obligation. Auroville Eco-Service retains full discretion to:
* Inspect, test, or adapt the architecture.
* Integrate selected components or proceed independently with alternative software or paper workflows.
* Invite Dmitry Lab for expert consultation or decline further engagement.

**Nature of the Contribution:**  
The free-of-charge contribution covers the existing development materials released under the MIT License. It does not constitute a transfer of exclusive intellectual property ownership, a contractual commitment to complete a production ERP system, or an obligation to provide continuous maintenance, hosting, or operational services.  
Any additional development, implementation, or support beyond the existing contribution may be discussed separately, without creating any obligation for either party.

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