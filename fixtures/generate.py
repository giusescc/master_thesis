"""Generate the synthetic dataset that experiment 03 migrates.

Everything here is FICTIONAL. The people do not exist, the addresses do not
exist, and the image depicts nobody. That is deliberate: building a
demonstration about data protection on a real person's data would be
self-defeating.

The binary is generated programmatically rather than downloaded, so that:

* ``./start.sh --reset`` needs no network access and cannot rot,
* the bytes are identical on every machine, and
* there is no third-party licensing question about the file itself.

Note that the image carries a licence statement *inside the pod*
(``media/portrait.ttl``). That licence is **part of the test scenario** -- it is
content being migrated, and whether it survives migration is one of the things
experiment 03 observes. It is not a legal statement about this repository.
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent


def make_png(width: int = 64, height: int = 64) -> bytes:
    """A small deterministic PNG: a two-channel gradient, no external deps.

    Written by hand rather than with Pillow so the lab has one fewer dependency
    and the bytes are byte-for-byte reproducible.
    """
    rows = bytearray()
    for y in range(height):
        rows.append(0)  # PNG filter type 0 (None) for this scanline
        for x in range(width):
            rows += bytes((x * 4 % 256, y * 4 % 256, 128))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)  # 8-bit RGB
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(bytes(rows), 9))
        + chunk(b"IEND", b"")
    )


def main() -> int:
    target = HERE / "portrait.png"
    target.write_bytes(make_png())
    print(f"wrote {target} ({target.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
