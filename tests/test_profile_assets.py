"""Static validation for the GitHub-profile README and its local SVG assets."""
import re
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
V4_ASSETS = ROOT / "assets" / "ahmetos-v4"


class ProfileAssetsTests(unittest.TestCase):
    def test_every_local_readme_image_exists(self):
        readme = README.read_text(encoding="utf-8")
        local_assets = re.findall(r'(?:src|srcset)="(assets/[^"]+)"', readme)
        self.assertGreaterEqual(len(local_assets), 16, "Missing referenced profile graphics")
        for rel in local_assets:
            with self.subTest(path=rel):
                self.assertTrue((ROOT / rel).is_file(), rel)

    def test_every_v4_svg_parses_and_supports_reduced_motion(self):
        files = sorted(V4_ASSETS.glob("*.svg"))
        self.assertGreaterEqual(len(files), 6)
        for path in files:
            with self.subTest(file=path.name):
                markup = path.read_text(encoding="utf-8")
                root = ET.fromstring(markup)
                self.assertTrue(root.tag.endswith("svg"))
                self.assertIn("prefers-reduced-motion", markup)
                self.assertNotIn("<script", markup.lower())
                self.assertIn("role=\"img\"", markup)
                self.assertIn("<title", markup)

    def test_tech_marquee_seamless_loop(self):
        path = V4_ASSETS / "tech-marquee.svg"
        root = ET.parse(path).getroot()
        ns = {"svg": "http://www.w3.org/2000/svg"}
        tracks = [g for g in root.findall(".//svg:g", ns) if g.get("class") == "ticker-track"]
        self.assertEqual(len(tracks), 1)
        cards = tracks[0].findall("svg:g", ns)
        self.assertEqual(len(cards), 14, "Seven tech cards must be duplicated for seamless motion")
        positions = [int(re.search(r"translate\\((\\d+) 85\\)", card.get("transform")).group(1))
                     for card in cards]
        self.assertEqual(positions[7:], [x + 1190 for x in positions[:7]])
        svg = path.read_text(encoding="utf-8")
        self.assertIn("translateX(-1190px)", svg)
        self.assertIn('clip-path="url(#marqueeWindow)"', svg)
        self.assertIn("prefers-reduced-motion", svg)
        self.assertIn("tech-marquee.svg", README.read_text(encoding="utf-8"))

    def test_profile_sections_are_sequential(self):
        readme = README.read_text(encoding="utf-8")
        section_nums = [int(n) for n in re.findall(r'^## `(\d\d) //', readme, flags=re.MULTILINE)]
        self.assertEqual(section_nums, list(range(1, len(section_nums) + 1)))
        self.assertEqual(len(section_nums), 9)

    def test_secret_level_uses_github_native_expanders(self):
        readme = README.read_text(encoding="utf-8")
        self.assertIn("## `08 // SECRET LEVEL`", readme)
        self.assertIn("secret-terminal.svg", readme)
        self.assertIn("arcade-powerups.svg", readme)
        self.assertEqual(readme.count("<details>"), readme.count("</details>"))
        self.assertNotIn("<iframe", readme.lower())
        self.assertNotIn("<script", readme.lower())

    def test_existing_sections_stay_intact(self):
        readme = README.read_text(encoding="utf-8")
        for expected in ["byte-mascot.svg", "skill-tree.svg", "developer-journey.svg",
                         "activity-live.svg", "github-contribution-grid-snake",
                         "contact-linkedin.svg", "contact-portfolio.svg", "contact-email.svg"]:
            with self.subTest(asset=expected):
                self.assertIn(expected, readme)


if __name__ == "__main__":
    unittest.main()
