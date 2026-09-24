#!/usr/bin/env python3
"""매일 1문장 표현 페이지 생성기.

저장소 루트에서 실행한다:  python3 tools/build_expressions.py

입력:  data/situations-source.json (situations: id -> title_ko, context_ko, context_en, question_en)
       data/scaffold-source.json   (id -> intent, chips[3], sample_en, sample_gloss)
출력:  expressions/<id>.html (상황마다 한 장) + expressions/index.html (허브)

표준 라이브러리만 쓰고, 같은 입력이면 항상 같은 파일을 만든다(날짜·난수 없음).
expressions/ 안에서 입력에 없는 옛 .html은 지운다.
"""

import html
import json
import os
import re
import sys

SITE = "https://richoh86.github.io/workenglish-site/"
DATE = "2026-09-24"
MAX_TITLE = 40
MAX_DESC = 90
OG_IMAGE = SITE + "assets/og.png"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "expressions")

# 지금은 모든 상황이 업무 카테고리다. id 접두어로 나눈다.
CATEGORY_BY_PREFIX = {"wk": "업무", "sample": "업무"}
CATEGORY_ORDER = ["업무"]

SAMPLE_PREFIX = "오늘 예시:"

# 사이트에 싣지 않는 id 접두어. sample_001은 앱 안 예시 세션이고 wk_042와 제목이 같다.
SKIP_PREFIXES = ("sample_",)


def e(text):
    return html.escape(text, quote=True)


def load():
    with open(os.path.join(ROOT, "data", "situations-source.json"), encoding="utf-8") as f:
        situations = json.load(f)["situations"]
    with open(os.path.join(ROOT, "data", "scaffold-source.json"), encoding="utf-8") as f:
        scaffold = json.load(f)
    items = []
    for sid in sorted(scaffold):
        if sid.startswith(SKIP_PREFIXES):
            continue
        if sid not in situations:
            sys.exit(f"error: {sid} is in scaffold-source.json but not in situations-source.json")
        s, c = situations[sid], scaffold[sid]
        if len(c["chips"]) != 3:
            sys.exit(f"error: {sid} has {len(c['chips'])} chips, expected 3")
        title = s["title_ko"].strip()
        if title.startswith(SAMPLE_PREFIX):
            title = title[len(SAMPLE_PREFIX):].strip()
        # 앱 안내용 문장('예시 상황입니다')은 웹 페이지에서 뺀다.
        sentences = [x for x in split_sentences(s["context_ko"]) if "예시 상황" not in x]
        items.append({
            "id": sid,
            "title_ko": title,
            "context_ko": " ".join(sentences),
            "first_sentence": sentences[0] if sentences else "",
            "context_en": s["context_en"].strip(),
            "question_en": s["question_en"].strip(),
            "category": CATEGORY_BY_PREFIX.get(sid.split("_")[0], "업무"),
            "intent_ko": c["intent"]["ko"].strip(),
            "chips": [(ch["en"].strip(), ch["gloss"]["ko"].strip()) for ch in c["chips"]],
            "sample_en": c["sample_en"].strip(),
            "sample_ko": c["sample_gloss"]["ko"].strip(),
        })
    return items


def split_sentences(text):
    parts = re.split(r"(?<=[.?!])\s+", text.strip())
    return [p for p in parts if p]


def cut_at_word(text, limit):
    """limit 글자 안에서 단어 경계로 자른다."""
    if len(text) <= limit:
        return text
    cut = text[:limit]
    if " " in cut:
        cut = cut[:cut.rfind(" ")]
    return cut.rstrip()


def page_title(item):
    # '…말하기'로 끝나는 제목은 '…말하기 영어로 말하기'가 되지 않도록 '…영어로 말하기'로 합친다.
    base = item["title_ko"]
    if base.endswith(" 말하기"):
        base = base[: -len("말하기")].rstrip()
    suffix = " 영어로 말하기 · 출근영어"
    return cut_at_word(base, MAX_TITLE - len(suffix)) + suffix


def page_description(item):
    first = item["first_sentence"]
    tail = " 이럴 때 영어로 뭐라고 할까요? 자연스러운 한 문장과 표현 조각 3개, 팁 하나."
    # 스펙 권장 70~90자. 첫 문장만으로 70자가 안 되면 상황 설명 전체를 쓴다(90자 안일 때만).
    if len(first + tail) < 70 and len(item["context_ko"] + tail) <= MAX_DESC:
        return item["context_ko"] + tail
    candidates = [
        f"{first} 이럴 때 영어로 뭐라고 할까요? 자연스러운 한 문장과 표현 조각 3개, 팁 하나.",
        f"{first} 이럴 때 영어로 뭐라고 할까요? 자연스러운 한 문장과 표현 조각 3개.",
        f"{first} 이럴 때 영어로 뭐라고 할까요?",
    ]
    for c in candidates:
        if len(c) <= MAX_DESC:
            return c
    return cut_at_word(candidates[-1], MAX_DESC - 1) + "…"


def tip_sentence(item):
    a, b = item["chips"][0][0], item["chips"][1][0]
    return (f"'{a}', '{b}' 같은 짧은 조각을 먼저 떠올리고 그 사이를 이어 붙이면 "
            "한 문장을 만들기가 한결 쉬워져요.")


def jsonld(obj):
    text = json.dumps(obj, ensure_ascii=False, indent=2)
    return text.replace("</", "<\\/")


def head(title, description, canonical, og_type, ld):
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{e(canonical)}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:image" content="{OG_IMAGE}">
<meta property="og:url" content="{e(canonical)}">
<meta property="og:site_name" content="출근영어">
<meta property="og:locale" content="ko_KR">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#F8F5F1" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#101211" media="(prefers-color-scheme: dark)">
<link rel="icon" href="/workenglish-site/assets/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="/workenglish-site/assets/apple-touch-icon.png">
<link rel="stylesheet" href="../assets/site.css">
<script type="application/ld+json">
{jsonld(ld)}
</script>
</head>
<body>
<div class="wrap">

<header class="site-header">
  <a class="brand" href="../index.html">출근영어</a>
  <nav>
    <a href="../index.html#quick">사용법</a>
    <a href="index.html">표현</a>
    <a href="../guide/index.html">가이드</a>
    <a href="../index.html#pricing">요금</a>
    <a href="../support.html">지원</a>
    <a href="../privacy.html">개인정보</a>
  </nav>
</header>
"""


CTA = """<div class="notice">
  <p><strong>이 상황을 60초 동안 직접 말해보세요.</strong> 출근영어는 하루 한 상황을 말하면 자연스러운 문장 한 개와 팁 한 개를 돌려주는 iOS 앱이에요.</p>
  <p class="actions"><a class="btn btn-primary" href="https://apps.apple.com/kr/app/id6811576834" rel="noopener">App Store에서 받기</a> <a class="btn btn-secondary" href="../index.html">출근영어 알아보기</a></p>
</div>
"""

FOOTER = """<footer>
  <a href="mailto:richohios@gmail.com">richohios@gmail.com</a> ·
  <a href="../privacy.html">개인정보 처리방침</a> ·
  <a href="../support.html">지원</a><br>
  © 2026 출근영어: 직장인 AI 영어회화. All rights reserved.
</footer>

</div>
</body>
</html>
"""

ORG = {"@type": "Organization", "name": "출근영어", "url": SITE}
HUB_URL = SITE + "expressions/index.html"


def breadcrumb_ld(last_name=None, last_url=None):
    items = [
        {"@type": "ListItem", "position": 1, "name": "홈", "item": SITE},
        {"@type": "ListItem", "position": 2, "name": "표현", "item": HUB_URL},
    ]
    if last_name:
        items.append({"@type": "ListItem", "position": 3, "name": last_name, "item": last_url})
    return {"@type": "BreadcrumbList", "itemListElement": items}


def render_page(item, related):
    canonical = f"{SITE}expressions/{item['id']}.html"
    title = page_title(item)
    headline = title[: -len(" · 출근영어")]
    desc = page_description(item)
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BlogPosting",
                "headline": headline,
                "description": desc,
                "inLanguage": "ko",
                "datePublished": DATE,
                "dateModified": DATE,
                "author": ORG,
                "publisher": ORG,
                "mainEntityOfPage": canonical,
                "image": OG_IMAGE,
            },
            breadcrumb_ld(item["title_ko"], canonical),
        ],
    }
    chips = "\n".join(
        f'  <p><span class="chip" lang="en">{e(en)}</span> <span class="small muted">{e(ko)}</span></p>'
        for en, ko in item["chips"]
    )
    links = "\n".join(
        f'    <li><a href="{r["id"]}.html">{e(r["title_ko"])}</a></li>' for r in related
    )
    body = f"""
<nav class="breadcrumb" aria-label="현재 위치"><a href="../index.html">홈</a> › <a href="index.html">표현</a> › <span>{e(item["title_ko"])}</span></nav>

<main>
<article>

<section class="hero">
  <h1>{e(item["title_ko"])}</h1>
  <p class="label">직장인 영어 한 문장 · {e(item["category"])}</p>
</section>

<section>
  <h2>상황</h2>
  <p>{e(item["context_ko"])}</p>
  <p class="small muted" lang="en">{e(item["context_en"])}</p>
</section>

<section>
  <h2>질문</h2>
  <div class="card muted-card">
    <p class="label">상대가 이렇게 물어요</p>
    <h3 lang="en">{e(item["question_en"])}</h3>
  </div>
</section>

<section>
  <h2>이렇게 말해보세요</h2>
  <div class="card">
    <p>{e(item["intent_ko"])}.</p>
  </div>
{chips}
</section>

<section>
  <h2>자연스러운 한 문장</h2>
  <div class="card">
    <h3 lang="en">{e(item["sample_en"])}</h3>
    <p class="small muted">{e(item["sample_ko"])}</p>
  </div>
</section>

<section>
  <h2>팁 하나</h2>
  <p>{e(tip_sentence(item))}</p>
</section>

<hr>

<section>
  <h2>다른 상황도 연습해 보세요</h2>
  <ul>
{links}
  </ul>
  <p class="small"><a href="index.html">상황별 영어 한 문장 전체 보기</a></p>
</section>

</article>
</main>

{CTA}
"""
    return head(title, desc, canonical, "article", ld) + body + FOOTER


def render_hub(items):
    title = "직장인 영어 표현: 상황별 한 문장 · 출근영어"
    desc = ("회의·출장·거래처 통화에서 바로 쓰는 직장인 영어를 상황별 한 문장으로 모았어요. "
            "표현 조각 3개와 팁 하나로 하루 하나씩 연습해 보세요.")
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CollectionPage",
                "name": "상황별 영어 한 문장",
                "description": desc,
                "url": HUB_URL,
                "inLanguage": "ko",
                "isPartOf": {"@type": "WebSite", "name": "출근영어", "url": SITE},
                "publisher": ORG,
                "mainEntity": {
                    "@type": "ItemList",
                    "numberOfItems": len(items),
                    "itemListElement": [
                        {"@type": "ListItem", "position": i + 1, "name": it["title_ko"],
                         "url": f"{SITE}expressions/{it['id']}.html"}
                        for i, it in enumerate(items)
                    ],
                },
            },
            breadcrumb_ld(),
        ],
    }
    groups = []
    for cat in CATEGORY_ORDER:
        members = [it for it in items if it["category"] == cat]
        if not members:
            continue
        cards = "\n".join(
            f"""  <div class="card">
    <h3><a href="{it["id"]}.html">{e(it["title_ko"])}</a></h3>
    <p class="small muted" lang="en">{e(it["question_en"])}</p>
  </div>""" for it in members
        )
        groups.append(f"""<section>
  <h2>{e(cat)}</h2>
{cards}
</section>
""")
    body = f"""
<nav class="breadcrumb" aria-label="현재 위치"><a href="../index.html">홈</a> › <span>표현</span></nav>

<main>

<section class="hero">
  <h1>상황별 영어 한 문장</h1>
  <p class="tagline">직장에서 실제로 마주치는 상황 하나에, 자연스러운 영어 한 문장 하나.</p>
  <p>여기 있는 페이지는 출근영어 앱이 하루에 하나씩 건네는 오늘의 상황을 그대로 옮긴 거예요.
  상황과 상대의 질문을 읽고, 표현 조각 3개를 떠올린 뒤 자연스러운 한 문장과 비교해 보세요.
  하루 하나씩이면 충분해요.</p>
</section>

{"".join(groups)}
</main>

{CTA}
"""
    return head(title, desc, HUB_URL, "website", ld) + body + FOOTER


def write(path, content):
    old = None
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            old = f.read()
    if old == content:
        return "unchanged"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return "written" if old is None else "updated"


def main():
    items = load()
    os.makedirs(OUT_DIR, exist_ok=True)
    expected = {"index.html"} | {f"{it['id']}.html" for it in items}
    stats = {"written": 0, "updated": 0, "unchanged": 0}
    n = len(items)
    for i, it in enumerate(items):
        related = [items[(i + k) % n] for k in (1, 2, 3) if n > 1]
        stats[write(os.path.join(OUT_DIR, f"{it['id']}.html"), render_page(it, related))] += 1
    stats[write(os.path.join(OUT_DIR, "index.html"), render_hub(items))] += 1
    removed = []
    for name in sorted(os.listdir(OUT_DIR)):
        if name.endswith(".html") and name not in expected:
            os.remove(os.path.join(OUT_DIR, name))
            removed.append(name)

    print(f"expressions: {n} pages + hub -> {os.path.relpath(OUT_DIR, ROOT)}/")
    print(f"  written {stats['written']}, updated {stats['updated']}, unchanged {stats['unchanged']}"
          + (f", removed {', '.join(removed)}" if removed else ""))
    for it in items:
        t, d = page_title(it), page_description(it)
        print(f"  {it['id']:<11} title {len(t):>2}자  desc {len(d):>2}자  {t}")


if __name__ == "__main__":
    main()
