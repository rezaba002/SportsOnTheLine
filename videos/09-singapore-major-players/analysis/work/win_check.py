"""Does dying early cost rounds? Team round-win % by how/when a player died (full-buy rounds).
Reads data/player_rounds.csv + data/players.json -> data/win_check.json"""
import csv, json, os, collections
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
roles = {}
P = json.load(open(os.path.join(ROOT, "data", "players.json"), encoding="utf-8"))
for p in P:
    for sid in p["steam_ids"]:
        roles[str(sid)] = (p["player"], p["role"])
rows = [r for r in csv.DictReader(open(os.path.join(ROOT, "data", "player_rounds.csv"), encoding="utf-8"))
        if r["eco"] == "2"]
def wr(rs):
    return round(100 * sum(r["win"] == "1" for r in rs) / len(rs), 1) if rs else None, len(rs)
def cat(r):
    if r["opening_death"] == "True":
        return "opening death, traded" if r["traded"] == "True" else "opening death, NOT traded"
    if r["opening_kill"] == "True":
        return "opening kill"
    return "not in opening duel"
def when(r):
    if r["died"] != "True":
        return "survived the round"
    t = float(r["death_t"])
    return "died 0-30 s" if t < 30 else "died 30-60 s" if t < 60 else "died 60 s+"

out = {"overall": {}, "by_role": {}, "by_time": {}, "players": {}}
print("ALL full-buy player-rounds", wr(rows))
groups = collections.defaultdict(list)
for r in rows: groups[cat(r)].append(r)
for k in ("opening kill", "not in opening duel", "opening death, traded", "opening death, NOT traded"):
    out["overall"][k] = wr(groups[k]); print(f"  {k:<28} team wins {out['overall'][k][0]}%  (n={out['overall'][k][1]})")
tg = collections.defaultdict(list)
for r in rows: tg[when(r)].append(r)
print("By time of death")
for k in ("died 0-30 s", "died 30-60 s", "died 60 s+", "survived the round"):
    out["by_time"][k] = wr(tg[k]); print(f"  {k:<28} team wins {out['by_time'][k][0]}%  (n={out['by_time'][k][1]})")
for role in ("AWPer", "entry", "rifler"):
    rr = [r for r in rows if roles.get(r["steam_id"], ("", ""))[1] == role]
    g = collections.defaultdict(list)
    for r in rr: g[cat(r)].append(r)
    out["by_role"][role] = {k: wr(v) for k, v in g.items()}
    print(f"{role}: " + ", ".join(f"{k} {v[0]}%" for k, v in sorted(out['by_role'][role].items())))

# per player: how many full-buy rounds his untraded opening deaths cost per 100 rounds
base_after = out["overall"]["not in opening duel"][0]
for p in P:
    if p["rounds"] < 300: continue
    sids = {str(s) for s in p["steam_ids"]}
    rs = [r for r in rows if r["steam_id"] in sids]
    ud = [r for r in rs if cat(r) == "opening death, NOT traded"]
    ok = [r for r in rs if cat(r) == "opening kill"]
    a60 = [r for r in rs if float(r["end_t"]) >= 60 or r["died"] != "True"]
    alive = [r for r in a60 if r["died"] != "True" or float(r["death_t"]) > 60]
    dead = [r for r in a60 if r["died"] == "True" and float(r["death_t"]) <= 60]
    out["players"][p["player"]] = {
        "team": p["team"], "role": p["role"], "rounds": len(rs), "win_pct": wr(rs)[0],
        "untraded_od_pct": round(100 * len(ud) / len(rs), 1), "win_after_untraded_od": wr(ud)[0],
        "opening_kill_pct": round(100 * len(ok) / len(rs), 1), "win_after_opening_kill": wr(ok)[0],
        "win_if_alive_60": wr(alive)[0], "win_if_dead_by_60": wr(dead)[0],
        # net opening rounds per 100: rounds won above baseline after his opening kills
        # minus rounds lost below baseline after his untraded opening deaths
        "opening_net_per100": round((len(ok) * (wr(ok)[0] - base_after) - len(ud) * (base_after - (wr(ud)[0] or 0))) / len(rs), 2) if ud and ok else None,
    }
json.dump(out, open(os.path.join(ROOT, "data", "win_check.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
