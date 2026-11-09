"""Highlight renderer v2 (video 02): rapid kill cuts with HUD-proof graphics. One JSON spec -> one clip.

Changes from highlight.py: every piece of our text sits on a solid block (white-on-black, or black-on-yellow for the
key fact) so it never melts into the broadcast HUD; a dark corner panel covers the broadcast minimap under our tag; the
info card slams in with a yellow slab; a "jump" tag marks time skipped between kills; the kill counter is a yellow block
("KILL 3/5") that pops on every kill.

Spec keys: source, card{dur,bg_at,kicker,title,fact,sub}, tag, total_kills, hits[], shots[{in,out,speed,zoom,center,
jump}], freeze{dur,text,sub} (as a shot with type freeze), sfx[], vod_audio[].
Usage: python highlight2.py highlights/C1.json [--stills]
"""
import functools, json, math, pathlib, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import highlight as H1
from highlight import W, H, FPS, FF, ease, font, zoomed, finish, frames_at, build_timeline, hit_fx, mix_audio

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent
YELLOW, BLACK, WHITE = (255, 211, 77), (10, 10, 12), (245, 243, 238)


def block(img, xy, s, size, fg, bg, a=1.0, pad=(26, 12), anchor="l", skew=12, style="Bold", slide=50):
    """Text on a solid slanted block. anchor 'l' (x is left edge) or 'm' (x is centre). Slides in with a."""
    if a <= 0.01:
        return 0, 0
    d = ImageDraw.Draw(img)
    f = font(size, style)
    l, t, r, b = d.textbbox((0, 0), s, font=f, anchor="ls")
    bw, bh = (r - l) + 2 * pad[0], (b - t) + 2 * pad[1]
    x, y = xy
    if anchor == "m":
        x -= bw / 2
    x -= slide * (1 - a)
    blk = Image.new("RGBA", (int(bw + skew + 2), int(bh)), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blk)
    al = int(255 * min(a, 1))
    bd.polygon([(skew, 0), (bw + skew, 0), (bw, bh), (0, bh)], fill=bg + (al,))
    bd.text((pad[0] + skew / 2 - l, pad[1] - t), s, font=f, fill=fg + (al,), anchor="ls")
    img.paste(blk, (int(x), int(y)), blk)
    return bw, bh


@functools.lru_cache(maxsize=None)
def corner_panel():
    """Dark corner gradient (top-left) that hides the broadcast minimap under our tag."""
    yy, xx = np.mgrid[0:520, 0:900]
    a = np.clip(1.0 - np.sqrt((xx / 900) ** 2 + (yy / 520) ** 2), 0, 1) ** 0.55 * 245
    arr = np.zeros((520, 900, 4), np.uint8)
    arr[..., 3] = a.astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


@functools.lru_cache(maxsize=None)
def team_logo(key, box_w, box_h):
    im = Image.open(ROOT / "assets" / "logos" / f"{key}.png").convert("RGBA")
    im = im.crop(im.getbbox())
    sc = min(box_w / im.width, box_h / im.height)
    return im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)


def put_logo(img, key, x, y, box_w, box_h, a=1.0, anchor="l"):
    if not key or a <= 0.01:
        return 0
    im = team_logo(key, box_w, box_h)
    if a < 1:
        im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * a)))
    if anchor == "r":
        x -= im.width
    img.paste(im, (int(x), int(y + (box_h - im.height) / 2)), im)
    return im.width


def tag(img, spec, t, hits):
    img.paste(corner_panel(), (0, 0), corner_panel())
    bw, _ = block(img, (54, 52), spec["tag"], 64, WHITE, BLACK)
    put_logo(img, spec.get("team"), 54 + bw + 30, 50, 170, 80)
    n = sum(1 for h in hits if h is not None and t >= h)
    if n:
        last = max(h for h in hits if h is not None and t >= h)
        pop = ease((t - last) / 0.12)
        size = int(54 + 16 * (1 - pop))
        block(img, (60, 150), f"KILL {n}/{spec['total_kills']}", size, BLACK, YELLOW, slide=0)


def jump_tag(img, s, k):
    """'+22 SECONDS' flash at the start of a shot that skips time."""
    t = k / FPS
    if t > 0.75:
        return
    a = ease(t / 0.12) * (1 - ease((t - 0.55) / 0.2))
    block(img, (W / 2, 470), s, 72, BLACK, YELLOW, a=a, anchor="m", slide=0)


def card_bg(frame):
    """Card background: the play's own key frame, pushed in, darkened and half-desaturated (still readable as 'where')."""
    return finish(zoomed(frame, 1.12, (W / 2, H / 2)).filter(ImageFilter.GaussianBlur(5)), dim=0.42, sat=0.45)


def speed_lines(img, t, seed=7):
    """Diagonal streaks racing left-to-right behind the slab; they thin out as the card settles."""
    rng = np.random.default_rng(seed)
    d = ImageDraw.Draw(img, "RGBA")
    fade = 1 - ease((t - 0.6) / 0.6)
    for i in range(26):
        y = rng.uniform(250, 760)
        speed = rng.uniform(2600, 4200)
        length = rng.uniform(180, 520)
        x = (rng.uniform(-W, W) + speed * t) % (W + 800) - 400
        col = YELLOW if i % 3 == 0 else WHITE
        a = int(rng.uniform(70, 160) * fade)
        if a > 0:
            d.line([(x, y), (x + length, y - length * 0.12)], fill=col + (a,), width=int(rng.uniform(2, 6)))


def card(spec, t, bg):
    c = spec["card"]
    img = bg.copy()
    speed_lines(img, t)
    d = ImageDraw.Draw(img)
    a0 = ease(t / 0.18)
    # yellow slab sweeping in from the left behind the name
    sx = -1400 + 1500 * a0
    d.polygon([(sx + 14, 344), (sx + 1264, 344), (sx + 1164, 654), (sx - 86, 654)], fill=BLACK)      # hard shadow
    d.polygon([(sx, 330), (sx + 1250, 330), (sx + 1150, 640), (sx - 100, 640)], fill=YELLOW)
    a1 = ease((t - 0.08) / 0.2)
    sc = 1.25 - 0.25 * a1
    size = 280
    while size > 120 and d.textlength(c["title"], font=font(size, "Bold")) > 1000:                  # long names shrink to fit
        size -= 10
    f = font(int(size * sc), "Bold")
    if a1 > 0:
        x = 150 - 60 * (1 - a1)
        d.text((x, 485), c["title"], font=f, fill=BLACK, anchor="lm")
    block(img, (150, 230), c["kicker"], 40, WHITE, BLACK, a=ease((t - 0.2) / 0.25), style="SemiBold")
    block(img, (150, 680), c["fact"], 76, BLACK, YELLOW, a=ease((t - 0.32) / 0.25))
    la = ease((t - 0.25) / 0.25)
    put_logo(img, spec.get("team"), 1790 - 60 * (1 - la), 330, 380, 300, a=la, anchor="r")
    block(img, (150, 800), c["sub"], 40, WHITE, BLACK, a=ease((t - 0.44) / 0.25), style="SemiBold")
    # camera shake when the name lands
    amp = 22 * math.exp(-max(t - 0.2, 0) / 0.09) if t >= 0.2 else 0
    if amp > 0.5:
        dx, dy = amp * math.sin(t * 97), amp * math.cos(t * 83)
        img = img.transform(img.size, Image.AFFINE, (1, 0, -dx, 0, 1, -dy), resample=Image.BILINEAR)
    return img


def freeze(img, s, t):
    img = zoomed(img, 1.0 + 0.05 * t / s["dur"], (W / 2, H / 2))
    img = finish(img, dim=0.45, sat=0.2)
    a1 = ease(t / 0.14)
    size = 250
    while size > 110 and ImageDraw.Draw(img).textlength(s["text"], font=font(size, "Bold")) > 1500:     # fit the frame
        size -= 10
    block(img, (W / 2, 330), s["text"], int(size * (1.3 - 0.3 * a1)), BLACK, YELLOW, a=a1, anchor="m", slide=0, pad=(60, 20))
    block(img, (W / 2, 690), s["sub"], 64, WHITE, BLACK, a=ease((t - 0.3) / 0.3), anchor="m", slide=0)
    return img


def lower(img, lt, t):
    block(img, (90, 850), lt["title"], 72, WHITE, BLACK, a=ease((t - 0.1) / 0.3))
    block(img, (96, 960), lt["sub"], 40, BLACK, YELLOW, a=ease((t - 0.3) / 0.3), style="SemiBold")


def auto_shots(spec):
    """Kill segments from the kill times: [kill - pre, kill + post] each, merged into one continuous roll whenever the
    next segment starts within `merge` s of the current one's end. Time skipped between segments of more than
    `jump_min` s gets a 'N SECONDS LATER' tag. Then the spec's 'after' shots (freeze, reaction) follow."""
    a = spec["auto"]
    segs = []
    for k in spec["hits"]:
        s, e = k - a.get("pre", 1.0), k + a.get("post", 0.5)
        if segs and s <= segs[-1][1] + a.get("merge", 1.0):
            segs[-1][1] = max(segs[-1][1], e)
        else:
            segs.append([s, e])
    shots = []
    for i, (s, e) in enumerate(segs):
        shot = {"in": round(s, 2), "out": round(e, 2), "speed": 1.0, "zoom": a.get("zoom", [1.15, 1.22]),
                "center": a.get("center", [960, 540])}
        if i and s - segs[i - 1][1] >= a.get("jump_min", 4.0):
            gap = (s + a.get("pre", 1.0)) - (segs[i - 1][1] - a.get("post", 0.5))     # last kill before -> first kill after
            shot["jump"] = a.get("jump_labels", {}).get(str(i), f"{round(gap)} SECONDS LATER")
        shots.append(shot)
    return shots + spec.get("after", [])


def default_sfx(spec):
    """The C1 sound design, derived from the shot list: card whoosh + slam, a hit on every kill, a whoosh into every
    time jump, a riser into the last kill, a big hit on the freeze, a soft impact on the reaction shot."""
    n = len(spec["hits"])
    sfx = [{"file": "whoosh-reverse-1s.wav", "at": "card-1.0", "gain": -5},
           {"file": "stinger-hit-short.wav", "at": 0.2, "gain": -4},
           {"file": ["stinger-hit-short.wav", "dry-thud.wav"], "at": [f"hit{i + 1}" for i in range(n)], "gain": -3},
           {"file": "riser-short-2s.wav", "at": f"hit{n}-2.0", "gain": -7}]
    for i, sh in enumerate(spec["shots"], 1):
        if sh.get("jump"):
            sfx.append({"file": "whoosh-reverse-1s.wav", "at": f"shot{i}-1.0", "gain": -6})
        if sh.get("type") == "freeze":
            sfx.append({"file": "stinger-energetic-hit.wav", "at": f"shot{i}", "gain": -1})
        if sh.get("lower_third"):
            sfx.append({"file": "impact-soft-1.wav", "at": f"shot{i}", "gain": -4})
    return sfx


# ---------- optional per-kill visual effects (spec "fx": ["shake", "edge_glow" | "vignette", "hold"]) ----------
def _since(t, hits):
    past = [h for h in hits if h is not None and t >= h]
    return (t - max(past)) if past else None, len(past)


def shake(img, t, hits):
    """(4) Short, sharp screen shake on every kill (footage only; our graphics stay still)."""
    dt, _ = _since(t, hits)
    if dt is None or dt > 0.35:
        return img
    amp = 16 * math.exp(-dt / 0.07)
    dx, dy = amp * math.sin(dt * 170), amp * math.cos(dt * 131)
    img = zoomed(img, 1.03, (W / 2, H / 2))                       # slight overscan so edges never show
    return img.transform(img.size, Image.AFFINE, (1, 0, -dx, 0, 1, -dy), resample=Image.BILINEAR)


@functools.lru_cache(maxsize=None)
def _edge_mask():
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.minimum.reduce([xx, W - 1 - xx, yy, H - 1 - yy]).astype(np.float32)
    return np.clip(1 - d / 170, 0, 1)[..., None] ** 1.6


def edge_glow(img, t, hits):
    """(9) The frame edges flare yellow on every kill and fade within 0.45 s."""
    dt, _ = _since(t, hits)
    if dt is None or dt > 0.45:
        return img
    a = 0.85 * (1 - ease(dt / 0.45))
    arr = np.asarray(img, dtype=np.float32)
    m = _edge_mask() * a
    arr = arr * (1 - m) + np.array(YELLOW, np.float32) * m
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))


@functools.lru_cache(maxsize=None)
def _vig_mask():
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    return np.clip((r - 0.45) / 0.95, 0, 1)[..., None] ** 1.3


def tension_vignette(img, t, hits):
    """(10) Edges darken a step with every kill (eased over 0.25 s): the last kill is the tightest frame."""
    dt, n = _since(t, hits)
    if not n:
        return img
    level = (n - 1 + ease(dt / 0.25)) / len(hits)
    arr = np.asarray(img, dtype=np.float32) * (1 - 0.8 * level * _vig_mask())
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))


def render(spec, out_mp4, stills=None):
    src = ROOT / spec["source"]
    total, hits = build_timeline(spec)
    print(f"timeline {total:.2f}s, hits at {[round(h, 2) if h else None for h in hits]}")
    enc = None if stills else subprocess.Popen(
        [FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", str(out_mp4)], stdin=subprocess.PIPE)
    sheet = []

    def emit(img, t):
        if enc:
            enc.stdin.write(img.tobytes())
        elif any(abs(t - s) < 0.5 / FPS for s in stills):
            sheet.append((t, img.resize((480, 270))))

    c = spec["card"]
    bg = card_bg(next(frames_at(src, c["bg_at"], [c["bg_at"]])))
    for k in range(round(c["dur"] * FPS)):
        emit(card(spec, k / FPS, bg), k / FPS)
    last = None
    fx = set(spec.get("fx", []))
    nxt_freeze = {id(a): b.get("type") == "freeze" for a, b in zip(spec["shots"], spec["shots"][1:])}
    for s in spec["shots"]:
        n = round(s["out_dur"] * FPS)
        if s.get("type") == "freeze":
            for k in range(n):
                emit(freeze(last, s, k / FPS), s["out_start"] + k / FPS)
            continue
        sp = s.get("speed", 1.0)
        z = s.get("zoom", 1.0)
        z0, z1 = z if isinstance(z, list) else (z, z)
        for k, fr in enumerate(frames_at(src, s["in"], [s["in"] + (k / FPS) * sp for k in range(n)])):
            t = s["out_start"] + k / FPS
            kick, flash = hit_fx(t, hits)
            raw = zoomed(fr, (z0 + (z1 - z0) * k / max(n - 1, 1)) * (1 + kick), s.get("center", (W / 2, H / 2)))
            if "shake" in fx:
                raw = shake(raw, t, hits)
            last = raw
            sat = 1.0
            if "hold" in fx and nxt_freeze.get(id(s)):                  # drain colour into the freeze
                sat = 1 - 0.8 * ease(1 - (n - k) / FPS / 0.5)
            img = finish(raw, flash=flash, sat=sat)
            if "vignette" in fx:
                img = tension_vignette(img, t, hits)
            if "edge_glow" in fx:
                img = edge_glow(img, t, hits)
            if s.get("tag", True):
                tag(img, spec, t, hits)
            else:
                img.paste(corner_panel(), (0, 0), corner_panel())      # still hide broadcast badges in that corner
            if s.get("jump"):
                jump_tag(img, s["jump"], k)
            if s.get("lower_third"):
                lower(img, s["lower_third"], k / FPS)
            if s.get("fade_out") and (n - k) / FPS < s["fade_out"]:
                img = finish(img, dim=(n - k) / FPS / s["fade_out"])
            emit(img, t)
    if enc:
        enc.stdin.close(); enc.wait()
    return total, hits, sheet


def main():
    spec_path = pathlib.Path(sys.argv[1])
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if "auto" in spec:
        spec["shots"] = auto_shots(spec)
        print("shots:", [(s.get("in"), s.get("out"), s.get("jump", "")) for s in spec["shots"] if "in" in s])
    if "sfx" not in spec:
        spec["sfx"] = default_sfx(spec)
    spec.setdefault("vod_audio", [])
    out = HERE / "highlights"
    name = spec_path.stem
    if "--stills" in sys.argv:
        total, hits = build_timeline(spec)
        marks = sorted([0.15, 0.4, spec["card"]["dur"] - 0.1] + [s["out_start"] + s["out_dur"] * f for s in spec["shots"] for f in (0.1, 0.6)]
                       + [h + 0.05 for h in hits if h])
        _, _, sheet = render(spec, None, stills=marks)
        cols = 4
        img = Image.new("RGB", (480 * cols, 270 * math.ceil(len(sheet) / cols)))
        for i, (t, im) in enumerate(sheet):
            ImageDraw.Draw(im).text((6, 4), f"{t:.2f}", fill=(255, 0, 255), font=font(22))
            img.paste(im, ((i % cols) * 480, (i // cols) * 270))
        img.save(out / f"{name}_sheet.jpg", quality=85)
        print("sheet:", out / f"{name}_sheet.jpg")
        return
    pic, wav, final = out / f"{name}_pic.mp4", out / f"{name}.wav", out / f"{name}.mp4"
    if "--audio-only" in sys.argv and pic.exists():          # picture unchanged: just redo the sound
        total, hits = build_timeline(spec)
    else:
        total, hits, _ = render(spec, pic)
    mix_audio(spec, total, hits, wav)
    if spec.get("caster"):
        add_caster(spec, total, wav)
    subprocess.run([FF, "-v", "error", "-y", "-i", str(pic), "-i", str(wav), "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
                    "-shortest", str(final)], check=True)
    print("done:", final)


def add_caster(spec, total, wav):
    """Caster audio = one continuous piece of the source clip's own audio, exactly as long as the finished highlight,
    laid under the whole highlight. The user gives either where it starts or where it ends (source-clip time)."""
    c = spec["caster"]
    start = c["start"] if "start" in c else c["end"] - total
    start = max(start, 0.0)
    tmp = wav.with_name(wav.stem + "_sfx.wav")
    wav.replace(tmp)
    fade = c.get("fade_out", 0.4)
    filt = (f"[0:a]atrim={start:.3f}:{start + total:.3f},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,"
            f"volume={c.get('gain', 0)}dB,afade=t=in:d=0.12,afade=t=out:st={total - fade:.3f}:d={fade}[cast];"
            f"[1:a]volume={c.get('sfx_gain', -18)}dB[fx];"
            f"[cast][fx]amix=inputs=2:normalize=0:duration=longest,atrim=0:{total:.3f},alimiter=limit=0.89[out]")
    subprocess.run([FF, "-v", "error", "-y", "-i", str(ROOT / spec["source"]), "-i", str(tmp), "-filter_complex", filt,
                    "-map", "[out]", "-ar", "48000", str(wav)], check=True)
    tmp.unlink()
    print(f"caster: source {start:.2f}–{start + total:.2f} s under the whole {total:.2f} s highlight")


if __name__ == "__main__":
    main()
