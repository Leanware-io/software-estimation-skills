# Scoring the nine attributes

Score each activity row 0, 1 or 2. Two favors AI; zero blocks it. The weights are inferred priors, not fitted values: verifiability carries triple weight because every source names it, and the five attributes most often cited as reasons for slowdown carry double weight.

| Attribute | Weight | 2 (favors AI) | 1 | 0 (blocks AI) |
|---|---|---|---|---|
| Verifiability | 3 | An automated pass/fail check exists (tests, compiler, type checker, `terraform plan`, screenshot against the mockup) and checking costs far less than creating | A partial check; behavior still needs human review | Correctness is a human judgment (taste, intent, UX, architecture, client agreement) |
| Specification clarity | 2 | Written acceptance criteria, a design or an API contract; "done" is defined | Mostly defined, open questions remain | Requirements emerge during the work |
| Tacit knowledge | 2 | Everything needed is in the repo, the docs or the prompt | Some unwritten conventions one person can write down in under an hour | Depends on rules, history or processes that live in people's heads |
| Codebase state and familiarity | 2 | Greenfield, or a small, loosely coupled module | Documented brownfield with tests | Large, mature, tightly coupled brownfield, or the engineer already maintains this exact code quickly |
| Complexity and novelty | 2 | Boilerplate, CRUD, standard patterns, docs, tests of clear behavior | Known patterns combined, moderate logic | Novel algorithms, concurrency, performance tuning, cross-cutting design |
| Context size | 1 | A few files; fits easily in one session | Tens of files or several services | Many repos or services, or very large schemas |
| Language and API popularity | 1 | Mainstream language, framework and high-frequency APIs (TypeScript, Python, Java, React, Postgres, Stripe) | A less common framework or documented internal libraries | A niche or legacy language, a proprietary DSL, a low-frequency or undocumented API |
| Task length vs model reliability | 1 | Splits into verifiable steps, each within the H80 horizon in the data file (about 4 hours of human work in October 2026) | Steps up to the 50% horizon | Cannot be cut into checkable steps |
| Stakes and reversibility | 1, plus gates | Internal, throwaway or trivially reverted | Production, reversible behind flags or rollback | Authentication, payments, personal data, compliance, irreversible data or infrastructure operations |

## Calibration notes

- **Seniority.** The aggressive figures assume a senior team. Never raise an item's saving because a junior staffs it unless senior review hours are added too: juniors gain more output per hour with AI, but they also accept more insecure code and catch fewer of its errors.
- **Outside teams.** A team entering a client codebase is in the position of an outside contractor: AI helps most with reading the code, and the risk is accepting output that breaks unwritten conventions. Score a documented client codebase 1 on codebase state and let tacit knowledge carry the risk.
- **Worked examples from the research.** A three-day invoice list and CRUD API with role-based filtering, in an existing Next.js and Postgres app with written acceptance criteria and a test suite: 2 on verifiability, spec, complexity, context, popularity and length; 1 on tacit knowledge and codebase; 0 on stakes (it touches authorization). D = 24/30 = 0.80. A five-day order sync into a client's on-premise ERP over an undocumented SOAP interface with no test instance: 0 on verifiability, tacit knowledge, codebase, popularity, length and stakes; 1 elsewhere. D = 5/30 = 0.17, G1 holds it at the floor, and it is flagged as a slowdown risk.
