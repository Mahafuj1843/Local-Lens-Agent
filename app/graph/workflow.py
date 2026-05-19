from typing import Any, Optional

from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict

from app.agents.review_aggregator import analyze_reviews
from app.agents.scoring_engine import score_results
from app.agents.search_agent import run_search_agent
from app.agents.summarizer import summarize_results
from app.schemas.intent_schema import IntentSchema


class GraphState(TypedDict):
    query: str
    intent: IntentSchema
    location: dict[str, Any]
    results: list


workflow = StateGraph(GraphState)

workflow.add_node("search", run_search_agent)
workflow.add_node("reviews", analyze_reviews)
workflow.add_node("score", score_results)
workflow.add_node("summary", summarize_results)

workflow.set_entry_point("search")

workflow.add_edge("search", "reviews")
workflow.add_edge("reviews", "score")
workflow.add_edge("score", "summary")
workflow.add_edge("summary", END)

app_graph = workflow.compile()
