"""Find kill moments in a broadcast clip by watching the kill feed (top-right) for new entries.

A new kill-feed line changes a band of pixels in the feed area while the rest of the frame does not jump (a camera cut
changes everything at once and is reported separately). Output per clip: candidate kill times, camera-cut times, and
a 0.25 s-step contact sheet around each candidate for checking by eye.

Usage: python find_kills.py C1 [S1 ...]      (reads footage/clips/<id>.mp4)
"""
import json, pathlib, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).parent.parent
FF = r"EDIT_ME\ffmpeg\bin\ffmpeg.exe"
FPS = 10
SW, SH = 480, 270                                   # analysis size (1/4 of 1080p)
FEED = (370, 14, 480, 80)                           # kill-feed box in analysis pixels (x0, y0, x1, y1) ≈ 1480–1920 × 56–320


def frames(path):
    p = subprocess.Popen([FF, "-v", "error", "-i", str(path), "-vf", f"fps={FPS},scale={SW}:{SH}", "-f", "rawvideo",
                          "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(SW * SH)
        if len(b) < SW * SH:
            break
        yield np.frombuffer(b, np.uint8).reshape(SH, SW).astype(np.int16)


def scan(cid):
    path = ROOT / "footage" / "clips" / f"{cid}.mp4"
    prev, feed_d, full_d = None, [], []
    for f in frames(path):
        if prev is not None:
            x0, y0, x1, y1 = FEED
            feed_d.append(float((np.abs(f[y0:y1, x0:x1] - prev[y0:y1, x0:x1]) > 40).mean()))
            full_d.append(float(np.abs(f - prev).mean()))
        prev = f
    feed_d, full_d = np.array(feed_d), np.array(full_d)
    cuts = [round((i + 1) / FPS, 1) for i in np.where(full_d > 28)[0]]
    kills = []
    for i in range(1, len(feed_d) - 1):
        t = (i + 1) / FPS
        if full_d[i] > 18 or any(abs(t - c) < 0.35 for c in cuts):
            continue
        if feed_d[i] > 0.035 and feed_d[i] >= feed_d[i - 1] and feed_d[i] >= feed_d[i + 1]:
            if not kills or t - kills[-1] > 0.4:
                kills.append(round(t, 1))
    return path, kills, cuts


def sheet(path, cid, kills):
    font = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 16)
    tiles = []
    for k in kills:
        for dt in (-0.5, -0.25, 0.0, 0.25):
            t = max(k + dt, 0)
            raw = subprocess.run([FF, "-v", "error", "-ss", f"{t:.2f}", "-i", str(path), "-frames:v", "1", "-vf",
                                  "scale=384:216", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
            im = Image.frombytes("RGB", (384, 216), raw)
            d = ImageDraw.Draw(im)
            d.rectangle([0, 0, 64, 20], fill="black")
            d.text((3, 1), f"{t:.2f}", font=font, fill="yellow" if dt == 0 else "white")
            tiles.append(im)
    if not tiles:
        return None
    out = Image.new("RGB", (384 * 4, 216 * len(kills)))
    for i, im in enumerate(tiles):
        out.paste(im, ((i % 4) * 384, (i // 4) * 216))
    p = ROOT / "work" / "killsheets" / f"{cid}.jpg"
    p.parent.mkdir(exist_ok=True)
    out.save(p, quality=80)
    return p


if __name__ == "__main__":
    res = {}
    for cid in [a for a in sys.argv[1:] if not a.startswith("--")]:
        path, kills, cuts = scan(cid)
        res[cid] = {"kills": kills, "cuts": cuts}
        print(f"{cid}: kills {kills}\n     cuts {cuts}", flush=True)
        if "--sheet" in sys.argv:
            sheet(path, cid, kills)
    out = ROOT / "work" / "killsheets" / "candidates.json"
    out.parent.mkdir(exist_ok=True)
    old = json.loads(out.read_text()) if out.exists() else {}
    old.update(res)
    out.write_text(json.dumps(old, indent=1))
