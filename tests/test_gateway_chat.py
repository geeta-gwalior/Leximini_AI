import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_gateway_health(gateway_client: AsyncClient):
    response = await gateway_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "gateway"

@pytest.mark.asyncio
async def test_gateway_root(gateway_client: AsyncClient):
    response = await gateway_client.get("/")
    assert response.status_code == 200
    assert "LexiMini AI Gateway" in response.json()["message"]

@pytest.mark.asyncio
async def test_chat_stream_endpoint(gateway_client: AsyncClient):
    payload = {
        "prompt": "What is Section 302 under Indian Penal Code?",
        "language": "en",
        "include_citations": True
    }
    response = await gateway_client.post("/api/v1/chat/stream", json=payload)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")
