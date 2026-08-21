# Scurnow88

## X-Clash Hero Reference

**Start here:** [`x-clash/X-CLASH-FULL-GUIDE.md`](x-clash/X-CLASH-FULL-GUIDE.md) — tiers, teams, upgrade priority, faction bonuses, skill-based team building.

**Master workbook:** [`x-clash/X-CLASH-MASTER-RAW-DATA.xlsx`](x-clash/X-CLASH-MASTER-RAW-DATA.xlsx) — 11 tabs (skills spec, teams, factions, roster, tiers).

### Key files

| File | Contents |
|------|----------|
| `x-clash-heroes-skills-spec.csv` | 140 skills — main stats, boss/PvP tier, synergy, verified |
| `x-clash-team-compositions.csv` | Best lineups by mode with key skills |
| `x-clash-hero-slot-guide.csv` | When to use / bench each hero |
| `x-clash-upgrade-priority.csv` | F2P + spender investment order |
| `x-clash-faction-reference.csv` | Faction triangle, +10% bonus, formation rules |
| `x-clash/X-CLASH-HERO-GUIDE.md` | Detailed per-hero skill tables (verified heroes) |
| `x-clash/YOUR-ROSTER-ADVICE.md` | Personalized roster notes |

Regenerate after CSV edits:

```bash
python3 x-clash/scripts/build-skills-spec.py
python3 x-clash/scripts/generate-master-workbook.py
```
