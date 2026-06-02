# Nate Herk — AI Project Delivery Framework

Source: Nate Herk (nateherk.com) — AI Automation Society Plus

---

## Core Philosophy

"Systems that are boringly reliable instead of flashy prototypes that break in production."

Treat every build like a product, not a one-off script. ROI-focused use case selection over flashy features. Production readiness first.

---

## The 5-Step Delivery Process

### Step 1: Foundations
- Learn automation fundamentals and core tooling (primarily n8n)
- Develop repeatable problem-framing habits
- Convert operational chaos into actionable specifications
- Build clear thinking and process mapping skills

### Step 2: Process Mapping
- Transform business workflows into detailed diagrams
- Identify triggers, handoffs, and inefficiencies
- Determine where automation delivers maximum ROI impact
- Map complete workflow architecture before writing any code

### Step 3: Workflow vs. Agent Decision
- **Deterministic workflow**: use for reliability-critical operations (invoicing, notifications, data sync)
- **AI agent**: use when judgment and context matter (email triage, content generation, research)
- **Combination**: deterministic scaffolding with AI nodes at reasoning points

### Step 4: Build and Validate
- Build in n8n with separate test + production environments
- Test against real inputs, not just "does the node run?"
- Add guardrails — errors must not spill into production
- Apply **Generate-Validate-Act pattern** (see below)
- Use human-in-the-loop gates for high-risk actions

### Step 5: Ship and Optimize
- Deploy into live environment
- Monitor metrics from day 1
- Iterate based on operational feedback
- Refine until consistent ROI emerges

---

## The Golden Rule for Client Handover

**"The client owns the keys. The client pays the bill."**

- Client sets up their own API accounts (OpenAI, n8n, etc.)
- Client pays for their own subscriptions
- Client owns all credentials
- You build and configure — client operates and owns
- This removes your liability for hosting costs and compliance risk

### Handover Checklist
- [ ] All credentials stored in n8n credential manager (never hardcoded)
- [ ] Separate test + production workflows
- [ ] Client has admin access to their own n8n instance
- [ ] n8n editor NOT exposed to public internet (VPN or IP allowlist)
- [ ] MFA enabled on all admin access
- [ ] API keys follow least-privilege (minimum permissions needed)
- [ ] Client has been trained on basic workflow management
- [ ] "Version 1" clearly documented and signed off

---

## Generate-Validate-Act Pattern

Never pass raw AI output directly into consequential actions.

```
Input → [Input Guardrails] → AI Generate → [Output Guardrails] → Execute Action
```

**Input guardrails** (before AI step):
- Detect jailbreak attempts
- Validate input format + completeness
- Check for PII that shouldn't be processed

**Output guardrails** (after AI step):
- Check output format matches expected schema
- Detect PII exposure, NSFW content, secret key leaks
- Validate against business rules before execution
- Kill switch if anomaly detected

---

## Security for Production

- Webhook URLs: treat as secrets, verify HMAC signatures
- Every external webhook needs API authentication
- Rate limiting on all AI endpoints
- Separate test/prod environments always

---

## What "Version 1 Done" Means

Version 1 is complete when:
- Client can operate it without calling you
- All credentials are in the client's hands
- Test environment is archived or removed
- SOPs exist for common operations
- Known limitations are documented

After Version 1: clean break. Future work is a new engagement, new scope, new price.

---

## n8n as Primary Tool

n8n preferred for:
- Visual workflow builder non-technical clients can understand
- 500+ integrations out of the box
- Self-hostable (client owns instance)
- Supports complex conditional logic + AI nodes
- Active community + templates library
