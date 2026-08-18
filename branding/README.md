# Tasty Treats WORLD — branding files

Format conversions of the original circular lockup. The cupcake, script, gold ring, and layout are not redrawn.

## Use these

| Need | File |
| --- | --- |
| Print on white | `exports/pdf/tasty-treats-world-white.pdf` or `exports/tiff/tasty-treats-world-white-300dpi.tif` |
| Print on black | `exports/pdf/tasty-treats-world-black.pdf` or `exports/tiff/tasty-treats-world-black-300dpi.tif` |
| Transparent PNG | `exports/png/4096/tasty-treats-world-transparent.png` |
| Dark overlay PNG | `exports/png/2048/tasty-treats-world-transparent-on-dark.png` |
| SVG (pixel-perfect embed) | `exports/svg/tasty-treats-world-transparent.svg` |
| SVG (traced vectors) | `exports/svg/tasty-treats-world-traced.svg` |
| Web JPG | `exports/jpg/` |
| Favicon | `exports/ico/tasty-treats-world-favicon.ico` |
| Instagram / OG | `exports/social/` |

Source file: `original/tasty-treats-world-source.png`. Replace that PNG with a higher-resolution original if you have one, then run:

```bash
python3 -m pip install -r branding/requirements.txt
python3 branding/src/export_formats.py
```
