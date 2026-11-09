"""Multi-part section renderer for video 04: narration blocks and footage clips placed one after another.

segments: list of dicts
  {"nar": "h01", "gap": 0.15}                       Brian block (narration/<id>.mp3), then a gap
  {"clip": "donk", "src": path, "in": a, "out": b, "gain": dB, "gap": 0.1}   footage with its own audio
Builds a schedule {name: (start, end)} and calls draw(img, t, sch). Audio = narration + clip audio + sfx.
Captions: Brian's words (engine style), clip lines are drawn by the section itself.
"""
import os, pathlib, re, subprocess
from engine import (W, H, FPS, FFMPEG, NAR, NAR_DIR, HERE, CLIPS, canvas, chunks, styled, ass_time, sfx_path)

FF = FFMPEG


def schedule(segments, lead=0.1):
    t, sch = lead, {}
    for s in segments:
        if "nar" in s:
            d = NAR[s["nar"]]["duration"]
            sch[s["nar"]] = (t, t + d)
        else:
            d = (s["out"] - s["in"]) / s.get("speed", 1.0)
            sch[s["clip"]] = (t, t + d)
        t += d + s.get("gap", 0.15)
    return sch, t


def captions(segments, sch, path, style="Low"):
    lines = []
    for s in segments:
        if "nar" not in s:
            continue
        off = sch[s["nar"]][0]
        ws = [(w["w"], w["s"] + off, w["e"] + off) for w in NAR[s["nar"]]["words"]]
        sent = []
        for w in ws:
            sent.append(w)
            if re.search(r"[.?!…]$", w[0]):
                lines += chunks(sent); sent = []
        if sent:
            lines += chunks(sent)
    ev = []
    for k, ln in enumerate(lines):
        a, b = ln[0][1], max(ln[-1][2], ln[0][1] + 0.6)
        if k + 1 < len(lines):
            b = min(b, lines[k + 1][0][1] - 0.02)
        st = style((a + b) / 2) if callable(style) else style
        ev.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},{st},,0,0,0,,{styled(' '.join(x[0] for x in ln))}")
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Low,Arial,54,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,5.5,3.5,2,130,130,46,1
Style: Box,Arial,54,&H00FFFFFF,&H00FFFFFF,&H70000000,&H70000000,1,0,0,0,100,100,0,0,3,9,0,2,130,130,262,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    path.write_text(head + "\n".join(ev) + "\n", encoding="utf-8")


def render(sid, segments, draw, sfx=(), lead=0.1, tail=0.4, caption_style="Low"):
    sch, end = schedule(segments, lead)
    dur = end + tail
    tmp = HERE / "tmp"; tmp.mkdir(exist_ok=True)
    CLIPS.mkdir(exist_ok=True)
    n = round(dur * FPS)
    video = tmp / f"{sid}_v.mp4"
    proc = subprocess.Popen([FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                             "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", str(video)],
                            stdin=subprocess.PIPE)
    for f in range(n):
        img = canvas(f)
        img = draw(img, f / FPS, sch) or img
        proc.stdin.write(img.convert("RGB").tobytes())
    proc.stdin.close(); proc.wait()
    # audio: narration + clip audio + sfx
    inputs, filt, labs = [], [], []
    for s in segments:
        i = len(inputs) // 2 if not any(x == "-ss" for x in inputs) else None
        st = sch[s.get("nar") or s["clip"]][0]
        d = int(st * 1000)
        if "nar" in s:
            k = sum(1 for x in inputs if x == "-i")
            inputs += ["-i", str(NAR_DIR / f"{s['nar']}.mp3")]
            filt.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={d}|{d}[n{k}]"); labs.append(f"[n{k}]")
        elif s.get("audio", True):
            k = sum(1 for x in inputs if x == "-i")
            inputs += ["-ss", f"{s['in']:.3f}", "-t", f"{s['out'] - s['in']:.3f}", "-i", str(s["src"])]
            sp = s.get("speed", 1.0)
            tempo = f",atempo={sp}" if sp != 1.0 else ""
            filt.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo{tempo},volume={s.get('gain', 0)}dB,"
                        f"afade=t=in:d=0.04,areverse,afade=t=in:d=0.08,areverse,adelay={d}|{d}[c{k}]"); labs.append(f"[c{k}]")
    for (t_, name, g) in sfx:
        k = sum(1 for x in inputs if x == "-i")
        inputs += ["-i", str(sfx_path(name))]
        d = int(max(0, t_) * 1000)
        filt.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={d}|{d},volume={g}dB[s{k}]"); labs.append(f"[s{k}]")
    filt.append("".join(labs) + f"amix=inputs={len(labs)}:normalize=0:duration=longest,atrim=0:{dur:.3f},apad=whole_dur={dur:.3f}[out]")
    audio = tmp / f"{sid}_a.wav"
    subprocess.run([FF, "-y", "-v", "error", *inputs, "-filter_complex", ";".join(filt), "-map", "[out]", "-c:a", "pcm_s16le", str(audio)], check=True)
    ass = tmp / f"{sid}.ass"
    captions(segments, sch, ass, caption_style)
    out = CLIPS / f"{sid}.mp4"
    subprocess.run([FF, "-y", "-v", "error", "-i", str(video), "-i", str(audio), "-vf", f"subtitles={ass.name}", "-c:v", "libx264",
                    "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)],
                   check=True, cwd=tmp)
    print(f"{sid}: {dur:.1f}s -> {out}")
    return out, sch
