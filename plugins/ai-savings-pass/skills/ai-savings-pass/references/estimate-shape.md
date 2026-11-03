# The estimate.json the pass reads

`software-cost-estimate` writes this file. To run the pass on an estimate from somewhere else, write it by hand with these fields (QA and delivery days can be zero if the estimate has none; the reserve then rises to 20%).

```json
{
  "project": { "name": "Customer Portal" },
  "settings": { "currency": "USD", "hours_per_day": 8, "working_days_per_month": 21 },
  "team": { "engineering": 2, "design": 0.5, "qa": 1, "delivery": 0.5 },
  "rate_scenarios": [
    { "name": "United States",
      "rates": { "engineering": { "low": 120, "high": 180 }, "design": { "low": 90, "high": 140 },
                 "qa": { "low": 70, "high": 110 }, "delivery": { "low": 100, "high": 150 } } }
  ],
  "items": [
    { "id": "E1", "epic": "Accounts and roles", "item": "Company accounts and role-based access",
      "engineering_days": 5, "design_days": 1.5, "qa_days": 1.3, "delivery_days": 1.3 }
  ],
  "totals": { "days": { "engineering": 5, "design": 1.5, "qa": 1.3, "delivery": 1.3 } }
}
```

`totals.days` must equal the sum of the items per discipline; the script checks it. Rates come from a sourced rates table, never from memory.
