# Auroville Eco-Service ERP

**Open Source Waste Management & Resource Accounting System**

An architectural and software development framework for recording waste collection, weighing, sorting, storage, and transfer operations.

Each waste bag can be assigned an individual record and QR-code identification. The system is designed to maintain traceability across its operational lifecycle: where the bag originated, who handled it, its recorded weight, and how its contents were sorted or transferred.

**Project Sponsor / Technical Developer:** Dmitry Lab  
**Status:** Open Source Development Framework  
**Database:** `auroville_eco_service`  
**Database Timezone:** UTC (0)

---

## 1. Project Overview

The project provides a technical foundation for a potential ERP system supporting waste management and resource accounting within Auroville Eco-Service.

Its main objective is to establish structured records for operational events and material flows.

The proposed workflow includes:

1. Waste submission or collection.
2. Arrival and receipt registration.
3. Weighing.
4. Sorting and classification.
5. Storage or transfer.
6. Recording of the final destination.

The database is designed around structured operational records and event history, allowing activities to be traced and analyzed over time.

**Development scope:** The repository contains an existing database architecture, backend components, application source code, and technical documentation. It is a development framework, not a complete, production-ready ERP deployment.

## 2. Project Structure

```text
eco_service/
│
├── ddl/
│   ├── full_schema_auroville_eco_service.sql  # Consolidated schema (single deployment script)
│   ├── 00_extensions_postgis.sql
│   ├── 01_dicts.sql
│   ├── 02_infrastructure.sql
│   ├── 03_security.sql
│   ├── 04_analytics.sql
│   └── readme.txt
│
├── app/                                   # Reflex application source (PWA)
│   ├── app.py
│   ├── dashboard/
│   │   ├── pages/
│   │   │   ├── index.py                   # Main role navigation portal
│   │   │   ├── collector/                 # Field collector interface
│   │   │   ├── sorter/                    # Hub sorter interface
│   │   │   ├── manager/                   # Manager dashboards & KPIs
│   │   │   └── routes.py
│   │   ├── components/
│   │   │   ├── charts.py                  # Collection trends & analytics charts
│   │   │   ├── kpi_cards.py
│   │   │   ├── analytics_tables.py
│   │   │   └── universal_form.py / operator_form.py
│   │   └── role_config.py
│   ├── database/
│   │   ├── connection.py                  # asyncpg connection
│   │   └── config.py
│   ├── models/
│   │   ├── dicts.py / infrastructure.py / analytics.py
│   ├── states/
│   │   ├── auth.py / analytics.py / base.py
│   └── assets/
│       └── icon.svg
│
├── docs/
│   ├── Auroville_Eco_Service_ERP_Development_Transfer_Proposal.pdf
│   ├── Auroville_Eco_Service_ERP_Governance_Framework.pdf
│   ├── UX_UI_&_System_Architecture_Overview.pdf
│   ├── database_design_document.md
│   ├── open_source_architecture_integration_proposal.md
│   ├── project_governance_and_decisions.md
│   └── screenshots/
│       ├── 1_desktop_main_screen.png
│       ├── 2-5_desktop_manager_screens.png
│       ├── 6_mobile_sorter.jpg / 7_mobile_collector.jpg
│       └── 8-9_mobile_manager_*.jpg
│
├── LICENSE                                # MIT License (Copyright © 2026 Dmitry Lab)
├── config.py / model_config.py            # Application & Pydantic models
├── database.py / security_utils.py        # DB connection & password hashing
├── environment_initializer.py              # Synthetic test data generator (DESTRUCTIVE - dev only)
├── set_operator_password.py
├── rxconfig.py / requirements.txt
├── AGENTS.md / CLAUDE.md
└── readme.md

The `ddl/` directory contains the database definitions. The consolidated SQL file provides the complete schema in one script.

The `.web/`, `.states/`, and `venv/` directories are local or generated environment artifacts and should not be treated as substitutes for the source code and configuration files.

## 3. Database Architecture

**Database name:** `auroville_eco_service`

The database is organized into four logical schemas:

| Schema | Purpose |
|---|---|
| `dicts` | Reference dictionaries and classification data |
| `infrastructure` | Physical infrastructure, bags, and operational events |
| `security` | Users, authentication, and access-related structures |
| `analytics` | Reporting views and analytical data structures |

**Database timezone:** UTC (0).

**Required extension:** PostGIS.

The complete database structure is provided in:

```text
ddl/full_schema_auroville_eco_service.sql
```

For a detailed description of the tables and their relationships, see:

```text
database_design_document.md
```

## 4. Software Requirements

### 4.1 Development Environment

- Ubuntu Linux or Windows Subsystem for Linux (WSL).
- Python 3.11 or newer.
- PostgreSQL 13 or newer.
- PostGIS extension compatible with the installed PostgreSQL version.
- DBeaver or another PostgreSQL administration tool.

### 4.2 Python Dependencies

The project uses the dependencies declared in `requirements.txt`, including:

- Reflex (version 0.6.0 or newer).
- asyncpg.
- bcrypt.
- Pydantic.
- python-dotenv.

Install the complete dependency set from the repository file rather than installing packages individually.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 5. Database Restoration

Database initialization is normally performed once by the receiving IT administrator.

### Step 1 — Create an Empty Database

Create a PostgreSQL database named:

```text
auroville_eco_service
```

The database should be owned by an appropriately configured application or administrative role.

### Step 2 — Enable Required Extensions

Ensure that PostGIS is installed and available on the PostgreSQL server.

The receiving administrator must verify that the required extensions can be created in the target database.

### Step 3 — Execute the Consolidated DDL

Run the complete schema file against the newly created database:

```text
ddl/full_schema_auroville_eco_service.sql
```

This script contains the consolidated database definitions.

It should be executed against an empty database, not against an existing operational database without a separate migration and backup plan.

### Step 4 — Verify the Database

Connect to `auroville_eco_service` using DBeaver or another PostgreSQL client.

Verify that the following four schemas are present:

- `dicts`
- `infrastructure`
- `security`
- `analytics`

Review the resulting tables and database objects against `docs/DBDD.md`.

**Important:** Database initialization and application configuration are separate tasks. Creating the database does not automatically configure application credentials, users, or deployment security.

## 6. Reflex Web Application (PWA)

The user interface is developed using Reflex.

A Progressive Web App (PWA) is a web application that can be accessed through a browser and, on supported devices, installed as an application-like shortcut without distribution through an app store.

The intended interface is organized around three operational access levels:

| Level | User Role | Intended Function |
|---|---|---|
| Level 0 | Resident | Submit or register a waste bag |
| Level 1 | Collector / Sorter | Record collection, weighing, and sorting operations |
| Levels 2–3 | Manager / CEO | Review dashboards, maps, KPIs, and operational information |

The actual availability of functions depends on the implemented application components and configured permissions.

### 6.1 Local Development Environment

For development and internal testing, the database and application can run on the same computer.

The application is accessed locally through the address provided by Reflex, normally:

```text
http://localhost:3000
```

Local access is intended for development and testing, not for public operational use.

### 6.2 VPS Deployment

A Virtual Private Server (VPS) is a remotely hosted computer that can run continuously and provide access to the application over the internet.

A possible deployment arrangement for Eco-Service is:

1. Prepare a Linux server.
2. Install PostgreSQL and the required PostGIS extension.
3. Create the `auroville_eco_service` database.
4. Initialize the database using the consolidated DDL script.
5. Transfer the project source code to the server.
6. Configure Python dependencies and application settings.
7. Configure database access and application credentials.
8. Start the Reflex application.
9. Configure Nginx as a reverse proxy.
10. Configure a domain name and HTTPS.
11. Establish backups, access controls, monitoring, and security procedures.

After successful deployment, authorized users can access the application through a common web address.

The receiving organization determines the hosting provider, infrastructure specifications, deployment configuration, and operating procedures.

**Deployment note:** The steps above describe a possible architecture, not a verified turnkey installation procedure. The actual configuration must be checked against the current application source, Reflex version, server environment, and security requirements.

## 7. Synthetic Test Data

The repository includes:

```text
environment_initializer.py
```

This utility is intended for software development and testing.

It initializes reference data and generates synthetic operational records for testing database operations, application workflows, and analytical views.

**CRITICAL WARNING — DESTRUCTIVE OPERATION**

The initializer clears existing database data before generating a synthetic dataset.

- Use it only in a dedicated development or test database.
- Never execute it against a production or operational Eco-Service database.
- Verify the active database connection and configuration before running it.
- Back up any data that must be retained.

The generated records are synthetic. They do not represent actual Eco-Service measurements, field operations, or pilot results.

A software simulation is not an operational field pilot.

## 8. Field Hardware & Identification

The proposed field configuration may include:

| Component | Intended Use |
|---|---|
| Niimbot B1 / B21 printer | Printing QR identification labels |
| Weather-resistant PET labels | Bag identification in field conditions |
| Smartphone or tablet | Recording collection and sorting events |
| Internet connection | Accessing the centrally hosted application |

The final hardware selection should be verified against the actual label dimensions, printer compatibility, expected environmental conditions, and operational requirements.

Hardware procurement is not included in the Open Source software contribution.

## 9. Configuration & Security

Application configuration is maintained separately from the source code.

Before deployment, the receiving administrator must configure the required environment variables and database connection settings in accordance with the current project configuration.

At a minimum:

- Do not commit passwords, database credentials, or secret keys to the public repository.
- Use appropriately restricted database accounts.
- Protect administrator and operator credentials.
- Use HTTPS for external access.
- Restrict server and database access to authorized users and services.
- Establish a backup and recovery procedure.
- Review access permissions before operational deployment.

The receiving organization is responsible for its hosting environment, credentials, infrastructure security, and operational data governance.

## 10. Technical Documentation

The repository includes the following reference materials:

| File | Description |
|---|---|
| `ddl/full_schema_auroville_eco_service.sql` | Consolidated database schema |
| `docs/DBDD.md` | Database structure and table documentation |
| `BP.md` | Business process description |
| `model_config.py` | Pydantic data models |
| `environment_initializer.py` | Synthetic test data initialization |
| `requirements.txt` | Python dependencies |
| `app/` | Reflex application source |

For additional architectural context, consult the project documentation in `docs/`.

## 11. Contribution & Licensing

The project is provided by Dmitry Lab as a free-of-charge Open Source contribution under the MIT License.

The license permits use, modification, distribution, and commercial use subject to its terms and conditions.

Third-party components remain subject to their respective licenses.

The contribution provides existing technical materials for independent review and potential adaptation. It does not include an obligation for production deployment, ongoing maintenance, hosting, continuous development, or operational support.

Auroville Eco-Service independently determines whether and how to use the materials.

---

**Project Repository:**  
https://github.com/dmitry-lab-git/projects/tree/main/eco_service

**Initiative Sponsor / Technical Developer:** Dmitry Lab

**THE DECISION REMAINS WITH AUROVILLE ECO-SERVICE.**
