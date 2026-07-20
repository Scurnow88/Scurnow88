#!/usr/bin/env python3
"""Build single XLSX workbook with all raw baseline X-Clash reference tabs."""
import csv
from pathlib import Path

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter
except ImportError:
    raise SystemExit("openpyxl required: pip install openpyxl")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "X-CLASH-MASTER-RAW-DATA.xlsx"

# Tab name (max 31 chars) -> CSV path relative to ROOT
TABS = [
    ("README", None),
    ("Heroes", "x-clash-heroes-profiles.csv"),
    ("Skills", "x-clash-heroes-skills-separated.csv"),
    ("Skills Raw", "x-clash-heroes-skills.csv"),
    ("Tier List", "x-clash-heroes-full-tier-list.csv"),
    ("Factions", "x-clash-faction-reference.csv"),
    ("Rankings", "x-clash-hero-rankings.csv"),
    ("Mode Ratings", "x-clash-hero-mode-ratings.csv"),
    ("Teams", "x-clash-team-compositions-raw.csv"),
    ("Destiny Gear", "x-clash-gear-destiny-set.csv"),
    ("Builds", "x-clash-hero-builds.csv"),
    ("Stats Lv150", "x-clash-heroes-stats.csv"),
]

README_ROWS = [
    ["X-Clash Heroes — Master Raw Data Reference"],
    [""],
    ["Purpose", "Baseline game data for all 31 heroes. NOT tied to any player account, levels, or star investments."],
    ["Skill numbers", "Lv30 / max-skill baseline from Xyland s39 PDF + verified Drive screenshots (Jul 2026)."],
    ["Star effects", "★1–★5 show awakening/star upgrade bonuses — not current unlock state."],
    ["Stats", "Lv.150 ATK/HP/DEF where confirmed (S+ heroes from PDF); S/A tier stats marked Pending."],
    ["Gear", "Destiny Legendary craft set = verified in-game. Artifact names in Builds tab = Hero Clash role guide."],
    ["Teams", "Generic meta compositions only — no personal roster assumptions."],
    ["Hero count", "31/31 verified"],
    ["Updated", "Jul 20 2026"],
    [""],
    ["TAB GUIDE"],
    ["Heroes", "One row per hero — tier, faction, role, gear summary, synergies, rankings"],
    ["Skills", "Separated Skill 1–4 labels + formatted descriptions with ★ effects"],
    ["Skills Raw", "Compact skill database (one row per skill)"],
    ["Tier List", "Tier-list export format with all skills per hero"],
    ["Factions", "Forest / Human / Nightfall triangle + team bonuses"],
    ["Rankings", "Top DPS / Tank / Support ordered lists"],
    ["Mode Ratings", "PvP / WB / Campaign / Siege tier ratings per hero"],
    ["Teams", "Reference team compositions by mode (raw baseline)"],
    ["Destiny Gear", "Craftable Legendary gear — Lv1 base + Lv10/20/30/40 unlocks"],
    ["Builds", "Artifact/rune/talent recommendations by role"],
    ["Stats Lv150", "Raw ATK/HP/DEF at level 150 where available"],
]

HEADER_FILL = PatternFill("solid", fgColor="1F4E79")
HEADER_FONT = Font(bold=True, color="FFFFFF")
WRAP = Alignment(wrap_text=True, vertical="top")


def write_readme(ws):
    for r, row in enumerate(README_ROWS, 1):
        for c, val in enumerate(row, 1):
            cell = ws.cell(row=r, column=c, value=val)
            if r == 1:
                cell.font = Font(bold=True, size=14)
            if r == 12:
                cell.font = Font(bold=True)
    ws.column_dimensions["A"].width = 18
    ws.column_dimensions["B"].width = 90


def csv_to_sheet(ws, csv_path: Path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for r_idx, row in enumerate(reader, 1):
            for c_idx, val in enumerate(row, 1):
                cell = ws.cell(row=r_idx, column=c_idx, value=val)
                if r_idx == 1:
                    cell.fill = HEADER_FILL
                    cell.font = HEADER_FONT
                    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
                else:
                    cell.alignment = WRAP
    # Auto-width (cap for readability)
    for col in ws.columns:
        letter = get_column_letter(col[0].column)
        max_len = 0
        for cell in col[: min(len(col), 50)]:
            if cell.value:
                max_len = max(max_len, min(len(str(cell.value).split("\n")[0]), 60))
        ws.column_dimensions[letter].width = min(max(max_len + 2, 10), 50)
    ws.freeze_panes = "A2"


def main():
    wb = Workbook()
    wb.remove(wb.active)
    for tab_name, csv_name in TABS:
        ws = wb.create_sheet(title=tab_name[:31])
        if csv_name is None:
            write_readme(ws)
        else:
            path = ROOT / csv_name
            if not path.exists():
                ws.cell(row=1, column=1, value=f"Missing: {csv_name}")
            else:
                csv_to_sheet(ws, path)
    wb.save(OUT)
    print(f"Wrote {OUT} ({len(TABS)} tabs)")


if __name__ == "__main__":
    main()
