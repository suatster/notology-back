import requests
from fastapi import APIRouter, HTTPException
from collections import deque

router = APIRouter(prefix="/quotes", tags=["Quotes"])

QUOTABLE_RANDOM_URL = "https://api.quotable.io/random"

MAX_CACHE_SIZE = 10
MAX_RETRY = 5

seen_quotes = set()
quote_queue = deque()


@router.get("/random")
def get_random_quote():
    for _ in range(MAX_RETRY):
        try:
            request = requests.get(QUOTABLE_RANDOM_URL, timeout=5, verify=False)
            request.raise_for_status()
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"Quote service error: {e}"
            )

        data = request.json()
        quote = data.get("content")

        if quote not in seen_quotes:
            seen_quotes.add(quote)
            quote_queue.append(quote)

            if len(quote_queue) > MAX_CACHE_SIZE:
                old = quote_queue.popleft()
                seen_quotes.remove(old)

            return {
                "quote": quote,
                "author": data.get("author"),
                "tags": data.get("tags")
            }

    raise HTTPException(
        status_code=503,
        detail="Could not fetch unique quote"
    )
