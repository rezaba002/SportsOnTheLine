# Builds the video08 comparison tables from the raw downloads in ./raw
# Run: python build.py  -> writes ./tables/*.csv and prints the headline rankings
import csv, json, re, os

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
OUT = os.path.join(HERE, "tables")
os.makedirs(OUT, exist_ok=True)

# --- population (World Bank 2024) ---
wb = json.load(open(os.path.join(RAW, "worldbank_population_2024.json"), encoding="utf8"))[1]
pop = {r["countryiso3code"]: r["value"] for r in wb if r["value"] and r["countryiso3code"]}
name_of = {r["countryiso3code"]: r["country"]["value"] for r in wb}

def write(name, header, rows):
    with open(os.path.join(OUT, name), "w", newline="", encoding="utf8") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)

# --- 1. Steam download traffic per country (all of Steam, not CS2-only) ---
s = open(os.path.join(RAW, "steam_download_traffic_per_country.jsonp"), encoding="utf8").read()
d = json.loads(s[s.index("(") + 1 : s.rindex(")")])
traffic = {k: int(v["totalbytes"]) for k, v in d.items() if "-" not in k}  # drop US states
total = sum(traffic.values())
rows = []
for iso, b in sorted(traffic.items(), key=lambda kv: -kv[1]):
    share = b / total * 100
    p = pop.get(iso)
    rows.append([iso, name_of.get(iso, iso), round(share, 3), p, round(b / p / 1e9, 2) if p else ""])
write("steam_traffic_by_country.csv", ["iso3", "country", "share_pct", "population_2024", "GB_per_person"], rows)
traffic_rows = rows

# --- 2. Steam Hardware Survey language (Oct 2026) ---
h = open(os.path.join(RAW, "steam_hwsurvey.html"), encoding="utf8").read()
i = h.find("Language", 186000)
t = re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", h[i : i + 40000])).replace("&nbsp;", " ")
langs, seen = [], set()
for lang, pct, chg in re.findall(r"([A-Z][A-Za-z\- ]+?)\s+(\d+\.\d+%)\s+([+\-]?\d+\.\d+%)", t):
    lang = lang.replace("Language ", "")
    if lang in seen: break
    seen.add(lang); langs.append([lang, float(pct[:-1]), chg])
langs.sort(key=lambda r: -r[1])
write("steam_survey_language_oct2026.csv", ["language", "share_pct", "change_vs_sep"], langs)

# --- 3. Pro players & prize money by country (Esports Earnings, CS2 2022-03-30 .. 2026-11-01) ---
e = open(os.path.join(RAW, "esportsearnings_cs2_countries.html"), encoding="utf8", errors="ignore").read()
et = re.sub(r"\s+", " ", re.sub("<[^>]+>", " | ", e))
pros = re.findall(r"(\d+)\. \|(?: \|)* ([^|$]+?) \| \| \| \$([\d,\.]+) \| \| (\d+) Players", et)
NAME_FIX = {"Russian Federation": "RUS", "Turkey": "TUR", "Kosovo, Republic of": "XKX", "Czech Republic": "CZE",
            "Slovakia": "SVK", "Hong Kong": "HKG", "Korea, Republic of": "KOR", "Iran": "IRN", "Vietnam": "VNM"}
iso_by_name = {v: k for k, v in name_of.items()}
prow = []
for rank, country, money, n in pros:
    country = country.strip()
    iso = NAME_FIX.get(country) or iso_by_name.get(country, "")
    p = pop.get(iso)
    prow.append([int(rank), country, iso, float(money.replace(",", "")), int(n), p, round(int(n) / p * 1e6, 2) if p else ""])
write("pros_by_country_esportsearnings.csv", ["rank", "country", "iso3", "prize_usd", "players", "population_2024", "pros_per_million"], prow)

# --- 4/5. Small published figures, entered by hand (see SOURCES.md) ---
write("leetify_playerbase_share.csv", ["country", "share_pct", "note"], [
    ["Russia", 11.51, "Leetify, CS:GO matchmaking, data from 2022 (via skin.club)"],
    ["United States", 10.71, "same"],
    ["Brazil", 5.32, "same"],
])
write("leetify_global_elites_per_million_2021.csv", ["country", "GE_per_million", "note"], [
    ["Finland", 3362, "Leetify, May 2021, 7M+ matchmaking games, European countries"],
    ["Estonia", 2046, "same"],
    ["Denmark", 1867, "same"],
])
write("ewc2026_hours_watched_by_language.csv", ["language", "share_pct"], [
    ["English", 31.6], ["Russian", 26.1], ["Portuguese", 14.7], ["Other (31 languages)", 27.6],
])
write("s_a_tier_pros_by_country_bettrails.csv", ["country", "players"], [
    ["Russia", 49], ["Brazil", 37], ["China", 30], ["Mongolia", 28], ["Ukraine", 28],
    ["Denmark", 24], ["Sweden", 24], ["Poland", 18], ["United States", 17], ["Australia", 16],
])

# --- print headlines ---
print("Steam traffic share, top 10:")
for r in traffic_rows[:10]: print(f"  {r[1]:<22}{r[2]:>6}%")
print("Steam traffic per person (pop > 1M), top 10:")
for r in sorted([r for r in traffic_rows if r[3] and r[3] > 1e6], key=lambda r: -r[4])[:10]:
    print(f"  {r[1]:<22}{r[4]:>8} GB/person")
print("Survey language, top 8:")
for l in langs[:8]: print(f"  {l[0]:<22}{l[1]:>6}%")
print("Pros by count, top 10:")
for r in sorted(prow, key=lambda r: -r[4])[:10]: print(f"  {r[1]:<22}{r[4]:>5}")
print("Pros per million (pop > 1M), top 10:")
for r in sorted([r for r in prow if r[5] and r[5] > 1e6], key=lambda r: -r[6])[:10]:
    print(f"  {r[1]:<22}{r[6]:>7}")
print(f"parsed {len(prow)} pro-country rows, {len(langs)} languages, {len(traffic_rows)} traffic countries")
