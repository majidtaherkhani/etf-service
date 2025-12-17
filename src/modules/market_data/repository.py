from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from src.modules.market_data.models import SecurityPrice

class MarketDataRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_price_history(self, tickers: list[str]) -> List[SecurityPrice]:
        
        if not tickers:
            return []
        
        
        return self.db.query(SecurityPrice)\
            .filter(SecurityPrice.ticker.in_(tickers))\
            .all()
    
    def get_latest_price(self, ticker: str) -> Optional[SecurityPrice]:
        return self.db.query(SecurityPrice)\
            .filter(SecurityPrice.ticker == ticker)\
            .order_by(desc(SecurityPrice.date))\
            .first()
    
    def get_latest_prices(self, tickers: list[str]) -> List[SecurityPrice]:
        if not tickers:
            return []
        
       
        subquery = self.db.query(
            SecurityPrice.ticker,
            func.max(SecurityPrice.date).label('max_date')
        ).filter(
            SecurityPrice.ticker.in_(tickers)
        ).group_by(SecurityPrice.ticker).subquery()
        
        return self.db.query(SecurityPrice)\
            .join(
                subquery,
                (SecurityPrice.ticker == subquery.c.ticker) & 
                (SecurityPrice.date == subquery.c.max_date)
            ).all()

    
    def bulk_save_prices(self, prices: List[SecurityPrice]):
        try:
            self.db.bulk_save_objects(prices)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e