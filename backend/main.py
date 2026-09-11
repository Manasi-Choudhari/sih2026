"""
Main FastAPI entry point for VAJRA Investigation Platform.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes.api_v1 import router as api_router

app = FastAPI(
    title="VAJRA Investigation API",
    description="Real-Time Crypto Fraud Attribution System (SIH 26183)",
    version="1.0.0"
)

# Enable CORS for Next.js Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
def root():
    return {
        "service": "VAJRA Backend Investigation Engine",
        "status": "operational",
        "version": "1.0.0",
        "ncrp_mock_mode": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
