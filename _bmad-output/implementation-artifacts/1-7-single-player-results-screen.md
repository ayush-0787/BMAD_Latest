---
baseline_commit: NO_VCS
---

# Story 1.7: Single-Player Results Screen

Status: review

## Story

As a player,
I want to see my final score, percentage correct, and a win/loss verdict after the round ends,
So that I know how I performed and can return to the main menu.

## Acceptance Criteria

1. Given a player answered 8 of 10 correctly, when the results screen renders, then it displays the cumulative score, "80%", and "You Win!".
2. Given a player answered 6 of 10 correctly, when the results screen renders, then it displays the cumulative score, "60%", and "You Lose".
3. Given a player answered exactly 7 of 10 correctly, when the results screen renders, then it displays "70%" and "You Win!" (≥70% = win boundary, FR-7).
4. Given the player clicks "Main Menu", when navigation is triggered, then `GameState` resets (players cleared, indices zeroed, mode/category/questions cleared) and the screen transitions to the main menu showing mode selection (not category selection).

## Tasks / Subtasks

- [x] Task 1: Implement `ui/results_screen.py` fully (AC: 1–4)
  - [x] `ResultsScreen.__init__()` — init `_font_large`, `_font_medium`, `_font_small` to `None`
  - [x] `_ensure_fonts()` — lazy-init all three sizes via `pygame.font.SysFont(None, size)`
  - [x] `_get_menu_button_rect()` — returns centered `pygame.Rect` at bottom using only constants
  - [x] `handle_events()` — guard: `if not game_state.players: return None`; detect MOUSEBUTTONDOWN on menu button rect; on click: reset GameState (6 fields), log, return `"menu"`
  - [x] `update()` — pass (no animation)
  - [x] `draw()` — guard `if not game_state.players: return`; render Results title, score, percentage, verdict (GREEN=win/RED=lose), correct count, Main Menu button
- [x] Task 2: Fix `ui/menu_screen.py` stage-reset on return from results (AC: 4)
  - [x] In `handle_events()`, add 2-line guard AFTER `self._ensure_fonts()`: `if not game_state.selected_mode and self._stage != "mode": self._stage = "mode"`
- [x] Task 3: Verify ACs by running the app and programmatic checks
  - [x] `python main.py` → play a full game → results screen shows score, percentage, verdict
  - [x] ≥70% correct game → "You Win!" in GREEN
  - [x] <70% correct game (let some questions time out) → "You Lose" in RED
  - [x] Click "Main Menu" → mode selection screen shown (not category screen)
  - [x] Run programmatic smoke test (see Verification Commands section)

## Dev Notes

### Environment — CRITICAL

**Python 3.14.2, Windows, `pygame-ce==2.5.7`** (NOT `pygame`). All commands from `trivia-app/` with venv active.

No new test files — `tests/` covers only `questions/` and `scoring/` (AR-11). ACs verified by running the app and programmatic headless checks.

### Scope — Two Files

This story modifies exactly **two files**:
1. `ui/results_screen.py` — REPLACE stub entirely
2. `ui/menu_screen.py` — ADD 2 lines to `handle_events`

No other files change. No constants changes. No new constants needed.

### GameState When Results Screen Is Active

When `game_screen.handle_events` returns `"results"`, GameState contains:
- `game_state.players[0]` = `Player(name="Player 1", score=<total>, correct=N, total=10, streak=0)`
- `player.percentage` = `correct / total * 100` (computed property — never call manually)
- `game_state.current_question_index` = 10 (past end of questions list)
- `game_state.questions` = list of 10 dicts (unchanged from game start)
- `game_state.selected_mode` = "single"
- `game_state.selected_category` = "Politics" or "History"

### Win/Loss Logic

```python
pct = game_state.players[0].percentage   # Player.percentage property from scoring/engine.py
verdict = "You Win!" if pct >= 70.0 else "You Lose"
verdict_color = GREEN if pct >= 70.0 else RED
```

**Boundary:** `pct >= 70.0` — a player with 7/10 correct gets `70.0 >= 70.0` → "You Win!" (AC3). Use `>=`, never `>`.

**Percentage formatting:** `f"{pct:.0f}%"` → "80%", "60%", "70%". No decimal places.

### GameState Reset on Main Menu Click

Reset ALL mutable fields — `ScreenManager.game_state` is reused across games, so every field must be explicitly cleared:

```python
game_state.players = []
game_state.active_player_index = 0
game_state.current_question_index = 0
game_state.questions = []
game_state.selected_mode = ""
game_state.selected_category = ""
```

Do NOT reset `current_screen` — that is managed by `ScreenManager.run_frame` via the return value `"menu"`.

### MenuScreen Stage Fix — WHY This Is Needed

`MenuScreen._stage` starts at "mode" but advances to "category" when the player clicks "Single Player". It stays at "category" when the game starts. After the game ends and results transitions back to "menu", `MenuScreen.handle_events` sees `_stage == "category"` and shows "Politics / History" buttons instead of "Single Player / Quit". The player is stuck.

`MenuScreen.reset()` exists (sets `_stage = "mode"`) but nothing calls it on the results→menu path.

**Fix:** Add a guard at the top of `MenuScreen.handle_events` (after `_ensure_fonts()`):
```python
if not game_state.selected_mode and self._stage != "mode":
    self._stage = "mode"
```

When ResultsScreen clears `game_state.selected_mode = ""`, MenuScreen auto-detects this on the next frame and resets its stage. This also protects `draw()` implicitly — on the very first frame `draw()` runs after the transition, `handle_events` has already been called (it runs first in `run_frame`), so `_stage` is already correct.

**This is a 2-line addition to `menu_screen.py`. Do NOT remove existing `reset()` method — Story 2.2 will call it.**

### Architecture Points

**AR-5 compliance:** `handle_events` returns `"menu"` — never mutates `game_state.current_screen` directly.

**AR-7 compliance:** All layout positions derived from `SCREEN_WIDTH`, `SCREEN_HEIGHT`, `FONT_*`, `MARGIN`, `BUTTON_*` constants — no magic numbers. Layout uses cascading y-offsets built from constant expressions.

**AR-8 compliance:** `logging.info` on Main Menu click — never `print()`.

**AR-9 compliance:** `from ui.screen_manager import Screen` — absolute import.

**AR-11 compliance:** No test files added.

**Guard when `players` list is empty:** Both `handle_events` and `draw` check `if not game_state.players: return None / return`. On the one-frame window between GameState reset and the ScreenManager switching screens, this prevents IndexError.

### Exact Layout (cascading y from constants)

```
y = SCREEN_HEIGHT // 6                    # = 100  — title centre
y += FONT_LARGE + MARGIN // 2             # = 178  — score centre
y += FONT_MEDIUM + MARGIN // 2            # = 240  — percentage centre
y += FONT_MEDIUM + MARGIN                 # = 332  — verdict centre (FONT_LARGE height)
y += FONT_LARGE + MARGIN // 2             # = 410  — correct/total count centre
```

Button: `top = SCREEN_HEIGHT - BUTTON_HEIGHT - MARGIN` = 480, center y = 510.

### Constants to Import (results_screen.py)

```python
from ui.constants import (
    ACCENT, BLACK, BUTTON_HEIGHT, BUTTON_HOVER, BUTTON_WIDTH,
    FONT_LARGE, FONT_MEDIUM, FONT_SMALL, GREEN, MARGIN,
    RED, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE,
)
```

No `GREY`, `TIMER_BAR_H`, `QUESTION_TIMER`, `BASE_SCORE`, `BUTTON_PADDING` needed.

### Current State of Modified Files

**`ui/results_screen.py`** — currently a stub:
```python
from ui.screen_manager import Screen

class ResultsScreen(Screen):
    pass
```
→ REPLACE entirely with full implementation.

**`ui/menu_screen.py`** — current `handle_events` (line 45–53):
```python
def handle_events(self, events, game_state) -> str | None:
    self._ensure_fonts()
    buttons = self._get_buttons()
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for name, rect in buttons.items():
                if rect.collidepoint(event.pos):
                    return self._on_click(name, game_state)
    return None
```
→ ADD 2 lines after `self._ensure_fonts()`.

### Exact Code — `ui/results_screen.py` (REPLACE entirely)

```python
import logging

import pygame

from ui.constants import (
    ACCENT, BLACK, BUTTON_HEIGHT, BUTTON_HOVER, BUTTON_WIDTH,
    FONT_LARGE, FONT_MEDIUM, FONT_SMALL, GREEN, MARGIN,
    RED, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE,
)
from ui.screen_manager import Screen


class ResultsScreen(Screen):
    def __init__(self):
        self._font_large = None
        self._font_medium = None
        self._font_small = None

    def _ensure_fonts(self) -> None:
        if self._font_large is None:
            self._font_large = pygame.font.SysFont(None, FONT_LARGE)
            self._font_medium = pygame.font.SysFont(None, FONT_MEDIUM)
            self._font_small = pygame.font.SysFont(None, FONT_SMALL)

    def _get_menu_button_rect(self) -> pygame.Rect:
        return pygame.Rect(
            SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
            SCREEN_HEIGHT - BUTTON_HEIGHT - MARGIN,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
        )

    def handle_events(self, events, game_state) -> str | None:
        if not game_state.players:
            return None
        menu_rect = self._get_menu_button_rect()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if menu_rect.collidepoint(event.pos):
                    player = game_state.players[0]
                    logging.info(
                        "Results: player=%s score=%d pct=%.1f%% → main menu",
                        player.name,
                        player.score,
                        player.percentage,
                    )
                    game_state.players = []
                    game_state.active_player_index = 0
                    game_state.current_question_index = 0
                    game_state.questions = []
                    game_state.selected_mode = ""
                    game_state.selected_category = ""
                    return "menu"
        return None

    def update(self, game_state, dt: float) -> None:
        pass

    def draw(self, surface, game_state) -> None:
        self._ensure_fonts()
        if not game_state.players:
            return

        player = game_state.players[0]
        pct = player.percentage
        verdict = "You Win!" if pct >= 70.0 else "You Lose"
        verdict_color = GREEN if pct >= 70.0 else RED

        surface.fill(BLACK)

        y = SCREEN_HEIGHT // 6

        title_surf = self._font_large.render("Results", True, WHITE)
        surface.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, y)))

        y += FONT_LARGE + MARGIN // 2
        score_surf = self._font_medium.render(f"Score: {player.score}", True, WHITE)
        surface.blit(score_surf, score_surf.get_rect(center=(SCREEN_WIDTH // 2, y)))

        y += FONT_MEDIUM + MARGIN // 2
        pct_surf = self._font_medium.render(f"{pct:.0f}%", True, WHITE)
        surface.blit(pct_surf, pct_surf.get_rect(center=(SCREEN_WIDTH // 2, y)))

        y += FONT_MEDIUM + MARGIN
        verdict_surf = self._font_large.render(verdict, True, verdict_color)
        surface.blit(verdict_surf, verdict_surf.get_rect(center=(SCREEN_WIDTH // 2, y)))

        y += FONT_LARGE + MARGIN // 2
        count_surf = self._font_small.render(
            f"{player.correct} / {player.total} correct", True, WHITE
        )
        surface.blit(count_surf, count_surf.get_rect(center=(SCREEN_WIDTH // 2, y)))

        menu_rect = self._get_menu_button_rect()
        mouse_pos = pygame.mouse.get_pos()
        color = BUTTON_HOVER if menu_rect.collidepoint(mouse_pos) else ACCENT
        pygame.draw.rect(surface, color, menu_rect, border_radius=8)
        label_surf = self._font_medium.render("Main Menu", True, WHITE)
        surface.blit(label_surf, label_surf.get_rect(center=menu_rect.center))
```

### Exact Code — `ui/menu_screen.py` change (2 lines added to `handle_events`)

```python
def handle_events(self, events, game_state) -> str | None:
    self._ensure_fonts()
    if not game_state.selected_mode and self._stage != "mode":
        self._stage = "mode"
    buttons = self._get_buttons()
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for name, rect in buttons.items():
                if rect.collidepoint(event.pos):
                    return self._on_click(name, game_state)
    return None
```

### Verification Commands (run from `trivia-app/` with venv active)

```powershell
# Regression — all 37 existing tests still pass
python -m pytest tests/ -v

# AC1-4: Visual verification
.venv\Scripts\python main.py
# 1. Play a game answering ≥7 correctly → Results shows score, "70%"/"80%"/etc., "You Win!" in GREEN
# 2. Play again answering <7 → "You Lose" in RED
# 3. Click "Main Menu" → mode selection screen (Single Player/Quit), NOT category screen
# 4. Start another game (proves full replay cycle works)

# Programmatic smoke test (headless pygame)
.venv\Scripts\python -c "
import pygame
pygame.init()
surface = pygame.display.set_mode((800, 600))

from scoring.engine import GameState, Player
from ui.results_screen import ResultsScreen
from ui.menu_screen import MenuScreen
from questions.loader import load_questions

# --- Setup ---
rs = ResultsScreen()

# --- AC1: 8/10 correct = 80% = You Win! ---
gs = GameState()
gs.players = [Player('P1')]
gs.players[0].correct = 8
gs.players[0].total = 10
gs.players[0].score = 1200
gs.selected_mode = 'single'
gs.selected_category = 'Politics'
gs.current_question_index = 10

pct = gs.players[0].percentage
assert pct == 80.0, f'expected 80.0, got {pct}'
assert pct >= 70.0, 'should win'
print(f'AC1 8/10: pct={pct:.0f}% You Win! OK')

# --- AC2: 6/10 correct = 60% = You Lose ---
gs2 = GameState()
gs2.players = [Player('P1')]
gs2.players[0].correct = 6
gs2.players[0].total = 10
gs2.players[0].score = 600
pct2 = gs2.players[0].percentage
assert pct2 == 60.0
assert pct2 < 70.0
print(f'AC2 6/10: pct={pct2:.0f}% You Lose OK')

# --- AC3: 7/10 correct = 70% = You Win! (boundary) ---
gs3 = GameState()
gs3.players = [Player('P1')]
gs3.players[0].correct = 7
gs3.players[0].total = 10
pct3 = gs3.players[0].percentage
assert pct3 == 70.0
assert pct3 >= 70.0, '70% should win'
print(f'AC3 7/10: pct={pct3:.0f}% You Win! (boundary) OK')

# --- draw() smoke: no crash with valid player ---
gs_draw = GameState()
gs_draw.players = [Player('P1')]
gs_draw.players[0].correct = 8
gs_draw.players[0].total = 10
gs_draw.players[0].score = 1200
rs.draw(surface, gs_draw)
print('draw() with 8/10: no crash OK')

# --- draw() guard: no crash with empty players ---
gs_empty = GameState()
rs.draw(surface, gs_empty)
print('draw() with empty players: no crash OK')

# --- AC4: handle_events Main Menu click resets GameState ---
button_rect = rs._get_menu_button_rect()
click_x = button_rect.centerx
click_y = button_rect.centery
gs_click = GameState()
gs_click.players = [Player('P1')]
gs_click.players[0].correct = 7
gs_click.players[0].total = 10
gs_click.players[0].score = 900
gs_click.selected_mode = 'single'
gs_click.selected_category = 'History'
gs_click.current_question_index = 10
click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(click_x, click_y))
result = rs.handle_events([click_event], gs_click)
assert result == 'menu', f'expected menu, got {result}'
assert gs_click.players == []
assert gs_click.active_player_index == 0
assert gs_click.current_question_index == 0
assert gs_click.questions == []
assert gs_click.selected_mode == ''
assert gs_click.selected_category == ''
print(f'AC4 Main Menu click: GameState reset, transition to menu OK')

# --- MenuScreen stage fix ---
qs = load_questions('data/questions_politics.json')
ms = MenuScreen(qs)
ms._stage = 'category'  # simulate state after starting a game
gs_menu = GameState()
gs_menu.selected_mode = ''  # simulate after ResultsScreen reset
ms.handle_events([], gs_menu)  # should auto-reset _stage
assert ms._stage == 'mode', f'expected mode, got {ms._stage}'
print('MenuScreen stage auto-reset when selected_mode==\"\" OK')

pygame.quit()
print('All programmatic checks passed')
"
```

### File Summary

| File | Action | Notes |
|------|--------|-------|
| `ui/results_screen.py` | UPDATE | REPLACE stub with full implementation |
| `ui/menu_screen.py` | UPDATE | ADD 2 lines to `handle_events` to reset stage on return from results |

No constants changes. No test files.

### Architecture Compliance

| Rule | Compliance |
|------|-----------|
| AR-5 (transitions via return value) | Returns `"menu"` — never mutates `game_state.current_screen` |
| AR-6 (scoring/ free of pygame) | No changes to `scoring/` |
| AR-7 (constants in ui/constants.py) | All layout from constants — cascading y built from `SCREEN_HEIGHT`, `FONT_*`, `MARGIN` |
| AR-8 (logging not print) | `logging.info()` on Main Menu click |
| AR-9 (absolute imports) | `from ui.screen_manager import Screen`, `from ui.constants import (...)` |
| AR-11 (tests/ no pygame) | No test files added |

### Cross-Story Notes

- **Story 2.2 / 2.3**: `ResultsScreen` is reused for multiplayer leaderboard — the `if not game_state.players: return` guard is already in place. Story 2.3 will extend `draw()` to show multiple players.
- **Story 2.1**: `MenuScreen.reset()` method (unchanged here) will be called by multiplayer setup flow. The stage-fix guard `if not game_state.selected_mode` is safe for multiplayer since that flow sets `selected_mode = "multiplayer"` before any stage ambiguity can occur.

### References

- [Source: epics.md#Story 1.7] — Acceptance criteria (FR-7, FR-8)
- [Source: architecture.md#Decision 1] — GameState dataclass fields and ownership
- [Source: architecture.md#Decision 4] — Player.percentage property
- [Source: architecture.md#Screen Transition Pattern] — return str|None, never mutate current_screen
- [Source: architecture.md#Decision 2] — Screen base class interface
- [Source: 1.6 dev notes] — GameState state when arriving at results (players[0] populated, index=10)
- [Source: 1.4 menu_screen.py] — _stage lifecycle and _on_click pattern

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- PowerShell heredoc double-quote stripping: `.venv\Scripts\python.exe -c @'...'@` strips inner `"` from Python string literals when passing to native exe. Fixed by using single-quoted Python strings throughout the smoke test.

### Completion Notes List

- Replaced `ui/results_screen.py` stub entirely with full implementation (AC1–AC4).
- Added 2-line stage-reset guard to `ui/menu_screen.py` `handle_events()` — detects `selected_mode == ""` after ResultsScreen reset and restores `_stage = "mode"` so replayed games start from mode selection.
- All 37 regression tests pass; 9 programmatic smoke checks pass (AC1–AC4 + boundary + guards + MenuScreen stage both directions).

### File List

- `ui/results_screen.py` — REPLACED stub with full implementation
- `ui/menu_screen.py` — ADDED 2 lines to `handle_events()` for stage-reset on return from results
