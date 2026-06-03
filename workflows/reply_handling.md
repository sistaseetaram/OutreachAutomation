# Workflow: Reply Handling

**Objective:** Classify every inbound reply and route it correctly. Protect compliance + the relationship.

## Steps
1. `reply_classifier.py --text "<reply>" --studio "<studio>" --apply`
2. Route by category:
   - **interested** → status `Replied` → book the free diagnosis (Gem + scoping chat).
   - **question** → `Replied` → answer plainly (Setu voice), then offer the diagnosis.
   - **not_now** → `Nurture` → revisit in ~30–60 days. No more cadence messages now.
   - **wrong_person** → `Lost` → ask for the right contact (1 line), else drop.
   - **unsubscribe** → `Lost` + **remove from all sequences immediately** (compliance, non-negotiable).
3. Positive reply → create Tier B Drive folder (`drive_sync.py --tier client`), move ClickUp to Engaged.
4. WhatsApp replies within 24h → you may free-text via `whatsapp_sender.py --session`.

## Notes
- Hot reply = notify yourself fast (`whatsapp_notifier.py`); speed of first response matters.
- Never argue with a "no". Quiet over loud.
