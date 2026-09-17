Additional instructions before you build:
1. Pin exact versions of @solid/community-server and all Python packages (package.json/package-lock + requirements.txt), and record them in RESULTS.md.
2. 01_share_revoke: describe the Bob's-copy result technically; phrase "does Bob become a controller under GDPR Art. 4(7)?" as an open question, not a conclusion.
3. 02_odrl_consent: scope the "no purpose channel" finding to CSS + WAC + Solid-OIDC; in the README note other Solid approaches that do carry purpose (e.g. Inrupt Access Grants, ODRL/DPV-based access control proposals) and whether they enforce or only record it. Don't overclaim.
4. 03_portability: note the identity problem applies when the WebID is hosted by the pod provider; if feasible, add a variant where the WebID is independent and only pim:storage changes, and compare. Use realistic-looking personal data (contacts, a licensed photo, notes linking to both) and include one container with its own ACL. For the pod-A wipe, add legal hooks to GDPR Art. 17 and EU Data Act Chapter VI (switching), phrased as open questions.
5. RESULTS.md: for each legal hook include the EUR-Lex link and mark quoted legal phrases as "to be verified".
6. List each check's expected outcome in the experiment README before running, so I can review the hypotheses.
7. Draw the figures only after the experiments have run, based on observed results. If a result is UNEXPECTED, the figure must reflect it.
8. outcome.md: note that my answers to the planning questions were made with advice from a separate Claude chat session, and list the figures as AI-generated.
9. Never commit .env, data/ or data2/. Keep the repo private.
10. Never delete or modify anything outside this project folder. If you're blocked by something you can't solve from the docs, stop and tell me instead of working around it silently.. /mattpocock-skills:grill-me
