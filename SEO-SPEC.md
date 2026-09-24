# 출근영어 사이트 SEO 반영 공통 스펙 (2026-09-24)

근거: `~/Documents/Obsidian Vault/outputs/workenglish-seo-audit-2026-09-24.md` (감사 보고서),
`~/Documents/Obsidian Vault/raw/workenglish-seo-2026/01-keyword-research-2026-09-24.md`, `02-competitor-seo-2026-09-24.md`.

사이트 루트: https://richoh86.github.io/workenglish-site/ (GitHub Pages, 정적 HTML, 템플릿 엔진 없음).
디자인 토큰·클래스는 `assets/site.css`에 있고, 새 페이지는 index.html의 골격(`.wrap` → `header.site-header` → `section` … → `footer`)을 그대로 복사해 쓴다. 톤: 해요체, 느낌표·이모지 없음, 과장 없음.

## 모든 페이지 `<head>` 필수 항목 (순서대로)
```html
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>…</title>                       <!-- 30자 내외, 뒤에 " · 출근영어" -->
<meta name="description" content="…"> <!-- 70~90자, 행동 문구 포함 -->
<link rel="canonical" href="https://richoh86.github.io/workenglish-site/<경로>">
<meta property="og:type" content="website|article">
<meta property="og:title" content="…">
<meta property="og:description" content="…">
<meta property="og:image" content="https://richoh86.github.io/workenglish-site/assets/og.png">
<meta property="og:url" content="(canonical과 동일)">
<meta property="og:site_name" content="출근영어">
<meta property="og:locale" content="ko_KR">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#F8F5F1" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#101211" media="(prefers-color-scheme: dark)">
<link rel="icon" href="/workenglish-site/assets/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="/workenglish-site/assets/apple-touch-icon.png">
<link rel="stylesheet" href="(상대경로)assets/site.css">
<script type="application/ld+json">…</script>
```
- 하위 폴더(`expressions/`, `guide/`) 페이지는 stylesheet·아이콘 경로를 `../assets/…`로 쓴다. 아이콘은 절대경로도 허용.
- JSON-LD는 페이지 종류별: 홈 = SoftwareApplication + FAQPage + Organization, 글 = Article(BlogPosting) + BreadcrumbList, 허브 = CollectionPage + BreadcrumbList, 비교 = Article + FAQPage(있을 때) + BreadcrumbList. `@context` 는 `https://schema.org`. 값은 페이지 본문과 일치해야 한다(FAQPage의 질문·답은 화면의 FAQ와 동일 텍스트).

## 상단 nav (모든 페이지 동일)
```
사용법(index.html#quick) · 표현(expressions/) · 가이드(guide/) · 요금(index.html#pricing) · 지원(support.html) · 개인정보(privacy.html)
```
하위 폴더에서는 `../index.html#quick` 등 상대경로.

## URL 규칙
- 매일 1문장: `expressions/<situation_id>.html` (예 `expressions/wk_014.html`), 허브 `expressions/index.html`.
- 가이드·비교: `guide/<slug>.html`(영문 소문자·하이픈), 허브 `guide/index.html`.
- 링크는 항상 `.html` 포함(GitHub Pages 확장자 없는 URL은 301).

## 글 하단 공통 CTA (표현·가이드 모두)
```html
<div class="notice">
  <p><strong>이 상황을 60초 동안 직접 말해보세요.</strong> 출근영어는 하루 한 상황을 말하면 자연스러운 문장 한 개와 팁 한 개를 돌려주는 iOS 앱이에요.</p>
  <p><a class="btn btn-secondary" href="../index.html">출근영어 알아보기</a></p>
</div>
```
App Store 링크는 아직 없다(출시 전). "곧 만나요" 문구 유지, 스토어 URL을 지어내지 않는다.

## 사실 규칙
- 경쟁사 가격·기능은 조사 파일(raw 02)에 적힌 것 또는 공식 페이지에서 오늘 확인한 것만 쓴다. 확인 못 하면 숫자를 쓰지 않고 "공식 사이트 기준"으로 넘긴다. 폄하 표현 금지, 사실 비교만.
- 출근영어 가격: 월 7,900원 / 연 59,000원 / 3일 무료 체험(출시 전 예정 가격). 음성은 iPhone 안에서 텍스트로 바뀌고 서버로 가지 않는다. 계정 없음. 스트릭 없음. 텍스트 모드 동등.

## 사이트맵
`tools/build_sitemap.py`(W1 작성)가 저장소의 모든 `.html`을 스캔해 `sitemap.xml`을 만든다. 각 워커는 페이지만 만들고 사이트맵은 마지막에 Advisor가 한 번 생성한다.
