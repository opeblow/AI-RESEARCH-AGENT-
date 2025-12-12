import sys
from pathlib import Path
project_root=Path(__file__).parent.parent
sys.path.insert(0,str(project_root))
from fastapi import FastAPI,HTTPException
import uvicorn
from dotenv import load_dotenv
load_dotenv()

from app.agent import app as crag_agent
from schemas import QueryRequest,QueryResponse

api=FastAPI(
    title="Mobolaji's CRAG API",
    description="Corrective RAG with loacl PDFs + Brave Search fallback",
    version="1.0"
)
@api.post("/ask",response_model=QueryResponse)
async def ask_crag(request:QueryRequest):
    try:
        result=crag_agent.invoke({"question":request.question})
        return QueryResponse(
            answer=result.get("answer","No answer generated"),
            sources=result.get("citations",[])

        )
    except Exception as e :
        raise HTTPException(status_code=500,detail=str(e))
    
@api.get("/")
def root():
    return {"message":"Mobolaji's CRAG API is live. POST to /ask with {'question':'your question'}"}

if __name__=="__main__":
    uvicorn.run("main:api",host="0.0.0.0",port=8000,reload=True)
    