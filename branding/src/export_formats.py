#!/usr/bin/env python3
"""Export the original Tasty Treats WORLD lockup into branding formats.

This does not redraw the mark. It sharpens, slightly enriches color, then
writes white / black / transparent files from the same pixels.
"""

from __future__ import annotations

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
BLACK = (11, 11, 11, 255)
GOLD_LIGHT = np.array([196, 160, 69], dtype=np.float32)
GOLD_DARK = np.array([228, 197, 106], dtype=np.float32)


def load_source() -> Image.Image:
    img = Image.open(SOURCE).convert("RGBA")
    # Tight crop of the artwork with even padding.
    arr = np.array(img)
    ink = arr[:, :, :3].min(axis=2) < 248
    ys, xs = np.where(ink)
    pad = int(0.08 * max(img.size))
    left = max(0, int(xs.min()) - pad)
    top = max(0, int(ys.min()) - pad)
    right = min(img.width, int(xs.max()) + pad)
    bottom = min(img.height, int(ys.max()) + pad)
    cropped = img.crop((left, top, right, bottom))
    side = max(cropped.size)
    canvas = Image.new("RGBA", (side, side), WHITE)
    canvas.paste(cropped, ((side - cropped.width) // 2, (side - cropped.height) // 2), cropped)
    return canvas


def classify(arr: np.ndarray) -> dict[str, np.ndarray]:
    rgb = arr[:, :, :3].astype(np.float32)
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    mx = rgb.max(axis=2)
    mn = rgb.min(axis=2)
    chroma = mx - mn
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    gold = (r - b >= 22) & (g - b >= 8) & (r >= 130) & (b <= 175) & (lum < 245)
    pink = (r > g + 3) & (r > b) & (lum >= 188) & (chroma >= 4) & ~gold
    white = (mn >= 242) & (chroma <= 10) & ~pink & ~gold
    ink = ~white & ~gold & ~pink
    return {"white": white, "gold": gold, "pink": pink, "ink": ink, "lum": lum, "rgb": rgb}


def make_light_transparent(base: Image.Image) -> Image.Image:
    arr = np.array(base.convert("RGBA"))
    c = classify(arr)
    alpha = np.full(c["lum"].shape, 255, dtype=np.uint8)
    alpha[c["white"]] = 0
    near = (c["lum"] >= 220) & ~c["gold"] & ~c["pink"] & ~c["white"]
    fade = np.clip((236 - c["lum"][near]) / 16.0 * 255.0, 0, 255)
    alpha[near] = fade.astype(np.uint8)
    pink_strength = np.clip((255 - c["lum"]) / 70.0, 0, 1)
    arr[c["pink"], 3] = np.clip(80 + pink_strength[c["pink"]] * 150, 0, 210).astype(np.uint8)
    arr[:, :, 3] = np.minimum(arr[:, :, 3], alpha)
    arr[c["white"], 3] = 0
    return Image.fromarray(arr)


def make_dark_transparent(base: Image.Image) -> Image.Image:
    arr = np.array(base.convert("RGBA"))
    c = classify(arr)
    out = np.zeros_like(arr)
    ink_alpha = np.clip((200 - c["lum"]) / 200.0 * 255.0, 0, 255).astype(np.uint8)
    out[c["ink"], 0] = 255
    out[c["ink"], 1] = 255
    out[c["ink"], 2] = 255
    out[c["ink"], 3] = ink_alpha[c["ink"]]
    out[c["gold"], :3] = GOLD_DARK.astype(np.uint8)
    out[c["gold"], 3] = 255
    rose = np.array([232, 168, 184], dtype=np.uint8)
    pink_alpha = np.clip((245 - c["lum"]) / 80.0 * 180.0, 50, 180).astype(np.uint8)
    out[c["pink"], :3] = rose
    out[c["pink"], 3] = pink_alpha[c["pink"]]
    return Image.fromarray(out)


def sharpen(img: Image.Image) -> Image.Image:
    return img.filter(ImageFilter.UnsharpMask(radius=1.35, percent=160, threshold=1))


def enrich_gold(arr: np.ndarray, mask: np.ndarray) -> np.ndarray:
    rgb = arr[:, :, :3].astype(np.float32)
    target = GOLD_LIGHT
    rgb[mask] = rgb[mask] * 0.55 + target * 0.45
    rgb[mask] = np.clip(rgb[mask], 0, 255)
    arr[:, :, :3] = rgb.astype(np.uint8)
    return arr


def composite(img: Image.Image, rgba: tuple[int, int, int, int]) -> Image.Image:
    bg = Image.new("RGBA", img.size, rgba)
    return Image.alpha_composite(bg, img.convert("RGBA"))


def resize(img: Image.Image, size: int) -> Image.Image:
    if img.size == (size, size):
        return img
    return sharpen(img.resize((size, size), Image.Resampling.LANCZOS))


def save_png(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG", optimize=True)


def save_jpg(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(path, "JPEG", quality=95, subsampling=0, optimize=True)


def save_webp(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "WEBP", quality=95, method=6)


def save_pdf(img: Image.Image, path: Path, title: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    c = pdf_canvas.Canvas(str(path), pagesize=letter)
    c.setTitle(title)
    page_w, page_h = letter
    side = 3.25 * 72
    x = (page_w - side) / 2
    y = (page_h - side) / 2
    c.drawImage(ImageReader(img.convert("RGB")), x, y, side, side, mask="auto")
    c.showPage()
    c.save()


def save_ico(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])


def checkerboard(size: int, cell: int = 28, dark: bool = False) -> Image.Image:
    a, b = ((32, 32, 32), (48, 48, 48)) if dark else ((244, 244, 244), (217, 217, 217))
    img = Image.new("RGB", (size, size), a)
    px = img.load()
    for y in range(size):
        for x in range(size):
            if ((x // cell) + (y // cell)) % 2 == 0:
                px[x, y] = b
    return img.convert("RGBA")


def build() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)

    base = load_source()
    arr = np.array(base)
    arr = enrich_gold(arr, classify(arr)["gold"])
    base = sharpen(Image.fromarray(arr))

    light = make_light_transparent(base)
    dark = make_dark_transparent(base)
    on_white = composite(light, WHITE)
    on_black = composite(dark, BLACK)

    masters = {
        "original-white": on_white,
        "original-black": on_black,
        "original-transparent": light,
        "original-transparent-on-dark": dark,
    }

    master_size = 2048
    sized: dict[str, Image.Image] = {k: resize(v, master_size) for k, v in masters.items()}

    for name, img in sized.items():
        save_png(img, OUT / "png" / "2048" / f"tasty-treats-world-{name}.png")
        save_webp(img, OUT / "webp" / "2048" / f"tasty-treats-world-{name}.webp")
        for size in (512, 1024):
            r = resize(img, size)
            save_png(r, OUT / "png" / str(size) / f"tasty-treats-world-{name}.png")
            save_webp(r, OUT / "webp" / str(size) / f"tasty-treats-world-{name}.webp")

    print_white = resize(on_white, 4096)
    print_black = resize(on_black, 4096)
    print_clear = resize(light, 4096)
    save_png(print_white, OUT / "png" / "4096" / "tasty-treats-world-original-white.png")
    save_png(print_black, OUT / "png" / "4096" / "tasty-treats-world-original-black.png")
    save_png(print_clear, OUT / "png" / "4096" / "tasty-treats-world-original-transparent.png")

    for size in (512, 1024, 2048):
        save_jpg(resize(on_white, size), OUT / "jpg" / str(size) / "tasty-treats-world-original-white.jpg")
        save_jpg(resize(on_black, size), OUT / "jpg" / str(size) / "tasty-treats-world-original-black.jpg")

    save_pdf(print_white, OUT / "pdf" / "tasty-treats-world-original-white.pdf", "Tasty Treats WORLD")
    save_pdf(print_black, OUT / "pdf" / "tasty-treats-world-original-black.pdf", "Tasty Treats WORLD on black")

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

    # Traced SVG from the white master so it stays the same drawing.
    tmp_png = OUT / "png" / "2048" / "tasty-treats-world-original-white.png"
    svg_path = OUT / "svg" / "tasty-treats-world-original-white.svg"
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    vtracer.convert_image_to_svg_py(
        str(tmp_png),
        str(svg_path),
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

    proof_dir = OUT / "proofs"
    proof_dir.mkdir(parents=True, exist_ok=True)
    light_1024 = resize(light, 1024)
    dark_1024 = resize(dark, 1024)
    Image.alpha_composite(checkerboard(1024), light_1024).save(proof_dir / "transparent-on-checker.png")
    Image.alpha_composite(checkerboard(1024, dark=True), dark_1024).save(proof_dir / "transparent-on-dark-checker.png")
    resize(on_white, 1024).save(proof_dir / "white.png")
    resize(on_black, 1024).save(proof_dir / "black.png")
    print("done")


if __name__ == "__main__":
    build()
