import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator

from services.gateway.main import app as gateway_app
from services.gateway.database import Base, get_db
from services.gateway.auth import create_access_token
from services.rag_engine.main import app as rag_app
from services.model_server.main import app as model_app

# In-memory SQLite async engine for unit testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)
AsyncSessionTest = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionTest() as session:
        yield session

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def gateway_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def _override_get_db():
        yield db_session

    gateway_app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=gateway_app)
    async with AsyncClient(transport=transport, base_url="http://testgateway") as client:
        yield client
    gateway_app.dependency_overrides.clear()

@pytest.fixture
async def rag_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=rag_app)
    async with AsyncClient(transport=transport, base_url="http://testrag") as client:
        yield client

@pytest.fixture
async def model_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=model_app)
    async with AsyncClient(transport=transport, base_url="http://testmodel") as client:
        yield client

@pytest.fixture
def auth_headers() -> dict:
    token = create_access_token({"sub": "testlawyer@leximini.in"})
    return {"Authorization": f"Bearer {token}"}
