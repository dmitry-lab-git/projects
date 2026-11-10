# AUROVILLE ECO-SERVICE ERP
## Project Governance, Methodology, and Decision Framework

**Initiative Sponsor / Technical Developer:** Dmitry Lab  
**Target Recipient:** Auroville Eco-Service Administration & Governance  
**Document Status:** Revised Draft — Third Edition (Open Source & Responsibilities Framework)  
**Language:** English  

---

## 1. PROJECT GOVERNANCE PRINCIPLE

> **"Dmitry Lab develops the digital system. Auroville Eco-Service implements and operates it, with consultative and expert support from Dmitry Lab."**

### 1.1 Open Source Contribution & No-Obligation Framework
* **Open Source Codebase:** The entire project is available under Open Source terms at [https://github.com/dmitry-lab-git/projects/tree/main/eco_service](https://github.com/dmitry-lab-git/projects/tree/main/eco_service).
* **Installation & Deployment Guide:** Instructions and setup details are maintained in the README file at [https://github.com/dmitry-lab-git/projects/blob/main/eco_service/readme.md](https://github.com/dmitry-lab-git/projects/blob/main/eco_service/readme.md).
* **Nature of Contribution:** Dmitry Lab provides the complete technical foundation as an in-kind gift and Open Source contribution, including SQL DDL schema definitions, Python backend code, Reflex web application source, Docker deployment scripts, and technical documentation.
* **No Obligation:** This contribution creates no legal, financial, or operational obligation for Auroville Eco-Service. Eco-Service is fully autonomous in deciding whether and how to use, modify, host, or deploy the materials.

---

## 2. RESPONSIBILITY MATRIX

| Functional Area | Dmitry Lab (Digital & Technical Development) | Auroville Eco-Service (Operational & Physical Implementation) |
| :--- | :--- | :--- |
| **System Architecture & Design** | **Lead Responsibility:** Database schemas, event sourcing logic, API design. | Review and approval of functional requirements. |
| **Software Development** | **Lead Responsibility:** SQL scripts, Python backend, Reflex App UI, simulation tools. | None. |
| **Open Source & Documentation** | **Lead Responsibility:** Maintaining GitHub repository and [Installation README](https://github.com/dmitry-lab-git/projects/blob/main/eco_service/readme.md). | Reviewing operational guides and manuals. |
| **Legal & Administrative Approvals** | Consultative support only. | **Lead Responsibility:** Obtaining necessary community and institutional approvals. |
| **Site Selection & Pilot Scope** | Consultative guidance. | **Lead Responsibility:** Selecting, approving, and preparing pilot yards and facilities. |
| **Infrastructure & Hosting** | Technical setup guidance via README. | **Lead Responsibility:** Procuring and owning VPS hosting, domain, and backups. |
| **Hardware & Consumables** | Recommendations on printer specs (Niimbot) and labels. | **Lead Responsibility:** Procuring hardware, smartphones, printers, and consumables. |
| **Staff Training & Operations** | Expert technical training and consultation. | **Lead Responsibility:** Assigning personnel, enforcing data workflows, and daily operations. |

---

## 3. METHODOLOGICAL DISTINCTION: SIMULATION VS. FIELD PILOT

### 3.1 Software Test Data Simulation (`environment_initializer.py`)
- **Classification:** Internal software development and validation utility.
- **Purpose:** Generates synthetic data to test database performance, event logging, and analytical views during development.
- **Status:** Performed by Dmitry Lab; does **not** represent actual Eco-Service waste operations and must not be cited as pilot performance statistics.

### 3.2 Proposed ERP Field Pilot
- **Classification:** Subsequent operational activity.
- **Purpose:** Live operational testing of the ERP system within Auroville Eco-Service waste collection workflows.
- **Status:** Organized and conducted entirely by Auroville Eco-Service at approved sites. Subject to prior confirmation by Eco-Service management.

---

## 4. PENDING CONFIRMATION CHECKLIST (FOR ECO-SERVICE)

- [ ] Review Open Source repository ([GitHub Eco-Service Link](https://github.com/dmitry-lab-git/projects/tree/main/eco_service)).
- [ ] Review installation and setup guide ([README.md](https://github.com/dmitry-lab-git/projects/blob/main/eco_service/readme.md)).
- [ ] Confirm selection of pilot sites and participating entities.
- [ ] Select preferred automation level (Levels 1 through 5).
- [ ] Authorize VPS hosting setup and hardware procurement.

---
*End of Project Governance and Decisions Document.*