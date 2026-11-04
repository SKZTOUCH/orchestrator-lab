#!/usr/bin/env python3
"""Fail-closed LAB-only credential preflight; read-only, no secret contents printed.

Checks the credential *visible to gh*, not every possible Git/GitHub credential.
This is not an OS / Claude Code cloud / MCP isolation attestation.
"""
import json
import os
from pathlib import Path
import re
import subprocess
import sys

EXPECTED_USER = "skz-lab-agent"
EXPECTED_REPO = "SKZTOUCH/orchestrator-lab"
PRIVATE_REPOS = (
    "orchestrator-os", "cockpit-trading-os", "cockpit-ai-orchestrator",
    "life-os", "super-cadets", "skz-agent-pilot", "trading-os",
)
FORBIDDEN_ENV = (
    "GH_TOKEN", "GH_ENTERPRISE_TOKEN", "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY",
    "SSH_AUTH_SOCK", "GIT_ASKPASS", "SSH_ASKPASS", "GIT_SSH_COMMAND",
    "GIT_CONFIG_COUNT", "GIT_CONFIG_PARAMETERS", "GIT_CONFIG_GLOBAL",
    "GIT_CONFIG_SYSTEM", "GIT_CONFIG_NOSYSTEM", "GIT_CREDENTIAL_HELPER",
)
HTTP_LINE = re.compile(r"^HTTP/\S+\s+([1-5]\d\d)(?:\s|$)", re.M)
ORIGIN = f"https://github.com/{EXPECTED_REPO}"


def call(*args):
    try:
        return subprocess.run(args, capture_output=True, text=True,
                              stdin=subprocess.DEVNULL, timeout=20, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None


def read_ok(*args):
    result = call(*args)
    return result.stdout.strip() if result and result.returncode == 0 else None


def api(path):
    """Return (HTTP status, JSON body). None status means indeterminate / error.

    Parse an explicit HTTP response status, never infer 404 from process failure.
    Discard all error bodies and headers from user-visible output.
    """
    result = call("gh", "api", "--include", path)
    if result is None:
        return None, None
    matches = HTTP_LINE.findall(result.stdout)
    if len(matches) != 1:
        return None, None  # redirects / proxy / malformed response need review
    status = int(matches[0])
    if (status < 400 and result.returncode != 0) or (status >= 400 and result.returncode == 0):
        return None, None
    try:
        body = json.loads(re.split(r"\r?\n\r?\n", result.stdout)[-1])
    except (ValueError, TypeError):
        body = None
    return status, body


def check(label, result):
    print(("[PASS] " if result else "[BLOCK] ") + label)
    return bool(result)


def env_gate():
    codespace = os.environ.get("CODESPACES") == "true"
    present = [k for k in FORBIDDEN_ENV if os.environ.get(k)]
    if os.environ.get("GITHUB_TOKEN") and not codespace:
        present.append("GITHUB_TOKEN")
    ok = check("No unexpected inherited credential / Git override variables", not present)
    if present:
        print("  Variables to clear (names only): " + ", ".join(present))

    if codespace:
        ok &= check("Codespaces identity and repository context match LAB", all((
            os.environ.get("GITHUB_REPOSITORY") == EXPECTED_REPO,
            os.environ.get("GITHUB_USER") == EXPECTED_USER,
            os.environ.get("GITHUB_SERVER_URL") == "https://github.com",
            os.environ.get("GITHUB_TOKEN") is not None,
            os.environ.get("CODESPACE_NAME") is not None,
        )))
    else:
        ok &= check("No unrecognized Codespaces context", not os.environ.get("CODESPACES"))
    host = os.environ.get("GH_HOST")
    ok &= check("GitHub host is github.com", host in (None, "github.com"))
    return ok


def devcontainer_gate(root):
    """Reject workspace-declared extra Codespaces repo grants.

    Absence of a request in a repo config does NOT verify account-level
    Codespaces secrets, other credentials or MCP tools.
    """
    ok = True
    for path in (Path(root) / "devcontainer.json",
                 Path(root) / ".devcontainer" / "devcontainer.json"):
        if not path.exists():
            continue
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
            # JSONC (comments) intentionally unsupported: fail closed.
            grants = doc.get("customizations", {}).get("codespaces", {}).get("repositories", {})
            allowed = isinstance(grants, dict) and not grants
        except (OSError, UnicodeError, ValueError, AttributeError):
            allowed = False
        ok &= check(f"No extra Codespaces repo grants in {path.name}", allowed)
    return bool(ok)


def git_gate():
    root = read_ok("git", "rev-parse", "--show-toplevel")
    inside = root is not None and Path(root).is_dir()
    ok = check("Inside a Git checkout", inside)
    if not inside:
        return False
    fetch = read_ok("git", "remote", "get-url", "origin")
    push = read_ok("git", "remote", "get-url", "--push", "origin")
    remotes = read_ok("git", "remote")
    ok &= check("Only HTTPS LAB origin is configured for fetch AND push", all((
        fetch in (ORIGIN, ORIGIN + ".git"),
        push in (ORIGIN, ORIGIN + ".git"),
        remotes == "origin",
    )))
    rewrites = call("git", "config", "--show-origin", "--get-regexp",
                    r"^url\..*\.(insteadOf|pushInsteadOf)$")
    # The normal return code 1 means no matching config; return code 0 means present.
    ok &= check("No Git URL rewriting of fetch/push targets", rewrites is not None
                and rewrites.returncode == 1)
    author = read_ok("git", "config", "--get", "user.name")
    email = read_ok("git", "config", "--get", "user.email")
    normalized = bool(email and re.fullmatch(
        r"(?:\d+\+)?skz-lab-agent@users\.noreply\.github\.com", email, re.I))
    ok &= check("Git commit identity configured as LAB account", author == EXPECTED_USER
                and normalized)
    env_author = os.environ.get("GIT_AUTHOR_EMAIL") or os.environ.get("GIT_COMMITTER_EMAIL")
    env_names = [os.environ.get("GIT_AUTHOR_NAME"), os.environ.get("GIT_COMMITTER_NAME")]
    ok &= check("No conflicting Git author / committer overrides", all((
        not env_author or bool(re.fullmatch(
            r"(?:\d+\+)?skz-lab-agent@users\.noreply\.github\.com", env_author, re.I)),
        all(not name or name == EXPECTED_USER for name in env_names),
    )))
    ok &= devcontainer_gate(root)
    return bool(ok)


def main():
    ok = True
    if hasattr(os, "geteuid"):
        ok &= check("Execution is not root", os.geteuid() != 0)
    # Env mismatch => stop *before* invoking the gh process.
    if not env_gate():
        print("RESULT=GH_CLI_PREFLIGHT_BLOCKED (environment)")
        return 2
    user_status, user = api("user")
    if not check("GitHub API identity exactly LAB user (HTTP 200)",
                 user_status == 200 and isinstance(user, dict)
                 and user.get("login") == EXPECTED_USER):
        print("RESULT=GH_CLI_PREFLIGHT_BLOCKED (identity)")
        return 2
    status, repo = api(f"repos/{EXPECTED_REPO}")
    ok &= check("LAB authenticated access has push=true", status == 200
                and isinstance(repo, dict)
                and repo.get("full_name") == EXPECTED_REPO
                and repo.get("permissions", {}).get("push") is True)
    status, branch = api(f"repos/{EXPECTED_REPO}/branches/main")
    ok &= check("LAB main reports protected=true", status == 200
                and isinstance(branch, dict) and branch.get("protected") is True)
    for private in PRIVATE_REPOS:
        status, _ = api(f"repos/SKZTOUCH/{private}")
        # A validated HTTP 404 is a DENIAL SIGNAL for this actor, not proof
        # of overall isolation, or of repository existence. Require external
        # independent existence inventory and separate credential checks.
        ok &= check(f"Private repository denies this gh credential (HTTP 404): {private}",
                    status == 404)
    ok &= git_gate()
    print("RESULT=" + ("GH_CLI_PREFLIGHT_PASS_LIMITED" if ok
                       else "GH_CLI_PREFLIGHT_BLOCKED"))
    print("NOTE: HTTP 404 only confirms denial signal for THIS gh credential; "
          "independent repo-existence evidence is required.")
    print("NOTE: not an OS, filesystem, SSH key, git push authorization, "
          "Claude cloud GitHub App, MCP or branch-bypass attestation.")
    print("NO agent execution is authorized solely by this result.")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
