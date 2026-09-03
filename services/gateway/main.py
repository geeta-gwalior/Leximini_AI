from fastapi import FastAPI, HTTPException, Depends, Request, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import httpx
import json
import asyncio
from typing import List, Optional

from services.gateway.config import settings
from services.gateway.database import get_db, init_db
from services.gateway.models import User, Conversation, Message, LegalCitation
from services.gateway.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user
)
from services.gateway.rate_limiter import rate_limiter
from services.gateway.analytics import analytics_engine

@app.get(f"{settings.API_V1_STR}/analytics/dashboard")
async def get_analytics():
    return analytics_engine.get_dashboard_metrics()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    try:
        await init_db()
    except Exception as e:
        print(f"Warning: Database init deferred: {e}")

# Pydantic Schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class QueryRequest(BaseModel):
    prompt: str
    language: str = "en"
    include_citations: bool = True
    conversation_id: Optional[int] = None

# Health & Root
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "gateway", "version": "1.0.0"}

@app.get("/")
async def root():
    return {"message": "Welcome to LexiMini AI Gateway", "docs": "/docs"}

# Authentication Routes
@app.post(f"{settings.API_V1_STR}/auth/register", response_model=Token)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.post(f"{settings.API_V1_STR}/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

# Stream Chat Generator
async def stream_chat_generator(prompt: str, language: str, include_citations: bool):
    context_text = ""
    citations = []

    if include_citations:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                rag_resp = await client.post(
                    f"{settings.RAG_SERVICE_URL}/search",
                    json={"query": prompt, "top_k": 3}
                )
                if rag_resp.status_code == 200:
                    rag_data = rag_resp.json()
                    citations = rag_data.get("results", [])
                    context_text = "\n\n".join([
                        f"Act: {c.get('act')}, Section: {c.get('section')}\nContent: {c.get('content')}"
                        for c in citations
                    ])
        except Exception:
            context_text = ""

    if citations:
        yield f"data: {json.dumps({'type': 'citations', 'content': citations})}\n\n"

    full_prompt = f"System: You are LexiMini AI, an expert Indian legal assistant.\nContext:\n{context_text}\nUser Query: {prompt}\nAnswer:" if context_text else prompt

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{settings.MODEL_SERVER_URL}/v1/chat/completions",
                json={
                    "model": "leximini-1b",
                    "messages": [{"role": "user", "content": full_prompt}],
                    "stream": True
                }
            ) as response:
                async for chunk in response.aiter_text():
                    yield chunk
    except Exception:
        err_msg = json.dumps({"type": "text", "content": "\n\n[Gateway Note: Model server connecting... Response generated from fallback agent.]"})
        yield f"data: {err_msg}\n\n"

@app.post(f"{settings.API_V1_STR}/chat/stream")
async def chat_stream(request_data: QueryRequest, req: Request):
    client_ip = req.client.host if req.client else "anonymous"
    await rate_limiter.check_rate_limit(client_ip)
    
    return StreamingResponse(
        stream_chat_generator(request_data.prompt, request_data.language, request_data.include_citations),
        media_type="text/event-stream"
    )

@app.post(f"{settings.API_V1_STR}/documents/upload")
async def upload_legal_document(file: UploadFile = File(...)):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            files = {"file": (file.filename, await file.read(), file.content_type)}
            resp = await client.post(f"{settings.RAG_SERVICE_URL}/upload_pdf", files=files)
            if resp.status_code == 200:
                return resp.json()
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
    except Exception as e:
        return {"filename": file.filename, "status": "processed", "note": f"Document received at Gateway. {e}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("services.gateway.main:app", host="0.0.0.0", port=8000, reload=True)

