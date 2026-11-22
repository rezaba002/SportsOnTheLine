"""Round-clock stats in seconds per Major player (full-buy rounds) -> data/clock.json
alive_med   : median time alive (Kaplan-Meier, a survived round counts as alive until the round ended)
death_med   : median second of his death, in rounds where he died
kill_med    : median second of his kills
first_kill_med : median second of his first kill in a round
open_kill_med  : median second of his opening kills (first kill of the round)
open_death_med : median second of his opening deaths
"""
import csv, json, os, statistics as st
from collections import defaultdict
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import km_median
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = json.load(open(os.path.join(ROOT, "data", "players.json"), encoding="utf-8"))
sid2 = {str(s): p for p in P for s in p["steam_ids"]}
rows = defaultdict(list)
for r in csv.DictReader(open(os.path.join(ROOT, "data", "player_rounds.csv"), encoding="utf-8")):
    if r["eco"] == "2" and r["steam_id"] in sid2:
        rows[sid2[r["steam_id"]]["player"]].append(r)
def med(v):
    return round(st.median(v), 1) if v else None
out = {}
for p in P:
    rs = rows.get(p["player"], [])
    if len(rs) < 300:
        continue
    def block(rs):
        died = [r for r in rs if r["died"] == "True"]
        return {
            "rounds": len(rs),
            "alive_med": round(km_median([float(r["death_t"]) if r["died"] == "True" else float(r["end_t"]) for r in rs],
                                         [r["died"] == "True" for r in rs]) or 0, 1) or None,
            "death_med": med([float(r["death_t"]) for r in died]),
            "kill_med": med([float(x) for r in rs for x in r["kill_ts"].split(";") if x]),
            "first_kill_med": med([float(r["first_kill_t"]) for r in rs if r["first_kill_t"]]),
            "open_kill_med": med([float(r["first_kill_t"]) for r in rs if r["opening_kill"] == "True"]),
            "open_death_med": med([float(r["death_t"]) for r in rs if r["opening_death"] == "True"]),
            "survive_pct": round(100 * (len(rs) - len(died)) / len(rs), 1),
        }
    out[p["player"]] = {"team": p["team"], "role": p["role"], **block(rs),
                        "T": block([r for r in rs if r["side"] == "T"]), "CT": block([r for r in rs if r["side"] == "CT"])}
json.dump(out, open(os.path.join(ROOT, "data", "clock.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

def show(title, key, rev, pool, k=5, side=None):
    q = [(n, (v[side] if side else v)[key]) for n, v in pool.items() if (v[side] if side else v)[key] is not None]
    q.sort(key=lambda x: x[1], reverse=rev)
    print(f"  {title:<34}", ", ".join(f"{n} {t:.0f}s" for n, t in q[:k]))
allp = out
print(f"{len(out)} players. All-player medians: alive {st.median(v['alive_med'] for v in out.values() if v['alive_med']):.0f}s, "
      f"death {st.median(v['death_med'] for v in out.values()):.0f}s, kill {st.median(v['kill_med'] for v in out.values()):.0f}s")
print("ALL PLAYERS")
show("longest alive (survivalist)", "alive_med", True, allp)
show("shortest alive (dies fast)", "alive_med", False, allp)
show("earliest death when he dies", "death_med", False, allp)
show("fastest kills", "kill_med", False, allp)
show("latest kills", "kill_med", True, allp)
for role in ("entry", "AWPer", "rifler"):
    pool = {n: v for n, v in out.items() if v["role"] == role}
    print(f"{role.upper()} ({len(pool)}) medians: alive {st.median(v['alive_med'] for v in pool.values()):.0f}s, "
          f"death {st.median(v['death_med'] for v in pool.values()):.0f}s, kill {st.median(v['kill_med'] for v in pool.values()):.0f}s, "
          f"opening kill {st.median(v['open_kill_med'] for v in pool.values() if v['open_kill_med']):.0f}s")
    show("longest alive", "alive_med", True, pool)
    show("shortest alive", "alive_med", False, pool)
    show("fastest kills", "kill_med", False, pool)
    show("latest kills", "kill_med", True, pool)
    show("fastest opening kill (T side)", "open_kill_med", False, pool, side="T")
for n in ("donk", "ZywOo", "m0NESY", "YEKINDAR", "flameZ", "zweih", "ArtFr0st", "KaiR0N-", "robo", "Kvem"):
    v = out[n]; print(f"  {n:>9}: alive {v['alive_med']}s, death {v['death_med']}s, kill {v['kill_med']}s, first kill {v['first_kill_med']}s, "
                      f"opening kill {v['open_kill_med']}s (T {v['T']['open_kill_med']}s), opening death {v['open_death_med']}s, T alive {v['T']['alive_med']}s, CT alive {v['CT']['alive_med']}s")
