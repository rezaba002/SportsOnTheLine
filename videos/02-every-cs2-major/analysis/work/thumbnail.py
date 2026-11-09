"""Thumbnails for video 02 (1280x720), two versions to choose from:
A  'EVERY CS2 MAJOR' + '5 MAJORS · 4 CHAMPIONS' + the four champions' logos, jL's fist pump on the right.
B  'EVERY CS2 MAJOR' + the FaZe curse: big red '0 FOR 3' + FaZe logo, same photo.
Output: D:\\Youtube\\video02\\thumbnail_A.jpg / _B.jpg + phone-size previews in work/thumb/."""
import pathlib
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from engine import font

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOGOS = ROOT / "assets" / "logos"
TW, TH = 1280, 720
YELLOW, BLACK, WHITE, RED = (255, 211, 77), (10, 12, 16), (245, 245, 245), (228, 40, 52)


def logo(key, box_w, box_h):
    im = Image.open(LOGOS / f"{key}.png").convert("RGBA")
    im = im.crop(im.getbbox())
    s = min(box_w / im.width, box_h / im.height)
    return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)


def base():
    fr = Image.open(ROOT / "work" / "thumb" / "src_jl.png").convert("RGB")      # C1 33.3 s: jL's fist pump
    crop = fr.crop((560, 60, 1260, 850)).resize((640, 722))
    crop = ImageEnhance.Brightness(ImageEnhance.Contrast(ImageEnhance.Color(crop).enhance(1.25)).enhance(1.15)).enhance(1.3)
    img = Image.new("RGB", (TW, TH), BLACK)
    img.paste(crop, (TW - 640, 0))
    edge = Image.linear_gradient("L").rotate(90).resize((200, TH)).transpose(Image.FLIP_LEFT_RIGHT)
    img.paste(BLACK, (TW - 640, 0, TW - 440, TH), edge)
    return img


def title(d):
    d.text((40, 50), "EVERY CS2", font=font(84), fill=WHITE, stroke_width=4, stroke_fill=BLACK)
    d.text((32, 130), "MAJOR", font=font(170), fill=YELLOW, stroke_width=6, stroke_fill=BLACK)


def version_a():
    img = base()
    d = ImageDraw.Draw(img)
    title(d)
    tag = "5 MAJORS · 4 CHAMPIONS"
    f = font(50)
    w = d.textlength(tag, font=f)
    d.rectangle([40, 360, 40 + w + 40, 440], fill=YELLOW)
    d.text((60, 400), tag, font=f, fill=BLACK, anchor="lm")
    x = 44
    for k in ("navi", "spirit", "vit", "falcons"):
        lg = logo(k, 150, 90)
        img.paste(lg, (x, 520 + (90 - lg.height) // 2), lg)
        x += lg.width + 36
    return img


def version_b():
    img = base()
    d = ImageDraw.Draw(img)
    title(d)
    lg = logo("faze", 170, 170)
    img.paste(lg, (44, 380 + (170 - lg.height) // 2), lg)
    d.text((240, 470), "0 FOR 3", font=font(124), fill=RED, stroke_width=6, stroke_fill=BLACK, anchor="lm")
    d.text((246, 570), "IN MAJOR FINALS", font=font(44, "SemiBold"), fill=WHITE, stroke_width=3, stroke_fill=BLACK, anchor="lm")
    return img


if __name__ == "__main__":
    for name, img in (("A", version_a()), ("B", version_b())):
        out = ROOT / f"thumbnail_{name}.jpg"
        img.save(out, quality=92)
        img.resize((320, 180), Image.LANCZOS).save(ROOT / "work" / "thumb" / f"phone_{name}.png")
        print(out)
