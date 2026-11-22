"""One row of 0.1 s frames per window: python sheet_rows.py <clip> "2.9-3.6,4.0-4.7" [crop x,y,w,h]"""
import pathlib, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
# ---- EDIT ME: ffmpeg path -------------------------------------------------------
# Folder that holds ffmpeg and ffprobe, e.g. r"C:\ffmpeg\bin" or "/usr/bin".
# Leave it as None to use the ffmpeg on your PATH.
FFMPEG_DIR = None
import pathlib, shutil, sys  # noqa: E401,E402


def ffmpeg_dir(d=FFMPEG_DIR):
    found = pathlib.Path(d) if d else (pathlib.Path(shutil.which("ffmpeg")).parent if shutil.which("ffmpeg") else None)
    if not found or not any((found / n).exists() for n in ("ffmpeg", "ffmpeg.exe")):
        sys.exit(f"[ffmpeg] not found. Install ffmpeg, or set FFMPEG_DIR in the EDIT ME block "
                 f"at the top of {pathlib.Path(__file__).name} (now: {d!r}).")
    return found
# ---------------------------------------------------------------------------------
FF = str(ffmpeg_dir() / "ffmpeg")
ROOT = pathlib.Path(__file__).parent.parent
cid, wins = sys.argv[1], [tuple(map(float, w.split("-"))) for w in sys.argv[2].split(",")]
crop = sys.argv[3].split(",") if len(sys.argv) > 3 else None
tw, th = 240, 135
font = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 14)
rows = []
for a, b in wins:
    vf = (f"crop={crop[2]}:{crop[3]}:{crop[0]}:{crop[1]}," if crop else "") + f"fps=10,scale={tw}:{th}"
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{a}", "-i", str(ROOT / "footage" / "clips" / f"{cid}.mp4"), "-t", f"{b - a + 0.01}",
                          "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    n = len(raw) // (tw * th * 3)
    rows.append([(a + i * 0.1, Image.frombytes("RGB", (tw, th), raw[i * tw * th * 3:(i + 1) * tw * th * 3])) for i in range(n)])
cols = max(len(r) for r in rows)
out = Image.new("RGB", (tw * cols, th * len(rows)))
for y, r in enumerate(rows):
    for x, (t, im) in enumerate(r):
        d = ImageDraw.Draw(im); d.rectangle([0, 0, 44, 16], fill="black"); d.text((2, 0), f"{t:.1f}", font=font, fill="yellow")
        out.paste(im, (x * tw, y * th))
p = ROOT / "work" / "killsheets" / f"{cid}_rows.jpg"
out.save(p, quality=80); print(p)
