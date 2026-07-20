#!/usr/bin/env python3
"""Generate master Google Sheets CSV exports for X-Clash hero reference."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PROFILES = {
    "Sera": {
        "strengths": "16-hit magic burst; Amplification scales with Forest allies; core F2P DPS",
        "best_for": "F2P PvP, World Boss, Campaign, Peak Arena",
        "gear": "Cursed Book + Angelic Headband; Evolution runes (ATK/CRIT); ATK/CRIT/Skill DMG",
        "synergies": "Yord (mandatory buffer), Monica (Forest DPS), Dragonic, Verna/Crystal (WB)",
        "f2p_pri": 1, "spender_pri": 3,
        "dps_rank": 2, "tank_rank": None, "support_rank": None,
        "roi": "Excellent",
    },
    "Dragonic": {
        "strengths": "511% burst + front-row damage reduction + physical Overload buff",
        "best_for": "F2P Campaign, early PvP, Forest faction tank until Andrew",
        "gear": "Eternal Cloak + Spirit Shield; Evolution (Health); HP/DMG Reduction/DEF",
        "synergies": "Yord, Sera, Rexar (Forest PvP), Andrew (handoff tank)",
        "f2p_pri": 3, "spender_pri": 8,
        "dps_rank": None, "tank_rank": 4, "support_rank": 6,
        "roi": "Good (F2P)",
    },
    "Yord": {
        "strengths": "Team ATK buff + protects highest-ATK ally; +Speed; fits every comp",
        "best_for": "Every mode — mandatory investment",
        "gear": "Devil's Heart + Spirit Shield; Evolution (Health); Health/Speed/Buff stats",
        "synergies": "All DPS (Sera, Monica, Fenixia, Sophia); never bench",
        "f2p_pri": 1, "spender_pri": 1,
        "dps_rank": None, "tank_rank": None, "support_rank": 1,
        "roi": "Excellent",
    },
    "Monica": {
        "strengths": "614% single + back-row splash; 396%×5 multi-hit; +30% CRIT",
        "best_for": "Spender PvP, World Boss, late-game Forest DPS",
        "gear": "Angelic Headband + Eternal Cloak; Evolution (Health); DMG Reduction/ATK/CRIT",
        "synergies": "Yord, Sera (Forest core), Rexar, Dragonic",
        "f2p_pri": None, "spender_pri": 1,
        "dps_rank": 1, "tank_rank": None, "support_rank": None,
        "roi": "Excellent (spender)",
    },
    "Sophia": {
        "strengths": "620% single + 447% back-row Stun; scales to 3 targets",
        "best_for": "Spender PvP, anti-backline, Human magic burst",
        "gear": "Cursed Book + Angelic Headband; Evolution (ATK/CRIT); ATK/CRIT/Control",
        "synergies": "Yord, Fenixia, Andrew, Valkyr (Human comp)",
        "f2p_pri": None, "spender_pri": 2,
        "dps_rank": 3, "tank_rank": None, "support_rank": None,
        "roi": "Excellent (spender)",
    },
    "Fenixia": {
        "strengths": "605% single + 320% AoE magic; Flame Overload per Human ally; +30% CRIT",
        "best_for": "World Boss, Human magic DPS, Lucky Spin F2P path",
        "gear": "Cursed Book + Angelic Headband; Evolution (ATK/CRIT); ATK/CRIT/Skill DMG",
        "synergies": "Yord, Andrew, Sophia, Human-heavy teams (3+ Human = bonus)",
        "f2p_pri": 5, "spender_pri": 5,
        "dps_rank": 4, "tank_rank": None, "support_rank": None,
        "roi": "High",
    },
    "Daphne": {
        "strengths": "605% random + 510% back-row priority; +30% magic dealt",
        "best_for": "Spender PvP — Nightfall counter to Human meta",
        "gear": "Cursed Book + Angelic Headband; Evolution (ATK); ATK/Magic DMG",
        "synergies": "Yord, Monica/Sophia (spender PvP), Nightfall buffers",
        "f2p_pri": None, "spender_pri": 3,
        "dps_rank": 5, "tank_rank": None, "support_rank": None,
        "roi": "High (spender)",
    },
    "Andrew": {
        "strengths": "619% duel; −40% magic taken; 144% AoE anti-magic debuff",
        "best_for": "Human tank from Day 60; faction bonus enabler; anti-magic PvP",
        "gear": "Eternal Cloak + Spirit Shield; Evolution (Health); HP/DMG Reduction/DEF",
        "synergies": "Valkyr, Fenixia, Sophia, Sera+Dragonic+Verna (3F+2H = +10%)",
        "f2p_pri": 6, "spender_pri": 7,
        "dps_rank": None, "tank_rank": 2, "support_rank": None,
        "roi": "Good (Day 60)",
    },
    "Crystal": {
        "strengths": "1372% execute + Forest backline +24.75% monster DMG; WB enabler",
        "best_for": "World Boss, Forest backline amplifier (Sera/Verna)",
        "gear": "Cursed Book or Devil's Heart + Angelic Headband; ATK/Execute/Buff",
        "synergies": "Sera, Verna, Yord, Fenixia (WB stack)",
        "f2p_pri": 4, "spender_pri": 6,
        "dps_rank": 6, "tank_rank": None, "support_rank": 4,
        "roi": "High (WB)",
    },
    "Valkyr": {
        "strengths": "Front-row −13% all + magic dmg; Judgment magic reduction for Humans",
        "best_for": "Spender PvP/rally Human buffer-tank",
        "gear": "Spirit Shield + Devil's Heart; Evolution (Health); HP/DMG Reduction/Buff",
        "synergies": "Andrew, Sophia, Fenixia, Human 3+2 comps",
        "f2p_pri": None, "spender_pri": 4,
        "dps_rank": None, "tank_rank": 3, "support_rank": 3,
        "roi": "High (spender)",
    },
    "Sparta": {
        "strengths": "Taunt 4 enemies; −30% damage taken; strong PvP control tank",
        "best_for": "Spender PvP taunt — skip World Boss",
        "gear": "Eternal Cloak + Spirit Shield; Evolution (Health); HP/DMG Reduction/Taunt",
        "synergies": "Nightfall DPS (Daphne, Belial), Yord",
        "f2p_pri": None, "spender_pri": 9,
        "dps_rank": None, "tank_rank": 5, "support_rank": None,
        "roi": "Medium",
    },
    "Rexar": {
        "strengths": "−30% dmg taken; +50% DEF team buff; Forest tank-buffer",
        "best_for": "Forest-focused spender PvP with Dragonic",
        "gear": "Eternal Cloak + Spirit Shield; Evolution (Health); HP/DEF/DMG Reduction",
        "synergies": "Dragonic, Monica, Sera, Yord (Forest PvP)",
        "f2p_pri": None, "spender_pri": 10,
        "dps_rank": None, "tank_rank": 6, "support_rank": None,
        "roi": "Medium (Forest PvP)",
    },
    "Alvarez": {
        "strengths": "620% single + 20×85% Terror Blade DEF shred; +23.6% physical dealt",
        "best_for": "Physical DPS; DEF shred multi-hit",
        "gear": "Cursed Book + Angelic Headband; Evolution (ATK/Penetration); ATK/Penetration/CRIT",
        "synergies": "Human DPS comps, Andrew front line",
        "f2p_pri": None, "spender_pri": 12,
        "dps_rank": 7, "tank_rank": None, "support_rank": None,
        "roi": "Medium",
    },
    "Belial": {
        "strengths": "605% lowest-HP execute; 399%×3 random; +30% CRIT",
        "best_for": "PvP finisher; spender situational",
        "gear": "Cursed Book + Angelic Headband; Evolution (CRIT/ATK); CRIT/ATK/Execute",
        "synergies": "Daphne, Sparta, Nightfall burst comps",
        "f2p_pri": None, "spender_pri": 11,
        "dps_rank": 8, "tank_rank": None, "support_rank": None,
        "roi": "Medium",
    },
    "Kataras": {
        "strengths": "516% random + Counterattack Mode retaliate tank",
        "best_for": "Nightfall counterattack tank — PvP/rally",
        "gear": "Eternal Cloak + Spirit Shield; Evolution (Health); HP/DMG Reduction/ATK",
        "synergies": "Sparta, Nightfall DPS, front-row comps",
        "f2p_pri": None, "spender_pri": 13,
        "dps_rank": None, "tank_rank": 7, "support_rank": None,
        "roi": "Medium",
    },
    "Mirana": {
        "strengths": "605% single + 320% AoE physical; +30% physical dealt",
        "best_for": "Nightfall AoE wave clear, PvE",
        "gear": "Cursed Book + Angelic Headband; Evolution (ATK); ATK/AoE/Physical DMG",
        "synergies": "Belial, Daphne, Nightfall buffers",
        "f2p_pri": None, "spender_pri": 14,
        "dps_rank": 9, "tank_rank": None, "support_rank": None,
        "roi": "Medium",
    },
    "Verna": {
        "strengths": "683% hit + monster vuln debuff; +17% monster DMG; resource farming",
        "best_for": "World Boss, monster hunt, PvE specialist",
        "gear": "Cursed Book + Angelic Headband; Evolution (ATK); ATK/Monster DMG/Debuff",
        "synergies": "Crystal, Yord, Sera (WB core), Fenixia",
        "f2p_pri": 4, "spender_pri": 6,
        "dps_rank": 10, "tank_rank": None, "support_rank": 5,
        "roi": "High (WB)",
    },
    "Chakiss": {
        "strengths": "297% charge + row AoE; −32% monster damage taken",
        "best_for": "PvE monster filler — pick ONE of Chakiss/Edric",
        "gear": "Eternal Cloak + Spirit Shield; Evolution (Health); HP/Monster DMG Reduction",
        "synergies": "Yord, PvE DPS backline; not PvP priority",
        "f2p_pri": None, "spender_pri": None,
        "dps_rank": None, "tank_rank": 8, "support_rank": None,
        "roi": "Low-Medium",
    },
    "Edric": {
        "strengths": "211% Savoir Faire + +80% DEF + −28% monster dmg; Forest tank filler",
        "best_for": "PvE monster filler — pick ONE of Chakiss/Edric",
        "gear": "Eternal Cloak + Spirit Shield; Evolution (Health); HP/DEF/DMG Reduction",
        "synergies": "Forest PvE comps; Yord + Sera backline",
        "f2p_pri": None, "spender_pri": None,
        "dps_rank": None, "tank_rank": 9, "support_rank": None,
        "roi": "Low-Medium",
    },
    "Denise": {
        "strengths": "Mirror Play + −21.8% monster dmg + back-row +12% monster buff",
        "best_for": "Campaign support, PvE buffer",
        "gear": "Devil's Heart + Time Amulet; Evolution (Health); Health/Buff/Speed",
        "synergies": "F2P PvE with Sera/Yord; Human support slot",
        "f2p_pri": None, "spender_pri": None,
        "dps_rank": None, "tank_rank": None, "support_rank": 7,
        "roi": "Medium",
    },
    "Faerie": {
        "strengths": "+169% ATK passive; 210% 2-target punishment; Forest physical DPS",
        "best_for": "Campaign DPS/healer hybrid, siege sustain",
        "gear": "Devil's Heart + Spirit Shield; Evolution (Health); Health/ATK",
        "synergies": "Forest PvE, Denise alternative backline",
        "f2p_pri": None, "spender_pri": None,
        "dps_rank": 11, "tank_rank": None, "support_rank": 8,
        "roi": "Medium",
    },
    "Garuda": {
        "strengths": "175% magic + −27% monster dmg + +26% DEF front row",
        "best_for": "Human tank/support filler",
        "gear": "Eternal Cloak + Spirit Shield; Evolution (Health); HP/DMG Reduction/DEF",
        "synergies": "Andrew, Human PvE comps",
        "f2p_pri": None, "spender_pri": None,
        "dps_rank": None, "tank_rank": 10, "support_rank": 9,
        "roi": "Low-Medium",
    },
    "Marissa": {
        "strengths": "425% Charge + Stun; 336% Precision; +27% monster dmg",
        "best_for": "Nightfall physical burst; situational PvE",
        "gear": "Cursed Book + Angelic Headband; Evolution (ATK); ATK/CRIT/Stun",
        "synergies": "Nightfall physical comps",
        "f2p_pri": None, "spender_pri": None,
        "dps_rank": 12, "tank_rank": None, "support_rank": None,
        "roi": "Low",
    },
    "Reina": {
        "strengths": "5×75% multi-hit + +23% monster dmg dealt",
        "best_for": "Nightfall support/DPS filler",
        "gear": "Cursed Book + Angelic Headband; Evolution (ATK); ATK/Multi-hit",
        "synergies": "Nightfall WB/PvE filler",
        "f2p_pri": None, "spender_pri": None,
        "dps_rank": 13, "tank_rank": None, "support_rank": 10,
        "roi": "Low",
    },
    "Aaron": {
        "strengths": "126% magic + front-row −11% monster dmg",
        "best_for": "Forest support filler — low priority",
        "gear": "Devil's Heart + Spirit Shield; Evolution (Health); Health/Buff",
        "synergies": "Forest PvE only",
        "f2p_pri": None, "spender_pri": None,
        "dps_rank": 14, "tank_rank": None, "support_rank": 11,
        "roi": "Low",
    },
    "Ali": {
        "strengths": "4×76% Piercing Fists multi-hit; +19% ATK passive",
        "best_for": "Human physical DPS filler",
        "gear": "Cursed Book + Angelic Headband; Evolution (ATK); ATK/CRIT/Multi-hit",
        "synergies": "Human DPS comps — invest core heroes first",
        "f2p_pri": None, "spender_pri": None,
        "dps_rank": 15, "tank_rank": None, "support_rank": None,
        "roi": "Low",
    },
    "Cthylla": {
        "strengths": "161% magic + Soul Bash DEF shred on 2 targets",
        "best_for": "Nightfall magic DEF shred — situational",
        "gear": "Cursed Book + Angelic Headband; Evolution (ATK); ATK/Magic DMG/DEB",
        "synergies": "Nightfall magic comps",
        "f2p_pri": None, "spender_pri": None,
        "dps_rank": 16, "tank_rank": None, "support_rank": None,
        "roi": "Low-Medium",
    },
    "Harold": {
        "strengths": "156% single + 143% 2-target; 3-skill budget DPS",
        "best_for": "Bench — do not invest",
        "gear": "Basic DPS gear if forced; Cursed Book; low priority",
        "synergies": "None — filler only",
        "f2p_pri": None, "spender_pri": None,
        "dps_rank": 17, "tank_rank": None, "support_rank": None,
        "roi": "Very Low",
    },
    "Moga": {
        "strengths": "236% Log Toss + 160% 2-target; best A-tier Forest DPS",
        "best_for": "Budget Forest DPS if no S-tier options",
        "gear": "Cursed Book + Angelic Headband; Evolution (ATK); ATK/Physical DMG",
        "synergies": "Forest PvE filler",
        "f2p_pri": None, "spender_pri": None,
        "dps_rank": 18, "tank_rank": None, "support_rank": None,
        "roi": "Very Low",
    },
    "Romano": {
        "strengths": "158% Cleanse Heresy + 145% Piercing Fists (CS); +5% innate",
        "best_for": "Bench — 3-skill budget DPS",
        "gear": "Basic DPS gear; low priority",
        "synergies": "Nightfall filler only",
        "f2p_pri": None, "spender_pri": None,
        "dps_rank": 19, "tank_rank": None, "support_rank": None,
        "roi": "Very Low",
    },
    "Torun": {
        "strengths": "156% Berserk Axe + 150% 2-target; 3-skill budget DPS",
        "best_for": "Bench — do not invest",
        "gear": "Basic DPS gear; low priority",
        "synergies": "Forest filler only",
        "f2p_pri": None, "spender_pri": None,
        "dps_rank": 20, "tank_rank": None, "support_rank": None,
        "roi": "Very Low",
    },
}

BUILD_DEFAULTS = {
    "DPS": ("Cursed Book", "Angelic Headband", "Evolution", "ATK or CRIT", "ATK / CRIT / Skill DMG", "Dove / Dragon / Soulgaze", "Damage talents"),
    "Tank": ("Eternal Cloak", "Spirit Shield", "Evolution", "Health", "HP / DMG Reduction / DEF", "Dove / Dragon / Soulgaze", "Survival talents"),
    "Support": ("Devil's Heart", "Spirit Shield / Time Amulet", "Evolution", "Health", "Health / Speed / Buff stats", "Dove / Dragon / Soulgaze", "Support talents"),
}

ROLE_MAP = {
    "DPS": "DPS", "Tank": "Tank", "Support": "Support", "Tank-Buffer": "Tank",
    "DPS / Support": "DPS", "Support / DPS": "Support", "Tank / Support": "Tank",
    "DPS / Debuff": "DPS", "DPS (Physical)": "DPS", "DPS (Magic)": "DPS",
    "Tank / DPS": "Tank", "Support / Control": "Support", "DPS / Support (WB)": "DPS",
}


def load_master():
    rows = {}
    with open(ROOT / "x-clash-heroes-master.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows[r["Hero Name"]] = r
    return rows


def skill_summary(hero):
    skills = []
    with open(ROOT / "x-clash-heroes-skills.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["Hero Name"] == hero:
                skills.append(f"{r['Skill Name']}: {r['Effect Summary (Lv30 baseline)']}")
    return " | ".join(skills)


def write_profiles(master):
    out = ROOT / "x-clash-heroes-profiles.csv"
    fields = [
        "Hero", "Official Title", "Tier", "Faction", "Role", "Dmg Type",
        "Strengths", "Best For", "Recommended Gear", "Team Synergies",
        "All Skills Summary", "F2P Priority", "Spender Priority",
        "DPS Rank", "Tank Rank", "Support Rank", "Investment ROI", "Notes",
    ]
    dmg_from_skills = {}
    with open(ROOT / "x-clash-heroes-skills.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["Hero Name"] not in dmg_from_skills:
                dmg_from_skills[r["Hero Name"]] = r["Dmg Type"]

    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for hero, m in master.items():
            p = PROFILES[hero]
            role = m["Primary Role"] or ""
            w.writerow({
                "Hero": hero,
                "Official Title": m["Official Title"],
                "Tier": m["Overall Tier"],
                "Faction": m["Faction"],
                "Role": role,
                "Dmg Type": dmg_from_skills.get(hero, ""),
                "Strengths": p["strengths"],
                "Best For": p["best_for"],
                "Recommended Gear": p["gear"],
                "Team Synergies": p["synergies"],
                "All Skills Summary": skill_summary(hero),
                "F2P Priority": p["f2p_pri"] or "",
                "Spender Priority": p["spender_pri"] or "",
                "DPS Rank": p["dps_rank"] or "",
                "Tank Rank": p["tank_rank"] or "",
                "Support Rank": p["support_rank"] or "",
                "Investment ROI": p["roi"],
                "Notes": m.get("Notes", ""),
            })
    print(f"Wrote {out}")


def write_builds(master):
    out = ROOT / "x-clash-hero-builds.csv"
    fields = [
        "Hero", "Role", "Primary Artifact", "Secondary Artifact", "Rune Set",
        "Rune Primary Stat", "Gear Priority Substats", "Gemstones",
        "Talent Priority (PvE)", "Talent Priority (PvP)", "Talent Priority (Boss)", "Notes",
    ]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for hero, m in master.items():
            role_raw = m["Primary Role"] or "DPS"
            kind = ROLE_MAP.get(role_raw, "DPS")
            if "Tank" in role_raw:
                kind = "Tank"
            elif "Support" in role_raw or hero in ("Yord", "Denise", "Crystal", "Verna"):
                if hero in ("Sera", "Monica", "Sophia", "Fenixia", "Alvarez", "Belial", "Mirana", "Marissa", "Faerie", "Ali", "Cthylla", "Harold", "Moga", "Romano", "Torun"):
                    kind = "DPS"
                elif hero in ("Crystal", "Verna"):
                    kind = "DPS"
                elif hero in ("Yord", "Denise", "Aaron", "Reina"):
                    kind = "Support"
            defaults = BUILD_DEFAULTS[kind]
            w.writerow({
                "Hero": hero,
                "Role": f"{role_raw} ({m['Row Position']})",
                "Primary Artifact": defaults[0],
                "Secondary Artifact": defaults[1],
                "Rune Set": defaults[2],
                "Rune Primary Stat": defaults[3],
                "Gear Priority Substats": defaults[4],
                "Gemstones": defaults[5],
                "Talent Priority (PvE)": defaults[6],
                "Talent Priority (PvP)": "Damage + CRIT" if kind == "DPS" else defaults[6],
                "Talent Priority (Boss)": "Boss damage" if kind == "DPS" else defaults[6],
                "Notes": PROFILES[hero]["gear"].split(";")[0],
            })
    print(f"Wrote {out}")


def write_teams():
    out = ROOT / "x-clash-team-compositions.csv"
    teams = [
        ("F2P PvE / Campaign", "PvE", "Mixed", "Sera", "Dragonic", "Yord", "Fenixia", "Denise/Faerie", "Core F2P campaign clear"),
        ("F2P World Boss", "World Boss", "Mixed", "Yord", "Sera", "Fenixia", "Crystal", "Verna", "No dedicated tank unless Dragonic out-DPSes weakest"),
        ("F2P PvP", "PvP", "Mixed", "Sera", "Yord", "Fenixia", "Dragonic", "Andrew/Crystal", "SS tier F2P arena core"),
        ("Spender PvP", "PvP", "Mixed", "Monica", "Sophia", "Yord", "Daphne", "Valkyr/Sparta", "Top spender arena"),
        ("Spender World Boss", "World Boss", "Mixed", "Monica", "Sophia", "Yord", "Daphne", "Sera/Fenixia", "Maximum WB damage"),
        ("Forest PvP (late)", "PvP", "5 Forest (+20%)", "Monica", "Sera", "Yord", "Dragonic", "Rexar", "Faction bonus focus"),
        ("Human PvP (late)", "PvP", "5 Human (+20%)", "Sophia", "Fenixia", "Andrew", "Valkyr", "Alvarez", "Human counter meta"),
        ("Nightfall PvP", "PvP", "5 Nightfall (+20%)", "Daphne", "Belial", "Sparta", "Mirana", "Kataras", "Nightfall counter to Human"),
        ("YOUR Team 1 — Forest/Human PvP", "PvP", "3 Forest + 2 Human (+10%)", "Sera", "Dragonic", "Verna", "Andrew", "Fenixia/Sophia", "Your current roster — invest Andrew to 5★ for faction bonus"),
        ("YOUR Team 2 — World Boss", "World Boss", "3 Forest + 2 Human (+10%)", "Yord", "Sera", "Verna", "Crystal", "Andrew", "WB focus with your 5★ Forest core + Andrew Human slot"),
        ("YOUR Next Investment", "Upgrade", "—", "Andrew", "—", "—", "—", "—", "Priority over Daphne/Kataras for 3F+2H +10% bonus"),
        ("Zombie Siege (F2P)", "Zombie Siege", "Mixed", "Yord", "Sera", "Dragonic", "Fenixia", "Denise", "Buffers + AoE"),
        ("Campaign (early)", "Campaign", "Mixed", "Sera", "Dragonic", "Yord", "Fenixia", "Denise", "Before Andrew Day 60"),
    ]
    fields = ["Team Name", "Mode", "Faction Bonus", "Hero 1", "Hero 2", "Hero 3", "Hero 4", "Hero 5", "Notes"]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in teams:
            w.writerow(dict(zip(fields, row)))
    print(f"Wrote {out}")


def write_rankings():
    out = ROOT / "x-clash-hero-rankings.csv"
    rankings = []
    for hero, p in PROFILES.items():
        if p["dps_rank"]:
            rankings.append(("Top DPS", p["dps_rank"], hero, p["strengths"]))
        if p["tank_rank"]:
            rankings.append(("Top Tank", p["tank_rank"], hero, p["strengths"]))
        if p["support_rank"]:
            rankings.append(("Top Support", p["support_rank"], hero, p["strengths"]))
    rankings.sort(key=lambda x: (x[0], x[1]))
    fields = ["Category", "Rank", "Hero", "Reason"]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in rankings:
            w.writerow(dict(zip(fields, row)))
    print(f"Wrote {out}")


def write_factions():
    out = ROOT / "x-clash-faction-reference.csv"
    data = [
        ("Forest", "Beats Human", "Sera, Dragonic, Monica, Yord, Rexar, Verna, Edric, Faerie, Aaron, Moga, Torun", "3 same = +5%; 3+2 = +10%; 4 = +15%; 5 = +20%"),
        ("Human", "Beats Nightfall", "Andrew, Fenixia, Sophia, Alvarez, Valkyr, Denise, Garuda, Ali, Harold", "Human counters Nightfall (−20% dmg taken vs countered faction)"),
        ("Nightfall", "Beats Forest", "Crystal, Daphne, Kataras, Sparta, Belial, Mirana, Chakiss, Marissa, Reina, Cthylla, Romano", "Nightfall counters Forest"),
        ("Triangle", "Forest → Human → Nightfall → Forest", "—", "Pick counters for arena/rally"),
    ]
    fields = ["Faction", "Beats", "Heroes", "Team Bonus Notes"]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in data:
            w.writerow(dict(zip(fields, row)))
    print(f"Wrote {out}")


if __name__ == "__main__":
    master = load_master()
    write_profiles(master)
    write_builds(master)
    write_teams()
    write_rankings()
    write_factions()
