from pydantic import BaseModel
from typing import List

class TimeSeriesPoint(BaseModel):
    date: str
    price: float

class LatestPriceResponse(BaseModel):
    ticker: str
    price: float

class EtfAnalysisResponse(BaseModel):
    etf_name: str
    latest_close: float
    etf_time_series: List[TimeSeriesPoint]
    latest_prices: List[LatestPriceResponse]