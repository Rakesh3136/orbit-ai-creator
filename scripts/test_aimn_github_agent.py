from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "aimn_github_agent.py"


class GitHubAgentRunnerTests(unittest.TestCase):
    def run_task(self, profile: str):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        subprocess.run(
            [
                sys.executable, str(RUNNER),
                "--task-type", "strategy",
                "--instruction", "Plan a test channel about science",
                "--access-profile", profile,
                "--output-dir", temp.name,
            ],
            check=True,
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        records = list(Path(temp.name).glob("*.json"))
        self.assertEqual(len(records), 1)
        return json.loads(records[0].read_text(encoding="utf-8"))

    def test_restricted_profile_never_performs_external_actions(self):
        record = self.run_task("restricted")
        self.assertEqual(record["mode"], "bounded_planning_only")
        self.assertFalse(record["permissions"]["external_actions"])
        self.assertFalse(record["safety"]["external_writes_performed"])
        self.assertFalse(record["agent_output"]["model_inference"])

    def test_balanced_profile_allows_only_internal_run_record_persistence(self):
        record = self.run_task("balanced")
        self.assertTrue(record["permissions"]["repository_writes"])
        self.assertFalse(record["permissions"]["external_actions"])
        self.assertTrue(record["safety"]["owner_approval_required_for_sensitive_actions"])

    def test_expanded_profile_does_not_mean_unlimited_access(self):
        record = self.run_task("expanded")
        self.assertFalse(record["permissions"]["external_actions"])
        self.assertFalse(record["safety"]["publishing_enabled"])
        self.assertTrue(any("literal unlimited access" in x for x in record["limitations"]))

    def test_credential_like_instruction_is_rejected(self):
        result = subprocess.run(
            [sys.executable, str(RUNNER), "--task-type", "research",
             "--instruction", "access_token=ghp_abcdefghijklmnopqrstuvwxyz123456",
             "--output-dir", tempfile.gettempdir()],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("credential", result.stderr.lower())

    def test_empty_instruction_is_rejected(self):
        result = subprocess.run(
            [sys.executable, str(RUNNER), "--task-type", "research",
             "--instruction", "   ", "--output-dir", tempfile.gettempdir()],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
