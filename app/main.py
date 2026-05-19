from fastapi import FastAPI

from app.agents.intent_parser import parse_intent
from app.agents.location_resolver import resolve_location
from app.graph.workflow import app_graph


app = FastAPI(title="LocalLens", version="1.0.0")


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }

print('Helo')
@app.post("/search")
async def search(payload: dict):
    query = payload["query"]
    print(f"Received payload: {query}")


    intent = parse_intent(query)
    print(f"Parsed intent: {intent}")

    location = resolve_location(intent.location)

    print(f"Parsed location: {location}")

    result = await app_graph.ainvoke({
        "intent": intent,
        "location": location,
        "results": []
    })
    return result
