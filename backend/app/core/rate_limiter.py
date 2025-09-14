from typing import Annotated

import aioredis

from fastapi import Depends, Request, Response, HTTPException, status
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi.responses import JSONResponse

from starlette.exceptions import HTTPException as StarletteHTTPException


from app.core.config import REDIS_URI, REQUEST_RATE_LIMIT_MINUTE


async def service_name_identifier(request: Request):
    service = request.headers.get("Service-Name")
    return service


async def custom_callback(request: Request, response: Response, pexpire: int):
    """
    default callback when too many requests
    :param request:
    :param pexpire: The remaining milliseconds
    :param response:
    :return:
    """
    expire = round(pexpire / 1000)

    raise HTTPException(
        status.HTTP_429_TOO_MANY_REQUESTS,
        f"Too Many Requests. Retry after {expire} seconds.",
        headers={"Retry-After": str(expire)},
    )



async def startup_redis():
    redis_connection = await aioredis.from_url(
        REDIS_URI, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(
                redis=redis_connection,
        identifier=service_name_identifier,
        http_callback=custom_callback
    )
    yield
    await FastAPILimiter.close()



def get_rate_limiter():
    with RateLimiter(times=REQUEST_RATE_LIMIT_MINUTE, seconds=60) as rl:
        yield rl


TMRateLimiter = Annotated[RateLimiter, Depends(get_rate_limiter)]
