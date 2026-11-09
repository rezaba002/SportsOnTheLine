"""Our own sound effects (synthesised, no licence questions) -> work/sfx/*.wav, 48 kHz stereo."""
import numpy as np, wave, pathlib
SR = 48000
OUT = pathlib.Path(__file__).parent / "sfx"


def save(name, y):
    y = np.clip(y / (np.abs(y).max() + 1e-9) * 0.9, -1, 1)
    st = np.stack([y, y], 1)
    with wave.open(str(OUT / f"{name}.wav"), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


t = lambda d: np.arange(int(SR * d)) / SR
rng = np.random.default_rng(3)
# sub drop: sine sweeping 120 -> 35 Hz with a punchy attack
x = t(1.2); f = 35 + 85 * np.exp(-x * 4); ph = 2 * np.pi * np.cumsum(f) / SR
save("sub-drop", np.sin(ph) * np.exp(-x * 2.2) + 0.25 * np.sin(2 * ph) * np.exp(-x * 6))
# bass hit: short low thump + noise click
x = t(0.6); ph = 2 * np.pi * np.cumsum(55 + 140 * np.exp(-x * 30)) / SR
save("bass-hit", np.sin(ph) * np.exp(-x * 7) + rng.normal(0, 1, len(x)) * np.exp(-x * 80) * 0.4)
# tape stop: chord that slows and drops in pitch
x = t(0.9); rate = np.clip(1 - x / 0.9, 0.02, 1) ** 1.5
ph = 2 * np.pi * np.cumsum(220 * rate) / SR
save("tape-stop", (np.sin(ph) + 0.5 * np.sin(1.5 * ph) + 0.3 * np.sin(2 * ph)) * np.clip(1 - x / 0.9, 0, 1))
# bomb beep (C4-style tick, generic sine beep)
x = t(0.12); save("bomb-beep", np.sin(2 * np.pi * 1850 * x) * np.exp(-x * 25))
# heartbeat: two low thumps
x = t(0.9); hb = np.zeros_like(x)
for st_, a in ((0.0, 1.0), (0.22, 0.7)):
    k = (x >= st_); xx = x[k] - st_
    hb[k] += a * np.sin(2 * np.pi * (48 + 30 * np.exp(-xx * 25)) * xx) * np.exp(-xx * 14)
save("heartbeat", hb)
# glitch burst: chopped noise + bitcrushed tone
x = t(0.35); g = rng.normal(0, 1, len(x)) * (np.sin(2 * np.pi * 37 * x) > 0) + np.sign(np.sin(2 * np.pi * 330 * x)) * 0.4
save("glitch-burst", g * np.exp(-x * 6))
# riser (noise swell 1.5 s, band rising)
x = t(1.5); n = rng.normal(0, 1, len(x)); sw = np.sin(2 * np.pi * np.cumsum(200 + 2400 * (x / 1.5) ** 2) / SR)
save("noise-riser", (n * 0.5 + sw * 0.5) * (x / 1.5) ** 2)
print("ok")
