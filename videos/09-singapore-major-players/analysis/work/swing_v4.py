"""Match-cross-fitted, bomb-aware kill/death swing. Objective counts are separate.

This measures model-estimated probability changes, not causal player value.
Model uncertainty is NOT included in the match-cluster bootstrap intervals.
Run again after collection completes; partial outputs are explicitly labelled.
"""
import argparse
import collections
import hashlib
import json
import itertools
import math
import pathlib
import re
import sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, str(pathlib.Path(__file__).parent / "vendor"))
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import brier_score_loss, log_loss
from sklearn.model_selection import GroupKFold
from threadpoolctl import threadpool_limits
from bomb_context import terminal_probability

ROOT = pathlib.Path(__file__).resolve().parents[1]


def current_team(actual, expected):
    def norm(s):
        return re.sub(r"[^a-z0-9]", "", s.lower().replace("team ", "").replace("esports", ""))
    return norm(actual) == norm(expected)


def features(t_alive, ct_alive, seconds, plant_s, eco_t, eco_ct, map_id):
    planted = plant_s is not None and seconds >= plant_s
    return [t_alive, ct_alive, int(planted), 0 if planted else max(0, 115-seconds)/115,
            max(0, 40-seconds+plant_s)/40 if planted else 0, eco_t, eco_ct, map_id]


def round_events(rd, context, map_id=0):
    # Replay rosters occasionally include spectators/substituted slots. Only
    # the ten actual API participants determine active IDs and initial counts.
    stats = {s["steam_id"]: s for s in rd["stats"] if s.get("steam_id") is not None}
    side = {sid: s["team_side"] for sid, s in stats.items()}
    names = {r[0]: r[1] for r in rd["roster"] if r[1] in side}
    alive = set(side)
    t_alive, ct_alive = sum(s == "T" for s in side.values()), sum(s == "CT" for s in side.values())
    def economy(s):
        vals = [x["economy_level"] for x in stats.values() if x["team_side"] == s and x.get("economy_level") is not None]
        return max(-1, min(2, collections.Counter(vals).most_common(1)[0][0])) if vals else -1
    et, ec = economy("T"), economy("CT")
    plant = context["plant_s"] if context["planted"] else None
    # Replays retain approximately 41 trailing frames. This clock comes from
    # replay metadata, not a player's eventual death or the round's winner.
    end_s = context.get("end_s", ((rd["tick0"] + rd["step"] * (rd["frames"] - 41) - rd["live_tick"]) / rd["rate"]
             if all(k in rd for k in ("tick0", "step", "frames", "live_tick", "rate")) else float("inf")))
    out = []
    for seconds, group in itertools.groupby(sorted(rd["kills"], key=lambda k: k[0]), key=lambda k: k[0]):
        if seconds < 0 or seconds > end_s + .01:
            continue
        if context.get("end_reason") in ("BombDefused", "TargetSaved", "TargetBombed"):
            # Objective events and kill clocks are quantized to sampled replay
            # frames. Conservatively exclude the unresolved final frame.
            if seconds >= end_s - rd.get("step", 8)/rd.get("rate", 64):
                continue
        # No-plant rounds end on the 115-second clock; post-timeout cleanup
        # kills do not create credit in the completed round.
        if plant is None and seconds > 115.2:
            continue
        if plant is not None and seconds > plant + 40.2:
            continue
        deaths = {}
        for _, kn, kt, vn, vt, weapon in group:
            victim, killer = names.get(vn), names.get(kn)
            if victim in alive:
                deaths[victim] = killer if killer in side and side[killer] != side[victim] else None
        if not deaths:
            continue
        before = features(t_alive, ct_alive, seconds, plant, et, ec, map_id)
        victims = sorted(deaths)
        after_t = t_alive - sum(side[v] == "T" for v in victims)
        after_ct = ct_alive - sum(side[v] == "CT" for v in victims)
        after = features(after_t, after_ct, seconds, plant, et, ec, map_id)
        terminal = terminal_probability(after_t, after_ct, bool(after[2]))
        if terminal is not None and (after_t or after_ct) and context.get("winner") and bool(terminal) != (context["winner"] == "T"):
            raise ValueError("terminal kill group contradicts objective winner")
        for victim in victims:
            # Shapley marginal attribution removes arbitrary ordering of kills
            # in one replay frame. Only joint observed states train the model;
            # counterfactual subset states are used solely for attribution.
            others = [v for v in victims if v != victim]
            alternatives = []
            for count in range(len(others)+1):
                weight = 1 / (len(victims)*math.comb(len(others), count))
                for subset in itertools.combinations(others, count):
                    at = t_alive - sum(side[v] == "T" for v in subset)
                    ac = ct_alive - sum(side[v] == "CT" for v in subset)
                    a = features(at, ac, seconds, plant, et, ec, map_id)
                    b = features(at-(side[victim] == "T"), ac-(side[victim] == "CT"), seconds, plant, et, ec, map_id)
                    alternatives.append((a, b, weight))
            out.append({"before": before, "after": after, "alternatives": alternatives, "killer": deaths[victim],
                        "victim": victim, "victim_side": side[victim], "seconds": seconds,
                        "phase": "postplant" if before[2] else "preplant", "winner": context.get("winner")})
        alive.difference_update(victims)
        t_alive, ct_alive = after_t, after_ct
        if terminal_probability(t_alive, ct_alive, bool(after[2])) is not None:
            break
    return out


def bootstrap_interval(clusters, seed=123):
    if len(clusters) < 2:
        return None, None
    rng = np.random.default_rng(seed)
    v = np.asarray(clusters, dtype=float)
    ix = rng.integers(0, len(v), size=(1000, len(v)))
    samples = v[ix].sum(axis=1)
    lo, hi = np.quantile(samples[:, 0] / samples[:, 1], [.025, .975])
    return round(float(lo), 3), round(float(hi), 3)


def model():
    return HistGradientBoostingClassifier(max_iter=100, max_leaf_nodes=15, min_samples_leaf=80,
        learning_rate=.08, l2_regularization=5, monotonic_cst=[1, -1, 0, 0, -1, 0, 0, 0],
        categorical_features=[7], random_state=109)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    games = json.loads((ROOT / "data/games.json").read_text())
    games = {g: v for g, v in games.items() if (ROOT / "data/rounds" / g).is_dir()}
    players = json.loads((ROOT / "data/players.json").read_text(encoding="utf-8"))
    old = json.loads((ROOT / "data/swing.json").read_text(encoding="utf-8"))
    maps = sorted({g["map"] for g in games.values()})
    sid2name = {sid: p["player"] for p in players for sid in p["steam_ids"]}
    meta = {p["player"]: p for p in players}
    rounds, X, y, groups, weights, elapsed = [], [], [], [], [], []
    available, skipped, missing, summary_errors, usable_maps = 0, 0, 0, 0, 0
    reader = ThreadPoolExecutor(8)
    for gid, game in games.items():
        path = ROOT / "data/bomb_context" / f"{gid}.json"
        if not path.exists():
            missing += 1
            continue
        cached = json.loads(path.read_text())
        source_key = hashlib.md5(f"games/{gid}/rounds".encode()).hexdigest()
        source = json.loads((ROOT / "research/bo3_cache" / f"{source_key}.json").read_text())
        durations = {str(r["round_number"]): r.get("round_duration") for r in source.get("game_rounds", [])}
        available += 1
        usable_maps += bool(cached["rounds"])
        summary_errors += len(cached["errors"])
        items = list(cached["rounds"].items())
        loaded = reader.map(lambda item: json.loads((ROOT / "data/rounds" / gid / f"{item[0]}.json").read_text(encoding="utf-8")), items)
        for (rn, context), rd in zip(items, loaded):
            stats = {s["steam_id"]: s for s in rd["stats"] if s.get("steam_id") is not None}
            if len(stats) != 10 or sum(s["team_side"] == "T" for s in stats.values()) != 5:
                skipped += 1
                continue
            wins = {s["team_side"] for s in stats.values() if s["win"] == 1}
            if len(wins) != 1 or context["winner"] not in wins:
                skipped += 1
                continue
            if durations.get(rn) is None:
                skipped += 1
                continue
            context = {**context, "end_s": durations[rn]/1e9 - (rd["live_tick"]-rd["tick0"])/rd["rate"]}
            try:
                events = round_events(rd, context, maps.index(game["map"]))
            except ValueError:
                skipped += 1
                continue
            if not events:
                skipped += 1
                continue
            # Deduplicate states within a round; equal round weight prevents
            # long rounds with many observed states dominating the fit.
            unique = {tuple(e[k]): e["seconds"] for e in events for k in ("before", "after")}
            for state, seconds in unique.items():
                X.append(state); y.append("T" in wins); groups.append(game["match_id"]); weights.append(1/len(unique))
                elapsed.append(seconds)
            rounds.append({"gid": gid, "match": game["match_id"], "date": game["date"], "stats": stats,
                           "winner": context["winner"], "context": context, "events": events})
    reader.shutdown()
    complete = missing == 0
    if args.require_complete and not complete:
        raise SystemExit(f"Collection incomplete: {missing} maps missing; {summary_errors} rounds separately excluded")
    if len(set(groups)) < 5:
        raise SystemExit("At least five independent matches required")
    print(f"Fitting {len(rounds)} rounds from {available} maps (complete={complete})", flush=True)
    X, y, groups, weights = np.asarray(X), np.asarray(y, dtype=int), np.asarray(groups), np.asarray(weights)
    predictions = np.zeros(len(y))
    baseline_predictions = np.zeros(len(y))
    fold_models = []
    for fold, (train, test) in enumerate(GroupKFold(5).split(X, y, groups)):
        with threadpool_limits(limits=2):
            fitted = model().fit(X[train], y[train], sample_weight=weights[train])
            predictions[test] = fitted.predict_proba(X[test])[:, 1]
            # Same rows/folds/capacity. Retain elapsed round clock while hiding
            # bomb status; this isolates the additional objective context.
            base = X.copy()
            # Original elapsed time is saved separately below; post-plant
            # elapsed cannot be recovered from bomb time alone.
            base[:, 2] = 0
            base[:, 3] = np.asarray(elapsed) / 115
            base[:, 4] = 0
            bm = model().fit(base[train], y[train], sample_weight=weights[train])
            baseline_predictions[test] = bm.predict_proba(base[test])[:, 1]
        fold_models.append((set(groups[test]), fitted))
        print(f"fold {fold+1}/5 complete", flush=True)
    # Validate the same terminal-aware probability function that supplies the
    # player credits. Both models share deterministic terminal rules.
    for i, state in enumerate(X):
        terminal = terminal_probability(state[0], state[1], bool(state[2]))
        if state[0] == 0 and state[1] == 0:
            terminal = float(y[i])
        if terminal is not None:
            predictions[i] = terminal
            baseline_predictions[i] = terminal
    sid_maps = collections.defaultdict(set)
    totals = collections.defaultdict(lambda: collections.defaultdict(float))
    current_maps = collections.defaultdict(set)
    clusters = collections.defaultdict(lambda: collections.defaultdict(lambda: [0., set()]))
    team_objectives = collections.defaultdict(lambda: collections.Counter())
    for heldout, fitted in fold_models:
        rr = [r for r in rounds if r["match"] in heldout]
        states = [a[k] for r in rr for e in r["events"] for a in e["alternatives"] for k in (0, 1)]
        with threadpool_limits(limits=2):
            pp = fitted.predict_proba(np.asarray(states))[:, 1]
        index = 0
        for rd in rr:
            for sid, stat in rd["stats"].items():
                name = sid2name.get(sid)
                if name:
                    sid_maps[name].add(rd["gid"])
                    clusters[name][rd["match"]][1].add(rd["gid"])
                    if current_team(stat["clan_name"], meta[name]["team"]):
                        current_maps[name].add(rd["gid"])
            for t in rd["context"]["teams"]:
                counter = team_objectives[t["clan_name"]]
                counter["rounds"] += 1
                counter["t_rounds" if t["team_side"] == "T" else "ct_rounds"] += 1
                counter["plants"] += t["bomb_plants"] or 0
                counter["defuses"] += t["bomb_defuses"] or 0
                if rd["context"]["planted"]:
                    key = "postplant_attack" if t["team_side"] == "T" else "retake"
                    counter[key+"_rounds"] += 1
                    counter[key+"_wins"] += rd["winner"] == t["team_side"]
            for event in rd["events"]:
                delta = 0
                for a, b, weight in event["alternatives"]:
                    ps = list(pp[index:index+2]); index += 2
                    for j, state in enumerate((a, b)):
                        terminal = terminal_probability(state[0], state[1], bool(state[2]))
                        if state[0] == 0 and state[1] == 0:
                            terminal = float(event["winner"] == "T")
                        if terminal is not None:
                            ps[j] = terminal
                    delta += weight*(ps[1]-ps[0])
                victim_delta = delta if event["victim_side"] == "T" else -delta
                for sid, gain in [(event["victim"], victim_delta), (event["killer"], -victim_delta)]:
                    name = sid2name.get(sid)
                    if name is None:
                        continue
                    v = totals[name]
                    v["total"] += gain
                    clock = "0-30" if event["seconds"] < 30 else "30-60" if event["seconds"] < 60 else "60+"
                    v[clock] += gain
                    phase = "preplant" if event["phase"] == "preplant" else ("postplant_attack" if rd["stats"][sid]["team_side"] == "T" else "retake")
                    v[phase] += gain
                    if event["seconds"] >= 60:
                        v["late_"+phase] += gain
                    if current_team(rd["stats"][sid]["clan_name"], meta[name]["team"]):
                        v["current_team"] += gain
                    clusters[name][rd["match"]][0] += gain
    output = {}
    for name, v in totals.items():
        nm = len(sid_maps[name]); nc = len(current_maps[name])
        seed = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)
        output[name] = {"team": meta[name]["team"], "role": meta[name]["role"], "igl": old.get(name, {}).get("igl", False),
            "maps": nm, "swing_per_map": round(v["total"]/nm, 3),
            "by_time": {k: round(v[k]/nm, 3) for k in ("0-30", "30-60", "60+")},
            "by_phase": {k: round(v[k]/nm, 3) for k in ("preplant", "postplant_attack", "retake")},
            "late_by_phase": {k: round(v["late_"+k]/nm, 3) for k in ("preplant", "postplant_attack", "retake")},
            "current_team_maps": nc, "current_team_swing_per_map": round(v["current_team"]/nc, 3) if nc else None,
            "ci95_match_bootstrap": bootstrap_interval([(s, len(g)) for s, g in clusters[name].values()], seed),
            "old_swing_per_map": old.get(name, {}).get("rounds_per_map")}
    bins = []
    for lo in np.arange(0, 1, .1):
        ix = (predictions >= lo) & ((predictions <= 1) if lo > .85 else (predictions < lo+.1))
        if ix.any():
            bins.append({"n": int(ix.sum()), "predicted": float(np.average(predictions[ix], weights=weights[ix])),
                         "observed": float(np.average(y[ix], weights=weights[ix]))})
    out = {"model_version": "bomb-v4-objective-end-shapley", "complete": complete, "coverage": {"maps_attempted": available, "maps": usable_maps, "expected_maps": len(games), "rounds": len(rounds),
        "missing_maps": missing, "round_errors": summary_errors, "excluded_roster_or_outcome_rounds": skipped},
        "date_range": [min(r["date"] for r in rounds), max(r["date"] for r in rounds)],
        "validation": {"split": "5-fold held-out matches; equal total weight per round", "brier": brier_score_loss(y, predictions, sample_weight=weights),
            "log_loss": log_loss(y, predictions, sample_weight=weights),
            "no_phase_control_brier": brier_score_loss(y, baseline_predictions, sample_weight=weights), "calibration": bins},
        "limitations": ["Kill/death probability swing is not causal player value or a forecast.",
            "Objective execution counts are separate; planter is not awarded all team-created site value.",
            "Opponent strength, positioning, utility and health are not modelled.",
            "Intervals resample matches with scoring model fixed; they exclude model uncertainty.",
            "Kills in the final sampled frame around objective resolution are conservatively excluded.",
            "Same-frame kill credit averages marginal state changes over all within-frame orderings.",
            "Current-team summaries restrict actual team, but do not require identical five-player rosters."],
        "players": output, "team_objectives": dict(team_objectives)}
    dest = ROOT / "data" / ("swing_v4.json" if complete else "swing_v4_partial.json")
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(dest, out["coverage"], out["validation"]["brier"], flush=True)
    for n in sorted(output, key=lambda n: -output[n]["swing_per_map"])[:18]:
        print(n, output[n]["team"], output[n]["maps"], output[n]["swing_per_map"], output[n]["by_phase"], flush=True)


if __name__ == "__main__":
    main()
