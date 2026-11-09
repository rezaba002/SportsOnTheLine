"""Parse the playoff brackets of the five CS2 Majors (Liquipedia wikitext) into results.json.

Map score = rounds by half (t1t + t1ct) plus every overtime half (o1t1t, o1t1ct, ...).
Rounds: R1 = quarterfinals, R2 = semifinals, R3 = grand final.
"""
import json, pathlib, re

SRC = {"cph24": "cph24.wiki", "sha24": "sha24_playoffs.wiki", "aus25": "aus25_playoffs.wiki",
       "bud25": "bud25_playoffs.wiki", "col26": "col26_playoffs.wiki"}
ROUND = {"R1": "QF", "R2": "SF", "R3": "Final"}


def block(text, start):
    """Return the {{...}} block starting at index `start` (balanced braces)."""
    depth, i = 0, start
    while i < len(text):
        if text.startswith("{{", i):
            depth += 1; i += 2; continue
        if text.startswith("}}", i):
            depth -= 1; i += 2
            if depth == 0:
                return text[start:i]
            continue
        i += 1
    raise ValueError("unbalanced")


def side_total(m, team):
    total = sum(int(m.get(f"t{team}{s}", 0) or 0) for s in ("t", "ct"))
    ot = 0
    for k in range(1, 10):
        a = m.get(f"o{k}t{team}t"); b = m.get(f"o{k}t{team}ct")
        if a is None and b is None:
            break
        ot += int(a or 0) + int(b or 0)
    return total + ot, ot


results = {}
for key, fn in SRC.items():
    t = pathlib.Path(fn).read_text(encoding="utf-8")
    b = block(t, t.index("{{Bracket|Bracket/8"))
    matches = []
    for mm in re.finditer(r"\|(R(\d)M(\d))=\{\{Match", b):
        mb = block(b, mm.start() + len(mm.group(1)) + 2)
        teams = re.findall(r"\{\{TeamOpponent\|([^}|]+)", mb)
        maps = []
        for mp in re.finditer(r"\{\{Map\|", mb):
            seg = block(mb, mp.start())
            kv = dict(re.findall(r"\|(\w+)=([^|}\n]*)", seg))
            if kv.get("finished") != "true":
                continue
            s1, ot1 = side_total(kv, 1); s2, ot2 = side_total(kv, 2)
            maps.append({"map": kv.get("map"), "score": [s1, s2], "overtime": ot1 + ot2 > 0,
                         "stats": kv.get("stats"), "vod": kv.get("vod")})
        won = [sum(1 for x in maps if x["score"][0] > x["score"][1]), sum(1 for x in maps if x["score"][1] > x["score"][0])]
        date = re.search(r"\|date=([^|{\n]*)", mb)
        hltv = re.search(r"\|hltv=(\d+)", mb)
        matches.append({"round": ROUND.get(f"R{mm.group(2)}", mm.group(1)), "id": mm.group(1), "teams": teams[:2],
                        "series": won, "maps": maps, "date": date.group(1).strip() if date else None,
                        "hltv": hltv.group(1) if hltv else None})
    results[key] = matches

pathlib.Path("results.json").write_text(json.dumps(results, indent=1), encoding="utf-8")
for key, ms in results.items():
    print("=" * 10, key)
    for m in ms:
        maps = ", ".join(f"{x['map']} {x['score'][0]}-{x['score'][1]}{' OT' if x['overtime'] else ''}" for x in m["maps"])
        print(f"  {m['round']:5} {m['teams'][0]:>10} {m['series'][0]}-{m['series'][1]} {m['teams'][1]:<10} | {maps}")
