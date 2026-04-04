"""Query processing router."""

import logging
import time
import uuid
from fastapi import APIRouter, HTTPException

from crag.schemas import QueryRequest, QueryResponse, SourceCitation, ErrorResponse
from crag.agent import crag_app

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/query",
    response_model=QueryResponse,
    responses={500: {"model": ErrorResponse}}
)
async def query_crag(request: QueryRequest):
    """Process a query through the CRAG system."""
    start_time = time.time()
    conversation_id = request.conversation_id or str(uuid.uuid4())

    try:
        logger.info(f"Processing query: {request.question[:100]}...")
        
        result = await crag_app.ainvoke({"question": request.question})
        
        processing_time = (time.time() - start_time) * 1000

        sources = [
            SourceCitation(
                source=c.get("source", ""),
                type=c.get("type", "local"),
                title=c.get("title")
            )
            for c in result.get("citations", [])
        ]

        doc_count = len(result.get("documents", []))
        confidence = sum(
            g.score for g in result.get("grades", [])
        ) / max(doc_count, 1) if doc_count > 0 else 0.0

        return QueryResponse(
            answer=result.get("answer", "No answer generated"),
            sources=sources,
            conversation_id=conversation_id,
            model="gpt-4o-mini",
            processing_time_ms=round(processing_time, 2),
            confidence=round(confidence, 2),
            retrieved_chunks=doc_count,
            used_web_search=result.get("used_web_search", False)
        )

    except Exception as e:
        logger.error(f"Query processing failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
