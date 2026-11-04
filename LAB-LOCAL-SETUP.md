# Lot B — read-only LAB preflight (Linux local or Codespaces)

`SKZTOUCH/orchestrator-lab` is **public, synthetic-only**. No production code, tokens, VPS, broker, deployment or merge.

## Isolated Linux session (PC or VM)

1. Use a fresh **non-admin** OS user/VM without production worktrees, SSH keys, credential helpers, secrets or MCP connectors mounted. Do not use the production Windows VPS.
2. Install Python3, Git and GitHub CLI. In this isolated session alone, authenticate with `gh auth login` as `skz-lab-agent`. Clone only the public LAB repo over HTTPS.
3. Configure Git identity locally as `skz-lab-agent` and its verified GitHub **noreply** address. Never share authentication codes, tokens or private email addresses.
4. On the reviewed hardening branch, run `python3 -m unittest discover -s tests -p 'test_lab_preflight.py' -v` and `python3 scripts/lab_preflight.py`. Any BLOCK means STOP.

## Codespaces from Android

See [LAB-CODESPACES-PILOT.md](LAB-CODESPACES-PILOT.md). Codespaces supplies a default repo-scoped `GITHUB_TOKEN`. **Do not run `gh auth login` or set `GH_TOKEN` inside Codespaces.** Use `skz-lab-agent` as the GitHub account that creates the Codespace; verify account and repository context. Never print the token.

## Unresolved Human Gates

The preflight only checks the currently selected `gh` credential and some Git metadata. It does **not** prove complete OS isolation, Git/SSH push identity, GitHub App / Claude cloud scope, MCP scope, or actual branch-protection no-bypass behavior. Check these independently, confirm a trusted LAB-only publisher, and record explicit Human Gate approval in `orchestrator-os#9` **before spawning agents**.

Do not modify `mathops.py` on this security branch. The synthetic acceptance baseline remains deliberately RED (9 tests, 4 expected failures).

STATUS: `HARDENING_LOCAL_TESTS_ONLY`; `CODESPACES_RUNTIME_UNTESTED`; `AGENTS_BLOCKED`.
