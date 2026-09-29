# ENVIRONMENT (Chapter 3)

Written by `npm run exp:setup` at **2026-09-29T07:17:06.254Z**. Git commit `567915a31f6f6515792b81860327e5840e72333b`.

## Node
- `node -v`: `v22.23.2` (pinned by `.nvmrc`: `22.23.2`)
- `npm -v`: `10.9.8`
- `npm ls --depth=0` (repo root):

```
solid-thesis-lab@1.0.0 /Users/giuseppesoccio/Desktop/THESIS/CODING/.claude/worktrees/closeout
└── @solid/community-server@7.2.0
```

- `npm ls --depth=0` (`ch3/phases/p4_comunica`):

```
ch3-p4-comunica@1.0.0 /Users/giuseppesoccio/Desktop/THESIS/CODING/.claude/worktrees/closeout/ch3/phases/p4_comunica
├── @comunica/query-sparql-link-traversal-solid@0.8.0
└── jose@6.2.12
```

## Community Solid Server

### WAC on :3100 (`ch3/config/css-wac.json`, expiry config: default)

- Version CSS wrote at startup (`ModuleVersionVerifier` → `.internal/setup/current-server-version`): **7.2.0**
- Startup log lines (`ch3/.state/logs/css-wac.log`, git-ignored):

```
2026-09-29T07:16:57.232Z [Components.js] info: Initiating component discovery from /Users/giuseppesoccio/Desktop/THESIS/CODING/.claude/worktrees/closeout/node_modules/@solid/community-server/
2026-09-29T07:17:00.240Z [ServerInitializer] {Primary} info: Listening to server at http://localhost:3100/
```

### ACP on :3101 (`ch3/config/css-acp.json`, expiry config: default)

- Version CSS wrote at startup (`ModuleVersionVerifier` → `.internal/setup/current-server-version`): **7.2.0**
- Startup log lines (`ch3/.state/logs/css-acp.log`, git-ignored):

```
2026-09-29T07:17:00.912Z [Components.js] info: Initiating component discovery from /Users/giuseppesoccio/Desktop/THESIS/CODING/.claude/worktrees/closeout/node_modules/@solid/community-server/
2026-09-29T07:17:04.062Z [ServerInitializer] {Primary} info: Listening to server at http://localhost:3101/
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
- Pinned reference: `nginx:1.28-alpine@sha256:a8b39bd9cf0f83869a2162827a0caf6137ddf759d50a171451b335cecc87d236`
- `docker image inspect`: `["nginx@sha256:a8b39bd9cf0f83869a2162827a0caf6137ddf759d50a171451b335cecc87d236"] sha256:a8b39bd9cf0f83869a2162827a0caf6137ddf759d50a171451b335cecc87d236`
- Docker: `29.7.2`

## Ollama (P6, P7)
- `ollama --version`: `ollama version is 0.34.4`
- `ollama list` (model name, digest):

```
NAME                       ID              SIZE      MODIFIED     
nomic-embed-text:latest    0a109f422b47    274 MB    22 hours ago    
qwen2.5:3b                 357c53fb659c    1.9 GB    22 hours ago
```

- Full sha256 digests (pinned in `config/ollama-models.txt` vs installed, from `/api/tags`):
  - embed `nomic-embed-text:latest`: pinned `0a109f422b47e3a30ba2b10eca18548e944e8a23073ee3f3e947efcf3c45e59f`, installed `0a109f422b47e3a30ba2b10eca18548e944e8a23073ee3f3e947efcf3c45e59f` (match)
  - generate `qwen2.5:3b`: pinned `357c53fb659c5076de1d65ccb0b397446227b71a42be9d1603d46168015c9e4b`, installed `357c53fb659c5076de1d65ccb0b397446227b71a42be9d1603d46168015c9e4b` (match)

### Model choice (P6, P7)

- Planned (Spec): `qwen2.5:7b-instruct`. Used: `qwen2.5:3b` (Q4_K_M, 3.1B parameters).
- Reason: the User's choice, on 2026-09-24, of the smallest size of the model ("let's go with the, the smallest size version"), confirmed as `qwen2.5:3b`. Recorded in `config/ollama-models.txt` and `HYPOTHESES.md` (P6).
- What actually ran, from the `models` header line of every P6/P7 raw file on disk (counted and excluded files alike):
  - P6: 45 raw files, generate `qwen2.5:3b` digest `357c53fb659c5076de1d65ccb0b397446227b71a42be9d1603d46168015c9e4b`
  - P7: 160 raw files, generate `qwen2.5:3b` digest `357c53fb659c5076de1d65ccb0b397446227b71a42be9d1603d46168015c9e4b`

_This "Model choice" subsection was added by hand on 2026-09-29, without rerunning `exp:setup` (which would restart the lab and replace the environment recorded above). It is the text `ch3/tools/environment.py` now writes here on every setup._
