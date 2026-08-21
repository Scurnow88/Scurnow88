# X-Clash Heroes — Full Guide

> **Tiers · Skills · Teams · Upgrade Priority · Faction Bonuses**  
> Master workbook: `X-CLASH-MASTER-RAW-DATA.xlsx` (11 tabs)  
> Skill database: `x-clash-heroes-skills-spec.csv` (140 skill rows)

---

## Table of contents

1. [Faction system & bonuses](#1-faction-system--bonuses)
2. [How to build teams (skill rules)](#2-how-to-build-teams-skill-rules)
3. [Best teams by mode](#3-best-teams-by-mode)
4. [Upgrade priority](#4-upgrade-priority)
5. [When to slot which hero](#5-when-to-slot-which-hero)
6. [S+ hero skill specs (main stats)](#6-s-hero-skill-specs-main-stats)
7. [Data files](#7-data-files)

---

## 1. Faction system & bonuses

### Counter triangle

```
Forest    →  beats  →  Human
Human     →  beats  →  Nightfall
Nightfall →  beats  →  Forest
```

When your faction **counters** the enemy, you take roughly **~20% less damage** from them. Use this for PvP and rally picks.

### Team composition bonus

| Composition | Bonus |
|-------------|-------|
| **3 heroes** faction A + **2 heroes** faction B | **+10% HP, ATK, DEF** |

**Example (PvP):** Sera + Dragonic + Verna (Forest) + Andrew + Fenixia (Human)

### Faction roster quick list

| Faction | Key heroes |
|---------|------------|
| **Forest** | Sera, Yord, Monica, Crystal, Verna, Dragonic, Rexar, Edric, Faerie |
| **Human** | Andrew, Fenixia, Sophia, Chakiss, Denise, Garuda, Marissa |
| **Nightfall** | Daphne, Belial, Alvarez, Mirana, Sparta, Cthylla |
| **God** | Valkyr, Kataras *(verify in client)* |

---

## 2. How to build teams (skill rules)

Boss modes (World Boss, Union Boss) score **total damage**. Stack these layers:

| Layer | Source | Example |
|-------|--------|---------|
| **Team buff** | Yord Travel Invitation | +14.5% ATK, +10% CRIT all allies |
| **Personal passive** | Sera +30% magic, Monica +28% CRIT | Multiplies each hit |
| **Skill shape** | Sera 16×127%, Monica 555% | Burst vs ramp |
| **Position synergy** | Crystal Soul Protection | +25.5% monster DMG to **back-row Forest** |
| **Investment** | CP, gear, skill level | % kits need high base ATK |

### Formation rules (critical)

| Skill | Rule |
|-------|------|
| **Crystal — Soul Protection** | **Forest heroes in BACK row** get +25.5% vs monsters (Sera, Monica, Yord, Crystal). Crystal should also be **back** — not front. |
| **Sera — Amplification** | Stack cap = **Forest allies on team**. Run 3+ Forest for max ramp. |
| **Yord — Travel Invitation** | Buffs **all allies** — any row. Mandatory on most teams. |
| **Fenixia — Flame Overload** | +2 stacks per **Human ally** at battle start. Weak with only 1 Human. |
| **Verna — Astral Guardian** | +17% monster DMG — only pays off when **CP/gear matches** other DPS. |

### Boss team builder (5 steps)

1. **Start with Yord** (buffer) unless your meter disproves it.  
2. Add **2–3 DPS** with highest CP + skill investment (Sera, Monica, Kataras, Fenixia).  
3. If using **Crystal**, put **all Forest DPS in back row** with her.  
4. **Front slot** = flex (Kataras, Fenixia, or tank) — tanks usually lose on boss meter.  
5. **Test on meter** — swap 5th slot (Fenixia ↔ Crystal ↔ Alvarez at 5★).

---

## 3. Best teams by mode

### World Boss & Union Boss (max damage)

**Default skill core (validated on meter):**

```
Yord · Sera · Monica · Kataras · Fenixia
```

| Hero | Key skills | Role |
|------|------------|------|
| **Yord** | Travel Invitation, Lingering Echo | Team ATK/CRIT + protect top DPS |
| **Sera** | Arrow of Destiny, Butterfly, Shadow Sprite | Ramp magic DPS |
| **Monica** | Desert Ember 555%, Savage Swoop, Feline Fury | Crit burst |
| **Kataras** | Burst kit (premium DPS) | Raw damage when fully built |
| **Fenixia** | Incinerate, Flame Spiral, Fireborn | AoE + CRIT |

**Forest buff variant (test on meter):**

```
Back: Yord · Sera · Monica · Crystal  |  Front: Kataras
```

Crystal adds **+25.5% monster damage** to all four Forest back-row heroes.

**Avoid on boss (unless meter says otherwise):** Verna at low CP, Andrew/Dragonic as pure DPS replacements.

### PvP — F2P (3 Forest + 2 Human)

```
Andrew (front) · Dragonic (front) · Sera · Verna/Monica · Fenixia
```

+10% faction bonus. Andrew anti-magic front.

### PvP — Spender

```
Monica · Sophia · Yord · Daphne · Valkyr/Sparta
```

### Campaign — F2P

```
Sera · Dragonic · Yord · Fenixia · Denise/Faerie
```

### Nightfall burst (PvP / PvE)

```
Alvarez · Belial · Mirana · Daphne · Yord
```

Pick **Alvarez** over Valkyr/Mirana/Sparta for **pure damage dealer** among those four.

---

## 4. Upgrade priority

| Priority | F2P | Spender |
|----------|-----|---------|
| 1 | **Yord** — all modes | **Monica** — primary DPS |
| 2 | **Sera** — core DPS | **Sophia** — PvP/boss |
| 3 | **Monica** (if owned) | **Daphne** — PvP counter |
| 4 | **Fenixia** / **Crystal** — boss | **Valkyr** — if on server |
| 5 | **Kataras** — if pulled + built | Nightfall stack (Belial, Alvarez, Mirana) |
| 6 | **Andrew** Day 60 — PvP | **Rexar** — Forest PvP only |
| — | **Verna** — only if boss meter proves value | — |

**Rules:** Max **one core team of 5** first. Stars > collecting heroes. Geared A-tier beats naked S-tier.

Full list: `x-clash-upgrade-priority.csv`

---

## 5. When to slot which hero

| Hero | Bring when… | Bench when… |
|------|-------------|---------------|
| **Yord** | Almost always | Never for max damage without testing |
| **Sera** | Boss, campaign, PvP | Never if built |
| **Monica** | Boss + PvP spender | Under-geared |
| **Crystal** | 3+ Forest in **back row** on boss | Few Forest allies |
| **Kataras** | Fully built; meter top performer | Low investment |
| **Fenixia** | 5th DPS / AoE / CRIT stack | Crystal variant scores higher |
| **Verna** | CP matches Monica/Sera | Low CP — % kit wasted |
| **Andrew** | PvP front, 3F+2H comp | Boss DPS teams |
| **Dragonic** | Early tank, PvP front | Boss unless meter proves DPS |
| **Alvarez** | 5★ Nightfall burst | Before awaken |
| **Valkyr** | PvP Human buffer-tank | Boss DPS |
| **Sparta** | PvP taunt control | World Boss |

Full table: `x-clash-hero-slot-guide.csv`

---

## 6. S+ hero skill specs (main stats)

*Verified values from screenshots. Per-level scaling in `x-clash-heroes-skills-spec.csv`.*

### Yord — Buffer (mandatory)

| Skill | Main stat | Effect @ high level |
|-------|-----------|---------------------|
| Travel Invitation | ATK / CRIT buff | **+14.55% ATK**, **+10% CRIT**, 2 turns @ 4★ |
| Lingering Echo | Speed / protect | **+35 Speed**; −11% dmg to highest-ATK ally |
| Universal Chord | Magic hit | **~403%** magic single |

### Sera — Forest magic DPS

| Skill | Main stat | Effect @ high level |
|-------|-----------|---------------------|
| Arrow of Destiny | Magic multi-hit | **16 × 127%** random + stacks |
| Arrow of the Butterfly | Magic burst | **628%** single; builds Amplification |
| Shadow Sprite | Passive | **+30% magic damage** dealt |

### Monica — Forest crit assassin

| Skill | Main stat | Effect @ high level |
|-------|-----------|---------------------|
| Desert Ember | Magic | **555%** + back-row splash |
| Savage Swoop | Magic multi | **3–5 × 348%** random |
| Feline Fury | CRIT | **+28% CRIT** (~43% @ 5★) |

### Crystal — Forest boss enabler

| Skill | Main stat | Effect @ max |
|-------|-----------|--------------|
| Ferry Soul | Physical | **~523%** single |
| Shadowy Soul | Execute | **~1373%**; recast 50% on kill |
| Soul Protection | Team buff | **+25.5% monster DMG** to **back-row Forest** |

### Fenixia — Human magic DPS

| Skill | Main stat | Effect @ high level |
|-------|-----------|---------------------|
| Incinerate | Magic | **481%** + Flame Overload |
| Flame Spiral | AoE magic | **254%** to all enemies |
| Fireborn | CRIT | **+27% CRIT** |

### Verna — Monster specialist *(investment-gated)*

| Skill | Main stat | Effect @ high level |
|-------|-----------|---------------------|
| Whispers of the Stars | Physical + debuff | **683%**; monsters +12% dmg taken |
| Astral Guardian | Passive | **+17.45%** monster DMG |
| Dance of the Stars | Physical | **331%** × 2 targets |

### Andrew — Human tank (PvP)

| Skill | Main stat | Effect |
|-------|-----------|--------|
| Ultimate Duel | Physical | **361%** single |
| Despair's Backlash | AoE debuff | **78%** all + −12% enemy magic dmg |
| Ode to Darkness | Passive | **−29%** magic taken |

### Alvarez — Nightfall burst DPS

| Skill | Main stat | Effect |
|-------|-----------|--------|
| Revolving Blades | Physical | **347%** single |
| Terror Blade | Multi-hit | **10×43%** random; DEF shred |
| Identify Weakness | Passive | **+24% physical** dealt |

### Belial / Mirana / Kataras / Valkyr / Sparta / Sophia / Dragonic

See **`x-clash-heroes-skills-spec.csv`** and **`X-CLASH-HERO-GUIDE.md`** for full verified tables.

---

## 7. Data files

| File | Contents |
|------|----------|
| **`X-CLASH-MASTER-RAW-DATA.xlsx`** | All tabs — import to Google Sheets |
| `x-clash-heroes-skills-spec.csv` | **140 skills** — stats, tiers, synergy, verified flag |
| `x-clash-team-compositions.csv` | Best teams by mode with key skills |
| `x-clash-hero-slot-guide.csv` | When to bring/bench each hero |
| `x-clash-upgrade-priority.csv` | F2P + spender investment order |
| `x-clash-faction-reference.csv` | Triangle, bonuses, formation rules |
| `x-clash-heroes-master.csv` | 31 heroes — roles, tiers, synergies |
| `x-clash-heroes-tier-by-mode.csv` | PvP / WB / Campaign tiers |
| `YOUR-ROSTER-ADVICE.md` | Personalized PeachesNme roster notes |

**Regenerate workbook after CSV edits:**

```bash
python3 x-clash/scripts/build-skills-spec.py
python3 x-clash/scripts/generate-master-workbook.py
```

---

## Sources

- [Van DeVaughn — First 60 Days Tier List](https://youtu.be/5UhwSZXyLr0)
- [LDShop — Survival Challenge Tier List](https://www.ldshop.gg/blog/tier-list/x-clash-survival-challenge-tier-list.html)
- In-game screenshots (user verified) — Sera, Monica, Yord, Crystal, Fenixia, Andrew, Verna, Alvarez, Belial, Mirana, Valkyr, Sparta, Sophia, Rexar, Chakiss, Dragonic

*16 lower-tier heroes still need skill screenshots — rows marked `Verified: No` in skills spec.*
