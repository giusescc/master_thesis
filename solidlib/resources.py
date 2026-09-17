"""Reading and writing pod resources: Turtle, binaries and containers.

Container listing follows the Solid Protocol's containment model: a container's
representation is RDF whose ``ldp:contains`` triples name its children
(Solid Protocol s.4.2, Resource Containment).  We parse that with rdflib rather
than guessing at URL patterns.
"""

from __future__ import annotations

from rdflib import Graph, URIRef
from rdflib.namespace import Namespace

from solidlib.session import SolidSession

LDP = Namespace("http://www.w3.org/ns/ldp#")

TURTLE = "text/turtle"


def put_turtle(session: SolidSession, url: str, turtle: str, **kwargs):
    return session.put(url, turtle.encode("utf-8"), TURTLE, **kwargs)


def put_bytes(session: SolidSession, url: str, data: bytes, content_type: str, **kwargs):
    return session.put(url, data, content_type, **kwargs)


def create_container(session: SolidSession, url: str):
    """Create a container by PUTting its (trailing-slash) URL."""
    if not url.endswith("/"):
        raise ValueError(f"Container URLs must end with '/': {url}")
    return session.put(url, b"", TURTLE)


def get_text(session: SolidSession, url: str) -> tuple[int, str]:
    response = session.get(url)
    return response.status_code, response.text


def parse_turtle(text: str, base: str) -> Graph:
    graph = Graph()
    graph.parse(data=text, format="turtle", publicID=base)
    return graph


def list_container(session: SolidSession, url: str) -> list[str]:
    """Return the URLs a container says it contains (``ldp:contains``)."""
    response = session.get(url, headers={"accept": TURTLE})
    if not response.ok:
        return []
    graph = parse_turtle(response.text, url)
    return sorted(str(o) for o in graph.objects(URIRef(url), LDP.contains))


def walk(session: SolidSession, root: str) -> list[str]:
    """Depth-first listing of every resource under a container, inclusive.

    Auxiliary resources (``.acl``, ``.meta``) are deliberately *not* returned:
    they are not contained resources and must be migrated explicitly, which is
    itself one of the findings of experiment 03.
    """
    found: list[str] = []
    stack = [root]
    seen: set[str] = set()
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        found.append(current)
        if current.endswith("/"):
            stack.extend(list_container(session, current))
    return sorted(found)


def delete_recursive(session: SolidSession, root: str) -> list[tuple[str, int]]:
    """Delete everything under ``root``, deepest first, then ``root`` itself.

    Used by every experiment's cleanup so runs are repeatable.  A container
    cannot be deleted while it still has children, hence the ordering.
    """
    targets = sorted(walk(session, root), key=lambda u: (u.count("/"), len(u)), reverse=True)
    results = []
    for url in targets:
        response = session.delete(url)
        results.append((url, response.status_code))
    return results
