"""Round swing (win probability added) per player, from our own 46K rounds.

1. Win model: P(T side wins) given the state before/after a kill:
   (T economy, CT economy, T alive, CT alive, 15-s time bucket), counted from the data, with back-off
   to coarser states when a cell has < MIN_N rounds.
2. Every kill moves that probability. Killer's team gains delta -> killer +delta; victim -delta.
   delta is measured at the moment of the kill (same time bucket before/after), so time passing is not credited.
3. Per player: swing per round, converted to rounds per map (x rounds he plays per map), also split by
   when in the round it happened (0-30 s, 30-60 s, 60 s+) and compared to his own teammates.
Bomb plants are not in our data, so post-plant states are approximated by time only.
Output: data/swing.json
"""
import glob, json, os, statistics as st
from collections import defaultdict, Counter

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
MIN_N = 40
BUCKET = 15


def eco_of(stats, side):
    v = [s["economy_level"] for s in stats if s["team_side"] == side and s["economy_level"] is not None]
    if not v:
        return 1
    m = Counter(v).most_common(1)[0][0]
    return 0 if m <= 0 else 1 if m == 1 else 2  # 0 eco/pistol/light, 1 force, 2 full


def load():
    rounds = []
    for f in glob.glob(os.path.join(ROOT, "data", "rounds", "*", "*.json")):
        d = json.load(open(f, encoding="utf-8"))
        side = {r[1]: ("T" if r[2] == 2 else "CT") for r in d["roster"]}
        name2sid = {r[0]: r[1] for r in d["roster"]}
        win = next((s["team_side"] for s in d["stats"] if s["win"] == 1), None)
        if win not in ("T", "CT") or len(side) != 10:
            continue
        ev = []
        for t, kn, kt, vn, vt, w in d["kills"]:
            v = name2sid.get(vn)
            if v is None or t < 0:
                continue
            k = name2sid.get(kn)
            ev.append((t, k if (k and side.get(k) != side[v]) else None, v))
        stats = {s["steam_id"]: s for s in d["stats"]}
        rounds.append({"g": d["g"], "r": d["r"], "side": side, "win": win, "ev": ev,
                       "eco": (eco_of(d["stats"], "T"), eco_of(d["stats"], "CT")),
                       "peco": {sid: s["economy_level"] for sid, s in stats.items()}})
    return rounds


def states(rd):
    """Yield (time, state_before, state_after, killer, victim) for each kill."""
    aT = aCT = 5
    eT, eC = rd["eco"]
    for t, k, v in rd["ev"]:
        b = int(t // BUCKET)
        before = (eT, eC, aT, aCT, b)
        if rd["side"][v] == "T":
            aT -= 1
        else:
            aCT -= 1
        yield t, before, (eT, eC, aT, aCT, b), k, v
        if aT <= 0 or aCT <= 0:
            break


def main():
    rounds = load()
    print(len(rounds), "rounds")
    # --- win model counts at three levels of detail
    cnt = [defaultdict(lambda: [0, 0]) for _ in range(3)]
    keys = [lambda s: s, lambda s: (s[2], s[3], s[4]), lambda s: (s[2], s[3])]
    for rd in rounds:
        tw = rd["win"] == "T"
        seen = set()
        for t, a, b, k, v in states(rd):
            for s in (a, b):
                if s in seen:
                    continue
                seen.add(s)
                for i in range(3):
                    c = cnt[i][keys[i](s)]
                    c[0] += tw; c[1] += 1

    def p_t(s):
        aT, aC = s[2], s[3]
        if aT <= 0:
            return 0.0
        if aC <= 0:
            return 1.0
        for i in range(3):
            c = cnt[i].get(keys[i](s))
            if c and c[1] >= MIN_N:
                return (c[0] + 1) / (c[1] + 2)
        return 0.5

    # sanity: model at 5v5 full buy
    print("P(T) 5v5 full/full by bucket:", [round(p_t((2, 2, 5, 5, b)), 2) for b in range(0, 8)])
    print("P(T) 4v5 / 5v4 at 30-45 s:", round(p_t((2, 2, 4, 5, 2)), 2), round(p_t((2, 2, 5, 4, 2)), 2))

    # --- credit swing
    sw = defaultdict(lambda: defaultdict(float))   # sid -> bucket -> swing
    nr = Counter()                                  # sid -> rounds played
    nfb = Counter(); swfb = defaultdict(float)      # full-buy rounds only
    games = defaultdict(set)
    for rd in rounds:
        for sid in rd["side"]:
            nr[sid] += 1
            games[sid].add(rd["g"])
            if rd["peco"].get(sid) == 2:
                nfb[sid] += 1
        for t, a, b, k, v in states(rd):
            d = p_t(b) - p_t(a)                     # change in P(T wins)
            gain_v_team = d if rd["side"][v] == "T" else -d  # change in the victim's team win chance (<= 0)
            win_bucket = "0-30" if t < 30 else "30-60" if t < 60 else "60+"
            sw[v][win_bucket] += gain_v_team
            if rd["peco"].get(v) == 2:
                swfb[v] += gain_v_team
            if k:
                sw[k][win_bucket] -= gain_v_team
                if rd["peco"].get(k) == 2:
                    swfb[k] -= gain_v_team

    P = json.load(open(os.path.join(ROOT, "data", "players.json"), encoding="utf-8"))
    out = {}
    for p in P:
        sids = p["steam_ids"]
        n = sum(nr[s] for s in sids)
        if n < 300:
            continue
        maps = len(set().union(*[games[s] for s in sids]))
        tot = {b: sum(sw[s][b] for s in sids) for b in ("0-30", "30-60", "60+")}
        total = sum(tot.values())
        out[p["player"]] = {"team": p["team"], "role": p["role"], "rounds": n, "maps": maps,
                            "swing_per_round": round(total / n, 4),
                            "rounds_per_map": round(total / maps, 2),
                            "season_rounds": round(total, 1),
                            "by_time_per_map": {b: round(v / maps, 2) for b, v in tot.items()},
                            "fullbuy_swing_per_round": round(sum(swfb[s] for s in sids) / max(1, sum(nfb[s] for s in sids)), 4)}
    # compare with own teammates (current five)
    team = defaultdict(list)
    for n, v in out.items():
        team[v["team"]].append(v["swing_per_round"])
    for n, v in out.items():
        mates = [x for x in team[v["team"]]]
        if len(mates) >= 4:
            others = (sum(mates) - v["swing_per_round"]) / (len(mates) - 1)
            v["vs_teammates_per_map"] = round((v["swing_per_round"] - others) * v["rounds"] / v["maps"], 2)
    json.dump(out, open(os.path.join(ROOT, "data", "swing.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    def show(title, key, rev, pool=None, k=8):
        q = sorted([(n, v) for n, v in out.items() if v.get(key) is not None and (pool is None or v["role"] == pool)],
                   key=lambda x: x[1][key], reverse=rev)[:k]
        print(f"\n{title}")
        for n, v in q:
            bt = v["by_time_per_map"]
            print(f"  {n:>11} {v['team'][:13]:>13} {v['role']:>6}  {v['rounds_per_map']:+.2f}/map  vs mates {v.get('vs_teammates_per_map', 0):+.2f}"
                  f"  season {v['season_rounds']:+.0f}  [0-30 {bt['0-30']:+.2f} | 30-60 {bt['30-60']:+.2f} | 60+ {bt['60+']:+.2f}]  maps {v['maps']}")
    show("CARRIES (rounds added per map)", "rounds_per_map", True)
    show("COSTS (rounds lost per map)", "rounds_per_map", False)
    show("CARRY vs OWN TEAMMATES", "vs_teammates_per_map", True)
    show("DRAG vs OWN TEAMMATES", "vs_teammates_per_map", False)
    for n in ("donk", "ZywOo", "m0NESY", "YEKINDAR", "flameZ", "zweih", "ArtFr0st", "KaiR0N-", "robo", "s1mple", "NiKo", "ropz"):
        if n in out:
            v = out[n]; bt = v["by_time_per_map"]
            print(f"  {n:>9}: {v['rounds_per_map']:+.2f}/map, vs mates {v.get('vs_teammates_per_map', 0):+.2f}, season {v['season_rounds']:+.0f}, "
                  f"[0-30 {bt['0-30']:+.2f} | 30-60 {bt['30-60']:+.2f} | 60+ {bt['60+']:+.2f}]")


if __name__ == "__main__":
    main()
