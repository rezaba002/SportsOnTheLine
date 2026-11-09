"""Fetch YouTube metadata (title, duration, chapters, "most replayed" heatmap) for every playoff VOD in results.json.

Metadata only, no video. Output: footage/meta/{vod_id}.json (skipped if already there).
"""
import json, pathlib, re, subprocess, sys, time

ROOT = pathlib.Path(__file__).parent.parent
OUT = ROOT / "footage" / "meta"
# ---- EDIT ME: network proxy ----------------------------------------------------
# I reach YouTube / Twitch / Edge TTS through a local proxy. If you need one too, put
# its URL here, e.g. "http://127.0.0.1:8080". Leave it as None to connect directly.
PROXY = None


def network_hint(what):
    print(f"\n[network] {what} failed. If your connection needs a proxy, set PROXY in the "
          f"EDIT ME block at the top of {pathlib.Path(__file__).name} (now: {PROXY!r}).", file=sys.stderr)
# ---------------------------------------------------------------------------------

ids = []
for major, matches in json.load(open(ROOT / "research" / "results.json", encoding="utf-8")).items():
    for m in matches:
        for mp in m["maps"]:
            v = re.search(r"youtu\.be/([\w-]{11})", mp.get("vod") or "")
            if v and v.group(1) not in ids:
                ids.append(v.group(1))
print(len(ids), "VODs", flush=True)
for i, vid in enumerate(ids, 1):
    path = OUT / f"{vid}.json"
    if path.exists():
        continue
    for attempt in range(3):
        r = subprocess.run([sys.executable, "-m", "yt_dlp", *(["--proxy", PROXY] if PROXY else []), "--js-runtimes", "node", "-J", "--skip-download",
                            f"https://www.youtube.com/watch?v={vid}"], capture_output=True, text=True, encoding="utf-8")
        if r.returncode == 0:
            j = json.loads(r.stdout)
            keep = {k: j.get(k) for k in ("id", "title", "duration", "chapters", "heatmap", "view_count", "upload_date", "channel")}
            path.write_text(json.dumps(keep, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"{i:>2} {vid} {keep['title'][:70]}  heatmap={'yes' if keep['heatmap'] else 'NO'}", flush=True)
            break
        time.sleep(5 * (attempt + 1))
    else:
        print(f"{i:>2} {vid} FAILED: {r.stderr.strip()[-200:]}", flush=True)
        network_hint("yt-dlp")
    time.sleep(2)
