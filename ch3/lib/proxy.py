"""Start/stop the P2 nginx caching proxy (Docker, pinned by digest), bound to 127.0.0.1."""

from __future__ import annotations

import subprocess
import time

import requests

from ch3.lib.env import CH3, LOGS

IMAGE = (CH3 / "config" / "nginx" / "IMAGE").read_text().strip()

PROXIES = {
    "proxyA": {"conf": "nginx-A.conf", "ports": {"wac": 3180, "acp": 3181}},
    "proxyB": {"conf": "nginx-B.conf", "ports": {"wac": 3182, "acp": 3183}},
}


def name(variant: str) -> str:
    return f"ch3-nginx-{variant.lower()}"


def start(variant: str) -> None:
    spec = PROXIES[variant]
    stop(variant)
    ports = [arg for p in spec["ports"].values() for arg in ("-p", f"127.0.0.1:{p}:{p}")]
    subprocess.run(
        ["docker", "run", "-d", "--name", name(variant), *ports,
         "-v", f"{CH3 / 'config' / 'nginx' / spec['conf']}:/etc/nginx/nginx.conf:ro", IMAGE],
        check=True, capture_output=True,
    )
    for port in spec["ports"].values():
        for _ in range(50):
            try:
                requests.get(f"http://127.0.0.1:{port}/", timeout=2)
                break
            except requests.RequestException:
                time.sleep(0.2)
        else:
            raise RuntimeError(f"nginx {variant} did not come up on :{port}")


def stop(variant: str) -> None:
    logs = subprocess.run(["docker", "logs", name(variant)], capture_output=True, text=True)
    if logs.returncode == 0:
        LOGS.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        (LOGS / f"{name(variant)}-{stamp}.log").write_text(logs.stdout + logs.stderr)
    subprocess.run(["docker", "rm", "-f", name(variant)], capture_output=True)


def proxy_base(variant: str, config: str) -> str:
    return f"http://localhost:{PROXIES[variant]['ports'][config]}/"
