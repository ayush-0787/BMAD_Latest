#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for the pure helpers in init-sanctum.py (no filesystem scaffolding)."""

import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parent.parent / "init-sanctum.py"
spec = importlib.util.spec_from_file_location("init_sanctum", MODULE_PATH)
init_sanctum = importlib.util.module_from_spec(spec)
sys.modules["init_sanctum"] = init_sanctum
spec.loader.exec_module(init_sanctum)


class TestParseFrontmatter(unittest.TestCase):
    def test_extracts_name_and_code(self, tmp_path=None):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "cap.md"
            f.write_text("---\nname: fetch-work-items\ndescription: Fetch stuff\ncode: FW\n---\n\nBody\n")
            meta = init_sanctum.parse_frontmatter(f)
            self.assertEqual(meta["name"], "fetch-work-items")
            self.assertEqual(meta["code"], "FW")

    def test_no_frontmatter_returns_empty(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "plain.md"
            f.write_text("# Just a heading\n")
            self.assertEqual(init_sanctum.parse_frontmatter(f), {})


class TestSubstituteVars(unittest.TestCase):
    def test_replaces_all_occurrences(self):
        result = init_sanctum.substitute_vars("Hi {user_name}, born {birth_date}", {"user_name": "Ayush", "birth_date": "2026-07-06"})
        self.assertEqual(result, "Hi Ayush, born 2026-07-06")

    def test_leaves_unknown_placeholders_untouched(self):
        result = init_sanctum.substitute_vars("Keep {unknown} as-is", {"user_name": "Ayush"})
        self.assertEqual(result, "Keep {unknown} as-is")


class TestGenerateCapabilitiesMd(unittest.TestCase):
    def test_includes_learned_section_when_evolvable(self):
        caps = [{"code": "FW", "name": "fetch-work-items", "description": "Fetch work items", "source": "references/fetch-work-items.md"}]
        content = init_sanctum.generate_capabilities_md(caps, evolvable=True)
        self.assertIn("[FW]", content)
        self.assertIn("## Learned", content)

    def test_omits_learned_section_when_not_evolvable(self):
        content = init_sanctum.generate_capabilities_md([], evolvable=False)
        self.assertNotIn("## Learned", content)


if __name__ == "__main__":
    unittest.main()
