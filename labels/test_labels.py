#!/usr/bin/env python3
"""Checks print-ready Tasty Treats World labels."""

from __future__ import annotations

import unittest
from pathlib import Path

from PIL import Image
from pyzbar.pyzbar import decode

from generate_labels import (
    DPI,
    LABEL_IN,
    PX,
    QR_URL,
    avery_22806_positions,
    avery_22807_positions,
    generate_all,
)

OUT = Path(__file__).resolve().parent / "output"
EXPECTED_QR = QR_URL.encode("ascii")


class LabelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.paths = generate_all()

    def test_square_is_2in_at_600dpi(self) -> None:
        with Image.open(self.paths["square"]) as img:
            self.assertEqual(img.size, (PX, PX))
            dpi = img.info.get("dpi") or (0, 0)
            self.assertAlmostEqual(dpi[0], DPI, delta=1)
            self.assertAlmostEqual(dpi[1], DPI, delta=1)

    def test_round_is_2in_circle(self) -> None:
        with Image.open(self.paths["round"]) as src:
            img = src.convert("RGBA")
        self.assertEqual(img.size, (PX, PX))
        # Corners of a circular label must be transparent for die-cutting.
        for xy in ((0, 0), (PX - 1, 0), (0, PX - 1), (PX - 1, PX - 1)):
            self.assertEqual(img.getpixel(xy)[3], 0, f"corner {xy} should be empty")
        # Center should be opaque cream.
        self.assertGreater(img.getpixel((PX // 2, PX // 2))[3], 250)

    def test_square_qr_decodes_to_website(self) -> None:
        with Image.open(self.paths["square"]) as img:
            found = decode(img)
        self.assertTrue(found, "square label QR did not scan")
        self.assertEqual(found[0].data, EXPECTED_QR)

    def test_round_qr_decodes_to_website(self) -> None:
        with Image.open(self.paths["round"]) as img:
            found = decode(img)
        self.assertTrue(found, "round label QR did not scan")
        self.assertEqual(found[0].data, EXPECTED_QR)

    def test_qr_is_large_enough_to_print(self) -> None:
        """Printed QR modules should stay near or above 0.55 inch."""
        with Image.open(self.paths["square"]) as img:
            square = decode(img)[0]
        with Image.open(self.paths["round"]) as img:
            round_qr = decode(img)[0]
        # Short HTTPS URL + ECC H stays readable a bit under 0.8".
        min_px = 0.55 * DPI
        self.assertGreaterEqual(square.rect.width, min_px)
        self.assertGreaterEqual(round_qr.rect.width, min_px)

    def test_logo_and_qr_do_not_overlap(self) -> None:
        with Image.open(self.paths["square"]) as img:
            square = decode(img)[0]
        with Image.open(self.paths["round"]) as img:
            round_qr = decode(img)[0]
        # Logo lives in the upper half; QR should start below mid-label.
        self.assertGreater(square.rect.top, PX * 0.45)
        self.assertGreater(round_qr.rect.top, PX * 0.50)

    def test_avery_sheet_counts(self) -> None:
        self.assertEqual(len(avery_22806_positions()), 12)
        self.assertEqual(len(avery_22807_positions()), 12)
        self.assertEqual(LABEL_IN, 2.0)

    def test_print_sheets_exist(self) -> None:
        for key in ("sheet_square", "sheet_round"):
            path = self.paths[key]
            self.assertTrue(path.is_file())
            self.assertGreater(path.stat().st_size, 10_000)
            data = path.read_bytes()
            self.assertTrue(data.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
