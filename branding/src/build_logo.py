#!/usr/bin/env python3
"""Build Tasty Treats WORLD logo files for print and digital branding."""

from __future__ import annotations

import math
import os
import shutil
import tempfile
from pathlib import Path

import cairosvg
import numpy as np
import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image, ImageFilter
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as pdf_canvas

ROOT = Path(__file__).resolve().parents[1]
FONTS = ROOT / "fonts"
OUT = ROOT / "exports"
VIEW = 1200
CX, CY, RADIUS = 600.0, 545.0, 372.0

COLORS = {
    "ink": "#111111",
    "gold": "#C4A045",
    "gold_on_dark": "#E4C56A",
    "glow": "#EFB6C6",
    "glow_mid": "#F7D6DE",
    "glow_on_dark": "#E59AAD",
    "white": "#FFFFFF",
    "black": "#0B0B0B",
}


def load_font(path: Path, weight: float | None = None) -> TTFont:
    font = TTFont(path)
    if weight is not None and "fvar" in font:
        font = instantiateVariableFont(font, {"wght": weight}, inplace=False)
    return font


def text_to_svg_path(
    ttf_path: Path,
    text: str,
    font_size: float,
    center_x: float,
    baseline_y: float,
    letter_spacing: float = 0.0,
    weight: float | None = None,
) -> str:
    tt = load_font(ttf_path, weight)
    with tempfile.NamedTemporaryFile(suffix=".ttf", delete=False) as tmp:
        tmp_path = tmp.name
        tt.save(tmp_path)
    try:
        blob = hb.Blob.from_file_path(tmp_path)
        face = hb.Face(blob)
        hb_font = hb.Font(face)
        upem = face.upem
        hb_font.scale = (upem, upem)
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(hb_font, buf)
        infos = buf.glyph_infos
        positions = buf.glyph_positions
        scale = font_size / upem
        cursor = 0.0
        glyph_order = tt.getGlyphOrder()
        glyph_set = tt.getGlyphSet()
        gid_to_name = {tt.getGlyphID(n): n for n in glyph_order}
        parts: list[str] = []
        for i, (info, pos) in enumerate(zip(infos, positions)):
            extra = letter_spacing if i < len(infos) - 1 else 0.0
            gx = cursor + pos.x_offset * scale
            gy = pos.y_offset * scale
            name = gid_to_name.get(info.codepoint) or glyph_order[info.codepoint]
            glyph = glyph_set[name]
            svg_pen = SVGPathPen(glyph_set)
            tpen = TransformPen(svg_pen, (scale, 0, 0, -scale, 0, 0))
            glyph.draw(tpen)
            d = svg_pen.getCommands()
            if d:
                parts.append(f'<path transform="translate({gx:.3f} {gy:.3f})" d="{d}"/>')
            cursor += pos.x_advance * scale + extra
        origin_x = center_x - cursor / 2.0
        inner = "\n      ".join(parts)
        return f'<g transform="translate({origin_x:.3f} {baseline_y:.3f})">\n      {inner}\n    </g>'
    finally:
        os.unlink(tmp_path)


def cupcake_mark(stroke: str, stroke_width: float = 4.15, centered: bool = False) -> str:
    sw = stroke_width
    # Lockup sits in the upper half of the ring; icon is centered in the ring.
    transform = (
        "translate(600 545) scale(1.06) translate(-600 -470)"
        if centered
        else "translate(600 428) scale(0.92) translate(-600 -470)"
    )
    return f'''
    <g transform="{transform}"
       fill="none" stroke="{stroke}" stroke-width="{sw}"
       stroke-linecap="round" stroke-linejoin="round">
      <path d="M 476 500 L 450 618 C 450 638 750 638 750 618 L 724 500"/>
      <path d="M 476 500 C 530 518 670 518 724 500"/>
      <path d="M 498 508 L 484 622"/>
      <path d="M 522 512 L 512 626"/>
      <path d="M 546 514 L 540 628"/>
      <path d="M 570 516 L 568 630"/>
      <path d="M 594 516 L 596 630"/>
      <path d="M 618 516 L 624 630"/>
      <path d="M 642 514 L 652 628"/>
      <path d="M 666 512 L 680 624"/>
      <path d="M 690 508 L 708 618"/>
      <path d="
        M 486 498
        C 444 478 452 424 500 416
        C 488 376 520 344 564 350
        C 558 312 598 286 634 304
        C 650 278 694 280 706 314
        C 748 320 764 368 734 400
        C 766 420 756 470 716 488
        C 686 512 528 518 486 498 Z"/>
      <path d="M 508 490 C 478 462 516 432 562 448 C 606 462 634 442 624 414"/>
      <path d="M 536 448 C 520 422 556 396 596 410 C 634 422 656 402 648 378"/>
      <path d="M 568 404 C 558 380 588 358 622 370 C 650 380 664 364 656 346"/>
      <path d="M 596 354 C 592 338 614 326 634 336"/>
      <circle cx="620" cy="292" r="25"/>
      <path d="M 634 274 C 650 244 688 234 708 252"/>
      <path d="M 612 284 C 616 278 624 278 628 284" stroke-width="{sw * 0.85}"/>
    </g>'''


def gold_ring(color: str, width: float = 6.0, full: bool = False) -> str:
    if full:
        return f'''
    <circle cx="{CX}" cy="{CY}" r="{RADIUS}"
      fill="none" stroke="{color}" stroke-width="{width}"/>'''
    circ = 2 * math.pi * RADIUS
    gap_deg = 34.0
    arc_deg = 180.0 - gap_deg
    unit = circ / 360.0
    dash = f"{arc_deg * unit:.3f} {gap_deg * unit:.3f}"
    offset = (arc_deg + gap_deg / 2.0) * unit
    return f'''
    <circle cx="{CX}" cy="{CY}" r="{RADIUS}"
      fill="none" stroke="{color}" stroke-width="{width}"
      stroke-linecap="butt"
      stroke-dasharray="{dash}"
      stroke-dashoffset="{offset:.3f}"/>'''


def glow_ellipse() -> str:
    return f'<ellipse cx="{CX}" cy="400" rx="198" ry="188" fill="url(#glow)"/>'


def defs_block(glow: str, glow_mid: str) -> str:
    return f'''
  <defs>
    <radialGradient id="glow" cx="50%" cy="40%" r="62%">
      <stop offset="0%" stop-color="{glow}" stop-opacity="0.95"/>
      <stop offset="45%" stop-color="{glow_mid}" stop-opacity="0.40"/>
      <stop offset="100%" stop-color="{glow_mid}" stop-opacity="0"/>
    </radialGradient>
  </defs>'''


def wordmark(ink: str) -> str:
    script = text_to_svg_path(
        FONTS / "GreatVibes-Regular.ttf",
        "Tasty Treats",
        font_size=156,
        center_x=CX,
        baseline_y=590,
    )
    world = text_to_svg_path(
        FONTS / "Montserrat-Variable.ttf",
        "WORLD",
        font_size=30,
        center_x=CX,
        baseline_y=648,
        letter_spacing=20,
        weight=580,
    )
    return f'''
    <g fill="{ink}" stroke="none">{script}</g>
    <g fill="{ink}" stroke="none">{world}</g>'''


def svg_document(body: str, background: str | None, glow: str, glow_mid: str, include_glow: bool) -> str:
    bg = f'<rect width="100%" height="100%" fill="{background}"/>' if background else ""
    defs = defs_block(glow, glow_mid) if include_glow else "  <defs></defs>"
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW} {VIEW}" width="{VIEW}" height="{VIEW}">
{defs}
  {bg}
  {body}
</svg>
'''


def logo_body(ink: str, gold: str, with_glow: bool, with_text: bool = True) -> str:
    parts = []
    if with_glow:
        parts.append(glow_ellipse())
    parts.append(gold_ring(gold, full=not with_text))
    parts.append(cupcake_mark(ink, 4.35 if with_text else 5.2, centered=not with_text))
    if with_text:
        parts.append(wordmark(ink))
    return "\n".join(parts)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def sharpen_rgba(img: Image.Image) -> Image.Image:
    alpha = img.getchannel("A")
    rgb = img.convert("RGB").filter(ImageFilter.UnsharpMask(radius=1.25, percent=130, threshold=2))
    out = rgb.convert("RGBA")
    out.putalpha(alpha)
    return out


def rasterize_svg(svg_path: Path, png_path: Path, size: int) -> Image.Image:
    png_path.parent.mkdir(parents=True, exist_ok=True)
    cairosvg.svg2png(
        url=str(svg_path),
        write_to=str(png_path),
        output_width=size,
        output_height=size,
    )
    img = Image.open(png_path).convert("RGBA")
    img = sharpen_rgba(img)
    img.save(png_path, "PNG", optimize=True)
    print(f"raster {png_path.relative_to(ROOT)}")
    return img


def composite_on(img: Image.Image, hex_color: str) -> Image.Image:
    bg = Image.new("RGBA", img.size, hex_color)
    return Image.alpha_composite(bg, img.convert("RGBA")).convert("RGB")


def save_jpg(img: Image.Image, path: Path, quality: int = 95) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(path, "JPEG", quality=quality, subsampling=0, optimize=True)


def save_webp(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "WEBP", quality=95, method=6)


def save_pdf(img: Image.Image, pdf_path: Path, title: str) -> None:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    c = pdf_canvas.Canvas(str(pdf_path), pagesize=letter)
    c.setTitle(title)
    page_w, page_h = letter
    side = 3.25 * 72
    x = (page_w - side) / 2
    y = (page_h - side) / 2
    c.drawImage(ImageReader(img.convert("RGB")), x, y, side, side, mask="auto")
    c.showPage()
    c.save()
    print(f"wrote {pdf_path.relative_to(ROOT)}")


def save_ico(src: Image.Image, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    src.save(dest, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"wrote {dest.relative_to(ROOT)}")


def knockout_near_white(img: Image.Image, threshold: int = 247) -> Image.Image:
    arr = np.array(img.convert("RGBA"))
    rgb = arr[:, :, :3].astype(np.int16)
    mn = rgb.min(axis=2)
    mx = rgb.max(axis=2)
    near = (mn >= threshold) & ((mx - mn) <= 10)
    arr[near, 3] = 0
    soft = (mn >= threshold - 16) & (mn < threshold) & ((mx - mn) <= 12)
    if soft.any():
        dist = (threshold - mn[soft]).astype(np.float32)
        arr[soft, 3] = np.clip((dist / 16.0) * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def knockout_near_black(img: Image.Image, threshold: int = 22) -> Image.Image:
    arr = np.array(img.convert("RGBA"))
    rgb = arr[:, :, :3].astype(np.int16)
    mx = rgb.max(axis=2)
    near = mx <= threshold
    arr[near, 3] = 0
    soft = (mx > threshold) & (mx <= threshold + 16)
    if soft.any():
        dist = (mx[soft] - threshold).astype(np.float32)
        arr[soft, 3] = np.clip((dist / 16.0) * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def process_illustrated() -> None:
    src_dir = Path("/opt/cursor/artifacts/assets")
    dest = OUT / "illustrated"
    dest.mkdir(parents=True, exist_ok=True)
    jobs = [
        ("tasty_treats_logo_white_bg.png", "full-color-white-bg.png", "white"),
        ("tasty_treats_logo_black_bg.png", "full-color-black-bg.png", "black"),
        ("tasty_treats_icon_mark.png", "icon-white-bg.png", "white"),
    ]
    for src_name, dest_name, kind in jobs:
        src = src_dir / src_name
        if not src.exists():
            continue
        img = sharpen_rgba(Image.open(src).convert("RGBA"))
        img.save(dest / dest_name, "PNG", optimize=True)
        if kind == "white":
            knockout_near_white(img).save(dest / dest_name.replace("-white-bg", "-transparent"), "PNG")
            save_jpg(composite_on(img, COLORS["white"]), dest / dest_name.replace(".png", ".jpg"))
        else:
            knockout_near_black(img).save(dest / dest_name.replace("-black-bg", "-transparent-on-dark"), "PNG")
            save_jpg(img, dest / dest_name.replace(".png", ".jpg"))
        print(f"illustrated {dest_name}")


def build() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)

    variants = {
        "full-color-transparent": dict(ink=COLORS["ink"], gold=COLORS["gold"], glow=True, bg=None, gc=COLORS["glow"], gm=COLORS["glow_mid"], text=True),
        "full-color-white": dict(ink=COLORS["ink"], gold=COLORS["gold"], glow=True, bg=COLORS["white"], gc=COLORS["glow"], gm=COLORS["glow_mid"], text=True),
        "on-dark-transparent": dict(ink=COLORS["white"], gold=COLORS["gold_on_dark"], glow=True, bg=None, gc=COLORS["glow_on_dark"], gm=COLORS["glow_on_dark"], text=True),
        "on-dark-black": dict(ink=COLORS["white"], gold=COLORS["gold_on_dark"], glow=True, bg=COLORS["black"], gc=COLORS["glow_on_dark"], gm=COLORS["glow_on_dark"], text=True),
        "mono-black-transparent": dict(ink=COLORS["ink"], gold=COLORS["ink"], glow=False, bg=None, gc=COLORS["glow"], gm=COLORS["glow_mid"], text=True),
        "mono-white-transparent": dict(ink=COLORS["white"], gold=COLORS["white"], glow=False, bg=None, gc=COLORS["glow"], gm=COLORS["glow_mid"], text=True),
        "icon-full-color-transparent": dict(ink=COLORS["ink"], gold=COLORS["gold"], glow=True, bg=None, gc=COLORS["glow"], gm=COLORS["glow_mid"], text=False),
        "icon-on-dark-transparent": dict(ink=COLORS["white"], gold=COLORS["gold_on_dark"], glow=True, bg=None, gc=COLORS["glow_on_dark"], gm=COLORS["glow_on_dark"], text=False),
        "icon-mono-black-transparent": dict(ink=COLORS["ink"], gold=COLORS["ink"], glow=False, bg=None, gc=COLORS["glow"], gm=COLORS["glow_mid"], text=False),
        "icon-mono-white-transparent": dict(ink=COLORS["white"], gold=COLORS["white"], glow=False, bg=None, gc=COLORS["glow"], gm=COLORS["glow_mid"], text=False),
    }

    svg_dir = OUT / "svg"
    png_dir = OUT / "png"
    jpg_dir = OUT / "jpg"
    webp_dir = OUT / "webp"
    pdf_dir = OUT / "pdf"
    svg_paths: dict[str, Path] = {}

    for name, spec in variants.items():
        body = logo_body(spec["ink"], spec["gold"], spec["glow"], spec["text"])
        doc = svg_document(body, spec["bg"], spec["gc"], spec["gm"], spec["glow"])
        path = svg_dir / f"tasty-treats-world-{name}.svg"
        write(path, doc)
        svg_paths[name] = path

    sizes = [512, 1024, 2048]
    masters: dict[str, Image.Image] = {}
    for name, svg_path in svg_paths.items():
        master_path = png_dir / "2048" / f"tasty-treats-world-{name}.png"
        masters[name] = rasterize_svg(svg_path, master_path, 2048)

    print_master = png_dir / "4096" / "tasty-treats-world-full-color-white.png"
    rasterize_svg(svg_paths["full-color-white"], print_master, 4096)
    rasterize_svg(svg_paths["on-dark-black"], png_dir / "4096" / "tasty-treats-world-on-dark-black.png", 4096)
    rasterize_svg(svg_paths["full-color-transparent"], png_dir / "4096" / "tasty-treats-world-full-color-transparent.png", 4096)

    for name, img in masters.items():
        spec = variants[name]
        for size in sizes:
            resized = img if size == 2048 else sharpen_rgba(img.resize((size, size), Image.Resampling.LANCZOS))
            png_path = png_dir / str(size) / f"tasty-treats-world-{name}.png"
            png_path.parent.mkdir(parents=True, exist_ok=True)
            resized.save(png_path, "PNG", optimize=True)
            save_webp(resized, webp_dir / str(size) / f"tasty-treats-world-{name}.webp")
            if spec["bg"] == COLORS["white"]:
                save_jpg(resized, jpg_dir / str(size) / f"tasty-treats-world-{name}.jpg")
            elif spec["bg"] == COLORS["black"]:
                save_jpg(resized, jpg_dir / str(size) / f"tasty-treats-world-{name}.jpg")
            elif spec["ink"] == COLORS["ink"]:
                save_jpg(composite_on(resized, COLORS["white"]), jpg_dir / str(size) / f"tasty-treats-world-{name}-on-white.jpg")
            else:
                save_jpg(composite_on(resized, COLORS["black"]), jpg_dir / str(size) / f"tasty-treats-world-{name}-on-black.jpg")

    save_pdf(Image.open(print_master), pdf_dir / "tasty-treats-world-full-color-white.pdf", "Tasty Treats WORLD")
    save_pdf(Image.open(png_dir / "4096" / "tasty-treats-world-on-dark-black.png"), pdf_dir / "tasty-treats-world-on-dark-black.pdf", "Tasty Treats WORLD on black")
    save_pdf(masters["mono-black-transparent"], pdf_dir / "tasty-treats-world-mono-black.pdf", "Tasty Treats WORLD one-color")
    save_pdf(masters["icon-full-color-transparent"], pdf_dir / "tasty-treats-world-icon.pdf", "Tasty Treats WORLD icon")

    save_ico(masters["icon-full-color-transparent"], OUT / "ico" / "tasty-treats-world-favicon.ico")
    for size in (180, 192, 512):
        src = sharpen_rgba(masters["icon-full-color-transparent"].resize((size, size), Image.Resampling.LANCZOS))
        dest = OUT / "app-icons" / f"apple-touch-icon-{size}.png"
        dest.parent.mkdir(parents=True, exist_ok=True)
        composite_on(src, COLORS["white"]).save(dest, "PNG", optimize=True)

    # Social square
    social = sharpen_rgba(masters["full-color-white"].resize((1080, 1080), Image.Resampling.LANCZOS))
    social_path = OUT / "social" / "instagram-1080.png"
    social_path.parent.mkdir(parents=True, exist_ok=True)
    social.save(social_path, "PNG", optimize=True)
    save_jpg(social, OUT / "social" / "instagram-1080.jpg")
    dark_social = sharpen_rgba(masters["on-dark-black"].resize((1080, 1080), Image.Resampling.LANCZOS))
    dark_social.save(OUT / "social" / "instagram-1080-dark.png", "PNG", optimize=True)
    save_jpg(dark_social, OUT / "social" / "instagram-1080-dark.jpg")

    banner = Image.new("RGB", (1200, 630), COLORS["white"])
    mark = sharpen_rgba(masters["full-color-transparent"].resize((560, 560), Image.Resampling.LANCZOS))
    banner.paste(mark, ((1200 - 560) // 2, (630 - 560) // 2), mark)
    banner.save(OUT / "social" / "og-image-1200x630.jpg", "JPEG", quality=95, subsampling=0)

    process_illustrated()
    print("done")


if __name__ == "__main__":
    build()
