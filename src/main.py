from fastapi import FastAPI
from src.modules.etf.router import router as etf_router

app = FastAPI()

app.include_router(etf_router)

@app.get("/health")
async def health():
    return {"status": "healthy"}

