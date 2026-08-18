#!/usr/bin/env python3
"""Fold the official Google Drive kit into the downloadable brand package."""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageOps
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as pdfcanvas

ROOT = Path("/workspace")
DRIVE = ROOT / "drive-import"
LOGOS = DRIVE / "Logos Tasty_Treats_World_Professional_Brand_Package"
PHOTOS = DRIVE / "TTW Images Pictures"
MENU = DRIVE / "TTW Menu"
OUT = ROOT / "TastyTreatsWorld-Brand-Package"

GOLD = HexColor("#B57A1E")
LUX_GOLD = HexColor("#C6932D")
HI_GOLD = HexColor("#D6A54A")
INK = HexColor("#111111")
SOFT = HexColor("#FAF8F2")
WHITE = HexColor("#FFFFFF")
ROSE = HexColor("#C9A3A8")

LOOKBOOK = [
    ("20260807_232042.jpg", "beso-de-angel-petal-white.jpg", "Beso de Ángel — petal white cake"),
    ("IMG-20260818-WA0036.jpg", "beso-de-angel-mothers-day.jpg", "Beso de Ángel — Mother's Day"),
    ("IMG-20260818-WA0030.jpg", "chocoflan-two-tier-mothers-day.jpg", "Chocoflan two-level — Mother's Day"),
    ("IMG-20260818-WA0024.jpg", "chocoflan-birthday-ferrero.jpg", "Chocoflan two-level — birthday Ferrero"),
    ("IMG-20260414-WA0016.jpg", "chocoflan-mothers-day-gold.jpg", "Chocoflan — gold Mother's Day topper"),
    ("Cupcakes.jpg", "mini-flan-box.jpg", "Mini vanilla flan / cupcakes, boxed"),
    ("IMG-20260818-WA0031.jpg", "chocoflan-boxed.jpg", "Chocoflan in bakery box"),
    ("IMG-20260818-WA0033.jpg", "celebration-cake-detail.jpg", "Celebration cake detail"),
    ("IMG-20260818-WA0038.jpg", "piped-cake-detail.jpg", "Piped cake detail"),
    ("IMG-20260818-WA0039.jpg", "gold-board-minis.jpg", "Mini desserts on gold boards"),
    ("IMG-20260414-WA0011.jpg", "flan-caramel-top.jpg", "Caramel flan top"),
    ("IMG-20260414-WA0018.jpg", "product-hero-01.jpg", "Product hero"),
    ("IMG-20260414-WA0019.jpg", "product-hero-02.jpg", "Product hero"),
    ("20260807_232211.jpg", "beso-de-angel-studio.jpg", "Beso de Ángel studio"),
    ("20260807_232320.jpg", "white-cake-texture.jpg", "White cake texture"),
    ("20260807_232446.jpg", "cake-detail-ruffle.jpg", "Ruffle piping detail"),
]


def hex_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def copy_official_logos() -> None:
    dest = OUT / "02-Official-Logos"
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    for src in sorted(LOGOS.iterdir()):
        if src.is_file():
            shutil.copy2(src, dest / src.name)


def copy_lookbook() -> list[tuple[Path, str]]:
    dest = OUT / "03-Product-Photography"
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    copied = []
    for src_name, dest_name, caption in LOOKBOOK:
        src = PHOTOS / src_name
        if not src.exists():
            continue
        target = dest / dest_name
        im = Image.open(src)
        im = ImageOps.exif_transpose(im)
        im.convert("RGB").save(target, "JPEG", quality=90, optimize=True)
        copied.append((target, caption))
    (dest / "PHOTO-INDEX.md").write_text(
        "# Product photography\n\n"
        "Curated from the shared Drive folder **TTW Images Pictures**.\n\n"
        + "\n".join(f"- `{p.name}` — {cap}" for p, cap in copied)
        + "\n",
        encoding="utf-8",
    )
    return copied


def copy_menu_source() -> None:
    dest = OUT / "04-Menu"
    dest.mkdir(parents=True, exist_ok=True)
    for src in MENU.iterdir():
        if src.is_file():
            safe = src.name.replace("🍰 ", "").replace("  ", " ").strip()
            shutil.copy2(src, dest / "source" / safe if False else dest / safe)
    # flatten
    src_dir = dest
    src_dir.mkdir(exist_ok=True)


def square_crop(im: Image.Image, size: int = 1080) -> Image.Image:
    im = ImageOps.exif_transpose(im).convert("RGB")
    w, h = im.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    im = im.crop((left, top, left + side, top + side))
    return im.resize((size, size), Image.Resampling.LANCZOS)


def make_social_posts(photos: list[tuple[Path, str]]) -> None:
    dest = OUT / "05-Social-Media" / "instagram-posts"
    dest.mkdir(parents=True, exist_ok=True)
    mark = Image.open(LOGOS / "13_Watermark_Gold_20pct.png").convert("RGBA")
    avatar = Image.open(LOGOS / "15_Instagram_Profile_1080.png").convert("RGBA")
    # official avatars already exist — copy into social
    social = OUT / "05-Social-Media"
    shutil.copy2(LOGOS / "15_Instagram_Profile_1080.png", social / "instagram-avatar-1080.png")
    shutil.copy2(LOGOS / "16_Instagram_Profile_320.png", social / "instagram-avatar-320.png")
    shutil.copy2(LOGOS / "13_Watermark_Gold_20pct.png", social / "watermark-gold.png")
    shutil.copy2(LOGOS / "14_Cupcake_Icon_Transparent_1200.png", social / "cupcake-icon.png")

    for i, (photo, caption) in enumerate(photos[:8], 1):
        base = square_crop(Image.open(photo), 1080)
        canvas = base.convert("RGBA")
        # bottom gradient
        overlay = Image.new("RGBA", (1080, 1080), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        for y in range(820, 1080):
            a = int(170 * (y - 820) / 260)
            d.line([(0, y), (1080, y)], fill=(17, 17, 17, a))
        canvas = Image.alpha_composite(canvas, overlay)
        wm = mark.copy()
        wm.thumbnail((220, 220), Image.Resampling.LANCZOS)
        canvas.alpha_composite(wm, (1080 - wm.size[0] - 36, 36))
        out = dest / f"post-{i:02d}-{photo.stem}.jpg"
        canvas.convert("RGB").save(out, "JPEG", quality=92)

    # story-sized using first hero + official dark logo
    story = Image.new("RGB", (1080, 1920), "#111111")
    hero = square_crop(Image.open(photos[0][0]), 1080)
    story.paste(hero, (0, 420))
    logo = Image.open(LOGOS / "06_Primary_Logo_On_Black_2000.png").convert("RGBA")
    logo.thumbnail((640, 640), Image.Resampling.LANCZOS)
    tmp = Image.new("RGBA", story.size, (0, 0, 0, 0))
    tmp.paste(logo, ((1080 - logo.size[0]) // 2, 80), logo)
    story = Image.alpha_composite(story.convert("RGBA"), tmp).convert("RGB")
    story.save(social / "instagram-story-product-1080x1920.jpg", "JPEG", quality=92)


def make_business_cards() -> None:
    dest = OUT / "06-Stationery"
    dest.mkdir(parents=True, exist_ok=True)
    w, h = 1050, 600  # 3.5x2 @ 300dpi
    # Front — official dark logo
    front = Image.new("RGB", (w, h), "#111111")
    logo = Image.open(LOGOS / "06_Primary_Logo_On_Black_2000.png").convert("RGBA")
    logo.thumbnail((460, 460), Image.Resampling.LANCZOS)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    layer.paste(logo, ((w - logo.size[0]) // 2, 40), logo)
    front = Image.alpha_composite(front.convert("RGBA"), layer).convert("RGB")
    front.save(dest / "business-card-front.png")

    # Back — cream + contact
    back = Image.new("RGB", (w, h), "#FAF8F2")
    icon = Image.open(LOGOS / "02_Primary_Logo_Soft_White_2000.png").convert("RGBA")
    icon.thumbnail((210, 210), Image.Resampling.LANCZOS)
    bl = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bl.paste(icon, (40, 40), icon)
    back = Image.alpha_composite(back.convert("RGBA"), bl)
    d = ImageDraw.Draw(back)
    d.rectangle((280, 48, 1010, 52), fill="#B57A1E")
    back.convert("RGB").save(dest / "business-card-back-base.png")

    # Type the back with reportlab overlay via a small PDF-to-png is heavy;
    # write a PDF card instead and a typed PNG using reportlab raster... use PIL default font for contact? Better: PDF only + keep photo front.
    from PIL import ImageFont

    try:
        font_b = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 22)
        font_s = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 18)
        font_t = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 28)
    except OSError:
        font_b = font_s = font_t = ImageFont.load_default()
    d = ImageDraw.Draw(back)
    x, y = 280, 80
    d.text((x, y), "TASTY TREATS WORLD", font=font_t, fill="#111111")
    d.text((x, y + 50), "786-505-5039", font=font_b, fill="#111111")
    d.text((x, y + 88), "Naples, Florida", font=font_s, fill="#111111")
    d.text((x, y + 122), "@TastyTreatsWorld", font=font_s, fill="#111111")
    d.text((x, y + 156), "tastytreatsworld.com", font=font_s, fill="#111111")
    d.text((x, y + 220), "Chocoflan  ·  Beso de Ángel  ·  Mini desserts", font=font_s, fill="#B57A1E")
    back.convert("RGB").save(dest / "business-card-back.png")
    Path(dest / "business-card-back-base.png").unlink(missing_ok=True)

    c = pdfcanvas.Canvas(str(dest / "business-card.pdf"), pagesize=(3.5 * inch, 2 * inch))
    c.drawImage(str(dest / "business-card-front.png"), 0, 0, 3.5 * inch, 2 * inch)
    c.showPage()
    c.drawImage(str(dest / "business-card-back.png"), 0, 0, 3.5 * inch, 2 * inch)
    c.save()


def make_menu_pdf() -> None:
    dest = OUT / "04-Menu"
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / "TastyTreatsWorld-Menu.pdf"
    c = pdfcanvas.Canvas(str(path), pagesize=letter)
    W, H = letter

    def bg() -> None:
        c.setFillColor(SOFT)
        c.rect(0, 0, W, H, fill=1, stroke=0)
        c.setStrokeColor(GOLD)
        c.setLineWidth(1.2)
        c.rect(28, 28, W - 56, H - 56, fill=0, stroke=1)

    bg()
    logo = LOGOS / "02_Primary_Logo_Soft_White_2000.png"
    c.drawImage(str(logo), W / 2 - 70, H - 168, 140, 140, mask="auto")
    c.setFillColor(GOLD)
    c.setFont("Times-Bold", 11)
    c.drawCentredString(W / 2, H - 186, "MENU  ·  NAPLES, FLORIDA")

    sections = [
        (
            "BESOS DE ÁNGEL CAKES",
            [("6 inch", "$75"), ("8 inch", "$95"), ("10 inch", "$125")],
        ),
        (
            "CHOCOFLAN CAKES",
            [
                ("6 inch — up to 6 people", "$30"),
                ("8 inch — up to 12 people", "$50"),
                ("10 inch — up to 24 people", "$70"),
                ("Two levels (premium)", "$100"),
            ],
        ),
        (
            "TRADITIONAL CAKES",
            [("6 inch", "$50"), ("8 inch", "$65")],
        ),
        (
            "FLAN",
            [("Small", "$35"), ("Large", "$65")],
        ),
        (
            "MINI DESSERTS & SHOOTERS",
            [
                ("12 Beso de Ángel shooters", "$50"),
                ("12 Tres Leches shooters", "$40"),
                ("12 Mini Chocoflan", "$30"),
                ("24 Mini Chocoflan", "$60"),
                ("24 Mini Vanilla Flan", "$60"),
            ],
        ),
        (
            "TRES LECHES  ·  ADD-ONS  ·  DELIVERY",
            [
                ("Tres Leches tray 9×9 in", "$40"),
                ("Cake topper", "$5"),
                ("Delivery", "from $7"),
            ],
        ),
    ]

    y = H - 220
    left = 64
    right = W - 64
    for title, rows in sections:
        c.setFillColor(GOLD)
        c.setFont("Times-Bold", 12)
        c.drawString(left, y, title)
        y -= 8
        c.setStrokeColor(HI_GOLD)
        c.setLineWidth(0.6)
        c.line(left, y, right, y)
        y -= 16
        c.setFillColor(INK)
        c.setFont("Times-Roman", 11)
        for name, price in rows:
            c.drawString(left, y, name)
            c.drawRightString(right, y, price)
            y -= 15
        y -= 10

    c.setFillColor(GOLD)
    c.setFont("Times-Roman", 10)
    c.drawCentredString(W / 2, 52, "786-505-5039   ·   @TastyTreatsWorld   ·   Naples, Florida")
    c.save()

    (dest / "MENU.txt").write_text(
        """TASTY TREATS WORLD — MENU
Naples, Florida  ·  786-505-5039  ·  @TastyTreatsWorld

BESOS DE ÁNGEL CAKES
6 inch $75   8 inch $95   10 inch $125

CHOCOFLAN CAKES
6 inch $30 (up to 6)   8 inch $50 (up to 12)
10 inch $70 (up to 24)   Two levels (premium) $100

TRADITIONAL CAKES
6 inch $50   8 inch $65

FLAN
Small $35   Large $65

MINI DESSERTS & SHOOTERS
12 Beso de Ángel shooters $50
12 Tres Leches shooters $40
12 Mini Chocoflan $30
24 Mini Chocoflan $60
24 Mini Vanilla Flan $60

TRES LECHES tray 9x9 $40
Cake topper $5
Delivery from $7 (varies by distance)
""",
        encoding="utf-8",
    )


def make_guidelines(photos: list[tuple[Path, str]]) -> None:
    dest = OUT / "01-Brand-Guidelines"
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(LOGOS / "00_READ_ME_BRAND_GUIDE.txt", dest / "Official-Brand-Guide.txt")
    (dest / "Instagram-and-Drive-Review.md").write_text(
        """# Tasty Treats World — review (Drive + Instagram)

Shared Drive: https://drive.google.com/drive/folders/1odFGlwKVleO3yf0fO_Sp5G5fA8XLWHGp

## What the Drive contains

1. **Official logos** — original cupcake badge with Beautifully Delicious Script lettering preserved (not a substitute font redraw). Light, dark, one-color gold/black/white, watermark, SVG, Instagram avatars, palette.
2. **Product photography** — Beso de Ángel petal cakes, two-level chocoflans, Ferrero birthday cakes, boxed minis, Mother’s Day toppers, gold boards.
3. **Menu** — priced list plus Mother’s Day flyers.

## Identity

Boutique home bakery. Signature products are **chocoflan** and **Beso de Ángel**, with minis, flan, and tres leches. Presentation is white boxes, gold boards, caramel glaze, and gold toppers. Colors from the official guide: Primary Gold `#B57A1E`, Luxury `#C6932D`, Highlight `#D6A54A`, Black `#111111`, Soft White `#FAF8F2`.

## Instagram / public presence

Handle: [@TastyTreatsWorld](https://www.instagram.com/tastytreatsworld)

The official brand guide notes that a public Linktree still said **Lehigh Acres, FL**, while this package’s contact line is **Naples, Florida**. Use Naples everywhere (Instagram bio, Linktree, flyers) unless pickup is still split.

Recommended bio:

```
Chocoflan · Beso de Ángel · minis
Naples, Florida
786-505-5039  ·  DM to order
```

Put the official `15_Instagram_Profile_1080.png` on the profile. Watermark product photos with `13_Watermark_Gold_20pct.png`.

## Menu (from Drive Word file)

See `04-Menu/TastyTreatsWorld-Menu.pdf`. Mother’s Day flyers in the same folder use slightly higher seasonal prices — keep those as campaign-only.
""",
        encoding="utf-8",
    )

    pdf = dest / "TastyTreatsWorld-Brand-Guidelines.pdf"
    c = pdfcanvas.Canvas(str(pdf), pagesize=letter)
    W, H = letter

    # Cover
    c.setFillColor(INK)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.drawImage(str(LOGOS / "06_Primary_Logo_On_Black_2000.png"), W / 2 - 150, H / 2 - 40, 300, 300, mask="auto")
    c.setFillColor(GOLD)
    c.setFont("Times-Roman", 11)
    c.drawCentredString(W / 2, 150, "BRAND PACKAGE  ·  OFFICIAL ARTWORK FROM DRIVE")
    c.setFillColor(WHITE)
    c.setFont("Times-Roman", 10)
    c.drawCentredString(W / 2, 130, "786-505-5039  ·  Naples, Florida  ·  @TastyTreatsWorld")
    c.showPage()

    # Page 2 logos + colors
    c.setFillColor(SOFT)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Times-Bold", 18)
    c.drawString(48, H - 56, "Official logos & colors")
    c.drawImage(str(LOGOS / "02_Primary_Logo_Soft_White_2000.png"), 48, H - 280, 200, 200, mask="auto")
    c.drawImage(str(LOGOS / "06_Primary_Logo_On_Black_2000.png"), 270, H - 280, 200, 200, mask="auto")
    c.drawImage(str(LOGOS / "14_Cupcake_Icon_Transparent_1200.png"), 490, H - 250, 140, 140, mask="auto")
    c.setFont("Times-Roman", 9)
    c.drawCentredString(148, H - 296, "LIGHT")
    c.drawCentredString(370, H - 296, "DARK")
    c.drawCentredString(560, H - 296, "ICON")
    c.drawImage(str(LOGOS / "17_Brand_Color_Palette.png"), 48, 80, 514, 280)
    c.showPage()

    # Page 3 products
    c.setFillColor(SOFT)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Times-Bold", 18)
    c.drawString(48, H - 56, "Product photography")
    c.setFont("Times-Roman", 11)
    c.drawString(48, H - 78, "From the shared Drive. Use these on the site and Instagram — not stock pastry photos.")
    x, y = 48, H - 300
    for i, (p, cap) in enumerate(photos[:6]):
        col = i % 3
        row = i // 3
        px = 48 + col * 180
        py = H - 300 - row * 200
        c.drawImage(str(p), px, py, 160, 160)
        c.setFont("Times-Roman", 7)
        c.drawString(px, py - 12, cap[:42])
    c.showPage()

    # Page 4 usage
    c.setFillColor(SOFT)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Times-Bold", 18)
    c.drawString(48, H - 56, "How to use the files")
    lines = [
        "Typography: Beautifully Delicious Script for Tasty Treats; Aegean Breeze for WORLD,",
        "menus, and contact. Logo files already contain the original lettering.",
        "",
        "01 transparent — websites and overlays. 02/03 light print. 06/07 black backgrounds.",
        "08–12 one-color (foil, vinyl, embroidery). 14 icon when the wordmark is too small.",
        "15/16 Instagram avatar. 13 gold watermark on every product photo.",
        "",
        "Do not redraw the script. Do not put the black wordmark on a black photo.",
        "Do not replace chocoflan photos with generic macaron/tart stock.",
        "",
        "Contact lockup: 786-505-5039  ·  Naples, Florida  ·  @TastyTreatsWorld",
    ]
    y = H - 90
    c.setFont("Times-Roman", 11)
    for line in lines:
        c.drawString(48, y, line)
        y -= 16
    c.save()


def write_start_here() -> None:
    (OUT / "00-START-HERE.md").write_text(
        """# Tasty Treats World — Brand Package

Official artwork from the shared Google Drive, plus a print menu, lookbook, and social files.

**Phone:** 786-505-5039  
**Location:** Naples, Florida  
**Social:** [@TastyTreatsWorld](https://www.instagram.com/tastytreatsworld)

## Folders

| Folder | Use first |
| --- | --- |
| `02-Official-Logos/` | Source logos (PNG, JPG, SVG). Start with `01`, `02`, `06`, `14`, `15`. |
| `03-Product-Photography/` | Real cakes and minis for the website and feed |
| `04-Menu/` | Priced menu PDF + Mother’s Day flyers |
| `05-Social-Media/` | Avatars, watermark, ready Instagram posts |
| `06-Stationery/` | Business card |
| `01-Brand-Guidelines/` | Colors, type, usage |

## Logo cheat sheet

- Website / labels: `02-Official-Logos/01_Primary_Logo_Transparent_2000.png`
- Light print: `02_Primary_Logo_Soft_White_2000.png`
- Black backgrounds: `06_Primary_Logo_On_Black_2000.png` (white script — readable)
- Tiny avatar: `15_Instagram_Profile_1080.png` or `14_Cupcake_Icon_Transparent_1200.png`
- Photo watermark: `13_Watermark_Gold_20pct.png`

Primary gold `#B57A1E`  ·  Beautifully Delicious Script  ·  Aegean Breeze
""",
        encoding="utf-8",
    )


def write_preview() -> None:
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Tasty Treats World — Brand Package</title>
  <style>
    body { margin:0; font-family: Georgia, serif; background:#FAF8F2; color:#111; }
    header { background:#111; color:#FAF8F2; text-align:center; padding:48px 20px; }
    header img { width:240px; height:240px; }
    a.btn { display:inline-block; margin-top:20px; background:#B57A1E; color:#111; text-decoration:none; padding:12px 22px; letter-spacing:.12em; font-size:13px; font-family:sans-serif; }
    main { max-width:1080px; margin:0 auto; padding:40px 20px 80px; }
    .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:18px; }
    figure { margin:0; background:#fff; padding:16px; }
    img { max-width:100%; height:auto; display:block; }
    figcaption { font-family:sans-serif; font-size:11px; letter-spacing:.12em; text-transform:uppercase; margin-top:10px; }
  </style>
</head>
<body>
  <header>
    <img src="TastyTreatsWorld-Brand-Package/02-Official-Logos/06_Primary_Logo_On_Black_2000.png" alt="Tasty Treats World"/>
    <p>Official brand package from Drive · Naples, Florida</p>
    <a class="btn" href="TastyTreatsWorld-Brand-Package.zip" download>Download .zip</a>
  </header>
  <main>
    <div class="grid">
      <figure><img src="TastyTreatsWorld-Brand-Package/02-Official-Logos/02_Primary_Logo_Soft_White_2000.png"/><figcaption>Primary light</figcaption></figure>
      <figure style="background:#111"><img src="TastyTreatsWorld-Brand-Package/02-Official-Logos/06_Primary_Logo_On_Black_2000.png"/><figcaption>Primary dark</figcaption></figure>
      <figure><img src="TastyTreatsWorld-Brand-Package/03-Product-Photography/chocoflan-two-tier-mothers-day.jpg"/><figcaption>Chocoflan</figcaption></figure>
      <figure><img src="TastyTreatsWorld-Brand-Package/03-Product-Photography/beso-de-angel-petal-white.jpg"/><figcaption>Beso de Ángel</figcaption></figure>
      <figure><img src="TastyTreatsWorld-Brand-Package/03-Product-Photography/mini-flan-box.jpg"/><figcaption>Minis</figcaption></figure>
      <figure><img src="TastyTreatsWorld-Brand-Package/06-Stationery/business-card-front.png"/><figcaption>Card front</figcaption></figure>
    </div>
  </main>
</body>
</html>
"""
    (ROOT / "index.html").write_text(html, encoding="utf-8")


def zip_package() -> None:
    zip_path = ROOT / "TastyTreatsWorld-Brand-Package.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in OUT.rglob("*"):
            if file.is_file():
                zf.write(file, file.relative_to(OUT.parent))


def main() -> None:
    # Keep reconstructed logos from the previous pass
    old_logos = OUT / "02-Logos"
    if old_logos.exists():
        reconstructed = OUT / "08-Reconstructed-Logos"
        if reconstructed.exists():
            shutil.rmtree(reconstructed)
        shutil.move(str(old_logos), str(reconstructed))
    for stale in ("03-Social-Media", "04-Stationery", "05-Colors", "06-Contact"):
        p = OUT / stale
        if p.exists():
            shutil.rmtree(p)

    copy_official_logos()
    photos = copy_lookbook()
    # menu sources
    mdest = OUT / "04-Menu"
    if mdest.exists():
        shutil.rmtree(mdest)
    mdest.mkdir()
    for src in MENU.iterdir():
        if src.is_file():
            shutil.copy2(src, mdest / src.name.replace("🍰 ", ""))
    make_menu_pdf()
    make_social_posts(photos)
    make_business_cards()
    # palette + contact from official
    col = OUT / "07-Colors-Contact"
    col.mkdir(exist_ok=True)
    shutil.copy2(LOGOS / "17_Brand_Color_Palette.png", col / "color-palette.png")
    shutil.copy2(LOGOS / "18_Brand_Contact_Reference.png", col / "contact-reference.png")
    make_guidelines(photos)
    write_start_here()
    write_preview()
    zip_package()
    print("photos", len(photos))
    print("zip", (ROOT / "TastyTreatsWorld-Brand-Package.zip").stat().st_size)


if __name__ == "__main__":
    main()
