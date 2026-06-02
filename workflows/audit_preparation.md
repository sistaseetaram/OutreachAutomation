# Workflow: Audit Preparation

**Track:** 2 — Audit
**Trigger:** After company_research.md runs AND call is booked within 48 hours
**Output:** `.tmp/[company_name]_audit_package.md` — complete pre-call audit package
**Tool:** `tools/interview_template_generator.py`

---

## Objective

Generate a complete pre-call package: company summary, customized interview questions, initial AI opportunity hypotheses, and a call agenda. Walk into every audit call prepared, specific, and confident.

## Required Inputs

- `[company_name]_profile.md` (from company_research workflow)
- Contact name + role
- Scheduled call date/time
- Known context (how they replied, what they said, what they seem interested in)

## Steps

### 1. Run the Template Generator
```bash
python tools/interview_template_generator.py --profile ".tmp/[company_name]_profile.md" --contact "Name, Role"
```

### 2. What Gets Generated

The tool outputs `.tmp/[company_name]_audit_package.md` containing:

---

**Section 1: Pre-Call Brief (read before the call)**
- Company: what they do, who they serve, their stage
- Contact: who you're talking to, their role, their likely perspective
- Why they're likely interested: based on pain signals found in research
- Key hypotheses: top 3 AI opportunity areas you expect to find
- Risks: anything unusual or sensitive to navigate

---

**Section 2: Customized Stakeholder Questions**
Not generic — tailored to their industry, company size, and known pain signals.

Format: [category] → [specific question] → [what to listen for]

Example for a 50-person SaaS company:
- "I noticed you're hiring 3 Account Executives — what's currently happening between a trial sign-up and the first sales call?" → Listen for: manual qualification, delayed follow-up, inconsistent process
- "Your Glassdoor reviews mention the onboarding process — can you walk me through how a new customer gets started?" → Listen for: human bottlenecks, repeatable steps

Standard categories always covered:
1. Role & team overview
2. Core processes (acquisition, delivery, support)
3. Tools & tech stack pain
4. Biggest frustrations
5. Future vision / what success looks like

---

**Section 3: End-User Questions (if interviewing employees)**
Tailored to their role types. If they're a SaaS company:
- Customer success team: "Walk me through what happens after a customer submits a support ticket"
- Sales team: "How do you currently research a prospect before reaching out?"
- Operations: "What does a typical Tuesday look like for you?"

---

**Section 4: Initial Opportunity Hypotheses**
Based on company profile, list top 3 most likely AI opportunities:
1. [Opportunity] — Evidence: [specific signals from research] — Likely impact: [High/Med] — Likely effort: [High/Med/Low]
2. [Same format]
3. [Same format]

These are hypotheses to test during the call, not conclusions.

---

**Section 5: Call Agenda**
```
[00:00–05:00] — Intro + set expectations for the call
[05:00–20:00] — Discovery: walk me through your business (stakeholder questions)
[20:00–35:00] — Deep dive: specific pain area (based on best hypothesis)
[35:00–45:00] — Next steps: propose the audit engagement
[45:00–50:00] — Q&A + close
```

---

**Section 6: What to Offer**
Based on company size + complexity:
- Small (10–50 employees): $10K audit, 2-week process, 3–5 interviews
- Medium (50–200 employees): $20K–$30K audit, 4-week process, 10–15 interviews
- Large (200+ employees): escalate to $60K model, 8-week, 20–30 interviews

Lead with the audit, not implementation. The audit IS the first product.

---

### 3. Review the Package

Human review before the call (10 min):
- [ ] Questions feel specific to THIS company, not generic
- [ ] Hypotheses are grounded in actual research signals
- [ ] Call agenda fits the scheduled duration
- [ ] Offer is calibrated to company size
- [ ] Red flags noted

### 4. Prepare Materials

Print or keep on screen during call:
- [ ] Company profile summary (Section 1)
- [ ] Customized questions list (Sections 2–3)
- [ ] Notepad for capturing pain points verbatim

## Quality Rule

If the generated questions could apply to ANY company without changing a word, the personalization failed. Regenerate with more specific company context.

## Applied Learning

<!-- Add lessons learned about what questions work best for which industries -->
