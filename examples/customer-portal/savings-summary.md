# Customer Portal: AI savings pass

Savings table dated 2026-10-28 (re-date by 2027-04-28). Aggressive by default: an item that is easy to hand to AI gets the full aggressive figure for its activity, a hard one falls to the floor.

## Without AI and with AI

| Region | Without AI | With AI | Saving |
|---|---|---|---|
| United States | $324,297 to $473,024 | $230,707 to $336,577 | 29% |
| Latin America | $131,606 to $177,312 | $92,419 to $125,210 | 30% |
| Eastern Europe | $121,248 to $217,046 | $85,323 to $154,526 | 30% |

| Discipline | Days without AI | Days saved | Reserve | Days with AI |
|---|---|---|---|---|
| Engineering | 186.0 | 68.1 | 7.5 | 125.5 |
| UI/UX design | 42.0 | 9.1 | 0.0 | 32.9 |
| QA | 45.6 | 16.9 | 0.0 | 28.7 |
| Delivery management | 45.6 | 6.8 | 0.0 | 38.8 |
| **Total** | **319.2** | **100.9** | **7.5** | **225.8** |

The reserve adds back 10% of the days saved on code-producing work, for the review, QA and fixes that AI output creates downstream. Code review and QA are priced on the hours without AI.

## Per work item

| Item | Work item | Days | Saved | Lowest D (code rows) | Caps fired |
|---|---|---|---|---|---|
| E1 | Discovery workshops, backlog and acceptance criteria | 7.0 | 28% | 0.33 | none |
| E2 | QuickBooks Online technical spike and data audit of the distributor's company file | 5.6 | 21% | 0.47 | none |
| E3 | Architecture and data model design (tenancy, roles, orders, invoices, payments, sync mapping) | 4.2 | 16% | 0.33 | none |
| E4 | User flows and wireframes for the customer portal and the back office | 8.4 | 34% | 0.33 | none |
| E5 | Visual design and responsive design system | 7.0 | 23% | 0.33 | none |
| E6 | Repository, CI/CD pipeline, agent instructions and test commands | 5.6 | 50% | 0.80 | none |
| E7 | Environments and infrastructure as code (dev, staging, production, managed Postgres, secrets, backups) | 5.6 | 29% | 0.63 | none |
| E8 | Data model and migrations | 5.6 | 34% | 0.63 | none |
| E9 | Audit log, error monitoring and structured logging | 2.8 | 39% | 0.63 | none |
| E10 | UI component library and responsive app shell | 5.6 | 41% | 0.80 | none |
| E11 | Sign-in, password reset and session management | 7.0 | 32% | 0.77 | G2 high stakes (auth, payments, personal data, compliance or irreversible changes) |
| E12 | Company accounts and invitation flow | 7.7 | 29% | 0.63 | G2 high stakes (auth, payments, personal data, compliance or irreversible changes) |
| E13 | Role-based access control and tenant isolation | 8.4 | 23% | 0.53 | G2 high stakes (auth, payments, personal data, compliance or irreversible changes) |
| E14 | Order approval workflow | 12.6 | 36% | 0.63 | none |
| E15 | Company admin user management (users, roles, approval limit, deactivation) | 6.3 | 30% | 0.63 | G2 high stakes (auth, payments, personal data, compliance or irreversible changes) |
| E16 | Product catalog with customer prices and stock | 9.8 | 36% | 0.67 | none |
| E17 | Cart and checkout | 9.8 | 36% | 0.67 | none |
| E18 | Order history with search and filters | 8.4 | 38% | 0.80 | none |
| E19 | One-click reorder with change summary | 7.7 | 36% | 0.67 | none |
| E20 | Email notifications (invites, approvals, order confirmations, payment receipts) | 5.6 | 38% | 0.80 | none |
| E21 | Invoice list and detail | 6.3 | 38% | 0.80 | none |
| E22 | Card payment of one or several invoices through Stripe | 9.1 | 29% | 0.63 | G2 high stakes (auth, payments, personal data, compliance or irreversible changes) |
| E23 | Stripe webhooks for payment status | 5.6 | 28% | 0.63 | G2 high stakes (auth, payments, personal data, compliance or irreversible changes) |
| E24 | QuickBooks OAuth connection, token rotation and production app approval | 5.6 | 24% | 0.57 | G2 high stakes (auth, payments, personal data, compliance or irreversible changes) |
| E25 | Sync engine: job queue, change data capture and webhooks, idempotency, rate limits, retries, sync log | 11.2 | 32% | 0.53 | none |
| E26 | Customer mapping and two-way customer sync | 8.4 | 33% | 0.53 | none |
| E27 | Products, prices and stock sync from QuickBooks | 7.0 | 33% | 0.53 | none |
| E28 | Portal orders to QuickBooks invoices | 8.4 | 29% | 0.57 | G2 high stakes (auth, payments, personal data, compliance or irreversible changes) |
| E29 | Invoices and payments from QuickBooks to the portal | 7.0 | 35% | 0.60 | none |
| E30 | Stripe payments recorded in QuickBooks | 5.6 | 26% | 0.50 | G2 high stakes (auth, payments, personal data, compliance or irreversible changes) |
| E31 | Conflict detection and staff resolution | 11.9 | 32% | 0.53 | none |
| E32 | Reconciliation job and mismatch report | 6.3 | 34% | 0.60 | none |
| E33 | Initial data load and customer onboarding | 5.6 | 27% | 0.53 | none |
| E34 | Back office shell and staff roles | 4.2 | 29% | 0.63 | G2 high stakes (auth, payments, personal data, compliance or irreversible changes) |
| E35 | Manage customer companies and users | 7.7 | 31% | 0.63 | G2 high stakes (auth, payments, personal data, compliance or irreversible changes) |
| E36 | Order administration (view, edit, cancel) | 9.1 | 36% | 0.63 | none |
| E37 | Sync log viewer | 5.6 | 39% | 0.80 | none |
| E38 | Payments view | 3.5 | 41% | 0.80 | none |
| E39 | Integration test suite against the QuickBooks sandbox and Stripe test mode | 8.4 | 28% | 0.60 | none |
| E40 | Security review and hardening | 5.6 | 24% | 0.60 | G2 high stakes (auth, payments, personal data, compliance or irreversible changes) |
| E41 | Performance and load check | 2.8 | 31% | 0.67 | none |
| E42 | Responsive, cross-browser and accessibility pass | 5.6 | 32% | 0.67 | none |
| E43 | User acceptance testing support and feedback rework round | 14.0 | 31% | 0.60 | none |
| E44 | Release hardening and production cutover | 5.6 | 23% | 0.63 | G2 high stakes (auth, payments, personal data, compliance or irreversible changes) |
| E45 | Documentation and handover | 2.8 | 30% | 0.33 | none |
| E46 | Post-launch hypercare (two weeks) | 5.6 | 22% | 0.60 | none |

## Barely discounted, and what would move them up

- E3 Architecture and data model design (tenancy, roles, orders, invoices, payments, sync mapping): 16% saved. Scored 0 on: complexity, tacit_knowledge, verifiability. Agreeing field ownership per synced entity before the design session would make the model checkable against written rules.
- E2 QuickBooks Online technical spike and data audit of the distributor's company file: 21% saved. Scored 0 on: spec_clarity, tacit_knowledge. Read-only API access to a copy of the real QuickBooks company file before kickoff would turn most of the audit into scripted queries.
- E46 Post-launch hypercare (two weeks): 22% saved. Scored 0 on: spec_clarity. Production logs and alerts wired to reproducible test cases would turn more incidents into reproducible bugs.
- E5 Visual design and responsive design system: 23% saved. Scored 0 on: tacit_knowledge, verifiability. Adopting an off-the-shelf design system and theming it, instead of designing one, would move this up.
- E44 Release hardening and production cutover: 23% saved. Scored 0 on: stakes. A rehearsed cutover on staging with the same scripts and checklists would make most steps repeatable and checkable.

## Hours freed versus calendar

Engineering effort goes from 4.4 to 3.0 months for the team in the estimate. That is the most the schedule could shorten if engineering is the bottleneck. Client feedback cycles, approvals, access to accounts and environments, and release windows do not compress, so the calendar saving is smaller than the effort saving.

These are planning figures for a senior team that uses AI coding tools every day, not measured results.
