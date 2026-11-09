"""Video 07, precise version: each team judged on its REAL current five (stand-ins and loans left out).

Era A  = Apr 1 – Jun 21 (the team at Cologne).
Era B  = maps played by the real current five only, from the day that five first played together (no-change teams:
         from Sep 8), up to Nov 7. Lineup per date comes from Valve's match-by-match rosters (data/lineup_timeline.json).
Other  = everything else (transition, stand-in and loan matches): fitted, not judged.
Model as eras.py: map-level logistic, base + era offsets shrunk to "no change". Then the fair verdict removes regression to
the mean (good teams drift down, weak teams up) and the Asia-wide drift. Moves with < 15 maps in era B: "too early".
Output: data/moves_verdict.json
"""
import datetime as dt, glob, json, math, pathlib
import numpy as np
from scipy.optimize import minimize
from scipy.sparse import csr_matrix

HERE = pathlib.Path(__file__).resolve().parent
DATA, RES = HERE.parent / "data", HERE.parent / "research"
A0, A1, BSTART, END = dt.date(2026, 4, 1), dt.date(2026, 6, 21), dt.date(2026, 9, 8), dt.date(2026, 11, 7)
MIN_B = 15
TL = json.loads((DATA / "lineup_timeline.json").read_text(encoding="utf-8"))
AUTO = json.loads((DATA / "net_moves.json").read_text(encoding="utf-8"))
CUR = {k: v for k, v in json.loads((DATA / "moves_curated.json").read_text(encoding="utf-8")).items() if not k.startswith("_")}
FIELD = json.loads(pathlib.Path(r"D:\Youtube\video06\research\field.json").read_text(encoding="utf-8"))
MAJOR = {t["hltv"] for k in ("stage1", "stage2", "stage3") for t in FIELD[k]}
VRS = json.loads(pathlib.Path(r"D:\Youtube\video05\research\hltv\vrs_daily_2026-10-05_to_2026-11-02.json").read_text(encoding="utf-8"))["days"]
REGION = {}
for dd in VRS.values():
    for x in dd:
        REGION.setdefault(x["n"].lower(), x["g"])
D = lambda s: dt.date.fromisoformat(s)


def hday(s):
    d, m, y = s.split("/")
    return dt.date(2000 + int(y), int(m), int(d))


# ---- maps and tracked teams
rows, seen, names, tracked = [], set(), {}, {}
for f in sorted(glob.glob(str(RES / "hltv" / "maps_*.json"))):
    j = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
    if "id" not in j:
        continue
    tracked[j["id"]] = j["slug"]
    for m in j["maps"]:
        names.setdefault(m["oppId"], m["opp"])
        if m["mapstatsid"] in seen:
            continue
        seen.add(m["mapstatsid"]); rows.append((hday(m["date"]), j["id"], m["oppId"], 1 if m["wl"] == "W" else 0))
valve_name = {}
for t in tracked:
    n = names.get(t, tracked[t]).lower()
    valve_name[t] = next((v for v in TL if v.lower() == n), None)

# ---- real current five + the date it starts, per tracked team
info = {}
for t, vn in valve_name.items():
    if not vn or not TL[vn]["runs"]:
        continue
    runs = TL[vn]["runs"]
    cur = CUR.get(vn, {})
    spec = cur.get("five", "auto-now")
    if spec == "auto-now":
        real = set(runs[-1]["five"])
    elif spec == "auto-prev":
        real = set(runs[-2]["five"]) if len(runs) > 1 else set(runs[-1]["five"])
    else:
        real = set(spec)
    ins = cur.get("in") if cur else AUTO.get(vn, {}).get("in", [])
    outs = cur.get("out") if cur else AUTO.get(vn, {}).get("out", [])
    # when did the real five start? the start of the last stretch of runs with exactly that five
    starts = [D(r["from"]) for r in runs if set(r["five"]) == real]
    changed = bool(ins)
    if changed:
        # first match the real five played together; stand-in matches after that are excluded by era()
        b_from = min(starts) if starts else BSTART
    else:
        b_from = BSTART
    info[t] = {"valve": vn, "real": real, "in": ins, "out": outs, "b_from": b_from, "runs": runs, "note": cur.get("note", "")}


def lineup_on(t, d):
    """the five that played for tracked team t on date d (Valve runs; between runs, the previous run)"""
    runs = info[t]["runs"]; best = None
    for r in runs:
        if D(r["from"]) <= d:
            best = r
    return set(best["five"]) if best else None


def era(t, d):
    if t not in tracked:
        return None
    if A0 <= d <= A1:
        return "A"
    if t in info and info[t]["b_from"] <= d <= END:
        lu = lineup_on(t, d)
        if lu is None or lu == info[t]["real"]:
            return "B"
    return "O"


# ---- fit: untracked opponents one value each; tracked team = base + offset(A / B / O)
SIG_U, SIG_B, SIG_E = 1.0, 1.5, 0.5
untracked = sorted({x for d, a, b, y in rows for x in (a, b) if x not in tracked})
tl = sorted(tracked); iu = {t: i for i, t in enumerate(untracked)}; it = {t: i for i, t in enumerate(tl)}
nu, nt = len(untracked), len(tl); E = {"A": 0, "B": 1, "O": 2}; n = nu + nt + 3 * nt


def cols(t, d):
    return [nu + it[t], nu + nt + 3 * it[t] + E[era(t, d)]] if t in tracked else [iu[t]]


data, ri, ci, cnt = [], [], [], {}
for k, (d, a, b, y) in enumerate(rows):
    for sgn, t in ((1.0, a), (-1.0, b)):
        for c in cols(t, d):
            ri.append(k); ci.append(c); data.append(sgn)
        if t in tracked:
            cnt[(t, era(t, d))] = cnt.get((t, era(t, d)), 0) + 1
X = csr_matrix((data, (ri, ci)), shape=(len(rows), n)); yv = np.array([r[3] for r in rows], dtype=float)
prec = np.concatenate([np.full(nu, 1 / SIG_U ** 2), np.full(nt, 1 / SIG_B ** 2), np.full(3 * nt, 1 / SIG_E ** 2)])


def f(r):
    p = 1 / (1 + np.exp(-(X @ r)))
    return -np.sum(yv * np.log(p + 1e-12) + (1 - yv) * np.log(1 - p + 1e-12)) + 0.5 * np.sum(prec * r ** 2), X.T @ (p - yv) + prec * r


r = minimize(f, np.zeros(n), jac=True, method="L-BFGS-B", options={"maxiter": 5000}).x
p = 1 / (1 + np.exp(-(X @ r))); w = p * (1 - p)
C = np.linalg.inv((X.T @ X.multiply(w[:, None])).toarray() + np.diag(prec))
off = lambda t, e: nu + nt + 3 * it[t] + E[e]
rating = lambda t, e: r[nu + it[t]] + r[off(t, e)]
ref = np.mean([rating(t, "B") for t in MAJOR if t in tracked and cnt.get((t, "B"), 0) >= 5])
win = lambda v: 1 / (1 + math.exp(-(v - ref)))

out = []
for t in tracked:
    if t not in info or cnt.get((t, "A"), 0) < 8:
        continue
    a_, b_ = off(t, "A"), off(t, "B")
    dlt = r[b_] - r[a_]; se = math.sqrt(max(C[a_, a_] + C[b_, b_] - 2 * C[a_, b_], 1e-12))
    i = info[t]
    out.append({"team": names.get(t, tracked[t]), "hltv": t, "region": REGION.get(names.get(t, "").lower(), "?"), "major": t in MAJOR,
                "moved": bool(i["in"]), "in": i["in"], "out": i["out"], "real_five_since": str(i["b_from"]), "note": i["note"],
                "maps_A": cnt.get((t, "A"), 0), "maps_B": cnt.get((t, "B"), 0), "too_early": cnt.get((t, "B"), 0) < MIN_B,
                "level_A": round(rating(t, "A") - ref, 3), "win_A": round(win(rating(t, "A")), 3), "win_B": round(win(rating(t, "B")), 3),
                "delta": round(dlt, 3), "delta_se": round(se, 3)})

# ---- fair verdict: remove regression to the mean + Asia drift (fitted on teams with enough data), keep the roster effect
ok = [o for o in out if not o["too_early"]]
Xr = np.array([[1, o["level_A"], 1.0 if o["moved"] else 0.0, 1.0 if o["region"] == "AS" else 0.0] for o in ok]); yr = np.array([o["delta"] for o in ok])
beta, *_ = np.linalg.lstsq(Xr, yr, rcond=None)
res = yr - Xr @ beta; s2 = res @ res / (len(yr) - 4); bse = np.sqrt(np.diag(np.linalg.inv(Xr.T @ Xr)) * s2)
for o in out:
    o["expected_drift"] = round(beta[0] + beta[1] * o["level_A"] + beta[3] * (o["region"] == "AS"), 3)
    o["verdict"] = round(o["delta"] - o["expected_drift"], 3)
    # in percentage points vs an average Major team, starting from where the team was
    base = o["level_A"] + o["expected_drift"]
    o["verdict_pts"] = round((1 / (1 + math.exp(-(base + o["verdict"]))) - 1 / (1 + math.exp(-base))) * 100, 1)
out.sort(key=lambda o: -o["verdict"])
summary = {"roster_effect_logit": round(beta[2], 3), "roster_effect_se": round(bse[2], 3), "regression_to_mean": round(beta[1], 3),
           "asia_drift": round(beta[3], 3), "teams_judged": len(ok)}
(DATA / "moves_verdict.json").write_text(json.dumps({"summary": summary, "teams": out}, indent=1, ensure_ascii=False), encoding="utf-8")

print(f"roster effect {beta[2]:+.2f} +- {2*bse[2]:.2f} (95%), regression to the mean {beta[1]:+.2f}, Asia {beta[3]:+.2f}, {len(ok)} teams judged\n")
print(f"{'team':18} {'move':52} {'since':10} {'Cologne':>7} {'now':>5} {'verdict':>8}  maps B")
for o in out:
    mv = ("+" + ",".join(o["in"]) + "  -" + ",".join(o["out"])) if o["moved"] else "(no real change)"
    v = "too early" if o["too_early"] else f"{o['verdict_pts']:+.0f} pts"
    print(f"{o['team']:18} {mv[:52]:52} {o['real_five_since']:10} {o['win_A']*100:6.0f}% {o['win_B']*100:4.0f}% {v:>9}  {o['maps_B']}")
