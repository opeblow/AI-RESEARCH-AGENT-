"""Document management router."""

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from crag.schemas import DocumentUploadResponse
from crag.document_processor import DocumentProcessor
from crag.vectorstore import get_vectorstore_manager

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and index a new document."""
    try:
        processor = DocumentProcessor()
        contents = await file.read()
        
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name
        
        try:
            doc = processor.load_document(file.filename)
            chunks = processor.chunk_documents([doc])
            
            vectorstore = get_vectorstore_manager()
            vectorstore.add_documents(chunks)
            
            return DocumentUploadResponse(
                status="success",
                filename=file.filename,
                chunks_created=len(chunks),
                message=f"Document indexed successfully with {len(chunks)} chunks"
            )
        finally:
            os.unlink(tmp_path)

    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/rebuild-index")
async def rebuild_index():
    """Rebuild the entire document index."""
    try:
        processor = DocumentProcessor()
        chunks = processor.process_folder("data")
        
        if not chunks:
            return JSONResponse(
                status_code=400,
                content={"error": "No documents found in data folder"}
            )
        
        from crag.vectorstore import VectorStoreManager
        manager = VectorStoreManager()
        manager._vectorstore = None
        
        for chunk in chunks:
            manager.add_documents([chunk])
        
        return JSONResponse({
            "status": "success",
            "chunks_created": len(chunks),
            "message": "Index rebuilt successfully"
        })

    except Exception as e:
        logger.error(f"Index rebuild failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
