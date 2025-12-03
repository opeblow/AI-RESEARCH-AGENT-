from langchain_community.tools import BraveSearch
from app.utils import get_retriever
import os 
from dotenv import load_dotenv
load_dotenv()

retriever=get_retriever()

brave_search=BraveSearch.from_api_key(
    api_key=os.getenv("BRAVE_API_KEY"),
    search_kwargs={"count":5}
)
__all__ = ["retriever","brave_search"]

