#!/usr/bin/env python3
"""Facebook cover (851x315) from the official cream logo and real product photos."""

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
DRIVE_PHOTOS = ROOT / "drive-import" / "TTW Images Pictures"

SOFT = (250, 248, 242)
INK = (17, 17, 17)
GOLD = (181, 122, 30)
LUX = (198, 147, 45)
HI = (214, 165, 74)
BAR = (17, 17, 17)
CREAM = (250, 248, 242)

W, H = 851, 315
SCALE = 4
SW, SH = W * SCALE, H * SCALE
BAR_H = 36 * SCALE
# Facebook's page photo covers the bottom-left of the cover.
PROFILE_SAFE = 196 * SCALE


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = {
        "julius": FONTS / "JuliusSansOne-Regular.ttf",
        "script": FONTS / "GreatVibes-Regular.ttf",
        "serif": Path("/usr/share/fonts/truetype/croscore/Tinos-Italic.ttf"),
        "serifb": Path("/usr/share/fonts/truetype/croscore/Tinos-Regular.ttf"),
        "sans": Path("/usr/share/fonts/truetype/croscore/Arimo-Regular.ttf"),
        "sansb": Path("/usr/share/fonts/truetype/croscore/Arimo-Bold.ttf"),
    }[name]
    return ImageFont.truetype(str(path), size)


def cream_canvas() -> Image.Image:
    base = Image.new("RGB", (SW, SH), SOFT)
    noise = Image.effect_noise((SW, SH), 16).convert("L")
    nrgb = Image.merge("RGB", (noise, noise, noise))
    base = Image.blend(base, nrgb, 0.035)
    wash = Image.new("RGB", (SW, SH), (247, 238, 220))
    mask = Image.new("L", (SW, SH), 0)
    md = ImageDraw.Draw(mask)
    for x in range(int(SW * 0.55), SW):
        t = (x - SW * 0.55) / (SW * 0.45)
        md.line([(x, 0), (x, SH)], fill=int(55 * t))
    return Image.composite(wash, base, mask)


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


def warm(im: Image.Image) -> Image.Image:
    im = ImageEnhance.Color(im).enhance(1.07)
    im = ImageEnhance.Contrast(im).enhance(1.05)
    overlay = Image.new("RGB", im.size, (214, 165, 74))
    return Image.blend(im, overlay, 0.04)


def tracked(draw: ImageDraw.ImageDraw, text: str, font_obj, xy, fill, tracking: float) -> float:
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font_obj, fill=fill)
        x += font_obj.getlength(ch) + tracking
    return x


def draw_heart(draw: ImageDraw.ImageDraw, cx: int, cy: int, s: int, fill) -> None:
    r = max(3, s // 2)
    draw.ellipse((cx - s, cy - r, cx, cy + r), fill=fill)
    draw.ellipse((cx, cy - r, cx + s, cy + r), fill=fill)
    draw.polygon([(cx - s - 1, cy), (cx + s + 1, cy), (cx, cy + int(s * 1.55))], fill=fill)


def filigree(draw: ImageDraw.ImageDraw, x0: int, x1: int, y: int) -> None:
    mid = (x0 + x1) // 2
    draw.line([(x0, y), (mid - 26, y)], fill=GOLD, width=3)
    draw.line([(mid + 26, y), (x1, y)], fill=GOLD, width=3)
    draw_heart(draw, mid, y - 1, 10, GOLD)


def gold_ring_photo(im: Image.Image, diameter: int, ring: int = 7, focus=(0.5, 0.42)) -> Image.Image:
    inner = diameter - ring * 2
    photo = warm(crop_cover(im, inner, inner, focus=focus))
    circ = Image.new("L", (inner, inner), 0)
    ImageDraw.Draw(circ).ellipse((0, 0, inner - 1, inner - 1), fill=255)
    cut = Image.new("RGBA", (inner, inner), (0, 0, 0, 0))
    cut.paste(photo.convert("RGBA"), mask=circ)

    canvas = Image.new("RGBA", (diameter + 56, diameter + 56), (0, 0, 0, 0))
    sh = Image.new("L", (diameter, diameter), 0)
    ImageDraw.Draw(sh).ellipse((0, 0, diameter - 1, diameter - 1), fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    canvas.paste((28, 20, 10, 100), (30, 36), sh)

    d = ImageDraw.Draw(canvas)
    ox, oy = 24, 18
    d.ellipse((ox, oy, ox + diameter - 1, oy + diameter - 1), fill=GOLD + (255,))
    d.ellipse((ox + 3, oy + 3, ox + diameter - 4, oy + diameter - 4), fill=HI + (255,))
    d.ellipse(
        (ox + ring, oy + ring, ox + diameter - ring - 1, oy + diameter - ring - 1),
        fill=SOFT + (255,),
    )
    canvas.paste(cut, (ox + ring, oy + ring), cut)
    return canvas


def load_logo() -> Image.Image:
    im = Image.open(LOGOS / "02_Primary_Logo_Soft_White_2000.png").convert("RGBA")
    return im.crop((90, 300, 1910, 1700))


def photo_panel() -> Image.Image:
    """Hero cake with a designed left edge, plus two gold-ring product windows."""
    panel_h = SH - BAR_H
    panel_w = int(SW * 0.46)
    ferrero = Image.open(PHOTOS / "chocoflan-birthday-ferrero.jpg")
    hero = warm(crop_cover(ferrero, panel_w + 80, panel_h, focus=(0.52, 0.38)))
    hero = hero.crop((40, 0, 40 + panel_w, panel_h))

    # Soft left fade into cream + rounded left corners
    layer = Image.new("RGBA", (panel_w, panel_h), (0, 0, 0, 0))
    hero_rgba = hero.convert("RGBA")
    fade = Image.new("L", (panel_w, panel_h), 255)
    fd = ImageDraw.Draw(fade)
    for x in range(0, 260):
        fd.line([(x, 0), (x, panel_h)], fill=int(255 * (x / 260) ** 1.15))
    round_mask = Image.new("L", (panel_w, panel_h), 0)
    ImageDraw.Draw(round_mask).rounded_rectangle(
        (0, 0, panel_w + 90, panel_h - 1), radius=36, fill=255
    )
    alpha = ImageChops_multiply(fade, round_mask)
    hero_rgba.putalpha(alpha)
    layer.alpha_composite(hero_rgba, (0, 0))

    kraft = DRIVE_PHOTOS / "copilot_image_1777064382337.jpeg"
    minis_path = kraft if kraft.exists() else PHOTOS / "mini-flan-box.jpg"
    beso = Image.open(PHOTOS / "beso-de-angel-petal-white.jpg")
    minis = Image.open(minis_path)

    # Two windows on the photo field only — keep the birthday cake readable
    ring_beso = gold_ring_photo(beso, 300, ring=7, focus=(0.48, 0.42))
    ring_minis = gold_ring_photo(minis, 268, ring=6, focus=(0.50, 0.45))
    layer.alpha_composite(ring_beso, (8, 56))
    layer.alpha_composite(ring_minis, (panel_w - 300, panel_h - 330))
    return layer


def ImageChops_multiply(a: Image.Image, b: Image.Image) -> Image.Image:
    from PIL import ImageChops

    return ImageChops.multiply(a, b)


def build() -> tuple[Image.Image, Image.Image]:
    SOCIAL.mkdir(parents=True, exist_ok=True)
    canvas = cream_canvas().convert("RGBA")

    panel = photo_panel()
    px0 = SW - panel.size[0]
    canvas.alpha_composite(panel, (px0, 0))

    # Cream veil so type sits on a calm field, not on cake crumbs
    veil = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    vd = ImageDraw.Draw(veil)
    for i in range(220):
        a = int(210 * (1 - i / 220) ** 1.4)
        vd.line([(px0 + i, 0), (px0 + i, SH - BAR_H)], fill=(*SOFT, a))
    canvas = Image.alpha_composite(canvas, veil)
    draw = ImageDraw.Draw(canvas)

    # Official cream logo
    logo = load_logo()
    logo_h = 560
    logo_w = int(logo.width * logo_h / logo.height)
    logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
    logo_x, logo_y = 36, 28
    canvas.alpha_composite(logo, (logo_x, logo_y))

    serif = font("serif", 38)
    tag = "Flans, Cakes & More — Right to Your Door."
    tw = serif.getlength(tag)
    tx = logo_x + (logo_w - tw) / 2
    ty = logo_y + logo_h + 18
    draw_heart(draw, int(logo_x + logo_w / 2), int(ty - 4), 8, GOLD)
    draw.text((tx, ty + 8), tag, font=serif, fill=INK)

    # Gold rule between logo and menu
    rule_x = logo_x + logo_w + 22
    draw.line([(rule_x, 130), (rule_x, SH - BAR_H - 80)], fill=GOLD, width=3)

    # Center menu — serif caps, matching the boutique banner
    items = [
        "BESO DE ÁNGEL",
        "CHOCOFLAN",
        "MINI DESSERTS & SHOOTERS",
        "TRES LECHES",
    ]
    col_x0 = rule_x + 40
    col_x1 = px0 - 24
    menu = font("serifb", 52)
    filigree(draw, col_x0 + 10, col_x1 - 10, 220)
    y = 280
    for i, line in enumerate(items):
        tracking = 4 if len(line) < 18 else 1.5
        lw = sum(menu.getlength(ch) + tracking for ch in line) - tracking
        x = col_x0 + max(0, (col_x1 - col_x0 - lw) / 2)
        tracked(draw, line, menu, (x, y), INK, tracking)
        y += 88
        if i < len(items) - 1:
            cx = (col_x0 + col_x1) / 2
            draw.ellipse((cx - 4, y - 22, cx + 4, y - 14), fill=GOLD)

    # Contact bar — thin, gold type, gap for the profile photo
    bar_y = SH - BAR_H
    draw.rectangle((0, bar_y - 3, SW, bar_y), fill=GOLD)
    draw.rectangle((0, bar_y, SW, SH), fill=BAR)

    sans = font("sans", 34)
    jul = font("julius", 32)
    y_text = bar_y + (BAR_H - 34) // 2 - 2
    x = PROFILE_SAFE + 8
    parts = [
        ("786-505-5039", sans, HI),
        ("NAPLES, FLORIDA", jul, HI),
        ("@TastyTreatsWorld", sans, CREAM),
    ]
    for idx, (label, fnt, fill) in enumerate(parts):
        if idx:
            draw.line([(x, bar_y + 28), (x, SH - 28)], fill=GOLD, width=2)
            x += 28
        if idx == 1:
            tracked(draw, label, fnt, (x, y_text + 4), fill, 5)
            x += sum(fnt.getlength(ch) + 5 for ch in label) + 22
        else:
            draw.text((x, y_text), label, font=fnt, fill=fill)
            x += fnt.getlength(label) + 22

    rgb = canvas.convert("RGB")
    cover = rgb.resize((W, H), Image.Resampling.LANCZOS)
    cover2x = rgb.resize((W * 2, H * 2), Image.Resampling.LANCZOS)
    return cover, cover2x


def save_lookbook_extra() -> None:
    src = DRIVE_PHOTOS / "copilot_image_1777064382337.jpeg"
    if not src.exists():
        return
    dest = PHOTOS / "mini-chocoflan-kraft-box.jpg"
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    im.save(dest, "JPEG", quality=90, optimize=True)
    idx = PHOTOS / "PHOTO-INDEX.md"
    text = idx.read_text(encoding="utf-8")
    if "mini-chocoflan-kraft-box.jpg" not in text:
        idx.write_text(
            text.rstrip() + "\n- `mini-chocoflan-kraft-box.jpg` — Mini chocoflan box with pink florals\n",
            encoding="utf-8",
        )


def write_usage() -> None:
    (SOCIAL / "FACEBOOK-COVER-README.txt").write_text(
        """Tasty Treats World — Facebook cover
===================================

Upload this file to Facebook as the page cover:
  facebook-cover-851x315.jpg

For a sharper upload (Facebook compresses covers), use:
  facebook-cover-1702x630.jpg

Size: 851 × 315 px

This cover uses:
- The official cream logo (02_Primary_Logo_Soft_White)
- Real cakes: two-tier Ferrero chocoflan, Beso de Ángel, boxed minis
- Soft White background #FAF8F2 (not black)
- Thin contact bar: 786-505-5039 · Naples, Florida · @TastyTreatsWorld

Facebook profile photo
The round page photo covers the bottom-left of the cover. Contact text
starts after that zone. Use instagram-avatar-1080.png as the page photo.

Do not stretch the square logo to fill the cover — that is what makes
the transparent file look like a black square in some apps.
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
    save_lookbook_extra()
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
