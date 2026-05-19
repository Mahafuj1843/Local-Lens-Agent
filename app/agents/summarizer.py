from app.services.ollama_service import llm
from app.utils.result_helpers import get_business_address, get_business_name


async def summarize_results(state):
    results = state["results"]
    summarized = []

    for item in results:
        name = get_business_name(item)
        address = get_business_address(item)

        prompt = f"""
Generate a short factual summary (2 sentences max) for this place.

Name: {name}
Address or area: {address or 'Unknown'}
"""
        response = llm.invoke(prompt)
        item["summary"] = response.content
        summarized.append(item)

    return {"results": summarized}
