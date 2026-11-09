"""Per-team roster moves since the Cologne Major, from the HLTV transfers list (top-30 teams, Jun 22 -> Nov 1).

Each line of the TSV becomes a move for every team it touches: "+" = joins the active five, "-" = leaves it
(transfer out, benched, parted ways, loaned out). Coach moves are kept but marked. Team names are mapped to the VRS names
used in the race. Output: sotl-graphics/public/data/transfers.json  {team: [{date, player, dir, kind, note}]}
"""
import json, pathlib, re

SRC = pathlib.Path(__file__).resolve().parents[1] / "research" / "transfers_top30_2026-06-22_to_2026-11-01.tsv"
OUT = pathlib.Path(r"D:\Youtube\sotl-graphics\public\data\transfers.json")
VRS_NAME = {"Natus Vincere": "Natus Vincere", "Ninjas in Pyjamas": "Ninjas in Pyjamas", "Inner Circle": "Inner Circle"}

moves = {}


def add(team, date, player, d, kind, note):
    if not team or team.startswith("ex-") or team == "No team":
        return
    moves.setdefault(VRS_NAME.get(team, team), []).append({"date": date, "player": player, "dir": d, "kind": kind, "note": note})


PATTERNS = [
    (r"^(\S+) transfers from (.+) to (.+?)( as coach)?$", lambda m: [(m[2], "-"), (m[3], "+")]),
    (r"^(\S+) joins (.+) on loan from (.+?)( as coach)?$", lambda m: [(m[3], "-"), (m[2], "+")]),
    (r"^(\S+) joins (.+?)( as coach)?$", lambda m: [(m[2], "+")]),
    (r"^(\S+) parts ways with (.+?)( as coach)?$", lambda m: [(m[2], "-")]),
    (r"^(\S+) is benched on (.+)$", lambda m: [(m[2], "-")]),
    (r"^(\S+) is moved to the active roster on (.+)$", lambda m: [(m[2], "+")]),
    (r"^(\S+) returns to (.+) \(benched\) from loan at (.+)$", lambda m: [(m[3], "-")]),
]

for line in SRC.read_text(encoding="utf-8").splitlines()[1:]:
    date, text, status = (line.split("\t") + ["", ""])[:3]
    coach = "COACH" in status or text.endswith("as coach")
    for pat, fn in PATTERNS:
        m = re.match(pat, text)
        if m:
            for team, d in fn(m):
                note = "benched" if "benched" in text and d == "-" else "loan" if "loan" in text else ""
                add(team, date, m[1], d, "coach" if coach else "player", note)
            break
    else:
        print("unparsed:", text)

for team, t in moves.items():
    t.sort(key=lambda x: x["date"])
    # a player benched first and transferred out later left the active five once: keep the first "-" only,
    # unless they came back to the active roster in between
    out, active = [], {}
    for x in t:
        if x["dir"] == "-" and active.get(x["player"]) is False:
            continue
        active[x["player"]] = x["dir"] == "+"
        out.append(x)
    moves[team] = out
OUT.write_text(json.dumps(moves, indent=1), encoding="utf-8")
print(len(moves), "teams")
for team in ("Luminosity", "Astralis", "The MongolZ", "GamerLegion", "paiN"):
    print(team, [(x["date"][5:], x["dir"] + x["player"], x["kind"][0], x["note"]) for x in moves.get(team, [])])
