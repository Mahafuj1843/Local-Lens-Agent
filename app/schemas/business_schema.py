from pydantic import BaseModel
from typing import Optional


class BusinessListing(BaseModel):
    name: str
    address: Optional[str]
    rating: Optional[float]
    review_count: Optional[int]
    sentiment_score: Optional[float]
    score: Optional[float]
    summary: Optional[str]