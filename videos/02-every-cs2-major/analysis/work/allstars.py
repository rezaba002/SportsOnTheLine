"""Video 02 all-star part (p19–p22): a00 intro, a01 Team 1 (gold), a02 Team 2 (silver), a03 question + Singapore.
Run through sections.py."""
from sections import *     # noqa: F401,F403
from chapters import faze_counter

TEAM1 = [  # role, name, badge, word that names him, chips (text, word that triggers it)
    ("IN-GAME LEADER", "apEX", "vit", "apEX.", [("2 CS2 MAJORS AS CAPTAIN", "lift")]),
    ("AWP", "ZywOo", "vit", "ZywOo.", [("MVP OF BOTH VITALITY TITLES", "both"), ("#1 KAST  ·  #1 DMG DIFF", "KAST")]),
    ("STAR RIFLER", "donk", "spirit", "donk.", [("LEADS 12 OF 25 CATEGORIES", "Twelve"), ("RATING 1.49", "categories.")]),
    ("RIFLER", "jL", "navi", "jL.", [("MAJOR TITLE  ·  MAJOR MVP", "title,"), ("FANS' PICK", "fans'")]),
    ("ANCHOR", "ropz", "vit", "ropz.", [("4 FINALS  ·  2 TITLES", "Four"), ("#1 PLAYOFF CLUTCHES", "clutches")]),
]
TEAM2 = [
    ("IN-GAME LEADER", "karrigan", "falcons", "karrigan,", [("4 FINALS", "four"), ("MOST ASSISTS  ·  MOST MAPS", "assists")]),
    ("AWP", "m0NESY", "falcons", "m0NESY", [("MOST AWP KILLS  ·  511", "kills,"), ("COLOGNE MVP", "MVP.")]),
    ("STAR RIFLER", "NiKo", "falcons", "NiKo:", [("COLOGNE CHAMPION", "champion,"), ("ELITE CT SIDE", "CT-sides")]),
    ("RIFLER", "frozen", "faze", "frozen:", [("MOST CLUTCHES  ·  28", "clutches"), ("2nd IN KILLS", "second")]),
    ("ANCHOR", "b1t", "navi", "b1t,", [("COPENHAGEN CHAMPION", "Copenhagen"), ("MAUISNAKE: TOP-2 ANCHOR AFTER ropz", "Mauisnake,")]),
]


def split2(s):
    """Split a chip label into two lines at the space nearest the middle."""
    sp = [i for i, c in enumerate(s) if c == " "]
    i = min(sp, key=lambda k: abs(k - len(s) / 2))
    return [s[:i].strip(" ·"), s[i + 1:].strip(" ·")]


def roster(img, t, w, team, col, y0=190, focus=True):
    """Five role cards in a row; each card lands on its name and collects stat chips on their words."""
    d = ImageDraw.Draw(img)
    on = [w(p[3]) for p in team]
    cur = max([i for i, x in enumerate(on) if t >= x - 0.1], default=-1)
    for i, (role, name, key, word, chips) in enumerate(team):
        x = 70 + i * 362
        t_on = on[i] - 0.1
        a = ramp(t, t_on, 0.25) if t >= t_on else 0
        lit = focus and i == cur
        # empty slot
        rrect(d, (x, y0, x + 340, y0 + 660), 20, fill=PANEL, outline=YELLOW if lit else LINE, width=5 if lit else 2)
        text(d, (x + 170, y0 + 44), role, 30, YELLOW if lit else MUTED, anchor="mm", tracking=3, bg=PANEL)
        if a <= 0:
            text(d, (x + 170, y0 + 300), "?", 160, DIM, anchor="mm", bg=PANEL)
            continue
        sc = 1.25 - 0.25 * a
        size = 104
        while size > 50 and d.textlength(name, font=font(size)) > 300:
            size -= 4
        f = font(int(size * sc))
        d.text((x + 170, y0 + 180), name, font=f, fill=col, anchor="mm")
        badge(img, x + 170, y0 + 262, key, h=58, a=a, anchor="m")
        for k, (chip, cw) in enumerate(chips):
            try:
                tc = w(cw)
            except KeyError:
                tc = t_on + 0.6 + 0.5 * k
            if t >= tc:
                p = ease((t - tc) / 0.2)
                cy = y0 + 380 + k * 128
                fsz = 30 if len(chip) <= 20 else 25
                rrect(d, (x + 14, cy - 10 * (1 - p), x + 326, cy + 104 - 10 * (1 - p)), 10, fill=col if k == 0 else INK,
                      outline=col, width=2)
                lines = [chip] if d.textlength(chip, font=font(fsz)) < 290 else split2(chip)
                fsz = fsz if len(lines) == 1 else 24
                for li, ln in enumerate(lines):
                    yy = cy + 52 + (li - (len(lines) - 1) / 2) * 32
                    d.text((x + 170, yy - 10 * (1 - p)), ln, font=font(fsz), fill=INK if k == 0 else col, anchor="mm")


def a00():
    lead = 0.15
    w = Words("p19", lead)
    cuts = [(0.0, clip("C1", 33.0, 1.0, (1.0, 1.06))), (1.0, clip("S1", 42.2, 1.0, (1.0, 1.06))),
            (2.0, clip("B5", 39.2, 1.0, (1.0, 1.06))), (3.0, clip("K2", 22.2, 2.4, (1.0, 1.08)))]

    def draw(img, t):
        st, fx = [c for c in cuts if t >= c[0]][-1]
        show(img, fx, t - st, dim=0.35)
        flash(img, t, st, strength=0.45)
        if t >= w("all-star") - 0.1:
            kinetic(img, "THE ALL-STAR TEAM", t, w("all-star") - 0.1, y=470, size=140, col=INK, block=YELLOW)
            block_text(img, (W / 2, 620), "OF THE CS2 ERA", 60, WHITE, INK, a=ramp(t, w("era?"), 0.2), anchor="m")

    sfx = [(c[0], "whoosh-short", -12) for c in cuts] + [(w("all-star") - 0.1, "stinger-energetic-hit", -6)]
    render_section("a00", "p19", draw, sfx=sfx, lead=lead, tail=0.5, caption_style="Box")


def a01():
    lead = 0.15
    w = Words("p20", lead)

    def draw(img, t):
        d = ImageDraw.Draw(img)
        title(d, "TEAM 1  ·  THE ALL-STARS", t, 0.05)
        roster(img, t, w, TEAM1, YELLOW)
        if t >= w("No"):
            stamp(img, "NO DEBATE", 70 + 2 * 362 + 170, 905 - 20, t, w("No"), col=YELLOW, size=54, angle=-4)

    sfx = [(0.05, "whoosh-soft", -12)] + [(w(p[3]) - 0.1, "stamp-thud", -6) for p in TEAM1] + \
          [(w(c[1]), "pop-1", -12) for p in TEAM1 for c in p[4]] + [(w("No"), "stamp-thud", -4)]
    render_section("a01", "p20", draw, sfx=sfx, lead=lead, tail=0.6)


def a02():
    lead = 0.15
    w = Words("p21", lead)

    def draw(img, t):
        d = ImageDraw.Draw(img)
        title(d, "TEAM 2  ·  THE CHALLENGERS", t, 0.05, col=SILVER)
        roster(img, t, w, TEAM2, SILVER)
        if t >= w("frozen:"):
            block_text(img, (70 + 3 * 362, 905), "THE NUMBERS", 40, INK, SILVER, a=ramp(t, w("frozen:"), 0.2))
        if t >= w("Mauisnake,"):
            text(d, (W - 70, 1000), "Anchor tier list: Mauisnake (analyst opinion)", 26, MUTED, anchor="rm")

    sfx = [(0.05, "whoosh-soft", -12)] + [(w(p[3]) - 0.1, "stamp-thud", -6) for p in TEAM2]
    render_section("a02", "p21", draw, sfx=sfx, lead=lead, tail=0.6)


def a03():
    lead = 0.15
    w = Words("p22", lead)
    pairs = [("jL", "frozen", w("jL")), ("apEX", "karrigan", w("apEX")), ("ZywOo", "m0NESY", w("ZywOo"))]
    t_build, t_sg, t_fz, t_see = w("Build"), w("Singapore", 0), w("Will"), w("See")
    sg_fx = clip("A2", 36.5, 3.5, (1.0, 1.1))

    def draw(img, t):
        d = ImageDraw.Draw(img)
        if t < t_sg - 0.1:
            title(d, "WHICH ROLE DOES TEAM 2 WIN?", t, 0.1)
            for k, (a_, b_, tk) in enumerate(pairs):
                if t < tk - 0.05:
                    continue
                p = ease((t - tk + 0.05) / 0.2)
                y = 260 + k * 170
                text(d, (W / 2 - 160 - 60 * (1 - p), y + 60), a_, 96, YELLOW, anchor="rm")
                text(d, (W / 2 + 160 + 60 * (1 - p), y + 60), b_, 96, SILVER, anchor="lm")
                pulse = 1 + 0.12 * math.sin((t - tk) * 7)
                rrect(d, (W / 2 - 60 * pulse, y + 60 - 60 * pulse, W / 2 + 60 * pulse, y + 60 + 60 * pulse), 16, fill=WHITE)
                text(d, (W / 2, y + 62), "?", int(90 * pulse), INK, anchor="mm", bg=WHITE)
            if t >= t_build:
                block_text(img, (W / 2, 790), "BUILD YOUR ALL-STAR FIVE IN THE COMMENTS", 52, INK, YELLOW, a=ramp(t, t_build, 0.25), anchor="m")
            return
        show(img, sg_fx, min(t - t_sg, 3.4), dim=0.55, blur=3)
        side_shade(img, 1.0, frac=0.8)
        block_text(img, (110, 160), "NEXT", 44, INK, YELLOW, a=ramp(t, t_sg - 0.1, 0.2))
        sc = 1.3 - 0.3 * ease((t - t_sg) / 0.15)
        d.text((116, 348), "SINGAPORE", font=font(int(180 * sc)), fill=(0, 0, 0), anchor="lm")
        d.text((110, 340), "SINGAPORE", font=font(int(180 * sc)), fill=WHITE, anchor="lm")
        block_text(img, (114, 430), "PGL MAJOR  ·  25 NOV – 13 DEC 2026", 52, INK, YELLOW, a=ramp(t, w("twenty-fifth"), 0.25))
        block_text(img, (114, 525), "THE FIRST MAJOR IN SOUTHEAST ASIA", 44, WHITE, INK, a=ramp(t, w("Southeast"), 0.25))
        if t >= t_fz:
            faze_counter(img, t, t_fz, 3)
            block_text(img, (114, 615), "WILL FAZE FINALLY WIN A FINAL?", 50, WHITE, (222, 36, 48), a=ramp(t, t_fz, 0.25))
        if t >= w("someone"):
            block_text(img, (114, 710), "OR DOES SOMEONE NEW JOIN THE LIST?", 44, WHITE, INK, a=ramp(t, w("someone"), 0.25))

    sfx = [(0.1, "whoosh-soft", -12)] + [(tk - 0.05, "pop-1", -8) for _, _, tk in pairs] + [(t_build, "notification-2", -10),
          (t_sg - 0.1, "stinger-energetic-hit", -8), (t_fz, "stamp-thud", -6), (t_see, "swell-soft-3s", -12)]
    render_section("a03", "p22", draw, sfx=sfx, lead=lead, tail=1.0, caption_style="Low")


if __name__ == "__main__":
    import sys as _s
    for sid in (_s.argv[1:] or ["a00", "a01", "a02", "a03"]):
        globals()[sid]()
