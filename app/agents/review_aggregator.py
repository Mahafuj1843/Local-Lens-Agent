from transformers import pipeline


sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)


async def analyze_reviews(state):
    results = state["results"]

    enriched = []

    for item in results:
        fake_review = "Great food and amazing staff"

        sentiment = sentiment_pipeline(fake_review)[0]

        item["sentiment"] = sentiment

        enriched.append(item)

    print("Analyzing reviews====>", enriched)

    return {
        "results": enriched
    }