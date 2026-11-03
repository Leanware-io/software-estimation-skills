#!/usr/bin/env python3
"""Recalculate a formula-driven workbook and check it against expected values.

Usage: python3 recalc_check.py WORKBOOK.xlsx [--expect expected.json]

expected.json maps "Sheet!A1" to the value Python computed for that cell. The check
uses the first engine it finds: the `formulas` Python package, then LibreOffice.
It fails (exit 1) on any formula error or any expected value that does not match.
If no engine is installed it says so and exits 0: Excel and Google Sheets compute
the formulas when the file is opened.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ERRORS = ("#REF!", "#DIV/0!", "#VALUE!", "#NAME?", "#N/A", "#NUM!", "#NULL!")


def with_formulas(path):
    os.environ.setdefault("TQDM_DISABLE", "1")
    import formulas  # noqa: F401  (optional dependency)
    model = formulas.ExcelModel().loads(str(path)).finish()
    solution = model.calculate()
    values = {}
    for ref, ranges in solution.items():
        # refs look like "'[book.xlsx]SHEET'!A1"
        if "!" not in ref or ":" in ref.split("!")[1]:
            continue
        sheet = ref.split("]")[1].split("'")[0]
        cell = ref.split("!")[1]
        value = ranges.value[0][0] if hasattr(ranges, "value") else ranges
        values[f"{sheet.upper()}!{cell}"] = value
    return values, "formulas"


def find_soffice():
    for name in ("soffice", "libreoffice"):
        found = shutil.which(name)
        if found:
            return found
    mac = Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")
    return str(mac) if mac.exists() else None


def with_libreoffice(path):
    soffice = find_soffice()
    if not soffice:
        raise RuntimeError("LibreOffice not found")
    from openpyxl import load_workbook
    with tempfile.TemporaryDirectory() as tmp:
        profile = Path(tmp) / "profile"
        subprocess.run([soffice, f"-env:UserInstallation=file://{profile}", "--headless",
                        "--calc", "--convert-to", "xlsx", "--outdir", tmp, str(path)],
                       check=True, capture_output=True, timeout=180)
        wb = load_workbook(Path(tmp) / Path(path).name, data_only=True)
        values = {}
        for ws in wb.worksheets:
            for row in ws.iter_rows():
                for c in row:
                    if c.value is not None:
                        values[f"{ws.title.upper()}!{c.coordinate}"] = c.value
        return values, "LibreOffice"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("workbook")
    ap.add_argument("--expect")
    args = ap.parse_args()

    values, engine = None, None
    for attempt in (with_formulas, with_libreoffice):
        try:
            values, engine = attempt(args.workbook)
            break
        except Exception:  # engine missing or failed; try the next one
            continue
    if values is None:
        print("No spreadsheet engine found (pip install formulas, or install LibreOffice); "
              "skipped recalculation. The numbers in the summary were computed in Python, "
              "and Excel or Google Sheets will compute the formulas on open.")
        return 0

    errors = [f"{k}: {v}" for k, v in values.items() if isinstance(v, str) and v.strip() in ERRORS]
    mismatches = []
    if args.expect:
        expected = json.loads(Path(args.expect).read_text())
        for ref, want in expected.items():
            sheet, cell = ref.split("!")
            got = values.get(f"{sheet.upper()}!{cell}")
            if isinstance(want, (int, float)):
                try:
                    ok = abs(float(got) - float(want)) <= max(0.01, abs(float(want)) * 1e-6)
                except (TypeError, ValueError):
                    ok = False
            else:
                ok = str(got) == str(want)
            if not ok:
                mismatches.append(f"{ref}: workbook {got!r}, expected {want!r}")

    print(f"Recalculated with {engine}: {len(values)} cells, {len(errors)} formula errors, "
          f"{len(mismatches)} mismatches against the Python values.")
    for line in (errors + mismatches)[:40]:
        print("  " + line)
    return 1 if errors or mismatches else 0


if __name__ == "__main__":
    sys.exit(main())
