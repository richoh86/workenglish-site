#!/bin/bash
# Headless screenshots of key pages for a visual check. Run from repo root.
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT=${1:-/Users/richoh/.claude/jobs/6675f30b/tmp/shots}
mkdir -p "$OUT"
ROOT="file://$(pwd)"
shot() { "$CHROME" --headless=new --disable-gpu --hide-scrollbars --window-size="$2" --screenshot="$OUT/$3" "$ROOT/$1" 2>/dev/null; }
shot index.html 900,2400 home.png
shot guide/meeting-english-phrases.html 900,2600 guide-meeting.png
shot guide/best-english-speaking-apps-for-office-workers-2026.html 900,2600 guide-apps.png
shot expressions/wk_014.html 900,2000 expr.png
shot expressions/index.html 900,2000 expr-hub.png
ls -la "$OUT"
