# app.py
from fastapi import FastAPI
from pydantic import BaseModel
from agent import agent_chat
import uvicorn

app = FastAPI(title="智能客服API")

class ChatRequest(BaseModel):
    conversation_id: str
    query: str

class ChatResponse(BaseModel):
    conversation_id: str
    answer: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    answer = agent_chat(request.conversation_id, request.query)
    return ChatResponse(conversation_id=request.conversation_id, answer=answer)

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)