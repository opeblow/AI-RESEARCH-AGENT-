"""Pydantic schemas for API request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class QueryRequest(BaseModel):
    """User query request schema."""
    question: str = Field(..., min_length=1, max_length=2000, description="User question")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for context")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What are the main findings in the Q3 2024 report?",
                "conversation_id": "conv_abc123"
            }
        }


class SourceCitation(BaseModel):
    """Citation source schema."""
    source: str
    type: str = Field(default="local", description="Source type: local or web")
    title: Optional[str] = None
    score: Optional[float] = None


class QueryResponse(BaseModel):
    """CRAG query response schema."""
    answer: str = Field(..., description="Generated answer")
    sources: List[SourceCitation] = Field(default_factory=list, description="Source citations")
    conversation_id: str = Field(..., description="Conversation ID")
    model: str = Field(default="gpt-4o-mini", description="Model used")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Answer confidence score")
    retrieved_chunks: int = Field(default=0, description="Number of chunks retrieved")
    used_web_search: bool = Field(default=False, description="Whether web search was used")


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = "healthy"
    version: str
    timestamp: datetime
    services: dict


class DocumentUploadResponse(BaseModel):
    """Document upload response schema."""
    status: str
    filename: str
    chunks_created: int
    message: str


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
