# Customer Portal: first-principles estimate

## Days by epic

| Epic | Engineering | UI/UX design | QA | Delivery mgmt | Total days |
|---|---|---|---|---|---|
| Discovery and design | 10.0 | 13.0 | 4.6 | 4.6 | 32.2 |
| Foundations | 17.0 | 1.0 | 3.6 | 3.6 | 25.2 |
| Accounts, roles and approvals | 24.0 | 6.0 | 6.0 | 6.0 | 42.0 |
| Ordering and reorder | 21.0 | 8.5 | 5.9 | 5.9 | 41.3 |
| Invoices and Stripe payments | 12.0 | 3.0 | 3.0 | 3.0 | 21.0 |
| QuickBooks Online sync | 53.0 | 2.0 | 11.0 | 11.0 | 77.0 |
| Staff back office | 16.0 | 5.5 | 4.3 | 4.3 | 30.1 |
| Quality and launch | 33.0 | 3.0 | 7.2 | 7.2 | 50.4 |
| **Total** | **186.0** | **42.0** | **45.6** | **45.6** | **319.2** |

QA and delivery management are derived at 20% and 20% of engineering plus design. A day is 8 working hours.

## Cost by rate region

| Region | Low | High |
|---|---|---|
| United States | $324,297 | $473,024 |
| Latin America | $131,606 | $177,312 |
| Eastern Europe | $121,248 | $217,046 |

## Capacity check

| Discipline | Days | People | Months of effort | Load | Status |
|---|---|---|---|---|---|
| Engineering | 186.0 | 2 | 4.4 | 111% | Bottleneck |
| UI/UX design | 42.0 | 0.5 | 4.0 | 100% | Tight |
| QA | 45.6 | 0.5 | 4.3 | 109% | Bottleneck |
| Delivery management | 45.6 | 0.5 | 4.3 | 109% | Bottleneck |

## Team-based cross-check (4 months)

| Region | Team cost low | Team cost high | Gap vs bottom-up |
|---|---|---|---|
| United States | $297,706 | $435,322 | -8% |
| Latin America | $120,288 | $162,624 | -8% |
| Eastern Europe | $110,880 | $200,256 | -8% |

## Open questions that would change the number

1. How does the distributor hold customer-specific prices: QuickBooks price rules, a single list price, or a spreadsheet? Affects: Product catalog; products, prices and stock sync; one-click reorder. Direction: up. QuickBooks price rules may not be reachable through the API; if not, the portal needs its own price table and a way to maintain it.
2. Does QuickBooks hold one customer per company, or sub-customers per site or buyer, and how many duplicates exist? Affects: Customer mapping and sync; initial data load. Direction: up. Sub-customers and duplicates need a matching step and a staff review queue before onboarding.
3. Which side owns which fields (for example, can staff edit a portal-created invoice in QuickBooks), and who resolves conflicts? Affects: Conflict detection and resolution; invoices from QuickBooks; order administration. Direction: either. Clear field ownership removes most conflicts; open-ended two-way editing makes the conflict module larger.
4. How should Stripe payments and fees be booked in QuickBooks (undeposited funds or a clearing account, fee expense, payout reconciliation), and are partial payments or card surcharges allowed? Affects: Stripe payments recorded in QuickBooks; reconciliation; card payment. Direction: up. Payout-level reconciliation and partial payments add mapping and edge cases.
5. Does the distributor use QuickBooks automated sales tax, and do customers have exemptions? Affects: Portal orders to QuickBooks invoices; cart and checkout. Direction: up. Tax must be shown at checkout and match the QuickBooks invoice; automated sales tax limits what the API lets us set.
6. Where does stock come from (QuickBooks inventory quantities, a warehouse system, or not tracked)? Affects: Products, prices and stock sync; one-click reorder; product catalog. Direction: either. A separate warehouse system is a new integration; no stock tracking removes work.
7. Is one approval limit per company enough, or are per-user limits, multi-level approvals or budgets needed? Affects: Order approval workflow; company admin user management. Direction: up. Each extra rule adds states, notifications and tests to the approval workflow.
8. Do new orders need a full catalog with search, or is reorder plus quick add by item code enough at launch? Affects: Product catalog; cart and checkout. Direction: down. A quick-add-by-code flow is smaller than a browsable catalog.
