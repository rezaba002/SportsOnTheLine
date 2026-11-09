"""Pitch variants of every sound effect, so repeated effects never sound identical (video 05 v4).

1. Copies the new CC0 clicks and whooshes from the editing-videos library into sotl-graphics/public/sfx/
   (clicks are levelled down to one loudness, so the rotation between them is even).
2. Writes public/sfx/v/<name>_<p>.wav for p = -3..+3 semitones (tape-style: asetrate + aresample, so the
   length changes with the pitch, which is what a real pitch change sounds like).
The Sfx component (src/cards/Sfx.tsx) picks a variant per play when variation is switched on.
"""
import json, pathlib, subprocess

LIB = pathlib.Path(r"EDIT_ME\sound-library")
PUB = pathlib.Path(r"D:\Youtube\sotl-graphics\public\sfx")
FFMPEG = "ffmpeg"
CLICKS = ["tap", "click-soft", "click-sharp", "select-1", "toggle", "hover-2"]
SWOOSH = ["slide-1", "slide-2", "sweep-long"]
CLICK_LUFS = -29.5   # quietest click in the pool is about -30; louder ones come down to it

cat = {c["id"]: c for c in json.loads((LIB / "catalog.json").read_text(encoding="utf-8"))["sounds"]}


def run(args):
    subprocess.run([FFMPEG, "-v", "error", "-y", *args], check=True)


for sid in CLICKS + SWOOSH:
    c = cat[sid]
    src, dst = LIB / c["file"], PUB / pathlib.Path(c["file"]).name
    gain = min(0.0, CLICK_LUFS - c["lufs"]) if sid in CLICKS else 0.0
    run(["-i", str(src), "-af", f"volume={gain:.1f}dB", "-ar", "48000", str(dst)])
    print(f"copied {dst.name:22} gain {gain:+.1f} dB")

out = PUB / "v"
out.mkdir(exist_ok=True)
n = 0
for wav in sorted(PUB.glob("*.wav")):
    for p in range(-3, 4):
        r = 2 ** (p / 12)
        run(["-i", str(wav), "-af", f"asetrate={48000 * r:.0f},aresample=48000", str(out / f"{wav.stem}_{p}.wav")])
        n += 1
print(f"{n} variants in {out}")
