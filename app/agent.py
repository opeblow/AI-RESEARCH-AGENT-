from typing import Literal
from langgraph.graph import StateGraph,START,END
from app.models import AgentState

from app.nodes import(
    retrieve,
    grade_documents,
    go_to_web,
    web_search,
    generate
)
workflow=StateGraph(AgentState)
#This is all stations(their nodes)
workflow.add_node("retrieve",retrieve)
workflow.add_node("grade_documents",grade_documents)
workflow.add_node("web_search",web_search)
workflow.add_node("generate",generate)

workflow.add_edge(START,"retrieve")#This is the starting point
workflow.add_edge("retrieve","grade_documents")

workflow.add_conditional_edges(
    "grade_documents",
    go_to_web,
    {
        "web_search":"web_search",
        "generate":"generate",
    },
)
workflow.add_edge("web_search","generate")#After web search always generate

workflow.add_edge("generate",END)#Final stop

app = workflow.compile()#Compiling the agent,so we work with this
