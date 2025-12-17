from fastapi import HTTPException

class InvalidCsvFormatException(HTTPException):
    """Raised when CSV file format is invalid"""
    def __init__(self, detail: str = "Invalid CSV format"):
        super().__init__(status_code=400, detail=detail)
        self.error_code = "INVALID_FILE"
