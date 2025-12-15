import json
import os
from typing import List
import requests
from bs4 import BeautifulSoup


from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langgraph.prebuilt import tool_node
from app.models import AgentState,DocumentGrade,Grade
from app.tools import retriever,brave_search_results
from app.prompts import GRADER_PROMPT,RAG_PROMPT
from langchain_core.callbacks import CallbackManagerForChainRun
from langchain_core.runnables import RunnableConfig
from tenacity import retry,stop_after_attempt,wait_exponential,retry_if_exception_type
from dotenv import load_dotenv
load_dotenv()
print(f"API Key loaded:{os.getenv("OPENAI_API_KEY")}")
llm=ChatOpenAI(model="gpt-4o-mini",temperature=0)

def with_retry(chain):
    return chain.with_retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1,min=2,max=10),
        retry=retry_if_exception_type((Exception,)),
        reraise=True
    )

grader_prompt=ChatPromptTemplate.from_template(GRADER_PROMPT)
generator_prompt=ChatPromptTemplate.from_template(RAG_PROMPT)

grader_chain=grader_prompt|llm|StrOutputParser()
generator_chain=generator_prompt|llm|StrOutputParser()


def fetch_web_page_content(url:str,max_chars:int=3000)->str:
    """Fetch and extract text content from a web page"""
    try:
        headers={
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response=requests.get(url,headers=headers,timeout=5)
        response.raise_for_status()
        soup=BeautifulSoup(response.content,'html.parser')

        for script in soup(["script","style","nav","header","footer"]):
            script.decompose()

        text=soup.get_text()
        lines=[line.strip() for line in text.splitlines() if line.strip()]
        clean_text=" ".join(lines)

        return clean_text[:max_chars]
    except Exception as e:
        print(f"Failed to fetch {url}:{e}")
        return ""


def retrieve(state:AgentState):
    print("Retrieving from local documents")
    docs:List[Document]=retriever.invoke(state["question"])
    return {"documents":docs}


def grade_documents(state:AgentState):
    print("Grading retrieved documents")
    docs=state["documents"]
    grades=[]

    for i,doc in enumerate(docs):
        raw=grader_chain.invoke(
            {"question":state["question"],"context":doc.page_content}
        )
        try:
            data=json.loads(raw)
            grade=data.get("grade","irrelevant").lower()
            score=float(data.get("score",0.0))
            explanation=data.get("explanation","")
            grades.append(
                DocumentGrade(
                    doc_id=i,
                    grade=Grade.RELEVANT if grade =="relevant" else Grade.IRRELEVANT,
                    score=score,
                    explanation=explanation,
                )
            )
        except:
            grades.append(
                DocumentGrade(
                    doc_id=i,
                    grade=Grade.IRRELEVANT,
                    score=0.0,
                    explanation="Failed to parse LLM output"
                )
            )
    return {"grades":grades}


def go_to_web(state:AgentState):
    relevant_count=sum(1 for g in state["grades"] if g.grade==Grade.RELEVANT and g.score>0.7)
    print(f"Found {relevant_count} high-quality chunks -> ",end="")
    if relevant_count < 2:
        print("Going to web to search")
        return "web_search"
    else:
        print("enough local info,generating answer")
        return "generate"
    
def web_search(state:AgentState):
    print("Searching the web via BRAVE...")
    try:
        results=brave_search_results(state["question"],count=5)
        web_docs=[]
        for r in results:
            url=r.get("link","")
            snippet=r.get("snippet","")

            print(f"Fetching full content from {url[:50]}...")
            full_content=fetch_web_page_content(url,max_chars=3000)

            content=full_content if full_content else snippet

            web_docs.append(
                Document(
                    page_content=content,
                    metadata={
                        "source":url,
                        "title":r.get("title","Web Result"),
                        "type":"web"
                    }
                )
            )

        print(f"Added {len(web_docs)} web results with full content")
        print("Replacing irrelevant local docs with web results")

        return {"documents":web_docs}
    except Exception as e:
        print(f"Web Search Failed:{e}")
        return {"documents":state["documents"]}
        
    
def generate(state:AgentState):
    print("Generating final answer")

    web_docs=[d for d in state["documents"] if d.metadata.get("type")=="web"]
    local_docs=[d for d in state["documents"] if d.metadata.get("type")!="web"]

    if web_docs:
        print(f"Using {len(web_docs)} web documents as primary source")
        docs_to_use=web_docs[:10]
    else:
        grades=state.get("grades",[])
        if grades:
            relevant_ids={g.doc_id for g in grades if g.grade==Grade.RELEVANT and g.score>0.6}
            relevant_docs=[d for i,d in enumerate(local_docs) if i in relevant_ids]
            print(f"Using {len(relevant_docs)} relevant local documents (filtered from {len(local_docs)})")
            docs_to_use=relevant_docs[:10]
        else:
            print(f"No grades available,using all {len(local_docs)} local documents")
            docs_to_use=local_docs[:10]

    if not docs_to_use:
        print("WARNING:No relevant documents found!")
        return {
            "answer":"I don't have enough relevant information to answer this question.",
            "citations":[]
        }

    context="\n\n".join([d.page_content for d in docs_to_use])
    answer=generator_chain.invoke(
        {
            "context":context,
            "question":state["question"]
        }
    )
    sources={}
    for d in docs_to_use:
        srs=d.metadata.get("source","unknown")
        doc_type=d.metadata.get("type","local")
        if srs not in sources:
            label="web" if  doc_type=="web" else "local"
            sources[srs]=f"[source:{srs} ({label})]"
    citations=list(sources.values())
    return {"answer":answer.strip(),"citations":citations}
      
__all__ = ["retrieve","grade_documents","go_to_web","web_search","generate"]
    