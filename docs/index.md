# Python Trivia App — Documentation Index

**Generated:** 2026-06-09 | **Scan:** Deep | **Primary AI entry point**

---

## Project Overview

- **Type:** Monolith — single Python process, Windows desktop
- **Primary Language:** Python 3.14.2
- **Game Engine:** pygame-ce 2.5.7
- **Architecture:** Screen Manager pattern with shared GameState
- **Modes:** Single-player, Pass-and-Play Multiplayer (2–4 players)
- **Sprint:** Epic 1 (7 stories) + Epic 2 (3 stories), all in review

---

## Quick Reference

- **Entry point:** `trivia-app/main.py`
- **Run:** `python main.py` (from project root, with `.venv` active)
- **Tests:** `python -m pytest tests/ -v` → 37 tests pass
- **Question data:** `data/questions_politics.json`, `data/questions_history.json`
- **Shared state:** `scoring/engine.py` → `GameState` dataclass
- **UI constants:** `ui/constants.py` (all sizes, colors, timings)
- **Screen routing:** return string from `handle_events()` → `ScreenManager`

---

**Last Updated:** 2026-06-15 | **Deep-Dives:** 1

## Deep-Dive Documentation

Detailed exhaustive analysis of specific areas:

- [UI Screens & Screen Manager Deep-Dive](./deep-dive-ui-screens-and-screen-manager.md) — Comprehensive analysis of all 8 files in `trivia-app/ui/` (829 LOC): Screen base class, ScreenManager orchestrator, MenuScreen, SetupScreen, GameScreen, HandoffScreen, ResultsScreen, and constants — Generated 2026-06-15

## Generated Documentation

| Document | Description |
|----------|-------------|
| [Project Overview](./project-overview.md) | App summary, tech stack, game rules, question banks, sprint status |
| [Architecture](./architecture.md) | Screen Manager pattern, module boundaries, data flow, scoring formulas, AR rules |
| [Source Tree Analysis](./source-tree-analysis.md) | Annotated directory tree, critical files, integration points |
| [Component Inventory](./component-inventory.md) | All 5 screens, scoring functions, question components, design patterns |
| [Data Models](./data-models.md) | Question JSON schema, GameState dataclass, Player dataclass, state lifecycle |
| [Development Guide](./development-guide.md) | Setup, run, test, architecture rules, adding questions/screens, common issues |

## Diagrams

| Diagram | Description |
|---------|-------------|
| [Screen Flow](./screen-flow.md) | Detailed flowchart of every screen, stage, decision point, and transition including GameState init and reset |
| [Scoring Logic](./scoring-logic.md) | Detailed flowchart of speed bonus, streak multiplier, point calculation, percentage tracking, and end-of-round outcomes |

---

## Screen Navigation Map

```
"menu" ──single+category──→ "game" ──last player done──→ "results" ──Main Menu──→ "menu"
"menu" ──multiplayer──────→ "setup" ─category──────────→ "game"
                                                            ↓ more players remain
                                                         "handoff" ──tap/click──→ "game"
```

---

## Module Boundaries (Critical for AI Context)

| Package | PyGame | Tests | Role |
|---------|--------|-------|------|
| `questions/` | No | Yes | Load JSON, validate, draw random subset |
| `scoring/` | No | Yes | GameState, Player, speed bonus, streak multiplier |
| `ui/` | Yes | No | All rendering, input handling, screen transitions |

> When generating code: `scoring/` and `questions/` changes need tests. `ui/` changes do not. Never add `pygame` imports to `scoring/` or `questions/`.

---

## Key Code Locations

| What | Where |
|------|-------|
| GameState definition | `scoring/engine.py:5` |
| Player definition | `scoring/engine.py:16` |
| Speed bonus formula | `scoring/engine.py:28` |
| Streak multiplier | `scoring/multiplier.py:1` |
| Screen base class | `ui/screen_manager.py:4` |
| ScreenManager frame loop | `ui/screen_manager.py:32` |
| All UI constants | `ui/constants.py` |
| Question validation | `questions/loader.py:29` |
| Handoff one-frame guard | `ui/handoff_screen.py:47` |
| Multiplayer leaderboard | `ui/results_screen.py:115` |

---

## Getting Started (for AI-Assisted Development)

1. Read [Architecture](./architecture.md) to understand the Screen Manager pattern and module rules before writing any code.
2. Read [Component Inventory](./component-inventory.md) to understand what each screen does and what state it owns.
3. Read [Data Models](./data-models.md) for the `GameState` and `Player` schemas before touching any state logic.
4. Check [Development Guide](./development-guide.md) for the exact commands to run tests and the PowerShell smoke test pattern.
5. Always run `python -m pytest tests/ -v` after changes to `scoring/` or `questions/`.

---

## Brownfield Development Notes

- **New game mode:** Add a screen, register in `ScreenManager.screens`, return its key from an existing screen's `handle_events`. GameState may need new fields.
- **New question category:** Add a JSON file in `data/`, update `main.py` to load it, update `questions/loader.py` validation for the new category string, add category button to `MenuScreen` and `SetupScreen`.
- **New scoring mechanic:** Add to `scoring/engine.py` or `scoring/multiplier.py` (PyGame-free). Add tests in `tests/test_engine.py` or `tests/test_multiplier.py`.
- **UI layout changes:** Only modify values in `ui/constants.py` (AR-7). Do not hardcode pixel values in screen files.
