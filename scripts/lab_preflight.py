#!/usr/bin/env python3
"""Read-only LAB GitHub identity gate. Never prints tokens or secret values.

Run *locally* in a fresh, unprivileged OS account/VM with GitHub CLI configured
as skz-lab-agent. This is a GitHub CLI check, NOT an OS sandbox attestation.
"""
import os
from pathlib import Path
import subprocess
import sys

EXPECTED_USER = "skz-lab-agent"
EXPECTED_REPO = "SKZTOUCH/orchestrator-lab"
PRIVATE_REPOS = (
    "orchestrator-os", "cockpit-trading-os", "cockpit-ai-orchestrator",
    "life-os", "super-cadets", "skz-agent-pilot", "trading-os",
)
FORBIDDEN_ENV = (
    "GH_TOKEN", "GITHUB_TOKEN", "GH_ENTERPRISE_TOKEN",
    "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY", "SSH_AUTH_SOCK", "GIT_ASKPASS",
    "SSH_ASKPASS", "GIT_SSH_COMMAND",
)


def call(*args):
    try:
        return subprocess.run(args, capture_output=True, text=True,
                              stdin=subprocess.DEVNULL, timeout=20, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None


def read_ok(*args):
    proc = call(*args)
    return proc.stdout.strip() if proc and proc.returncode == 0 else None


def check(name, passed):
    print(("[PASS] " if passed else "[BLOCK] ") + name)
    return passed


def main():
    ok = True
    if hasattr(os, "geteuid"):
        ok &= check("Execution is not root", os.geteuid() != 0)
    present = [key for key in FORBIDDEN_ENV if os.environ.get(key)]
    ok &= check("No inherited API keys, PATs or SSH agent env (names only)",
                not present)
    if present:
        print("  Clear these env variable NAMES from the lab session: " +
              ", ".join(present))

    # Never invoke gh if the shell environment has an overriding GH_TOKEN.
    if present:
        print("BLOCKED: clear inherited credentials before GitHub checks.")
        return 2

    user = read_ok("gh", "api", "user", "--jq", ".login")
    ok &= check("GitHub CLI identity exactly skz-lab-agent",
                user == EXPECTED_USER)
    if user != EXPECTED_USER:
        print("BLOCKED: do not run Claude or any git push.")
        return 2

    can_push = read_ok("gh", "api", f"repos/{EXPECTED_REPO}",
                       "--jq", ".permissions.push")
    ok &= check("LAB repository has write permission", can_push == "true")

    protected = read_ok("gh", "api", f"repos/{EXPECTED_REPO}/branches/main",
                        "--jq", ".protected")
    ok &= check("LAB main reports protected=true", protected == "true")

    # A private repository MUST be inaccessible to this worker's gh identity.
    # gh API access returning 404 (or other nonzero status) is expected here.
    for private in PRIVATE_REPOS:
        result = call("gh", "api", f"repos/SKZTOUCH/{private}",
                      "--jq", ".full_name")
        inaccessible = result is not None and result.returncode != 0
        ok &= check(f"No authenticated access to private {private}",
                    inaccessible)

    root = read_ok("git", "rev-parse", "--show-toplevel")
    remote = read_ok("git", "remote", "get-url", "origin")
    allowed = {
        "https://github.com/SKZTOUCH/orchestrator-lab.git",
        "https://github.com/SKZTOUCH/orchestrator-lab",
        "git@github.com:SKZTOUCH/orchestrator-lab.git",
    }
    ok &= check("Working inside a Git checkout", root is not None
                and Path(root).exists())
    ok &= check("Only LAB origin is configured",
                remote in allowed)
    remotes = read_ok("git", "remote")
    ok &= check("Only the origin remote exists", remotes == "origin")

    print("RESULT=" + ("GH_CLI_PREFLIGHT_PASS" if ok
                       else "GH_CLI_PREFLIGHT_BLOCKED"))
    print("NOTE: this does NOT verify OS isolation, other GitHub Apps, "
          "MCP connections or an effective direct-push denial.")
    print("NO agent execution is authorized solely by this result.")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
