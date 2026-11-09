"""Video 02 Major chapters (p09–p18): c1a/c1b … c5a/c5b. Each Major = a story half (chapter card, underdog path,
key series) and a final half (map-by-map final, champion stamp, MVP on camera). Run through sections.py."""
from sections import *     # noqa: F401,F403  (helpers, TEAM badges, engine)


# ---------- building blocks ----------
def chapter_card(img, t, cfg, w):
    """Footage behind a big chapter number, event, city and date; the city slams in on its word."""
    show(img, cfg["bgfx"], t, dim=0.5, blur=2)
    side_shade(img, 1.0, frac=0.8)
    d = ImageDraw.Draw(img)
    text(d, (130, 250), cfg["num"], 220, YELLOW, anchor="lm", alpha=ramp(t, 0.05, 0.3))
    block_text(img, (130, 390), cfg["event"], 40, WHITE, INK, a=ramp(t, 0.15, 0.3))
    t_city = w(cfg["city_word"])
    if t >= t_city - 0.05:
        sc = 1.3 - 0.3 * ease((t - t_city + 0.05) / 0.15)
        f = font(int(190 * sc))
        d.text((136, 568), cfg["city"], font=f, fill=(0, 0, 0), anchor="lm")
        d.text((130, 560), cfg["city"], font=f, fill=WHITE, anchor="lm")
    block_text(img, (134, 680), cfg["date"], 54, INK, YELLOW, a=ramp(t, 0.1, 0.3))
    for tag_, word in cfg.get("tags", []):
        if t >= w(word):
            block_text(img, (134, 790), tag_, 44, WHITE, INK, a=ramp(t, w(word), 0.25))


def stage_path(img, t, stages, teams, t0, y0=None, title_s=None):
    """Teams climbing through the stages: one row per team, the badge steps right column by column."""
    d = ImageDraw.Draw(img)
    if title_s:
        title(d, title_s, t, t0)
    x0, step = 300, (W - 600) / max(len(stages) - 1, 1)
    gap = 240
    if y0 is None:
        y0 = int(H / 2 - (len(teams) - 1) * gap / 2) - 40
    for j, sname in enumerate(stages):
        last = j == len(stages) - 1
        text(d, (x0 + j * step, y0 - 90), sname, 34, YELLOW if last else MUTED, anchor="mm", alpha=ramp(t, t0 + 0.05 * j, 0.3), tracking=2)
    for i, (key, frm, to, ts) in enumerate(teams):
        y = y0 + i * gap
        a = ramp(t, t0, 0.3)
        d.line([(x0, y + 32), (x0 + (len(stages) - 1) * step, y + 32)], fill=fade(LINE, a), width=6)
        pos = min(to, frm + (t - ts) / 0.28) if t >= ts else frm
        for j in range(len(stages)):
            r = 11
            reached = t >= ts and frm <= j <= pos
            d.ellipse([x0 + j * step - r, y + 32 - r, x0 + j * step + r, y + 32 + r], fill=YELLOW if reached else fade(DIM, a))
        badge(img, x0 + pos * step, y - 8, key, h=80, a=1.0 if t >= ts else a * 0.35, anchor="m")
        if t >= ts and pos >= to:
            stamp(img, "MADE IT", x0 + to * step - 40, y + 110, t, ts + (to - frm) * 0.28 + 0.05, col=YELLOW, size=36, angle=-5)


def series_card(img, t, t_on, a_key, b_key, maps, x, y, w_=760, note=None, note_t=None):
    """Match card: two badges, then one row per map with scores (winner's score yellow); OT maps get a tag."""
    if t < t_on:
        return
    d = ImageDraw.Draw(img)
    a = ease((t - t_on) / 0.25)
    h_ = 120 + 74 * len(maps)
    yy = y + 30 * (1 - a)
    rrect(d, (x, yy, x + w_, yy + h_), 18, fill=(16, 19, 26), outline=LINE, width=2)
    badge(img, x + 30, yy + 26, a_key, h=56, a=a)
    bw = d.textlength(TEAM[b_key][0], font=font(int(56 * 0.56))) + 56 * 0.9
    badge(img, x + w_ - 40 - bw, yy + 26, b_key, h=56, a=a)
    text(d, (x + w_ / 2, yy + 54), "vs", 30, MUTED, anchor="mm", alpha=a)
    for k, (m, sa, sb, ot, t_row) in enumerate(maps):
        if t < t_row:
            continue
        p = ease((t - t_row) / 0.2)
        ry = yy + 110 + k * 74
        text(d, (x + 40, ry + 30), m, 34, WHITE, anchor="lm", alpha=p)
        win_a = sa > sb
        text(d, (x + w_ / 2 - 30, ry + 30), str(sa), 50, YELLOW if win_a else WHITE, anchor="rm", alpha=p)
        text(d, (x + w_ / 2, ry + 30), "–", 40, MUTED, anchor="mm", alpha=p)
        text(d, (x + w_ / 2 + 30, ry + 30), str(sb), 50, WHITE if win_a else YELLOW, anchor="lm", alpha=p)
        if ot:
            block_text(img, (x + w_ - 190, ry + 8), "OVERTIME", 28, INK, YELLOW, a=p, pad=(12, 8))
    if note and note_t is not None:
        stamp(img, note, x + w_ / 2, yy + h_ + 60, t, note_t, size=50, angle=-4)


def mvp_card(img, t, t_on, fx, name, sub):
    """MVP on camera: footage, MVP tag, the name slamming in, one line of context."""
    show(img, fx, t - t_on, dim=0.15)
    side_shade(img, 1.0, frac=0.6, strength=0.7)
    block_text(img, (110, 620), "MVP", 60, INK, YELLOW, a=ramp(t, t_on, 0.2))
    if t >= t_on + 0.1:
        sc = 1.3 - 0.3 * ease((t - t_on - 0.1) / 0.15)
        d = ImageDraw.Draw(img)
        f = font(int(170 * sc))
        d.text((116, 808), name, font=f, fill=(0, 0, 0), anchor="lm")
        d.text((110, 800), name, font=f, fill=WHITE, anchor="lm")
    if sub:
        block_text(img, (114, 900), sub, 36, WHITE, INK, a=ramp(t, t_on + 0.4, 0.25))


def final_board(img, t, t0, champ, runner, maps, label="GRAND FINAL"):
    """Map-by-map final. maps: (map, champion score, runner-up score, t_on, shake). Maps the champion lost go red."""
    d = ImageDraw.Draw(img)
    title(d, label, t, t0)
    a = ramp(t, t0, 0.3)
    badge(img, 560, 200, champ, h=80, a=a, anchor="m")
    text(d, (W / 2, 240), "vs", 40, MUTED, anchor="mm", alpha=a)
    badge(img, 1360, 200, runner, h=80, a=a, anchor="m")
    for k, (m, sa, sb, t_on, shake_) in enumerate(maps):
        if t < t_on:
            continue
        p = ease((t - t_on) / 0.2)
        y = 330 + k * 118
        dx = 16 * math.sin((t - t_on) * 60) * max(0.0, 1 - (t - t_on) / 0.35) if shake_ else 0
        won = sa > sb
        rrect(d, (360 + dx, y, 1560 + dx, y + 98), 16, fill=(18, 22, 30) if won else (56, 20, 24), outline=YELLOW if won else LOSS, width=3)
        text(d, (400 + dx, y + 49), m, 44, WHITE, anchor="lm", alpha=p)
        text(d, (900 + dx, y + 49), str(sa), 72, YELLOW if won else LOSS, anchor="mm", alpha=p)
        text(d, (1020 + dx, y + 49), str(sb), 72, WHITE, anchor="mm", alpha=p)
        text(d, (1520 + dx, y + 49), "WIN" if won else "LOSS", 34, YELLOW if won else LOSS, anchor="rm", alpha=p, tracking=3)


def faze_counter(img, t, t_on, n, flip_t=None):
    """Corner counter FAZE · n FINALS · 0 TITLES (flips from n-1 to n at flip_t)."""
    if t < t_on:
        return
    val = n if flip_t is None or t >= flip_t else n - 1
    block_text(img, (W - 680, 60), f"FAZE  ·  {val} FINALS  ·  0 TITLES", 38, WHITE, (222, 36, 48), a=ramp(t, t_on, 0.25))
    if flip_t is not None:
        flash(img, t, flip_t, dur=0.2, strength=0.3)


def score_race(img, d, t, t_on, a_key, b_key, sa, sb, dur, y=500):
    badge(img, 560, y - 260, a_key, h=90, anchor="m")
    badge(img, 1360, y - 260, b_key, h=90, anchor="m")
    p = ease((t - t_on) / dur) if t >= t_on else 0
    text(d, (760, y), str(int(round(sa * p))), 240, YELLOW if (p >= 1 and sa > sb) else WHITE, anchor="mm")
    text(d, (W / 2, y), "–", 150, MUTED, anchor="mm")
    text(d, (1160, y), str(int(round(sb * p))), 240, YELLOW if (p >= 1 and sb > sa) else WHITE, anchor="mm")


CHAPTERS = {
    "c1": dict(num="01", event="PGL MAJOR", city="COPENHAGEN", city_word="Copenhagen", date="MARCH 2024",
               tags=[("THE FIRST CS2 MAJOR", "first")], bgfx=("C6", 41.5, 5.0)),
    "c2": dict(num="02", event="PERFECT WORLD MAJOR", city="SHANGHAI", city_word="Shanghai", date="DECEMBER 2024",
               tags=[], bgfx=("S3", 30.0, 4.0)),
    "c3": dict(num="03", event="BLAST.tv MAJOR", city="AUSTIN", city_word="Austin", date="JUNE 2025",
               tags=[("THE FIRST 32-TEAM MAJOR", "32-team")], bgfx=("A2", 36.0, 6.0)),
    "c4": dict(num="04", event="STARLADDER MAJOR", city="BUDAPEST", city_word="Budapest", date="DECEMBER 2025",
               tags=[], bgfx=("B4", 30.5, 4.0)),
    "c5": dict(num="05", event="IEM MAJOR", city="COLOGNE", city_word="Cologne", date="JUNE 2026",
               tags=[], bgfx=("K8all", 60.5, 2.5)),
}


def chapter_cfg(cid):
    cfg = dict(CHAPTERS[cid])
    c, st, du = cfg["bgfx"]
    cfg["bgfx"] = clip(c, st, du, (1.05, 1.15))
    return cfg


def box_before(t_end):
    return lambda tt: "Box" if tt < t_end else "Low"


def box_after(t_start):
    return lambda tt: "Box" if tt >= t_start else "Low"


# ---------- Copenhagen ----------
def c1a():
    lead = 0.15
    w = Words("p09", lead)
    cfg = chapter_cfg("c1")
    t_ud, t_sf, t_ng = w("Two"), w("Spirit"), w("Then")
    stages = ["OPENING STAGE", "ELIMINATION STAGE", "QUARTER-FINALS"]

    def draw(img, t):
        if t < t_ud - 0.1:
            chapter_card(img, t, cfg, w)
            return
        if t < t_sf - 0.1:
            stage_path(img, t, stages, [("ef", 0, 2, w("Eternal")), ("c9", 0, 2, w("Cloud9"))], t_ud - 0.1,
                       title_s="FROM THE VERY FIRST STAGE")
            return
        d = ImageDraw.Draw(img)
        title(d, "QUARTER-FINAL  ·  TWO OVERTIMES" if t < t_ng - 0.1 else "SEMI-FINAL  ·  OVERTIME AGAIN", t, t_sf - 0.1)
        series_card(img, t, t_sf - 0.05, "spirit", "faze", [("MIRAGE", 7, 13, False, t_sf + 0.2), ("NUKE", 19, 16, True, w("overtime", 0)),
                    ("VERTIGO", 14, 16, True, w("twice"))], 110, 230, note="FAZE SURVIVE", note_t=w("survived"))
        series_card(img, t, t_ng, "navi", "g2", [("ANUBIS", 16, 13, True, w("sixteen-thirteen") - 0.3)], 1050, 230)

    sfx = [(w("Copenhagen") - 0.05, "stinger-hit-short", -6), (t_ud, "whoosh-soft", -12), (w("Eternal"), "riser-short-2s", -16),
           (t_sf, "whoosh-short", -10), (w("overtime", 0), "pop-1", -8), (w("twice"), "pop-1", -8), (w("survived"), "stamp-thud", -6),
           (t_ng, "slide-1", -10), (w("sixteen-thirteen") - 0.3, "pop-2", -8)]
    render_section("c1a", "p09", draw, sfx=sfx, lead=lead, caption_style="Low")


def c1b():
    lead = 0.15
    w = Words("p10", lead)
    t_ch, t_mvp = w("champions"), w("MVP:")
    jl = clip("C1", 32.7, 2.2, (1.0, 1.12), (0.45, 0.45))

    def draw(img, t):
        if t >= t_mvp - 0.1:
            mvp_card(img, t, t_mvp - 0.1, jl, "jL", "NAVI  ·  PGL MAJOR COPENHAGEN 2024")
            return
        final_board(img, t, 0.1, "navi", "faze", [("ANCIENT", 13, 9, w("Ancient"), False), ("MIRAGE", 2, 13, w("thirteen", 0), True),
                                                   ("INFERNO", 13, 3, w("thirteen", 1), False)])
        if t >= w("three"):
            block_text(img, (W / 2, 720), "NAVI WIN 2–1", 56, INK, YELLOW, a=ramp(t, w("three"), 0.2), anchor="m")
        stamp(img, "CHAMPIONS", W / 2, 880, t, t_ch, col=YELLOW, size=80, angle=-3)

    sfx = [(0.1, "whoosh-soft", -12), (w("Ancient"), "pop-1", -8), (w("thirteen", 0), "dry-thud", -3), (w("thirteen", 1), "pop-2", -6),
           (t_ch, "stinger-win-brass", -10), (t_mvp - 0.1, "stinger-hit-short", -6)]
    render_section("c1b", "p10", draw, sfx=sfx, lead=lead, tail=0.6, caption_style="Low")


# ---------- Shanghai ----------
def c2a():
    lead = 0.15
    w = Words("p11", lead)
    cfg = chapter_cfg("c2")
    t_ud, t_g2 = w("The MongolZ"), w("G2")
    stages = ["OPENING STAGE", "ELIMINATION STAGE", "QUARTER-FINALS"]

    def draw(img, t):
        if t < t_ud - 0.1:
            chapter_card(img, t, cfg, w)
            return
        if t < t_g2 - 0.1:
            stage_path(img, t, stages, [("mongolz", 0, 2, w("The MongolZ")), ("tl", 0, 2, w("Liquid"))], t_ud - 0.1,
                       title_s="ALL THE WAY UP")
            return
        d = ImageDraw.Draw(img)
        title(d, "SEMI-FINAL  ·  NUKE", t, t_g2 - 0.1)
        score_race(img, d, t, w("Nuke"), "g2", "faze", 14, 16, 1.2, y=560)
        if t >= w("overtime"):
            block_text(img, (W / 2, 720), "OVERTIME", 56, INK, YELLOW, a=ramp(t, w("overtime"), 0.2), anchor="m")
        if t >= w("final"):
            block_text(img, (W / 2, 840), "FAZE TO ANOTHER FINAL", 50, WHITE, (222, 36, 48), a=ramp(t, w("final"), 0.2), anchor="m")

    sfx = [(w("Shanghai") - 0.05, "stinger-hit-short", -6), (t_ud, "riser-short-2s", -16), (t_g2, "whoosh-short", -10),
           (w("Nuke"), "clock-tick", -10), (w("sixteen-fourteen"), "stamp-thud", -5), (w("final"), "pop-2", -8)]
    render_section("c2a", "p11", draw, sfx=sfx, lead=lead, caption_style="Low")


def c2b():
    lead = 0.15
    w = Words("p12", lead)
    t_fz, t_mvp = w("FaZe", 1), w("MVP", 0)
    donk = clip("S1", 42.0, 1.9, (1.0, 1.12), (0.4, 0.4))

    def draw(img, t):
        if t >= t_mvp - 0.1:
            mvp_card(img, t, t_mvp - 0.1, donk, "donk", "YOUNGEST & HIGHEST-RATED MAJOR MVP  ·  HLTV")
            return
        final_board(img, t, 0.1, "spirit", "faze", [("NUKE", 13, 8, w("Nuke"), False), ("ANCIENT", 6, 13, w("Ancient"), True),
                                                     ("DUST II", 13, 11, w("thirteen-eleven"), False)])
        stamp(img, "CHAMPIONS", W / 2, 780, t, w("thirteen-eleven") + 0.3, col=YELLOW, size=80, angle=-3)
        faze_counter(img, t, t_fz, 2)

    sfx = [(0.1, "whoosh-soft", -12), (w("Nuke"), "pop-1", -8), (w("Ancient"), "dry-thud", -4), (w("Dust II"), "riser-short-2s", -16),
           (w("thirteen-eleven"), "stinger-win-brass", -10), (t_fz, "stamp-thud", -6), (t_mvp - 0.1, "stinger-hit-short", -6)]
    render_section("c2b", "p12", draw, sfx=sfx, lead=lead, tail=0.6, caption_style="Low")


# ---------- Austin ----------
def c3a():
    lead = 0.15
    w = Words("p13", lead)
    cfg = chapter_cfg("c3")
    t_pain, t_sp = w("paiN"), w("Spirit", 0)
    stages = ["STAGE 2", "STAGE 3", "QUARTER-FINAL", "SEMI-FINAL"]

    def draw(img, t):
        if t < t_pain - 0.1:
            chapter_card(img, t, cfg, w)
            return
        if t < t_sp - 0.1:
            stage_path(img, t, stages, [("pain", 0, 3, t_pain)], t_pain - 0.1, title_s="paiN's RUN")
            series_card(img, t, w("knocked"), "pain", "furia", [("INFERNO", 16, 12, True, w("overtime"))], 580, 640, w_=760)
            return
        d = ImageDraw.Draw(img)
        title(d, "QUARTER-FINAL  ·  MIRAGE", t, t_sp - 0.1)
        score_race(img, d, t, w("played"), "spirit", "mouz", 25, 21, 1.6)
        if t >= w("forty-six"):
            block_text(img, (W / 2, 660), "46 ROUNDS", 56, INK, YELLOW, a=ramp(t, w("forty-six"), 0.2), anchor="m")
        stamp(img, "SERIES LOST 1–2", W / 2, 840, t, w("still"), size=80, angle=-4)

    sfx = [(w("Austin") - 0.05, "stinger-hit-short", -6), (t_pain, "riser-short-2s", -16), (w("overtime"), "pop-2", -8),
           (t_sp, "whoosh-short", -10), (w("played"), "clock-tick", -10), (w("still"), "stamp-thud", -4)]
    render_section("c3a", "p13", draw, sfx=sfx, lead=lead, caption_style="Low")


def c3b():
    lead = 0.15
    w = Words("p14", lead)
    t_ropz, t_mvp = w("ropz"), w("MVP")
    zy = clip("B5", 39.0, 1.9, (1.0, 1.12))

    def draw(img, t):
        if t >= t_mvp - 0.1:
            mvp_card(img, t, t_mvp - 0.1, zy, "ZywOo", "VITALITY  ·  BLAST.tv AUSTIN MAJOR 2025")
            return
        d = ImageDraw.Draw(img)
        if t >= t_ropz - 0.1:
            title(d, "ropz", t, t_ropz - 0.1, size=60)
            badge(img, 520, 420, "faze", h=110, a=ramp(t, w("left"), 0.3), anchor="m")
            p = ramp(t, w("His"), 0.4)
            d.line([(720, 475), (720 + 400 * p, 475)], fill=YELLOW, width=12)
            if p > 0.9:
                d.polygon([(1120, 445), (1170, 475), (1120, 505)], fill=YELLOW)
            badge(img, 1400, 420, "vit", h=110, a=ramp(t, w("His") + 0.3, 0.3), anchor="m")
            block_text(img, (W / 2, 640), "FIRST MAJOR WITH VITALITY  ·  FIRST ATTEMPT", 50, INK, YELLOW, a=ramp(t, w("attempt"), 0.25), anchor="m")
            return
        final_board(img, t, 0.1, "vit", "mongolz", [("MIRAGE", 5, 13, w("five-thirteen"), True), ("DUST II", 13, 4, w("Thirteen-four"), False),
                                                   ("INFERNO", 13, 6, w("Thirteen-six"), False)])
        stamp(img, "CHAMPIONS", W / 2, 780, t, w("Thirteen-six") + 0.4, col=YELLOW, size=80, angle=-3)

    sfx = [(0.1, "whoosh-soft", -12), (w("five-thirteen"), "dry-thud", -4), (w("Thirteen-four"), "pop-1", -8), (w("Thirteen-six"), "stinger-win-brass", -10),
           (t_ropz - 0.1, "whoosh-short", -10), (w("His"), "slide-2", -10), (w("attempt"), "pop-2", -8), (t_mvp - 0.1, "stinger-hit-short", -6)]
    render_section("c3b", "p14", draw, sfx=sfx, lead=lead, tail=0.6, caption_style="Low")


# ---------- Budapest ----------
def c4a():
    lead = 0.15
    w = Words("p15", lead)
    cfg = chapter_cfg("c4")
    t_ud, t_vit = w("underdog"), w("Vitality")
    stages = ["STAGE 1", "STAGE 2", "STAGE 3", "QF", "SF", "FINAL"]

    def draw(img, t):
        if t < t_ud - 0.1:
            chapter_card(img, t, cfg, w)
            return
        if t < t_vit - 0.1:
            stage_path(img, t, stages, [("faze", 0, 5, w("fought"))], t_ud - 0.1, title_s="THE UNDERDOG STORY: FAZE")
            if t >= w("bottom"):
                block_text(img, (300, 700), "FROM THE VERY BOTTOM OF 32 TEAMS", 46, WHITE, INK, a=ramp(t, w("bottom"), 0.25))
            return
        d = ImageDraw.Draw(img)
        title(d, "SEMI-FINAL  ·  MIRAGE", t, t_vit - 0.1)
        series_card(img, t, t_vit, "vit", "spirit", [("MIRAGE", 19, 17, True, w("nineteen-seventeen"))], 580, 330, w_=760)

    sfx = [(w("Budapest") - 0.05, "stinger-hit-short", -6), (w("fought"), "riser-short-2s", -16), (t_vit, "whoosh-short", -10),
           (w("nineteen-seventeen"), "pop-2", -6)]
    render_section("c4a", "p15", draw, sfx=sfx, lead=lead, caption_style="Low")


def c4b():
    lead = 0.15
    w = Words("p16", lead)
    t_fz, t_mvp = w("FaZe", 1), w("MVP")
    zy = clip("B5", 28.0, 2.4, (1.0, 1.1))

    def draw(img, t):
        if t >= t_mvp - 0.2:
            mvp_card(img, t, t_mvp - 0.2, zy, "ZywOo", "MVP AGAIN  ·  HIS THIRD MAJOR MVP")
            return
        final_board(img, t, 0.1, "vit", "faze", [("NUKE", 6, 13, w("first"), False), ("DUST II", 13, 3, w("three"), False),
                                                 ("INFERNO", 13, 9, w("three") + 0.25, False), ("OVERPASS", 13, 2, w("thirteen-two"), False)],
                    label="GRAND FINAL  ·  BEST OF FIVE")
        stamp(img, "BACK-TO-BACK", W / 2, 920, t, w("back-to-back"), col=YELLOW, size=66, angle=-3)
        faze_counter(img, t, t_fz, 3, flip_t=w("three", 1))

    sfx = [(0.1, "whoosh-soft", -12), (w("first"), "dry-thud", -4), (w("three"), "pop-1", -8), (w("thirteen-two"), "pop-2", -6),
           (w("back-to-back"), "stinger-win-brass", -10), (w("three", 1), "stamp-thud", -5), (t_mvp - 0.2, "stinger-hit-short", -6)]
    render_section("c4b", "p16", draw, sfx=sfx, lead=lead, tail=0.6, caption_style="Low")


# ---------- Cologne ----------
def c5a():
    lead = 0.15
    w = Words("p17", lead)
    cfg = chapter_cfg("c5")
    t_ud, t_sp = w("BetBoom"), w("Spirit")

    def draw(img, t):
        if t < t_ud - 0.1:
            chapter_card(img, t, cfg, w)
            return
        if t < t_sp - 0.1:
            stage_path(img, t, ["STAGE 1", "STAGE 2", "STAGE 3", "QUARTER-FINALS"],
                       [("betboom", 0, 3, w("BetBoom")), ("9z", 1, 3, w("9z"))], t_ud - 0.1, title_s="THE LONG SHOTS")
            return
        d = ImageDraw.Draw(img)
        title(d, "LONGEST MAP OF THE CS2 ERA", t, t_sp - 0.1)
        score_race(img, d, t, w("played"), "spirit", "g2", 25, 22, 2.4)
        if t >= w("forty-seven"):
            block_text(img, (W / 2, 660), "47 ROUNDS  ·  MIRAGE", 60, INK, YELLOW, a=ramp(t, w("forty-seven"), 0.2), anchor="m")
        if t >= w("after"):
            block_text(img, (W / 2, 800), "AFTER DUST II 16–14 IN OVERTIME", 44, WHITE, INK, a=ramp(t, w("after"), 0.2), anchor="m")

    sfx = [(w("Cologne") - 0.05, "stinger-hit-short", -6), (t_ud, "riser-short-2s", -16), (t_sp, "whoosh-short", -10),
           (w("played"), "clock-tick", -10), (w("forty-seven"), "stamp-thud", -5), (w("after"), "pop-1", -10)]
    render_section("c5a", "p17", draw, sfx=sfx, lead=lead, caption_style="Low")


def c5b():
    lead = 0.15
    w = Words("p18", lead)
    t_fin, t_k, t_mvp = w("In", 0), w("karrigan"), w("MVP:")
    eights = [w("Thirteen-eight.", k) for k in range(3)]
    mon = clip("K2", 22.0, 2.6, (1.0, 1.1), (0.4, 0.45))

    def draw(img, t):
        if t >= t_mvp - 0.1:
            mvp_card(img, t, t_mvp - 0.1, mon, "m0NESY", "FALCONS  ·  IEM COLOGNE MAJOR 2026")
            return
        d = ImageDraw.Draw(img)
        if t >= t_k - 0.1:
            title(d, "karrigan", t, t_k - 0.1, size=60)
            for k, ev in enumerate(["COPENHAGEN 2024", "SHANGHAI 2024", "BUDAPEST 2025"]):
                a = ramp(t, w("lost") + k * 0.15, 0.25)
                x = 140 + k * 430
                rrect(d, (x, 300, x + 390, 470), 16, fill=fade((60, 26, 30), a), outline=fade(LOSS, a), width=3)
                text(d, (x + 195, 350), ev, 30, MUTED, anchor="mm", alpha=a, tracking=2)
                text(d, (x + 195, 420), "FINAL LOST · FAZE", 34, LOSS, anchor="mm", alpha=a)
            a = ramp(t, w("signed"), 0.3)
            if a > 0:
                x = 140 + 3 * 430
                rrect(d, (x, 300 - 20 * (1 - a), x + 390, 470), 16, fill=YELLOW)
                text(d, (x + 195, 350), "COLOGNE 2026", 30, INK, anchor="mm", tracking=2)
                text(d, (x + 195, 420), "CHAMPION · FALCONS", 34, INK, anchor="mm")
            block_text(img, (140, 560), "JOINED FALCONS TWO MONTHS BEFORE", 46, WHITE, (0, 156, 96), a=ramp(t, w("signed"), 0.25))
            return
        if t < t_fin - 0.1:
            title(d, "FALCONS' PLAYOFF ROAD", t, 0.1)
            series_card(img, t, 0.2, "falcons", "vit", [("QUARTER-FINAL", 2, 1, False, w("Vitality"))], 110, 260, w_=760)
            series_card(img, t, w("Spirit") - 0.1, "falcons", "spirit", [("SEMI-FINAL", 2, 1, False, w("Spirit")),
                        ("OT MAPS", 2, 0, True, w("overtimes"))], 1050, 260, w_=760)
            return
        title(d, "GRAND FINAL  ·  FALCONS 3–0 FURIA", t, t_fin - 0.1)
        for k, (m, tk) in enumerate(zip(["MIRAGE", "ANUBIS", "INFERNO"], eights)):
            if t < tk:
                continue
            p = ease((t - tk) / 0.18)
            x = 170 + k * 540
            rrect(d, (x, 330, x + 480, 720), 22, fill=(0, 156, 96))
            text(d, (x + 240, 400), m, 44, WHITE, anchor="mm", tracking=3)
            text(d, (x + 240, 560), "13–8", int(150 * (1.15 - 0.15 * p)), WHITE, anchor="mm")
        if t >= w("drop"):
            block_text(img, (W / 2, 800), "NOT A SINGLE MAP DROPPED", 50, INK, YELLOW, a=ramp(t, w("drop"), 0.2), anchor="m")

    sfx = [(0.1, "whoosh-soft", -12), (w("Vitality"), "pop-1", -10), (w("overtimes"), "pop-1", -10), (t_fin - 0.1, "whoosh-short", -10)] + \
          [(x, "stamp-thud", -5) for x in eights] + [(t_k - 0.1, "whoosh-short", -10), (w("signed"), "stinger-win-brass", -10),
          (t_mvp - 0.1, "stinger-hit-short", -6)]
    render_section("c5b", "p18", draw, sfx=sfx, lead=lead, tail=0.6, caption_style="Low")


if __name__ == "__main__":
    import sys as _s
    for sid in (_s.argv[1:] or ["c1a", "c1b", "c2a", "c2b", "c3a", "c3b", "c4a", "c4b", "c5a", "c5b"]):
        globals()[sid]()
