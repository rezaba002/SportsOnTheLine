"""List every 1-vs-N situation (N >= 2) in a demo, from the kill order of each round.

Usage: python find_clutches.py demo1.dem [demo2.dem ...]
A player is "in a clutch" when he is his team's last one alive against N >= 2 opponents.
Won = his team won the round (by kills, bomb or defuse). Spirit/G2 rosters are read from the demo.
"""
import sys
from awpy import Demo


def team_of(demo):
    return {r["name"]: r["team_clan_name"] for r in demo.players.to_dicts() if r["team_clan_name"]}


def scan(path):
    d = Demo(path)
    teams = team_of(d)
    kills = d.kills
    rounds = {r["round_num"]: r for r in d.rounds.to_dicts()}
    print("kills columns:", kills.columns) if "--cols" in sys.argv else None
    out = []
    for rn, r in rounds.items():
        rk = kills.filter((kills["tick"] >= r["freeze_end_tick"]) & (kills["tick"] <= r["end_tick"])).sort("tick").to_dicts()
        alive = {t: {n for n, tt in teams.items() if tt == t} for t in set(teams.values())}
        side_of_team = {}
        seen = set()
        for k in rk:
            v = k.get("victim_name")
            vt = teams.get(v)
            if vt and k.get("victim_side"):
                side_of_team.setdefault(vt, k["victim_side"])
            if vt and v in alive[vt]:
                alive[vt].discard(v)
            for t, members in alive.items():
                other = [o for o in alive if o != t][0]
                if len(members) == 1 and len(alive[other]) >= 2 and (rn, t) not in seen:
                    seen.add((rn, t))
                    out.append({"round": rn, "player": next(iter(members)), "team": t, "vs": len(alive[other]),
                                "tick": k["tick"], "opponents": sorted(alive[other])})
        for c in out:
            if c["round"] == rn:
                ts = side_of_team.get(c["team"])
                c["won"] = (ts == r["winner_side"]) if ts else None
                c["how"] = r["reason_name"]
                c["round_end_tick"] = r["end_tick"]
    return d, out


if __name__ == "__main__":
    for path in [a for a in sys.argv[1:] if a.endswith(".dem")]:
        d, cl = scan(path)
        print("=====", path)
        for c in cl:
            ot = "OT" if c["round"] > 24 else "  "
            print(f"  R{c['round']:>2} {ot} {c['player']:>9} ({c['team'][:6]}) 1v{c['vs']}  "
                  f"{'WON ' if c['won'] else 'lost' if c['won'] is False else '?   '} by {c['how']:<16} "
                  f"vs {', '.join(c['opponents'])}")
