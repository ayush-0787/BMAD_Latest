---
name: fetch-work-items
description: Query TFS/Azure DevOps for the work items behind a release
code: FW
---

# Fetch Work Items

## What Success Looks Like

Your owner gives you a scope — an iteration path, a release tag, a saved query, or a list of work item IDs — and gets back the full, structured detail of every matching work item (type, title, description, resolution notes, area path, tags, state) ready to classify into release note sections. Nothing is fetched twice if it's already in front of you; nothing is skipped because it looked irrelevant.

## Your Approach

Use `scripts/fetch_work_items.py` for the actual TFS calls — it handles the WIQL query, the batch fetch of full work item fields, and auth. Run `uv run scripts/fetch_work_items.py --help` to see the current inputs/outputs before invoking; the script's interface is the source of truth over any description here.

The PAT is supplied by your owner in the prompt, for this run only. Pipe it into the script the way `--help` describes rather than passing it as a plain argument, and never write it to a file, quote it back in a message, echo it in a session log, or let it survive into your sanctum.

If the connection details don't match what's recorded in BOND.md, or the script fails to connect, work with your owner to find the right server/project/API pattern rather than guessing silently — TFS on-prem URL shapes vary by deployment and are worth getting exactly right once.

## Memory Integration

Check BOND.md for the known-good server/project/API pattern before asking your owner to repeat it — the PAT is the only thing you should be asking for fresh every time. Check the work-item-type-to-section conventions already learned so classification during drafting doesn't start from scratch.

## After the Session

If a new connection pattern got validated, or a work item type/tag turned out to map to a release-notes section differently than assumed, record it in BOND.md. Flag any work item with a thin or missing description in the session log — that's a support burden waiting to happen, and worth surfacing per your standing orders.
