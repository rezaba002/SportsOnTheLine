"""Video 05 timeline: Brian's narration (work/narration/narration.json, word timings) -> what is on screen and when.

Every visual beat is tied to a narration block; inside a block, a card / a move / a reveal starts on a spoken word
("drop", "back", "Out"…), so the picture follows the voice. Cards are filled from the data, never typed by hand:
match rows from research/hltv/team_matches_2026-11-02.json, ranks/points from the daily race files.
Output: sotl-graphics/public/data/video05_timeline.json; narration mp3s copied to sotl-graphics/public/narration05/.
"""
import json, re, shutil
from pathlib import Path

FPS = 30
HERE = Path(__file__).resolve().parent
GFX = Path(r"D:\Youtube\sotl-graphics\public")
NAR = json.loads((HERE / "narration" / "narration.json").read_text(encoding="utf-8"))
NAR = {b["id"]: b for b in NAR}
MATCHES = json.loads((HERE.parent / "research" / "hltv" / "team_matches_2026-11-02.json").read_text(encoding="utf-8"))
RACE = {k: json.loads((GFX / "data" / f"vrs_daily_{f}.json").read_text(encoding="utf-8")) for k, f in
        (("euDaily", "eu"), ("amDaily", "am"), ("asDaily", "as"))}
GAP = 0.35            # seconds of air between blocks
REGION_GAP = 0.9      # extra air before a new region

MON = {"10": "Oct", "11": "Nov"}


def day_index(ds, date):
    return next(i for i, f in enumerate(RACE[ds]["frames"]) if f["date"] == date)


def rank_points(ds, date, team):
    t = next(t for t in RACE[ds]["frames"][day_index(ds, date)]["teams"] if t["name"] == team)
    return t["rank"], t["points"]


def label(date):  # 2026-10-27 -> Oct 27
    return f"{MON[date[5:7]]} {int(date[8:])}"


def matches(team, dates, event_hint=None):
    """The team's matches on these dates (YYYY-MM-DD), oldest first, from the HLTV details data."""
    want = {f"{d[8:10]}/{d[5:7]}/{d[2:4]}" for d in dates}
    rows = [m for m in MATCHES[team]["matches"] if m["date"] in want and (not event_hint or event_hint.lower() in m["event"].lower())]
    rows.sort(key=lambda m: (m["date"][6:], m["date"][3:5], m["date"][:2]))
    assert rows, (team, dates)
    return [{"date": label(f"20{m['date'][6:]}-{m['date'][3:5]}-{m['date'][:2]}"), "opp": m["opp"], "wl": m["wl"], "event": m["event"],
             "pts": int(m["pts"])} for m in rows]


def impact(ds, team, d0, d1, rows=None):
    """Rank change over the days, and the points the card's own matches are worth (HLTV's per-match value), so a win
    never shows a minus because of something else the team did that day."""
    r0, p0 = rank_points(ds, d0, team); r1, p1 = rank_points(ds, d1, team)
    return {"team": team, "rankFrom": r0, "rankTo": r1, "points": sum(r["pts"] for r in rows) if rows else p1 - p0}


def word_time(block, word, nth=1, after=-1.0):
    """Start (s) of the nth spoken occurrence of `word` (a word or a whole multi-word unit) after `after` seconds."""
    norm = lambda s: re.sub(r"[^\w']", "", s).lower()
    units = [w for w in NAR[block]["words"] if w["s"] > after]
    hits = [w for w in units if norm(w["w"]) == norm(word)] or [w for w in units if norm(w["w"].split()[0]) == norm(word.split()[0])]
    assert len(hits) >= nth, (block, word, [w["w"] for w in NAR[block]["words"]])
    return hits[nth - 1]["s"]


# ---------------- beats ----------------
# race step: dict(to=date, card=..., move=(word, nth) or None, focus=[...]); a step starts at `at` (word) or block start
def race(ds, blocks, start, steps, focus=(), banner=None, rows=None):
    return {"kind": "race", "ds": ds, "blocks": blocks, "start": start, "steps": steps, "focus": list(focus), "banner": banner,
            "rows": rows or {"euDaily": 24, "amDaily": 14, "asDaily": 10}[ds]}


def free(ds, blocks, start, to):
    """The race running on its own between two days, full brightness, no card, no stamps: viewers watch."""
    return {"kind": "race", "free": True, "ds": ds, "blocks": blocks, "start": start, "steps": [dict(to=to, move=None, card=None)], "focus": [], "banner": None,
            "rows": {"euDaily": 24, "amDaily": 14, "asDaily": 10}[ds]}


def list_card(ds, team, event, dates, d0, d1, title=None, tag=None, tag_opp=None):
    rows = matches(team, dates, event)
    return {"type": "list", "team": team, "event": event, "title": title, "tag": tag, "tagOpp": tag_opp,
            "rows": rows, "impact": impact(ds, team, d0, d1, rows)}


def duel(ds, left, right, d0, d1, same_event=True):
    """Two sides; each: team, event, its matches. Head-to-head when both list the same match."""
    sides = []
    for (team, event, dates), other in ((left, right[0]), (right, left[0])):
        rows = matches(team, dates, event)
        if same_event:   # head-to-head: only the matches between the two teams
            rows = [r for r in rows if r["opp"] == other]
            assert rows, (team, other, dates)
        sides.append({"team": team, "event": event, "rows": rows, "impact": impact(ds, team, d0, d1, rows)})
    return {"type": "duel", "sides": sides, "sameEvent": same_event}


def roster(team, d0, d1):
    return {"type": "roster", "team": team, "fromDate": d0, "toDate": d1}


def noplay(ds, team, d0, d1, why):
    r0, _ = rank_points(ds, d0, team); r1, _ = rank_points(ds, d1, team)
    return {"type": "noplay", "team": team, "from": r0, "to": r1, "why": why, "date": f"{label(d0)} → {label(d1)}"}


def verdict(ds, date, ranks, switch, spots):
    teams = [t for t in RACE[ds]["frames"][day_index(ds, date)]["teams"] if t["rank"] in ranks]
    return {"kind": "verdict", "ds": ds, "date": date, "spots": spots, "rows": [{"rank": t["rank"], "name": t["name"], "points": t["points"]} for t in teams],
            "switch": switch, "region": RACE[ds]["region"]}


def missed(ds, block, teams, spots):
    last = next(t for t in RACE[ds]["frames"][-1]["teams"] if t["rank"] == spots)
    out = []
    for name in teams:
        r, p = rank_points(ds, RACE[ds]["frames"][-1]["date"], name)
        out.append({"name": name, "rank": r, "points": p, "short": last["points"] - p})  # "at" set in build()
    return {"kind": "missed", "ds": ds, "blocks": [block], "region": RACE[ds]["region"], "teams": out, "lastIn": last["name"], "lastPoints": last["points"]}


def made_it(ds, blocks, stages):
    return {"kind": "madeit", "ds": ds, "blocks": blocks, "region": RACE[ds]["region"], "stages": stages}


EU, AM, AS = "euDaily", "amDaily", "asDaily"
BEATS = [
    {"kind": "page", "page": "teams32", "blocks": ["h01"]},
    {"kind": "page", "page": "cutoff", "blocks": ["h02"]},
    {"kind": "page", "page": "teasers", "blocks": ["h03"]},
    {"kind": "page", "page": "title", "blocks": ["h04"]},
    {"kind": "page", "page": "ranking", "blocks": ["r01"]},
    {"kind": "page", "page": "spots", "blocks": ["r02"]},
    {"kind": "page", "page": "daily", "blocks": ["r03"]},
    # ---------------- Europe ----------------
    # v2 (owner): the race runs on its own, bright; a card only on the result that decided a team's fate.
    race(EU, ["e01"], "2026-10-06", [], banner={"title": "EUROPE", "sub": "18 SPOTS"}),
    free(EU, ["e02"], "2026-10-06", "2026-10-23"),
    race(EU, ["e03"], "2026-10-23", [dict(to="2026-10-25", move=("twenty-sixth", 1),
         card=list_card(EU, "Natus Vincere", "PGL Masters", ["2026-10-24", "2026-10-25"], "2026-10-23", "2026-10-25", title="THE RUN THAT SENT THEM"))],
         focus=["Natus Vincere"]),
    free(EU, ["e04"], "2026-10-25", "2026-10-28"),
    race(EU, ["e05"], "2026-10-28", [dict(to="2026-10-29", move=("they", 1),
         card=duel(EU, ("FaZe", "RLG Tesla", ["2026-10-29"]), ("B8", "RLG Tesla", ["2026-10-29"]), "2026-10-28", "2026-10-29"))], focus=["B8", "FaZe"]),
    race(EU, ["e06"], "2026-10-29", [dict(to="2026-10-30", move=("won", 1),
         card=duel(EU, ("Eternal Fire", "Stake Ranked", ["2026-10-30"]), ("fnatic", "Stake Ranked", ["2026-10-30"]), "2026-10-29", "2026-10-30"))],
         focus=["Eternal Fire", "fnatic"]),
    free(EU, ["e07"], "2026-10-30", "2026-10-31"),
    race(EU, ["e08"], "2026-10-31", [dict(to="2026-11-01", move=("100 thieves", 2),
         card=duel(EU, ("HOTU", "GLuck Moscow", ["2026-11-01"]), ("100 Thieves", "FiRe Last Chance", ["2026-11-01"]), "2026-10-31", "2026-11-01", same_event=False))],
         focus=["HOTU", "100 Thieves"]),
    verdict(EU, "2026-11-02", range(16, 22), ("hotu", 1), 18) | {"blocks": ["e11"]},
    missed(EU, "e12", ["fnatic", "HOTU", "B8", "Virtus.pro", "BIG", "GamerLegion"], 18),
    made_it(EU, ["e13", "e14", "e15"], [
        {"label": "STAGE 3", "block": "e13", "teams": ["MOUZ", "Vitality", "Aurora", "Spirit", "BETBOOM", "Falcons"]},
        {"label": "STAGE 2", "block": "e14", "teams": ["FUT", "Nemiga", "G2", "1win", "Natus Vincere", "Astralis"]},
        {"label": "STAGE 1", "block": "e15", "teams": ["Ninjas in Pyjamas", "PARIVISION", "HEROIC", "FaZe", "Eternal Fire", "100 Thieves"]}]),
    # ---------------- Americas ----------------
    race(AM, ["a01"], "2026-10-06", [], banner={"title": "AMERICAS", "sub": "9 SPOTS"}),
    free(AM, ["a02"], "2026-10-06", "2026-10-21"),
    race(AM, ["a03"], "2026-10-21", [dict(to="2026-10-26", move=("that", 1),
         card=list_card(AM, "Imperial", "Circuit X", ["2026-10-22", "2026-10-23", "2026-10-24", "2026-10-25", "2026-10-26"], "2026-10-21", "2026-10-26", title="CURITIBA"))],
         focus=["Imperial"]),
    free(AM, ["a04"], "2026-10-26", "2026-10-31"),
    race(AM, ["a05"], "2026-10-31", [dict(to="2026-11-01", move=("wildcard", 2),
         card=duel(AM, ("Wildcard", "FiRe Last Chance", ["2026-11-01"]), ("NRG", "FiRe Last Chance", ["2026-11-01"]), "2026-10-31", "2026-11-01"))],
         focus=["Wildcard", "NRG"]),
    verdict(AM, "2026-11-02", range(7, 13), ("nrg", 1), 9) | {"blocks": ["a06"]},
    missed(AM, "a07", ["NRG", "BESTIA", "paiN", "Fluxo"], 9),
    made_it(AM, ["a08"], [
        {"label": "STAGE 3", "block": "a08", "teams": ["FURIA", "Legacy"]},
        {"label": "STAGE 2", "block": "a08", "teams": ["MIBR"]},
        {"label": "STAGE 1", "block": "a08", "teams": ["Liquid", "9z", "M80", "DENDELE", "Imperial", "Wildcard"]}]),
    # ---------------- Asia ----------------
    race(AS, ["s01"], "2026-10-06", [], banner={"title": "ASIA", "sub": "5 SPOTS"}),
    {"kind": "story", "ds": AS, "blocks": ["s01b", "s01c"], "team": "BC.Game",
     "roster": [["s1mple", ""], ["Magisk", ""], ["asap", ""], ["Senzu", "ex-MongolZ"], ["mzinho", "ex-MongolZ"]],
     "rank": rank_points(AS, "2026-11-02", "BC.Game")},
    free(AS, ["s02"], "2026-10-06", "2026-10-22"),
    race(AS, ["s03"], "2026-10-22", [dict(to="2026-10-24", move=("remember", 1),
         card=duel(AS, ("Lynn Vision", "MaceMedia", ["2026-10-23", "2026-10-24"]), ("Chinggis Warriors", "MaceMedia", ["2026-10-23", "2026-10-24"]), "2026-10-22", "2026-10-24"))],
         focus=["TYLOO", "Lynn Vision", "Chinggis Warriors"]),
    free(AS, ["s04"], "2026-10-24", "2026-10-30"),
    race(AS, ["s05"], "2026-10-30", [dict(to="2026-10-31", move=("dropped", 1),
         card=list_card(AS, "TYLOO", "HyperX", ["2026-10-31"], "2026-10-30", "2026-10-31", tag="FORFEIT", tag_opp="Metizport"))],
         focus=["TYLOO", "Lynn Vision", "Chinggis Warriors"]),
    verdict(AS, "2026-11-02", range(2, 8), None, 5) | {"blocks": ["s07", "s08"]},
    missed(AS, "s09", ["TYLOO", "5star", "NEXVOID"], 5),
    made_it(AS, ["s10"], [
        {"label": "STAGE 2", "block": "s10", "teams": ["The MongolZ"]},
        {"label": "STAGE 1", "block": "s10", "teams": ["BC.Game", "FlyQuest", "Chinggis Warriors", "Lynn Vision"]}]),
    {"kind": "page", "page": "field", "blocks": ["o01"]},
    {"kind": "page", "page": "next", "blocks": ["o02"]},
]


# ---------------- place blocks on the timeline ----------------
def build():
    t, audio, out = 0.6, [], []
    prev_region = None
    for b in BEATS:
        region = b.get("ds")
        if region and region != prev_region and b["kind"] == "race" and b.get("banner"):
            t += REGION_GAP
        prev_region = region or prev_region
        start = t
        block_at = {}
        for bid in b["blocks"]:
            block_at[bid] = t
            audio.append({"id": bid, "file": f"narration05/{bid}.mp3", "from": round(t * FPS)})
            t += NAR[bid]["duration"] + GAP
        seg = {k: v for k, v in b.items() if k not in ("blocks",)}
        seg["from"] = round(start * FPS)
        seg["dur"] = round((t - start) * FPS)
        # resolve word cues to frames relative to the segment
        rel = lambda bid, sec: round((block_at[bid] - start + sec) * FPS)
        if b["kind"] == "race":
            bid = b["blocks"][0]
            seg["startDay"] = day_index(b["ds"], b["start"])
            steps = []
            for i, st in enumerate(b["steps"]):
                at = rel(bid, word_time(bid, *st["at"])) if st.get("at") else (0 if i == 0 else None)
                steps.append({"at": at, "toDay": day_index(b["ds"], st["to"]), "card": st.get("card"),
                              "move": rel(bid, word_time(bid, *st["move"])) if st.get("move") else None})
            for i, st in enumerate(steps):      # a step without its own start begins where the previous one ends
                if st["at"] is None:
                    st["at"] = steps[i - 1]["move"] + 40
            seg["steps"] = steps
        if b["kind"] == "verdict":
            bid = b["blocks"][0]
            seg["switchAt"] = rel(b["blocks"][-1], 0) if b["switch"] is None else rel(bid, word_time(bid, *b["switch"]))
            seg["dayIndex"] = day_index(b["ds"], b["date"])
        if b["kind"] == "missed":
            bid = b["blocks"][0]
            last = -1.0
            for tm in seg["teams"]:          # names are spoken in order: each cue is searched after the previous one
                last = word_time(bid, tm["name"], after=last)
                tm["at"] = rel(bid, last)
        if b["kind"] == "madeit":
            for st in seg["stages"]:
                bid = st["block"]
                st["at"] = rel(bid, 0)
                st["teamAt"] = []
                last = -1.0
                for name in st["teams"]:
                    key = {"Natus Vincere": "NAVI"}.get(name, name)
                    last = word_time(bid, key, after=last)
                    st["teamAt"].append(rel(bid, last))
        if b["kind"] in ("page", "story"):
            seg["cues"] = {f"{bid}:{w['w']}:{i}": rel(bid, w["s"]) for bid in b["blocks"] for i, w in enumerate(NAR[bid]["words"])}
        out.append(seg)
    total = round((t + 1.5) * FPS)
    (GFX / "narration05").mkdir(exist_ok=True)
    for a in audio:
        shutil.copy(HERE / "narration" / f"{a['id']}.mp3", GFX / a["file"])
    (GFX / "data" / "video05_timeline.json").write_text(json.dumps({"fps": FPS, "total": total, "audio": audio, "segments": out}, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{len(out)} segments, {len(audio)} audio blocks, {total / FPS:.1f} s ({total / FPS / 60:.2f} min)")


if __name__ == "__main__":
    build()
