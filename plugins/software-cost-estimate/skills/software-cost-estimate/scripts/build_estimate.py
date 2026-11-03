#!/usr/bin/env python3
"""Build a formula-driven, first-principles estimate workbook.

Usage: python3 build_estimate.py estimate-input.json [--rates rates-for-estimate.json] [--out DIR]

Writes "<Project> - Estimate.xlsx", estimate.json and estimate-summary.md. Every
derived number is computed here in Python too, then checked against the workbook
with recalc_check.py when a spreadsheet engine is available.
"""
import argparse
import json
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

DISCIPLINES = ("engineering", "design", "qa", "delivery")
LABELS = {"engineering": "Engineering", "design": "UI/UX design", "qa": "QA",
          "delivery": "Delivery management"}
MAX_ENGINEERING_DAYS = 15

HEADER = PatternFill("solid", fgColor="1F2933")
INPUT = PatternFill("solid", fgColor="FFF4C2")
DERIVED = PatternFill("solid", fgColor="EEF0F2")
WHITE_BOLD = Font(bold=True, color="FFFFFF")
BLUE = Font(color="1D4ED8")
BOLD = Font(bold=True)


def fail(message, code=2):
    print(message)
    sys.exit(code)


def load(args):
    data = json.loads(Path(args.input).read_text())
    if args.rates:
        rates = json.loads(Path(args.rates).read_text())
        data["rate_scenarios"] = [{"name": s["name"], "rates": s["rates"]} for s in rates["rate_scenarios"]]
        data.setdefault("settings", {}).setdefault("currency", rates.get("currency", "USD"))
    s = {"currency": "USD", "hours_per_day": 8, "working_days_per_month": 21,
         "qa_share": 0.2, "delivery_share": 0.2}
    s.update(data.get("settings") or {})
    data["settings"] = s
    data["team"] = {d: float((data.get("team") or {}).get(d, 0)) for d in DISCIPLINES}
    data.setdefault("timeline_months", 0)
    if not data.get("rate_scenarios"):
        fail("No rates. Supply rate_scenarios in the input or --rates rates-for-estimate.json. Never guess a rate.")
    for sc in data["rate_scenarios"]:
        for d in DISCIPLINES:
            r = (sc.get("rates") or {}).get(d)
            if not r or r.get("low") is None or r.get("high") is None:
                fail(f"Rate scenario '{sc.get('name')}' has no low/high rate for {d}.")
    too_big = [i["item"] for i in data["items"] if float(i.get("engineering_days", 0)) > MAX_ENGINEERING_DAYS]
    if too_big:
        fail("Split these items (over 15 engineering days): " + "; ".join(too_big))
    return data


def compute(data):
    s = data["settings"]
    items = []
    for n, raw in enumerate(data["items"], start=1):
        e, d = float(raw.get("engineering_days", 0)), float(raw.get("design_days", 0))
        it = dict(raw, id=f"E{n}", engineering_days=e, design_days=d,
                  qa_days=(e + d) * s["qa_share"], delivery_days=(e + d) * s["delivery_share"])
        it["total_days"] = e + d + it["qa_days"] + it["delivery_days"]
        items.append(it)
    days = {d: sum(i[f"{d}_days"] for i in items) for d in DISCIPLINES}
    days["total"] = sum(days[d] for d in DISCIPLINES)
    hpd = s["hours_per_day"]

    def cost(day_map, sc, band):
        return sum(day_map[d] * sc["rates"][d][band] for d in DISCIPLINES) * hpd

    first = data["rate_scenarios"][0]
    for it in items:
        it["cost_low"] = cost({d: it[f"{d}_days"] for d in DISCIPLINES}, first, "low")
        it["cost_high"] = cost({d: it[f"{d}_days"] for d in DISCIPLINES}, first, "high")
    regions = []
    for sc in data["rate_scenarios"]:
        lo, hi = cost(days, sc, "low"), cost(days, sc, "high")
        team_days = {d: data["team"][d] * data["timeline_months"] * s["working_days_per_month"] for d in DISCIPLINES}
        tlo, thi = cost(team_days, sc, "low"), cost(team_days, sc, "high")
        mid, tmid = (lo + hi) / 2, (tlo + thi) / 2
        regions.append({"name": sc["name"], "low": lo, "mid": mid, "high": hi,
                        "team_low": tlo, "team_high": thi, "gap": (tmid / mid - 1) if mid else 0})
    capacity = []
    for d in DISCIPLINES:
        people = data["team"][d]
        months = days[d] / people / s["working_days_per_month"] if people else 0
        load = months / data["timeline_months"] if data["timeline_months"] else 0
        status = "Bottleneck" if load > 1 else ("Tight" if load > 0.85 else "OK")
        capacity.append({"discipline": d, "days": days[d], "people": people, "months": months,
                         "load": load, "status": status})
    epics = OrderedDict()
    for it in items:
        ep = epics.setdefault(it["epic"], {d: 0.0 for d in DISCIPLINES})
        for d in DISCIPLINES:
            ep[d] += it[f"{d}_days"]
    phases = OrderedDict()
    for it in items:
        phases[it["phase"]] = phases.get(it["phase"], 0.0) + it["total_days"]
    return {"items": items, "days": days, "regions": regions, "capacity": capacity,
            "epics": epics, "phases": phases}


def style_header(ws, row, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill, cell.font = HEADER, WHITE_BOLD
        cell.alignment = Alignment(wrap_text=True, vertical="center")


def build(data, calc, path):
    s = data["settings"]
    money = '"$"#,##0' if s["currency"] == "USD" else "#,##0"
    wb = Workbook()
    expect = {}

    # Settings
    st = wb.active
    st.title = "Settings"
    st["A1"] = "Settings (yellow cells are inputs; everything else is calculated)"
    st["A1"].font = BOLD
    p = data.get("project") or {}
    rows = [(3, "Project", p.get("name", "")), (4, "Prepared by", p.get("prepared_by", "")),
            (5, "Date", p.get("date", "")), (7, "Currency", s["currency"]),
            (8, "Hours per day", s["hours_per_day"]), (9, "Working days per month", s["working_days_per_month"]),
            (10, "QA share of engineering + design", s["qa_share"]),
            (11, "Delivery management share of engineering + design", s["delivery_share"]),
            (12, "Timeline (months)", data["timeline_months"])]
    for r, label, value in rows:
        st.cell(row=r, column=1, value=label)
        c = st.cell(row=r, column=2, value=value)
        c.fill, c.font = INPUT, BLUE
    st["B10"].number_format = st["B11"].number_format = "0%"
    st["A14"] = "People available (full-time equivalents)"
    st["A14"].font = BOLD
    for k, d in enumerate(DISCIPLINES):
        st.cell(row=15 + k, column=1, value=LABELS[d])
        c = st.cell(row=15 + k, column=2, value=data["team"][d])
        c.fill, c.font = INPUT, BLUE
    st["A20"] = f"Hourly rates by region ({s['currency']}); sources in the rates table"
    st["A20"].font = BOLD
    head = ["Region"] + [f"{LABELS[d]} {b}" for d in DISCIPLINES for b in ("low", "high")]
    for c, h in enumerate(head, start=1):
        st.cell(row=21, column=c, value=h)
    style_header(st, 21, len(head))
    for k, sc in enumerate(data["rate_scenarios"]):
        r = 22 + k
        st.cell(row=r, column=1, value=sc["name"])
        for j, d in enumerate(DISCIPLINES):
            for b, band in enumerate(("low", "high")):
                c = st.cell(row=r, column=2 + 2 * j + b, value=float(sc["rates"][d][band]))
                c.fill, c.font, c.number_format = INPUT, BLUE, money
    st.column_dimensions["A"].width = 48
    for col in range(2, 10):
        st.column_dimensions[get_column_letter(col)].width = 16
    rate_col = {d: (get_column_letter(2 + 2 * j), get_column_letter(3 + 2 * j)) for j, d in enumerate(DISCIPLINES)}

    # Estimation
    es = wb.create_sheet("Estimation")
    first = data["rate_scenarios"][0]["name"]
    head = ["#", "Phase", "Epic", "Ref", "Work item", "Acceptance criteria (preliminary)", "Risk / buffer note",
            "Engineering (days)", "UI/UX design (days)", "QA (days)", "Delivery mgmt (days)", "Total (days)",
            f"Cost low ({first})", f"Cost high ({first})"]
    for c, h in enumerate(head, start=1):
        es.cell(row=1, column=c, value=h)
    style_header(es, 1, len(head))
    n = len(calc["items"])
    last = n + 1
    for k, it in enumerate(calc["items"]):
        r = 2 + k
        for c, v in enumerate([it["id"], it["phase"], it["epic"], it.get("ref", ""), it["item"],
                               it.get("acceptance", ""), it.get("risk_note", "")], start=1):
            es.cell(row=r, column=c, value=v).alignment = Alignment(wrap_text=True, vertical="top")
        for c, v in ((8, it["engineering_days"]), (9, it["design_days"])):
            cell = es.cell(row=r, column=c, value=v)
            cell.fill, cell.font = INPUT, BLUE
        es.cell(row=r, column=10, value=f"=(H{r}+I{r})*Settings!$B$10")
        es.cell(row=r, column=11, value=f"=(H{r}+I{r})*Settings!$B$11")
        es.cell(row=r, column=12, value=f"=SUM(H{r}:K{r})")
        for col, band in ((13, 0), (14, 1)):
            refs = "+".join(f"{L}{r}*Settings!${rate_col[d][band]}$22"
                            for L, d in zip("HIJK", DISCIPLINES))
            es.cell(row=r, column=col, value=f"=({refs})*Settings!$B$8")
        for col in range(10, 15):
            es.cell(row=r, column=col).fill = DERIVED
        for col in range(8, 13):
            es.cell(row=r, column=col).number_format = "0.0"
        es.cell(row=r, column=13).number_format = es.cell(row=r, column=14).number_format = money
    tot = last + 1
    es.cell(row=tot, column=5, value="Total").font = BOLD
    for col in range(8, 15):
        L = get_column_letter(col)
        c = es.cell(row=tot, column=col, value=f"=SUM({L}2:{L}{last})")
        c.font = BOLD
        c.number_format = money if col >= 13 else "0.0"
    for L, key in zip("HIJKL", list(DISCIPLINES) + ["total"]):
        expect[f"Estimation!{L}{tot}"] = calc["days"][key]
    expect[f"Estimation!M{tot}"] = sum(i["cost_low"] for i in calc["items"])
    expect[f"Estimation!N{tot}"] = sum(i["cost_high"] for i in calc["items"])
    for col, w in zip("ABCDEFGHIJKLMN", (5, 12, 22, 7, 40, 48, 32, 12, 12, 10, 12, 10, 14, 14)):
        es.column_dimensions[col].width = w
    es.freeze_panes = "F2"
    days_ref = {d: f"Estimation!${L}${tot}" for L, d in zip("HIJK", DISCIPLINES)}

    # Capacity
    cp = wb.create_sheet("Capacity")
    head = ["Discipline", "Total days", "People", "Months of effort", "Timeline (months)", "Load", "Status"]
    for c, h in enumerate(head, start=1):
        cp.cell(row=1, column=c, value=h)
    style_header(cp, 1, len(head))
    for k, d in enumerate(DISCIPLINES):
        r = 2 + k
        cp.cell(row=r, column=1, value=LABELS[d])
        cp.cell(row=r, column=2, value=f"={days_ref[d]}").number_format = "0.0"
        cp.cell(row=r, column=3, value=f"=Settings!$B${15 + k}")
        cp.cell(row=r, column=4, value=f"=IF(C{r}>0,B{r}/C{r}/Settings!$B$9,0)").number_format = "0.0"
        cp.cell(row=r, column=5, value="=Settings!$B$12")
        cp.cell(row=r, column=6, value=f"=IF(E{r}>0,D{r}/E{r},0)").number_format = "0%"
        cp.cell(row=r, column=7, value=f'=IF(F{r}>1,"Bottleneck",IF(F{r}>0.85,"Tight","OK"))')
        expect[f"Capacity!D{r}"] = calc["capacity"][k]["months"]
        expect[f"Capacity!G{r}"] = calc["capacity"][k]["status"]
    cp["A7"] = "Months of effort = total days / people / working days per month. Over 100% load means the plan has a bottleneck, not just a cost."
    cp.column_dimensions["A"].width = 24
    for col in "BCDEFG":
        cp.column_dimensions[col].width = 16

    # Summary
    sm = wb.create_sheet("Summary")
    sm["A1"] = "Days by epic"
    sm["A1"].font = BOLD
    head = ["Epic", "Engineering", "UI/UX design", "QA", "Delivery mgmt", "Total days", "Share"]
    for c, h in enumerate(head, start=1):
        sm.cell(row=2, column=c, value=h)
    style_header(sm, 2, len(head))
    r = 3
    first_epic_row = r
    for epic in calc["epics"]:
        sm.cell(row=r, column=1, value=epic)
        for j, L in enumerate("HIJK"):
            sm.cell(row=r, column=2 + j,
                    value=f"=SUMIF(Estimation!$C$2:$C${last},$A{r},Estimation!{L}$2:{L}${last})").number_format = "0.0"
        sm.cell(row=r, column=6, value=f"=SUM(B{r}:E{r})").number_format = "0.0"
        r += 1
    epic_total = r
    sm.cell(row=epic_total, column=1, value="Total").font = BOLD
    for col in range(2, 7):
        L = get_column_letter(col)
        sm.cell(row=epic_total, column=col, value=f"=SUM({L}{first_epic_row}:{L}{epic_total - 1})").number_format = "0.0"
    for rr in range(first_epic_row, epic_total + 1):
        sm.cell(row=rr, column=7, value=f"=IF($F${epic_total}>0,F{rr}/$F${epic_total},0)").number_format = "0%"
    expect[f"Summary!F{epic_total}"] = calc["days"]["total"]

    r = epic_total + 3
    sm.cell(row=r, column=1, value="Cost by rate region (bottom-up: days x hours per day x hourly rate, per discipline)").font = BOLD
    head = ["Region", "Low", "Mid", "High"]
    for c, h in enumerate(head, start=1):
        sm.cell(row=r + 1, column=c, value=h)
    style_header(sm, r + 1, len(head))
    region_rows = []
    for k, reg in enumerate(calc["regions"]):
        rr = r + 2 + k
        sr = 22 + k
        sm.cell(row=rr, column=1, value=f"=Settings!$A${sr}")
        for col, band in ((2, 0), (4, 1)):
            refs = "+".join(f"{days_ref[d]}*Settings!${rate_col[d][band]}${sr}" for d in DISCIPLINES)
            sm.cell(row=rr, column=col, value=f"=({refs})*Settings!$B$8").number_format = money
        sm.cell(row=rr, column=3, value=f"=AVERAGE(B{rr},D{rr})").number_format = money
        expect[f"Summary!B{rr}"], expect[f"Summary!C{rr}"], expect[f"Summary!D{rr}"] = reg["low"], reg["mid"], reg["high"]
        region_rows.append(rr)

    r = region_rows[-1] + 3
    sm.cell(row=r, column=1, value="Team-based cross-check (people x timeline x working days x hours x rate)").font = BOLD
    head = ["Region", "Team cost low", "Team cost high", "Bottom-up mid", "Gap (team mid vs bottom-up mid)"]
    for c, h in enumerate(head, start=1):
        sm.cell(row=r + 1, column=c, value=h)
    style_header(sm, r + 1, len(head))
    for k, reg in enumerate(calc["regions"]):
        rr = r + 2 + k
        sr = 22 + k
        sm.cell(row=rr, column=1, value=f"=Settings!$A${sr}")
        for col, band in ((2, 0), (3, 1)):
            refs = "+".join(f"Settings!$B${15 + j}*Settings!${rate_col[d][band]}${sr}" for j, d in enumerate(DISCIPLINES))
            sm.cell(row=rr, column=col,
                    value=f"=({refs})*Settings!$B$12*Settings!$B$9*Settings!$B$8").number_format = money
        sm.cell(row=rr, column=4, value=f"=C{region_rows[k]}").number_format = money
        sm.cell(row=rr, column=5, value=f"=IF(D{rr}>0,AVERAGE(B{rr},C{rr})/D{rr}-1,0)").number_format = "0%"
        expect[f"Summary!B{rr}"], expect[f"Summary!C{rr}"] = reg["team_low"], reg["team_high"]

    r = r + 2 + len(calc["regions"]) + 2
    sm.cell(row=r, column=1, value="Days by phase").font = BOLD
    for c, h in enumerate(["Phase", "Total days", "Share"], start=1):
        sm.cell(row=r + 1, column=c, value=h)
    style_header(sm, r + 1, 3)
    for k, phase in enumerate(calc["phases"]):
        rr = r + 2 + k
        sm.cell(row=rr, column=1, value=phase)
        sm.cell(row=rr, column=2, value=f"=SUMIF(Estimation!$B$2:$B${last},$A{rr},Estimation!$L$2:$L${last})").number_format = "0.0"
        sm.cell(row=rr, column=3, value=f"=IF(Estimation!$L${tot}>0,B{rr}/Estimation!$L${tot},0)").number_format = "0%"
    sm.column_dimensions["A"].width = 40
    for col in "BCDEFG":
        sm.column_dimensions[col].width = 18

    # Scope and open questions
    sc = wb.create_sheet("Scope")
    sc["A1"], sc["A1"].font = "Requirements", BOLD
    r = 2
    for req in data.get("requirements", []):
        sc.cell(row=r, column=1, value=req.get("ref"))
        sc.cell(row=r, column=2, value=req.get("text")).alignment = Alignment(wrap_text=True)
        r += 1
    r += 1
    sc.cell(row=r, column=1, value="Assumptions").font = BOLD
    for a in data.get("assumptions", []):
        r += 1
        sc.cell(row=r, column=2, value=a).alignment = Alignment(wrap_text=True)
    sc.column_dimensions["A"].width, sc.column_dimensions["B"].width = 10, 100

    oq = wb.create_sheet("Open Questions")
    head = ["#", "Question", "Affects", "Direction", "Why it matters"]
    for c, h in enumerate(head, start=1):
        oq.cell(row=1, column=c, value=h)
    style_header(oq, 1, len(head))
    for k, q in enumerate(data.get("open_questions", []), start=1):
        for c, v in enumerate([k, q.get("question"), q.get("affects"), q.get("direction"), q.get("why")], start=1):
            oq.cell(row=1 + k, column=c, value=v).alignment = Alignment(wrap_text=True, vertical="top")
    for col, w in zip("ABCDE", (5, 60, 30, 10, 60)):
        oq.column_dimensions[col].width = w

    wb.save(path)
    return expect


def fmt_money(v, currency):
    return f"${v:,.0f}" if currency == "USD" else f"{v:,.0f} {currency}"


def summary_md(data, calc):
    cur = data["settings"]["currency"]
    out = [f"# {data.get('project', {}).get('name', 'Estimate')}: first-principles estimate", "",
           "## Days by epic", "",
           "| Epic | Engineering | UI/UX design | QA | Delivery mgmt | Total days |", "|---|---|---|---|---|---|"]
    for epic, d in calc["epics"].items():
        out.append(f"| {epic} | " + " | ".join(f"{d[x]:.1f}" for x in DISCIPLINES) + f" | {sum(d.values()):.1f} |")
    t = calc["days"]
    out.append("| **Total** | " + " | ".join(f"**{t[x]:.1f}**" for x in DISCIPLINES) + f" | **{t['total']:.1f}** |")
    out += ["", f"QA and delivery management are derived at {data['settings']['qa_share']:.0%} and "
                f"{data['settings']['delivery_share']:.0%} of engineering plus design. "
                f"Days are senior-engineer days of {data['settings']['hours_per_day']:g} hours.", "",
            "## Cost by rate region", "", "| Region | Low | High |", "|---|---|---|"]
    for reg in calc["regions"]:
        out.append(f"| {reg['name']} | {fmt_money(reg['low'], cur)} | {fmt_money(reg['high'], cur)} |")
    out += ["", "## Capacity check", "", "| Discipline | Days | People | Months of effort | Load | Status |",
            "|---|---|---|---|---|---|"]
    for c in calc["capacity"]:
        out.append(f"| {LABELS[c['discipline']]} | {c['days']:.1f} | {c['people']:g} | {c['months']:.1f} | "
                   f"{c['load']:.0%} | {c['status']} |")
    out += ["", f"## Team-based cross-check ({data['timeline_months']} months)", "",
            "| Region | Team cost low | Team cost high | Gap vs bottom-up |", "|---|---|---|---|"]
    for reg in calc["regions"]:
        out.append(f"| {reg['name']} | {fmt_money(reg['team_low'], cur)} | {fmt_money(reg['team_high'], cur)} | {reg['gap']:+.0%} |")
    qs = data.get("open_questions", [])
    if qs:
        out += ["", "## Open questions that would change the number", ""]
        for k, q in enumerate(qs, start=1):
            out.append(f"{k}. {q['question']} Affects: {q.get('affects', '')}. Direction: {q.get('direction', '')}. {q.get('why', '')}".rstrip())
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--rates")
    ap.add_argument("--out", default=".")
    args = ap.parse_args()
    data = load(args)
    calc = compute(data)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    name = (data.get("project") or {}).get("name", "Project")
    xlsx = out / f"{name} - Estimate.xlsx"
    expect = build(data, calc, xlsx)
    (out / "expected-values.json").write_text(json.dumps(expect, indent=2))

    est = {k: data.get(k) for k in ("project", "settings", "team", "timeline_months", "rate_scenarios",
                                     "requirements", "open_questions", "assumptions")}
    est["items"] = calc["items"]
    est["totals"] = {"days": calc["days"], "regions": calc["regions"]}
    (out / "estimate.json").write_text(json.dumps(est, indent=2) + "\n")
    (out / "estimate-summary.md").write_text(summary_md(data, calc))

    print(f"Wrote {xlsx}, estimate.json and estimate-summary.md ({len(calc['items'])} work items, "
          f"{calc['days']['total']:.1f} days).")
    for reg in calc["regions"]:
        print(f"  {reg['name']}: {fmt_money(reg['low'], data['settings']['currency'])} to "
              f"{fmt_money(reg['high'], data['settings']['currency'])}")
    check = Path(__file__).with_name("recalc_check.py")
    result = subprocess.run([sys.executable, str(check), str(xlsx), "--expect", str(out / "expected-values.json")])
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
