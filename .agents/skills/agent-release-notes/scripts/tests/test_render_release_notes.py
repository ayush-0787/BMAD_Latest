#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for render_release_notes.py."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from render_release_notes import render, validate


MINIMAL = {
    "title": "RELEASE NOTES",
    "header_fields": [["Product", "TouchWorks EHR -- Hub"], ["Version", "26.3"]],
    "sections": [
        {
            "heading": "NEW FEATURES",
            "entries": [
                {
                    "title": "Sample Feature",
                    "fields": [
                        {"label": "Description", "text": "Does a thing."},
                        {"label": "Details", "items": ["Detail one.", "Detail two."]},
                    ],
                }
            ],
        },
        {"heading": "BUG FIXES", "empty_text": "None."},
    ],
}


class TestValidate(unittest.TestCase):
    def test_missing_sections_raises(self):
        with self.assertRaises(ValueError):
            validate({})

    def test_field_without_text_or_items_raises(self):
        bad = {"sections": [{"heading": "X", "entries": [{"title": "T", "fields": [{"label": "L"}]}]}]}
        with self.assertRaises(ValueError):
            validate(bad)

    def test_valid_input_passes(self):
        validate(MINIMAL)  # should not raise


class TestRender(unittest.TestCase):
    def setUp(self):
        self.output = render(MINIMAL)

    def test_starts_and_ends_with_divider(self):
        divider = "=" * 80
        lines = self.output.splitlines()
        self.assertEqual(lines[0], divider)
        self.assertEqual(lines[-1], divider)
        self.assertEqual(lines[-2], "END OF RELEASE NOTES")

    def test_contains_title_and_headings(self):
        self.assertIn("RELEASE NOTES", self.output)
        self.assertIn("NEW FEATURES", self.output)
        self.assertIn("BUG FIXES", self.output)

    def test_empty_section_uses_empty_text(self):
        self.assertIn("None.", self.output)

    def test_entry_title_and_fields_present(self):
        self.assertIn("Sample Feature", self.output)
        self.assertIn("Description:", self.output)
        self.assertIn("Does a thing.", self.output)

    def test_items_render_as_indented_bullets(self):
        self.assertIn("Details:", self.output)
        self.assertIn("- Detail one.", self.output)
        self.assertIn("- Detail two.", self.output)

    def test_numbered_items_use_numeric_markers(self):
        data = {
            "sections": [
                {
                    "heading": "BREAKING CHANGES",
                    "entries": [
                        {
                            "title": "Change",
                            "fields": [{"label": "Migration Steps", "items": ["Step one.", "Step two."], "numbered": True}],
                        }
                    ],
                }
            ]
        }
        output = render(data)
        self.assertIn("1. Step one.", output)
        self.assertIn("2. Step two.", output)

    def test_long_text_wraps_with_hanging_indent(self):
        data = {
            "sections": [
                {
                    "heading": "NEW FEATURES",
                    "entries": [
                        {
                            "title": "Long",
                            "fields": [{"label": "Description", "text": "word " * 40}],
                        }
                    ],
                }
            ]
        }
        output = render(data)
        lines = [l for l in output.splitlines() if l.strip()]
        wrapped_lines = [l for l in lines if l.startswith("             ")]
        self.assertTrue(len(wrapped_lines) > 0, "expected at least one continuation line")


if __name__ == "__main__":
    unittest.main()
