"""Round clock per player: when do they die, when do they kill.

Reads data/rounds/<game>/<round>.json (from collect.py) -> data/player_rounds.csv + data/players.json.
Time = seconds after freeze end. A round is "full buy" for a player when bo3.gg's economy_level == 2.
Usage: python analyze.py [--min-rounds 300] [--all-buys]
"""
import argparse, csv, glob, json, os, statistics as stt
from collections import defaultdict

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
AWP = 309             # bo3.gg weapon id of the AWP (about half of m0NESY/w0nderful/torzsi/Jame kills)
AWP_MIN = 25.0        # a team's AWPer needs at least this % of his kills with the AWP
ENTRY_MIN_T = 40      # full-buy T rounds needed before a player can be tagged entry
TRADE_S = 5.0          # teammate kills your killer within 5 s -> your death was traded
POST_ROUND_FRAMES = 41  # replay keeps ~5 s after the round ends (checked: frames = round_duration*8 + 41)


def norm(s):
    return "".join(ch for ch in (s or "").lower() if ch.isalnum())


def major_players():
    """HLTV current lineups of the 32 Major teams -> {normalised name: team}."""
    field = json.load(open(os.path.join(ROOT, "..", "video06", "research", "field.json"), encoding="utf-8"))
    team_of = {t["hltv"]: t["team"] for s in ("stage1", "stage2", "stage3") for t in field[s]}
    lu = json.load(open(os.path.join(ROOT, "..", "video06", "research", "hltv", "lineups_now.json"), encoding="utf-8"))
    out = {}
    for hid, players in lu["teams"].items():
        if hid in team_of:
            for p in players:
                out[norm(p["name"])] = {"name": p["name"], "team": team_of[hid]}
    return out


def player_rows(d, game):
    """One row per player in this round."""
    rate, step = d["rate"], d["step"]
    end_t = (d["tick0"] + step * (d["frames"] - POST_ROUND_FRAMES) - d["live_tick"]) / rate
    name2sid = {r[0]: r[1] for r in d["roster"]}
    side_of = {r[1]: ("T" if r[2] == 2 else "CT") for r in d["roster"]}
    kills = [k for k in d["kills"] if k[3] in name2sid]
    if kills:
        end_t = max(end_t, kills[-1][0])
    death, kill_ts, killer_of, awp = {}, defaultdict(list), {}, defaultdict(int)
    for t, kn, kt, vn, vt, w in kills:
        v = name2sid[vn]
        death.setdefault(v, t)
        killer_of.setdefault(v, (name2sid.get(kn), t))
        if kn in name2sid and kt != vt:
            kill_ts[name2sid[kn]].append(t)
            awp[name2sid[kn]] += w == AWP
    first = kills[0] if kills else None
    rows = []
    for s in d["stats"]:
        sid = s["steam_id"]
        if sid not in side_of:
            continue
        dt = death.get(sid)
        traded = False
        if dt is not None and killer_of.get(sid, (None,))[0]:
            k_sid = killer_of[sid][0]
            kd = death.get(k_sid)
            traded = kd is not None and 0 <= kd - dt <= TRADE_S
        name = next((r[0] for r in d["roster"] if r[1] == sid), s["nick"])
        rows.append({
            "game": game["id"], "round": d["r"], "date": game["date"][:10], "map": game["map"], "tier": game["tier"],
            "steam_id": sid, "slug": s["player"], "name": name, "clan": s["clan_name"], "side": side_of[sid],
            "win": s["win"], "eco": s["economy_level"], "end_t": round(end_t, 2),
            "died": dt is not None, "death_t": dt, "traded": traded,
            "kills": len(kill_ts[sid]), "awp_kills": awp[sid], "first_kill_t": min(kill_ts[sid]) if kill_ts[sid] else None,
            "kill_ts": ";".join(f"{x:.2f}" for x in kill_ts[sid]),
            "opening_kill": bool(first) and name2sid.get(first[1]) == sid and first[2] != first[4],
            "opening_death": bool(first) and name2sid.get(first[3]) == sid,
        })
    return rows


def km_median(times, events):
    """Kaplan-Meier median survival (time alive), censored at round end."""
    pts = sorted(zip(times, events))
    n, s = len(pts), 1.0
    i = 0
    while i < len(pts):
        t = pts[i][0]
        d = sum(1 for x in pts[i:] if x[0] == t and x[1])
        c = sum(1 for x in pts[i:] if x[0] == t)
        if d:
            s *= 1 - d / n
            if s <= 0.5:
                return t
        n -= c
        i += c
    return None  # survives more than half the time


def alive_at(rows, t):
    """Share of rounds still alive at t seconds (rounds that ended earlier count if he survived them)."""
    ok = [r for r in rows if r["end_t"] >= t or not r["died"]]
    return sum(1 for r in ok if not r["died"] or r["death_t"] > t) / len(ok) if ok else None


def summarize(rows):
    deaths = [r["death_t"] for r in rows if r["died"]]
    kts = [float(x) for r in rows for x in r["kill_ts"].split(";") if x]
    fk = [r["first_kill_t"] for r in rows if r["first_kill_t"] is not None]
    od = [r for r in rows if r["opening_death"]]
    n = len(rows)
    return {
        "rounds": n,
        "survive_pct": round(100 * sum(not r["died"] for r in rows) / n, 1),
        "median_death_t": round(stt.median(deaths), 1) if deaths else None,
        "km_median_alive_t": km_median([r["death_t"] if r["died"] else r["end_t"] for r in rows],
                                       [r["died"] for r in rows]),
        "alive_at_30": round(100 * alive_at(rows, 30), 1),
        "alive_at_60": round(100 * alive_at(rows, 60), 1),
        "opening_death_pct": round(100 * len(od) / n, 1),
        "untraded_opening_death_pct": round(100 * sum(1 for r in od if not r["traded"]) / n, 1),
        "opening_kill_pct": round(100 * sum(r["opening_kill"] for r in rows) / n, 1),
        "kills_per_round": round(len(kts) / n, 3),
        "median_kill_t": round(stt.median(kts), 1) if kts else None,
        "median_first_kill_t": round(stt.median(fk), 1) if fk else None,
        "win_pct": round(100 * sum(r["win"] for r in rows) / n, 1),
        "awp_kill_pct": round(100 * sum(r["awp_kills"] for r in rows) / max(1, len(kts)), 1),
        "opening_duel_pct": round(100 * sum(r["opening_kill"] or r["opening_death"] for r in rows) / n, 1),
    }


def tag_roles(players):
    """Per team: AWPer = highest AWP-kill share (>= AWP_MIN); entry = non-AWPer with the most
    T-side opening duels (opening kill or death per full-buy T round); everyone else = rifler."""
    teams = defaultdict(list)
    for p in players:
        teams[p["team"]].append(p)
    for team, ps in teams.items():
        for p in ps:
            p["role"] = "rifler"
        awp = max(ps, key=lambda p: p["awp_kill_pct"])
        if awp["awp_kill_pct"] >= AWP_MIN:
            awp["role"] = "AWPer"
        rest = [p for p in ps if p["role"] != "AWPer" and p.get("T", {}).get("rounds", 0) >= ENTRY_MIN_T]
        if rest:
            max(rest, key=lambda p: p["T"]["opening_duel_pct"])["role"] = "entry"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-rounds", type=int, default=300)
    ap.add_argument("--all-buys", action="store_true")
    a = ap.parse_args()
    games = json.load(open(os.path.join(ROOT, "data", "games.json"), encoding="utf-8"))
    rows = []
    for f in glob.glob(os.path.join(ROOT, "data", "rounds", "*", "*.json")):
        d = json.load(open(f, encoding="utf-8"))
        g = games.get(str(d["g"]))
        if g:
            rows += player_rows(d, g)
    with open(os.path.join(ROOT, "data", "player_rounds.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    major = major_players()
    by_sid = defaultdict(list)
    for r in rows:
        if a.all_buys or r["eco"] == 2:
            by_sid[r["steam_id"]].append(r)
    # one player can have several Steam accounts -> merge on the Major roster name
    by = defaultdict(list)
    sids = defaultdict(set)
    for sid, rs in by_sid.items():
        names = [r["slug"] or "" for r in rs] + [r["name"] for r in rs]
        key = next((norm(x) for x in names if norm(x) in major), None)
        if key:
            by[key] += rs
            sids[key].add(sid)
    out = []
    for key, rs in by.items():
        m = major[key]
        s = {"player": m["name"], "team": m["team"], "steam_ids": sorted(sids[key]), **summarize(rs)}
        for side in ("T", "CT"):
            sr = [r for r in rs if r["side"] == side]
            if sr:
                s[side] = summarize(sr)
        out.append(s)
    tag_roles(out)
    json.dump(out, open(os.path.join(ROOT, "data", "players.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    found = {norm(p["player"]) for p in out}
    missing = sorted(v["name"] + " (" + v["team"] + ")" for k, v in major.items() if k not in found)
    print(f"{len(rows)} player-rounds, {len(out)} Major players found, missing {len(missing)}: {', '.join(missing[:40])}")

    ok = [p for p in out if p["rounds"] >= a.min_rounds]
    print(f"{len(ok)} players with {a.min_rounds}+ {'' if a.all_buys else 'full-buy '}rounds")
    cols = ["role", "awp_kill_pct", "rounds", "survive_pct", "km_median_alive_t", "alive_at_60", "opening_death_pct",
            "untraded_opening_death_pct", "opening_kill_pct", "median_kill_t", "median_first_kill_t"]
    def show(title, key, rev, pool, k=5):
        print(f"\n{title}")
        print(f"{'player':>12} {'team':>14} " + " ".join(f"{c[:10]:>10}" for c in cols))
        for p in sorted([p for p in pool if p.get(key) is not None], key=lambda p: p[key], reverse=rev)[:k]:
            print(f"{p['player']:>12} {p['team'][:14]:>14} " + " ".join(f"{str(p[c]):>10}" for c in cols))
    print("\nROLES:", {r: sum(1 for p in out if p.get("role") == r) for r in ("AWPer", "entry", "rifler")})
    print("AWPers:", ", ".join(f"{p['player']} ({p['team']}, {p['awp_kill_pct']}%)" for p in out if p["role"] == "AWPer"))
    print("entries:", ", ".join(f"{p['player']} ({p['team']}, T duels {p['T']['opening_duel_pct']}%)"
                                for p in out if p["role"] == "entry"))
    for role in ("AWPer", "entry", "rifler"):
        pool = [p for p in ok if p.get("role") == role]
        print(f"\n==================== {role.upper()}S ({len(pool)} with {a.min_rounds}+ rounds) ====================")
        show("HARDEST TO KILL (alive at 60 s)", "alive_at_60", True, pool)
        show("FIRST ON THE FLOOR (alive at 60 s, lowest)", "alive_at_60", False, pool)
        show("EASY FARM (untraded opening deaths)", "untraded_opening_death_pct", True, pool)
        show("FASTEST KILLERS (median kill time)", "median_kill_t", False, pool)
        show("LATEST KILLERS (median kill time)", "median_kill_t", True, pool)


if __name__ == "__main__":
    main()
