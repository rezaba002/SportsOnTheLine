"""Section clips for video 03. One function per section; render with:  python sections.py s01 [s02 ...]

Every element is anchored to a narration word (Words), so the same code re-times itself when the owner's own
recording replaces the timing-guide voice.
"""
import json, math, sys

import numpy as np

import pandas as pd
from PIL import Image, ImageDraw

from engine import (BG, CT, DIM, FPS, H, LINE, LOSS, MUTED, PANEL, TT, W, WHITE, WIN, YELLOW, Words, block_text, counter, font, side_shade,
                    ease, ease_io, fade, headset, mix, ramp, render_section, ring, rrect, text)

RES = r"D:\Research\cs2-timeouts"
# Approximate start of each section in the finished video, for the music-bed slice (updated as clips change).
ORDER = ["s00", "s01", "s02", "s03", "s04", "s05", "s06", "s07", "s08", "s09", "s10"]
PLANNED = {"s00": 17.0, "s01": 14.6, "s02": 10.8, "s03": 22.0, "s04": 29.1, "s05": 14.4, "s06": 21.0,
           "s07": 21.2, "s08": 19.7, "s09": 21.5, "s10": 8.0}


def music_at(sid):
    return sum(PLANNED[s] for s in ORDER[:ORDER.index(sid)])


def title(d, s, t, t0, y=110):
    a = ramp(t, t0, 0.35)
    text(d, (W // 2, y - 12 * (1 - a)), s, 44, WHITE, anchor="mm", alpha=a, tracking=6)


# ---------------------------------------------------------------- S01: what a timeout is
def s01():
    w = Words("p02", lead=0.15)
    t_ring, t_coach, t_three, t_ot, t_and, t_both = w("thirty"), w("coach"), w("Three"), w("overtime"), w("And"), w("both")
    t_any, t_coaches, t_talk = w("any"), w("coaches"), w("talk", 1)

    def draw(img, t):
        d = ImageDraw.Draw(img)
        out = 1 - ramp(t, t_and - 0.1, 0.35)            # phase A/B fades out when "And here's the detail" starts
        if out > 0:
            title(d, "TACTICAL TIMEOUT", t, w("tactical") - 0.3)
            if t < t_and:
                pass
            a = ramp(t, t_ring - 0.2, 0.4) * out
            if a > 0:
                cx, cy, r = W // 2, 390, 175
                left = max(0.0, 30 - max(0.0, t - t_ring))
                frac = left / 30
                d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=fade(LINE, a), width=20)
                d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * frac * ease((t - t_ring + 0.2) / 0.5),
                      fill=fade(YELLOW, a), width=20)
                text(d, (cx, cy - 8), f"{math.ceil(left):d}", 150, WHITE, anchor="mm", alpha=a)
                text(d, (cx, cy + 82), "SECONDS", 30, MUTED, anchor="mm", alpha=a, tracking=5)
            # the coach talks (phase A only)
            ha = ramp(t, t_coach - 0.3, 0.35) * (1 - ramp(t, t_three - 0.25, 0.3)) * out
            if ha > 0:
                headset(d, W // 2, 700, 120, fade(CT, ha), glow=max(0, t - w("talk")) * 1.2 if t > w("talk") else 0)
                text(d, (W // 2, 820), "THE COACH CAN TALK", 34, WHITE, anchor="mm", alpha=ha, tracking=4)
            # three per team, +1 per overtime
            pa = ramp(t, t_three - 0.2, 0.35) * out
            if pa > 0:
                for row, (lab, col, y) in enumerate((("TEAM A", CT, 660), ("TEAM B", TT, 760))):
                    text(d, (700, y), lab, 36, col, anchor="rm", alpha=pa, tracking=3)
                    for k in range(3):
                        ka = ramp(t, t_three - 0.1 + 0.12 * k + 0.25 * row, 0.25) * out
                        x = 760 + k * 90
                        d.ellipse([x, y - 28, x + 56, y + 28], fill=fade(col, ka))
                    oa = ramp(t, t_ot - 0.35 + 0.15 * row, 0.3) * out
                    if oa > 0:
                        x = 760 + 3 * 90 + 30
                        d.ellipse([x, y - 28, x + 56, y + 28], outline=fade(col, oa), width=5)
                        text(d, (x + 80, y), "+1 EVERY OVERTIME", 30, MUTED, anchor="lm", alpha=oa, tracking=2)
        # phase C: both coaches talk
        ca = ramp(t, t_and + 0.05, 0.4)
        if ca > 0:
            text(d, (W // 2, 110), "DURING ANY TIMEOUT", 44, WHITE, anchor="mm", alpha=ramp(t, t_any - 0.15, 0.35), tracking=6)
            for side, (lab, col, x, t_on) in enumerate((("YOUR COACH", CT, 600, t_both), ("THEIR COACH", TT, 1320, t_coaches))):
                on = ramp(t, t_on - 0.1, 0.3)
                col_now = mix(DIM, col, on)
                headset(d, x, 450, 230, fade(col_now, ca), glow=on * min(1.0, max(0.0, (t - t_on) * 1.5)))
                text(d, (x, 650), lab, 42, col_now, anchor="mm", alpha=ca, tracking=4)
            sw = ramp(t, t_and + 0.2, 0.4)
            cx, cy, r = W // 2, 450, 78
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=fade(LINE, sw), width=10)
            d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * sw * 0.85, fill=fade(YELLOW, sw), width=10)
            text(d, (cx, cy), "30", 64, WHITE, anchor="mm", alpha=sw)
            ba = ramp(t, t_both - 0.05, 0.3)
            if ba > 0:
                s = 1 + 0.25 * (1 - ease((t - t_both + 0.05) / 0.3))
                text(d, (W // 2, 790), "BOTH COACHES TALK", int(64 * s), YELLOW, anchor="mm", alpha=ba, tracking=5)

    sfx = [(w("tactical") - 0.35, "whoosh-short", -4), (t_ring - 0.15, "pop-1", -2),
           (t_coach - 0.25, "pop-2", -2), (t_three, "pop-2", -4), (t_three + 0.37, "pop-2", -4),
           (t_ot - 0.3, "toggle", -4), (t_and - 0.1, "whoosh-soft", -4), (t_both - 0.05, "impact-soft-1", -3)]
    render_section("s01", "p02", draw, sfx, lead=0.15, music_offset=music_at("s01"))


# ---------------------------------------------------------------- S02: the data
def s02():
    w = Words("p03", lead=0.15)
    tr = pd.read_csv(fr"{RES}\data\col26\team_rounds.csv")
    to = pd.read_csv(fr"{RES}\results\col26\decision_points.csv")
    rounds = tr[tr.win == 1].sort_values(["game_id", "round"])
    timeout_rounds = set(zip(to[to.to == 1].game_id, to[to.to == 1]["round"]))
    cells = [(r.side, (r.game_id, r["round"]) in timeout_rounds) for _, r in rounds.iterrows()]
    n = len(cells)                                       # 2,255
    cols, cell = 60, 16
    x0, y0 = 830, 230
    t_demo, t_maps0, t_maps1 = w("demos"), w("One"), w("maps", end=True)
    t_r0, t_r1, t_to = w("two"), w("rounds", end=True), w("timeout")

    def draw(img, t):
        d = ImageDraw.Draw(img)
        # demo files
        mv = ease_io((t - (t_maps0 - 0.5)) / 0.6)          # centre & big -> left & normal
        sc = 1.7 - 0.7 * mv
        cx, cy = W / 2 + (342 - W / 2) * mv, 420 + (404 - 420) * mv
        for k in range(3):
            ka = ramp(t, w("pulled") - 0.2 + 0.12 * k, 0.35)
            x, y = cx - 132 * sc + k * 26 * sc, cy - 154 * sc + k * 22 * sc
            rrect(d, (x, y, x + 170 * sc, y + 210 * sc), 14 * sc, fill=fade(PANEL, ka), outline=fade(LINE, ka), width=3)
            d.polygon([(x + 125 * sc, y), (x + 170 * sc, y + 45 * sc), (x + 125 * sc, y + 45 * sc)], fill=fade(LINE, ka))
        text(d, (cx, cy), ".dem", int(44 * sc), CT, anchor="mm", alpha=ramp(t, t_demo - 0.3, 0.3))
        text(d, (cx, cy + 131 * sc), "OFFICIAL DEMOS", int(30 * sc), MUTED, anchor="mm", alpha=ramp(t, t_demo - 0.2, 0.3), tracking=3)
        # counters
        rows = [(103, "MAPS", t_maps0, t_maps1, WHITE), (n, "ROUNDS", t_r0, t_r1, WHITE), (430, "TIMEOUTS", t_to - 0.4, t_to + 0.2, YELLOW)]
        for k, (v, lab, s0, s1, col) in enumerate(rows):
            ca = ramp(t, s0 - 0.2, 0.3)
            if ca <= 0:
                continue
            val = int(round(counter(v, t, s0, max(0.3, s1 - s0))))
            y = 640 + k * 92
            text(d, (520, y), f"{val:,}", 72, col, anchor="rm", alpha=ca)
            text(d, (545, y + 4), lab, 34, MUTED, anchor="lm", alpha=ca, tracking=3)
        # grid of every round, filling while "two thousand ... rounds" is said; winners' side colours
        fill_n = int(n * ease_io((t - t_r0) / max(0.4, t_r1 - t_r0))) if t > t_r0 else 0
        flash = ramp(t, t_to - 0.4, 0.4)
        ga = ramp(t, t_r0 - 0.4, 0.3)
        if ga > 0:
            text(d, (x0, y0 - 40), "EVERY ROUND OF THE MAJOR  ·  winner's side", 26, MUTED, anchor="ls", alpha=ga, tracking=2)
        for i, (side, is_to) in enumerate(cells):
            r_, c_ = divmod(i, cols)
            x, y = x0 + c_ * cell, y0 + r_ * cell
            if i < fill_n:
                col = CT if side == "CT" else TT
                col = mix(col, BG, 0.45)
                if is_to and flash > 0:
                    col = mix(col, YELLOW, flash)
                elif flash > 0:
                    col = mix(col, BG, 0.45 * flash)
                d.rectangle([x, y, x + cell - 3, y + cell - 3], fill=col)
            elif ga > 0:
                d.rectangle([x, y, x + cell - 3, y + cell - 3], fill=fade(PANEL, ga))

    sfx = [(w("pulled") - 0.3, "whoosh-short", -4), (t_maps0 - 0.1, "pop-1", -3), (t_r0 - 0.1, "riser-short-2s", -10),
           (t_to - 0.35, "impact-soft-2", -3)]
    render_section("s02", "p03", draw, sfx, lead=0.15, music_offset=music_at("s02"))


# ---------------------------------------------------------------- S03: the coach leaderboard
COACH = {"Monte": ("kakafu", "Monte"), "9z": ("BIT", "9z"), "MOUZ": ("sycrone", "MOUZ"), "FUT Esports": ("coolio", "FUT"),
         "Natus Vincere": ("B1ad3", "NAVI"), "FURIA": ("sidde", "FURIA"), "Team Vitality": ("XTQZZZ", "Vitality"),
         "BetBoom Team": ("Fierce", "BetBoom"), "Team Falcons": ("zonic", "Falcons"), "Legacy": ("adr", "Legacy"),
         "Team Spirit": ("no coach on site", "Spirit"), "Aurora Gaming": ("Fabre", "Aurora"), "G2 Esports": ("sAw", "G2"),
         "The MongolZ": ("maaRaa", "MongolZ"), "PARIVISION": ("dastan", "PARIVISION"), "B8 Esports": ("no coach", "B8")}


def leaderboard_rows():
    js = json.load(open(fr"{RES}\results\col26\explore_coaches.json", encoding="utf-8"))
    rows = sorted(js["teams"], key=lambda r: -r["raw_gap"])
    return [(COACH[r["team"]][0], COACH[r["team"]][1], r["raw_gap"] * 100) for r in rows]


def draw_board(d, t, rows, grow_t, hi=None, hi_bottom=(), dim=0.0, pin_t=None, stagger=0.045):
    """16 diverging bars. hi: index highlighted in yellow; hi_bottom: [(index, t_on)] tinted red."""
    zero, scale, y0, step = 1210, 17.0, 205, 47
    la = ramp(t, grow_t - 0.15, 0.3)          # the zero line arrives with the bars, never alone
    if la > 0:
        d.line([zero, y0 - 30, zero, y0 - 30 + (step * len(rows) + 15) * la], fill=LINE, width=3)
    for i, (coach, team, gap) in enumerate(rows):
        y = y0 + i * step
        g = ramp(t, grow_t + stagger * i, 0.5)
        if g <= 0:
            continue
        focus = (hi == i)
        reds = [ton for (j, ton) in hi_bottom if j == i]
        red_a = ramp(t, reds[0] - 0.1, 0.25) if reds else 0.0
        a = g * (1 - dim * (0 if focus else 1) * 0.72)
        name_col = YELLOW if focus and t >= grow_t else mix(WHITE, LOSS, red_a)
        coachless = coach.startswith("no coach")
        text(d, (640, y), coach, 30, MUTED if coachless else name_col, anchor="rm", alpha=a,
             style="SemiBold" if coachless else "Bold")
        text(d, (662, y), team, 26, MUTED, anchor="lm", alpha=a)
        length = gap * scale * ease((t - grow_t - stagger * i) / 0.6)
        col = WIN if gap >= 0 else LOSS
        if focus:
            col = YELLOW
        col = mix(col, LOSS, red_a) if gap < 0 else col
        x1, x2 = (zero, zero + length) if length >= 0 else (zero + length, zero)
        if abs(length) >= 1:
            rrect(d, (x1, y - 15, x2, y + 15), 6, fill=fade(col, a))
        lab = "0" if abs(gap) < 0.5 else f"{gap:+.0f}"
        lx = zero + length + (14 if gap >= 0 else -14)
        text(d, (lx, y), lab, 28, col, anchor="lm" if gap >= 0 else "rm", alpha=a * ramp(t, grow_t + stagger * i + 0.35, 0.3))
        if focus and pin_t is not None and t >= pin_t:
            p = ease((t - pin_t) / 0.25)
            px, py = zero + length + 85, y - 70 * (1 - p)
            d.line([px, py, px - 18, py + 34], fill=fade(WHITE, p), width=5)
            d.ellipse([px - 16, py - 30, px + 16, py + 2], fill=fade(LOSS, p))
    return zero, scale, y0, step


def s03():
    w = Words("p04", lead=0.15)
    rows = leaderboard_rows()
    i_bottom = {team: i for i, (_, team, _) in enumerate(rows)}
    t_grow, t_top, t_fift, t_magic, t_hold = w("which") + 0.25, w("top"), w("fifteen"), w("magic"), w("Hold")
    bottom = [(i_bottom["B8"], w("B8")), (i_bottom["PARIVISION"], w("PARIVISION")), (i_bottom["MongolZ"], w("the MongolZ"))]
    from engine import Footage, lower_third
    # kakafu walking Monte's booth with his notes during a timeout (Aurora vs Monte, Nuke) — the face behind the +15
    kak = Footage(FOOT + r"\coaches\kakafu.mp4", 15.2, 3.4, (1.12, 1.45), (0.27, 0.36))
    cut_in, cut_out = t_top - 0.1, min(t_fift - 0.2, t_top - 0.1 + 3.4)

    def draw(img, t):
        if cut_in <= t < cut_out:
            local = t - cut_in
            fr = kak.frame(local)
            img.paste(fr)
            d = ImageDraw.Draw(img)
            lower_third(d, t, cut_in + 0.1, "kakafu", "Monte's coach", "#1 ON THE BOARD", YELLOW, y=560)
            if local < 0.067:
                d.rectangle([0, 0, W, H], fill=(245, 245, 245))
            return
        if t >= cut_out and kak.frames is not None:
            kak.free()
        d = ImageDraw.Draw(img)
        if t >= cut_out and t < cut_out + 0.067:                  # flash back into the board
            d.rectangle([0, 0, W, H], fill=(245, 245, 245))
            return
        title(d, "WHOSE TIMEOUTS WORKED BEST?", t, w("which") - 0.3, y=88)
        sa = ramp(t, w("which"), 0.4)
        text(d, (W // 2, 140), "next gun round won after a timeout vs. without one  ·  percentage points  ·  raw",
             26, MUTED, anchor="mm", alpha=sa)
        hi = 0 if t >= t_top - 0.1 else None
        dim = ramp(t, t_hold - 0.1, 0.4)
        draw_board(d, t, rows, t_grow - 0.2, hi=hi, hi_bottom=bottom, dim=dim, pin_t=t_hold)
        # +15 callout and the sparkle on "magic"
        fa = ramp(t, t_fift - 0.15, 0.3)
        if fa > 0:
            s = 1 + 0.3 * (1 - ease((t - t_fift + 0.15) / 0.35))
            text(d, (1640, 205), "+15", int(70 * s), YELLOW, anchor="lm", alpha=fa * (1 - 0.6 * dim))
        ma = ramp(t, t_magic - 0.1, 0.25) * (1 - ramp(t, t_magic + 0.9, 0.4))
        if ma > 0:
            for k in range(6):
                ang = k * math.pi / 3 + t * 2
                x, y = 1490 + 60 * math.cos(ang), 205 + 32 * math.sin(ang)
                r = 6 + 3 * math.sin(t * 9 + k)
                d.polygon([(x, y - r * 2), (x + r * 0.6, y), (x, y + r * 2), (x - r * 0.6, y)], fill=fade(YELLOW, ma))

    sfx = [(w("which") - 0.35, "whoosh-short", -4), (t_grow - 0.15, "whoosh-soft", -6), (t_top - 0.1, "pop-1", -2),
           (t_fift - 0.15, "impact-soft-1", -4)] + [(ton - 0.1, "error-2", -8) for _, ton in bottom] + \
          [(t_magic - 0.1, "notification-1" if False else "pop-2", -2), (t_hold - 0.05, "dry-thud", -1)]
    sfx += [(cut_in - 0.1, "whoosh-short", -5), (cut_out - 0.1, "whoosh-short", -6)]
    render_section("s03", "p04", draw, sfx, lead=0.15, music_offset=music_at("s03"),
                   caption_style=lambda m: "Box" if cut_in <= m < cut_out else "Low")


# ---------------------------------------------------------------- shared helpers for footage + stamps
FOOT = r"D:\Youtube\video03\footage"


def paste_footage(img, fx, local, darken=0.0):
    fr = fx.frame(local)
    if darken > 0:
        fr = Image.blend(fr, Image.new("RGB", fr.size, (0, 0, 0)), darken)
    img.paste(fr)


def stamp(img, s, cx, cy, t, t_on, col=LOSS, size=78, angle=-12):
    """A rubber stamp that slams in (scale 1.6 -> 1) and stays."""
    if t < t_on:
        return
    p = ease((t - t_on) / 0.18)
    sc = 1.6 - 0.6 * p
    f = font(int(size * sc))
    tmp = Image.new("RGBA", (int(size * sc * len(s) * 0.75 + 80), int(size * sc * 1.9)), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    w_ = d.textlength(s, font=f)
    box = (20, 14, 20 + w_ + 40, 14 + size * sc * 1.25)
    d.rounded_rectangle(box, radius=10, outline=col + (int(255 * p),), width=max(4, int(7 * sc)))
    d.text((40, 14 + size * sc * 0.62), s, font=f, fill=col + (int(255 * p),), anchor="lm")
    tmp = tmp.crop((0, 0, int(box[2] + 20), int(box[3] + 20))).rotate(angle, expand=True, resample=Image.BICUBIC)
    img.paste(tmp, (int(cx - tmp.width / 2), int(cy - tmp.height / 2)), tmp)


def thumbs_up(d, cx, cy, s, col):
    rrect(d, (cx - s * 0.35, cy - s * 0.05, cx + s * 0.35, cy + s * 0.5), s * 0.12, fill=col)      # fist
    rrect(d, (cx - s * 0.30, cy - s * 0.55, cx - s * 0.05, cy + s * 0.05), s * 0.12, fill=col)    # thumb
    rrect(d, (cx - s * 0.62, cy - s * 0.02, cx - s * 0.40, cy + s * 0.52), s * 0.06, fill=col)    # cuff


# ---------------------------------------------------------------- S04: the teams without a coach
def s04():
    from engine import Footage
    w = Words("p05", lead=0.15)
    frog = Footage(fr"{FOOT}\coaches\jabjabich.mp4", 6.0, 4.5, (1.0, 1.12), (0.45, 0.4))
    zon = Footage(fr"{FOOT}\coaches\zonic.mp4", 6.2, 6.5, (1.0, 1.08), (0.55, 0.4))
    spirit = [0, 0, 2, 0, 0, 0, 2, 0, 1, 1, 2, 0, 1, 0]            # Spirit's timeouts on its 14 maps (demos)
    opps = [3, 3, 2, 3, 2, 4, 4, 3, 3, 4, 7, 4, 3, 2]              # their opponents, same maps
    legacy = [("MOUZ", 4), ("NAVI", 4), ("PARIVISION", 6), ("G2", 1)]
    t_sp, t_watch, t_nine, t_their, t_47 = w("Spirit's"), w("Watch"), w("nine"), w("Their"), w("forty-seven")
    t_leg2, t_one, t_why, t_30 = w("Legacy", 0), w("one"), w("Why"), w("thirty")
    t_end = w.lead + w.duration + 0.8

    def draw(img, t):
        if t < t_sp - 0.15:                                      # 1. the frog, no coach
            paste_footage(img, frog, t, darken=0.25)
            d = ImageDraw.Draw(img)
            a = ramp(t, w("without") - 0.2, 0.3)
            side_shade(img, a)
            block_text(img, (100, 130), "TWO TEAMS.", 110, WHITE, (10, 12, 16), a=a)
            block_text(img, (100, 300), "NO COACH.", 110, (10, 12, 16), YELLOW, a=ramp(t, w("coach") - 0.2, 0.25))
            return
        if t >= t_why - 0.1:                                     # 5. their coach gets 30 free seconds
            local = t - (t_why - 0.1)
            if frog.frames is not None:
                frog.free()
            paste_footage(img, zon, local, darken=0.3)
            d = ImageDraw.Draw(img)
            a = ramp(t, t_30 - 0.25, 0.3)
            if a > 0:
                cx, cy, r = 1600, 330, 120
                left = max(0.0, 30 - (t - t_30))
                d.ellipse([cx - r - 30, cy - r - 30, cx + r + 30, cy + r + 30], fill=(8, 10, 14))
                d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(60, 60, 70), width=16)
                d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * left / 30, fill=YELLOW, width=16)
                text(d, (cx, cy), f"{math.ceil(left)}", 96, WHITE, anchor="mm", bg=(0, 0, 0))
                side_shade(img, a)
                block_text(img, (100, 470), "THEIR COACH GETS", 76, WHITE, (10, 12, 16), a=a)
                block_text(img, (100, 610), "30 FREE SECONDS", 110, (10, 12, 16), YELLOW, a=a)
            return
        d = ImageDraw.Draw(img)
        if t < t_watch - 0.1:                                    # 2. what happened to the coaches
            for k, (team, x, col) in enumerate((("TEAM SPIRIT", 160, WHITE), ("LEGACY", 1010, WHITE))):
                ca = ramp(t, (t_sp if k == 0 else w("Legacy's")) - 0.3, 0.35)
                if ca <= 0:
                    continue
                rrect(d, (x, 170, x + 750, 860), 24, fill=fade(PANEL, ca), outline=fade(LINE, ca), width=3)
                text(d, (x + 375, 240), team, 56, col, anchor="mm", alpha=ca, tracking=4, bg=PANEL)
            if t >= t_sp - 0.3:
                a = ramp(t, w("hally") - 0.2, 0.3)
                headset(d, 360, 450, 150, fade(DIM, a))
                text(d, (560, 420), "hally", 52, WHITE, alpha=a, bg=PANEL)
                text(d, (560, 482), "in hospital", 34, MUTED, alpha=ramp(t, w("hospital") - 0.2, 0.3), bg=PANEL)
                b = ramp(t, w("second") - 0.2, 0.3)
                headset(d, 360, 700, 150, fade(DIM, b))
                text(d, (560, 670), "S0tF1k", 52, WHITE, alpha=b, bg=PANEL)
                stamp(img, "VISA DENIED", 640, 775, t, w("visa") - 0.05, size=58)
            if t >= w("Legacy's") - 0.3:
                a = ramp(t, w("Legacy's") - 0.1, 0.3)
                headset(d, 1385, 520, 210, fade(MUTED, a))
                text(d, (1385, 760), "adr", 56, WHITE, anchor="mm", alpha=a, bg=PANEL)
                if t >= w("thumbs-up") - 0.2:
                    s = 1 + 0.25 * math.sin(min(1.0, (t - w("thumbs-up") + 0.2) / 0.5) * math.pi)
                    thumbs_up(d, 1610, 440, 120 * s, YELLOW)
                stamp(img, "BANNED", 1385, 560, t, w("banned") - 0.05, size=92)
            return
        if t < t_leg2 - 0.15:                                    # 3. Spirit vs their opponents, same 14 maps
            title(d, "SAME 14 MAPS", t, t_watch, y=120)
            for row, (lab, vals, col, t_on, t_full) in enumerate(
                    (("SPIRIT", spirit, CT, t_nine - 0.4, t_nine + 0.6),
                     ("THEIR OPPONENTS", opps, TT, t_their - 0.2, t_47 + 0.2))):
                y = 340 + row * 300
                a = ramp(t, t_on - 0.2, 0.3)
                text(d, (110, y - 70), lab, 40, col, alpha=a, tracking=3)
                total = sum(vals)
                shown = int(round(total * ease_io((t - t_on) / max(0.3, t_full - t_on)))) if t > t_on else 0
                k = 0
                for m, v in enumerate(vals):
                    x = 110 + m * 115
                    rrect(d, (x, y, x + 100, y + 150), 12, fill=fade(PANEL, a), outline=fade(LINE, a), width=2)
                    for j in range(v):
                        on = k < shown
                        k += 1
                        cx_, cy_ = x + 30 + (j % 2) * 40, y + 30 + (j // 2) * 32
                        if on:
                            d.ellipse([cx_ - 13, cy_ - 13, cx_ + 13, cy_ + 13], fill=col)
                text(d, (1810, y + 75), f"{shown}", 120, col, anchor="rm", alpha=a)
            return
        title(d, "LEGACY'S TIMEOUTS PER MATCH", t, t_leg2 - 0.15, y=120)   # 4. Legacy's matches
        for k, (opp, n) in enumerate(legacy):
            x = 190 + k * 400
            on = ramp(t, t_leg2 + 0.25 * k, 0.3)
            last = k == 3
            col = LOSS if last else YELLOW
            rrect(d, (x, 260, x + 340, 820), 22, fill=fade(PANEL, on),
                  outline=fade(LOSS if last and t >= t_one - 0.1 else LINE, on), width=4 if last else 2)
            text(d, (x + 170, 310), f"vs {opp}", 40, WHITE, anchor="mm", alpha=on, bg=PANEL)
            for j in range(n):
                pa = ramp(t, t_leg2 + 0.25 * k + 0.08 * j + 0.2, 0.2) if not last else ramp(t, t_one - 0.1, 0.2)
                cy_ = 730 - j * 62
                d.ellipse([x + 140, cy_ - 26, x + 200, cy_ + 26], fill=fade(col, pa))
            text(d, (x + 170, 780), "with coach" if not last else "NO COACH", 32, MUTED if not last else LOSS,
                 anchor="mm", alpha=on if not last else ramp(t, t_one - 0.1, 0.3), bg=PANEL, tracking=2)

    sfx = [(w("without") - 0.25, "whoosh-short", -4), (t_sp - 0.2, "whoosh-soft", -6),
           (w("visa"), "stamp-thud", -2), (w("banned"), "stamp-thud", -1), (w("thumbs-up"), "pop-1", -3),
           (t_watch - 0.15, "whoosh-short", -5), (t_nine - 0.3, "pop-2", -4), (t_47, "impact-soft-1", -4),
           (t_leg2 - 0.2, "whoosh-short", -5), (t_one - 0.1, "error-buzz-soft", -6), (t_why - 0.15, "whoosh-soft", -5)]
    render_section("s04", "p05", draw, sfx, lead=0.15, music_offset=music_at("s04"),
                   caption_style=lambda m: "Box" if (m < t_sp - 0.15 or m >= t_why - 0.1) else "Low")


# ---------------------------------------------------------------- icons
def rifle(d, x, y, s, col):
    """AK-style silhouette, s = length in px, (x, y) = left end of the stock, middle height."""
    k = s / 100
    pts = [(0, -6), (22, -9), (30, -6), (72, -6), (72, -10), (88, -10), (88, -6), (100, -6), (100, -2), (72, -2),
           (66, 4), (60, 14), (54, 14), (58, 2), (44, 2), (40, 16), (32, 16), (34, 2), (22, 2), (0, 8)]
    d.polygon([(x + px * k, y + py * k) for px, py in pts], fill=col)


def pistol(d, x, y, s, col):
    k = s / 100
    pts = [(0, -14), (100, -14), (100, 2), (40, 2), (34, 40), (12, 40), (18, 2), (0, 2)]
    d.polygon([(x + px * k, y + py * k) for px, py in pts], fill=col)


def gauge(d, cx, cy, r, frac, col, label, value, t_on, t, width=34):
    a = ramp(t, t_on - 0.3, 0.3)
    if a <= 0:
        return
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=fade(LINE, a), width=width)
    f = frac * ease((t - t_on) / 0.9)
    if f > 0:
        d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * f, fill=col, width=width)
    text(d, (cx, cy - 10), f"{round(value * ease((t - t_on) / 0.9))}%", 120, WHITE, anchor="mm", alpha=a, bg=(0, 0, 0))
    text(d, (cx, cy + r + 60), label, 36, col, anchor="mm", alpha=a, tracking=3, bg=(0, 0, 0))


# ---------------------------------------------------------------- S05: the naive answer
def s05():
    from engine import Footage
    w = Words("p06", lead=0.15)
    act = Footage(fr"{FOOT}\coldopen\vit_to_r6.mp4", 110.0, 16.0)
    t_43, t_34, t_9, t_case = w("forty-three"), w("thirty-four"), w("Nine"), w("Case")
    t_end = w("closed?", end=True)

    def draw(img, t):
        frozen = t > t_end + 0.25                                # record scratch: freeze + desaturate
        local = min(t, t_end + 0.25)
        paste_footage(img, act, local * 0.8, darken=0.74)
        if frozen:
            g = img.convert("L").convert("RGB")
            img.paste(Image.blend(img, g, min(1.0, (t - t_end - 0.25) / 0.15)))
        d = ImageDraw.Draw(img)
        a = ramp(t, w("timeouts") - 0.2, 0.3)
        block_text(img, (W // 2, 150), "AFTER LOSING A ROUND, WON THE NEXT ROUND", 50, WHITE, (10, 12, 16), a=a, anchor="m")
        gauge(d, 620, 520, 210, 0.432, YELLOW, "CALLED A TIMEOUT", 43, t_43 - 0.1, t)
        gauge(d, 1300, 520, 210, 0.34, (170, 176, 190), "DIDN'T", 34, t_34 - 0.1, t)
        ba = ramp(t, t_9 - 0.1, 0.2)
        if ba > 0:
            s = 1 + 0.4 * (1 - ease((t - t_9 + 0.1) / 0.3))
            rrect(d, (W // 2 - 95 * s, 430 - 60 * s, W // 2 + 95 * s, 430 + 60 * s), 30, fill=WIN)
            text(d, (W // 2, 430), "+9", int(90 * s), (10, 12, 16), anchor="mm")
        stamp(img, "CASE CLOSED?", W // 2, 880, t, t_case - 0.05, col=WIN, size=80, angle=-6)
        if frozen:                                               # rewind lines
            d2 = ImageDraw.Draw(img)
            for k in range(14):
                y = int((k * 83 + (t - t_end) * 900) % H)
                d2.line([0, y, W, y], fill=(200, 200, 200), width=2)

    sfx = [(w("timeouts") - 0.3, "whoosh-short", -6), (t_43 - 0.1, "pop-1", -3), (t_34 - 0.1, "pop-1", -3),
           (t_9 - 0.1, "impact-soft-1", -3), (t_case - 0.05, "stamp-thud", -2), (t_end + 0.2, "record-scratch", 2)]
    render_section("s05", "p06", draw, sfx, lead=0.15, tail=0.9, music_offset=music_at("s05"))


# ---------------------------------------------------------------- S06: it's the money
def s06():
    from engine import Footage
    w = Words("p07", lead=0.15)
    eq = Footage(fr"{FOOT}\coldopen\vit_to_r6.mp4", 68.5, 1.4, (1.0, 2.4), (0.24, 0.84))   # broadcast equipment values
    t_look, t_eight, t_teams2, t_rifle, t_thats, t_and, t_loss = (w("Look"), w("Eight"), w("Teams"), w("rifle"),
                                                                 w("That's"), w("And"), w("loss"))
    bonus = [1400, 1900, 2400, 2900, 3400]

    def draw(img, t):
        if t < t_look - 0.05:                                    # "Not so fast" — rewind lines over black
            d = ImageDraw.Draw(img)
            for k in range(14):
                y = int((k * 83 - t * 900) % H)
                d.line([0, y, W, y], fill=(90, 90, 96), width=2)
            text(d, (W // 2, H // 2 - 40), "NOT SO FAST.", 120, WHITE, anchor="mm", alpha=ramp(t, w("Not") - 0.1, 0.2))
            return
        if t < t_eight - 0.1:                                    # zoom into the broadcast's equipment value
            paste_footage(img, eq, t - (t_look - 0.05))
            d = ImageDraw.Draw(img)
            block_text(img, (W // 2, 90), "LOOK AT THE MONEY", 100, (10, 12, 16), YELLOW, a=ramp(t, t_look, 0.2), anchor="m")
            return
        if eq.frames is not None:
            eq.free()
        d = ImageDraw.Draw(img)
        if t < t_rifle - 0.15:                                   # 16/20 vs 11/20 rifles
            for row, (lab, n_on, col, t_on) in enumerate((("CALLED A TIMEOUT", 16, YELLOW, t_eight),
                                                          ("DIDN'T", 11, (170, 176, 190), t_teams2))):
                y = 330 + row * 330
                a = ramp(t, t_on - 0.2, 0.3)
                text(d, (130, y - 90), lab, 42, col, alpha=a, tracking=3)
                lit = int(n_on * ease((t - t_on) / 1.2))
                pct = round(100 * lit / 20)
                text(d, (1790, y - 90), f"{pct}% full-buy", 42, col, anchor="ra", alpha=a)
                for k in range(20):
                    x = 130 + (k % 10) * 168
                    yy = y + (k // 10) * 80
                    rifle(d, x, yy, 140, fade(col if k < lit else DIM, a))
            return
        if t < t_and - 0.1:                                      # a rifle beats a pistol; that's not the coach
            a = ramp(t, t_rifle - 0.15, 0.25)
            rifle(d, 330, 440, 520, fade(YELLOW, a))
            text(d, (W // 2 + 10, 440), ">", 160, WHITE, anchor="mm", alpha=ramp(t, w("beats") - 0.1, 0.2))
            pistol(d, 1220, 420, 330, fade((170, 176, 190), ramp(t, w("pistol") - 0.15, 0.25)))
            ca = ramp(t, t_thats - 0.1, 0.25)
            if ca > 0:
                headset(d, W // 2, 800, 130, fade(MUTED, ca))
                d.line([W // 2 - 110, 690, W // 2 + 110, 910], fill=fade(LOSS, ca), width=16)
                text(d, (W // 2 + 170, 800), "not the coach", 48, WHITE, anchor="lm", alpha=ca)
            return
        title(d, "LOSS BONUS PER PLAYER", t, t_and - 0.1, y=150)   # streaks end on their own
        for k, v in enumerate(bonus):
            on = ramp(t, t_and + 0.1 + 0.45 * k, 0.3)
            x = 330 + k * 280
            h = int(v / 3400 * 520 * ease((t - (t_and + 0.1 + 0.45 * k)) / 0.5))
            for c in range(0, h, 26):                            # coin stack
                d.ellipse([x, 820 - c - 22, x + 170, 820 - c + 8], fill=fade(YELLOW if k == 4 else (214, 178, 70), on),
                          outline=fade((120, 96, 30), on), width=2)
            text(d, (x + 85, 860), f"${v:,}", 40, WHITE, anchor="mm", alpha=on)
            text(d, (x + 85, 910), f"{k + 1} lost", 28, MUTED, anchor="mm", alpha=on)

    sfx = [(0.05, "whoosh-reverse-1s" if False else "whoosh-soft", -4), (t_look - 0.1, "whoosh-short", -4),
           (t_eight - 0.1, "pop-1", -4), (t_teams2 - 0.1, "pop-1", -4), (t_rifle - 0.15, "impact-soft-1", -4),
           (t_thats - 0.1, "error-buzz-soft", -7)] + [(t_and + 0.1 + 0.45 * k, "purchase-coins", -12) for k in range(0, 5, 2)]
    render_section("s06", "p07", draw, sfx, lead=0.15, music_offset=music_at("s06"),
                   caption_style=lambda m: "Box" if t_look - 0.05 <= m < t_eight - 0.1 else "Low")


# ---------------------------------------------------------------- S07: the fair fight
def s07():
    from engine import Footage
    w = Words("p08", lead=0.15)
    act = Footage(fr"{FOOT}\coldopen\vit_to_r6.mp4", 118.0, 12.0)
    checks = [("SAME SCORE", w("score,")), ("SAME STREAK", w("streak,")), ("SAME MONEY", w("money,")),
              ("SAME TEAMS", w("teams,")), ("NEXT GUN ROUND", w("gun"))]
    t_to, t_minus, t_nothing, t_and, t_open, t_no = (w("Timeout"), w("minus"), w("Nothing."), w("And"), w("Opening"),
                                                     w("no", 1))
    rows = [("Opening duels won", "-3 pts", (-8.3, 1.9), w("Opening")), ("Grenades thrown", "-0.1", (-4.9, 3.0), w("grenades,")),
            ("Bomb planted", "-5 pts", (-13.3, 2.9), w("bomb")), ("Switched bomb site", "-1 pt", (-14.9, 11.4), w("site,")),
            ("Plant timing", "-1 s", (-5.5, 5.4), w("plant"))]

    def axis(d, t, y, lo, hi, est, t_on, scale=60, big=True):
        a = ramp(t, t_on - 0.2, 0.3)
        cx = W // 2
        d.line([cx - 10 * scale, y, cx + 10 * scale, y], fill=fade(LINE, a), width=4)
        for v in range(-10, 11, 5):
            d.line([cx + v * scale, y - 12, cx + v * scale, y + 12], fill=fade(LINE, a), width=3)
            if big:
                text(d, (cx + v * scale, y + 46), f"{v:+d}" if v else "0", 30, MUTED, anchor="mm", alpha=a)
        sp = ease((t - t_on) / 0.6)
        x1, x2 = cx + est * scale + (lo - est) * scale * sp, cx + est * scale + (hi - est) * scale * sp
        rrect(d, (x1, y - 14, x2, y + 14), 14, fill=fade(mix(YELLOW, BG, 0.45), a))
        ex = cx + est * scale * ease((t - t_on) / 0.5)
        r = 26 if big else 16
        d.ellipse([ex - r, y - r, ex + r, y + r], fill=fade(YELLOW, a))

    def draw(img, t):
        if t < t_and - 0.15:
            d = ImageDraw.Draw(img)
            if t < t_to - 0.15:                                  # fair-fight checklist
                title(d, "FAIR FIGHTS ONLY", t, w("fair") - 0.2, y=150)
                for side, (lab, col, x) in enumerate((("TIMEOUT", YELLOW, 360), ("NO TIMEOUT", (170, 176, 190), 1110))):
                    a = ramp(t, w("fair") - 0.1 + 0.1 * side, 0.3)
                    rrect(d, (x, 250, x + 450, 860), 24, fill=fade(PANEL, a), outline=fade(col, a), width=3)
                    text(d, (x + 225, 310), lab, 46, col, anchor="mm", alpha=a, tracking=3, bg=PANEL)
                    for k, (c, tc) in enumerate(checks):
                        ca = ramp(t, tc - 0.1, 0.2)
                        y = 410 + k * 92
                        text(d, (x + 50, y), c, 32, WHITE, anchor="lm", alpha=ca, bg=PANEL)
                        if ca > 0:
                            d.line([(x + 380, y), (x + 395, y + 16), (x + 420, y - 18)], fill=WIN, width=7)
                return
            title(d, "TIMEOUT vs NO TIMEOUT  ·  NEXT GUN ROUND", t, t_to - 0.15, y=170)
            if t < t_minus:                                    # empty scale waits for the number
                a0 = ramp(t, t_to - 0.1, 0.3)
                d.line([W // 2 - 600, 560, W // 2 + 600, 560], fill=fade(LINE, a0), width=4)
                for v in range(-10, 11, 5):
                    d.line([W // 2 + v * 60, 548, W // 2 + v * 60, 572], fill=fade(LINE, a0), width=3)
                    text(d, (W // 2 + v * 60, 606), f"{v:+d}" if v else "0", 30, MUTED, anchor="mm", alpha=a0)
                text(d, (W // 2, 430), "?", 130, MUTED, anchor="mm", alpha=a0)
                return
            axis(d, t, 560, -6.2, 5.0, -0.7, t_minus)
            a = ramp(t, t_minus + 0.4, 0.3)
            text(d, (W // 2 - 42, 430), "-0.7", 110, YELLOW, anchor="mm", alpha=a)
            text(d, (W // 2, 700), "range: -6 to +5 points", 34, MUTED, anchor="mm", alpha=a)
            stamp(img, "NOTHING.", W // 2, 860, t, t_nothing - 0.05, col=YELLOW, size=96, angle=-5)
            return
        paste_footage(img, act, t - (t_and - 0.15), darken=0.7)  # mechanism rows over live gameplay
        d = ImageDraw.Draw(img)
        block_text(img, (W // 2, 90), "IT'S NOT HIDING IN THE PLAN EITHER", 58, WHITE, (10, 12, 16), anchor="m",
                   a=ramp(t, t_and - 0.1, 0.3))
        text(d, (W // 2, 140), "", 52, WHITE, anchor="mm",
             alpha=ramp(t, t_and - 0.1, 0.3), bg=(0, 0, 0), tracking=2)
        for k, (lab, val, (lo, hi), t_on) in enumerate(rows):
            y = 300 + k * 125
            a = ramp(t, t_on - 0.15, 0.25)
            text(d, (150, y), lab, 40, WHITE, anchor="lm", alpha=a, bg=(0, 0, 0))
            est = (lo + hi) / 2
            axis(d, t, y, max(lo, -10), min(hi, 10), max(-10, min(10, est)), t_on - 0.1, scale=26, big=False)
            done = ramp(t, t_no - 0.1 + 0.08 * k, 0.2)
            text(d, (1780, y), "±0" if done > 0.5 else val, 44, YELLOW if done > 0.5 else MUTED, anchor="rm", alpha=a, bg=(0, 0, 0))

    sfx = [(w("fair") - 0.3, "whoosh-short", -5)] + [(tc - 0.1, "toggle", -6) for _, tc in checks] + \
          [(t_to - 0.2, "whoosh-soft", -6), (t_minus, "pop-1", -3), (t_nothing - 0.05, "stamp-thud", -1),
           (t_and - 0.2, "whoosh-short", -5)] + [(tc - 0.15, "pop-2", -6) for *_, tc in rows] + [(t_no - 0.1, "impact-soft-2", -4)]
    render_section("s07", "p08", draw, sfx, lead=0.15, music_offset=music_at("s07"))


# ---------------------------------------------------------------- S08: back to kakafu — the luck test
def mini_board(d, x, y, gaps, t, t_on, label, w_=360, h_=520, hi=None):
    a = ramp(t, t_on - 0.2, 0.3)
    if a <= 0:
        return
    rrect(d, (x, y, x + w_, y + h_), 18, fill=fade(PANEL, a), outline=fade(LINE, a), width=2)
    text(d, (x + w_ / 2, y + 44), label, 46, WHITE, anchor="mm", alpha=a, bg=PANEL)
    zero, step = x + w_ / 2, (h_ - 110) / len(gaps)
    for i, g in enumerate(sorted(gaps, reverse=True)):
        yy = y + 90 + i * step
        L = g * 4.2 * ease((t - t_on - 0.03 * i) / 0.4)
        col = WIN if g >= 0 else LOSS
        if i == 0 and hi:
            col = hi
        x1, x2 = (zero, zero + L) if L >= 0 else (zero + L, zero)
        if abs(L) >= 1:
            d.rectangle([x1, yy + 2, x2, yy + step - 4], fill=fade(col, a))
    d.line([zero, y + 86, zero, y + h_ - 18], fill=fade(LINE, a), width=2)


def s08():
    w = Words("p09", lead=0.15)
    sim = json.load(open(r"D:\Youtube\video03\work\luck_sim.json", encoding="utf-8"))
    mx = np.array(sim["max_gap"])
    flick = sim["flicker"]
    real = [g for *_, g in leaderboard_rows()]
    fakes = [flick[0], flick[1], flick[2]]
    tables = [fakes[0], fakes[1], real, fakes[2]]            # the real one is C
    rows = leaderboard_rows()
    t_if, t_i, t_the, t_21, t_three, t_end = w("If"), w("I"), w("The"), w("plus"), w("Three"), w("which?", end=True)
    t_reveal = t_end + 0.9
    bins = np.arange(0, 52, 2)
    hist = np.histogram(mx, bins=bins)[0]

    def draw(img, t):
        d = ImageDraw.Draw(img)
        if t < t_if - 0.1:                                     # the pinned leaderboard comes back
            draw_board(d, t, rows, -5.0, hi=0, dim=1.0, pin_t=-5.0)
            return
        if t < t_i - 0.1:                                      # coin flips
            ph = (t - t_if) * 9
            cx, cy, r = W // 2, 470, 190
            wdt = abs(math.cos(ph)) * r
            face = CT if math.cos(ph) > 0 else TT
            d.ellipse([cx - wdt, cy - r, cx + wdt, cy + r], fill=face, outline=WHITE, width=6)
            if wdt > 60:
                text(d, (cx, cy), "CT" if face == CT else "T", int(min(1.0, wdt / r) * 120), (10, 12, 16), anchor="mm", bg=face)
            text(d, (W // 2, 140), "WHAT IF EVERY TIMEOUT WAS A COIN FLIP?", 52, WHITE, anchor="mm",
                 alpha=ramp(t, w("pure") - 0.2, 0.3), tracking=2)
            text(d, (W // 2, 800), "how good would the best coach look?", 46, YELLOW, anchor="mm", alpha=ramp(t, w("how") - 0.1, 0.3))
            return
        if t < t_the - 0.1:                                    # 10,000 runs: leaderboards reshuffle
            k = int((t - t_i) * 15) % len(flick)
            g = sorted(flick[k], reverse=True)
            for i, v in enumerate(g):
                y = 230 + i * 44
                L = v * 15
                col = WIN if v >= 0 else LOSS
                x1, x2 = (W // 2, W // 2 + L) if L >= 0 else (W // 2 + L, W // 2)
                rrect(d, (x1, y - 14, x2, y + 14), 5, fill=mix(col, BG, 0.25))
            n = int(10000 * ease_io((t - w("ten")) / max(0.5, t_the - 0.2 - w("ten")))) if t > w("ten") else 0
            text(d, (W // 2, 120), f"SIMULATION  #{n:,}", 64, YELLOW, anchor="mm")
            return
        if t < t_three - 0.1:                                  # histogram of the luckiest coach
            title(d, "THE LUCKIEST COACH IN EACH OF 10,000 RUNS", t, t_the - 0.1, y=120)
            x0, base, bw = 260, 840, 54
            top = hist.max()
            for i, c in enumerate(hist):
                g = ease((t - (t_the + 0.03 * i)) / 0.5)
                h = c / top * 560 * g
                lo = bins[i]
                col = YELLOW if 20 <= lo < 22 else (170, 176, 190)
                d.rectangle([x0 + i * bw, base - h, x0 + i * bw + bw - 6, base], fill=col)
                if i % 5 == 0:
                    text(d, (x0 + i * bw, base + 36), f"+{lo}", 28, MUTED, anchor="mm")
            kx = x0 + 15.4 / 2 * bw
            ka = ramp(t, w("luckiest") - 0.1, 0.3)
            d.line([kx, 260, kx, base], fill=fade(WHITE, ka), width=4)
            text(d, (kx - 14, 250), "kakafu +15", 38, WHITE, anchor="rs", alpha=ka)
            ya = ramp(t, t_21 - 0.1, 0.3)
            mxx = x0 + 21 / 2 * bw
            text(d, (mxx + 20, 250), "typical luckiest: +21", 38, YELLOW, anchor="ls", alpha=ya)
            text(d, (W // 2, 960), "luck alone beats +15 in 87 of 100 runs", 34, MUTED, anchor="mm", alpha=ya)
            return
        labels = "ABCD"                                        # spot the real one
        for k, g in enumerate(tables):
            mini_board(d, 120 + k * 430, 230, g, t, t_three + 0.12 * k, labels[k])
        text(d, (W // 2, 140), "3 ARE LUCK.  1 IS REAL.", 64, WHITE, anchor="mm", alpha=ramp(t, t_three - 0.1, 0.3), tracking=3)
        if t >= t_reveal:
            for k in range(4):
                cx = 120 + k * 430 + 180
                if k == 2:
                    stamp(img, "REAL", cx, 820, t, t_reveal + 0.15, col=YELLOW, size=80, angle=-8)
                else:
                    stamp(img, "LUCK", cx, 820, t, t_reveal + 0.05 * k, col=(170, 176, 190), size=70, angle=-8)

    sfx = [(t_if - 0.15, "whoosh-short", -5)] + [(t_if + 0.35 * k, "toggle", -9) for k in range(4)] + \
          [(t_i - 0.15, "riser-short-2s", -10), (t_the - 0.15, "whoosh-soft", -6), (t_21 - 0.1, "pop-1", -3),
           (t_three - 0.15, "whoosh-short", -5), (t_reveal, "stamp-thud", -3), (t_reveal + 0.15, "impact-soft-2", -2)]
    render_section("s08", "p09", draw, sfx, lead=0.15, tail=2.3, music_offset=music_at("s08"))


# ---------------------------------------------------------------- S09: the answer + Singapore
def s09():
    from engine import Footage
    w = Words("p10", lead=0.15)
    frog = Footage(fr"{FOOT}\coaches\jabjabich.mp4", 6.0, 4.4, (1.0, 1.12), (0.45, 0.4))
    zon = Footage(fr"{FOOT}\coaches\zonic.mp4", 6.0, 6.5, (1.0, 1.06), (0.55, 0.4))
    top3 = leaderboard_rows()[:3]
    t_for, t_but, t_maybe, t_sg, t_my = w("For"), w("But"), w("Maybe"), w("Singapore"), w("My")

    def draw(img, t):
        if t < t_for - 0.1:
            d = ImageDraw.Draw(img)
            text(d, (W // 2, 420), "ARE TIMEOUTS", 110, WHITE, anchor="mm", alpha=ramp(t, 0.2, 0.25))
            text(d, (W // 2, 570), "USELESS?", 170, YELLOW, anchor="mm", alpha=ramp(t, w("useless?") - 0.1, 0.2))
            return
        if t < t_but - 0.1:                                    # the verdict
            d = ImageDraw.Draw(img)
            text(d, (W // 2, 200), "NEXT GUN ROUND, AT THIS MAJOR:", 50, WHITE, anchor="mm", alpha=ramp(t, t_for - 0.1, 0.3), tracking=2)
            text(d, (W // 2, 330), "NO EFFECT FOUND", 120, YELLOW, anchor="mm", alpha=ramp(t, w("anything.") - 0.2, 0.25))
            cx, y, sc = W // 2, 620, 55
            a = ramp(t, w("data") - 0.2, 0.3)
            d.line([cx - 10 * sc, y, cx + 10 * sc, y], fill=fade(LINE, a), width=4)
            rrect(d, (cx - 6.2 * sc, y - 16, cx + 5.0 * sc, y + 16), 16, fill=fade(mix(YELLOW, BG, 0.45), a))
            d.ellipse([cx - 0.7 * sc - 24, y - 24, cx - 0.7 * sc + 24, y + 24], fill=fade(YELLOW, a))
            d.line([cx, y - 40, cx, y + 40], fill=fade(WHITE, a), width=3)
            text(d, (cx, y + 70), "0", 32, MUTED, anchor="mm", alpha=a)
            return
        if t < t_maybe - 0.1:                                  # but the coachless teams stopped calling them
            paste_footage(img, frog, t - (t_but - 0.1), darken=0.45)
            d = ImageDraw.Draw(img)
            side_shade(img, ramp(t, t_but - 0.1, 0.3))
            block_text(img, (100, 150), "NO COACH  =  NO TIMEOUTS", 80, (10, 12, 16), YELLOW, a=ramp(t, w("stopped") - 0.2, 0.25))
            for k, (lab, val) in enumerate((("SPIRIT", "9  vs  47"), ("LEGACY", "4-6  →  1"))):
                a = ramp(t, w("teams") + 0.25 * k, 0.3)
                if a <= 0:
                    continue
                box = Image.new("RGBA", (650, 120), (10, 12, 16, int(225 * a)))
                img.paste(box, (110, 330 + k * 150), box)
                d = ImageDraw.Draw(img)
                text(d, (140, 390 + k * 150), lab, 44, MUTED, anchor="lm", alpha=a, bg=(10, 12, 16))
                text(d, (730, 390 + k * 150), val.replace("→", "->"), 60, YELLOW, anchor="rm", alpha=a, bg=(10, 12, 16))
            return
        if t < t_sg - 0.1:                                     # what the scoreboard can't see
            if frog.frames is not None:
                frog.free()
            local = (t - (t_maybe - 0.1)) * 0.6                # slow motion
            fr = zon.frame(local)
            g = fr.convert("L").convert("RGB")
            img.paste(Image.blend(Image.blend(fr, g, 0.5), Image.new("RGB", fr.size, (0, 0, 0)), 0.35))
            d = ImageDraw.Draw(img)
            side_shade(img, ramp(t, w("scoreboard") - 0.3, 0.3))
            block_text(img, (100, 130), "WHAT THE SCOREBOARD", 88, WHITE, (10, 12, 16), a=ramp(t, w("scoreboard") - 0.3, 0.25))
            block_text(img, (100, 290), "CAN'T SEE", 130, (10, 12, 16), YELLOW, a=ramp(t, w("can't", 1) - 0.1, 0.25))
            return
        if zon.frames is not None:
            zon.free()
        d = ImageDraw.Draw(img)
        if t < t_my - 0.1:                                     # Singapore
            a = ramp(t, t_sg - 0.1, 0.3)
            text(d, (W // 2, 330), "NEXT MAJOR", 44, MUTED, anchor="mm", alpha=a, tracking=6)
            text(d, (W // 2, 460), "SINGAPORE", 170, WHITE, anchor="mm", alpha=a)
            da = ramp(t, w("November") - 0.15, 0.25)
            rrect(d, (W // 2 - 330, 580, W // 2 + 330, 690), 16, fill=fade(YELLOW, da))
            text(d, (W // 2, 635), "25 NOV - 13 DEC 2026", 56, (10, 12, 16), anchor="mm", alpha=da, bg=YELLOW)
            return
        title(d, "MY PREDICTION", t, t_my - 0.1, y=150)       # the top of this table won't stay on top
        drop = ease((t - (w("won't") - 0.05)) / 0.6)
        for k, (coach, team, gap) in enumerate(top3):
            x = 260 + k * 480
            y = 330 + drop * (180 + 90 * k) * (1 if k != 1 else 0.6)
            ang_shake = math.sin(t * 20 + k) * 4 * min(1.0, drop * 3) * (1 - drop)
            a = ramp(t, t_my + 0.15 * k, 0.3)
            rrect(d, (x, y + ang_shake, x + 400, y + 260 + ang_shake), 20, fill=fade(PANEL, a), outline=fade(YELLOW if k == 0 else LINE, a), width=3)
            text(d, (x + 200, y + 70 + ang_shake), f"#{k + 1}", 44, MUTED, anchor="mm", alpha=a, bg=PANEL)
            text(d, (x + 200, y + 140 + ang_shake), coach, 58, WHITE, anchor="mm", alpha=a, bg=PANEL)
            text(d, (x + 200, y + 205 + ang_shake), f"{team}  {gap:+.0f}", 36, YELLOW, anchor="mm", alpha=a, bg=PANEL)
        text(d, (W // 2, 960), "check back after 13 December", 36, MUTED, anchor="mm", alpha=ramp(t, w("top", 1) - 0.1, 0.3))

    sfx = [(0.1, "impact-soft-1", -6), (t_for - 0.15, "whoosh-short", -5), (w("anything.") - 0.2, "stamp-thud", -3),
           (t_but - 0.15, "whoosh-soft", -6), (t_maybe - 0.15, "whoosh-soft", -7), (t_sg - 0.15, "impact-soft-2", -3),
           (t_my - 0.15, "whoosh-short", -5), (w("won't") - 0.05, "error-buzz-soft", -7)]
    render_section("s09", "p10", draw, sfx, lead=0.15, tail=0.45, music_offset=music_at("s09"),
                   caption_style=lambda m: "Box" if t_but - 0.1 <= m < t_sg - 0.1 else "Low")


# ---------------------------------------------------------------- S10: outro — comment prompt, ident, end-screen space
def s10():
    w = Words("p11", lead=0.15)
    logo = Image.open(r"D:\Youtube\video03\work\logo.png").convert("RGBA")
    logo.thumbnail((300, 300))
    names = ["zonic", "B1ad3", "sAw", "kakafu", "XTQZZZ", "sidde", "Fabre", "maaRaa", "sycrone", "Jab Jabich (frog)"]
    t_tell, t_ident = w("Tell"), w("comments.", end=True) + 0.5
    dur = t_ident + 7.7 + 8.0                                  # ident + space for YouTube end-screen elements

    def draw(img, t):
        d = ImageDraw.Draw(img)
        if t < t_ident:
            a = ramp(t, 0.1, 0.3)
            rrect(d, (W // 2 - 520, 250, W // 2 + 520, 760), 26, fill=fade(PANEL, a), outline=fade(LINE, a), width=3)
            text(d, (W // 2, 330), "BEST TIMEOUT CALLER IN CS?", 54, WHITE, anchor="mm", alpha=a, bg=PANEL, tracking=2)
            k = int(max(0.0, t - 0.4) * 5) % len(names)
            for j in range(3):
                nm = names[(k + j) % len(names)]
                y = 450 + j * 100
                rrect(d, (W // 2 - 440, y - 38, W // 2 + 440, y + 38), 14, fill=fade(BG, a), outline=fade(LINE, a), width=2)
                text(d, (W // 2 - 400, y), nm, 44, YELLOW if "frog" in nm else WHITE, anchor="lm", alpha=a, bg=BG)
            text(d, (W // 2, 860), "tell me in the comments", 40, MUTED, anchor="mm", alpha=ramp(t, t_tell - 0.1, 0.3))
            return
        a = ramp(t, t_ident, 0.5)                              # ident card; lower area left free for end-screen elements
        lg = logo.copy()
        lg.putalpha(lg.getchannel("A").point(lambda v: int(v * a)))
        img.paste(lg, (W // 2 - lg.width // 2, 110), lg)
        text(d, (W // 2, 480), "SPORTS ON THE LINE", 84, WHITE, anchor="mm", alpha=a, tracking=8)
        text(d, (W // 2, 560), "data stories from the games we love", 34, MUTED, anchor="mm", alpha=ramp(t, t_ident + 1.0, 0.5))

    sfx = [(0.05, "whoosh-short", -6), (t_ident, "ident", 0)]
    render_section("s10", "p11", draw, sfx, lead=0.15, dur=dur, music_offset=music_at("s10"))


# ---------------------------------------------------------------- S00: cold open (Vitality 0-5 -> timeout -> 5 straight)
def round_strip(d, t, red_on, green_on, y=190, label="VITALITY vs FALCONS  ·  ANUBIS  ·  PLAYOFFS"):
    x0 = W // 2 - 330
    rrect(d, (x0 - 30, y - 62, x0 + 10 * 66 + 20, y + 80), 16, fill=(10, 12, 16))   # own panel, clear of the broadcast HUD
    text(d, (W // 2, y - 30), label, 26, WHITE, anchor="mm", tracking=3, bg=(10, 12, 16))
    for i in range(10):
        x = x0 + i * 66
        rrect(d, (x, y, x + 56, y + 56), 8, fill=(18, 20, 26), outline=(70, 76, 90), width=2)
        on = red_on(i) if i < 5 else green_on(i - 5)
        if on > 0:
            col = LOSS if i < 5 else WIN
            s = 1 + 0.35 * (1 - ease(on))
            h = 26 * s * min(1.0, on * 3)
            rrect(d, (x + 28 - h, y + 28 - h, x + 28 + h, y + 28 + h), 8, fill=col)


def s00():
    from engine import Footage
    w = Words("p01", lead=0.15)
    src = fr"{FOOT}\coldopen\vit_to_r6.mp4"
    sad = Footage(src, 52.8, 3.0, (1.0, 1.06), (0.55, 0.4))        # Vitality players right after going 0-5
    tout = Footage(src, 66.8, 3.0, (1.0, 1.05), (0.5, 0.45))       # the broadcast TIMEOUT shot
    act = Footage(src, 104.0, 9.0)                                 # round 6 action
    t_to, t_won, t_thats, t_lets = w("Timeout"), w("Five", 1), w("That's"), w("Or")
    t_end = w("it?", end=True)
    freeze = {}

    def draw(img, t):
        if t < t_to - 0.05:                                        # five rounds down
            paste_footage(img, sad, t, darken=0.15)
            d = ImageDraw.Draw(img)
            round_strip(d, t, lambda i: ramp(t, w("Five") + 0.12 * i, 0.15), lambda i: 0)
            return
        if t < t_won - 0.05:                                       # timeout
            paste_footage(img, tout, t - (t_to - 0.05), darken=0.1)
            d = ImageDraw.Draw(img)
            round_strip(d, t, lambda i: 1, lambda i: 0)
            a = ramp(t, t_to - 0.05, 0.15)
            cx, cy, r = W - 300, 420, 80
            d.ellipse([cx - r - 26, cy - r - 26, cx + r + 26, cy + r + 26], fill=(8, 10, 14))
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(60, 60, 70), width=12)
            d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * a, fill=YELLOW, width=12)
            text(d, (cx, cy), "30", 56, WHITE, anchor="mm", bg=(0, 0, 0))
            return
        if t < t_lets - 0.1:                                       # five rounds won (speed-ramped), the claim
            local = t - (t_won - 0.05)
            ramp_end = t_thats - (t_won - 0.05)
            fl = local * 2.2 if local < ramp_end else ramp_end * 2.2 + (local - ramp_end)
            paste_footage(img, act, min(fl, act.dur - 0.05), darken=0.15 if t < t_thats else 0.45)
            d = ImageDraw.Draw(img)
            round_strip(d, t, lambda i: 1, lambda i: ramp(t, t_won + 0.12 * i, 0.15))
            if t >= t_thats - 0.1:
                block_text(img, (W // 2, 440), "THE TIMEOUT THAT", 88, WHITE, (10, 12, 16), a=ramp(t, t_thats - 0.1, 0.25), anchor="m")
                block_text(img, (W // 2, 580), "TURNED THE GAME?", 120, (10, 12, 16), YELLOW, a=ramp(t, w("turned") - 0.1, 0.2), anchor="m")
                text(d, (W // 2, 625), "", 96, YELLOW, anchor="mm",
                     alpha=ramp(t, w("turned") - 0.1, 0.25), bg=(0, 0, 0))
            return
        if "img" not in freeze:                                    # "Or was it?": freeze the last action frame
            local = t_lets - 0.1 - (t_won - 0.05)
            ramp_end = t_thats - (t_won - 0.05)
            fl = ramp_end * 2.2 + (local - ramp_end)
            fr = act.frame(min(fl, act.dur - 0.05))
            g = fr.convert("L").convert("RGB")
            freeze["img"] = Image.blend(Image.blend(fr, g, 0.85), Image.new("RGB", fr.size, (0, 0, 0)), 0.5)
            for fx in (sad, tout, act):
                fx.free()
        img.paste(freeze["img"])
        d = ImageDraw.Draw(img)
        round_strip(d, t, lambda i: 1, lambda i: 1)
        s = 1 + 0.3 * (1 - ease((t - t_lets) / 0.25))
        block_text(img, (W // 2, 470), "OR WAS IT?", int(150 * s), (10, 12, 16), YELLOW, a=ramp(t, t_lets - 0.05, 0.15), anchor="m")

    sfx = [(t_to - 0.1, "impact-soft-1", -3), (t_won - 0.1, "whoosh-short", -4), (t_lets - 0.1, "dry-thud", -1),
           (t_lets, "impact-soft-2", -3)]
    sfx += [(w("Five") + 0.12 * i, "click-soft", -2) for i in range(5)] + [(t_won + 0.12 * i, "click-soft", -2) for i in range(5)]
    render_section("s00", "p01", draw, sfx, lead=0.15, tail=0.5, music_offset=music_at("s00"), caption_style="Box")


# ---------------------------------------------------------------- S00A: opener — coaches named by the narration, then the title
def s00a():
    from PIL import ImageFilter
    from engine import Footage, block_text, lower_third, side_shade
    w = Words("p12", lead=0.15)
    src = r"D:\Youtube\video03\footage\coaches"
    fab = Footage(fr"{src}\fabre.mp4", 3.6, 4.0, (1.0, 1.08), (0.55, 0.4))
    sid = Footage(fr"{src}\sidde.mp4", 4.0, 4.0, (1.0, 1.08), (0.6, 0.4))
    zon = Footage(fr"{src}\zonic.mp4", 3.0, 4.0, (1.0, 1.08), (0.6, 0.45))
    frog_close = Footage(fr"{src}\jabjabich.mp4", 6.0, 4.4, (1.0, 1.15), (0.45, 0.4))
    frog_pc = Footage(fr"{src}\jabjabich.mp4", 10.62, 4.8, (1.0, 1.18), (0.5, 0.42))
    cuts = [(0.0, fab, "Fabre", "Aurora", "SEMI-FINAL", MUTED),
            (w("FURIA.") - 0.12, sid, "sidde", "FURIA", "RUNNER-UP", (200, 200, 210)),
            (w("champions,") - 0.12, zon, "zonic", "Team Falcons", "CHAMPIONS", YELLOW),
            (w("And") - 0.08, frog_close, None, None, None, None),
            (w("is") - 0.05, frog_pc, "Jab Jabich", "Team Spirit  ·  a plush frog", "SEMI-FINAL", WIN)]
    t_title = w("Are") - 0.12
    blurred = {}

    def draw(img, t):
        if t < t_title:
            k = max(i for i, c in enumerate(cuts) if t >= c[0])
            for j, c in enumerate(cuts):
                if j != k and c[1].frames is not None and c[1] is not cuts[k][1]:
                    c[1].free()
            t0, fx, name, sub, tag, tag_col = cuts[k]
            local = t - t0
            img.paste(fx.frame(local))
            d = ImageDraw.Draw(img)
            if name:
                lower_third(d, t, t0 + 0.08, name, sub, tag, tag_col, y=640)
            if local < 0.067 and k > 0 and k != 4:     # white flash on the coach cuts; the frog reveal is a hard cut
                d.rectangle([0, 0, W, H], fill=(245, 245, 245))
            if k == 4 and local < 0.12:                # frog reveal: quick punch
                pass
            return
        # title card over the blurred frog: the video's title, said by the narration
        if "bg" not in blurred:
            fr = frog_pc.frame(min(4.7, t_title - cuts[4][0]))
            blurred["bg"] = Image.blend(fr.filter(ImageFilter.GaussianBlur(18)), Image.new("RGB", fr.size, (0, 0, 0)), 0.55)
            frog_pc.free()
        img.paste(blurred["bg"])
        d = ImageDraw.Draw(img)
        a = ramp(t, t_title, 0.15)
        s1 = 1 + 0.25 * (1 - ease((t - t_title) / 0.25))
        text(d, (W // 2, 330), "ARE TIMEOUTS", int(130 * s1), WHITE, anchor="mm", alpha=a, bg=(0, 0, 0))
        ua = ramp(t, w("useless?") - 0.12, 0.15)
        s2 = 1 + 0.35 * (1 - ease((t - w("useless?") + 0.12) / 0.25))
        text(d, (W // 2, 500), "USELESS?", int(200 * s2), YELLOW, anchor="mm", alpha=ua, bg=(0, 0, 0))
        ca = ramp(t, w("checked") - 0.1, 0.25)
        if ca > 0:
            n = int(430 * ease_io((t - w("all")) / max(0.4, w("thirty,", end=True) - w("all"))))
            text(d, (W // 2, 690), f"I CHECKED ALL {n}", 72, WHITE, anchor="mm", alpha=ca, bg=(0, 0, 0), tracking=3)
            text(d, (W // 2, 780), "AT THE COLOGNE MAJOR 2026", 40, MUTED, anchor="mm",
                 alpha=ramp(t, w("Cologne") - 0.15, 0.25), bg=(0, 0, 0), tracking=4)

    sfx = [(c[0] - 0.12, "whoosh-short", -6) for c in cuts[1:4]] + [(cuts[4][0], "pop-1", -2),
           (t_title - 1.9, "riser-short-2s", -9), (t_title, "impact-soft-1", -2), (w("useless?") - 0.1, "impact-soft-2", -1)]
    render_section("s00a", "p12", draw, sfx, lead=0.15, tail=0.9, music_offset=0.0, caption_style="Low")


# ---------------------------------------------------------------- S00A option B: stakes-first hook over the coaches
def s00a_b():
    from PIL import ImageFilter
    from engine import Footage, block_text, lower_third, side_shade
    w = Words("p13", lead=0.15)
    src = FOOT + r"\coaches"
    fab = Footage(src + r"\fabre.mp4", 3.6, 5.0, (1.0, 1.10), (0.55, 0.4))
    vto = Footage(FOOT + r"\coldopen\vit_to_r6.mp4", 66.8, 4.5, (1.0, 1.08), (0.5, 0.45))   # a real broadcast TIMEOUT
    zon = Footage(src + r"\zonic.mp4", 3.0, 4.0, (1.0, 1.08), (0.6, 0.45))
    sid = Footage(src + r"\sidde.mp4", 4.0, 4.0, (1.0, 1.08), (0.6, 0.4))
    frog_close = Footage(src + r"\jabjabich.mp4", 6.0, 4.4, (1.0, 1.15), (0.45, 0.4))
    frog_pc = Footage(src + r"\jabjabich.mp4", 10.62, 4.8, (1.0, 1.18), (0.5, 0.42))
    cuts = [(0.0, fab, None), (w("At") - 0.1, vto, None),
            (w("champions") - 0.15, zon, ("zonic", "Team Falcons", "CHAMPIONS", YELLOW)),
            (w("runners-up") - 0.15, sid, ("sidde", "FURIA", "RUNNER-UP", (200, 200, 210))),
            (w("and", 1) - 0.08, frog_close, None),     # 2nd "and" (the 1st is in "four hundred and thirty")
            (w("brought") - 0.05, frog_pc, ("Jab Jabich", "Team Spirit  ·  a plush frog", "SEMI-FINAL", WIN))]
    t_title = w("So,") - 0.1
    blurred = {}

    def draw(img, t):
        if t < t_title:
            k = max(i for i, c in enumerate(cuts) if t >= c[0])
            for j, c in enumerate(cuts):
                if j != k and c[1].frames is not None and c[1] is not cuts[k][1]:
                    c[1].free()
            t0, fx, plate = cuts[k]
            local = t - t0
            paste_footage(img, fx, local, darken=0.15 if k in (0, 1) else 0.0)
            d = ImageDraw.Draw(img)
            if k == 0:                                         # thirty seconds: the ring counts down
                a = ramp(t, w("Thirty") - 0.1, 0.2)
                side_shade(img, a)
                cx, cy, r = W - 330, 400, 170
                left = max(0.0, 30 - max(0.0, t - w("Thirty")) * 3)          # fast countdown for tension
                if a > 0:
                    d.ellipse([cx - r - 34, cy - r - 34, cx + r + 34, cy + r + 34], fill=(8, 10, 14))
                    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(55, 60, 72), width=24)
                    d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * left / 30 * a, fill=YELLOW, width=24)
                    text(d, (cx, cy - 6), f"{math.ceil(left)}", 170, WHITE, anchor="mm", alpha=a, bg=(8, 10, 14))
                block_text(img, (100, 130), "30 SECONDS", 130, WHITE, (10, 12, 16), a=a)
                block_text(img, (100, 320), "TO SAVE A GAME", 84, (10, 12, 16), YELLOW, a=ramp(t, w("save") - 0.15, 0.2))
            elif k == 1:                                       # 430 of them
                a = ramp(t, w("four") - 0.15, 0.2)
                side_shade(img, a)
                n = int(430 * ease_io((t - w("four")) / max(0.4, w("them.", end=True) - w("four"))))
                block_text(img, (100, 120), f"{n}", 250, (10, 12, 16), YELLOW, a=a, pad=(36, 18))
                block_text(img, (100, 470), "TIMEOUTS AT THE COLOGNE MAJOR", 56, WHITE, (10, 12, 16), a=a)
            if plate:
                lower_third(d, t, t0 + 0.08, *plate, y=590)
            if local < 0.067 and 0 < k < 4:                    # white flash on the coach cuts; hard cuts into the frog
                d.rectangle([0, 0, W, H], fill=(245, 245, 245))
            return
        if "bg" not in blurred:                                # title card over the blurred frog
            fr = frog_pc.frame(min(4.7, t_title - cuts[5][0]))
            blurred["bg"] = Image.blend(fr.filter(ImageFilter.GaussianBlur(18)), Image.new("RGB", fr.size, (0, 0, 0)), 0.55)
            frog_pc.free()
        img.paste(blurred["bg"])
        d = ImageDraw.Draw(img)
        a = ramp(t, w("are") - 0.12, 0.15)
        s1 = 1 + 0.25 * (1 - ease((t - w("are") + 0.12) / 0.25))
        text(d, (W // 2, 330), "ARE TIMEOUTS", int(130 * s1), WHITE, anchor="mm", alpha=a, bg=(0, 0, 0))
        tu = w("useless?") - 0.12
        s2 = 1 + 0.35 * (1 - ease((t - tu) / 0.25))
        text(d, (W // 2, 500), "USELESS?", int(200 * s2), YELLOW, anchor="mm", alpha=ramp(t, tu, 0.15), bg=(0, 0, 0))
        tc = w("checked") - 0.1                                # second half of the title, said by the narration
        if t >= tc:
            n = int(430 * ease_io((t - w("all")) / max(0.4, w("thirty,", end=True) - w("all"))))
            text(d, (W // 2, 690), f"I CHECKED ALL {n}", 72, WHITE, anchor="mm", alpha=ramp(t, tc, 0.2), bg=(0, 0, 0), tracking=3)
            text(d, (W // 2, 780), "AT THE COLOGNE MAJOR 2026", 40, MUTED, anchor="mm", alpha=ramp(t, w("Cologne") - 0.15, 0.25),
                 bg=(0, 0, 0), tracking=4)

    sfx = [(w("Thirty") - 0.05, "impact-soft-1", -3)] + [(w("Thirty") + 0.33 * k, "click-soft", -6) for k in range(6)] + \
          [(cuts[1][0] - 0.1, "whoosh-short", -5), (cuts[2][0] - 0.12, "whoosh-short", -6), (cuts[3][0] - 0.12, "whoosh-short", -6),
           (cuts[5][0], "pop-1", -2), (t_title - 1.9, "riser-short-2s", -9), (w("useless?") - 0.1, "impact-soft-2", -1),
           (w("checked") - 0.1, "dry-thud", -3)]
    render_section("s00a_b", "p13", draw, sfx, lead=0.15, tail=0.6, music_offset=0.0, caption_style="Box")


if __name__ == "__main__":
    for sid in sys.argv[1:]:
        globals()[sid]()
