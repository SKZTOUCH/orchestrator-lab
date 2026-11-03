# Lot B — local execution preflight (non-secret, lab only)

## Goal and scope

This **public** synthetic repository contains no private code. The preflight
checks whether the local GitHub CLI is authenticated as `skz-lab-agent`,
has access to `SKZTOUCH/orchestrator-lab`, **does not have authenticated access
to the seven private SKZTOUCH repositories**, and sees `main protected:true`.
It NEVER reads or prints tokens. This is a **read-only check**: no branch,
push, PR, merge, network daemon or Claude session is started by the script.

Preflight success is NOT certification of isolation: GitHub CLI identity is
not the same thing as the Claude Code cloud GitHub App identity, or other
available credentials. Do not grant lab workers production access.

## Recommended environment

Use an isolated Linux VM/container or a dedicated **non-administrator OS
account** on a supported host, with a fresh HOME and no host SSH keys,
production GitHub sessions, MCP connections, private project directories or
production tokens mounted. Keep the SKZTOUCH production login in a separate
OS user/environment. Do **not** use Windows 8.1 / old production VPS.

Claude Code officially supports modern macOS, Linux, Windows 10+ and
Windows Server 2019+; Git and GitHub CLI must be installed for this preflight.
Use official setup: https://code.claude.com/docs/en/setup and
https://cli.github.com/manual/gh_auth_login .

## Human setup and checks (NO commands containing secrets)

1. Enter your clean LAB-only OS environment and install **Git**, **Python3**,
   **GitHub CLI** and **Claude Code** using their official installation guides.
2. In that isolated OS session run `gh auth login` and authenticate GitHub as
   **skz-lab-agent**, not SKZTOUCH. Do not paste a personal access token in chat.
3. Clone **only the public** `SKZTOUCH/orchestrator-lab` repo using HTTPS.
   `cd orchestrator-lab` and `git switch pilot/lot-b-synthetic-fixture`.
4. Run `python3 scripts/lab_preflight.py`. STOP if any check prints BLOCK.
   Do not paste screenshots of authentication screens, tokens or recovery codes.
5. In this same environment sign in to **Claude Code** using the existing
   Claude subscription login (not Anthropic Console API/PAYG).
   Verify `ANTHROPIC_API_KEY` is **absent**: if present, Claude may choose
   billable API access over subscription. Do not enable unrelated MCP tools.
6. Enable the Claude Code local sandbox according to official docs with
   `/sandbox`; the OS identity/VM boundary remains necessary.
   Start a local mobile-linked session **only after** all human gates are met:
   `claude remote-control` (or `/remote-control` inside a local session).
   Open the linked session in the Claude mobile **Code** tab.

Official Remote Control docs: https://code.claude.com/docs/en/remote-control .
The CLI session continues running on the machine; phone is the interface.

## Explicit human gates STILL REQUIRED

- A controlled, non-destructive test proving direct push to `main` is denied
  for a **non-bypass** identity, and protected branch requirements observed.
- Independent evidence that Claude's actual process sees no production
  credentials or filesystem, and its GitHub access is restricted to LAB.
- Approval of a trusted publisher with LAB-only credentials to create a
  **draft PR**. The worker is never authorized to merge/deploy.
- Do not start the synthetic `mathops.py` correction before above
  checks pass. The expected RED baseline is GitHub Actions run
  https://github.com/SKZTOUCH/orchestrator-lab/actions/runs/41472348858 .

Status remains `LAB_PREFLIGHT_PREPARED`, not `LOT_B_FUNCTIONAL`.
