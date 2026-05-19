import re

from langchain_core.prompts import ChatPromptTemplate

from app.services.ollama_service import llm


prompt = ChatPromptTemplate.from_template(
    """
You are an OpenStreetMap tag expert.

Convert the business category into exactly one OSM tag as key=value.

Examples:
hotel → tourism=hotel
resort → tourism=resort
burger restaurant → amenity=restaurant
mobile shop → shop=mobile_phone
fruit shop → shop=greengrocer
tax advisor → office=accountant
hospital → amenity=hospital
grocery store → shop=supermarket
pharmacy → amenity=pharmacy
cafe → amenity=cafe

Return ONLY the tag in key=value form with no quotes or explanation.

Category:
{category}
"""
)

chain = prompt | llm

_TAG_RE = re.compile(r'^[\w:-]+=[\w:-]+$')


def _parse_osm_tag(raw: str) -> tuple[str, str]:
    line = raw.strip().splitlines()[0].strip().strip('"').strip("'")
    if "=" not in line:
        return "amenity", "restaurant"
    key, value = line.split("=", 1)
    key = key.strip()
    value = value.strip().strip('"').strip("'")
    if not key or not value:
        return "amenity", "restaurant"
    return key, value


def generate_osm_tag(category: str) -> tuple[str, str]:
    response = chain.invoke({"category": category})
    raw = response.content.strip()
    if _TAG_RE.match(raw):
        return raw.split("=", 1)
    return _parse_osm_tag(raw)
