"""Lineup changes from Valve's monthly global standings (each row lists the team's five). Jun 1 -> Nov 2 2026.
Prints every top-40 team whose five changed, with players in / out and its rank at both ends; writes rosters.json."""
import json, re, pathlib
P = pathlib.Path(r"D:\Youtube\video06\research\valve")
OUT = pathlib.Path(r"D:\Youtube\video07\research\valve_rosters.json")
MONTHS = ["2026_06_01", "2026_07_06", "2026_08_03", "2026_09_07", "2026_10_05", "2026_11_02"]

def rosters(f):
    out = {}
    for line in (P / f).read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", line)
        if m and m.group(3) not in out:      # duplicate names: the first (higher) row is the real team
            out[m.group(3)] = {"rank": int(m.group(1)), "points": int(m.group(2)), "five": sorted(x.strip() for x in m.group(4).split(","))}
    return out

R = {m: rosters(f"standings_global_{m}.md") for m in MONTHS}
teams = sorted(set(R[MONTHS[0]]) | set(R[MONTHS[-1]]))      # every team (the 40 filter is only for the printout)
report = {}
for t in teams:
    seq = [(m, R[m].get(t)) for m in MONTHS]
    changes, prev = [], None
    for m, v in seq:
        if v and prev and set(v["five"]) != set(prev[1]["five"]):
            changes.append({"between": [prev[0], m], "in": sorted(set(v["five"]) - set(prev[1]["five"])), "out": sorted(set(prev[1]["five"]) - set(v["five"]))})
        if v: prev = (m, v)
    report[t] = {"ranks": {m: (v["rank"] if v else None) for m, v in seq}, "points": {m: (v["points"] if v else None) for m, v in seq}, "changes": changes}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
ch = {t: r for t, r in report.items() if r["changes"] and min([x for x in r["ranks"].values() if x] or [999]) <= 40}
print(len(teams), "teams in the world top 40 (June or November);", len(ch), "changed their five")
for t, r in ch.items():
    rk = r["ranks"]; first = next((x for x in rk.values() if x), None); last = rk[MONTHS[-1]]
    moves = "; ".join(f"{c['between'][0][5:].replace('_','/')}-{c['between'][1][5:].replace('_','/')}: +{','.join(c['in'])} -{','.join(c['out'])}" for c in r["changes"])
    print(f"  {t:18} #{first} -> #{last}   {moves}")
