"""Thumbnail for video 03 (1280x720): the frog coach in a headset + 'ARE TIMEOUTS USELESS?' + '430 TIMEOUTS'.
Output: D:\\Youtube\\video03\\thumbnail.jpg (+ a 320 px preview to judge it at phone size)."""
import pathlib, subprocess

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from engine import FFMPEG, font

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "footage" / "coaches" / "jabjabich.mp4"
TW, TH = 1280, 720
YELLOW, BLACK, WHITE = (255, 211, 77), (10, 12, 16), (245, 245, 245)


def grab(t):
    out = ROOT / "work" / "tmp" / "thumb_src.png"
    subprocess.run([FFMPEG, "-y", "-v", "error", "-ss", str(t), "-i", str(SRC), "-frames:v", "1", str(out)], check=True)
    return Image.open(out).convert("RGB")


def main():
    fr = grab(11.6)                                     # frog in headset under "RUSH B / DONK GO KILL"
    crop = fr.crop((600, 30, 1240, 750))                # 640x720: frog + note, unobstructed on the right half
    crop = ImageEnhance.Contrast(ImageEnhance.Color(crop).enhance(1.3)).enhance(1.15)
    img = Image.new("RGB", (TW, TH), BLACK)
    img.paste(crop, (TW - 640, 0))
    # soft edge between the text half and the frog
    edge = Image.linear_gradient("L").rotate(90).resize((160, TH)).transpose(Image.FLIP_LEFT_RIGHT)
    img.paste(BLACK, (TW - 640, 0, TW - 480, TH), edge)
    d = ImageDraw.Draw(img)
    d.text((40, 60), "ARE TIMEOUTS", font=font(78), fill=WHITE, stroke_width=4, stroke_fill=BLACK)
    d.text((32, 140), "USELESS?", font=font(150), fill=YELLOW, stroke_width=6, stroke_fill=BLACK)
    tag = "430 CHECKED"
    f = font(60)
    wtag = d.textlength(tag, font=f)
    d.rectangle([40, 370, 40 + wtag + 44, 458], fill=YELLOW)
    d.text((62, 414), tag, font=f, fill=BLACK, anchor="lm")
    d.text((44, 500), "COLOGNE MAJOR 2026", font=font(40, "SemiBold"), fill=(200, 205, 215))
    d.text((44, 600), "THE COACH", font=font(56), fill=WHITE, stroke_width=4, stroke_fill=BLACK)
    d.line([(370, 628), (600, 560)], fill=WHITE, width=10)
    d.polygon([(625, 552), (585, 548), (598, 582)], fill=WHITE)
    out = ROOT / "thumbnail.jpg"
    img.save(out, quality=92)
    img.resize((320, 180), Image.LANCZOS).save(ROOT / "review" / "thumbnail_phone.png")
    print(out)


if __name__ == "__main__":
    main()
