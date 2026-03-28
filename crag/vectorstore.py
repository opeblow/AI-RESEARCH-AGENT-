"""Vector store management with lazy loading."""

import logging
from pathlib import Path
from typing import List, Optional
from functools import lru_cache

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Manages FAISS vector store with lazy loading."""

    def __init__(self, persist_path: str = "vectorstore"):
        self.persist_path = Path(persist_path)
        self._embeddings: Optional[HuggingFaceEmbeddings] = None
        self._vectorstore: Optional[FAISS] = None

    @property
    def embeddings(self) -> HuggingFaceEmbeddings:
        """Lazy load embedding model."""
        if self._embeddings is None:
            logger.info("Loading embedding model: all-MiniLM-L6-v2")
            self._embeddings = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"}
            )
        return self._embeddings

    def load_or_create(self) -> FAISS:
        """Load existing vectorstore or create new one."""
        if self._vectorstore is not None:
            return self._vectorstore

        if self.persist_path.exists():
            logger.info(f"Loading existing vectorstore from {self.persist_path}")
            self._vectorstore = FAISS.load_local(
                str(self.persist_path),
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            logger.info("No existing vectorstore found. Use build_index() to create one.")
            self._vectorstore = FAISS.from_texts(
                [""],
                self.embeddings
            )
        return self._vectorstore

    def get_retriever(self, search_kwargs: dict = None):
        """Get retriever from vectorstore."""
        vectorstore = self.load_or_create()
        default_kwargs = {"k": 10}
        if search_kwargs:
            default_kwargs.update(search_kwargs)
        return vectorstore.as_retriever(search_kwargs=default_kwargs)

    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to vectorstore."""
        vectorstore = self.load_or_create()
        vectorstore.add_documents(documents)
        self.save()
        logger.info(f"Added {len(documents)} documents to vectorstore")

    def save(self) -> None:
        """Persist vectorstore to disk."""
        if self._vectorstore is not None:
            self.persist_path.mkdir(parents=True, exist_ok=True)
            self._vectorstore.save_local(str(self.persist_path))
            logger.info(f"Vectorstore saved to {self.persist_path}")

    @classmethod
    @lru_cache(maxsize=1)
    def get_instance(cls, persist_path: str = "vectorstore") -> "VectorStoreManager":
        """Get singleton instance."""
        return cls(persist_path=persist_path)


def get_vectorstore_manager(persist_path: str = "vectorstore") -> VectorStoreManager:
    """Factory function for vector store manager."""
    return VectorStoreManager.get_instance(persist_path)


def get_retriever(search_kwargs: dict = None):
    """Convenience function to get retriever."""
    manager = get_vectorstore_manager()
    return manager.get_retriever(search_kwargs)
