import pytest
from httpx import AsyncClient
from services.rag_engine.hybrid_search import HybridLegalSearch
import os

@pytest.mark.asyncio
async def test_rag_health(rag_client: AsyncClient):
    response = await rag_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "rag_engine"

@pytest.mark.asyncio
async def test_rag_search_endpoint(rag_client: AsyncClient):
    query_payload = {
        "query": "BNS Section for bail conditions",
        "top_k": 2
    }
    response = await rag_client.post("/search", json=query_payload)
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) > 0
    first_result = data["results"][0]
    assert "act" in first_result
    assert "section" in first_result

def test_hybrid_search_bm25_fallback():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "indian_laws_2026.csv")
    searcher = HybridLegalSearch(data_path=data_path)
    if searcher.df is not None and not searcher.df.empty:
        results = searcher.search_bm25(query="murder penalty", top_k=2)
        assert isinstance(results, list)
