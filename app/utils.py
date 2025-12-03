import os
from pathlib import Path
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from unstructured.partition.auto import partition
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings


embeddings=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

VECTORSTORE_PATH=Path("vectorstore")

def load_all_documents(folder:str="data")->List[Document]:
    """Loads every PDF,DOCX,TXT,HTML from data folder using unstructured"""
    docs:List[Document]=[]
    folder_path=Path(folder)
    if not folder_path.exists():
        print("No 'data' folder found,create it and drop your files there jahre")
        return docs
    for file_path in folder_path.rglob("*.*"):
        if file_path.suffix.lower() in {".pdf",".docx",".txt",".html",".htm",".md"}:
            print(f"Loading --->{file_path.name}")
            elements=partition(filename=str(file_path))
            text="\n\n".join([el.text for el in elements if getattr(el,"text",None)])
            if text.strip():
                docs.append(
                    Document(
                        page_content=text.strip(),
                        metadata={"source":file_path.name}
                    )
                )
    print(f"Loaded{len(docs)} douments")
    return docs


def chunk_documents(docs:List[Document])->List[Document]:
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    chunks=splitter.split_documents(docs)
    print(f"Split into {len(chunks)}chunks")
    return chunks


def create_and_store_vectorstore()->None:
    raw_docs=load_all_documents()
    if not raw_docs:
        return 
    chunks=chunk_documents(raw_docs)
    vectorstore=FAISS.from_documents(chunks,embeddings)
    VECTORSTORE_PATH.mkdir(parents=True,exist_ok=True)
    vectorstore.save_local(str(VECTORSTORE_PATH))
    print(f"Vectorstore created and saved  in '{VECTORSTORE_PATH}'")


def get_retriever():
    """Going to be used by AGENT ,loads existing vectorstore or creates it once"""
    if VECTORSTORE_PATH.exists():
        print("Loading existing vectorstore")
        vectorstore=FAISS.load_local(
            str(VECTORSTORE_PATH),
            allow_dangerous_deserialization=True
        )
    else:
        print("First run detected,build vectorestore")
        create_and_store_vectorstore()
        vectorstore=FAISS.load_local(str(VECTORSTORE_PATH),embeddings,allow_dangerous_deserialization=True)

    return vectorstore.as_retriever(search_kwargs={"k":10})


__all__ = ["get_retriever"]
