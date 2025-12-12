"""
Main FastAPI application for KiranaChain Credit Scoring API.

This is the entry point for the FastAPI application that provides
ML-based credit scoring endpoints.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from api.credit_score_api import router as credit_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="KiranaChain Credit Scoring API",
    description="ML-powered credit scoring system for shopkeepers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(credit_router)

logger.info("✅ FastAPI application initialized")


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "message": "KiranaChain Credit Scoring API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

