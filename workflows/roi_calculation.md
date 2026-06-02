# Workflow: ROI Calculation

**Track:** 2 — Audit
**Trigger:** After opportunity matrix is finalized and validated with client
**Input:** `[company_name]_opportunity_matrix.md` + data collected during interviews
**Output:** `[company_name]_roi_summary.md` — The Money Slide data
**Tool:** `tools/roi_calculator.py`

---

## Objective

Build the financial case for every Quick Win and key Big Swing. Translate "hours saved" and "errors reduced" into dollars. This becomes the Money Slide in the audit presentation — the single most powerful slide for getting buy-in.

---

## Data to Collect During Interviews

You must ask these questions during discovery calls (or follow up after):

**For Time-Based Savings:**
- How many people perform this task?
- How often (daily / weekly / monthly)?
- How long does it take each time?
- What's the approximate annual salary of the people doing this? (or just use industry average)

**For Error / Quality Savings:**
- How often does [error/quality issue] occur?
- What does it cost when it happens? (rework hours, client churn, refunds)
- Who cleans it up, and how long does that take?

**For Revenue Uplift:**
- How much of your team's time could shift to revenue-generating activities if [task] was automated?
- What's the value of those activities? (e.g., if 1 extra sales meeting/week = $X pipeline)

---

## Step 1: Run the Calculator Tool

```bash
python tools/roi_calculator.py --matrix ".tmp/[company_name]_opportunity_matrix.md"
```

The tool prompts for missing data interactively, then outputs calculations.

---

## Step 2: Cost Savings Formula (Per Solution)

```
HOURS SAVED PER WEEK:
= (Time on task per occurrence) × (Frequency per week) × (Number of staff)
× (% of time AI saves — typically 70–90%)

ANNUAL COST SAVINGS:
= (Hours saved per week) × (Avg hourly rate) × 52

AVERAGE HOURLY RATE:
= Annual salary / 2,080 working hours

SIMPLE ROI:
= (Annual savings / Implementation cost) × 100%
```

**Example:**
- 3 staff spend 2h/day on data entry
- Average salary: $50K → $24/hr
- AI saves 80% of that time
- Hours saved/week = (2h × 5 days × 3 staff) × 80% = 24 hrs/week
- Annual savings = 24 × $24 × 52 = **$29,952/year**
- Implementation cost: $8,000
- ROI = $29,952 / $8,000 = **374%**

---

## Step 3: Revenue Uplift Formula (Optional but powerful)

```
REVENUE-GENERATING HOURS UNLOCKED:
= Total hours saved per week × 50%
(conservative estimate: only half of saved time converts to productive revenue work)

ADDITIONAL REVENUE POTENTIAL:
= Unlocked hours × Value per hour for revenue activities
(e.g., if 1 sales call/hour = $2,500 pipeline, use $2,500)

ANNUAL UPLIFT POTENTIAL:
= Additional weekly revenue × 52
```

**Example:**
- 24 hrs/week saved → 12 hrs/week available for sales
- Sales rep closes 1 deal per 10 hours of prospecting at $15K avg deal
- Value per hour = $1,500
- Annual uplift = 12 hrs × $1,500 × 52 = **$936,000 pipeline potential**

Note: Present uplift as "potential" — don't guarantee it.

---

## Step 4: Build the Summary Table (Money Slide)

```
| AI Solution | Annual Cost Savings | Impl. Cost | Annual ROI | Payback Period |
|---|---|---|---|---|
| [Solution 1] | $X | $Y | Z% | N months |
| [Solution 2] | $X | $Y | Z% | N months |
| TOTAL | $X | $Y | Z% | N months |
```

**Format tips:**
- Round to nearest $1K — false precision loses trust
- Show total at bottom — aggregate is always more impressive
- Payback period = Implementation cost / (Annual savings / 12)

---

## Step 5: Conservative vs. Optimistic Range

Show two scenarios:
- **Conservative (use in presentation)**: 60–70% of estimated savings
- **Optimistic (reference internally)**: full calculation

This protects your credibility. Under-promise, over-deliver.

---

## Benchmark Sanity Check

If your numbers seem too high or low, compare:
- $10K audit → should show at minimum $50K annual savings (5x ROI minimum to justify price)
- $20K audit → should show $100K+ annual savings
- $60K audit → should show $300K+ annual savings

If the math doesn't work at 5x, either: the opportunity is smaller than expected (reprice the audit), or you missed bigger opportunities (dig deeper).

---

## Output Format

`[company_name]_roi_summary.md`:
```
## ROI Summary — [Company Name]

Implementation: [Total cost] for [scope]
Annual savings: [Conservative estimate]
Annual ROI: [%]
Payback period: [X months]

### Per Solution Breakdown
[Table from Step 4]

### Revenue Uplift Potential (additional)
[If calculated]

### Data Sources
[What data came from interviews vs. industry estimates]
```

---

## Applied Learning

<!-- Add notes on which industries have higher/lower hourly rates, common estimation mistakes -->
