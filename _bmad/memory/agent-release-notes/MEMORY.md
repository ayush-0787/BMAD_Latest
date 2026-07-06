# Memory

_Curated long-term knowledge. Empty at birth — grows through sessions._

_This file is for distilled insights, not raw notes: release history, refined classification conventions, validated connection patterns, open questions. Capture the essence — never the PAT, never a full work item dump._

_Keep under 200 lines. Raw session notes go in `sessions/YYYY-MM-DD.md` (not here). Distill insights from session logs into this file periodically. Prune what's stale. Every token here loads every session — make each one count. See `references/memory-guidance.md` for full discipline._

## Open Questions

- What is the actual saved query used to identify Known Issues? Ayush confirmed the *mechanism* (a query) but not the query itself — get it the next time Known Issues is in scope.
- Is there a per-product default template pattern worth inferring (e.g. Unity/customer-visible features get both internal+customer, a narrow single-item fix like #9248686 gets internal only)? Only one data point so far (v26.3 got both) — watch for a second before treating it as a rule.
- Does the dedicated "Release Note" work item type in TWEHR get used to track releases themselves, or is it unrelated to how Ayush scopes work? Asked, not yet answered.
- Is `System.State` a generally unreliable signal for "did this actually ship" on this project (see #9329271, "Committed" but confirmed shipped), or was that a one-off board lag? Watch the next few items before drawing a rule — see BOND.md for the field-level detail.
- Does #9329271 relate to / retire any of the RTPB v13 Known Issues already in `release-notes-v26.3.txt`? Adjacent symptom (incorrect display vs. missing display), not confirmed as the same root cause — don't assume without asking.

## Prior Releases (context, not to re-derive from docs/ each time)

- **#9248686** (ADP 26.2, 2026-05-12): Doc Admin role edit access for Unity Release Notes page. Internal template only, single work item.
- **v26.3 / TouchWorks EHR -- Hub**: NCPDP RTPB v13, PDMP endpoint migration, RxTP cert migration to Key Vault, KS SOAP signature update. Internal-only notes produced; Known Issues section is RTPB v13 / Formulary v60 heavy — recurring pain points worth flagging if they resurface in a later release.
- **Unity 26.3 / TouchWorks EHR -- Unity** (customer-facing, 2026-07-06): portal-type visibility in TW Mobile tasks, always-visible active clinical data fix. Companion customer-facing note to the same v26.3 wave as the Hub notes above — confirms "both templates for one release" is a real pattern, not a one-off.
- **#9329271** (Hub 26.3, 2026-07-06): RTPB v13 Common UI display fix — pharmacies with a CoverageStatusCode-only response were showing false "Pricing not available"/"Not Covered" instead of being suppressed per display rules. Internal template only, single work item. First release note drafted from a live TFS fetch (not sourced from pre-existing `docs/` precedent).
