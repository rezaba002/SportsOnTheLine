"""Video 07 timeline: narration blocks back to back (longer pauses between sections), word timings for cues, and every
number on screen from data/moves_verdict.json + valve_rosters.json + lineup_timeline.json.
Writes sotl-graphics/public/data/video07.json and copies the mp3s to public/narration07/."""
import json, pathlib, shutil

HERE = pathlib.Path(__file__).resolve().parent
PUB = pathlib.Path(r"D:\Youtube\sotl-graphics\public")
FPS, GAP, SECTION_GAP, LEAD = 30, 8, 20, 10
SECTION_START = {"m1", "a1", "b1", "s1", "w1", "t1", "z1"}
narr = json.loads((HERE / "narration" / "narration.json").read_text(encoding="utf-8"))
V = json.loads((HERE.parent / "data" / "moves_verdict.json").read_text(encoding="utf-8"))
R = json.loads((HERE.parent / "research" / "valve_rosters.json").read_text(encoding="utf-8"))
L = json.loads((HERE.parent / "data" / "lineup_timeline.json").read_text(encoding="utf-8"))

(PUB / "narration07").mkdir(exist_ok=True)
t, blocks, words = LEAD, [], []
for b in narr:
    if b["id"] in SECTION_START:
        t += SECTION_GAP - GAP
    shutil.copy(HERE / "narration" / f"{b['id']}.mp3", PUB / "narration07" / f"{b['id']}.mp3")
    dur = round(b["duration"] * FPS)
    blocks.append({"id": b["id"], "from": t, "dur": dur, "file": f"narration07/{b['id']}.mp3"})
    for w in b["words"]:
        words.append({"w": w["w"], "s": t + round(w["s"] * FPS), "e": t + round(w["e"] * FPS), "block": b["id"]})
    t += dur + GAP
END_FRAMES = 600                      # 20 s end screen (YouTube end-screen elements: video suggestions + subscribe)
end_from = t + 30
total = end_from + END_FRAMES

teams = {o["team"]: o for o in V["teams"]}
rank = lambda name: R.get(name, {}).get("ranks", {})


def card(name):
    o = teams[name]; rk = rank(name)
    return {"team": name, "in": o["in"], "out": o["out"], "win_A": o["win_A"], "win_B": o["win_B"], "verdict_pts": o["verdict_pts"],
            "rank_jun": rk.get("2026_06_01"), "rank_nov": rk.get("2026_11_02"), "moved": o["moved"], "since": o["real_five_since"]}


judged = [o for o in V["teams"] if not o["too_early"]]
moved = [o for o in judged if o["moved"]]; kept = [o for o in judged if not o["moved"]]
jl = []
for team in ("MOUZ", "Vitality"):
    for r in L[team]["runs"]:
        if "jL" in r["five"]:
            jl.append({"team": team, "from": r["from"], "to": r["to"], "matches": r["n"]})
data = {
    "fps": FPS, "total": total, "end_from": end_from, "blocks": blocks, "words": words,
    "hook_teams": [{"team": o["team"], "n_in": len(o["in"])} for o in sorted(V["teams"], key=lambda o: -abs(o["verdict_pts"])) if o["moved"]][:18],
    "answer": {"moved_n": len(moved), "moved_up": sum(o["verdict"] > 0 for o in moved), "kept_n": len(kept), "kept_up": sum(o["verdict"] > 0 for o in kept),
               "avg_pts": round(sum(o["verdict_pts"] for o in moved) / len(moved), 1)},
    "method_example": card("MOUZ"),
    "best": [card(n) for n in ("Nemiga", "MOUZ", "HEROIC")],
    "best_more": [card(n) for n in ("Liquid", "PARIVISION", "fnatic", "100 Thieves")],
    "worst": [card(n) for n in ("paiN", "G2")],
    "still": [card(n) for n in ("9z", "B8", "Spirit")],
    "spirit": {**card("Spirit"), "valve_ranks": rank("Spirit")},
    "too_early": [o["team"] for o in V["teams"] if o["too_early"] and o["moved"]],
    "jl": jl,
}
(PUB / "data" / "video07.json").write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"{len(blocks)} blocks, {total} frames ({total / FPS:.1f} s); answer {data['answer']}; too early {data['too_early']}; jL {jl}")
