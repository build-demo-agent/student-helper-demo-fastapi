from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict
import httpx, os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

AZURE_URL   = "https://student-helper-dev-001.swedencentral.inference.ml.azure.com/score"
API_KEY     = os.getenv("API_KEY")
DEPLOYMENT  = "student-helper-dev-001-3"

# --- Data Models ---

class ChatTurn(BaseModel):
    inputs: Dict[str, str]
    outputs: Optional[Dict[str, str]] = None

class ChatReq(BaseModel):
    message: str
    chat_history: List[ChatTurn]

# --- Main Chat Endpoint ---

@app.post("/chat")
async def chat(req: ChatReq):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
        "azureml-model-deployment": DEPLOYMENT
    }

    body = {
        "chat_input": req.message,
        "chat_history": [turn.dict() for turn in req.chat_history]
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(AZURE_URL, headers=headers, json=body)
    except httpx.ReadTimeout:
        return {"answer": "Azure took too long. Please try again."}

    if resp.status_code != 200:
        return {"answer": f"Azure error {resp.status_code}: {resp.text}"}

    data = resp.json()
    return {"answer": data.get("chat_output", data)}
