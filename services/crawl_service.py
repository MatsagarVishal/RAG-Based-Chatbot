import os
import json
import shutil
import pickle

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.crawler.playwright_crawler import crawl_website_playwright as crawl_website
from utils.url_hash import generate_kb_id
from utils.kb_exists import kb_exists


def crawl_and_build_kb(url, force_refresh: bool = False):
    url_str = str(url)
    kb_id = generate_kb_id(url_str)
    base_path = f"storage/data/{kb_id}"

    # 🔁 Force refresh
    if force_refresh and os.path.exists(base_path):
        shutil.rmtree(base_path)

    os.makedirs(base_path, exist_ok=True)

    # ♻️ Reuse KB
    if not force_refresh and kb_exists(base_path):
        return {
            "status": "exists",
            "kb_id": kb_id,
            "message": "Knowledge base already exists. Reusing cached data."
        }

    # ----------------------------
    # 🔥 Streaming KB components
    # ----------------------------
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100
    )

    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    faiss_index = None
    metadatas = []
    texts = []
    total_chunks = 0

    # 1️⃣ Crawl website (already optimized & parallel)
    pages = crawl_website(url_str, max_depth=2)

    if not pages:
        return {
            "status": "failed",
            "kb_id": kb_id,
            "reason": "No pages could be crawled from the given URL."
        }

    # 2️⃣ Process pages immediately
    for page in pages:
        text = page.get("text", "")
        url = page.get("url", "")

        if not text or len(text) < 400:
            continue

        chunks = splitter.split_text(text)
        if not chunks:
            continue

        embeddings = embedder.encode(chunks, show_progress_bar=False)
        embeddings = np.array(embeddings).astype("float32")

        # Lazy FAISS init
        if faiss_index is None:
            dim = embeddings.shape[1]
            faiss_index = faiss.IndexFlatL2(dim)

        faiss_index.add(embeddings)

        for chunk in chunks:
            metadatas.append({"source": url})
            texts.append(chunk)

        total_chunks += len(chunks)

    # ❌ No usable content
    if faiss_index is None or total_chunks == 0:
        return {
            "status": "failed",
            "kb_id": kb_id,
            "reason": "Crawled pages but no meaningful text was found."
        }

    # 3️⃣ Persist FAISS + metadata
    faiss.write_index(faiss_index, f"{base_path}/faiss.index")

    with open(f"{base_path}/metadata.pkl", "wb") as f:
        pickle.dump({"texts": texts, "metadatas": metadatas}, f)

    # Optional: keep raw crawl for debugging
    with open(f"{base_path}/raw_pages.json", "w", encoding="utf-8") as f:
        json.dump(pages, f, indent=2, ensure_ascii=False)

    return {
        "status": "success",
        "kb_id": kb_id,
        "pages_crawled": len(pages),
        "chunks_created": total_chunks
    }


def update_knowledge_base(url):
    """
    Force refresh KB for an existing website
    """
    return crawl_and_build_kb(
        url=url,
        force_refresh=True
    )
