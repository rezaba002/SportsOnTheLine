"""Video 04 sections ("Do pistol rounds decide CS2?"). python sections4.py s00 [s01 ...] -> clips/<id>.mp4

Every number comes from D:\\Research\\cs2-pistols\\results\\NUMBERS.md. Rapid-edit rules: a cut or a visual hit every
1.5–3 s, CS2 interface motifs (kill feed, hitmarkers, money HUD, round history, bomb timer, scope), no slow board
right after a peak, no leak of the #1 (donk) before the countdown reveal.
"""
import functools, math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path[:0] = [r"D:\Youtube\video04\work", r"D:\Youtube\video02\work"]
from engine import *                    # noqa: F401,F403
import fx
import timeline as TL
import v2                               # logos (assets/logos) + rotating sfx pools

FOOT2 = r"D:\Youtube\video02\footage\clips"
FOOT4 = r"D:\Youtube\video04\footage"
INK = (12, 12, 14)
logo = v2.logo


class Src:
    """Source frames at 60 fps for a short span (smooth slow motion), indexed by source time."""

    def __init__(self, path, a, b, fps=60):
        self.path, self.a, self.b, self.fps, self.frames = path, a, b, fps, None

    def frame(self, t):
        if self.frames is None:
            raw = subprocess.run([FFMPEG, "-v", "error", "-ss", f"{self.a:.3f}", "-t", f"{self.b - self.a + 0.1:.3f}", "-i", self.path,
                                  "-vf", f"fps={self.fps},scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                 capture_output=True, check=True).stdout
            k = len(raw) // (W * H * 3)
            self.frames = np.frombuffer(raw[:k * W * H * 3], np.uint8).reshape(k, H, W, 3)
        i = int(round((t - self.a) * self.fps))
        return Image.fromarray(self.frames[min(max(i, 0), len(self.frames) - 1)])


def wt(sch, pid, word, nth=0, end=False):
    hits = [w for w in NAR[pid]["words"] if core(w["w"]) == core(word)]
    return sch[pid][0] + hits[nth]["e" if end else "s"]


def sub(img, s, t, t_on, y=860, size=64, col=WHITE, bg=INK, t_off=None):
    """Speaker subtitle on a solid block (centre)."""
    if t < t_on or (t_off is not None and t > t_off):
        return
    block_text(img, (W / 2, y), s, size, col, bg, a=ease((t - t_on) / 0.12), anchor="m")


def tag(img, s, x=60, y=50):
    block_text(img, (x, y), s, 30, WHITE, INK, a=1.0, pad=(16, 10))


# ---------- S00: hook ----------
def s00():
    donk = FOOT4 + r"\donk_tldr_remove_pistols.mkv"
    segs = [{"nar": "h01", "gap": 0.55},
            {"clip": "donkA", "src": donk, "in": 8.15, "out": 12.25, "gain": 0, "gap": 0.0},
            {"nar": "h02", "gap": 0.0},
            {"clip": "donkB", "src": donk, "in": 16.85, "out": 20.05, "gain": 0, "gap": 0.05},
            {"nar": "h03", "gap": 0.1}]
    sch, _ = TL.schedule(segs)
    t_pistol = wt(sch, "h01", "pistol.")
    # ZywOo's round-13 pistol (Budapest final, B5): his 3rd kill (src 12.25) lands on "pistol"
    zy = Src(FOOT2 + r"\B5.mp4", 7.0, 14.5)
    src_at = lambda t: 12.25 - (t_pistol - t) if t < t_pistol else fx.speed_ramp(t - t_pistol, 0.25, 0.5, 0.35) + 12.25
    kills_src = [9.15, 11.15, 12.25]
    kills_out = [t_pistol - (12.25 - k) for k in kills_src]
    feed = [(kills_out[0], "ZywOo", "USP-S", "Twistzz", False), (kills_out[1], "ZywOo", "USP-S", "karrigan", False),
            (kills_out[2], "ZywOo", "USP-S", "jcobbb", True)]
    dk = Src(donk, 8.0, 20.2, fps=30)
    t_ans = sch["donkA"][0] + (10.45 - 8.15)
    majors = ["COPENHAGEN 2024", "SHANGHAI 2024", "AUSTIN 2025", "BUDAPEST 2025", "COLOGNE 2026"]
    t_maj = wt(sch, "h03", "every", 1)
    t_379, t_758, t_right = wt(sch, "h03", "three"), wt(sch, "h03", "Seven"), wt(sch, "h03", "Is")

    def draw(img, t, sch):
        a0, a1 = sch["h01"]
        if t < sch["donkA"][0]:                                           # ZywOo pistol, $800, "A pistol."
            fr = zy.frame(src_at(t))
            fr = fx.vignette_pulse(fr, 0.35)
            for k in kills_out:
                fr = fx.punch(fr, t, k, 0.07)
                fr = fx.flash(fr, t, k, 0.06, 0.35)
            fr = fx.punch(fr, t, wt(sch, "h01", "Ten"), 0.05)
            d0 = ImageDraw.Draw(fr, "RGBA"); d0.rectangle([0, 0, 760, 260], fill=(0, 0, 0, 150))
            fx.killfeed(fr, feed, t, y0=150)
            for i, k in enumerate(kills_out):
                fx.hitmarker(fr, W / 2, H / 2, t, k, hs=(i == 2))
            if t >= wt(sch, "h01", "Eight"):
                fx.money(fr, 90, 940, 800, t, wt(sch, "h01", "Eight"), frm=0, dur=0.5)
            if t >= wt(sch, "h01", "Ten"):
                fx.word_pop(fr, "10 PLAYERS", 110, 160, t, wt(sch, "h01", "Ten"), size=70, anchor="lm")
            if t >= t_pistol - 0.05:
                fx.word_pop(fr, "A PISTOL.", W / 2, 380, t, t_pistol - 0.05, size=170, col=YELLOW)
            tag(fr, "ZywOo · BUDAPEST MAJOR FINAL · ROUND 13", y=990)
            return fr
        if t < sch["h02"][0]:                                             # donk: "Remove pistol rounds."
            fr = dk.frame(8.15 + (t - sch["donkA"][0]))
            fr = fx.punch(fr, t, t_ans, 0.12, 0.2)
            fr = fx.glitch_at(fr, t, t_ans, 0.2, 30)
            fr = fx.flash(fr, t, sch["donkA"][0], 0.08, 0.6)
            tag(fr, "donk · TL;DR on CS2 · Oct 2026")
            sub(fr, "“If you could make one change to CS…”", t, sch["donkA"][0], y=900, size=50, t_off=t_ans - 0.05)
            if t >= t_ans:
                block_text(fr, (W / 2, 820), "“REMOVE PISTOL ROUNDS.”", 110, INK, YELLOW, a=ease((t - t_ans) / 0.1), anchor="m", pad=(40, 22))
            return fr
        if t < sch["donkB"][0]:                                           # freeze: the most dominant player
            fr = dk.frame(12.2)
            g = fr.convert("L").convert("RGB")
            fr = Image.blend(g, fr, 0.35)
            fr = fx.punch(fr, t, sch["h02"][0], 0.05)
            side_shade(fr, 1.0, frac=0.7)
            fx.word_pop(fr, "donk", 120, 380, t, sch["h02"][0] + 0.05, size=180, anchor="lm")
            logo(fr, 125, 500, "spirit", h=60, wmax=330)
            chips = [("LEADS 12 OF 25 HLTV CATEGORIES", wt(sch, "h02", "dominant")), ("MAJOR MVP · SHANGHAI 2024", wt(sch, "h02", "era"))]
            for i, (s, at) in enumerate(chips):
                if t >= at:
                    block_text(fr, (125, 640 + i * 100), s, 44, INK if i == 0 else WHITE, YELLOW if i == 0 else INK, a=ease((t - at) / 0.12))
            return fr
        if t < sch["h03"][0]:                                             # donk: "too important and too random"
            fr = dk.frame(16.85 + (t - sch["donkB"][0]))
            fr = fx.flash(fr, t, sch["donkB"][0], 0.08, 0.5)
            tag(fr, "donk · TL;DR on CS2 · Oct 2026")
            sub(fr, "“…too important and too random…”", t, sch["donkB"][0] + 0.1, y=840, size=76, col=INK, bg=YELLOW)
            return fr
        # h03: every Major, 379 maps, 758 pistols, "Is he right?"
        d = ImageDraw.Draw(img)
        if t < t_right - 0.05:
            # 758 pistol-round tiles filling fast in the background (half won = green, half lost = red)
            k = int(758 * ease((t - sch["h03"][0]) / 2.6))
            for j in range(k):
                cx, cy = 60 + (j % 54) * 33, 330 + (j // 54) * 33
                d.rectangle([cx, cy, cx + 24, cy + 24], fill=(52, 120, 76) if (j * 7) % 2 else (130, 44, 44))
            if k:
                d.rectangle([0, 320, W, 820], fill=None)
                img = Image.blend(img, Image.new("RGB", (W, H), (14, 17, 23)), 0.55 if t >= t_379 - 0.1 else 0.15)
                d = ImageDraw.Draw(img)
            for i, m in enumerate(majors):
                at = t_maj + i * 0.14
                if t >= at:
                    x = 70 + i * 362
                    p = ease((t - at) / 0.15)
                    d.rounded_rectangle([x, 120 + 40 * (1 - p), x + 340, 280 + 40 * (1 - p)], 16, fill=(26, 30, 40), outline=YELLOW, width=4)
                    city, yr = m.split()
                    d.text((x + 170, 180 + 40 * (1 - p)), city, font=font(44), fill=WHITE, anchor="mm")
                    d.text((x + 170, 238 + 40 * (1 - p)), yr, font=font(34, "SemiBold"), fill=YELLOW, anchor="mm")
            if t >= t_379 - 0.1:
                v = 379 * ease((t - t_379 + 0.1) / 0.7)
                fx.word_pop(img, f"{int(v)}", 520, 560, t, t_379 - 0.1, size=210, col=WHITE)
                d.text((520, 690), "MAPS · LAST 16 TEAMS", font=font(40), fill=MUTED, anchor="mm")
            if t >= t_758 - 0.1:
                v = 758 * ease((t - t_758 + 0.1) / 0.7)
                fx.word_pop(img, f"{int(v)}", 1400, 560, t, t_758 - 0.1, size=210, col=YELLOW)
                d.text((1400, 690), "PISTOL ROUNDS", font=font(40), fill=MUTED, anchor="mm")
                # a fast-scrolling feed of pistol results
                k = int((t - t_758) * 14)
                names = ["NAVI", "Spirit", "FaZe", "Vitality", "MOUZ", "G2", "Falcons", "FURIA", "MongolZ", "9z"]
                feed2 = [(t_758 + j / 14, names[j % 10], "USP-S" if j % 2 else "Glock-18", names[(j * 3 + 1) % 10], False) for j in range(k + 1)]
                fx.killfeed(img, feed2, t, y0=740, maxn=3)
            return img
        img = fx.flash(img, t, t_right - 0.05, 0.1, 0.7)
        d = ImageDraw.Draw(img)
        fx.word_pop(img, "DO PISTOLS", W / 2, 430, t, t_right - 0.05, size=150)
        fx.word_pop(img, "DECIDE CS2?", W / 2, 600, t, t_right + 0.12, size=170, col=YELLOW)
        img = fx.glitch_at(img, t, t_right + 0.12, 0.22, 34)
        return img

    sfx = [(k, "hitmarker", -6) for k in kills_out] + [(kills_out[2], "headshot-ding", -6), (wt(sch, "h01", "Eight"), "cash-register-cha-ching", -14),
           (t_pistol - 0.05, "bass-hit", -6), (sch["donkA"][0], "glitch-burst", -12), (t_ans, "sub-drop", -8),
           (sch["h02"][0], "whoosh-short", -12), (sch["donkB"][0], "glitch-soft-1", -12), (sch["h03"][0], "whoosh-medium-1s", -12)] + \
          [(t_maj + i * 0.14, "feed-tick", -8) for i in range(5)] + [(t_379 - 0.1, "stamp-thud", -8), (t_758 - 0.1, "stamp-thud", -8)] + \
          [(t_758 + j / 14, "feed-tick", -18) for j in range(0, 12, 2)] + [(t_right - 0.05, "stinger-energetic-hit", -7), (t_right + 0.12, "glitch-burst", -10)]
    TL.render("s00", segs, draw, sfx=sfx, tail=1.4, caption_style=lambda tt: "Box" if tt < sch["h02"][0] else "Low")


if __name__ == "__main__":
    for sid in sys.argv[1:]:
        globals()[sid]()
