from fastapi import APIRouter, HTTPException
from schemas.chat import ChatRequest, ChatResponse
from services.chat_service import ask_question

router = APIRouter(prefix="/api", tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
def chat_api(req: ChatRequest):
    try:
        answer, sources = ask_question(req.kb_id, req.question)
        return ChatResponse(answer=answer, sources=sources)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="KB not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
