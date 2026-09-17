"""One authenticated (or deliberately anonymous) identity talking to a pod.

Every experiment works through ``SolidSession`` objects so that *who is asking*
is explicit at each call site -- ``alice.get(url)`` versus ``bob.get(url)``
versus ``anon.get(url)``.  That readability matters more here than brevity,
because the whole point of the experiments is who may do what.

Each session records every exchange to the shared ``EvidenceLog``.
"""

from __future__ import annotations

from typing import Any

import requests

from solidlib.auth import SolidAuth
from solidlib.evidence import EvidenceLog
from solidlib.provision import PodIdentity


class SolidSession:
    """A named identity with a ``requests``-like API that logs its evidence."""

    def __init__(
        self,
        name: str,
        base_url: str,
        auth: SolidAuth | None = None,
        evidence: EvidenceLog | None = None,
        web_id: str | None = None,
        pod_url: str | None = None,
    ) -> None:
        self.name = name
        self.base_url = base_url.rstrip("/")
        self._auth = auth
        self.evidence = evidence
        self.web_id = web_id
        self.pod_url = pod_url

    # -- constructors ------------------------------------------------------

    @classmethod
    def from_identity(
        cls,
        name: str,
        base_url: str,
        identity: PodIdentity,
        evidence: EvidenceLog | None = None,
    ) -> "SolidSession":
        auth = SolidAuth(base_url, identity.client_id, identity.client_secret)
        return cls(
            name=name,
            base_url=base_url,
            auth=auth,
            evidence=evidence,
            web_id=identity.web_id,
            pod_url=identity.pod_url,
        )

    @classmethod
    def anonymous(
        cls, base_url: str, evidence: EvidenceLog | None = None, name: str = "anonymous"
    ) -> "SolidSession":
        """An unauthenticated client -- the 'any agent on the web' case."""
        return cls(name=name, base_url=base_url, auth=None, evidence=evidence)

    # -- core --------------------------------------------------------------

    def request(self, method: str, url: str, note: str = "", **kwargs: Any) -> requests.Response:
        auth = self._auth.auth() if self._auth is not None else None
        response = requests.request(method, url, auth=auth, timeout=30, **kwargs)
        if self.evidence is not None:
            self.evidence.record(self.name, response, note)
        return response

    def get(self, url: str, **kwargs: Any) -> requests.Response:
        return self.request("GET", url, **kwargs)

    def head(self, url: str, **kwargs: Any) -> requests.Response:
        return self.request("HEAD", url, **kwargs)

    def put(self, url: str, data: Any, content_type: str, **kwargs: Any) -> requests.Response:
        headers = {"content-type": content_type, **kwargs.pop("headers", {})}
        return self.request("PUT", url, data=data, headers=headers, **kwargs)

    def post(self, url: str, data: Any, content_type: str, **kwargs: Any) -> requests.Response:
        headers = {"content-type": content_type, **kwargs.pop("headers", {})}
        return self.request("POST", url, data=data, headers=headers, **kwargs)

    def patch_n3(self, url: str, body: str, **kwargs: Any) -> requests.Response:
        """N3 Patch -- the only way to modify description resources.

        Solid Protocol s.5.3.1 (Modifying Resources Using N3 Patches).
        """
        return self.request(
            "PATCH", url, data=body, headers={"content-type": "text/n3"}, **kwargs
        )

    def delete(self, url: str, **kwargs: Any) -> requests.Response:
        return self.request("DELETE", url, **kwargs)

    # -- credential control (used by 01_share_revoke) ----------------------

    def force_new_token(self) -> None:
        """Discard the cached access token and obtain a fresh one."""
        if self._auth is not None:
            self._auth.access_token(force_refresh=True)

    def has_cached_token(self) -> bool:
        return self._auth is not None and self._auth._token is not None
