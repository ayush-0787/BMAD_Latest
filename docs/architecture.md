# Architecture — Python Trivia App

**Generated:** 2026-06-09 | **Scan level:** Deep

---

## Executive Summary

Python Trivia App is a single-process desktop game using the **Screen Manager** pattern. The `pygame-ce` event loop drives a fixed-step `handle_events → update → draw` cycle per frame at 60 FPS. All game state is held in a single `GameState` dataclass instance that lives inside `ScreenManager`; screens read from and write to it directly rather than owning their own state. Three strictly-separated packages (`questions`, `scoring`, `ui`) enforce testability: the first two have zero `pygame` imports and are covered by the pytest suite; `ui` is excluded from automated tests.

---

## Technology Stack

| Layer | Technology | Version | Notes |
|-------|-----------|---------|-------|
| Language | Python | 3.14.2 | Windows 11 |
| Game engine | pygame-ce | 2.5.7 | Drop-in replacement for pygame; identical API |
| Testing | pytest | 9.0.3 | `tests/` covers questions + scoring only |
| Logging | stdlib `logging` | — | `logging.basicConfig(level=DEBUG)` in main.py |
| Data | JSON | — | UTF-8 encoded question banks |

---

## Architecture Pattern: Screen Manager

```
main.py
└── ScreenManager
    ├── GameState (shared mutable state)
    └── screens dict
        ├── "menu"     → MenuScreen
        ├── "setup"    → SetupScreen
        ├── "game"     → GameScreen
        ├── "handoff"  → HandoffScreen
        └── "results"  → ResultsScreen
```

**Frame lifecycle** (`ScreenManager.run_frame`):

```python
screen = screens[game_state.current_screen]
next_screen = screen.handle_events(events, game_state)
if next_screen:
    incoming = screens[next_screen]
    if hasattr(incoming, "reset"):
        incoming.reset()         # zero per-session state
    game_state.current_screen = next_screen
screen.update(game_state, dt)
screen.draw(surface, game_state)
```

Important: `update()` and `draw()` are called on the **outgoing** screen once more after a transition fires within the same frame. Each screen's `draw()` must guard against this (see `HandoffScreen`).

---

## Module Boundaries (Hard Constraints)

### AR-6: `scoring/` is PyGame-free

`scoring/engine.py` and `scoring/multiplier.py` contain only pure Python. They have no `import pygame`, no `from ui`, no `from questions`. This is enforced by the test suite (`test_no_pygame_in_scoring_engine`, `test_no_pygame_in_scoring_multiplier`).

### AR-9: Absolute imports only

All cross-package imports use absolute paths: `from scoring.engine import GameState`, never `from ..scoring`. Enforced throughout all source files.

### AR-11: No PyGame tests

`tests/` covers only `questions/` and `scoring/`. No `pygame.init()` calls in tests. UI behaviour is verified manually or via non-rendering smoke tests.

---

## Data Flow

```
startup:
  main.py
    → load_questions("data/questions_politics.json")
    → load_questions("data/questions_history.json")
    → all_questions passed to ScreenManager(all_questions)
    → ScreenManager passes slice to MenuScreen and SetupScreen constructors

game round (single-player):
  MenuScreen.handle_events
    → draw_questions(all_questions, category)  [questions/bank.py]
    → GameState.questions = drawn_list
    → GameState.players = [Player("Player 1")]
    → return "game"

game round (multiplayer):
  SetupScreen.handle_events
    → draw_questions(all_questions, category)
    → GameState.questions = drawn_list
    → GameState.players = [Player(name) for name in player_names]
    → return "game"

per question:
  GameScreen.handle_events
    → calculate_speed_bonus(BASE_SCORE, time_elapsed, QUESTION_TIMER)  [scoring/engine.py]
    → apply_streak_multiplier(points, player.streak)                    [scoring/multiplier.py]
    → mutates player.score, player.streak, player.correct, player.total

turn end (multiplayer):
  GameScreen.handle_events → return "handoff"
  HandoffScreen.handle_events
    → game_state.active_player_index += 1
    → game_state.current_question_index = 0
    → return "game"

results:
  ResultsScreen.draw
    → branches on game_state.selected_mode
    → "multiplayer": sorted leaderboard, dense ranking
    → other: win/lose verdict, single score
```

---

## GameState Schema

Defined in `scoring/engine.py` as a `@dataclass`. This is the **single source of truth** for all runtime game data.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `current_screen` | `str` | `"menu"` | Active screen key; controls routing |
| `selected_mode` | `str` | `""` | `"single"` or `"multiplayer"` |
| `selected_category` | `str` | `""` | `"Politics"` or `"History"` |
| `players` | `list[Player]` | `[]` | Ordered player list |
| `active_player_index` | `int` | `0` | Index into `players` for current turn |
| `current_question_index` | `int` | `0` | Index into `questions` for current question |
| `questions` | `list[dict]` | `[]` | Current round's drawn question dicts |

Reset on "Main Menu" click in `ResultsScreen`: all 6 mutable fields reset to defaults, `current_screen` handled by screen transition `"menu"`.

---

## Player Schema

Defined in `scoring/engine.py` as a `@dataclass`.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | — | Display name |
| `score` | `int` | `0` | Accumulated point total |
| `streak` | `int` | `0` | Current correct-answer streak |
| `correct` | `int` | `0` | Count of correct answers |
| `total` | `int` | `0` | Count of answered questions |
| `.percentage` | `float` (property) | — | `correct/total*100` or `0.0` if total==0 |

---

## Screen Descriptions

| Screen | Key | Description |
|--------|-----|-------------|
| `MenuScreen` | `"menu"` | Mode selection (Single/Multiplayer/Quit) and category selection (single-player only). Has `reset()` to return to mode stage. |
| `SetupScreen` | `"setup"` | Multiplayer setup: player count (2–4) → names → category. Has `reset()` to zero all input state. |
| `GameScreen` | `"game"` | Question display, answer input, timer countdown, live scoring HUD. Has `reset()` for per-player state. |
| `HandoffScreen` | `"handoff"` | Pass-device screen between multiplayer turns. Tap/click advances `active_player_index`. No `reset()` needed. |
| `ResultsScreen` | `"results"` | End-of-game results. Single-player: win/lose. Multiplayer: ranked leaderboard. |

---

## Screen Transitions

Transitions are communicated **only** via return string from `handle_events()`. Screens never import each other or call `ScreenManager` methods.

```
"menu" ──(single + category selected)──────────────────→ "game"
"menu" ──(multiplayer selected)────────────────────────→ "setup"
"setup" ──(category selected)──────────────────────────→ "game"
"game" ──(questions complete, more players remain)─────→ "handoff"
"game" ──(questions complete, last player or single)───→ "results"
"handoff" ──(tap/click)────────────────────────────────→ "game"
"results" ──(Main Menu clicked)────────────────────────→ "menu"
```

---

## Scoring Formulas

**Speed bonus** (`scoring/engine.py`):
```
speed_bonus = int(BASE_SCORE * max(0, 1 - time_elapsed / QUESTION_TIMER))
```
Range: 0–100 additional points.

**Streak multiplier** (`scoring/multiplier.py`):
```
streak 0–1  → ×1.0
streak 2    → ×1.5
streak 3–4  → ×2.0
streak 5+   → ×3.0
```

**Final points per correct answer:**
```
points = apply_streak_multiplier(BASE_SCORE + speed_bonus, player.streak)
```

---

## Constants (ui/constants.py)

All UI magic numbers live here. Screens import from this file; no hardcoded values anywhere else.

| Constant | Value | Purpose |
|----------|-------|---------|
| `SCREEN_WIDTH` | 800 | Window width (px) |
| `SCREEN_HEIGHT` | 600 | Window height (px) |
| `FPS` | 60 | Target frame rate |
| `QUESTION_TIMER` | 30 | Seconds per question |
| `BASE_SCORE` | 100 | Base points per correct answer |
| `FONT_LARGE` | 48 | Large font size |
| `FONT_MEDIUM` | 32 | Medium font size |
| `FONT_SMALL` | 24 | Small font size |
| `BUTTON_WIDTH` | 300 | Standard button width |
| `BUTTON_HEIGHT` | 60 | Standard button height |
| `MARGIN` | 60 | Standard layout margin |
| `TIMER_BAR_H` | 10 | Timer progress bar height |

---

## Testing Strategy

Tests live in `tests/` and run with `python -m pytest tests/ -v`.

| Test file | Coverage |
|-----------|----------|
| `test_engine.py` | `calculate_speed_bonus` edge cases; PyGame-free assertion |
| `test_multiplier.py` | `get_multiplier` and `apply_streak_multiplier` boundary values; PyGame-free assertion |
| `test_bank.py` | `draw_questions` filtering, deduplication, randomness, error exit |
| `test_loader.py` | `load_questions` valid files, missing fields, bad types, missing file |

**Not tested by automated suite:** Any `ui/` code (all `pygame.Surface`, `pygame.Rect`, and event-processing code). UI is verified by manual smoke tests using PowerShell heredocs that exercise logic paths without a display.

---

## Architecture Rules Reference

| Rule | Description |
|------|-------------|
| AR-5 | Screen transitions via return string from `handle_events()` only |
| AR-6 | `scoring/` completely free of PyGame; enforced by tests |
| AR-7 | All UI constants in `ui/constants.py`; no magic numbers in screens |
| AR-8 | `logging` module throughout; never bare `print()` |
| AR-9 | Absolute imports only |
| AR-11 | `tests/` covers only `questions/` and `scoring/`; no PyGame tests |
