"""HTTP clients for alice, appR and bob, reusing solidlib's DPoP auth.

``Agent.request`` returns the raw ``requests.Response`` and never raises on a
non-2xx status: in this experiment the status code *is* the observation.

Headers are redacted with the same rule as ``solidlib/evidence.py``
(Authorization, DPoP and cookies are never written), but unlike solidlib every
other header is kept: Chapter 3 needs Cache-Control, ETag, Vary etc. in full.
"""

from __future__ import annotations

import hashlib
from typing import Any
from urllib.parse import urlsplit

import requests

from ch3.lib.env import Identity, base_url, identity
from solidlib.auth import SolidAuth

SENSITIVE = {"authorization", "dpop", "cookie", "set-cookie"}
TIMEOUT = 30


def redact(headers: Any) -> dict[str, str]:
    return {
        k: ("<redacted>" if k.lower() in SENSITIVE else v) for k, v in dict(headers).items()
    }


class _DPoPAuth(requests.auth.AuthBase):
    """Signs each request with a fresh DPoP proof.

    ``htu_rewrite`` maps a URL prefix the client *sends to* onto the prefix the
    server *sees*. It is used only in P2, where the request goes to a caching
    proxy but the DPoP proof must name the origin server's URL (CSS compares
    ``htu`` with its own base URL). That is a lab arrangement, not CSS behaviour.
    """

    def __init__(self, auth: SolidAuth, htu_rewrite: tuple[str, str] | None) -> None:
        self._auth = auth
        self._rewrite = htu_rewrite

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        token = self._auth.access_token()
        url = str(request.url)
        if self._rewrite and url.startswith(self._rewrite[0]):
            url = self._rewrite[1] + url[len(self._rewrite[0]):]
        request.headers["Authorization"] = f"DPoP {token.value}"
        request.headers["DPoP"] = self._auth.dpop_proof(url, str(request.method), token.value)
        return request


class Agent:
    """One identity on one server; ``anonymous`` has no credentials."""

    def __init__(self, ident: Identity | None, config: str, name: str | None = None) -> None:
        self.ident = ident
        self.config = config
        self.name = name or (ident.name if ident else "anonymous")
        self.web_id = ident.web_id if ident else None
        self.pod_url = ident.pod_url if ident else None
        self._auth = (
            SolidAuth(base_url(config), ident.client_id, ident.client_secret) if ident else None
        )
        self.http = requests.Session()
        self.htu_rewrite: tuple[str, str] | None = None

    @classmethod
    def of(cls, config: str, agent: str) -> "Agent":
        if agent == "anonymous":
            return cls(None, config, "anonymous")
        return cls(identity(config, agent), config)

    def request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        auth = _DPoPAuth(self._auth, self.htu_rewrite) if self._auth else None
        kwargs.setdefault("timeout", TIMEOUT)
        return self.http.request(method, url, auth=auth, **kwargs)

    def get(self, url: str, **kw: Any) -> requests.Response:
        return self.request("GET", url, **kw)

    def put(self, url: str, body: str | bytes, content_type: str, **kw: Any) -> requests.Response:
        headers = {"content-type": content_type, **kw.pop("headers", {})}
        return self.request("PUT", url, data=body, headers=headers, **kw)

    def post(self, url: str, body: str | bytes, content_type: str, **kw: Any) -> requests.Response:
        headers = {"content-type": content_type, **kw.pop("headers", {})}
        return self.request("POST", url, data=body, headers=headers, **kw)

    def patch_n3(self, url: str, body: str, **kw: Any) -> requests.Response:
        return self.request("PATCH", url, data=body, headers={"content-type": "text/n3"}, **kw)

    def delete(self, url: str, **kw: Any) -> requests.Response:
        return self.request("DELETE", url, **kw)

    def token_now(self) -> None:
        """Fetch the access token up front so it is not inside a timed window."""
        if self._auth:
            self._auth.access_token()

    def token_fingerprint(self) -> dict | None:
        """Identify the current access token without logging it: sha256 prefix + expiry."""
        if not self._auth or self._auth._token is None:
            return None
        token = self._auth._token
        return {
            "sha256_12": hashlib.sha256(token.value.encode()).hexdigest()[:12],
            "expires_at": token.expires_at.isoformat(),
        }


def response_record(response: requests.Response, body: bool = False, limit: int = 4000) -> dict:
    """What gets logged about one response."""
    record = {
        "method": response.request.method,
        "url": response.url,
        "status": response.status_code,
        "headers": redact(response.headers),
        "elapsed_ms": round(response.elapsed.total_seconds() * 1000, 3),
    }
    if body:
        record["body"] = response.text[:limit]
        record["body_truncated"] = len(response.text) > limit
    return record


def path_of(url: str) -> str:
    return urlsplit(url).path
