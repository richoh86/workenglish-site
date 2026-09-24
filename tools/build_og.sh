#!/usr/bin/env bash
# assets/og.html 을 headless Chrome으로 렌더링해 assets/og.png (1200x630) 를 만든다.
# 사용: tools/build_og.sh   (CHROME 환경변수로 브라우저 경로 변경 가능)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
OUT="$ROOT/assets/og.png"
"$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
  --window-size=1200,630 --screenshot="$OUT" "file://$ROOT/assets/og.html" >/dev/null 2>&1
sips -g pixelWidth -g pixelHeight "$OUT"
