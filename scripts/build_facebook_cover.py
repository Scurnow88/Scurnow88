#!/usr/bin/env python3
"""Facebook cover 851x315 — cream left panel, full-bleed real cake on the right."""

from __future__ import annotations

import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT = Path("/workspace")
PKG = ROOT / "TastyTreatsWorld-Brand-Package"
PHOTOS = PKG / "03-Product-Photography"
LOGOS = PKG / "02-Official-Logos"
SOCIAL = PKG / "05-Social-Media"
FONTS = ROOT / "brand-kit" / "fonts"
FERRERO_CUT = Path("/tmp/ttw-cutouts/ferrero.png")
BESO_CUT = Path("/tmp/ttw-cutouts/beso-studio.png")

SOFT = (250, 248, 242)
INK = (17, 17, 17)
GOLD = (181, 122, 30)
HI = (214, 165, 74)
BAR = (22, 18, 14)
CREAM = (250, 248, 242)

W, H = 851, 315
SCALE = 4
SW, SH = W * SCALE, H * SCALE
BAR_H = 34 * SCALE
PROFILE_SAFE = 196 * SCALE


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = {
        "julius": FONTS / "JuliusSansOne-Regular.ttf",
        "serif": Path("/usr/share/fonts/truetype/croscore/Tinos-Italic.ttf"),
        "serifb": Path("/usr/share/fonts/truetype/croscore/Tinos-Regular.ttf"),
        "sans": Path("/usr/share/fonts/truetype/croscore/Arimo-Regular.ttf"),
    }[name]
    return ImageFont.truetype(str(path), size)


def tracked(draw, text, font_obj, xy, fill, tracking: float) -> float:
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font_obj, fill=fill)
        x += font_obj.getlength(ch) + tracking
    return x


def draw_heart(draw, cx: int, cy: int, s: int, fill) -> None:
    r = max(3, s // 2)
    draw.ellipse((cx - s, cy - r, cx, cy + r), fill=fill)
    draw.ellipse((cx, cy - r, cx + s, cy + r), fill=fill)
    draw.polygon([(cx - s - 1, cy), (cx + s + 1, cy), (cx, cy + int(s * 1.55))], fill=fill)


def crop_cover(im: Image.Image, tw: int, th: int, focus=(0.5, 0.42)) -> Image.Image:
    im = ImageOps.exif_transpose(im).convert("RGB")
    src_w, src_h = im.size
    scale = max(tw / src_w, th / src_h)
    nw, nh = int(src_w * scale + 0.5), int(src_h * scale + 0.5)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    cx, cy = int(nw * focus[0]), int(nh * focus[1])
    left = max(0, min(nw - tw, cx - tw // 2))
    top = max(0, min(nh - th, cy - th // 2))
    return im.crop((left, top, left + tw, top + th))


def cream_canvas() -> Image.Image:
    base = Image.new("RGB", (SW, SH), SOFT)
    noise = Image.effect_noise((SW, SH), 13).convert("L")
    nrgb = Image.merge("RGB", (noise, noise, noise))
    base = Image.blend(base, nrgb, 0.03)
    # Warm blush on the right so the white plate does not vanish
    rose = Image.new("RGB", (SW, SH), (232, 210, 204))
    mask = Image.new("L", (SW, SH), 0)
    ImageDraw.Draw(mask).ellipse(
        (int(SW * 0.46), -40, SW + 200, int(SH * 0.95)), fill=70
    )
    mask = mask.filter(ImageFilter.GaussianBlur(90))
    return Image.composite(rose, base, mask)


def tighten_mask(im: Image.Image, erode: int = 6) -> Image.Image:
    a = im.split()[-1]
    a = a.filter(ImageFilter.MinFilter(erode * 2 + 1))
    a = a.filter(ImageFilter.GaussianBlur(1.6))
    out = im.copy()
    out.putalpha(a)
    return trim_alpha(out)


def cutout_sprite(cache: Path, src: Path, height: int, erode: int = 6) -> Image.Image:
    if cache.exists():
        im = Image.open(cache).convert("RGBA")
    else:
        from rembg import remove

        raw = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        im = remove(raw)
        cache.parent.mkdir(parents=True, exist_ok=True)
        im.save(cache)
    im = tighten_mask(im, erode)
    width = int(im.width * height / im.height)
    return im.resize((width, height), Image.Resampling.LANCZOS)


def paste_still(canvas: Image.Image, sprite: Image.Image, xy: tuple[int, int]) -> None:
    x, y = xy
    alpha = sprite.split()[-1]
    sh = alpha.filter(ImageFilter.GaussianBlur(36))
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    black = Image.new("RGBA", sprite.size, (48, 32, 20, 0))
    black.putalpha(sh.point(lambda p: int(p * 0.34)))
    shadow.alpha_composite(black, (x + 14, y + 34))
    canvas.alpha_composite(shadow)
    canvas.alpha_composite(sprite, (x, y))


def trim_alpha(im: Image.Image, pad: int = 0) -> Image.Image:
    bbox = im.getbbox()
    if not bbox:
        return im
    x0, y0, x1, y1 = bbox
    return im.crop(
        (max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad))
    )


def load_logo() -> Image.Image:
    im = Image.open(LOGOS / "01_Primary_Logo_Transparent_2000.png").convert("RGBA")
    return trim_alpha(im, pad=6)


def build() -> tuple[Image.Image, Image.Image]:
    SOCIAL.mkdir(parents=True, exist_ok=True)
    canvas = cream_canvas().convert("RGBA")
    content_h = SH - BAR_H

    cake = cutout_sprite(
        FERRERO_CUT, PHOTOS / "gold-board-minis.jpg", int(content_h * 0.94), erode=7
    )
    beso = cutout_sprite(
        BESO_CUT, PHOTOS / "beso-de-angel-studio.jpg", int(content_h * 0.88), erode=5
    )
    bx = int(SW * 0.30)
    by = content_h - beso.height + 40
    fx = bx + int(beso.width * 0.50)
    fy = content_h - cake.height + 24
    paste_still(canvas, beso, (bx, by))
    paste_still(canvas, cake, (fx, fy))

    draw = ImageDraw.Draw(canvas)

    logo = load_logo()
    logo_h = 620
    logo_w = int(logo.width * logo_h / logo.height)
    logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
    logo_x, logo_y = 40, 48
    canvas.alpha_composite(logo, (logo_x, logo_y))

    serif = font("serif", 36)
    tag = "Flans, Cakes & More — Right to Your Door."
    tw = serif.getlength(tag)
    tx = logo_x + max(0, (logo_w - tw) / 2)
    ty = logo_y + logo_h + 10
    draw_heart(draw, int(logo_x + logo_w / 2), int(ty - 2), 8, GOLD)
    draw.text((tx, ty + 6), tag, font=serif, fill=INK)

    bar_y = content_h
    draw.rectangle((0, bar_y - 3, SW, bar_y), fill=GOLD)
    draw.rectangle((0, bar_y, SW, SH), fill=BAR)

    sans = font("sans", 32)
    jul = font("julius", 30)
    y_text = bar_y + (BAR_H - 32) // 2 - 1
    x = PROFILE_SAFE + 12
    parts = [
        (False, "786-505-5039", sans, HI),
        (True, "NAPLES, FLORIDA", jul, HI),
        (False, "@TastyTreatsWorld", sans, CREAM),
    ]
    for i, (do_track, label, fnt, fill) in enumerate(parts):
        if i:
            draw.line([(x, bar_y + 26), (x, SH - 26)], fill=GOLD, width=2)
            x += 26
        if do_track:
            tracked(draw, label, fnt, (x, y_text + 4), fill, 5)
            x += sum(fnt.getlength(ch) + 5 for ch in label) + 20
        else:
            draw.text((x, y_text), label, font=fnt, fill=fill)
            x += fnt.getlength(label) + 20

    rgb = canvas.convert("RGB")
    cover = rgb.resize((W, H), Image.Resampling.LANCZOS)
    cover2x = rgb.resize((W * 2, H * 2), Image.Resampling.LANCZOS)
    return cover, cover2x


def write_usage() -> None:
    (SOCIAL / "FACEBOOK-COVER-README.txt").write_text(
        """Tasty Treats World — Facebook cover
===================================

Upload: facebook-cover-851x315.jpg
Sharper upload: facebook-cover-1702x630.jpg

851 × 315 px. Official logo on Soft White with real cakes
(Beso de Ángel and Ferrero chocoflan) sitting on the cream.
No stretched square logo, no black canvas.

Page profile photo: instagram-avatar-1080.png
(Facebook covers the bottom-left of this banner with that photo.)
""",
        encoding="utf-8",
    )


def zip_package() -> None:
    zip_path = ROOT / "TastyTreatsWorld-Brand-Package.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in PKG.rglob("*"):
            if file.is_file():
                zf.write(file, file.relative_to(PKG.parent))


def main() -> None:
    cover, cover2x = build()
    jpg = SOCIAL / "facebook-cover-851x315.jpg"
    jpg2 = SOCIAL / "facebook-cover-1702x630.jpg"
    png = SOCIAL / "facebook-cover-851x315.png"
    cover.save(jpg, "JPEG", quality=93, optimize=True, subsampling=1)
    cover2x.save(jpg2, "JPEG", quality=93, optimize=True, subsampling=1)
    cover.save(png, "PNG")
    write_usage()
    zip_package()
    print("wrote", jpg, cover.size)
    print("wrote", jpg2, cover2x.size)


if __name__ == "__main__":
    main()
