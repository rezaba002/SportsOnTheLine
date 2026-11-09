"""Team logos from Liquipedia (same source as video 02): dark-mode version when there is one, 400 px wide.

Names come from the daily race files. Liquipedia's API resolves redirects (FUT -> FUT Esports), reads each team's
infobox (|imagedark= else |image=) and returns the file URL. Two to four API calls in total, a few seconds apart.
Output: sotl-graphics/public/logos/<slug>.png + logos.json (name -> file, source page, source file).
"""
import json, pathlib, re, time, urllib.parse, urllib.request

DATA = pathlib.Path(r"D:\Youtube\sotl-graphics\public\data")
OUT = pathlib.Path(r"D:\Youtube\sotl-graphics\public\logos")
API = "https://liquipedia.net/counterstrike/api.php"
UA = {"User-Agent": "SportsOnTheLine-research/1.0", "Accept-Encoding": "gzip"}
# VRS names whose Liquipedia page has a different title and no redirect
ALIAS = {"BETBOOM": "BetBoom Team", "FUT": "FUT Esports", "1win": "1win", "THUNDER dOWNUNDER": "THUNDERdOWNUNDER",
         "5star": "5star eSports", "9z": "9z Team", "BC.Game": "BC.Game Esports", "DENDELE": "DENDELE CS",
         "Ground Zero": "Ground Zero Gaming", "Imperial": "Imperial Esports", "Inner Circle": "Inner Circle Esports",
         "Sashi": "Sashi Esport", "paiN": "PaiN Gaming", "Aurora": "Aurora Gaming", "Spirit": "Team Spirit",
         "Sangal": "Sangal Esports", "PURE": "PURE (Kazakh team)", "Isurus": "Isurus Gaming"}


def api(params):
    import gzip
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode({**params, "format": "json"}), headers=UA)
    with urllib.request.urlopen(req) as r:
        body = r.read()
        if r.headers.get("Content-Encoding") == "gzip":
            body = gzip.decompress(body)
    time.sleep(3)
    return json.loads(body)


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


# race teams + the opponents named on the video-05 cards
EXTRA = ["K27", "Alliance", "Sangal", "PURE", "NAVI Junior", "Isurus", "The Audacity", "Metizport", "The Huns",
         "Iberian Soul", "Roman Imperium", "SportsBetExpert"]
names = sorted({n for k in ("eu", "am", "as") for n in json.loads((DATA / f"vrs_daily_{k}.json").read_text(encoding="utf-8"))["teams"]} | set(EXTRA))
titles = {n: ALIAS.get(n, n) for n in names}

# 1) team pages (with redirects) -> infobox image
pages = {}
for chunk in [list(titles.values())[i:i + 50] for i in range(0, len(titles), 50)]:
    res = api({"action": "query", "prop": "revisions", "rvprop": "content", "rvslots": "main", "redirects": 1,
               "titles": "|".join(chunk)})["query"]
    redirect = {r["from"]: r["to"] for r in res.get("redirects", []) + res.get("normalized", [])}
    for p in res["pages"].values():
        text = p.get("revisions", [{}])[0].get("slots", {}).get("main", {}).get("*", "")
        dark = re.search(r"\|\s*imagedark\s*=\s*([^\n|]+)", text)
        light = re.search(r"\|\s*image\s*=\s*([^\n|]+)", text)
        pages[p["title"]] = (dark or light).group(1).strip() if (dark or light) else None
    for src, dst in redirect.items():
        pages.setdefault(src, None)
        pages[src] = pages.get(dst) or pages[src]
        for n, t in titles.items():
            if t == src:
                titles[n] = dst

files = {n: pages.get(t) for n, t in titles.items()}
missing = [n for n, f in files.items() if not f]

# 2) file URLs, 400 px wide
want = sorted({f for f in files.values() if f})
urls = {}
for chunk in [want[i:i + 50] for i in range(0, len(want), 50)]:
    res = api({"action": "query", "prop": "imageinfo", "iiprop": "url", "iiurlwidth": 400,
               "titles": "|".join("File:" + f for f in chunk)})["query"]
    norm = {r["to"]: r["from"] for r in res.get("normalized", [])}
    for p in res["pages"].values():
        if "imageinfo" in p:
            urls[norm.get(p["title"], p["title"])[5:]] = p["imageinfo"][0].get("thumburl") or p["imageinfo"][0]["url"]

# 3) download
OUT.mkdir(parents=True, exist_ok=True)
index = {}
for n, f in files.items():
    if not f or f not in urls:
        continue
    req = urllib.request.Request(urls[f], headers={"User-Agent": UA["User-Agent"]})
    (OUT / f"{slug(n)}.png").write_bytes(urllib.request.urlopen(req).read())
    index[n] = {"file": f"logos/{slug(n)}.png", "page": titles[n], "source": f}
    time.sleep(1)
(OUT / "logos.json").write_text(json.dumps(index, indent=1), encoding="utf-8")
print(len(index), "of", len(names), "logos saved")
print("no logo found:", missing + [n for n, f in files.items() if f and f not in urls])
