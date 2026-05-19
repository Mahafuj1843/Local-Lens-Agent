from app.services.overpass_service import search_places
from app.services.duckduckgo_service import duckduckgo_search
from app.services.playwright_service import scrape_google_results

# def filter_hotels_missing_name_and_address(hotels):
#     filtered = []

#     for hotel in hotels:
#         tags = hotel.get("tags", {})

#         name = tags.get("name") or tags.get("name:en")
#         address_fields = [
#             tags.get("addr:street"),
#             tags.get("addr:housenumber"),
#             tags.get("addr:postcode"),
#         ]

#         has_name = bool(name)
#         has_address = any(address_fields)  # at least one address field exists

#         # keep only hotels missing BOTH name AND address
#         if not has_name and not has_address:
#             filtered.append(hotel)

#     return filtered


async def run_search_agent(state):

    intent = state["intent"]

    location = state["location"]

    category = intent.category

    user_query = state.get("query") or intent.search_phrase

    lat = location["lat"]
    lon = location["lon"]
    display_name = location["display_name"]

    print("Trying Overpass API...")

    overpass_results = await search_places(
        category,
        lat,
        lon
    )

    if overpass_results:

        print("Overpass success")

        # filtered_results = filter_hotels_missing_name_and_address(overpass_results)

        return {
            "results": overpass_results
        }

    print("Overpass failed. Trying DuckDuckGo...")

    ddg_query = f"{category} near {display_name}"

    print("DuckDuckGo query")

    ddg_results = await duckduckgo_search(ddg_query)

    if ddg_results:

        print("DuckDuckGo success")

        return {
            "results": ddg_results
        }

    print("Trying Playwright scraping...")

    # Pass "{category} in {location}" so the playwright service can detect category
    playwright_query = f"{category} in {display_name}"

    playwright_results = await scrape_google_results(playwright_query)

    print("Playwright success", playwright_results)

    return {
        "results": playwright_results
    }