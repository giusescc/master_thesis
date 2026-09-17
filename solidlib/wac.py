"""Web Access Control: discovering, reading and writing ``.acl`` resources.

Spec: https://solidproject.org/TR/wac (Draft CG Report v1.0.0, 2024-05-12)

* s.3.1 ACL Resource Discovery -- the ``Link: <...>; rel="acl"`` header.  We
  always follow that header rather than assuming the ``.acl`` suffix, because
  the suffix is a CSS convention, not a guarantee.  (Under an ACP
  configuration the same ``rel="acl"`` link points at a ``.acr`` instead --
  which is why the *target*, not the relation, is the reliable discriminator.)
* s.4.1 Access Objects -- ``acl:accessTo`` (this resource) versus
  ``acl:default`` (inherited by contained resources).
* s.4.2 Access Modes -- ``acl:Read``, ``acl:Write``, ``acl:Append``,
  ``acl:Control``.
* s.4.3 Access Subjects -- ``acl:agent`` (a specific WebID) versus
  ``acl:agentClass foaf:Agent`` (everybody, including the unauthenticated).
* s.6.1 ``wac-allow`` header -- the server advertising the permissions it will
  apply.  CSS emits it as ``WAC-Allow``; HTTP field names are case-insensitive.

Editing an ``.acl`` requires ``acl:Control`` on the subject resource, so only
the owner can grant or revoke.
"""

from __future__ import annotations

import re

from solidlib.session import SolidSession

ACL_PREFIXES = """@prefix acl: <http://www.w3.org/ns/auth/acl#>.
@prefix foaf: <http://xmlns.com/foaf/0.1/>.
"""


def acl_url(session: SolidSession, url: str) -> str | None:
    """Discover a resource's ACL via its ``Link: rel="acl"`` header."""
    response = session.head(url)
    return _link_target(response.headers.get("Link", ""), "acl")


def _link_target(link_header: str, relation: str) -> str | None:
    for match in re.finditer(r'<([^>]+)>\s*;\s*rel="([^"]+)"', link_header):
        target, rel = match.group(1), match.group(2)
        if rel == relation:
            return target
    return None


def read_acl(session: SolidSession, resource_url: str) -> tuple[int, str]:
    target = acl_url(session, resource_url)
    if target is None:
        return 0, ""
    response = session.get(target)
    return response.status_code, response.text


def write_acl(session: SolidSession, resource_url: str, turtle: str):
    """Replace a resource's ACL.  Requires ``acl:Control``."""
    target = acl_url(session, resource_url)
    if target is None:
        raise RuntimeError(f"No acl link advertised for {resource_url}")
    return session.put(target, turtle.encode("utf-8"), "text/turtle")


def parse_wac_allow(header: str | None) -> dict[str, set[str]]:
    """Parse ``WAC-Allow: user="read write",public="read"`` into a dict.

    This is the server's *advertised* permissions -- what it says it will allow.
    Experiments compare it against what the status codes show it actually
    enforces.
    """
    result: dict[str, set[str]] = {}
    if not header:
        return result
    for match in re.finditer(r'(\w+)\s*=\s*"([^"]*)"', header):
        group, modes = match.group(1), match.group(2)
        result[group] = {m for m in modes.split() if m}
    return result


# -- ACL document builders --------------------------------------------------


def owner_only(resource_url: str, owner_web_id: str) -> str:
    """An ACL granting the owner full control and nobody else anything."""
    return f"""{ACL_PREFIXES}
<#owner>
    a acl:Authorization;
    acl:agent <{owner_web_id}>;
    acl:accessTo <{resource_url}>;
    acl:mode acl:Read, acl:Write, acl:Control.
"""


def owner_plus_reader(resource_url: str, owner_web_id: str, reader_web_id: str) -> str:
    """Owner keeps control; one named agent additionally gets Read.

    This is the WAC expression of "Alice shares this file with Bob".
    """
    return f"""{ACL_PREFIXES}
<#owner>
    a acl:Authorization;
    acl:agent <{owner_web_id}>;
    acl:accessTo <{resource_url}>;
    acl:mode acl:Read, acl:Write, acl:Control.

<#reader>
    a acl:Authorization;
    acl:agent <{reader_web_id}>;
    acl:accessTo <{resource_url}>;
    acl:mode acl:Read.
"""


def container_owner_only(container_url: str, owner_web_id: str) -> str:
    """Owner-only ACL for a container, inherited by everything inside it.

    ``acl:default`` is what makes the rule apply to contained resources
    (WAC s.5.1, Effective ACL Resource).
    """
    return f"""{ACL_PREFIXES}
<#owner>
    a acl:Authorization;
    acl:agent <{owner_web_id}>;
    acl:accessTo <{container_url}>;
    acl:default <{container_url}>;
    acl:mode acl:Read, acl:Write, acl:Control.
"""
