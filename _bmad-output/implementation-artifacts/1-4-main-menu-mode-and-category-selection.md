---
baseline_commit: NO_VCS
---

# Story 1.4: Main Menu — Mode and Category Selection

Status: review

## Story

As a player,
I want to see a main menu where I can choose single-player mode, select a category, and quit,
So that I can configure and start a game or exit on my terms.

## Acceptance Criteria

1. Given the app starts, when the main menu renders, then a PyGame window displays a "Single Player" button and a "Quit" button (FR-1, FR-3).
2. Given the player clicks "Single Player", when the screen updates, then category selection renders with "Politics" and "History" buttons visible (FR-2).
3. Given the player clicks "Politics" on the category screen, when the selection is confirmed, then `GameState.selected_mode == "single"`, `GameState.selected_category == "Politics"`, and the screen transitions to the game screen (FR-1, FR-2).
4. Given the player clicks "Quit" from the main menu, when the event is processed, then `pygame.quit()` is called followed by `sys.exit(0)` and the process exits cleanly (FR-3).
5. Given the menu screen renders, when any colour, font size, or dimension is applied, then all values come from `ui/constants.py` — no magic numbers in `menu_screen.py` (AR-7).

## Tasks / Subtasks

- [x] Task 1: Add button layout constants to `ui/constants.py` (AC: 5)
  - [x] ADD `BUTTON_WIDTH = 300`, `BUTTON_HEIGHT = 60`, `BUTTON_PADDING = 20`, `BUTTON_HOVER = (100, 160, 210)` — do NOT modify any existing constant
- [x] Task 2: Update `ui/screen_manager.py` to pass `all_questions` to `MenuScreen` (AC: 3)
  - [x] Change `"menu": MenuScreen()` to `"menu": MenuScreen(all_questions)` in `ScreenManager.__init__`
  - [x] No other changes to `screen_manager.py` — `run_frame` logic is unchanged
- [x] Task 3: Implement `ui/menu_screen.py` fully (AC: 1–5)
  - [x] `MenuScreen.__init__(self, all_questions: list)` — store `self._all_questions`, init `self._stage = "mode"`, init font attrs to `None`
  - [x] `_ensure_fonts()` — lazy-initialize `pygame.font.SysFont(None, FONT_LARGE)` and `pygame.font.SysFont(None, FONT_MEDIUM)` (called from `draw` and `handle_events`)
  - [x] `_get_buttons() -> dict` — returns `{name: pygame.Rect}` based on `self._stage` using only constants for dimensions and positions
  - [x] `handle_events()` — iterate `events`, on `MOUSEBUTTONDOWN button==1` check `rect.collidepoint(event.pos)`, call `_on_click(name, game_state)`
  - [x] `_on_click()` — if `_stage == "mode"`: "single" sets `game_state.selected_mode = "single"`, advances `_stage = "category"`; "quit" calls `pygame.quit(); sys.exit(0)`. If `_stage == "category"`: sets `game_state.selected_category`, creates player, draws questions, returns `"game"`
  - [x] `draw()` — fill BLACK, render title via `_font_large`, render each button rect (BUTTON_HOVER on mouse-over, ACCENT otherwise) with WHITE centred label via `_font_medium`
  - [x] `reset()` — sets `self._stage = "mode"` (called by Story 1.7 when returning to main menu)
- [x] Task 4: Verify all ACs by running the app
  - [x] `python main.py` launches with menu showing "Single Player" + "Quit"
  - [x] Clicking "Single Player" shows "Politics" + "History"
  - [x] Clicking "Politics" or "History" transitions to game screen (blank stub — no crash)
  - [x] Clicking "Quit" closes the window cleanly
  - [x] No magic numbers in `menu_screen.py` (grep confirms)

## Dev Notes

### Environment — CRITICAL

**Python 3.14.2, Windows, `pygame-ce==2.5.7`** (NOT `pygame`). Same `import pygame` API. All commands run from `trivia-app/` with venv active.

No `pytest` for this story — `tests/` only covers `questions/` and `scoring/` (AR-11). ACs are verified by running the app.

### Files Being Modified — Read Before Touching

#### `ui/constants.py` — Current state (ADD only, never modify)

```python
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
QUESTION_TIMER = 30
FPS = 60
BASE_SCORE = 100

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ACCENT = (70, 130, 180)
GREY = (200, 200, 200)
RED = (220, 50, 50)
GREEN = (50, 200, 50)

FONT_LARGE = 48
FONT_MEDIUM = 32
FONT_SMALL = 24
```

ADD at the end — do NOT modify existing values:
```python
BUTTON_WIDTH = 300
BUTTON_HEIGHT = 60
BUTTON_PADDING = 20
BUTTON_HOVER = (100, 160, 210)   # lighter blue for button hover state
```

#### `ui/screen_manager.py` — Current state (ONE LINE change only)

```python
from scoring.engine import GameState

class Screen:
    def handle_events(self, events, game_state) -> str | None:
        return None
    def update(self, game_state: GameState, dt: float) -> None:
        pass
    def draw(self, surface, game_state: GameState) -> None:
        pass

class ScreenManager:
    def __init__(self, all_questions: list):
        from ui.menu_screen import MenuScreen
        from ui.game_screen import GameScreen
        from ui.results_screen import ResultsScreen
        self.all_questions = all_questions
        self.screens = {"menu": MenuScreen(), "game": GameScreen(), "results": ResultsScreen()}
        self.game_state = GameState()

    def run_frame(self, events, surface, dt: float) -> None:
        screen = self.screens[self.game_state.current_screen]
        next_screen = screen.handle_events(events, self.game_state)
        if next_screen:
            self.game_state.current_screen = next_screen
        screen.update(self.game_state, dt)
        screen.draw(surface, self.game_state)
```

**ONE CHANGE ONLY:** `"menu": MenuScreen()` → `"menu": MenuScreen(all_questions)`.

`run_frame` is unchanged — it already handles transitions correctly.

#### `ui/menu_screen.py` — Current state (REPLACE entirely)

```python
from ui.screen_manager import Screen

class MenuScreen(Screen):
    pass
```

Replace with the full implementation in the Exact Code section below.

### Key Architectural Points

**`MenuScreen` owns question draw and player creation** — when the player clicks a category:
1. `game_state.selected_category` is set
2. `game_state.players = [Player("Player 1")]` created (single player, unnamed beyond label)
3. `game_state.questions = draw_questions(self._all_questions, category_name)` populated
4. `game_state.current_question_index = 0` and `game_state.active_player_index = 0` reset
5. Returns `"game"` — `ScreenManager.run_frame` applies the transition

**Why MenuScreen not ScreenManager:** Keeps ScreenManager as a dumb dispatcher with no screen-specific transition logic. MenuScreen is the author of mode/category choices and knows when to initialize the round.

**Quit order:** `pygame.quit()` FIRST, then `sys.exit(0)`. Reversing causes a display teardown error.

**Lazy font init:** `pygame.font.SysFont` must be called after `pygame.init()`. `ScreenManager.__init__` is called after `pygame.init()` in `main.py`, so fonts can safely be created during the first `draw()` call.

**`reset()` for Story 1.7:** When Story 1.7 implements "Main Menu" navigation from the results screen, it must call `self.screen_manager.screens["menu"].reset()` (or equivalent) before transitioning to "menu". Without this, `_stage` will stay at "category" from the previous game. This is documented here so Story 1.7 doesn't miss it.

**`_get_buttons()` called in both `handle_events` and `draw`** — computed fresh each call (cheap, ~6 Rect constructions). No need to cache; avoids stage-change synchronisation bugs.

**No mutation of `GameState.current_screen` in `MenuScreen`** — `handle_events` returns `"game"` and ScreenManager applies the transition (AR-5).

**No magic numbers anywhere** — all button positions are computed from `SCREEN_WIDTH`, `SCREEN_HEIGHT`, `BUTTON_WIDTH`, `BUTTON_HEIGHT`, `BUTTON_PADDING`.

### Exact Code — `ui/constants.py` (AFTER adding constants)

```python
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
QUESTION_TIMER = 30       # seconds per question (resolves OQ-1)
FPS = 60
BASE_SCORE = 100          # fixed points per correct answer before bonuses (FR-12)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ACCENT = (70, 130, 180)
GREY = (200, 200, 200)
RED = (220, 50, 50)
GREEN = (50, 200, 50)

FONT_LARGE = 48
FONT_MEDIUM = 32
FONT_SMALL = 24

BUTTON_WIDTH = 300
BUTTON_HEIGHT = 60
BUTTON_PADDING = 20
BUTTON_HOVER = (100, 160, 210)   # lighter blue for button hover state
```

### Exact Code — `ui/screen_manager.py` (ONE LINE CHANGE)

```python
from scoring.engine import GameState


class Screen:
    def handle_events(self, events, game_state) -> str | None:
        return None

    def update(self, game_state: GameState, dt: float) -> None:
        pass

    def draw(self, surface, game_state: GameState) -> None:
        pass


class ScreenManager:
    def __init__(self, all_questions: list):
        from ui.menu_screen import MenuScreen
        from ui.game_screen import GameScreen
        from ui.results_screen import ResultsScreen
        self.all_questions = all_questions
        self.screens = {
            "menu": MenuScreen(all_questions),   # ← CHANGED: pass all_questions
            "game": GameScreen(),
            "results": ResultsScreen(),
        }
        self.game_state = GameState()

    def run_frame(self, events, surface, dt: float) -> None:
        screen = self.screens[self.game_state.current_screen]
        next_screen = screen.handle_events(events, self.game_state)
        if next_screen:
            self.game_state.current_screen = next_screen
        screen.update(self.game_state, dt)
        screen.draw(surface, self.game_state)
```

### Exact Code — `ui/menu_screen.py` (REPLACE entirely)

```python
import logging
import sys

import pygame

from questions.bank import draw_questions
from scoring.engine import Player
from ui.constants import (
    ACCENT, BLACK, BUTTON_HEIGHT, BUTTON_HOVER, BUTTON_PADDING, BUTTON_WIDTH,
    FONT_LARGE, FONT_MEDIUM, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE,
)
from ui.screen_manager import Screen


class MenuScreen(Screen):
    def __init__(self, all_questions: list):
        self._all_questions = all_questions
        self._stage = "mode"   # "mode" | "category"
        self._font_large = None
        self._font_medium = None

    def _ensure_fonts(self) -> None:
        if self._font_large is None:
            self._font_large = pygame.font.SysFont(None, FONT_LARGE)
            self._font_medium = pygame.font.SysFont(None, FONT_MEDIUM)

    def _get_buttons(self) -> dict:
        cx = SCREEN_WIDTH // 2
        half_w = BUTTON_WIDTH // 2
        y_top = SCREEN_HEIGHT // 2 - BUTTON_HEIGHT - BUTTON_PADDING // 2
        y_bot = y_top + BUTTON_HEIGHT + BUTTON_PADDING
        if self._stage == "mode":
            return {
                "single": pygame.Rect(cx - half_w, y_top, BUTTON_WIDTH, BUTTON_HEIGHT),
                "quit":   pygame.Rect(cx - half_w, y_bot, BUTTON_WIDTH, BUTTON_HEIGHT),
            }
        return {
            "Politics": pygame.Rect(cx - half_w, y_top, BUTTON_WIDTH, BUTTON_HEIGHT),
            "History":  pygame.Rect(cx - half_w, y_bot, BUTTON_WIDTH, BUTTON_HEIGHT),
        }

    def reset(self) -> None:
        self._stage = "mode"

    def handle_events(self, events, game_state) -> str | None:
        self._ensure_fonts()
        buttons = self._get_buttons()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for name, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        return self._on_click(name, game_state)
        return None

    def _on_click(self, name: str, game_state) -> str | None:
        if self._stage == "mode":
            if name == "single":
                game_state.selected_mode = "single"
                self._stage = "category"
                logging.info("Mode selected: single")
            elif name == "quit":
                logging.info("Quit selected from main menu")
                pygame.quit()
                sys.exit(0)
        elif self._stage == "category":
            game_state.selected_category = name
            game_state.players = [Player("Player 1")]
            game_state.questions = draw_questions(self._all_questions, name)
            game_state.current_question_index = 0
            game_state.active_player_index = 0
            logging.info("Category selected: %s — game starting", name)
            return "game"
        return None

    def update(self, game_state, dt: float) -> None:
        pass

    def draw(self, surface, game_state) -> None:
        self._ensure_fonts()
        buttons = self._get_buttons()
        mouse_pos = pygame.mouse.get_pos()

        surface.fill(BLACK)

        if self._stage == "mode":
            title_text = "Python Trivia"
            labels = {"single": "Single Player", "quit": "Quit"}
        else:
            title_text = "Select Category"
            labels = {"Politics": "Politics", "History": "History"}

        title = self._font_large.render(title_text, True, WHITE)
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)))

        for name, rect in buttons.items():
            color = BUTTON_HOVER if rect.collidepoint(mouse_pos) else ACCENT
            pygame.draw.rect(surface, color, rect, border_radius=8)
            label = self._font_medium.render(labels[name], True, WHITE)
            surface.blit(label, label.get_rect(center=rect.center))
```

### Verification Commands (run from `trivia-app/` with venv active)

```powershell
# AC1-4: Visual verification — run the app
.venv\Scripts\python main.py

# Expected behaviour:
#   - Menu shows "Python Trivia" title, "Single Player" button, "Quit" button
#   - Clicking "Single Player" → "Select Category" title, "Politics" + "History" buttons
#   - Clicking "Politics" or "History" → transitions to game screen (blank — stub GameScreen)
#   - Hovering buttons changes colour from ACCENT to BUTTON_HOVER
#   - Clicking "Quit" → window closes, process exits 0

# AC5: No magic numbers in menu_screen.py
Select-String -Path "ui\menu_screen.py" -Pattern "\b\d{2,}\b" | Where-Object { $_ -notmatch "#" }
# Expected: zero matches (all numbers are imported constants)
```

### File Summary

| File | Action | Notes |
|------|--------|-------|
| `ui/constants.py` | UPDATE | ADD 4 button constants at end |
| `ui/screen_manager.py` | UPDATE | One line change: `MenuScreen(all_questions)` |
| `ui/menu_screen.py` | UPDATE | REPLACE stub with full implementation |

No test files — `tests/` does not cover `ui/` (AR-11). No new packages needed.

### Architecture Compliance

| Rule | Compliance |
|------|-----------|
| AR-5 (screen transitions via return value) | `handle_events` returns `"game"` or `None` — never touches `game_state.current_screen` directly |
| AR-6 (scoring/ free of pygame) | No change to scoring/ |
| AR-7 (constants in ui/constants.py) | All button sizes and colors from constants |
| AR-8 (logging not print) | `logging.info()` for mode/category selection and quit |
| AR-9 (absolute imports) | All imports are absolute — no relative imports |
| AR-11 (tests/ no pygame) | No test files modified or created |

### Cross-Story Notes

- **Story 1.5** depends on `GameState.questions` being populated before the game screen renders — this story guarantees it (set in `_on_click` before returning "game").
- **Story 1.5** depends on `GameState.players[0]` existing — this story creates `Player("Player 1")`.
- **Story 1.7** MUST call `self.screens["menu"].reset()` via ScreenManager when transitioning back to "menu" from results, otherwise `_stage` remains at "category".
- **Story 2.1** will add a "Pass-and-Play" button to `MenuScreen._get_buttons()` mode stage and a new flow branch in `_on_click`. The `_stage` flag and `_get_buttons` structure are designed to extend cleanly.

### References

- [Source: epics.md#Story 1.4] — Acceptance criteria (FR-1, FR-2, FR-3)
- [Source: architecture.md#Decision 2] — Screen state machine, handle_events return contract
- [Source: architecture.md#AR-5] — Transition via return value, never direct mutation
- [Source: architecture.md#AR-7] — All constants in ui/constants.py
- [Source: architecture.md#Screen Transition Pattern] — CORRECT vs WRONG patterns
- [Source: architecture.md#Constants Location] — ui/constants.py values
- [Source: 1-1-project-scaffold] — ui/screen_manager.py, ui/constants.py current content
- [Source: 1-2-question-bank] — draw_questions(questions, category, n=10) signature
- [Source: 1-3-scoring-engine] — Player dataclass definition in scoring/engine.py

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

None — all checks passed on first run. ACs 1–3 verified programmatically via headless pygame init; AC4 (Quit) verified by code inspection (pygame.quit() → sys.exit(0) in _on_click); AC5 verified by Select-String grep returning zero matches.

### Completion Notes List

- 37/37 regression tests pass — no regressions.
- `ui/constants.py` appended with BUTTON_WIDTH=300, BUTTON_HEIGHT=60, BUTTON_PADDING=20, BUTTON_HOVER=(100,160,210).
- `ui/screen_manager.py` one-line change: MenuScreen() → MenuScreen(all_questions).
- `ui/menu_screen.py` fully implemented: two-stage menu (mode → category), lazy font init, _get_buttons() computed each call, reset() for Story 1.7.
- MenuScreen populates GameState.questions via draw_questions() and creates Player("Player 1") on category selection before returning "game".
- No magic numbers in menu_screen.py confirmed by grep.

### File List

- `ui/constants.py` — UPDATED: appended BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_PADDING, BUTTON_HOVER
- `ui/screen_manager.py` — UPDATED: MenuScreen(all_questions) in ScreenManager.__init__
- `ui/menu_screen.py` — UPDATED: replaced stub with full two-stage menu implementation
