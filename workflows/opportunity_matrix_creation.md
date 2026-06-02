# Workflow: Opportunity Matrix Creation

**Track:** 2 — Audit
**Trigger:** After discovery interviews are complete
**Input:** `[company_name]_interview_notes.md` + any follow-up interview notes
**Output:** `[company_name]_opportunity_matrix.md` + Excalidraw diagram

---

## Objective

Turn raw interview notes into a visual AI Opportunity Matrix. Identify every potential AI solution, score each by impact and effort, and surface the Quick Wins that will form the core of your audit presentation.

---

## Step 1: Extract All Friction Points

From your interview notes, list every pain point, bottleneck, or manual process mentioned. Be exhaustive — include small ones.

**Format:**
```
FRICTION POINT: [Name]
Source: [Who mentioned it / which engine it's in]
Current state: [What happens today]
Type: ⏱️ Time Sink / ⚠️ Quality Risk / 💸 Cost Sink / 🔄 Repeat Error
People affected: [How many, which roles]
Frequency: [How often / volume]
```

Target: 10–20 friction points from a typical audit.

---

## Step 2: Map to Ops Canvas Engines

Categorize each friction point:
- **Acquisition Engine** — finding clients, marketing, sales, proposals
- **Delivery Engine** — doing the work, fulfillment, project management
- **Support Engine** — client success, support tickets, renewals, billing

---

## Step 3: Generate AI Solutions

For each friction point, brainstorm 1–2 potential AI solutions:

| Friction Point | Engine | Potential AI Solution |
|---|---|---|
| Manual CRM data entry after calls | Acquisition | AI auto-transcribes + updates CRM from call recordings |
| Email triage taking 2h/day | Support | AI classifies + drafts responses; human reviews |
| Weekly report compilation takes 4h | Delivery | AI pulls data from tools + generates report |

---

## Step 4: Score Each Solution

Score on two dimensions (1–5 scale):

**Business Impact (X-axis):**
- 5: Directly generates revenue or saves >$50K/year
- 4: Saves >$20K/year or unblocks key bottleneck
- 3: Saves $5–20K/year or meaningfully improves quality
- 2: Minor time saving, limited scope
- 1: Nice to have, minimal measurable impact

**Implementation Effort (Y-axis):**
- 5: 3+ months, custom dev, complex integrations
- 4: 4–8 weeks, moderate complexity
- 3: 2–4 weeks, standard integrations
- 2: 1–2 weeks, simple automation
- 1: Days, off-the-shelf solution

---

## Step 5: Place on Matrix

Plot each solution:

```
HIGH IMPACT
    |  BIG SWINGS    |  QUICK WINS ⭐
    |  (plan later)  |  (build first)
    |________________|________________
    |  DEPRIORITIZE  |  NICE-TO-HAVE
    |  (avoid)       |  (add-ons only)
LOW IMPACT
         HIGH EFFORT    LOW EFFORT
```

**Quick Wins** = Impact ≥ 3, Effort ≤ 2 → BUILD THESE FIRST
**Big Swings** = Impact ≥ 4, Effort ≥ 3 → Phase 2 roadmap
**Nice-to-Have** = Impact ≤ 2, Effort ≤ 2 → Optional add-ons
**Deprioritize** = Impact ≤ 2, Effort ≥ 3 → Actively avoid

---

## Step 6: Validate with Client

Before finalizing, share preliminary matrix in a 30-min validation session:

**Questions to ask:**
- "Looking at these Quick Wins — which resonates most with what your team described?"
- "Is there anything on here that looks simpler or harder than I've scored it?"
- "Does this fit with your priorities for the next 6–12 months?"
- "Which of these would your team be most excited about? Which might they resist?"

**Goal:** Co-create the final prioritized list. By the end, they should feel like the roadmap is theirs, not yours.

---

## Step 7: Create the Excalidraw Process Map

Use `tools/excalidraw_generator.py` to generate the visual diagram.

The process map shows the 3 engines with their current-state steps and friction tags. This is a key audit deliverable — clients often say they've never seen their own business drawn out before.

```bash
python tools/excalidraw_generator.py --notes ".tmp/[company_name]_interview_notes.md"
```

Output: `.tmp/[company_name]_process_map.excalidraw`

Import into Excalidraw.com to render and share.

---

## Step 8: Output the Matrix Document

Write `[company_name]_opportunity_matrix.md`:

```
## AI Opportunity Matrix — [Company Name]

### Quick Wins (build first)
| Solution | Current Pain | Impact | Effort | Est. Annual Value |
|---|---|---|---|---|
| [Name] | [Specific pain] | 4/5 | 1/5 | $[X]K |

### Big Swings (Phase 2 roadmap)
| Solution | Current Pain | Impact | Effort | Est. Annual Value |
|---|---|---|---|---|

### Deprioritized
| Solution | Why |
|---|---|
```

---

## Applied Learning

<!-- Add lessons on scoring calibration, client reactions to different matrix presentations -->
