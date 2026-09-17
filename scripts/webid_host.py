"""A deliberately dumb static host for a provider-independent WebID.

Experiment 03 asks whether portability improves when the WebID lives somewhere
that is *not* either pod provider.  To test that, Alice's WebID document has to
be served from a third origin that is neither pod server -- so this is a plain
static file server with no Solid features whatsoever, which is precisely the
point: an independent WebID needs nothing more than an HTTP server that returns
Turtle.

Caveat recorded here and in the experiment README: three ports on ``localhost``
*simulate* three independent origins.  They are not separate providers, and
real-world DNS, TLS, CORS and organisational boundaries are out of scope.
"""

from __future__ import annotations

import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "webid"


class TurtleHandler(SimpleHTTPRequestHandler):
    """Serves ``.ttl`` as ``text/turtle`` and allows cross-origin reads."""

    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".ttl": "text/turtle",
    }

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("webid-host: " + (fmt % args) + "\n")


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3002
    ROOT.mkdir(parents=True, exist_ok=True)
    handler = partial(TurtleHandler, directory=str(ROOT))
    server = ThreadingHTTPServer(("localhost", port), handler)
    sys.stderr.write(f"webid-host: serving {ROOT} on http://localhost:{port}/\n")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
