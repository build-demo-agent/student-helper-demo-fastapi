from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import httpx, os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

AZURE_URL   = "https://student-helper-001-akqkg.swedencentral.inference.ml.azure.com/score"
API_KEY = os.getenv("API_KEY")
DEPLOYMENT  = "student-helper-001-akqkg-1"

class ChatReq(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatReq):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
        "azureml-model-deployment": DEPLOYMENT
    }
    body = { "chat_input": req.message }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:     # 30-second timeout
            resp = await client.post(AZURE_URL, headers=headers, json=body)
    except httpx.ReadTimeout:
        return {"answer": "Azure took too long. Please try again."}

    if resp.status_code != 200:
        return {"answer": f"Azure error {resp.status_code}: {resp.text}"}

    data = resp.json()
    return {"answer": data.get("chat_output", data)}
