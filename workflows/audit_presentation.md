# Workflow: Audit Presentation

**Track:** 2 — Audit
**Trigger:** After opportunity matrix + ROI calculations are complete
**Input:** `[company_name]_opportunity_matrix.md` + `[company_name]_roi_summary.md`
**Output:** Slide deck + closing conversation → signed proposal

---

## Objective

Deliver the audit findings in a way that makes the client feel heard, seen, and excited — and positions your implementation proposal as the obvious next step.

---

## The 5 Slides (Non-Negotiable)

### Slide 1: Scope & Objectives
Show them what you set out to do and confirm you understood their goals.

Content:
- "What we set out to understand" — restate their stated goals in their own language
- "Who we spoke with" — list names + roles of everyone interviewed
- "What we mapped" — Acquisition / Delivery / Support engines
- "Time period covered" — dates of engagement

**Why first:** Validates you did the work. Sets credibility. Shows you listened.

---

### Slide 2: Process Map (The Ops Canvas)

Show the Excalidraw diagram of their current-state business processes.

Content:
- 3-engine flowchart (Acquisition → Delivery → Support)
- Yellow highlights on friction points (Time Sinks + Quality Risks)
- Label each friction point with the problem + estimated hours/week

**How to present:**
> "This is your business as it works today. The yellow marks are where we found friction — these are the specific spots where time is being lost and errors are being introduced."

**Why it lands:** Most clients have never seen their own business drawn out. It's immediately validating — they recognize every pain point you've circled.

---

### Slide 3: AI Opportunity Matrix

Show the 2x2 matrix with all identified solutions plotted.

Content:
- Full matrix with all solutions labeled
- Quick Wins highlighted / starred
- Brief label for each solution (not full description yet)

**How to present:**
> "We found [X] places where AI could make a significant difference. We've plotted them by how much impact they'd have vs. how much effort to implement. I want to focus your attention on this quadrant — the Quick Wins. These are high-impact, low-effort. These are where we start."

---

### Slide 4: Deep Dive — Top Quick Wins

One slide per top 1–3 Quick Wins. Each slide shows:
- **Current state diagram** (what the process looks like today — from Excalidraw)
- **Future state diagram** (what it looks like with AI)
- Key metrics: hours saved/week, people affected, error reduction
- What the AI actually does (in plain language, not jargon)

**Template per slide:**
```
SOLUTION: [Name]
TODAY: [2–3 step current process with pain circled]
WITH AI: [2–3 step future process, manual steps removed]
IMPACT: Saves [X hours/week] for [Y people] = [annual $]
HOW: [Plain language — "AI reads each email, classifies it, and drafts a response. Human reviews in 2 minutes instead of 20."]
```

---

### Slide 5: ROI Summary — The Money Slide

The table from `[company_name]_roi_summary.md`.

Content:
- One row per recommended solution
- Columns: Solution | Annual Savings | Implementation Cost | ROI% | Payback Period
- TOTAL row at bottom (always more impressive than individual numbers)

**How to present:**
> "Here's what this looks like in terms of numbers. These are conservative estimates based on what you told us about your team size, salaries, and time spent. At [X] total investment, you're looking at [Y] in annual savings — that pays for itself in [Z months]."

**Then pause. Let it land. Don't rush past the numbers.**

---

## How to Run the Presentation Meeting

### Setup (5 min before)
- [ ] Test screen share
- [ ] Have `[company_name]_audit_package.md` open for reference
- [ ] Have ROI summary open to fill in any missing numbers
- [ ] Have proposal draft ready to send immediately after

### During Presentation (30–40 min)

**Open:**
> "I want to spend 30 minutes walking you through what we found. I'll show you your business from the outside in — and then show you where the opportunity is. At the end, I want to propose exactly what I'd recommend we do first."

**After Slide 2 (Process Map) — pause and ask:**
> "Does this resonate with how things actually work? Is there anything here that looks wrong or that we missed?"

**After Slide 4 (Deep Dives) — check temperature:**
> "Of these three Quick Wins, which one feels most urgent for your team right now?"

**After Slide 5 (Money Slide) — close:**
> "Based on everything we've found, here's what I'd like to propose for Phase 1."

---

### The Close (10 min)

**Present Phase 1 scope:**
> "I'd like to start with [Quick Win 1] and [Quick Win 2]. Here's what that engagement looks like: [brief scope — timeline, deliverables, price]."

**Handle the silence:**
After you name the price, stop talking. Let them respond.

**Typical next steps:**
- Interested → "Let me send you a proposal today and we can schedule a kick-off for next week."
- Need to think → "Completely understand. What's your timeline for making a decision? I'll follow up [day]."
- Need approval → "Who else needs to be in the loop? Can we schedule a 20-min call with them this week?"
- Not ready → "Makes sense. Would it help if I sent the deck to share internally?"

---

## Sending the Follow-Up Proposal (within 2 hours)

Email subject: "[Company Name] — AI Implementation Proposal"

Body:
> "Hi [Name], great presentation today. As discussed, here's the proposal for Phase 1. It covers [Quick Win 1] and [Quick Win 2] — the two highest-impact opportunities we identified. Happy to jump on a quick call to walk through any questions. [Name]"

Attach: proposal PDF (from `proposal_generator.py` — Track 3)

---

## Applied Learning

<!-- Add notes: what landed, what confused people, how to handle specific objections in the close -->
