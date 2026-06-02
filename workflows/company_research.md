# Workflow: Company Research

**Track:** 2 — Audit
**Trigger:** Prospect replies to outreach OR user says "research [company name]"
**Output:** `.tmp/[company_name]_profile.md` — structured company profile
**Tool:** `tools/company_researcher.py`

---

## Objective

Before any client call, generate a comprehensive company profile so you enter the conversation knowing more about their business than they expect. This builds instant credibility and lets you ask specific, intelligent questions instead of generic ones.

## Required Inputs

- Company name
- Company website URL (if known)
- Contact name + LinkedIn URL (if known)
- Industry (if not obvious)

## Steps

### 1. Run the Research Tool
```bash
python tools/company_researcher.py --company "Company Name" --url "https://company.com" --contact "First Last"
```

### 2. The Tool Pulls (in order of reliability)

**Company basics:**
- Official website: about page, services/products, team page
- LinkedIn company page: size, industry, recent posts, hiring activity
- Crunchbase: funding rounds, investors, founded year, revenue range
- Google News: last 6 months of news (funding, launches, hires, expansions)

**People:**
- Founder/CEO name, background, LinkedIn
- Key decision-makers (CTO, COO, VP Ops — whoever you'll talk to)
- Approximate team size per department

**Pain signals:**
- Job postings: what roles are they hiring? (signals bottlenecks)
- Glassdoor reviews: what do employees complain about?
- LinkedIn posts by leadership: what problems are they talking about?
- Recent news: any operational challenges mentioned?

**Tech stack:**
- BuiltWith or Wappalyzer for website tech
- Job posting requirements (reveal internal tools)
- LinkedIn tech stack if listed

### 3. Output Structure

The tool writes a structured profile to `.tmp/[company_name]_profile.md`:

```
## Company: [Name]
Founded: [Year] | Size: [Range] | Industry: [Vertical]
Website: [URL] | LinkedIn: [URL]

## Key People
- CEO/Founder: [Name], [brief background]
- Decision-maker (your contact): [Name], [role], [LinkedIn]
- Other relevant: [Name, role]

## Business Model
[1–2 sentences: what they do, who they serve, how they make money]

## Current State (from research)
- Revenue stage: [pre-revenue / $XM ARR / growth / enterprise]
- Recent news: [bullet points of last 3–6 months]
- Hiring signals: [what roles, implies what bottlenecks]
- Tech stack: [key tools identified]

## Likely Pain Points (hypothesis)
1. [Most likely pain based on company size + industry + signals]
2. [Second likely pain]
3. [Third likely pain]

## Red Flags / Watch For
- [Anything unusual or worth probing]

## Research Confidence
- [High / Medium / Low — based on data available]
- [Gaps: what you couldn't find]
```

## Time Budget

- Automated research: 5–10 minutes
- Human review of output: 5 minutes
- Total before call: 15 minutes max

## Quality Check

Before using the profile, verify:
- [ ] Decision-maker name and role confirmed (not guessed)
- [ ] At least 1 specific pain signal found (not just general assumption)
- [ ] Business model understood clearly
- [ ] No fabricated or unverifiable claims in profile

## Error Handling

If tool fails to find data:
1. Try manual search: LinkedIn + company website + "site:news.ycombinator.com [company]"
2. Reduce scope — even name + role + company size is enough to start
3. Note gaps in profile — ask these questions during the call

## Applied Learning

<!-- Add lessons learned here as research quality improves -->
