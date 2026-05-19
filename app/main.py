from fastapi import FastAPI, HTTPException

from app.agents.intent_parser import parse_intent
from app.agents.location_resolver import resolve_location
from app.graph.workflow import app_graph
from app.schemas.search_schema import SearchRequest, SearchResponse


app = FastAPI(title="LocalLens", version="1.0.0")


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/search", response_model=SearchResponse)
async def search(body: SearchRequest):
    query = body.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="query must not be empty")

    try:
        intent = parse_intent(query)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not parse query: {exc}") from exc

    try:
        location = resolve_location(intent)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    result = await app_graph.ainvoke(
        {
            "query": query,
            "intent": intent,
            "location": location,
            "results": [],
        }
    )

    return SearchResponse(
        query=query,
        intent=intent.model_dump(),
        location=location,
        results=result.get("results", []),
    )
