"""Solid-OIDC client-credentials authentication with DPoP-bound access tokens.

Why this file exists at all
---------------------------
The Community Solid Server (CSS) protects resources with DPoP-bound access
tokens (RFC 9449).  A plain ``requests.get()`` with a bearer token is refused:
once the token carries a ``cnf.jkt`` confirmation claim, the server demands a
matching proof-of-possession JWT on *every* request.

This module is **adapted from** ``SolidClientCredentials`` 1.0.3 by A_A
(MIT licence, see ``solidlib/vendor/LICENSE-solid-client-credentials.md``;
source: https://github.com/Otto-AA/solid-client-credentials-py).

It was vendored rather than installed as a dependency for three reasons, all of
which are thesis-relevant:

1. The upstream package's last commit was 2025-03-05; its CSS helper module has
   since been deleted and its README documents CSS 5.x, three major versions
   behind the CSS 7.2.0 this lab pins.
2. Upstream **omits the ``ath`` claim**, which RFC 9449 s.4.2 requires when a
   DPoP proof accompanies an access token.  We add it (see ``_dpop_proof``).
3. A thesis should not rest on an unexplained dependency.  Every step of the
   authentication flow is visible here.

Spec references
---------------
* Solid-OIDC s.9.3 -- a valid DPoP proof MUST be present when a DPoP-bound
  token is used.  https://solidproject.org/TR/oidc#resource-access-validation
* RFC 9449 s.4.2 (proof format), s.4.3 (checks), s.7.1 (the ``DPoP`` auth
  scheme).  https://www.rfc-editor.org/rfc/rfc9449.html
* CSS client-credentials documentation (token endpoint discovery, the
  form-encoding requirement on id/secret):
  https://communitysolidserver.github.io/CommunitySolidServer/7.x/usage/client-credentials/

Algorithm choice
----------------
**ES256.**  CSS's OIDC provider advertises EdDSA among its DPoP signing
algorithms, but the resource server verifies proofs with
``@solid/access-token-verifier``, whose accepted set does *not* include EdDSA.
ES256 is accepted by both ends.
"""

from __future__ import annotations

import base64
import datetime as _dt
import hashlib
import math
import uuid
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote, urlsplit

import jwt
import requests
from jwcrypto import jwk

#: The only signing algorithm accepted by *both* the CSS OIDC provider and the
#: resource-side token verifier.  See the module docstring.
SIGNING_ALG = "ES256"

#: Refresh a token this many seconds before it actually expires, so a long
#: experiment never trips over an expiry mid-run.
REFRESH_MARGIN_SECONDS = 30


def _b64url(raw: bytes) -> str:
    """base64url without padding, as used throughout JOSE."""
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _form_encode(value: str) -> str:
    """Percent-encode exactly as JavaScript's ``encodeURIComponent`` does.

    CSS's documentation is explicit that "both the ID and the secret need to be
    form-encoded" before being joined with ``:`` and base64-encoded for HTTP
    Basic.  Upstream SolidClientCredentials skips this step; with CSS's own
    ``name_uuid`` / hex credentials it is a no-op in practice, but it is a
    latent mismatch and cheap to get right.
    """
    return quote(value, safe="-_.!~*'()")


@dataclass
class AccessToken:
    """A DPoP-bound access token and the moment it stops being useful."""

    value: str
    expires_at: _dt.datetime

    def expires_within(self, seconds: int) -> bool:
        now = _dt.datetime.now(tz=_dt.timezone.utc)
        return self.expires_at <= now + _dt.timedelta(seconds=seconds)


class SolidClientCredentialsAuth(requests.auth.AuthBase):
    """``requests`` auth handler that signs each request with a fresh DPoP proof.

    A DPoP proof is bound to a single (method, URL) pair and is rejected by CSS
    if older than 120 seconds, so a new proof is minted per request rather than
    cached.
    """

    def __init__(self, session: "SolidAuth") -> None:
        self._session = session

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        token = self._session.access_token()
        request.headers["Authorization"] = f"DPoP {token.value}"
        request.headers["DPoP"] = self._session.dpop_proof(
            url=str(request.url),
            method=str(request.method),
            access_token=token.value,
        )
        return request


class SolidAuth:
    """Holds one identity's credentials, DPoP key pair and current token.

    One instance == one WebID.  Experiments create one per user (Alice, Bob) so
    that "who is asking" is always explicit at the call site.
    """

    def __init__(
        self,
        issuer: str,
        client_id: str,
        client_secret: str,
        *,
        include_ath: bool = True,
        timeout: int = 30,
    ) -> None:
        self.issuer = issuer.rstrip("/")
        self._client_id = client_id
        self._client_secret = client_secret
        self._timeout = timeout
        #: Whether to emit the RFC 9449 ``ath`` claim.  Configurable purely so
        #: that experiments can *test* whether CSS enforces it -- see
        #: ``experiments/00_hello_pod`` and the methods note in RESULTS.md.
        self.include_ath = include_ath
        self._key = jwk.JWK.generate(kty="EC", crv="P-256")
        self._token: AccessToken | None = None
        self._token_endpoint: str | None = None

    # -- discovery ---------------------------------------------------------

    def token_endpoint(self) -> str:
        """Discover the token endpoint from the issuer's OIDC configuration.

        Hardcoding ``/.oidc/token`` would work against a default CSS but is
        exactly the kind of convention-over-discovery shortcut the Solid specs
        warn against, so we read it from ``.well-known``.
        """
        if self._token_endpoint is None:
            url = f"{self.issuer}/.well-known/openid-configuration"
            response = requests.get(url, timeout=self._timeout)
            response.raise_for_status()
            self._token_endpoint = response.json()["token_endpoint"]
        return self._token_endpoint

    # -- DPoP --------------------------------------------------------------

    def dpop_proof(
        self, url: str, method: str, access_token: str | None = None
    ) -> str:
        """Mint a DPoP proof JWT for one (method, URL) pair.

        ``htu`` must match the URL with query and fragment stripped -- CSS
        compares it by strict string equality, so a stray ``?`` or a missing
        trailing slash is an instant 401.
        """
        htu = urlsplit(url)._replace(query="", fragment="").geturl()
        payload: dict[str, Any] = {
            "htu": htu,
            "htm": method.upper(),
            "jti": str(uuid.uuid4()),
            "iat": math.floor(_dt.datetime.now(tz=_dt.timezone.utc).timestamp()),
        }
        # RFC 9449 s.4.2: `ath` is REQUIRED when the proof accompanies an access
        # token.  CSS 7.2.0 only validates it *if present* -- its verifier
        # carries a literal `TODO: Phased-in ath becomes enforced` -- so
        # upstream libraries get away with omitting it.  We send it anyway.
        if access_token is not None and self.include_ath:
            payload["ath"] = _b64url(hashlib.sha256(access_token.encode("ascii")).digest())

        headers = {"typ": "dpop+jwt", "jwk": self._key.export_public(as_dict=True)}
        key_pem = self._key.export_to_pem(private_key=True, password=None).decode("utf-8")
        return jwt.encode(payload, key=key_pem, algorithm=SIGNING_ALG, headers=headers)

    # -- tokens ------------------------------------------------------------

    def access_token(self, force_refresh: bool = False) -> AccessToken:
        """Return a valid access token, requesting a new one only when needed."""
        if (
            force_refresh
            or self._token is None
            or self._token.expires_within(REFRESH_MARGIN_SECONDS)
        ):
            self._token = self._request_token()
        return self._token

    def _request_token(self) -> AccessToken:
        endpoint = self.token_endpoint()
        basic = _b64url_basic(self._client_id, self._client_secret)
        response = requests.post(
            endpoint,
            headers={
                "authorization": f"Basic {basic}",
                "content-type": "application/x-www-form-urlencoded",
                "dpop": self.dpop_proof(endpoint, "POST"),
            },
            data={"grant_type": "client_credentials", "scope": "webid"},
            timeout=self._timeout,
        )
        if not response.ok:
            raise RuntimeError(
                f"Token request to {endpoint} failed: "
                f"HTTP {response.status_code} {response.text[:300]}"
            )
        body = response.json()
        value = body["access_token"]
        claims = jwt.api_jwt.decode_complete(
            value, options={"verify_signature": False}
        )["payload"]
        expires_at = _dt.datetime.fromtimestamp(claims["exp"], tz=_dt.timezone.utc)
        return AccessToken(value=value, expires_at=expires_at)

    def auth(self) -> SolidClientCredentialsAuth:
        """A ``requests`` auth handler bound to this identity."""
        return SolidClientCredentialsAuth(self)


def _b64url_basic(client_id: str, client_secret: str) -> str:
    """Build the HTTP Basic payload CSS expects: base64(form(id):form(secret))."""
    pair = f"{_form_encode(client_id)}:{_form_encode(client_secret)}"
    return base64.b64encode(pair.encode("utf-8")).decode("ascii")
