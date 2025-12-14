from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from api.routes.crawl import router as crawl_router
from api.routes.chat import router as chat_router
from fastapi.middleware.cors import CORSMiddleware
from api.routes.kb_update import router as kb_update_router

app = FastAPI(title="RAG Headless Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

app.include_router(crawl_router)
app.include_router(chat_router)
app.include_router(kb_update_router)

@app.get("/health")
def health():
    return {"status": "ok"}
