from sqlalchemy import Column, Integer, String, DateTime, func
from configs.db.postgresql import Base

class AnalysisLog(Base):
    __tablename__ = "etf_analysis_files"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String)
    storage_url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())