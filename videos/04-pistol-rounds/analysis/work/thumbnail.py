"""Thumbnails for video 04 (1280x720), two versions to choose from:
A  donk looking into the camera + his quote "REMOVE PISTOL ROUNDS?" + "IS HE RIGHT?"
B  ZywOo's USP-S pistol round (Budapest final) + "DO PISTOLS DECIDE CS2?" + the 66% / 34% split.
Output: D:\\Youtube\\video04\\thumbnail_A.jpg / _B.jpg + phone-size previews in work/thumb/."""
import pathlib
from PIL import Image, ImageDraw, ImageEnhance

from engine import font

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOGOS = ROOT / "assets" / "logos"
TW, TH = 1280, 720
YELLOW, BLACK, WHITE, RED, GREEN = (255, 211, 77), (10, 12, 16), (245, 245, 245), (228, 40, 52), (88, 196, 104)


def logo(key, box_w, box_h):
    im = Image.open(LOGOS / f"{key}.png").convert("RGBA")
    im = im.crop(im.getbbox())
    s = min(box_w / im.width, box_h / im.height)
    return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)


def pop(im, color=1.2, contrast=1.15, bright=1.1):
    return ImageEnhance.Brightness(ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(color)).enhance(contrast)).enhance(bright)


def fade_left(img, x0, width):
    """Blend the photo into black towards the left from x0 over `width` px."""
    edge = Image.linear_gradient("L").rotate(90).resize((width, TH)).transpose(Image.FLIP_LEFT_RIGHT)
    img.paste(BLACK, (x0, 0, x0 + width, TH), edge)
    img.paste(BLACK, (0, 0, x0, TH))


def block(d, xy, s, size, fg, bg, pad=(22, 12)):
    f = font(size)
    l, t, r, b = d.textbbox((0, 0), s, font=f)
    x, y = xy
    d.rectangle([x, y, x + r - l + 2 * pad[0], y + b - t + 2 * pad[1]], fill=bg)
    d.text((x + pad[0] - l, y + pad[1] - t), s, font=f, fill=fg)


def version_a():
    fr = Image.open(ROOT / "work" / "thumb" / "src_donk_11.4.png").convert("RGB")      # looking into the camera
    crop = pop(fr.crop((560, 0, 1210, 935)).resize((500, 720), Image.LANCZOS))
    img = Image.new("RGB", (TW, TH), BLACK)
    img.paste(crop, (TW - 500, 0))
    fade_left(img, TW - 500, 170)
    d = ImageDraw.Draw(img)
    block(d, (40, 70), "“REMOVE PISTOL", 74, BLACK, YELLOW)
    block(d, (40, 175), "ROUNDS.”", 74, BLACK, YELLOW)
    d.text((40, 330), "IS HE", font=font(150), fill=WHITE, stroke_width=6, stroke_fill=BLACK)
    d.text((40, 480), "RIGHT?", font=font(170), fill=YELLOW, stroke_width=6, stroke_fill=BLACK)
    return img


def version_b():
    fr = Image.open(ROOT / "work" / "thumb" / "src_zy_12.3.png").convert("RGB")         # USP-S muzzle flash, round 13
    img = pop(fr.crop((540, 215, 1640, 834)).resize((TW, TH), Image.LANCZOS), 1.25, 1.2, 1.0)
    shade = Image.linear_gradient("L").rotate(90).resize((TW, TH)).transpose(Image.FLIP_LEFT_RIGHT)   # dark on the left
    img.paste(BLACK, (0, 0, TW, TH), shade.point(lambda v: int(v * 0.85)))
    d = ImageDraw.Draw(img)
    d.text((40, 40), "DO PISTOLS", font=font(118), fill=WHITE, stroke_width=6, stroke_fill=BLACK)
    d.text((40, 160), "DECIDE CS2?", font=font(140), fill=YELLOW, stroke_width=6, stroke_fill=BLACK)
    for i, (lab, val, col) in enumerate([("WIN BOTH", "66%", GREEN), ("LOSE BOTH", "34%", RED)]):
        y = 370 + i * 160
        block(d, (40, y + 24), lab, 46, BLACK, WHITE, pad=(16, 10))
        d.text((330, y + 60), val, font=font(130), fill=col, stroke_width=6, stroke_fill=BLACK, anchor="lm")
    return img


if __name__ == "__main__":
    for name, img in (("A", version_a()), ("B", version_b())):
        out = ROOT / f"thumbnail_{name}.jpg"
        img.save(out, quality=92)
        img.resize((320, 180), Image.LANCZOS).save(ROOT / "work" / "thumb" / f"phone_{name}.png")
        print(out)
