# Software estimation skills for Claude

These three free Claude skills help you estimate the cost of custom software. The follow a senior engineer's estimating process: research the rates, break down the work and assess where AI could save time.

| Skill | What it does | You give it | You get |
|---|---|---|---|
| [`software-market-rates`](plugins/software-market-rates/skills/software-market-rates/SKILL.md) | Researches developer rates by role, seniority and country, with a source and a month on every number | Roles, seniority, countries or regions, firm / freelancer / employee, the team mix | A rate table (Markdown and CSV) and a blended hourly rate per region |
| [`software-cost-estimate`](plugins/software-cost-estimate/skills/software-cost-estimate/SKILL.md) | Builds a first-principles, bottom-up estimate: work items, days per discipline, capacity check, cost per region | A requirements document or a plain description, platforms, integrations, compliance needs, rates | A formula-driven Excel workbook, the roll-up by epic, the cost range per region and the open questions |
| [`ai-savings-pass`](plugins/ai-savings-pass/skills/ai-savings-pass/SKILL.md) | Splits each work item into activities and applies a dated, per-activity AI savings table | The estimate from the second skill and how your team uses AI | The same estimate without AI and with AI, the limits applied to the savings, and the items AI barely helps |

To estimate software development cost, count the days needed for engineering, design, QA and delivery management. Then, multiply each discipline's effort by its rate. The skills apply this calculation to your project. You still need to define the work and check the assumptions. Take the open questions to a vendor to clarify anything that could change the estimate.

For the method behind the skills, savings table, rate sources and a step-by-step worked example, see [Software Development Cost: Estimate It With Claude or ChatGPT](https://leanware.co/insights/software-development-cost).

## Install

**Claude Code**

```text
/plugin marketplace add Leanware-io/software-estimation-skills
/plugin install software-market-rates@software-estimation-skills
/plugin install software-cost-estimate@software-estimation-skills
/plugin install ai-savings-pass@software-estimation-skills
```

**Claude.ai and the Claude desktop app**: download the three zips from the [latest release](https://github.com/Leanware-io/software-estimation-skills/releases/latest), then upload each one in Settings > Capabilities > Skills. Code execution and file creation must be on, because the skills build spreadsheets.

**ChatGPT**: see OpenAI's help article on [skills in ChatGPT](https://help.openai.com/en/articles/20001066-skills-in-chatgpt), or skip installing and paste the chaining prompt below.

## Run all three in one go

Paste [the chaining prompt](prompts/chain.md) into Claude, fill in the four bracketed lines about your project, and it runs the three steps in order. The prompt also works pasted into an assistant with no skills installed, because it carries the method and the savings table itself.

## How AI savings are decided

AI saves the most in time and cost when a machine can check the output (tests, a compiler, a validator) and the least when the work needs human judgment or client approval. The skill assesses each activity separately. It starts with an aggressive savings figure and lowers it toward a minimum, or floor, based on nine sttributes of the work item. Whether the output can be checked automatically carries the most weight. Code review and QA keep their original hours, and the skill adds back 10% of the hours saved on code to cover additional review, QA and fixes.

The figures are planning figures for a senior team that uses agentic coding tools every day, dated October 2026 and due for a re-check by April 2027. They are not measured results; typical teams in the published studies save less. See [`savings-2026-10.json`](plugins/ai-savings-pass/skills/ai-savings-pass/data/savings-2026-10.json), the scoring guide in [`attributes.md`](plugins/ai-savings-pass/skills/ai-savings-pass/references/attributes.md).

## Worked example

[`examples/customer-portal/`](examples/customer-portal/) holds a full run on a fictional B2B distributor customer portal (logins and roles, order history and one-click reorder, card payments through Stripe, a two-way QuickBooks Online sync, an admin back office, responsive web): the rates table, the estimate workbook and the AI savings workbook.

The estimate came to 46 work items and 319 days of effort across engineering, design, QA and delivery management. The two-way QuickBooks Online sync was the largest epic at 77 days. With the AI savings pass, effort fell to 226 days (29% fewer):

| Rate region (firms, billed hourly) | Without AI | With the AI savings pass |
|---|---|---|
| United States | $324,000 to $473,000 | $231,000 to $337,000 |
| Latin America | $132,000 to $177,000 | $92,000 to $125,000 |
| Eastern Europe | $121,000 to $217,000 | $85,000 to $155,000 |

Every rate in the run has a source and the month it was checked ([rates.md](examples/customer-portal/rates.md)). The product is fictional; your scope will move the number more than anything else.

## From a ballpark to a committed number

These skills give you a careful ballpark to discuss with a vendor. To turn it into a number someone commits to, the requirements need to be written down, the risky items identified, and the person estimating needs to be accountable for delivering it. Leanware publishes these skills and offers [Sprint 0](https://leanware.co/services/sprint-0) a fixed-fee discovery phase that produces a milestone plan with every milestone defined and priced. For more on how Leanware builds custom software see, [Software Product Development](https://leanware.co/services/software-product-development#claude-skills) and [Dedicated Software Development Teams](https://leanware.co/services/dedicated-development-team#claude-skills).

## Repository layout

```text
.claude-plugin/marketplace.json     the Claude Code marketplace (three plugins, one skill each)
plugins/<name>/.claude-plugin/      plugin manifests
plugins/<name>/skills/<name>/       SKILL.md, scripts, data and references
prompts/chain.md                    the chaining prompt
examples/customer-portal/           the worked example
scripts/build-zips.sh               builds the Claude.ai zips into dist/
tests/check_table.py                checks the savings data against the published table
```

The scripts need Python 3 and `openpyxl`. To recalculate and check the workbooks locally, install `formulas` (`pip install formulas`) or LibreOffice; without either, Excel and Google Sheets compute the formulas when the file opens.

## License

MIT. See [LICENSE](LICENSE).
