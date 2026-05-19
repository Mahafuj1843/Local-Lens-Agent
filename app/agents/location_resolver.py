import requests


def resolve_location(location: str = None):

    # ==================================
    # USER PROVIDED LOCATION
    # ==================================

    if location:

        url = "https://nominatim.openstreetmap.org/search"

        params = {
            "q": location,
            "format": "json",
            "limit": 1
        }

        response = requests.get(
            url,
            params=params,
            headers={
                "User-Agent": "LocalLens/1.0"
            },
            timeout=30
        )

        data = response.json()

        result = data[0]

        return {
            "lat": float(result["lat"]),
            "lon": float(result["lon"]),
            "display_name": result["display_name"]
        }

    # ==================================
    # NEAR ME (IP LOCATION)
    # ==================================

    response = requests.get(
        "http://ip-api.com/json",
        headers={
            "User-Agent": "LocalLens/1.0"
        },
        timeout=30
    )

    data = response.json()

    return {
        "lat": data["lat"],
        "lon": data["lon"],
        "display_name": f"{data['city']}, {data['country']}"
    }