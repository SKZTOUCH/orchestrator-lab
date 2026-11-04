"""Standalone stdlib tests for preflight's fail-closed responses."""
import importlib.util
import os
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "lab_preflight.py"
spec = importlib.util.spec_from_file_location("lab_preflight", SCRIPT)
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)


def response(status, body='{"message":"Not Found"}', rc=1):
    return subprocess.CompletedProcess(["gh", "api"], rc,
        f"HTTP/2 {status}\ncontent-type: application/json\n\n{body}\n", "")


class TestApiClassification(unittest.TestCase):
    def test_private_404_only_explicit(self):
        with patch.object(preflight, "call", return_value=response(404)):
            self.assertEqual(preflight.api("repos/SKZTOUCH/orchestrator-os")[0], 404)

    def test_401_403_500_do_not_become_404(self):
        for status in (401, 403, 500):
            with self.subTest(status=status), patch.object(preflight, "call", return_value=response(status)):
                self.assertNotEqual(preflight.api("repos/x")[0], 404)

    def test_missing_http_header_fails_closed(self):
        with patch.object(preflight, "call", return_value=subprocess.CompletedProcess([], 1, "", "HTTP 404")):
            self.assertEqual(preflight.api("repos/x"), (None, None))

    def test_timeout_fails_closed(self):
        with patch.object(preflight, "call", return_value=None):
            self.assertEqual(preflight.api("repos/x"), (None, None))

    def test_success_requires_valid_json(self):
        with patch.object(preflight, "call", return_value=response(200, '{"login":"skz-lab-agent"}', 0)):
            self.assertEqual(preflight.api("user"), (200, {"login":"skz-lab-agent"}))

    def test_inconsistent_process_rc_fails_closed(self):
        with patch.object(preflight, "call", return_value=response(404, '{}', 0)):
            self.assertEqual(preflight.api("repos/x"), (None, None))


class TestEnvironment(unittest.TestCase):
    def test_local_token_is_blocked(self):
        with patch.dict(os.environ, {"CODESPACES": "", "GITHUB_TOKEN": "stub", "GH_TOKEN":""}, clear=True):
            self.assertFalse(preflight.env_gate())

    def test_codespaces_repo_scoped_token_context_allowed(self):
        env = {"CODESPACES":"true", "GITHUB_TOKEN":"stub", "GITHUB_REPOSITORY":preflight.EXPECTED_REPO,
               "GITHUB_USER":preflight.EXPECTED_USER, "GITHUB_SERVER_URL":"https://github.com",
               "CODESPACE_NAME":"synthetic"}
        with patch.dict(os.environ, env, clear=True):
            self.assertTrue(preflight.env_gate())

    def test_codespaces_main_account_context_blocked(self):
        env = {"CODESPACES":"true", "GITHUB_TOKEN":"stub", "GITHUB_REPOSITORY":preflight.EXPECTED_REPO,
               "GITHUB_USER":"SKZTOUCH", "GITHUB_SERVER_URL":"https://github.com",
               "CODESPACE_NAME":"synthetic"}
        with patch.dict(os.environ, env, clear=True):
            self.assertFalse(preflight.env_gate())

    def test_gh_token_override_blocked_in_codespaces(self):
        env = {"CODESPACES":"true", "GITHUB_TOKEN":"stub", "GH_TOKEN":"override",
               "GITHUB_REPOSITORY":preflight.EXPECTED_REPO, "GITHUB_USER":preflight.EXPECTED_USER,
               "GITHUB_SERVER_URL":"https://github.com", "CODESPACE_NAME":"synthetic"}
        with patch.dict(os.environ, env, clear=True):
            self.assertFalse(preflight.env_gate())


class TestDevcontainer(unittest.TestCase):
    def test_declared_additional_repo_grant_blocks(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "devcontainer.json"
            file.write_text('{"customizations":{"codespaces":{"repositories":{"SKZTOUCH/orchestrator-os":{"permissions":{"contents":"read"}}}}}}')
            self.assertFalse(preflight.devcontainer_gate(directory))

    def test_no_devcontainer_grants_allows(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            self.assertTrue(preflight.devcontainer_gate(directory))


class TestGitIdentity(unittest.TestCase):
    def test_wrong_push_url_or_author_blocks(self):
        values = {
            ("git", "rev-parse", "--show-toplevel"): "/tmp",
            ("git", "remote", "get-url", "origin"): preflight.ORIGIN,
            ("git", "remote", "get-url", "--push", "origin"): "https://github.com/SKZTOUCH/orchestrator-os.git",
            ("git", "remote"): "origin",
            ("git", "config", "--get", "user.name"): "SKZTOUCH",
            ("git", "config", "--get", "user.email"): "skz-lab-agent@users.noreply.github.com",
        }
        with patch.object(preflight, "read_ok", side_effect=lambda *args: values.get(args)), \
             patch.object(preflight, "call", return_value=subprocess.CompletedProcess([], 1, "", "")), \
             patch.dict(os.environ, {}, clear=True):
            self.assertFalse(preflight.git_gate())

    def test_rewrite_rule_blocks(self):
        values = {
            ("git", "rev-parse", "--show-toplevel"): "/tmp",
            ("git", "remote", "get-url", "origin"): preflight.ORIGIN,
            ("git", "remote", "get-url", "--push", "origin"): preflight.ORIGIN,
            ("git", "remote"): "origin",
            ("git", "config", "--get", "user.name"): preflight.EXPECTED_USER,
            ("git", "config", "--get", "user.email"): "123+skz-lab-agent@users.noreply.github.com",
        }
        with patch.object(preflight, "read_ok", side_effect=lambda *args: values.get(args)), \
             patch.object(preflight, "call", return_value=subprocess.CompletedProcess([], 0, "url.https://...insteadOf", "")), \
             patch.dict(os.environ, {}, clear=True):
            self.assertFalse(preflight.git_gate())


if __name__ == "__main__":
    unittest.main()
