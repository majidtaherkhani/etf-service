import asyncio
import io
import pandas as pd
from io import BytesIO
from fastapi import UploadFile
from sqlalchemy.orm import Session
from typing import Dict

from src.modules.market_data.repository import MarketDataRepository
from src.modules.storage.service import StorageService
from src.modules.etf.repository import EtfRepository
from src.modules.etf import schemas
from src.exceptions import InvalidCsvFormatException
from src.modules.etf.exceptions import (
    InvalidCsvColumnsException,
    NoPriceDataException,
    NoMatchingTickerDataException
)
from configs.db.postgresql import SessionLocal

class EtfService:
    ENABLE_BACKGROUND_TASKS = True

    def __init__(self, db: Session):
        self.market_data = MarketDataRepository(db)
        self.etf_repo = EtfRepository(db)
        self.storage = StorageService()

    async def analyze_portfolio(self, file: UploadFile) -> schemas.EtfAnalysisResponse:
        await file.seek(0)
        content = await file.read()
        filename = file.filename

        try:
            df_input = pd.read_csv(BytesIO(content))
            if df_input.empty:
                raise InvalidCsvFormatException("CSV file is empty")
            weights = dict(zip(df_input['name'].str.strip().str.upper(), df_input['weight']))
        except KeyError as e:
            raise InvalidCsvColumnsException()
        except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as e:
            raise InvalidCsvFormatException()
        except Exception as e:
            raise InvalidCsvFormatException()

        if self.ENABLE_BACKGROUND_TASKS:
            asyncio.create_task(self._store_and_log_background(content, filename))

        etf_name = filename.rsplit('.', 1)[0] if filename else "ETF"
        return await self._process_portfolio_data(weights, etf_name)

    async def _process_portfolio_data(self, weights: Dict[str, float], etf_name: str) -> schemas.EtfAnalysisResponse:
        tickers = list(weights.keys())
        price_records = await asyncio.to_thread(self.market_data.get_price_history, tickers)
        
        if not price_records:
            raise NoPriceDataException()

        return await asyncio.to_thread(
            self._calculate_portfolio_math, 
            weights, 
            price_records,
            etf_name
        )

    async def _store_and_log_background(self, file_content: bytes, filename: str):
        db = SessionLocal()
        try:
            public_url = await self.storage.upload(file_content=file_content, filename=filename)
            etf_repo = EtfRepository(db)
            await asyncio.to_thread(etf_repo.log_request, filename, public_url)
        except Exception as e:
            print(f"Background storage/DB task failed: {e}")
        finally:
            db.close()

    def _calculate_portfolio_math(self, weights: Dict[str, float], price_records: list, etf_name: str) -> schemas.EtfAnalysisResponse:
        try:
            data = [{'date': r.date, 'ticker': r.ticker, 'price': r.price} for r in price_records]
        except AttributeError:
            data = price_records
             
        df_prices = pd.DataFrame(data)
        
        if df_prices.empty:
            raise NoPriceDataException()

        prices_df = df_prices.pivot(index='date', columns='ticker', values='price')
        available_tickers = prices_df.columns.intersection(weights.keys())
        
        if available_tickers.empty:
            raise NoMatchingTickerDataException()

        weight_series = pd.Series(weights)[available_tickers]
        prices_subset = prices_df[available_tickers]
        weighted_prices = prices_subset.mul(weight_series, axis=1)
        etf_series = weighted_prices.sum(axis=1)

        last_date = prices_subset.index.max()
        last_prices = prices_subset.loc[last_date]
        latest_close = round(etf_series.iloc[-1], 2)
        
        latest_prices_resp = [
            schemas.LatestPriceResponse(
                ticker=t, 
                price=round(last_prices[t] * weights[t], 2),
                weight=weights[t]
            ) 
            for t in available_tickers
        ]
        
        etf_time_series_resp = [
            schemas.TimeSeriesPoint(date=str(d), price=round(p, 2))
            for d, p in etf_series.items()
        ]

        return schemas.EtfAnalysisResponse(
            etf_name=etf_name,
            latest_close=latest_close,
            etf_time_series=etf_time_series_resp,
            latest_prices=latest_prices_resp
        )