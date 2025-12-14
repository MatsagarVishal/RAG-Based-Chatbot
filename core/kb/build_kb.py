import json
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .vector_store import save_faiss_index


def load_crawled_data(raw_pages_path: str):
    with open(raw_pages_path, "r", encoding="utf-8") as f:
        return json.load(f)


def prepare_documents(pages):
    documents = []
    for page in pages:
        combined_text = f"""
Title: {page.get('title', '')}
Headings: {' '.join(page.get('headings', []))}
Content: {page.get('text', '')}
"""
        documents.append(
            {
                "text": combined_text,
                "source": page.get("url", "")
            }
        )
    return documents


def build_knowledge_base(raw_pages_path: str, output_dir: str):
    """
    Builds FAISS knowledge base from crawled pages.
    """

    pages = load_crawled_data(raw_pages_path)

    # ✅ Guard 1: No pages at all
    if not pages:
        raise ValueError("No pages crawled. Knowledge base not created.")

    docs = prepare_documents(pages)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100
    )

    chunks = []
    metadatas = []

    for doc in docs:
        split_texts = splitter.split_text(doc["text"])
        for chunk in split_texts:
            # Optional: skip very small chunks
            if len(chunk.strip()) < 200:
                continue
            chunks.append(chunk)
            metadatas.append({"source": doc["source"]})

    # ✅ Guard 2: No usable text
    if not chunks:
        raise ValueError("No meaningful text extracted. Knowledge base not created.")

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks, show_progress_bar=False)

    save_faiss_index(
        embeddings=embeddings,
        texts=chunks,
        metadatas=metadatas,
        output_dir=output_dir
    )

    return len(chunks)
