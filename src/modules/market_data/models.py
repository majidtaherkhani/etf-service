from sqlalchemy import Column, String, Float, DateTime, Index, text
from configs.db.postgresql import Base

class SecurityPrice(Base):
    __tablename__ = "security_prices"

    date = Column(DateTime, primary_key=True, nullable=False, index=True)
    ticker = Column(String, primary_key=True, nullable=False, index=True)
    price = Column(Float, nullable=False)
    
    
    __table_args__ = (
        Index('idx_ticker_date', 'ticker', text('date DESC')),
    )