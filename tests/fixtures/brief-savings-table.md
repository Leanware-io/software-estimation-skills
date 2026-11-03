| Activity | Aggressive saving (applied) | Floor (item hard to hand to AI) | What AI does not save |
|---|---|---|---|
| Project setup, scaffolding and CI/CD bootstrap | 75% | 35% | Stack and repo-layout decisions, house conventions, cloud accounts and secrets, approving the production pipeline |
| CRUD screens and standard business logic | 55% | 20% | Settling ambiguous business rules and edge cases, permission and data-integrity decisions, client acceptance |
| UI built from an existing design system | 60% | 25% | Visual QA across browsers and screen sizes, accessibility review, interaction polish, fidelity to design intent |
| Integrations with documented APIs | 50% | 20% | Sandbox and credential access, auth flows, webhook ordering and idempotency, vendor quirks, reconciliation edge cases |
| Integrations with legacy or undocumented systems | 25% | 0% | Discovering undocumented behavior, test-environment access, knowledge held by client staff, side effects on systems of record |
| Data modeling and database migrations | 35% | 10% | Normalization, tenancy and ownership decisions, backfill and rollback strategy, live-data safety |
| AI features (retrieval, prompts, evaluations, guardrails) | 35% | 10% | Defining success criteria, reading real outputs, labeling, re-running evaluations on every model or prompt change, safety sign-off |
| Debugging and bug fixing | 45% | 10% | Reproducing the bug, production access and logs, root-cause judgment across systems, proving no regression |
| Refactoring and large mechanical migrations | 65% | 20% | Choosing the target design, building the validation harness, the long tail of edge cases, rollout and equivalence sign-off |
| Automated test generation and test automation | 70% | 30% | Deciding which behavior matters and what correct looks like, flaky-test triage, test data and environments, owning the suite |
| Manual and exploratory QA | 30% | 5% | Noticing what feels wrong, usability, unspecified behavior, go or no-go decisions, checking AI-written test cases are real |
| Code documentation and technical writing | 65% | 25% | Deciding what to document and for whom, rationale that is not in the code, factual accuracy, editorial review |
| Code review | 20% | -20% (can take longer) | Judging design fit and whether the change should exist, business context, approval accountability; AI produces more and larger changes to review |
| Security and compliance | 30% | 5% | Risk judgment, proving a patch keeps behavior intact, attack chains in business logic, security review of AI-written code, attestation |
| DevOps and infrastructure | 35% | 10% | Network and permission design, production change approval and rollback, environment failures outside the model's view |
| UI/UX design | 35% | 10% | Research with real users, design judgment, production visual polish, design review |
| Requirements and discovery | 45% | 15% | Getting the truth from real stakeholders, prioritization trade-offs, sign-off |
| Business domain understanding | 25% | 5% | Unwritten rules, exceptions and politics, why a process exists, who actually decides |
| Delivery and project management | 30% | 10% | Coordination and unblocking, sequencing and escalation decisions, risk judgment |
| Client communication and stakeholder management | 20% | 5% | Live conversations, scope and price negotiation, expectation-setting, trust |
