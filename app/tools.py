import requests
from app.utils import get_retriever
import os 
from dotenv import load_dotenv
load_dotenv()

retriever=get_retriever()

def brave_search_results(query:str,count:int=5):
    """Direct Brave search API call"""
    api_key=os.getenv("BRAVE_API_KEY")
    url="https://api.search.brave.com/res/v1/web/search"
    headers={
        "Accept":"application/json",
        "Accept-Encoding":"gzip",
        "X-Subscription-Token":api_key
    }
    params={"q":query,"count":count}
    response=requests.get(url,headers=headers,params=params)
    response.raise_for_status()
    data=response.json()
    results=[]
    for item in data.get("web",{}).get("results",[]):
        results.append(
            {
                "title":item.get("title",""),
                "link":item.get("url",""),
                "snippet":item.get("description","")
            }
        )
    return results

__all__ = ["retriever","brave_search_results"]



