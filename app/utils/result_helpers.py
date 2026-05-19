def get_business_name(item: dict) -> str:
    tags = item.get("tags") or {}
    for key in ("name", "name:en", "brand"):
        if tags.get(key):
            return str(tags[key])
    if item.get("name"):
        return str(item["name"])
    return "Unknown"


def get_business_address(item: dict) -> str:
    if item.get("location"):
        return str(item["location"])
    tags = item.get("tags") or {}
    parts = [
        tags.get("addr:street"),
        tags.get("addr:housenumber"),
        tags.get("addr:city"),
        tags.get("addr:postcode"),
    ]
    joined = ", ".join(p for p in parts if p)
    return joined or item.get("description", "")
