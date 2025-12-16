import firebase_admin
from firebase_admin import credentials, storage
import os
from dotenv import load_dotenv

load_dotenv()

cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'bmo-etf.firebasestorage.app'
    })

bucket = storage.bucket()


def get_storage_bucket():
    """Get Firebase Storage bucket"""
    return bucket

