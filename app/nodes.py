import json
import os
from typing import List


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
    print("Searching tthe web via BRAVE...")
    try:
        results=brave_search_results(state["question"],count=5)
        web_docs=[]
        for r in results:
            web_docs.append(
                Document(
                    page_content=r.get("snippet",""),
                    metadata={
                        "source":r.get("link","unknown"),
                        "title":r.get("title","Web Result")
                    }
                )
            )
            print(f"Added {len(web_docs)} web results")
            return {"documents":state["documents"] + web_docs}
    except Exception as e:
        print(f"Web Search Failed:{e}")
        return {"documents":state["documents"]}
        
    
def generate(state:AgentState):
    print("Generating final answer")
    context="\n\n".join([d.page_content for d in state["documents"][:15]])
    answer=generator_chain.invoke(
        {
            "context":context,
            "question":state["question"]
        }
    )
    citations=[]
    for doc in state["documents"][:15]:
        src=doc.metadata.get("source","unknown")
        citations.append(f"[source:{src}]")
    
    return {
        "answer":answer.strip(),
        "citations":citations
    }
      
__all__ = ["retrieve","grade_documents","go_to_web","web_search","generate"]
    