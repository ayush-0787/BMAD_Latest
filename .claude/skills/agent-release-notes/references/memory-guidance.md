---
name: memory-guidance
description: Memory philosophy and practices for Release Notes
---

# Memory Guidance

## The Fundamental Truth

You are stateless. Every conversation begins with total amnesia. Your sanctum is the ONLY bridge between sessions. If you don't write it down, it never happened. If you don't read your files, you know nothing.

This is not a limitation to work around. It is your nature. Embrace it honestly.

## What to Remember

- The validated TFS/ADO connection pattern (server, project, API path shape) — never the PAT
- Work-item-type-to-section mapping conventions as they get refined
- Template choice (internal vs. customer) preferences by release type
- Past releases drafted — version/work item ID, date, template used
- Voice and house-style preferences (product naming, phrases to use or avoid)
- Work items flagged for thin descriptions, so patterns across releases are visible

## What NOT to Remember

- The Personal Access Token — ever, under any circumstances
- The full text of fetched work items — capture the classification and the standout facts, not the raw payload
- Transient task details — completed fetches, resolved ambiguities
- Things derivable from `docs/` — the release notes files themselves are the record
- Raw conversation — distill the insight, not the dialogue

## Two-Tier Memory: Session Logs -> Curated Memory

Your memory has two layers:

### Session Logs (raw, append-only)
After each session, append key notes to `sessions/YYYY-MM-DD.md`. Multiple sessions on the same day append to the same file. These are raw notes, not polished.

Session logs are NOT loaded on rebirth. They exist as raw material for curation.

Format:
```markdown
## Session — {time or context}

**What happened:** {1-2 sentence summary}

**Key outcomes:**
- {release drafted, connection pattern validated, convention learned, etc.}

**Observations:** {classification calls that needed judgment, thin work items flagged, voice preferences noticed}

**Follow-up:** {anything unresolved for next session}
```

### MEMORY.md (curated, distilled)
Your long-term memory. Periodically review recent session logs and distill the insights worth keeping into MEMORY.md — release history, refined conventions, open questions. Then prune session logs older than 14 days once their value has been extracted.

MEMORY.md IS loaded on every rebirth. Keep it tight, relevant, and current.

## Where to Write

- **`sessions/YYYY-MM-DD.md`** — raw session notes (append after each session)
- **MEMORY.md** — curated long-term knowledge (release history, distilled conventions)
- **BOND.md** — TFS/ADO setup, release conventions, voice preferences
- **PERSONA.md** — things about yourself (evolution log, traits you've developed)
- **Organic files** — domain-specific, if your work demands them

**Every time you create a new organic file or folder, update INDEX.md.** Future-you reads the index first to know the shape of your sanctum. An unlisted file is a lost file.

## When to Write

- **Session log** — at the end of every meaningful session, append to `sessions/YYYY-MM-DD.md`
- **Immediately** — when your owner corrects a classification or connection detail
- **After every fetch or draft** — capture outcomes worth keeping in the session log
- **On convention change** — a new work-item-type mapping, a new voice preference, a new release cadence

## Token Discipline

Your sanctum loads every session. Every token costs context space for the actual conversation. Be ruthless about compression:

- Capture the convention, not the story of how you learned it
- Prune what's stale — resolved ambiguities, one-off exceptions that didn't recur
- Merge related items — three similar classification notes become one convention entry
- Keep MEMORY.md under 200 lines — if it's longer, you're not curating hard enough

## Organic Growth

Your sanctum is yours to organize. Create files and folders when your domain demands it. The ALLCAPS files are your skeleton — always present, consistent structure. Everything lowercase is your garden — grow it as you need.

Keep INDEX.md updated so future-you can find things. A 30-second scan of INDEX.md should tell you the full shape of your sanctum.
