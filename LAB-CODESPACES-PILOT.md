# Lot B — Codespaces mobile security runbook (NOT AUTHORIZED)

Scope: public synthetic `SKZTOUCH/orchestrator-lab` only. No production secrets, repos, agents, VPS, trading API, merge or deployment.

## Phone-first setup (Human Gate required before any Claude process)

1. In Android Chrome/Brave, sign in to GitHub as **skz-lab-agent**, not SKZTOUCH. Verify the GitHub avatar/account. Do not disturb the existing Claude cloud connection.
2. Review personal GitHub Codespaces quota and spending limit **before** creating a machine. Free personal accounts include 120 core-hours/month (60 active hours on 2 vCPU) and 15 GB-month storage. Keep paid spending at 0 and stop/delete unused environments. Quota remaining is account-dependent and not verified here.
3. In [LAB repo](https://github.com/SKZTOUCH/orchestrator-lab), use Code → Codespaces → choose the reviewed branch, select a 2-core machine and open in browser. Do not use `main`. Test Android browser usability; support is not an empirical phone test.
4. Use default HTTPS and its repo-scoped `GITHUB_TOKEN`. Do **not** run `gh auth login`, add a PAT, use SSH keys, or set `GH_TOKEN`. Do not enable dotfiles, account-level secrets, Settings Sync or unrelated MCP integrations. Reject extra repository permission prompts and inspect `devcontainer.json`.
5. On the **security hardening branch**, first run `python3 -m unittest discover -s tests -p 'test_lab_preflight.py' -v`; then `python3 scripts/lab_preflight.py`. It checks Codespaces context and the actual `gh` API identity, but **PASS is limited**. Git commit email configuration may need manual account-safe setup; no token or email output in issues.
6. Independently verify Git/SSH credential scope, OS files and mounts, Claude/GitHub App and MCP authorities. Prove a non-bypass direct push to `main` would be rejected using an approved harmless test plan (without changing `main`). This must be separate from merely observing `protected:true`.
7. Record sanitized evidence and obtain explicit owner Human Gate approval in [orchestrator-os#9](https://github.com/SKZTOUCH/orchestrator-os/issues/9). **STOP until then.**
8. Only once authorized: create an implementation branch from the synthetic fixture; Claude changes **mathops.py only**; independent Codex review on the exact SHA; CI verified green; trusted LAB-only publisher creates **draft PR**; HUMAN_GATE=PENDING; no merge/deployment.

## Hard limits

- Default Codespaces idle stop: 30 min; session max lifetime: 12 h; stopped instance retention by default 30 days. This is not a permanent AO host.
- Codespaces grants `GITHUB_TOKEN` by default; the hardened preflight allows it only for matching Codespaces context. A forged env context or another credential is outside its proof.
- Explicit authenticated HTTP 404 is a denial *signal* for that credential, not sufficient proof a private repo exists or that other credentials are isolated. 401/403/5xx/timeout are **BLOCK**, never success.
- No forwarded ports and no resident daemon; AO engine remains offline until a separate gate.
- Existing GitHub acceptance tests and SPEC are immutable; this hardening branch does not change them.

Official sources:
- https://docs.github.com/en/billing/concepts/product-billing/github-codespaces
- https://docs.github.com/en/codespaces/developing-in-a-codespace/default-environment-variables-for-your-codespace
- https://docs.github.com/en/codespaces/managing-your-codespaces/managing-repository-access-for-your-codespaces
- https://docs.github.com/en/codespaces/reference/security-in-github-codespaces
- https://docs.github.com/en/codespaces/about-codespaces/understanding-the-codespace-lifecycle

STATUS: `CODESPACES_PLAN_PREPARED` / `RUNTIME_UNTESTED` / `LOT_B_AGENTS_BLOCKED`.
