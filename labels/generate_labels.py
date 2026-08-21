#!/usr/bin/env python3
"""Print-ready bakery box labels for Tasty Treats World.

Generates 2-inch artwork for:
  - Avery 22806  (2\" square, 12-up US Letter)
  - Avery 22807  (2\" round, 12-up US Letter)

QR codes currently encode QR_URL. Change that constant and re-run
this script if the destination should be Instagram, a review page, or
another site.
"""

from __future__ import annotations

import io
import math
from pathlib import Path

import cairosvg
import segno
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as pdf_canvas

ROOT = Path(__file__).resolve().parent
FONT_DIR = ROOT / "fonts"
OUT = ROOT / "output"

QR_URL = "https://tastytreatsworld.com/"
BRAND_SCRIPT = "Tasty Treats"
BRAND_MARK = "WORLD"
TAGLINE = "THANK YOU"
SQUARE_PROMPT = "SCAN TO CONNECT"
ROUND_PROMPT = "HANDMADE WITH LOVE"

# Palette sampled from the existing logo / QR artwork.
ESPRESSO = (14, 10, 8)
CHOCOLATE = (44, 24, 16)
CHARCOAL = (46, 38, 34)
GOLD = (196, 163, 90)
GOLD_LIGHT = (232, 213, 163)
GOLD_DEEP = (140, 106, 47)
CREAM = (246, 239, 228)
IVORY = (252, 248, 241)
CHERRY = (148, 48, 48)

DPI = 600
LABEL_IN = 2.0
PX = int(LABEL_IN * DPI)  # 1200

FONT_SCRIPT = FONT_DIR / "GreatVibes-Regular.ttf"
FONT_SERIF = FONT_DIR / "Cinzel-Regular.ttf"


def hex_rgb(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def load_font(path: Path, size: float) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def center_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill,
    tracking: int = 0,
) -> None:
    """Draw text centered on xy. tracking is extra px between characters."""
    cx, cy = xy
    if tracking == 0:
        draw.text((cx, cy), text, font=font, fill=fill, anchor="mm")
        return
    widths = []
    for ch in text:
        bbox = draw.textbbox((0, 0), ch, font=font)
        widths.append(bbox[2] - bbox[0])
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x + w / 2, cy), ch, font=font, fill=fill, anchor="mm")
        x += w + tracking


def rounded_rect(draw, box, radius, fill=None, outline=None, width=1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def cupcake_svg(size: int, stroke: str, gold: str, cherry: str, ring: bool = True) -> bytes:
    """Line-art cupcake in a gold double ring, matching the brand mark."""
    ring_svg = ""
    if ring:
        ring_svg = f"""
  <circle cx="100" cy="100" r="96" fill="url(#spot)"/>
  <circle cx="100" cy="100" r="93.5" fill="none" stroke="url(#gold)" stroke-width="2.4"/>
  <circle cx="100" cy="100" r="88.2" fill="none" stroke="url(#gold)" stroke-width="0.7" stroke-opacity="0.9"/>
"""
    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="{size}" height="{size}">
  <defs>
    <linearGradient id="gold" x1="18" y1="12" x2="186" y2="190" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="{hex_rgb(GOLD_LIGHT)}"/>
      <stop offset="48%" stop-color="{gold}"/>
      <stop offset="100%" stop-color="{hex_rgb(GOLD_DEEP)}"/>
    </linearGradient>
    <radialGradient id="spot" cx="50%" cy="42%" r="48%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.92"/>
      <stop offset="70%" stop-color="#f3eadc" stop-opacity="0.55"/>
      <stop offset="100%" stop-color="#e7dcc8" stop-opacity="0.0"/>
    </radialGradient>
  </defs>
  {ring_svg}
  <!-- cherry stem -->
  <path d="M100.5 40 C109 31, 120 30, 123 38"
        fill="none" stroke="{stroke}" stroke-width="2.15" stroke-linecap="round"/>
  <!-- cherry -->
  <circle cx="100" cy="50" r="8.6" fill="{cherry}" stroke="{stroke}" stroke-width="1.5"/>
  <circle cx="97.1" cy="47.6" r="2.15" fill="#f7d6d0" fill-opacity="0.9"/>

  <!-- frosting swirl (tall peak, line-art with a cream fill) -->
  <path d="
      M 70 112
      C 58 112, 54 98, 64 92
      C 58 80, 70 66, 82 74
      C 84 58, 98 50, 106 64
      C 112 50, 132 52, 132 70
      C 144 66, 152 82, 142 92
      C 154 98, 150 114, 136 114
      C 122 122, 80 122, 70 112 Z"
        fill="{hex_rgb(IVORY)}" fill-opacity="0.92" stroke="{stroke}"
        stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/>
  <path d="M 78 98 C 90 88, 114 88, 124 100"
        fill="none" stroke="{stroke}" stroke-width="1.5" stroke-linecap="round" opacity="0.85"/>
  <path d="M 92 80 C 100 72, 114 74, 118 84"
        fill="none" stroke="{stroke}" stroke-width="1.3" stroke-linecap="round" opacity="0.78"/>

  <!-- liner -->
  <path d="
      M 73 114
      C 80 120, 120 120, 127 114
      L 120 156
      Q 100 165, 80 156 Z"
        fill="{hex_rgb(IVORY)}" fill-opacity="0.92" stroke="{stroke}"
        stroke-width="2.15" stroke-linejoin="round" stroke-linecap="round"/>
  <!-- pleats -->
  <path d="M 81 118 L 85 154" fill="none" stroke="{stroke}" stroke-width="1.3" stroke-linecap="round" opacity="0.85"/>
  <path d="M 91 120 L 93 157" fill="none" stroke="{stroke}" stroke-width="1.3" stroke-linecap="round" opacity="0.85"/>
  <path d="M 100 121 L 100 159" fill="none" stroke="{stroke}" stroke-width="1.3" stroke-linecap="round" opacity="0.9"/>
  <path d="M 109 120 L 107 157" fill="none" stroke="{stroke}" stroke-width="1.3" stroke-linecap="round" opacity="0.85"/>
  <path d="M 119 118 L 115 154" fill="none" stroke="{stroke}" stroke-width="1.3" stroke-linecap="round" opacity="0.85"/>
</svg>
"""
    return svg.encode("utf-8")


def rasterize_svg(svg_bytes: bytes, size: int) -> Image.Image:
    png = cairosvg.svg2png(bytestring=svg_bytes, output_width=size, output_height=size)
    return Image.open(io.BytesIO(png)).convert("RGBA")


def draw_brand_badge(size: int, dark: bool = False, ring: bool = True) -> Image.Image:
    """Circular logo: gold ring, cupcake, script name, WORLD."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    stroke = hex_rgb(IVORY if dark else CHARCOAL)
    cup = rasterize_svg(
        cupcake_svg(size, stroke=stroke, gold=hex_rgb(GOLD), cherry=hex_rgb(CHERRY), ring=ring),
        size,
    )
    img.alpha_composite(cup)

    draw = ImageDraw.Draw(img)
    script_size = size * (0.155 if ring else 0.175)
    mark_size = size * (0.048 if ring else 0.055)
    script = load_font(FONT_SCRIPT, script_size)
    mark = load_font(FONT_SERIF, mark_size)
    script_fill = IVORY if dark else CHARCOAL
    mark_fill = GOLD_LIGHT if dark else GOLD_DEEP

    # Script sits across the lower third of the ring, as in the source logo.
    center_text(draw, (size / 2, size * 0.73), BRAND_SCRIPT, script, script_fill)
    center_text(draw, (size / 2, size * 0.845), BRAND_MARK, mark, mark_fill, tracking=int(size * 0.018))
    return img


def qr_matrix() -> tuple[list[list[bool]], int]:
    qr = segno.make(QR_URL, error="h")
    matrix = [list(row) for row in qr.matrix]
    return matrix, len(matrix)


def is_finder(row: int, col: int, n: int) -> bool:
    in_tl = row < 7 and col < 7
    in_tr = row < 7 and col >= n - 7
    in_bl = row >= n - 7 and col < 7
    return in_tl or in_tr or in_bl


def draw_finder(draw: ImageDraw.ImageDraw, x: int, y: int, module: float, dark, light) -> None:
    outer = module * 7
    pad = module * 0.08
    r = module * 0.9
    rounded_rect(draw, (x + pad, y + pad, x + outer - pad, y + outer - pad), r, fill=dark)
    inner = module
    rounded_rect(
        draw,
        (x + inner, y + inner, x + outer - inner, y + outer - inner),
        r * 0.7,
        fill=light,
    )
    eye = module * 2.15
    inset = (outer - eye) / 2
    rounded_rect(draw, (x + inset, y + inset, x + inset + eye, y + inset + eye), r * 0.45, fill=dark)


def render_qr(size: int, dark=CHOCOLATE, light=IVORY, dotty: bool = True) -> Image.Image:
    """High-contrast QR with slightly rounded modules for a pastry-shop look."""
    matrix, n = qr_matrix()
    quiet = 3
    total = n + quiet * 2
    img = Image.new("RGB", (size, size), light)
    draw = ImageDraw.Draw(img)
    module = size / total
    origin = quiet * module

    # Finder patterns first.
    finders = [(0, 0), (0, n - 7), (n - 7, 0)]
    for fr, fc in finders:
        draw_finder(draw, origin + fc * module, origin + fr * module, module, dark, light)

    radius = module * (0.48 if dotty else 0.22)
    for r, row in enumerate(matrix):
        for c, on in enumerate(row):
            if not on or is_finder(r, c, n):
                continue
            x0 = origin + c * module
            y0 = origin + r * module
            inset = module * 0.07
            box = (x0 + inset, y0 + inset, x0 + module - inset, y0 + module - inset)
            if dotty:
                draw.ellipse(box, fill=dark)
            else:
                rounded_rect(draw, box, radius, fill=dark)
    return img.convert("RGBA")


def double_gold_frame(draw: ImageDraw.ImageDraw, box, inset: float) -> None:
    x0, y0, x1, y1 = box
    w_outer = max(2, int(inset * 0.18))
    w_inner = max(1, int(inset * 0.07))
    rounded_rect(draw, (x0, y0, x1, y1), inset * 0.35, outline=GOLD, width=w_outer)
    pad = inset * 0.42
    rounded_rect(
        draw,
        (x0 + pad, y0 + pad, x1 - pad, y1 - pad),
        inset * 0.22,
        outline=GOLD_DEEP,
        width=w_inner,
    )


def make_square_label() -> Image.Image:
    """Avery 22806 — cream bakery seal, logo on top, QR below."""
    img = Image.new("RGB", (PX, PX), CREAM)
    draw = ImageDraw.Draw(img)

    margin = PX * 0.045
    double_gold_frame(draw, (margin, margin, PX - margin, PX - margin), PX * 0.06)

    # Soft inner panel
    inner = margin + PX * 0.035
    rounded_rect(
        draw,
        (inner, inner, PX - inner, PX - inner),
        PX * 0.04,
        outline=GOLD_LIGHT,
        width=max(1, PX // 400),
    )

    badge = draw_brand_badge(int(PX * 0.40), dark=False)
    badge_x = (PX - badge.width) // 2
    badge_y = int(PX * 0.042)
    img.paste(badge, (badge_x, badge_y), badge)

    # Hairline divider between seal and QR.
    div_y = int(PX * 0.455)
    draw.line((PX * 0.22, div_y, PX * 0.78, div_y), fill=GOLD, width=max(1, PX // 500))

    qr_size = int(PX * 0.42)
    qr = render_qr(qr_size, dark=CHOCOLATE, light=IVORY, dotty=True)
    qr_x = (PX - qr_size) // 2
    qr_y = int(PX * 0.478)
    # Gold hairline around the QR so it reads as a printed plate.
    pad = int(PX * 0.012)
    rounded_rect(
        draw,
        (qr_x - pad, qr_y - pad, qr_x + qr_size + pad, qr_y + qr_size + pad),
        pad * 1.4,
        fill=IVORY,
        outline=GOLD,
        width=max(2, PX // 350),
    )
    img.paste(qr, (qr_x, qr_y), qr)

    prompt = load_font(FONT_SERIF, PX * 0.032)
    url_font = load_font(FONT_SERIF, PX * 0.026)
    center_text(draw, (PX / 2, PX * 0.935), SQUARE_PROMPT, prompt, GOLD_DEEP, tracking=int(PX * 0.006))
    center_text(
        draw,
        (PX / 2, PX * 0.968),
        "tastytreatsworld.com",
        url_font,
        CHARCOAL,
        tracking=int(PX * 0.002),
    )
    return img


def make_round_label() -> Image.Image:
    """Avery 22807 — chocolate medallion clipped to a 2\" circle."""
    img = Image.new("RGBA", (PX, PX), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx = cy = PX / 2
    r = PX / 2 - 1

    # Full-bleed chocolate, then cream inner disc.
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=ESPRESSO)
    gold_outer = r - PX * 0.018
    gold_inner = r - PX * 0.048
    draw.ellipse(
        (cx - gold_outer, cy - gold_outer, cx + gold_outer, cy + gold_outer),
        outline=GOLD,
        width=max(3, int(PX * 0.012)),
    )
    draw.ellipse(
        (cx - gold_inner, cy - gold_inner, cx + gold_inner, cy + gold_inner),
        outline=GOLD_LIGHT,
        width=max(1, int(PX * 0.004)),
    )

    cream_r = r - PX * 0.07
    draw.ellipse(
        (cx - cream_r, cy - cream_r, cx + cream_r, cy + cream_r),
        fill=CREAM,
    )

    # Ring lives on the label itself, so the mark omits a second gold circle.
    badge = draw_brand_badge(int(PX * 0.34), dark=False, ring=False)
    img.paste(badge, ((PX - badge.width) // 2, int(PX * 0.175)), badge)

    qr_size = int(PX * 0.36)
    qr = render_qr(qr_size, dark=CHOCOLATE, light=IVORY, dotty=True)
    qr_x = (PX - qr_size) // 2
    qr_y = int(PX * 0.528)
    pad = int(PX * 0.01)
    rounded_rect(
        draw,
        (qr_x - pad, qr_y - pad, qr_x + qr_size + pad, qr_y + qr_size + pad),
        pad * 1.6,
        fill=IVORY,
        outline=GOLD,
        width=max(2, PX // 400),
    )
    img.paste(qr, (qr_x, qr_y), qr)

    # Arc caption along the bottom of the cream disc.
    draw_text_on_arc(
        img,
        ROUND_PROMPT,
        load_font(FONT_SERIF, PX * 0.038),
        center=(cx, cy),
        radius=cream_r - PX * 0.055,
        start_angle=210,
        end_angle=330,
        fill=GOLD_DEEP,
    )
    return img


def draw_text_on_arc(
    img: Image.Image,
    text: str,
    font: ImageFont.FreeTypeFont,
    center: tuple[float, float],
    radius: float,
    start_angle: float,
    end_angle: float,
    fill,
) -> None:
    """Place characters along the lower arc (angles in degrees, 0 = 3 o'clock)."""
    probe = ImageDraw.Draw(img)
    widths = []
    for ch in text:
        bbox = probe.textbbox((0, 0), ch, font=font)
        widths.append(max(1, bbox[2] - bbox[0]))
    total = sum(widths)
    span = math.radians(end_angle - start_angle)
    # Center the string on the arc.
    # Walk from start_angle with arc-length proportional to glyph width.
    cx, cy = center
    angle = math.radians(start_angle)
    # Extra leading/trailing space is already in start/end.
    for ch, w in zip(text, widths):
        delta = span * (w / total)
        mid = angle + delta / 2
        # PIL y grows down; convert math angle (CCW from +x) accordingly.
        x = cx + radius * math.cos(mid)
        y = cy + radius * math.sin(mid)
        rotation = -math.degrees(mid) - 90
        glyph = Image.new("RGBA", (int(w * 3) + 40, int(font.size * 3) + 40), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glyph)
        gdraw.text((glyph.width / 2, glyph.height / 2), ch, font=font, fill=fill, anchor="mm")
        glyph = glyph.rotate(rotation, resample=Image.Resampling.BICUBIC, expand=True)
        img.alpha_composite(glyph, (int(x - glyph.width / 2), int(y - glyph.height / 2)))
        angle += delta


def avery_22806_positions() -> list[tuple[float, float]]:
    """US Letter, 3x4, 2\" squares butted together (print-to-the-edge)."""
    left, top = 1.25, 1.50
    pitch = 2.00
    cells = []
    for row in range(4):
        for col in range(3):
            cells.append((left + col * pitch, top + row * pitch))
    return cells


def avery_22807_positions() -> list[tuple[float, float]]:
    """US Letter, 3x4, 2\" circles with published Avery 22807 pitch."""
    left, top = 0.625, 0.625
    x_pitch, y_pitch = 2.625, 2.5833
    cells = []
    for row in range(4):
        for col in range(3):
            cells.append((left + col * x_pitch, top + row * y_pitch))
    return cells


def save_png(img: Image.Image, path: Path, dpi: int = DPI) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG", dpi=(dpi, dpi))


def sheet_pdf(
    path: Path,
    label: Image.Image,
    positions: list[tuple[float, float]],
    round_clip: bool,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    c = pdf_canvas.Canvas(str(path), pagesize=letter)
    c.setTitle(path.stem)
    c.setAuthor("Tasty Treats World")
    work = label.convert("RGBA")
    if round_clip:
        mask = Image.new("L", work.size, 0)
        ImageDraw.Draw(mask).ellipse((0, 0, work.size[0] - 1, work.size[1] - 1), fill=255)
        bg = Image.new("RGB", work.size, (255, 255, 255))
        bg.paste(work, mask=mask)
        work_rgb = bg
    else:
        work_rgb = work.convert("RGB")
    buf = io.BytesIO()
    work_rgb.save(buf, format="PNG", dpi=(DPI, DPI))
    buf.seek(0)
    reader = ImageReader(buf)
    for x, y in positions:
        # reportlab origin is bottom-left.
        pdf_y = letter[1] - (y * 72) - (LABEL_IN * 72)
        c.drawImage(
            reader,
            x * 72,
            pdf_y,
            width=LABEL_IN * 72,
            height=LABEL_IN * 72,
            mask="auto",
            preserveAspectRatio=True,
            anchor="c",
        )
    c.showPage()
    c.save()


def make_preview_board(square: Image.Image, round_label: Image.Image) -> Image.Image:
    """Side-by-side design board for reviewing both labels at once."""
    pad = int(PX * 0.18)
    width = PX * 2 + pad * 3
    height = PX + pad * 2 + int(PX * 0.22)
    board = Image.new("RGB", (width, height), (32, 24, 20))
    draw = ImageDraw.Draw(board)
    title = load_font(FONT_SCRIPT, PX * 0.09)
    sub = load_font(FONT_SERIF, PX * 0.028)
    center_text(draw, (width / 2, pad * 0.42), "Tasty Treats World", title, GOLD_LIGHT)
    center_text(draw, (width / 2, pad * 0.72), "BAKERY BOX LABELS  ·  2 INCH", sub, GOLD, tracking=6)

    sq = square.convert("RGB")
    rnd = Image.new("RGB", (PX, PX), (32, 24, 20))
    rnd.paste(round_label, mask=round_label.split()[-1])

    # Drop shadows
    def paste_with_shadow(base, face, xy):
        shadow = Image.new("RGBA", (PX + 24, PX + 24), (0, 0, 0, 0))
        sdraw = ImageDraw.Draw(shadow)
        if face is rnd:
            sdraw.ellipse((12, 16, PX + 12, PX + 16), fill=(0, 0, 0, 110))
        else:
            sdraw.rounded_rectangle((12, 16, PX + 12, PX + 16), 18, fill=(0, 0, 0, 110))
        shadow = shadow.filter(ImageFilter.GaussianBlur(10))
        base.paste(shadow, (xy[0] - 12, xy[1] - 12), shadow)
        base.paste(face, xy)

    paste_with_shadow(board, sq, (pad, pad))
    paste_with_shadow(board, rnd, (pad * 2 + PX, pad))

    caption = load_font(FONT_SERIF, PX * 0.03)
    center_text(draw, (pad + PX / 2, pad + PX + PX * 0.08), "SQUARE  ·  AVERY 22806", caption, GOLD_LIGHT, tracking=4)
    center_text(
        draw,
        (pad * 2 + PX + PX / 2, pad + PX + PX * 0.08),
        "ROUND  ·  AVERY 22807",
        caption,
        GOLD_LIGHT,
        tracking=4,
    )
    return board


def make_box_mockup(square: Image.Image, round_label: Image.Image) -> Image.Image:
    """Simple pastry-box mockup showing where each sticker would sit."""
    w, h = 1800, 1200
    img = Image.new("RGB", (w, h), (40, 30, 24))
    draw = ImageDraw.Draw(img)

    # Kraft box body
    box = (280, 260, 1520, 980)
    draw.rounded_rectangle(box, 18, fill=(186, 142, 90), outline=(120, 84, 48), width=4)
    # Lid seam
    draw.line((280, 430, 1520, 430), fill=(120, 84, 48), width=3)
    # Twine
    draw.line((280, 700, 1520, 700), fill=(245, 236, 214), width=10)
    draw.line((900, 260, 900, 980), fill=(245, 236, 214), width=10)
    draw.ellipse((840, 640, 960, 760), outline=(245, 236, 214), width=8)

    sq = square.resize((320, 320), Image.Resampling.LANCZOS)
    img.paste(sq, (1080, 300))

    rnd = round_label.resize((260, 260), Image.Resampling.LANCZOS)
    img.paste(rnd, (360, 520), rnd)

    title = load_font(FONT_SCRIPT, 64)
    sub = load_font(FONT_SERIF, 22)
    center_text(draw, (w / 2, 90), "On the pastry box", title, GOLD_LIGHT)
    center_text(
        draw,
        (w / 2, 150),
        "SQUARE ON THE LID   ·   ROUND ON THE SIDE",
        sub,
        GOLD,
        tracking=5,
    )
    cap = load_font(FONT_SERIF, 18)
    center_text(draw, (1240, 650), "AVERY 22806", cap, (70, 48, 28), tracking=3)
    center_text(draw, (490, 820), "AVERY 22807", cap, (70, 48, 28), tracking=3)
    return img


def generate_all() -> dict[str, Path]:
    OUT.mkdir(parents=True, exist_ok=True)
    square = make_square_label()
    round_label = make_round_label()
    badge = draw_brand_badge(1200, dark=False)
    badge_card = Image.new("RGB", (1200, 1200), CREAM)
    badge_card.paste(badge, mask=badge.split()[-1])
    qr = render_qr(800)

    paths = {
        "square": OUT / "label_square_2in_avery_22806.png",
        "round": OUT / "label_round_2in_avery_22807.png",
        "badge": OUT / "logo_badge.png",
        "qr": OUT / "qr_tastytreatsworld.png",
        "preview": OUT / "design_preview.png",
        "mockup": OUT / "box_mockup.png",
        "sheet_square": OUT / "avery_22806_print_sheet.pdf",
        "sheet_round": OUT / "avery_22807_print_sheet.pdf",
    }
    save_png(square, paths["square"])
    save_png(round_label, paths["round"])
    save_png(badge_card, paths["badge"])
    save_png(qr, paths["qr"])
    save_png(make_preview_board(square, round_label), paths["preview"], dpi=150)
    save_png(make_box_mockup(square, round_label), paths["mockup"], dpi=150)
    sheet_pdf(paths["sheet_square"], square, avery_22806_positions(), round_clip=False)
    sheet_pdf(paths["sheet_round"], round_label, avery_22807_positions(), round_clip=True)
    return paths


if __name__ == "__main__":
    generated = generate_all()
    for name, path in generated.items():
        print(f"{name:14s}  {path}  ({path.stat().st_size} bytes)")
