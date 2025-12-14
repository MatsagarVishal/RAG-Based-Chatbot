from pydantic import BaseModel, HttpUrl
from typing import Optional


class CrawlRequest(BaseModel):
    url: HttpUrl


class CrawlResponse(BaseModel):
    status: str
    kb_id: str

    pages_crawled: Optional[int] = None
    chunks_created: Optional[int] = None
    reason: Optional[str] = None
    message: Optional[str] = None
