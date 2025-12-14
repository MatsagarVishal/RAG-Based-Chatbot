from pydantic import BaseModel, HttpUrl
from typing import Optional


class KBUpdateRequest(BaseModel):
    url: HttpUrl


class KBUpdateResponse(BaseModel):
    status: str
    kb_id: str

    pages_crawled: Optional[int] = None
    chunks_created: Optional[int] = None
    reason: Optional[str] = None
