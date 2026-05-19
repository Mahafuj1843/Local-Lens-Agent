from ddgs import DDGS


async def duckduckgo_search(query: str):

    results = []

    with DDGS() as ddgs:

        search_results = ddgs.text(
            query,
            max_results=5
        )

        for item in search_results:

            results.append({
                "name": item.get("title"),
                "url": item.get("href"),
                "description": item.get("body")
            })

    return results