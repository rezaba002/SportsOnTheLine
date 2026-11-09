"""Daily ranking-race data per region (HLTV's daily Valve ranking, Oct 5 -> last day collected) for Remotion.

Input: research/hltv/vrs_daily_*.json (collected in the built-in browser, see receiver.py).
Output: sotl-graphics/public/data/vrs_daily_{eu,am,as}.json, same shape as vrs_race_eu.json (rank field = regional rank).
Prints, per region, every day a team crossed the Major line, for the callouts.
"""
import json, pathlib

SRC = sorted((pathlib.Path(__file__).resolve().parents[1] / "research" / "hltv").glob("vrs_daily_*.json"))[-1]
OUT = pathlib.Path(r"D:\Youtube\sotl-graphics\public\data")
REGIONS = {"eu": ("EU", "Europe", 18, 24), "am": ("AM", "Americas", 9, 15), "as": ("AS", "Asia", 5, 10)}
MON = {"10": "Oct", "11": "Nov", "12": "Dec"}

raw = json.loads(SRC.read_text(encoding="utf-8"))
days = sorted(raw["days"])

for key, (code, region, spots, show) in REGIONS.items():
    frames = []
    for d in days:
        lst, names = [], set()
        for t in raw["days"][d]:  # same name twice (an old and a current roster): the higher-ranked one counts
            if t["g"] == code and t["n"] not in names:
                names.add(t["n"]); lst.append(t)
        frames.append({"label": f"{MON[d[5:7]]} {int(d[8:])}", "date": d,
                       "teams": [{"name": t["n"], "points": t["p"], "rank": i + 1} for i, t in enumerate(lst)]})
    seen = sorted({t["name"] for f in frames for t in f["teams"] if t["rank"] <= show})
    for f in frames:
        f["teams"] = [t for t in f["teams"] if t["name"] in seen]
    (OUT / f"vrs_daily_{key}.json").write_text(json.dumps(
        {"region": region, "spots": spots, "show": show, "teams": seen, "frames": frames,
         "logos": {n: raw["logos"].get(n, "") for n in seen}, "approximate": []}, indent=1), encoding="utf-8")

    crossings = []
    for a, b in zip(frames, frames[1:]):
        ra = {t["name"]: t["rank"] for t in a["teams"]}
        for t in b["teams"]:
            if t["name"] in ra and (ra[t["name"]] <= spots) != (t["rank"] <= spots):
                crossings.append(f'{b["label"]}: {t["name"]} {"IN" if t["rank"] <= spots else "OUT"} ({ra[t["name"]]}->{t["rank"]})')
    print(f"{region}: {len(seen)} teams, {len(frames)} days, {len(crossings)} line crossings")
    for c in crossings:
        print("  ", c)
