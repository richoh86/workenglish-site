#!/bin/bash
# Waits until the live home page carries the App Store link, then spot-checks two pages.
B=https://richoh86.github.io/workenglish-site
for i in $(seq 1 20); do
  n=$(curl -s "$B/" | grep -c "apps.apple.com/kr/app/id6811576834")
  if [ "$n" != "0" ]; then echo "store links on home: $n (after $((i*15))s)"; break; fi
  sleep 15
done
echo "speak-vs page links: $(curl -s "$B/guide/speak-vs-workenglish.html" | grep -c id6811576834)"
echo "expression page: $(curl -s -o /dev/null -w '%{http_code}' "$B/expressions/wk_014.html")"
