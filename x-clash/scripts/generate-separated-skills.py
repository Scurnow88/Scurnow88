#!/usr/bin/env python3
"""Generate separated skill descriptions for Google Sheets."""
import csv
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def slot_label(skill_num: int, skill_type: str, total: int) -> str:
    st = skill_type.lower()
    if "bond" in st or "awaken" in st:
        return f"Skill {skill_num} (Bond / Awaken Passive)"
    if st == "innate":
        return f"Skill {skill_num} (Innate Passive)"
    if st == "passive":
        return f"Skill {skill_num} (Passive/Battle Skill)"
    if "(cs)" in st:
        return f"Skill {skill_num} (Combat Skill / CS)"
    if skill_num == 1 and st.startswith("active"):
        return f"Skill {skill_num} (Basic Attack)"
    if "(buff)" in st or "(aoe)" in st:
        return f"Skill {skill_num} (Active Skill)"
    if st.startswith("active"):
        return f"Skill {skill_num} (Active Skill)"
    return f"Skill {skill_num} ({skill_type})"


def clean_effect(name: str, effect: str, dmg_type: str) -> str:
    e = effect.strip()
    # Normalize common shorthand from CSV
    m = re.match(
        r"^Deals\s+([\d.]+%)\s+ATK\s+(Physical|Magic)\s+DMG\s+single\.?\s*enemy?\.?$",
        e,
        re.I,
    )
    if m:
        e = f"Deals {m.group(1)} ATK {m.group(2)} DMG to a single enemy."
    m = re.match(r"^([\d.]+%)\s+(Physical|Magic)\s+single\.?$", e, re.I)
    if m:
        e = f"Deals {m.group(1)} {m.group(2)} DMG to a single enemy."
    else:
        e = re.sub(r"\bsingle\.\s*$", "to a single enemy.", e, flags=re.I)
        e = re.sub(r"\bsingle\s*$", "to a single enemy.", e, flags=re.I)
        if re.match(r"^[\d.]+%", e) and "deals" not in e.lower() and "to " not in e.lower():
            kind = dmg_type or "DMG"
            if "Physical" not in e and "Magic" not in e and kind:
                e = f"Deals {e} {kind} DMG"
            else:
                e = f"Deals {e}"
    if not e.lower().startswith(name.lower()):
        e = f"{name} — {e}"
    else:
        e = e.replace(f"{name} ", f"{name} — ", 1)
    e = re.sub(r"to a to a single enemy(?: enemy)?\.?", "to a single enemy.", e)
    e = re.sub(r"\s+", " ", e).strip()
    return e


def expand_stars(star_gate: str, skill_type: str, effect: str, dmg_type: str) -> str:
    sg = star_gate.strip()
    if not sg or sg.lower() == "innate":
        return "  Innate — max level 1/1, no star scaling."
    if sg.lower() == "fixed":
        return "  Fixed bonus — no star scaling."
    if sg.lower().startswith("unlocks"):
        return f"  {sg} — bond passive unlock."
    lines = []

    # ★1-5: +30/+70/+120/+185/+270%
    m = re.match(r"★1-5:\s*\+([^/]+)/\+([^/]+)/\+([^/]+)/\+([^/]+)/\+([^%]+)%", sg)
    if m:
        vals = m.groups()
        label = "physical DMG" if dmg_type == "Physical" else "magic DMG" if dmg_type == "Magic" else "bonus DMG"
        for i, v in enumerate(vals, 1):
            lines.append(f"  ★{i}: +{v}% {label}")
        lines.append(f"  (★5 adds up to +{vals[-1]}% bonus {label} on top of base skill scaling)")
        return "\n".join(lines)

    # ★1-5: +15/+30/...
    m = re.match(r"★1-5:\s*\+([^/]+)/\+([^/]+)/\+([^/]+)/\+([^/]+)/\+([^%]+)%", sg)
    if m and not lines:
        vals = m.groups()
        label = "physical DMG" if dmg_type == "Physical" else "magic DMG" if dmg_type == "Magic" else "bonus DMG"
        for i, v in enumerate(vals, 1):
            lines.append(f"  ★{i}: +{v}% {label}")
        return "\n".join(lines)

    # ★1-5: +20/+45/+70/+100/+150%
    m = re.match(r"★1-5:\s*\+(\d+)/\+(\d+)/\+(\d+)/\+(\d+)/\+(\d+)%", sg)
    if m:
        vals = m.groups()
        label = "physical DMG" if dmg_type == "Physical" else "magic DMG" if dmg_type == "Magic" else "bonus DMG"
        for i, v in enumerate(vals, 1):
            lines.append(f"  ★{i}: +{v}% {label}")
        return "\n".join(lines)

    # ★1-5: −2% per star / +3% per star / +4% per star
    m = re.match(r"★1-5:\s*([+−-])(\d+(?:\.\d+)?)% per star", sg)
    if m:
        sign, val = m.group(1), m.group(2)
        sign = "−" if sign in "−-" else "+"
        unit = "DMG reduction" if any(x in effect.lower() for x in ("taken", "reduce", "−")) else "additional"
        for i in range(1, 6):
            lines.append(f"  ★{i}: {sign}{val}% {unit}")
        total = float(val) * 5
        lines.append(f"  (★5: {sign}{total:g}% total from stars on top of base effect)")
        return "\n".join(lines)

  # ★1-5: +2 Speed, −1% per star
    if "★1-5:" in sg and "per star" in sg and "," in sg:
        parts = sg.replace("★1-5:", "").strip().split(",")
        for i in range(1, 6):
            detail = " / ".join(p.strip() for p in parts)
            lines.append(f"  ★{i}: {detail}")
        return "\n".join(lines)

    # ★1-4: +4% per star
    m = re.match(r"★1-4:\s*([+−-])(\d+(?:\.\d+)?)% per star", sg)
    if m:
        sign, val = m.group(1), m.group(2)
        sign = "−" if sign in "−-" else "+"
        for i in range(1, 5):
            lines.append(f"  ★{i}: {sign}{val}% additional")
        lines.append(f"  ★5: (see in-game — often requires 5★ awaken)")
        return "\n".join(lines)

    # ★1-3: +4%; ★4: 2 turns; ★5: +4%
    if ";" in sg:
        for part in sg.split(";"):
            part = part.strip()
            lines.append(f"  {part}")
        return "\n".join(lines)

    # ★1: +30%; ★2: 12 hits; ...
    if re.search(r"★\d", sg):
        for part in re.split(r";\s*", sg):
            part = part.strip()
            if part:
                lines.append(f"  {part}")
        return "\n".join(lines)

    # ★1-4: Human +4/8/12/16%; ★5: 2 turns
    if "★1-4:" in sg:
        lines.append(f"  {sg}")
        return "\n".join(lines)

    # ★1-2: +5% DEF; ★3: all allies; ...
    if "★1-2:" in sg or "★1-3:" in sg:
        for part in sg.split(";"):
            lines.append(f"  {part.strip()}")
        return "\n".join(lines)

    # ★1-5: +10% DEF per star
    m = re.match(r"★1-5:\s*\+(\d+)% DEF per star", sg)
    if m:
        v = m.group(1)
        for i in range(1, 6):
            lines.append(f"  ★{i}: +{v}% DEF additional")
        lines.append(f"  (★5: +{int(v) * 5}% DEF from stars on top of base effect)")
        return "\n".join(lines)

    # ★1-3: +4%; ★4: 2 turns; ★5: +4%
    if sg.startswith("★1-3:"):
        for part in sg.split(";"):
            lines.append(f"  {part.strip()}")
        return "\n".join(lines)

    # ★1-5: +2% DMG, +5% resources per star
    if "resources per star" in sg:
        for i in range(1, 6):
            lines.append(f"  ★{i}: +2% monster DMG / +5% resources after kills")
        return "\n".join(lines)

    return f"  {sg}"


def format_skill(name, skill_type, effect, dmg_type, star_gate) -> str:
    header = clean_effect(name, effect, dmg_type)
    stars = expand_stars(star_gate, skill_type, effect, dmg_type)
    if skill_type.lower() in ("bond/awaken",) or "bond" in skill_type.lower():
        if star_gate.lower() == "fixed":
            return f'{header}\n  Passive, always active when unlocked — fixed bonus, no star scaling.'
    return f"{header}\n{stars}"


def load_skills():
    by_hero = defaultdict(list)
    with open(ROOT / "x-clash-heroes-skills.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            num = int(r["Skill Slot"].split()[1])
            by_hero[r["Hero Name"]].append((num, r))
    for h in by_hero:
        by_hero[h].sort(key=lambda x: x[0])
    return by_hero


def load_meta():
    meta = {}
    with open(ROOT / "x-clash-heroes-master.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            meta[r["Hero Name"]] = r
    return meta


def write_wide(by_hero, meta):
    out = ROOT / "x-clash-heroes-skills-separated.csv"
    fields = [
        "Hero", "Official Title", "Tier", "Faction", "Role", "Dmg Type",
        "Skill 1 Label", "Skill 1",
        "Skill 2 Label", "Skill 2",
        "Skill 3 Label", "Skill 3",
        "Skill 4 Label", "Skill 4",
    ]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for hero in sorted(by_hero.keys(), key=lambda h: (meta.get(h, {}).get("Overall Tier", "Z"), h)):
            skills = [r for _, r in by_hero[hero]]
            m = meta.get(hero, {})
            row = {
                "Hero": hero,
                "Official Title": m.get("Official Title", ""),
                "Tier": m.get("Overall Tier", ""),
                "Faction": m.get("Faction", ""),
                "Role": m.get("Primary Role", ""),
                "Dmg Type": skills[0]["Dmg Type"] if skills else "",
            }
            for i in range(4):
                n = i + 1
                if i < len(skills):
                    s = skills[i]
                    label = slot_label(n, s["Skill Type"], len(skills))
                    text = format_skill(
                        s["Skill Name"], s["Skill Type"],
                        s["Effect Summary (Lv30 baseline)"],
                        s["Dmg Type"], s["Star Gate (★1-★5)"],
                    )
                    row[f"Skill {n} Label"] = label
                    row[f"Skill {n}"] = text
                else:
                    row[f"Skill {n} Label"] = ""
                    row[f"Skill {n}"] = ""
            w.writerow(row)
    print(f"Wrote {out}")


def write_long(by_hero, meta):
    out = ROOT / "x-clash-heroes-skills-separated-long.csv"
    fields = ["Hero", "Official Title", "Tier", "Faction", "Role", "Skill Slot Label", "Skill Description"]
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for hero in sorted(by_hero.keys(), key=lambda h: (meta.get(h, {}).get("Overall Tier", "Z"), h)):
            m = meta.get(hero, {})
            for num, s in sorted(by_hero[hero], key=lambda x: x[0]):
                w.writerow({
                    "Hero": hero,
                    "Official Title": m.get("Official Title", ""),
                    "Tier": m.get("Overall Tier", ""),
                    "Faction": m.get("Faction", ""),
                    "Role": m.get("Primary Role", ""),
                    "Skill Slot Label": slot_label(num, s["Skill Type"], len(by_hero[hero])),
                    "Skill Description": format_skill(
                        s["Skill Name"], s["Skill Type"],
                        s["Effect Summary (Lv30 baseline)"],
                        s["Dmg Type"], s["Star Gate (★1-★5)"],
                    ),
                })
    print(f"Wrote {out}")


if __name__ == "__main__":
    by_hero = load_skills()
    meta = load_meta()
    write_wide(by_hero, meta)
    write_long(by_hero, meta)
