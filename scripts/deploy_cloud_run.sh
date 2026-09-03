#!/usr/bin/env bash
# LexiMini AI — Automated GCP Cloud Run Serverless Deployer

set -e

PROJECT_ID=${GCP_PROJECT_ID:-"leximini-ai-project"}
REGION=${GCP_REGION:-"asia-south1"} # Mumbai region for low latency in India
REGISTRY="gcr.io/${PROJECT_ID}"

echo "========================================================="
echo "   🚀 LexiMini AI — GCP Cloud Run Deployment Automation  "
echo "========================================================="
echo "Project ID: ${PROJECT_ID}"
echo "Region:     ${REGION}"
echo ""

# 1. Build & Push Gateway Image
echo "[1/3] Building & Pushing API Gateway Container..."
docker build -t ${REGISTRY}/leximini-gateway:latest -f services/gateway/Dockerfile .
# docker push ${REGISTRY}/leximini-gateway:latest
# gcloud run deploy leximini-gateway --image ${REGISTRY}/leximini-gateway:latest --region ${REGION} --platform managed --allow-unauthenticated

# 2. Build & Push RAG Engine Image
echo "[2/3] Building & Pushing RAG Engine Container..."
docker build -t ${REGISTRY}/leximini-rag-engine:latest -f services/rag_engine/Dockerfile .
# docker push ${REGISTRY}/leximini-rag-engine:latest
# gcloud run deploy leximini-rag-engine --image ${REGISTRY}/leximini-rag-engine:latest --region ${REGION} --platform managed --no-allow-unauthenticated

# 3. Build & Push Web App Container
echo "[3/3] Building & Pushing Web App Container..."
docker build -t ${REGISTRY}/leximini-web:latest -f apps/web/Dockerfile .
# docker push ${REGISTRY}/leximini-web:latest
# gcloud run deploy leximini-web --image ${REGISTRY}/leximini-web:latest --region ${REGION} --platform managed --allow-unauthenticated

echo ""
echo "========================================================="
echo "   [Success] Cloud Run Deployment Scripts Prepared!     "
echo "========================================================="
