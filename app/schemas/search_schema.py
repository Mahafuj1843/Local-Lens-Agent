from typing import Any, List, Optional

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=3,
        examples=["Best hotels in Cox's Bazar", "best burger restaurant in Gulshan, Dhaka"],
    )


class SearchResponse(BaseModel):
    query: str
    intent: dict[str, Any]
    location: Optional[dict[str, Any]] = None
    results: List[dict[str, Any]] = Field(default_factory=list)
