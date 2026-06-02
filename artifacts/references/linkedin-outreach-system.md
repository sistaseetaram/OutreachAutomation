# LinkedIn AI Outreach System

Source: "Claude Code Turned My LinkedIn Into a Lead Gen Machine" (YouTube, March 2026)

---

## Performance Benchmarks

| Approach | Connection Acceptance | Reply Rate | Meeting Rate |
|---|---|---|---|
| Generic messaging | 5–10% | 2–5% | 0.5–1% |
| AI-personalized (Claude) | 35–50% | 15–25% | 5–10% |

Example weekly volume: 100 prospects → 42 connections → 19 replies → 5 meetings

---

## The 4-Step System

### Step 1: Research & Qualification
- Pull data from public sources (LinkedIn, company site, news, job boards)
- Cross-reference multiple sources
- Identify genuine connection points vs. surface-level hooks
- Filter for ICP fit before personalizing

### Step 2: Personalized Message Generation
**Connection Request (300-char limit):**
- Reference ONE specific real discovery
- Zero sales language
- Match their communication tone (formal vs. casual, technical vs. business)

**Follow-up DMs:**
- Under 500 characters
- Conversation-starters
- Offer value or ask a soft question
- No pitch until 3–4 touches minimum

### Step 3: Delivery & Safety
- Non-uniform timing (appears organic)
- Message queue with status tracking
- Weekend pauses
- CRM sync + sales routing

### Step 4: Compliance
Daily LinkedIn limits (CRITICAL — exceeding = account restriction):
- Connection requests: **20–25/day max**
- Messages: **50–75/day max**
- Profile views: **100–150/day max**
- Randomize send timing
- Vary message length and content
- Pre-connection engagement (likes/comments) before requesting

---

## Role-Based Sequence

| Prospect Role | Day 0 | Day 3 | Day 7 | Day 14 |
|---|---|---|---|---|
| Decision-Maker | Connection + note | First follow-up | Value content share | Soft meeting ask |
| Individual Contributor | Connection + note | Peer-tone follow-up | Resource share | Intro request |

3:1 value-to-ask ratio. Delay pitch until relationship established.

---

## Buying Signal Detection

Monitor for signals that indicate high intent — reply rates 5–7x higher:

| Signal Type | What to Watch For |
|---|---|
| Competitor engagement | Prospect liked/commented on competitor content |
| Pain point posts | Prospect complained about a problem you solve |
| Job postings | Hiring for role that signals operational bottleneck |
| Funding news | Series A/B — growth means new problems |
| Content resonance | Prospect engaging with specific topic area |
| Leadership changes | New CTO/COO = new initiatives = new budget |

---

## Personalization Quality Rules

**Strong (implement):**
- Reference prospect's recent post by topic
- Comment on their activity history
- Mention company milestone relevant to your solution
- Use their actual phrasing/terminology

**Weak (avoid):**
- "I see you're passionate about sales — me too!"
- Generic reference to job title only
- Forced false connections ("we both care about innovation")

**The rule:** If authentic hooks don't exist, honest generic > fabricated connection.
Never reference information you don't have or can't verify.

---

## CRM Integration Flow

```
Connection accepted → auto-create contact in CRM
Reply received → sentiment analysis → route to correct pipeline stage
Positive reply → Slack alert to sales team with context summary
Meeting booked → trigger onboarding research workflow
```

---

## Tool Stack for LinkedIn Automation

- **Playwright** (self-hosted): profile views, likes, comments, pre-engagement
- **Expandi** (cloud, preferred for safety): connection requests + DMs at scale
- **Apollo/Hunter**: email enrichment from LinkedIn profiles
- **n8n**: orchestration + scheduling + CRM sync
- **Claude**: research synthesis + message personalization

Start with Expandi-only. Add Playwright for pre-engagement only after first 50 sends are validated.
