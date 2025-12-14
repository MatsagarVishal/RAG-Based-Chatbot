import os
from pathlib import Path


def get_storage_root():
    """Get the root directory for storage based on environment"""
    return os.getenv("STORAGE_ROOT", "storage/data")


def ensure_storage_dir(kb_id: str) -> Path:
    """Ensure storage directory exists for a given kb_id"""
    storage_root = Path(get_storage_root())
    kb_dir = storage_root / kb_id
    kb_dir.mkdir(parents=True, exist_ok=True)
    return kb_dir
