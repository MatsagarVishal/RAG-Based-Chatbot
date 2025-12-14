import os


def kb_exists(kb_dir: str) -> bool:
    index_path = os.path.join(kb_dir, "faiss.index")
    meta_path = os.path.join(kb_dir, "metadata.pkl")

    return os.path.exists(index_path) and os.path.exists(meta_path)
