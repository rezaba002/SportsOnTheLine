"""Video 04 sections s01–s05 (acts 1–4 + verdict), cut v2: slower, and every analysis ends on a held conclusion.
python sections4b.py s01 [s02 ...]   (run with NAR_DIR=narration_v2; v1 kept as sections4b_v1.py)

Layout rules (no overlaps): title band y 90–170 · content y 200–800 · conclusion strip y 800–930 ·
captions (Low) from y ~960 down. Takeaway cards dim everything behind them.
"""
import math, sys
import numpy as np
from PIL import Image, ImageDraw

from sections4 import *          # noqa: F401,F403  (engine, fx, TL, v2, Src, wt, sub, tag, logo, FOOT2, FOOT4, INK)

S = v2.S
GREEN_HP, RED_HP, CASH, GREY = (88, 196, 104), (214, 64, 58), (120, 214, 110), (150, 156, 170)
HOLD = 1.4                       # silence after a conclusion line, with its card still on screen


def segs_of(*ids, gap=0.4, holds=()):
    return [{"nar": i, "gap": HOLD if i in holds else gap} for i in ids]


def strip(img, s, t, t_on, y=840, size=52):
    """Conclusion strip under the content (yellow block, centred)."""
    if t >= t_on:
        block_text(img, (W / 2, y), s, size, INK, YELLOW, a=ease((t - t_on) / 0.3), anchor="m", pad=(30, 14))


def grow(t, at, dur=0.8):
    return ease((t - at) / dur) if t >= at else 0.0


# ---------- S01: it looks like destiny ----------
def s01():
    segs = segs_of("a1a", "a1t", "a1b", "a1c", holds=("a1t",))
    segs[-1]["gap"] = 1.0
    sch, _ = TL.schedule(segs)
    w = lambda pid, word, n=0: wt(sch, pid, word, n)
    champs = [("navi", "COPENHAGEN 2024", 47, "4/4"), ("spirit", "SHANGHAI 2024", 61, "5/5"), ("vit", "AUSTIN 2025", 62, "4/4"),
              ("vit", "BUDAPEST 2025", 58, "6/6"), ("falcons", "COLOGNE 2026", 63, "4/7")]
    t_win, t_lose = w("a1a", "Win"), w("a1a", "Lose")
    t_split = (w("a1a", "three.") + t_lose) / 2 - 0.4
    t_card = sch["a1t"][0] + 0.2
    t_ch, t_took, t_23 = w("a1b", "champions?"), w("a1b", "took"), w("a1b", "twenty-three")
    t_case = sch["a1c"][0]

    def draw(img, t, sch):
        d = ImageDraw.Draw(img)
        if t < sch["a1b"][0] - 0.1:
            S.title(d, "MAP RESULT BY PISTOLS WON  ·  379 MAPS", t, 0.1)
            d.text((1770, 240), "MAPS WON OF 3", font=font(26), fill=MUTED, anchor="mm")
            rows = [("WON BOTH", 0.66, GREEN_HP, "66%", t_win, 2), ("SPLIT 1–1", 0.50, GREY, "50%", t_split, None),
                    ("LOST BOTH", 0.34, RED_HP, "34%", t_lose, 1)]
            for i, (lab, fr, col, val, at, k) in enumerate(rows):
                y = 290 + i * 170
                p = grow(t, at)
                d.text((510, y + 45), lab, font=font(46), fill=WHITE if t >= at else MUTED, anchor="rm")
                d.rounded_rectangle([540, y, 1440, y + 90], 10, fill=(30, 34, 44))
                if p > 0:
                    d.rounded_rectangle([540, y, 540 + max(900 * fr * p, 12), y + 90], 10, fill=col)
                if p > 0.95:
                    d.text((1470, y + 45), val, font=font(72), fill=col, anchor="lm")
                if k is not None and t >= at + 0.8:
                    for j in range(3):
                        d.rounded_rectangle([1690 + j * 60, y + 22, 1736 + j * 60, y + 68], 8, fill=col if j < k else (50, 54, 66))
            out = fx.punch(img, t, t_win, 0.03)
            out = fx.punch(out, t, t_lose, 0.03)
            return fx.takeaway(out, t, t_card, 1, [("ON PAPER:", MUTED), ("EVERY PISTOL WON", WHITE), ("= +16% TO WIN THE MAP", YELLOW)])
        S.title(d, "THE CHAMPIONS' PISTOLS ON THEIR TITLE RUN", t, sch["a1b"][0])
        for i, (k, ev, pct, both) in enumerate(champs):
            at = sch["a1b"][0] + 0.05 + i * 0.22
            if t < at:
                continue
            p = ease((t - at) / 0.3)
            x, dy = 70 + i * 362, 40 * (1 - p)
            d.rounded_rectangle([x, 220 + dy, x + 340, 760 + dy], 18, fill=(24, 28, 38), outline=(60, 66, 80), width=2)
            logo(img, x + 170, 250 + dy, k, h=80, a=p, anchor="m", wmax=280)
            d.text((x + 170, 400 + dy), ev, font=font(30, "SemiBold"), fill=MUTED, anchor="mm")
            d.text((x + 170, 480 + dy), f"{pct}%", font=font(80), fill=WHITE, anchor="mm")
            d.text((x + 170, 540 + dy), "PISTOLS WON", font=font(26), fill=MUTED, anchor="mm")
            if t >= t_took + i * 0.2:
                q = ease((t - t_took - i * 0.2) / 0.25)
                d.rounded_rectangle([x + 30, 600, x + 310, 730], 14, fill=GREEN_HP if both != "4/7" else (190, 150, 50))
                d.text((x + 170, 640), "WON BOTH PISTOLS", font=font(24), fill=INK, anchor="mm")
                d.text((x + 170, 692), f"{both} MAPS", font=font(int(46 * (1.2 - 0.2 * q))), fill=INK, anchor="mm")
        if t >= t_23:
            v = 23 * ease((t - t_23) / 0.6)
            block_text(img, (W / 2, 810), f"{int(round(v))} OF 26 MAPS WON", 76, INK, YELLOW, a=ease((t - t_23) / 0.2), anchor="m", pad=(40, 18))
        if t >= t_case - 0.05:
            img = Image.blend(img.convert("L").convert("RGB"), img, 0.3)
            img = Image.blend(img, Image.new("RGB", (W, H), BG), 0.6 * ease((t - t_case + 0.05) / 0.25))
            S.stamp(img, "CASE CLOSED?", W / 2, 480, t, t_case - 0.05, col=YELLOW, size=130, angle=-6)
        return fx.punch(img, t, t_23, 0.04)

    sfx = [(t_win + 0.8, "hitmarker", -8), (t_lose + 0.8, "hitmarker", -8), (t_card, "stamp-thud", -9),
           (sch["a1b"][0] - 0.1, "whoosh-short", -12)] + [(sch["a1b"][0] + 0.05 + i * 0.22, "feed-tick", -10) for i in range(5)] + \
          [(t_took + i * 0.2, "pop-1", -15) for i in range(5)] + [(t_23, "stinger-hit-short", -8), (t_case - 0.05, "stamp-thud", -5)]
    TL.render("s01", segs, draw, sfx=sfx, tail=0.3)


# ---------- S02: the snowball, the loser's choice, donk's eco, the trend ----------
def s02():
    segs = segs_of("a2a", "a2t", "a2b", "a2u", holds=("a2t", "a2u")) + \
        [{"nar": "a2c", "gap": 0.2}, {"clip": "S1", "src": FOOT2 + r"\S1.mp4", "in": 4.3, "out": 9.7, "gain": -4, "gap": 0.3}] + \
        segs_of("a2d", "a2e", "a2v", holds=("a2v",))
    segs[-1]["gap"] = 1.0
    sch, _ = TL.schedule(segs)
    w = lambda pid, word, n=0: wt(sch, pid, word, n)
    t_here, t_r1, t_80, t_23, t_half = w("a2a", "Here's"), w("a2a", "Win"), w("a2a", "eighty"), w("a2a", "But"), w("a2a", "half")
    t_card2 = sch["a2t"][0] + 0.2
    t_force, t_one, t_broke, t_save, t_away, t_coin = w("a2b", "Force-buy,"), w("a2b", "one"), w("a2b", "broke."), w("a2b", "save"), \
        w("a2b", "away,"), w("a2b", "coin")
    t_tab, t_shot2, t_shot3 = sch["a2u"][0], w("a2u", "two."), w("a2u", "three.")
    t_never, t_almost = w("a2c", "never"), w("a2c", "Almost.")
    t_first, t_col, t_more = w("a2d", "first"), w("a2d", "Cologne,"), w("a2d", "force")
    t_end_half, t_end_map, t_flip = w("a2e", "half,"), w("a2e", "map,"), w("a2e", "flips.")
    t_card3 = sch["a2v"][0] + 0.1
    s1 = Src(FOOT2 + r"\S1.mp4", 4.2, 9.9)
    k_out = [sch["S1"][0] + (k - 4.3) for k in (5.45, 9.05)]
    trend = [("COPENHAGEN", 53), ("SHANGHAI", 40), ("AUSTIN", 35), ("BUDAPEST", 40), ("COLOGNE", 32)]

    def draw(img, t, sch):
        d = ImageDraw.Draw(img)
        if t < sch["a2b"][0] - 0.1:                                         # what a pistol buys: R2 80%, R2+R3 54%
            S.title(d, "AFTER A PISTOL WIN  ·  758 PISTOLS", t, 0.05)
            if t < t_here - 0.05:
                fx.word_pop(img, "NOT QUITE.", W / 2, 500, t, 0.0, size=170, col=YELLOW)
                return fx.glitch_at(img, t, 0.0, 0.2, 26)
            tiles = [("PISTOL", "WON", "", t_r1, GREEN_HP, 1.0), ("ROUND 2", "80%", "WON THE NEXT ROUND", t_80, GREEN_HP, 0.8),
                     ("ROUNDS 2 + 3", "54%", "WON BOTH NEXT ROUNDS", t_23, (200, 150, 50), 0.54)]
            for i, (lab, val, note, at, col, fr) in enumerate(tiles):
                x = 230 + i * 540
                d.rounded_rectangle([x, 260, x + 380, 640], 22, fill=(26, 30, 40))
                if t < at:
                    d.text((x + 190, 310), lab, font=font(42), fill=MUTED, anchor="mm")
                    continue
                p = grow(t, at, 0.6)
                broken = i == 2 and t >= t_half
                c = RED_HP if broken else col
                d.rounded_rectangle([x, 260, x + 380, 640], 22, outline=c, width=5)
                d.rounded_rectangle([x + 18, 622 - 260 * fr * p, x + 362, 622], 16, fill=c)
                if broken:                                                  # crack: jagged lines on the tile, under the text
                    d.line([(x + 120, 262), (x + 170, 360), (x + 140, 440), (x + 210, 530), (x + 180, 638)], fill=(14, 14, 18), width=7)
                    d.line([(x + 210, 530), (x + 300, 600)], fill=(14, 14, 18), width=5)
                d.text((x + 190, 310), lab, font=font(42), fill=WHITE, anchor="mm")
                sz = int(120 * (1.2 - 0.2 * p))
                d.text((x + 194, 506), val, font=font(sz), fill=(0, 0, 0), anchor="mm")
                d.text((x + 190, 500), val, font=font(sz), fill=WHITE, anchor="mm")
                if note:
                    d.text((x + 190, 690), note, font=font(30), fill=MUTED, anchor="mm")
                if i < 2 and t >= tiles[i + 1][3]:
                    d.polygon([(x + 410, 430), (x + 470, 450), (x + 410, 470)], fill=MUTED)
            out = fx.punch(img, t, t_80, 0.03)
            out = fx.shake(out, t, t_half, 16)
            return fx.takeaway(out, t, t_card2, 2, [("A PISTOL BUYS ROUND 2", WHITE), ("NOT ROUND 3", YELLOW)])
        if t < sch["a2c"][0] - 0.1:                                         # the loser's choice -> the comparison table
            S.title(d, "LOST THE PISTOL  ·  WHAT NOW?", t, sch["a2b"][0] - 0.1)
            if t < t_tab - 0.05:
                d.line([(W / 2, 210), (W / 2, 800)], fill=(60, 66, 80), width=4)
                if t < t_force - 0.1:
                    text(d, (480, 260), "FORCE?", 110, (90, 96, 110), anchor="mm", alpha=ramp(t, sch["a2b"][0], 0.3))
                    text(d, (1440, 260), "ECO?", 110, (90, 96, 110), anchor="mm", alpha=ramp(t, sch["a2b"][0] + 0.15, 0.3))
                if t >= t_force - 0.1:
                    fx.word_pop(img, "FORCE-BUY", 480, 260, t, t_force - 0.1, size=100, col=RED_HP)
                    fx.money(img, 480, 400, 600, t, t_force, frm=12000, dur=1.2, size=100, col=CASH if t < t_broke else RED_HP, anchor="mm")
                    d.text((480, 475), "LEFT AFTER BUYING", font=font(30), fill=MUTED, anchor="mm")
                    if t >= t_one:
                        block_text(img, (480, 545), "WINS ROUND 2: 1 IN 3", 50, INK, YELLOW, a=ease((t - t_one) / 0.2), anchor="m")
                    if t >= t_broke:
                        S.stamp(img, "BROKE", 480, 720, t, t_broke, col=RED_HP, size=90, angle=-8)
                if t >= t_save - 0.1:
                    fx.word_pop(img, "SAVE (ECO)", 1440, 260, t, t_save - 0.1, size=100, col=CASH)
                    fx.money(img, 1440, 400, 10150, t, t_save, frm=0, dur=1.0, size=100, anchor="mm")
                    d.text((1440, 475), "KEPT FOR ROUND 3", font=font(30), fill=MUTED, anchor="mm")
                    if t >= t_away:
                        block_text(img, (1440, 545), "GIVES ROUND 2 AWAY", 50, WHITE, (60, 66, 80), a=ease((t - t_away) / 0.2), anchor="m")
                    if t >= t_coin - 0.2:
                        wc = abs(math.cos((t - t_coin + 0.2) * 9)) * 70 + 6 if t < t_coin + 0.8 else 76
                        d.ellipse([1440 - wc, 650, 1440 + wc, 802], fill=(232, 190, 60), outline=(150, 110, 20), width=6)
                        if t >= t_coin + 0.8:
                            d.text((1440, 726), "49%", font=font(52), fill=INK, anchor="mm")
                            d.text((1440, 850), "ROUND 3 = A COIN FLIP", font=font(34), fill=WHITE, anchor="mm")
                out = fx.punch(img, t, t_force, 0.03)
                return fx.punch(out, t, t_save, 0.03)
            # comparison table (the conclusion of the choice), held
            a = ease((t - t_tab + 0.05) / 0.3)
            for j, (lab, col) in enumerate([("FORCE-BUY", RED_HP), ("SAVE (ECO)", CASH)]):
                text(d, (900 + j * 480, 280), lab, 64, col, anchor="mm", alpha=a)
            rows = [("WIN ROUND 2", 32, 1, t_tab + 0.2, t_shot2), ("WIN ROUND 3", 36, 49, t_tab + 0.5, t_shot3)]
            for i, (lab, f, e, at, t_hi) in enumerate(rows):
                if t < at:
                    continue
                y, q = 430 + i * 190, ease((t - at) / 0.3)
                text(d, (620, y), lab, 52, WHITE, anchor="rm", alpha=q)
                best = 0 if f > e else 1
                for j, v in enumerate((f, e)):
                    cx = 900 + j * 480
                    hi = t >= t_hi - 0.3 and j == best
                    if hi:
                        d.rounded_rectangle([cx - 170, y - 75, cx + 170, y + 75], 18, fill=(50, 44, 20), outline=YELLOW, width=5)
                    text(d, (cx, y), f"{v}%", 96, YELLOW if hi else GREY, anchor="mm", alpha=q, bg=(50, 44, 20) if hi else BG)
            strip(img, "FORCE = A SHOT AT ROUND 2  ·  ECO = A SHOT AT ROUND 3", t, t_shot3, y=800, size=48)
            return img
        if t < sch["S1"][0]:                                                # "almost never"
            S.title(d, "ECO TEAMS IN ROUND 2  ·  298 ECOS", t, sch["a2c"][0] - 0.1)
            fx.word_pop(img, "1%", W / 2, 460, t, sch["a2c"][0], size=300, col=RED_HP)
            d.text((W / 2, 640), "OF ECO TEAMS WON ROUND 2", font=font(46), fill=MUTED, anchor="mm")
            if t >= t_almost:
                img = fx.flash(img, t, t_almost, 0.2, 0.6)
                fx.word_pop(img, "ALMOST.", W / 2, 790, t, t_almost, size=120, col=YELLOW)
            return img
        if t < sch["a2d"][0] - 0.1:                                         # donk's eco Deagles
            fr = s1.frame(4.3 + (t - sch["S1"][0]))
            for k in k_out:
                fr = fx.punch(fr, t, k, 0.08)
                fr = fx.flash(fr, t, k, 0.06, 0.4)
            ImageDraw.Draw(fr, "RGBA").rectangle([0, 0, 900, 240], fill=(0, 0, 0, 160))
            fx.killfeed(fr, [(k_out[0], "donk", "Desert Eagle", "FaZe", True), (k_out[1], "donk", "Desert Eagle", "FaZe", True)], t, y0=150)
            for k in k_out:
                fx.hitmarker(fr, W / 2, H / 2, t, k, hs=True)
            block_text(fr, (60, 60), "ECO ROUND · ROUND 2", 40, INK, YELLOW, pad=(18, 10))
            tag(fr, "donk · SHANGHAI MAJOR FINAL · NUKE", y=990)
            return fx.flash(fr, t, sch["S1"][0], 0.08, 0.6)
        if t < sch["a2e"][0] - 0.1:                                         # eco share per Major
            S.title(d, "PISTOL LOSERS WHO SAVED (ECO)  ·  BY MAJOR", t, sch["a2d"][0] - 0.1)
            shown = []
            for i, (lab, v) in enumerate(trend):
                x, y = 330 + i * 315, 740 - v * 9
                d.text((x, 775), lab, font=font(32), fill=MUTED, anchor="mm")
                if t >= t_first + (t_col - t_first) * i / 4:
                    shown.append((x, y))
                    d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=YELLOW)
                    d.text((x, y - 52), f"{v}%", font=font(54), fill=WHITE, anchor="mm")
            if len(shown) > 1:
                d.line(shown, fill=YELLOW, width=6)
            strip(img, "TEAMS FORCE MORE AND MORE", t, t_more, y=840, size=48)
            return img
        # how it ends: half and map won, force vs eco -> takeaway 3
        S.title(d, "AFTER A LOST PISTOL  ·  HOW IT ENDS", t, sch["a2e"][0] - 0.1)
        for g, (lab, f, e, at) in enumerate([("HALF WON", 32, 27, sch["a2e"][0] + 0.6), ("MAP WON", 40, 46, t_end_map)]):
            if t < at - 0.6:
                continue
            y0, p = 300 + g * 270, grow(t, at - 0.6, 0.7)
            d.text((560, y0 + 64), lab, font=font(50), fill=WHITE, anchor="rm")
            for j, (name, v, col) in enumerate([("FORCE", f, RED_HP), ("ECO", e, CASH)]):
                y = y0 + j * 72
                d.rounded_rectangle([600, y, 600 + 18 * v * p, y + 56], 8, fill=col)
                hi = t >= t_flip and v == max(f, e)
                d.text((620 + 18 * v * p, y + 28), f"{name} {v}%", font=font(44), fill=YELLOW if hi else WHITE, anchor="lm")
        if t >= t_flip:
            d.text((W / 2, 860), "SMALL GAPS  ·  AND THEY POINT OPPOSITE WAYS", font=font(40), fill=MUTED, anchor="mm")
        return fx.takeaway(img, t, t_card3, 3, [("FORCE OR SAVE:", WHITE), ("NO CLEAR WINNER", YELLOW)])

    sfx = [(0.0, "tape-stop", -10), (t_r1, "hitmarker", -8), (t_80, "pop-1", -9), (t_23, "pop-2", -9), (t_half, "glitch-burst", -10),
           (t_card2, "stamp-thud", -9), (sch["a2b"][0] - 0.1, "whoosh-short", -12), (t_force, "cash-register-cha-ching", -13),
           (t_broke, "stamp-thud", -6), (t_save, "coins-handful-1", -13), (t_coin - 0.2, "coin-drop", -11), (t_tab, "whoosh-short", -13),
           (t_shot2 - 0.3, "select-1", -11), (t_shot3 - 0.3, "select-1", -11), (t_never, "error-buzz-soft", -11), (t_almost, "sub-drop", -8)] + \
          [(k, "hitmarker", -10) for k in k_out] + [(k_out[0], "headshot-ding", -12),
           (sch["a2d"][0] - 0.1, "whoosh-medium-1s", -12), (t_first, "feed-tick", -9), (t_col, "feed-tick", -9),
           (sch["a2e"][0] - 0.1, "whoosh-short", -13), (t_flip, "pop-2", -10), (t_card3, "stamp-thud", -8)]
    TL.render("s02", segs, draw, sfx=sfx, tail=0.3)


# ---------- S03: the catch ----------
def s03():
    segs = segs_of("a3a", "a3b", "a3t", "a3c", "a3u", holds=("a3t", "a3u"))
    segs[-1]["gap"] = 1.0
    sch, _ = TL.schedule(segs)
    w = lambda pid, word, n=0: wt(sch, pid, word, n)
    t_better, t_maps, t_16 = w("a3a", "Better"), w("a3a", "maps."), w("a3a", "sixteen")
    t_same, t_only = w("a3b", "same"), w("a3b", "Only")
    t_seven, t_card4 = w("a3t", "seven"), w("a3t", "about", 1)
    t_navi, t_losing, t_one, t_still = w("a3c", "NaVi"), w("a3c", "losing"), w("a3c", "one"), w("a3c", "still")
    t_card5 = sch["a3u"][0] + 0.05

    def draw(img, t, sch):
        d = ImageDraw.Draw(img)
        if t < sch["a3b"][0] - 0.1:
            S.title(d, "THE CATCH", t, 0.05)
            if t < t_better - 0.05:
                fx.word_pop(img, "THE CATCH.", W / 2, 480, t, 0.0, size=170, col=YELLOW)
                return fx.glitch_at(img, t, 0.0, 0.2, 26)
            fx.word_pop(img, "BETTER TEAM", 470, 470, t, t_better, size=100)
            for j, (lab, at) in enumerate([("MORE PISTOLS", t_better + 0.6), ("MORE MAPS", t_maps - 0.3)]):
                if t >= at:
                    p = ease((t - at) / 0.3)
                    d.line([(830, 470), (830 + 260 * p, 370 + 200 * j)], fill=YELLOW, width=8)
                    block_text(img, (1120, 330 + 200 * j), lab, 64, INK, YELLOW, a=p)
            strip(img, "PART OF THE +16% IS JUST THE BETTER TEAM", t, t_16, y=760, size=52)
            return img
        if t < sch["a3t"][0] - 0.1:                                         # same two teams, same series
            S.title(d, "THE FAIR TEST", t, sch["a3b"][0] - 0.1)
            d.text((W / 2, 230), "SAME TWO TEAMS  ·  SAME SERIES  ·  MAP AGAINST MAP", font=font(46), fill=YELLOW, anchor="mm")
            for i, (m, pis, res) in enumerate([("MAP 1", 2, "W"), ("MAP 2", 0, "L"), ("MAP 3", 1, "W")]):
                at = sch["a3b"][0] + 0.2 + i * 0.45
                if t < at:
                    continue
                x, p = 190 + i * 540, ease((t - at) / 0.3)
                dy = 30 * (1 - p)
                d.rounded_rectangle([x, 290 + dy, x + 460, 710 + dy], 20, fill=(24, 28, 38), outline=(60, 66, 80), width=3)
                d.text((x + 230, 340 + dy), m, font=font(48), fill=WHITE, anchor="mm")
                d.text((x + 230, 410 + dy), "TEAM A's PISTOLS", font=font(30), fill=MUTED, anchor="mm")
                for j in range(2):
                    d.ellipse([x + 135 + j * 120, 445 + dy, x + 205 + j * 120, 515 + dy], fill=GREEN_HP if j < pis else (70, 74, 86))
                d.text((x + 230, 570 + dy), f"{pis} OF 2", font=font(44), fill=WHITE, anchor="mm")
                d.text((x + 230, 650 + dy), "A WINS THE MAP" if res == "W" else "A LOSES THE MAP", font=font(40),
                       fill=GREEN_HP if res == "W" else RED_HP, anchor="mm")
            strip(img, "SAME PLAYERS · SAME STRENGTH · ONLY THE PISTOLS CHANGE", t, t_only - 0.1, y=790, size=46)
            return img
        if t < sch["a3c"][0] - 0.1:                                         # +16 -> +7, then takeaway 4
            S.title(d, "WHAT ONE PISTOL IS WORTH", t, sch["a3t"][0] - 0.1)
            fx.word_pop(img, "+16%", W / 2 - 400, 470, t, sch["a3t"][0], size=190, col=GREY)
            d.text((W / 2 - 400, 620), "ALL MAPS (RAW)", font=font(40), fill=MUTED, anchor="mm")
            if t >= t_seven - 0.2:
                d.line([(W / 2 - 600, 540), (W / 2 - 200, 400)], fill=RED_HP, width=14)
            if t >= t_seven:
                fx.word_pop(img, "+7%", W / 2 + 400, 470, t, t_seven, size=240, col=YELLOW)
                d.text((W / 2 + 400, 620), "SAME TEAMS", font=font(40), fill=MUTED, anchor="mm")
            out = fx.punch(img, t, t_seven, 0.05)
            return fx.takeaway(out, t, t_card4, 4, [("BETWEEN EQUAL TEAMS", WHITE), ("A PISTOL = ~7% OF A MAP", YELLOW),
                                                     ("HALF THE 16% WAS TEAM STRENGTH", MUTED)])
        if t < t_one - 0.1:                                                 # NaVi won the Major losing most pistols
            logo(img, W / 2, 170, "navi", h=150, anchor="m", wmax=420, a=ease((t - t_navi) / 0.3))
            d.text((W / 2, 385), "COPENHAGEN 2024 · CHAMPIONS", font=font(48), fill=YELLOW, anchor="mm")
            if t >= t_losing - 0.1:
                fx.word_pop(img, "15 / 32", W / 2, 530, t, t_losing - 0.1, size=150, col=WHITE)
                d.text((W / 2, 650), "PISTOLS WON  ·  47%", font=font(44), fill=MUTED, anchor="mm")
                strip(img, "AND STILL WON THE MAJOR", t, t_losing + 0.6, y=760, size=56)
            return fx.punch(img, t, t_navi, 0.04)
        S.title(d, "LOST BOTH PISTOLS  ·  STILL WON THE MAP", t, t_one - 0.1)
        for j in range(3):
            x = W / 2 - 360 + j * 360
            lit = j == 2 and t >= t_still
            d.ellipse([x - 90, 230, x + 90, 410], fill=YELLOW if lit else (60, 64, 76))
            d.rounded_rectangle([x - 120, 430, x + 120, 600], 40, fill=YELLOW if lit else (60, 64, 76))
        if t >= t_still:
            block_text(img, (W / 2, 640), "63 OF 185 MAPS  ·  1 IN 3", 64, INK, YELLOW, a=ease((t - t_still) / 0.2), anchor="m")
            for i, (k, n) in enumerate([("spirit", 8), ("g2", 8), ("navi", 7)]):
                at = t_still + 0.3 + i * 0.15
                logo(img, 560 + i * 400, 820, k, h=60, a=ease((t - at) / 0.2), anchor="m", wmax=220)
                if t >= at:
                    d.text((690 + i * 400, 850), f"×{n}", font=font(48), fill=WHITE, anchor="lm")
        return fx.takeaway(img, t, t_card5, 5, [("LOSING THE PISTOLS", WHITE), ("IS NOT LOSING THE MAP", YELLOW)])

    sfx = [(0.0, "glitch-soft-1", -12), (t_better, "bass-hit", -9), (t_better + 0.6, "pop-1", -11), (t_maps - 0.3, "pop-2", -11),
           (sch["a3b"][0] - 0.1, "whoosh-short", -12)] + [(sch["a3b"][0] + 0.2 + i * 0.45, "feed-tick", -9) for i in range(3)] + \
          [(sch["a3t"][0], "stamp-thud", -11), (t_seven, "sub-drop", -8), (t_card4, "stamp-thud", -8),
           (t_navi, "stinger-hit-short", -9), (t_losing, "pop-1", -11), (t_one - 0.1, "whoosh-short", -12), (t_still, "success-bell", -12),
           (t_card5, "stamp-thud", -8)]
    TL.render("s03", segs, draw, sfx=sfx, tail=0.3)


# ---------- S04: luck or skill + the countdown (no leak of #1 before the reveal) ----------
TOP = [("yuurih", "furia", 89.9), ("Senzu", "mongolz", 90.7), ("XANTARES", "aurora", 91.6), ("snow", "pain", 93.0),
       ("m0NESY", "falcons", 93.8), ("xertioN", "mouz", 94.5), ("ZywOo", "vit", 99.0), ("frozen", "faze", 102.0),
       ("kyousuke", "falcons", 102.1)]                       # #10 .. #2; #1 = donk 119.8, revealed only in a4d
# real team pistol records (>= 20 pistols), D:\Research\cs2-pistols\results\pistols.json leaderboard
REAL = [("9z", 21, 32), ("Vitality", 70, 116), ("Falcons", 36, 62), ("MOUZ", 61, 108), ("Aurora", 21, 38), ("Monte", 12, 22),
        ("MongolZ", 49, 92), ("paiN", 38, 72), ("FaZe", 58, 110), ("HEROIC", 20, 38), ("NaVi", 63, 120), ("Spirit", 51, 102),
        ("FURIA", 42, 86), ("G2", 53, 110), ("FUT", 13, 28), ("Liquid", 14, 34), ("PARIVISION", 10, 26), ("3DMAX", 13, 34),
        ("Virtus.pro", 11, 30), ("Imperial", 6, 22), ("BetBoom", 7, 26), ("Legacy", 8, 32), ("B8", 6, 28)]


def luck_draw():
    """One coin-flip world with the same number of pistols per team, picked to have the typical (median) spread 0.074."""
    for seed in range(1000):
        r = np.random.default_rng(seed)
        v = [r.binomial(n, 0.5) / n for _, _, n in REAL]
        if abs(np.std(v) - 0.074) < 0.002:
            return sorted(v)
    raise RuntimeError("no typical draw")


def s04():
    ropz = FOOT4 + r"\ropz_mr12_random.mkv"
    segs = [{"clip": "ropz", "src": ropz, "in": 12.9, "out": 17.5, "gain": 0, "gap": 0.3}] + \
        segs_of("a4a", "a4b", "a4t", holds=("a4t",)) + [{"nar": "a4c", "gap": 2.4}, {"nar": "a4d", "gap": 0.6}]
    sch, _ = TL.schedule(segs)
    w = lambda pid, word, n=0: wt(sch, pid, word, n)
    rz = Src(ropz, 12.8, 17.6, fps=30)
    t_if = w("a4a", "If")
    t_real, t_b8, t_sim = w("a4b", "real"), w("a4b", "B8,"), w("a4b", "simulations,")
    t_card6 = sch["a4t"][0] + 0.05
    t_avg, t_these = w("a4c", "average"), w("a4c", "These")
    t_donk, t_120 = w("a4d", "donk."), w("a4d", "hundred")
    t_sixty, t_man, t_best = w("a4d", "sixty"), w("a4d", "man"), w("a4d", "best")
    steps = [t_these + i * ((sch["a4c"][1] + 1.6) - t_these) / len(TOP) for i in range(len(TOP))]
    donk_fr = Src(FOOT4 + r"\donk_tldr_remove_pistols.mkv", 10.4, 12.3, fps=30)
    luck = luck_draw()
    real = sorted(wn / n for _, wn, n in REAL)
    X0, X1 = 520, 1820
    px = lambda v: X0 + (v * 100 - 15) / 60 * (X1 - X0)            # 15% .. 75%

    def draw(img, t, sch):
        d = ImageDraw.Draw(img)
        if t < sch["a4a"][0] - 0.05:                                         # ropz on stream (facecam punch-in)
            fr = rz.frame(12.9 + (t - sch["ropz"][0]))
            fr = fr.resize((W, H), Image.LANCZOS, box=(0, 40, 520, 332))
            fr = fx.flash(fr, t, sch["ropz"][0], 0.08, 0.5)
            tag(fr, "ropz · on MR12 · 2023 stream")
            sub(fr, "“I think it's gonna be even more random results.”", t, sch["ropz"][0] + 0.1, y=860, size=58, col=INK, bg=YELLOW)
            return fr
        if t < sch["a4c"][0] - 0.1:                                          # luck vs reality: two dot strips
            S.title(d, "TEAM PISTOL WIN RATE  ·  23 TEAMS", t, sch["a4a"][0])
            d.line([(px(0.5), 250), (px(0.5), 690)], fill=(70, 76, 90), width=3)
            for v in (0.2, 0.3, 0.4, 0.5, 0.6, 0.7):
                d.text((px(v), 720), f"{int(round(v * 100))}%", font=font(32), fill=MUTED, anchor="mm")
            for row, (lab, vals, at, y) in enumerate([("PURE LUCK", luck, t_if, 380), ("REAL TEAMS", real, t_real, 590)]):
                if t < at:
                    continue
                text(d, (470, y), lab, 44, YELLOW if row else WHITE, anchor="rm", alpha=ramp(t, at, 0.3))
                for i, v in enumerate(vals):
                    q = ease((t - at - i * 0.03) / 0.25)
                    if q <= 0:
                        continue
                    x = px(0.5) + (px(v) - px(0.5)) * q
                    yy = y + (i % 3 - 1) * 22
                    col = GREY if row == 0 else (RED_HP if v < 0.4 else GREEN_HP if v > 0.57 else GREY)
                    d.ellipse([x - 15, yy - 15, x + 15, yy + 15], fill=col)
                if t >= at + 1.2:                                            # bracket: the spread
                    lo, hi = px(min(vals)), px(max(vals))
                    yb = y - 70
                    d.line([(lo, yb + 14), (lo, yb), (hi, yb), (hi, yb + 14)], fill=YELLOW if row else WHITE, width=4)
            if t >= t_b8:
                block_text(img, (px(6 / 28), 640), "B8 21%", 38, INK, RED_HP, a=ease((t - t_b8) / 0.2), anchor="m", pad=(14, 8))
            strip(img, "10,000 SIMULATIONS: LUCK NEVER SPREAD THEM THIS WIDE", t, t_sim, y=800, size=46)
            return fx.takeaway(img, t, t_card6, 6, [("PISTOL SKILL IS REAL", YELLOW), ("SOME TEAMS ARE GENUINELY BETTER", WHITE)])
        if t < t_donk - 0.15:                                                # countdown 10..2 with the average line
            S.title(d, "BEST PISTOL PLAYERS  ·  DAMAGE PER PISTOL ROUND  ·  MIN. 50 PISTOLS", t, sch["a4c"][0], size=34)
            bx0, sc = 600, 9.0
            if t >= t_avg:
                xa = bx0 + 75.6 * sc
                a = ramp(t, t_avg, 0.4)
                d.line([(xa, 190), (xa, 830)], fill=fade(WHITE, a), width=3)
                text(d, (xa, 875), "AVERAGE PLAYER: 75", 40, WHITE, anchor="mm", alpha=a)
            k = sum(1 for s in steps if t >= s)
            for i in range(k):
                name, team, dmg = TOP[i]
                y = 200 + i * 70
                p = ease((t - steps[i]) / 0.3)
                d.text((150, y + 26), f"#{10 - i}", font=font(42), fill=MUTED, anchor="lm")
                logo(img, 300, y + 7, team, h=38, a=p, anchor="m", wmax=110)
                d.text((370, y + 26), name, font=font(44), fill=WHITE, anchor="lm")
                d.rounded_rectangle([bx0, y + 8, bx0 + dmg * sc * p, y + 46], 8, fill=GREY)
                if p > 0.9:
                    d.text((bx0 + dmg * sc + 20, y + 26), f"{dmg:.0f}", font=font(40), fill=WHITE, anchor="lm")
            if t >= steps[-1] + 0.3:
                d.text((150, 856), "#1", font=font(52), fill=YELLOW, anchor="lm")
                rem = max(0.0, t_donk - t)
                fx.bomb_timer(img, 420, 856, f"{min(rem, 9.9):0.1f}", t, 2 + 6 * (1 - min(rem, 3) / 3), k=0.55)
            return fx.punch(img, t, steps[k - 1] if k else 0, 0.02)
        # #1 reveal: donk
        fr = donk_fr.frame(10.4 + min(t - t_donk, 1.8))
        side_shade(fr, 1.0, frac=0.68)
        fr = fx.flash(fr, t, t_donk - 0.1, 0.25, 1.0)
        fr = fx.shake(fr, t, t_donk - 0.1, 26)
        fx.word_pop(fr, "#1  donk", 110, 250, t, t_donk - 0.1, size=160, col=YELLOW, anchor="lm")
        logo(fr, 120, 370, "spirit", h=56, wmax=330)
        if t < t_man - 0.1:
            if t >= t_120 - 0.1:
                fx.word_pop(fr, "120", 110, 540, t, t_120 - 0.1, size=190, col=WHITE, anchor="lm")
            if t >= t_120:
                block_text(fr, (120, 640), "DAMAGE PER PISTOL ROUND", 40, WHITE, INK, a=ease((t - t_120) / 0.2))
            if t >= t_sixty - 0.2:
                block_text(fr, (120, 740), "+58% vs THE AVERAGE PLAYER (75)", 46, INK, YELLOW, a=ease((t - t_sixty + 0.2) / 0.2))
            return fr
        block_text(fr, (120, 520), "“REMOVE PISTOL ROUNDS.”", 66, INK, YELLOW, a=ease((t - t_man + 0.1) / 0.2))
        if t >= t_best:
            S.stamp(fr, "AND THE BEST AT THEM", 560, 720, t, t_best, col=YELLOW, size=76, angle=-5)
        return fr

    sfx = [(sch["ropz"][0], "glitch-soft-2", -12), (t_if, "whoosh-short", -13), (t_real, "bass-hit", -8), (t_b8, "hitmarker", -9),
           (t_sim, "pop-2", -11), (t_card6, "stamp-thud", -8), (sch["a4c"][0], "whoosh-short", -12)] + \
          [(s, "feed-tick", -9) for s in steps] + [(t_donk - 1.6 + k * 0.4 * (0.75 ** k), "bomb-beep", -11) for k in range(7)] + \
          [(t_donk - 0.1, "sub-drop", -5), (t_donk - 0.1, "stinger-energetic-hit", -7), (t_sixty, "pop-1", -11),
           (t_man, "glitch-burst", -13), (t_best, "stamp-thud", -5)]
    TL.render("s04", segs, draw, sfx=sfx, tail=0.4, caption_style=lambda tt: "Box" if tt < sch["a4a"][0] else "Low")


# ---------- S05: verdict + your call + Singapore + ident ----------
def s05():
    segs = segs_of("v01", "v02", "v03", "v04", "v05", gap=0.5, holds=("v03",))
    sch, end = TL.schedule(segs)
    w = lambda pid, word, n=0: wt(sch, pid, word, n)
    t_little = w("v01", "little.")
    t_seven, t_buys, t_one3 = w("v02", "seven"), w("v02", "buys"), w("v02", "one")
    t_real = sch["v03"][0]
    t_rem, t_nerf, t_keep, t_tell = w("v04", "remove"), w("v04", "nerf"), w("v04", "keep"), w("v04", "Tell")
    t_sg, t_watch = w("v05", "Singapore"), w("v05", "Watch")
    t_ident = sch["v05"][1] + 0.6
    lg = Image.open(r"D:\Youtube\video03\work\logo.png").convert("RGBA"); lg.thumbnail((300, 300))

    def draw(img, t, sch):
        d = ImageDraw.Draw(img)
        if t < sch["v04"][0] - 0.1:
            S.title(d, "THE VERDICT", t, 0.05)
            if t < t_little - 0.05:
                fx.word_pop(img, "DO PISTOLS", W / 2, 420, t, 0.05, size=140)
                fx.word_pop(img, "DECIDE MATCHES?", W / 2, 580, t, 0.35, size=150, col=YELLOW)
                return img
            fx.word_pop(img, "A LITTLE.", W / 2, 260, t, t_little, size=130)
            rows = [("~7% OF A MAP, BETWEEN EQUAL TEAMS", sch["v02"][0] + 0.2), ("BUYS ROUND 2, NOT ROUND 3", t_buys), ("1 IN 3 COME BACK ANYWAY", t_one3)]
            for i, (s, at) in enumerate(rows):
                if t < at - 0.1:
                    continue
                y, p = 410 + i * 120, ease((t - at + 0.1) / 0.3)
                d.rounded_rectangle([360, y - 40, 440, y + 40], 14, fill=YELLOW)
                d.text((400, y), str(i + 1), font=font(50), fill=INK, anchor="mm")
                text(d, (480 - 30 * (1 - p), y), s, 62, WHITE, anchor="lm", alpha=p)
            if t >= t_real:
                block_text(img, (W / 2, 790), "REAL  ·  NOT DESTINY", 80, INK, YELLOW, a=ease((t - t_real) / 0.2), anchor="m", pad=(40, 18))
            return fx.punch(img, t, t_real, 0.04)
        if t < sch["v05"][0] - 0.1:
            S.title(d, "YOUR CALL", t, sch["v04"][0] - 0.1)
            for i, (lab, at, col) in enumerate([("REMOVE", t_rem, RED_HP), ("NERF", t_nerf, (230, 170, 60)), ("KEEP", t_keep, GREEN_HP)]):
                if t < at - 0.1:
                    continue
                x = 260 + i * 500
                p = ease((t - at + 0.1) / 0.2)
                d.rounded_rectangle([x, 330 + 30 * (1 - p), x + 420, 620 + 30 * (1 - p)], 24, fill=(24, 28, 38), outline=col, width=6)
                d.text((x + 210, 475 + 30 * (1 - p)), lab, font=font(84), fill=col, anchor="mm")
            if t >= t_tell:
                block_text(img, (W / 2, 760), "VOTE IN THE COMMENTS", 70, INK, YELLOW, a=ease((t - t_tell) / 0.2), anchor="m")
            return img
        if t < t_ident:
            fx.word_pop(img, "SINGAPORE", W / 2, 340, t, t_sg, size=180)
            d.text((W / 2, 480), "PGL MAJOR · 25 NOV – 13 DEC 2026", font=font(52), fill=YELLOW, anchor="mm")
            if t >= t_watch:
                x0 = W / 2 - 241
                fx.round_history(img, x0, 600, ["W", "W", "?"], t, t_watch - 0.3, step=0.15, size=150, labels=["ROUND 1", "ROUND 2", "ROUND 3"])
                if t >= t_watch + 0.5:
                    bx = x0 + 2 * 166
                    d.rounded_rectangle([bx - 12, 588, bx + 162, 762], 16, outline=YELLOW, width=8)
            return img
        a = ramp(t, t_ident, 0.5)
        l2 = lg.copy(); l2.putalpha(l2.getchannel("A").point(lambda v: int(v * a)))
        img.paste(l2, (W // 2 - l2.width // 2, 110), l2)
        text(d, (W // 2, 480), "SPORTS ON THE LINE", 84, WHITE, anchor="mm", alpha=a, tracking=8)
        text(d, (W // 2, 560), "data stories from the games we love", 34, MUTED, anchor="mm", alpha=ramp(t, t_ident + 1.0, 0.5))
        return img

    sfx = [(t_little, "bass-hit", -9), (t_seven, "pop-1", -11), (t_buys, "pop-1", -11), (t_one3, "pop-1", -11), (t_real, "stamp-thud", -7),
           (t_rem, "pop-1", -10), (t_nerf, "pop-2", -10), (t_keep, "select-1", -10), (t_tell, "notification-2", -11),
           (t_sg, "whoosh-medium-1s", -12), (t_watch, "bomb-beep", -10), (t_ident, "ident", 0)]
    TL.render("s05", segs, draw, sfx=sfx, tail=0.6 + 7.7 + 3.0)


if __name__ == "__main__":
    for sid in sys.argv[1:]:
        globals()[sid]()
