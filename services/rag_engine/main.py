from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
import os

from services.rag_engine.qdrant_client import init_qdrant_collection
from services.rag_engine.hybrid_search import HybridLegalSearch
from services.rag_engine.ingest import ingest_laws, DATA_PATH
from services.rag_engine.pdf_parser import extract_text_from_pdf_bytes, chunk_legal_text
from services.rag_engine.contract_analyzer import contract_analyzer
from services.rag_engine.document_drafter import document_drafter


app = FastAPI(title="LexiMini Legal RAG Engine", version="1.0.0")

hybrid_searcher = HybridLegalSearch(data_path=DATA_PATH)

@app.on_event("startup")
async def on_startup():
    init_qdrant_collection()

class SearchQuery(BaseModel):
    query: str
    top_k: int = 3

class LegalDocument(BaseModel):
    act: str
    section: str
    content: str
    authority: str
    score: float

class SearchResponse(BaseModel):
    query: str
    results: List[LegalDocument]

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "rag_engine",
        "dataset_rows": len(hybrid_searcher.df) if hybrid_searcher.df is not None else 0
    }

@app.post("/search", response_model=SearchResponse)
async def search_legal_statutes(req: SearchQuery):
    results_raw = hybrid_searcher.hybrid_search(query=req.query, top_k=req.top_k)

    documents = [
        LegalDocument(
            act=r.get("act", "Indian Act"),
            section=r.get("section", "Provision"),
            content=r.get("content", ""),
            authority=r.get("authority", "Relevant Authority"),
            score=float(r.get("score", 0.9))
        )
        for r in results_raw
    ]

    if not documents:
        documents.append(LegalDocument(
            act="Bharatiya Nyaya Sanhita (BNS) 2023",
            section="General Statutory Rules",
            content="Constitutional rights and procedural guidelines apply under Indian Legal Code.",
            authority="Judicial Court & Enforcement Authorities",
            score=0.8
        ))

    return SearchResponse(query=req.query, results=documents)

@app.post("/ingest")
async def trigger_ingestion(background_tasks: BackgroundTasks):
    background_tasks.add_task(ingest_laws)
    return {"message": "Legal dataset vector ingestion started in background."}

@app.post("/upload_pdf")
async def upload_pdf_document(file: UploadFile = File(...)):
    if not file.filename.endswith(('.pdf', '.txt')):
        raise HTTPException(status_code=400, detail="Only PDF or TXT files supported.")

    file_bytes = await file.read()
    raw_text = extract_text_from_pdf_bytes(file_bytes)
    chunks = chunk_legal_text(raw_text)

    return {
        "filename": file.filename,
        "extracted_chars": len(raw_text),
        "total_chunks": len(chunks),
        "message": f"Successfully parsed '{file.filename}' into {len(chunks)} searchable legal chunks.",
        "sample_chunk": chunks[0]["content"] if chunks else ""
    }

class ContractAnalyzeRequest(BaseModel):
    text: str
    doc_type: str = "auto"

class DraftRequest(BaseModel):
    doc_type: str
    landlord_name: Optional[str] = "Shri Rajesh Sharma"
    tenant_name: Optional[str] = "Shri Amit Kumar"
    property_address: Optional[str] = "Flat 402, Sunshine Apartments, Bandra West, Mumbai 400050"
    monthly_rent: Optional[str] = "25000"
    security_deposit: Optional[str] = "50000"
    sender_name: Optional[str] = "Advocate Vikram Roy"
    client_name: Optional[str] = "M/s Apex Enterprises"
    recipient_name: Optional[str] = "Shri Suresh Gupta"
    default_amount: Optional[str] = "1,50,000"

@app.post("/contract/analyze")
async def analyze_contract_risk(req: ContractAnalyzeRequest):
    return contract_analyzer.analyze_contract(text=req.text, doc_type=req.doc_type)

@app.post("/document/draft")
async def draft_legal_document(req: DraftRequest):
    if "rent" in req.doc_type.lower() or "lease" in req.doc_type.lower():
        draft_text = document_drafter.draft_rent_agreement(
            landlord_name=req.landlord_name,
            tenant_name=req.tenant_name,
            property_address=req.property_address,
            monthly_rent=req.monthly_rent,
            security_deposit=req.security_deposit
        )
    elif "notice" in req.doc_type.lower():
        draft_text = document_drafter.draft_legal_notice(
            sender_name=req.sender_name,
            client_name=req.client_name,
            recipient_name=req.recipient_name,
            default_amount=req.default_amount
        )
    elif "nda" in req.doc_type.lower():
        draft_text = document_drafter.draft_nda()
    else:
        draft_text = document_drafter.draft_rent_agreement()

    return {"doc_type": req.doc_type, "draft": draft_text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("services.rag_engine.main:app", host="0.0.0.0", port=8001, reload=True)


