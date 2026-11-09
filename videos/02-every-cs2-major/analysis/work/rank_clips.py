"""Rank HLTV highlight clips per Major by Twitch views; Part 1 (observer) + Part 2 (replay) of one play count as one.

Inputs: research/hltv_highlights/pass9_merged.json, clips_meta.json, research/results.json.
Output: research/hltv_clip_ranking.md
"""
import json, pathlib, re

R = pathlib.Path(__file__).parent.parent / "research"
res = json.load(open(R / "results.json", encoding="utf-8"))
hl = json.load(open(R / "hltv_highlights" / "pass9_merged.json", encoding="utf-8"))
meta = json.load(open(R / "hltv_highlights" / "clips_meta.json", encoding="utf-8"))
NAMES = {"cph24": "Copenhagen 2024", "sha24": "Shanghai 2024", "aus25": "Austin 2025", "bud25": "Budapest 2025", "col26": "Cologne 2026"}
TEAM = {"navi": "NaVi", "vit": "Vitality", "faze": "FaZe", "g2": "G2", "mouz": "MOUZ", "spirit": "Spirit", "tl": "Liquid", "heroic": "HEROIC",
        "mongolz": "MongolZ", "pain": "paiN", "furia": "FURIA", "falcons": "Falcons", "aurora": "Aurora", "betboom": "BetBoom", "9z": "9z",
        "c9": "Cloud9", "ef": "Eternal Fire", "cloud9": "Cloud9", "eternalfire": "Eternal Fire", "eternal fire": "Eternal Fire"}

lines = ["# HLTV highlight clips ranked by Twitch views (2026-10-18)\n",
         "Every clip listed under 'Highlights' on HLTV's page for each playoff match (Twitch clips by the 'cshighlights' channel,",
         "up to 60 s, 1080p, caster audio included). Views = Twitch view count. A play split into 'Part 1 - observer' and",
         "'Part 2 - REPLAY' is one row with both links; its views are the sum. M2R11 = map 2, round 11.\n"]
for major, matches in res.items():
    plays = []
    for m in matches:
        h = hl.get(m["hltv"])
        if not h:
            continue
        maps = [mp["map"] for mp in m["maps"]]
        teams = " – ".join(TEAM.get(t, t) for t in m["teams"])
        groups = {}
        for slug, label in h["hl"]:
            key = re.sub(r"\s*[-(]\s*Part \d.*$", "", label).strip(" -(")
            g = groups.setdefault(key, {"label": key, "clips": [], "views": 0})
            v = (meta.get(slug) or {}).get("views") or 0
            part = "replay" if re.search(r"REPLAY", label, re.I) and re.search(r"Part 2", label, re.I) else ""
            g["clips"].append((slug, v, part, (meta.get(slug) or {}).get("dur")))
            g["views"] += v
        for g in groups.values():
            mm = re.match(r"M(\d)(?:R(\d+))?", g["label"])
            mapname = maps[int(mm.group(1)) - 1] if mm and int(mm.group(1)) <= len(maps) else "?"
            plays.append((g["views"], m["round"], teams, mapname, g))
    plays.sort(key=lambda p: -p[0])
    lines.append(f"\n## {NAMES[major]}  ({len(plays)} plays)\n")
    lines.append("| # | views | match | map | play | clip(s) |\n|---|---|---|---|---|---|")
    for i, (views, rnd, teams, mapname, g) in enumerate(plays[:12], 1):
        links = " · ".join(f"[{'replay' if part else ('part ' + str(k + 1) if len(g['clips']) > 1 else 'clip')} {d or '?'}s]"
                           f"(https://clips.twitch.tv/{s})" for k, (s, v, part, d) in enumerate(g["clips"]))
        lab = g["label"].split("|", 1)
        play = (lab[0].strip() + " · " + lab[1].strip()) if len(lab) == 2 else g["label"]
        lines.append(f"| {major[:1].upper() if major != 'col26' else 'K'}{i} | {views:,} | {rnd} {teams} | {mapname} | {play[:110]} | {links} |")
(R / "hltv_clip_ranking.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
