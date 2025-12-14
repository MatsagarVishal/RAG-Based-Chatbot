import os
from core.rag.qa_chain import RAGBot


def ask_question(kb_id: str, question: str):
    kb_dir = f"storage/data/{kb_id}"

    if not os.path.exists(kb_dir):
        raise FileNotFoundError("Knowledge base not found")

    bot = RAGBot(kb_dir)
    answer, sources = bot.ask(question)

    return answer, sources
