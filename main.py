from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_chatBot import ask_garden_bot

app = FastAPI(title="GreenAI Plant Assistant")

origins = [
    "http://127.0.0.1:5500",   # your static HTML origin
    "http://localhost:5173",   # optional, if you also use Vite later
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,     # or ["*"] while testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
