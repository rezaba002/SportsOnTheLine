"""Contact sheets for picking cut points. python sheet.py <clip> <start> <end> <step> [cols] [crop: x,y,w,h]"""
import pathlib, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
FF = r"EDIT_ME\ffmpeg\bin\ffmpeg.exe"
ROOT = pathlib.Path(__file__).parent.parent
cid, a, b, step = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
cols = int(sys.argv[5]) if len(sys.argv) > 5 else 6
crop = sys.argv[6] if len(sys.argv) > 6 else None
tw, th = 320, 180
cx, cy, cw, ch = (crop.split(",") if crop else (0, 0, 0, 0))
vf = (f"crop={cw}:{ch}:{cx}:{cy}," if crop else "") + f"fps={1/step},scale={tw}:{th}"
raw = subprocess.run([FF, "-v", "error", "-ss", f"{a}", "-i", str(ROOT / "footage" / "clips" / f"{cid}.mp4"), "-t", f"{b - a}",
                      "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
n = len(raw) // (tw * th * 3)
font = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 15)
out = Image.new("RGB", (tw * cols, th * ((n + cols - 1) // cols)))
for i in range(n):
    im = Image.frombytes("RGB", (tw, th), raw[i * tw * th * 3:(i + 1) * tw * th * 3])
    d = ImageDraw.Draw(im); d.rectangle([0, 0, 52, 18], fill="black"); d.text((3, 1), f"{a + i * step:.1f}", font=font, fill="yellow")
    out.paste(im, ((i % cols) * tw, (i // cols) * th))
p = ROOT / "work" / "killsheets" / f"{cid}_{a:g}-{b:g}{'_crop' if crop else ''}.jpg"
p.parent.mkdir(exist_ok=True)
out.save(p, quality=78)
print(p)
