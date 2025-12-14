import os
from core.rag.qa_chain import RAGBot
from utils.storage_factory import get_storage_backend


def ask_question(kb_id: str, question: str):
    # Get storage backend (S3 or local)
    storage = get_storage_backend()
    
    # Check if KB exists
    if not storage.kb_exists(kb_id):
        raise FileNotFoundError(f"Knowledge base '{kb_id}' not found")

    # Load KB and create RAG bot
    bot = RAGBot(kb_id, storage)
    answer, sources = bot.ask(question)

    return answer, sources

