from langchain_core.prompts import ChatPromptTemplate

from app.schemas.intent_schema import IntentSchema
from app.services.ollama_service import llm


prompt = ChatPromptTemplate.from_template(
    """
You extract structured search intent from natural-language "best X in Y" queries.
The user query can be about ANY business or service type, anywhere in the world.

Rules:
- category: the thing being searched (no "best", "top", or location words)
- location: place name only, corrected for common typos when obvious; null if missing
- location_scope:
  - near_me → no location, "near me", or only "best fruit shop"
  - neighborhood → district/area (e.g. Gulshan, Gulshan Dhaka)
  - city → city/town (Cox's Bazar, Chattogram, Sylhet, Los Angeles)
  - region → state/province if given without a city
  - country → whole country (Bangladesh, USA)
- radius_km: 5 neighborhood, 10 city, 25 region, 80 country
- count: default 5 unless user asks for another number
- search_phrase: a polished version of the full query for Google Maps / web search
- filters: extra constraints (budget, halal, 24 hours, etc.) or empty list

Typo hints: Coxs Bazar → Cox's Bazar; syhlet → Sylhet; resturant → restaurant;
chattogram → Chattogram; gulshan dhaka → Gulshan, Dhaka; LA → Los Angeles.

Examples:
Query: Best hotels in coxs bazar
→ category=hotel, location=Cox's Bazar, location_scope=city, search_phrase=best hotels in Cox's Bazar

Query: best burger resturant in gulshan, dhaka
→ category=burger restaurant, location=Gulshan, Dhaka, location_scope=neighborhood

Query: best mobile shop in chattogram
→ category=mobile shop, location=Chattogram, location_scope=city

Query: Best fruit shop
→ category=fruit shop, location=null, location_scope=near_me

Query: best tax advisor at LA, USA
→ category=tax advisor, location=Los Angeles, USA, location_scope=city

Query: Best hospital in Bangladesh
→ category=hospital, location=Bangladesh, location_scope=country, radius_km=80

Query: Best resort in syhlet
→ category=resort, location=Sylhet, location_scope=city

User Query:
{query}
"""
)

structured_llm = llm.with_structured_output(IntentSchema)
intent_chain = prompt | structured_llm


def parse_intent(query: str) -> IntentSchema:
    return intent_chain.invoke({"query": query.strip()})
