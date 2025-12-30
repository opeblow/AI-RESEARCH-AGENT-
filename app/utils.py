import os
from pathlib import Path
from typing import List

# Lazy-loaded heavy dependencies
_embeddings = None
_Document = None
_RecursiveCharacterTextSplitter = None
_FAISS = None
_partition = None

VECTORSTORE_PATH = Path("vectorstore")


def _get_document_class():
    global _Document
    if _Document is None:
        from langchain_core.documents import Document
        _Document = Document
    return _Document


def _get_text_splitter():
    global _RecursiveCharacterTextSplitter
    if _RecursiveCharacterTextSplitter is None:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        _RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter
    return _RecursiveCharacterTextSplitter


def _get_faiss():
    global _FAISS
    if _FAISS is None:
        from langchain_community.vectorstores import FAISS
        _FAISS = FAISS
    return _FAISS


def _get_partition():
    global _partition
    if _partition is None:
        from unstructured.partition.auto import partition
        _partition = partition
    return _partition


def get_embeddings():
    global _embeddings
    if _embeddings is None:
        print("Loading embedding model...")
        from langchain_community.embeddings import HuggingFaceEmbeddings
        _embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return _embeddings


def load_all_documents(folder: str = "data") -> List:
    """Loads every PDF,DOCX,TXT,HTML from data folder using unstructured"""
    partition = _get_partition()
    Document = _get_document_class()

    docs = []
    folder_path = Path(folder)
    if not folder_path.exists():
        print("No 'data' folder found, create it and drop your files there")
        return docs
    for file_path in folder_path.rglob("."):
        if file_path.suffix.lower() in {".pdf", ".docx", ".txt", ".html", ".htm", ".md"}:
            print(f"Loading ---> {file_path.name}")
            try:
                elements = partition(filename=str(file_path))
                text = "\n\n".join([el.text for el in elements if getattr(el, "text", None)])
                if text.strip():
                    docs.append(
                        Document(
                            page_content=text.strip(),
                            metadata={"source": file_path.name}
                        )
                    )
                print(f"✓ Successfully loaded {file_path.name}")
            except Exception as e:
                print(f" Error loading {file_path.name}: {str(e)}")
                print(f"   Skipping this file and continuing...")
                continue
    print(f"Loaded {len(docs)} documents")
    return docs


def chunk_documents(docs: List) -> List:
    RecursiveCharacterTextSplitter = _get_text_splitter()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    chunks = splitter.split_documents(docs)
    print(f"Split into {len(chunks)} chunks")
    return chunks


def create_and_store_vectorstore() -> None:
    FAISS = _get_faiss()
    raw_docs = load_all_documents()
    if not raw_docs:
        print("No documents loaded. Please add files to the 'data' folder.")
        return
    chunks = chunk_documents(raw_docs)
    vectorstore = FAISS.from_documents(chunks, get_embeddings())
    VECTORSTORE_PATH.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(VECTORSTORE_PATH))
    print(f"Vectorstore created and saved in '{VECTORSTORE_PATH}'")


def get_retriever():
    """Going to be used by AGENT, loads existing vectorstore or creates it once"""
    FAISS = _get_faiss()

    if VECTORSTORE_PATH.exists():
        print("Loading existing vectorstore")
        vectorstore = FAISS.load_local(
            str(VECTORSTORE_PATH),
            get_embeddings(),
            allow_dangerous_deserialization=True
        )
    else:
        print("First run detected, building vectorstore")
        create_and_store_vectorstore()
        vectorstore = FAISS.load_local(str(VECTORSTORE_PATH), get_embeddings(), allow_dangerous_deserialization=True)

    return vectorstore.as_retriever(search_kwargs={"k": 10})


__all__ = ["get_retriever"]
