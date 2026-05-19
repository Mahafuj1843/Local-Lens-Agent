import requests

from app.schemas.intent_schema import IntentSchema

PHOTON_URL = "https://photon.komoot.io/api"
IP_API_URL = "http://ip-api.com/json"


def _display_from_photon(properties: dict, fallback: str) -> str:
    parts = [
        properties.get("name"),
        properties.get("city"),
        properties.get("state"),
        properties.get("country"),
    ]
    label = ", ".join(p for p in parts if p)
    return label or fallback


def resolve_location(intent: IntentSchema | str | None):
    """
    Resolve coordinates from parsed intent or a raw location string.
    Uses IP geolocation when location is missing or near_me.
    """
    if isinstance(intent, IntentSchema):
        location = intent.location
        use_near_me = intent.location_scope == "near_me" or not location
    else:
        location = intent
        use_near_me = not location or (
            isinstance(location, str) and location.strip().lower() == "near me"
        )

    if use_near_me:
        return _resolve_from_ip()

    return _resolve_from_photon(location.strip())


def _resolve_from_ip() -> dict:
    try:
        response = requests.get(
            IP_API_URL,
            headers={"User-Agent": "LocalLens/1.0"},
            timeout=30,
        )
        data = response.json()
        if "lat" in data and "lon" in data:
            return {
                "lat": data["lat"],
                "lon": data["lon"],
                "display_name": f"{data.get('city', '')}, {data.get('country', '')}".strip(", "),
            }
        raise ValueError("Could not resolve coordinates from IP response")
    except Exception as exc:
        raise RuntimeError(f"IP-based location resolution failed: {exc}") from exc


def _resolve_from_photon(location: str) -> dict:
    try:
        response = requests.get(
            PHOTON_URL,
            params={"q": location, "limit": 1, "lang": "en"},
            headers={"User-Agent": "LocalLens/1.0"},
            timeout=30,
        )
        data = response.json()
        features = data.get("features") if isinstance(data, dict) else None
        if not features:
            raise ValueError(f"No location found for query: {location}")

        result = features[0]
        geometry = result.get("geometry") or {}
        coords = geometry.get("coordinates")
        if not coords or len(coords) != 2:
            raise ValueError("Malformed coordinates in Photon API response")

        properties = result.get("properties") or {}
        return {
            "lat": float(coords[1]),
            "lon": float(coords[0]),
            "display_name": _display_from_photon(properties, location),
        }
    except Exception as exc:
        raise RuntimeError(f"Error resolving '{location}': {exc}") from exc
