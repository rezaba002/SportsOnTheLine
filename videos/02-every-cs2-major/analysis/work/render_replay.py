"""2D tactical replay of one round, drawn from the demo (no broadcast footage).

Test case: Cologne 2026 QF, G2 v Spirit, Mirage round 34 (OT2): magixx's 1v4 on B.
Output: work/replays/r34_magixx_1v4.mp4 (1280x720, 30 fps)

Timeline (game seconds after freeze end): card → setup at 3x → zoom to B + slow motion for the kills → freeze.
"""
import math, pathlib, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from awpy import Demo, data as awdata

HERE = pathlib.Path(__file__).parent
DEMO = HERE.parent / "demos" / "g2-vs-spirit-m3-mirage-p2.dem"
OUT = HERE / "replays" / "r34_magixx_1v4.mp4"
FF = r"EDIT_ME\ffmpeg\bin\ffmpeg.exe"
W, H, FPS, SS = 1280, 720, 30, 2          # output size; supersample factor for smooth shapes
ROUND, HERO = 34, "magixx"
SPIRIT = {"sh1ro", "zont1x", "magixx", "donk", "tN1R"}
T_COL, CT_COL = (236, 170, 60), (80, 160, 255)
BG, WHITE, MUTED, RED, GOLD = (12, 12, 15), (240, 238, 232), (140, 140, 150), (230, 60, 50), (255, 210, 0)
C4_TIME = 40.0

# ---------- data ----------
d = Demo(DEMO)
R = next(r for r in d.rounds.to_dicts() if r["round_num"] == ROUND)
T0 = R["freeze_end_tick"]
sec = lambda tick: (tick - T0) / 64.0
from demoparser2 import DemoParser                     # awpy's ticks() has no view angle; demoparser2 does
_tk = DemoParser(str(DEMO)).parse_ticks(["X", "Y", "yaw", "health", "name"], ticks=list(range(T0, R["end_tick"] + 64 * 3)))
_tk = _tk[_tk["name"].notna()]
pos = {}                                   # name -> (tick array, x, y, yaw, health)
for name, t in _tk.groupby("name"):
    t = t.sort_values("tick")
    pos[name] = tuple(t[c].to_numpy(dtype=float) for c in ("tick", "X", "Y", "yaw", "health"))
kills = [k for k in d.kills.sort("tick").to_dicts() if T0 <= k["tick"] <= R["end_tick"]]
plant = next(b for b in d.bomb.to_dicts() if b["event"] == "finish_plant" and T0 <= b["tick"] <= R["end_tick"])
smokes = [s for s in d.smokes.to_dicts() if s["end_tick"] >= T0 and s["start_tick"] <= R["end_tick"]]
fires = [f for f in d.fires.to_dicts() if f["end_tick"] >= T0 and f["start_tick"] <= R["end_tick"]]

hero_last_alone = max(sec(k["tick"]) for k in kills if k["victim_name"] in SPIRIT)      # sh1ro's death → 1v4
hero_kills = [sec(k["tick"]) for k in kills if k["attacker_name"] == HERO]
S_FAST0, S_SLOW0 = sec(plant["tick"]) - 2.5, hero_kills[0] - 0.6
S_END = hero_kills[-1] + 0.5

# ---------- map ----------
md = awdata.map_data()["de_mirage"]
radar = Image.open(awdata.radar_path("de_mirage")).convert("RGB")
gray = ImageEnhance.Contrast(ImageEnhance.Brightness(ImageEnhance.Color(radar).enhance(0.3)).enhance(1.0)).enhance(1.15)
tint = Image.new("RGB", radar.size, (20, 26, 38))
radar = Image.blend(gray, tint, 0.18)

def to_radar(x, y):
    return (x - md["pos_x"]) / md["scale"], (md["pos_y"] - y) / md["scale"]

# camera: (cx, cy, size) in radar pixels, square box shown in the map panel
FULL = (512, 512, 1024)
def _zoom_box():
    """Square around the hero and his opponents during the slow-motion part, with a margin."""
    pts = []
    for name in pos:
        if name != HERO and name in SPIRIT:
            continue
        tk, x, y, yaw, hp = pos[name]
        m = (tk >= T0 + S_SLOW0 * 64) & (tk <= T0 + S_END * 64) & (hp > 0)
        pts += [to_radar(a, b) for a, b in zip(x[m], y[m])]
    pts.append(to_radar(plant["x"], plant["y"]))
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    size = max(max(xs) - min(xs), max(ys) - min(ys)) * 1.35 + 60
    return ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, max(size, 260))
def lerp(a, b, u):
    return tuple(p + (q - p) * u for p, q in zip(a, b))

def ease(u):
    u = min(max(u, 0), 1); return u * u * (3 - 2 * u)

# ---------- timeline: output time -> game time ----------
CARD = 1.6
segments = [("card", CARD, S_FAST0, S_FAST0), ("fast", (S_SLOW0 - S_FAST0) / 4.0, S_FAST0, S_SLOW0),
            ("slow", (S_END - S_SLOW0) / 0.5, S_SLOW0, S_END), ("freeze", 2.0, S_END, S_END)]

def game_time(t):
    acc = 0
    for kind, dur, g0, g1 in segments:
        if t < acc + dur:
            u = (t - acc) / dur
            return kind, g0 + (g1 - g0) * u, u
        acc += dur
    return "freeze", S_END, 1.0

TOTAL = sum(s[1] for s in segments)

# ---------- fonts ----------
def font(size, style="Bold"):
    f = ImageFont.truetype(r"C:\Windows\Fonts\bahnschrift.ttf", size * SS)
    try: f.set_variation_by_name(style)
    except Exception: pass
    return f

def state(name, g):
    tk, x, y, yaw, hp = pos[name]
    i = int(np.clip(np.searchsorted(tk, T0 + g * 64), 0, len(tk) - 1))
    return x[i], y[i], yaw[i], hp[i]

# ---------- frame ----------
MAP_PX = H * SS                      # map panel is a square on the left, full height
ZOOM = _zoom_box()
def frame(t):
    kind, g, u = game_time(t)
    cam = FULL if kind in ("card", "fast") else lerp(FULL, ZOOM, ease(u * 4))      # zoom in during the first quarter of slow-mo
    if kind == "freeze": cam = ZOOM
    cx, cy, size = cam
    crop = radar.crop((int(cx - size / 2), int(cy - size / 2), int(cx + size / 2), int(cy + size / 2))).resize((MAP_PX, MAP_PX), Image.LANCZOS)
    img = Image.new("RGB", (W * SS, H * SS), BG)
    img.paste(crop, (0, 0))
    d2 = ImageDraw.Draw(img, "RGBA")
    k = MAP_PX / size
    P = lambda x, y: ((to_radar(x, y)[0] - (cx - size / 2)) * k, (to_radar(x, y)[1] - (cy - size / 2)) * k)
    tick_now = T0 + g * 64
    for s in smokes:                                       # smokes: ~144 units radius
        if s["start_tick"] <= tick_now <= s["end_tick"]:
            px, py = P(s["x"], s["y"]); r = 144 / md["scale"] * k
            d2.ellipse([px - r, py - r, px + r, py + r], fill=(200, 200, 210, 110), outline=(220, 220, 230, 160), width=SS)
    for f in fires:
        if f["start_tick"] <= tick_now <= f["end_tick"]:
            px, py = P(f["x"], f["y"]); r = 120 / md["scale"] * k
            d2.ellipse([px - r, py - r, px + r, py + r], fill=(255, 110, 30, 90))
    if g >= sec(plant["tick"]):                            # planted bomb, pulsing
        px, py = P(plant["x"], plant["y"]); pr = (9 + 4 * math.sin(t * 8)) * SS
        d2.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(*RED, 220), outline=(255, 255, 255, 230), width=2 * SS)
    for kl in kills:                                       # death marks
        if sec(kl["tick"]) <= g:
            px, py = P(kl["victim_x"], kl["victim_y"]); a = 9 * SS
            col = (*(T_COL if kl["victim_name"] in SPIRIT else CT_COL), 150)
            d2.line([px - a, py - a, px + a, py + a], fill=col, width=3 * SS); d2.line([px - a, py + a, px + a, py - a], fill=col, width=3 * SS)
    for name in pos:                                        # living players
        x, y, yaw, hp = state(name, g)
        if hp <= 0: continue
        px, py = P(x, y); hero = name == HERO
        col = T_COL if name in SPIRIT else CT_COL
        r = (12 if hero else 9) * SS
        if hero:
            gl = (r * 2.2 + 6 * SS * math.sin(t * 6))
            d2.ellipse([px - gl, py - gl, px + gl, py + gl], fill=(*GOLD, 45))
        ang = math.radians(yaw)
        if math.isfinite(ang): d2.line([px, py, px + math.cos(ang) * r * 2.6, py - math.sin(ang) * r * 2.6], fill=(*col, 230), width=3 * SS)
        d2.ellipse([px - r, py - r, px + r, py + r], fill=(*col, 255), outline=(255, 255, 255, 255 if hero else 120), width=(3 if hero else 1) * SS)
        d2.text((px, py - r - 4 * SS), name, font=font(15 if hero else 12), fill=WHITE if hero else (220, 220, 225), anchor="ms")
    # ---- right panel ----
    X0 = MAP_PX + 40 * SS
    d2.text((X0, 40 * SS), "IEM COLOGNE 2026 · QUARTERFINAL", font=font(18, "SemiBold"), fill=GOLD)
    d2.text((X0, 72 * SS), "G2 vs SPIRIT · MIRAGE", font=font(28), fill=WHITE)
    d2.text((X0, 112 * SS), "OT2 · ROUND 34 · SPIRIT 17–16", font=font(20, "SemiBold"), fill=MUTED)
    sp_alive = [n for n in SPIRIT if state(n, g)[3] > 0]
    g2_alive = [n for n in pos if n not in SPIRIT and state(n, g)[3] > 0]
    if len(sp_alive) == 1 and sp_alive[0] == HERO and len(g2_alive) >= 1:
        badge = f"1v{len(g2_alive)}"
        d2.text((X0, 160 * SS), badge, font=font(96), fill=GOLD)
    elif g >= hero_kills[-1]:
        d2.text((X0, 160 * SS), "CLUTCH", font=font(80), fill=GOLD)
    if g >= sec(plant["tick"]):                           # C4 timer
        left = max(0.0, C4_TIME - (g - sec(plant["tick"])))
        d2.text((X0, 290 * SS), f"C4  {left:4.1f}", font=font(30), fill=RED)
    y = 360 * SS                                           # kill feed, newest at the bottom
    for kl in [kk for kk in kills if sec(kk["tick"]) <= g][-5:]:
        a, v = kl["attacker_name"] or "world", kl["victim_name"]
        ac = T_COL if a in SPIRIT else CT_COL; vc = T_COL if v in SPIRIT else CT_COL
        wpn = kl["weapon"].replace("_silencer", "-S").upper()
        line = [(a, ac), (f"  {wpn}{' · HS' if kl['headshot'] else ''}  ", MUTED), (v, vc)]
        xx = X0
        if a == HERO:
            d2.rectangle([X0 - 10 * SS, y - 6 * SS, X0 + 520 * SS, y + 30 * SS], fill=(255, 210, 0, 40))
        for txt, c in line:
            d2.text((xx, y), txt, font=font(20, "SemiBold"), fill=c); xx += d2.textlength(txt, font=font(20, "SemiBold"))
        y += 42 * SS
    if kind == "fast":
        d2.text((MAP_PX - 30 * SS, 30 * SS), "×4", font=font(34), fill=WHITE, anchor="ra")
    if kind == "slow":
        d2.text((MAP_PX - 30 * SS, 30 * SS), "SLOW-MO", font=font(26), fill=GOLD, anchor="ra")
    img = img.resize((W, H), Image.LANCZOS)
    d3 = ImageDraw.Draw(img, "RGBA")
    if kind == "card":                                    # info card over a dimmed frame
        a = min(1, (1 - u) * 3)
        d3.rectangle([0, 0, W, H], fill=(0, 0, 0, int(170 * a)))
        f1 = ImageFont.truetype(r"C:\Windows\Fonts\bahnschrift.ttf", 64); f1.set_variation_by_name("Bold")
        f2 = ImageFont.truetype(r"C:\Windows\Fonts\bahnschrift.ttf", 28); f2.set_variation_by_name("SemiBold")
        d3.text((W / 2, H / 2 - 30), "magixx · 1v4 · B SITE", font=f1, fill=(*GOLD, int(255 * a)), anchor="mm")
        d3.text((W / 2, H / 2 + 35), "OT2 · ROUND 34 · SPIRIT 17–16 G2 · IEM COLOGNE 2026", font=f2, fill=(*WHITE, int(255 * a)), anchor="mm")
    if kind == "freeze":
        f1 = ImageFont.truetype(r"C:\Windows\Fonts\bahnschrift.ttf", 54); f1.set_variation_by_name("Bold")
        a = min(1, u * 4)
        d3.rectangle([0, H - 120, W, H - 40], fill=(0, 0, 0, int(170 * a)))
        span = hero_kills[-1] - hero_kills[0]
        d3.text((W / 2, H - 80), f"4 KILLS · {span:.1f} SECONDS", font=f1, fill=(*GOLD, int(255 * a)), anchor="mm")
    return img

def main():
    OUT.parent.mkdir(exist_ok=True)
    n = int(TOTAL * FPS)
    p = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", str(OUT)], stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait()
    print(f"{OUT} · {TOTAL:.1f}s · kills at {[round(x, 1) for x in hero_kills]} · 1v4 from {hero_last_alone:.1f}s")

if __name__ == "__main__":
    main()
