"""Pick the caster-audio window for each highlight automatically (the user reviews the picks later).

Window length = the finished highlight's length. Rule: the window must contain the casters' call on the decisive kill
(last kill .. last kill + 3 s); among those windows, pick the one with the most caster/crowd energy (mean loudness above
the clip's median, 0.1 s steps). The chosen window's transcript (faster-whisper small.en) is printed so the pick can be
judged by reading. Writes "caster": {"start": s} into highlights/<id>.json and research/caster_picks.md.

Usage: python caster_pick.py C1 C6 ...
"""
import json, pathlib, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel

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
FF = str(ffmpeg_dir() / "ffmpeg")
SR = 16000


def audio(path):
    raw = subprocess.run([FF, "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32)


def total_of(spec_path):
    sys.path.insert(0, str(HERE))
    import highlight2
    from highlight import build_timeline
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if "auto" in spec:
        spec["shots"] = highlight2.auto_shots(spec)
    return build_timeline(spec)[0], spec


def main():
    model = WhisperModel("small.en", device="cpu", compute_type="int8")
    lines = ["# Caster audio picks (automatic, 2026-10-24) — for the user to confirm or replace\n",
             "Window = finished highlight length; contains the call on the decisive kill; most energy among those.",
             "Times are in the original Twitch clip (footage/clips/<id>.mp4).\n"]
    for cid in sys.argv[1:]:
        sp = HERE / "highlights" / f"{cid}.json"
        total, spec = total_of(sp)
        src = ROOT / spec["source"]
        a = audio(src)
        hop = SR // 10
        db = np.array([20 * np.log10(np.sqrt(np.mean(a[i:i + hop] ** 2)) + 1e-9) for i in range(0, len(a) - hop, hop)])
        excite = np.clip(db - np.median(db), 0, None)
        dur = len(a) / SR
        last = spec["hits"][-1]
        best, best_s = -1, 0.0
        for s in np.arange(0, max(dur - total, 0) + 0.01, 0.1):
            if not (s <= last and s + total >= min(last + 3.0, dur)):
                continue
            score = excite[int(s * 10):int((s + total) * 10)].mean()
            if score > best:
                best, best_s = score, float(s)
        if best < 0:                                 # clip too short around the kill: end on the clip's end
            best_s = max(dur - total, 0.0)
        segs, _ = model.transcribe(str(src), word_timestamps=True, beam_size=5)
        words = [w for sg in segs for w in sg.words if best_s <= w.start <= best_s + total]
        text = " ".join(w.word.strip() for w in words) or "(no clear words: crowd / shouting)"
        spec_raw = json.loads(sp.read_text(encoding="utf-8"))
        spec_raw["caster"] = {"start": round(best_s, 1)}
        sp.write_text(json.dumps(spec_raw, ensure_ascii=False, indent=1), encoding="utf-8")
        mm = lambda x: f"{int(x // 60)}:{x % 60:04.1f}"
        lines.append(f"- **{cid}** ({total:.1f} s): {mm(best_s)} – {mm(best_s + total)}  ·  \"{text}\"")
        print(lines[-1], flush=True)
    out = ROOT / "research" / "caster_picks.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
