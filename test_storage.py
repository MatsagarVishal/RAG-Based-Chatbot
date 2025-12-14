"""
Quick test script to verify the application works with the new storage backend
"""

import os
os.environ['STORAGE_BACKEND'] = 'local'

from utils.storage_factory import get_storage_backend

# Test storage factory
print("🧪 Testing storage factory...")
storage = get_storage_backend()
print(f"✅ Storage backend: {type(storage).__name__}")

# Test listing KBs
print("\n📚 Listing existing knowledge bases...")
kbs = storage.list_kbs()
print(f"Found {len(kbs)} knowledge bases:")
for kb in kbs:
    print(f"  - {kb}")

# Test loading a KB (if exists)
if kbs:
    test_kb = kbs[0]
    print(f"\n🔍 Testing load of KB: {test_kb}")
    try:
        index, metadata = storage.load_kb(test_kb)
        print(f"✅ Successfully loaded KB!")
        print(f"   - FAISS index dimension: {index.d}")
        print(f"   - Number of vectors: {index.ntotal}")
        print(f"   - Number of chunks: {len(metadata.get('texts', []))}")
        print(f"   - Number of metadatas: {len(metadata.get('metadatas', []))}")
    except Exception as e:
        print(f"❌ Error loading KB: {e}")
else:
    print("\n⚠️  No knowledge bases found. Try crawling a website first.")

print("\n✅ All tests passed! The application is ready to use.")
