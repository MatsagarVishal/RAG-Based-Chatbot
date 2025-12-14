from fastapi import APIRouter
from schemas.crawl import CrawlRequest, CrawlResponse
from services.crawl_service import crawl_and_build_kb

router = APIRouter(prefix="/api", tags=["Crawl"])


@router.post("/crawl", response_model=CrawlResponse)
def crawl_website_api(req: CrawlRequest):
    result = crawl_and_build_kb(req.url)
    return result
