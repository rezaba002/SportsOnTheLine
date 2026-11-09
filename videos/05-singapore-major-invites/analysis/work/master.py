"""Video 05 final audio: the Remotion render (Brian + sound effects) + one CC0 music bed, sidechain-ducked under the
voice, then a two-pass -14 LUFS / -1.5 dBTP master (same chain as video 04's assemble.py). Also writes chapters.
python master.py v1  ->  drafts/video05_v1.mp4 + drafts/chapters.txt
"""
import json, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
FFB = r"EDIT_ME\ffmpeg\bin"
FF, FFP = FFB + r"\ffmpeg.exe", FFB + r"\ffprobe.exe"
RAW = pathlib.Path(r"D:\Youtube\sotl-graphics\out\video05_raw.mp4")
TL = pathlib.Path(r"D:\Youtube\sotl-graphics\public\data\video05_timeline.json")
MUSIC = pathlib.Path(r"EDIT_ME\sound-library\music\music-tension-soft.mp3")  # CC0, see library/LICENSES.md
MUSIC_DB = -17.0


def run(*args):
    subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", *args], check=True)


def main(ver):
    out_dir = ROOT / "drafts"; out_dir.mkdir(exist_ok=True)
    tmp = HERE / "tmp"; tmp.mkdir(exist_ok=True)
    total = float(subprocess.run([FFP, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(RAW)], capture_output=True, text=True).stdout)
    voice = tmp / "v05_voice.wav"
    run("-i", str(RAW), "-map", "0:a", "-ar", "48000", "-ac", "2", str(voice))
    graph = ";".join([
        f"[1:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{total:.3f},volume={MUSIC_DB}dB,afade=t=in:d=2,afade=t=out:st={total - 3.5:.2f}:d=3.5[m]",
        "[0:a]asplit=2[keep][key]",
        "[m][key]sidechaincompress=threshold=0.04:ratio=5:attack=20:release=400:makeup=1[md]",
        "[keep][md]amix=inputs=2:normalize=0:duration=first[out]"])
    mix = tmp / "v05_mix.wav"
    run("-i", str(voice), "-stream_loop", "-1", "-i", str(MUSIC), "-filter_complex", graph, "-map", "[out]", "-ar", "48000", str(mix))
    stats = subprocess.run([FF, "-v", "info", "-i", str(mix), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    js = json.loads(stats[stats.rindex("{"):stats.rindex("}") + 1])
    master = tmp / "v05_master.wav"
    run("-i", str(mix), "-af", f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
        f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true", "-ar", "48000", str(master))
    out = out_dir / f"video05_{ver}.mp4"
    run("-i", str(RAW), "-i", str(master), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", str(out))
    # chapters from the timeline (first segment of each part)
    tl = json.loads(TL.read_text(encoding="utf-8"))
    marks = [("00:00", "32 teams, one ranking")]
    for seg in tl["segments"]:
        b = seg.get("banner")
        if b:
            m, s = divmod(int(seg["from"] / tl["fps"]), 60)
            marks.append((f"{m:02d}:{s:02d}", b["title"].title()))
        if seg["kind"] == "page" and seg["page"] == "ranking":
            m, s = divmod(int(seg["from"] / tl["fps"]), 60)
            marks.append((f"{m:02d}:{s:02d}", "How the invites work"))
        if seg["kind"] == "page" and seg["page"] == "field":
            m, s = divmod(int(seg["from"] / tl["fps"]), 60)
            marks.append((f"{m:02d}:{s:02d}", "The field"))
    (out_dir / "chapters.txt").write_text("\n".join(f"{t} {n}" for t, n in marks) + "\n", encoding="utf-8")
    loud = subprocess.run([FF, "-hide_banner", "-i", str(out), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    summary = [l.strip() for l in loud.splitlines() if l.strip().startswith(("I:", "Peak:"))][-2:]
    print(out, f"{total:.1f}s", summary)
    print("\n".join(f"{t} {n}" for t, n in marks))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "v1")
