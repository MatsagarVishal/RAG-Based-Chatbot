from fastapi import APIRouter
from schemas.kb_update import KBUpdateRequest, KBUpdateResponse
from services.crawl_service import update_knowledge_base

router = APIRouter(prefix="/api/kb", tags=["Knowledge Base"])


@router.post("/update", response_model=KBUpdateResponse)
def update_kb_api(req: KBUpdateRequest):
    return update_knowledge_base(req.url)
