"""Assemble video 03 from the section clips: whip transitions, one continuous music bed ducked under the voice,
then a -14 LUFS master.

Order: opener (option B) -> cold open -> S01..S10. Clips must be rendered with NO_MUSIC=1 (voice + sfx only).
Joins: 0.2 s xfade (alternating slide left/right) + a whoosh. Music: music_bed.wav, sidechain-ducked by the
voice+sfx, faded out before the ident. Output: drafts/video03_<ver>.mp4 + drafts/chapters.txt

Usage: python assemble.py v2
"""
import json, pathlib, subprocess, sys

from engine import FFMPEG, FFPROBE, SFX_LIB

HERE = pathlib.Path(__file__).parent
CLIPS = HERE.parent / "clips"
OUT = HERE.parent / "drafts"
ORDER = ["s00a_b", "s00", "s01", "s02", "s03", "s04", "s05", "s06", "s07", "s08", "s09", "s10"]
CHAPTERS = {"s00a_b": "Are timeouts useless?", "s01": "What a timeout is", "s03": "The coach leaderboard",
            "s04": "The teams without a coach", "s05": "The naive answer", "s06": "It's the money",
            "s07": "The fair fight", "s08": "Luck or skill?", "s09": "The answer + Singapore"}
XF = 0.2                # transition length
MUSIC_DB = -13.5        # measured: ducked bed sits ~12 dB under the voice (v1 was ~20 dB = inaudible)
IDENT_AT = 4.3 + 0.65   # seconds into S10 where the ident starts (comment line + lead)


def dur(p):
    return float(subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True).stdout)


def run(*a):
    subprocess.run([FFMPEG, "-y", "-v", "error", *a], check=True)


def main(ver):
    OUT.mkdir(exist_ok=True)
    tmp = HERE / "tmp"
    clips = [CLIPS / f"{s}.mp4" for s in ORDER]
    durs = [dur(c) for c in clips]
    # start of each clip on the final timeline (each join overlaps XF seconds)
    starts, t = [], 0.0
    for d in durs:
        starts.append(t)
        t += d - XF
    total = t + XF
    # 1. picture + clip audio with xfade / acrossfade chains
    inputs = []
    for c in clips:
        inputs += ["-i", str(c)]
    vf, af = [], []
    vprev, aprev = "[0:v]", "[0:a]"
    for k in range(1, len(clips)):
        trans = "slideleft" if k % 2 else "slideright"
        off = starts[k]
        vf.append(f"{vprev}[{k}:v]xfade=transition={trans}:duration={XF}:offset={off:.3f}[v{k}]")
        af.append(f"{aprev}[{k}:a]acrossfade=d={XF}:c1=tri:c2=tri[a{k}]")
        vprev, aprev = f"[v{k}]", f"[a{k}]"
    joined_v = tmp / "joined_v.mp4"
    clip_a = tmp / "clip_audio.wav"
    run(*inputs, "-filter_complex", ";".join(vf + af), "-map", vprev, "-map", aprev,
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-tune", "animation", "-pix_fmt", "yuv420p",
        "-c:a", "pcm_s16le", "-ar", "48000", str(joined_v.with_suffix(".mkv")))
    run("-i", str(joined_v.with_suffix(".mkv")), "-map", "0:a", str(clip_a))
    # 2. whooshes on the joins + music bed ducked by voice/sfx, faded before the ident
    whoosh = SFX_LIB / "sfx" / "whoosh-short.wav"
    w_in, w_f, w_lab = [], [], []
    for k in range(1, len(clips)):
        i = 2 + len(w_in) // 2
        w_in += ["-i", str(whoosh)]
        dms = int(max(0.0, starts[k] - 0.12) * 1000)
        w_f.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={dms}|{dms},volume=-7dB[w{k}]")
        w_lab.append(f"[w{k}]")
    fade_at = total - 3.0                    # keep the bed under the ident (ducked by it) and the end screen
    mix = tmp / "mix.wav"
    graph = ";".join(w_f + [
        "[0:a]" + "".join(w_lab) + f"amix=inputs={1 + len(w_lab)}:normalize=0:duration=first[fx]",
        f"[1:a]atrim=0:{total:.3f},volume={MUSIC_DB}dB,afade=t=in:d=1.0,afade=t=out:st={fade_at:.2f}:d=3.0[m]",
        "[fx]asplit=2[keep][key]",
        "[m][key]sidechaincompress=threshold=0.05:ratio=3:attack=30:release=400:makeup=1[md]",
        "[keep][md]amix=inputs=2:normalize=0:duration=first[out]"])
    run("-i", str(clip_a), "-i", str(HERE / "music_bed.wav"), *w_in, "-filter_complex", graph,
        "-map", "[out]", "-ar", "48000", str(mix))
    # 3. loudness: two-pass loudnorm to -14 LUFS / -1 dBTP
    stats = subprocess.run([FFMPEG, "-v", "info", "-i", str(mix), "-af",
                            "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    js = json.loads(stats[stats.rindex("{"):stats.rindex("}") + 1])
    master = tmp / "master.wav"
    run("-i", str(mix), "-af",
        f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:"
        f"measured_LRA={js['input_lra']}:measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true",
        "-ar", "48000", str(master))
    out = OUT / f"video03_{ver}.mp4"
    run("-i", str(joined_v.with_suffix(".mkv")), "-i", str(master), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
        "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", str(out))
    lines = []
    for s, name in CHAPTERS.items():
        m, sec = divmod(int(starts[ORDER.index(s)]), 60)
        lines.append(f"{m:02d}:{sec:02d} {name}")
    (OUT / "chapters.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{out}  {total:.1f}s ({total / 60:.2f} min)")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "v2")
