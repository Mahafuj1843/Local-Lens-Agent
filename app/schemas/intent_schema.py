from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class IntentSchema(BaseModel):
    """Structured intent extracted from a free-form local search query."""

    category: str = Field(
        description=(
            "Business or service type only, without words like best/top. "
            "Examples: hotel, burger restaurant, mobile shop, fruit shop, tax advisor, hospital, resort"
        )
    )
    count: int = Field(
        default=5,
        ge=1,
        le=20,
        description="How many places the user wants",
    )
    location: Optional[str] = Field(
        default=None,
        description=(
            "Place to search in. Use null when the query has no location "
            "(e.g. 'best fruit shop') or when the user says near me."
        ),
    )
    location_scope: Literal["near_me", "neighborhood", "city", "region", "country"] = Field(
        default="city",
        description=(
            "near_me: no place given or explicit near me; "
            "neighborhood: area/district (Gulshan); city: city name; "
            "region: state/province; country: whole country"
        ),
    )
    radius_km: int = Field(
        default=10,
        ge=1,
        le=200,
        description="Search radius in km; use larger values for country-wide queries",
    )
    sort_by: str = Field(default="rating")
    filters: List[str] = Field(default_factory=list)
    search_phrase: str = Field(
        description=(
            "Clean web/maps search phrase preserving user intent, "
            "e.g. 'best hotels in Cox's Bazar' or 'best tax advisor in Los Angeles, USA'"
        )
    )
