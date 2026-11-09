"""Twitch metadata (views, duration, date, best height) for every HLTV highlight clip; cached per clip.

Reads research/hltv_highlights/pass*.json (match id -> {teams, hl: [[slug, label], ...]}), writes
research/hltv_highlights/clips_meta.json {slug: {...}}. Metadata only, no video.
"""
import json, pathlib, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

# ---- EDIT ME: network proxy ----------------------------------------------------
# I reach YouTube / Twitch / Edge TTS through a local proxy. If you need one too, put
# its URL here, e.g. "http://127.0.0.1:8080". Leave it as None to connect directly.
PROXY = None


def network_hint(what):
    print(f"\n[network] {what} failed. If your connection needs a proxy, set PROXY in the "
          f"EDIT ME block at the top of {pathlib.Path(__file__).name} (now: {PROXY!r}).", file=sys.stderr)
# ---------------------------------------------------------------------------------


D = pathlib.Path(__file__).parent.parent / "research" / "hltv_highlights"
cache_p = D / "clips_meta.json"
cache = json.loads(cache_p.read_text(encoding="utf-8")) if cache_p.exists() else {}
slugs = set()
for p in sorted(D.glob("pass*.json")):
    for mid, m in json.loads(p.read_text(encoding="utf-8")).items():
        for slug, label in m["hl"]:
            slugs.add(slug)
todo = [s for s in slugs if s not in cache]
print(len(slugs), "clips,", len(todo), "to fetch", flush=True)

def meta(slug):
    for attempt in range(3):
        r = subprocess.run([sys.executable, "-m", "yt_dlp", *(["--proxy", PROXY] if PROXY else []), "-J", f"https://clips.twitch.tv/{slug}"],
                           capture_output=True, text=True, encoding="utf-8")
        if r.returncode == 0:
            j = json.loads(r.stdout)
            return slug, {"views": j.get("view_count"), "dur": j.get("duration"), "date": j.get("upload_date"),
                          "title": j.get("title"), "maxh": max([f.get("height") or 0 for f in j.get("formats", []) if "portrait" not in (f.get("format_id") or "")] or [0])}
        time.sleep(3)
    return slug, {"error": r.stderr.strip()[-200:]}

with ThreadPoolExecutor(4) as ex:
    for i, (slug, m) in enumerate(ex.map(meta, todo), 1):
        cache[slug] = m
        if i % 20 == 0:
            cache_p.write_text(json.dumps(cache, ensure_ascii=False, indent=0), encoding="utf-8")
            print(i, "done", flush=True)
cache_p.write_text(json.dumps(cache, ensure_ascii=False, indent=0), encoding="utf-8")
errors = sum(1 for m in cache.values() if "error" in m)
print("errors:", errors)
if errors:
    network_hint(f"{errors} clip lookups")
