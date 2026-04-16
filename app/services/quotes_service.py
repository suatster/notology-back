import httpx
from collections import deque
from app.core.config import settings
from app.core.http_client import client


class QuotesService:
    
    def __init__(self):
        self.seen_quotes = set()
        self.quote_queue = deque()


    async def get_random_quote(self):
        for _ in range(settings.MAX_RETRY):
            try:
                response = await client.get(settings.QUOTABLE_URL)
                response.raise_for_status()
            except httpx.RequestError as e:
                raise Exception(f"Request error: {e}")
            except httpx.HTTPStatusError as e:
                raise Exception(f"Bad response: {e}")

            data = response.json()
            quote = data.get("content")

            if quote not in self.seen_quotes:
                self.seen_quotes.add(quote)
                self.quote_queue.append(quote)

                if len(self.quote_queue) > settings.MAX_CACHE_SIZE:
                    old = self.quote_queue.popleft()
                    self.seen_quotes.remove(old)

                return {
                    "quote": quote,
                    "author": data.get("author"),
                    "tags": data.get("tags")
                }

        raise HTTPException(
            status_code=503, 
            detail="Could not fetch unique quote"
        )
