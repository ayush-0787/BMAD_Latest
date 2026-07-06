#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for the pure (non-networked) helpers in fetch_work_items.py."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fetch_work_items import build_api_base, build_wiql, escape_wiql_literal, normalize_work_item


class TestEscapeWiqlLiteral(unittest.TestCase):
    def test_no_quotes(self):
        self.assertEqual(escape_wiql_literal("TWEHR"), "TWEHR")

    def test_embedded_quote_is_doubled(self):
        self.assertEqual(escape_wiql_literal("O'Brien"), "O''Brien")


class TestBuildApiBase(unittest.TestCase):
    def test_default_concatenation(self):
        base = build_api_base("https://server.example.com/tfs/projects/", "TWEHR", None, None)
        self.assertEqual(base, "https://server.example.com/tfs/projects/TWEHR/_apis")

    def test_with_collection(self):
        base = build_api_base("https://server.example.com/tfs", "TWEHR", "DefaultCollection", None)
        self.assertEqual(base, "https://server.example.com/tfs/DefaultCollection/TWEHR/_apis")

    def test_override_wins(self):
        base = build_api_base("https://ignored", "ignored", "ignored", "https://custom/_apis")
        self.assertEqual(base, "https://custom/_apis")


class TestBuildWiql(unittest.TestCase):
    def test_raw_wiql_passthrough(self):
        self.assertEqual(build_wiql("TWEHR", raw_wiql="SELECT [System.Id] FROM WorkItems"), "SELECT [System.Id] FROM WorkItems")

    def test_ids_need_no_query(self):
        self.assertIsNone(build_wiql("TWEHR", ids=[1, 2, 3]))

    def test_iteration_path_scope(self):
        wiql = build_wiql("TWEHR", iteration_path="TWEHR\\ADP 26.2")
        self.assertIn("[System.TeamProject] = 'TWEHR'", wiql)
        self.assertIn("[System.IterationPath] UNDER 'TWEHR\\ADP 26.2'", wiql)

    def test_multiple_scopes_combine_with_and(self):
        wiql = build_wiql("TWEHR", area_path="TWEHR\\Hub", tag="Release 26.3")
        self.assertIn(" AND ", wiql)
        self.assertIn("[System.AreaPath] UNDER 'TWEHR\\Hub'", wiql)
        self.assertIn("[System.Tags] CONTAINS 'Release 26.3'", wiql)

    def test_no_scope_raises(self):
        with self.assertRaises(ValueError):
            build_wiql("TWEHR")


class TestNormalizeWorkItem(unittest.TestCase):
    def test_extracts_expected_fields(self):
        raw = {
            "id": 9248686,
            "url": "https://server/_apis/wit/workItems/9248686",
            "fields": {
                "System.WorkItemType": "Product Backlog Item",
                "System.Title": "Doc Admin Role Edit Access",
                "System.State": "Closed",
                "System.Description": "Some description",
                "System.Tags": "ADP",
                "System.AreaPath": "TWEHR\\CC\\ADP",
                "System.IterationPath": "TWEHR\\ADP 26.2",
            },
        }
        normalized = normalize_work_item(raw)
        self.assertEqual(normalized["id"], 9248686)
        self.assertEqual(normalized["type"], "Product Backlog Item")
        self.assertEqual(normalized["title"], "Doc Admin Role Edit Access")
        self.assertEqual(normalized["area_path"], "TWEHR\\CC\\ADP")
        self.assertIsNone(normalized["repro_steps"])


if __name__ == "__main__":
    unittest.main()
