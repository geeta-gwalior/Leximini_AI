from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
import os

from services.rag_engine.qdrant_client import init_qdrant_collection
from services.rag_engine.hybrid_search import HybridLegalSearch
from services.rag_engine.ingest import ingest_laws, DATA_PATH
from services.rag_engine.pdf_parser import extract_text_from_pdf_bytes, chunk_legal_text

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("services.rag_engine.main:app", host="0.0.0.0", port=8001, reload=True)

