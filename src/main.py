from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from src.modules.etf.router import router as etf_router
from configs.limiter import limiter

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://etf-web-wine.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173", 
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(etf_router)

@app.get("/health")
async def health():
    return {"status": "healthy"}

