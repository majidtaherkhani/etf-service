from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from configs.db.postgresql import get_db
from src.modules.etf.service import EtfService
from src.modules.etf import schemas

router = APIRouter(prefix="/etf", tags=["Analysis"])

@router.post("/analyze", response_model=schemas.EtfAnalysisResponse)
async def analyze(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    service = EtfService(db)
    
    return await service.analyze_portfolio(file)