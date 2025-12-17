import uuid
from fastapi import UploadFile
from configs.objectstorage.firebase import get_storage_bucket
from src.modules.storage.exceptions import InvalidUploadParametersException

class StorageService:
    def __init__(self):
        self.bucket = get_storage_bucket()

    async def upload(self, file: UploadFile = None, file_content: bytes = None, filename: str = None, content_type: str = None) -> str:
        if file:
            filename = file.filename
            content = await file.read()
            content_type = file.content_type
        elif file_content and filename:
            content = file_content
            if not content_type:
                content_type = "application/octet-stream"
        else:
            raise InvalidUploadParametersException()
        
        unique_name = f"{uuid.uuid4()}_{filename}"
        blob = self.bucket.blob(f"ETF/{unique_name}")
        
        blob.upload_from_string(
            content, 
            content_type=content_type
        )
        blob.make_public()
        
        return blob.public_url