# OutreachAutomation — Improvements Note

> Generated: 2026-07-07 (Day-3 connecting-layer sprint, Track C)
> Derived from: brief inspection of STATUS.md, CLAUDE.md, tools/, dashboard/, workflows/, artifacts/
> Purpose: resume-anchor for whoever picks this project back up. Concrete items only, no rebuild scope.
> STRICT: do not touch the `codex` branch — it is owned by Codex for ClickUp tracking.

---

## Dashboard Script Sprawl

- **Five separate dashboard scripts do related jobs with no shared contract.** `build_board.py`, `build_html.py`, `log_sent.py`, `log_reply.py`, and `scan_replies.py` each read and write `leads.json`-adjacent state. There is no validation that they agree on field names. Consolidating them into a single `dashboard_cli.py` with sub-commands (`build`, `log-sent`, `log-reply`, `scan`, `add-lead`) would cut maintenance surface and make the interface clear.
- **`build_board.py` and `build_html.py` are functionally redundant.** Both produce HTML boards from the same lead data. `build_html.py` appears to be an earlier version. Confirm which is canonical and remove (or clearly deprecate) the other.
- **`add_lead.py` in dashboard/ vs `lead_tracker.py` in tools/ are overlapping entry points.** Two scripts that add a lead to the same store. Pick one; document why the other exists or delete it.

---

## ClickUp Sync Decision Pending

- **Dual-path ClickUp sync (MCP vs REST token) was flagged as undecided on 2026-06-07 and is still unresolved.** `clickup_sync.py` is wired for a REST token; the actual ClickUp build-out used MCP. The `codex` branch is tackling this separately. Check whether Codex's branch resolves it before building more tooling on top. Do not create a third path.
- **`clickup_build_out.py` did the one-time setup work.** Now that the ClickUp space is built, this script has no recurring role. Annotate it clearly as "one-time setup, do not re-run" or move it to `artifacts/setup/`.

---

## Brand Voice Duplication

- **`tools/setu_voice.py` is a hand-embedded copy of voice rules from content-wiki.** The comment at the top of the file acknowledges this: "If the wiki changes, update this file." That manual sync has already drifted — the content-wiki version is the authoritative source. The shared context store introduced in this sprint (`SharedInfra/shared_context/`) provides a single source of truth. See `shared_context/ADAPTER.md` in this project for the adapter pattern to adopt when resuming.

---

## Missing Leads

- **Four warm leads were listed as "add to tracker" in STATUS.md on 2026-06-07.** As of 2026-07-07 they are still absent from `.tmp/leads.json`. The tracker has only Nine Bricks Studio seeded. Before running outreach metrics or any analytics, populate the missing leads.
- **Thread files in `dashboard/threads/` are ahead of `.tmp/leads.json`.** Eighteen thread files exist (Studio Artha, Monica Reddy, etc.) but leads.json has one record. Either hydrate leads.json from the thread files or establish which store is canonical.

---

## Phase 2 Cold Outreach

- **Phase 2 is scaffolding-only.** Domain warmup, `email_sender.py`, `compliance.py`, and `domain_checker.py` are all listed in `artifacts/docs/SYSTEM-COMPONENTS.md` but none exist in `tools/`. The Phase 2 decision should wait until warm outreach produces at least one client or a clear "warm is exhausted" signal — consistent with the current MentorsWikki doctrine (warm-first at Setu's stage).
- **Apollo People Search blocked on free plan.** This is correctly deferred. Re-evaluate when Phase 2 starts and a budget decision is made. Do not build tooling that assumes Apollo access.

---

## Workflow Hygiene

- **`workflows/` has 12 files but not all have been run against real leads.** `audit_preparation.md`, `audit_presentation.md`, `discovery_interview_conduct.md`, and `free_build_delivery.md` assume a prospect who has already replied. Until the first Diagnosis Call is booked, these are dead weight in the active context. Mark them PHASE-2+ so session context does not load them prematurely.
- **`artifacts/outreach/session-status-2026-06-07.md` is a point-in-time snapshot.** It predates the Day-1 sends (2026-06-18 commit) and the thread files. Supersede it with STATUS.md updates rather than creating new dated snapshot files.
- **Google OAuth client mismatch (web vs Desktop) is flagged as fragile but unfixed.** If Drive sync breaks, this is the first place to look. Document the workaround steps in `credentials/README.md` so they are not lost between sessions.

---

## On Resume

1. Populate the four missing warm leads into `.tmp/leads.json` from the existing thread files.
2. Decide the canonical dashboard script and deprecate the duplicate.
3. Lock the ClickUp sync approach once Codex's branch is reviewed.
4. Register the shared context store adapter (see `shared_context/ADAPTER.md`) to stop hand-syncing setu_voice.py.
5. Do not start Phase 2 cold email until at least one warm lead converts to a booked call.
