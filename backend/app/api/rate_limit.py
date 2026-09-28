from collections.abc import Callable
from hashlib import sha256
from ipaddress import ip_address
from fastapi import Depends, HTTPException, Request
from redis import Redis
from redis.exceptions import RedisError
from app.core.redis import get_redis
from app.core.settings import settings

_FIXED_WINDOW = "local count = redis.call('INCR', KEYS[1]); if count == 1 then redis.call('EXPIRE', KEYS[1], ARGV[1]); end; return count"
def rate_limit(scope: str, requests: int, period_seconds: int) -> Callable[..., None]:
    def enforce(request: Request, client: Redis = Depends(get_redis)) -> None:
        if settings.environment == "test":
            return
        peer = request.client.host if request.client else "unknown"
        address = peer
        if peer in settings.trusted_proxy_addresses:
            forwarded = request.headers.get("x-forwarded-for", "").split(",", 1)[0].strip()
            try:
                address = str(ip_address(forwarded))
            except ValueError:
                address = peer
        identity = sha256(address.encode()).hexdigest()
        key = f"ivoirex:ratelimit:v1:{scope}:{identity}"
        try:
            count = int(client.eval(_FIXED_WINDOW, 1, key, period_seconds))
            if count > requests:
                retry_after = max(client.ttl(key), 1)
                raise HTTPException(status_code=429, detail="Too many requests", headers={"Retry-After": str(retry_after)})
        except RedisError as exc:
            raise HTTPException(status_code=503, detail="Rate limiting service unavailable") from exc
    return enforce
