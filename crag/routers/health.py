"""Health check router."""

import logging
from datetime import datetime
from fastapi import APIRouter

from crag.schemas import HealthResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check application health status."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow(),
        services={
            "api": "operational",
            "vectorstore": "ready",
            "llm": "ready"
        }
    )


@router.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "CRAG API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }
