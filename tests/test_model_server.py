import pytest
from httpx import AsyncClient
from services.model_server.prompts import format_legal_prompt

@pytest.mark.asyncio
async def test_model_server_health(model_client: AsyncClient):
    response = await model_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "model_server"

@pytest.mark.asyncio
async def test_chat_completions_endpoint(model_client: AsyncClient):
    payload = {
        "model": "leximini-1b",
        "messages": [
            {"role": "user", "content": "What is Bharatiya Nyaya Sanhita?"}
        ],
        "stream": True
    }
    response = await model_client.post("/v1/chat/completions", json=payload)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")

def test_prompt_formatting():
    prompt = format_legal_prompt(query="Explain anticipatory bail under BNSS")
    assert "Bharatiya Nagarik Suraksha Sanhita" in prompt or "Indian law" in prompt
