#!/usr/bin/env python3
"""Build the Tasty Treats World professional brand package."""

from __future__ import annotations

import math
import os
import shutil
import zipfile
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw, ImageFilter
from fontTools.misc.transform import Transform
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as pdfcanvas

ROOT = Path("/workspace")
FONTS = ROOT / "brand-kit" / "fonts"
OUT = ROOT / "TastyTreatsWorld-Brand-Package"
PREVIEW = ROOT / "preview"

SCRIPT_FONT = FONTS / "GreatVibes-Regular.ttf"
SANS_FONT = FONTS / "JuliusSansOne-Regular.ttf"

# Brand colors
INK = "#1A1410"
WARM_BLACK = "#0C0B0A"
CREAM = "#FBF6F1"
WHITE = "#FFFFFF"
GOLD = "#C9A45C"
GOLD_DEEP = "#A9843F"
BLUSH = "#F4DCE3"
BLUSH_MID = "#E8C5CF"
CHOCOLATE = "#3D2A24"
CARAMEL = "#C4A882"
CHARCOAL = "#2C2623"


class FontFace:
    def __init__(self, path: Path):
        self.font_path = path
        self.font = TTFont(path)
        self.glyph_set = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.units = self.font["head"].unitsPerEm
        self.hmtx = self.font["hmtx"]

    @classmethod
    def load(cls, path: Path) -> "FontFace":
        return cls(path)

    def glyph_name(self, ch: str) -> str:
        return self.cmap.get(ord(ch), ".notdef")

    def advance(self, ch: str, size: float) -> float:
        name = self.glyph_name(ch)
        return self.hmtx[name][0] * (size / self.units)

    def kern(self, left: str, right: str, size: float) -> float:
        g1, g2 = self.glyph_name(left), self.glyph_name(right)
        if "kern" not in self.font:
            return 0.0
        total = 0.0
        for table in self.font["kern"].kernTables:
            total += table.kernTable.get((g1, g2), 0)
        return total * (size / self.units)

    def measure(self, text: str, size: float, tracking: float = 0.0) -> float:
        if not text:
            return 0.0
        width = 0.0
        for i, ch in enumerate(text):
            width += self.advance(ch, size)
            if i + 1 < len(text):
                width += self.kern(ch, text[i + 1], size)
            if i + 1 < len(text):
                width += tracking
        return width

    def text_path(self, text: str, size: float, x: float, y: float, tracking: float = 0.0) -> tuple[str, float]:
        scale = size / self.units
        pen = SVGPathPen(self.glyph_set)
        cursor = 0.0
        for i, ch in enumerate(text):
            name = self.glyph_name(ch)
            tpen = TransformPen(pen, Transform(scale, 0, 0, -scale, x + cursor, y))
            self.glyph_set[name].draw(tpen)
            cursor += self.advance(ch, size)
            if i + 1 < len(text):
                cursor += self.kern(ch, text[i + 1], size) + tracking
        return pen.getCommands(), cursor


def pt(cx: float, cy: float, r: float, deg: float) -> tuple[float, float]:
    """0deg = top, clockwise, SVG y-down."""
    rad = math.radians(deg)
    return cx + r * math.sin(rad), cy - r * math.cos(rad)


def arc_path(cx: float, cy: float, r: float, a0: float, a1: float) -> str:
    sweep = (a1 - a0) % 360
    large = 1 if sweep > 180 else 0
    x0, y0 = pt(cx, cy, r, a0)
    x1, y1 = pt(cx, cy, r, a1)
    return f"M {x0:.3f},{y0:.3f} A {r:.3f} {r:.3f} 0 {large} 1 {x1:.3f},{y1:.3f}"


def cupcake_group(cx: float, cy: float, scale: float, color: str, stroke: float = 2.15) -> str:
    """Line-art cupcake: pleated liner, frosting swirl, cherry + stem.

    Stroke is in local units; the group transform scales it with the drawing.
    """
    return f'''<g transform="translate({cx:.2f} {cy:.2f}) scale({scale:.4f})" fill="none" stroke="{color}" stroke-width="{stroke:.3f}" stroke-linecap="round" stroke-linejoin="round">
  <!-- liner -->
  <path d="M -30,18 L -22,54 Q 0,64 22,54 L 30,18"/>
  <path d="M -30,18 L -24,24 L -18,15 L -12,24 L -6,15 L 0,24 L 6,15 L 12,24 L 18,15 L 24,24 L 30,18"/>
  <path d="M -18,24 L -14,51"/>
  <path d="M -6,24 L -4.5,53"/>
  <path d="M 6,24 L 4.5,53"/>
  <path d="M 18,24 L 14,51"/>
  <!-- frosting swirl -->
  <path d="M -34,18 C -36,6 -24,-4 -14,2 C -8,-10 8,-10 14,2 C 24,-4 36,6 34,18"/>
  <path d="M -22,1 C -22,-12 -10,-20 0,-13 C 8,-24 24,-16 22,0"/>
  <path d="M -8,-12 C -4,-26 12,-30 16,-16 C 18,-26 8,-34 2,-28"/>
  <path d="M 2,-27 C 2,-36 10,-40 14,-32"/>
  <!-- cherry -->
  <circle cx="8" cy="-42" r="6.6"/>
  <path d="M 10,-48 Q 22,-62 30,-52"/>
</g>'''


def text_path_el(d: str, fill: str) -> str:
    return f'<path d="{d}" fill="{fill}"/>'


def arc_text_paths(face: FontFace, text: str, cx: float, cy: float, radius: float, center_deg: float, size: float, tracking: float, fill: str) -> str:
    """Place outlined glyphs along a circle. Tops point toward the center on the bottom arc."""
    width = face.measure(text, size, tracking)
    angular_width = math.degrees(width / radius)
    # Bottom-arc copy reads left → right, so walk counter-clockwise from the left.
    start = center_deg + angular_width / 2
    parts = []
    cursor = 0.0
    for i, ch in enumerate(text):
        gw = face.advance(ch, size)
        mid = cursor + gw / 2
        theta = start - math.degrees(mid / radius)
        x, y = pt(cx, cy, radius, theta)
        rot = theta - 180
        d, _ = face.text_path(ch, size, -gw / 2, 0, 0)
        parts.append(
            f'<g transform="translate({x:.3f} {y:.3f}) rotate({rot:.3f})">{text_path_el(d, fill)}</g>'
        )
        cursor += gw
        if i + 1 < len(text):
            cursor += face.kern(ch, text[i + 1], size) + tracking
    return "\n".join(parts)


def svg_doc(width: int, height: int, body: str, background: str | None = None) -> str:
    bg = f'<rect width="100%" height="100%" fill="{background}"/>' if background else ""
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  {bg}
  {body}
</svg>
'''


def circular_logo(
    script: FontFace,
    sans: FontFace,
    *,
    ink: str,
    gold: str,
    background: str | None,
    glow: bool,
    glow_center: str,
    glow_edge: str,
    secondary: str,
    secondary_curved: bool,
    size: int = 1000,
) -> str:
    cx = cy = size / 2
    ring_r = size * 0.338
    stroke = size * 0.0062
    knockout_fill = background if background else "#000000"

    glow_svg = ""
    if glow:
        glow_svg = f'''
        <radialGradient id="glow" cx="50%" cy="40%" r="44%">
          <stop offset="0%" stop-color="{glow_center}" stop-opacity="0.95"/>
          <stop offset="38%" stop-color="{glow_center}" stop-opacity="0.42"/>
          <stop offset="100%" stop-color="{glow_edge}" stop-opacity="0"/>
        </radialGradient>
        <circle cx="{cx}" cy="{cy}" r="{ring_r * 1.08:.2f}" fill="url(#glow)"/>
        '''

    tasty_size = size * 0.122
    treats_size = size * 0.122
    tasty_w = script.measure("Tasty", tasty_size)
    treats_w = script.measure("Treats", treats_size)
    baseline = size * 0.535
    tasty_x = cx - ring_r - tasty_w * 0.18
    treats_x = cx + ring_r - treats_w * 0.82
    pad = size * 0.018
    tasty_box = (tasty_x - pad, baseline - tasty_size * 0.78, tasty_w + pad * 2, tasty_size * 1.12)
    treats_box = (treats_x - pad, baseline - treats_size * 0.78, treats_w + pad * 2, treats_size * 1.12)

    # Broken gold ring — gaps at 3 o'clock and 9 o'clock so script can cross the frame.
    ring = f'''
      <path d="{arc_path(cx, cy, ring_r, 302, 58)}" fill="none" stroke="{gold}" stroke-width="{stroke:.2f}" stroke-linecap="round"/>
      <path d="{arc_path(cx, cy, ring_r, 122, 238)}" fill="none" stroke="{gold}" stroke-width="{stroke:.2f}" stroke-linecap="round"/>
    '''
    knockouts = ""

    cupcake = cupcake_group(cx, size * 0.395, size / 1000 * 2.05, ink, 2.05)

    tasty_d, _ = script.text_path("Tasty", tasty_size, tasty_x, baseline)
    treats_d, _ = script.text_path("Treats", treats_size, treats_x, baseline)
    wordmark = text_path_el(tasty_d, ink) + text_path_el(treats_d, ink)

    if secondary_curved:
        secondary_svg = arc_text_paths(
            sans,
            secondary,
            cx,
            cy,
            ring_r * 0.80,
            180,
            size * 0.026,
            size * 0.010,
            gold if (background == WARM_BLACK or ink == GOLD or ink == CREAM) else ink,
        )
    else:
        sec_size = size * 0.030
        tracking = size * 0.016
        sec_w = sans.measure(secondary, sec_size, tracking)
        d, _ = sans.text_path(secondary, sec_size, cx - sec_w / 2, size * 0.695, tracking)
        secondary_svg = text_path_el(d, ink)

    body = f"""
    {glow_svg}
    {ring}
    {knockouts}
    {cupcake}
    {wordmark}
    {secondary_svg}
    """
    return svg_doc(size, size, body, background)


def icon_logo(ink: str, gold: str, background: str | None, glow: bool, size: int = 1000) -> str:
    cx = cy = size / 2
    ring_r = size * 0.36
    stroke = size * 0.01
    glow_svg = ""
    if glow:
        glow_svg = f'''
        <radialGradient id="glow" cx="50%" cy="46%" r="48%">
          <stop offset="0%" stop-color="{BLUSH}" stop-opacity="1"/>
          <stop offset="55%" stop-color="{BLUSH}" stop-opacity="0.25"/>
          <stop offset="100%" stop-color="{background or WHITE}" stop-opacity="0"/>
        </radialGradient>
        <circle cx="{cx}" cy="{cy}" r="{ring_r * 1.15:.2f}" fill="url(#glow)"/>
        '''
    ring = f'<circle cx="{cx}" cy="{cy}" r="{ring_r:.2f}" fill="none" stroke="{gold}" stroke-width="{stroke:.2f}"/>'
    cupcake = cupcake_group(cx, size * 0.52, size / 1000 * 2.45, ink, 2.1)
    return svg_doc(size, size, glow_svg + ring + cupcake, background)


def wordmark_svg(script: FontFace, sans: FontFace, ink: str, gold: str, background: str | None, stacked: bool, with_world: bool, size=(1600, 600)) -> str:
    w, h = size
    script_size = 210 if stacked else 200
    d, tw = script.text_path("Tasty Treats", script_size, 0, 0)
    # Recenter after measuring
    d, tw = script.text_path("Tasty Treats", script_size, (w - tw) / 2, h * (0.48 if with_world or stacked else 0.62))
    parts = [text_path_el(d, ink)]
    if with_world:
        sec_size = 28
        tracking = 16
        sw = sans.measure("WORLD", sec_size, tracking)
        sd, _ = sans.text_path("WORLD", sec_size, (w - sw) / 2, h * 0.72, tracking)
        parts.append(text_path_el(sd, ink))
        # gold rule
        y = h * 0.705
        gap = 22
        left = w * 0.22
        right = w * 0.78
        world_left = (w - sw) / 2
        world_right = (w + sw) / 2
        parts.append(f'<line x1="{left}" y1="{y}" x2="{world_left - gap}" y2="{y}" stroke="{gold}" stroke-width="1.4" stroke-linecap="round"/>')
        parts.append(f'<line x1="{world_right + gap}" y1="{y}" x2="{right}" y2="{y}" stroke="{gold}" stroke-width="1.4" stroke-linecap="round"/>')
    return svg_doc(w, h, "\n".join(parts), background)


def horizontal_lockup(script: FontFace, sans: FontFace, ink: str, gold: str, background: str | None) -> str:
    w, h = 1800, 520
    icon = cupcake_group(210, 268, 2.05, ink, 2.05)
    ring = f'<circle cx="210" cy="255" r="168" fill="none" stroke="{gold}" stroke-width="4"/>'
    glow = f'''
    <radialGradient id="glow" cx="210" cy="240" r="190" gradientUnits="userSpaceOnUse">
      <stop offset="0%" stop-color="{BLUSH}" stop-opacity="0.9"/>
      <stop offset="70%" stop-color="{BLUSH}" stop-opacity="0"/>
    </radialGradient>
    <circle cx="210" cy="255" r="180" fill="url(#glow)"/>
    '''
    d, tw = script.text_path("Tasty Treats", 168, 430, 250)
    sd, _ = sans.text_path("NAPLES, FLORIDA   SWEETS & PASTRIES", 18, 445, 330, 8)
    return svg_doc(w, h, glow + ring + icon + text_path_el(d, ink) + text_path_el(sd, ink), background)


def save_svg(path: Path, svg: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")


def rasterize(svg: str, png_path: Path, px: int | None = None) -> None:
    png_path.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"write_to": str(png_path)}
    if px:
        kwargs["output_width"] = px
        kwargs["output_height"] = px
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), **kwargs)


def rasterize_wh(svg: str, png_path: Path, w: int, h: int) -> None:
    png_path.parent.mkdir(parents=True, exist_ok=True)
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(png_path), output_width=w, output_height=h)


def to_jpg(png_path: Path, jpg_path: Path, bg: str) -> None:
    im = Image.open(png_path).convert("RGBA")
    ground = Image.new("RGB", im.size, bg)
    ground.paste(im, mask=im.split()[-1])
    jpg_path.parent.mkdir(parents=True, exist_ok=True)
    ground.save(jpg_path, "JPEG", quality=95)


def add_margin(im: Image.Image, ratio: float = 0.08) -> Image.Image:
    w, h = im.size
    pad = int(max(w, h) * ratio)
    canvas = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    canvas.paste(im, (pad, pad), im)
    return canvas


def make_social_avatar(src: Path, dest: Path, size: int, bg: tuple[int, int, int, int]) -> None:
    im = Image.open(src).convert("RGBA")
    im = im.resize((size, size), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size), bg)
    canvas.alpha_composite(im)
    dest.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(dest)


def make_story(logo: Path, dest: Path) -> None:
    w, h = 1080, 1920
    canvas = Image.new("RGB", (w, h), WARM_BLACK)
    draw = ImageDraw.Draw(canvas)
    # blush glow
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse((190, 430, 890, 1130), fill=(244, 220, 227, 70))
    glow = glow.filter(ImageFilter.GaussianBlur(80))
    canvas.paste(Image.alpha_composite(canvas.convert("RGBA"), glow).convert("RGB"))
    mark = Image.open(logo).convert("RGBA").resize((760, 760), Image.Resampling.LANCZOS)
    canvas.paste(mark, ((w - 760) // 2, 520), mark)
    canvas.save(dest)


def make_highlight(icon_png: Path, dest: Path, label: str, sans: FontFace) -> None:
    size = 1080
    canvas = Image.new("RGB", (size, size), WARM_BLACK)
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((180, 140, 900, 860), fill=(244, 220, 227, 80))
    glow = glow.filter(ImageFilter.GaussianBlur(70))
    base = Image.alpha_composite(canvas.convert("RGBA"), glow)
    mark = Image.open(icon_png).convert("RGBA").resize((640, 640), Image.Resampling.LANCZOS)
    base.alpha_composite(mark, ((size - 640) // 2, 150))
    # label via SVG overlay
    tracking = 10
    d, tw = sans.text_path(label.upper(), 36, (size - sans.measure(label.upper(), 36, tracking)) / 2, 900, tracking)
    svg = svg_doc(size, size, text_path_el(d, CREAM), None)
    tmp = dest.with_suffix(".label.png")
    rasterize_wh(svg, tmp, size, size)
    lab = Image.open(tmp).convert("RGBA")
    base.alpha_composite(lab)
    tmp.unlink(missing_ok=True)
    dest.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(dest)


def make_business_card(front_logo: Path, back_logo: Path, dest_front: Path, dest_back: Path, script: FontFace, sans: FontFace) -> None:
    # 3.5 x 2 in at 300 dpi
    w, h = 1050, 600
    # Front
    front = Image.new("RGB", (w, h), WARM_BLACK)
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((280, 40, 770, 530), fill=(244, 220, 227, 70))
    glow = glow.filter(ImageFilter.GaussianBlur(50))
    f = Image.alpha_composite(front.convert("RGBA"), glow)
    logo = Image.open(front_logo).convert("RGBA").resize((420, 420), Image.Resampling.LANCZOS)
    f.alpha_composite(logo, ((w - 420) // 2, 40))
    d, tw = sans.text_path("NAPLES, FLORIDA", 18, (w - sans.measure("NAPLES, FLORIDA", 18, 8)) / 2, 545, 8)
    svg = svg_doc(w, h, text_path_el(d, GOLD), None)
    tmp = dest_front.with_suffix(".tmp.png")
    rasterize_wh(svg, tmp, w, h)
    f.alpha_composite(Image.open(tmp).convert("RGBA"))
    tmp.unlink(missing_ok=True)
    dest_front.parent.mkdir(parents=True, exist_ok=True)
    f.convert("RGB").save(dest_front)

    # Back
    back = Image.new("RGB", (w, h), CREAM)
    icon = Image.open(back_logo).convert("RGBA").resize((160, 160), Image.Resampling.LANCZOS)
    b = back.convert("RGBA")
    b.alpha_composite(icon, (70, 70))
    lines = [
        (script, "Tasty Treats", 54, 250, 150, 0, INK),
        (sans, "WORLD", 16, 258, 195, 10, GOLD_DEEP),
        (sans, "786-505-5039", 22, 250, 310, 6, INK),
        (sans, "NAPLES, FLORIDA", 18, 250, 360, 8, CHARCOAL),
        (sans, "@TASTYTREATSWORLD", 18, 250, 410, 8, CHARCOAL),
        (sans, "TASTYTREATSWORLD.COM", 16, 250, 460, 6, CHARCOAL),
    ]
    parts = []
    for face, text, size, x, y, tr, color in lines:
        d, _ = face.text_path(text, size, x, y, tr)
        parts.append(text_path_el(d, color))
    parts.append(f'<line x1="250" y1="230" x2="920" y2="230" stroke="{GOLD}" stroke-width="1.2"/>')
    svg = svg_doc(w, h, "\n".join(parts), None)
    rasterize_wh(svg, tmp, w, h)
    b.alpha_composite(Image.open(tmp).convert("RGBA"))
    tmp.unlink(missing_ok=True)
    b.convert("RGB").save(dest_back)

    # Print PDF — 3.5 × 2 in, front then back
    pdf_path = dest_front.parent / "business-card.pdf"
    from reportlab.lib.units import inch as _inch
    c = pdfcanvas.Canvas(str(pdf_path), pagesize=(3.5 * _inch, 2 * _inch))
    c.drawImage(str(dest_front), 0, 0, 3.5 * _inch, 2 * _inch)
    c.showPage()
    c.drawImage(str(dest_back), 0, 0, 3.5 * _inch, 2 * _inch)
    c.save()


def palette_png(dest: Path) -> None:
    swatches = [
        ("Ink", INK),
        ("Warm Black", WARM_BLACK),
        ("Cream", CREAM),
        ("Blush", BLUSH),
        ("Gold", GOLD),
        ("Deep Gold", GOLD_DEEP),
        ("Caramel", CARAMEL),
        ("Chocolate", CHOCOLATE),
    ]
    w, h = 1600, 520
    im = Image.new("RGB", (w, h), WHITE)
    draw = ImageDraw.Draw(im)
    pad = 40
    box_w = (w - pad * 2) // len(swatches)
    for i, (name, hexcol) in enumerate(swatches):
        x = pad + i * box_w
        draw.rounded_rectangle((x + 10, 60, x + box_w - 20, 320), 18, fill=hexcol)
        # labels rendered later as SVG overlay
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp_base = dest.with_suffix(".base.png")
    im.save(tmp_base)
    labels = []
    sans = FontFace.load(SANS_FONT)
    for i, (name, hexcol) in enumerate(swatches):
        x = pad + i * box_w + 18
        d1, _ = sans.text_path(name.upper(), 14, x, 370, 3)
        d2, _ = sans.text_path(hexcol.upper(), 12, x, 400, 2)
        labels.append(text_path_el(d1, INK))
        labels.append(text_path_el(d2, CHARCOAL))
    svg = svg_doc(w, h, "\n".join(labels), None)
    tmp = dest.with_suffix(".lab.png")
    rasterize_wh(svg, tmp, w, h)
    base = Image.open(tmp_base).convert("RGBA")
    base.alpha_composite(Image.open(tmp).convert("RGBA"))
    dest.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(dest, quality=95)
    tmp.unlink(missing_ok=True)
    tmp_base.unlink(missing_ok=True)


def write_pdf_guidelines(logo_light: Path, logo_dark: Path, icon: Path, palette: Path, card_front: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    c = pdfcanvas.Canvas(str(dest), pagesize=letter)
    W, H = letter

    def header(title: str) -> None:
        c.setFillColor(WARM_BLACK)
        c.rect(0, 0, W, H, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.rect(0, H - 8, W, 8, fill=1, stroke=0)
        c.setFillColor(CREAM)
        c.setFont("Times-Roman", 11)
        c.drawString(48, H - 36, "TASTY TREATS WORLD  ·  BRAND GUIDELINES")
        c.setFont("Times-Bold", 22)
        c.drawString(48, H - 68, title)

    def footer(page: int) -> None:
        c.setFillColor(GOLD)
        c.setFont("Times-Roman", 9)
        c.drawString(48, 28, "Confidential  ·  Naples, Florida  ·  @TastyTreatsWorld")
        c.drawRightString(W - 48, 28, str(page))

    # Cover
    c.setFillColor(WARM_BLACK)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.drawImage(str(logo_dark), W / 2 - 160, H / 2 - 40, 320, 320, mask="auto")
    c.setFillColor(GOLD)
    c.setFont("Times-Roman", 11)
    c.drawCentredString(W / 2, 160, "BRAND IDENTITY SYSTEM")
    c.setFillColor(CREAM)
    c.setFont("Times-Roman", 10)
    c.drawCentredString(W / 2, 140, "Naples, Florida  ·  786-505-5039  ·  @TastyTreatsWorld")
    c.showPage()

    # Review
    header("Instagram review")
    c.setFillColor(CREAM)
    review = [
        "Handle reviewed: instagram.com/tastytreatsworld",
        "Public site: tastytreatsworld.com",
        "",
        "Tasty Treats World is a Naples boutique dessert studio. The feed is built around",
        "hand-finished celebration cakes and a signature chocoflan / mini-chocoflan line,",
        "photographed close-up with caramel glaze, gold boards, and pastry-case lighting.",
        "",
        "What is working",
        "• The circular cupcake mark already feels boutique and feminine — keep it as the hero.",
        "• Product photos are the brand: glossy caramel, cream piping, gold leaf, white boxes.",
        "• Voice is warm, bilingual, and proud of the craft (mini chocoflans, hermosuras).",
        "",
        "Gaps this package closes",
        "• Profile art is too delicate at 110px; a stronger ring, blush glow, and icon-only",
        "  avatar are included so the cupcake reads on Instagram, TikTok, and the phone dialer.",
        "• Bio, location, and phone are missing on social. Use: Artisan chocoflans & custom",
        "  cakes — Naples, FL — 786-505-5039 — DM to order.",
        "• Website hero currently uses generic pastry stock. Replace with real chocoflans.",
        "• Watermark @TastyTreatsWorld on every photo with the mark in this kit.",
        "",
        "Positioning line",
        "Handcrafted chocoflans and celebration cakes in Naples, Florida.",
    ]
    y = H - 100
    c.setFont("Times-Roman", 11)
    for line in review:
        if line.startswith("What") or line.startswith("Gaps") or line.startswith("Positioning"):
            c.setFillColor(GOLD)
            c.setFont("Times-Bold", 12)
        elif line.startswith("•"):
            c.setFillColor(CREAM)
            c.setFont("Times-Roman", 11)
        else:
            c.setFillColor(CREAM)
            c.setFont("Times-Roman", 11)
        c.drawString(48, y, line)
        y -= 16
    footer(2)
    c.showPage()

    # Logos
    header("Logo suite")
    c.setFillColor(CREAM)
    c.setFont("Times-Roman", 11)
    c.drawString(48, H - 100, "Primary badge (light) for packaging, site, and print. Dark badge for social and foil.")
    c.setFillColor(WHITE)
    c.roundRect(48, H - 360, 250, 230, 8, fill=1, stroke=0)
    c.drawImage(str(logo_light), 73, H - 345, 200, 200, mask="auto")
    c.setFillColor(CHARCOAL)
    c.roundRect(320, H - 360, 250, 230, 8, fill=1, stroke=0)
    c.drawImage(str(logo_dark), 345, H - 345, 200, 200, mask="auto")
    c.setFillColor(WHITE)
    c.roundRect(592, H - 360, 160, 230, 8, fill=1, stroke=0)
    c.drawImage(str(icon), 612, H - 330, 120, 120, mask="auto")
    c.setFillColor(GOLD)
    c.setFont("Times-Roman", 9)
    c.drawCentredString(173, H - 380, "PRIMARY LIGHT")
    c.drawCentredString(445, H - 380, "PRIMARY DARK")
    c.drawCentredString(672, H - 380, "ICON / AVATAR")
    c.setFillColor(CREAM)
    c.setFont("Times-Roman", 11)
    notes = [
        "Clear space: keep a cupcake-width of empty space around the badge.",
        "Minimum size: badge 120px digital / 0.75 in print. Icon-only below 80px.",
        "Do not recolor the gold ring, stretch the mark, or replace the cupcake with clip art.",
        "Do not place the light badge on busy dessert photos — use the dark badge or the icon.",
        "Live typesetting for new ads should use Beautifully Delicious Script + Aegean Breeze",
        "once licensed. These logo files are outlined and do not require those fonts to open.",
    ]
    y = H - 420
    for line in notes:
        c.drawString(48, y, line)
        y -= 16
    footer(3)
    c.showPage()

    # Color + type
    header("Color & type")
    c.drawImage(str(palette), 48, H - 300, 514, 167)
    c.setFillColor(CREAM)
    c.setFont("Times-Bold", 12)
    c.drawString(48, H - 330, "Typography")
    c.setFont("Times-Roman", 11)
    type_lines = [
        "Primary script (specified): Beautifully Delicious Script — wordmark, headlines, cake toppers.",
        "Secondary (specified): Aegean Breeze — WORLD, SWEETS & PASTRIES, contact, navigation.",
        "Packaged OFL substitutes used to outline this kit: Great Vibes (script) and Julius Sans One",
        "(all-caps boutique sans). License Beautifully Delicious and Aegean Breeze for new typesetting.",
        "Body / UI: Montserrat or the system sans. Never set long paragraphs in the script face.",
    ]
    y = H - 352
    for line in type_lines:
        c.drawString(48, y, line)
        y -= 15
    c.setFillColor(GOLD)
    c.setFont("Times-Bold", 12)
    c.drawString(48, y - 10, "Contact lockup")
    c.setFillColor(CREAM)
    c.setFont("Times-Roman", 11)
    y -= 30
    for line in [
        "Phone   786-505-5039",
        "Location   Naples, Florida",
        "Social   @TastyTreatsWorld",
        "Web   tastytreatsworld.com",
    ]:
        c.drawString(48, y, line)
        y -= 16
    footer(4)
    c.showPage()

    # Stationery
    header("Stationery & social")
    c.drawImage(str(card_front), 48, H - 320, 350, 200)
    c.setFillColor(CREAM)
    c.setFont("Times-Roman", 11)
    social = [
        "Social files included",
        "• Instagram / TikTok avatar 1080px (light and dark)",
        "• Story background 1080×1920 with centered badge",
        "• Highlight covers: Menu, Orders, Reviews, Naples, About",
        "• Watermark mark for product photography",
        "",
        "Recommended Instagram bio",
        "Artisan chocoflans & custom cakes",
        "Naples, Florida",
        "786-505-5039  ·  DM to order",
        "tastytreatsworld.com",
    ]
    y = H - 120
    x = 420
    for line in social:
        c.setFillColor(GOLD if line in ("Social files included", "Recommended Instagram bio") else CREAM)
        c.setFont("Times-Bold" if line in ("Social files included", "Recommended Instagram bio") else "Times-Roman", 11)
        c.drawString(x, y, line)
        y -= 16
    footer(5)
    c.save()


def write_markdown() -> None:
    (OUT / "01-Brand-Guidelines").mkdir(parents=True, exist_ok=True)
    (OUT / "00-START-HERE.md").write_text(
        """# Tasty Treats World — Brand Package

Boutique dessert studio · Naples, Florida  
Phone: 786-505-5039  
Instagram / TikTok: [@TastyTreatsWorld](https://www.instagram.com/tastytreatsworld)  
Web: [tastytreatsworld.com](https://tastytreatsworld.com)

## What’s inside

| Folder | Use |
| --- | --- |
| `01-Brand-Guidelines/` | Review of the Instagram presence + printable PDF system |
| `02-Logos/` | Outlined SVG, transparent PNG, light/dark PNG, JPG |
| `03-Social-Media/` | Avatars, story, highlight covers, watermark |
| `04-Stationery/` | Business card front/back |
| `05-Colors/` | Palette reference |
| `06-Contact/` | Contact lockup |
| `licenses/` | Open-font licenses for the outlined substitutes |

## Logo files to reach for first

- **Website / packaging / print:** `02-Logos/SVG/logo-primary-light.svg`
- **Instagram profile & dark UI:** `02-Logos/PNG-Dark/logo-primary-dark-2048.png`
- **App icon / tiny avatar:** `02-Logos/PNG-Transparent/logo-icon-1024.png`
- **Email / letterhead:** `02-Logos/SVG/logo-horizontal.svg`

All vector logos are **outlined** (no font install required).

## Typefaces

- **Specified primary script:** Beautifully Delicious Script (My Creative Land) — license for new typesetting.
- **Specified secondary:** Aegean Breeze — license for new typesetting.
- **Outlined in this kit:** Great Vibes (OFL) + Julius Sans One (OFL), matched to the cupcake badge you supplied.

## Contact lockup

**786-505-5039**  
Naples, Florida  
@TastyTreatsWorld
""",
        encoding="utf-8",
    )

    (OUT / "01-Brand-Guidelines" / "Instagram-Review.md").write_text(
        """# Instagram review — @tastytreatsworld

Reviewed: [instagram.com/tastytreatsworld](https://www.instagram.com/tastytreatsworld)  
Also referenced: [tastytreatsworld.com](https://tastytreatsworld.com) and public profile mirrors when Instagram required login.

## Snapshot

Tasty Treats World presents as a Naples, Florida boutique bakery. The live mark is already the circular cupcake badge with script “Tasty Treats” and “world” underneath — the same structure refined in this package.

The grid is product-first: mini chocoflans, full caramel-glazed chocoflans, petal-piped white cakes, gold-board minis, and occasion cakes (birthday, Thanksgiving) with gold toppers. Lighting is close, warm, and domestic-kitchen rather than studio seamless. Captions mix English and Spanish and celebrate the pastry itself.

The marketing site uses the line “Delicious Treats for Any Occasion” but currently leads with generic pastry-assortment photography that does not match the chocoflan-forward feed.

## Visual identity (from the feed)

| Token | How it shows up |
| --- | --- |
| Caramel / dulce | Flan tops, glaze, gold boards |
| Chocolate | Cake bases, ganache, Ferrero accents |
| Cream / white | Petal piping, bakery boxes |
| Gold | Cake toppers, pearl décor, the logo ring |
| Blush | Soft glow already in the supplied badge |

## Voice

Warm, proud, handmade, occasion-based. Short product shouts work (“MINI CHOCOFLANS”). Customers already describe the cakes as magical and elegant — lean into that, not into generic “sweets shop” language.

## Gaps

1. **No bio, city, or phone on social.** Orders depend on DMs that people cannot start with confidence.
2. **Badge is too thin at profile size.** Script plus cupcake collapses; use the icon-only avatar from this kit.
3. **Website ≠ feed.** Stock tarts/macarons on the homepage undercut the chocoflan specialty.
4. **Inconsistent watermark.** Some clips have `@tastytreatsworld`, others do not.
5. **Sparse posting cadence** on the public mirrors reviewed — the product can carry a tighter rhythm (process reels, order cutoffs, weekend pickups).

## Immediate profile copy

```
Artisan chocoflans & custom cakes
Naples, Florida
786-505-5039  ·  DM to order
tastytreatsworld.com
```

Highlights to add: Menu · Orders · Reviews · Naples · About.

## How this package maps to the review

The supplied artwork (cupcake, broken gold ring, Beautifully Delicious-style script, Aegean Breeze-style small caps) is treated as the official system. Light and dark badges, an icon that survives 110px, social story/highlights, cards, and a contact lockup with the Naples phone number are all production-ready.
""",
        encoding="utf-8",
    )


def zip_package() -> Path:
    zip_path = ROOT / "TastyTreatsWorld-Brand-Package.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in OUT.rglob("*"):
            if file.is_file():
                zf.write(file, file.relative_to(OUT.parent))
    return zip_path


def write_preview_index(zip_name: str) -> None:
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Tasty Treats World — Brand Package</title>
  <style>
    :root {{ --ink:#1A1410; --cream:#FBF6F1; --gold:#C9A45C; --black:#0C0B0A; --blush:#F4DCE3; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; font-family: Georgia, serif; background: var(--cream); color: var(--ink); }}
    header {{ background: var(--black); color: var(--cream); padding: 72px 24px 56px; text-align:center; }}
    header img {{ width: 280px; height:280px; }}
    h1 {{ font-weight: 400; font-size: 18px; letter-spacing: .4em; text-transform: uppercase; color: var(--gold); }}
    .sub {{ opacity:.8; }}
    a.btn {{ display:inline-block; margin-top:28px; background: var(--gold); color: var(--black); text-decoration:none; padding:14px 28px; letter-spacing:.12em; font-family: sans-serif; font-size:13px; }}
    main {{ max-width: 1080px; margin: 0 auto; padding: 48px 24px 80px; }}
    .grid {{ display:grid; grid-template-columns: repeat(auto-fit,minmax(240px,1fr)); gap: 24px; }}
    figure {{ margin:0; background:#fff; padding:24px; text-align:center; }}
    figure.dark {{ background: var(--black); }}
    img {{ max-width:100%; height:auto; }}
    figcaption {{ font-family: sans-serif; font-size:12px; letter-spacing:.14em; text-transform:uppercase; margin-top:12px; }}
    .contact {{ display:flex; flex-wrap:wrap; gap:24px; justify-content:space-between; margin: 48px 0; padding: 28px; background:#fff; font-family: sans-serif; }}
  </style>
</head>
<body>
  <header>
    <img src="TastyTreatsWorld-Brand-Package/02-Logos/PNG-Dark/logo-primary-dark-1024.png" alt="Tasty Treats World logo"/>
    <h1>Tasty Treats World</h1>
    <p class="sub">Professional brand package · Naples, Florida</p>
    <a class="btn" href="{zip_name}" download>Download brand package (.zip)</a>
  </header>
  <main>
    <div class="contact">
      <div>786-505-5039</div>
      <div>Naples, Florida</div>
      <div>@TastyTreatsWorld</div>
      <div>tastytreatsworld.com</div>
    </div>
    <div class="grid">
      <figure><img src="TastyTreatsWorld-Brand-Package/02-Logos/PNG-Light/logo-primary-light-1024.png"/><figcaption>Primary light</figcaption></figure>
      <figure class="dark"><img src="TastyTreatsWorld-Brand-Package/02-Logos/PNG-Dark/logo-primary-dark-1024.png"/><figcaption>Primary dark</figcaption></figure>
      <figure><img src="TastyTreatsWorld-Brand-Package/02-Logos/PNG-Light/logo-icon-1024.png"/><figcaption>Icon</figcaption></figure>
      <figure><img src="TastyTreatsWorld-Brand-Package/02-Logos/PNG-Light/logo-horizontal-1600.png"/><figcaption>Horizontal</figcaption></figure>
      <figure><img src="TastyTreatsWorld-Brand-Package/04-Stationery/business-card-front.png"/><figcaption>Business card front</figcaption></figure>
      <figure><img src="TastyTreatsWorld-Brand-Package/04-Stationery/business-card-back.png"/><figcaption>Business card back</figcaption></figure>
    </div>
  </main>
</body>
</html>
"""
    (ROOT / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    script = FontFace.load(SCRIPT_FONT)
    sans = FontFace.load(SANS_FONT)

    logos = {
        "logo-primary-light": circular_logo(
            script, sans, ink=INK, gold=GOLD, background=WHITE, glow=True,
            glow_center=BLUSH, glow_edge=WHITE, secondary="WORLD", secondary_curved=False,
        ),
        "logo-primary-cream": circular_logo(
            script, sans, ink=INK, gold=GOLD, background=CREAM, glow=True,
            glow_center=BLUSH, glow_edge=CREAM, secondary="WORLD", secondary_curved=False,
        ),
        "logo-primary-dark": circular_logo(
            script, sans, ink=CREAM, gold=GOLD, background=WARM_BLACK, glow=True,
            glow_center=BLUSH, glow_edge=WARM_BLACK, secondary="SWEETS & PASTRIES",
            secondary_curved=True,
        ),
        "logo-primary-transparent": circular_logo(
            script, sans, ink=INK, gold=GOLD, background=None, glow=True,
            glow_center=BLUSH, glow_edge="#FFFFFF", secondary="WORLD", secondary_curved=False,
        ),
        "logo-mono-black": circular_logo(
            script, sans, ink=INK, gold=INK, background=None, glow=False,
            glow_center=BLUSH, glow_edge=WHITE, secondary="WORLD", secondary_curved=False,
        ),
        "logo-mono-white": circular_logo(
            script, sans, ink=WHITE, gold=WHITE, background=None, glow=False,
            glow_center=BLUSH, glow_edge=WHITE, secondary="WORLD", secondary_curved=False,
        ),
        "logo-gold-dark": circular_logo(
            script, sans, ink=GOLD, gold=GOLD, background=WARM_BLACK, glow=True,
            glow_center=CHOCOLATE, glow_edge=WARM_BLACK, secondary="SWEETS & PASTRIES",
            secondary_curved=True,
        ),
        "logo-icon": icon_logo(INK, GOLD, WHITE, True),
        "logo-icon-transparent": icon_logo(INK, GOLD, None, True),
        "logo-icon-dark": icon_logo(CREAM, GOLD, WARM_BLACK, True),
        "logo-wordmark": wordmark_svg(script, sans, INK, GOLD, WHITE, False, True, (1600, 520)),
        "logo-wordmark-dark": wordmark_svg(script, sans, CREAM, GOLD, WARM_BLACK, False, True, (1600, 520)),
        "logo-horizontal": horizontal_lockup(script, sans, INK, GOLD, WHITE),
        "logo-horizontal-dark": horizontal_lockup(script, sans, CREAM, GOLD, WARM_BLACK),
    }

    svg_dir = OUT / "02-Logos" / "SVG"
    png_t = OUT / "02-Logos" / "PNG-Transparent"
    png_l = OUT / "02-Logos" / "PNG-Light"
    png_d = OUT / "02-Logos" / "PNG-Dark"
    jpg_dir = OUT / "02-Logos" / "JPG"

    sizes = (512, 1024, 2048)

    for name, svg in logos.items():
        save_svg(svg_dir / f"{name}.svg", svg)
        wide = name.startswith("logo-wordmark") or name.startswith("logo-horizontal")
        transparent = "transparent" in name or "mono" in name
        dark = "dark" in name or "gold-dark" in name
        for px in sizes:
            if wide:
                continue
            target = png_t if transparent else (png_d if dark else png_l)
            rasterize(svg, target / f"{name}-{px}.png", px)
        if name in ("logo-wordmark", "logo-horizontal"):
            hpx = 520 if "wordmark" in name else 462
            rasterize_wh(svg, png_l / f"{name}-1600.png", 1600, hpx)
        if name in ("logo-wordmark-dark", "logo-horizontal-dark"):
            hpx = 520 if "wordmark" in name else 462
            rasterize_wh(svg, png_d / f"{name}-1600.png", 1600, hpx)
        if not transparent and not wide:
            png = (png_d if dark else png_l) / f"{name}-1024.png"
            if png.exists():
                to_jpg(png, jpg_dir / f"{name}.jpg", WARM_BLACK if dark else WHITE)

    # Favicon sizes from icon
    icon_svg = logos["logo-icon"]
    for px in (16, 32, 48, 180, 512):
        rasterize(icon_svg, OUT / "02-Logos" / "Favicon" / f"favicon-{px}.png", px)

    # Social
    social = OUT / "03-Social-Media"
    make_social_avatar(png_l / "logo-primary-light-1024.png", social / "instagram-avatar-light-1080.png", 1080, (255, 255, 255, 255))
    make_social_avatar(png_d / "logo-primary-dark-1024.png", social / "instagram-avatar-dark-1080.png", 1080, (12, 11, 10, 255))
    make_social_avatar(png_l / "logo-icon-1024.png", social / "instagram-avatar-icon-1080.png", 1080, (255, 255, 255, 255))
    make_story(png_d / "logo-primary-dark-1024.png", social / "instagram-story-1080x1920.png")
    shutil.copy2(png_t / "logo-icon-transparent-512.png", social / "watermark-icon-512.png")
    for label in ("Menu", "Orders", "Reviews", "Naples", "About"):
        make_highlight(png_d / "logo-icon-dark-1024.png", social / "highlights" / f"highlight-{label.lower()}.png", label, sans)

    # Stationery
    make_business_card(
        png_d / "logo-primary-dark-1024.png",
        png_t / "logo-icon-transparent-1024.png",
        OUT / "04-Stationery" / "business-card-front.png",
        OUT / "04-Stationery" / "business-card-back.png",
        script,
        sans,
    )

    palette_png(OUT / "05-Colors" / "color-palette.png")

    # Contact lockup
    contact_svg = horizontal_lockup(script, sans, INK, GOLD, CREAM)
    # dedicated contact card
    w, h = 1600, 900
    d1, _ = script.text_path("Tasty Treats World", 110, 120, 220)
    lines = [
        sans.text_path("786-505-5039", 32, 130, 400, 10)[0],
        sans.text_path("NAPLES, FLORIDA", 24, 130, 470, 10)[0],
        sans.text_path("@TASTYTREATSWORLD", 24, 130, 540, 10)[0],
        sans.text_path("TASTYTREATSWORLD.COM", 22, 130, 610, 8)[0],
    ]
    cup = cupcake_group(1280, 430, 3.1, INK, 3.0)
    ring = f'<circle cx="1280" cy="410" r="230" fill="none" stroke="{GOLD}" stroke-width="5"/>'
    body = text_path_el(d1, INK) + "".join(text_path_el(d, INK) for d in lines) + ring + cup
    body += f'<line x1="120" y1="280" x2="720" y2="280" stroke="{GOLD}" stroke-width="1.5"/>'
    csvg = svg_doc(w, h, body, CREAM)
    save_svg(OUT / "06-Contact" / "contact-lockup.svg", csvg)
    rasterize_wh(csvg, OUT / "06-Contact" / "contact-lockup.png", w, h)

    write_markdown()
    write_pdf_guidelines(
        png_l / "logo-primary-light-1024.png",
        png_d / "logo-primary-dark-1024.png",
        png_l / "logo-icon-1024.png",
        OUT / "05-Colors" / "color-palette.png",
        OUT / "04-Stationery" / "business-card-front.png",
        OUT / "01-Brand-Guidelines" / "TastyTreatsWorld-Brand-Guidelines.pdf",
    )

    # licenses
    lic = OUT / "licenses"
    lic.mkdir(exist_ok=True)
    shutil.copy2(FONTS / "OFL-GreatVibes.txt", lic / "OFL-GreatVibes.txt")
    shutil.copy2(FONTS / "OFL-JuliusSansOne.txt", lic / "OFL-JuliusSansOne.txt")
    (lic / "FONT-NOTES.txt").write_text(
        "Logo artwork is outlined. Great Vibes and Julius Sans One (SIL Open Font License)\n"
        "were used as production substitutes so files open without commercial fonts.\n"
        "For new typesetting, license Beautifully Delicious Script (My Creative Land)\n"
        "and Aegean Breeze as specified by the brand.\n",
        encoding="utf-8",
    )

    zpath = zip_package()
    write_preview_index(zpath.name)
    print("Wrote", OUT)
    print("Zip", zpath, zpath.stat().st_size)


if __name__ == "__main__":
    main()
