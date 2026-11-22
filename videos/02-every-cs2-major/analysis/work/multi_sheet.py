"""One row per clip, n frames each: python multi_sheet.py out.jpg n clip1.mp4 clip2.mp4 ..."""
import subprocess, sys
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
FFB = str(ffmpeg_dir())
out, n, paths = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
font = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 16)
tw, th = 400, 225
img = Image.new("RGB", (tw * n, th * len(paths)))
for r, p in enumerate(paths):
    dur = float(subprocess.run([FFB + r"\ffprobe.exe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)
    for k in range(n):
        t = dur * (k + 0.6) / n
        raw = subprocess.run([FFB + r"\ffmpeg.exe", "-v", "error", "-ss", f"{t:.2f}", "-i", p, "-frames:v", "1", "-vf", f"scale={tw}:{th}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        im = Image.frombytes("RGB", (tw, th), raw); d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 92, 20], fill="magenta"); d.text((3, 1), f"{p.split('/')[-1][:4]} {t:.1f}", font=font, fill="white")
        img.paste(im, (k * tw, r * th))
img.save(out, quality=78); print(out)
