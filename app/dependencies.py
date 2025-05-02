from fastapi import HTTPException, Depends
from redis import Redis
import time
from fastapi.security import APIKeyHeader

class RedisRateLimiter:
    def __init__(self, redis: Redis, calls: int = 100, period: int = 60):
        self.redis = redis
        self.calls = calls
        self.period = period

    async def __call__(self, key: str):
        current = self.redis.get(key)
        if current and int(current) > self.calls:
            raise HTTPException(429, "Rate limit exceeded")
        
        pipeline = self.redis.pipeline()
        pipeline.incr(key, 1)
        pipeline.expire(key, self.period)
        pipeline.execute()
        return True
    api_key_header = APIKeyHeader(name="X-API-Key")

    async def validate_api_key(api_key: str = Depends(api_key_header)):
        if api_key != os.getenv("API_KEY"):
            raise HTTPException(403, "Invalid API key")
        return True

    async def validate_content_type(request):
        if request.headers.get("Content-Type") != "application/json":
            raise HTTPException(400, "Invalid content type")