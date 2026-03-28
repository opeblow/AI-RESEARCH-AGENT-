"""CRAG LangGraph workflow definition."""

import logging
from langgraph.graph import StateGraph, START, END

from crag.models import AgentState
from crag.nodes import get_nodes

logger = logging.getLogger(__name__)


def create_crag_workflow():
    """Create and compile the CRAG LangGraph workflow."""
    nodes = get_nodes()
    
    workflow = StateGraph(AgentState)

    workflow.add_node("retrieve", nodes.retrieve)
    workflow.add_node("grade_documents", nodes.grade_documents)
    workflow.add_node("web_search", nodes.web_search)
    workflow.add_node("generate", nodes.generate)

    workflow.add_edge(START, "retrieve")
    workflow.add_edge("retrieve", "grade_documents")

    workflow.add_conditional_edges(
        "grade_documents",
        nodes.decide_next_step,
        {
            "web_search": "web_search",
            "generate": "generate",
        },
    )
    
    workflow.add_edge("web_search", "generate")
    workflow.add_edge("generate", END)

    return workflow.compile()


crag_app = create_crag_workflow()
