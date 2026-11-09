"""Video 04 sections s01–s05 (acts 1–4 + verdict). python sections4b.py s01 [s02 ...]"""
import math, sys
from PIL import Image, ImageDraw

from sections4 import *          # noqa: F401,F403  (engine, fx, TL, v2, Src, wt, sub, tag, logo, FOOT2, FOOT4, INK)

S = v2.S
GREEN_HP, RED_HP, CASH = (88, 196, 104), (214, 64, 58), (120, 214, 110)


def bar(d, x, y, w, h, frac, col, label, value):
    d.rounded_rectangle([x, y, x + w, y + h], 10, fill=(30, 34, 44))
    if frac > 0:
        d.rounded_rectangle([x, y, x + max(w * frac, 12), y + h], 10, fill=col)
    d.text((x - 30, y + h / 2), label, font=font(44), fill=WHITE, anchor="rm")
    d.text((x + w + 30, y + h / 2), value, font=font(70), fill=col, anchor="lm")


def segs_of(*ids, gap=0.25):
    return [{"nar": i, "gap": gap} for i in ids]


# ---------- S01: it looks like destiny ----------
def s01():
    segs = segs_of("a1a", "a1b")
    sch, _ = TL.schedule(segs)
    champs = [("navi", "COPENHAGEN 2024", 47, "4/4"), ("spirit", "SHANGHAI 2024", 61, "5/5"), ("vit", "AUSTIN 2025", 62, "4/4"),
              ("vit", "BUDAPEST 2025", 58, "6/6"), ("falcons", "COLOGNE 2026", 63, "4/7")]
    t_win, t_lose, t_16 = wt(sch, "a1a", "Win"), wt(sch, "a1a", "Lose"), wt(sch, "a1a", "sixteen")
    t_ch, t_took, t_23, t_case = wt(sch, "a1b", "champions?"), wt(sch, "a1b", "took"), wt(sch, "a1b", "twenty-three"), wt(sch, "a1b", "Case")

    def draw(img, t, sch):
        d = ImageDraw.Draw(img)
        if t < sch["a1b"][0] - 0.1:
            S.title(d, "MAP RESULT BY PISTOLS WON  ·  379 MAPS", t, 0.1)
            rows = [("WON BOTH", 0.66, GREEN_HP, "66%", t_win), ("SPLIT 1–1", 0.50, (150, 156, 170), "50%", t_win + 1.5),
                    ("LOST BOTH", 0.34, RED_HP, "34%", t_lose)]
            for i, (lab, fr, col, val, at) in enumerate(rows):
                y = 260 + i * 170
                p = ease((t - at) / 0.5) if t >= at else 0
                bar(d, 520, y, 1000, 90, fr * p, col if t >= at else (60, 64, 76), lab, val if p > 0.9 else "")
                if p > 0:
                    fx.hitmarker(img, 520 + 1000 * fr, y + 45, t, at + 0.5, size=38, hs=(i == 0))
                k = {0: 2, 1: None, 2: 1}[i]
                if k is not None and t >= at + 0.6:
                    for j in range(3):
                        d.rounded_rectangle([1640 + j * 70, y + 20, 1690 + j * 70, y + 70], 8, fill=col if j < k else (50, 54, 66))
            if t >= t_16 - 0.1:
                fx.word_pop(img, "+16% PER PISTOL", W / 2, 840, t, t_16, size=110, col=YELLOW)
            out = fx.punch(img, t, t_win, 0.04)
            out = fx.punch(out, t, t_lose, 0.04)
            return fx.punch(out, t, t_16, 0.06)
        S.title(d, "THE CHAMPIONS' PISTOLS ON THEIR TITLE RUN", t, sch["a1b"][0])
        for i, (k, ev, pct, both) in enumerate(champs):
            at = t_ch + i * 0.12
            if t < at:
                continue
            p = ease((t - at) / 0.18)
            x = 70 + i * 362
            d.rounded_rectangle([x, 230 + 50 * (1 - p), x + 340, 760 + 50 * (1 - p)], 18, fill=(24, 28, 38), outline=(60, 66, 80), width=2)
            logo(img, x + 170, 260 + 50 * (1 - p), k, h=80, a=p, anchor="m", wmax=280)
            d.text((x + 170, 420), ev, font=font(30, "SemiBold"), fill=MUTED, anchor="mm")
            d.text((x + 170, 500), f"{pct}%", font=font(80), fill=WHITE, anchor="mm")
            d.text((x + 170, 560), "PISTOLS WON", font=font(26), fill=MUTED, anchor="mm")
            if t >= t_took + i * 0.1:
                q = ease((t - t_took - i * 0.1) / 0.15)
                d.rounded_rectangle([x + 30, 610, x + 310, 730], 14, fill=GREEN_HP if both != "4/7" else (190, 150, 50))
                d.text((x + 170, 650), "WON BOTH", font=font(28), fill=INK, anchor="mm")
                d.text((x + 170, 700), f"{both} MAPS", font=font(int(44 * (1.2 - 0.2 * q))), fill=INK, anchor="mm")
        if t >= t_23:
            v = 23 * ease((t - t_23) / 0.5)
            block_text(img, (W / 2, 820), f"{int(v)} OF 26 MAPS WON", 76, INK, YELLOW, a=ease((t - t_23) / 0.12), anchor="m", pad=(40, 18))
        if t >= t_case - 0.05:
            img = Image.blend(img.convert("L").convert("RGB"), img, 0.3)
            S.stamp(img, "CASE CLOSED?", W / 2, 520, t, t_case - 0.05, col=YELLOW, size=130, angle=-6)
            img = fx.glitch_at(img, t, t_case + 0.35, 0.25, 30)
        return fx.punch(img, t, t_23, 0.05)

    sfx = [(t_win + 0.5, "hitmarker", -6), (t_win + 0.5, "headshot-ding", -10), (t_lose + 0.5, "hitmarker", -6),
           (t_16, "bass-hit", -7), (sch["a1b"][0] - 0.1, "whoosh-short", -12)] + [(t_ch + i * 0.12, "feed-tick", -9) for i in range(5)] + \
          [(t_took + i * 0.1, "pop-1", -14) for i in range(5)] + [(t_23, "stinger-hit-short", -7), (t_case - 0.05, "stamp-thud", -4),
          (t_case + 0.35, "tape-stop", -8)]
    TL.render("s01", segs, draw, sfx=sfx, tail=0.6)


# ---------- S02: the snowball, the loser's choice, donk's eco, the trend ----------
def s02():
    segs = [{"nar": "a2a", "gap": 0.25}, {"nar": "a2b", "gap": 0.25}, {"nar": "a2c", "gap": 0.1},
            {"clip": "S1", "src": FOOT2 + r"\S1.mp4", "in": 4.3, "out": 9.7, "gain": -4, "gap": 0.15}, {"nar": "a2d", "gap": 0.2}]
    sch, _ = TL.schedule(segs)
    w = lambda pid, word, n=0: wt(sch, pid, word, n)
    t_r1, t_80, t_half, t_break = w("a2a", "Win"), w("a2a", "eighty"), w("a2a", "half"), w("a2a", "breaks")
    t_force, t_one, t_broke, t_save, t_coin = w("a2b", "Force-buy,"), w("a2b", "one"), w("a2b", "broke."), w("a2b", "save"), w("a2b", "coin")
    t_never, t_almost = w("a2c", "never"), w("a2c", "Almost.")
    t_first, t_col, t_neither, t_clear = w("a2d", "first"), w("a2d", "Cologne,"), w("a2d", "Neither"), w("a2d", "clearly")
    s1 = Src(FOOT2 + r"\S1.mp4", 4.2, 9.9)
    k_out = [sch["S1"][0] + (k - 4.3) for k in (5.45, 9.05)]
    trend = [("COPENHAGEN", 53), ("SHANGHAI", 40), ("AUSTIN", 35), ("BUDAPEST", 40), ("COLOGNE", 32)]

    def draw(img, t, sch):
        d = ImageDraw.Draw(img)
        if t < sch["a2b"][0] - 0.1:                                         # snowball: R1 -> R2 80% -> R3 54%
            S.title(d, "AFTER A PISTOL WIN  ·  758 PISTOLS", t, 0.05)
            if t < t_r1 - 0.05:
                fx.word_pop(img, "NOT QUITE.", W / 2, 520, t, 0.0, size=170, col=YELLOW)
                return fx.glitch_at(img, t, 0.0, 0.2, 26)
            tiles = [("ROUND 1", "WON", t_r1, GREEN_HP, 1.0), ("ROUND 2", "80%", t_80, GREEN_HP, 0.8), ("ROUND 3", "54%", t_half, (200, 150, 50), 0.54)]
            for i, (lab, val, at, col, fr) in enumerate(tiles):
                x = 230 + i * 520
                if t < at:
                    d.rounded_rectangle([x, 300, x + 420, 720], 22, fill=(26, 30, 40))
                    continue
                p = ease((t - at) / 0.2)
                broken = i == 2 and t >= t_break
                c = RED_HP if broken else col
                d.rounded_rectangle([x, 300, x + 420, 720], 22, fill=(26, 30, 40), outline=c, width=5)
                d.rounded_rectangle([x + 20, 700 - 360 * fr * p, x + 400, 700], 16, fill=c)
                d.text((x + 210, 350), lab, font=font(44), fill=WHITE, anchor="mm")
                d.text((x + 210, 560), val, font=font(int(110 * (1.25 - 0.25 * p))), fill=WHITE, anchor="mm")
                if broken:
                    for k in range(5):
                        d.line([(x + 210, 300), (x + 90 + 60 * k, 720)], fill=(10, 10, 12), width=6)
            if t >= t_r1:
                xs = [440 + i * 520 for i in range(3)]
                tt = [t_r1, t_80, t_half]
                k = max(i for i in range(3) if t >= tt[i])
                bx = xs[k] + ((xs[k + 1] - xs[k]) * ease((t - tt[k]) / 0.8) if k < 2 else 0)
                r = 40 + 14 * k
                if not t >= t_break:
                    d.ellipse([bx - r, 220 - r, bx + r, 220 + r], fill=(236, 240, 246), outline=(160, 170, 190), width=4)
            if t >= t_half:
                block_text(img, (W / 2, 800), "THE 3-ROUND SWING: ONLY ~HALF THE TIME", 52, INK, YELLOW, a=ease((t - t_half) / 0.15), anchor="m")
            out = fx.punch(img, t, t_80, 0.05)
            out = fx.shake(out, t, t_break, 22)
            return fx.glitch_at(out, t, t_break, 0.2, 26)
        if t < sch["a2c"][0] - 0.1:                                         # the loser's wallet
            S.title(d, "LOST THE PISTOL · WHAT NOW?", t, sch["a2b"][0] - 0.1)
            d.line([(W / 2, 200), (W / 2, 900)], fill=(60, 66, 80), width=4)
            if t < t_force - 0.1:
                text(d, (480, 280), "FORCE?", 110, (90, 96, 110), anchor="mm", alpha=ramp(t, sch["a2b"][0], 0.3))
                text(d, (1440, 280), "ECO?", 110, (90, 96, 110), anchor="mm", alpha=ramp(t, sch["a2b"][0] + 0.15, 0.3))
            if t >= t_force - 0.1:
                fx.word_pop(img, "FORCE", 480, 280, t, t_force - 0.1, size=110, col=RED_HP)
                fx.money(img, 480, 440, 600, t, t_force, frm=12000, dur=1.0, size=110, col=CASH if t < t_broke else RED_HP, anchor="mm")
                d.text((480, 520), "LEFT AFTER BUYING", font=font(30), fill=MUTED, anchor="mm")
                if t >= t_one:
                    block_text(img, (480, 600), "WINS ROUND 2: 1 IN 3", 54, INK, YELLOW, a=ease((t - t_one) / 0.12), anchor="m")
                if t >= t_broke:
                    S.stamp(img, "BROKE", 480, 770, t, t_broke, col=RED_HP, size=90, angle=-8)
            if t >= t_save - 0.1:
                fx.word_pop(img, "ECO", 1440, 280, t, t_save - 0.1, size=110, col=CASH)
                fx.money(img, 1440, 440, 10150, t, t_save, frm=0, dur=0.8, size=110, anchor="mm")
                d.text((1440, 520), "SAVED FOR ROUND 3", font=font(30), fill=MUTED, anchor="mm")
                if t >= t_coin - 0.2:
                    wc = abs(math.cos((t - t_coin + 0.2) * 14)) * 110 + 8
                    d.ellipse([1440 - wc, 530, 1440 + wc, 750], fill=(232, 190, 60), outline=(150, 110, 20), width=6)
                    if t >= t_coin + 0.4:
                        block_text(img, (1440, 800), "ROUND 3: 49%", 60, INK, YELLOW, a=ease((t - t_coin - 0.4) / 0.12), anchor="m")
            out = fx.punch(img, t, t_force, 0.04)
            return fx.punch(out, t, t_save, 0.04)
        if t < sch["S1"][0]:                                                # "almost never"
            S.title(d, "ECO TEAMS IN ROUND 2", t, sch["a2c"][0] - 0.1)
            fx.word_pop(img, "1%", W / 2, 500, t, t_never, size=320, col=RED_HP)
            d.text((W / 2, 700), "OF ECO ROUNDS WON  ·  298 ECOS", font=font(44), fill=MUTED, anchor="mm")
            if t >= t_almost:
                img = fx.flash(img, t, t_almost, 0.2, 0.6)
                fx.word_pop(img, "ALMOST.", W / 2, 840, t, t_almost, size=120, col=YELLOW)
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
        S.title(d, "PISTOL LOSERS WHO SAVED (ECO)", t, sch["a2d"][0] - 0.1)
        pts, shown = [], []
        for i, (lab, v) in enumerate(trend):
            x, y = 300 + i * 330, 760 - v * 9
            on = t >= t_first + (t_col - t_first) * i / 4
            pts.append((x, y))
            if on:
                shown.append((x, y))
                d.ellipse([x - 16, y - 16, x + 16, y + 16], fill=YELLOW)
                d.text((x, y - 50), f"{v}%", font=font(52), fill=WHITE, anchor="mm")
            d.text((x, 830), lab, font=font(32), fill=MUTED, anchor="mm")
        if len(shown) > 1:
            d.line(shown, fill=YELLOW, width=6)
        if t >= t_neither - 0.1:
            img = Image.blend(img, Image.new("RGB", (W, H), (14, 17, 23)), 0.6)
            d = ImageDraw.Draw(img)
            for j, (lab, f, e) in enumerate([("HALF WON", 32, 27), ("MAP WON", 40, 46)]):
                y = 300 + j * 230
                d.text((560, y + 40), lab, font=font(44), fill=WHITE, anchor="rm")
                d.rounded_rectangle([600, y, 600 + 14 * f, y + 36], 8, fill=RED_HP)
                d.text((620 + 14 * f, y + 18), f"FORCE {f}%", font=font(34), fill=WHITE, anchor="lm")
                d.rounded_rectangle([600, y + 48, 600 + 14 * e, y + 84], 8, fill=CASH)
                d.text((620 + 14 * e, y + 66), f"ECO {e}%", font=font(34), fill=WHITE, anchor="lm")
            S.stamp(img, "NO CLEAR WINNER", W / 2, 820, t, t_clear, col=YELLOW, size=80, angle=-4)
        return img

    sfx = [(0.0, "tape-stop", -10), (t_r1, "hitmarker", -6), (t_80, "pop-1", -8), (t_half, "bomb-beep", -10), (t_break, "glitch-burst", -8),
           (t_break, "bass-hit", -8), (sch["a2b"][0] - 0.1, "whoosh-short", -12), (t_force, "cash-register-cha-ching", -12),
           (t_broke, "stamp-thud", -5), (t_save, "coins-handful-1", -12), (t_coin - 0.2, "coin-drop", -10), (t_never, "error-buzz-soft", -10),
           (t_almost, "sub-drop", -8)] + [(k, "hitmarker", -10) for k in k_out] + [(k_out[0], "headshot-ding", -12),
           (sch["a2d"][0] - 0.1, "whoosh-medium-1s", -12), (t_first, "feed-tick", -8), (t_col, "feed-tick", -8), (t_clear, "stamp-thud", -6)]
    TL.render("s02", segs, draw, sfx=sfx, tail=0.5)


# ---------- S03: the catch ----------
def s03():
    segs = segs_of("a3a", "a3b", "a3c")
    sch, _ = TL.schedule(segs)
    w = lambda pid, word, n=0: wt(sch, pid, word, n)
    t_better, t_same, t_seven, t_not16 = w("a3a", "Better"), w("a3a", "same"), w("a3b", "seven"), w("a3b", "Not")
    t_navi, t_one, t_still = w("a3c", "NaVi"), w("a3c", "one"), w("a3c", "still")

    def draw(img, t, sch):
        d = ImageDraw.Draw(img)
        if t < sch["a3b"][0] - 0.1:
            S.title(d, "THE CATCH", t, 0.05)
            if t < t_same - 0.1:
                fx.word_pop(img, "BETTER TEAM", 480, 520, t, t_better, size=100)
                for j, (lab, at) in enumerate([("MORE PISTOLS", t_better + 0.6), ("MORE MAPS", w("a3a", "maps."))]):
                    if t >= at:
                        p = ease((t - at) / 0.2)
                        d.line([(850, 520), (850 + 260 * p, 400 + 240 * j)], fill=YELLOW, width=8)
                        block_text(img, (1140, 360 + 240 * j), lab, 64, INK, YELLOW, a=p)
                return img
            d.text((W / 2, 230), "SAME TWO TEAMS  ·  SAME SERIES", font=font(52), fill=YELLOW, anchor="mm")
            for i, (m, pis, res) in enumerate([("MAP 1", 2, "W"), ("MAP 2", 0, "L"), ("MAP 3", 1, "W")]):
                at = t_same + 0.3 + i * 0.3
                if t < at:
                    continue
                x = 200 + i * 540
                d.rounded_rectangle([x, 320, x + 460, 760], 20, fill=(24, 28, 38), outline=(60, 66, 80), width=3)
                d.text((x + 230, 370), m, font=font(44), fill=WHITE, anchor="mm")
                d.text((x + 120, 450), "TEAM A", font=font(36), fill=(93, 156, 236), anchor="mm")
                d.text((x + 340, 450), "TEAM B", font=font(36), fill=(232, 184, 74), anchor="mm")
                for j in range(2):
                    d.ellipse([x + 140 + j * 110, 520, x + 210 + j * 110, 590], fill=GREEN_HP if j < pis else (70, 74, 86))
                d.text((x + 230, 640), f"TEAM A: {pis}/2 PISTOLS", font=font(32), fill=MUTED, anchor="mm")
                d.text((x + 230, 710), "MAP WON" if res == "W" else "MAP LOST", font=font(40), fill=GREEN_HP if res == "W" else RED_HP, anchor="mm")
            return img
        if t < sch["a3c"][0] - 0.1:
            fx.word_pop(img, "+16%", W / 2 - 380, 520, t, sch["a3b"][0], size=200, col=(150, 156, 170))
            if t >= t_seven - 0.2:
                d.line([(W / 2 - 600, 600), (W / 2 - 160, 440)], fill=RED_HP, width=14)
            if t >= t_seven:
                fx.word_pop(img, "+7%", W / 2 + 380, 520, t, t_seven, size=260, col=YELLOW)
                d.text((W / 2 + 380, 700), "PER PISTOL · SAME TEAMS", font=font(40), fill=MUTED, anchor="mm")
            if t >= t_not16:
                block_text(img, (W / 2, 830), "HALF THE MYTH = BETTER TEAMS", 60, INK, YELLOW, a=ease((t - t_not16) / 0.12), anchor="m")
            out = fx.punch(img, t, t_seven, 0.08)
            return fx.glitch_at(out, t, t_seven, 0.15, 22)
        if t < t_one - 0.1:
            logo(img, W / 2, 220, "navi", h=150, anchor="m", wmax=420, a=ease((t - t_navi) / 0.2))
            d.text((W / 2, 500), "COPENHAGEN 2024 · CHAMPIONS", font=font(48), fill=YELLOW, anchor="mm")
            fx.word_pop(img, "15 / 32", W / 2, 660, t, w("a3c", "losing"), size=150, col=WHITE)
            d.text((W / 2, 780), "PISTOLS WON", font=font(44), fill=MUTED, anchor="mm")
            return fx.punch(img, t, t_navi, 0.05)
        S.title(d, "LOST BOTH PISTOLS · STILL WON THE MAP", t, t_one - 0.1)
        for j in range(3):
            x = W / 2 - 360 + j * 360
            lit = j == 2 and t >= t_still
            d.ellipse([x - 90, 260, x + 90, 440], fill=YELLOW if lit else (60, 64, 76))
            d.rounded_rectangle([x - 120, 460, x + 120, 640], 40, fill=YELLOW if lit else (60, 64, 76))
        if t >= t_still:
            block_text(img, (W / 2, 700), "63 OF 185 MAPS", 70, INK, YELLOW, a=ease((t - t_still) / 0.12), anchor="m")
            for i, (k, n) in enumerate([("spirit", 8), ("g2", 8), ("navi", 7)]):
                logo(img, 520 + i * 420, 860, k, h=60, a=ease((t - t_still - 0.2 - i * 0.1) / 0.15), anchor="m", wmax=240)
                d.text((660 + i * 420, 900), f"×{n}", font=font(48), fill=WHITE, anchor="lm")
        return img

    sfx = [(0.0, "glitch-soft-1", -12), (t_better, "bass-hit", -8), (t_better + 0.6, "pop-1", -10), (w("a3a", "maps."), "pop-2", -10),
           (t_same, "whoosh-short", -12)] + [(t_same + 0.3 + i * 0.3, "feed-tick", -8) for i in range(3)] + \
          [(sch["a3b"][0], "stamp-thud", -10), (t_seven, "sub-drop", -7), (t_seven, "glitch-burst", -12), (t_not16, "stamp-thud", -7),
           (t_navi, "stinger-hit-short", -8), (w("a3c", "losing"), "pop-1", -10), (t_one - 0.1, "whoosh-short", -12), (t_still, "success-bell", -12)]
    TL.render("s03", segs, draw, sfx=sfx, tail=0.4)


# ---------- S04: random? not quite + the countdown (no leak of #1 before the reveal) ----------
TOP = [("yuurih", "furia", 89.9), ("Senzu", "mongolz", 90.7), ("XANTARES", "aurora", 91.6), ("snow", "pain", 93.0),
       ("m0NESY", "falcons", 93.8), ("xertioN", "mouz", 94.5), ("ZywOo", "vit", 99.0), ("frozen", "faze", 102.0),
       ("kyousuke", "falcons", 102.1)]                       # #10 .. #2; #1 = donk 119.8, revealed only in a4c
TEAMS = [("9z", 66), ("vit", 60), ("falcons", 58), ("mouz", 57), ("aurora", 55), ("heroic", 54), ("mongolz", 53), ("pain", 53),
         ("faze", 53), ("navi", 53), ("spirit", 50), ("furia", 49), ("g2", 48), ("tl", 41), ("betboom", 27)]


def s04():
    ropz = FOOT4 + r"\ropz_mr12_random.mkv"
    segs = [{"clip": "ropz", "src": ropz, "in": 12.9, "out": 17.5, "gain": 0, "gap": 0.1}, {"nar": "a4a", "gap": 0.2},
            {"nar": "a4b", "gap": 2.6}, {"nar": "a4c", "gap": 0.3}]
    sch, _ = TL.schedule(segs)
    w = lambda pid, word, n=0: wt(sch, pid, word, n)
    rz = Src(ropz, 12.8, 17.6, fps=30)
    t_no, t_some, t_own = w("a4a", "No."), w("a4a", "Some"), w("a4a", "own")
    t_list = sch["a4b"][0] + 0.2
    t_one = w("a4c", "Number")
    t_donk, t_man, t_best = w("a4c", "donk."), w("a4c", "man"), w("a4c", "best")
    steps = [t_list + i * ((t_one - 0.4) - t_list) / len(TOP) for i in range(len(TOP))]
    donk_fr = Src(FOOT4 + r"\donk_tldr_remove_pistols.mkv", 10.4, 12.3, fps=30)

    def draw(img, t, sch):
        d = ImageDraw.Draw(img)
        if t < sch["a4a"][0] - 0.05:                                         # ropz on stream (facecam punch-in)
            fr = rz.frame(12.9 + (t - sch["ropz"][0]))
            fr = fr.resize((W, H), Image.LANCZOS, box=(0, 40, 520, 332))
            fr = fx.flash(fr, t, sch["ropz"][0], 0.08, 0.5)
            tag(fr, "ropz · on MR12 · 2023 stream")
            sub(fr, "“I think it's gonna be even more random results.”", t, sch["ropz"][0] + 0.1, y=860, size=58, col=INK, bg=YELLOW)
            return fr
        if t < sch["a4b"][0] - 0.1:                                          # team pistol win rates vs a coin flip
            S.title(d, "TEAM PISTOL WIN RATE vs A COIN FLIP", t, sch["a4a"][0])
            x0, x1 = 200, 1720
            px = lambda v: x0 + (v - 20) / 50 * (x1 - x0)
            d.rectangle([px(40), 300, px(60), 760], fill=(40, 44, 56))
            d.text((px(50), 280), "COIN-FLIP RANGE", font=font(32), fill=MUTED, anchor="mm")
            for v in (20, 30, 40, 50, 60, 70):
                d.text((px(v), 800), f"{v}%", font=font(30), fill=MUTED, anchor="mm")
            if t >= t_no - 0.1:
                for i, (k, v) in enumerate(TEAMS):
                    at = t_no + i * 0.06
                    if t < at:
                        continue
                    y = 330 + (i % 5) * 88
                    out = v > 60 or v < 40
                    logo(img, px(v), y, k, h=46, a=ease((t - at) / 0.12), anchor="m", wmax=150)
                    if out and t >= t_some:
                        fx.hitmarker(img, px(v), y + 30, t, t_some + 0.05 * (i % 3), size=34)
                for j, (lab, v) in enumerate((("B8 21%", 21), ("LEGACY 25%", 25))):
                    if t >= t_some:
                        d.text((px(v), 700 + j * 44), lab, font=font(32), fill=RED_HP, anchor="lm" if j else "mm")
            if t >= t_own:
                block_text(img, (W / 2, 900), "SOME TEAMS ARE GENUINELY BETTER AT PISTOLS", 50, INK, YELLOW, a=ease((t - t_own) / 0.12), anchor="m")
            return fx.punch(img, t, t_no, 0.06)
        if t < t_one - 0.1 or t < t_donk - 0.15:                             # countdown 10..2 with a bomb timer
            S.title(d, "BEST PISTOL PLAYERS · DAMAGE PER PISTOL ROUND · CS2 MAJORS", t, sch["a4b"][0], size=34)
            k = sum(1 for s in steps if t >= s)
            for i in range(k):
                name, team, dmg = TOP[i]
                rank = 10 - i
                y = 200 + (i % 9) * 82
                p = ease((t - steps[i]) / 0.12)
                d.text((150, y + 30), f"#{rank}", font=font(44), fill=MUTED, anchor="lm")
                logo(img, 250, y + 4, team, h=40, a=p, wmax=120)
                d.text((400, y + 30), name, font=font(46), fill=WHITE, anchor="lm")
                d.rounded_rectangle([720, y + 10, 720 + (dmg - 60) * 18 * p, y + 50], 8, fill=(150, 160, 180))
                d.text((740 + (dmg - 60) * 18, y + 30), f"{dmg:.0f}", font=font(40), fill=WHITE, anchor="lm")
            if t >= steps[-1] + 0.2:
                rem = max(0.0, t_donk - t)
                fx.bomb_timer(img, 1550, 940, f"{rem:0.1f}", t, 2 + 6 * (1 - rem / 3))
                d.text((150, 960), "#1  ?", font=font(56), fill=YELLOW, anchor="lm")
            return fx.punch(img, t, steps[min(k, len(steps)) - 1] if k else 0, 0.03)
        # #1 reveal: donk
        fr = donk_fr.frame(10.4 + min(t - t_donk, 1.8))
        side_shade(fr, 1.0, frac=0.65)
        fr = fx.flash(fr, t, t_donk - 0.1, 0.25, 1.0)
        fr = fx.shake(fr, t, t_donk - 0.1, 26)
        fx.word_pop(fr, "#1  donk", 110, 300, t, t_donk - 0.1, size=170, col=YELLOW, anchor="lm")
        logo(fr, 120, 420, "spirit", h=56, wmax=330)
        fx.word_pop(fr, "120", 120, 590, t, t_donk + 0.2, size=190, col=WHITE, anchor="lm")
        if t >= t_donk + 0.3:
            block_text(fr, (125, 700), "DAMAGE PER PISTOL ROUND  ·  AVERAGE: 75", 38, WHITE, INK, a=ease((t - t_donk - 0.3) / 0.12))
        if t >= t_man:
            block_text(fr, (120, 800), "“REMOVE PISTOL ROUNDS.”", 64, INK, YELLOW, a=ease((t - t_man) / 0.12))
        if t >= t_best:
            S.stamp(fr, "THE BEST AT THEM", 1300, 520, t, t_best, col=YELLOW, size=80, angle=-6)
        return fr

    sfx = [(sch["ropz"][0], "glitch-soft-2", -12), (t_no, "bass-hit", -7), (t_some, "hitmarker", -8), (t_own, "pop-2", -10),
           (sch["a4b"][0], "whoosh-short", -12)] + [(s, "feed-tick", -8) for s in steps] + \
          [(t_donk - 1.6 + k * 0.4 * (0.75 ** k), "bomb-beep", -10) for k in range(7)] + \
          [(t_donk - 0.1, "sub-drop", -4), (t_donk - 0.1, "stinger-energetic-hit", -6), (t_man, "glitch-burst", -12), (t_best, "stamp-thud", -4)]
    TL.render("s04", segs, draw, sfx=sfx, tail=0.6, caption_style=lambda tt: "Box" if tt < sch["a4a"][0] else "Low")


# ---------- S05: verdict + your call + Singapore + ident ----------
def s05():
    segs = segs_of("v01", "v02", "v03", gap=0.3)
    sch, end = TL.schedule(segs)
    w = lambda pid, word, n=0: wt(sch, pid, word, n)
    t_little, t_seven, t_real = w("v01", "little."), w("v01", "seven"), w("v01", "Real,")
    t_rem, t_nerf, t_keep, t_tell = w("v02", "remove"), w("v02", "nerf"), w("v02", "keep"), w("v02", "Tell")
    t_sg, t_watch = w("v03", "Singapore"), w("v03", "Watch")
    t_ident = sch["v03"][1] + 0.6
    lg = Image.open(r"D:\Youtube\video03\work\logo.png").convert("RGBA"); lg.thumbnail((300, 300))

    def draw(img, t, sch):
        d = ImageDraw.Draw(img)
        if t < sch["v02"][0] - 0.1:
            S.title(d, "THE VERDICT", t, 0.05)
            if t < t_little - 0.05:
                fx.word_pop(img, "DO PISTOLS", W / 2, 440, t, 0.05, size=140)
                fx.word_pop(img, "DECIDE MATCHES?", W / 2, 600, t, 0.35, size=150, col=YELLOW)
                return img
            fx.word_pop(img, "A LITTLE.", W / 2, 330, t, t_little, size=150)
            if t >= t_seven:
                fx.word_pop(img, "~7% OF A MAP", W / 2, 540, t, t_seven, size=140, col=YELLOW)
            if t >= t_real:
                block_text(img, (W / 2, 720), "REAL · NOT DESTINY", 70, INK, YELLOW, a=ease((t - t_real) / 0.12), anchor="m")
                d.text((W / 2, 840), "ROUND 3 DECIDES THE SWING", font=font(46), fill=MUTED, anchor="mm")
            return fx.punch(img, t, t_seven, 0.05)
        if t < sch["v03"][0] - 0.1:
            S.title(d, "YOUR CALL", t, sch["v02"][0] - 0.1)
            for i, (lab, key, at, col) in enumerate([("REMOVE", "F1", t_rem, RED_HP), ("NERF", "F2", t_nerf, (230, 170, 60)), ("KEEP", "F3", t_keep, GREEN_HP)]):
                if t < at - 0.1:
                    continue
                x = 260 + i * 500
                p = ease((t - at + 0.1) / 0.15)
                d.rounded_rectangle([x, 330 + 30 * (1 - p), x + 420, 620 + 30 * (1 - p)], 24, fill=(24, 28, 38), outline=col, width=6)
                d.text((x + 210, 420), key, font=font(40), fill=MUTED, anchor="mm")
                d.text((x + 210, 520), lab, font=font(80), fill=col, anchor="mm")
            if t >= t_tell:
                block_text(img, (W / 2, 760), "VOTE IN THE COMMENTS", 70, INK, YELLOW, a=ease((t - t_tell) / 0.12), anchor="m")
            return img
        if t < t_ident:
            fx.word_pop(img, "SINGAPORE", W / 2, 360, t, t_sg, size=180)
            d.text((W / 2, 500), "PGL MAJOR · 25 NOV – 13 DEC 2026", font=font(52), fill=YELLOW, anchor="mm")
            if t >= t_watch:
                fx.round_history(img, W / 2 - 300, 620, ["W", "W", "?"], t, t_watch - 0.3, step=0.12, size=150, labels=["ROUND 1", "ROUND 2", "ROUND 3"])
                if t >= t_watch + 0.5:
                    d.rounded_rectangle([W / 2 + 208 - 10, 610, W / 2 + 208 + 160, 780], 14, outline=YELLOW, width=8)
            return img
        a = ramp(t, t_ident, 0.5)
        l2 = lg.copy(); l2.putalpha(l2.getchannel("A").point(lambda v: int(v * a)))
        img.paste(l2, (W // 2 - l2.width // 2, 110), l2)
        text(d, (W // 2, 480), "SPORTS ON THE LINE", 84, WHITE, anchor="mm", alpha=a, tracking=8)
        text(d, (W // 2, 560), "data stories from the games we love", 34, MUTED, anchor="mm", alpha=ramp(t, t_ident + 1.0, 0.5))
        return img

    sfx = [(t_little, "bass-hit", -8), (t_seven, "stinger-hit-short", -8), (t_real, "stamp-thud", -7), (t_rem, "pop-1", -9), (t_nerf, "pop-2", -9),
           (t_keep, "select-1", -9), (t_tell, "notification-2", -10), (t_sg, "whoosh-medium-1s", -12), (t_watch, "bomb-beep", -10), (t_ident, "ident", 0)]
    TL.render("s05", segs, draw, sfx=sfx, tail=0.6 + 7.7 + 6.0)


if __name__ == "__main__":
    for sid in sys.argv[1:]:
        globals()[sid]()
