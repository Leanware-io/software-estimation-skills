# Software estimation skills for Claude

Three free Claude skills that estimate what custom software costs to build, the way a senior engineer prices a proposal:

| Skill | What it does | You give it | You get |
|---|---|---|---|
| [`software-market-rates`](plugins/software-market-rates/skills/software-market-rates/SKILL.md) | Researches developer rates by role, seniority and country, with a source and a month on every number | Roles, seniority, countries or regions, firm / freelancer / employee, the team mix | A rate table (Markdown and CSV) and a blended hourly rate per region |
| [`software-cost-estimate`](plugins/software-cost-estimate/skills/software-cost-estimate/SKILL.md) | Builds a first-principles, bottom-up estimate: work items, days per discipline, capacity check, cost per region | A requirements document or a plain description, platforms, integrations, compliance needs, rates | A formula-driven Excel workbook, the roll-up by epic, the cost range per region and the open questions |
| [`ai-savings-pass`](plugins/ai-savings-pass/skills/ai-savings-pass/SKILL.md) | Splits each work item into activities and applies a dated, per-activity AI savings table | The estimate from the second skill and how your team uses AI | The same estimate without AI and with AI, the caps that fired, and the items AI barely helps |

Software development cost is the effort the work needs, counted in days per discipline (engineering, design, QA, delivery management), multiplied by the rates of the people doing it. The skills run that formula on your project. Claude runs the method; it does not supply the judgment, and it does not know what you have not written down. The open-questions list is the part to take to a vendor.

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

## How the AI savings are decided

AI saves the most where a machine can check the output (tests, a compiler, a validator) and the least where a person must judge it or a client must agree to it. So the saving is set per activity, not per project: each activity has an aggressive figure and a floor, and nine attributes of the work item (verifiability counts the most) place it between them. Code review and QA are priced on the hours without AI, and 10% of the hours saved on code is added back for the review, QA and fixes AI output creates downstream.

The figures are planning figures for a senior team that uses agentic coding tools every day, dated October 2026 and due for a re-check by April 2027. They are not measured results; typical teams in the published studies save less. The full table lives in [`savings-2026-10.json`](plugins/ai-savings-pass/skills/ai-savings-pass/data/savings-2026-10.json), the scoring guide in [`attributes.md`](plugins/ai-savings-pass/skills/ai-savings-pass/references/attributes.md).

## Worked example

[`examples/customer-portal/`](examples/customer-portal/) holds a full run on a fictional B2B distributor customer portal (logins and roles, order history and one-click reorder, card payments through Stripe, a two-way QuickBooks Online sync, an admin back office, responsive web): the rates table, the estimate workbook and the AI savings workbook.

## From a ballpark to a committed number

These skills give you a careful ballpark. To turn it into a number someone commits to, the requirements need to be written down, the risky items identified, and the person estimating needs to be accountable for delivering it. Leanware, which publishes these skills, does that in [Sprint 0](https://leanware.co/services/sprint-0): a fixed-fee discovery phase that ends with a milestone plan where every milestone is defined and priced. More on how Leanware builds custom software: [Software Product Development](https://leanware.co/services/software-product-development#claude-skills) and [Dedicated Software Development Teams](https://leanware.co/services/dedicated-development-team#claude-skills).

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
