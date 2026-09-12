# ⚖️ LexiMini AI — Indian Legal Assistant Platform

<div align="center">

**An Enterprise-Grade, Domain-Specific AI Assistant for the Indian Legal System**

*Trained on 400+ Indian Laws • Bilingual (English + हिन्दी) • Hybrid RAG • Fine-Tuned & Distilled LLM*

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-DC2626?style=for-the-badge)](https://qdrant.tech)
[![GCP](https://img.shields.io/badge/GCP-Cloud_Run_%7C_GKE-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)](https://cloud.google.com)

</div>

---

## 📌 Overview

**LexiMini AI** is an AI legal assistant built specifically for Indian Law. Generic AI models often hallucinate legal section numbers or confuse old Indian Penal Code (IPC 1860) sections with the new statutory laws introduced in 2023–2024:
* **Bharatiya Nyaya Sanhita (BNS) 2023** (replaces IPC)
* **Bharatiya Nagarik Suraksha Sanhita (BNSS) 2023** (replaces CrPC)
* **Bharatiya Sakshya Adhiniyam (BSA) 2023** (replaces Evidence Act)

LexiMini AI solves this problem by combining a **Distilled Legal Language Model** with a **Hybrid Retrieval-Augmented Generation (RAG)** engine to deliver 100% accurate statutory citations, contract analysis, and automated legal drafting in both **English and Hindi (हिन्दी)**.

---

## ✨ Key Features & Functions

### 1. 💬 Bilingual Legal AI Assistant
* Answers legal queries in simple **English** and **Hindi (हिन्दी)**.
* Accurately cites act names, statutory sections, legal rights, and enforcement authorities.
* Eliminates section hallucinations by cross-verifying answers against verified statutory databases.

### 2. 📝 Automated Legal Document Drafting
* Instantly drafts common legal documents including:
  * Legal Notices & Cease and Desist Notices
  * Non-Disclosure Agreements (NDAs) & Rental Contracts
  * Employment Contracts & Service Agreements
  * Bail Applications & RTI Applications
* Customizes templates dynamically based on user input parameters.

### 3. 🔍 Contract Risk Scanner & Compliance Analysis
* Scans uploaded contracts (PDF / Text) for legal risks, missing protection clauses, and ambiguous terms.
* Highlights potential liabilities and checks compliance against active Indian statutes.
* Provides clear actionable advice and recommendations for contract negotiation.

### 4. ⚡ Hybrid RAG Engine (BM25 + Qdrant Vector Search)
* Combines **BM25 keyword search** (for exact statutory numbers) with **Qdrant dense vector embeddings** (for semantic concept matching).
* Includes an integrated **PDF/OCR Parser** for processing scanned legal notices and contracts.

### 5. 🔐 SaaS Multi-Tenant Authentication & Access Control
* **JWT Authentication** with password hashing (`bcrypt`).
* Supports **Role-Based Access Control (RBAC)**: Individual Users, Law Firms, and Company Admins.
* Guest Mode for public queries and trial access.

### 6. 📊 Real-Time Analytics Dashboard
* Tracks total chat queries, latency metrics, top legal categories, and active sessions.
* Interactive visual reporting for enterprise organization admins.

---

## 🏗️ System Architecture

LexiMini AI is built as a modular microservices architecture:

```
                      ┌────────────────────────────────────────┐
                      │          Web UI / Client Apps          │
                      │  • React (Vite) App  (Port 3000)       │
                      │  • Streamlit App     (Port 8501)       │
                      └───────────────────┬────────────────────┘
                                          │ HTTP / SSE
                                          ▼
                      ┌────────────────────────────────────────┐
                      │    FastAPI API Gateway  (Port 8000)    │
                      │  • JWT Auth & SaaS Session Management  │
                      │  • Redis Rate Limiting & User Caching │
                      │  • Real-Time SSE Streaming Router      │
                      └───────────┬────────────────┬───────────┘
                                  │                │
             ┌────────────────────┘                └────────────────────┐
             ▼                                                          ▼
┌───────────────────────────┐                              ┌───────────────────────────┐
│ Hybrid RAG Engine  :8001  │                              │ Model Server      :8002   │
│ • BM25 Keyword Search     │                              │ • Domain Fine-Tuned AI    │
│ • Qdrant Vector Search    │                              │ • OpenAI API Compatibility│
│ • PDF Parser & Chunker    │                              │ • Ollama / vLLM Connector │
│ • Document Risk & Draft   │                              └───────────────────────────┘
└────────────┬──────────────┘
             │
             ▼
┌───────────────────────────┐
│     Qdrant Vector DB      │
│  (400+ Indian Laws Engine)│
└───────────────────────────┘
```

---

## 🧠 Machine Learning & Training Pipeline

LexiMini AI uses a 4-step pipeline to fine-tune and distill legal intelligence into a lightweight model:

```
[400 Raw Indian Laws] ➔ [Data Prep Script] ➔ [3,800+ QA Pairs (Colab QLoRA)] ➔ [4B Gemma Model] ➔ [TPU Distillation] ➔ [1B GGUF Model (850 MB)]
```

1. **Data Augmentation (`scripts/prepare_data.py`)**:
   * Converts 400+ Indian statutory laws into 3,800+ multi-turn QA samples, Chain-of-Thought reasoning chains, and bilingual pairs (English + Hindi).
2. **QLoRA Fine-Tuning (`notebooks/leximini_colab.ipynb`)**:
   * Fine-tunes `google/gemma-4-E4B-it` on Google Colab (T4 GPU) using 4-bit quantization and LoRA.
3. **Logit Knowledge Distillation (`notebooks/leximini_distillation_kaggle.ipynb`)**:
   * Distills the 4B teacher model into a 1B student model using **Google Tunix** on Kaggle TPU v5e-8. Retains **90%+ accuracy** at 25% of the model size.
4. **Local Serving**:
   * Converts the model to GGUF format (`850 MB`) for fast inference on CPU/GPU via **Ollama** or **vLLM**.

---

## 🚀 Quick Start & How to Run

### Prerequisite Checklist
* **Python**: 3.10 or higher installed
* **Docker & Docker Compose**: (Optional, required for containerized setup)

---

### Option 1: 1-Click Local Demo (Zero Cost, No Docker Required)

Run the entire application locally with a single command:

```bash
make demo
```

This starts all services locally in demo mode:
* **Web UI (Streamlit)**: `http://localhost:8501`
* **API Gateway Docs**: `http://localhost:8000/docs`
* **RAG Engine Docs**: `http://localhost:8001/docs`
* **Model Server Docs**: `http://localhost:8002/docs`

---

### Option 2: Docker Microservices Stack

To run the complete production microservices stack with PostgreSQL, Redis, and Qdrant:

```bash
# 1. Build Docker containers
make build

# 2. Start all 7 services in the background
make up

# 3. Seed Qdrant vector database with Indian Legal Corpus
make seed

# 4. Run automated test suite
make test

# 5. Stop all services
make down
```

**Containers Started:**
* `leximini-postgres` (Port 5432) — User store and history
* `leximini-redis` (Port 6379) — Cache and rate limiting
* `leximini-qdrant` (Port 6333) — Vector database
* `leximini-rag-engine` (Port 8001) — Hybrid search service
* `leximini-model-server` (Port 8002) — Model inference service
* `leximini-gateway` (Port 8000) — FastAPI Gateway
* `leximini-web` (Port 8501) — Streamlit User Interface

---

### Option 3: Standalone Streamlit App

Run only the standalone desktop interface:

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 📁 Project Directory Structure

```
Leximini_AI/
├── app.py                      # Standalone Streamlit app
├── docker-compose.yml          # Full 7-service Docker setup
├── Makefile                    # Command shortcuts for developers
├── requirements.txt            # Python dependencies
│
├── apps/
│   └── web/                    # React (Vite) + Tailwind web application
│
├── services/
│   ├── gateway/                # FastAPI Gateway (Auth, SSE Streaming, Analytics)
│   ├── rag_engine/             # RAG Engine (BM25 + Qdrant, PDF Parser, Contract Risk)
│   └── model_server/           # Model Inference Server (Ollama / vLLM connector)
│
├── scripts/
│   ├── prepare_data.py         # Data preparation & sample generator
│   ├── seed_vector_db.py       # Qdrant legal corpus ingestion script
│   ├── demo_runner.py          # Local demo orchestrator script
│   └── deploy_cloud_run.sh     # GCP Cloud Run deployment script
│
├── notebooks/
│   ├── leximini_colab.ipynb              # QLoRA Fine-tuning notebook
│   └── leximini_distillation_kaggle.ipynb # TPU Distillation notebook
│
├── data/
│   └── indian_laws_2026.csv    # Indian Legal statutory dataset (400+ laws)
│
├── infrastructure/
│   └── terraform/              # Infrastructure-as-Code for GKE & Cloud SQL
│
├── mlops/                      # Legal accuracy benchmark evaluator
└── tests/                      # Pytest unit & integration test suite
```

---

## 🔌 Key API Endpoints Reference

### API Gateway (`http://localhost:8000`)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health status |
| `GET` | `/docs` | Interactive Swagger API documentation |
| `POST` | `/api/v1/auth/register` | Register a new user |
| `POST` | `/api/v1/auth/login` | Login and receive JWT token |
| `POST` | `/api/v1/chat/stream` | Real-time Server-Sent Events (SSE) chat stream |
| `POST` | `/api/v1/documents/upload` | Upload PDF legal document for indexing |
| `POST` | `/api/v1/contracts/analyze` | Analyze uploaded contract for risk and compliance |
| `POST` | `/api/v1/documents/draft` | Draft a new legal document (Notice, NDA, Contract) |
| `GET` | `/api/v1/analytics/dashboard` | Real-time query and usage analytics |

### RAG Engine (`http://localhost:8001`)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/search` | Perform hybrid BM25 + Qdrant vector legal search |
| `POST` | `/upload_pdf` | Parse PDF and extract legal text chunks |
| `POST` | `/analyze_contract` | Run statutory risk analysis on contract text |

---

## ⚙️ Configuration & Environment Variables

Create a `.env` file or use environment variables to customize settings:

```env
# Database & Cache
DATABASE_URL=postgresql+asyncpg://leximini:leximini_pass@localhost:5432/leximinidb
REDIS_URL=redis://localhost:6379/0

# Service Connections
GATEWAY_URL=http://localhost:8000
RAG_SERVICE_URL=http://localhost:8001
MODEL_SERVER_URL=http://localhost:8002

# Authentication
SECRET_KEY=your_secure_jwt_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Model Provider Choice (ollama / vllm / vertex / demo)
MODEL_PROVIDER=demo
```

---

## 🧪 Testing & Benchmark Evaluation

Run the automated test suite to verify all components:

```bash
# Run unit & integration tests
make test

# Run MLOps legal benchmark evaluation
make eval
```

**Test Coverage Includes:**
* JWT Authentication & User Session Management (`tests/test_gateway_auth.py`)
* SSE Chat Streaming API (`tests/test_gateway_chat.py`)
* Hybrid Search & Vector DB Ingestion (`tests/test_rag_engine.py`)
* OpenAI-Compatible Model Completion (`tests/test_model_server.py`)
* PDF Parsing & Document Chunking (`tests/test_pdf_parser.py`)

---

## ☁️ Cloud Deployment Guide

### Deploy to GCP Cloud Run (Serverless)

```bash
bash scripts/deploy_cloud_run.sh
```

### Deploy to GCP GKE (Kubernetes via Terraform)

```bash
cd infrastructure/terraform
terraform init
terraform apply
```

---

## 📋 Helpful Makefile Commands

| Command | Description |
|---|---|
| `make help` | Display all available make commands |
| `make demo` | Start 1-click local demo environment |
| `make build` | Build Docker images for all services |
| `make up` | Launch full stack using Docker Compose |
| `make down` | Stop and remove running containers |
| `make seed` | Ingest Indian Legal Corpus into Qdrant |
| `make test` | Run automated test suite using pytest |
| `make eval` | Run legal accuracy benchmark evaluation |
| `make clean` | Clean up temporary cache and build files |

---

## ⚖️ Disclaimer

LexiMini AI is created for **educational and informational purposes only**. It is not a substitute for professional legal advice from a licensed advocate or attorney.

---

<div align="center">

**LexiMini AI** — *Making Indian Law Accessible, Transparent, and Precise.*

</div>
