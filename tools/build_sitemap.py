#!/usr/bin/env python3
"""저장소의 모든 .html 을 스캔해 sitemap.xml 을 만든다 (표준 라이브러리만 사용).

사용: python3 tools/build_sitemap.py
- 제외: assets/og.html(OG 이미지 원본), tools/ 아래, 숨김 폴더(.git 등)
- lastmod: `git log -1 --format=%cI -- <file>` (커밋 이력이 없으면 파일 수정 시각)
- 우선순위: 홈 1.0 weekly / 허브(<폴더>/index.html) 0.8 weekly /
  글 0.6 monthly / support·privacy 0.3 yearly
"""
import datetime
import pathlib
import subprocess
from xml.sax.saxutils import escape

BASE = "https://richoh86.github.io/workenglish-site/"
ROOT = pathlib.Path(__file__).resolve().parent.parent
EXCLUDE = {"assets/og.html"}
LOW = {"support.html", "privacy.html"}


def lastmod(path: pathlib.Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    try:
        # 커밋 안 된 수정·새 파일이면 마지막 커밋 시각이 옛 값이므로 파일 수정 시각을 쓴다
        dirty = subprocess.run(
            ["git", "-C", str(ROOT), "status", "--porcelain", "--", rel],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        if dirty:
            raise OSError("uncommitted")
        out = subprocess.run(
            ["git", "-C", str(ROOT), "log", "-1", "--format=%cI", "--", rel],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        if out:
            return out
    except (OSError, subprocess.CalledProcessError):
        pass
    ts = datetime.datetime.fromtimestamp(path.stat().st_mtime).astimezone()
    return ts.replace(microsecond=0).isoformat()


def classify(rel: str):
    if rel == "index.html":
        return BASE, "weekly", "1.0"
    if rel in LOW:
        return BASE + rel, "yearly", "0.3"
    if rel.endswith("/index.html"):
        return BASE + rel, "weekly", "0.8"
    return BASE + rel, "monthly", "0.6"


def collect():
    rows = []
    for path in sorted(ROOT.rglob("*.html")):
        rel = path.relative_to(ROOT).as_posix()
        parts = rel.split("/")
        if rel in EXCLUDE or parts[0] == "tools" or any(p.startswith(".") for p in parts):
            continue
        loc, freq, prio = classify(rel)
        rows.append((float(prio), rel, loc, lastmod(path), freq, prio))
    # 우선순위 높은 순, 같으면 경로순
    rows.sort(key=lambda r: (-r[0], r[1]))
    return rows


def main():
    rows = collect()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for _, _, loc, mod, freq, prio in rows:
        lines += ["  <url>",
                  f"    <loc>{escape(loc)}</loc>",
                  f"    <lastmod>{mod}</lastmod>",
                  f"    <changefreq>{freq}</changefreq>",
                  f"    <priority>{prio}</priority>",
                  "  </url>"]
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"sitemap.xml: {len(rows)} URLs")


if __name__ == "__main__":
    main()
