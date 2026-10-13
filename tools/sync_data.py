"""Copies the app's situation + scaffold data into data/ for the expression pages.
Usage: python3 tools/sync_data.py <worktree root>"""
import json
import sys

root = sys.argv[1]
src = json.load(open(f"{root}/Tools/l10n/source.json"))
batch2 = json.load(open(f"{root}/Tools/l10n/batch2-source.json"))["situations"]
for sid, s in batch2.items():
    src["situations"][sid] = {k: s[k] for k in ("title_ko", "context_ko", "context_en", "question_en")}
scaffold = json.load(open(f"{root}/Tools/l10n/scaffold-source.json"))
# batch3 = 1.2 직무 트랙 60개(tr_<track>_NNN). 발판(scaffold)이 상황 안에 함께 들어 있다.
batch3 = json.load(open(f"{root}/Tools/l10n/batch3-source.json"))["situations"]
for sid, s in batch3.items():
    src["situations"][sid] = {k: s[k] for k in ("title_ko", "context_ko", "context_en", "question_en")}
    scaffold[sid] = {k: s["scaffold"][k] for k in ("intent", "chips", "sample_en", "sample_gloss")}
json.dump(src, open("data/situations-source.json", "w"), ensure_ascii=False, indent=1)
json.dump(scaffold, open("data/scaffold-source.json", "w"), ensure_ascii=False, indent=1)
print("situations", len(src["situations"]), "scaffold", len(scaffold))
