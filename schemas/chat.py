from pydantic import BaseModel


class ChatRequest(BaseModel):
    kb_id: str
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
