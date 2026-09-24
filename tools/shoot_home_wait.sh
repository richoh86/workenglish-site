#!/bin/bash
# Home screenshot with a virtual-time budget so async-decoded images have time to paint.
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT=/Users/richoh/.claude/jobs/6675f30b/tmp/shots
"$CHROME" --headless=new --disable-gpu --hide-scrollbars --window-size=900,1400 --virtual-time-budget=8000 --screenshot="$OUT/home-wait.png" "file://$(pwd)/index.html" 2>/dev/null
ls -la "$OUT/home-wait.png"
