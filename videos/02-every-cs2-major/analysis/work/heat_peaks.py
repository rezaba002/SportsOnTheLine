"""Rank "most replayed" peaks per Major from footage/meta/*.json and tie each to its match and map (via results.json).

A peak = a heatmap segment that is a local maximum and stands clear of the VOD's median. The first and last 3% of a VOD
are ignored (intros, outros). Output: research/heat_peaks.md
"""
import json, pathlib, re, statistics

ROOT = pathlib.Path(__file__).parent.parent
res = json.load(open(ROOT / "research" / "results.json", encoding="utf-8"))
NAMES = {"cph24": "Copenhagen 2024", "sha24": "Shanghai 2024", "aus25": "Austin 2025", "bud25": "Budapest 2025", "col26": "Cologne 2026"}


def hms(s):
    s = int(s)
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"


def where(vid, t, major):
    """(match label, map, map score) for VOD time t: the last map whose VOD start is <= t."""
    best = None
    for m in res[major]:
        for mp in m["maps"]:
            v = re.search(r"(?:youtu\.be/|v=)([\w-]{11})(?:[?&]t=(\d+))?", mp.get("vod") or "")
            if v and v.group(1) == vid:
                st = int(v.group(2) or 0)
                if st <= t and (best is None or st >= best[0]):
                    best = (st, f"{m['round']} {' v '.join(m['teams'])}", mp["map"], "-".join(map(str, mp["score"])) + (" OT" if mp["overtime"] else ""))
    return best[1:] if best else ("before first map", "-", "-")


lines = ["# Most-replayed peaks per Major (YouTube heatmap)\n",
         "value = YouTube's replay intensity (1.0 = the most replayed moment of that VOD); ratio = value / VOD median.\n"]
for major in NAMES:
    vids = []
    for m in res[major]:
        for mp in m["maps"]:
            v = re.search(r"(?:youtu\.be/|v=)([\w-]{11})", mp.get("vod") or "")
            if v and v.group(1) not in vids:
                vids.append(v.group(1))
    peaks = []
    for vid in vids:
        p = ROOT / "footage" / "meta" / f"{vid}.json"
        if not p.exists():
            continue
        j = json.loads(p.read_text(encoding="utf-8"))
        hm = j.get("heatmap") or []
        if not hm:
            continue
        vals = [h["value"] for h in hm]
        med = statistics.median(vals) or 1e-3
        dur = j["duration"]
        for i, h in enumerate(hm):
            if h["start_time"] < 0.03 * dur or h["end_time"] > 0.97 * dur:
                continue
            if vals[i] >= max(vals[max(0, i - 2):i + 3]) and vals[i] / med >= 1.6:
                mt, mp, sc = where(vid, h["start_time"], major)
                if mt == "before first map":
                    continue                       # pre-show, ceremonies, showmatches
                ch = [c["title"] for c in (j.get("chapters") or []) if c["start_time"] <= h["end_time"] and c["end_time"] >= h["start_time"]]
                peaks.append((vals[i] / med, h["value"], vid, h["start_time"], h["end_time"], mt, mp, sc, " / ".join(ch)[:60]))
    peaks.sort(reverse=True)
    lines.append(f"\n## {NAMES[major]}  ({len([v for v in vids if (ROOT / 'footage' / 'meta' / f'{v}.json').exists() and json.loads((ROOT / 'footage' / 'meta' / f'{v}.json').read_text(encoding='utf-8')).get('heatmap')])} of {len(vids)} VODs have a heatmap)\n")
    lines.append("| # | ratio | value | match | map (score) | VOD | window |\n|---|---|---|---|---|---|---|")
    for k, (ratio, val, vid, a, b, mt, mp, sc, ch) in enumerate(peaks[:10], 1):
        lines.append(f"| {k} | {ratio:.1f} | {val:.2f} | {mt} | {mp} ({sc}) | [{vid}](https://youtu.be/{vid}?t={int(a)}) | {hms(a)}–{hms(b)} | {ch} |")
(ROOT / "research" / "heat_peaks.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
