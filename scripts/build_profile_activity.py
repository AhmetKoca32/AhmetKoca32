#!/usr/bin/env python3
"""Render AhmetOS public activity from an explicit six-repository allowlist.

Only public repositories owned by AhmetKoca32 are queried. A failed query
aborts the refresh and leaves the previously generated SVG untouched.
"""
from __future__ import annotations

import html
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

OWNER = "AhmetKoca32"
REPOS = [
    ("zerowaste", "ZeroWaste", "#5BE7BC"),
    ("Shoplytic", "Shoplytic", "#BEA5FF"),
    ("Stayzi", "Stayzi", "#77BDFF"),
    ("AI-180", "DermaScope", "#FF9FC0"),
    ("ZoneRun", "ZoneRun", "#FFD27C"),
    ("ChatBot_with_RAG", "RAG Lab", "#73DFF7"),
]
TARGET = Path("assets/ahmetos-v4/activity-live.svg")


def fetch_json(path: str):
    headers = {"Accept": "application/vnd.github+json",
               "User-Agent": "AhmetOS-Public-Activity",
               "X-GitHub-Api-Version": "2022-11-28"}
    token = os.getenv("GH_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    try:
        with urlopen(Request("https://api.github.com" + path, headers=headers), timeout=20) as res:
            return json.load(res)
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        raise RuntimeError("Public GitHub API request failed: " + path) from exc


def classify(message: str) -> str | None:
    title = message.splitlines()[0].strip()
    if re.search(r"^merge\b", title, re.I):
        return None
    if re.search(r"^docs?(\([^)]*\))?:|readme|documentation|privacy policy|data deletion", title, re.I):
        return None
    if re.search(r"security|secret|credential|password|\.env", title, re.I):
        return "SECURITY"
    if re.search(r"\bci\b|github actions|workflow|pipeline", title, re.I):
        return "CI"
    if re.search(r"^(feat|feature)(\([^)]*\))?:", title, re.I):
        return "FEATURE"
    if re.search(r"^(fix|bugfix)(\([^)]*\))?:", title, re.I):
        return "FIX"
    return "ENGINEERING"


def collect():
    found = []
    for slug, name, color in REPOS:
        meta = fetch_json("/repos/" + OWNER + "/" + quote(slug))
        if meta.get("private") is not False or meta.get("owner", {}).get("login", "").lower() != OWNER.lower():
            raise RuntimeError("Repository is not verified public and owned: " + slug)
        branch = meta.get("default_branch")
        if not branch:
            raise RuntimeError("Missing default branch: " + slug)
        commits = fetch_json("/repos/" + OWNER + "/" + quote(slug) + "/commits?sha=" +
                             quote(branch, safe="") + "&author=" + OWNER + "&per_page=100")
        if not isinstance(commits, list):
            raise RuntimeError("Unexpected commits payload: " + slug)
        entry = {"slug": slug, "name": name, "color": color,
                 "kind": "NO DATA", "date": None, "message": "", "sha": ""}
        for commit in commits:
            author = commit.get("author")
            if author and author.get("login", "").lower() != OWNER.lower():
                continue
            data = commit.get("commit") or {}
            title = (data.get("message") or "").splitlines()[0]
            kind = classify(title)
            if kind is None:
                continue
            try:
                timestamp = datetime.fromisoformat(data["author"]["date"].replace("Z", "+00:00"))
            except (KeyError, TypeError, ValueError, AttributeError):
                continue
            entry.update(kind=kind, date=timestamp, message=title, sha=commit.get("sha", "")[:8])
            break
        found.append(entry)
    return found


def escape(s):
    return html.escape(str(s), quote=True)


def clipped(s, limit=41):
    s = " ".join(s.split())
    return s if len(s) <= limit else s[:limit - 1].rstrip() + "…"


def render(rows, now):
    top = sorted((r for r in rows if r["date"]), key=lambda r: r["date"], reverse=True)[:3]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="535" viewBox="0 0 1100 535" role="img" aria-labelledby="title desc">',
        '<title id="title">AhmetOS verified public GitHub activity</title>',
        '<desc id="desc">The last qualifying technical commit from each of six selected public GitHub repositories, updated by GitHub Actions.</desc>',
        '<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#10182C"/><stop offset=".6" stop-color="#171B38"/><stop offset="1" stop-color="#291632"/></linearGradient><linearGradient id="line" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#5DF2D4"/><stop offset=".35" stop-color="#79B9FF"/><stop offset=".68" stop-color="#CBA5FF"/><stop offset="1" stop-color="#FFA8B9"/></linearGradient></defs>',
        '<style>text{font-family:Arial,Helvetica,sans-serif}.mono{font-family:Consolas,monospace}.pulse{animation:pulse 3s ease-in-out infinite}.flow{animation:flow 6s linear infinite}@keyframes pulse{0%,100%{opacity:.4}50%{opacity:1}}@keyframes flow{to{stroke-dashoffset:-140}}@media(prefers-reduced-motion:reduce){*{animation:none!important}}</style>',
        '<rect x="1" y="1" width="1098" height="533" rx="20" fill="url(#bg)" stroke="#475574" stroke-width="2"/>',
        '<path d="M2 3H1098" stroke="url(#line)" stroke-width="5"/>',
        '<text x="28" y="39" class="mono" font-size="18" fill="#75F4DF">PUBLIC ACTIVITY // VERIFIED SIGNALS</text>',
        '<text x="28" y="67" class="mono" font-size="13" fill="#B2C8DF">LAST SUCCESSFUL SYNC: ' + now.strftime("%Y-%m-%d %H:%M UTC") + '</text>',
        '<text x="28" y="94" class="mono" font-size="13" fill="#E0BBFF">LATEST MEANINGFUL TECHNICAL COMMITS</text>',
    ]
    for i, row in enumerate(top):
        x = 24 + i * 360
        c = row["color"]
        date = row["date"].strftime("%Y-%m-%d")
        parts += [
            f'<rect x="{x}" y="106" width="335" height="132" rx="16" fill="#1D2A42" stroke="{c}" stroke-width="2"/>',
            f'<circle cx="{x+20}" cy="128" r="5" fill="{c}" class="pulse"/>',
            f'<text x="{x+36}" y="135" font-size="19" font-weight="800" fill="#F9F8FF">{escape(row["name"])}</text>',
            f'<text x="{x+17}" y="162" class="mono" font-size="12" fill="{c}">{row["kind"]} · {date}</text>',
            f'<text x="{x+17}" y="192" font-size="13.8" fill="#E7EDF8">{escape(clipped(row["message"]))}</text>',
            f'<text x="{x+17}" y="219" class="mono" font-size="11" fill="#B5C9DC">COMMIT {escape(row["sha"])}</text>',
        ]
    parts += [
        '<text x="28" y="270" class="mono" font-size="13" fill="#D8B9FF">PROJECT WATCHLIST // 6 PUBLIC REPOSITORIES</text>',
        '<path d="M29 282H1069" stroke="#495B79" stroke-width="3"/>',
        '<path d="M29 282H1069" stroke="url(#line)" stroke-width="3" stroke-dasharray="16 19" class="flow"/>',
    ]
    for i, row in enumerate(rows):
        x, y = 22 + (i % 2) * 548, 296 + (i // 2) * 69
        date = row["date"].strftime("%Y-%m-%d") if row["date"] else "N/A"
        c = row["color"]
        parts += [
            f'<rect x="{x}" y="{y}" width="522" height="60" rx="11" fill="#1C2A42" stroke="#40546F"/>',
            f'<circle cx="{x+21}" cy="{y+27}" r="5.5" fill="{c}" class="pulse"/>',
            f'<text x="{x+38}" y="{y+24}" font-size="17" font-weight="700" fill="#F5F6FF">{escape(row["name"])}</text>',
            f'<text x="{x+38}" y="{y+44}" class="mono" font-size="12" fill="#B3CBE1">{row["kind"]} · {date}</text>',
            f'<text x="{x+505}" y="{y+36}" text-anchor="end" class="mono" font-size="10" fill="{c}">{escape(row["sha"])}</text>',
        ]
    parts += [
        '<text x="28" y="519" class="mono" font-size="12" fill="#AFC0D6">No private repositories · No fabricated totals · Docs and merge commits excluded</text>',
        '</svg>',
    ]
    return "\n".join(parts) + "\n"


def main():
    timestamp = datetime.now(timezone.utc)
    rows = collect()
    markup = render(rows, timestamp)
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(markup, encoding="utf-8")
    print("Updated public activity from", len(rows), "verified repositories")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError) as exc:
        print("Refresh failed; existing activity panel preserved:", exc, file=sys.stderr)
        sys.exit(1)
