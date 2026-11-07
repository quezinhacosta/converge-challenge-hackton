# PAYTRUST (POWERED BY TAKO)

Digital Worker for Payroll Governance, Anti-Fraud, and Leaves
Converge Challenge powered by Tako

---

## 1. Executive Summary and Business Thesis

### Product Definition
PayTrust is a digital worker and financial intelligence middleware for enterprise payroll. It integrates predictive Machine Learning anomaly detection with automated statutory leave processing, temporary substitution wage adjustments (Sumula 159 TST), and real-time paystub explainability.

### Market Pain Point
Traditional ERPs and HR systems (e.g., TOTVS, Senior, ADP) operate as blind calculators: they process inputs, timecards, and manager approvals without verifying historical behavioral patterns or complex labor regulations.

- Labor Liabilities and Rework: Inaccurate additions, miscalculated sick leaves, and unverified overtime inflations affect 5% to 8% of corporate payroll batches.
- Rework Friction: Personnel Departments (DP) spend days resolving eSocial submission rejections and fielding repetitive employee questions regarding paystub line items.

### Business Model and Scalability
- B2B SaaS Model: Priced per audited active employee per month (R$ 3.00 to R$ 6.00 / life).
- Immediate Return on Investment (ROI): Preventing a single fraudulent overtime incident or labor lawsuit covers platform operating costs for years.
- Mergers and Acquisitions (M&A) Thesis: Highly defensible, pre-payment governance layer designed as a modular plug-in for major ERP and HRTech ecosystems (TOTVS, Senior, ADP, Flash, Caju).

---

## 2. Two-Layer AI Architecture

PayTrust separates statistical fraud detection from regulatory interpretation through a two-layer decoupled design:

```
+-----------------------------------------------------------+
|   Input: Payroll Batch (CSV/JSON) + Certificates (Img/PDF)|
+-----------------------------+-----------------------------+
                              |
                              v
+-----------------------------------------------------------+
|   LAYER 1: Predictive Anomaly Detection (ML Engine)       |
|   - Scikit-Learn Isolation Forest / LinearSVC             |
|   - Generates the continuous PayTrust Score (0 to 100)    |
+-----------------------------+-----------------------------+
                              |
                              v
+-----------------------------------------------------------+
|   LAYER 2: Generative Compliance & Vision OCR (LLM Engine)|
|   - OCR and Vision parser for medical certificates        |
|   - RAG with Brazilian Labor Law (CLT) and Sumula 159 TST |
+-----------------------------+-----------------------------+
                              |
                              v
+-----------------------------------------------------------+
|   Interfaces: DP Governance Dashboard + Employee Portal   |
+-----------------------------------------------------------+
```

### Layer Comparison Matrix

| Layer | Technology | Functional Role |
| :--- | :--- | :--- |
| Layer 1: Predictive Detection (ML) | Scikit-Learn (Isolation Forest / LinearSVC) in Python | Analyzes batch metrics to compute the PayTrust Score (0-100), detecting numerical anomalies, sudden overtime spikes, and duplicates. |
| Layer 2: Parsing & Compliance (LLM) | Groq / OpenAI (Llama-3 / GPT-4o-mini) + Vision OCR | Extracts structured data from doctor notes, validates statutory thresholds (Employer 15-day cap vs. INSS), calculates Sumula 159 TST differentials, and provides transparent explanations. |

---

## 3. Monorepo Structure (Clean Architecture)

```
converge-challenge-hackton/
|-- .github/
|   `-- workflows/
|       |-- ci.yml                   # Linting (Ruff), Type-checking (Mypy), and ML validation
|       `-- cd.yml                   # Automated deployment pipeline
|-- .pre-commit-config.yaml          # Git hooks: Ruff format, Ruff check, Mypy, file hygiene
|-- backend/                         # Python 3.11+ / FastAPI
|   |-- pyproject.toml               # Tooling configuration (Ruff, Mypy, Pytest)
|   |-- requirements.txt             # Production and development dependencies
|   |-- app/
|   |   |-- domain/                  # Pure enterprise domain entities and repository contracts
|   |   |   |-- entities/            # Employee, Absence, Paystub, Anomaly
|   |   |   `-- repositories/        # Abstract repository interfaces
|   |   |-- application/             # Business use cases and data transfer objects (DTOs)
|   |   |   |-- dtos/                # Request/response schemas
|   |   |   `-- use_cases/           # AuditPayrollUseCase, ProcessAbsenceUseCase, CalculateSubstitutionUseCase
|   |   |-- infrastructure/          # Adapters and external service implementations
|   |   |   |-- ml/                  # Isolation Forest anomaly model and artifacts (.pkl)
|   |   |   |-- ocr/                 # Vision parser for medical certificates
|   |   |   |-- llm/                 # Compliance agent and explainability clients
|   |   |   `-- repositories/        # In-memory and persistent database adapters
|   |   `-- presentation/            # Entrypoints and API layer
|   |       |-- main.py              # FastAPI server entrypoint
|   |       `-- api/v1/endpoints/    # REST endpoints (health, payroll, absences)
|   |-- scripts/
|   |   `-- train_anomaly_model.py   # Isolated model training and serialization script
|   `-- tests/
|       `-- unit/                    # Unit tests for domain entities and ML serialization
`-- frontend/                        # Next.js / TypeScript / Tailwind CSS
    |-- package.json                 # Node package configuration
    |-- tsconfig.json                # TypeScript compiler configuration
    `-- src/
        |-- app/                     # Next.js App Router root layout and pages
        |-- components/
        |   |-- dp-dashboard/        # DP Analyst Interface (AuditActionCenter, AbsenceManager, AnomalyAlertsList)
        |   |-- employee-portal/     # Employee Interface (InteractivePaystub, CertificateUploadModal, ExplainabilityChat)
        |   `-- common/              # Shared design components (MetricsCard)
        |-- services/                # Backend API integration clients
        `-- types/                   # TypeScript domain contracts
```

---

## 4. MVP Use Case Matrix

| ID | Use Case | PayTrust Automated Action | Expected Impact |
| :--- | :--- | :--- | :--- |
| 1 | Simple Medical Leave (<= 15 days) | OCR parses dates and doctor information; attributes 100% of days to employer responsibility under CLT Art. 476. | Happy Path: Automated logging with manager notification. |
| 2 | Long Medical Leave (> 15 days) | Automatically splits leave: first 15 days paid by company; remaining days routed to INSS with medical exam scheduling checklist. | Business Rule: Statutory threshold enforcement without manual calculation. |
| 3 | Illegible Medical Certificate | Instant OCR rejection during upload; prompts the employee to upload a legible photograph immediately. | Exception Handling: Prevents degraded or invalid submissions from reaching DP. |
| 4 | Leave Overlapping Scheduled Vacation | Detects schedule conflict between medical leave and booked annual vacation; escalates immediate resolution card to HR. | Escalation: Proactive conflict resolution before payroll lock. |
| 5 | Non-Occasional Replacement (Sumula 159 TST) | Validates replacement condition and calculates proportional wage differential based on the absent employee's salary. | Financial Compliance: Full alignment with labor jurisprudence. |
| 6 | Overtime Anomaly Spike | Isolation Forest flags uncharacteristic overtime surge (e.g., PayTrust Score 94/100); blocks item pending review. | Anti-Fraud: Halts improper cash outflow before monthly disbursement. |

---

## 5. Human-in-the-Loop Governance Guardrails

To ensure labor compliance, accountability, and ethical deployment:

- Automated Assistant Role: The AI digital worker performs OCR parsing, calculates proportional wage differentials, executes ML anomaly scoring, and cites labor regulations.
- Human Final Authority: The Department of Personnel (DP) analyst or HR manager retains exclusive authority to approve disbursements or dismiss flagged items via a 1-click review action.

---

## 6. Code Quality, Tooling, and CI/CD

### Static Analysis and Linters
- Ruff: Python linter and formatter running on py311 rules.
- Mypy: Strict static typing verification on domain, application, and infrastructure modules.
- Pre-commit: Local Git hooks ensuring clean commits, trailing whitespace removal, and code formatting.

### CI/CD Pipeline
- Continuous Integration (`.github/workflows/ci.yml`):
  1. Executes `ruff check` and `ruff format --check`.
  2. Executes `mypy app scripts` across the backend codebase.
  3. Executes model training and runs automated `pytest` test suites.
  4. Verifies frontend package dependencies and configuration files.
- Continuous Deployment (`.github/workflows/cd.yml`):
  Prepares automated deployment targets for FastAPI and the Next.js web application.

---

## 7. Local Setup Instructions

### Backend (Python 3.11+)
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run linter and formatting checks
ruff check .
ruff format --check .

# Run static type checker
mypy app scripts

# Train anomaly model artifact
python scripts/train_anomaly_model.py

# Run unit tests
pytest tests/ -v
```

### Pre-commit Configuration
```bash
pre-commit install
pre-commit run --all-files
```

### Frontend (Node.js 20+)
```bash
cd frontend
npm install
npm run type-check
npm run dev
```
