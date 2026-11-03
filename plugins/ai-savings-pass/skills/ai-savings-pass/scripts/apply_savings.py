#!/usr/bin/env python3
"""Apply the per-task AI savings pass to an estimate.

Usage: python3 apply_savings.py estimate.json savings-input.json [--data ../data/savings-2026-10.json] [--out DIR]

Splits every work item into activities, scores nine attributes per activity,
computes the saving (floor + (aggressive - floor) x D, then the gates), prices code
review and QA on the hours without AI, adds the downstream reserve, and writes
"<Project> - AI Savings.xlsx", savings.json and savings-summary.md.
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
LABELS = {"engineering": "Engineering", "design": "UI/UX design", "qa": "QA", "delivery": "Delivery management"}
FLAGS = ("agent_writes_security_code", "cold_start", "large_unsliced_diff")
HEADER = PatternFill("solid", fgColor="1F2933")
INPUT = PatternFill("solid", fgColor="FFF4C2")
DERIVED = PatternFill("solid", fgColor="EEF0F2")
WHITE_BOLD = Font(bold=True, color="FFFFFF")
BLUE = Font(color="1D4ED8")
BOLD = Font(bold=True)
DEFAULT_DATA = Path(__file__).resolve().parent.parent / "data" / "savings-2026-10.json"


def fail(msg, code=2):
    print(msg)
    sys.exit(code)


def saving_for(act, scores, flags, weights):
    """Return (D, gate points, base, saving, caps fired, slowdown)."""
    total_w = sum(weights.values())
    d = sum(scores[k] * w for k, w in weights.items()) / (2 * total_w)
    agg, floor = act["aggressive"], act["floor"]
    base = floor + (agg - floor) * d
    caps = []
    s = base
    if scores["verifiability"] == 0 and scores["stakes"] == 0:
        s = floor
        caps.append("G1 no automatic check and high stakes: floor")
    points = 0
    touches_code = act["code_producing"] or act["id"].startswith("code_review")
    if touches_code and scores["stakes"] == 0:
        p = 10 if flags.get("agent_writes_security_code") else 5
        points += p
        caps.append(f"G2 auth, payments or personal data: -{p} points")
    if touches_code and flags.get("cold_start"):
        points += 5
        caps.append("G3 unfamiliar codebase without agent-ready docs: -5 points")
    if touches_code and flags.get("large_unsliced_diff"):
        points += 5
        caps.append("G4 large unsliced AI change: -5 points")
    s -= points / 100
    lower = min(0.0, floor)
    if s < lower:
        s = lower
        caps.append("held at the lower bound")
    if s > agg:
        s = agg
    slowdown = bool(act["code_producing"] and d < 0.25)
    return d, points, base, s, caps, slowdown


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("estimate")
    ap.add_argument("savings_input")
    ap.add_argument("--data", default=str(DEFAULT_DATA))
    ap.add_argument("--out", default=".")
    args = ap.parse_args()

    est = json.loads(Path(args.estimate).read_text())
    inp = json.loads(Path(args.savings_input).read_text())
    table = json.loads(Path(args.data).read_text())
    acts = {a["id"]: a for a in table["activities"]}
    for sub in table["subrows"]:
        acts[sub["id"]] = dict(sub, row=acts[sub["parent"]]["row"])
    weights = OrderedDict((a["id"], a["weight"]) for a in table["attributes"])
    hpd = est["settings"]["hours_per_day"]
    currency = est["settings"].get("currency", "USD")

    by_id = {i["id"]: i for i in inp.get("items", [])}
    missing = [i["id"] for i in est["items"] if i["id"] not in by_id]
    if missing:
        fail("The savings input has no entry for: " + ", ".join(missing) + ". Every work item needs one.")

    rows, problems = [], []
    for item in est["items"]:
        spec = by_id[item["id"]]
        for disc in DISCIPLINES:
            days = float(item.get(f"{disc}_days", 0))
            if days <= 0:
                continue
            splits = (spec.get("splits") or {}).get(disc) or table["default_splits"].get(disc)
            if not splits:
                problems.append(f"{item['id']} has {days:g} {disc} days but no {disc} split")
                continue
            share_sum = sum(float(s["share"]) for s in splits)
            if abs(share_sum - 1) > 0.011:
                problems.append(f"{item['id']} {disc} shares add up to {share_sum:.2f}, not 1")
                continue
            for s in splits:
                act = acts.get(s["activity"])
                if not act:
                    problems.append(f"{item['id']}: unknown activity '{s['activity']}'")
                    continue
                scores = dict(inp.get("default_scores") or {})
                scores.update(spec.get("scores") or {})
                scores.update(s.get("scores") or {})
                absent = [k for k in weights if k not in scores]
                if absent:
                    problems.append(f"{item['id']} / {s['activity']}: no score for {', '.join(absent)}")
                    continue
                bad = [k for k in weights if scores[k] not in (0, 1, 2)]
                if bad:
                    problems.append(f"{item['id']} / {s['activity']}: scores must be 0, 1 or 2 ({', '.join(bad)})")
                    continue
                flags = dict(inp.get("default_flags") or {})
                flags.update(spec.get("flags") or {})
                flags.update(s.get("flags") or {})
                d, points, base, sv, caps, slow = saving_for(act, scores, flags, weights)
                row_days = days * float(s["share"])
                rows.append({"item_id": item["id"], "item": item["item"], "epic": item["epic"], "discipline": disc,
                             "activity": act["id"], "activity_label": act["label"], "days": row_days,
                             "aggressive": act["aggressive"], "floor": act["floor"],
                             "lower_bound": min(0.0, act["floor"]), "scores": {k: scores[k] for k in weights},
                             "flags": {f: bool(flags.get(f)) for f in FLAGS},
                             "code_producing": act["code_producing"],
                             "touches_code": act["code_producing"] or act["id"].startswith("code_review"), "D": d, "gate_points": points,
                             "base": base, "saving": sv, "saved_days": row_days * sv, "caps": caps,
                             "slowdown": slow, "zero_scored": [k for k in weights if scores[k] == 0]})
    if problems:
        fail("Fix the savings input:\n  " + "\n  ".join(problems))

    has_review_or_qa = any(r["activity"].startswith("code_review") or r["discipline"] == "qa" for r in rows)
    res = table["downstream_reserve"]
    lam = res["applied_lambda"] + (0 if has_review_or_qa else res["no_review_or_qa_lines_extra"])
    code_saved = sum(r["saved_days"] for r in rows if r["code_producing"])
    reserve = lam * max(0.0, code_saved)

    disc_tot = OrderedDict()
    for disc in DISCIPLINES:
        without = sum(r["days"] for r in rows if r["discipline"] == disc)
        saved = sum(r["saved_days"] for r in rows if r["discipline"] == disc)
        rsv = reserve if disc == "engineering" else 0.0
        disc_tot[disc] = {"without": without, "saved": saved, "reserve": rsv, "with": without - saved + rsv}
    for disc in DISCIPLINES:
        want = est["totals"]["days"][disc]
        if abs(disc_tot[disc]["without"] - want) > 0.01:
            fail(f"{disc}: the split rows hold {disc_tot[disc]['without']:.2f} days but the estimate has {want:.2f}")
    days_without = sum(v["without"] for v in disc_tot.values())
    days_with = sum(v["with"] for v in disc_tot.values())

    regions = []
    for sc in est["rate_scenarios"]:
        reg = {"name": sc["name"]}
        for band in ("low", "high"):
            reg[f"without_{band}"] = sum(disc_tot[d]["without"] * sc["rates"][d][band] for d in DISCIPLINES) * hpd
            reg[f"with_{band}"] = sum(disc_tot[d]["with"] * sc["rates"][d][band] for d in DISCIPLINES) * hpd
        reg["saving_share"] = 1 - reg["with_low"] / reg["without_low"] if reg["without_low"] else 0
        regions.append(reg)

    items = OrderedDict()
    for r in rows:
        it = items.setdefault(r["item_id"], {"item": r["item"], "epic": r["epic"], "days": 0.0, "saved": 0.0,
                                             "min_D": 1.0, "caps": set(), "zero": set(), "slowdown": False})
        it["days"] += r["days"]
        it["saved"] += r["saved_days"]
        it["min_D"] = min(it["min_D"], r["D"])
        it["caps"].update(c.split(":")[0] for c in r["caps"] if c.startswith("G"))
        it["zero"].update(r["zero_scored"])
        it["slowdown"] = it["slowdown"] or r["slowdown"]
    for iid, it in items.items():
        it["share"] = it["saved"] / it["days"] if it["days"] else 0
        it["move_up"] = by_id[iid].get("move_up", "")

    eng = est["team"].get("engineering", 0)
    dpm = est["settings"]["working_days_per_month"]
    eng_months = (disc_tot["engineering"]["without"] / eng / dpm, disc_tot["engineering"]["with"] / eng / dpm) if eng else (0, 0)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    name = (est.get("project") or {}).get("name", "Project")
    xlsx = out / f"{name} - AI Savings.xlsx"
    expect = write_workbook(xlsx, est, table, weights, rows, lam, has_review_or_qa, disc_tot, regions, currency)
    (out / "savings-expected-values.json").write_text(json.dumps(expect, indent=2))
    result = {"table_version": table["version"], "table_dated": table["dated"], "lambda": lam,
              "has_review_or_qa_lines": has_review_or_qa, "reserve_days": reserve,
              "days_without_ai": days_without, "days_with_ai": days_with, "disciplines": disc_tot,
              "regions": regions, "rows": rows,
              "items": {k: dict(v, caps=sorted(v["caps"]), zero=sorted(v["zero"])) for k, v in items.items()},
              "engineering_months": {"without_ai": eng_months[0], "with_ai": eng_months[1]}}
    (out / "savings.json").write_text(json.dumps(result, indent=2) + "\n")
    (out / "savings-summary.md").write_text(summary(est, table, result, currency))
    print(f"Wrote {xlsx}, savings.json and savings-summary.md: {days_without:.1f} days without AI, "
          f"{days_with:.1f} with AI ({1 - days_with / days_without:.0%} fewer).")
    check = Path(__file__).with_name("recalc_check.py")
    sys.exit(subprocess.run([sys.executable, str(check), str(xlsx), "--expect",
                             str(out / "savings-expected-values.json")]).returncode)


def header(ws, row, labels):
    for c, h in enumerate(labels, start=1):
        cell = ws.cell(row=row, column=c, value=h)
        cell.fill, cell.font = HEADER, WHITE_BOLD
        cell.alignment = Alignment(wrap_text=True, vertical="center")


def write_workbook(path, est, table, weights, rows, lam, has_rq, disc_tot, regions, currency):
    money = '"$"#,##0' if currency == "USD" else "#,##0"
    wb = Workbook()
    expect = {}
    st = wb.active
    st.title = "Settings"
    st["A1"] = f"AI savings settings (table dated {table['dated']}, re-date by {table['redate_by']})"
    st["A1"].font = BOLD
    st["A3"], st["B3"] = "Hours per day", est["settings"]["hours_per_day"]
    st["A4"], st["B4"] = "Downstream reserve (share of hours saved on code-producing rows)", lam
    st["C4"] = "0.10; 0.20 when the estimate has no code-review or QA lines" + ("" if has_rq else " (none here)")
    st["B4"].number_format = "0%"
    for c in ("B3", "B4"):
        st[c].fill, st[c].font = INPUT, BLUE
    st["A6"] = "Attribute weights"
    st["A6"].font = BOLD
    for j, (k, w) in enumerate(weights.items()):
        st.cell(row=7, column=2 + j, value=k)
        c = st.cell(row=8, column=2 + j, value=w)
        c.fill, c.font = INPUT, BLUE
    st["A8"] = "Weight"
    wl, wr = "B", get_column_letter(1 + len(weights))
    st["A10"] = f"Hourly rates by region ({currency})"
    st["A10"].font = BOLD
    header(st, 11, ["Region"] + [f"{LABELS[d]} {b}" for d in DISCIPLINES for b in ("low", "high")])
    for k, sc in enumerate(est["rate_scenarios"]):
        st.cell(row=12 + k, column=1, value=sc["name"])
        for j, d in enumerate(DISCIPLINES):
            for b, band in enumerate(("low", "high")):
                c = st.cell(row=12 + k, column=2 + 2 * j + b, value=float(sc["rates"][d][band]))
                c.fill, c.font, c.number_format = INPUT, BLUE, money
    st.column_dimensions["A"].width = 60
    rate_col = {d: (get_column_letter(2 + 2 * j), get_column_letter(3 + 2 * j)) for j, d in enumerate(DISCIPLINES)}

    sv = wb.create_sheet("Savings")
    attr_labels = [a["label"] for a in table["attributes"]]
    cols = (["Item", "Work item", "Discipline", "Activity", "Days without AI", "Aggressive", "Floor", "Lower bound"]
            + attr_labels + ["Agent writes security code", "Cold start", "Large unsliced diff", "Code-producing", "Touches code",
                             "D", "Gate points", "Base saving", "Saving", "Days saved", "Slowdown risk",
                             "Caps fired", "Attributes scored 0"])
    header(sv, 1, cols)
    n_attr = len(weights)
    c_score0 = 9
    c_flag0 = c_score0 + n_attr
    L = {name: get_column_letter(i) for i, name in enumerate(cols, start=1)}
    score_letters = [get_column_letter(c_score0 + j) for j in range(n_attr)]
    vL, stkL = score_letters[0], score_letters[-1]
    secL, coldL, diffL, codeL, touchL = (get_column_letter(c_flag0 + j) for j in range(5))
    for k, r in enumerate(rows):
        x = 2 + k
        vals = [r["item_id"], r["item"], LABELS[r["discipline"]], r["activity_label"], r["days"],
                r["aggressive"], r["floor"], r["lower_bound"]] + list(r["scores"].values()) + \
               ["Yes" if r["flags"][f] else "No" for f in FLAGS] + ["Yes" if r["code_producing"] else "No",
                                                                    "Yes" if r["touches_code"] else "No"]
        for c, v in enumerate(vals, start=1):
            cell = sv.cell(row=x, column=c, value=v)
            if c >= c_score0 and c < c_flag0 + 3:
                cell.fill, cell.font = INPUT, BLUE
        wsum = "+".join(f"{sl}{x}*Settings!${get_column_letter(2 + j)}$8" for j, sl in enumerate(score_letters))
        sv[f"{L['D']}{x}"] = f"=({wsum})/(2*SUM(Settings!${wl}$8:${wr}$8))"
        sv[f"{L['Gate points']}{x}"] = (f'=IF({touchL}{x}="Yes",IF({stkL}{x}=0,IF({secL}{x}="Yes",10,5),0)'
                                        f'+IF({coldL}{x}="Yes",5,0)+IF({diffL}{x}="Yes",5,0),0)')
        sv[f"{L['Base saving']}{x}"] = f"=G{x}+(F{x}-G{x})*{L['D']}{x}"
        sv[f"{L['Saving']}{x}"] = (f"=MIN(F{x},MAX(H{x},IF(AND({vL}{x}=0,{stkL}{x}=0),G{x},{L['Base saving']}{x})"
                                   f"-{L['Gate points']}{x}/100))")
        sv[f"{L['Days saved']}{x}"] = f"=E{x}*{L['Saving']}{x}"
        sv[f"{L['Slowdown risk']}{x}"] = f'=IF(AND({codeL}{x}="Yes",{L["D"]}{x}<0.25),"Slowdown risk","")'
        sv[f"{L['Caps fired']}{x}"] = "; ".join(r["caps"])
        sv[f"{L['Attributes scored 0']}{x}"] = ", ".join(r["zero_scored"])
        for name in ("Aggressive", "Floor", "Lower bound", "D", "Base saving", "Saving"):
            sv[f"{L[name]}{x}"].number_format = "0%"
        sv[f"E{x}"].number_format = sv[f"{L['Days saved']}{x}"].number_format = "0.00"
        for name in ("D", "Gate points", "Base saving", "Saving", "Days saved", "Slowdown risk"):
            sv[f"{L[name]}{x}"].fill = DERIVED
        expect[f"Savings!{L['Saving']}{x}"] = r["saving"]
        expect[f"Savings!{L['Days saved']}{x}"] = r["saved_days"]
    last = len(rows) + 1
    tot = last + 1
    sv.cell(row=tot, column=2, value="Total").font = BOLD
    for name in ("Days without AI", "Days saved"):
        sv[f"{L[name]}{tot}"] = f"=SUM({L[name]}2:{L[name]}{last})"
        sv[f"{L[name]}{tot}"].font = BOLD
        sv[f"{L[name]}{tot}"].number_format = "0.0"
    sv.freeze_panes = "E2"
    for c, w in enumerate([6, 36, 14, 34] + [10] * (len(cols) - 4), start=1):
        sv.column_dimensions[get_column_letter(c)].width = w
    sv.column_dimensions[L["Caps fired"]].width = 50
    sv.column_dimensions[L["Attributes scored 0"]].width = 30

    tt = wb.create_sheet("Totals")
    tt["A1"] = "Totals without and with AI (days)"
    tt["A1"].font = BOLD
    header(tt, 2, ["Discipline", "Days without AI", "Days saved", "Downstream reserve", "Days with AI"])
    rng = lambda col: f"Savings!${L[col]}$2:${L[col]}${last}"  # noqa: E731
    for k, d in enumerate(DISCIPLINES):
        x = 3 + k
        tt.cell(row=x, column=1, value=LABELS[d])
        tt.cell(row=x, column=2, value=f'=SUMIF({rng("Discipline")},$A{x},{rng("Days without AI")})')
        tt.cell(row=x, column=3, value=f'=SUMIF({rng("Discipline")},$A{x},{rng("Days saved")})')
        tt.cell(row=x, column=4, value=(f'=Settings!$B$4*MAX(0,SUMIF({rng("Code-producing")},"Yes",{rng("Days saved")}))'
                                         if d == "engineering" else 0))
        tt.cell(row=x, column=5, value=f"=B{x}-C{x}+D{x}")
        for c in range(2, 6):
            tt.cell(row=x, column=c).number_format = "0.0"
        expect[f"Totals!E{x}"] = disc_tot[d]["with"]
    tt.cell(row=7, column=1, value="Total").font = BOLD
    for c in "BCDE":
        tt[f"{c}7"] = f"=SUM({c}3:{c}6)"
        tt[f"{c}7"].number_format = "0.0"
        tt[f"{c}7"].font = BOLD
    tt["A8"], tt["B8"] = "Effort saved", "=IF(B7>0,1-E7/B7,0)"
    tt["B8"].number_format = "0%"
    tt["A9"] = "Reserve: review, QA, security and fixes that AI output creates downstream; assigned to engineering."
    tt["A11"] = "Cost by rate region"
    tt["A11"].font = BOLD
    header(tt, 12, ["Region", "Without AI low", "Without AI high", "With AI low", "With AI high", "Saving"])
    for k, reg in enumerate(regions):
        x = 13 + k
        sr = 12 + k
        tt.cell(row=x, column=1, value=f"=Settings!$A${sr}")
        for col, (src, band) in zip((2, 3, 4, 5), (("B", 0), ("B", 1), ("E", 0), ("E", 1))):
            refs = "+".join(f"${src}${3 + j}*Settings!${rate_col[d][band]}${sr}" for j, d in enumerate(DISCIPLINES))
            tt.cell(row=x, column=col, value=f"=({refs})*Settings!$B$3").number_format = money
        tt.cell(row=x, column=6, value=f"=IF(B{x}>0,1-D{x}/B{x},0)").number_format = "0%"
        expect[f"Totals!B{x}"], expect[f"Totals!C{x}"] = reg["without_low"], reg["without_high"]
        expect[f"Totals!D{x}"], expect[f"Totals!E{x}"] = reg["with_low"], reg["with_high"]
    tt.column_dimensions["A"].width = 30
    for c in "BCDEF":
        tt.column_dimensions[c].width = 18

    ac = wb.create_sheet("Activities")
    header(ac, 1, ["Row", "Activity", "Aggressive (applied)", "Floor", "Expected (reference, not applied)",
                   "Code-producing", "What AI does not save"])
    for k, a in enumerate(table["activities"] + table["subrows"]):
        x = 2 + k
        vals = [a.get("row", ""), a["label"] if "parent" not in a else "  " + a["label"], a["aggressive"], a["floor"],
                a["expected_reference"], "Yes" if a["code_producing"] else "No", a.get("what_ai_does_not_save", "")]
        for c, v in enumerate(vals, start=1):
            ac.cell(row=x, column=c, value=v)
        for c in (3, 4, 5):
            ac.cell(row=x, column=c).number_format = "0%"
    ac.column_dimensions["B"].width = 60
    ac.column_dimensions["G"].width = 90
    wb.save(path)
    return expect


def money_fmt(v, currency):
    return f"${v:,.0f}" if currency == "USD" else f"{v:,.0f} {currency}"


def summary(est, table, res, currency):
    m = lambda v: money_fmt(v, currency)  # noqa: E731
    name = (est.get("project") or {}).get("name", "Estimate")
    o = [f"# {name}: AI savings pass", "",
         f"Savings table dated {table['dated']} (re-date by {table['redate_by']}). Aggressive by default: an item that is easy "
         "to hand to AI gets the full aggressive figure for its activity, a hard one falls to the floor.", "",
         "## Without AI and with AI", "", "| Region | Without AI | With AI | Saving |", "|---|---|---|---|"]
    for r in res["regions"]:
        o.append(f"| {r['name']} | {m(r['without_low'])} to {m(r['without_high'])} | "
                 f"{m(r['with_low'])} to {m(r['with_high'])} | {r['saving_share']:.0%} |")
    dt = res["disciplines"]
    o += ["", "| Discipline | Days without AI | Days saved | Reserve | Days with AI |", "|---|---|---|---|---|"]
    for d, v in dt.items():
        o.append(f"| {LABELS[d]} | {v['without']:.1f} | {v['saved']:.1f} | {v['reserve']:.1f} | {v['with']:.1f} |")
    o.append(f"| **Total** | **{res['days_without_ai']:.1f}** | **{sum(v['saved'] for v in dt.values()):.1f}** | "
             f"**{res['reserve_days']:.1f}** | **{res['days_with_ai']:.1f}** |")
    o += ["", f"The reserve adds back {res['lambda']:.0%} of the days saved on code-producing work, for the review, QA "
              "and fixes that AI output creates downstream. Code review and QA are priced on the hours without AI.", "",
          "## Per work item", "", "| Item | Work item | Days | Saved | Lowest D | Caps fired |", "|---|---|---|---|---|---|"]
    for iid, it in res["items"].items():
        o.append(f"| {iid} | {it['item']} | {it['days']:.1f} | {it['share']:.0%} | {it['min_D']:.2f} | "
                 f"{', '.join(it['caps']) or 'none'} |")
    barely = sorted((kv for kv in res["items"].items() if kv[1]["days"] >= 1), key=lambda kv: kv[1]["share"])[:5]
    o += ["", "## Barely discounted, and what would move them up", ""]
    for iid, it in barely:
        why = ", ".join(it["zero"]) or "no attribute at 0"
        flag = " Slowdown risk." if it["slowdown"] else ""
        o.append(f"- {iid} {it['item']}: {it['share']:.0%} saved. Scored 0 on: {why}.{flag} {it['move_up']}".rstrip())
    em = res["engineering_months"]
    o += ["", "## Hours freed versus calendar", "",
          f"Engineering effort goes from {em['without_ai']:.1f} to {em['with_ai']:.1f} months for the team in the estimate. "
          "That is the most the schedule could shorten if engineering is the bottleneck. Client feedback cycles, approvals, "
          "access to accounts and environments, and release windows do not compress, so the calendar saving is smaller "
          "than the effort saving.", "",
          "These are planning figures for a senior team that uses AI coding tools every day, not measured results.", ""]
    return "\n".join(o)


if __name__ == "__main__":
    main()
