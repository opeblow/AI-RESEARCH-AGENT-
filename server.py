#!/usr/bin/env python3
"""CRAG API Server entry point."""

import uvicorn
from crag.config import get_settings

settings = get_settings()

if __name__ == "__main__":
    uvicorn.run(
        "crag.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
