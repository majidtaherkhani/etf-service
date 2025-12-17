from fastapi import HTTPException

class InvalidCsvColumnsException(HTTPException):
    """Raised when CSV is missing required columns"""
    def __init__(self, detail: str = "CSV must have 'name' and 'weight' columns"):
        super().__init__(status_code=400, detail=detail)
        self.error_code = "INVALID_CSV_COLS"

class NoPriceDataException(HTTPException):
    """Raised when no price data is found for the provided tickers"""
    def __init__(self, detail: str = "No price data found for these tickers"):
        super().__init__(status_code=404, detail=detail)
        self.error_code = "NO_DATA"

class NoMatchingTickerDataException(HTTPException):
    """Raised when no matching price data exists for the provided tickers"""
    def __init__(self, detail: str = "No matching price data for the provided tickers"):
        super().__init__(status_code=404, detail=detail)
        self.error_code = "NO_MATCHING_DATA"
