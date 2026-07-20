# X-Clash — One Master Spreadsheet (Raw Data)

## Download (single file, all tabs)

**[`X-CLASH-MASTER-RAW-DATA.xlsx`](X-CLASH-MASTER-RAW-DATA.xlsx)** — import to Google Sheets or open in Excel.

[GitHub download](https://github.com/Scurnow88/Scurnow88/raw/cursor/drive-hero-data-update-4d17/x-clash/X-CLASH-MASTER-RAW-DATA.xlsx)

---

## What this is

- **Raw baseline reference** for all **31 heroes**
- Skill % values at **Lv30 / max skill baseline** (not your current skill levels)
- ★1–★5 = **star upgrade effects** (not what you have unlocked today)
- **No personal roster**, no account power, no investment tracking
- Stats = **Lv.150** where confirmed from PDF; others marked Pending

---

## Tabs inside the workbook

| Tab | Contents |
|-----|----------|
| **README** | Data dictionary + what is / isn't included |
| **Heroes** | Tier, faction, role, gear summary, synergies, rankings |
| **Skills** | Skill 1–4 separated with formatted ★1–★5 text |
| **Skills Raw** | One row per skill (compact database) |
| **Tier List** | Full tier-list export format |
| **Factions** | Forest / Human / Nightfall + team bonuses |
| **Rankings** | Top DPS / Tank / Support lists |
| **Mode Ratings** | PvP, WB, Campaign, Siege ratings |
| **Teams** | Generic meta comps only (no personal teams) |
| **Destiny Gear** | Legendary craft set Lv1–40 stats |
| **Builds** | Artifact / rune / talent role guides |
| **Stats Lv150** | ATK / HP / DEF baseline |

---

## Import to Google Sheets

1. Go to [Google Drive](https://drive.google.com) → **New → File upload**
2. Upload `X-CLASH-MASTER-RAW-DATA.xlsx`
3. Right-click → **Open with → Google Sheets**
4. All 12 tabs appear at the bottom automatically

**Tip:** Widen columns on the **Skills** tab so multi-line ★ text displays cleanly.

---

## Regenerate after data updates

```bash
python3 x-clash/scripts/generate-separated-skills.py
python3 x-clash/scripts/generate-master-workbook.py
```

---

## Optional: personal tracker (NOT in master file)

Use `x-clash-my-roster-template.csv` separately if you want to track **your** levels, stars, and gear — kept out of the raw master workbook on purpose.
