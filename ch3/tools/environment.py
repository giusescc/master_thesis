"""Write ``ch3/results/ENVIRONMENT.md``: every version the results depend on.

Run by ``npm run exp:setup`` after the servers are up. The current file is
replaced on each setup, and a copy is kept, never overwritten, as
``ch3/results/environment/<UTC timestamp>.md``, so each full run's environment
stays on record.

A tool that is missing is written as "not available" with the reason. It is
never silently skipped.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from ch3.lib.env import CH3, CONFIGS, LOGS, RAW, RESULTS, ROOT, STATE
from ch3.lib.jsonl import git_commit, utc_ms

NGINX_IMAGE_FILE = CH3 / "config" / "nginx" / "IMAGE"
OLLAMA_MODELS_FILE = CH3 / "config" / "ollama-models.txt"
P4_DIR = CH3 / "phases" / "p4_comunica"


def sh(cmd: list[str], cwd: Path = ROOT) -> str:
    try:
        out = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=60)
    except FileNotFoundError:
        return f"not available ({cmd[0]} not installed)"
    except subprocess.TimeoutExpired:
        return f"not available ({' '.join(cmd)} timed out)"
    text = (out.stdout + out.stderr).strip()
    if out.returncode != 0 and not text:
        return f"not available ({' '.join(cmd)} exited {out.returncode})"
    return text


def block(text: str) -> str:
    return f"```\n{text}\n```\n"


def css_section() -> str:
    parts = []
    for name, cfg in CONFIGS.items():
        log = LOGS / f"css-{name}.log"
        lines = log.read_text(errors="replace").splitlines() if log.exists() else []
        strip = lambda s: re.sub(r"\x1b\[[0-9;]*m", "", s)  # noqa: E731
        picked = [strip(l) for l in lines if "component discovery" in l or "Listening to server" in l]
        stored = STATE / f"data-{name}" / ".internal" / "setup" / "current-server-version$.json"
        version = json.loads(stored.read_text())["payload"] if stored.exists() else "not available"
        expiry = (LOGS / f"css-{name}.expiry").read_text().strip() if (LOGS / f"css-{name}.expiry").exists() else "?"
        parts.append(
            f"### {name.upper()} on :{cfg['port']} (`{cfg['config']}`, expiry config: {expiry})\n\n"
            f"- Version CSS wrote at startup (`ModuleVersionVerifier` → "
            f"`.internal/setup/current-server-version`): **{version}**\n"
            f"- Startup log lines (`ch3/.state/logs/css-{name}.log`, git-ignored):\n\n"
            + block("\n".join(picked) or "log not found")
        )
    note = (
        "Note: at log level `info`, CSS 7.2.0 prints no line containing its own version "
        "number. The startup log names the package directory it loaded (above); the version "
        "is the value CSS itself stored at startup, read from package.json in that directory.\n"
    )
    return "\n".join(parts) + "\n" + note


def nginx_section() -> str:
    if not NGINX_IMAGE_FILE.exists():
        return "not used yet (P2 not built)\n"
    image = NGINX_IMAGE_FILE.read_text().strip()
    digest = sh(["docker", "image", "inspect", "--format", "{{json .RepoDigests}} {{.Id}}", image])
    return f"- Pinned reference: `{image}`\n- `docker image inspect`: `{digest}`\n- Docker: `{sh(['docker', 'version', '--format', '{{.Server.Version}}'])}`\n"


def ollama_section() -> str:
    version = sh(["ollama", "--version"])
    out = f"- `ollama --version`: `{version}`\n"
    if OLLAMA_MODELS_FILE.exists():
        out += "- `ollama list` (model name, digest):\n\n" + block(sh(["ollama", "list"]))
        tags = sh(["curl", "-s", "http://127.0.0.1:11434/api/tags"])
        try:
            installed = {m["name"]: m["digest"] for m in json.loads(tags)["models"]}
        except (ValueError, KeyError):
            installed = {}
        out += "\n- Full sha256 digests (pinned in `config/ollama-models.txt` vs installed, from `/api/tags`):\n"
        for line in OLLAMA_MODELS_FILE.read_text().splitlines():
            if line.strip() and not line.startswith("#"):
                role, name, digest = line.split()
                got = installed.get(name, "not available")
                out += f"  - {role} `{name}`: pinned `{digest}`, installed `{got}` ({'match' if got == digest else 'MISMATCH'})\n"
    else:
        out += "- models: not used yet (P6 not built)\n"
    return out + "\n" + model_choice()


PLANNED_GENERATE_MODEL = "qwen2.5:7b-instruct"


def model_choice() -> str:
    """The planned vs used generation model, and what the raw files record.

    Tallies the ``models`` header line of every P6/P7 raw file on disk (counted
    and excluded alike), so a change of model would show up here.
    """
    seen: dict[tuple[str, str, str], int] = {}
    for path in sorted(RAW.glob("p[67]/*/*.jsonl")):
        with path.open(encoding="utf-8") as handle:
            line = next((json.loads(l) for l in handle if '"event": "models"' in l), None)
        key = (path.parts[-3], line["generate"]["name"], line["generate"]["digest"]) if line else (path.parts[-3], "no models line", "-")
        seen[key] = seen.get(key, 0) + 1
    out = (
        "### Model choice (P6, P7)\n\n"
        f"- Planned (Spec): `{PLANNED_GENERATE_MODEL}`. Used: `qwen2.5:3b` (Q4_K_M, 3.1B parameters).\n"
        "- Reason: the User's choice, on 2026-09-24, of the smallest size of the model "
        "(\"let's go with the, the smallest size version\"), confirmed as `qwen2.5:3b`. "
        "Recorded in `config/ollama-models.txt` and `HYPOTHESES.md` (P6).\n"
        "- What actually ran, from the `models` header line of every P6/P7 raw file on disk "
        "(counted and excluded files alike):\n"
    )
    for (phase, name, digest), n in sorted(seen.items()):
        out += f"  - {phase.upper()}: {n} raw files, generate `{name}` digest `{digest}`\n"
    if not seen:
        out += "  - no P6/P7 raw files yet\n"
    return out


def main() -> int:
    stamp = utc_ms()
    p4 = sh(["npm", "ls", "--depth=0"], cwd=P4_DIR) if (P4_DIR / "package.json").exists() else "not built yet"
    text = f"""# ENVIRONMENT (Chapter 3)

Written by `npm run exp:setup` at **{stamp}**. Git commit `{git_commit()}`.

## Node
- `node -v`: `{sh(['node', '-v'])}` (pinned by `.nvmrc`: `{(ROOT / '.nvmrc').read_text().strip() if (ROOT / '.nvmrc').exists() else 'missing'}`)
- `npm -v`: `{sh(['npm', '-v'])}`
- `npm ls --depth=0` (repo root):

{block(sh(['npm', 'ls', '--depth=0']))}
- `npm ls --depth=0` (`ch3/phases/p4_comunica`):

{block(p4)}
## Community Solid Server

{css_section()}
## Python
- `uv --version`: `{sh(['uv', '--version'])}`
- `uv run python --version`: `{sh(['uv', 'run', 'python', '--version'])}` (pinned by `.python-version` + `uv.lock`)

## OS
- `sw_vers`:

{block(sh(['sw_vers']))}
- `uname -a`: `{sh(['uname', '-a'])}`

## nginx (P2 caching proxy)
{nginx_section()}
## Ollama (P6, P7)
{ollama_section()}"""
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "ENVIRONMENT.md").write_text(text)
    history = RESULTS / "environment"
    history.mkdir(exist_ok=True)
    name = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%f")[:-3] + "Z.md"
    fd = os.open(history / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "w") as handle:
        handle.write(text)
    print(f"  wrote ch3/results/ENVIRONMENT.md (+ ch3/results/environment/{name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
