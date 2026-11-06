"""Regression checks for AhmetOS v4 SVG card/badge line alignment."""
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = {"svg": "http://www.w3.org/2000/svg"}


class SvgGeometryTests(unittest.TestCase):
    def test_mission_card_insets_and_footer_alignment(self):
        for slug in ("zerowaste", "shoplytic", "stayzi", "dermascope", "zonerun", "rag"):
            path = ROOT / "assets" / "ahmetos-v3" / ("mission-" + slug + ".svg")
            with self.subTest(card=slug):
                root = ET.parse(path).getroot()
                self.assertEqual(root.attrib.get("shape-rendering"), "geometricPrecision")
                accent = [r for r in root.findall("svg:rect", NS)
                          if r.attrib.get("x") == "4" and r.attrib.get("width") == "4"]
                self.assertEqual(len(accent), 1, "Accent line must avoid rounded outer corner")
                self.assertEqual(accent[0].attrib.get("y"), "18")
                self.assertEqual(accent[0].attrib.get("height"), "166")
                footer_tracks = [r for r in root.findall("svg:rect", NS)
                                 if r.attrib.get("width") in ("135", "47")]
                self.assertEqual(len(footer_tracks), 2)
                self.assertTrue(all(r.attrib.get("y") == "177" for r in footer_tracks))
                css = "".join(el.text or "" for el in root.findall("svg:style", NS))
                self.assertIn("transform-origin:433px 82px", css)
                self.assertIn("prefers-reduced-motion", css)

    def test_achievement_ring_centers_and_label_clearances(self):
        path = ROOT / "assets" / "ahmetos-v3-arcade" / "achievements.svg"
        root = ET.parse(path).getroot()
        circles = root.findall("svg:circle", NS)
        labels = {"154": 95, "507": 448, "855": 800}
        texts = root.findall("svg:text", NS)
        for label_x, cx in labels.items():
            with self.subTest(center=cx):
                matches = [c for c in circles if c.attrib.get("cx") == str(cx)
                           and c.attrib.get("class", "").startswith("spin")]
                self.assertEqual(len(matches), 1)
                ring = matches[0]
                self.assertNotIn("transform", ring.attrib, "The orbit cannot be shifted across text")
                right_edge = float(ring.attrib["cx"]) + float(ring.attrib["r"]) + float(ring.attrib.get("stroke-width", 1)) / 2
                self.assertGreaterEqual(float(label_x) - right_edge, 4,
                                        "Dashed orbit must not touch label")
                self.assertTrue(any(t.attrib.get("x") == label_x for t in texts))
        self.assertEqual(len([p for p in root.findall("svg:path", NS)
                              if p.attrib.get("d") == "M20 5H1080"]), 1)


if __name__ == "__main__":
    unittest.main()
