"""Offline tests: public allowlist, filtering, SVG XML, and failure behavior."""
import unittest
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from scripts import build_profile_activity as p


class ActivityTests(unittest.TestCase):
    def test_classifications(self):
        self.assertIsNone(p.classify("Merge pull request #10 from example"))
        self.assertIsNone(p.classify("docs: update README"))
        self.assertIsNone(p.classify("add privacy policy"))
        self.assertEqual(p.classify("feat: update Firebase configuration"), "FEATURE")
        self.assertEqual(p.classify("chore(security): stop tracking secrets"), "SECURITY")
        self.assertEqual(p.classify("Add GitHub Actions workflow for Dart CI"), "CI")
        self.assertEqual(p.classify("fix: missing profile image"), "FIX")

    def test_private_repository_is_rejected(self):
        with patch.object(p, "fetch_json", return_value={
            "private": True,
            "owner": {"login": p.OWNER},
            "default_branch": "main",
        }):
            with self.assertRaises(RuntimeError):
                p.collect()

    def test_collect_only_six_public_owners(self):
        seen = []
        def mock_fetch(path):
            seen.append(path)
            if "/commits?" in path:
                return [{
                    "author": {"login": p.OWNER},
                    "sha": "a" * 40,
                    "commit": {
                        "message": "feat: safe improvement",
                        "author": {"date": "2026-11-05T10:00:00Z"},
                    },
                }]
            return {"private": False, "owner": {"login": p.OWNER}, "default_branch": "main"}
        with patch.object(p, "fetch_json", side_effect=mock_fetch):
            rows = p.collect()
        self.assertEqual(len(rows), 6)
        self.assertTrue(all(row["kind"] == "FEATURE" for row in rows))
        self.assertEqual(len(seen), 12)
        self.assertTrue(all("/repos/AhmetKoca32/" in path for path in seen))

    def test_render_is_valid_svg_and_escapes_messages(self):
        rows = [{
            "slug": slug, "name": name, "color": color,
            "date": datetime(2026, 11, 5, tzinfo=timezone.utc),
            "message": "feat: check <xml> & entities",
            "kind": "FEATURE", "sha": "abcdef12",
        } for slug, name, color in p.REPOS]
        markup = p.render(rows, datetime(2026, 11, 6, tzinfo=timezone.utc))
        ET.fromstring(markup)
        self.assertIn("&lt;xml&gt;", markup)
        self.assertIn("&amp;", markup)
        self.assertIn("LAST SUCCESSFUL SYNC:", markup)

    def test_initial_snapshot_parses(self):
        root = ET.parse(Path("assets/ahmetos-v4/activity-live.svg")).getroot()
        self.assertTrue(root.tag.endswith("svg"))


if __name__ == "__main__":
    unittest.main()
