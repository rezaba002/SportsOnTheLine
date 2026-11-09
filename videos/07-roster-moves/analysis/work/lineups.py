"""Match-by-match lineups from Valve's ranking details (Nov 2 2026 files: every match since May with the five who played).

1. Downloads the details file of every team in Valve's Nov 2 global standings (top 120) -> research/valve_details/.
2. Builds each team's lineup timeline: runs of matches with the same five.
3. Classifies each change:
   stand-in   a player fills in for a short run (<= STANDIN_MAX matches or <= STANDIN_DAYS days) and the regular returns
   permanent  the new five lasts (or is still playing at the end and the replaced player never came back) ...
   ongoing    the latest run differs but is short: could be a stand-in or a new signing -> needs a human check
Writes data/lineup_timeline.json and prints the timeline of the teams named on the command line (default: all changed).
"""
import json, pathlib, re, sys, time, urllib.request

HERE = pathlib.Path(__file__).resolve().parent
VALVE = pathlib.Path(r"D:\Youtube\video06\research\valve")
DET = HERE.parent / "research" / "valve_details"; DET.mkdir(parents=True, exist_ok=True)
BASE = "https://raw.githubusercontent.com/ValveSoftware/counter-strike_regional_standings/main/invitation/2026/"
STANDIN_MAX, STANDIN_DAYS = 8, 24

links = []
for line in (VALVE / "standings_global_2026_11_02.md").read_text(encoding="utf-8").splitlines():
    m = re.match(r"\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|.*\[details\]\((details/[^)]+)\)", line)
    if m and int(m.group(1)) <= 120:
        links.append((int(m.group(1)), m.group(3), m.group(4)))
for rank, team, rel in links:
    f = DET / pathlib.Path(rel).name
    if not f.exists():
        for k in range(3):
            try:
                f.write_bytes(urllib.request.urlopen(BASE + rel, timeout=60).read()); break
            except Exception:
                time.sleep(3)
        time.sleep(0.4)

from datetime import date
def d(s): return date.fromisoformat(s)

timeline = {}
for rank, team, rel in links:
    f = DET / pathlib.Path(rel).name
    if not f.exists():
        continue
    matches = []
    for line in f.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*\d+\s*\|\s*\d+\s*\|\s*(\d{4}-\d\d-\d\d)\s*\|\s*([^|]+?)\s*\|\s*([WL])\s*\|.*\|\s*([^|]+?)\s*\|\s*$", line)
        if m:
            matches.append({"date": m.group(1), "opp": m.group(2), "wl": m.group(3), "five": tuple(sorted(x.strip() for x in m.group(4).split(",")))})
    matches.sort(key=lambda x: x["date"])
    runs = []
    for mt in matches:
        if runs and runs[-1]["five"] == mt["five"]:
            runs[-1]["to"] = mt["date"]; runs[-1]["n"] += 1
        else:
            runs.append({"five": mt["five"], "from": mt["date"], "to": mt["date"], "n": 1})
    # classify each run that differs from the one before
    events = []
    for i in range(1, len(runs)):
        prev, cur = runs[i - 1], runs[i]
        ins, outs = sorted(set(cur["five"]) - set(prev["five"])), sorted(set(prev["five"]) - set(cur["five"]))
        short = cur["n"] <= STANDIN_MAX or (d(cur["to"]) - d(cur["from"])).days <= STANDIN_DAYS
        returns = any(set(outs) <= set(r["five"]) for r in runs[i + 1:])
        last = i == len(runs) - 1
        if short and returns:
            kind = "stand-in"
        elif returns and not short:
            kind = "long stand-in / temporary"
        elif last and short:
            kind = "ongoing (check)"
        else:
            kind = "permanent"
        events.append({"date": cur["from"], "in": ins, "out": outs, "kind": kind, "run_matches": cur["n"], "run_until": cur["to"]})
    timeline[team] = {"rank_nov": rank, "matches": len(matches), "first": matches[0]["date"] if matches else None,
                      "runs": [{**r, "five": list(r["five"])} for r in runs], "events": events}
out = HERE.parent / "data" / "lineup_timeline.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(timeline, indent=1, ensure_ascii=False), encoding="utf-8")

want = sys.argv[1:] or [t for t, v in timeline.items() if v["events"] and v["rank_nov"] <= 60]
for t in want:
    v = timeline.get(t)
    if not v:
        print(t, "not found"); continue
    print(f"\n{t} (#{v['rank_nov']}, {v['matches']} matches since {v['first']})")
    for e in v["events"]:
        print(f"  {e['date']}  {e['kind']:26} in: {', '.join(e['in']):22} out: {', '.join(e['out']):22} ({e['run_matches']} matches, until {e['run_until']})")
