#!/usr/bin/env python3
"""Fail if the ai-savings-pass data file drifts from the published savings table.

The fixture is the table printed in the companion article. Every activity label,
aggressive figure, floor and "what AI does not save" text must match it exactly.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "plugins/ai-savings-pass/skills/ai-savings-pass/data/savings-2026-10.json"
FIXTURE = ROOT / "tests/fixtures/brief-savings-table.md"


def pct(text):
    return int(re.match(r"(-?\d+)%", text).group(1)) / 100


def main():
    rows = [[c.strip() for c in line.strip().strip("|").split("|")]
            for line in FIXTURE.read_text().splitlines()[2:] if line.startswith("|")]
    acts = json.loads(DATA.read_text())["activities"]
    errors = []
    if len(rows) != len(acts):
        errors.append(f"{len(rows)} rows in the published table, {len(acts)} in the data file")
    for n, (row, act) in enumerate(zip(rows, acts), start=1):
        label, aggressive, floor, not_saved = row
        for name, want, got in (("label", label, act["label"]), ("aggressive", pct(aggressive), act["aggressive"]),
                                ("floor", pct(floor), act["floor"]),
                                ("what AI does not save", not_saved, act["what_ai_does_not_save"])):
            if want != got:
                errors.append(f"row {n} {name}: table {want!r}, data {got!r}")
    for line in errors:
        print(line)
    print("Savings table matches the published table." if not errors else f"{len(errors)} differences.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
