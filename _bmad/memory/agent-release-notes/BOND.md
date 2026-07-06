# Bond

## Basics
- **Name:** Ayush Pandya
- **Call them:** Ayush
- **Language:** English

## TFS/Azure DevOps Setup
- **Server:** https://almdivapp1.rd.allscripts.com/tfs/projects/
- **Project:** TWEHR
- **Collection (if any):** None — the server URL already resolves straight to the project, no collection segment needed.
- **Validated API base pattern:** `https://almdivapp1.rd.allscripts.com/tfs/projects/TWEHR/_apis` — i.e. `scripts/fetch_work_items.py` defaults (`--server` + `--project TWEHR`, no `--collection`, `api-version=5.1`) work as-is. Confirmed live 2026-07-06 via `--test-connection`. Auth is Basic (empty username, PAT as password) — server also advertises Negotiate/NTLM/Bearer but Basic+PAT is what works and is simplest.
- **PAT handling:** Supplied fresh in the prompt every session. Never stored here or anywhere else.
- **Known TFS project work item types:** Task, Bug, Code Review Request/Response, Feedback Request/Response, Impediment, Product Backlog Item, Shared Steps, Test Case, **Release Note** (a dedicated ADO work item type — worth checking whether releases already get tracked this way before treating scope-gathering as a cold start), Test Plan, Test Suite, Epic, Feature, Shared Parameter, DevAssist, AI Usage, License.
- **Custom Allscripts.Field.\* fields exist and are useful** (added to `DEFAULT_FIELDS` 2026-07-06): `Allscripts.Field.TargetRelease`, `InjectedinRelease`, `ReportedinRelease`, `GoLiveBlocking`, `Regulatory`, plus `System.Reason` and `Microsoft.VSTS.Common.AcceptanceCriteria`. TargetRelease is TFS's own authoritative release label for a Bug — treat it as more trustworthy than an owner-stated release name if the two ever conflict, and flag the conflict rather than silently picking one.
- **Comments/history are usually empty on this project.** The dedicated ADO "comments" REST endpoint returns HTTP 400 on this TFS version (unsupported — not an auth problem). Classic revision history (`/wit/workitems/{id}/updates`) works but most Bugs here apparently don't get free-text `System.History` notes added — field changes only. Practical implication: don't expect comment/history fetches to reliably surface "what was the fix" — `Microsoft.VSTS.Common.AcceptanceCriteria` turned out to be the more reliable place to find fix/expected-behavior detail on a Bug. `fetch_work_items.py` now supports `--with-comments` / `--with-history` flags for when they do have content.
- **State discipline:** `System.State` = "Committed" with `System.Reason` = "Commitment made by team" means the team has committed to doing the work this sprint — it does NOT mean the fix is done/merged/shipped. Only Resolved/Closed states (with a populated `resolved_reason`) mean the work actually landed. Never write a "Committed" bug into a Bug Fixes section as if it shipped — confirm actual completion status with Ayush first.
- **Windows/PowerShell PAT-piping gotcha:** `"$PAT" | python fetch_work_items.py ...` on Windows PowerShell prepends a UTF-8 BOM to stdin that Python's text-mode stdin decoder can mangle into 3 stray bytes instead of one U+FEFF char, corrupting the Basic auth header into a 401 "anonymous access" error even with a correct, valid PAT. Fixed in the script by reading `sys.stdin.buffer` raw and decoding with `utf-8-sig`. If a fresh copy of the script ever regresses on this, that's the first thing to check before assuming the PAT is bad.

## Release & Item Conventions
- **How releases are scoped:** Explicit ID list — Ayush hands over specific work item IDs, not an iteration/tag sweep. (Confirmed 2026-07-06.)
- **Work item type -> section mapping:** Not yet confirmed rule-by-rule with Ayush; working assumption from observed docs is Bug -> Bug Fixes, Product Backlog Item / Feature -> New Features. Verify against real output as it happens rather than treating this as settled.
- **Breaking change signal:** None — no tag/field flags it. Always a judgement call; flag anything that looks migration-impacting and ask rather than relying on metadata. (Confirmed 2026-07-06.)
- **Known issue signal:** Identified via a saved query (the specific query itself not yet captured — confirm next time it matters). (Confirmed 2026-07-06.)
- **Template default:** Depends on release/product — no fixed default. Ask which template(s) each time until a pattern per-product emerges (e.g. is it always both for a `vX.Y` release like 26.3, always internal-only for a single work item like #9248686?). (Confirmed 2026-07-06.)
- **Output location:** `C:\Users\A974997\BMAD\docs\release-notes-{name}.txt` — matches existing files (`release-notes-9248686.txt`, `release-notes-v26.3.txt`, `release-notes-unity-26.3-customer.txt`, etc.). Not yet explicitly confirmed with Ayush, inferred from precedent.

## Their Voice

Product naming observed in existing notes (not yet explicitly confirmed with Ayush, inferred from precedent):
- "TouchWorks EHR -- Hub" and "TouchWorks EHR -- Unity" — double-hyphen (` -- `), not an em dash.
- "ADP" and "Unity" used standalone in ADP-context notes.
- Customer-facing tone: plain language, benefit-first, structured around what the user does/gains rather than what changed technically (see `docs/release-notes-unity-26.3-customer.txt`).
- Internal tone: engineer to engineer, still crisp — see `docs/release-notes-9248686.txt` and `release-notes-v26.3.txt`.

## Things They've Asked Me to Remember

None yet — no explicit "remember that..." requests so far.

## Things to Avoid

None yet identified. Nothing corrected so far this session.
