# Project Overview — Python Trivia App

**Generated:** 2026-06-09 | **Scan level:** Deep

---

## Summary

Python Trivia App is a desktop quiz game built with Python and the `pygame-ce` library. Players answer 10 multiple-choice questions per round against a 30-second countdown timer. The game supports two modes: **single-player** (one player, 10 questions) and **pass-and-play multiplayer** (2–4 players sharing one device, each answering the same 10 questions in turn). After all turns complete, a ranked leaderboard declares the winner.

---

## Technology Stack

| Category | Technology | Version |
|----------|-----------|---------|
| Language | Python | 3.14.2 |
| Game engine | pygame-ce | 2.5.7 |
| Testing | pytest | 9.0.3 |
| Platform | Windows 11 | Desktop |
| Dev environment | Python venv | `.venv/` |

> **Note:** The package is `pygame-ce`, not `pygame` — the API is identical but the package name differs. Do not install both.

---

## Architecture Type

**Monolith — Screen Manager pattern**

The app is a single-process, event-driven game loop. UI state is managed through a `ScreenManager` that routes each frame to the active `Screen` subclass. A shared `GameState` dataclass passes mutable game data across screens with no global state or dependency injection.

Three enforced module boundaries:

| Package | Responsibility | PyGame dependency |
|---------|----------------|-------------------|
| `questions/` | Load and validate question JSON; draw random subsets | None |
| `scoring/` | GameState, Player dataclass, scoring formulas | None |
| `ui/` | All rendering, input handling, screen transitions | pygame-ce |

---

## Game Rules

- **10 questions per player** drawn randomly from the selected category bank.
- **30-second timer** per question; expiry counts as a wrong answer.
- **Base score:** 100 points per correct answer.
- **Speed bonus:** Up to 100 additional points (proportional to time remaining).
- **Streak multiplier:**
  - Streak 1: ×1.0
  - Streak 2: ×1.5
  - Streak 3–4: ×2.0
  - Streak 5+: ×3.0
- **Win condition (single-player):** ≥ 70% correct = "You Win!"; < 70% = "You Lose".
- **Multiplayer:** Dense-ranked leaderboard by percentage; winner is highest percentage player.

---

## Question Banks

| File | Category | Questions |
|------|----------|-----------|
| `data/questions_politics.json` | Politics | 12 |
| `data/questions_history.json` | History | 12 |

Each question requires exactly 10 questions per round, so a minimum of 10 per category must be present. The loader validates structure at startup and exits with a descriptive error if data is malformed or insufficient.

---

## Repository Structure

```
trivia-app/           ← project root (monolith)
├── main.py           ← entry point
├── requirements.txt  ← pygame-ce, pytest, colorama
├── data/             ← question JSON banks
├── questions/        ← loading + validation + draw
├── scoring/          ← GameState, Player, formulas (PyGame-free)
├── ui/               ← all screens + ScreenManager (PyGame)
└── tests/            ← pytest suite (questions + scoring only)
```

---

## Sprint Status

| Epic | Stories | Status |
|------|---------|--------|
| Epic 1: Single-Player | 7 stories (1.1–1.7) | All in review |
| Epic 2: Multiplayer | 3 stories (2.1–2.3) | All in review |

Test suite: **37 tests**, all passing.
