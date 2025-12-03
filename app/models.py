from enum import Enum
from typing import List,Optional,Literal,TypedDict
from pydantic import BaseModel,Field
from langchain_core.documents import Document


class Grade(str,Enum):

    RELEVANT="relevant"
    IRRELEVANT="irrelevant"

class DocumentGrade(BaseModel):
    """Output from the relevance grader for one document chunk"""
    doc_id:int=Field(description="Index of the document in the retrieved list")
    grade:Grade
    score:float=Field(ge=0.0,le=1.0,description="Confidence score 0.0-1.0")
    explanation:str=Field(description="A sentence reason")


class WebResult(BaseModel):
    title:str
    url:str
    snippet:str


class AgentState(TypedDict,total=False):
    """Langgraph state,everything the agent remembers as it runs"""
    question:str
    documents:List[Document]
    grades:List[DocumentGrade]
    web_results:Optional[List[WebResult]]
    answer:str
    citations:List[dict]

__all__ = ["AgentState","Grade","DocumentGrade","WebResult"]
