"""Assemble cut v2: sections + highlights in running order, hard cuts, per-clip loudness match, one music bed
sidechain-ducked under voice/casters, transition sounds only into chapter cards, -14 LUFS master.
python assemble_v2.py v1  ->  drafts/video02_v1.mp4 + drafts/chapters_v2.txt"""
import json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent
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
FF, FFP = FFB + r"\ffmpeg.exe", FFB + r"\ffprobe.exe"
# EDIT ME: sound library. My CC0 sound effects and music are not in this repo; point this at your own folder with the same file names.
LIB = pathlib.Path("EDIT_ME/sound-library")
ORDER = ["s00", "s01", "s02", "s03", "s04",
         "c1a", "c1b", "C6", "C1", "c1m", "c2a", "c2b", "S5", "S3", "c2m", "c3a", "c3b", "A3", "A2", "c3m",
         "c4a", "c4b", "B1", "B5", "c4m", "c5a", "c5b", "K1", "K2", "c5m", "a00", "a01", "a02", "a03", "z99"]
CHAP = {"s00": "Five Majors, four champions", "s01": "The big picture", "c1a": "Copenhagen 2024 — NaVi",
        "c2a": "Shanghai 2024 — Spirit", "c3a": "Austin 2025 — Vitality", "c4a": "Budapest 2025 — Vitality again",
        "c5a": "Cologne 2026 — Falcons", "a00": "The all-star teams", "a03": "Your all-star five + Singapore"}
INTO = ["whoosh-long-2s", "send-whoosh-up", "sweep-long", "whoosh-medium-1s", "reverse-cymbal-2s"]   # rotate, never repeat
MUSIC = LIB / "music" / "music-energetic-jazz-funk.mp3"
MUSIC_DB = -15.0
TARGET = -16.0          # per-clip loudness before the master


def path(x):
    return (HERE / "highlights" / f"{x}.mp4") if x[0].isupper() else (ROOT / "clips" / f"{x}.mp4")


def dur(p):
    return float(subprocess.run([FFP, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout)


def lufs(p):
    err = subprocess.run([FF, "-hide_banner", "-i", str(p), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", err)
    return float(m[-1]) if m else TARGET


def run(*a):
    subprocess.run([FF, "-y", "-v", "error", *a], check=True)


def main(ver):
    tmp = HERE / "tmp"; tmp.mkdir(exist_ok=True)
    out_dir = ROOT / "drafts"; out_dir.mkdir(exist_ok=True)
    clips = [path(x) for x in ORDER]
    miss = [str(c) for c in clips if not c.exists()]
    if miss:
        raise SystemExit("missing: " + ", ".join(miss))
    durs = [dur(c) for c in clips]
    gains = [max(-12.0, min(12.0, TARGET - lufs(c))) for c in clips]
    starts, t = [], 0.0
    for d in durs:
        starts.append(t); t += d
    total = t
    args, filt = [], []
    for i, c in enumerate(clips):
        args += ["-i", str(c)]
        filt.append(f"[{i}:v]fps=30,scale=1920:1080,setsar=1,format=yuv420p[v{i}];"
                    f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,volume={gains[i]:.2f}dB[a{i}]")
    filt.append("".join(f"[v{i}][a{i}]" for i in range(len(clips))) + f"concat=n={len(clips)}:v=1:a=1[v][a]")
    joined = tmp / "v2_joined.mkv"
    run(*args, "-filter_complex", ";".join(filt), "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium",
        "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", "-ar", "48000", str(joined))
    clip_a = tmp / "v2_clip_audio.wav"
    run("-i", str(joined), "-map", "0:a", str(clip_a))
    # transition sounds into each chapter card + the all-star intro
    t_in, t_f, t_l = [], [], []
    k = 0
    for i, x in enumerate(ORDER):
        if x in ("c1a", "c2a", "c3a", "c4a", "c5a", "a00"):
            name = INTO[k % len(INTO)]; k += 1
            j = 2 + len(t_in) // 2
            t_in += ["-i", str(LIB / "sfx" / f"{name}.wav")]
            dms = int(max(0.0, starts[i] - 0.35) * 1000)
            t_f.append(f"[{j}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={dms}|{dms},volume=-9dB[t{k}]")
            t_l.append(f"[t{k}]")
    end_music = starts[ORDER.index("z99")] + 1.0
    graph = ";".join(t_f + [
        "[0:a]" + "".join(t_l) + f"amix=inputs={1 + len(t_l)}:normalize=0:duration=first[fx]",
        f"[1:a]atrim=0:{total:.3f},volume={MUSIC_DB}dB,afade=t=in:d=1.5,afade=t=out:st={end_music:.2f}:d=2.5[m]",
        "[fx]asplit=2[keep][key]",
        "[m][key]sidechaincompress=threshold=0.04:ratio=4:attack=25:release=350:makeup=1[md]",
        "[keep][md]amix=inputs=2:normalize=0:duration=first[out]"])
    mix = tmp / "v2_mix.wav"
    run("-i", str(clip_a), "-stream_loop", "-1", "-i", str(MUSIC), *t_in, "-filter_complex", graph, "-map", "[out]", "-ar", "48000", str(mix))
    stats = subprocess.run([FF, "-v", "info", "-i", str(mix), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    js = json.loads(stats[stats.rindex("{"):stats.rindex("}") + 1])
    master = tmp / "v2_master.wav"
    run("-i", str(mix), "-af", f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
        f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true", "-ar", "48000", str(master))
    out = out_dir / f"video02_{ver}.mp4"
    run("-i", str(joined), "-i", str(master), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
        "-movflags", "+faststart", str(out))
    lines = []
    for s, name in CHAP.items():
        m, sec = divmod(int(starts[ORDER.index(s)]), 60)
        lines.append(f"{m:02d}:{sec:02d} {name}")
    lines[0] = "00:00 " + CHAP["s00"]
    (out_dir / "chapters_v2.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{out}  {total:.1f}s ({total / 60:.2f} min)")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "v1")
