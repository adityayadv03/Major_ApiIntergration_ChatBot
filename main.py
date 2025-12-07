from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_chatBot import ask_garden_bot

app = FastAPI(title="GreenAI Plant Assistant")

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    answer = ask_garden_bot(req.message)
    return ChatResponse(reply=answer)
