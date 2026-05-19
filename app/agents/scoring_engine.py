from app.schemas.intent_schema import IntentSchema
from app.utils.result_helpers import get_business_name


def _intent_from_state(state) -> IntentSchema:
    intent = state["intent"]
    if isinstance(intent, IntentSchema):
        return intent
    return IntentSchema.model_validate(intent)


async def score_results(state):
    intent = _intent_from_state(state)
    results = state["results"]
    scored = []

    for item in results:
        rating = item.get("rating")
        if rating is None:
            tags = item.get("tags") or {}
            stars = tags.get("stars")
            try:
                rating = float(stars) if stars else 4.0
            except (TypeError, ValueError):
                rating = 4.0

        sentiment = item.get("sentiment") or {}
        sentiment_score = 90 if sentiment.get("label") == "POSITIVE" else 60

        review_count = item.get("review_count") or 50
        score = rating * 0.4 + (review_count / 100) * 0.3 + (sentiment_score / 100) * 0.3
        item["score"] = round(score, 2)
        item["display_name"] = get_business_name(item)
        scored.append(item)

    scored.sort(key=lambda x: x["score"], reverse=True)
    return {"results": scored[: intent.count]}
