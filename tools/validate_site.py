"""Whole-site check: tidy errors, JSON-LD parses, internal links resolve,
required head tags present, nav consistent. Run from repo root."""
import glob
import json
import os
import re
import subprocess
import sys

REQUIRED = ['rel="canonical"', 'property="og:title"', 'property="og:image"', 'name="twitter:card"',
            'rel="icon"', 'application/ld+json', 'name="description"']
NAV = ["사용법", "표현", "가이드", "요금", "지원", "개인정보"]
pages = sorted(p for p in glob.glob("**/*.html", recursive=True)
               if not p.startswith("tools/") and p != "assets/og.html")
problems = []
for p in pages:
    html = open(p, encoding="utf-8").read()
    tidy = subprocess.run(["tidy", "-q", "-e", p], capture_output=True, text=True)
    errs = [l for l in tidy.stderr.splitlines() if "Error:" in l]
    if errs:
        problems.append(f"{p}: tidy {errs[:2]}")
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            json.loads(m.group(1))
        except json.JSONDecodeError as e:
            problems.append(f"{p}: ld+json {e}")
    for tag in REQUIRED:
        if tag not in html:
            problems.append(f"{p}: missing {tag}")
    for word in NAV:
        if f">{word}</a>" not in html:
            problems.append(f"{p}: nav lacks {word}")
    if len(re.findall(r"<h1[\s>]", html)) != 1:
        problems.append(f"{p}: h1 count != 1")
    base = os.path.dirname(p)
    for href in re.findall(r'(?:href|src)="([^"#]+)"', html):
        if href.startswith(("http", "mailto:", "data:")):
            continue
        target = href[len("/workenglish-site/"):] if href.startswith("/workenglish-site/") else os.path.normpath(os.path.join(base, href))
        if href.endswith("/"):
            target = os.path.join(target, "index.html")
        if not os.path.exists(target):
            problems.append(f"{p}: broken {href}")
    if "sample_001" in html:
        problems.append(f"{p}: references sample_001")
    t = re.search(r"<title>(.*?)</title>", html, re.S)
    d = re.search(r'name="description" content="([^"]*)"', html)
    print(f"{p:70} title={len(t.group(1)) if t else 0:3} desc={len(d.group(1)) if d else 0:3}")
print(f"\n{len(pages)} pages, {len(problems)} problems")
for x in problems:
    print(" -", x)
sys.exit(1 if problems else 0)
