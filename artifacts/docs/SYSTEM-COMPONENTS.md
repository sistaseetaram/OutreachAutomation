# OutreachAutomation — System Components Registry

Complete component list for the 5-track AI agency pipeline.
Build phase-by-phase. Only implement what the current track requires.

Last updated: 2026-06-01
Source of truth: `.claude/plans/so-the-goal-here-glittery-token.md`

---

## The 5-Track Pipeline

```
COLD LEAD → [Track 1: Outreach] → WARM REPLY
           → [Track 2: Audit] → BOOKED CALL
           → [Track 3: Conversion] → SIGNED CLIENT
           → [Track 4: Delivery] → DELIVERED PROJECT
           → [Track 5: Retention] → EXTENDED CLIENT → referral back to Track 1
```

---

## AGENTS

### Cross-Cutting (all tracks)
| Agent | Description | Status |
|---|---|---|
| `executive-agent` | Orchestrates department; interfaces with user | planned |
| `intake-agent` | Triages incoming messages; routes to correct track | planned |
| `analytics-agent` | Tracks metrics across all tracks | planned |
| `compliance-agent` | CAN-SPAM/GDPR, LinkedIn limits, DNC | planned |
| `feedback-loop-agent` | Updates templates from win/loss data | planned |
| `daily-ops-agent` | Morning routine: replies, follow-ups, action items | planned |

### Track 1: Outreach
| Agent | Description | Status |
|---|---|---|
| `icp-agent` | Defines ICP: niche, pain points, budget, triggers | planned |
| `niche-selector-agent` | Researches and scores target niches | planned |
| `offer-architect-agent` | Builds Grand Slam Offers (Hormozi) | planned |
| `buying-signal-detector-agent` | Monitors competitor engagement, job posts, funding | planned |
| `lead-sourcer-agent` | Finds prospects from Apollo/LinkedIn/web | planned |
| `lead-enricher-agent` | Enriches with email, LinkedIn, company data | planned |
| `lead-qualifier-agent` | BANT + signal scoring; routes or discards | planned |
| `pre-engagement-agent` | Likes/comments before connection request | planned |
| `copywriter-agent` | Personalized cold email + DM; real info only | planned |
| `sequence-builder-agent` | Role-based sequences: DM vs IC, Day 0/3/7/14 | planned |
| `outreach-executor-agent` | Sends; enforces LinkedIn daily limits | planned |
| `follow-up-agent` | 3:1 value-to-ask follow-ups across channels | planned |
| `reply-handler-agent` | Classifies replies; routes interested → Track 2 | planned |
| `meeting-scheduler-agent` | Books discovery calls; Calendar integration | planned |

### Track 2: Audit
| Agent | Description | Status |
|---|---|---|
| `company-researcher-agent` | Deep research: founders, team, tech, news, jobs | **building** |
| `audit-prep-agent` | Customized stakeholder + end-user interview Qs | **building** |
| `ops-canvas-agent` | Maps 3-engine Ops Canvas from interview notes | planned |
| `opportunity-matrix-agent` | Plots AI opps: impact vs. effort; Quick Wins first | planned |
| `roi-calculator-agent` | Cost savings + revenue uplift calculation | **building** |
| `audit-presenter-agent` | 5-slide executive audit deck + Money Slide | planned |

### Track 3: Conversion
| Agent | Description | Status |
|---|---|---|
| `onboarding-prep-agent` | Pre-call brief: summary, pain map, call script | planned |
| `onboarding-call-agent` | Guides call; captures notes; flags objections | planned |
| `objection-resolution-agent` | Tailored objection responses | planned |
| `proposal-builder-agent` | Scoped proposal from audit findings | planned |
| `contract-closer-agent` | Generates contract; tracks signature | planned |

### Track 4: Delivery
| Agent | Description | Status |
|---|---|---|
| `project-scoper-agent` | Converts proposal into build spec | planned |
| `delivery-manager-agent` | Manages build lifecycle | planned |
| `testing-agent` | Real-input validation + edge cases | planned |
| `handover-prep-agent` | Credential guide + SOPs + training doc | planned |
| `credential-setup-agent` | Client owns keys + pays bill setup | planned |

### Track 5: Retention
| Agent | Description | Status |
|---|---|---|
| `retention-agent` | Post-delivery check-ins + satisfaction | planned |
| `roi-dashboard-agent` | Monthly ROI report | planned |
| `upsell-identifier-agent` | Surfaces next AI opportunities | planned |
| `retainer-manager-agent` | Ongoing maintenance contracts | planned |
| `referral-agent` | Referral ask at right moment | planned |

---

## SKILLS

### Track 1: Outreach
| Skill | Status |
|---|---|
| `icp-builder` | planned |
| `offer-scorer` | planned |
| `niche-analyzer` | planned |
| `buying-signal-scanner` | planned |
| `outreach-writer` | planned |
| `linkedin-connector` | planned |
| `sequence-designer` | planned |
| `deal-qualifier` | planned |
| `campaign-reviewer` | planned |
| `objection-handler` | planned |
| `case-study-builder` | planned |
| `contract-drafter` | planned |

### Track 2: Audit
| Skill | Status |
|---|---|
| `company-research` | **building** |
| `audit-template-generator` | **building** |
| `process-map-builder` | planned |
| `ops-canvas-builder` | planned |
| `opportunity-matrix-builder` | planned |
| `roi-calculator` | **building** |
| `audit-deck-builder` | planned |

### Track 3: Conversion
| Skill | Status |
|---|---|
| `onboarding-call-prep` | planned |
| `proposal-builder` | planned |
| `objection-handler-live` | planned |

### Track 4: Delivery
| Skill | Status |
|---|---|
| `project-scoper` | planned |
| `handover-builder` | planned |
| `generate-validate-act` | planned |

### Track 5: Retention
| Skill | Status |
|---|---|
| `roi-dashboard-builder` | planned |
| `upsell-identifier` | planned |
| `client-health-scorer` | planned |
| `referral-ask-writer` | planned |

---

## TOOLS (`tools/`)

### Cross-Cutting
| Tool | Status |
|---|---|
| `prospect_state_manager.py` | planned |
| `crm_sync.py` | planned |
| `analytics_reporter.py` | planned |
| `model_router.py` | planned |

### Track 1: Outreach
| Tool | Status |
|---|---|
| `apollo_search.py` | planned |
| `buying_signal_detector.py` | planned |
| `lead_enrichment.py` | planned |
| `personalization_engine.py` | planned |
| `email_sender.py` | planned |
| `email_tracker.py` | planned |
| `linkedin_playwright.py` | planned |
| `linkedin_connector.py` | planned |
| `reply_classifier.py` | planned |
| `sequence_scheduler.py` | planned |
| `offer_scorer.py` | planned |
| `list_cleaner.py` | planned |
| `domain_checker.py` | planned |
| `compliance_checker.py` | planned |
| `calendar_booking.py` | planned |

### Track 2: Audit
| Tool | Status |
|---|---|
| `company_researcher.py` | **building** |
| `interview_template_generator.py` | **building** |
| `excalidraw_generator.py` | planned |
| `roi_calculator.py` | **building** |

### Track 3: Conversion
| Tool | Status |
|---|---|
| `onboarding_call_prep.py` | planned |
| `proposal_generator.py` | planned |

### Track 4: Delivery
| Tool | Status |
|---|---|
| `handover_package_builder.py` | planned |
| `env_setup_guide_generator.py` | planned |
| `test_validator.py` | planned |

### Track 5: Retention
| Tool | Status |
|---|---|
| `roi_dashboard_generator.py` | planned |
| `client_health_scorer.py` | planned |
| `upsell_opportunity_scanner.py` | planned |

---

## WORKFLOWS (`workflows/`)

### Track 1: Outreach
| Workflow | Status |
|---|---|
| `niche_selection.md` | planned |
| `icp_definition.md` | planned |
| `offer_creation.md` | planned |
| `offer_scoring.md` | planned |
| `lead_sourcing.md` | planned |
| `lead_enrichment.md` | planned |
| `lead_qualification.md` | planned |
| `cold_email_sequence.md` | planned |
| `linkedin_outreach.md` | planned |
| `follow_up_cadence.md` | planned |
| `reply_handling.md` | planned |
| `discovery_call_prep.md` | planned |
| `objection_handling.md` | planned |
| `campaign_review.md` | planned |
| `feedback_integration.md` | planned |
| `contract_process.md` | planned |

### Track 2: Audit
| Workflow | Status |
|---|---|
| `company_research.md` | **building** |
| `audit_preparation.md` | **building** |
| `discovery_interview_conduct.md` | **building** |
| `ops_canvas_creation.md` | planned |
| `opportunity_matrix_creation.md` | **building** |
| `opportunity_validation.md` | planned |
| `roi_calculation.md` | **building** |
| `audit_presentation.md` | **building** |

### Track 3–5
| Workflow | Status |
|---|---|
| `warm_to_hot.md` | planned |
| `onboarding_call_prep.md` | planned |
| `onboarding_call_conduct.md` | planned |
| `proposal_creation.md` | planned |
| `contract_and_kickoff.md` | planned |
| `project_scoping.md` | planned |
| `process_mapping.md` | planned |
| `build_and_test.md` | planned |
| `security_guardrails.md` | planned |
| `client_handover.md` | planned |
| `post_delivery_checkin.md` | planned |
| `roi_reporting.md` | planned |
| `upsell_process.md` | planned |
| `retainer_management.md` | planned |
| `referral_process.md` | planned |

---

## TECH STACK

| Task | Primary | Fallback 1 | Fallback 2 |
|---|---|---|---|
| Executive orchestration | Claude Opus 4.8 | Claude Sonnet 4.6 | — |
| Company research | Gemini 2.5 Flash | GPT-4o | Claude Sonnet 4.6 |
| Copywriting + proposals | Claude Sonnet 4.6 | GPT-4o | Gemini 2.5 Flash |
| Classification + routing | Claude Haiku 4.5 | GPT-4o-mini | Gemini 2.5 Flash |
| Bulk research | Groq Llama 3.3 70B | DeepSeek-V3 | Gemini 2.5 Flash |
| ROI + financial calc | Claude Sonnet 4.6 | GPT-4o | — |
| Process maps (Excalidraw) | Claude Sonnet 4.6 | GPT-4o | — |

Cost guard: $5/day. Review cycle: Day 7, then every 30 days.

---

## INFRASTRUCTURE

| Component | Status |
|---|---|
| Outreach domain + SPF/DKIM/DMARC | needed |
| Gmail API OAuth2 | needed |
| Apollo.io API | needed |
| Hunter.io API | needed |
| Google Sheets API | needed |
| Google Calendar API | needed |
| Expandi (LinkedIn cloud) | needed |
| Playwright (LinkedIn pre-engagement) | needed |
| Firecrawl (web scraping) | available |
| Excalidraw | available |
| n8n | optional |
| Anthropic API | available |
