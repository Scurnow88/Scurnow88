# Tasty Treats WORLD — logo files

These are format conversions of the original circular lockup: same cupcake, same script, same gold ring. Colors are slightly enriched and the lines are sharpened. This is not a redesign.

## Which file to use

| Use | File |
| --- | --- |
| Website, overlay, stickers | `exports/png/4096/tasty-treats-world-original-transparent.png` or `exports/svg/tasty-treats-world-original-white.svg` |
| Print on white | `exports/pdf/tasty-treats-world-original-white.pdf` or `exports/png/4096/tasty-treats-world-original-white.png` |
| Print on black | `exports/pdf/tasty-treats-world-original-black.pdf` or `exports/png/4096/tasty-treats-world-original-black.png` |
| Dark websites / video | `exports/png/2048/tasty-treats-world-original-transparent-on-dark.png` |
| Instagram | `exports/social/instagram-1080.png` (light) or `instagram-1080-dark.png` |
| Link preview | `exports/social/og-image-1200x630.jpg` |
| Favicon | `exports/ico/tasty-treats-world-favicon.ico` |

JPG copies are in `exports/jpg/` for email and printers that want a white or black background baked in.

## Rebuild

```bash
python3 -m pip install -r branding/requirements.txt
python3 branding/src/export_formats.py
```
