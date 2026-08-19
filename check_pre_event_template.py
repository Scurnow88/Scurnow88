#!/usr/bin/env python3
"""Validate Archangel pre-event Mailchimp template structure and branding."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
TEMPLATE = ROOT / "mailchimp-pre-event.html"

REQUIRED_COLORS = [
    "#0c1970",  # navy accent
    "#181B6B",  # CTA pill
    "#0b2a5b",  # contact name
    "#1d1d1f",  # headline
    "#f5f5f7",  # light card
]

REQUIRED_COPY = [
    "Archangel Education + Technology",
    "Looking forward to",
    "serving your school",
    "Desire Vanterpool",
    "Technology Advisor",
    "Partner with Archangel to create engaging, student-centered learning environments.",
    "Diocese of Arlington Principals",
    "St. Andrew Catholic School",
    "Tuesday, August 4, 2026",
]

REQUIRED_ASSETS = [
    "42785579-57e7-1dab-2d73-73efc65d4612.png",  # logo
    "27586e50-576c-f726-7a14-0015a08907c8.png",  # Desire headshot
    "Promo_Flyer_8.5x11_Vanterpool.pdf",
    "Promo_Flyer_8.5x11_Asus_Vanterpool",
    "calendar.google.com/calendar",
    "mailto:dvanterpool@arch-te.com",
    "tel:+17866345839",
]

REQUIRED_CLASSES = [
    "pre-shell",
    "pre-hero",
    "pre-h1",
    "offer-col",
    "desire-cta-desktop",
    "desire-btn-mobile",
]


def main() -> int:
    html = TEMPLATE.read_text(encoding="utf-8")
    errors = []

    if "<style" not in html:
        errors.append("Missing <style> block")
    if "@media only screen and (max-width: 620px)" not in html:
        errors.append("Missing 620px mobile CSS")
    if html.count("<table") < 8:
        errors.append(f"Expected several tables, found {html.count('<table')}")
    if "max-width:600px" not in html:
        errors.append("Missing 600px email shell")

    for color in REQUIRED_COLORS:
        if color.lower() not in html.lower():
            errors.append(f"Missing brand color {color}")

    for copy in REQUIRED_COPY:
        if copy not in html:
            errors.append(f"Missing copy: {copy}")

    for asset in REQUIRED_ASSETS:
        if asset not in html:
            errors.append(f"Missing asset/link: {asset}")

    for cls in REQUIRED_CLASSES:
        if cls not in html:
            errors.append(f"Missing CSS class: {cls}")

    # Mailchimp paste file should not be a full HTML document
    if re.search(r"<!DOCTYPE|<html[\s>]", html, re.I):
        errors.append("Template should be a Mailchimp snippet, not a full HTML document")

    size = TEMPLATE.stat().st_size
    if size > 102400:
        errors.append(f"Template is {size} bytes; Gmail clips around 102KB")

    if errors:
        print("FAIL")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("PASS")
    print(f"  file: {TEMPLATE.name} ({size} bytes)")
    print(f"  tables: {html.count('<table')}")
    print(f"  links: {len(re.findall(r'href=', html))}")
    print(f"  images: {len(re.findall(r'<img ', html))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
