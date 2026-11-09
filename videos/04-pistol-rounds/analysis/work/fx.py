"""Rapid-edit effects for video 04, built from CS2's own interface (kill feed, hitmarkers, money HUD, round history,
bomb timer, AWP scope) plus cut effects (punch-in, RGB split, whip-pan, flash, shake, speed ramp).
All functions draw onto a PIL RGB image in place (or return a new image where noted)."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from engine import W, H, FPS, font, ease, YELLOW, WHITE, LOSS, WIN, MUTED

CT_BLUE, T_GOLD, KF_RED = (93, 156, 236), (232, 184, 74), (214, 50, 50)


# ---------- cut effects ----------
def punch(img, t, at, amount=0.08, decay=0.12):
    """Zoom punch-in that snaps on `at` and settles (returns new image)."""
    if t < at:
        return img
    z = 1 + amount * math.exp(-(t - at) / decay)
    if z < 1.002:
        return img
    w, h = W / z, H / z
    return img.resize((W, H), Image.BICUBIC, box=((W - w) / 2, (H - h) / 2, (W + w) / 2, (H + h) / 2))


def shake(img, t, at, amp=18, decay=0.09):
    if t < at or t - at > 0.45:
        return img
    a = amp * math.exp(-(t - at) / decay)
    dx, dy = a * math.sin((t - at) * 140), a * math.cos((t - at) * 113)
    big = img.resize((int(W * 1.04), int(H * 1.04)), Image.BILINEAR)
    return big.crop((int(W * 0.02 + dx), int(H * 0.02 + dy), int(W * 0.02 + dx) + W, int(H * 0.02 + dy) + H))


def rgb_split(img, strength):
    """Chromatic glitch: R and B channels pushed apart horizontally (returns new image)."""
    if strength <= 0.5:
        return img
    r, g, b = img.split()
    s = int(strength)
    r = r.transform(img.size, Image.AFFINE, (1, 0, s, 0, 1, 0))
    b = b.transform(img.size, Image.AFFINE, (1, 0, -s, 0, 1, 0))
    return Image.merge("RGB", (r, g, b))


def glitch_at(img, t, at, dur=0.18, px=26):
    if 0 <= t - at < dur:
        img = rgb_split(img, px * (1 - (t - at) / dur))
        if (t - at) < dur * 0.5:                                  # one displaced slice for 2-3 frames
            y = int((at * 997) % (H - 120))
            sl = img.crop((0, y, W, y + 90))
            img.paste(sl, (int(40 * math.sin(at * 31)), y))
    return img


def flash(img, t, at, dur=0.1, strength=0.8, col=(255, 255, 255)):
    if 0 <= t - at < dur:
        a = strength * (1 - (t - at) / dur)
        return Image.blend(img, Image.new("RGB", (W, H), col), a)
    return img


def whip(a_img, b_img, p):
    """Whip-pan from frame a to frame b, p in 0..1 (returns new image): slide + heavy horizontal blur."""
    p = min(max(p, 0), 1)
    off = int(W * (p * p * (3 - 2 * p)))
    canvas = Image.new("RGB", (W, H))
    canvas.paste(a_img, (-off, 0))
    canvas.paste(b_img, (W - off, 0))
    blur = int(60 * math.sin(math.pi * p))
    if blur > 2:
        arr = np.asarray(canvas, dtype=np.float32)
        k = blur
        cs = np.cumsum(np.pad(arr, ((0, 0), (k, k), (0, 0)), mode="edge"), axis=1)
        arr = (cs[:, 2 * k:] - cs[:, :-2 * k]) / (2 * k)
        canvas = Image.fromarray(arr[:, :W].clip(0, 255).astype(np.uint8))
    return canvas


def speed_ramp(local, slow_at, slow_len=0.6, factor=0.3):
    """Map clip-local output time to source time: normal speed, a slow-motion window around `slow_at`
    (source time), then normal again. Returns source time."""
    pre = slow_at - slow_len / 2
    if local <= pre:
        return local
    slow_out = slow_len / factor
    if local <= pre + slow_out:
        return pre + (local - pre) * factor
    return pre + slow_len + (local - pre - slow_out)


def vignette_pulse(img, strength):
    if strength <= 0.01:
        return img
    yy, xx = np.ogrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    m = np.clip((r - 0.55) / 0.8, 0, 1)[..., None] * strength
    arr = np.asarray(img, dtype=np.float32) * (1 - m)
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))


# ---------- CS2 interface motifs ----------
def killfeed(img, entries, t, x_right=W - 40, y0=60, maxn=5):
    """CS2-style kill feed. entries: [(t_on, left, weapon, right, highlight)] newest at the bottom; each slides in
    from the right and stays. highlight -> red border like the local player's kills."""
    d = ImageDraw.Draw(img, "RGBA")
    shown = [e for e in entries if t >= e[0]]
    for i, (t_on, left, weapon, right, hl) in enumerate(shown[-maxn:]):
        p = ease((t - t_on) / 0.16)
        f, fw = font(34, "SemiBold"), font(30, "Bold")
        wl, ww, wr = d.textlength(left, font=f), d.textlength(weapon, font=fw), d.textlength(right, font=f)
        bw = wl + ww + wr + 90
        x = x_right - bw + 80 * (1 - p)
        y = y0 + i * 62
        d.rectangle([x, y, x + bw, y + 50], fill=(10, 10, 12, 190), outline=(KF_RED + (255,)) if hl else None, width=3)
        d.text((x + 18, y + 25), left, font=f, fill=CT_BLUE + (255,), anchor="lm")
        d.text((x + 34 + wl, y + 25), weapon, font=fw, fill=WHITE + (255,), anchor="lm")
        d.text((x + 50 + wl + ww, y + 25), right, font=f, fill=T_GOLD + (255,), anchor="lm")


def hitmarker(img, cx, cy, t, at, size=46, col=(255, 255, 255), hs=False):
    """Hitmarker X that pops and fades; hs=True draws it red with a small headshot ring."""
    if not 0 <= t - at < 0.35:
        return
    d = ImageDraw.Draw(img)
    p = (t - at) / 0.35
    s = size * (0.7 + 0.5 * ease(p * 3))
    c = (230, 50, 50) if hs else col
    a = 1 - p
    c = tuple(int(v * a + 20 * (1 - a)) for v in c)
    gap = s * 0.35
    for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        d.line([(cx + sx * gap, cy + sy * gap), (cx + sx * s, cy + sy * s)], fill=c, width=7)
    if hs:
        d.ellipse([cx - s * 1.25, cy - s * 1.25, cx + s * 1.25, cy + s * 1.25], outline=c, width=4)


def money(img, x, y, value, t, t_on, frm=None, dur=0.6, size=96, col=(120, 214, 110), anchor="lm"):
    """CS2 money counter: green $ value that rolls from `frm` to `value`."""
    if t < t_on:
        return
    v = value if frm is None else frm + (value - frm) * ease((t - t_on) / dur)
    d = ImageDraw.Draw(img)
    s = f"${int(round(v)):,}"
    d.text((x + 5, y + 5), s, font=font(size), fill=(0, 0, 0), anchor=anchor)
    d.text((x, y), s, font=font(size), fill=col, anchor=anchor)


def round_history(img, x, y, results, t, t0, step=0.35, size=84, labels=None):
    """CS2 round-history strip: one tile per round, filled as time passes. results: 'W' / 'L' / '?'."""
    d = ImageDraw.Draw(img)
    for i, r in enumerate(results):
        on = t >= t0 + i * step
        p = ease((t - t0 - i * step) / 0.18) if on else 0
        xx = x + i * (size + 16)
        col = {"W": WIN, "L": LOSS, "?": (90, 96, 110)}[r] if on else (40, 44, 54)
        sz = size * (1.2 - 0.2 * p) if on else size
        d.rounded_rectangle([xx + (size - sz) / 2, y + (size - sz) / 2, xx + (size + sz) / 2, y + (size + sz) / 2], 10, fill=col)
        if on:
            cx, cy, k = xx + size / 2, y + size / 2, size * 0.22
            if r == "W":
                d.line([(cx - k, cy), (cx - k * 0.3, cy + k * 0.8), (cx + k * 1.1, cy - k * 0.9)], fill=(255, 255, 255), width=8)
            elif r == "L":
                d.line([(cx - k, cy - k), (cx + k, cy + k)], fill=(255, 255, 255), width=8)
                d.line([(cx - k, cy + k), (cx + k, cy - k)], fill=(255, 255, 255), width=8)
            else:
                d.text((cx, cy), "?", font=font(int(size * 0.55)), fill=(255, 255, 255), anchor="mm")
        if labels:
            d.text((xx + size / 2, y + size + 30), labels[i], font=font(26, "SemiBold"), fill=MUTED, anchor="mm")


def bomb_timer(img, cx, cy, value, t, blink_rate, k=1.0):
    """Red LED bomb-timer digits; the dot blinks at blink_rate (Hz). k scales the whole box."""
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([cx - 260 * k, cy - 90 * k, cx + 260 * k, cy + 90 * k], 18, fill=(18, 20, 18), outline=(60, 64, 60), width=4)
    on = int(t * blink_rate * 2) % 2 == 0
    d.ellipse([cx - 230 * k, cy - 18 * k, cx - 194 * k, cy + 18 * k], fill=(255, 40, 40) if on else (70, 20, 20))
    d.text((cx + 30 * k, cy), value, font=font(int(110 * k)), fill=(255, 60, 60), anchor="mm")


def scope_reveal(img_under, img_over, p):
    """AWP-scope wipe: img_over appears inside a growing circle with crosshair lines (returns new image)."""
    p = min(max(p, 0), 1)
    r = int(1200 * (p ** 1.6))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).ellipse([W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r], fill=255)
    out = Image.composite(img_over, img_under, mask)
    if 0.02 < p < 0.98:
        d = ImageDraw.Draw(out)
        d.ellipse([W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r], outline=(0, 0, 0), width=26)
        d.line([(W / 2 - r, H / 2), (W / 2 + r, H / 2)], fill=(0, 0, 0), width=3)
        d.line([(W / 2, H / 2 - r), (W / 2, H / 2 + r)], fill=(0, 0, 0), width=3)
    return out


def word_pop(img, s, x, y, t, t_on, size=150, col=WHITE, anchor="mm", overshoot=0.35):
    """Kinetic word with a spring overshoot (1.35 -> 0.95 -> 1.0)."""
    if t < t_on:
        return
    u = min((t - t_on) / 0.28, 1)
    sc = 1 + overshoot * math.exp(-6 * u) * math.cos(9 * u)
    d = ImageDraw.Draw(img)
    f = font(max(10, int(size * sc)))
    d.text((x + 7, y + 9), s, font=f, fill=(0, 0, 0), anchor=anchor)
    d.text((x, y), s, font=f, fill=col, anchor=anchor)


def fit(d, s, size, wmax, style="Bold"):
    """Largest font size <= size that keeps s within wmax pixels."""
    while size > 20 and d.textlength(s, font=font(size, style)) > wmax:
        size -= 4
    return size


def takeaway(img, t, t_on, n, lines, bg=(14, 17, 23)):
    """Conclusion card: the analysis behind it dims, a 'TAKEAWAY #n' tag and 1-3 big lines settle in the centre and
    stay. lines: [(text, colour)]. Returns a new image. Captions stay free below y 900."""
    if t < t_on:
        return img
    p = min(1.0, (t - t_on) / 0.35)
    img = Image.blend(img, Image.new("RGB", (W, H), bg), p)
    d = ImageDraw.Draw(img)
    from engine import block_text
    block_text(img, (W / 2, 250), f"TAKEAWAY #{n}", 40, (12, 12, 14), YELLOW, a=ease((t - t_on) / 0.25), anchor="m", pad=(22, 12))
    total = len(lines)
    y0 = 520 - (total - 1) * 70
    for i, (s, col) in enumerate(lines):
        at = t_on + 0.15 + i * 0.35
        if t < at:
            continue
        q = ease((t - at) / 0.3)
        size = fit(d, s, 104, 1700)
        y = y0 + i * 140 + 30 * (1 - q)
        c = tuple(int(BGc + (v - BGc) * q) for v, BGc in zip(col, bg))
        d.text((W / 2 + 5, y + 7), s, font=font(size), fill=(0, 0, 0), anchor="mm")
        d.text((W / 2, y), s, font=font(size), fill=c, anchor="mm")
    return img
