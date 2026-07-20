# X-Clash — Google Sheets Master Reference

Import these CSV files as **separate tabs** in one Google Sheet for a complete hero database.

## Quick Start

1. Open [Google Sheets](https://sheets.google.com) → **Blank spreadsheet**
2. **File → Import → Upload** each CSV below
3. Choose **Replace current sheet** for the first file, then **Insert new sheet(s)** for the rest
4. Rename tabs to match the names in the table below

---

## Recommended Tab Layout

| Tab Name | File | What It Contains |
|----------|------|------------------|
| **Profiles** | `x-clash-heroes-profiles.csv` | **Main sheet** — Hero, Tier, Faction, Role, Gear, Synergies, Rankings, all skills summary |
| **Skills (Separated)** | `x-clash-heroes-skills-separated.csv` | **Your format** — Skill 1–4 labels + full descriptions with ★1–★5 |
| **Skills (Long)** | `x-clash-heroes-skills-separated-long.csv` | One row per skill (easier filtering) |
| **Skills (Raw)** | `x-clash-heroes-skills.csv` | Compact skill database with star gates |
| **Tier List** | `x-clash-heroes-full-tier-list.csv` | Your tier-list format (skill name + description per row) |
| **Builds** | `x-clash-hero-builds.csv` | Artifacts, runes, substats, talents per hero |
| **Mode Ratings** | `x-clash-hero-mode-ratings.csv` | PvP / WB / Campaign / Siege ratings per hero |
| **Teams** | `x-clash-team-compositions.csv` | PvE, PvP, Boss comps + **your Team 1 & Team 2** |
| **Rankings** | `x-clash-hero-rankings.csv` | Top DPS / Tank / Support ordered lists |
| **Factions** | `x-clash-faction-reference.csv` | Forest / Human / Nightfall triangle + bonuses |
| **Destiny Gear** | `x-clash-gear-destiny-set.csv` | Craftable Legendary set — Lv1–40 stats per piece |
| **Stats** | `x-clash-heroes-stats.csv` | Lv.150 ATK/HP/DEF (S+ from PDF; S/A pending) |
| **My Roster** | `x-clash-my-roster-template.csv` | **Your** heroes — fill in levels, stars, gear |

---

## Your Recommended Teams (from Profiles tab → Teams tab)

### Team 1 — Forest/Human PvP *(3 Forest + 2 Human = +10%)*
```
Sera + Dragonic + Verna + Andrew + Fenixia (or Sophia)
```
- Your 5★ Forest core: **Sera, Dragonic, Verna**
- **Andrew** is priority investment for Human slot + anti-magic tank

### Team 2 — World Boss
```
Yord + Sera + Verna + Crystal + Andrew
```
- Buffers + damage; no dedicated tank unless Dragonic out-DPSes your weakest hero

---

## Faction Bonuses

| Composition | Bonus |
|-------------|-------|
| 3 same faction | +5% HP/ATK/DEF |
| 3 + 2 split | +10% |
| 4 same | +15% |
| 5 same | +20% |

**Triangle:** Forest → Human → Nightfall → Forest

---

## Useful Sheet Formulas

**Lookup hero profile from Skills tab:**
```
=IFERROR(VLOOKUP(A2, Profiles!A:A, 1, FALSE), "Not found")
```

**Filter your owned heroes (My Roster tab):**
```
=FILTER(Profiles!A:R, MyRoster!B:B="Y")
```

---

## Data Status

- **31/31 heroes** — skills verified from Drive screenshots + Xyland s39 PDF
- **Gear/builds** — role-based + AllClash community guides (Hero Clash equivalent)
- **Stats (S/A tier)** — pending in-game screenshots for Lv.150 panels

**Source:** [Google Drive folder](https://drive.google.com/drive/folders/1c-1VQk8gCxEjVDPTN7oQ44K3dMGGatlO)

---

## GitHub Raw Downloads

Replace `BRANCH` with `cursor/drive-hero-data-update-4d17`:

```
https://raw.githubusercontent.com/Scurnow88/Scurnow88/BRANCH/x-clash/x-clash-heroes-profiles.csv
https://raw.githubusercontent.com/Scurnow88/Scurnow88/BRANCH/x-clash/x-clash-heroes-skills-separated.csv
https://raw.githubusercontent.com/Scurnow88/Scurnow88/BRANCH/x-clash/x-clash-heroes-skills-separated-long.csv
https://raw.githubusercontent.com/Scurnow88/Scurnow88/BRANCH/x-clash/x-clash-gear-destiny-set.csv
https://raw.githubusercontent.com/Scurnow88/Scurnow88/BRANCH/x-clash/x-clash-heroes-full-tier-list.csv
https://raw.githubusercontent.com/Scurnow88/Scurnow88/BRANCH/x-clash/x-clash-hero-builds.csv
https://raw.githubusercontent.com/Scurnow88/Scurnow88/BRANCH/x-clash/x-clash-hero-mode-ratings.csv
https://raw.githubusercontent.com/Scurnow88/Scurnow88/BRANCH/x-clash/x-clash-team-compositions.csv
https://raw.githubusercontent.com/Scurnow88/Scurnow88/BRANCH/x-clash/x-clash-hero-rankings.csv
https://raw.githubusercontent.com/Scurnow88/Scurnow88/BRANCH/x-clash/x-clash-faction-reference.csv
https://raw.githubusercontent.com/Scurnow88/Scurnow88/BRANCH/x-clash/x-clash-my-roster-template.csv
```
