# Lot B — Claude Code mission entrypoint (NOT ACTIVE until external Human Gate)

**This is a public, synthetic-only repository; no private code or secrets.**
Master control issue: https://github.com/SKZTOUCH/orchestrator-os/issues/9

**Prerequisite:** owner has verified effective `main` branch protection and identities isolated to this laboratory; GitHub Actions baseline is RED as expected. **Until then STOP.**

Once explicitly authorized:
1. Work on a new branch based on `pilot/lot-b-synthetic-fixture`, not on `main`; correct only `mathops.py`.
2. Run `python3 -m unittest discover -s tests -p 'test_*.py' -v` in the isolated sandbox.
3. Create evidence of a distinct Claude Code implementation session; do not provide secrets in its logs.
4. Hand the exact code diff and SHA to Codex for independent read-only review.
5. If Codex finds a reproducible defect, fix it, rerun tests/CI, and seek a fresh review.
6. A trusted separate GitHub publisher (not the worker's general production identity) may open a draft PR; no merge.
7. Report PR URL, GitHub CI run, two distinct session IDs, baseline and candidate SHA, daemon restart evidence and smartphone initiation if done. Mark untested steps as untested.
8. Stop at `HUMAN_GATE=PENDING`; never automatically merge or deploy.

Do not use a production GitHub token, Windows Administrator, VPS MT5, trading API, Council V2 or billable API calls.
