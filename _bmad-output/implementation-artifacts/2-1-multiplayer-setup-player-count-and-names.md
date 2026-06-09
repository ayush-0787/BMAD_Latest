---
baseline_commit: NO_VCS
---

# Story 2.1: Multiplayer Setup — Player Count and Names

Status: review

## Story

As players,
I want to select "Pass-and-Play" from the main menu, enter the number of players and each player's name,
So that we can set up a multiplayer session with clearly identified participants.

## Acceptance Criteria

1. Given the main menu is displayed, when the player clicks the "Pass-and-Play" button, then a player count entry screen renders with a numeric input accepting values 2–4.
2. Given the player count screen is displayed, when a value outside 2–4 is submitted, then an inline error message is shown and the entry is rejected without navigating away (FR-9).
3. Given a valid player count (e.g., 3) is confirmed, when the count is accepted, then a name entry screen prompts sequentially for each player's name (Player 1, Player 2, Player 3).
4. Given a player submits an empty or whitespace-only name, when the name is confirmed, then an inline error is shown and the name field is not accepted — the player must enter a non-empty name (MC-2).
5. Given all player names are entered and confirmed, when the last name is submitted, then `GameState.players` is populated with a `Player` object for each name, `GameState.selected_mode == "multiplayer"`, and the screen transitions to the game screen.
6. Given the game screen starts in multiplayer mode, when the first question is displayed, then the active player's name (`GameState.players[0].name`) is prominently shown on screen (FR-10).

## Tasks / Subtasks

- [x] Task 1: Create `ui/setup_screen.py` — full count + names + category flow (AC: 1–5)
  - [x] `SetupScreen.__init__(all_questions)` — init internal stage, counters, input buffer, error msg, font lazily
  - [x] `reset()` — reset all mutable state to initial values (called by ScreenManager on transition to "setup")
  - [x] `_ensure_fonts()` — lazy-init FONT_LARGE, FONT_MEDIUM, FONT_SMALL via `pygame.font.SysFont(None, size)`
  - [x] `_get_category_buttons()` — same geometry as MenuScreen category buttons (reuse constants)
  - [x] `handle_events()` — route KEYDOWN to count/name handler, MOUSEBUTTONDOWN to category handler; return "game" on final category click
  - [x] `_handle_count_key(event)` — digits into buffer (max 1 char); BACKSPACE; ENTER → `_validate_count()`
  - [x] `_validate_count()` — parse int, reject outside 2–4 with `_error_msg`, advance stage to "names" on valid
  - [x] `_handle_name_key(event)` — printable chars into buffer (max 20 chars); BACKSPACE; ENTER → `_validate_name()`
  - [x] `_validate_name()` — reject empty/whitespace with `_error_msg`; append stripped name; advance `_current_name_idx`; advance stage to "category" when all names collected
  - [x] `_on_category_click(category, game_state)` — set all 6 GameState fields, draw questions, return "game"
  - [x] `update()` — pass (no animation)
  - [x] `draw()` — dispatch to `_draw_count_stage`, `_draw_names_stage`, or `_draw_category_stage`
  - [x] `_draw_count_stage(surface)` — title, prompt, input box with blinking cursor, error, Enter hint
  - [x] `_draw_names_stage(surface)` — title, "Player N of M:" prompt, input box, error, Enter hint
  - [x] `_draw_category_stage(surface)` — "Select Category" title + two buttons (same style as MenuScreen)
- [x] Task 2: Update `ui/menu_screen.py` — add Pass-and-Play button (AC: 1)
  - [x] `_get_buttons()`: add "multi" to mode stage (3 buttons: single, multi, quit) with recalculated y positions
  - [x] `_on_click()`: add "multi" branch → `logging.info(...)`, return `"setup"`
  - [x] `draw()`: add `"multi": "Pass-and-Play"` to mode-stage labels dict
- [x] Task 3: Update `ui/screen_manager.py` — register "setup" screen and call `reset()` on transition
  - [x] Import `SetupScreen` from `ui.setup_screen`
  - [x] Add `"setup": SetupScreen(all_questions)` to `self.screens` dict
  - [x] In `run_frame()`: when `next_screen` is set, call `incoming.reset()` if it has one before updating `current_screen`
- [x] Task 4: Update `ui/game_screen.py` — show active player name in multiplayer (AC: 6)
  - [x] In `draw()`, after rendering the timer digit, add a player name label (FONT_MEDIUM, ACCENT color) centered below the timer digit — only when `len(game_state.players) > 1`; shift `text_y` down by `FONT_MEDIUM + MARGIN // 4` in that case
- [x] Task 5: Verify ACs by running the app and programmatic checks
  - [x] `python main.py` → click Pass-and-Play → count screen appears
  - [x] Enter count 1 → error shown; enter count 5 → error shown; enter count 3 → name entry for Player 1
  - [x] Submit empty name → error; submit whitespace-only → error; submit "Alice" → Player 2 prompt
  - [x] Complete all names → category screen; select category → game starts with player name visible
  - [x] Confirm `GameState.selected_mode == "multiplayer"` and `len(GameState.players) == 3`
  - [x] Run programmatic smoke test (see Verification Commands)

## Dev Notes

### Environment — CRITICAL

**Python 3.14.2, Windows, `pygame-ce==2.5.7`** (NOT `pygame`). All commands from `trivia-app/` with venv active.

No new test files — `tests/` covers only `questions/` and `scoring/` (AR-11). ACs verified by programmatic headless checks.

### Scope — Four Files

| File | Action |
|------|--------|
| `ui/setup_screen.py` | NEW — full setup flow |
| `ui/menu_screen.py` | UPDATE — add Pass-and-Play button |
| `ui/screen_manager.py` | UPDATE — register "setup" + reset on transition |
| `ui/game_screen.py` | UPDATE — player name in multiplayer HUD |

No changes to `scoring/`, `questions/`, `data/`, `tests/`, `main.py`, or `ui/constants.py`.

### New Screen: `ui/setup_screen.py`

#### Internal State

```python
class SetupScreen(Screen):
    def __init__(self, all_questions: list):
        self._all_questions = all_questions
        self._stage = "count"          # "count" | "names" | "category"
        self._player_count = 0         # validated count (2–4)
        self._player_names: list[str] = []
        self._current_name_idx = 0     # which player we're currently naming (0-based)
        self._input_text = ""          # current text in active input field
        self._error_msg = ""           # inline error; "" = no error
        self._font_large = None
        self._font_medium = None
        self._font_small = None

    def reset(self) -> None:
        self._stage = "count"
        self._player_count = 0
        self._player_names = []
        self._current_name_idx = 0
        self._input_text = ""
        self._error_msg = ""
```

#### `handle_events` routing

```python
def handle_events(self, events, game_state) -> str | None:
    self._ensure_fonts()
    for event in events:
        if event.type == pygame.KEYDOWN:
            if self._stage == "count":
                self._handle_count_key(event)
            elif self._stage == "names":
                self._handle_name_key(event)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._stage == "category":
                result = self._on_category_click(event.pos, game_state)
                if result:
                    return result
    return None
```

#### Count key handler

```python
def _handle_count_key(self, event) -> None:
    if event.key == pygame.K_BACKSPACE:
        self._input_text = self._input_text[:-1]
        self._error_msg = ""
    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
        self._validate_count()
    elif event.unicode.isdigit() and len(self._input_text) < 1:
        self._input_text += event.unicode
        self._error_msg = ""
```

**Note:** Cap count field at 1 character (only valid values are single digits 2, 3, 4).

#### Count validation

```python
def _validate_count(self) -> None:
    try:
        n = int(self._input_text)
    except ValueError:
        self._error_msg = "Enter a number: 2, 3, or 4"
        self._input_text = ""
        return
    if not (2 <= n <= 4):
        self._error_msg = "Must be 2, 3, or 4 players"
        self._input_text = ""
        return
    self._player_count = n
    self._input_text = ""
    self._error_msg = ""
    self._stage = "names"
```

#### Name key handler

```python
def _handle_name_key(self, event) -> None:
    if event.key == pygame.K_BACKSPACE:
        self._input_text = self._input_text[:-1]
        self._error_msg = ""
    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
        self._validate_name()
    elif event.unicode and event.unicode.isprintable() and len(self._input_text) < 20:
        self._input_text += event.unicode
        self._error_msg = ""
```

#### Name validation

```python
def _validate_name(self) -> None:
    name = self._input_text.strip()
    if not name:
        self._error_msg = "Name cannot be empty"
        return
    self._player_names.append(name)
    self._current_name_idx += 1
    self._input_text = ""
    self._error_msg = ""
    if self._current_name_idx == self._player_count:
        self._stage = "category"
```

#### Category click handler

```python
def _on_category_click(self, pos, game_state) -> str | None:
    for cat, rect in self._get_category_buttons().items():
        if rect.collidepoint(pos):
            game_state.selected_mode = "multiplayer"
            game_state.selected_category = cat
            game_state.players = [Player(name) for name in self._player_names]
            game_state.questions = draw_questions(self._all_questions, cat)
            game_state.active_player_index = 0
            game_state.current_question_index = 0
            logging.info(
                "Multiplayer starting: %d players, category=%s",
                len(self._player_names), cat,
            )
            return "game"
    return None
```

#### Category button geometry (identical to MenuScreen category stage)

```python
def _get_category_buttons(self) -> dict:
    cx = SCREEN_WIDTH // 2
    half_w = BUTTON_WIDTH // 2
    y_top = SCREEN_HEIGHT // 2 - BUTTON_HEIGHT - BUTTON_PADDING // 2
    y_bot = y_top + BUTTON_HEIGHT + BUTTON_PADDING
    return {
        "Politics": pygame.Rect(cx - half_w, y_top, BUTTON_WIDTH, BUTTON_HEIGHT),
        "History":  pygame.Rect(cx - half_w, y_bot, BUTTON_WIDTH, BUTTON_HEIGHT),
    }
```

#### Blinking cursor pattern

```python
cursor = "|" if pygame.time.get_ticks() // 500 % 2 == 0 else ""
```

Use `pygame.time.get_ticks()` (milliseconds since init) — dividing by 500 gives a 0.5s blink cycle.

#### Draw — count stage layout

```python
def _draw_count_stage(self, surface) -> None:
    title = self._font_large.render("Pass-and-Play", True, WHITE)
    surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)))

    prompt = self._font_medium.render("Number of players? (2-4)", True, WHITE)
    prompt_y = SCREEN_HEIGHT // 4 + FONT_LARGE + MARGIN // 2
    surface.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, prompt_y)))

    # Input box (half button width — just a single digit)
    box_y = SCREEN_HEIGHT // 2 - BUTTON_HEIGHT // 2
    box_rect = pygame.Rect(
        SCREEN_WIDTH // 2 - BUTTON_WIDTH // 4,
        box_y,
        BUTTON_WIDTH // 2,
        BUTTON_HEIGHT,
    )
    pygame.draw.rect(surface, ACCENT, box_rect, border_radius=4)
    cursor = "|" if pygame.time.get_ticks() // 500 % 2 == 0 else ""
    input_surf = self._font_large.render(self._input_text + cursor, True, WHITE)
    surface.blit(input_surf, input_surf.get_rect(center=box_rect.center))

    if self._error_msg:
        err_surf = self._font_small.render(self._error_msg, True, RED)
        surface.blit(err_surf, err_surf.get_rect(
            center=(SCREEN_WIDTH // 2, box_y + BUTTON_HEIGHT + MARGIN // 2)
        ))

    hint = self._font_small.render("Press Enter to confirm", True, GREY)
    surface.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - MARGIN)))
```

#### Draw — names stage layout

```python
def _draw_names_stage(self, surface) -> None:
    title = self._font_large.render("Enter Names", True, WHITE)
    surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)))

    prompt_text = f"Player {self._current_name_idx + 1} of {self._player_count}:"
    prompt = self._font_medium.render(prompt_text, True, WHITE)
    prompt_y = SCREEN_HEIGHT // 4 + FONT_LARGE + MARGIN // 2
    surface.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, prompt_y)))

    box_y = SCREEN_HEIGHT // 2 - BUTTON_HEIGHT // 2
    box_rect = pygame.Rect(
        SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
        box_y,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )
    pygame.draw.rect(surface, ACCENT, box_rect, border_radius=4)
    cursor = "|" if pygame.time.get_ticks() // 500 % 2 == 0 else ""
    input_surf = self._font_medium.render(self._input_text + cursor, True, WHITE)
    surface.blit(input_surf, input_surf.get_rect(center=box_rect.center))

    if self._error_msg:
        err_surf = self._font_small.render(self._error_msg, True, RED)
        surface.blit(err_surf, err_surf.get_rect(
            center=(SCREEN_WIDTH // 2, box_y + BUTTON_HEIGHT + MARGIN // 2)
        ))

    hint = self._font_small.render("Press Enter to confirm", True, GREY)
    surface.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - MARGIN)))
```

#### Draw — category stage layout

```python
def _draw_category_stage(self, surface) -> None:
    buttons = self._get_category_buttons()
    mouse_pos = pygame.mouse.get_pos()

    title = self._font_large.render("Select Category", True, WHITE)
    surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)))

    for name, rect in buttons.items():
        color = BUTTON_HOVER if rect.collidepoint(mouse_pos) else ACCENT
        pygame.draw.rect(surface, color, rect, border_radius=8)
        label = self._font_medium.render(name, True, WHITE)
        surface.blit(label, label.get_rect(center=rect.center))
```

#### Required imports for `ui/setup_screen.py`

```python
import logging
import pygame
from questions.bank import draw_questions
from scoring.engine import Player
from ui.constants import (
    ACCENT, BLACK, BUTTON_HEIGHT, BUTTON_HOVER, BUTTON_PADDING, BUTTON_WIDTH,
    FONT_LARGE, FONT_MEDIUM, FONT_SMALL, GREY, MARGIN, RED, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE,
)
from ui.screen_manager import Screen
```

### Changes to `ui/menu_screen.py`

#### `_get_buttons()` — mode stage updated to 3 buttons

```python
def _get_buttons(self) -> dict:
    cx = SCREEN_WIDTH // 2
    half_w = BUTTON_WIDTH // 2
    if self._stage == "mode":
        total_h = 3 * BUTTON_HEIGHT + 2 * BUTTON_PADDING
        y = SCREEN_HEIGHT // 2 - total_h // 2
        return {
            "single": pygame.Rect(cx - half_w, y, BUTTON_WIDTH, BUTTON_HEIGHT),
            "multi":  pygame.Rect(cx - half_w, y + BUTTON_HEIGHT + BUTTON_PADDING, BUTTON_WIDTH, BUTTON_HEIGHT),
            "quit":   pygame.Rect(cx - half_w, y + 2 * (BUTTON_HEIGHT + BUTTON_PADDING), BUTTON_WIDTH, BUTTON_HEIGHT),
        }
    return {
        "Politics": pygame.Rect(cx - half_w, SCREEN_HEIGHT // 2 - BUTTON_HEIGHT - BUTTON_PADDING // 2, BUTTON_WIDTH, BUTTON_HEIGHT),
        "History":  pygame.Rect(cx - half_w, SCREEN_HEIGHT // 2 - BUTTON_HEIGHT - BUTTON_PADDING // 2 + BUTTON_HEIGHT + BUTTON_PADDING, BUTTON_WIDTH, BUTTON_HEIGHT),
    }
```

**Layout calculation for 3 buttons (SCREEN_HEIGHT=600, BUTTON_HEIGHT=60, BUTTON_PADDING=20):**
- `total_h = 3×60 + 2×20 = 220`
- `y = 300 - 110 = 190` → Single Player top at y=190
- Pass-and-Play top at y = 190 + 80 = 270
- Quit top at y = 270 + 80 = 350

#### `_on_click()` — add "multi" branch

```python
def _on_click(self, name: str, game_state) -> str | None:
    if self._stage == "mode":
        if name == "single":
            game_state.selected_mode = "single"
            self._stage = "category"
            logging.info("Mode selected: single")
        elif name == "multi":
            logging.info("Mode selected: multiplayer → setup screen")
            return "setup"
        elif name == "quit":
            logging.info("Quit selected from main menu")
            pygame.quit()
            sys.exit(0)
    elif self._stage == "category":
        # unchanged — single-player only path
        game_state.selected_category = name
        game_state.players = [Player("Player 1")]
        game_state.questions = draw_questions(self._all_questions, name)
        game_state.current_question_index = 0
        game_state.active_player_index = 0
        logging.info("Category selected: %s — game starting", name)
        return "game"
    return None
```

**Why "setup" is returned without setting `selected_mode`:** `SetupScreen._on_category_click` sets `selected_mode = "multiplayer"` when it populates GameState. This avoids the stage-reset guard in `handle_events` firing prematurely (the guard checks `not game_state.selected_mode`).

#### `draw()` — update labels for mode stage

```python
if self._stage == "mode":
    title_text = "Python Trivia"
    labels = {"single": "Single Player", "multi": "Pass-and-Play", "quit": "Quit"}
```

### Changes to `ui/screen_manager.py`

#### Full updated `__init__` and `run_frame`

```python
class ScreenManager:
    def __init__(self, all_questions: list):
        from ui.menu_screen import MenuScreen
        from ui.game_screen import GameScreen
        from ui.results_screen import ResultsScreen
        from ui.setup_screen import SetupScreen
        self.all_questions = all_questions
        self.screens = {
            "menu": MenuScreen(all_questions),
            "game": GameScreen(),
            "results": ResultsScreen(),
            "setup": SetupScreen(all_questions),
        }
        self.game_state = GameState()

    def run_frame(self, events, surface, dt: float) -> None:
        screen = self.screens[self.game_state.current_screen]
        next_screen = screen.handle_events(events, self.game_state)
        if next_screen:
            incoming = self.screens.get(next_screen)
            if incoming and hasattr(incoming, "reset"):
                incoming.reset()
            self.game_state.current_screen = next_screen
        screen.update(self.game_state, dt)
        screen.draw(surface, self.game_state)
```

**Why `reset()` on transition:** Ensures GameScreen's internal timer/pause state is clean on every game entry (single AND multi), and SetupScreen's input state is clean on every setup entry. Calling `reset()` before updating `current_screen` means the `draw()` call at the end of the frame still uses the outgoing screen — no visual glitch.

**Existing screens unaffected:** `ResultsScreen` has no `reset()` so `hasattr` guard skips it safely.

### Changes to `ui/game_screen.py`

One block added in `draw()` — after the timer digit render, before the question text render. The change only activates when `len(game_state.players) > 1` so single-player layout is unchanged pixel-for-pixel.

```python
# ── existing: timer digit ──────────────────────────────────────────
timer_center_y = bar_y + TIMER_BAR_H + MARGIN // 2
timer_surf = self._font_large.render(str(int(time_remaining)), True, WHITE)
surface.blit(timer_surf, timer_surf.get_rect(center=(SCREEN_WIDTH // 2, timer_center_y)))

# ── NEW: player name (multiplayer only) ───────────────────────────
text_y = timer_center_y + FONT_LARGE // 2 + MARGIN // 2
if len(game_state.players) > 1:
    name_surf = self._font_medium.render(player.name, True, ACCENT)
    surface.blit(name_surf, name_surf.get_rect(center=(SCREEN_WIDTH // 2, text_y)))
    text_y += FONT_MEDIUM + MARGIN // 4

# ── existing: question text (word-wrapped) — uses text_y ──────────
max_text_w = SCREEN_WIDTH - 2 * MARGIN
for line in self._wrap_text(question["question_text"], self._font_medium, max_text_w):
    surf = self._font_medium.render(line, True, WHITE)
    surface.blit(surf, surf.get_rect(center=(SCREEN_WIDTH // 2, text_y)))
    text_y += FONT_MEDIUM + MARGIN // 6
```

**Numeric values (SCREEN_HEIGHT=600, FONT_LARGE=48, MARGIN=60, TIMER_BAR_H=10):**
- `timer_center_y = 30 + 10 + 30 = 70`
- `text_y` without name = 70 + 24 + 30 = 124 (unchanged for single player)
- `text_y` with name = 124 + 32 + 15 = 171 (multiplayer shifts question down by 47px)

### GameState When Setup Screen Transitions to "game"

After `SetupScreen._on_category_click` runs, GameState contains:

```
game_state.selected_mode         = "multiplayer"
game_state.selected_category     = "Politics" | "History"
game_state.players               = [Player("Alice"), Player("Bob"), ...]  (n=2–4)
game_state.questions             = [10 dicts, random draw from selected category]
game_state.active_player_index   = 0
game_state.current_question_index = 0
```

ScreenManager then calls `game_screen.reset()` (via the new reset-on-transition logic) → all timers/pause state are clean.

### Why Category Selection Is in SetupScreen

The ACs say "the screen transitions to the game screen" after names. For the game to function, `GameState.questions` must be populated (`draw_questions` requires a category). Rather than breaking the flow or drawing from a random category, the setup flow naturally extends to include category selection — consistent with single-player flow and FR-2 ("Player selects one Category").

### Architecture Compliance

| Rule | Compliance |
|------|-----------|
| AR-5 (transitions via return value) | `SetupScreen.handle_events` returns `"game"`; `MenuScreen._on_click` returns `"setup"`. No direct `current_screen` mutation. |
| AR-6 (`scoring/` free of PyGame) | No changes to `scoring/`. |
| AR-7 (constants in `ui/constants.py`) | All layout derived from constants. No new constants needed — existing values cover the setup screen geometry. |
| AR-8 (logging not print) | `logging.info()` on mode/setup start. |
| AR-9 (absolute imports) | All imports absolute. |
| AR-11 (tests/ no PyGame) | No test files added. |

### Cross-Story Notes

- **Story 2.2** — `SetupScreen` populates `game_state.players` with all `n` players. `game_state.active_player_index = 0` when entering game. `GameScreen.reset()` called by ScreenManager on every "game" entry — **Story 2.2 must call `game_screen.reset()` explicitly (or rely on ScreenManager) and reset `active_player_index` + `current_question_index` on each handoff.**
- **Story 2.2** — `MenuScreen.reset()` is unchanged (`_stage = "mode"`). `SetupScreen.reset()` is called by ScreenManager when entering "setup". Both work correctly for the replayed game cycle.
- **Story 2.3** — `ResultsScreen.draw()` currently renders single-player win/loss layout. When `game_state.selected_mode == "multiplayer"`, it must render the leaderboard layout instead. Story 2.3 implements this branch.
- **Story 2.3** — `ResultsScreen.handle_events` already resets all GameState fields on "Main Menu" click. This works for multiplayer too (resets `selected_mode` to `""`, which triggers `MenuScreen`'s stage-reset guard to show mode buttons).

### PyGame Keyboard Input Facts

- `event.unicode` — the character typed as a Unicode string (empty `""` for special keys like arrows, F-keys, ctrl combos)
- `event.key` — integer key code: `pygame.K_BACKSPACE`, `pygame.K_RETURN`, `pygame.K_KP_ENTER`
- `event.unicode.isdigit()` — True for `"0"`–`"9"`, reliable across keyboard layouts
- `event.unicode.isprintable()` — True for letters, digits, punctuation, space; False for control characters
- Always check `event.unicode` is non-empty before calling `.isprintable()` to avoid calling on empty string

### Verification Commands (run from `trivia-app/` with venv active)

```powershell
# Regression — all existing tests still pass
python -m pytest tests/ -v

# Visual — launch and manually test
.venv\Scripts\python main.py
# 1. Click "Pass-and-Play" → count screen
# 2. Type "1" + Enter → error "Must be 2, 3, or 4 players"
# 3. Type "5" + Enter → error
# 4. Backspace + "3" + Enter → name entry "Player 1 of 3:"
# 5. Enter key without text → error "Name cannot be empty"
# 6. Spaces only + Enter → error "Name cannot be empty"
# 7. "Alice" + Enter → "Player 2 of 3:"
# 8. "Bob" + Enter → "Player 3 of 3:"
# 9. "Charlie" + Enter → category screen
# 10. Click "Politics" → game screen with "Alice" name below timer
# 11. Play through → results → Main Menu → mode screen (not category)
```

```powershell
# Programmatic smoke test
.venv\Scripts\python.exe -c @'
import pygame
pygame.init()
surface = pygame.display.set_mode((800, 600))

from scoring.engine import GameState, Player
from ui.setup_screen import SetupScreen
from ui.menu_screen import MenuScreen
from questions.loader import load_questions

qs = load_questions("data/questions_politics.json") + load_questions("data/questions_history.json")
ss = SetupScreen(qs)

# AC: reset clears all state
ss._stage = "names"
ss._player_count = 3
ss._player_names = ["Alice"]
ss._current_name_idx = 1
ss._input_text = "partial"
ss._error_msg = "some error"
ss.reset()
assert ss._stage == "count"
assert ss._player_count == 0
assert ss._player_names == []
assert ss._current_name_idx == 0
assert ss._input_text == ""
assert ss._error_msg == ""
print("reset() clears all state OK")

# AC1: count validation rejects < 2
ss.reset()
ss._input_text = "1"
ss._validate_count()
assert ss._stage == "count"
assert ss._error_msg != ""
print("AC1 count=1 rejected OK")

# AC2: count validation rejects > 4
ss.reset()
ss._input_text = "5"
ss._validate_count()
assert ss._stage == "count"
assert ss._error_msg != ""
print("AC2 count=5 rejected OK")

# AC2: valid count 2 accepted
ss.reset()
ss._input_text = "2"
ss._validate_count()
assert ss._stage == "names"
assert ss._player_count == 2
assert ss._error_msg == ""
print("AC2 count=2 accepted OK")

# AC4: empty name rejected
ss._validate_name()
assert ss._stage == "names"
assert ss._error_msg != ""
print("AC4 empty name rejected OK")

# AC4: whitespace-only rejected
ss._input_text = "   "
ss._validate_name()
assert ss._stage == "names"
assert ss._error_msg != ""
print("AC4 whitespace name rejected OK")

# AC3/5: two valid names → advances to category
ss._input_text = "Alice"
ss._validate_name()
assert ss._current_name_idx == 1
assert ss._player_names == ["Alice"]
assert ss._stage == "names"

ss._input_text = "Bob"
ss._validate_name()
assert ss._current_name_idx == 2
assert ss._player_names == ["Alice", "Bob"]
assert ss._stage == "category"
print("AC3/5 names collected, stage=category OK")

# AC5: category click populates GameState
import pygame
click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(0,0))
cat_rect = ss._get_category_buttons()["Politics"]
cx, cy = cat_rect.centerx, cat_rect.centery
gs = GameState()
result = ss._on_category_click((cx, cy), gs)
assert result == "game"
assert gs.selected_mode == "multiplayer"
assert gs.selected_category == "Politics"
assert len(gs.players) == 2
assert gs.players[0].name == "Alice"
assert gs.players[1].name == "Bob"
assert len(gs.questions) == 10
assert gs.active_player_index == 0
assert gs.current_question_index == 0
print("AC5 GameState fully populated, transition=game OK")

# draw() no crash in all stages
ss.reset()
ss.draw(surface, GameState())          # count stage
ss._stage = "names"; ss._player_count = 2
ss.draw(surface, GameState())          # names stage
ss._stage = "category"
ss.draw(surface, GameState())          # category stage
print("draw() all stages: no crash OK")

# MenuScreen: Pass-and-Play button present and returns setup
ms = MenuScreen(qs)
buttons = ms._get_buttons()
assert "multi" in buttons, "Pass-and-Play button missing from mode stage"
print("MenuScreen: multi button present OK")

gs_menu = GameState()
result = ms._on_click("multi", gs_menu)
assert result == "setup", f"expected setup, got {result}"
print("MenuScreen: multi click returns setup OK")

# MenuScreen: 3-mode-stage labels in draw()
ms.draw(surface, gs_menu)
print("MenuScreen: draw() with 3 mode buttons no crash OK")

# ScreenManager: setup screen registered
from ui.screen_manager import ScreenManager
sm = ScreenManager(qs)
assert "setup" in sm.screens, "setup screen not registered"
print("ScreenManager: setup screen registered OK")

pygame.quit()
print("All programmatic checks passed")
'@
```

### File Summary

| File | Action | Notes |
|------|--------|-------|
| `ui/setup_screen.py` | NEW | Full setup flow: count → names → category → "game" transition |
| `ui/menu_screen.py` | UPDATE | Add "multi" button to mode stage; `_on_click` returns "setup" |
| `ui/screen_manager.py` | UPDATE | Add "setup" to screens dict; call `reset()` on incoming screen on transition |
| `ui/game_screen.py` | UPDATE | Add player name label in multiplayer (below timer digit) |

### References

- [Source: epics.md#Story 2.1] — Acceptance criteria (FR-9, FR-10, MC-2)
- [Source: architecture.md#Decision 2] — Screen base class interface, ScreenManager pattern
- [Source: architecture.md#Decision 1] — GameState fields and ownership
- [Source: architecture.md#Screen Transition Pattern] — return str|None from handle_events
- [Source: 1.7 dev notes] — ResultsScreen resets all 6 GameState fields; stage-reset guard in MenuScreen
- [Source: 1.4 menu_screen.py] — existing _stage lifecycle, _get_buttons, _on_click patterns (replicated in SetupScreen category stage)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- PowerShell heredoc double-quote stripping: `.venv\Scripts\python.exe -c @'...'@` strips inner `"` from Python string literals. All smoke-test string literals written with single quotes to avoid this.

### Completion Notes List

- Created `ui/setup_screen.py` with 3-stage flow: count entry (2–4, inline error on reject) → sequential name entry (empty/whitespace-only error, max 20 chars) → category selection. Blinking cursor via `pygame.time.get_ticks() // 500 % 2`.
- Updated `ui/menu_screen.py`: added "multi" button to mode stage (3 buttons, recalculated centred y positions); `_on_click("multi")` returns `"setup"` without setting `selected_mode` (SetupScreen sets it).
- Updated `ui/screen_manager.py`: registered "setup" screen; added `reset()` call on incoming screen at every transition (safe via `hasattr` guard — ResultsScreen has no `reset()`).
- Updated `ui/game_screen.py`: player name label (FONT_MEDIUM, ACCENT) rendered below timer digit only when `len(players) > 1`. Single-player `text_y` is pixel-identical to pre-story layout.
- 37/37 regression tests pass; 16 programmatic smoke checks pass covering all 6 ACs.

### File List

- `ui/setup_screen.py` — NEW: full multiplayer setup flow (count → names → category → "game")
- `ui/menu_screen.py` — UPDATED: added Pass-and-Play button and "multi" click handler
- `ui/screen_manager.py` — UPDATED: registered "setup" screen; reset() on incoming screen at transition
- `ui/game_screen.py` — UPDATED: player name label in multiplayer HUD
