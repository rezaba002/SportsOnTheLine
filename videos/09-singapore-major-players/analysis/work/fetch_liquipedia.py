"""Liquipedia team pages (wikitext) for the Major teams -> research/liquipedia/<team>.wiki
Liquipedia allows one action=parse request per 30 s; we wait 31 s."""
import json, os, subprocess, time, urllib.parse
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
f = json.load(open(os.path.join(ROOT, "..", "video06", "research", "field.json"), encoding="utf-8"))
teams = [t["team"] for s in ("stage3", "stage2", "stage1") for t in f[s]]
alias = {"Vitality": "Team Vitality", "Spirit": "Team Spirit", "Falcons": "Team Falcons", "Liquid": "Team Liquid",
         "FaZe": "FaZe Clan", "G2": "G2 Esports", "BETBOOM": "BetBoom Team", "Aurora": "Aurora Gaming",
         "Nemiga": "Nemiga Gaming", "Imperial": "Imperial Esports", "Wildcard": "Wildcard Gaming", "Legacy": "Legacy",
         "FUT": "FUT Esports", "9z": "9z Team", "Lynn Vision": "Lynn Vision Gaming", "BC.Game": "BC.Game Esports"}
for t in teams:
    path = os.path.join(ROOT, "research", "liquipedia", t.replace(" ", "_").replace(".", "") + ".wiki")
    if os.path.exists(path):
        continue
    url = ("https://liquipedia.net/counterstrike/api.php?action=parse&format=json&prop=wikitext&redirects=1&page="
           + urllib.parse.quote(alias.get(t, t)))
    r = subprocess.run(["curl", "-s", "-m", "30", "--compressed", "-A", "SportsOnTheLine-research/1.0", url], capture_output=True)
    try:
        wt = json.loads(r.stdout)["parse"]["wikitext"]["*"]
        open(path, "w", encoding="utf-8").write(wt)
        print(t, "ok", len(wt), flush=True)
    except Exception:
        print(t, "FAILED", r.stdout[:120], flush=True)
    time.sleep(31)
