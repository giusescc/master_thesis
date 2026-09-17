"""Create accounts, pods and client credentials through the CSS account API.

No browser is involved anywhere in this lab.  Everything below is the JSON API
CSS exposes at ``/.account/``, introduced in CSS v7.0.0.  (CSS v6 used an
entirely different ``/idp/register/`` endpoint; documentation for v6 and
earlier does not apply.)

Docs: https://communitysolidserver.github.io/CommunitySolidServer/7.x/usage/account/json-api/

Two rules this module follows, both straight from those docs:

* **Never hardcode endpoint URLs.**  Every response carries a ``controls``
  object holding the URLs of every other endpoint, and the docs advise using
  it.  The account UUID appears in most paths, so hardcoding is not even
  possible for the interesting ones.
* **An account is unusable until a login method is added**, and will expire on
  its own if none ever is.  So ``create account`` and ``add password login``
  always happen together.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests

TIMEOUT = 30


@dataclass
class PodIdentity:
    """Everything needed to act as one user, as returned by the account API."""

    email: str
    pod_url: str
    web_id: str
    client_id: str
    client_secret: str


def _json(response: requests.Response, what: str) -> dict[str, Any]:
    if not response.ok:
        raise RuntimeError(
            f"{what} failed: HTTP {response.status_code} {response.text[:400]}"
        )
    return response.json()


def get_controls(base_url: str, token: str | None = None) -> dict[str, Any]:
    """Fetch the ``controls`` object, optionally as an authenticated account.

    Authenticating widens the set of controls considerably: ``account.pod``,
    ``account.clientCredentials`` and ``password.create`` only appear once a
    session token is supplied.
    """
    headers = {"authorization": f"CSS-Account-Token {token}"} if token else {}
    response = requests.get(
        f"{base_url.rstrip('/')}/.account/", headers=headers, timeout=TIMEOUT
    )
    return _json(response, "Fetching account controls")["controls"]


def create_account(base_url: str) -> tuple[str, dict[str, Any]]:
    """Create an empty account; returns (session token, controls).

    The account is not yet usable -- a login method must be added before it can
    do anything, and it expires if one never is.
    """
    controls = get_controls(base_url)
    response = requests.post(
        controls["account"]["create"],
        json={},
        headers={"content-type": "application/json"},
        timeout=TIMEOUT,
    )
    body = _json(response, "Creating account")
    return body["authorization"], body["controls"]


def add_password_login(controls: dict[str, Any], token: str, email: str, password: str) -> None:
    """Attach an email/password login, which is what makes the account usable."""
    response = requests.post(
        controls["password"]["create"],
        json={"email": email, "password": password},
        headers={
            "authorization": f"CSS-Account-Token {token}",
            "content-type": "application/json",
        },
        timeout=TIMEOUT,
    )
    _json(response, f"Adding password login for {email}")


def login(base_url: str, email: str, password: str) -> tuple[str, dict[str, Any]]:
    """Log in to an existing account; returns (session token, controls)."""
    controls = get_controls(base_url)
    response = requests.post(
        controls["password"]["login"],
        json={"email": email, "password": password, "remember": False},
        headers={"content-type": "application/json"},
        timeout=TIMEOUT,
    )
    body = _json(response, f"Logging in as {email}")
    return body["authorization"], body["controls"]


def create_pod(controls: dict[str, Any], token: str, name: str) -> dict[str, Any]:
    """Create a pod and, implicitly, a WebID inside it.

    Supplying no ``settings.webId`` is the browser-free happy path: CSS
    generates a WebID in the new pod and links it to the account immediately.
    Supplying an *external* WebID instead triggers an ownership challenge that
    cannot be satisfied non-interactively -- experiment 03 deals with that case
    explicitly.

    Note: CSS forces pod names to lower case (since 7.1.7).
    """
    response = requests.post(
        controls["account"]["pod"],
        json={"name": name},
        headers={
            "authorization": f"CSS-Account-Token {token}",
            "content-type": "application/json",
        },
        timeout=TIMEOUT,
    )
    return _json(response, f"Creating pod '{name}'")


def create_client_credentials(
    controls: dict[str, Any], token: str, name: str, web_id: str
) -> dict[str, Any]:
    """Mint a client id/secret pair bound to a WebID this account owns.

    The secret is shown exactly once and cannot be retrieved again, so callers
    must persist it immediately.
    """
    response = requests.post(
        controls["account"]["clientCredentials"],
        json={"name": name, "webId": web_id},
        headers={
            "authorization": f"CSS-Account-Token {token}",
            "content-type": "application/json",
        },
        timeout=TIMEOUT,
    )
    return _json(response, f"Creating client credentials '{name}'")


def provision_user(
    base_url: str, email: str, password: str, pod_name: str, token_name: str = "lab"
) -> PodIdentity:
    """Create account + login + pod + credentials in one call, idempotently.

    Re-running without ``--reset`` must not fail, so we try to log in first and
    only create the account if that login does not work.  Client credentials are
    minted fresh every time: CSS shows a secret exactly once and offers no way
    to read it back, so reuse is not an option.

    Order matters here.  The ``controls`` object returned *by* account creation
    is the unauthenticated one -- it does not yet contain ``password.create``,
    ``account.pod`` or ``account.clientCredentials``.  Those appear only when
    the controls are re-read with the session token, which is why
    ``get_controls`` is called again immediately after creating the account.
    """
    pod_name = pod_name.lower()  # CSS forces pod names to lower case (>= 7.1.7)

    try:
        token, _ = login(base_url, email, password)
        existing = True
    except RuntimeError:
        token, _ = create_account(base_url)
        controls = get_controls(base_url, token)  # authenticated controls
        add_password_login(controls, token, email, password)
        existing = False

    controls = get_controls(base_url, token)

    if existing:
        pod_url = f"{base_url.rstrip('/')}/{pod_name}/"
        web_id = f"{pod_url}profile/card#me"
    else:
        pod = create_pod(controls, token, pod_name)
        pod_url, web_id = pod["pod"], pod["webId"]

    creds = create_client_credentials(controls, token, token_name, web_id)
    return PodIdentity(
        email=email,
        pod_url=pod_url,
        web_id=web_id,
        client_id=creds["id"],
        client_secret=creds["secret"],
    )
