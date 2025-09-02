from typing import Annotated

import aioredis

from fastapi import Depends, Request
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi.responses import JSONResponse

from starlette.exceptions import HTTPException as StarletteHTTPException


from app.core.config import REDIS_URI, REQUEST_RATE_LIMIT_MINUTE


async def startup_redis():
    redis = await aioredis.from_url(
        REDIS_URI, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis)

"""

# Custom handler for "Too Many Requests"
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 429:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests, slow down! 🚦"},
        )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
"""

def get_rate_limiter():
    with RateLimiter(times=REQUEST_RATE_LIMIT_MINUTE, seconds=60) as rl:
        return rl

TMRateLimiter = Annotated[RateLimiter, Depends(get_rate_limiter)]
