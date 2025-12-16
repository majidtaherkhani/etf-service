"""Test Firebase Storage connection"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from configs.objectstorage.firebase import get_storage_bucket

try:
    bucket = get_storage_bucket()
    list(bucket.list_blobs(max_results=1))
    print("Firebase Storage connection: SUCCESS")
    print(f"Bucket: {bucket.name}")
except Exception as e:
    print(f"Firebase Storage connection: FAILED - {e}")
    sys.exit(1)

