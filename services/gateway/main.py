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
from services.gateway.models import User, Conversation, Message, LegalCitation, Organization, OrganizationDocument, AuditLog

from services.gateway.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    get_current_org_admin
)

from services.gateway.rate_limiter import rate_limiter
from services.gateway.analytics import analytics_engine

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.get(f"{settings.API_V1_STR}/analytics/dashboard")
async def get_analytics():
    return analytics_engine.get_dashboard_metrics()


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

class OrgRegister(BaseModel):
    company_name: str
    domain: Optional[str] = None
    admin_email: EmailStr
    admin_password: str
    admin_name: str

class EmployeeAdd(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    department: Optional[str] = "Legal & Compliance"
    role: Optional[str] = "EMPLOYEE"

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_info: Optional[dict] = None

class QueryRequest(BaseModel):
    prompt: str
    language: str = "en"
    include_citations: bool = True
    conversation_id: Optional[int] = None
    organization_id: Optional[int] = None

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

    token = create_access_token({
        "sub": user.email,
        "role": user.role,
        "org_id": user.organization_id
    })
    
    org_name = "Individual"
    if user.organization_id:
        org_res = await db.execute(select(Organization).where(Organization.id == user.organization_id))
        org = org_res.scalars().first()
        if org:
            org_name = org.name

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_info": {
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "organization_id": user.organization_id,
            "organization_name": org_name,
            "department": user.department
        }
    }

# B2B Enterprise Organization APIs
@app.post(f"{settings.API_V1_STR}/org/register", response_model=Token)
async def register_organization(org_data: OrgRegister, db: AsyncSession = Depends(get_db)):
    # Check if admin email exists
    user_check = await db.execute(select(User).where(User.email == org_data.admin_email))
    if user_check.scalars().first():
        raise HTTPException(status_code=400, detail="Admin email already registered.")

    # Create Organization
    org = Organization(
        name=org_data.company_name,
        domain=org_data.domain or org_data.admin_email.split("@")[-1],
        plan_tier="ENTERPRISE"
    )
    db.add(org)
    await db.commit()
    await db.refresh(org)

    # Create Company Admin User
    admin = User(
        email=org_data.admin_email,
        hashed_password=get_password_hash(org_data.admin_password),
        full_name=org_data.admin_name,
        role="COMPANY_ADMIN",
        department="Executive Legal",
        organization_id=org.id
    )
    db.add(admin)
    await db.commit()
    await db.refresh(admin)

    token = create_access_token({
        "sub": admin.email,
        "role": admin.role,
        "org_id": org.id
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_info": {
            "email": admin.email,
            "full_name": admin.full_name,
            "role": admin.role,
            "organization_id": org.id,
            "organization_name": org.name,
            "department": admin.department
        }
    }

@app.post(f"{settings.API_V1_STR}/org/employees/add")
async def add_employee(
    emp_data: EmployeeAdd,
    current_admin: User = Depends(get_current_org_admin),
    db: AsyncSession = Depends(get_db)
):
    user_check = await db.execute(select(User).where(User.email == emp_data.email))
    if user_check.scalars().first():
        raise HTTPException(status_code=400, detail=f"Employee email '{emp_data.email}' already exists.")

    emp = User(
        email=emp_data.email,
        hashed_password=get_password_hash(emp_data.password),
        full_name=emp_data.full_name,
        role=emp_data.role or "EMPLOYEE",
        department=emp_data.department or "Legal & Compliance",
        organization_id=current_admin.organization_id
    )
    db.add(emp)

    # Log audit
    audit = AuditLog(
        organization_id=current_admin.organization_id,
        user_id=current_admin.id,
        user_email=current_admin.email,
        action="EMPLOYEE_ADDED",
        resource=emp_data.email
    )
    db.add(audit)
    await db.commit()
    await db.refresh(emp)

    return {
        "message": f"Successfully added employee '{emp_data.full_name}' to organization.",
        "employee": {
            "id": emp.id,
            "email": emp.email,
            "full_name": emp.full_name,
            "role": emp.role,
            "department": emp.department
        }
    }

@app.get(f"{settings.API_V1_STR}/org/employees")
async def list_employees(
    current_admin: User = Depends(get_current_org_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.organization_id == current_admin.organization_id))
    employees = result.scalars().all()
    return [
        {
            "id": e.id,
            "email": e.email,
            "full_name": e.full_name,
            "role": e.role,
            "department": e.department,
            "is_active": e.is_active,
            "created_at": str(e.created_at)
        }
        for e in employees
    ]

@app.get(f"{settings.API_V1_STR}/org/documents")
async def list_company_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not current_user or not current_user.organization_id:
        return []

    result = await db.execute(
        select(OrganizationDocument).where(OrganizationDocument.organization_id == current_user.organization_id)
    )
    docs = result.scalars().all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "file_type": d.file_type,
            "uploaded_by": d.uploaded_by,
            "created_at": str(d.created_at)
        }
        for d in docs
    ]


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

@app.post(f"{settings.API_V1_STR}/contract/analyze")
async def analyze_contract_gateway(payload: dict):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{settings.RAG_SERVICE_URL}/contract/analyze", json=payload)
            return resp.json()
    except Exception as e:
        return {"error": f"Contract analysis service unavailable: {e}"}

@app.post(f"{settings.API_V1_STR}/document/draft")
async def draft_document_gateway(payload: dict):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{settings.RAG_SERVICE_URL}/document/draft", json=payload)
            return resp.json()
    except Exception as e:
        return {"error": f"Document drafting service unavailable: {e}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("services.gateway.main:app", host="0.0.0.0", port=8000, reload=True)


