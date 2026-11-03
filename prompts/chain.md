# Chaining prompt

Paste this into Claude with the three skills installed, or into any assistant without them (the instructions stand on their own). Fill in the four bracketed lines first.

```text
Estimate what this custom software will cost to build, in three steps. Show the output of each step before starting the next. If the skills software-market-rates, software-cost-estimate and ai-savings-pass are available, use them for steps 1, 2 and 3; otherwise follow the instructions below.

MY PROJECT
What it must do: [who uses it (user roles), the main workflows, each integration and whether it has a documented API, the platforms (web, iOS, Android), compliance needs, anything already built]
Rate regions to compare: [for example United States, Latin America, Eastern Europe]
Team and timeline: [for example 2 senior engineers, a part-time designer, 1 QA engineer, a part-time project manager, 4 months]
How the team uses AI: [for example senior engineers use agentic coding tools such as Claude Code every day]

STEP 1. MARKET RATES
Research billed hourly rates from firms for each role and seniority in each region. Every number needs a named source, a link and the month you checked it; leave a cell empty rather than guess. Keep billed rates, salaries and loaded employee cost apart. Output a table (role, seniority, region, low, high, source, month) and a blended rate per region for the team above.

STEP 2. FIRST-PRINCIPLES ESTIMATE
Ignore any budget I mentioned. Restate the scope as numbered requirements. Break the work into atomic, demoable work items grouped by phase and epic, none over 15 days of engineering, including setup and CI/CD, the data model, integration testing, release hardening and a round of feedback rework. Estimate engineering days and design days per item as a senior engineer would, rounding up when unsure. Derive QA and project management at 20% each of engineering plus design. Put the risk buffer inside the risky items (integrations, AI features, compliance, undocumented systems), never as a separate line. Check capacity: days per discipline divided by the people available, against the timeline. Cost = days x 8 hours x each discipline's hourly rate, for every region, as a low-to-high range. Cross-check against people x months x 21 working days x 8 hours x rates. List the open questions that would change the number. If you can create files, also give me a spreadsheet.

STEP 3. AI SAVINGS PASS
Split each work item into its activities. Each activity saves between a floor and an aggressive figure (planning figures for a senior team that uses agentic coding tools daily, dated October 2026): setup and CI/CD 35% to 75%; CRUD and business logic 20% to 55%; UI from a design system 25% to 60%; documented-API integrations 20% to 50%; legacy or undocumented integrations 0% to 25%; data modeling and migrations 10% to 35%; AI features 10% to 35%; debugging 10% to 45%; refactoring and mechanical migrations 20% to 65%; test automation 30% to 70%; manual QA 5% to 30%; documentation 25% to 65%; code review -20% to 20%; security and compliance 5% to 30%; DevOps 10% to 35%; UI/UX design 10% to 35%; requirements and discovery 15% to 45%; domain understanding 5% to 25%; project management 10% to 30%; client communication 5% to 20%.
Score each activity 0, 1 or 2 (2 favors AI) on verifiability (weight 3), spec clarity, tacit knowledge, codebase state and complexity (weight 2 each), context size, language and API popularity, task length and stakes (weight 1 each). D = weighted sum / 30. Saving = floor + (aggressive - floor) x D. With no automatic check and high stakes, use the floor. Subtract 5 points for high-stakes work (authentication, payments, personal data, compliance or irreversible changes; 10 if the AI writes that code), 5 for an unfamiliar codebase without agent-ready docs, and 5 for a large unsliced AI change. Build work never goes below 0%; flag it as a slowdown risk when D is under 0.25. Price code review and QA on the days without AI. Add back 10% of the days saved on code-producing work as a reserve for the extra review, QA and fixes. Show each region's cost without AI and with AI, the items you barely discounted and what would move them up, and keep hours freed separate from calendar time.

Finish with the cost range, what drives it most, and the open questions I should take to a vendor.
```
