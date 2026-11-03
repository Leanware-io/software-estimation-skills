# estimate-input.json

```json
{
  "project": {
    "name": "Customer Portal",
    "prepared_by": "Your name",
    "date": "2026-11-03",
    "summary": "One paragraph restating the scope."
  },
  "settings": {
    "currency": "USD",
    "hours_per_day": 8,
    "working_days_per_month": 21,
    "qa_share": 0.2,
    "delivery_share": 0.2
  },
  "team": { "engineering": 2, "design": 0.5, "qa": 1, "delivery": 0.5 },
  "timeline_months": 4,
  "rate_scenarios": [
    {
      "name": "United States",
      "rates": {
        "engineering": { "low": 120, "high": 180 },
        "design": { "low": 90, "high": 140 },
        "qa": { "low": 70, "high": 110 },
        "delivery": { "low": 100, "high": 150 }
      }
    }
  ],
  "requirements": [
    { "ref": "R1", "text": "Customers sign in and see only their company's data." }
  ],
  "items": [
    {
      "phase": "Build",
      "epic": "Accounts and roles",
      "ref": "R1",
      "item": "Company accounts, user invites and role-based access",
      "acceptance": "An admin invites a user, assigns a role, and the user sees only their company's orders.",
      "engineering_days": 5,
      "design_days": 1.5,
      "risk_note": "+1 day: permission edge cases across roles"
    }
  ],
  "open_questions": [
    {
      "question": "Does QuickBooks hold one customer record per company or per buyer?",
      "affects": "QuickBooks sync items",
      "direction": "up",
      "why": "Per-buyer records need a matching step before the sync."
    }
  ],
  "assumptions": ["Responsive web only; no native mobile app."]
}
```

## Field rules

- `settings` is optional; the defaults are the values shown. `qa_share` and `delivery_share` are each a share of engineering plus design days.
- `rate_scenarios` can be left out of the input and supplied instead with `--rates rates-for-estimate.json` (the file the `software-market-rates` skill writes). Each scenario needs a low and high hourly rate for all four disciplines: `engineering`, `design`, `qa`, `delivery`.
- `items[].engineering_days` and `items[].design_days` are the only effort inputs. QA and delivery management days are derived. Put risk days inside the item and explain them in `risk_note`.
- No item may exceed 15 engineering days; the script stops and names the item so it can be split.
- `direction` in `open_questions` is `up`, `down` or `either`.
- The first rate scenario is the one shown per item in the Estimation sheet; the Summary sheet shows every scenario.

## estimate.json (written by the script)

The script writes `estimate.json` with the same fields plus, per item, `id` (E1, E2, ...), `qa_days`, `delivery_days` and `total_days`, and a `totals` block (days per discipline, cost low and high per scenario). The `ai-savings-pass` skill reads this file.
