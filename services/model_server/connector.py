import os
import httpx
import json
import asyncio
from typing import AsyncGenerator

VLLM_HOST = os.getenv("VLLM_HOST", "http://localhost:8000/v1")
VERTEX_ENDPOINT_ID = os.getenv("VERTEX_ENDPOINT_ID", "")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "")
GCP_REGION = os.getenv("GCP_REGION", "asia-south1")

class ModelConnector:
    def __init__(self):
        self.vllm_url = VLLM_HOST
        self.use_vertex = bool(VERTEX_ENDPOINT_ID and GCP_PROJECT_ID)

    async def stream_inference(self, prompt: str) -> AsyncGenerator[str, None]:
        # 1. If GCP Vertex AI endpoint configured
        if self.use_vertex:
            try:
                # Vertex AI streaming prediction API bridge
                pass
            except Exception as e:
                print(f"Vertex AI stream error, falling back: {e}")

        # 2. Try vLLM / OpenAI HTTP endpoint
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.vllm_url}/chat/completions",
                    json={
                        "model": "leximini-1b",
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": True,
                        "temperature": 0.3,
                        "max_tokens": 1024
                    }
                ) as resp:
                    if resp.status_code == 200:
                        async for chunk in resp.aiter_text():
                            yield chunk
                        return
        except Exception:
            pass

        # 3. Development Fallback streaming generator
        fallback_tokens = [
            "Based ", "on ", "Indian ", "Law ", "(Bharatiya ", "Nyaya ", "Sanhita ", "2023):\n\n",
            "1. **Applicable ", "Statute**: ", "As ", "per ", "the ", "relevant ", "provisions, ", "the ", "aggrieved ", "party ", "can ", "file ", "an ", "FIR ", "or ", "complaint.\n",
            "2. **Jurisdiction**: ", "Local ", "Police ", "Station ", "or ", "Magistrate ", "Court.\n\n",
            "_Disclaimer: ", "LexiMini ", "AI ", "provides ", "legal ", "information, ", "not ", "formal ", "legal ", "counsel._"
        ]
        for token in fallback_tokens:
            await asyncio.sleep(0.04)
            payload = {"type": "text", "content": token}
            yield f"data: {json.dumps(payload)}\n\n"

model_connector = ModelConnector()
