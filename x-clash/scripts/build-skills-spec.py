#!/usr/bin/env python3
"""Build x-clash-heroes-skills-spec.csv from skills + master data."""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Extra metadata not in base skills CSV
HERO_META = {
    "Sera": {"faction": "Forest", "row": "Back", "boss": "SS", "pvp": "SS"},
    "Yord": {"faction": "Forest", "row": "Back", "boss": "SS", "pvp": "SS"},
    "Monica": {"faction": "Forest", "row": "Back", "boss": "SS", "pvp": "SS"},
    "Dragonic": {"faction": "Forest", "row": "Front", "boss": "C", "pvp": "A"},
    "Fenixia": {"faction": "Human", "row": "Back", "boss": "S", "pvp": "S"},
    "Crystal": {"faction": "Forest", "row": "Back", "boss": "SS", "pvp": "B"},
    "Verna": {"faction": "Forest", "row": "Back", "boss": "B*", "pvp": "B"},
    "Andrew": {"faction": "Human", "row": "Front", "boss": "D", "pvp": "A"},
    "Sophia": {"faction": "Human", "row": "Back", "boss": "SS", "pvp": "SS"},
    "Daphne": {"faction": "Nightfall", "row": "Back", "boss": "SS", "pvp": "SS"},
    "Alvarez": {"faction": "Nightfall", "row": "Back", "boss": "S", "pvp": "A"},
    "Belial": {"faction": "Nightfall", "row": "Back", "boss": "A", "pvp": "S"},
    "Mirana": {"faction": "Nightfall", "row": "Back", "boss": "S", "pvp": "A"},
    "Kataras": {"faction": "God/Nightfall", "row": "Back", "boss": "SS+", "pvp": "S"},
    "Valkyr": {"faction": "God", "row": "Front", "boss": "C", "pvp": "SS"},
    "Sparta": {"faction": "Nightfall", "row": "Front", "boss": "D", "pvp": "S"},
    "Rexar": {"faction": "Forest", "row": "Front", "boss": "C", "pvp": "S"},
    "Chakiss": {"faction": "Human", "row": "Front", "boss": "B", "pvp": "C"},
    "Edric": {"faction": "Forest", "row": "Front", "boss": "C", "pvp": "C"},
    "Denise": {"faction": "Human", "row": "Back", "boss": "C", "pvp": "C"},
    "Faerie": {"faction": "Forest", "row": "Back", "boss": "C", "pvp": "C"},
}

SYNERGY = {
    "Sera": "Pair Yord buffer; more Forest allies = higher Amplification cap",
    "Yord": "Mandatory buffer; buffs all DPS; protects highest-ATK ally",
    "Monica": "Stack CRIT with Yord; Forest back row for Crystal Soul Protection",
    "Crystal": "Keep Forest DPS in BACK row (Sera/Monica/Yord/Crystal)",
    "Verna": "Only when CP matches team; pairs Crystal back-row buff",
    "Fenixia": "Flame Overload scales with Human ally count",
    "Kataras": "Raw burst; eats Yord ATK/CRIT buff; verify on meter",
    "Andrew": "3 Forest + 2 Human = faction bonus; PvP front not boss",
    "Alvarez": "Nightfall burst; DEF shred; 5★ for boss consideration",
    "Belial": "Execute + CRIT; Nightfall comps",
    "Mirana": "AoE physical; Soul Drain +35% phys at 5★",
    "Dragonic": "Front tank; skip boss unless out-DPSes carries",
}


def main() -> None:
    skills_path = ROOT / "x-clash-heroes-skills.csv"
    out_path = ROOT / "x-clash-heroes-skills-spec.csv"

    rows_out = []
    with skills_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            hero = row["Hero Name"]
            meta = HERO_META.get(hero, {"faction": "?", "row": "?", "boss": "?", "pvp": "?"})
            verified = "No" if row.get("Needs Screenshot Update") == "Yes" else "Yes"
            if "TBD" in row.get("Skill Name", "") or row.get("Effect Summary (Max/Lv30 baseline)", "").startswith("Level 1"):
                verified = "Partial" if "TBD" not in row.get("Skill Name", "") else "No"
            if row.get("Data Source", "") == "In-game" and "TBD" in row.get("Skill Name", ""):
                verified = "No"

            rows_out.append(
                {
                    "Hero": hero,
                    "Faction": meta["faction"],
                    "Recommended_Row": meta["row"],
                    "Skill_Slot": row["Skill Slot"],
                    "Skill_Name": row["Skill Name"],
                    "Skill_Type": row["Skill Type"],
                    "Main_Stat_Scale": row["Scales With"],
                    "Effect_Summary": row["Effect Summary (Max/Lv30 baseline)"],
                    "Star_Gates": row["Star Gate"],
                    "Boss_Tier": meta["boss"],
                    "PvP_Tier": meta["pvp"],
                    "Team_Synergy_Note": SYNERGY.get(hero, row.get("Data Source", "")),
                    "Verified": verified,
                    "Source": row["Data Source"],
                }
            )

    fields = list(rows_out[0].keys()) if rows_out else []
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows_out)
    print(f"Wrote {out_path} ({len(rows_out)} rows)")


if __name__ == "__main__":
    main()
