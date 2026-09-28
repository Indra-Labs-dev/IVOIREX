from hashlib import sha256
from starlette.requests import Request
from app.api.rate_limit import rate_limit
from app.core.settings import settings


class RecordingRedis:
    def __init__(self):
        self.key = None

    def eval(self, script, key_count, key, period):
        self.key = key
        return 1

    def ttl(self, key):
        return 10


def make_request(peer: str, forwarded: str) -> Request:
    return Request({
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/auth/login",
        "raw_path": b"/auth/login",
        "query_string": b"",
        "headers": [(b"x-forwarded-for", forwarded.encode())],
        "client": (peer, 12345),
        "server": ("localhost", 8000),
    })


def test_forwarded_address_is_used_only_for_trusted_proxy(monkeypatch):
    monkeypatch.setattr(settings, "environment", "development")
    monkeypatch.setattr(settings, "trusted_proxy_ips", "172.29.0.10")
    enforce = rate_limit("test", 5, 60)

    trusted_redis = RecordingRedis()
    enforce(make_request("172.29.0.10", "198.51.100.7, 10.0.0.1"), trusted_redis)
    expected_client = sha256(b"198.51.100.7").hexdigest()
    assert trusted_redis.key == f"ivoirex:ratelimit:v1:test:{expected_client}"

    untrusted_redis = RecordingRedis()
    enforce(make_request("172.29.0.22", "203.0.113.99"), untrusted_redis)
    expected_peer = sha256(b"172.29.0.22").hexdigest()
    assert untrusted_redis.key == f"ivoirex:ratelimit:v1:test:{expected_peer}"
