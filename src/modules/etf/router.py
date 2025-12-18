from fastapi import APIRouter, UploadFile, File, Depends, Request
from sqlalchemy.orm import Session
from configs.db.postgresql import get_db
from configs.limiter import limiter
from src.modules.etf.service import EtfService
from src.modules.etf import schemas

router = APIRouter(prefix="/etf", tags=["Analysis"])

@router.post("/analyze", response_model=schemas.EtfAnalysisResponse)
@limiter.limit("5/minute")
async def analyze(
    request: Request,
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    service = EtfService(db)
    
    return await service.analyze_portfolio(file)