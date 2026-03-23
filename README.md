<div align="center">

# 🧬 QuantumDX  
### *Privacy-FirstQuantum-Enhanced Disease Detection with Production-Grade MLOps*

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![Qiskit](https://img.shields.io/badge/Qiskit-2.2-6929C4?logo=qiskit&logoColor=white)](https://qiskit.org)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.134-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Deploy: Railway](https://img.shields.io/badge/API-Railway-0B0D0E?logo=railway&logoColor=white)](https://railway.app)
[![Deploy: Vercel](https://img.shields.io/badge/Frontend-Vercel-000000?logo=vercel&logoColor=white)](https://vercel.com)
[![Tests](https://img.shields.io/badge/Tests-25%2F25_passing-brightgreen)](#testing)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**Encode patient symptoms into quantum states. Diagnose disease with quantum fidelity. Destroy the raw data forever.**

---

* Conceptionalized and built for [Hack for Humanity 2026](https://www.hackforhumanity.io/) — targeting leptospirosis screening at community health posts in Kisumu County, Kenya.*

</div>

---

## The Problem

In rural Kenya, **leptospirosis** kills through misdiagnosis. Community health workers lack lab infrastructure, and sending patient data to centralized systems creates privacy risks in regions with limited data protection.

**QuantumDx** solves both problems at once: it uses quantum computing to diagnose disease from symptoms alone, then **permanently destroys** the raw patient data — leaving only a quantum fingerprint that cannot be reverse-engineered.

---

## How It Works

```mermaid
flowchart LR
    A["24 Clinical Features\nfever, jaundice, vitals, labs..."] --> B["8-Qubit ZZFeatureMap\nlinear entanglement, depth=2\n256-dim statevector"]
    B --> C["Fidelity Kernel\nF = |⟨ψ|φ⟩|²\nvs 30 synthetic references"]
    B --> D["Raw Data Shredded\nDoD 5220.22-M 3-pass wipe"]
    C --> E["anomaly_prob\n0% = healthy → 100% = sick"]
```
---

### The Quantum Pipeline

1. **Condense** — 24 raw clinical features (17 symptoms + 7 vitals/labs) are compressed into 8 composite features mapped to `[0, π]`
2. **Encode** — Each composite drives one qubit of an 8-qubit [ZZFeatureMap](https://docs.quantum.ibm.com/api/qiskit/qiskit.circuit.library.ZZFeatureMap) circuit with linear entanglement
3. **Simulate** — Statevector simulation produces a 256-dimensional complex vector (the "quantum fingerprint")
4. **Classify** — Fidelity kernel `F(ψ,φ) = |⟨ψ|φ⟩|²` compares the patient state against 30 synthetic reference patients (15 healthy, 15 sick)
5. **Shred** — Raw patient data is overwritten using DoD 5220.22-M 3-pass secure erasure

> The quantum fingerprint is **one-way** — you cannot recover the original symptoms from the statevector.

## Validation Results

Tested on **141 real leptospirosis patients** from Kisumu County, Kenya:

| Metric | Value |
|:-------|:------|
| **Accuracy** | 79% (111/141) |
| **Sensitivity** | 60% (34/57 positives caught) |
| **Specificity** | 92% (77/84 negatives cleared) |

```
                Predicted
              Neg     Pos
Actual Neg │  77   │   7  │  92% specificity
Actual Pos │  23   │  34  │  60% sensitivity
```

High specificity (92%) means fewer false alarms — critical for resource-constrained clinics where every referral costs time and money.

---

## Solution

**QuantumDX** combines:

- ⚛️ Quantum-inspired feature encoding
- 🤖 Machine learning diagnostics
- 🏥 Clinical symptom analysis
- 🔄 Real-time data ingestion + retraining

To deliver:

Fast, explainable, and continuously improving diagnosis.

---

## Validation

•	✔️ High sensitivity for severe cases
•	✔️ Robust across multiple clinics
•	✔️ Improved early-stage detection


---

## Architecture

```mermaid
flowchart LR
    subgraph Frontend
        UI[React App]
    end

    subgraph API["FastAPI + Pipeline"]
        API1[patients]
        API2[diagnose]
        API3[retrain]
        API4[metrics]
    end

    subgraph Agents
        ING[IngestionAgent]
        VAL[ValidationAgent]
        ENC[EncodingAgent]
        PRIV[PrivacyAgent]
        FS[FeatureStoreAgent]
        TRAIN[TrainingAgent]
        FED[FederatedAgent]
        REG[RegistryAgent]
        DIAG[DiagnosisAgent]
    end

    subgraph Data
        SQL1[(PatientIntake - CDC)]
        SQL2[(PatientMLDataset - Columnstore)]
        FSDB[(Feature Store - Parquet/Delta)]
    end

    subgraph Streaming
        KAFKA[Kafka]
        EH[Event Hub]
    end

    subgraph Observability
        OTEL[OpenTelemetry]
        PROM[Prometheus]
    end

    UI --> API1
    UI --> API2

    API1 --> ING --> VAL --> ENC --> PRIV --> FS
    FS --> TRAIN --> FED --> REG
    REG --> DIAG

    SQL1 -->|CDC| ING
    ING --> SQL2
    FS --> FSDB

    KAFKA --> ING
    EH --> ING

    API1 --> OTEL
    API2 --> OTEL
    OTEL --> PROM
```
---

### Tech Stack

|                  Service                |              Platform            |                Trigger               |                      Notes                    |
|:---------------------------------------:|:--------------------------------:|:------------------------------------:|:---------------------------------------------:|
|   Backend API (FastAPI)                 |   Railway                        |   Auto-deploy on push to main        |   Hosts API, pipeline, OpenTelemetry metrics  |
|   Frontend (React)                      |   Vercel                         |   cd "Web App" && npx vercel --prod  |   UI for diagnosis                            |
|   CDC Worker                            |   Railway Worker / Cron          |   Scheduled / always-on              |   Runs cdc_retrain_worker.py                  |
|   Streaming Consumers (Kafka/EventHub)  |   Railway Worker / Container     |   Always-on                          |   Real-time ingestion                         |
|   SQL Server                            |   Azure SQL / Railway / Docker   |   Managed                            |   Stores PatientIntake + PatientMLDataset     |
|   Feature Store (Delta/Parquet)         |   Local / S3 / ADLS              |   Mounted / cloud storage            |   Stores encoded features                     |
|   Prometheus                            |   Docker / Cloud VM              |   Always-on                          |   Scrapes OpenTelemetry metrics               |
|   Vault (Secrets)                       |   HashiCorp Cloud / Self-hosted  |   Always-on                          |   Secure DB credentials                       |


---

## Agent-Based Pipeline

|         Agent        |                   Role                  |
|:--------------------:|:---------------------------------------:|
|   IngestionAgent     |   Accepts data (API / SQL / streaming)  |
|   ValidationAgent    |   Ensures correctness                   |
|   EncodingAgent      |   Quantum feature encoding              |
|   PrivacyAgent       |   Removes PHI                           |
|   FeatureStoreAgent  |   Stores features                       |
|   TrainingAgent      |   Trains models                         |
|   FederatedAgent     |   Aggregates models                     |
|   RegistryAgent      |   Versioning                            |
|   DiagnosisAgent     |   Inference                             |

---

## Data Architecture

|         Table       |            Purpose          |
|:-------------------:|:---------------------------:|
|   PatientIntake     |   Rowstore + CDC ingestion  |
|   PatientMLDataset  |   Columnstore analytics     |


```mermaid
flowchart TD
    A[API / CSV / Streaming] --> B[PatientIntake]
    B -->|CDC| C[Worker]
    C --> D[Pipeline]
    D --> E[Feature Store]
    D --> F[PatientMLDataset]
```

## Dataset (Initial Seed Data)

**498 leptospirosis patients** from Kisumu County, Kenya (cleaned from 1,734 raw records). 

Features include:

- **17 binary symptoms**: fever, jaundice, vomiting, confusion, muscle pain, headache, chills, rigors, nausea, diarrhea, cough, bleeding, prostration, oliguria, anuria, conjunctival suffusion, muscle tenderness
- **7 continuous values**: heart rate, systolic BP, diastolic BP, age, sex, WBC count, platelet count


---

## CDC-Based Retraining

Automatically retrains when enough labeled data arrives:

```text
New labeled records ≥ threshold → retrain()
```

Run:

```bash
python mlops/cdc_retrain_worker.py
```

---

## Streaming Ingestion

Supports real-time pipelines:

Kafka

```bash
python streaming/kafka_patient_consumer.py
```

Azure Event Hub
```bash
python streaming/eventhub_patient_consumer.py
```

---

## Feature Store

Supports:
	•	✅ Parquet (local/dev)
	•	✅ Delta Lake (production)

Features
	•	ACID transactions
	•	Time travel
	•	Schema evolution
	•	Deduplication (patient_id + clinic_id)

```bash

FEATURE_STORE_MODE=delta
FEATURE_STORE_PATH=data/feature_store
```

---

## Security

	•	HashiCorp Vault integration
	•	No credentials stored in code

---

## Observability

Powered by:
    •    OpenTelemetry
    •    Prometheus

Metrics
|                Metric              |   Description  |
|:----------------------------------:|:--------------:|
|   quantumdx_requests_total         |   Requests     |
|   quantumdx_failures_total         |   Errors       |
|   quantumdx_operation_duration_ms  |   Latency      |
|   quantumdx_pipeline_inflight      |   Active ops   |
|   quantumdx_retrain_total          |   Retrains     |
|   quantumdx_diagnosis_total        |   Diagnoses    |


Prometheus Config
```yaml
scrape_configs:
  - job_name: "quantumdx"
    static_configs:
      - targets: ["localhost:9464"]
```
---

## API Endpoints

|   Method  |                 Endpoint               |    Description   |
|:---------:|:--------------------------------------:|:----------------:|
|   POST    |   /patients                            |   Add patient    |
|   POST    |   /diagnose                            |   Diagnose       |
|   POST    |   /patients/label                      |   Label          |
|   POST    |   /retrain                             |   Retrain        |
|   GET     |   /models/current                      |   Model info     |
|   GET     |   /feature-store/summary               |   Stats          |
|   POST    |   /patients/ingest-from-sql/{user_id}  |   SQL ingestion  |
|   GET     |   /metrics                             |   Prometheus     |
|   GET     |   /health                              |   Health         |


---

## Testing

Run all tests:
```bash

pytest
```
Coverage:
```bash

pytest --cov=agents --cov=observability --cov=mlops
```
---

## MLOps Capabilities

    •    ✅ Automated retraining (CDC)
    •    ✅ Feature store (Delta/Parquet)
    •    ✅ Model versioning
    •    ✅ Federated learning
    •    ✅ Streaming ingestion
    •    ✅ Observability
    •    ✅ CI-ready testing

---

## Getting Started
Install
```bash

pip install -r requirements.txt'
```
Run API
```bash

uvicorn api:app --reload
```
Load Data
```bash

python mlops/load_clean_csv_to_sql.py
```

Start CDC Worker
```bash

python mlops/cdc_retrain_worker.py
```
---

## Project Structure
```
QuantumDX/
├── api.py                         # FastAPI entrypoint (routes, startup, dependency wiring)

├── agents/                        # Core modular pipeline agents
│   ├── __init__.py                # Package exports
│   ├── base.py                    # AgentResult + shared base utilities
│   ├── pipeline.py                # QuantumDxPipeline orchestrator
│   ├── ingestion_agent.py         # Handles incoming patient data
│   ├── validation_agent.py        # Data validation + schema enforcement
│   ├── encoding_agent.py          # Quantum feature encoding
│   ├── privacy_agent.py           # PHI stripping / redaction
│   ├── feature_store_agent.py     # Parquet/Delta feature storage + dedup
│   ├── training_agent.py          # Model training logic
│   ├── federated_agent.py         # Aggregates models across clinics
│   ├── registry_agent.py          # Model versioning + persistence
│   ├── diagnosis_agent.py         # Inference logic
│   ├── vault_agent.py             # HashiCorp Vault integration
│   ├── sql_patient_data_agent.py  # SQL Server read access
│   ├── sql_ingestion_agent.py     # SQL → pipeline ingestion
│   └── evaluation_agent.py        # Model evaluation metrics

├── mlops/                         # Data pipeline + retraining automation
│   ├── load_clean_csv_to_sql.py   # Bulk loader into PatientIntake
│   └── cdc_retrain_worker.py      # CDC listener + retraining trigger

├── streaming/                     # Real-time ingestion consumers
│   ├── kafka_patient_consumer.py  # Kafka ingestion → pipeline
│   └── eventhub_patient_consumer.py # Azure Event Hub ingestion

├── observability/                 # Logging, metrics, tracing
│   ├── __init__.py                # Exports observability utilities
│   ├── logging_config.py          # JSON structured logging
│   ├── telemetry.py               # OpenTelemetry setup (Prometheus exporter)
│   └── decorators.py              # @monitored decorator for metrics/logging

├── tests/                         # Automated test suite (pytest)
│   ├── __init__.py                # Test package marker
│   ├── test_api.py                # API endpoint tests
│   ├── test_pipeline.py           # Pipeline orchestration tests
│   ├── test_sql_ingestion_agent.py # SQL ingestion tests
│   ├── test_observability.py      # Metrics + logging tests
│   └── test_cdc_worker_helpers.py # CDC helper logic tests

├── core/                          # Core ML + quantum logic
│   ├── __init__.py                # Package marker
│   ├── quantum_engine.py          # Quantum encoding implementation
│   └── aggregator.py              # Federated aggregation logic

├── utils/                         # Shared helpers (optional but recommended)
│   ├── __init__.py                # Package marker
│   ├── config.py                  # Environment + config loader
│   └── constants.py               # Shared constants/enums

├── scripts/                       # Utility scripts (optional)
│   └── seed_data.py               # Example data seeding script

├── main.py                        # Optional entrypoint (alternative to uvicorn CLI)

└── conftest.py                    # Shared pytest fixtures + mocks
```

---
## Deployment

|                  Service                |              Platform            |                Trigger               |                      Notes                    |
|:---------------------------------------:|:--------------------------------:|:------------------------------------:|:---------------------------------------------:|
|   Backend API (FastAPI)                 |   Railway                        |   Auto-deploy on push to main        |   Hosts API, pipeline, OpenTelemetry metrics  |
|   Frontend (React)                      |   Vercel                         |   cd "Web App" && npx vercel --prod  |   UI for diagnosis                            |
|   CDC Worker                            |   Railway Worker / Cron          |   Scheduled / always-on              |   Runs cdc_retrain_worker.py                  |
|   Streaming Consumers (Kafka/EventHub)  |   Railway Worker / Container     |   Always-on                          |   Real-time ingestion                         |
|   SQL Server                            |   Azure SQL / Railway / Docker   |   Managed                            |   Stores PatientIntake + PatientMLDataset     |
|   Feature Store (Delta/Parquet)         |   Local / S3 / ADLS              |   Mounted / cloud storage            |   Stores encoded features                     |
|   Prometheus                            |   Docker / Cloud VM              |   Always-on                          |   Scrapes OpenTelemetry metrics               |
|   Vault (Secrets)                       |   HashiCorp Cloud / Self-hosted  |   Always-on                          |   Secure DB credentials                       |

--

## What Changed

Before
	•	Quantum encoding demo
	•	Static ML model
	•	No pipeline

Now
	•	Full AI + data platform
	•	Agent-based architecture
	•	SQL + CDC ingestion
	•	Streaming ingestion
	•	Feature store (Delta Lake)
	•	Observability (OTel + Prometheus)
	•	Automated testing

---

<div align="center">

***Forked from https://github.com/MatthiasMasiero/H4H2026

*Quantum diagnostics for the communities that need them most.*

</div>
