# Workflow: Free Build Delivery (the proof engine)

**Objective:** Deliver ONE working `buildbridge` output free to a founding client, walk it through on
Loom, and convert it into a testimonial + case study + referral (the fence).

## The free build = buildbridge
Project: `Artchitectural_design_automation/` (FastAPI + OpenRouter, 14 stages). Pick ONE output that
matches the lead's pain:
- **Stage 1** mood board + palette
- **Stage 2** activity overlay on their floor plan
- **Stage 3** material / lighting / BOQ → Google Sheet (Setu-styled)
- **Stage 4** FF&E sourcing sheet
For architecture/infra leads (e.g. Nine Bricks) the wedge may be a doc/report workflow (status report,
BOQ) rather than interior stages — match the real pain, deliver one thing.

## Steps
1. Get one real input from them (a brief, a floor plan, a project's last status update).
2. Run the matched buildbridge stage → deliverable (Google Sheet / mood board).
3. **Storage:** create Tier B Drive folder `Clients/<Name>/free-build/` (`drive_sync.py --tier client
   --subfolder free-build`). buildbridge's own "Project Reports/<Vendor>/" output is linked/copied here.
4. **Loom:** script the walkthrough (`loom-walkthrough-recorder` for the deliverable demo). Show the
   output running; state the measured time saved (conservative, measured on their real project).
5. **Fence:** ask for testimonial + case-study permission + 1 referral. Save testimonial to
   `Clients/<Name>/case-study/`.
6. Track: `lead_tracker.py --advance` → Free Build → Delivered → Testimonial/Referral.

## Rule
"Built, not advised." Show something running. Conservative ROI. Cap at 7 free builds.
Once they book a paid call / active delivery starts → artifacts move to LOCAL `~/Desktop/MyClients/<Name>/` (Tier C).
