# Tasty Treats World — bakery box labels

Print-ready 2-inch stickers for pastry and cake boxes after a sale.
Each label carries the cupcake seal, a scannable QR code, and a short thank-you line.

| File | Use |
| --- | --- |
| `output/label_square_2in_avery_22806.png` | Single **2" square** design. Upload to Avery template **22806**. |
| `output/label_round_2in_avery_22807.png` | Single **2" round** design. Upload to Avery template **22807**. |
| `output/avery_22806_print_sheet.pdf` | 12-up US Letter sheet aligned to Avery 22806. |
| `output/avery_22807_print_sheet.pdf` | 12-up US Letter sheet aligned to Avery 22807. |

QR codes currently open [tastytreatsworld.com](https://tastytreatsworld.com/).

## Design

Both stickers share one pastry-shop palette: cream paper, chocolate ink, champagne gold, and a cherry accent.

- **Square (22806)** — bakery seal. Gold double frame, logo on top, QR below, then `SCAN TO CONNECT`. Best on the box lid.
- **Round (22807)** — chocolate medallion. Dark outer ring, cream center, `HANDMADE WITH LOVE` on the upper arc, logo, then QR. Best on the box side or twine.

The QR uses rounded modules so it feels closer to the existing dotted QR artwork, on a cream plate so phones can actually read it at 2 inches.

## Print on Avery sheets

1. Use **Avery 22806** (matte white 2" square, 12 per sheet) or **Avery 22807** (glossy white 2" round, 12 per sheet).
2. Either:
   - Open [Avery Design & Print](https://www.avery.com/templates), pick the template number, and upload the matching PNG, or
   - Print the matching PDF from `output/` on the label sheet.
3. Printer settings: **actual size / 100%**. Do not use fit-to-page.
4. Print one test page on plain paper, hold it against a label sheet up to the light, and check alignment before using real labels.

Safe area: keep the gold frames. Backgrounds are full-bleed, so a 1/16" cutter shift will not slice the logo or QR.

## Change the QR destination

Edit `QR_URL` at the top of `generate_labels.py` (Instagram, Google reviews, a menu page, and so on), then:

```bash
python3 labels/generate_labels.py
python3 labels/test_labels.py
```

Dependencies: `pillow`, `segno`, `reportlab`, `cairosvg`, `pyzbar`.
