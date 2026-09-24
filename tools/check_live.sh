#!/bin/bash
# Waits for GitHub Pages to serve the new build, then checks key URLs.
B=https://richoh86.github.io/workenglish-site
for i in $(seq 1 24); do
  if curl -s "$B/" | grep -q 'rel="canonical"'; then echo "LIVE after $((i*15))s"; break; fi
  sleep 15
done
for p in "" robots.txt sitemap.xml assets/og.png assets/favicon-32.png expressions/index.html expressions/wk_014.html guide/index.html guide/meeting-english-phrases.html guide/speak-vs-workenglish.html; do
  curl -s -o /dev/null -w "%{http_code} %{size_download}B  $p\n" "$B/$p"
done
curl -s "$B/" | grep -o '<title>[^<]*</title>'
curl -s "$B/sitemap.xml" | grep -c "<loc>"
