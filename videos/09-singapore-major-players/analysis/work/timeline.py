"""Video 09 timeline: narration blocks back to back (longer pauses between sections, air after the intro),
word timings for cues, and every number on screen straight from data/ (swing.json, clock.json, players.json, igls.json).
Writes sotl-graphics/public/data/video09.json and copies the mp3s to public/narration09/."""
import json, pathlib, shutil

HERE = pathlib.Path(__file__).resolve().parent
D = HERE.parent / "data"
PUB = pathlib.Path(r"D:\Youtube\sotl-graphics\public")
FPS, GAP, SECTION_GAP, LEAD = 30, 8, 22, 12
SECTION_START = {"k1", "i1", "f1", "r1", "w1"}
AIR = {"k1": 10, "m2": 10, "f4": 16, "r5": 12}
# channel intro v2 (sotl-graphics/src/cards/ChannelIntro2.tsx) sits right after the hook: same frame count as INTRO2_FRAMES
IW = json.load(open(PUB / "data" / "intro.json", encoding="utf-8"))["words"]
INTRO_FRAMES = round(IW[17]["e"] * FPS) + 8 + 28
INTRO_IN, INTRO_OUT = 14, 10      # frames after h4 before the intro starts / after the intro before k1
narr = json.loads((HERE / "narration" / "narration.json").read_text(encoding="utf-8"))

(PUB / "narration09").mkdir(exist_ok=True)
t, blocks, words, intro = LEAD, [], [], None
for b in narr:
    if b["id"] in SECTION_START:
        t += SECTION_GAP - GAP
    shutil.copy(HERE / "narration" / f"{b['id']}.mp3", PUB / "narration09" / f"{b['id']}.mp3")
    dur = round(b["duration"] * FPS)
    blocks.append({"id": b["id"], "from": t, "dur": dur, "file": f"narration09/{b['id']}.mp3"})
    for w in b["words"]:
        words.append({"w": w["w"], "s": t + round(w["s"] * FPS), "e": t + round(w["e"] * FPS), "block": b["id"]})
    t += dur + GAP + AIR.get(b["id"], 0)
    if b["id"] == "h4":                       # the hook ends -> channel intro
        intro = {"from": t - GAP + INTRO_IN, "dur": INTRO_FRAMES}
        t = intro["from"] + INTRO_FRAMES + INTRO_OUT - (SECTION_GAP - GAP)
END_FRAMES = 600
end_from = t + 30
total = end_from + END_FRAMES

S = json.load(open(D / "swing.json", encoding="utf-8"))
C = json.load(open(D / "clock.json", encoding="utf-8"))
P = {p["player"]: p for p in json.load(open(D / "players.json", encoding="utf-8"))}
G = json.load(open(D / "games.json", encoding="utf-8"))
ranked = {n: v for n, v in S.items() if v["maps"] >= 60}
order = sorted(ranked, key=lambda n: -ranked[n]["rounds_per_map"])


def card(n):
    v = S[n]
    return {"name": n, "team": v["team"], "role": v["role"], "igl": v["igl"], "rpm": v["rounds_per_map"], "season": round(v["season_rounds"]),
            "maps": v["maps"], "vs_mates": v.get("vs_teammates_per_map"), "rank": order.index(n) + 1 if n in ranked else None,
            "by_time": v["by_time_per_map"], "kill_med": C.get(n, {}).get("kill_med"), "open_kill_pct": P.get(n, {}).get("opening_kill_pct")}


igls = [n for n in order if ranked[n]["igl"]]
non_igl = [n for n in order if not ranked[n]["igl"]]
close = sum(1 for g in G.values() if g["score"][0] is not None and g["score"][0] - g["score"][1] <= 2)
data = {
    "fps": FPS, "total": total, "end_from": end_from, "blocks": blocks, "words": words, "intro": intro,
    "n_ranked": len(ranked), "rounds": 46353, "maps": len(G), "close_maps_pct": round(100 * close / len(G)),
    "top10": [card(n) for n in order[:10]],
    "spirit": [card(n) for n in ("donk", "sh1ro")],
    "igls": [card(n) for n in igls],
    "igl_red": sum(1 for n in igls if ranked[n]["rounds_per_map"] < 0),
    "falcons": [card("m0NESY"), card("karrigan")],
    "reds": [card(n) for n in non_igl[::-1][:4]],
    "heroic": [card(n) for n in ("nilo", "Brollan", "susp", "Chr1zN")],
    "watch_green": [card(n) for n in ("ZywOo", "m0NESY", "donk", "sh1ro")],
    "watch_red": [card(n) for n in ("Neityu", "BELCHONOKK", "Brollan", "susp")],
    "model": {"even": 0.5, "up": 0.7},
}
(PUB / "data").mkdir(exist_ok=True)
(PUB / "data" / "video09.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"intro {intro}"); print(f"{len(blocks)} blocks, narration ends {t / FPS:.1f}s, end screen {end_from / FPS:.1f}s, total {total / FPS:.1f}s")
print("top10:", [(c["name"], c["rpm"]) for c in data["top10"]])
print("reds:", [(c["name"], c["rpm"]) for c in data["reds"]], "| IGLs red", data["igl_red"], "of", len(igls), "| close maps", data["close_maps_pct"], "%")
