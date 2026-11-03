#!/usr/bin/env python3
"""Validate a sourced rates file and write the rate tables and blended rates.

Usage: python3 rates_table.py rates.json [--out DIR] [--drop-unsourced]

Writes rates.md, rates.csv and rates-for-estimate.json. Exits with code 2 when a
row has no source, URL or month checked (unless --drop-unsourced), and with code 3
when the proposed team needs a rate cell the table does not have.
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

METRICS = {
    "billed_hourly": "Billed hourly rates (firms and freelancers)",
    "salary_annual": "Annual salaries (employees)",
    "loaded_hourly": "Loaded hourly cost (employees: salary plus overhead)",
}
ENGAGEMENTS = {"firm", "freelancer", "employee"}
DISCIPLINES = ("engineering", "design", "qa", "delivery")
MONTH = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
CSV_FIELDS = ["role", "seniority", "region", "country", "engagement", "metric",
              "low", "high", "currency", "source", "url", "checked", "note"]


def problems_with(row):
    issues = []
    for field in ("role", "seniority", "region", "engagement", "metric", "low", "high"):
        if row.get(field) in (None, ""):
            issues.append(f"missing {field}")
    for field in ("source", "url"):
        if not str(row.get(field) or "").strip():
            issues.append(f"missing {field}")
    if not MONTH.match(str(row.get("checked") or "")):
        issues.append("checked must be YYYY-MM")
    if row.get("metric") and row["metric"] not in METRICS:
        issues.append(f"unknown metric {row['metric']}")
    if row.get("engagement") and row["engagement"] not in ENGAGEMENTS:
        issues.append(f"unknown engagement {row['engagement']}")
    try:
        if float(row["low"]) > float(row["high"]):
            issues.append("low is above high")
    except (KeyError, TypeError, ValueError):
        issues.append("low and high must be numbers")
    return issues


def key(role, seniority, region, engagement, metric):
    return (role.strip().lower(), seniority.strip().lower(), region.strip().lower(),
            engagement, metric)


def money(value, currency):
    symbol = "$" if currency == "USD" else ""
    suffix = "" if symbol else f" {currency}"
    return f"{symbol}{value:,.0f}{suffix}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rates")
    ap.add_argument("--out", default=".")
    ap.add_argument("--drop-unsourced", action="store_true")
    args = ap.parse_args()

    data = json.loads(Path(args.rates).read_text())
    currency = data.get("currency", "USD")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    rows, rejected = [], []
    for i, row in enumerate(data.get("rows", []), start=1):
        issues = problems_with(row)
        (rejected if issues else rows).append((i, row, issues))
    if rejected:
        print("Rows without a usable source or value:")
        for i, row, issues in rejected:
            print(f"  row {i}: {row.get('role')} / {row.get('seniority')} / {row.get('region')}: {', '.join(issues)}")
        if not args.drop_unsourced:
            print("Refusing to write a table with unsourced cells. Source them or remove them.")
            sys.exit(2)
    rows = [r for _, r, _ in rows]

    # Tables
    lines = [f"# Software development rates ({currency})", ""]
    for metric, title in METRICS.items():
        subset = [r for r in rows if r["metric"] == metric]
        if not subset:
            continue
        unit = "per year" if metric == "salary_annual" else "per hour"
        lines += [f"## {title}, {unit}", "",
                  "| Role | Seniority | Region | Country | Engagement | Low | High | Source | Checked | Note |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        for r in sorted(subset, key=lambda r: (r["region"], r["role"], r["seniority"])):
            lines.append(
                f"| {r['role']} | {r['seniority']} | {r['region']} | {r.get('country') or 'Region-wide'} | "
                f"{r['engagement']} | {money(float(r['low']), currency)} | {money(float(r['high']), currency)} | "
                f"[{r['source']}]({r['url']}) | {r['checked']} | {r.get('note', '')} |")
        lines.append("")

    with open(out / "rates.csv", "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for r in rows:
            writer.writerow({f: (currency if f == "currency" else r.get(f, "")) for f in CSV_FIELDS})

    # Blended rate for the proposed team, per region. When a cell has several
    # sourced rows (several countries or several sources), its range spans them.
    team = data.get("team") or []
    blend = data.get("blend") or {}
    engagement = blend.get("engagement", "firm")
    metric = blend.get("metric", "billed_hourly")
    regions = blend.get("regions") or sorted({r["region"] for r in rows})
    cells = {}
    for r in rows:
        k = key(r["role"], r["seniority"], r["region"], r["engagement"], r["metric"])
        lo, hi = cells.get(k, (float("inf"), float("-inf")))
        cells[k] = (min(lo, float(r["low"])), max(hi, float(r["high"])))

    estimate = {"currency": currency, "engagement": engagement, "metric": metric,
                "source_file": "rates.csv", "rate_scenarios": []}
    missing, fallbacks = [], []
    if team:
        total_fte = sum(float(m["fte"]) for m in team)
        mix = ", ".join(f"{m['fte']} {m['seniority'].lower()} {m['role'].lower()}" for m in team)
        lines += [f"## Blended {metric.replace('_', ' ')} rate for the proposed team ({engagement})", "",
                  f"Team: {mix} ({total_fte:g} FTE). Weighted by FTE.", "",
                  "| Region | Low | Mid | High |", "|---|---|---|---|"]
        for region in regions:
            lo_sum = hi_sum = 0.0
            per_discipline = {}
            for m in team:
                cell = cells.get(key(m["role"], m["seniority"], region, engagement, metric))
                if not cell:
                    # A source with no seniority split is recorded as "All levels"; use it, and say so.
                    cell = cells.get(key(m["role"], "All levels", region, engagement, metric))
                    if cell:
                        fallbacks.append(f"{m['role']} in {region}: all-levels figure used for {m['seniority'].lower()}")
                if not cell:
                    missing.append(f"{m['seniority']} {m['role']} / {region} / {engagement} / {metric}")
                    continue
                lo_sum += cell[0] * float(m["fte"])
                hi_sum += cell[1] * float(m["fte"])
                disc = m.get("discipline")
                if disc in DISCIPLINES:
                    d = per_discipline.setdefault(disc, [0.0, 0.0, 0.0])
                    d[0] += cell[0] * float(m["fte"])
                    d[1] += cell[1] * float(m["fte"])
                    d[2] += float(m["fte"])
            lo, hi = lo_sum / total_fte, hi_sum / total_fte
            lines.append(f"| {region} | {money(lo, currency)} | {money((lo + hi) / 2, currency)} | {money(hi, currency)} |")
            scenario = {"name": region, "blended": {"low": round(lo, 2), "high": round(hi, 2)}, "rates": {}}
            for disc, (dlo, dhi, fte) in per_discipline.items():
                scenario["rates"][disc] = {"low": round(dlo / fte, 2), "high": round(dhi / fte, 2)}
            estimate["rate_scenarios"].append(scenario)
        lines.append("")
        lines.append("Where a cell has several sourced rows (countries or sources), its range spans all of them.")
        for f in fallbacks:
            lines.append(f"- {f}.")
        lines.append("")
    if missing:
        print("The proposed team needs rate cells the table does not have:")
        for m in missing:
            print(f"  {m}")
        sys.exit(3)

    (out / "rates.md").write_text("\n".join(lines))
    (out / "rates-for-estimate.json").write_text(json.dumps(estimate, indent=2) + "\n")
    print(f"Wrote {len(rows)} sourced rows to {out / 'rates.md'} and {out / 'rates.csv'}")
    for s in estimate["rate_scenarios"]:
        b = s["blended"]
        print(f"  {s['name']}: blended {money(b['low'], currency)} to {money(b['high'], currency)} per hour")


if __name__ == "__main__":
    main()
