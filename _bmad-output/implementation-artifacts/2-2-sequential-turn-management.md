---
baseline_commit: NO_VCS
---

# Story 2.2: Sequential Turn Management

Status: review

## Story

As players,
I want each player's turn to follow the previous one with a handoff screen between turns,
So that we take turns fairly without seeing each other's answers.

## Acceptance Criteria

1. Given Player 1 finishes their 10th question, when `current_question_index` reaches 10 and more players remain, then `GameScreen.handle_events` returns `"handoff"` instead of `"results"`, and the handoff screen displays "Pass to [Player 2 name]" until confirmed.

2. Given the handoff screen displays, when the next player taps or clicks, then `active_player_index` increments by 1, `current_question_index` resets to 0, `game_screen.reset()` fires automatically via ScreenManager, and the game screen shows the new player's name and a fresh score of 0.

3. Given the handoff transition completes, when Player 2 answers the question at index 0, the question object is the same instance that Player 1 answered at index 0 — `game_state.questions` is never redrawn or replaced between handoffs (FR-10, OQ-3).

4. Given the last player finishes their 10th question, when `active_player_index + 1 >= len(players)`, then `GameScreen.handle_events` returns `"results"` (unchanged single-player path; no extra handoff screen).

## Tasks / Subtasks

- [x] Task 1: Create `ui/handoff_screen.py` — HandoffScreen class (AC: 1, 2, 3)
  - [x] `HandoffScreen.__init__()` — lazy font refs only; all session data read from GameState at draw/event time
  - [x] `_ensure_fonts()` — lazy `pygame.font.SysFont(None, size)` for FONT_LARGE, FONT_MEDIUM, FONT_SMALL
  - [x] `handle_events(events, game_state) → str | None` — on MOUSEBUTTONDOWN (button==1) or any KEYDOWN: call `_advance_turn(game_state)` and return result; return None otherwise
  - [x] `_advance_turn(game_state) → str` — `game_state.active_player_index += 1`; `game_state.current_question_index = 0`; log at INFO; return `"game"`
  - [x] `update(game_state, dt)` — `pass`
  - [x] `draw(surface, game_state)` — guard: if no players or `active_player_index + 1 >= len(players)` → `surface.fill(BLACK)` and return; otherwise fill BLACK and render four centred lines (see Dev Notes for layout)

- [x] Task 2: Update `ui/game_screen.py` — branch handoff vs results (AC: 1, 4)
  - [x] In `handle_events()` at line 67: replace `return "results"` with branch — if `selected_mode == "multiplayer"` and `active_player_index + 1 < len(players)` → return `"handoff"`; else → return `"results"` (single line change in the guard block at the top of `handle_events`)

- [x] Task 3: Update `ui/screen_manager.py` — register HandoffScreen (AC: 1, 2)
  - [x] Add `from ui.handoff_screen import HandoffScreen` inside `__init__` alongside the existing screen imports
  - [x] Add `"handoff": HandoffScreen()` to `self.screens` dict

- [x] Task 4: Verify ACs by smoke test
  - [x] 2-player game: Player 1 completes all 10 questions → handoff screen appears with "Pass to [Player 2]"; click or keypress → game screen shows Player 2 name and score 0, question 1/10
  - [x] Player 2 completes all 10 questions → results screen appears (no second handoff)
  - [x] 3-player game: two handoff transitions then results; `game_state.questions` list identity unchanged throughout
  - [x] Single-player regression: no handoff screen, goes directly to results after Q10

## Dev Notes

### Architecture Rules in Force

- **AR-5 (Screen transitions via return string):** `_advance_turn` mutates `active_player_index` and `current_question_index` BEFORE returning `"game"`. The mutation-then-return pattern is correct and matches the pattern used in `SetupScreen._on_category_click`.
- **AR-6 (PyGame-free scoring):** HandoffScreen only touches `game_state.active_player_index` and `game_state.current_question_index` — plain Python ints. No PyGame objects enter `scoring/`. ✓
- **AR-7 (All UI constants in `ui/constants.py`):** No magic numbers. Use `FONT_LARGE`, `MARGIN`, etc. throughout.
- **AR-8 (logging, never print):** Log in `_advance_turn` at INFO: `"Handoff: advancing to player %d (%s)", game_state.active_player_index, game_state.players[game_state.active_player_index].name`
- **AR-9 (Absolute imports):** `from ui.handoff_screen import HandoffScreen` — not a relative import.
- **AR-11 (No PyGame tests):** No new test files. ACs 1–4 verified by smoke test only.

### ScreenManager reset() on transition (Story 2.1 learning)

`run_frame` calls `incoming.reset()` (via `hasattr` guard) on the incoming screen at every transition:

```python
if next_screen:
    incoming = self.screens.get(next_screen)
    if incoming and hasattr(incoming, "reset"):
        incoming.reset()
    self.game_state.current_screen = next_screen
```

When HandoffScreen returns `"game"`, ScreenManager calls `game_screen.reset()` automatically — this zeroes `_question_timer`, `_pause_timer`, `_in_pause`, `_correct_index`, `_last_multiplier`. HandoffScreen itself has **no `reset()` method** — none needed since it carries no persistent state between sessions.

### One-frame draw guard in HandoffScreen (critical for correctness)

After `handle_events` returns `"game"`, `run_frame` continues to call `handoff_screen.update()` and `handoff_screen.draw()` once more in the **same frame** (before the next frame picks up `current_screen = "game"`). By this point `active_player_index` has already been incremented. Without the guard, the draw would compute `active_player_index + 1` on the already-incremented value and potentially index out of bounds.

Guard in `draw()`:
```python
if not game_state.players or game_state.active_player_index + 1 >= len(game_state.players):
    surface.fill(BLACK)
    return
```

This renders a blank frame for 1/60 s — imperceptible.

### GameScreen.handle_events — exact change (lines 67–68)

Current (`ui/game_screen.py:67`):
```python
if game_state.current_question_index >= len(game_state.questions):
    return "results"
```

Replace with:
```python
if game_state.current_question_index >= len(game_state.questions):
    if (game_state.selected_mode == "multiplayer"
            and game_state.active_player_index + 1 < len(game_state.players)):
        return "handoff"
    return "results"
```

No other changes to `game_screen.py`.

### HandoffScreen constants import

```python
from ui.constants import (
    ACCENT, BLACK, FONT_LARGE, FONT_MEDIUM, FONT_SMALL, GREY, MARGIN,
    SCREEN_HEIGHT, SCREEN_WIDTH, WHITE,
)
```

All required constants already exist in `ui/constants.py`. No new constants needed.

### HandoffScreen draw layout

```
y = SCREEN_HEIGHT // 6
→ "Turn Complete!"                         WHITE, font_large,  center x
y += FONT_LARGE + MARGIN // 2
→ "{curr_player.name} is done"             GREY,  font_medium, center x
y += FONT_MEDIUM + MARGIN
→ "Pass to {next_player.name}"             ACCENT, font_large, center x
y += FONT_LARGE + MARGIN
→ "Tap or click anywhere to begin"         WHITE, font_small,  center x
```

Where:
- `curr_player = game_state.players[game_state.active_player_index]`
- `next_player = game_state.players[game_state.active_player_index + 1]`

### Shared questions draw — AC3 verification

`game_state.questions` is assigned once in `SetupScreen._on_category_click`. Neither `HandoffScreen` nor `GameScreen` reassigns or mutates this list. After `current_question_index = 0`, `game_state.questions[0]` returns the same Python object for all players. Smoke test: confirm `id(game_state.questions[0])` is identical across turns using a programmatic check.

### AC4 — last player path

When `active_player_index + 1 >= len(players)` (last player finished), `GameScreen.handle_events` returns `"results"`. `ResultsScreen` currently renders only `players[0]` — this will be replaced by the full leaderboard in Story 2.3. **Do not extend ResultsScreen in this story.**

### PowerShell smoke test quoting (Story 2.1 Dev Agent Record — recurring issue)

When using `.venv\Scripts\python.exe -c @'...'@` in PowerShell, use **single quotes** for ALL Python string literals inside the heredoc. Double quotes are stripped by the PowerShell parser:

```powershell
# WRONG — "Alice" becomes Alice → NameError
.venv\Scripts\python.exe -c @"
gs.players = [Player("Alice")]
"@

# CORRECT
.venv\Scripts\python.exe -c @'
gs.players = [Player('Alice')]
'@
```

### Files modified by this story

| File | Change |
|------|--------|
| `ui/handoff_screen.py` | **NEW** — HandoffScreen class |
| `ui/game_screen.py` | **UPDATE** — `handle_events`: branch `"handoff"` vs `"results"` |
| `ui/screen_manager.py` | **UPDATE** — import + register HandoffScreen |

### Files NOT modified (do not touch)

| File | Reason |
|------|--------|
| `ui/setup_screen.py` | Story 2.1, complete |
| `ui/menu_screen.py` | Story 2.1, complete |
| `ui/results_screen.py` | Story 2.3 scope (leaderboard); current `players[0]`-only render is intentional for now |
| `ui/constants.py` | No new constants needed |
| `scoring/` | AR-6: no PyGame |
| `questions/` | No changes |
| `tests/` | AR-11: no PyGame tests |

## Dev Agent Record

### Debug Log

- PowerShell heredoc stripped double-quotes in smoke test (`"."` became `.` → SyntaxError). Fixed by using single quotes for all Python string literals inside `@'...'@` heredocs. This is the same recurring issue from Story 2.1.

### Completion Notes

- Created `ui/handoff_screen.py` with `HandoffScreen` class: lazy font init, guard in `draw()` for the extra post-transition frame, `_advance_turn()` mutates `active_player_index` and resets `current_question_index` before returning `"game"`.
- Updated `ui/game_screen.py` `handle_events()` with a two-line branch: `multiplayer` + remaining players → `"handoff"`, all other cases → `"results"` (single-player and last-player paths unchanged).
- Updated `ui/screen_manager.py` to import and register `HandoffScreen` under key `"handoff"`. ScreenManager's existing `hasattr(incoming, "reset")` guard handles HandoffScreen having no `reset()` method cleanly.
- 9 programmatic AC checks passed. 37/37 regression tests passed.

## File List

- `ui/handoff_screen.py` — NEW
- `ui/game_screen.py` — UPDATED
- `ui/screen_manager.py` — UPDATED

## Change Log

- 2026-06-09: Story 2.2 implemented — added HandoffScreen, branched GameScreen transitions for multiplayer turn sequencing, registered handoff screen in ScreenManager.
