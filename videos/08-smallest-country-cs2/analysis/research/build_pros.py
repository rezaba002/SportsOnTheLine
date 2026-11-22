# video08 angle B: which country produces the most CS pros per person?
# Three tiers, each divided by World Bank 2024 population. Run: python build_pros.py
import csv, json, re, os

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
OUT = os.path.join(HERE, "tables")
os.makedirs(OUT, exist_ok=True)

wb = json.load(open(os.path.join(RAW, "worldbank_population_2024.json"), encoding="utf8"))[1]
pop = {r["countryiso3code"]: r["value"] for r in wb if r["value"] and r["countryiso3code"]}
iso3_of_iso2 = {r["country"]["id"]: r["countryiso3code"] for r in wb}
name_of = {r["countryiso3code"]: r["country"]["value"] for r in wb}
iso3_of_name = {v: k for k, v in name_of.items()}
NAME_FIX = {"Russian Federation": "RUS", "Russia": "RUS", "Turkey": "TUR", "Türkiye": "TUR", "Kosovo, Republic of": "XKX",
            "Kosovo": "XKX", "Czech Republic": "CZE", "Czechia": "CZE", "Slovakia": "SVK", "Hong Kong": "HKG",
            "Iran": "IRN", "Iran, Islamic Republic of": "IRN", "Palestine": "PSE", "Palestine, State of": "PSE",
            "Kyrgyzstan": "KGZ", "Egypt": "EGY", "Venezuela": "VEN", "Moldova, Republic of": "MDA",
            "Korea, Republic of": "KOR", "Vietnam": "VNM"}  # Taiwan has no World Bank row
ISO2_FIX = {"xk": "XKX", "uk": "GBR"}

def iso(name):
    return NAME_FIX.get(name) or iso3_of_name.get(name, "")

def per_million(counts, min_pop=1e6):
    rows = []
    for k, n in counts.items():
        p = pop.get(k)
        if not p: continue
        rows.append([k, name_of.get(k, k), n, p, round(n / p * 1e6, 3)])
    big = [r for r in rows if r[3] >= min_pop]
    return sorted(rows, key=lambda r: -r[2]), sorted(big, key=lambda r: -r[4])

def write(name, rows):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf8") as f:
        w = csv.writer(f); w.writerow(["iso3", "country", "count", "population_2024", "per_million"]); w.writerows(rows)

tiers = {}

# Tier 1 — anyone with CS2 prize money (Esports Earnings, 2022-03-30..2026-11-01)
e = open(os.path.join(RAW, "esportsearnings_cs2_countries.html"), encoding="utf8", errors="ignore").read()
et = re.sub(r"\s+", " ", re.sub("<[^>]+>", " | ", e))
t1 = {iso(c.strip()): int(n) for _, c, _, n in re.findall(r"(\d+)\. \|(?: \|)* ([^|$]+?) \| \| \| \$([\d,\.]+) \| \| (\d+) Players", et)}
tiers["1_any_prize_money"] = t1

# Tier 2 — players in S/A-tier events this season (Bettrails, 420 players)
b = open(os.path.join(RAW, "bettrails_cs2_countries.html"), encoding="utf8", errors="ignore").read()
b = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", b, flags=re.S)
bt = re.sub(r"(\| )+", "| ", re.sub(r"\s+", " ", re.sub("<[^>]+>", " | ", b)))
bt = bt[bt.find("Most represented"):bt.find("Team analysis")]
t2 = {iso(c.strip()): int(n) for c, n in re.findall(r"\| ([^|]+?) \| (\d+) players", bt)}
tiers["2_s_a_tier_2026"] = t2

# Tier 3 — HLTV Top 20 of the year, 2013-2025 (Liquipedia): unique players and total appearances
top = json.load(open(os.path.join(RAW, "hltv_top20_parsed.json"), encoding="utf8"))
uniq, apps = {}, {}
seen = set()
for yr, ents in top.items():
    if not 2013 <= int(yr) <= 2025: continue
    for x in ents:
        k = ISO2_FIX.get(x["flag"]) or iso3_of_iso2.get(x["flag"].upper(), x["flag"])
        apps[k] = apps.get(k, 0) + 1
        if x["player"] not in seen:
            seen.add(x["player"]); uniq[k] = uniq.get(k, 0) + 1
tiers["3_hltv_top20_unique_2013_2025"] = uniq
tiers["3b_hltv_top20_appearances_2013_2025"] = apps

for name, counts in tiers.items():
    raw, pc = per_million(counts)
    write(f"pros_{name}.csv", pc)
    unmapped = [k for k in counts if k not in pop]
    print(f"\n== {name}  (total {sum(counts.values())}, unmapped {unmapped})")
    print("  raw:        " + ", ".join(f"{r[1]} {r[2]}" for r in raw[:6]))
    print("  per million:" + ", ".join(f" {r[1]} {r[4]}" for r in pc[:8]))
