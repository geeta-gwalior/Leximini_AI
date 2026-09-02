from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import json

from services.model_server.connector import model_connector
from services.model_server.prompts import format_legal_prompt

app = FastAPI(title="LexiMini AI Model Serving Engine", version="1.0.0")

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "leximini-1b"
    messages: List[Message]
    stream: bool = True

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "model_server",
        "vertex_enabled": model_connector.use_vertex,
        "vllm_url": model_connector.vllm_url
    }

@app.post("/v1/chat/completions")
async def chat_completions(req: ChatCompletionRequest):
    last_user_msg = req.messages[-1].content if req.messages else ""
    formatted_prompt = format_legal_prompt(query=last_user_msg)

    return StreamingResponse(
        model_connector.stream_inference(prompt=formatted_prompt),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("services.model_server.main:app", host="0.0.0.0", port=8002, reload=True)
