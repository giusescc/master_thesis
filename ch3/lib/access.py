"""Grant and revoke Read, under WAC (``.acl``) or ACP (``.acr``), one interface.

The pattern is identical under both configs. Each resource gets its own
access-control document naming exactly the agents who may read it. "Revoke"
means alice replaces that document with one that no longer names the agent.

* WAC (https://solidproject.org/TR/wac): a resource's own ``.acl`` replaces
  inheritance, so it must name alice (the owner) as well as the readers.
* ACP (https://solidproject.org/TR/acp): the pod-root ACR that CSS 7.2.0 writes
  gives the owner full access to every member through
  ``acp:memberAccessControl``. A resource's ACR therefore only needs the reader
  policy; alice keeps Control through inheritance.

The document's URL is discovered from ``Link: rel="acl"``. Under ACP, CSS uses
the same relation to point at the ``.acr``.
"""

from __future__ import annotations

import re

from ch3.lib.agents import Agent


def acl_link(alice: Agent, url: str) -> str:
    response = alice.request("HEAD", url)
    for target, rel in re.findall(r'<([^>]+)>\s*;\s*rel="([^"]+)"', response.headers.get("Link", "")):
        if rel == "acl":
            return target
    raise RuntimeError(f"no rel=acl link on {url} (HTTP {response.status_code})")


def wac_document(url: str, owner: str, readers: list[str], mode: str = "acl:Read",
                 container: bool = False) -> str:
    default = f"\n    acl:default <{url}>;" if container else ""
    doc = f"""@prefix acl: <http://www.w3.org/ns/auth/acl#>.

<#owner>
    a acl:Authorization;
    acl:agent <{owner}>;
    acl:accessTo <{url}>;{default}
    acl:mode acl:Read, acl:Write, acl:Control.
"""
    if readers:
        agents = ", ".join(f"<{r}>" for r in readers)
        doc += f"""
<#readers>
    a acl:Authorization;
    acl:agent {agents};
    acl:accessTo <{url}>;
    acl:mode {mode}.
"""
    return doc


def acp_document(url: str, readers: list[str], mode: str = "acl:Read") -> str:
    doc = f"""@prefix acl: <http://www.w3.org/ns/auth/acl#>.
@prefix acp: <http://www.w3.org/ns/solid/acp#>.

<#acr>
    a acp:AccessControlResource;
    acp:resource <{url}>"""
    if not readers:
        return doc + ".\n"
    matchers = ",\n        ".join(f"[ a acp:Matcher; acp:agent <{r}> ]" for r in readers)
    return doc + f""";
    acp:accessControl <#readers>.

<#readers>
    a acp:AccessControl;
    acp:apply [
        a acp:Policy;
        acp:allow {mode};
        acp:anyOf
        {matchers}
    ].
"""


def document(config: str, url: str, owner: str, readers: list[str], mode: str = "acl:Read",
             container: bool = False) -> str:
    if config == "wac":
        return wac_document(url, owner, readers, mode, container)
    return acp_document(url, readers, mode)


def set_readers(alice: Agent, url: str, readers: list[str], mode: str = "acl:Read",
                container: bool = False):
    """Replace the access-control document of ``url``. Returns (doc_url, body, response)."""
    target = acl_link(alice, url)
    body = document(alice.config, url, alice.web_id, readers, mode, container)
    response = alice.put(target, body, "text/turtle")
    if response.status_code not in (200, 201, 204, 205):
        raise RuntimeError(f"writing {target} failed: HTTP {response.status_code} {response.text[:300]}")
    return target, body, response
