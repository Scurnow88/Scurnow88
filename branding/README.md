# Tasty Treats WORLD — logo pack

Print-ready and digital files of the Tasty Treats WORLD mark, rebuilt as sharp vector artwork with adjusted gold and blush tones.

## Which file to use

| Use | File |
| --- | --- |
| Website, overlay, merch mockup | `exports/svg/tasty-treats-world-full-color-transparent.svg` |
| Print on white (cards, bags, labels) | `exports/pdf/tasty-treats-world-full-color-white.pdf` or `exports/png/4096/tasty-treats-world-full-color-white.png` |
| Print on black (boxes, shirts, dark bags) | `exports/pdf/tasty-treats-world-on-dark-black.pdf` or `exports/png/4096/tasty-treats-world-on-dark-black.png` |
| Dark website / video overlay | `exports/svg/tasty-treats-world-on-dark-transparent.svg` |
| Embroidery, foil, stamp, one-color print | `exports/svg/tasty-treats-world-mono-black-transparent.svg` or `...-mono-white-transparent.svg` |
| Profile photo, favicon, app icon | `exports/svg/tasty-treats-world-icon-full-color-transparent.svg` and `exports/ico/tasty-treats-world-favicon.ico` |
| Instagram / square social | `exports/social/instagram-1080.png` (light) or `instagram-1080-dark.png` |
| Facebook / link preview | `exports/social/og-image-1200x630.jpg` |

JPG versions sit in `exports/jpg/` for email and places that do not allow transparency.

`exports/illustrated/` holds extra full-color painted rasters of the same lockup if you want a slightly softer, hand-drawn look.

## Color

| Role | Light backgrounds | Dark backgrounds |
| --- | --- | --- |
| Ink | `#111111` | `#FFFFFF` |
| Gold ring | `#C4A045` | `#E4C56A` |
| Blush glow | `#EFB6C6` | `#E59AAD` |

## Rebuild

```bash
python3 -m pip install pillow fonttools uharfbuzz numpy reportlab cairosvg
python3 branding/src/build_logo.py
```

Script font is Great Vibes; `WORLD` is Montserrat. Both are SIL Open Font License (see `fonts/`).
