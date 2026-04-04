"""LangGraph workflow nodes for CRAG system."""

import json
import logging
from typing import Dict, List, Literal
from functools import lru_cache

from langchain_core.documents import Document

from crag.models import AgentState, DocumentGrade, Grade
from crag.prompts import GRADER_PROMPT, RAG_PROMPT

logger = logging.getLogger(__name__)


class CRAGNodes:
    """Collection of nodes for the CRAG LangGraph workflow."""

    def __init__(self):
        self._retriever = None
        self._grader_chain = None
        self._generator_chain = None
        self._brave_search = None

    @property
    def retriever(self):
        """Lazy load retriever."""
        if self._retriever is None:
            from crag.vectorstore import get_retriever
            self._retriever = get_retriever(search_kwargs={"k": 10})
        return self._retriever

    @property
    def grader_chain(self):
        """Lazy load grader chain."""
        if self._grader_chain is None:
            from crag.llm_manager import get_llm_manager
            manager = get_llm_manager()
            self._grader_chain = manager.get_grader_chain(GRADER_PROMPT)
        return self._grader_chain

    @property
    def generator_chain(self):
        """Lazy load generator chain."""
        if self._generator_chain is None:
            from .llm_manager import get_llm_manager
            manager = get_llm_manager()
            self._generator_chain = manager.get_generator_chain(RAG_PROMPT)
        return self._generator_chain

    def get_brave_search(self):
        """Lazy load Brave search."""
        if self._brave_search is None:
            import os
            from crag.search import brave_search_results
            api_key = os.getenv("BRAVE_API_KEY", "")
            self._brave_search = lambda q, c=5: brave_search_results(q, api_key, c)
        return self._brave_search

    async def retrieve(self, state: AgentState) -> Dict:
        """Retrieve documents from vector store."""
        logger.info("Retrieving from local documents")
        try:
            docs: List[Document] =await self.retriever.ainvoke(state["question"])
            logger.info(f"Retrieved {len(docs)} documents")
            return {"documents": docs}
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return {"documents": []}

    async def grade_documents(self, state: AgentState) -> Dict:
        """Grade retrieved documents for relevance."""
        logger.info("Grading retrieved documents")
        docs = state["documents"]
        grades = []

        for i, doc in enumerate(docs):
            try:
                raw =await self.grader_chain.ainvoke({
                    "question": state["question"],
                    "context": doc.page_content
                })
                data = json.loads(raw)
                grade = data.get("grade", "irrelevant").lower()
                grades.append(DocumentGrade(
                    doc_id=i,
                    grade=Grade.RELEVANT if grade == "relevant" else Grade.IRRELEVANT,
                    score=float(data.get("score", 0.0)),
                    explanation=data.get("explanation", "")
                ))
            except Exception as e:
                logger.warning(f"Grading failed for doc {i}: {e}")
                grades.append(DocumentGrade(
                    doc_id=i,
                    grade=Grade.IRRELEVANT,
                    score=0.0,
                    explanation="Failed to parse LLM output"
                ))

        return {"grades": grades}

    def decide_next_step(self, state: AgentState) -> Literal["web_search", "generate"]:
        """Decide whether to use web search or generate answer."""
        relevant_count = sum(
            1 for g in state["grades"]
            if g.grade == Grade.RELEVANT and g.score > 0.7
        )
        logger.info(f"Found {relevant_count} high-quality chunks")
        
        if relevant_count < 2:
            logger.info("Insufficient relevant chunks -> using web search")
            return "web_search"
        else:
            logger.info("Sufficient relevant chunks -> generating answer")
            return "generate"

    def web_search(self, state: AgentState) -> Dict:
        """Perform web search via Brave Search."""
        logger.info("Searching the web via Brave Search")
        web_docs = []

        try:
            search_func = self.get_brave_search()
            results = search_func(state["question"], 5)

            for r in results:
                url = r.get("link", "")
                snippet = r.get("snippet", "")

                full_content = ""
                if url:
                    from crag.search import BraveSearchClient
                    full_content = BraveSearchClient.fetch_page_content(url, max_chars=3000)

                content = full_content if full_content else snippet
                web_docs.append(Document(
                    page_content=content,
                    metadata={
                        "source": url,
                        "title": r.get("title", "Web Result"),
                        "type": "web"
                    }
                ))

            logger.info(f"Added {len(web_docs)} web results")
            return {"documents": web_docs, "used_web_search": True}

        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return {"documents": state["documents"], "used_web_search": False}

    async def generate(self, state: AgentState) -> Dict:
        """Generate final answer from relevant documents."""
        logger.info("Generating final answer")

        web_docs = [d for d in state["documents"] if d.metadata.get("type") == "web"]
        local_docs = [d for d in state["documents"] if d.metadata.get("type") != "web"]

        if web_docs:
            docs_to_use = web_docs[:10]
        else:
            grades = state.get("grades", [])
            if grades:
                relevant_ids = {
                    g.doc_id for i, g in enumerate(grades)
                    if g.grade == Grade.RELEVANT and g.score > 0.6
                }
                relevant_docs = [d for i, d in enumerate(local_docs) if i in relevant_ids]
                docs_to_use = relevant_docs[:10]
            else:
                docs_to_use = local_docs[:10]

        if not docs_to_use:
            logger.warning("No relevant documents found")
            return {
                "answer": "I don't have enough relevant information to answer this question.",
                "citations": [],
                "used_web_search": state.get("used_web_search", False)
            }

        context = "\n\n".join([d.page_content for d in docs_to_use])
        answer =await self.generator_chain.ainvoke({
            "context": context,
            "question": state["question"]
        })

        sources = {}
        for d in docs_to_use:
            src = d.metadata.get("source", "unknown")
            doc_type = d.metadata.get("type", "local")
            if src not in sources:
                sources[src] = {
                    "source": src,
                    "type": "web" if doc_type == "web" else "local",
                    "title": d.metadata.get("title")
                }

        return {
            "answer": answer.strip(),
            "citations": list(sources.values()),
            "used_web_search": state.get("used_web_search", False)
        }


@staticmethod
@lru_cache(maxsize=1)
def get_nodes() -> CRAGNodes:
    """Get singleton node instance."""
    return CRAGNodes()
