"""Rough preview cut: every section and highlight in running order, plain cuts, no music bed -> drafts/preview_v0.mp4"""
import pathlib, subprocess
ROOT = pathlib.Path(__file__).parent.parent
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
ORDER = ["s00", "s01", "s02", "s03", "s04", "s05", "s06", "s07",
         "c1a", "C6", "C1", "c1b", "c2a", "S1", "S5", "S3", "c2b", "c3a", "A4", "A3", "A2", "c3b",
         "c4a", "B4", "B1", "B5", "c4b", "c5a", "K1", "K8", "K2", "c5b", "a00", "a01", "a02", "a03"]
paths = [(ROOT / "work" / "highlights" / f"{x}.mp4") if x[0].isupper() else (ROOT / "clips" / f"{x}.mp4") for x in ORDER]
missing = [str(p) for p in paths if not p.exists()]
if missing:
    raise SystemExit("missing: " + ", ".join(missing))
args, filt = [FF, "-v", "error", "-y"], []
for i, p in enumerate(paths):
    args += ["-i", str(p)]
    filt.append(f"[{i}:v]fps=30,scale=1920:1080,setsar=1,format=yuv420p[v{i}];[{i}:a]aresample=48000,aformat=channel_layouts=stereo[a{i}]")
filt.append("".join(f"[v{i}][a{i}]" for i in range(len(paths))) + f"concat=n={len(paths)}:v=1:a=1[v][a]")
out = ROOT / "drafts" / "preview_v0.mp4"
out.parent.mkdir(exist_ok=True)
subprocess.run(args + ["-filter_complex", ";".join(filt), "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast",
                       "-crf", "21", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)], check=True)
print(out)
