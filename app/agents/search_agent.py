from app.schemas.intent_schema import IntentSchema
from app.services.duckduckgo_service import duckduckgo_search
from app.services.overpass_service import search_places
from app.services.playwright_service import scrape_google_results


def _intent_from_state(state) -> IntentSchema:
    intent = state["intent"]
    if isinstance(intent, IntentSchema):
        return intent
    return IntentSchema.model_validate(intent)


def _web_search_query(intent: IntentSchema, location_display: str) -> str:
    if intent.search_phrase:
        return intent.search_phrase
    if location_display:
        return f"best {intent.category} in {location_display}"
    return f"best {intent.category} near me"


def _skip_local_osm(intent: IntentSchema) -> bool:
    return intent.location_scope == "country"


async def run_search_agent(state):
    intent = _intent_from_state(state)
    location = state["location"]
    lat = location["lat"]
    lon = location["lon"]
    display_name = location["display_name"]

    web_query = _web_search_query(intent, display_name)
    print(f"Search: category={intent.category!r} location={display_name!r} query={web_query!r}")

    if not _skip_local_osm(intent):
        overpass_results = await search_places(
            intent.category,
            lat,
            lon,
            radius_km=intent.radius_km,
        )
        if overpass_results:
            print("Overpass success")
            return {"results": overpass_results[: intent.count]}

    print("Overpass skipped or empty. Trying DuckDuckGo...")
    ddg_results = await duckduckgo_search(web_query)
    if ddg_results:
        print("DuckDuckGo success")
        return {"results": ddg_results[: intent.count]}

    print("Trying Playwright scraping...")
    playwright_results = await scrape_google_results(
        web_query,
        category=intent.category,
    )
    return {"results": playwright_results[: intent.count]}
