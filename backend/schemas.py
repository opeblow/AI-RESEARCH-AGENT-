from pydantic import BaseModel
from typing import List


class QueryRequest(BaseModel):
    question:str

class QueryResponse(BaseModel):
    answer:str
    sources:List[str]=[]
    built_by:str="MOBOLAJI OPEYEMI BOLATITO OBINNA . CRAG SYSTEM(Corrective Retrieval -Augmented Generation)"
    model:str="gpt-4o-mini  + all-MiniLM-L6-V2 embeddings"

__all__ = ["QueryRequest","QueryResponse"]
