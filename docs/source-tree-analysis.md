# Source Tree Analysis — Python Trivia App

**Generated:** 2026-06-09 | **Scan level:** Deep

---

## Annotated Directory Tree

```
trivia-app/                          ← project root
│
├── main.py                          ← ENTRY POINT: init pygame, load questions, run game loop
├── requirements.txt                 ← pygame-ce==2.5.7, pytest==9.0.3 + helpers
├── .gitignore                       ← excludes .venv/, __pycache__/, .pytest_cache/
│
├── data/                            ← QUESTION BANKS (JSON, UTF-8)
│   ├── questions_politics.json      ← 12 Politics questions
│   └── questions_history.json       ← 12 History questions
│
├── questions/                       ← MODULE: question loading & draw (PyGame-free)
│   ├── __init__.py                  ← empty
│   ├── loader.py                    ← load_questions(path): validates + returns list[dict]
│   └── bank.py                      ← draw_questions(questions, category, n=10): random sample
│
├── scoring/                         ← MODULE: game state & scoring formulas (PyGame-free)
│   ├── __init__.py                  ← empty
│   └── engine.py                    ← GameState dataclass, Player dataclass, calculate_speed_bonus()
│   └── multiplier.py                ← get_multiplier(streak), apply_streak_multiplier(score, streak)
│
├── ui/                              ← MODULE: all rendering & input (requires PyGame)
│   ├── __init__.py                  ← empty
│   ├── constants.py                 ← ALL UI magic numbers: sizes, colors, timings
│   ├── screen_manager.py            ← Screen base class + ScreenManager (owns GameState)
│   ├── menu_screen.py               ← MenuScreen: mode selection, category selection
│   ├── setup_screen.py              ← SetupScreen: player count + names + category (multiplayer)
│   ├── game_screen.py               ← GameScreen: question display, timer, answer input, scoring
│   ├── handoff_screen.py            ← HandoffScreen: pass-device prompt between turns
│   └── results_screen.py            ← ResultsScreen: end-of-game results / leaderboard
│
└── tests/                           ← PYTEST SUITE (covers questions + scoring only)
    ├── __init__.py                  ← empty
    ├── test_engine.py               ← 7 tests: calculate_speed_bonus + PyGame-free assertion
    ├── test_multiplier.py           ← 13 tests: streak multiplier logic + PyGame-free assertion
    ├── test_bank.py                 ← 7 tests: draw_questions filtering/randomness/errors
    └── test_loader.py               ← 10 tests: load_questions validation/error handling
```

---

## Critical Files

### Entry Point

**`main.py`**
Bootstraps the application:
1. Loads all questions from both JSON files via `questions.loader.load_questions`.
2. Calls `pygame.init()`, creates the display surface, clock.
3. Instantiates `ScreenManager(all_questions)`.
4. Runs the game loop: `clock.tick(FPS)` → `pygame.event.get()` → `manager.run_frame()` → `pygame.display.flip()`.
5. Handles the `pygame.QUIT` event to exit cleanly.

### Shared State

**`scoring/engine.py`**
The `GameState` dataclass is the single source of truth passed by reference to every screen's `handle_events`, `update`, and `draw` methods. Any mutation (incrementing score, advancing question index) is visible to the next method called in the same frame.

### Screen Routing

**`ui/screen_manager.py`**
Contains the `Screen` ABC (with no-op base implementations) and the `ScreenManager`. The `run_frame` method orchestrates the per-frame lifecycle and applies transitions. The `ScreenManager.__init__` instantiates all screens and passes them the shared `all_questions` list where needed.

### UI Constants

**`ui/constants.py`**
Single location for all numeric and color constants. Any value that could otherwise be a magic number in a screen file belongs here. AR-7 mandates this.

---

## Integration Points

All cross-package flow goes through `GameState`. Screens never import each other directly.

```
questions/loader.py  ──→  main.py  ──→  ui/screen_manager.py
questions/bank.py    ──→  ui/menu_screen.py (via direct import)
questions/bank.py    ──→  ui/setup_screen.py (via direct import)
scoring/engine.py    ──→  ui/screen_manager.py (GameState import)
scoring/engine.py    ──→  ui/menu_screen.py (Player import)
scoring/engine.py    ──→  ui/setup_screen.py (Player import)
scoring/engine.py    ──→  ui/game_screen.py (calculate_speed_bonus import)
scoring/multiplier.py ──→  ui/game_screen.py (apply_streak_multiplier, get_multiplier imports)
ui/constants.py      ──→  all ui/*.py screens
ui/screen_manager.py ──→  all ui/*.py screens (Screen base class import)
```

---

## Excluded Directories

| Path | Reason excluded |
|------|----------------|
| `.venv/` | Python virtual environment (binary, not source) |
| `__pycache__/` | Compiled bytecode |
| `.pytest_cache/` | pytest run cache |
