import pickle
import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import faiss



class LocalStorage:
    """
    Local file system storage backend for FAISS indexes and metadata.
    Used for development and testing.
    """

    def __init__(self):
        self.storage_root = Path(os.getenv('STORAGE_ROOT', 'storage/data'))
        self.storage_root.mkdir(parents=True, exist_ok=True)

    def _get_kb_path(self, kb_id: str) -> Path:
        """Get directory path for a knowledge base"""
        kb_path = self.storage_root / kb_id
        kb_path.mkdir(parents=True, exist_ok=True)
        return kb_path

    def kb_exists(self, kb_id: str) -> bool:
        """Check if a knowledge base exists locally"""
        kb_path = self._get_kb_path(kb_id)
        return (kb_path / "faiss.index").exists()

    def save_kb(
        self,
        kb_id: str,
        faiss_index: Any,
        metadata: Dict,
        raw_pages: Optional[List[Dict]] = None
    ) -> None:
        """
        Save knowledge base to local file system
        
        Args:
            kb_id: Unique identifier for the knowledge base
            faiss_index: FAISS index object
            metadata: Metadata dictionary (chunks, sources, etc.)
            raw_pages: Optional raw page data
        """
        kb_path = self._get_kb_path(kb_id)
        
        # Save FAISS index
        index_path = kb_path / "faiss.index"
        faiss.write_index(faiss_index, str(index_path))
        print(f"✅ Saved FAISS index locally: {index_path}")
        
        # Save metadata
        metadata_path = kb_path / "metadata.pkl"
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        print(f"✅ Saved metadata locally: {metadata_path}")
        
        # Save raw pages if provided
        if raw_pages:
            raw_pages_path = kb_path / "raw_pages.json"
            with open(raw_pages_path, 'w', encoding='utf-8') as f:
                json.dump(raw_pages, f, indent=2)
            print(f"✅ Saved raw pages locally: {raw_pages_path}")

    def load_kb(self, kb_id: str) -> Tuple[Any, Dict]:
        """
        Load knowledge base from local file system
        
        Args:
            kb_id: Unique identifier for the knowledge base
            
        Returns:
            Tuple of (faiss_index, metadata)
        """
        kb_path = self._get_kb_path(kb_id)
        
        # Load FAISS index
        index_path = kb_path / "faiss.index"
        if not index_path.exists():
            raise FileNotFoundError(f"FAISS index not found: {index_path}")
        
        faiss_index = faiss.read_index(str(index_path))
        
        # Load metadata
        metadata_path = kb_path / "metadata.pkl"
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata not found: {metadata_path}")
        
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        
        # Handle legacy format (list of metadatas only)
        if isinstance(metadata, list):
            print(f"⚠️  Converting legacy KB format for '{kb_id}'...")
            # Try to load raw_pages to reconstruct texts
            raw_pages_path = kb_path / "raw_pages.json"
            if raw_pages_path.exists():
                with open(raw_pages_path, 'r', encoding='utf-8') as f:
                    raw_pages = json.load(f)
                
                # Reconstruct texts from raw pages (approximate)
                # This is a best-effort conversion
                texts = []
                for page in raw_pages:
                    text = page.get("text", "")
                    if text:
                        # Simple chunking to match original
                        from langchain_text_splitters import RecursiveCharacterTextSplitter
                        splitter = RecursiveCharacterTextSplitter(
                            chunk_size=600,
                            chunk_overlap=100
                        )
                        chunks = splitter.split_text(text)
                        texts.extend(chunks)
                
                metadata = {
                    "texts": texts,
                    "metadatas": metadata  # The list we loaded
                }
                
                # Save in new format
                with open(metadata_path, 'wb') as f:
                    pickle.dump(metadata, f)
                print(f"✅ Converted and saved KB '{kb_id}' in new format")
            else:
                raise ValueError(
                    f"Legacy KB '{kb_id}' detected but cannot convert (missing raw_pages.json). "
                    "Please re-crawl the website."
                )
        
        return faiss_index, metadata

    def list_kbs(self) -> List[str]:
        """List all knowledge bases in local storage"""
        if not self.storage_root.exists():
            return []
        
        kb_ids = []
        for kb_dir in self.storage_root.iterdir():
            if kb_dir.is_dir() and (kb_dir / "faiss.index").exists():
                kb_ids.append(kb_dir.name)
        
        return kb_ids

    def delete_kb(self, kb_id: str) -> None:
        """Delete a knowledge base from local storage"""
        kb_path = self._get_kb_path(kb_id)
        if kb_path.exists():
            import shutil
            shutil.rmtree(kb_path)
            print(f"✅ Deleted KB locally: {kb_id}")
