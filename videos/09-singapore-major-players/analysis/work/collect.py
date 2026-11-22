"""Collect round-clock data for the 32 Singapore Major teams, season 2026 (Jan 1 -> now).

Scope: bo3.gg S/A-tier matches with a Major team, parsed. Per round we keep
  kills  (seconds after freeze end, killer, side, victim, side, weapon id)   <- 2D-replay file head
  roster (in-game name, steam id, side, money at freeze start)               <- first replay state
  stats  (per player: side, win, K/D, opening kill/death, trades, economy)   <- players_stats API
Output: data/rounds/<game>/<round>.json, data/games.json. Safe to stop and restart.
Usage: python collect.py [--tiers s,a] [--workers 5] [--limit N]
"""
import argparse, json, os, sys, time, traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from bo3 import api
from bo3_round_kills import round_kills

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "data", "rounds")
STAT_KEYS = ("team_side", "win", "kills", "death", "assists", "headshots", "first_kills", "first_death",
             "trade_kills", "trade_death", "clutches", "economy_level", "enemy_economy_level",
             "total_equipment_value", "damage", "clan_name", "enemy_clan_name")


def games_for(match):
    d = api(f"games?filter%5Bgames.match_id%5D%5Beq%5D={match['id']}")
    return [g for g in d.get("results", []) if g.get("state") == "done" and g.get("rounds_count")]


def do_round(game, rnd):
    path = os.path.join(OUT, str(game), f"{rnd}.json")
    if os.path.exists(path):
        return "skip"
    k = round_kills(game, rnd)
    st = api(f"games/{game}/rounds/{rnd}/players_stats", cache=False)
    k["stats"] = [{"steam_id": (p.get("steam_profile") or {}).get("steam_id_64"),
                   "nick": (p.get("steam_profile") or {}).get("nickname"),
                   "player": ((p.get("steam_profile") or {}).get("player") or {}).get("slug"),
                   **{x: p.get(x) for x in STAT_KEYS}} for p in st]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(k, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, path)
    return k["how"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tiers", default="s,a")
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--limit", type=int, default=0, help="max matches (testing)")
    a = ap.parse_args()
    tiers = set(a.tiers.split(","))
    teams = set(json.load(open(os.path.join(ROOT, "research", "major_teams_bo3.json"))).values())
    matches = json.load(open(os.path.join(ROOT, "research", "matches_2026.json"), encoding="utf-8"))
    sel = [m for m in matches if m["tier"] in tiers and m["parsed_status"] in ("done", "partially_done")
           and (m["team1_id"] in teams or m["team2_id"] in teams)]
    sel.sort(key=lambda m: m["start_date"], reverse=True)
    if a.limit:
        sel = sel[:a.limit]
    print(f"{len(sel)} matches, tiers {sorted(tiers)}", flush=True)

    gpath = os.path.join(ROOT, "data", "games.json")
    games = json.load(open(gpath, encoding="utf-8")) if os.path.exists(gpath) else {}
    for i, m in enumerate(sel):
        if any(g["match_id"] == m["id"] for g in games.values()):
            continue
        for g in games_for(m):
            games[str(g["id"])] = {"id": g["id"], "match_id": m["id"], "match": m["slug"], "date": m["start_date"],
                                   "tier": m["tier"], "tournament": m["tournament"], "map": g["map_name"],
                                   "number": g.get("number"), "rounds": g["rounds_count"],
                                   "winner": g.get("winner_clan_name"), "loser": g.get("loser_clan_name"),
                                   "score": [g.get("winner_clan_score"), g.get("loser_clan_score")]}
        if i % 50 == 0:
            json.dump(games, open(gpath, "w", encoding="utf-8"), ensure_ascii=False)
            print(f"  game lists {i}/{len(sel)}", flush=True)
    json.dump(games, open(gpath, "w", encoding="utf-8"), ensure_ascii=False)
    sel_ids = {m["id"] for m in sel}
    todo = [(g["id"], r) for g in sorted(games.values(), key=lambda g: g["date"], reverse=True)
            if g["match_id"] in sel_ids for r in range(1, g["rounds"] + 1)]
    print(f"{len(games)} maps, {len(todo)} rounds", flush=True)

    t0, done, fails = time.time(), 0, 0
    errlog = open(os.path.join(ROOT, "data", "errors.log"), "a", encoding="utf-8")
    with ThreadPoolExecutor(a.workers) as ex:
        futs = {ex.submit(do_round, g, r): (g, r) for g, r in todo}
        for f in as_completed(futs):
            g, r = futs[f]
            try:
                f.result()
            except Exception as e:
                fails += 1
                errlog.write(f"{g} {r} {e!r}\n"); errlog.flush()
            done += 1
            if done % 250 == 0:
                rate = done / (time.time() - t0)
                print(f"{done}/{len(todo)} rounds, {fails} failed, {rate:.1f}/s, "
                      f"eta {(len(todo) - done) / rate / 3600:.1f} h", flush=True)
    print(f"finished: {done} rounds, {fails} failed", flush=True)


if __name__ == "__main__":
    main()
