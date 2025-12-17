from sqlalchemy.orm import Session
from src.modules.etf.models import AnalysisLog

class EtfRepository:
    def __init__(self, db: Session):
        self.db = db

    def log_request(self, file_name: str, url: str) -> AnalysisLog:
        log = AnalysisLog(file_name=file_name, storage_url=url)
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log