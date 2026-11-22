"""Versioned objective context, kept separate from original round-clock inputs.

Map summaries establish whether a plant occurred. Ranged replay samples locate
its clock time; missing/rejected data remains unknown, never a no-plant round.
"""
import argparse
import json
import pathlib
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from bo3 import api, get_range
from bo3_round_kills import SAMPLE, PHASE, REMAIN

ROOT = pathlib.Path(__file__).resolve().parents[1]


def terminal_probability(t_alive, ct_alive, planted):
    if ct_alive <= 0:
        return 1.0
    if t_alive <= 0 and not planted:
        return 0.0
    return None


def plant_from_samples(samples, live_tick, rate):
    values = [(tick - (40 - remaining) * rate - live_tick) / rate
              for tick, phase, remaining in samples if phase == 2 and remaining is not None]
    return sum(values) / len(values) if values else None


def extract_context(replay, live_tick, rate):
    bomb, players, last_actor = {}, {}, None
    out = {"plant_s": None, "planter": None, "defuse_s": None, "explode_s": None}
    for state in replay["states"]:
        prev = dict(bomb)
        bomb.update(state.get("bomb", {}))
        for index, p in enumerate(state.get("players", [])):
            if p is not None:
                players.setdefault(index, {}).update(p)
        actors = [p.get("name") for p in players.values() if p.get("is_planting")]
        sec = (state["ingame_tick"] - live_tick) / rate
        if bomb.get("is_planted") and not prev.get("is_planted"):
            out.update(plant_s=sec, planter=(actors or [last_actor])[0])
        for field, target in [("is_defused", "defuse_s"), ("is_explode", "explode_s")]:
            if bomb.get(field) and not prev.get(field):
                out[target] = sec
        last_actor = actors[0] if actors else None
    return out


def samples_in(body):
    result = []
    for match in SAMPLE.finditer(body):
        phase, remain = PHASE.search(match[2]), REMAIN.search(match[2])
        if phase:
            result.append((int(match[1]), int(phase[1]), int(remain[1]) / 1e9 if remain else None))
    return result


def locate_plant(rd):
    url = f"https://files.bo3.gg/round_maps/{rd['g']}/{rd['r']}.json"
    # All live states have roughly the same payload density. Start near the
    # final fight, then bracket phase 2 using actual sampled ticks/phases.
    size = rd["size"]
    lo, hi = 0, max(0, size - 60000)
    offset = int(hi * .82)
    fetched = 0
    for _ in range(14):
        body, actual_size = get_range(url, offset, min(size - 1, offset + 59999))
        if actual_size != size:
            raise ValueError("replay size changed since original collection")
        fetched += len(body)
        pts = samples_in(body)
        found = plant_from_samples(pts, rd["live_tick"], rd["rate"])
        if found is not None:
            if not -0.2 <= found <= 116:
                raise ValueError(f"implausible plant time {found}")
            return {"plant_s": round(found, 3), "method": "phase2_timer", "bytes": fetched}
        if not pts or max(p[1] for p in pts) <= 1:
            lo = offset + 30000
        else:
            hi = offset
        if hi - lo < 20000:
            break
        offset = (lo + hi) // 2
    # Very short post-plants can sit between probes. Full reconstruction is
    # a correctness fallback, not a guess from the last kill or end reason.
    body, actual_size = get_range(url, 0, size - 1)
    full = extract_context(json.loads(body), rd["live_tick"], rd["rate"])
    if full["plant_s"] is None:
        raise ValueError("API reports plant but replay has no completed plant")
    return {**full, "method": "full_replay", "bytes": fetched + len(body)}


def collect_map(gid):
    out = ROOT / "data/bomb_context" / f"{gid}.json"
    if out.exists():
        cached = json.loads(out.read_text())
        if not cached.get("errors"):
            return "cached"
    summary = api(f"games/{gid}/rounds")
    records, errors = {}, []
    for r in summary.get("game_rounds", []):
        path = ROOT / "data/rounds" / str(gid) / f"{r['round_number']}.json"
        if not path.exists():
            continue
        try:
            teams = r["game_round_team_clans"]
            if len(teams) != 2 or any(x.get("bomb_plants") is None for x in teams):
                raise ValueError("objective summary missing")
            plants = sum(x["bomb_plants"] for x in teams)
            if plants not in (0, 1):
                raise ValueError("invalid completed plant count")
            record = {"planted": bool(plants), "plant_s": None, "end_reason": r["end_reason"],
                      "winner": r["winner_clan_side"], "teams": [{k: t.get(k) for k in
                      ("team_side", "clan_name", "bomb_plants", "bomb_defuses", "bomb_plant_attempts",
                       "bomb_defuse_attempts", "equipment_value")} for t in teams]}
            if plants:
                record.update(locate_plant(json.loads(path.read_text(encoding="utf-8"))))
            records[str(r["round_number"])] = record
        except Exception as exc:
            errors.append({"round": r["round_number"], "error": str(exc)})
    out.parent.mkdir(exist_ok=True)
    tmp = out.with_suffix(".tmp")
    tmp.write_text(json.dumps({"game": gid, "rounds": records, "errors": errors}, separators=(",", ":")))
    tmp.replace(out)
    return f"{len(records)} rounds, {len(errors)} errors"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    games = json.loads((ROOT / "data/games.json").read_text(encoding="utf-8"))
    ordered = sorted(games, key=lambda g: games[g]["date"], reverse=True)
    if args.limit:
        ordered = ordered[:args.limit]
    start = time.time()
    with ThreadPoolExecutor(args.workers) as ex:
        futures = {ex.submit(collect_map, int(g)): g for g in ordered}
        for i, f in enumerate(as_completed(futures), 1):
            try:
                result = f.result()
            except Exception as exc:
                result = f"ERROR {exc}"
            print(f"{i}/{len(ordered)} map {futures[f]}: {result} elapsed={time.time()-start:.0f}s", flush=True)


if __name__ == "__main__":
    main()
