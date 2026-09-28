# ENVIRONMENT (Chapter 3)

Written by `npm run exp:setup` at **2026-09-24T14:16:28.665Z**. Git commit `7f2be9ac338318924c72084d85846bd4f0cc8a5e`.

## Node
- `node -v`: `v22.23.2` (pinned by `.nvmrc`: `22.23.2`)
- `npm -v`: `10.9.8`
- `npm ls --depth=0` (repo root):

```
solid-thesis-lab@1.0.0 /Users/giuseppesoccio/Desktop/THESIS/CODING/.claude/worktrees/revocation
└── @solid/community-server@7.2.0
```

- `npm ls --depth=0` (`ch3/phases/p4_comunica`):

```
not built yet
```

## Community Solid Server

### WAC on :3100 (`ch3/config/css-wac.json`, expiry config: default)

- Version CSS wrote at startup (`ModuleVersionVerifier` → `.internal/setup/current-server-version`): **7.2.0**
- Startup log lines (`ch3/.state/logs/css-wac.log`, git-ignored):

```
2026-09-24T14:16:24.427Z [Components.js] info: Initiating component discovery from /Users/giuseppesoccio/Desktop/THESIS/CODING/.claude/worktrees/revocation/node_modules/@solid/community-server/
2026-09-24T14:16:25.979Z [ServerInitializer] {Primary} info: Listening to server at http://localhost:3100/
```

### ACP on :3101 (`ch3/config/css-acp.json`, expiry config: default)

- Version CSS wrote at startup (`ModuleVersionVerifier` → `.internal/setup/current-server-version`): **7.2.0**
- Startup log lines (`ch3/.state/logs/css-acp.log`, git-ignored):

```
2026-09-24T14:16:27.099Z [Components.js] info: Initiating component discovery from /Users/giuseppesoccio/Desktop/THESIS/CODING/.claude/worktrees/revocation/node_modules/@solid/community-server/
2026-09-24T14:16:28.592Z [ServerInitializer] {Primary} info: Listening to server at http://localhost:3101/
```

Note: at log level `info`, CSS 7.2.0 prints no line containing its own version number. The startup log names the package directory it loaded (above); the version is the value CSS itself stored at startup, read from package.json in that directory.

## Python
- `uv --version`: `uv 0.11.28 (Homebrew 2026-07-07 aarch64-apple-darwin)`
- `uv run python --version`: `Python 3.12.13` (pinned by `.python-version` + `uv.lock`)

## OS
- `sw_vers`:

```
ProductName:		macOS
ProductVersion:		26.5.2
BuildVersion:		25F84
```

- `uname -a`: `Darwin Giuseppes-MacBook-Pro.local 25.5.0 Darwin Kernel Version 25.5.0: Tue Jun  9 22:28:17 PDT 2026; root:xnu-12377.121.10~1/RELEASE_ARM64_T8142 arm64`

## nginx (P2 caching proxy)
not used yet (P2 not built)

## Ollama (P6, P7)
- `ollama --version`: `not available (ollama not installed)`
- models: not used yet (P6 not built)
