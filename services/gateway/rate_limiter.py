import redis.asyncio as redis
import time
from fastapi import HTTPException, Request, status
from services.gateway.config import settings

redis_client = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute

    async def check_rate_limit(self, identifier: str):
        key = f"rate_limit:{identifier}"
        now = time.time()
        window_start = now - 60

        try:
            pipe = redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zadd(key, {str(now): now})
            pipe.zcard(key)
            pipe.expire(key, 60)
            results = await pipe.execute()

            request_count = results[2]
            if request_count > self.requests_per_minute:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded. Maximum 60 requests per minute allowed."
                )
        except redis.RedisError:
            # Fallback gracefully if Redis is unavailable during dev
            pass

rate_limiter = RateLimiter(requests_per_minute=60)
