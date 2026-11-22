"""Shared engine for video 02 section clips (copied from video 03): canvas, palette, fonts, word timing, frame piping, captions, audio mix.

A section is rendered with render_section(sid, pid, draw, sfx=..., lead=..., tail=...):
  draw(img, t) paints frame time t (seconds from the clip start) onto a 1920x1080 RGB image;
  the narration paragraph pid starts at t = lead; sfx = [(t, name, gain_db)].
Output: clips/<sid>.mp4 (H.264 + AAC, voice + sfx + the music bed slice, captions burned in).
"""
import functools, json, math, os, pathlib, re, subprocess

import numpy as np
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
FFDIR = ffmpeg_dir()
FFMPEG, FFPROBE = str(FFDIR / "ffmpeg.exe"), str(FFDIR / "ffprobe.exe")
HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent
CLIPS = ROOT / "clips"
# EDIT ME: sound library. My CC0 sound effects and music are not in this repo; point this at your own folder with the same file names.
SFX_LIB = pathlib.Path("EDIT_ME/sound-library")
NAR_DIR = HERE / os.environ.get("NAR_DIR", "narration_v2")
NAR = {p["id"]: p for p in json.loads((NAR_DIR / "narration.json").read_text(encoding="utf-8"))}

W, H, FPS = 1920, 1080, 30
# Palette: CS2-dark, CT blue / T orange for data, green/red for won/lost rounds, yellow for the number that matters.
BG = (14, 17, 23)
PANEL = (24, 29, 38)
LINE = (52, 60, 74)
WHITE = (238, 240, 245)
MUTED = (138, 147, 162)
DIM = (78, 86, 100)
CT = (93, 156, 236)
TT = (236, 150, 60)
WIN = (76, 200, 120)
LOSS = (228, 76, 76)
YELLOW = (255, 211, 77)


# ---------- timing ----------
def ease(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def ease_io(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def ramp(t, start, length=0.4):
    return ease((t - start) / length)


def core(s):
    return re.sub(r"[^\w']", "", s).lower()


class Words:
    """Word times of one narration paragraph, shifted by the clip's lead-in."""

    def __init__(self, pid, lead):
        self.p, self.lead = NAR[pid], lead

    def __call__(self, word, nth=0, end=False):
        hits = [w for w in self.p["words"] if core(w["w"]) == core(word)]
        if len(hits) <= nth:
            raise KeyError(f"{self.p['id']}: word '{word}' #{nth} not in narration")
        return self.lead + hits[nth]["e" if end else "s"]

    @property
    def duration(self):
        return self.p["duration"]


# ---------- drawing ----------
@functools.lru_cache(maxsize=None)
def font(size, style="Bold"):
    f = ImageFont.truetype(r"C:\Windows\Fonts\bahnschrift.ttf", size)
    try:
        f.set_variation_by_name(style)
    except Exception:
        pass
    return f


@functools.lru_cache(maxsize=None)
def _base(k):
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    shade = np.clip(1.18 - 0.42 * r, 0.6, 1.12)
    img = np.stack([np.full((H, W), c, float) * shade for c in BG], -1)
    img += np.random.default_rng(k).normal(0, 2.6, (H, W, 1))
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


def canvas(frame):
    return _base(0).copy()          # static grain: a per-frame pattern flickers and blows up the bitrate


def mix(c1, c2, a):
    return tuple(int(x * (1 - a) + y * a) for x, y in zip(c1, c2))


def fade(c, a, bg=BG):
    """Colour c at opacity a over the background colour (good enough for elements on the plain background)."""
    return mix(bg, c, max(0.0, min(1.0, a)))


def text(d, xy, s, size, fill, anchor="la", style="Bold", alpha=1.0, tracking=0, bg=BG):
    if alpha <= 0.01:
        return
    f = font(size, style)
    col = fade(fill, alpha, bg) if alpha < 1 else fill
    if not tracking:
        d.text(xy, s, font=f, fill=col, anchor=anchor)
        return
    width = sum(d.textlength(ch, font=f) + tracking for ch in s) - tracking
    x, y = xy
    if anchor[0] == "m":
        x -= width / 2
    elif anchor[0] == "r":
        x -= width
    for ch in s:
        d.text((x, y), ch, font=f, fill=col, anchor="l" + anchor[1])
        x += d.textlength(ch, font=f) + tracking


def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle([int(v) for v in box], radius=int(r), fill=fill, outline=outline, width=width)


def counter(value, t, start, dur=0.9):
    """Rolling number: 0 -> value over dur seconds from start."""
    return value * ease((t - start) / dur)


def headset(d, cx, cy, s, col, glow=0.0):
    """Simple headset icon centred at (cx, cy), size s."""
    w = max(3, int(s * 0.09))
    d.arc([cx - s * 0.42, cy - s * 0.48, cx + s * 0.42, cy + s * 0.36], 180, 360, fill=col, width=w)
    for sx in (-1, 1):
        x = cx + sx * s * 0.42
        rrect(d, (x - s * 0.11, cy - s * 0.08, x + s * 0.11, cy + s * 0.26), s * 0.06, fill=col)
    # microphone boom
    d.arc([cx - s * 0.42, cy - s * 0.1, cx + s * 0.1, cy + s * 0.42], 90, 180, fill=col, width=max(2, w // 2))
    d.ellipse([cx + s * 0.02, cy + s * 0.34, cx + s * 0.14, cy + s * 0.46], fill=col)
    if glow > 0:   # speech waves
        for k in range(3):
            a = max(0.0, min(1.0, glow * 1.4 - k * 0.25))
            rad = s * (0.62 + 0.14 * k)
            d.arc([cx - rad, cy - rad * 0.9, cx + rad, cy + rad * 0.9], -35, 35, fill=fade(col, a), width=max(2, w // 2))
            d.arc([cx - rad, cy - rad * 0.9, cx + rad, cy + rad * 0.9], 145, 215, fill=fade(col, a), width=max(2, w // 2))


def ring(d, cx, cy, r, frac, col, width=22, track=LINE):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=track, width=width)
    if frac > 0:
        d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * frac, fill=col, width=width)


# ---------- footage ----------
class Footage:
    """Frames of one source segment at the project frame rate, decoded once on first use (kept small: seconds)."""

    def __init__(self, path, start, dur, zoom=(1.0, 1.0), focus=(0.5, 0.5)):
        self.path, self.start, self.dur, self.zoom, self.focus = str(path), start, dur, zoom, focus
        self.frames = None

    def load(self):
        n = round(self.dur * FPS)
        raw = subprocess.run([FFMPEG, "-v", "error", "-ss", f"{self.start:.3f}", "-t", f"{self.dur + 0.2:.3f}",
                              "-i", self.path, "-vf", f"fps={FPS},scale={W}:{H}:flags=lanczos", "-f", "rawvideo",
                              "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
        arr = np.frombuffer(raw, np.uint8)
        k = len(arr) // (W * H * 3)
        self.frames = arr[:k * W * H * 3].reshape(k, H, W, 3)[:n]

    def free(self):
        self.frames = None

    def frame(self, t):
        """Frame at local time t, with a slow punch-in from zoom[0] to zoom[1] around focus."""
        if self.frames is None:
            self.load()
        i = min(len(self.frames) - 1, max(0, int(t * FPS)))
        img = Image.fromarray(self.frames[i])
        z = self.zoom[0] + (self.zoom[1] - self.zoom[0]) * min(1.0, max(0.0, t / self.dur))
        if z > 1.001:
            cw, ch = W / z, H / z
            fx, fy = self.focus
            x0 = min(max(0, fx * W - cw / 2), W - cw)
            y0 = min(max(0, fy * H - ch / 2), H - ch)
            img = img.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))
        return img


@functools.lru_cache(maxsize=None)
def _side_mask(frac, strength):
    """Horizontal gradient mask: opaque at the left edge, clear at frac of the width."""
    x = np.linspace(0, 1, W)
    a = np.clip(1 - x / frac, 0, 1) ** 1.3 * strength
    return Image.fromarray((np.tile(a, (H, 1)) * 255).astype(np.uint8), "L")


def side_shade(img, a=1.0, frac=0.62, strength=0.82):
    """Darken the left part of a footage frame so text there reads over busy broadcast HUDs."""
    if a <= 0:
        return
    mask = _side_mask(frac, strength)
    if a < 1:
        mask = mask.point(lambda v: int(v * a))
    img.paste((0, 0, 0), (0, 0, W, H), mask)


def block_text(img, xy, s, size, fg, block, a=1.0, pad=(26, 14), anchor="l", skew=10):
    """Text on a solid (slightly slanted) block — for numbers/headlines over footage. Slides in with a."""
    if a <= 0.01:
        return
    d = ImageDraw.Draw(img)
    f = font(size)
    l, tp, r, b = d.textbbox((0, 0), s, font=f, anchor="ls")
    wt, ht = r - l, b - tp
    x, y = xy
    if anchor == "m":
        x -= wt / 2 + pad[0]
    x += -40 * (1 - a)
    bw, bh = wt + 2 * pad[0], ht + 2 * pad[1]
    blk = Image.new("RGBA", (int(bw + skew + 4), int(bh)), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blk)
    bd.polygon([(skew, 0), (bw + skew, 0), (bw, bh), (0, bh)], fill=block + (int(255 * a),))
    bd.text((pad[0] + skew / 2 - l, pad[1] - tp), s, font=f, fill=fg + (int(255 * a),), anchor="ls")
    img.paste(blk, (int(x), int(y)), blk)
    return bw, bh


def lower_third(d, t, t0, name, sub, tag=None, tag_col=None, x=90, y=860):
    """Name plate: yellow bar + big name + muted sub line; slides in from the left."""
    a = ease((t - t0) / 0.3)
    if a <= 0:
        return
    dx = -60 * (1 - a)
    f_name, f_sub = font(84), font(40, "SemiBold")
    wname = d.textlength(name, font=f_name)
    wsub = d.textlength(sub, font=f_sub)
    wbox = max(wname, wsub) + 80
    rrect(d, (x + dx + 6, y + 6, x + dx + wbox + 6, y + 176), 12, fill=(0, 0, 0))      # hard shadow
    rrect(d, (x + dx, y, x + dx + wbox, y + 170), 12, fill=(10, 12, 16))
    d.rectangle([x + dx, y, x + dx + 14, y + 170], fill=YELLOW)
    d.text((x + dx + 40, y + 18), name, font=f_name, fill=WHITE)
    d.text((x + dx + 40, y + 114), sub, font=f_sub, fill=(200, 205, 215))
    if tag:
        f_tag = font(36)
        wt_ = d.textlength(tag, font=f_tag) + 36
        tx = x + dx + wbox + 16
        rrect(d, (tx, y + 4, tx + wt_, y + 62), 8, fill=tag_col or YELLOW)
        d.text((tx + 18, y + 33), tag, font=f_tag, fill=(10, 12, 16), anchor="lm")


# ---------- captions ----------
KEYWORDS = ["four different teams", "twice in a row", "never missed", "Three grand finals", "Three losses", "32",
            "overtime team", "All four", "still lost", "Mirage", "nineteen times", "sixteen of ninety-one", "donk",
            "twelve", "ZywOo", "ropz", "Eternal Fire", "Cloud9", "overtime", "thirteen to two", "thirteen to three",
            "jL", "The MongolZ", "Liquid", "sixteen-fourteen", "thirteen-eleven", "two finals, two defeats",
            "youngest", "highest-rated", "paiN", "forty-six rounds", "still went out", "five-thirteen", "Thirteen-four",
            "Thirteen-six", "Stage 1", "FaZe", "nineteen-seventeen", "thirteen-two", "back-to-back", "third",
            "BetBoom", "9z", "forty-seven rounds", "didn't drop a map", "Thirteen-eight", "karrigan", "m0NESY",
            "apEX", "No debate", "fans' favourite", "most clutches", "NiKo", "frozen", "b1t", "Singapore",
            "comments", "all-star"]
PUNCH = {"Five Majors.", "Four champions.", "Then there's FaZe.", "Three grand finals.", "Three losses.",
         "Thirteen-eight.", "No debate.", "See you in Singapore."}
MAX_WORDS, MAX_CHARS = 4, 26


def ass_time(t):
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def styled(s):
    taken, spans = [], []
    for kw in KEYWORDS:
        for m in re.finditer(r"(?<![\w'])" + re.escape(kw) + r"(?![\w'])", s):
            if not any(m.start() < b and a < m.end() for a, b in taken):
                taken.append((m.start(), m.end()))
                spans.append((KEYWORDS.index(kw), m.start(), m.end()))
    spans = sorted(sorted(spans)[:2], key=lambda x: x[1])
    out, pos = "", 0
    for _, a, b in spans:
        out += s[pos:a] + r"{\c&H004DD3FF&}" + s[a:b] + r"{\c&H00FFFFFF&}"
        pos = b
    out += s[pos:]
    return (r"{\fs76}" + out) if s.strip() in PUNCH else out


def chunks(ws):
    """Sentence -> short chunks (clause by clause, then evenly), punch lines whole."""
    if " ".join(w[0] for w in ws) in PUNCH:
        return [ws]
    clauses, cur = [], []
    for w in ws:
        cur.append(w)
        if w[0].endswith((",", ":")):
            clauses.append(cur); cur = []
    if cur:
        clauses.append(cur)
    joined = []
    for c in clauses:
        if joined and (len(c) == 1 or len(joined[-1]) == 1) and len(joined[-1]) + len(c) <= MAX_WORDS + 1:
            joined[-1] += c
        else:
            joined.append(c)
    out = []
    for c in joined:
        chars = len(" ".join(w[0] for w in c))
        n = min(len(c), max(math.ceil(len(c) / MAX_WORDS), math.ceil(chars / MAX_CHARS), 1))
        size, extra = divmod(len(c), n)
        i = 0
        for k in range(n):
            step = size + (1 if k < extra else 0)
            out.append(c[i:i + step]); i += step
    return out


def captions(pid, lead, path, style="Low"):
    ws = [(w["w"], w["s"] + lead, w["e"] + lead) for w in NAR[pid]["words"]]
    lines, sent = [], []
    for w in ws:
        sent.append(w)
        if re.search(r"[.?!]$", w[0]):
            lines += chunks(sent); sent = []
    if sent:
        lines += chunks(sent)
    ev = []
    for k, ln in enumerate(lines):
        s, e = ln[0][1], max(ln[-1][2], ln[0][1] + 0.67)
        if k + 1 < len(lines):
            e = min(e, lines[k + 1][0][1] - 0.02)
        st = style((s + e) / 2) if callable(style) else style      # e.g. "Box" only while footage is on screen
        ev.append(f"Dialogue: 0,{ass_time(s)},{ass_time(e)},{st},,0,0,0,,{styled(' '.join(x[0] for x in ln))}")
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Mid,Arial,66,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,6.5,4,5,130,130,0,1
Style: Low,Arial,54,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,5.5,3.5,2,130,130,46,1
Style: Box,Arial,54,&H00FFFFFF,&H00FFFFFF,&H70000000,&H70000000,1,0,0,0,100,100,0,0,3,9,0,2,130,130,262,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    path.write_text(head + "\n".join(ev) + "\n", encoding="utf-8")


# ---------- audio ----------
def sfx_path(name):
    local = HERE / "sfx" / f"{name}.wav"
    return local if local.exists() else SFX_LIB / "sfx" / f"{name}.wav"


MUSIC_BED = HERE / "music_bed.wav"


def build_audio(pid, lead, dur, sfx, out, music_offset=None):
    """Voice at full level (normalised later in the master), sfx ~15 dB under, music ~20 dB under, ducked by ear."""
    inputs, filt, labels = [], [], []
    if pid:
        inputs += ["-i", str(NAR_DIR / f"{pid}.mp3")]
        d = int(lead * 1000)
        filt.append(f"[0:a]aresample=48000,aformat=channel_layouts=stereo,adelay={d}|{d},volume=1.0[v]")
        labels.append("[v]")
    for k, (t, name, gain_db) in enumerate(sfx):
        i = len(inputs) // 2
        inputs += ["-i", str(sfx_path(name))]
        d = int(max(0.0, t) * 1000)
        filt.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={d}|{d},volume={gain_db}dB[s{k}]")
        labels.append(f"[s{k}]")
    if music_offset is not None and MUSIC_BED.exists():
        i = len(inputs) // 2
        inputs += ["-ss", f"{music_offset:.3f}", "-t", f"{dur:.3f}", "-i", str(MUSIC_BED)]
        filt.append(f"[{i}:a]aresample=48000,volume=-21dB[m]")
        labels.append("[m]")
    if not labels:
        filt.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{dur}[x]")
        labels = ["[x]"]
    filt.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=longest,atrim=0:{dur:.3f},"
                f"apad=whole_dur={dur:.3f}[out]")
    subprocess.run([FFMPEG, "-y", "-v", "error", *inputs, "-filter_complex", ";".join(filt), "-map", "[out]",
                    "-c:a", "pcm_s16le", str(out)], check=True)


# ---------- render ----------
def render_section(sid, pid, draw, sfx=(), lead=0.15, tail=0.35, music_offset=None, caption_style="Low", dur=None):
    CLIPS.mkdir(exist_ok=True)
    tmp = HERE / "tmp"
    tmp.mkdir(exist_ok=True)
    dur = dur or (lead + NAR[pid]["duration"] + tail)
    n = round(dur * FPS)
    video = tmp / f"{sid}_v.mp4"
    proc = subprocess.Popen([FFMPEG, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-tune", "animation",
                             "-pix_fmt", "yuv420p", str(video)], stdin=subprocess.PIPE)
    for f in range(n):
        img = canvas(f)
        draw(img, f / FPS)
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    proc.wait()
    audio = tmp / f"{sid}_a.wav"
    if os.environ.get("NO_MUSIC"):                              # final assembly lays one continuous music bed instead
        music_offset = None
    build_audio(pid, lead, dur, list(sfx), audio, music_offset)
    ass = tmp / f"{sid}.ass"
    vf = "null"
    if pid:
        captions(pid, lead, ass, caption_style)
        vf = f"subtitles={ass.name}"          # relative name, ffmpeg runs inside tmp/ (drive letters break the filter)
    out = CLIPS / f"{sid}.mp4"
    subprocess.run([FFMPEG, "-y", "-v", "error", "-i", str(video), "-i", str(audio), "-vf", vf, "-c:v", "libx264",
                    "-preset", "medium", "-crf", "19", "-tune", "animation", "-g", "60", "-pix_fmt", "yuv420p", "-c:a", "aac",
                    "-b:a", "192k", "-movflags", "+faststart", "-shortest", str(out)], check=True, cwd=tmp)
    print(f"{sid}: {dur:.1f}s -> {out}")
    return out
