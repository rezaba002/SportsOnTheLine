"""All finished CS2 matches on bo3.gg since the season start -> research/matches_2026.json"""
import json
from bo3 import api

SEASON_START = "2026-01-01"
base = ("matches?page%5Blimit%5D=100&sort=-start_date&filter%5Bmatches.status%5D%5Bin%5D=finished"
        "&filter%5Bmatches.discipline_id%5D%5Beq%5D=1&with=teams,tournament")
out, off = [], 0
while True:
    d = api(base + f"&page%5Boffset%5D={off}", cache=False)
    rows = d["results"]
    if not rows:
        break
    keep = [r for r in rows if r["start_date"][:10] >= SEASON_START]
    for r in keep:
        out.append({k: r.get(k) for k in ("id", "slug", "start_date", "tier", "bo_type", "parsed_status",
                                          "team1_id", "team2_id", "team1_score", "team2_score")}
                   | {"team1": (r.get("team1") or {}).get("name"), "team2": (r.get("team2") or {}).get("name"),
                      "tournament": (r.get("tournament") or {}).get("name")})
    if len(keep) < len(rows):
        break
    off += 100
    if off % 2000 == 0:
        print(off, rows[-1]["start_date"][:10], flush=True)
json.dump(out, open("../research/matches_2026.json", "w", encoding="utf-8"), ensure_ascii=False)
print("matches since", SEASON_START, len(out))
