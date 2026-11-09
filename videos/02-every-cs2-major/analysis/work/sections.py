"""Video 02 sections: one function per narration beat, rendered to clips/<sid>.mp4 with the Brian voice and captions.

python sections.py s00 s01 ...     (no arguments: every section in ORDER)

Style rules carried over from video 03 (user, 2026-10-20): real footage mixed in often (not a school stats board),
stat boards graphical and satisfying, every number over footage sits on a solid block (block_text / side_shade).
Team "logos" are our own text badges in the team colour (no real logos).
"""
import math, sys
from PIL import Image, ImageDraw, ImageFilter

from engine import *          # noqa: F401,F403  (canvas, text, rrect, block_text, side_shade, Footage, Words, ...)

CLIPDIR = ROOT / "footage" / "clips"
ORDER = ["s00", "s01", "s02", "s03", "s04", "s05", "s06", "s07"]
INK = (12, 12, 14)
GOLD = YELLOW
SILVER = (196, 204, 216)

TEAM = {  # key: (badge text, badge colour, text colour, outline)
    "navi": ("NAVI", (255, 214, 0), INK, None), "spirit": ("SPIRIT", (214, 219, 228), INK, None),
    "vit": ("VITALITY", (16, 16, 18), (255, 221, 0), (255, 221, 0)), "falcons": ("FALCONS", (0, 156, 96), WHITE, None),
    "faze": ("FAZE", (222, 36, 48), WHITE, None), "mouz": ("MOUZ", (196, 30, 70), WHITE, None),
    "g2": ("G2", (238, 238, 238), INK, None), "mongolz": ("THE MONGOLZ", (232, 112, 32), WHITE, None),
    "tl": ("LIQUID", (30, 98, 196), WHITE, None), "pain": ("paiN", (176, 18, 30), WHITE, None),
    "furia": ("FURIA", (26, 26, 28), WHITE, (200, 200, 200)), "ef": ("ETERNAL FIRE", (236, 116, 20), WHITE, None),
    "c9": ("CLOUD9", (36, 150, 224), WHITE, None), "betboom": ("BETBOOM", (150, 70, 210), WHITE, None),
    "9z": ("9z", (24, 24, 26), (0, 226, 196), (0, 226, 196)), "heroic": ("HEROIC", (240, 240, 240), INK, None),
    "aurora": ("AURORA", (120, 60, 200), WHITE, None),
}


# ---------- helpers ----------
def clip(name, start, dur, zoom=(1.0, 1.08), focus=(0.5, 0.5)):
    return Footage(CLIPDIR / f"{name}.mp4", start, dur, zoom, focus)


def show(img, fx, local, dim=0.0, blur=0, sat=1.0):
    """Paste a footage frame over the whole canvas, optionally darkened, blurred or desaturated."""
    fr = fx.frame(local)
    if blur:
        fr = fr.filter(ImageFilter.GaussianBlur(blur))
    if sat != 1.0:
        g = fr.convert("L").convert("RGB")
        fr = Image.blend(g, fr, max(0.0, min(1.0, sat)))
    if dim > 0:
        fr = Image.blend(fr, Image.new("RGB", (W, H), (0, 0, 0)), min(dim, 1.0))
    img.paste(fr)


def badge(img, x, y, key, h=64, a=1.0, anchor="l"):
    """Team badge: solid slanted block in the team colour. Returns its width."""
    if a <= 0.01:
        return 0
    label, bg, fg, outline = TEAM[key]
    d = ImageDraw.Draw(img)
    f = font(int(h * 0.56))
    tw = d.textlength(label, font=f)
    w = tw + h * 0.9
    if anchor == "m":
        x -= w / 2
    x -= 30 * (1 - a)
    lay = Image.new("RGBA", (int(w + 16), int(h)), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    sk = h * 0.18
    al = int(255 * a)
    ld.polygon([(sk, 0), (w + sk, 0), (w, h - 1), (0, h - 1)], fill=bg + (al,), outline=(outline + (al,)) if outline else None)
    ld.text((w / 2 + sk / 2, h / 2), label, font=f, fill=fg + (al,), anchor="mm")
    img.paste(lay, (int(x), int(y)), lay)
    return w


def stamp(img, s, cx, cy, t, t_on, col=LOSS, size=96, angle=-10):
    """Rubber stamp that thumps in (scale 1.4 -> 1.0)."""
    if t < t_on:
        return
    a = ease((t - t_on) / 0.16)
    sc = 1.4 - 0.4 * a
    f = font(int(size * sc))
    tmp = Image.new("RGBA", (1400, 400), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    tw = td.textlength(s, font=f)
    pad = 26 * sc
    al = int(240 * a)
    td.rectangle([700 - tw / 2 - pad, 200 - size * sc * 0.62 - pad / 2, 700 + tw / 2 + pad, 200 + size * sc * 0.62 + pad / 2],
                 outline=col + (al,), width=max(5, int(9 * sc)))
    td.text((700, 200), s, font=f, fill=col + (al,), anchor="mm")
    tmp = tmp.rotate(angle, resample=Image.BICUBIC)
    img.paste(tmp, (int(cx - 700), int(cy - 200)), tmp)


def kinetic(img, s, t, t_on, y=H / 2, size=170, col=WHITE, block=None, t_off=None, anchor="m", x=W / 2):
    """Big word slamming in (scale 1.35 -> 1) and optionally out; on a solid block when block is given."""
    if t < t_on or (t_off is not None and t > t_off + 0.15):
        return
    a = ease((t - t_on) / 0.14)
    if t_off is not None and t > t_off:
        a *= 1 - (t - t_off) / 0.15
    size_now = int(size * (1.35 - 0.35 * ease((t - t_on) / 0.14)))
    if block:
        block_text(img, (x, y - size_now * 0.6), s, size_now, col, block, a=a, anchor=anchor, pad=(36, 20))
    else:
        d = ImageDraw.Draw(img)
        f = font(size_now)
        d.text((x + 6, y + 8), s, font=f, fill=(0, 0, 0), anchor="mm")
        d.text((x, y), s, font=f, fill=col, anchor="mm")


def title(d, s, t, t0, y=96, x=110, size=46, col=YELLOW):
    a = ramp(t, t0, 0.35)
    text(d, (x, y + 12 * (1 - a)), s, size, col, alpha=a, tracking=4)
    if a > 0:
        d.rectangle([x, y + size + 18, x + 90 * a, y + size + 24], fill=col)


def flash(img, t, at, dur=0.12, strength=0.75):
    if 0 <= t - at < dur:
        a = strength * (1 - (t - at) / dur)
        img.paste(Image.blend(img, Image.new("RGB", (W, H), (255, 255, 255)), a))


# ---------- s00: cold open (p01) ----------
def s00():
    lead = 0.15
    w = Words("p01", lead)
    t_four, t_two, t_three = w("Four"), w("two"), w("three")
    t_this, t_champ, t_under, t_mvp, t_mom = w("This"), w("champions", 1), w("underdogs"), w("MVPs"), w("moments")
    t_end, t_you = w("And", 2), w("You")
    cuts = [  # (start time, footage, local offset)
        (0.0, clip("A2", 36.5, 1.5, (1.05, 1.15)), 0),
        (t_four, clip("C1", 33.0, 0.5, (1.0, 1.06)), 0),
        (t_four + 0.4, clip("S3", 32.0, 0.5, (1.0, 1.06)), 0),
        (t_four + 0.8, clip("B5", 28.2, 0.5, (1.0, 1.06)), 0),
        (t_four + 1.2, clip("K2", 22.2, 0.6, (1.0, 1.06)), 0),
        (t_two - 0.6, clip("B5", 28.8, 2.4, (1.0, 1.1)), 0),
        (w("and", 0) - 0.1, clip("S1", 44.0, 1.9, (1.0, 1.1), (0.55, 0.45)), 0),
        (w("lost") - 0.4, clip("S5", 20.0, 2.0, (1.0, 1.08)), 0),
        (t_champ - 0.05, clip("S3", 33.0, 1.2, (1.0, 1.08)), 0),
        (t_under - 0.05, clip("A2", 29.0, 1.3, (1.0, 1.08)), 0),
        (t_mvp - 0.05, clip("S1", 42.0, 1.2, (1.0, 1.08)), 0),
        (t_mom - 0.05, clip("K1", 13.0, 2.3, (1.15, 1.25)), 0),
    ]
    fx_end = t_end - 0.05
    title_on, title_off = t_this - 0.1, t_champ - 0.1

    def draw(img, t):
        d = ImageDraw.Draw(img)
        if title_on <= t < title_off:                                      # title card on the plain canvas
            a = ramp(t, title_on, 0.3)
            text(d, (W / 2, 330), "SPORTS ON THE LINE", 40, YELLOW, anchor="mm", alpha=a, tracking=10)
            sc = 1.3 - 0.3 * ease((t - title_on) / 0.2)
            f = font(int(150 * sc))
            d.text((W / 2, 500), "EVERY CS2 MAJOR", font=f, fill=WHITE, anchor="mm")
            block_text(img, (W / 2, 610), "SO FAR  ·  2024–2026", 64, INK, YELLOW, a=ramp(t, title_on + 0.25, 0.3), anchor="m")
            flash(img, t, title_on)
            return
        if t >= fx_end:                                                     # all-star teaser: 5 empty slots
            roles = ["IGL", "AWP", "RIFLER", "RIFLER", "ANCHOR"]
            title(d, "THE ALL-STAR TEAM OF THE CS2 ERA", t, fx_end, y=150, x=W / 2 - 520, size=50)
            for i, r in enumerate(roles):
                a = ramp(t, fx_end + 0.25 + i * 0.12, 0.3)
                x0 = 210 + i * 310
                rrect(d, (x0, 280 + 30 * (1 - a), x0 + 260, 620 + 30 * (1 - a)), 18, fill=fade(PANEL, a), outline=fade(LINE, a), width=3)
                text(d, (x0 + 130, 420 + 30 * (1 - a)), "?", 150, YELLOW, anchor="mm", alpha=a)
                text(d, (x0 + 130, 575 + 30 * (1 - a)), r, 34, MUTED, anchor="mm", alpha=a, tracking=4)
            if t >= t_you:
                stamp(img, "YOU WON'T AGREE", W / 2, 750, t, t_you + 0.2, col=YELLOW, size=64, angle=-4)
            return
        cur = None
        for st, fx, off in cuts:
            if t >= st:
                cur = (st, fx, off)
        st, fx, off = cur
        show(img, fx, t - st + off, dim=0.25)
        flash(img, t, st, strength=0.5)
        side_shade(img, 0.6, frac=0.9, strength=0.55)
        kinetic(img, "FIVE MAJORS", t, w("Five"), size=180, t_off=t_four - 0.05)
        if t_four <= t < t_two - 0.6:
            kinetic(img, "FOUR CHAMPIONS", t, t_four, size=170)
            names = ["NAVI", "SPIRIT", "VITALITY", "FALCONS"]
            k = min(3, int((t - t_four) / 0.4))
            block_text(img, (W / 2, 640), names[k], 60, INK, YELLOW, anchor="m")
        if t_two - 0.6 <= t < w("and", 0) - 0.1:
            kinetic(img, "TWO IN A ROW", t, t_two - 0.3, size=150)
            block_text(img, (W / 2, 640), "VITALITY", 60, (255, 221, 0), INK, anchor="m")
        if w("and", 0) - 0.1 <= t < title_on:
            n = 1 + min(2, int(max(0.0, t - t_three) / 0.33)) if t >= t_three else 0
            if n:
                block_text(img, (140, 300), "FAZE", 70, WHITE, (222, 36, 48))
                text(d, (140, 520), f"{n}", 260, WHITE, anchor="lm")
                text(d, (330, 540), "FINALS", 90, WHITE, anchor="lm")
            stamp(img, "0 TITLES", 1250, 470, t, w("lost"), size=130)
        words = [(t_champ, "THE CHAMPIONS"), (t_under, "THE UNDERDOGS"), (t_mvp, "THE MVPs"), (t_mom, "THE MOMENTS")]
        for i, (tw_, s) in enumerate(words):
            nxt = words[i + 1][0] if i + 1 < len(words) else fx_end
            if tw_ - 0.05 <= t < nxt:
                kinetic(img, s, t, tw_ - 0.05, size=150, col=INK, block=YELLOW, t_off=nxt - 0.2)

    sfx = [(w("Five") - 0.05, "stinger-hit-short", -6), (t_four, "whoosh-short", -10)] + \
          [(t_four + k * 0.4, "click-sharp", -8) for k in range(4)] + \
          [(t_two - 0.6, "whoosh-medium-1s", -12), (w("and", 0), "whoosh-reverse-1s", -12)] + \
          [(t_three + k * 0.33, "dry-thud", -6) for k in range(3)] + [(w("lost"), "stamp-thud", -3),
          (title_on, "stinger-energetic-hit", -6)] + [(x - 0.05, "whoosh-short", -10) for x in (t_champ, t_under, t_mvp, t_mom)] + \
          [(fx_end, "send-whoosh-up", -10), (t_you + 0.2, "stamp-thud", -5)]
    render_section("s00", "p01", draw, sfx=sfx, lead=lead, tail=0.5, caption_style="Box")


# ---------- s01: four champions, trophy shelf (p02) ----------
MAJORS = [("COPENHAGEN", "MAR 2024", "navi"), ("SHANGHAI", "DEC 2024", "spirit"), ("AUSTIN", "JUN 2025", "vit"),
          ("BUDAPEST", "DEC 2025", "vit"), ("COLOGNE", "JUN 2026", "falcons")]


def trophy(d, cx, cy, s, col):
    """Simple cup icon."""
    d.pieslice([cx - s * 0.5, cy - s * 0.75, cx + s * 0.5, cy + s * 0.25], 0, 180, fill=col)
    d.rectangle([cx - s * 0.5, cy - s * 0.3, cx + s * 0.5, cy - s * 0.25], fill=col)
    hw = max(3, int(s * 0.07))
    d.arc([cx - s * 0.72, cy - s * 0.6, cx - s * 0.28, cy - s * 0.05], 90, 270, fill=col, width=hw)
    d.arc([cx + s * 0.28, cy - s * 0.6, cx + s * 0.72, cy - s * 0.05], 270, 450, fill=col, width=hw)
    d.rectangle([cx - s * 0.07, cy + s * 0.2, cx + s * 0.07, cy + s * 0.45], fill=col)
    d.rectangle([cx - s * 0.3, cy + s * 0.45, cx + s * 0.3, cy + s * 0.55], fill=col)


def s01():
    lead = 0.15
    w = Words("p02", lead)
    fills = [w("Copenhagen"), w("Shanghai"), w("Austin"), w("Budapest"), w("Cologne")]
    bgfx = clip("S3", 31.0, 4.0, (1.0, 1.1))

    def draw(img, t):
        show(img, bgfx, min(t, 3.9) * 0.6, dim=0.78, blur=6, sat=0.3)
        d = ImageDraw.Draw(img)
        title(d, "THE CHAMPIONS", t, 0.2)
        if t >= w("four"):
            a = ramp(t, w("four"), 0.3)
            block_text(img, (110, 210), "4 DIFFERENT TEAMS", 56, INK, YELLOW, a=a)
        for i, (city, date, key) in enumerate(MAJORS):
            x0 = 120 + i * 345
            a = ramp(t, 0.5 + i * 0.12, 0.35)
            rrect(d, (x0, 330 + 20 * (1 - a), x0 + 315, 780 + 20 * (1 - a)), 20, fill=fade(PANEL, a * 0.92), outline=fade(LINE, a), width=3)
            text(d, (x0 + 157, 380), city, 40, WHITE, anchor="mm", alpha=a)
            text(d, (x0 + 157, 425), date, 28, MUTED, anchor="mm", alpha=a, tracking=3)
            on = t >= fills[i]
            p = ease((t - fills[i]) / 0.25) if on else 0
            trophy(d, x0 + 157, 560 - 10 * p, 120, fade(GOLD if on else DIM, a))
            if on:
                badge(img, x0 + 157, 690 - 30 * (1 - p), key, h=62, a=p, anchor="m")
        if t >= w("twice"):
            a = ramp(t, w("twice"), 0.3)
            d.line([(120 + 2 * 345 + 40, 815), (120 + 4 * 345 - 40, 815)], fill=fade((255, 221, 0), a), width=6)
            block_text(img, (120 + 3 * 345 - 20 + 157 - 150, 835), "BACK-TO-BACK", 44, INK, (255, 221, 0), a=a)
        for f_ in fills:
            flash(img, t, f_, dur=0.1, strength=0.25)

    sfx = [(0.2, "whoosh-soft", -12), (w("four"), "stamp-thud", -8)] + [(f_, "impact-soft-2", -6) for f_ in fills] + \
          [(w("twice"), "pop-1", -8)]
    render_section("s01", "p02", draw, sfx=sfx, lead=lead)


# ---------- s02: never missed the playoffs (p03) ----------
PLAYOFF = {"spirit": [1, 1, 1, 1, 1], "vit": [1, 1, 1, 1, 1], "faze": [1, 1, 1, 1, 0], "mouz": [1, 1, 1, 1, 0],
           "navi": [1, 0, 1, 1, 0], "g2": [1, 1, 0, 0, 1], "mongolz": [0, 1, 1, 1, 0], "furia": [0, 0, 1, 1, 1]}


def s02():
    lead = 0.15
    w = Words("p03", lead)
    t_sp, t_vi = w("Spirit"), w("Vitality")
    rows = list(PLAYOFF.items())

    def draw(img, t):
        d = ImageDraw.Draw(img)
        title(d, "PLAYOFF RUNS  ·  5 MAJORS", t, 0.1)
        cols = ["CPH 24", "SHA 24", "AUS 25", "BUD 25", "COL 26"]
        gx, gy, cw, ch = 640, 220, 210, 72
        for j, c in enumerate(cols):
            text(d, (gx + j * cw + cw / 2, gy - 30), c, 30, MUTED, anchor="mm", alpha=ramp(t, 0.2, 0.3), tracking=2)
        for i, (key, runs) in enumerate(rows):
            y = gy + 20 + i * ch
            a = ramp(t, 0.3 + i * 0.06, 0.3)
            gold = (key == "spirit" and t >= t_sp) or (key == "vit" and t >= t_vi)
            dim_other = t >= t_sp and not gold
            badge(img, 160, y, key, h=58, a=a * (0.45 if dim_other else 1.0))
            for j, r in enumerate(runs):
                x = gx + j * cw
                p = ramp(t, 0.5 + i * 0.06 + j * 0.05, 0.25)
                if r:
                    col = GOLD if gold else (fade(WIN, 0.55) if dim_other else WIN)
                    rrect(d, (x + 14, y + 8, x + cw - 14, y + 8 + 42 * p), 8, fill=col)
                else:
                    rrect(d, (x + 14, y + 8, x + cw - 14, y + 50), 8, outline=fade(LINE, a), width=2)
            if gold:
                p = ramp(t, t_sp if key == "spirit" else t_vi, 0.3)
                block_text(img, (gx + 5 * cw + 30, y + 2), "5 / 5", 44, INK, YELLOW, a=p)
        if t >= w("Five", 0):
            block_text(img, (W / 2, 830), "FIVE MAJORS  ·  FIVE PLAYOFF RUNS EACH", 48, WHITE, INK, a=ramp(t, w("Five", 0), 0.3), anchor="m")

    sfx = [(0.1, "whoosh-soft", -12), (t_sp, "success-chime", -10), (t_vi, "success-chime", -10)]
    render_section("s02", "p03", draw, sfx=sfx, lead=lead)


# ---------- s03: FaZe, three finals three losses (p04) ----------
def s03():
    lead = 0.15
    w = Words("p04", lead)
    bgfx = clip("S1", 44.0, 2.0, (1.05, 1.15), (0.55, 0.45))
    finals = [("COPENHAGEN 2024", "navi", "1–2"), ("SHANGHAI 2024", "spirit", "1–2"), ("BUDAPEST 2025", "vit", "1–3")]
    t_cards = [w("Three", 0) + k * 0.25 for k in range(3)]

    def draw(img, t):
        show(img, bgfx, min(t, 1.9), dim=0.45, sat=0.6)
        side_shade(img, 1.0, frac=0.75)
        block_text(img, (110, 150), "FAZE", 90, WHITE, (222, 36, 48), a=ramp(t, w("FaZe"), 0.2))
        d = ImageDraw.Draw(img)
        for k, (ev, opp, score) in enumerate(finals):
            if t < t_cards[k]:
                continue
            a = ease((t - t_cards[k]) / 0.2)
            y = 330 + k * 170
            rrect(d, (110 - 40 * (1 - a), y, 900 - 40 * (1 - a), y + 140), 14, fill=(16, 18, 24), outline=LINE, width=2)
            text(d, (140, y + 26), "GRAND FINAL  ·  " + ev, 28, MUTED, tracking=2)
            text(d, (140, y + 72), "FAZE", 56, WHITE)
            text(d, (330, y + 72), score, 56, WHITE)
            badge(img, 470, y + 70, opp, h=52)
            stamp(img, "L", 820, y + 70, t, w("Three", 1) + k * 0.18, size=80, angle=-8)
        if t >= w("losses"):
            block_text(img, (110, 860), "3 FINALS  ·  0 TITLES", 64, WHITE, LOSS, a=ramp(t, w("losses"), 0.25))

    sfx = [(w("FaZe"), "stinger-serious-low", -12)] + [(x, "dry-thud", -6) for x in t_cards] + \
          [(w("Three", 1) + k * 0.18, "stamp-thud", -4) for k in range(3)]
    render_section("s03", "p04", draw, sfx=sfx, lead=lead, tail=0.6, caption_style="Low")


# ---------- s04: 24 -> 32 teams (p05) ----------
def s04():
    lead = 0.15
    w = Words("p05", lead)
    t24, t32, tstage = w("24"), w("32"), w("brand-new")

    def draw(img, t):
        d = ImageDraw.Draw(img)
        title(d, "THE FIELD GREW", t, 0.1)
        n = 0
        if t >= t24:
            n = int(min(24, counter(24, t, t24, 0.6)))
        if t >= t32:
            n = 24 + int(min(8, counter(8, t, t32, 0.5)))
        for i in range(32):
            col, row = i % 8, i // 8
            x, y = 640 + col * 140, 300 + row * 130
            if i < n:
                new = i >= 24
                p = 1.0
                c = YELLOW if new else WHITE
                rrect(d, (x, y, x + 110, y + 100), 14, fill=c if not new else YELLOW)
                if new and t >= tstage:
                    pass
            else:
                rrect(d, (x, y, x + 110, y + 100), 14, outline=fade(LINE, 0.8), width=2)
        num = 24 if t < t32 else 32
        if t >= t24:
            sc = 1.0 + 0.25 * max(0.0, 1 - (t - (t32 if t >= t32 else t24)) / 0.2)
            text(d, (360, 470), str(num), int(260 * sc), YELLOW if num == 32 else WHITE, anchor="mm")
            text(d, (360, 640), "TEAMS", 60, MUTED, anchor="mm", tracking=6)
            text(d, (360, 720), "2024" if num == 24 else "FROM AUSTIN 2025", 34, MUTED, anchor="mm", tracking=3)
        if t >= tstage:
            a = ramp(t, tstage, 0.3)
            block_text(img, (640, 840), "NEW  STAGE 1  ·  FOR THE LONG SHOTS", 50, INK, YELLOW, a=a)

    sfx = [(t24, "click-sharp", -8), (t32, "stamp-thud", -6), (tstage, "pop-2", -8)]
    render_section("s04", "p05", draw, sfx=sfx, lead=lead)


# ---------- s05: Spirit, the overtime team (p06) ----------
def s05():
    lead = 0.15
    w = Words("p06", lead)
    bars = [(47, "SPIRIT 25–22 G2", "MIRAGE · COLOGNE QF", None), (46, "SPIRIT 25–21 MOUZ", "MIRAGE · AUSTIN QF", "STILL LOST 1–2"),
            (36, "SPIRIT 17–19 VITALITY", "MIRAGE · BUDAPEST SF", None), (35, "SPIRIT 19–16 FAZE", "NUKE · COPENHAGEN QF", None)]
    t_bars = w("four", 0) + 0.3
    t_all = w("All")
    t_47, t_46 = w("Twenty-five", 0), w("Twenty-five", 1)
    bgfx = clip("K1", 16.0, 3.0, (1.0, 1.08))

    def draw(img, t):
        if t < w("The", 0) - 0.1:                                          # opener on Spirit footage
            show(img, bgfx, t, dim=0.35)
            kinetic(img, "THE OVERTIME TEAM", t, 0.15, y=470, size=130, col=INK, block=YELLOW)
            block_text(img, (W / 2, 640), "TEAM SPIRIT", 56, WHITE, INK, a=ramp(t, 0.5, 0.3), anchor="m")
            return
        d = ImageDraw.Draw(img)
        title(d, "LONGEST PLAYOFF MAPS OF THE CS2 ERA", t, w("The", 0) - 0.1)
        for i, (r, lab, sub, tagtxt) in enumerate(bars):
            y = 260 + i * 160
            p = ramp(t, t_bars + i * 0.18, 0.6)
            length = 1150 * r / 47 * p
            hi = (i == 0 and t >= t_47) or (i == 1 and t >= t_46)
            col = YELLOW if hi else (214, 219, 228)
            rrect(d, (520, y, 520 + max(length, 2), y + 96), 12, fill=col)
            text(d, (490, y + 34), lab, 36, WHITE, anchor="rm")
            text(d, (490, y + 74), sub, 24, MUTED, anchor="rm", tracking=2)
            if p > 0.95:
                text(d, (520 + length - 20, y + 48), f"{r}", 58, INK, anchor="rm")
                text(d, (520 + length + 14, y + 48), "ROUNDS", 26, MUTED, anchor="lm", tracking=3)
            if t >= t_all:
                block_text(img, (520 + 14, y + 22), "SPIRIT", 30, INK, (214, 219, 228) if not hi else WHITE, a=ramp(t, t_all + i * 0.1, 0.25), pad=(14, 8))
            if tagtxt and t >= w("still"):
                stamp(img, tagtxt, 1000, y + 48, t, w("still"), size=50, angle=-6)

    sfx = [(0.15, "stinger-hit-short", -6)] + [(t_bars + i * 0.18, "slide-1", -12) for i in range(4)] + \
          [(t_all, "success-1", -12), (t_47, "pop-1", -8), (t_46, "pop-1", -8), (w("still"), "stamp-thud", -4)]
    render_section("s05", "p06", draw, sfx=sfx, lead=lead)


# ---------- s06: map pool + overtime (p07) ----------
def s06():
    lead = 0.15
    w = Words("p07", lead)
    maps = [("MIRAGE", 19), ("NUKE", 18), ("INFERNO", 14), ("DUST II", 13), ("ANUBIS", 11), ("ANCIENT", 8),
            ("VERTIGO", 3), ("OVERPASS", 3), ("TRAIN", 2)]
    t_m, t_ot = w("Mirage"), w("sixteen")

    def draw(img, t):
        d = ImageDraw.Draw(img)
        title(d, "MAPS PLAYED  ·  91 PLAYOFF MAPS", t, 0.1)
        for i, (m, n) in enumerate(maps):
            y = 220 + i * 76
            p = ramp(t, 0.4 + i * 0.07, 0.5)
            hi = i == 0 and t >= t_m
            text(d, (330, y + 28), m, 34, YELLOW if hi else WHITE, anchor="rm")
            rrect(d, (360, y + 4, 360 + max(2, 40 * n * p), y + 54), 8, fill=YELLOW if hi else (120, 130, 148))
            if p > 0.9:
                text(d, (360 + 40 * n + 16, y + 28), str(n), 34, YELLOW if hi else WHITE, anchor="lm")
        if t >= t_m:
            block_text(img, (360 + 40 * 19 + 90, 210), "PICKED 19 TIMES", 40, INK, YELLOW, a=ramp(t, w("picked"), 0.25))
        if t >= t_ot:
            cx, cy = 1560, 560
            frac = 16 / 91 * ease((t - t_ot) / 1.0)
            ring(d, cx, cy, 190, frac, YELLOW, width=40)
            text(d, (cx, cy - 20), f"{int(round(16 * ease((t - t_ot) / 1.0)))}", 130, WHITE, anchor="mm")
            text(d, (cx, cy + 70), "OF 91", 40, MUTED, anchor="mm", tracking=3)
            block_text(img, (cx, 800), "WENT TO OVERTIME", 44, INK, YELLOW, a=ramp(t, w("overtime"), 0.25), anchor="m")

    sfx = [(0.1, "whoosh-soft", -12), (t_m, "pop-1", -8), (t_ot, "riser-short-2s", -14), (w("overtime"), "stamp-thud", -6)]
    render_section("s06", "p07", draw, sfx=sfx, lead=lead)


# ---------- s07: donk's stat wall, ZywOo, ropz (p08) ----------
DONK = ["RATING 1.49", "DAMAGE / ROUND 97.6", "KILLS 1211", "OPENING KILLS 220", "KILLS / ROUND 0.95", "HEADSHOTS 715",
        "HS / ROUND 0.56", "K–D DIFF +372", "ROUND SWING +4.0%", "ROUNDS WITH A KILL 57%", "IMPACT 1.68", "MULTI-KILL 1.48"]
ZYWOO = ["K/D 1.49", "KAST 79.2%", "DAMAGE DIFF +22.9"]


def s07():
    lead = 0.15
    w = Words("p08", lead)
    t_donk, t_12 = w("donk", 0), w("twelve")
    callouts = {0: w("highest"), 1: w("damage"), 2: w("kills", 0), 3: w("opening")}
    t_zy = w("ZywOo")
    zy_on = [w("K/D"), w("KAST"), w("damage", 1)]
    t_po = w("playoffs")
    donk_fx = clip("S1", 42.0, 1.9, (1.0, 1.1), (0.4, 0.4))
    zy_fx = clip("B5", 39.0, 1.9, (1.0, 1.1))
    ropz_fx = clip("B5", 28.0, 2.6, (1.05, 1.15))

    def tiles(img, d, t, items, t0, col, x0=110, y0=250, cols=4, w_=420, h_=118, hi=()):
        for i, s in enumerate(items):
            on = t0 + i * 0.09
            p = ease((t - on) / 0.2) if t >= on else 0
            x, y = x0 + (i % cols) * (w_ + 20), y0 + (i // cols) * (h_ + 18)
            flip = abs(math.cos(math.pi * (1 - p) / 2)) if p < 1 else 1.0
            hh = h_ * max(flip, 0.05)
            fill = col if p >= 0.5 else PANEL
            ring_ = i in hi
            rrect(d, (x, y + (h_ - hh) / 2, x + w_, y + (h_ + hh) / 2), 12, fill=fill, outline=WHITE if ring_ else None, width=4)
            if p >= 0.5:
                name, _, val = s.rpartition(" ")
                text(d, (x + 22, y + 38), name, 26, INK, anchor="lm", tracking=1)
                text(d, (x + 22, y + 84), val, 46, INK, anchor="lm")

    def draw(img, t):
        if t < t_donk - 0.1:
            d = ImageDraw.Draw(img)
            kinetic(img, "ONE PLAYER", t, w("one") - 0.05, y=500, size=150)
            return
        if t < t_12 + 0.2:                                                  # donk on camera
            show(img, donk_fx, t - (t_donk - 0.1), dim=0.2)
            side_shade(img, 1.0, frac=0.7)
            kinetic(img, "donk", t, t_donk - 0.05, y=430, size=200, x=520)
            block_text(img, (140, 600), "TEAM SPIRIT", 50, INK, (214, 219, 228))
            return
        d = ImageDraw.Draw(img)
        if t < t_zy - 0.1:
            title(d, "donk LEADS 12 OF 25 HLTV CATEGORIES  ·  ALL CS2 MAJOR MATCHES", t, t_12 + 0.2, size=36)
            hi = tuple(k for k, tc in callouts.items() if t >= tc)
            tiles(img, d, t, DONK, t_12 + 0.25, YELLOW, hi=hi)
            return
        if t < t_po - 1.2:
            if t < t_zy + 0.9:
                show(img, zy_fx, t - (t_zy - 0.1), dim=0.2)
                side_shade(img, 1.0, frac=0.7)
                kinetic(img, "ZywOo", t, t_zy - 0.05, y=430, size=200, x=520)
                block_text(img, (140, 600), "VITALITY", 50, (255, 221, 0), INK)
                return
            title(d, "ZywOo LEADS WHERE donk DOESN'T", t, t_zy + 0.9, size=40)
            for i, s in enumerate(ZYWOO):
                on = zy_on[i]
                if t < on - 0.05:
                    continue
                p = ease((t - on + 0.05) / 0.2)
                x = 160 + i * 560
                rrect(d, (x, 360 + 30 * (1 - p), x + 500, 640 + 30 * (1 - p)), 18, fill=(255, 221, 0))
                name, _, val = s.rpartition(" ")
                text(d, (x + 250, 440), name, 40, INK, anchor="mm", tracking=3)
                text(d, (x + 250, 550), val, 110, INK, anchor="mm")
            return
        show(img, ropz_fx, t - (t_po - 1.2), dim=0.35)
        side_shade(img, 1.0, frac=0.72)
        block_text(img, (110, 160), "IN THE PLAYOFFS", 44, INK, YELLOW, a=ramp(t, t_po - 1.1, 0.25))
        kinetic(img, "ropz", t, w("ropz") - 0.05, y=380, size=200, x=380)
        if t >= w("clutches"):
            block_text(img, (110, 520), "14 CLUTCHES", 70, WHITE, INK, a=ramp(t, w("clutches"), 0.2))
        if t >= w("kills", 2):
            block_text(img, (110, 640), "596 KILLS", 70, WHITE, INK, a=ramp(t, w("kills", 2), 0.2))
        if t >= w("ropz"):
            block_text(img, (110, 760), "MOST OF ANYONE  ·  CS2 MAJOR PLAYOFFS", 40, INK, YELLOW, a=ramp(t, w("ropz") + 0.2, 0.25))

    sfx = [(w("one") - 0.05, "whoosh-short", -10), (t_donk - 0.05, "stinger-hit-short", -6)] + \
          [(t_12 + 0.25 + i * 0.09, "click-soft", -14) for i in range(12)] + \
          [(tc, "pop-1", -10) for tc in callouts.values()] + [(t_zy - 0.05, "stinger-hit-short", -6)] + \
          [(x, "pop-2", -8) for x in zy_on] + [(t_po - 1.2, "whoosh-medium-1s", -12), (w("ropz") - 0.05, "stinger-hit-short", -6)]
    render_section("s07", "p08", draw, sfx=sfx, lead=lead, tail=0.6, caption_style=lambda tt: "Box" if (tt < t_12 + 0.2 or t_zy - 0.1 <= tt < t_zy + 0.9 or tt >= t_po - 1.2) else "Low")


if __name__ == "__main__":
    import chapters, allstars
    for sid in (sys.argv[1:] or ORDER + ["a00", "a01", "a02", "a03"]):
        (globals().get(sid) or getattr(chapters, sid, None) or getattr(allstars, sid))()
