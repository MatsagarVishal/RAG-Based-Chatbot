import boto3
import pickle
import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import faiss


class S3Storage:
    """
    S3-based storage backend for FAISS indexes and metadata.
    Provides persistent storage for knowledge bases in AWS.
    """

    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket_name = os.getenv('S3_BUCKET_NAME')
        
        if not self.bucket_name:
            raise ValueError(
                "S3_BUCKET_NAME environment variable is required for S3 storage backend"
            )
        
        # Local cache directory
        self.cache_dir = Path("/tmp/rag_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_s3_key(self, kb_id: str, filename: str) -> str:
        """Generate S3 key for a file"""
        return f"{kb_id}/{filename}"

    def _get_cache_path(self, kb_id: str) -> Path:
        """Get local cache directory for a KB"""
        cache_path = self.cache_dir / kb_id
        cache_path.mkdir(parents=True, exist_ok=True)
        return cache_path

    def kb_exists(self, kb_id: str) -> bool:
        """Check if a knowledge base exists in S3"""
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=self._get_s3_key(kb_id, "faiss.index")
            )
            return True
        except:
            return False

    def save_kb(
        self,
        kb_id: str,
        faiss_index: Any,
        metadata: Dict,
        raw_pages: Optional[List[Dict]] = None
    ) -> None:
        """
        Save knowledge base to S3
        
        Args:
            kb_id: Unique identifier for the knowledge base
            faiss_index: FAISS index object
            metadata: Metadata dictionary (chunks, sources, etc.)
            raw_pages: Optional raw page data
        """
        cache_path = self._get_cache_path(kb_id)
        
        # Save FAISS index locally first
        index_path = cache_path / "faiss.index"
        faiss.write_index(faiss_index, str(index_path))
        
        # Upload FAISS index to S3
        self.s3_client.upload_file(
            str(index_path),
            self.bucket_name,
            self._get_s3_key(kb_id, "faiss.index")
        )
        print(f"✅ Uploaded FAISS index to S3: {kb_id}/faiss.index")
        
        # Save and upload metadata
        metadata_path = cache_path / "metadata.pkl"
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        
        self.s3_client.upload_file(
            str(metadata_path),
            self.bucket_name,
            self._get_s3_key(kb_id, "metadata.pkl")
        )
        print(f"✅ Uploaded metadata to S3: {kb_id}/metadata.pkl")
        
        # Save and upload raw pages if provided
        if raw_pages:
            raw_pages_path = cache_path / "raw_pages.json"
            with open(raw_pages_path, 'w', encoding='utf-8') as f:
                json.dump(raw_pages, f, indent=2)
            
            self.s3_client.upload_file(
                str(raw_pages_path),
                self.bucket_name,
                self._get_s3_key(kb_id, "raw_pages.json")
            )
            print(f"✅ Uploaded raw pages to S3: {kb_id}/raw_pages.json")

    def load_kb(self, kb_id: str) -> Tuple[Any, Dict]:
        """
        Load knowledge base from S3
        
        Args:
            kb_id: Unique identifier for the knowledge base
            
        Returns:
            Tuple of (faiss_index, metadata)
        """
        cache_path = self._get_cache_path(kb_id)
        
        # Download FAISS index
        index_path = cache_path / "faiss.index"
        if not index_path.exists():
            print(f"📥 Downloading FAISS index from S3: {kb_id}/faiss.index")
            self.s3_client.download_file(
                self.bucket_name,
                self._get_s3_key(kb_id, "faiss.index"),
                str(index_path)
            )
        
        # Download metadata
        metadata_path = cache_path / "metadata.pkl"
        if not metadata_path.exists():
            print(f"📥 Downloading metadata from S3: {kb_id}/metadata.pkl")
            self.s3_client.download_file(
                self.bucket_name,
                self._get_s3_key(kb_id, "metadata.pkl"),
                str(metadata_path)
            )
        
        # Load FAISS index
        faiss_index = faiss.read_index(str(index_path))
        
        # Load metadata
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        
        return faiss_index, metadata

    def list_kbs(self) -> List[str]:
        """List all knowledge bases in S3"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Delimiter='/'
            )
            
            kb_ids = []
            if 'CommonPrefixes' in response:
                for prefix in response['CommonPrefixes']:
                    kb_id = prefix['Prefix'].rstrip('/')
                    kb_ids.append(kb_id)
            
            return kb_ids
        except Exception as e:
            print(f"❌ Error listing KBs from S3: {e}")
            return []

    def delete_kb(self, kb_id: str) -> None:
        """Delete a knowledge base from S3"""
        try:
            # List all objects with the kb_id prefix
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=f"{kb_id}/"
            )
            
            if 'Contents' in response:
                # Delete all objects
                objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
                self.s3_client.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={'Objects': objects_to_delete}
                )
                print(f"✅ Deleted KB from S3: {kb_id}")
            
            # Clean up local cache
            cache_path = self._get_cache_path(kb_id)
            if cache_path.exists():
                import shutil
                shutil.rmtree(cache_path)
                
        except Exception as e:
            print(f"❌ Error deleting KB from S3: {e}")
            raise
