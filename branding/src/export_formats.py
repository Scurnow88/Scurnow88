#!/usr/bin/env python3
"""Convert the original Tasty Treats WORLD lockup into branding formats.

No redraw, no crop, no recolor. White becomes transparent; black ink becomes
white for dark grounds. Everything else stays the original pixels.
"""

from __future__ import annotations

import base64
import shutil
from pathlib import Path

import numpy as np
import vtracer
from PIL import Image, ImageFilter
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as pdf_canvas

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "original" / "tasty-treats-world-source.png"
OUT = ROOT / "exports"

WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)


def load_source() -> Image.Image:
    return Image.open(SOURCE).convert("RGBA")


def mild_sharpen(img: Image.Image) -> Image.Image:
    return img.filter(ImageFilter.UnsharpMask(radius=0.8, percent=70, threshold=3))


def knockout_white(img: Image.Image) -> Image.Image:
    arr = np.array(img.convert("RGBA"))
    rgb = arr[:, :, :3].astype(np.int16)
    mn = rgb.min(axis=2)
    mx = rgb.max(axis=2)
    chroma = mx - mn
    lum = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
    # Keep gold and the faint pink wash; only drop paper-white.
    paper = (mn >= 248) & (chroma <= 8)
    arr[paper, 3] = 0
    near = (mn >= 236) & (mn < 248) & (chroma <= 10)
    arr[near, 3] = np.clip((248 - mn[near]) / 12.0 * 255.0, 0, 255).astype(np.uint8)
    # Soft pink wash stays, with alpha from how far it is from white.
    pink = (rgb[:, :, 0] > rgb[:, :, 1] + 2) & (rgb[:, :, 0] > rgb[:, :, 2]) & (lum > 200) & (chroma > 3) & ~paper
    arr[pink, 3] = np.clip(255 - mn[pink], 30, 180).astype(np.uint8)
    return Image.fromarray(arr)


def dark_from_light(img: Image.Image) -> Image.Image:
    """Same lockup on dark grounds: black ink becomes white, gold stays gold."""
    arr = np.array(img.convert("RGBA"))
    rgb = arr[:, :, :3].astype(np.float32)
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    mx = rgb.max(axis=2)
    mn = rgb.min(axis=2)
    chroma = mx - mn
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    paper = (lum >= 250) & (chroma <= 6)
    gold = (r - b >= 18) & (g - b >= 5) & (r >= 110) & (chroma >= 12) & (lum < 240) & ~paper
    out = np.zeros_like(arr)
    out[gold, :3] = arr[gold, :3]
    out[gold, 3] = 255
    rest = ~gold & ~paper
    out[rest, 0] = 255
    out[rest, 1] = 255
    out[rest, 2] = 255
    # Boost thin anti-aliased script so it does not vanish on black.
    out[rest, 3] = np.clip((255.0 - lum[rest]) * 1.9, 0, 255).astype(np.uint8)
    return Image.fromarray(out)


def composite(img: Image.Image, rgba: tuple[int, int, int, int]) -> Image.Image:
    bg = Image.new("RGBA", img.size, rgba)
    return Image.alpha_composite(bg, img.convert("RGBA"))


def resize(img: Image.Image, size: int) -> Image.Image:
    if img.size == (size, size):
        return img
    return img.resize((size, size), Image.Resampling.LANCZOS)


def save_png(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG", optimize=True)


def save_jpg(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(path, "JPEG", quality=95, subsampling=0, optimize=True, dpi=(300, 300))


def save_webp(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "WEBP", quality=95, method=6)


def save_tiff(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "TIFF", compression="tiff_lzw", dpi=(300, 300))


def save_pdf(img: Image.Image, path: Path, title: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    c = pdf_canvas.Canvas(str(path), pagesize=letter)
    c.setTitle(title)
    c.setAuthor("Tasty Treats WORLD")
    page_w, page_h = letter
    side = 4 * 72  # 4 inches
    x = (page_w - side) / 2
    y = (page_h - side) / 2
    c.drawImage(ImageReader(img.convert("RGB")), x, y, side, side, mask="auto")
    c.showPage()
    c.save()


def save_svg_embedded(png_path: Path, svg_path: Path, size: int) -> None:
    raw = png_path.read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.write_text(
        f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{size}" height="{size}" viewBox="0 0 {size} {size}">
  <image width="{size}" height="{size}" xlink:href="data:image/png;base64,{b64}"/>
</svg>
''',
        encoding="utf-8",
    )


def save_ico(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])


def build() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)

    base = mild_sharpen(load_source())
    light = knockout_white(base)
    dark = dark_from_light(base)
    on_white = composite(light, WHITE)
    on_black = composite(dark, BLACK)

    variants = {
        "white": on_white,
        "black": on_black,
        "transparent": light,
        "transparent-on-dark": dark,
    }

    sizes = (512, 1024, 2048, 4096)
    for name, img in variants.items():
        for size in sizes:
            r = resize(img, size)
            save_png(r, OUT / "png" / str(size) / f"tasty-treats-world-{name}.png")
            save_webp(r, OUT / "webp" / str(size) / f"tasty-treats-world-{name}.webp")
            if name in ("white", "black"):
                save_jpg(r, OUT / "jpg" / str(size) / f"tasty-treats-world-{name}.jpg")

    save_tiff(resize(on_white, 4096), OUT / "tiff" / "tasty-treats-world-white-300dpi.tif")
    save_tiff(resize(on_black, 4096), OUT / "tiff" / "tasty-treats-world-black-300dpi.tif")
    save_tiff(resize(light, 4096), OUT / "tiff" / "tasty-treats-world-transparent-300dpi.tif")

    save_pdf(on_white, OUT / "pdf" / "tasty-treats-world-white.pdf", "Tasty Treats WORLD")
    save_pdf(on_black, OUT / "pdf" / "tasty-treats-world-black.pdf", "Tasty Treats WORLD")

    png2048 = OUT / "png" / "2048" / "tasty-treats-world-white.png"
    save_svg_embedded(png2048, OUT / "svg" / "tasty-treats-world-white.svg", 2048)
    save_svg_embedded(
        OUT / "png" / "2048" / "tasty-treats-world-transparent.png",
        OUT / "svg" / "tasty-treats-world-transparent.svg",
        2048,
    )
    save_svg_embedded(
        OUT / "png" / "2048" / "tasty-treats-world-black.png",
        OUT / "svg" / "tasty-treats-world-black.svg",
        2048,
    )
    traced = OUT / "svg" / "tasty-treats-world-traced.svg"
    vtracer.convert_image_to_svg_py(
        str(png2048),
        str(traced),
        colormode="color",
        hierarchical="stacked",
        mode="spline",
        filter_speckle=4,
        color_precision=6,
        layer_difference=16,
        corner_threshold=60,
        length_threshold=4.0,
        max_iterations=10,
        splice_threshold=45,
        path_precision=3,
    )

    save_ico(resize(light, 256), OUT / "ico" / "tasty-treats-world-favicon.ico")

    ig_w = resize(on_white, 1080)
    ig_b = resize(on_black, 1080)
    save_png(ig_w, OUT / "social" / "instagram-1080.png")
    save_jpg(ig_w, OUT / "social" / "instagram-1080.jpg")
    save_png(ig_b, OUT / "social" / "instagram-1080-dark.png")
    save_jpg(ig_b, OUT / "social" / "instagram-1080-dark.jpg")
    banner = Image.new("RGB", (1200, 630), (255, 255, 255))
    mark = resize(light, 540)
    banner.paste(mark, ((1200 - 540) // 2, (630 - 540) // 2), mark)
    save_jpg(banner, OUT / "social" / "og-image-1200x630.jpg")
    print("done")


if __name__ == "__main__":
    build()
