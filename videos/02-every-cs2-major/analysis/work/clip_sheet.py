"""Contact sheet of a rendered clip: python clip_sheet.py <path> [n=16] [cols=4] -> <path>_sheet.jpg"""
import subprocess, sys
from PIL import Image, ImageDraw, ImageFont
FFB = r"EDIT_ME\ffmpeg\bin"
path = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 16; cols = int(sys.argv[3]) if len(sys.argv) > 3 else 4
dur = float(subprocess.run([FFB + r"\ffprobe.exe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True).stdout)
font = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 18)
tiles = []
for k in range(n):
    t = dur * (k + 0.5) / n
    raw = subprocess.run([FFB + r"\ffmpeg.exe", "-v", "error", "-ss", f"{t:.2f}", "-i", path, "-frames:v", "1", "-vf", "scale=480:270", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    im = Image.frombytes("RGB", (480, 270), raw); d = ImageDraw.Draw(im); d.rectangle([0, 0, 60, 22], fill="magenta"); d.text((3, 1), f"{t:.1f}", font=font, fill="white")
    tiles.append(im)
out = Image.new("RGB", (480 * cols, 270 * ((n + cols - 1) // cols)))
for i, im in enumerate(tiles):
    out.paste(im, ((i % cols) * 480, (i // cols) * 270))
out.save(path.rsplit(".", 1)[0] + "_sheet.jpg", quality=78)
print(path.rsplit(".", 1)[0] + "_sheet.jpg")
