"""Video 07: did the roster moves since the Cologne Major work?

Each tracked team (48, HLTV map results Apr 1 – Nov 7 2026) gets three separate strength values:
  A  "Cologne era"  Apr 1 – Jun 21   (the team as it was at the last Major)
  T  transition     Jun 22 – Sep 7   (moves happening; fitted but not judged)
  B  "now"          Sep 8 – Nov 7    (the team that goes to Singapore)
Opponents we don't track keep one value for the whole period (they anchor the scale). Map-level logistic model
(Bradley-Terry), opponent-adjusted, mild shrinkage to the average. Strength is shown as the chance to win a map against
an average Singapore Major team (the 32 teams' B values). Change = B - A, with a +-2 standard-error band.
Control group: teams whose five didn't change (Valve's monthly rosters) — how much do teams move anyway?
Output: video07/data/eras.json
"""
import datetime as dt, glob, json, math, pathlib
import numpy as np
from scipy.optimize import minimize

HERE = pathlib.Path(__file__).resolve().parent
RES = HERE.parent / "research"
A0, A1, B0, B1 = dt.date(2026, 4, 1), dt.date(2026, 6, 21), dt.date(2026, 9, 8), dt.date(2026, 11, 7)
FIELD = json.loads(pathlib.Path(r"D:\Youtube\video06\research\field.json").read_text(encoding="utf-8"))
MAJOR = {t["hltv"] for k in ("stage1", "stage2", "stage3") for t in FIELD[k]}
ROST = json.loads((RES / "valve_rosters.json").read_text(encoding="utf-8"))


def day(s):
    d, m, y = s.split("/")
    return dt.date(2000 + int(y), int(m), int(d))


def era(d):
    return "A" if A0 <= d <= A1 else ("B" if B0 <= d <= B1 else "T")


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
        seen.add(m["mapstatsid"])
        rows.append((day(m["date"]), j["id"], m["oppId"], 1 if m["wl"] == "W" else 0))
names.update({t: names.get(t, s) for t, s in tracked.items()})


# Parameters: one value per untracked opponent; per tracked team a BASE strength plus an offset for each era (A, T, B).
# Offsets are pulled toward 0 = "no change" (sd SIG_E), so a team with few maps in an era stays close to its own level
# instead of being dragged toward the average of all teams. Rating of a team in an era = base + offset.
SIG_U, SIG_B, SIG_E = 1.0, 1.5, 0.5
untracked = sorted({b for d, a, b, y in rows if b not in tracked} | {a for d, a, b, y in rows if a not in tracked})
tl = sorted(tracked)
iu = {t: i for i, t in enumerate(untracked)}; nu = len(untracked)
it = {t: i for i, t in enumerate(tl)}; nt = len(tl)
E = {"A": 0, "T": 1, "B": 2}
n = nu + nt + 3 * nt                      # [untracked | bases | offsets (team, era)]


def cols(team, d):
    """indices that make up this team's rating on date d"""
    if team in tracked:
        return [nu + it[team], nu + nt + 3 * it[team] + E[era(d)]]
    return [iu[team]]


ca = [cols(a, d) for d, a, b, y in rows]; cb = [cols(b, d) for d, a, b, y in rows]
y = np.array([r[3] for r in rows], dtype=float)
M = len(rows)
from scipy.sparse import csr_matrix
data, ri, ci = [], [], []
for k, (xa, xb) in enumerate(zip(ca, cb)):
    for c in xa: ri.append(k); ci.append(c); data.append(1.0)
    for c in xb: ri.append(k); ci.append(c); data.append(-1.0)
X = csr_matrix((data, (ri, ci)), shape=(M, n))
prec = np.concatenate([np.full(nu, 1 / SIG_U ** 2), np.full(nt, 1 / SIG_B ** 2), np.full(3 * nt, 1 / SIG_E ** 2)])


def f(r):
    z = X @ r; p = 1 / (1 + np.exp(-z))
    loss = -np.sum(y * np.log(p + 1e-12) + (1 - y) * np.log(1 - p + 1e-12)) + 0.5 * np.sum(prec * r ** 2)
    return loss, X.T @ (p - y) + prec * r


r = minimize(f, np.zeros(n), jac=True, method="L-BFGS-B", options={"maxiter": 5000}).x
p = 1 / (1 + np.exp(-(X @ r))); w = p * (1 - p)
H = (X.T @ X.multiply(w[:, None])).toarray() + np.diag(prec)        # full Hessian (n is small)
C = np.linalg.inv(H)
cnt_era = {}
for (d, a, b, yy) in rows:
    for t in (a, b):
        if t in tracked:
            cnt_era[(t, era(d))] = cnt_era.get((t, era(d)), 0) + 1


def rating(t, e):
    return r[nu + it[t]] + r[nu + nt + 3 * it[t] + E[e]]


def delta(t):
    ia_, ib_ = nu + nt + 3 * it[t] + E["A"], nu + nt + 3 * it[t] + E["B"]
    v = C[ib_, ib_] + C[ia_, ia_] - 2 * C[ia_, ib_]
    return r[ib_] - r[ia_], math.sqrt(max(v, 1e-12))


ref = np.mean([rating(t, "B") for t in MAJOR if t in tracked])        # average Singapore team, now
win = lambda v: 1 / (1 + math.exp(-(v - ref)))

valve_by_lower = {k.lower(): k for k in ROST}
alias = {"natus-vincere": "natus vincere", "ninjas-in-pyjamas": "ninjas in pyjamas", "the-mongolz": "the mongolz", "eternal-fire": "eternal fire",
         "100-thieves": "100 thieves", "bcgame": "bc.game", "chinggis-warriors": "chinggis warriors", "lynn-vision": "lynn vision",
         "inner-circle": "inner circle", "virtuspro": "virtus.pro", "passion-ua": "passion ua", "gentle-mates": "gentle mates", "betboom": "betboom"}
out = []
for t, slug in tracked.items():
    if cnt_era.get((t, "A"), 0) < 8 or cnt_era.get((t, "B"), 0) < 8:
        continue                                                     # too little data in one of the eras
    vk = valve_by_lower.get(alias.get(slug, slug.replace("-", " ")).lower())
    ro = ROST.get(vk) if vk else None
    changes = ro["changes"] if ro else None
    d, dse = delta(t)
    out.append({"team": names.get(t, slug), "hltv": t, "major": t in MAJOR, "maps_A": cnt_era.get((t, "A"), 0), "maps_B": cnt_era.get((t, "B"), 0),
                "win_A": round(win(rating(t, "A")), 3), "win_B": round(win(rating(t, "B")), 3), "delta_logit": round(d, 3), "delta_se": round(dse, 3),
                "clear": bool(abs(d) > 2 * dse), "roster_changed": None if changes is None else bool(changes), "changes": changes,
                "valve_rank": None if not ro else {"jun": ro["ranks"]["2026_06_01"], "nov": ro["ranks"]["2026_11_02"]}})
out.sort(key=lambda o: -o["delta_logit"])
(HERE.parent / "data").mkdir(exist_ok=True)
(HERE.parent / "data" / "eras.json").write_text(json.dumps({"eras": {"A": [str(A0), str(A1)], "B": [str(B0), str(B1)]}, "maps": len(rows), "teams": out}, indent=1, ensure_ascii=False), encoding="utf-8")

print(f"{len(rows)} unique maps, {len(out)} teams with both eras\n")
print(f"{'team':18} {'Cologne':>7} {'now':>6} {'change':>7}  {'maps A/B':>8}  clear  five changed   valve rank")
for o in out:
    ch = {None: "?", True: "yes", False: "no"}[o["roster_changed"]]
    vr = f"#{o['valve_rank']['jun']} -> #{o['valve_rank']['nov']}" if o["valve_rank"] else ""
    print(f"{o['team']:18} {o['win_A']*100:6.0f}% {o['win_B']*100:5.0f}% {(o['win_B']-o['win_A'])*100:+6.0f}  {o['maps_A']:>4}/{o['maps_B']:<4}  {'*' if o['clear'] else ' '}      {ch:4}         {vr}")
for grp, flag in (("changed", True), ("kept their five", False)):
    ds = [o["delta_logit"] for o in out if o["roster_changed"] is flag]
    if ds:
        print(f"\n{grp}: {len(ds)} teams, average change {np.mean(ds):+.2f} logit, spread (sd) {np.std(ds):.2f}")
