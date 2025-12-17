from fastapi import HTTPException

class InvalidUploadParametersException(HTTPException):
    """Raised when upload parameters are invalid"""
    def __init__(self, detail: str = "Either 'file' or both 'file_content' and 'filename' must be provided"):
        super().__init__(status_code=400, detail=detail)
        self.error_code = "INVALID_UPLOAD_PARAMS"
