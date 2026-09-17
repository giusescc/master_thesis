"""Description resources: attaching RDF metadata *about* a resource.

Solid Protocol s.4.3.2 (Description Resource).  Every resource has one; it is
discovered through the ``Link: <...>; rel="describedby"`` header on the subject
resource.  CSS's convention is ``<resource>.meta``, but the header is the
contract and the convention is not.

Three CSS behaviours matter for experiment 02 and are encoded here:

1. Description resources **cannot be created or deleted** directly -- they
   always exist.  ``PUT`` and ``DELETE`` are refused by design.
2. They can only be modified with **N3 PATCH**.
3. A ``PUT`` to the *subject* resource **resets** its description resource,
   unless the client sends ``Link: <...>; rel="preserve"``.  That is why an
   ordinary data update can silently discard an attached policy -- the finding
   experiment 02 tests directly.

Authorization is inherited from the subject resource (unlike ``.acl``, which
requires ``acl:Control``), so whoever may write the data may write its
description.
"""

from __future__ import annotations

from solidlib.session import SolidSession
from solidlib.wac import _link_target


def meta_url(session: SolidSession, url: str) -> str | None:
    """Discover a resource's description resource (``rel="describedby"``)."""
    response = session.head(url)
    return _link_target(response.headers.get("Link", ""), "describedby")


def read_meta(session: SolidSession, resource_url: str) -> tuple[int, str]:
    target = meta_url(session, resource_url)
    if target is None:
        return 0, ""
    response = session.get(target, headers={"accept": "text/turtle"})
    return response.status_code, response.text


def insert_triples(session: SolidSession, resource_url: str, triples: str):
    """Insert triples into a resource's description resource via N3 Patch."""
    target = meta_url(session, resource_url)
    if target is None:
        raise RuntimeError(f"No describedby link advertised for {resource_url}")
    body = (
        "@prefix solid: <http://www.w3.org/ns/solid/terms#>.\n"
        "<> a solid:InsertDeletePatch;\n"
        f"solid:inserts {{ {triples} }}.\n"
    )
    return session.patch_n3(target, body)


def delete_triples(session: SolidSession, resource_url: str, triples: str):
    target = meta_url(session, resource_url)
    if target is None:
        raise RuntimeError(f"No describedby link advertised for {resource_url}")
    body = (
        "@prefix solid: <http://www.w3.org/ns/solid/terms#>.\n"
        "<> a solid:InsertDeletePatch;\n"
        f"solid:deletes {{ {triples} }}.\n"
    )
    return session.patch_n3(target, body)


def put_preserving_meta(session: SolidSession, url: str, data, content_type: str):
    """``PUT`` a resource while explicitly preserving its description resource.

    Without the ``rel="preserve"`` link CSS discards the description resource on
    every write.  The workaround is entirely voluntary and client-side: a client
    that does not know to send this header destroys the metadata silently.
    """
    target = meta_url(session, url)
    headers = {"link": f'<{target}>; rel="preserve"'} if target else {}
    return session.put(url, data, content_type, headers=headers)
