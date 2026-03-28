"""Document processing utilities."""

import logging
from pathlib import Path
from typing import List

from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Processes documents for vector storage."""

    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".html", ".htm", ".md"}

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._splitter = None
        self._partition = None

    @property
    def splitter(self):
        """Lazy load text splitter."""
        if self._splitter is None:
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            self._splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len,
            )
        return self._splitter

    @property
    def partition(self):
        """Lazy load unstructured partition."""
        if self._partition is None:
            from unstructured.partition.auto import partition
            self._partition = partition
        return self._partition

    def load_document(self, file_path: Path) -> Document:
        """Load a single document."""
        try:
            elements = self.partition(filename=str(file_path))
            text = "\n\n".join([el.text for el in elements if getattr(el, "text", None)])
            return Document(
                page_content=text.strip(),
                metadata={"source": file_path.name, "path": str(file_path)}
            )
        except Exception as e:
            logger.error(f"Failed to load {file_path.name}: {e}")
            raise

    def load_documents(self, folder: str = "data") -> List[Document]:
        """Load all supported documents from folder."""
        docs = []
        folder_path = Path(folder)
        
        if not folder_path.exists():
            logger.warning(f"Data folder '{folder}' does not exist")
            return docs

        for file_path in folder_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                try:
                    doc = self.load_document(file_path)
                    if doc.page_content.strip():
                        docs.append(doc)
                        logger.info(f"Loaded: {file_path.name}")
                except Exception as e:
                    logger.warning(f"Skipping {file_path.name}: {e}")
                    continue

        logger.info(f"Loaded {len(docs)} documents")
        return docs

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks."""
        if not documents:
            return []
        chunks = self.splitter.split_documents(documents)
        logger.info(f"Split into {len(chunks)} chunks")
        return chunks

    def process_folder(self, folder: str = "data") -> List[Document]:
        """Load and chunk all documents from folder."""
        docs = self.load_documents(folder)
        return self.chunk_documents(docs)
