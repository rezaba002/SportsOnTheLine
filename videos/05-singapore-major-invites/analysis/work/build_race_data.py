"""Build the Europe ranking-race data (Valve Regional Standings, monthly 2026 files) for the Remotion race chart.

Team set = Valve's Europe file of Oct 5 (Valve sets region by roster, so a name can switch region: Liquid's Sep roster
was "Europe", its Oct roster is not). Sep 7 and Oct 5 use Valve's own Europe ranks. Jan-Aug have no Europe file, so the
rank there is the order of the Oct-5 Europe teams in that month's global file (approximate: teams that left Europe or
disbanded are missing). Same name twice in a month (two rosters) -> the better-ranked row counts.
Output: sotl-graphics/public/data/vrs_race_eu.json
"""
import json, pathlib

VRS = pathlib.Path(__file__).resolve().parents[1] / "research" / "vrs"
OUT = pathlib.Path(r"D:\Youtube\sotl-graphics\public\data\vrs_race_eu.json")
MONTHS = ["01_05", "02_02", "03_02", "04_06", "05_04", "06_01", "07_06", "08_03", "09_07", "10_05"]
LABEL = {"01_05": "Jan 5", "02_02": "Feb 2", "03_02": "Mar 2", "04_06": "Apr 6", "05_04": "May 4", "06_01": "Jun 1",
         "07_06": "Jul 6", "08_03": "Aug 3", "09_07": "Sep 7", "10_05": "Oct 5"}
SHOW = 26  # rows on screen; the cutoff sits after 18


def rows(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        c = [x.strip() for x in line.split("|")]
        if len(c) > 4 and c[1].isdigit():
            yield int(c[1]), int(c[2]), c[3]


eu = {name for _, _, name in rows(VRS / "europe_2026_10_05.md")}

frames = []
for m in MONTHS:
    best = {}
    regional = VRS / f"europe_2026_{m}.md"
    src = regional if regional.exists() else VRS / f"global_2026_{m}.md"
    for rank, pts, name in rows(src):
        if name in eu and name not in best:
            best[name] = (rank, pts)
    order = sorted(best.items(), key=lambda kv: kv[1][0])
    frames.append({"label": LABEL[m], "teams": [{"name": n, "points": p, "rank": i + 1, "sourceRank": g}
                                                for i, (n, (g, p)) in enumerate(order)]})

# keep only teams that are ever on screen
seen = sorted({t["name"] for f in frames for t in f["teams"] if t["rank"] <= SHOW})
for f in frames:
    f["teams"] = [t for t in f["teams"] if t["name"] in seen]

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({"region": "Europe", "spots": 18, "show": SHOW, "teams": seen, "frames": frames, "approximate": [f["label"] for f, m in zip(frames, MONTHS) if not (VRS / f"europe_2026_{m}.md").exists()]},
                          indent=1), encoding="utf-8")
print(len(seen), "teams,", len(frames), "frames ->", OUT)
for f in frames[-1:]:
    print(f["label"], [(t["rank"], t["name"]) for t in f["teams"][:20]])
