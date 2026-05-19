import requests

from app.mappers.osm_mapper import generate_osm_tag

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Country-wide OSM radius queries are slow and sparse; skip Overpass for those.
COUNTRY_SCOPE_MAX_RADIUS_M = 30_000


async def search_places(category: str, lat: float, lon: float, radius_km: int = 10):
    if radius_km > COUNTRY_SCOPE_MAX_RADIUS_M / 1000:
        return []

    key, value = generate_osm_tag(category)
    radius_m = min(max(radius_km, 1), 30) * 1000

    query = f"""
    [out:json][timeout:25];
    (
      node["{key}"="{value}"](around:{radius_m},{lat},{lon});
      way["{key}"="{value}"](around:{radius_m},{lat},{lon});
      relation["{key}"="{value}"](around:{radius_m},{lat},{lon});
    );
    out center;
    """

    try:
        response = requests.post(
            OVERPASS_URL,
            data={"data": query},
            headers={"User-Agent": "LocalLens/1.0"},
            timeout=60,
        )
    except Exception as exc:
        print(f"Overpass request failed: {exc}")
        return []

    if response.status_code != 200 or not response.text.strip():
        print(f"Overpass non-200 or empty: {response.status_code}")
        return []

    data = response.json()
    return data.get("elements", [])
