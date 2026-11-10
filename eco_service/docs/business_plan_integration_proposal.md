# AUROVILLE ECO-SERVICE ERP
## Business Plan & Integration Proposal

**Initiative Sponsor / Technical Developer:** Dmitry Lab  
**Target Recipient:** Auroville Eco-Service Administration & Governance  
**Document Status:** Revised Draft — Third Edition (Open Source & No-Obligation Framework)  
**Language:** English  

---

## EXECUTIVE SUMMARY

The **Auroville Eco-Service ERP** initiative is a proposed digital transformation project designed to establish structured material resource accounting, batch traceability, and operational data visibility for municipal waste management across Auroville.

### Essential Project Principle & Open Source Availability
> **"Dmitry Lab develops the digital system. Auroville Eco-Service implements and operates it, with consultative and expert support from Dmitry Lab."**

* **Nature of Contribution & Open Source Access:** Dmitry Lab provides the complete technical foundation as an in-kind gift and Open Source contribution. The entire project repository is publicly accessible under Open Source terms:
  - **Main Repository:** [https://github.com/dmitry-lab-git/projects/tree/main/eco_service](https://github.com/dmitry-lab-git/projects/tree/main/eco_service)
  - **Installation Guide (README):** [https://github.com/dmitry-lab-git/projects/blob/main/eco_service/readme.md](https://github.com/dmitry-lab-git/projects/blob/main/eco_service/readme.md)

* **No Obligation:** This contribution creates no legal, financial, or operational obligation for Auroville Eco-Service. Auroville Eco-Service is free to use, modify, extend, host, and operate all provided materials at its sole discretion, independently and without any requirement to proceed with a pilot, purchase services, or maintain an ongoing relationship with Dmitry Lab.

---

## TABLE OF CONTENTS
1. [Project Background & Value Proposition](#1-project-background--value-proposition)
2. [Proposed System Overview](#2-proposed-system-overview)
3. [Project Governance & Responsibility Model](#3-project-governance--responsibility-model)
4. [System Architecture & Client Touchpoints](#4-system-architecture--client-touchpoints)
5. [Software Test Data Simulation & Technical Validation](#5-software-test-data-simulation--technical-validation)
6. [Proposed ERP Field Pilot (Subsequent Operational Activity)](#6-proposed-erp-field-pilot-subsequent-operational-activity)
7. [Phased Implementation Roadmap](#7-phased-implementation-roadmap)
8. [Economic Model & Infrastructure Costs](#8-economic-model--infrastructure-costs)
9. [Optional Automation Configurations](#9-optional-automation-configurations)
10. [Ownership, Data Sovereignty, and Governance Agreements](#10-ownership-data-sovereignty-and-governance-agreements)
11. [Unresolved Decisions Requiring Eco-Service Confirmation](#11-unresolved-decisions-requiring-eco-service-confirmation)

---

## 1. PROJECT BACKGROUND & VALUE PROPOSITION

### 1.1 Practical Operational Challenges
Managing municipal waste streams in a decentralized community requires strict accounting between initial receipt at community collection yards, transport logistics, and central sorting facility processing. Without unified digital tracking:
- Material throughput and balance across sorted fractions cannot be verified in real time.
- Volume variations create scheduling bottlenecks at processing hubs.
- Physical accountability between collection, transport, and sorting relies on paper or verbal reporting, increasing administrative overhead.

### 1.2 Proposed ERP Value
The proposed ERP digitizes material flows from intake to recovery. It offers:
- **Material Balance Accountability:** Verification of gross intake weights against sorted fraction yields (`CLEAN_DRY`, `DIRTY_MIXED`, `ORGANIC`).
- **Operational Efficiency:** Simplified field data collection using accessible mobile tools (PWA, Telegram Mini Apps, and administrative web panels).
- **Data-Driven Oversight:** Real-time dashboards enabling Eco-Service leadership to optimize collection routes, facility staffing, and resource recovery strategies.

---

## 2. PROPOSED SYSTEM OVERVIEW

The system structures operations into six functional layers without imposing rigid hardware requirements:

```
+-----------------------------------------------------------------------------------+
|                            AUROVILLE ECO-SERVICE ERP                              |
+--------------------------+----------------------------+---------------------------+
| Master Data Management   | Waste Collection           | Material Resource         |
| (dicts)                  | Management (infrastructure)| Accounting (analytics)    |
+--------------------------+----------------------------+---------------------------+
| Operational Event        | Analytics & Reporting      | User & Access Management  |
| Tracking (bag_events)    | (Views & Dashboards)       | (security / RBAC)         |
+--------------------------+----------------------------+---------------------------+
```

1. **Master Data Management (`dicts`):** Centralized registers for yards, commercial entities, households, raw material categories, bag types, and authorized staff.
2. **Collection Lifecycle (`infrastructure.bags`):** Unique registration of individual waste batches or collection containers linked to origin points.
3. **Operational Event Store (`infrastructure.bag_events`):** Append-only log recording state changes (`SUBMITTED`, `ARRIVED`, `WEIGHED`, `SORTED`) with dynamic contextual data.
4. **Material Accounting (`analytics`):** Real-time aggregation of input mass versus sorted output fractions derived via event replay.
5. **Analytics & Executive Dashboards:** Reporting panels tracking site processing speeds, category yields, and collection frequencies.
6. **User & Access Management (`security`):** Role-based access control (RBAC) isolating field worker tasks, manager administrative panels, and executive reporting views.

---

## 3. PROJECT GOVERNANCE & RESPONSIBILITY MODEL

To ensure operational clarity, project responsibilities are strictly separated between digital software development and physical operational management.

```
+-----------------------------------------------------------------------------------+
|                            PROJECT GOVERNANCE MODEL                               |
+------------------------------------------+----------------------------------------+
| DMITRY LAB                               | AUROVILLE ECO-SERVICE                  |
| Digital & Technical Development          | Operational & Physical Implementation  |
+------------------------------------------+----------------------------------------+
| • System & database design               | • Legal & administrative approvals     |
| • Software & API development             | • Selection & approval of pilot sites  |
| • Application UI (Reflex, PWA specs)     | • Personnel assignment & management    |
| • Software testing & synthetic simulation| • Equipment procurement (printers/tags)|
| • Open Source codebase & documentation   | • VPS hosting & infrastructure setup   |
| • Expert technical consultation          | • Field operations & daily maintenance |
+------------------------------------------+----------------------------------------+
```

### 3.1 Scope of Dmitry Lab (Digital & Technical Development)
Dmitry Lab provides the complete technical software foundation as an Open Source in-kind contribution. Scope includes:
- Business process modeling and database schema architecture design.
- SQL DDL script development (schemata, spatial PostGIS indexes, constraints, audit views).
- Application backend logic and integration code (Python, `asyncpg`, `Pydantic`).
- Web administrative application development using the Reflex framework.
- Client interface specifications for PWA and Telegram Mini Apps.
- Synthetic simulation engine (`environment_initializer.py`) for software verification.
- Technical documentation, Docker deployment scripts, and the installation guide available at [eco_service/readme.md](https://github.com/dmitry-lab-git/projects/blob/main/eco_service/readme.md).
- Consultative technical support during system setup and evaluation.

*Dmitry Lab does not act as an operational manager, does not direct Eco-Service staff, and does not execute daily waste management operations.*

### 3.2 Scope of Auroville Eco-Service (Operational & Physical Implementation)
The administration of Auroville Eco-Service retains complete authority and executive responsibility for:
- Legal, administrative, and organizational approvals.
- Final selection and authorization of participating pilot sites, yards, and facilities.
- Allocation and management of Eco-Service staff and operators.
- Financial management, including procurement of hardware, smartphones, printers, and consumables.
- Provisioning and owning server hosting, domains, and security certificates.
- Physical facility preparation, equipment deployment, and field installation.
- Operational staff training and enforcement of daily data-entry workflows.
- Ongoing operational management, database backups, and daily system administration.

---

## 4. SYSTEM ARCHITECTURE & CLIENT TOUCHPOINTS

### 4.1 Core Architecture
The system utilizes PostgreSQL 13+ with the PostGIS spatial extension. Operational data uses an **Event Sourcing** design pattern: state transitions are saved as immutable historical events containing `JSONB` context structures, ensuring complete historical auditability.

### 4.2 Application Layer & Interface Clarification
- **Reflex App (Administrative Web Application):** A Python-based full-stack web framework used to build management dashboards, master data configuration tools, dispatch views, and reporting panels. Accessible via desktop and mobile web browsers for managers and system administrators.
- **Progressive Web Applications (PWA):** Mobile-optimized web interfaces designed for field operators (collectors, weighers, sorters). PWAs run directly in mobile web browsers and utilize standard Web Bluetooth APIs for printing.
- **Telegram Mini Apps (Optional Client Interface):** Light web-app touchpoints hosted inside Telegram, providing simple status queries and submission interfaces for residents or organization managers.

---

## 5. SOFTWARE TEST DATA SIMULATION & TECHNICAL VALIDATION

To ensure absolute methodological clarity, **Software Test Data Simulation** is strictly distinguished from real operational field testing.

### 5.1 Purpose of the Simulator (`environment_initializer.py`)
- **Scope:** Software development and technical validation utility.
- **Function:** Generates synthetic, artificially created operational records to test database schema performance, event-recording logic, JSONB payload integrity, analytical view calculations, and system behavior under load.
- **Boundaries:** 
  - Performed entirely within the software development and validation scope by Dmitry Lab.
  - Does **not** involve actual Auroville Eco-Service operations.
  - Does **not** constitute an ERP implementation or a field pilot.
  - Must **never** be presented as evidence of actual operational performance or real waste generation in Auroville.

### 5.2 Illustrative Planning Parameters Used in Simulation Testing
For software testing purposes only, the simulation script was configured with illustrative parameters (simulated window: September 1, 2026, 07:00 UTC to October 31, 2026, 21:00 UTC; ~580–760 generated test records; ~4.8–6.4 metric tonnes synthetic volume). These figures represent artificial test data parameters, **not** verified historical statistics of Eco-Service operations.

---

## 6. PROPOSED ERP FIELD PILOT (SUBSEQUENT OPERATIONAL ACTIVITY)

The **Proposed ERP Field Pilot** is a separate, subsequent implementation activity representing the actual use of the developed ERP system within Auroville Eco-Service operations.

### 6.1 Field Pilot Scope & Responsibilities
- **Execution:** Auroville Eco-Service is exclusively responsible for organizing and conducting the field pilot. Dmitry Lab provides technical, consultative, and expert support.
- **Operational Elements (Subject to Confirmation):**
  - Use of approved operational sites and facilities.
  - Participation of actual Eco-Service personnel.
  - Implementation of physical identification, QR code labeling, and marking procedures.
  - Execution of real collection, transportation, weighing, and sorting activities.
  - Recording of authentic operational data and generation of management reports.
  - Evaluation of application usability and operational suitability under tropical field conditions.
- **Important Status Note:** Participating sites, exact duration, operational scope, required resources, and start date remain **subject to confirmation by Auroville Eco-Service**. No field pilot has taken place, and no operational conditions have been pre-approved.

---

## 7. PHASED IMPLEMENTATION ROADMAP

```
+-----------------------------------------------------------------------------------+
| PHASE 1: Digital System Development & Technical Validation (Dmitry Lab)           |
| Deliver software repository, database DDL, Reflex web app, and simulation tests.  |
+-----------------------------------------------------------------------------------+
                                          │
                                          ▼
+-----------------------------------------------------------------------------------+
| PHASE 2: Operational Preparation (Eco-Service with Dmitry Lab support)           |
| Select pilot sites, setup VPS hosting, procure hardware, train field operators.   |
+-----------------------------------------------------------------------------------+
                                          │
                                          ▼
+-----------------------------------------------------------------------------------+
| PHASE 3: Field Pilot Execution (Eco-Service with Dmitry Lab support)             |
| Conduct live operations, record real waste flows, gather field usability feedback. |
+-----------------------------------------------------------------------------------+
                                          │
                                          ▼
+-----------------------------------------------------------------------------------+
| PHASE 4: Evaluation & Strategic Decisions (Eco-Service & Dmitry Lab)              |
| Review system performance KPI, audit OPEX, decide on potential scaling.           |
+-----------------------------------------------------------------------------------+
```

### Roadmap Summary Table

| Phase | Phase Name | Primary Responsibility | Key Deliverables & Activities |
| :---: | :--- | :--- | :--- |
| **1** | **Digital System Development & Technical Validation** | **Dmitry Lab** | Deliver database DDL, backend scripts, Reflex app code, Docker scripts, and installation instructions via [GitHub](https://github.com/dmitry-lab-git/projects/tree/main/eco_service). |
| **2** | **Operational Preparation** | **Auroville Eco-Service** *(Support: Dmitry Lab)* | Confirm pilot sites, provision VPS hosting, procure hardware/printers, establish operational procedures, train staff. |
| **3** | **Field Pilot Execution** | **Auroville Eco-Service** *(Support: Dmitry Lab)* | Execute live field operations, tag waste batches, record weights, process sorting flows, refine software based on feedback. |
| **4** | **Evaluation & Strategic Decisions** | **Auroville Eco-Service** *(Support: Dmitry Lab)* | Review operational KPIs, analyze material balance precision, assess ongoing OPEX, decide on further system scaling. |

---

## 8. ECONOMIC MODEL & INFRASTRUCTURE COSTS

The financial model clearly separates Dmitry Lab's technical contribution from Eco-Service's operational expenses.

### 8.1 Dmitry Lab Software Contribution
Offered as an in-kind Open Source gift to Auroville:
- System architecture & database schema design ($0 software license fee).
- Application code, API logic, and Reflex administrative panels ($0 software license fee).
- Technical documentation, deployment scripts, and installation guide ($0 software license fee).
- Expert technical advisory support ($0 consulting fee within agreed pilot scope).

### 8.2 Eco-Service Implementation Expenses
Eco-Service is responsible for funding practical setup and operational costs:

1. **Mandatory Hosting & Infrastructure Expenses:**
   - Virtual Private Server (VPS) hosting (PostgreSQL + Python application backend).
   - Domain name registration, SSL/TLS security certificates, DNS services.
   - Offsite database backup storage infrastructure.
2. **Optional Hardware & Consumables Expenses (Subject to local supplier quotes):**
   - Portable Bluetooth thermal printers (e.g., Niimbot B1 / B21) if automated labeling is selected.
   - Field operator smartphones (Android 7.0+, autofocus camera, Bluetooth 4.2+).
   - Label consumables (weather-resistant synthetic media).
3. **Operational Expenses:**
   - Staff time, facility preparation, physical installation, and ongoing site maintenance.

*Note: The project cannot operate at absolute zero cost. Even at Level 1 manual entry, basic hosting, domain, and server maintenance costs remain mandatory.*

---

## 9. OPTIONAL AUTOMATION CONFIGURATIONS

Eco-Service can choose from five modular automation levels based on operational priorities and budget. Higher levels can be introduced progressively without altering core database history.

```
 LEVEL 1: Manual Data Entry ─────────────> Web Form Entry at Processing Hub (Zero CAPEX)
 LEVEL 2: Stationary Placards ───────────> Laminated Code Placards at Collection Yards
 LEVEL 3: Container QR Identification ───> Durable QR Stickers on Bins + Portable Printer
 LEVEL 4: Individual Bag Tracking ───────> PET/PP Label Printed for Every Bag Handover
 LEVEL 5: Automated IoT Infrastructure ──> Load-Cell Scales + RFID Bins + Resident Cards
```

### Detailed Configuration Comparison

| Level | Configuration Name | Equipment Requirements | Consumables | Financial Profile | Operator Workflow |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **1** | **Manual Data Entry** | Existing smartphone or desktop PC at sorting hub. | None. | **Zero CAPEX / Low OPEX** *(VPS hosting only)* | Manual numeric entry of weights into web forms. |
| **2** | **Stationary Placards** | Laminated code placards attached to yard collection bins. | Paper/Lamination film. | **Minimal CAPEX (<$10)** | Staff manually enter or scan fixed location codes. |
| **3** | **Container QR Identification** | 1–3 portable Bluetooth thermal printers + operator smartphones. | Direct thermal paper or synthetic stickers. | **Low CAPEX (~$60–$120)** *(Preliminary estimate)* | Operators scan fixed bin QR stickers to log collection events. |
| **4** | **Individual Bag QR Tracking** | Fleet of portable Bluetooth thermal printers + smartphones. | Weather-resistant synthetic rolls (PET / PP). | **Moderate CAPEX (~$150–$200)** + **Regular Consumable OPEX** | Printer generates a unique synthetic label for every bag at intake. |
| **5** | **Automated IoT Infrastructure** | Bins with integrated load cells, ESP32/Raspberry Pi controllers, RFID readers, resident cards. | Plastic RFID cards, hardware spares. | **High CAPEX ($1,000+)** + **IoT Maintenance OPEX** | Residents tap RFID card; container automatically weighs and logs waste. |

### Label Material Clarification (For Levels 3 & 4)
- **Polypropylene (PP):** Flexible, water-resistant synthetic material suitable for short-to-medium term bag identification under typical field handling.
- **Polyethylene Terephthalate (PET):** High-durability synthetic material offering superior tear resistance, UV stability, and chemical tolerance for harsh environmental conditions.

---

## 10. OWNERSHIP, DATA SOVEREIGNTY, AND GOVERNANCE AGREEMENTS

Prior to formal deployment, Dmitry Lab and Auroville Eco-Service will formalize a lightweight governance agreement covering the following operational matters:

1. **Source Code Rights & Open Source Terms:** The software repository is provided as Open Source ([Repository URL](https://github.com/dmitry-lab-git/projects/tree/main/eco_service)), granting Auroville Eco-Service an irrevocable, non-exclusive, royalty-free license to use, modify, and extend the codebase.
2. **Data Ownership & Privacy:** All operational data, resident registries, facility statistics, and analytical reports remain the exclusive property of Auroville Eco-Service. Dmitry Lab claims no ownership or commercial rights over operational data.
3. **Hosting Infrastructure Administration:** Server accounts, database access keys, domain registrations, and cloud management dashboards must be registered under accounts owned and controlled by Eco-Service.
4. **Information Security & Backups:** Eco-Service maintains administrative responsibility for managing database access credentials, firewall settings, and automated offsite backup policies, supported by the installation README guide.
5. **Post-Pilot Technical Support:** Following the completion of Phase 3, ongoing technical support, custom feature development, or system maintenance arrangements will be reviewed and agreed upon by both parties based on pilot evaluation results.

---

## 11. UNRESOLVED DECISIONS REQUIRING ECO-SERVICE CONFIRMATION

The following items are marked **"To be confirmed by Auroville Eco-Service"** and require executive confirmation prior to Phase 2 operational launch:

- [ ] **Confirmation of Pilot Scope:** Selection and approval of specific participating pilot locations, yards, and facilities.
- [ ] **Selected Automation Level:** Selection of baseline automation configuration (Level 1, 2, 3, 4, or 5).
- [ ] **Hosting Provisioning:** Approval of VPS server hosting budget, domain name, and hosting provider account ownership.
- [ ] **Hardware Procurement Approval:** Authorization for purchasing portable thermal printers, label media, and smartphones (if Level 3 or 4 is selected).
- [ ] **Personnel Allocation:** Designation of Eco-Service staff responsible for project coordination, field operations, and database administration.
- [ ] **Pilot Schedule Authorization:** Approval of target start date and evaluation timeline for Phase 3 field operations.

---
*End of Business Plan & Integration Proposal Document.*