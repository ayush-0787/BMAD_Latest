---
name: draft-release-notes
description: Classify fetched work items and draft release notes in the chosen template
code: DR
---

# Draft Release Notes

## What Success Looks Like

A release notes document that reads as if someone who understood both the change and the audience wrote it — work items correctly classified into New Features / Bug Fixes / Breaking Changes / Known Issues (or the customer template's equivalent sections), matching the chosen template's structure exactly, saved to `{project-root}/docs/release-notes-{name}.txt` following the project's existing naming convention.

## Your Approach

Classify each work item using the conventions in BOND.md, asking your owner when a type is genuinely ambiguous rather than guessing silently. Confirm which template applies — internal or customer-facing — before drafting, unless it's already obvious from context or a recent, unambiguous default in memory.

Write the prose yourself: the internal template gets technical, engineer-to-engineer language; the customer template gets plain-language, benefit-first framing (what it does, why it matters, how to reach it). The same work item gets rewritten for each audience, never copy-pasted across templates. Ground every sentence in the work item's actual title, description, and comments — if the source material doesn't support a claim, leave it out or flag it to your owner rather than inventing detail. "None." is a legitimate section body; don't pad a section for the sake of symmetry.

Once the content is decided, use `scripts/render_release_notes.py` to stamp it into the exact template layout — run `uv run scripts/render_release_notes.py --help` for its current input shape. Don't hand-format the dividers, field alignment, or wrapping yourself; the script guarantees the output matches every other release notes file in `docs/`. Before writing, check whether a file already exists at the target output path and confirm with your owner before overwriting — these are historical records, not scratch files.

## Memory Integration

Reuse the classification and voice conventions already recorded in BOND.md. If this looks like a recurring release cadence, check MEMORY.md for the previous release's version and date to sanity-check the new one isn't a duplicate or a regression.

## After the Session

Record what was drafted — version or work item ID, date, template used, output path — in the session log for later curation into MEMORY.md's release history. Note any classification call that needed your owner's judgment; that's a candidate for a BOND.md convention update.
