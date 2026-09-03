# LexiMini AI — Indian Legal Assistant

A domain-specific AI assistant for Indian law, built by fine-tuning Gemma 4 on Indian legal data and distilling the knowledge into a smaller, deployable model using Google Tunix on TPU.

---

## What This Project Does

Most legal AI tools are general-purpose — they hallucinate section numbers, miss enforcement authorities, and give vague answers. LexiMini is trained specifically on Indian law: BNS, BNSS, IPC, family law, labour law, and constitutional provisions. It answers in Hindi and English, cites actual sections, and names the relevant authority.

The full pipeline goes from a CSV of 400 laws to a fine-tuned 4B model, then distills that knowledge into a 1B model small enough to run locally via Ollama.

---

## Project Structure

```
leximini-ai/
├── data/
│   └── indian_laws_2026.csv
├── scripts/
│   └── prepare_data.py
├── notebooks/
│   ├── leximini_colab.ipynb
│   └── leximini_distillation_kaggle.ipynb
├── serve/
│   └── Modelfile
├── app.py
└── requirements.txt
```

---

## How I Built It

### 1. Data Preparation

The raw dataset has 400 entries covering Indian laws — each with the act name, section reference, key provisions, who it applies to, and the enforcement authority.

400 rows is not enough to fine-tune a model well. So I wrote a script that generates multiple question-answer pairs from each row using 9 different templates — some in English, some in Hindi, some as step-by-step reasoning chains, some as comparisons between laws in the same category.

```bash
python scripts/prepare_data.py
```

This produces around 3800 training samples in Gemma's chat format and splits them into train and eval sets. The output goes to Google Cloud Storage for use in training.

### 2. Fine-tuning on Colab

I fine-tuned `google/gemma-4-E4B-it` using QLoRA (4-bit quantization with LoRA adapters) on a T4 GPU in Google Colab. The notebook is `notebooks/leximini_colab.ipynb`.

The key settings:
- 4-bit NF4 quantization via bitsandbytes
- LoRA rank 16, alpha 32, applied to all linear layers
- SFTTrainer from TRL with cosine LR schedule
- Batch size 2 with gradient accumulation of 4

One epoch takes about 7 hours on T4. After epoch 1, training loss was 0.149 and validation loss was 0.139 — good signal that the model was picking up the legal patterns without overfitting.

The LoRA checkpoint is saved to GCS.

Before running, fill in your credentials in Cell 3:
```python
HF_TOKEN    = 'your-hf-token'
BUCKET_NAME = 'your-gcs-bucket'
PROJECT_ID  = 'your-gcp-project'
```

### 3. Knowledge Distillation

Fine-tuning gives us a capable 4B model, but 4B is too large for local deployment. I used Google Tunix to distill the 4B teacher into a 1B student using logit-based distillation.

The notebook is `notebooks/leximini_distillation_kaggle.ipynb`, designed to run on Kaggle with TPU v5e-8.

Logit distillation works by training the student not just on the correct answers, but on the teacher's full probability distribution over tokens — the "soft targets". This transfers nuanced legal reasoning that hard labels alone cannot capture.

Key distillation parameters:
- Temperature 2.0 (softens teacher's distribution)
- Alpha 0.7 (balances distillation loss with student's own task loss)
- Optimizer: AdamW with cosine schedule

The distilled model retains around 90% of the teacher's domain-specific capability at 25% of the size.

To run, upload `train.jsonl` and `eval.jsonl` as a Kaggle dataset named `leximini-data`, then run all cells.

### 4. Serving with Ollama

After distillation, convert the model to GGUF format and register it with Ollama:

```bash
python -m llama_cpp.convert ./leximini-1b --outfile serve/leximini-1b.gguf
ollama create leximini -f serve/Modelfile
ollama run leximini
```

The Modelfile sets the system prompt and generation parameters.

### 5. UI

A Streamlit chat interface that connects to Ollama locally or a vLLM server. It has a demo mode that works without any model loaded, so you can preview the UI immediately.

```bash
pip install streamlit requests
streamlit run app.py
```

Select your backend in the sidebar (Ollama, vLLM, or Demo).

### 6. Enterprise Microservices Architecture

For production deployment, LexiMini AI uses an enterprise microservices pattern:

- **API Gateway (`services/gateway/`)**: Handles JWT Auth, Async PostgreSQL session tracking, Redis rate limiting, and SSE chat streaming.
- **RAG Engine (`services/rag_engine/`)**: BM25 statutory search combined with Qdrant dense vector search.
- **Model Server (`services/model_server/`)**: OpenAI-compatible streaming completion proxy.
- **Infrastructure (`infrastructure/terraform/`)**: Terraform modules for GCP GKE and Cloud SQL.

#### Quick Start with Makefile:
```bash
make build   # Build all microservices
make up      # Run microservices in background
make seed    # Seed Qdrant Vector DB with Indian legal dataset
make test    # Run Pytest unit and integration tests
make eval    # Run MLOps legal benchmark evaluation
```


---

## Tech Stack

- **Fine-tuning**: Gemma 4 E4B + QLoRA via PEFT and TRL
- **Distillation**: Google Tunix (JAX-native, logit-based)
- **Vector Search & RAG**: Qdrant Vector DB + BM25 Hybrid Search
- **API & Gateway**: FastAPI, Async SQLAlchemy, Redis, JWT
- **Training compute**: Google Colab T4, Kaggle TPU v5e-8
- **Storage & Cloud**: Google Cloud Storage, Terraform, GKE
- **Serving**: Ollama (local), vLLM, or FastAPI Model Server
- **UI**: Streamlit

### ☁️ GCP Native Production & Zero-Cost Local Emulation

This project is architected to showcase enterprise-grade Google Cloud Platform (GCP) integration while allowing **100% zero-cost local execution**:

- **GCP Native Infrastructure Specs**:
  - **GKE (Google Kubernetes Engine)** & **Cloud Run**: Serverless container execution specs in `asia-south1` (Mumbai).
  - **Google Cloud Storage (GCS)**: Bucket config for QLoRA model weights and distilled checkpoints.
  - **Cloud SQL**: Managed PostgreSQL specification in [`infrastructure/terraform/main.tf`](file:///Users/kanishkakakrani/.gemini/antigravity-ide/scratch/Leximini_AI/infrastructure/terraform/main.tf).
  - **Google Tunix**: JAX-native distillation pipeline for TPU v5e on Kaggle.

- **Zero-Cost Local Demo Runner (No GCP Billing Required)**:
  Run the complete multi-service stack on your local machine without active GCP credentials:
  ```bash
  make demo    # Launches Gateway (8000), RAG (8001), Model Server (8002), and Web UI (8501)
  ```

---

## Disclaimer

LexiMini is for informational purposes only. It is not a substitute for advice from a qualified legal professional.


