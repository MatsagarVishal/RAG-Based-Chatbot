import os
from typing import Union
from core.storage.s3_storage import S3Storage
from core.storage.local_storage import LocalStorage


def get_storage_backend() -> Union[S3Storage, LocalStorage]:
    """
    Factory function to get the appropriate storage backend based on environment.
    
    Returns:
        S3Storage or LocalStorage instance based on STORAGE_BACKEND env var
    """
    backend = os.getenv('STORAGE_BACKEND', 'local').lower()
    
    if backend == 's3':
        print("🌐 Using S3 storage backend")
        return S3Storage()
    else:
        print("💾 Using local storage backend")
        return LocalStorage()
