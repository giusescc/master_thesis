I'm a master's student starting the coding part of my thesis on Solid (supervised by Prof. Simon Mayer, HSG). I have never used Solid. Do everything yourself from this empty folder; only stop to ask me if something truly requires my input. Explain what you're doing in plain language as you go.

GOAL
Set up a local Solid environment and run small, reproducible experiments on PORTABILITY and CONSENT, so I can later analyse them against EU law (GDPR Art. 20, Data Act, DMA Art. 6(9)). The key question in every experiment: what does the protocol/server actually ENFORCE vs. what is only DECLARED?

SETUP (do all of this yourself)
1. Check Node (18+), Python (3.10+) and git; tell me if something is missing and how to install it.
2. git init, create .gitignore (.venv, .env, data/, data2/, __pycache__), Python venv, install: SolidClientCredentials requests rdflib python-dotenv pytest.
3. Start the Community Solid Server in the background with file storage and keep it running:
   npx @solid/community-server -p 3000 -c @css:config/file.json -f ./data
   Docs: https://communitysolidserver.github.io/CommunitySolidServer/latest/
4. Using the CSS account API (not the browser), create two accounts with pods "alice" and "bob", and create client credentials for each WebID.
   Client credentials docs: https://communitysolidserver.github.io/CommunitySolidServer/latest/usage/client-credentials/
   Save them in .env (ISSUER, ALICE_CLIENT_ID/SECRET, BOB_CLIENT_ID/SECRET). Never print or commit secrets.
5. Write a CLAUDE.md summarising this project, the environment, the users and the rules below, so future sessions have context.
6. Create a start.sh script that restarts the server(s) so I can resume later with one command.

CODE STRUCTURE
- solidlib/: authenticated session per user, read/write/delete Turtle resources, list containers, read/write WAC .acl files.
- experiments/NN_name/: one folder per experiment, each with a run script and a README.md (goal, steps, result in plain language, spec references).
- Every experiment sets up its state, acts, checks the outcome as each user, prints a PASS/FAIL table, and cleans up so it can be re-run.
- If something isn't supported by the server or the specs, say so explicitly instead of faking it. Those gaps are my thesis findings.

EXPERIMENTS (run each one, then show me the results before moving on)
00_hello_pod: Alice writes a resource and reads it back; Bob is denied; an unauthenticated request is denied.
01_share_revoke: Alice grants Bob read via WAC; Bob reads; Alice revokes; Bob is denied. Does revocation affect a copy Bob saved earlier?
02_odrl_consent: Alongside the WAC rule, attach an ODRL 2.2 policy using DPV terms ("Bob may read for purpose ScientificResearch, no redistribution"). Test what the server enforces vs. what is only metadata.
03_portability: Start a second CSS on port 3001 (./data2) with user alice2. Migrate Alice's data from pod A to pod B. Report what survives: data, internal links, ACLs, ODRL policies, and whether links pointing to the old location still work.

SPECS TO RELY ON (cite sections in comments/READMEs)
- Solid Protocol: https://solidproject.org/TR/protocol
- Web Access Control: https://solidproject.org/TR/wac
- ODRL 2.2: https://www.w3.org/TR/odrl-model/
- DPV: https://w3id.org/dpv

FINISH
Write RESULTS.md: one table across all experiments (enforced / declared only / not supported) plus a short plain-language summary I can use as a starting point for my thesis chapter. Commit everything with clear messages.. Use subagents if needed. My github repo is https://github.com/giusescc/master_thesis (it's empty).  open a pr when done. Also open a folder for each prompt that I give you and save each prompt numbering it. /mattpocock-skills:grill-me
