"""Agent state models and types."""

from enum import Enum
from typing import List, Optional, TypedDict
from pydantic import BaseModel, Field
from langchain_core.documents import Document


class Grade(str, Enum):
    """Document relevance grade."""
    RELEVANT = "relevant"
    IRRELEVANT = "irrelevant"


class DocumentGrade(BaseModel):
    """Output from the relevance grader for one document chunk."""
    doc_id: int = Field(description="Index of the document in the retrieved list")
    grade: Grade
    score: float = Field(ge=0.0, le=1.0, description="Confidence score 0.0-1.0")
    explanation: str = Field(description="Reason for the grade")


class WebResult(BaseModel):
    """Web search result."""
    title: str
    url: str
    snippet: str


class AgentState(TypedDict, total=False):
    """LangGraph state - everything the agent remembers during execution."""
    question: str
    documents: List[Document]
    grades: List[DocumentGrade]
    web_results: Optional[List[WebResult]]
    answer: str
    citations: List[dict]
    used_web_search: bool
    processing_metadata: dict
