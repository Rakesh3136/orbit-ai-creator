from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONSOLE = ROOT / "apps" / "console"


class InlineScriptParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_inline_script = False
        self.scripts: list[str] = []
        self._parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "script" and not dict(attrs).get("src"):
            self.in_inline_script = True
            self._parts = []

    def handle_data(self, data):
        if self.in_inline_script:
            self._parts.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.in_inline_script:
            self.scripts.append("".join(self._parts))
            self.in_inline_script = False


class AIMNConsoleTests(unittest.TestCase):
    def test_manifest_and_icon_are_valid(self):
        manifest = json.loads((CONSOLE / "manifest.webmanifest").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "AIMN Owner Console")
        for icon in manifest["icons"]:
            self.assertTrue((CONSOLE / icon["src"].removeprefix("./")).is_file())

    def test_console_has_session_only_token_handling_and_workflow_controls(self):
        html = (CONSOLE / "index.html").read_text(encoding="utf-8")
        self.assertIn("fine-grained token", html)
        self.assertIn("aimn-agent-run.yml/dispatches", html)
        self.assertIn("navigator.serviceWorker.register", html)
        self.assertNotIn("localStorage", html)
        self.assertNotIn("sessionStorage", html)

    def test_inline_javascript_passes_node_syntax_check(self):
        parser = InlineScriptParser()
        parser.feed((CONSOLE / "index.html").read_text(encoding="utf-8"))
        self.assertEqual(len(parser.scripts), 1)
        with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8") as script:
            script.write(parser.scripts[0])
            script.flush()
            subprocess.run(["node", "--check", script.name], check=True, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()
