"""Checks every number Brian says (script_v1.md) against the research tables. Prints one line per claim: OK / FAIL.
Facts that come from sources rather than our tables are listed at the end with their source (checked by hand)."""
import csv, json, pathlib

R = pathlib.Path(__file__).resolve().parent.parent / "research"
T = R / "tables"
wb = json.load(open(R / "raw" / "worldbank_population_2024.json", encoding="utf8"))[1]
pop = {r["countryiso3code"]: r["value"] for r in wb if r["value"]}
rows = lambda f: list(csv.DictReader(open(T / f, encoding="utf8")))
t1, t2, t3 = rows("pros_1_any_prize_money.csv"), rows("pros_2_s_a_tier_2026.csv"), rows("pros_3_hltv_top20_unique_2013_2025.csv")
rank = lambda tbl, iso: next(i + 1 for i, r in enumerate(tbl) if r["iso3"] == iso)
val = lambda tbl, iso, k="per_million": float(next(r[k] for r in tbl if r["iso3"] == iso))
top20 = json.load(open(R / "raw" / "hltv_top20_parsed.json", encoding="utf8"))
players = rows("s_a_tier_players_2026.csv")
ee = json.load(open(R / "raw" / "hltv_cs2era_maps_by_country_2026-11-08.json", encoding="utf8"))
# raw counts (all countries, not only > 1M) from the Esports Earnings table
es = {r["iso3"]: int(r["players"]) for r in rows("pros_by_country_esportsearnings.csv") if r["iso3"]}
es_total = sum(int(r["players"]) for r in rows("pros_by_country_esportsearnings.csv"))

def per_m_rank(counts, iso):
    pc = sorted(((n / pop[k], k) for k, n in counts.items() if pop.get(k, 0) > 1e6), reverse=True)
    return [k for _, k in pc].index(iso) + 1 if iso in counts else None

checks = []
def ok(block, claim, cond, got=""):
    checks.append((block, claim, bool(cond), got))

raw_order = sorted(es.items(), key=lambda kv: -kv[1])[:4]
ok("h1", "Russia 525 players with prize money", es["RUS"] == 525, es["RUS"])
ok("h1", "then United States, Brazil, China", [k for k, _ in raw_order] == ["RUS", "USA", "BRA", "CHN"], raw_order)
ok("h2", "Russia over 140 million people", 140e6 < pop["RUS"] < 150e6, pop["RUS"])
ok("h2", "Russia 29th / Brazil 44th / USA 49th per million", (rank(t1, "RUS"), rank(t1, "BRA"), rank(t1, "USA")) == (29, 44, 49), (rank(t1, "RUS"), rank(t1, "BRA"), rank(t1, "USA")))
ok("h3", "new #1 has 1.4 million people", t1[0]["iso3"] == "EST" and round(pop["EST"] / 1e6, 1) == 1.4, (t1[0]["iso3"], pop["EST"]))
ok("r1", "almost five thousand players with prize money", 4800 <= es_total < 5000, es_total)
ok("r2", "420 players at top-tier events", len(players) == 420, len(players))
ok("r2", "Top 20 since 2013", min(int(y) for y in top20 if int(y) >= 2013) == 2013, "")
ok("e1", "Estonia 34 per million", round(val(t1, "EST")) == 34, val(t1, "EST"))
ok("e1", "then Latvia, Denmark, Mongolia, Finland", [r["iso3"] for r in t1[1:5]] == ["LVA", "DNK", "MNG", "FIN"], [r["iso3"] for r in t1[:5]])
BALTIC = {"EST", "LVA", "LTU", "DNK", "FIN", "SWE", "POL", "DEU", "RUS"}
ok("e2", "six of the top eight around the Baltic", sum(r["iso3"] in BALTIC for r in t1[:8]) == 6, [r["iso3"] for r in t1[:8]])
ropz = sum(1 for y, e in top20.items() if 2013 <= int(y) <= 2025 for x in e if x["player"] == "ropz")
ok("e3", "ropz in the Top 20 eight times", ropz == 8, ropz)
mn = [p for p in players if p["iso3"] == "MNG"]
ok("m1", "28 of the 420 from Mongolia", len(mn) == 28, len(mn))
ok("m2", "almost eight per million", 7.5 <= val(t2, "MNG") < 8, val(t2, "MNG"))
ok("m2", "twice Denmark, in second", t2[1]["iso3"] == "DNK" and abs(val(t2, "MNG") / val(t2, "DNK") - 2) < 0.1, val(t2, "MNG") / val(t2, "DNK"))
ok("m3", "only seven play for The MongolZ", sum(p["team"] == "The MongolZ" for p in mn) == 7, sum(p["team"] == "The MongolZ" for p in mn))
for th in (20, 50, 100):
    c = {}
    for p in players:
        if int(p["maps"]) >= th: c[p["iso3"]] = c.get(p["iso3"], 0) + 1
    ok("m3", f"Mongolia top 2 at {th}+ maps", per_m_rank(c, "MNG") <= 2, per_m_rank(c, "MNG"))
mongol_top20 = [(y, x["player"]) for y, e in top20.items() if 2010 <= int(y) <= 2025 for x in e if x["flag"] == "mn" and not x["player"].startswith(":")]
ok("m5", "Senzu, 2025, the only Mongolian ever in the Top 20", mongol_top20 == [("2025", "Senzu")], mongol_top20)
uniq = {x["player"] for y, e in top20.items() if 2013 <= int(y) <= 2025 for x in e}
ok("t1", "101 players in the Top 20 since 2013", len(uniq) == 101, len(uniq))
ok("t1", "Denmark miles ahead (#1, over 2x #2)", t3[0]["iso3"] == "DNK" and val(t3, "DNK") > 2 * float(t3[1]["per_million"]), (val(t3, "DNK"), t3[1]["per_million"]))
def yr(y): return [x for x in top20[str(y)]]
ok("t3", "GeT_RiGhT #1 in 2013 and 2014, olofmeister #1 in 2015", (yr(2013)[0]["player"], yr(2014)[0]["player"], yr(2015)[0]["player"]) == ("GeT_RiGhT", "GeT_RiGhT", "olofmeister"), "")
ok("t3", "seven Swedes in 2014", sum(x["flag"] == "se" for x in yr(2014)) == 7, sum(x["flag"] == "se" for x in yr(2014)))
dev = sum(1 for y, e in top20.items() if 2013 <= int(y) <= 2025 for x in e if x["player"] == "dev1ce")
ok("t4", "dev1ce in the Top 20 nine times", dev == 9, dev)
iso2 = {"se": "SWE", "dk": "DNK", "lv": "LVA", "ee": "EST", "ba": "BIH", "sk": "SVK", "il": "ISR", "lt": "LTU", "fi": "FIN"}
leader = {}
for y in range(2013, 2026):
    c = {}
    for x in yr(y):
        k = iso2.get(x["flag"])
        if k: c[k] = c.get(k, 0) + 1
    leader[y] = max(c, key=lambda k: c[k] / pop[k])
ok("t2-t5", "per-person leader: SWE 2013-15, DNK 2016-18, shared with LVA/EST since 2019",
   [leader[y] for y in range(2013, 2019)] == ["SWE"] * 3 + ["DNK"] * 3 and set(leader[y] for y in range(2019, 2026)) == {"LVA", "DNK", "EST"}, leader)
niko = sum(1 for y, e in top20.items() if 2013 <= int(y) <= 2025 for x in e if x["player"] == "NiKo")
ok("t6", "NiKo ten times in the Top 20", niko == 10, niko)
ok("t6", "Bosnia 3.2 million people", round(pop["BIH"] / 1e6, 1) == 3.2, pop["BIH"])
ok("v1", "Estonia wins L1, Mongolia L2, Denmark L3", (t1[0]["iso3"], t2[0]["iso3"], t3[0]["iso3"]) == ("EST", "MNG", "DNK"), "")
both = [r["iso3"] for r in t1[:3] if r["iso3"] in {x["iso3"] for x in t2[:3]} and r["iso3"] in {x["iso3"] for x in t3[:3]}]
ok("v2", "only Denmark is top 3 at every level", both == ["DNK"], both)
c500 = {a.split(":")[0]: int(a.split(":")[1]) for a in ee["c500"].split(", ")}
fix = {"Denmark": "DNK", "Kosovo": "XKX", "Sweden": "SWE", "Russia": "RUS"}
pc500 = sorted(((n / pop[fix[k]], k) for k, n in c500.items() if k in fix), reverse=True)
ok("v2", "500+ maps: Denmark still first", pc500[0][1] == "Denmark", pc500[:2])
ok("v3", "Russia 20th or lower at every level", min(rank(t1, "RUS"), rank(t2, "RUS"), rank(t3, "RUS")) >= 20, (rank(t1, "RUS"), rank(t2, "RUS"), rank(t3, "RUS")))
ok("z1", "Mongolia #1 at today's top tier", t2[0]["iso3"] == "MNG", "")
# v2 lines (owner review)
ok("h2", "China seventieth per million", rank(t1, "CHN") == 70, rank(t1, "CHN"))
ok("e1", "Estonia: 47 pros, 1.4 million people", int(next(r["count"] for r in t1 if r["iso3"] == "EST")) == 47 and round(pop["EST"] / 1e6, 1) == 1.4, "")
ok("m1", "Mongolia: three and a half million people", round(pop["MNG"] / 1e6, 1) == 3.5, pop["MNG"])
oth = [int(p["maps"]) for p in mn if p["team"] != "The MongolZ"]
ok("m3", "the other 21 played 25 maps or fewer", len(oth) == 21 and max(oth) == 25, (len(oth), max(oth)))
def first_at(th):
    c = {}
    for p in players:
        if int(p["maps"]) >= th: c[p["iso3"]] = c.get(p["iso3"], 0) + 1
    pc = sorted(((n / pop[k], k) for k, n in c.items() if pop.get(k, 0) > 1e6), reverse=True)
    return [k for _, k in pc[:2]], c
ok("m3b", "20+ maps: Mongolia first", first_at(20)[0][0] == "MNG", first_at(20)[0])
ok("m3b", "50+ maps: Denmark first, Mongolia second", first_at(50)[0] == ["DNK", "MNG"], first_at(50)[0])
ok("m3c", "100+ maps: Kosovo first with two players, Mongolia second", first_at(100)[0] == ["XKX", "MNG"] and first_at(100)[1]["XKX"] == 2, first_at(100)[0])
ok("t1", "14 Danes in the Top 20, Denmark six million people", int(next(r["count"] for r in t3 if r["iso3"] == "DNK")) == 14 and round(pop["DNK"] / 1e6) == 6, "")


for b, c, good, got in checks:
    print(f"{'OK  ' if good else 'FAIL'} [{b}] {c}" + ("" if good else f"   -> {got}"))
print(f"\n{sum(g for *_, g, _ in checks)}/{len(checks)} table checks OK")
print("""
Checked by hand against sources (research/findings_pros.md 'Verified'):
  e3  ropz + broky won Antwerp 2022 with karrigan (DK) .............. Wikipedia PGL Major Antwerp 2022
  m4  MongolZ first Asian team in a CS2 Major final, lost 2-1 to Vitality, ropz on Vitality ... HLTV n/42036, Wikipedia Austin 2025
  t4  Astralis 5 Danes, 4 Majors, only team with 3 in a row, 406 days #1 ... Liquipedia Astralis
  t6  3,067 days, Cologne June 2026, karrigan + TeSeS ................ BLAST.tv / Sheep Esports, Valve roster file
""")
