"""Video 02, cut v2 (script_v2.md): shorter, chapter = card+story -> final -> [2 highlights] -> MVP slam.
Real team logos everywhere (assets/logos), sound effects drawn from rotating pools (never the same file twice in a row).

python v2.py s00 c1a ...   (no args: all)    ->  clips/<id>.mp4
"""
import functools, math, sys
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFilter

import sections as S
import chapters as C
from engine import *          # noqa: F401,F403

LOGOS = ROOT / "assets" / "logos"
INK, SILVER, GOLD = S.INK, S.SILVER, YELLOW
NAME = {"navi": "NAVI", "spirit": "SPIRIT", "vit": "VITALITY", "falcons": "FALCONS", "faze": "FAZE", "mouz": "MOUZ", "g2": "G2",
        "mongolz": "THE MONGOLZ", "tl": "LIQUID", "pain": "paiN", "furia": "FURIA", "ef": "ETERNAL FIRE", "c9": "CLOUD9",
        "betboom": "BETBOOM", "9z": "9z", "heroic": "HEROIC", "aurora": "AURORA"}


# ---------- logos ----------
@functools.lru_cache(maxsize=None)
def _logo(key, box_w, box_h):
    im = Image.open(LOGOS / f"{key}.png").convert("RGBA")
    bb = im.getbbox()
    if bb:
        im = im.crop(bb)
    s = min(box_w / im.width, box_h / im.height)
    im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    sh = Image.new("RGBA", (im.width + 24, im.height + 24), (0, 0, 0, 0))
    a = im.split()[3].point(lambda v: int(v * 0.7))
    sh.paste((0, 0, 0, 255), (12, 12), a)
    return im, sh.filter(ImageFilter.GaussianBlur(6))


def logo(img, x, y, key, h=64, a=1.0, anchor="l", wmax=None, scale=1.0):
    """Team logo fitted in a box (h*1.35 tall, up to wmax or 3.4*h wide). y = top of the old badge row.
    anchor l/m/r on x. Returns the drawn width. Soft shadow so it reads over footage."""
    if a <= 0.01:
        return 0
    bh = int(h * 1.35 * scale)
    bw = int((wmax or h * 3.4) * scale)
    im, sh = _logo(key, bw, bh)
    if a < 1:
        im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * a)))
        sh = sh.copy(); sh.putalpha(sh.split()[3].point(lambda v: int(v * a)))
    if anchor == "m":
        x -= im.width / 2
    elif anchor == "r":
        x -= im.width
    x -= 30 * (1 - a)
    yy = y + h / 2 - im.height / 2
    img.paste(sh, (int(x) - 6, int(yy) - 4), sh)
    img.paste(im, (int(x), int(yy)), im)
    return im.width


S.badge = logo
C.badge = logo


# ---------- sound effects: rotating pools ----------
POOL = {"hit": ["stinger-hit-short", "bass-hit", "impact-soft-2", "impact-soft-3", "dry-thud"],
        "whoosh": ["whoosh-short", "whoosh-soft", "whoosh-medium-1s", "send-whoosh-up", "slide-1", "slide-2"],
        "pop": ["pop-1", "pop-2", "click-sharp", "tap", "select-1", "switch-1", "toggle", "copy-pluck"],
        "stamp": ["stamp-thud", "bass-hit", "impact-wood-light", "dry-thud"],
        "rise": ["riser-short-2s", "noise-riser", "swell-soft-3s", "reverse-cymbal-2s"],
        "tick": ["clock-tick", "bomb-beep", "tick-soft"],
        "win": ["stinger-win-brass", "stinger-fanfare-short", "success-bell", "stinger-win-strings"],
        "big": ["sub-drop", "stinger-energetic-hit", "bass-hit"],
        "glitch": ["glitch-burst", "glitch-soft-1", "glitch-soft-2"],
        "card": ["sub-drop", "stinger-hit-short", "bass-hit", "stinger-energetic-hit"]}


class Sfx:
    def __init__(self):
        self.i, self.last = defaultdict(int), None

    def __call__(self, cat):
        pool = POOL[cat]
        for _ in range(len(pool)):
            name = pool[self.i[cat] % len(pool)]
            self.i[cat] += 1
            if name != self.last:
                break
        self.last = name
        return name


FX = Sfx()


def sfx_list(events):
    """events: (time, category, gain) -> (time, file, gain), sorted so 'never twice in a row' holds in time order."""
    return [(t, FX(cat), g) for t, cat, g in sorted(events)]


# ---------- shared pieces ----------
def series_card(img, t, t_on, a_key, b_key, maps, x, y, w_=780, note=None, note_t=None):
    """Match card with logos left and right, one row per map (winner's score yellow), OT tag."""
    if t < t_on:
        return
    d = ImageDraw.Draw(img)
    a = ease((t - t_on) / 0.25)
    h_ = 150 + 78 * len(maps)
    yy = y + 30 * (1 - a)
    rrect(d, (x, yy, x + w_, yy + h_), 18, fill=(16, 19, 26), outline=LINE, width=2)
    logo(img, x + 34, yy + 26, a_key, h=70, a=a, wmax=260)
    logo(img, x + w_ - 34, yy + 26, b_key, h=70, a=a, anchor="r", wmax=260)
    text(d, (x + w_ / 2, yy + 72), "vs", 32, MUTED, anchor="mm", alpha=a)
    for k, (m, sa, sb, ot, t_row) in enumerate(maps):
        if t < t_row:
            continue
        p = ease((t - t_row) / 0.2)
        ry = yy + 140 + k * 78
        text(d, (x + 40, ry + 30), m, 36, WHITE, anchor="lm", alpha=p)
        win_a = sa > sb
        text(d, (x + w_ / 2 - 34, ry + 30), str(sa), 54, YELLOW if win_a else WHITE, anchor="rm", alpha=p)
        text(d, (x + w_ / 2, ry + 30), "–", 40, MUTED, anchor="mm", alpha=p)
        text(d, (x + w_ / 2 + 34, ry + 30), str(sb), 54, WHITE if win_a else YELLOW, anchor="lm", alpha=p)
        if ot:
            block_text(img, (x + w_ - 200, ry + 8), "OVERTIME", 28, INK, YELLOW, a=p, pad=(12, 8))
    if note and note_t is not None:
        S.stamp(img, note, x + w_ / 2, yy + h_ + 60, t, note_t, size=50, angle=-4)


def bgfoot(img, fx, t, dim=0.82, blur=8):
    S.show(img, fx, t, dim=dim, blur=blur, sat=0.5)


def chapter(cid):
    return C.chapter_cfg(cid)


def mvp(sid, cid, fx_args, name, sub, team):
    """MVP slam: footage, MVP tag, name, team logo; ~3 s."""
    lead = 0.1
    w = Words(sid, lead)
    fx = S.clip(*fx_args)

    def draw(img, t):
        C.mvp_card(img, t, 0.0, fx, name, sub)
        logo(img, 110, 470, team, h=90, a=ramp(t, 0.15, 0.25), wmax=360)
        S.flash(img, t, 0.0, strength=0.5)

    ev = [(0.0, "big", -6), (w("MVP") + 0.3 if False else 0.35, "whoosh", -14)]
    render_section(sid, sid, draw, sfx=sfx_list(ev), lead=lead, tail=0.9, caption_style="Low")


# ---------- s00 cold open ----------
def s00():
    lead = 0.15
    w = Words("s00", lead)
    t_four, t_two, t_three = w("Four"), w("two"), w("three")
    t_this, t_champ, t_under, t_mvp, t_mom = w("This"), w("champions", 1), w("underdogs"), w("MVPs"), w("moments")
    t_end, t_you = w("And", 2), w("You")
    champs = ["navi", "spirit", "vit", "falcons"]
    step = (t_two - 0.6 - t_four) / 4
    cuts = [(0.0, S.clip("A2", 36.5, 1.5, (1.05, 1.15))),
            (t_four, S.clip("C1", 33.0, step + 0.1, (1.0, 1.06))), (t_four + step, S.clip("S3", 32.0, step + 0.1, (1.0, 1.06))),
            (t_four + 2 * step, S.clip("B5", 28.2, step + 0.1, (1.0, 1.06))), (t_four + 3 * step, S.clip("K2", 22.2, step + 0.2, (1.0, 1.06))),
            (t_two - 0.6, S.clip("B5", 28.8, 2.4, (1.0, 1.1))),
            (w("and", 0) - 0.1, S.clip("S1", 44.0, 1.9, (1.0, 1.1), (0.55, 0.45))),
            (w("lost") - 0.4, S.clip("S5", 20.0, 2.0, (1.0, 1.08))),
            (t_champ - 0.05, S.clip("S3", 33.0, 1.2, (1.0, 1.08))), (t_under - 0.05, S.clip("A2", 29.0, 1.3, (1.0, 1.08))),
            (t_mvp - 0.05, S.clip("S1", 42.0, 1.2, (1.0, 1.08))), (t_mom - 0.05, S.clip("K1", 13.0, 2.3, (1.15, 1.25)))]
    title_on, title_off = t_this - 0.1, t_champ - 0.1

    def draw(img, t):
        d = ImageDraw.Draw(img)
        if title_on <= t < title_off:
            a = ramp(t, title_on, 0.3)
            text(d, (W / 2, 300), "SPORTS ON THE LINE", 40, YELLOW, anchor="mm", alpha=a, tracking=10)
            sc = 1.3 - 0.3 * ease((t - title_on) / 0.2)
            d.text((W / 2, 470), "EVERY CS2 MAJOR", font=font(int(150 * sc)), fill=WHITE, anchor="mm")
            block_text(img, (W / 2, 580), "SO FAR  ·  2024–2026", 64, INK, YELLOW, a=ramp(t, title_on + 0.25, 0.3), anchor="m")
            for i, k in enumerate(champs):                         # the four champions' logos under the title
                logo(img, W / 2 + (i - 1.5) * 300, 760, k, h=70, a=ramp(t, title_on + 0.35 + i * 0.08, 0.25), anchor="m", wmax=240)
            S.flash(img, t, title_on)
            return
        if t >= t_end - 0.05:
            roles = ["IGL", "AWP", "RIFLER", "RIFLER", "ANCHOR"]
            S.title(d, "THE ALL-STAR TEAM OF THE CS2 ERA", t, t_end - 0.05, y=150, x=W / 2 - 520, size=50)
            for i, r in enumerate(roles):
                a = ramp(t, t_end + 0.2 + i * 0.12, 0.3)
                x0 = 210 + i * 310
                rrect(d, (x0, 280 + 30 * (1 - a), x0 + 260, 620 + 30 * (1 - a)), 18, fill=fade(PANEL, a), outline=fade(LINE, a), width=3)
                text(d, (x0 + 130, 420 + 30 * (1 - a)), "?", 150, YELLOW, anchor="mm", alpha=a)
                text(d, (x0 + 130, 575 + 30 * (1 - a)), r, 34, MUTED, anchor="mm", alpha=a, tracking=4)
            if t >= t_you:
                S.stamp(img, "YOU WON'T AGREE", W / 2, 690, t, t_you + 0.2, col=YELLOW, size=64, angle=-4)
            return
        st, fx = [c for c in cuts if t >= c[0]][-1]
        S.show(img, fx, t - st, dim=0.25)
        S.flash(img, t, st, strength=0.5)
        side_shade(img, 0.6, frac=0.9, strength=0.55)
        S.kinetic(img, "FIVE MAJORS", t, w("Five"), size=180, t_off=t_four - 0.05)
        if t_four <= t < t_two - 0.6:
            S.kinetic(img, "FOUR CHAMPIONS", t, t_four, size=170)
            k = min(3, int((t - t_four) / step))
            logo(img, W / 2, 600, champs[k], h=110, anchor="m", wmax=520)
        if t_two - 0.6 <= t < w("and", 0) - 0.1:
            S.kinetic(img, "TWO IN A ROW", t, t_two - 0.3, size=150)
            logo(img, W / 2, 600, "vit", h=110, anchor="m", wmax=520)
        if w("and", 0) - 0.1 <= t < title_on:
            logo(img, 140, 230, "faze", h=110, wmax=300)
            n = 1 + min(2, int(max(0.0, t - t_three) / 0.33)) if t >= t_three else 0
            if n:
                text(d, (140, 520), f"{n}", 260, WHITE, anchor="lm")
                text(d, (330, 540), "FINALS", 90, WHITE, anchor="lm")
            S.stamp(img, "0 TITLES", 1250, 470, t, w("lost"), size=130)
        words = [(t_champ, "THE CHAMPIONS"), (t_under, "THE UNDERDOGS"), (t_mvp, "THE MVPs"), (t_mom, "THE MOMENTS")]
        for i, (tw_, s) in enumerate(words):
            nxt = words[i + 1][0] if i + 1 < len(words) else t_end - 0.05
            if tw_ - 0.05 <= t < nxt:
                S.kinetic(img, s, t, tw_ - 0.05, size=150, col=INK, block=YELLOW, t_off=nxt - 0.2)

    ev = [(w("Five") - 0.05, "big", -6), (t_four, "whoosh", -12)] + [(t_four + k * step, "pop", -9) for k in range(4)] + \
         [(t_two - 0.6, "whoosh", -12), (w("and", 0), "glitch", -12)] + [(t_three + k * 0.33, "hit", -7) for k in range(3)] + \
         [(w("lost"), "stamp", -4), (title_on, "card", -5)] + [(x - 0.05, "whoosh", -11) for x in (t_champ, t_under, t_mvp, t_mom)] + \
         [(t_end - 0.05, "rise", -14), (t_you + 0.2, "stamp", -5)]
    render_section("s00", "s00", draw, sfx=sfx_list(ev), lead=lead, tail=0.4, caption_style="Box")


# ---------- s01 champions shelf with logos ----------
def s01():
    lead = 0.15
    w = Words("s01", lead)
    fills = [w("Copenhagen"), w("Shanghai"), w("Austin"), w("Budapest"), w("Cologne")]
    bgfx = S.clip("S3", 31.0, 4.0, (1.0, 1.1))

    def draw(img, t):
        S.show(img, bgfx, min(t, 3.9) * 0.6, dim=0.8, blur=6, sat=0.3)
        d = ImageDraw.Draw(img)
        S.title(d, "THE CHAMPIONS", t, 0.2)
        if t >= w("four"):
            block_text(img, (110, 200), "4 DIFFERENT TEAMS", 56, INK, YELLOW, a=ramp(t, w("four"), 0.3))
        for i, (city, date, key) in enumerate(S.MAJORS):
            x0 = 120 + i * 345
            a = ramp(t, 0.5 + i * 0.12, 0.35)
            rrect(d, (x0, 320 + 20 * (1 - a), x0 + 315, 800 + 20 * (1 - a)), 20, fill=fade(PANEL, a * 0.92), outline=fade(LINE, a), width=3)
            text(d, (x0 + 157, 372), city, 40, WHITE, anchor="mm", alpha=a)
            text(d, (x0 + 157, 418), date, 28, MUTED, anchor="mm", alpha=a, tracking=3)
            if t >= fills[i]:
                p = ease((t - fills[i]) / 0.22)
                sc = 1.35 - 0.35 * p
                logo(img, x0 + 157, 560, key, h=110, a=p, anchor="m", wmax=270, scale=sc)
                text(d, (x0 + 157, 740), NAME[key], 34, YELLOW, anchor="mm", alpha=p, tracking=3)
            else:
                text(d, (x0 + 157, 600), "?", 120, DIM, anchor="mm", alpha=a)
        if t >= w("twice"):
            a = ramp(t, w("twice"), 0.3)
            d.line([(120 + 2 * 345 + 40, 830), (120 + 4 * 345 - 40, 830)], fill=fade((255, 221, 0), a), width=6)
            block_text(img, (120 + 3 * 345 - 150 + 157, 850), "BACK-TO-BACK", 44, INK, (255, 221, 0), a=a)
        for f_ in fills:
            S.flash(img, t, f_, dur=0.1, strength=0.25)

    ev = [(0.2, "whoosh", -12), (w("four"), "stamp", -8)] + [(f_, "hit", -7) for f_ in fills] + [(w("twice"), "pop", -8)]
    render_section("s01", "s01", draw, sfx=sfx_list(ev), lead=lead)


# ---------- s02 playoff runs grid: logo + name per row ----------
def s02():
    lead = 0.15
    w = Words("s02", lead)
    t_sp, t_vi = w("Spirit"), w("Vitality")
    rows = list(S.PLAYOFF.items())

    def draw(img, t):
        d = ImageDraw.Draw(img)
        S.title(d, "PLAYOFF RUNS  ·  5 MAJORS", t, 0.1)
        cols = ["CPH 24", "SHA 24", "AUS 25", "BUD 25", "COL 26"]
        gx, gy, cw, ch = 700, 210, 200, 76
        for j, c in enumerate(cols):
            text(d, (gx + j * cw + cw / 2, gy - 26), c, 30, MUTED, anchor="mm", alpha=ramp(t, 0.2, 0.3), tracking=2)
        for i, (key, runs) in enumerate(rows):
            y = gy + 18 + i * ch
            a = ramp(t, 0.3 + i * 0.06, 0.3)
            gold = (key == "spirit" and t >= t_sp) or (key == "vit" and t >= t_vi)
            dim_other = t >= t_sp and not gold
            aa = a * (0.4 if dim_other else 1.0)
            logo(img, 120, y + 2, key, h=44, a=aa, wmax=170)
            text(d, (330, y + 30), NAME[key], 34, YELLOW if gold else WHITE, anchor="lm", alpha=aa)
            for j, r in enumerate(runs):
                x = gx + j * cw
                p = ramp(t, 0.5 + i * 0.06 + j * 0.05, 0.25)
                if r:
                    col = GOLD if gold else (fade(WIN, 0.5) if dim_other else WIN)
                    rrect(d, (x + 14, y + 10, x + cw - 14, y + 10 + 40 * p), 8, fill=col)
                else:
                    rrect(d, (x + 14, y + 10, x + cw - 14, y + 50), 8, outline=fade(LINE, a), width=2)
            if gold:
                block_text(img, (gx + 5 * cw + 24, y + 4), "5 / 5", 42, INK, YELLOW, a=ramp(t, t_sp if key == "spirit" else t_vi, 0.3))
        if t >= w("Five", 0):
            block_text(img, (W / 2, 840), "FIVE MAJORS  ·  FIVE PLAYOFF RUNS EACH", 48, WHITE, INK, a=ramp(t, w("Five", 0), 0.3), anchor="m")

    ev = [(0.1, "whoosh", -12), (t_sp, "win", -12), (t_vi, "pop", -8), (w("Five", 0), "hit", -10)]
    render_section("s02", "s02", draw, sfx=sfx_list(ev), lead=lead)


# ---------- s03 FaZe: three lost finals ----------
def s03():
    lead = 0.15
    w = Words("s03", lead)
    bgfx = S.clip("S1", 44.0, 1.9, (1.05, 1.15), (0.55, 0.45))
    finals = [("COPENHAGEN 2024", "navi", "1–2"), ("SHANGHAI 2024", "spirit", "1–2"), ("BUDAPEST 2025", "vit", "1–3")]
    t_cards = [w("Three", 0) + k * 0.22 for k in range(3)]

    def draw(img, t):
        S.show(img, bgfx, min(t, 1.85), dim=0.45, sat=0.6)
        side_shade(img, 1.0, frac=0.75)
        logo(img, 110, 120, "faze", h=100, a=ramp(t, w("FaZe"), 0.2), wmax=260)
        d = ImageDraw.Draw(img)
        for k, (ev_, opp, score) in enumerate(finals):
            if t < t_cards[k]:
                continue
            a = ease((t - t_cards[k]) / 0.2)
            y = 330 + k * 160
            rrect(d, (110 - 40 * (1 - a), y, 960 - 40 * (1 - a), y + 136), 14, fill=(16, 18, 24), outline=LINE, width=2)
            text(d, (140, y + 26), "GRAND FINAL  ·  " + ev_, 28, MUTED, tracking=2)
            logo(img, 140, y + 50, "faze", h=52, wmax=150)
            text(d, (320, y + 82), score, 56, WHITE, anchor="lm")
            logo(img, 470, y + 50, opp, h=52, wmax=200)
            S.stamp(img, "L", 880, y + 70, t, w("Three", 1) + k * 0.16, size=80, angle=-8)
        if t >= w("losses"):
            block_text(img, (110, 830), "3 FINALS  ·  0 TITLES", 64, WHITE, LOSS, a=ramp(t, w("losses"), 0.25))

    ev = [(w("FaZe"), "glitch", -12)] + [(x, "hit", -7) for x in t_cards] + [(w("Three", 1) + k * 0.16, "stamp", -4) for k in range(3)]
    render_section("s03", "s03", draw, sfx=sfx_list(ev), lead=lead, tail=0.5, caption_style="Low")


# ---------- s04 donk / ZywOo / ropz ----------
def s04():
    lead = 0.15
    w = Words("s04", lead)
    t_donk, t_12, t_zy, t_po = w("donk", 0), w("twelve"), w("ZywOo"), w("playoffs,")
    zy_on = [w("K/D,"), w("KAST"), w("damage")]
    donk_fx, zy_fx, ropz_fx = S.clip("S1", 42.0, 1.9, (1.0, 1.1), (0.4, 0.4)), S.clip("B5", 39.0, 1.9, (1.0, 1.1)), S.clip("B5", 28.0, 2.6, (1.05, 1.15))

    def tiles(img, d, t, t0):
        for i, s in enumerate(S.DONK):
            on = t0 + i * 0.08
            p = ease((t - on) / 0.18) if t >= on else 0
            x, y = 110 + (i % 4) * 440, 250 + (i // 4) * 136
            hh = 118 * max(abs(math.cos(math.pi * (1 - p) / 2)) if p < 1 else 1.0, 0.05)
            rrect(d, (x, y + (118 - hh) / 2, x + 420, y + (118 + hh) / 2), 12, fill=YELLOW if p >= 0.5 else PANEL)
            if p >= 0.5:
                name, _, val = s.rpartition(" ")
                text(d, (x + 22, y + 38), name, 26, INK, anchor="lm", tracking=1, bg=YELLOW)
                text(d, (x + 22, y + 84), val, 46, INK, anchor="lm", bg=YELLOW)

    def draw(img, t):
        d = ImageDraw.Draw(img)
        if t < t_donk - 0.1:
            S.kinetic(img, "ONE PLAYER", t, w("one") - 0.05, y=500, size=150)
            return
        if t < t_12 + 0.3:
            S.show(img, donk_fx, t - (t_donk - 0.1), dim=0.2)
            side_shade(img, 1.0, frac=0.7)
            S.kinetic(img, "donk", t, t_donk - 0.05, y=430, size=200, x=520)
            logo(img, 140, 560, "spirit", h=60, wmax=330)
            return
        if t < t_zy - 0.1:
            S.title(d, "donk LEADS 12 OF 25 HLTV CATEGORIES  ·  ALL CS2 MAJOR MATCHES", t, t_12 + 0.3, size=36)
            tiles(img, d, t, t_12 + 0.35)
            return
        if t < t_po - 0.5:
            if t < t_zy + 0.8:
                S.show(img, zy_fx, t - (t_zy - 0.1), dim=0.2)
                side_shade(img, 1.0, frac=0.7)
                S.kinetic(img, "ZywOo", t, t_zy - 0.05, y=430, size=200, x=520)
                logo(img, 140, 560, "vit", h=60, wmax=330)
                return
            S.title(d, "ZywOo LEADS WHERE donk DOESN'T", t, t_zy + 0.8, size=40)
            for i, s in enumerate(S.ZYWOO):
                if t < zy_on[i] - 0.05:
                    continue
                p = ease((t - zy_on[i] + 0.05) / 0.2)
                x = 160 + i * 560
                rrect(d, (x, 360 + 30 * (1 - p), x + 500, 640 + 30 * (1 - p)), 18, fill=(255, 221, 0))
                name, _, val = s.rpartition(" ")
                text(d, (x + 250, 440), name, 40, INK, anchor="mm", tracking=3, bg=(255, 221, 0))
                text(d, (x + 250, 550), val, 110, INK, anchor="mm", bg=(255, 221, 0))
            return
        S.show(img, ropz_fx, t - (t_po - 0.5), dim=0.35)
        side_shade(img, 1.0, frac=0.72)
        block_text(img, (110, 160), "IN THE PLAYOFFS", 44, INK, YELLOW, a=ramp(t, t_po - 0.4, 0.25))
        logo(img, 110, 250, "vit", h=56, wmax=300)
        S.kinetic(img, "ropz", t, w("ropz") - 0.05, y=420, size=200, x=380)
        if t >= w("clutches"):
            block_text(img, (110, 540), "14 CLUTCHES", 70, WHITE, INK, a=ramp(t, w("clutches"), 0.2))
        if t >= w("kills"):
            block_text(img, (110, 660), "596 KILLS", 70, WHITE, INK, a=ramp(t, w("kills"), 0.2))

    ev = [(w("one") - 0.05, "whoosh", -10), (t_donk - 0.05, "card", -6)] + [(t_12 + 0.35 + i * 0.08, "pop", -16) for i in range(0, 12, 3)] + \
         [(t_zy - 0.05, "card", -6)] + [(x, "pop", -9) for x in zy_on] + [(t_po - 0.5, "whoosh", -12), (w("ropz") - 0.05, "big", -7)]
    render_section("s04", "s04", draw, sfx=sfx_list(ev), lead=lead, tail=0.5,
                   caption_style=lambda tt: "Box" if (t_donk - 0.1 <= tt < t_12 + 0.3 or t_zy - 0.1 <= tt < t_zy + 0.8 or tt >= t_po - 0.5) else "Low")


# ---------- chapters ----------
def story(sid, cid, draw_rest, ev_rest, t_split_word):
    """Chapter card until t_split_word, then draw_rest(img, t, w)."""
    lead = 0.15
    w = Words(sid, lead)
    cfg = chapter(cid)
    t_split = w(*t_split_word) - 0.1 if isinstance(t_split_word, tuple) else w(t_split_word) - 0.1

    def draw(img, t):
        if t < t_split:
            C.chapter_card(img, t, cfg, w)
            return
        draw_rest(img, t, w)

    ev = [(w(cfg["city_word"]) - 0.05, "card", -5), (t_split, "whoosh", -11)] + ev_rest(w)
    render_section(sid, sid, draw, sfx=sfx_list(ev), lead=lead, caption_style="Low")


def c1a():
    stages = ["OPENING STAGE", "ELIMINATION STAGE", "QUARTER-FINALS"]

    def rest(img, t, w):
        if t < w("semi-final") - 0.1:
            C.stage_path(img, t, stages, [("ef", 0, 2, w("Eternal")), ("c9", 0, 2, w("Cloud9"))], w("Eternal") - 0.3,
                         title_s="FROM THE VERY FIRST STAGE")
            return
        d = ImageDraw.Draw(img)
        S.title(d, "SEMI-FINAL  ·  ANUBIS", t, w("semi-final") - 0.1)
        series_card(img, t, w("semi-final"), "navi", "g2", [("ANUBIS", 16, 13, True, w("edged"))], 570, 300)

    story("c1a", "c1", rest, lambda w: [(w("Eternal"), "rise", -16), (w("semi-final"), "whoosh", -11), (w("overtime"), "pop", -8)], "Eternal")


def c1b():
    lead = 0.15
    w = Words("c1b", lead)

    def draw(img, t):
        C.final_board(img, t, 0.1, "navi", "faze", [("ANCIENT", 13, 9, w("Ancient"), False), ("MIRAGE", 2, 13, w("thirteen"), True),
                                                     ("INFERNO", 13, 3, w("Inferno."), False)])
        S.stamp(img, "CHAMPIONS", W / 2, 760, t, w("Champions"), col=YELLOW, size=80, angle=-3)

    ev = [(0.1, "whoosh", -12), (w("thirteen"), "hit", -4), (w("Ancient"), "pop", -9), (w("Inferno."), "pop", -9), (w("Champions"), "win", -10)]
    render_section("c1b", "c1b", draw, sfx=sfx_list(ev), lead=lead, tail=0.4)


def c2a():
    stages = ["OPENING STAGE", "ELIMINATION STAGE", "QUARTER-FINALS"]

    def rest(img, t, w):
        if t < w("And") - 0.1:
            C.stage_path(img, t, stages, [("mongolz", 0, 2, w("The MongolZ")), ("tl", 0, 2, w("Liquid"))], w("The MongolZ") - 0.3,
                         title_s="ALL THE WAY UP")
            return
        d = ImageDraw.Draw(img)
        S.title(d, "SEMI-FINAL  ·  NUKE", t, w("And") - 0.1)
        C.score_race(img, d, t, w("reached"), "g2", "faze", 14, 16, 1.0, y=560)
        if t >= w("overtime"):
            block_text(img, (W / 2, 720), "OVERTIME  ·  FAZE TO ANOTHER FINAL", 50, INK, YELLOW, a=ramp(t, w("overtime"), 0.2), anchor="m")

    story("c2a", "c2", rest, lambda w: [(w("The MongolZ"), "rise", -16), (w("reached"), "tick", -10), (w("sixteen-fourteen"), "stamp", -5)], "The MongolZ")


def c2b():
    lead = 0.15
    w = Words("c2b", lead)

    def draw(img, t):
        C.final_board(img, t, 0.1, "spirit", "faze", [("NUKE", 13, 8, 0.4, False), ("ANCIENT", 6, 13, 0.7, False),
                                                       ("DUST II", 13, 11, w("thirteen-eleven"), False)])
        S.stamp(img, "CHAMPIONS", W / 2, 760, t, w("thirteen-eleven") + 0.3, col=YELLOW, size=80, angle=-3)
        C.faze_counter(img, t, w("FaZe:"), 2)

    ev = [(0.1, "whoosh", -12), (0.4, "pop", -10), (0.7, "pop", -10), (w("Dust II"), "rise", -16), (w("thirteen-eleven"), "win", -10), (w("FaZe:"), "stamp", -6)]
    render_section("c2b", "c2b", draw, sfx=sfx_list(ev), lead=lead, tail=0.4)


def c3a():
    stages = ["STAGE 2", "STAGE 3", "QUARTER-FINAL", "SEMI-FINAL"]

    def rest(img, t, w):
        if t < w("And") - 0.1:
            C.stage_path(img, t, stages, [("pain", 0, 3, w("paiN"))], w("paiN") - 0.1, title_s="paiN's RUN")
            return
        d = ImageDraw.Draw(img)
        S.title(d, "QUARTER-FINAL  ·  MIRAGE", t, w("And") - 0.1)
        C.score_race(img, d, t, w("won"), "spirit", "mouz", 25, 21, 1.2)
        if t >= w("forty-six-round"):
            block_text(img, (W / 2, 660), "46 ROUNDS", 56, INK, YELLOW, a=ramp(t, w("forty-six-round"), 0.2), anchor="m")
        S.stamp(img, "SERIES LOST 1–2", W / 2, 830, t, w("still"), size=80, angle=-4)

    story("c3a", "c3", rest, lambda w: [(w("paiN"), "rise", -16), (w("won"), "tick", -10), (w("still"), "stamp", -4)], "paiN")


def c3b():
    lead = 0.15
    w = Words("c3b", lead)

    def draw(img, t):
        d = ImageDraw.Draw(img)
        if t >= w("ropz") - 0.1:
            S.title(d, "ropz", t, w("ropz") - 0.1, size=60)
            logo(img, 560, 380, "faze", h=130, a=ramp(t, w("FaZe"), 0.3), anchor="m", wmax=360)
            p = ramp(t, w("won"), 0.4)
            d.line([(760, 470), (760 + 360 * p, 470)], fill=YELLOW, width=12)
            if p > 0.9:
                d.polygon([(1120, 440), (1170, 470), (1120, 500)], fill=YELLOW)
            logo(img, 1400, 380, "vit", h=130, a=ramp(t, w("won") + 0.3, 0.3), anchor="m", wmax=420)
            block_text(img, (W / 2, 660), "FIRST MAJOR WITH VITALITY  ·  FIRST ATTEMPT", 50, INK, YELLOW, a=ramp(t, w("first", 1), 0.25), anchor="m")
            return
        C.final_board(img, t, 0.1, "vit", "mongolz", [("MIRAGE", 5, 13, w("first"), True), ("DUST II", 13, 4, w("next"), False),
                                                     ("INFERNO", 13, 6, w("two."), False)])
        S.stamp(img, "CHAMPIONS", W / 2, 760, t, w("two.") + 0.3, col=YELLOW, size=80, angle=-3)

    ev = [(0.1, "whoosh", -12), (w("first"), "hit", -5), (w("next"), "pop", -9), (w("two."), "win", -10), (w("ropz") - 0.1, "whoosh", -11), (w("won"), "pop", -9)]
    render_section("c3b", "c3b", draw, sfx=sfx_list(ev), lead=lead, tail=0.4)


def c4a():
    stages = ["STAGE 1", "STAGE 2", "STAGE 3", "QF", "SF", "FINAL"]

    def rest(img, t, w):
        C.stage_path(img, t, stages, [("faze", 0, 5, w("Stage"))], w("underdog") - 0.1, title_s="THE UNDERDOG STORY: FAZE")
        if t >= w("bottom"):
            block_text(img, (300, 700), "FROM THE VERY BOTTOM OF 32 TEAMS", 46, WHITE, INK, a=ramp(t, w("bottom"), 0.25))

    story("c4a", "c4", rest, lambda w: [(w("Stage"), "rise", -15), (w("final."), "stamp", -6)], "underdog")


def c4b():
    lead = 0.15
    w = Words("c4b", lead)

    def draw(img, t):
        C.final_board(img, t, 0.1, "vit", "faze", [("NUKE", 6, 13, w("first"), False), ("DUST II", 13, 3, w("next"), False),
                                                   ("INFERNO", 13, 9, w("next") + 0.2, False), ("OVERPASS", 13, 2, w("three."), False)],
                      label="GRAND FINAL  ·  BEST OF FIVE")
        S.stamp(img, "BACK-TO-BACK", W / 2, 875, t, w("Back-to-back"), col=YELLOW, size=62, angle=-3)
        C.faze_counter(img, t, w("FaZe", 1), 3, flip_t=w("three", 1))

    ev = [(0.1, "whoosh", -12), (w("first"), "hit", -5), (w("next"), "pop", -9), (w("three."), "pop", -9), (w("Back-to-back"), "win", -10), (w("three", 1), "stamp", -5)]
    render_section("c4b", "c4b", draw, sfx=sfx_list(ev), lead=lead, tail=0.4)


def c5a():
    def rest(img, t, w):
        d = ImageDraw.Draw(img)
        S.title(d, "LONGEST MAP OF THE CS2 ERA", t, w("Spirit") - 0.1)
        C.score_race(img, d, t, w("played"), "spirit", "g2", 25, 22, 2.0)
        if t >= w("forty-seven"):
            block_text(img, (W / 2, 660), "47 ROUNDS  ·  MIRAGE", 60, INK, YELLOW, a=ramp(t, w("forty-seven"), 0.2), anchor="m")

    story("c5a", "c5", rest, lambda w: [(w("played"), "tick", -10), (w("forty-seven"), "big", -6)], "Spirit")


def c5b():
    lead = 0.15
    w = Words("c5b", lead)
    eights = [w("Thirteen-eight.", k) for k in range(3)]

    def draw(img, t):
        d = ImageDraw.Draw(img)
        if t >= w("karrigan") - 0.1:
            S.title(d, "karrigan", t, w("karrigan") - 0.1, size=60)
            for k, ev_ in enumerate(["COPENHAGEN 2024", "SHANGHAI 2024", "BUDAPEST 2025"]):
                a = ramp(t, w("lost") + k * 0.15, 0.25)
                x = 140 + k * 430
                rrect(d, (x, 300, x + 390, 500), 16, fill=fade((60, 26, 30), a), outline=fade(LOSS, a), width=3)
                text(d, (x + 195, 340), ev_, 28, MUTED, anchor="mm", alpha=a, tracking=2)
                logo(img, x + 195, 370, "faze", h=60, a=a, anchor="m", wmax=200)
                text(d, (x + 195, 470), "FINAL LOST", 34, LOSS, anchor="mm", alpha=a)
            a = ramp(t, w("FaZe."), 0.3)
            if a > 0:
                x = 140 + 3 * 430
                rrect(d, (x, 300 - 20 * (1 - a), x + 390, 500), 16, fill=YELLOW)
                text(d, (x + 195, 340), "COLOGNE 2026", 28, INK, anchor="mm", tracking=2, bg=YELLOW)
                logo(img, x + 195, 370, "falcons", h=60, anchor="m", wmax=260)
                text(d, (x + 195, 470), "CHAMPION", 34, INK, anchor="mm", bg=YELLOW)
            return
        if t < w("In") - 0.1:
            S.title(d, "FALCONS' PLAYOFF ROAD", t, 0.1)
            series_card(img, t, 0.2, "falcons", "vit", [("QUARTER-FINAL", 2, 1, False, w("Vitality,"))], 110, 280)
            series_card(img, t, w("Spirit.") - 0.1, "falcons", "spirit", [("SEMI-FINAL", 2, 1, False, w("Spirit."))], 1030, 280)
            return
        S.title(d, "GRAND FINAL  ·  FALCONS 3–0 FURIA", t, w("In") - 0.1)
        logo(img, 640, 220, "falcons", h=70, anchor="m", wmax=300)
        text(d, (W / 2, 265), "vs", 36, MUTED, anchor="mm")
        logo(img, 1280, 220, "furia", h=70, anchor="m", wmax=200)
        for k, (m, tk) in enumerate(zip(["MIRAGE", "ANUBIS", "INFERNO"], eights)):
            if t < tk:
                continue
            p = ease((t - tk) / 0.18)
            x = 170 + k * 540
            rrect(d, (x, 380, x + 480, 740), 22, fill=(0, 156, 96))
            text(d, (x + 240, 440), m, 44, WHITE, anchor="mm", tracking=3, bg=(0, 156, 96))
            text(d, (x + 240, 590), "13–8", int(150 * (1.15 - 0.15 * p)), WHITE, anchor="mm", bg=(0, 156, 96))

    ev = [(0.1, "whoosh", -12), (w("Vitality,"), "pop", -10), (w("Spirit."), "pop", -10), (w("In") - 0.1, "whoosh", -11)] + \
         [(x, "stamp", -5) for x in eights] + [(w("karrigan") - 0.1, "glitch", -12), (w("FaZe."), "win", -10)]
    render_section("c5b", "c5b", draw, sfx=sfx_list(ev), lead=lead, tail=0.4)


def c1m(): mvp("c1m", "c1", ("C1", 32.7, 2.3, (1.0, 1.14), (0.45, 0.45)), "jL", "PGL MAJOR COPENHAGEN 2024", "navi")
def c2m(): mvp("c2m", "c2", ("S1", 42.0, 1.9, (1.0, 1.14), (0.4, 0.4)), "donk", "YOUNGEST & HIGHEST-RATED MAJOR MVP  ·  HLTV", "spirit")
def c3m(): mvp("c3m", "c3", ("B5", 39.0, 1.9, (1.0, 1.14)), "ZywOo", "BLAST.tv AUSTIN MAJOR 2025", "vit")
def c4m(): mvp("c4m", "c4", ("B5", 28.0, 2.6, (1.0, 1.12)), "ZywOo", "MVP AGAIN  ·  HIS THIRD MAJOR MVP", "vit")
def c5m(): mvp("c5m", "c5", ("K2", 22.0, 2.6, (1.0, 1.12), (0.4, 0.45)), "m0NESY", "IEM COLOGNE MAJOR 2026", "falcons")


# ---------- all-stars ----------
def a00():
    lead = 0.15
    w = Words("a00", lead)
    cuts = [(0.0, S.clip("C1", 33.0, 0.8, (1.0, 1.06))), (0.75, S.clip("S1", 42.2, 0.8, (1.0, 1.06))),
            (1.5, S.clip("B5", 39.2, 0.8, (1.0, 1.06))), (2.25, S.clip("K2", 22.2, 2.0, (1.0, 1.08)))]

    def draw(img, t):
        st, fx = [c for c in cuts if t >= c[0]][-1]
        S.show(img, fx, t - st, dim=0.35)
        S.flash(img, t, st, strength=0.45)
        if t >= w("all-star") - 0.1:
            S.kinetic(img, "THE ALL-STAR TEAM", t, w("all-star") - 0.1, y=470, size=140, col=INK, block=YELLOW)
            block_text(img, (W / 2, 620), "OF THE CS2 ERA", 60, WHITE, INK, a=ramp(t, w("era?"), 0.2), anchor="m")

    ev = [(c[0], "whoosh", -12) for c in cuts] + [(w("all-star") - 0.1, "big", -6)]
    render_section("a00", "a00", draw, sfx=sfx_list(ev), lead=lead, tail=0.5, caption_style="Box")


def roster_section(sid, team, col, heading, extra=None):
    import allstars as A
    lead = 0.15
    w = Words(sid, lead)

    def draw(img, t):
        d = ImageDraw.Draw(img)
        S.title(d, heading, t, 0.05, col=col)
        A.roster(img, t, w, team, col)
        if extra:
            extra(img, t, w)

    on = [w(p[3]) - 0.1 for p in team]
    ev = [(0.05, "whoosh", -12)] + [(x, "stamp", -6) for x in on]
    render_section(sid, sid, draw, sfx=sfx_list(ev), lead=lead, tail=0.5)


TEAM1 = [("IN-GAME LEADER", "apEX", "vit", "apEX,", [("2 CS2 MAJORS AS CAPTAIN", "captain")]),
         ("AWP", "ZywOo", "vit", "ZywOo.", [("MVP OF BOTH VITALITY TITLES", "ZywOo."), ("#1 KAST  ·  #1 DMG DIFF", "Star")]),
         ("STAR RIFLER", "donk", "spirit", "donk", [("LEADS 12 OF 25 CATEGORIES", "no"), ("RATING 1.49", "debate.")]),
         ("RIFLER", "jL", "navi", "jL,", [("MAJOR TITLE  ·  MAJOR MVP", "jL,"), ("FANS' PICK", "fans'")]),
         ("ANCHOR", "ropz", "vit", "ropz", [("4 FINALS  ·  2 TITLES", "ropz"), ("#1 PLAYOFF CLUTCHES", "clutches")])]
TEAM2 = [("IN-GAME LEADER", "karrigan", "falcons", "karrigan,", [("4 MAJOR FINALS", "four"), ("MOST ASSISTS  ·  MOST MAPS", "finals.")]),
         ("AWP", "m0NESY", "falcons", "m0NESY,", [("MOST AWP KILLS  ·  511", "AWP"), ("COLOGNE MVP", "kills.")]),
         ("STAR RIFLER", "NiKo", "falcons", "NiKo,", [("COLOGNE CHAMPION", "Cologne"), ("ELITE CT SIDE", "champion.")]),
         ("RIFLER", "frozen", "faze", "frozen,", [("MOST CLUTCHES  ·  28", "clutches"), ("2nd IN KILLS", "anyone.")]),
         ("ANCHOR", "b1t", "navi", "b1t", [("COPENHAGEN CHAMPION", "b1t"), ("MAUISNAKE: TOP-2 ANCHOR AFTER ropz", "Mauisnake,")])]


def a01():
    def extra(img, t, w):
        if t >= w("no"):
            S.stamp(img, "NO DEBATE", 70 + 2 * 362 + 170, 905, t, w("no"), col=YELLOW, size=54, angle=-4)
    roster_section("a01", TEAM1, YELLOW, "TEAM 1  ·  THE ALL-STARS", extra)


def a02():
    def extra(img, t, w):
        if t >= w("frozen,"):
            block_text(img, (70 + 3 * 362, 880), "THE NUMBERS", 40, INK, SILVER, a=ramp(t, w("frozen,"), 0.2))
        if t >= w("Mauisnake,"):
            text(ImageDraw.Draw(img), (W - 70, 1000), "Anchor tier list: Mauisnake (analyst opinion)", 26, MUTED, anchor="rm")
    roster_section("a02", TEAM2, SILVER, "TEAM 2  ·  THE CHALLENGERS", extra)


def a03():
    lead = 0.15
    w = Words("a03", lead)
    pairs = [("jL", "frozen", w("jL"), "navi", "faze"), ("apEX", "karrigan", w("apEX"), "vit", "falcons"),
             ("ZywOo", "m0NESY", w("ZywOo"), "vit", "falcons")]
    t_build, t_sg, t_fz, t_see = w("Build"), w("Singapore", 0), w("Will"), w("See")
    sg_fx = S.clip("A2", 36.5, 3.5, (1.0, 1.1))

    def draw(img, t):
        d = ImageDraw.Draw(img)
        if t < t_sg - 0.1:
            S.title(d, "WHICH ROLE DOES TEAM 2 WIN?", t, 0.1)
            for k, (a_, b_, tk, la, lb) in enumerate(pairs):
                if t < tk - 0.05:
                    continue
                p = ease((t - tk + 0.05) / 0.2)
                y = 250 + k * 170
                logo(img, 110 - 60 * (1 - p), y + 22, la, h=60, a=p, wmax=220)
                text(d, (W / 2 - 110 - 60 * (1 - p), y + 60), a_, 84, YELLOW, anchor="rm")
                text(d, (W / 2 + 110 + 60 * (1 - p), y + 60), b_, 84, SILVER, anchor="lm")
                logo(img, W - 110 + 60 * (1 - p), y + 22, lb, h=60, a=p, anchor="r", wmax=240)
                pulse = 1 + 0.12 * math.sin((t - tk) * 7)
                rrect(d, (W / 2 - 60 * pulse, y + 60 - 60 * pulse, W / 2 + 60 * pulse, y + 60 + 60 * pulse), 16, fill=WHITE)
                text(d, (W / 2, y + 62), "?", int(90 * pulse), INK, anchor="mm", bg=WHITE)
            if t >= t_build:
                block_text(img, (W / 2, 790), "BUILD YOUR ALL-STAR FIVE IN THE COMMENTS", 52, INK, YELLOW, a=ramp(t, t_build, 0.25), anchor="m")
            return
        S.show(img, sg_fx, min(t - t_sg, 3.4), dim=0.55, blur=3)
        side_shade(img, 1.0, frac=0.8)
        block_text(img, (110, 160), "NEXT", 44, INK, YELLOW, a=ramp(t, t_sg - 0.1, 0.2))
        sc = 1.3 - 0.3 * ease((t - t_sg) / 0.15)
        d.text((116, 348), "SINGAPORE", font=font(int(180 * sc)), fill=(0, 0, 0), anchor="lm")
        d.text((110, 340), "SINGAPORE", font=font(int(180 * sc)), fill=WHITE, anchor="lm")
        block_text(img, (114, 430), "PGL MAJOR  ·  25 NOV – 13 DEC 2026", 52, INK, YELLOW, a=ramp(t, w("twenty-fifth"), 0.25))
        if t >= t_fz:
            logo(img, 114, 560, "faze", h=70, a=ramp(t, t_fz, 0.25), wmax=200)
            block_text(img, (330, 560), "WILL FAZE FINALLY WIN A FINAL?", 50, WHITE, (222, 36, 48), a=ramp(t, t_fz, 0.25))

    ev = [(0.1, "whoosh", -12)] + [(p[2] - 0.05, "pop", -8) for p in pairs] + [(t_build, "hit", -10), (t_sg - 0.1, "big", -7),
                                                                                 (t_fz, "stamp", -6), (t_see, "rise", -14)]
    render_section("a03", "a03", draw, sfx=sfx_list(ev), lead=lead, tail=1.0, caption_style="Low")


ORDER = ["s00", "s01", "s02", "s03", "s04", "c1a", "c1b", "c1m", "c2a", "c2b", "c2m", "c3a", "c3b", "c3m",
         "c4a", "c4b", "c4m", "c5a", "c5b", "c5m", "a00", "a01", "a02", "a03"]


# ---------- end card: channel ident + end-screen space ----------
def z99():
    lg = Image.open(r"D:\Youtube\video03\work\logo.png").convert("RGBA")
    lg.thumbnail((300, 300))
    dur = 0.3 + 7.7 + 6.0

    def draw(img, t):
        d = ImageDraw.Draw(img)
        a = ramp(t, 0.3, 0.5)
        l2 = lg.copy(); l2.putalpha(l2.getchannel("A").point(lambda v: int(v * a)))
        img.paste(l2, (W // 2 - l2.width // 2, 110), l2)
        text(d, (W // 2, 480), "SPORTS ON THE LINE", 84, WHITE, anchor="mm", alpha=a, tracking=8)
        text(d, (W // 2, 560), "data stories from the games we love", 34, MUTED, anchor="mm", alpha=ramp(t, 1.3, 0.5))

    render_section("z99", None, draw, sfx=[(0.3, "ident", 0)], lead=0.0, dur=dur)

if __name__ == "__main__":
    for sid in (sys.argv[1:] or ORDER):
        globals()[sid]()
