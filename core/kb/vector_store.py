import faiss
import pickle
import os


def load_faiss_index(kb_dir: str):
    """
    Loads FAISS index and metadata for querying
    """
    index_path = os.path.join(kb_dir, "faiss.index")
    meta_path = os.path.join(kb_dir, "metadata.pkl")

    if not os.path.exists(index_path):
        raise FileNotFoundError("FAISS index not found")

    if not os.path.exists(meta_path):
        raise FileNotFoundError("Metadata file not found")

    index = faiss.read_index(index_path)

    with open(meta_path, "rb") as f:
        data = pickle.load(f)

    # Handle legacy format where only metadatas list was saved
    if isinstance(data, list):
        raise ValueError("Legacy Knowledge Base detected. Please re-crawl the website to update the data structure.")

    return index, data
