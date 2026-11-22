"""Highlight renderer for video 02: one JSON spec -> one finished highlight (1920x1080, 30 fps, H.264 + AAC).

A spec lists the info card, then shots cut from a downloaded broadcast clip. Each shot has its own speed (0.5 = slow
motion; the 60 fps source makes 0.5x perfectly smooth at 30 fps out), zoom and zoom centre. "hits" are the kill moments
in source-clip seconds: each one gets a zoom kick, a white flash, a kill pip and an impact sound, wherever it lands.
Shots can also be a "freeze" (holds the last frame with big text) or carry a lower third.

Audio is our own sound effects plus any broadcast audio the user picks by VOD time ("vod_audio": cut with yt-dlp, cached
in footage/audio/). Nothing else from the broadcast is used.

Usage: python highlight.py highlights/col26_magixx.json [--stills]   (--stills: a contact sheet instead of the video)
"""
import functools, json, math, pathlib, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

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
FFB = ffmpeg_dir()
FF, FFPROBE = str(FFB / "ffmpeg.exe"), str(FFB / "ffprobe.exe")
# ---- EDIT ME: network proxy ----------------------------------------------------
# I reach YouTube / Twitch / Edge TTS through a local proxy. If you need one too, put
# its URL here, e.g. "http://127.0.0.1:8080". Leave it as None to connect directly.
PROXY = None


def network_hint(what):
    print(f"\n[network] {what} failed. If your connection needs a proxy, set PROXY in the "
          f"EDIT ME block at the top of {pathlib.Path(__file__).name} (now: {PROXY!r}).", file=sys.stderr)
# ---------------------------------------------------------------------------------
W, H, FPS = 1920, 1080, 30
GOLD, WHITE, MUTED, INK = (232, 190, 60), (245, 243, 238), (170, 170, 178), (10, 10, 12)
GRADE = "eq=contrast=1.07:saturation=1.22:gamma=0.97"


# ---------- drawing helpers ----------
def ease(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


@functools.lru_cache(maxsize=None)
def font(size, style="Bold"):
    f = ImageFont.truetype(r"C:\Windows\Fonts\bahnschrift.ttf", size)
    try:
        f.set_variation_by_name(style)
    except Exception:
        pass
    return f


def text(layer, xy, s, f, fill, alpha=1.0, anchor="la", tracking=0, shadow=True):
    """Text on an RGBA layer, with letter spacing and a soft drop shadow so it reads on footage."""
    if alpha <= 0:
        return
    d = ImageDraw.Draw(layer)
    a = int(255 * min(alpha, 1))
    width = sum(d.textlength(ch, font=f) + tracking for ch in s) - tracking
    x, y = xy
    x -= width / 2 if anchor[0] == "m" else width if anchor[0] == "r" else 0
    for dx, dy, col in ([(4, 5, (0, 0, 0, int(a * 0.6)))] if shadow else []) + [(0, 0, fill + (a,))]:
        cx = x
        for ch in s:
            d.text((cx + dx, y + dy), ch, font=f, fill=col, anchor="l" + anchor[1])
            cx += d.textlength(ch, font=f) + tracking


@functools.lru_cache(maxsize=None)
def vignette():
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    return np.clip(1.12 - 0.32 * r ** 2, 0.6, 1.0)[..., None].astype(np.float32)


def finish(img, flash=0.0, dim=1.0, sat=1.0):
    a = np.asarray(img, dtype=np.float32)
    if sat != 1.0:
        g = a.mean(axis=2, keepdims=True)
        a = g + (a - g) * sat
    a = a * vignette() * dim
    if flash > 0:
        a = a + (255 - a) * flash
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def zoomed(frame, z, c):
    """Crop a 1/z window around centre c (source pixels) and scale it back to full frame."""
    w, h = W / z, H / z
    cx = min(max(c[0], w / 2), W - w / 2)
    cy = min(max(c[1], h / 2), H - h / 2)
    return frame.resize((W, H), Image.BICUBIC, box=(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))


# ---------- source frames ----------
def src_fps(path):
    num, den = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate",
                               "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout.strip().split("/")
    return float(num) / float(den)


def frames_at(path, start, times):
    """Yield graded source frames for each requested source time (sorted), decoding [start, max(times)] once."""
    fps = src_fps(path)
    p = subprocess.Popen([FF, "-v", "error", "-ss", f"{start:.3f}", "-i", str(path), "-t", f"{max(times) - start + 0.2:.3f}",
                          "-vf", f"{GRADE},scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL)
    idx, cur = -1, None
    for t in times:
        want = round((t - start) * fps)
        while idx < want:
            buf = p.stdout.read(W * H * 3)
            if len(buf) < W * H * 3:
                break
            cur, idx = buf, idx + 1
        yield Image.frombytes("RGB", (W, H), cur)
    p.stdout.close(); p.kill()


# ---------- timeline ----------
def build_timeline(spec):
    """Each shot gets out_start/out_dur; each hit gets its output time (or None if it falls in no shot)."""
    t = spec["card"]["dur"]
    for s in spec["shots"]:
        s["out_start"] = t
        s["out_dur"] = s["dur"] if s.get("type") == "freeze" else (s["out"] - s["in"]) / s.get("speed", 1.0)
        t += s["out_dur"]
    hits = []
    for h in spec["hits"]:
        for s in spec["shots"]:
            if s.get("type") != "freeze" and s["in"] <= h < s["out"]:
                hits.append(s["out_start"] + (h - s["in"]) / s.get("speed", 1.0)); break
        else:
            print(f"  note: hit at {h}s is not inside any shot (cut); no effect drawn")
            hits.append(None)
    return t, hits


def hit_fx(t, hits):
    """(zoom kick, white flash) at output time t from the nearest past hit."""
    kick = flash = 0.0
    for h in hits:
        if h is not None and 0 <= t - h < 0.5:
            kick = max(kick, 0.075 * math.exp(-(t - h) / 0.11))
            flash = max(flash, 0.5 * math.exp(-(t - h) / 0.05))
    return kick, flash


@functools.lru_cache(maxsize=None)
def tag_panel():
    """Dark corner gradient under the tag; it also covers the broadcast minimap."""
    yy, xx = np.mgrid[0:480, 0:820]
    a = np.clip(1.25 - np.sqrt((xx / 820) ** 2 + (yy / 480) ** 2), 0, 1) ** 0.8 * 235
    arr = np.zeros((480, 820, 4), np.uint8)
    arr[..., :3] = INK
    arr[..., 3] = a.astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def overlay_pips(img, spec, t, hits):
    """Top-left tag: player + situation, and one pip per kill that fills as the kills land."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    tag = spec["tag"]
    lay.paste(tag_panel(), (0, 0))
    d.rectangle([72, 70, 80, 150], fill=GOLD + (255,))
    text(lay, (100, 72), tag["name"], font(54, "Bold"), WHITE, tracking=2)
    text(lay, (102, 132), tag["sub"], font(28, "SemiBold"), GOLD, tracking=4)
    n = len(hits)
    for i in range(n):
        x = 100 + i * 46
        on = hits[i] is not None and t >= hits[i]
        pop = ease((t - hits[i]) / 0.15) if on else 0
        grow = 6 * (1 - pop) if on else 0
        d.rectangle([x - grow, 178 - grow, x + 34 + grow, 192 + grow], fill=(GOLD if on else (255, 255, 255)) + ((255 if on else 70),))
    img.paste(lay, (0, 0), lay)
    return img


def card_frame(spec, t, bg):
    c = spec["card"]
    img = bg.copy()
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    a = [ease((t - s) / 0.35) for s in (0.05, 0.18, 0.32, 0.45)]
    d = ImageDraw.Draw(lay)
    d.rectangle([200, 330, 200 + 10, 330 + 400 * a[0]], fill=GOLD + (255,))
    text(lay, (240, 330 + 14 * (1 - a[0])), c["kicker"], font(38, "SemiBold"), GOLD, a[0], tracking=6)
    text(lay, (232, 390 + 20 * (1 - a[1])), c["title"], font(200, "Bold"), WHITE, a[1], tracking=4)
    text(lay, (240, 610 + 16 * (1 - a[2])), c["line"], font(66, "SemiBold"), GOLD, a[2], tracking=3)
    text(lay, (242, 690 + 12 * (1 - a[3])), c["sub"], font(40, "SemiLight"), MUTED, a[3], tracking=2)
    img.paste(lay, (0, 0), lay)
    fade = min(1.0, t / 0.2)
    return finish(img, dim=fade)


def freeze_frame(img, s, t):
    """Big two-line stamp over a dimmed, desaturated still that keeps creeping in."""
    z = 1.0 + 0.05 * t / s["dur"]
    img = zoomed(img, z, (W / 2, H / 2))
    img = finish(img, dim=0.5, sat=0.25)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    a1 = ease(t / 0.16)
    f1 = font(int(230 * (1.3 - 0.3 * a1)), "Bold")
    text(lay, (W / 2, 470), s["text"], f1, GOLD, a1, anchor="mm", tracking=8)
    a2 = ease((t - 0.3) / 0.3)
    text(lay, (W / 2, 640 + 14 * (1 - a2)), s["sub"], font(84, "SemiBold"), WHITE, a2, anchor="mm", tracking=10)
    img.paste(lay, (0, 0), lay)
    return img


def lower_third(img, lt, t):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    a = ease((t - 0.15) / 0.4)
    d.rectangle([110, 820, 118, 820 + 150 * a], fill=GOLD + (255,))
    text(lay, (146, 818 + 16 * (1 - a)), lt["title"], font(86, "Bold"), WHITE, a, tracking=3)
    a2 = ease((t - 0.45) / 0.4)
    text(lay, (148, 922 + 12 * (1 - a2)), lt["sub"], font(40, "SemiLight"), MUTED, a2, tracking=1)
    img.paste(lay, (0, 0), lay)
    return img


# ---------- render ----------
def render_video(spec, out_mp4, stills=None):
    src = ROOT / spec["source"]
    total, hits = build_timeline(spec)
    print(f"timeline {total:.2f}s, hits at {[round(h, 2) if h else None for h in hits]}")
    enc = None
    if not stills:
        enc = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                                "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
                                str(out_mp4)], stdin=subprocess.PIPE)
    sheet = []

    def emit(img, t):
        if enc:
            enc.stdin.write(img.tobytes())
        elif any(abs(t - s) < 0.5 / FPS for s in stills):
            sheet.append((t, img.resize((480, 270))))

    # info card over a blurred, darkened frame of the play
    c = spec["card"]
    bg = next(frames_at(src, c["bg_at"], [c["bg_at"]])).filter(ImageFilter.GaussianBlur(22))
    bg = finish(bg, dim=0.42)
    for k in range(round(c["dur"] * FPS)):
        emit(card_frame(spec, k / FPS, bg), k / FPS)

    last = None
    for s in spec["shots"]:
        n = round(s["out_dur"] * FPS)
        if s.get("type") == "freeze":
            for k in range(n):
                t = s["out_start"] + k / FPS
                emit(freeze_frame(last, s, k / FPS), t)
            continue
        sp = s.get("speed", 1.0)
        times = [s["in"] + (k / FPS) * sp for k in range(n)]
        z0, z1 = s.get("zoom", [1.0, 1.0]) if isinstance(s.get("zoom"), list) else (s.get("zoom", 1.0),) * 2
        for k, fr in enumerate(frames_at(src, s["in"], times)):
            t = s["out_start"] + k / FPS
            u = k / max(n - 1, 1)
            kick, flash = hit_fx(t, hits)
            raw = zoomed(fr, (z0 + (z1 - z0) * u) * (1 + kick), s.get("center", (W / 2, H / 2)))
            last = raw
            img = finish(raw, flash=flash)
            if s.get("pips", True):
                img = overlay_pips(img, spec, t, hits)
            if s.get("lower_third"):
                img = lower_third(img, s["lower_third"], k / FPS)
            fade_out = s.get("fade_out", 0)
            if fade_out and (n - k) / FPS < fade_out:
                img = finish(img, dim=(n - k) / FPS / fade_out)
            emit(img, t)
    if enc:
        enc.stdin.close(); enc.wait()
    return total, hits, sheet


# ---------- audio ----------
def vod_audio(item):
    """Cut [start, end] (VOD seconds or h:mm:ss) of a YouTube VOD's audio with yt-dlp; cached."""
    def secs(v):
        if isinstance(v, (int, float)):
            return float(v)
        p = [float(x) for x in v.split(":")]
        return sum(x * 60 ** i for i, x in enumerate(reversed(p)))
    a, b = secs(item["start"]), secs(item["end"])
    cache = ROOT / "footage" / "audio"
    cache.mkdir(exist_ok=True)
    out = cache / f"{item['vod']}_{a:.2f}_{b:.2f}.wav"
    if not out.exists():
        pre = 5.0                                  # sections snap to keyframes: fetch with margin, trim exactly after
        raw = cache / f"_raw_{item['vod']}_{a:.0f}"
        hms = lambda x: f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:06.3f}"
        r = subprocess.run([sys.executable, "-m", "yt_dlp", *(["--proxy", PROXY] if PROXY else []), "--js-runtimes", "node", "-f", "bestaudio",
                        "--ffmpeg-location", str(FFB), "--download-sections", f"*{hms(max(a - pre, 0))}-{hms(b + 1)}",
                        "--force-keyframes-at-cuts", "-x", "--audio-format", "wav", "-o", str(raw) + ".%(ext)s",
                        f"https://www.youtube.com/watch?v={item['vod']}"])
        if r.returncode:
            network_hint("yt-dlp audio download")
            sys.exit(1)
        subprocess.run([FF, "-v", "error", "-y", "-ss", f"{min(pre, a):.3f}", "-t", f"{b - a:.3f}", "-i", str(raw) + ".wav",
                        "-ar", "48000", "-ac", "2", str(out)], check=True)
        (pathlib.Path(str(raw) + ".wav")).unlink(missing_ok=True)
    return out


def mix_audio(spec, total, hits, out_wav):
    """Place every sound at its output time and mix. Times may be numbers or 'hitN' / 'hitN-0.5' / 'shotN' / 'end'."""
    def when(v):
        if isinstance(v, (int, float)):
            return float(v)
        base, _, off = v.replace("+", " +").replace("-", " -").partition(" ")
        off = float(off.replace(" ", "")) if off else 0.0
        if base.startswith("hit"):
            return hits[int(base[3:]) - 1] + off
        if base.startswith("shot"):
            return spec["shots"][int(base[4:]) - 1]["out_start"] + off
        return {"end": total, "card": spec["card"]["dur"]}[base] + off
    items = []
    for s in spec["sfx"]:
        names = s["file"] if isinstance(s["file"], list) else [s["file"]]
        ats = [when(a) for a in (s["at"] if isinstance(s["at"], list) else [s["at"]])]
        for at in ats:
            for nm in names:
                items.append((HERE / "sfx" / nm, at, s.get("gain", 0.0), None))
    for v in spec.get("vod_audio", []):
        items.append((vod_audio(v), when(v["at"]), v.get("gain", 0.0), v.get("fade", 0.15)))
    args, filt = [FF, "-v", "error", "-y"], []
    for i, (path, at, gain, fade) in enumerate(items):
        args += ["-i", str(path)]
        f = f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,volume={gain}dB"
        if fade:
            f += f",afade=t=in:d={fade},areverse,afade=t=in:d={fade},areverse"
        f += f",adelay={max(at, 0) * 1000:.0f}:all=1[a{i}]"
        filt.append(f)
    filt.append("".join(f"[a{i}]" for i in range(len(items))) +
                f"amix=inputs={len(items)}:normalize=0,atrim=0:{total:.3f},apad=whole_dur={total:.3f},alimiter=limit=0.89[out]")
    subprocess.run(args + ["-filter_complex", ";".join(filt), "-map", "[out]", "-ar", "48000", str(out_wav)], check=True)


def main():
    spec_path = pathlib.Path(sys.argv[1])
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    out_dir = HERE / "highlights"
    out_dir.mkdir(exist_ok=True)
    name = spec_path.stem
    if "--stills" in sys.argv:
        total, hits = build_timeline(spec)
        marks = [0.6, 1.3] + [s["out_start"] + s["out_dur"] * f for s in spec["shots"] for f in (0.15, 0.6)] + \
                [h + 0.03 for h in hits if h]
        _, _, sheet = render_video(spec, None, stills=sorted(marks))
        cols = 4
        img = Image.new("RGB", (480 * cols, 270 * math.ceil(len(sheet) / cols)))
        for i, (t, im) in enumerate(sheet):
            ImageDraw.Draw(im).text((6, 4), f"{t:.2f}", fill=(255, 255, 0), font=font(22))
            img.paste(im, ((i % cols) * 480, (i // cols) * 270))
        img.save(out_dir / f"{name}_sheet.jpg", quality=85)
        print("sheet:", out_dir / f"{name}_sheet.jpg")
        return
    pic, wav, final = out_dir / f"{name}_pic.mp4", out_dir / f"{name}.wav", out_dir / f"{name}.mp4"
    total, hits, _ = render_video(spec, pic)
    mix_audio(spec, total, hits, wav)
    subprocess.run([FF, "-v", "error", "-y", "-i", str(pic), "-i", str(wav), "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
                    "-shortest", str(final)], check=True)
    print("done:", final)


if __name__ == "__main__":
    main()
