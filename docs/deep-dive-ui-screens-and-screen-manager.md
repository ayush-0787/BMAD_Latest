# UI Screens & Screen Manager — Deep Dive Documentation

**Generated:** 2026-06-15
**Scope:** `trivia-app/ui/`
**Files Analyzed:** 8
**Lines of Code:** 829
**Workflow Mode:** Exhaustive Deep-Dive

## Overview

The `ui/` package is the entire rendering and interaction layer of the Python Trivia App. It contains the `Screen` abstract base class, the `ScreenManager` orchestrator, five concrete screen implementations, and the global constants file. Every pixel drawn and every user input handled passes through this package.

**Purpose:** Render all game screens and handle all user input (mouse clicks and keyboard events). Owns the per-frame lifecycle (handle_events → update → draw) and all screen-to-screen transitions.

**Key Responsibilities:**
- Define the shared `Screen` interface and enforce the handle/update/draw contract
- Orchestrate screen transitions in response to user actions
- Display question text, answer buttons, timer, HUD, and results
- Manage multi-stage wizards (mode selection, player setup)
- Reset `GameState` at session end before returning to the main menu

**Integration Points:** Reads `GameState` and `Player` from `scoring/engine.py`; calls `draw_questions` from `questions/bank.py`; calls `calculate_speed_bonus` and streak helpers from `scoring/`; driven frame-by-frame by `main.py`.

---

## Complete File Inventory

### `ui/__init__.py`

**Purpose:** Marks `ui/` as a Python package. Contains no code.
**Lines of Code:** 1
**File Type:** Package marker

**What Future Contributors Must Know:** This file must exist for Python to treat `ui/` as an importable package. Do not delete it. Never add imports or code here — it will be executed on every `import ui.*` and can cause subtle startup-order bugs with pygame.

**Exports:** None

**Dependencies:** None

**Used By:** Python import machinery (implicit)

**Key Implementation Details:** Empty.

**Patterns Used:**
- Python package marker convention

**State Management:** None

**Side Effects:** None

**Error Handling:** None

**Testing:**
- Test File: None
- Coverage: N/A
- Test Approach: Not applicable

**Comments/TODOs:** None

---

### `ui/constants.py`

**Purpose:** Single source of truth for every magic number and color in the UI — screen dimensions, timer duration, font sizes, button geometry, color palette, and layout margins. No logic, no imports, no pygame dependency.
**Lines of Code:** 25
**File Type:** Configuration / constants module

**What Future Contributors Must Know:** AR-7 mandates that all pixel values live here. Never hardcode a number in a screen file. Changing `QUESTION_TIMER` or `BASE_SCORE` has downstream effects on scoring formulas in `game_screen.py` (those values are passed into `scoring/` functions). Changing any dimension constant will shift layout across all five screens simultaneously — test all screens visually after any edit.

**Exports:**
- `SCREEN_WIDTH: int = 800` — display surface width in pixels
- `SCREEN_HEIGHT: int = 600` — display surface height in pixels
- `QUESTION_TIMER: int = 30` — seconds allowed per question (OQ-1)
- `FPS: int = 60` — target frame rate; used by main.py clock
- `BASE_SCORE: int = 100` — base points awarded per correct answer before bonuses (FR-12)
- `WHITE: tuple = (255, 255, 255)` — primary text color
- `BLACK: tuple = (0, 0, 0)` — background fill color
- `ACCENT: tuple = (70, 130, 180)` — steel blue; default button color
- `GREY: tuple = (200, 200, 200)` — timer bar background, hint text
- `RED: tuple = (220, 50, 50)` — error messages, low-time timer bar
- `GREEN: tuple = (50, 200, 50)` — correct-answer highlight, win verdict
- `FONT_LARGE: int = 48` — title and large-number font size
- `FONT_MEDIUM: int = 32` — body text and button labels
- `FONT_SMALL: int = 24` — HUD labels, hints, error messages
- `BUTTON_WIDTH: int = 300` — standard button width
- `BUTTON_HEIGHT: int = 60` — standard button height
- `BUTTON_PADDING: int = 20` — vertical gap between stacked buttons
- `BUTTON_HOVER: tuple = (100, 160, 210)` — lighter blue for mouse-hover state
- `MARGIN: int = 60` — horizontal inset for text blocks and the timer bar
- `TIMER_BAR_H: int = 10` — pixel height of the question timer progress bar

**Dependencies:** None

**Used By:**
- `ui/menu_screen.py`
- `ui/setup_screen.py`
- `ui/game_screen.py`
- `ui/handoff_screen.py`
- `ui/results_screen.py`

**Key Implementation Details:**

```python
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
QUESTION_TIMER = 30       # seconds per question (resolves OQ-1)
FPS = 60
BASE_SCORE = 100          # fixed points per correct answer before bonuses (FR-12)
```

No function calls, no imports. Values are plain Python literals — importable before pygame is initialized.

**Patterns Used:**
- Constants module: all UI magic numbers centralized, no duplication

**State Management:** Stateless (module-level constants only)

**Side Effects:** None

**Error Handling:** None — wrong constant values produce visual glitches, not exceptions

**Testing:**
- Test File: None (constants require no unit tests)
- Coverage: 0% (not applicable)
- Test Approach: Visual regression only

**Comments/TODOs:**
- Line 3: `# seconds per question (resolves OQ-1)`
- Line 5: `# fixed points per correct answer before bonuses (FR-12)`
- Line 21: `# lighter blue for button hover state`
- Line 23: `# horizontal UI margin for text and bars`
- Line 24: `# height of the timer progress bar`

---

### `ui/screen_manager.py`

**Purpose:** Defines the `Screen` abstract base class and the `ScreenManager` orchestrator. `ScreenManager` owns the single `GameState` instance, instantiates all five screens, and drives the per-frame lifecycle: handle_events → update → draw, with transition logic between them.
**Lines of Code:** 42
**File Type:** Orchestrator / base class

**What Future Contributors Must Know:** Screen imports are deferred inside `__init__` to break circular import chains (each screen imports `Screen` from this file). When you add a new screen, add a deferred import and a `screens` dict entry here. `reset()` is called on the INCOMING screen before the transition fires — any screen with mutable internal state must implement `reset()`. The `update` and `draw` calls in `run_frame` always execute on the screen that was active at the START of the frame, even if `handle_events` triggered a transition — this one-frame lag is intentional and correct.

**Exports:**
- `class Screen` — Abstract base with no-op implementations:
  - `handle_events(events, game_state) -> str | None` — return a screen key to transition, or None to stay
  - `update(game_state: GameState, dt: float) -> None` — per-frame state update
  - `draw(surface, game_state: GameState) -> None` — per-frame render
- `class ScreenManager` — Main orchestrator:
  - `__init__(all_questions: list)` — creates all screens and the shared `GameState`
  - `run_frame(events, surface, dt: float) -> None` — single frame dispatch

**Dependencies:**
- `scoring.engine.GameState` — the shared game state passed to every screen method

**Used By:**
- `main.py` — instantiates `ScreenManager`, calls `run_frame` every frame
- All five screen files — import `Screen` as their base class

**Key Implementation Details:**

```python
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

The local `screen` variable is set before the transition check. If `handle_events` returns a new key, the incoming screen's `reset()` is called and `current_screen` is updated — but `update` and `draw` still run on the original `screen` object this frame. The new screen starts rendering on the next frame. This prevents a half-drawn frame on the incoming screen.

**Patterns Used:**
- Screen Manager pattern: central orchestrator holds screen registry and state
- Template Method: `Screen` base class defines interface; subclasses override behavior
- Deferred import: circular-import prevention by moving screen imports into `__init__`

**State Management:** Owns and creates the single `GameState()` instance. All screens receive it by reference — mutations are immediately visible to subsequent calls in the same frame.

**Side Effects:** None beyond state mutations delegated to screens

**Error Handling:** `self.screens.get(next_screen)` returns `None` for unknown keys (no exception). The `hasattr(incoming, "reset")` guard makes `reset()` optional on screens that have no stateful init.

**Testing:**
- Test File: None (no direct unit tests for ScreenManager)
- Coverage: Tested implicitly through integration/smoke tests
- Test Approach: PyGame-dependent; excluded from pytest suite per architecture rule

**Comments/TODOs:** None

---

### `ui/menu_screen.py`

**Purpose:** The first screen displayed on launch. A two-stage screen: stage `"mode"` presents Single Player / Pass-and-Play / Quit buttons; stage `"category"` presents Politics / History buttons (single-player path only). Initialises `GameState` for single-player sessions before transitioning to `"game"`.
**Lines of Code:** 108
**File Type:** Screen implementation

**What Future Contributors Must Know:** This screen is responsible for initialising the single-player `GameState` fields (`players`, `questions`, `selected_mode`, `selected_category`). The multiplayer path does NOT set these — it hands off to `SetupScreen` immediately. Fonts are lazy-initialised via `_ensure_fonts()` because `pygame.font.SysFont` requires `pygame.init()` to have run first; calling it at `__init__` time would crash if pygame isn't ready. The guard `if not game_state.selected_mode and self._stage != "mode"` in `handle_events` auto-resets to the mode stage when returning from the results screen; without it, returning players would land on the category stage of a previous session.

**Exports:**
- `class MenuScreen(Screen)`:
  - `__init__(all_questions: list)` — stores question reference, sets `_stage = "mode"`
  - `reset() -> None` — resets `_stage` to `"mode"`
  - `handle_events(events, game_state) -> str | None`
  - `_on_click(name: str, game_state) -> str | None` — click dispatch by button name
  - `_get_buttons() -> dict[str, pygame.Rect]` — returns button rects for current stage
  - `_ensure_fonts() -> None` — lazy font init
  - `update(game_state, dt: float) -> None` — no-op
  - `draw(surface, game_state) -> None`

**Dependencies:**
- `pygame` — event types, Rect, font, mouse, display
- `logging` — logs mode/category selections and quit
- `sys` — `sys.exit(0)` on Quit
- `questions.bank.draw_questions` — random question sample on category selection
- `scoring.engine.Player` — creates `Player("Player 1")` for single-player
- `ui.constants.*` — all geometry and color values
- `ui.screen_manager.Screen` — base class

**Used By:**
- `ui/screen_manager.py` — instantiated as `screens["menu"]`

**Key Implementation Details:**

```python
def _on_click(self, name: str, game_state) -> str | None:
    if self._stage == "mode":
        if name == "single":
            game_state.selected_mode = "single"
            self._stage = "category"   # internal stage change, no screen transition
        elif name == "multi":
            return "setup"             # immediate screen transition
        elif name == "quit":
            pygame.quit(); sys.exit(0)
    elif self._stage == "category":
        game_state.selected_category = name
        game_state.players = [Player("Player 1")]
        game_state.questions = draw_questions(self._all_questions, name)
        game_state.current_question_index = 0
        game_state.active_player_index = 0
        return "game"
```

Hover effect is applied in `draw` via `pygame.mouse.get_pos()` — buttons change to `BUTTON_HOVER` when the cursor is over them.

**Patterns Used:**
- Internal stage machine: `_stage` field drives two-phase UI without a separate screen
- Lazy font init: avoids pygame-not-ready crash at construction time

**State Management:** Internal: `_stage`, `_all_questions`, font references. Writes to `game_state` on category selection (single-player path only).

**Side Effects:**
- Logging: mode and category selections at INFO level
- `sys.exit(0)` + `pygame.quit()` on Quit (hard process exit)
- `draw_questions` called inside `handle_events` on click (not per-frame)

**Error Handling:** No explicit error handling. `draw_questions` may raise if `_all_questions` is empty or category is invalid — callers upstream must ensure questions are loaded.

**Testing:**
- Test File: None (pygame-dependent)
- Coverage: 0% direct; covered by manual smoke test
- Test Approach: Excluded per architecture rule (no tests for `ui/`)

**Comments/TODOs:** None

---

### `ui/setup_screen.py`

**Purpose:** Multiplayer setup wizard with three sequential keyboard/mouse sub-stages: `"count"` (enter number of players 2–4), `"names"` (enter each player's name one by one), `"category"` (click Politics or History). Fully initialises `GameState` for multiplayer sessions on completion.
**Lines of Code:** 216
**File Type:** Screen implementation (wizard)

**What Future Contributors Must Know:** This is the most stateful screen and the only one whose `reset()` clears multiple fields. If you add new setup fields (e.g., difficulty level), add them here and to `reset()`. The count input only accepts a single digit — `len(self._input_text) < 1` enforces this. There is no "back" navigation between stages; once a player has entered the count and moved to names, they cannot go back without quitting and restarting. The blinking cursor uses `pygame.time.get_ticks() // 500 % 2` — this is a frame-rate-independent blink that works even before the game clock is used.

**Exports:**
- `class SetupScreen(Screen)`:
  - `__init__(all_questions: list)`
  - `reset() -> None` — full reset of all 6 internal state fields
  - `handle_events(events, game_state) -> str | None`
  - `_handle_count_key(event) -> None` — keyboard handler for count stage
  - `_handle_name_key(event) -> None` — keyboard handler for names stage
  - `_validate_count() -> None` — validates and advances to names stage
  - `_validate_name() -> None` — validates, appends name, advances or transitions to category
  - `_on_category_click(pos, game_state) -> str | None` — initialises GameState and returns `"game"`
  - `_get_category_buttons() -> dict[str, pygame.Rect]`
  - `_ensure_fonts() -> None`
  - `update(game_state, dt: float) -> None` — no-op
  - `draw(surface, game_state) -> None` — dispatches to stage-specific draw helpers
  - `_draw_count_stage(surface) -> None`
  - `_draw_names_stage(surface) -> None`
  - `_draw_category_stage(surface) -> None`

**Dependencies:**
- `pygame` — events, Rect, font, mouse, time
- `logging` — player count and names at INFO level
- `questions.bank.draw_questions`
- `scoring.engine.Player`
- `ui.constants.*`
- `ui.screen_manager.Screen`

**Used By:**
- `ui/screen_manager.py` — instantiated as `screens["setup"]`

**Key Implementation Details:**

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
    self._stage = "names"

def _validate_name(self) -> None:
    name = self._input_text.strip()
    if not name:
        self._error_msg = "Name cannot be empty"
        return
    self._player_names.append(name)
    self._current_name_idx += 1
    if self._current_name_idx == self._player_count:
        self._stage = "category"
```

Category click creates all `Player` objects from `_player_names` list and writes the full multiplayer `GameState` before returning `"game"`.

**Patterns Used:**
- Multi-stage wizard: single screen class, `_stage` string drives which sub-UI is shown and which input handler runs
- Inline validation with user-visible error messages
- Lazy font init

**State Management:** Owns 6 internal mutable fields. All are cleared in `reset()`. Writes `game_state` once on category selection.

**Side Effects:**
- Logging at INFO level for count and each player name
- `draw_questions` called on category click

**Error Handling:** Explicit validation with `_error_msg` shown in RED. Count must parse as int, must be 2–4. Name must be non-empty after strip, max 20 printable characters.

**Testing:**
- Test File: None (pygame-dependent)
- Coverage: 0% direct
- Test Approach: Excluded per architecture rule

**Comments/TODOs:** None

---

### `ui/game_screen.py`

**Purpose:** Core gameplay screen. Manages the 30-second countdown timer, 2×2 answer button grid, score/streak calculation on click, a 1-second post-answer feedback pause, and timer-expiry handling. Transitions to `"handoff"` (more multiplayer turns remain) or `"results"` (all players done).
**Lines of Code:** 215
**File Type:** Screen implementation (core game loop)

**What Future Contributors Must Know:** The question advancement is split across two methods by design: `handle_events` sets `_in_pause = True` and `_pause_timer = 1.0` when an answer is clicked or the timer expires; `update` decrements `_pause_timer` each frame and increments `current_question_index` when it hits zero. Never advance `current_question_index` in `handle_events` — doing so would skip the feedback pause. The transition check (`current_question_index >= len(questions)`) lives at the top of `handle_events` and fires on the frame AFTER the last question's pause expires (because `update` advanced the index the previous frame). `_in_pause` blocks new clicks during the feedback window — this is critical for correctness. `reset()` only resets per-question screen state; `GameState` reset happens in `ResultsScreen`.

**Exports:**
- `class GameScreen(Screen)`:
  - `__init__()` — initialises all timer/pause/state fields to defaults
  - `reset() -> None` — resets `_question_timer`, `_pause_timer`, `_in_pause`, `_correct_index`, `_last_multiplier`
  - `handle_events(events, game_state) -> str | None`
  - `update(game_state, dt: float) -> None`
  - `draw(surface, game_state) -> None`
  - `_get_answer_rects() -> list[pygame.Rect]` — 2×2 grid layout
  - `_wrap_text(text: str, font, max_width: int) -> list[str]` — greedy word-wrap
  - `_ensure_fonts() -> None`

**Dependencies:**
- `pygame` — events, Rect, font, draw, mouse
- `logging` — correct/wrong/timeout at INFO level per question
- `scoring.engine.calculate_speed_bonus` — speed bonus on correct answer
- `scoring.multiplier.apply_streak_multiplier` — applies streak multiplier to final score
- `scoring.multiplier.get_multiplier` — reads current multiplier for HUD display
- `ui.constants.*`
- `ui.screen_manager.Screen`

**Used By:**
- `ui/screen_manager.py` — instantiated as `screens["game"]`

**Key Implementation Details:**

```python
# handle_events: click path
if i == self._correct_index:
    player.streak += 1
    speed_bonus = calculate_speed_bonus(BASE_SCORE, self._question_timer, QUESTION_TIMER)
    points = apply_streak_multiplier(BASE_SCORE + speed_bonus, player.streak)
    player.score += points
    player.correct += 1
    self._last_multiplier = get_multiplier(player.streak)
else:
    player.streak = 0
player.total += 1
self._in_pause = True
self._pause_timer = 1.0

# update: pause countdown and question advancement
if self._in_pause:
    self._pause_timer -= dt
    if self._pause_timer <= 0.0:
        self._in_pause = False
        game_state.current_question_index += 1
        self._question_timer = 0.0
        self._correct_index = -1

# update: timer expiry
self._question_timer += dt
if self._question_timer >= QUESTION_TIMER:
    player.streak = 0
    player.total += 1
    self._correct_index = question["correct_index"]
    self._in_pause = True
    self._pause_timer = 1.0
```

Timer bar is GREEN when `time_remaining > 10`, RED when ≤ 10. During `_in_pause`, the correct answer button is highlighted GREEN; wrong buttons remain ACCENT blue (no red highlight for wrong answers — design intent is to show the right answer, not penalize).

**Patterns Used:**
- State machine: `_in_pause` boolean gates click handling and timer increment
- Observer-like: `update` drives time-based state; `handle_events` drives input-based state; `draw` is pure read

**State Management:** Owns 5 internal fields. Writes directly to `player.score`, `player.streak`, `player.correct`, `player.total` and `game_state.current_question_index`. Does NOT own or reset `GameState`.

**Side Effects:**
- Logging per question at INFO: correct answer (with points/streak/multiplier), wrong answer, timer expiry
- Mutates `Player` and `GameState` fields on every answered or expired question

**Error Handling:** Guards `if game_state.current_question_index >= len(game_state.questions)` in both `handle_events` and `draw` prevent index-out-of-range errors during the transition frame. `max(0.0, ...)` clamps timer display to avoid negative countdown.

**Testing:**
- Test File: None (pygame-dependent)
- Coverage: 0% direct; scoring functions tested in `tests/test_engine.py` and `tests/test_multiplier.py`
- Test Approach: Excluded per architecture rule; scoring logic tested separately

**Comments/TODOs:**
- Line 153: `# HUD: question counter top-left, streak+multiplier centre, score top-right`
- Line 174: `# Timer progress bar (full-width background, coloured fill)`
- Line 183: `# Timer countdown digit (centred below bar)`
- Line 188: `# Player name label (multiplayer only — single-player layout unchanged)`
- Line 195: `# Question text (word-wrapped, centred)`
- Line 202: `# Answer buttons (2×2 grid)`

---

### `ui/handoff_screen.py`

**Purpose:** Privacy barrier shown between multiplayer turns. Displays which player just finished and who plays next. Any mouse click or key press advances `active_player_index` by 1 and resets `current_question_index` to 0, then returns `"game"` for the next player's turn.
**Lines of Code:** 72
**File Type:** Screen implementation (transition/barrier)

**What Future Contributors Must Know:** This is the only screen that accepts BOTH `MOUSEBUTTONDOWN` and `KEYDOWN` for navigation. The `draw` method has a bounds guard: `if game_state.active_player_index + 1 >= len(game_state.players)` — it fills black and returns without rendering, preventing an out-of-bounds access on `players[active_player_index + 1]`. However, this state (last player done, handoff shown) should never occur in practice because `GameScreen.handle_events` already routes the last player to `"results"`. There is no `reset()` method because `HandoffScreen` owns no mutable state between renders.

**Exports:**
- `class HandoffScreen(Screen)`:
  - `__init__()` — initialises font fields only
  - `handle_events(events, game_state) -> str | None`
  - `_advance_turn(game_state) -> str` — increments index, resets question counter, returns `"game"`
  - `update(game_state, dt: float) -> None` — no-op
  - `draw(surface, game_state) -> None`
  - `_ensure_fonts() -> None`

**Dependencies:**
- `pygame` — events, font
- `logging` — handoff advance at INFO level
- `ui.constants.*`
- `ui.screen_manager.Screen`

**Used By:**
- `ui/screen_manager.py` — instantiated as `screens["handoff"]`

**Key Implementation Details:**

```python
def handle_events(self, events, game_state) -> str | None:
    if not game_state.players:
        return None
    for event in events:
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or event.type == pygame.KEYDOWN:
            return self._advance_turn(game_state)
    return None

def _advance_turn(self, game_state) -> str:
    game_state.active_player_index += 1
    game_state.current_question_index = 0
    return "game"
```

The `draw` guard checks `active_player_index + 1 >= len(players)` before reading `players[active_player_index + 1]` for the "next player" name label.

**Patterns Used:**
- Barrier screen: no game logic, pure navigation and privacy separation

**State Management:** No internal game state. Writes `active_player_index` and `current_question_index` to `game_state` on advance.

**Side Effects:**
- Logging at INFO: player index and name on each handoff

**Error Handling:** Guard in `handle_events` returns `None` if `game_state.players` is empty. Guard in `draw` prevents rendering when `active_player_index + 1` would be out of bounds.

**Testing:**
- Test File: None (pygame-dependent)
- Coverage: 0% direct
- Test Approach: Excluded per architecture rule

**Comments/TODOs:** None

---

### `ui/results_screen.py`

**Purpose:** End-of-game display. Single-player mode shows score, percentage, and a Win (≥70%) or Lose verdict. Multiplayer mode shows a ranked leaderboard sorted by percentage, with tied-rank support. The "Main Menu" button resets all `GameState` fields and returns `"menu"`.
**Lines of Code:** 150
**File Type:** Screen implementation (end state)

**What Future Contributors Must Know:** The 70% win threshold is hardcoded in `_draw_single` — not in `constants.py`. If this ever needs to be configurable, move it to `constants.py` (add a `WIN_THRESHOLD = 70.0` constant). `GameState` is reset manually field-by-field in `handle_events` rather than via a `GameState.reset()` method — if new fields are added to `GameState`, they must also be cleared here or they will bleed into the next session. The multiplayer leaderboard uses dense ranking: tied players share a rank and the next rank is NOT skipped (e.g., 1, 1, 2, not 1, 1, 3). The winner display always uses `sorted_players[0]`; if two players tie for first, only the first one in the sorted list (stable sort by Python, so original order is preserved among ties) is shown as "Winner" — a cosmetic limitation.

**Exports:**
- `class ResultsScreen(Screen)`:
  - `__init__()` — font fields only
  - `handle_events(events, game_state) -> str | None`
  - `update(game_state, dt: float) -> None` — no-op
  - `draw(surface, game_state) -> None`
  - `_ensure_fonts() -> None`
  - `_get_menu_button_rect() -> pygame.Rect`
  - `_draw_single(surface, game_state) -> None`
  - `_draw_multiplayer(surface, game_state) -> None`

**Dependencies:**
- `pygame` — events, Rect, font, draw, mouse
- `logging` — results summary at INFO level
- `ui.constants.*`
- `ui.screen_manager.Screen`

**Used By:**
- `ui/screen_manager.py` — instantiated as `screens["results"]`

**Key Implementation Details:**

```python
# GameState reset on "Main Menu" click
game_state.players = []
game_state.active_player_index = 0
game_state.current_question_index = 0
game_state.questions = []
game_state.selected_mode = ""
game_state.selected_category = ""
return "menu"

# Dense ranking for multiplayer leaderboard
prev_pct = None
rank = 0
for player in sorted_players:
    pct = player.percentage
    if pct != prev_pct:
        rank += 1
        prev_pct = pct
    # draw rank, name, score, pct
```

Win condition: `pct >= 70.0`. Verdict rendered in GREEN for win, RED for lose. Winner row in multiplayer rendered in GREEN; all others WHITE.

**Patterns Used:**
- Dense ranking algorithm for tied leaderboard positions
- Manual GameState teardown before screen exit

**State Management:** No internal game state. Reads `game_state.players`, `game_state.selected_mode`. Writes (resets) all `GameState` fields on "Main Menu" click.

**Side Effects:**
- Logging at INFO: single-player score/percentage, multiplayer winner name/percentage

**Error Handling:** `draw` returns early if `game_state.players` is empty, preventing a render before any game has been played. `player.percentage` depends on `player.total > 0` — `GameScreen` ensures `total >= 1` before routing here.

**Testing:**
- Test File: None (pygame-dependent)
- Coverage: 0% direct; `player.percentage` tested via `tests/test_engine.py`
- Test Approach: Excluded per architecture rule

**Comments/TODOs:** None

---

## Contributor Checklist

**Risks & Gotchas:**
- `constants.py` changes have pixel-perfect layout impact across all five screens simultaneously — always test visually after any constant edit
- `QUESTION_TIMER` and `BASE_SCORE` also feed into scoring formulas; changing them affects points, not just display
- The 70% win threshold is in `results_screen.py:80`, NOT in `constants.py` — easy to miss
- `GameState` fields are reset manually in `results_screen.py` — if you add a new field to `GameState`, you MUST also clear it there or it will leak into the next session
- `SetupScreen` has no "back" navigation — once a player enters the count and moves to name entry, they cannot return to the count stage without quitting
- `HandoffScreen` advances on ANY click or keypress — a rapid accidental input skips a player's turn
- `_last_multiplier` in `GameScreen` persists from the last correct answer; it is cosmetically stale after a streak reset until the next correct answer
- Tied "winners" in multiplayer only show the first player in original list order — could surprise users who expect both names

**Pre-change Verification Steps:**
1. Run `python -m pytest tests/ -v` — must pass all 37 tests before and after any change
2. Launch the app with `python main.py` and manually walk through single-player mode end-to-end
3. Walk through multiplayer mode with at least 2 players to verify handoff and leaderboard
4. If touching `constants.py`, check all five screens visually for layout regressions
5. If touching `screen_manager.py`, verify screen transitions in both single and multiplayer flows
6. If adding a field to `GameState`, grep for the reset block in `results_screen.py` and update it

**Suggested Tests Before PR:**
- `python -m pytest tests/ -v` — full suite (all 37 tests)
- Manual smoke: single-player win path (≥7/10 correct)
- Manual smoke: single-player lose path (<7/10 correct)
- Manual smoke: timer expiry — let a question expire and verify streak resets
- Manual smoke: streak display — answer 5+ correctly in a row to verify x3.0 multiplier
- Manual smoke: multiplayer 2-player path, full handoff, leaderboard with tie
- Manual smoke: quit from main menu exits cleanly

---

## Architecture & Design Patterns

### Code Organization

The `ui/` package follows a clean separation between infrastructure (`screen_manager.py`, `constants.py`) and feature implementations (the five screen files). No screen file imports another screen file — all cross-screen coupling flows through `GameState`. This makes each screen independently comprehensible.

### Design Patterns

- **Screen Manager**: `ScreenManager` holds a registry of all screens keyed by string, owns `GameState`, and drives the frame lifecycle. Adding a screen requires only a new entry in the registry and a new deferred import — no other files change.
- **Template Method**: `Screen` base class defines the three-method contract (`handle_events`, `update`, `draw`). Subclasses override what they need; the base provides no-op defaults so screens that don't need `update` (four out of five) aren't forced to define it.
- **Lazy Initialization**: All five screen classes defer `pygame.font.SysFont` calls to the first render frame via `_ensure_fonts()`. This allows screen objects to be constructed before `pygame.init()` runs.
- **Internal Stage Machine**: `MenuScreen` and `SetupScreen` use a `_stage` string field to drive multi-step UIs within a single screen class, avoiding the overhead of separate screen objects for transient sub-states.
- **Constants Module**: All magic numbers live in `constants.py`. The architecture explicitly forbids inline pixel values in screen files (AR-7).

### State Management Strategy

There are two types of state in this package:

1. **`GameState` (shared, owned by `ScreenManager`)**: The single source of truth for session data — mode, category, players, questions, indices. All screens receive it by reference. `GameState` is created once at startup and manually reset by `ResultsScreen` at session end.

2. **Screen-local state**: Each screen owns only the state it needs between frames (`_stage`, `_input_text`, `_in_pause`, `_question_timer`, etc.). This state is cleared by `reset()` when the screen is entered. It is never shared with other screens.

### Error Handling Philosophy

Defensive at input boundaries, trusting internally. User text input is validated with inline error messages (empty names, out-of-range counts). Internal invariants (non-empty questions list, valid player indices) are assumed to hold — no try/catch inside game logic. Guards like `if not game_state.players: return None` protect against edge cases during screen transitions rather than raising exceptions.

### Testing Strategy

The `ui/` package has zero automated test coverage by design (architecture rule). All pygame-dependent code is untestable in the pytest suite. The testing boundary falls between `ui/` (excluded) and `scoring/` + `questions/` (fully covered). Manual smoke testing is the only verification path for UI behavior.

---

## Data Flow

```
main.py
  └─ loads all_questions from JSON files
  └─ creates ScreenManager(all_questions)
       └─ creates GameState()  [current_screen="menu"]
       └─ creates all 5 screens

Every frame (60 FPS):
  main.py → ScreenManager.run_frame(events, surface, dt)
    → screen.handle_events(events, game_state)  [may return next_screen key]
      if next_screen:
        → incoming.reset()
        → game_state.current_screen = next_screen
    → screen.update(game_state, dt)             [timer advancement]
    → screen.draw(surface, game_state)          [render]
```

### Data Entry Points

- **`MenuScreen` (single-player path)**: Mouse click on category → sets `game_state.players`, `game_state.questions`, `game_state.selected_mode`, `game_state.current_question_index`, `game_state.active_player_index`
- **`SetupScreen` (multiplayer path)**: Keyboard input (count, names) + mouse click (category) → sets all of the above plus a full `[Player(name) for name in self._player_names]` list
- **`GameScreen`**: Mouse click on answer → writes to `player.score`, `player.streak`, `player.correct`, `player.total`; timer expiry → writes to `player.streak`, `player.total`; pause expiry → advances `game_state.current_question_index`

### Data Transformations

- **Speed bonus**: `calculate_speed_bonus(BASE_SCORE, elapsed_seconds, QUESTION_TIMER)` → `int` bonus points (0–100)
- **Streak multiplier**: `apply_streak_multiplier(BASE_SCORE + speed_bonus, streak)` → final `int` points for the question
- **Question sampling**: `draw_questions(all_questions, category, n=10)` → `list[dict]` of 10 random questions
- **Percentage**: `player.percentage` (computed property on `Player`) = `correct / total * 100`
- **Dense ranking**: sorted leaderboard list → rank numbers using `prev_pct` tracker

### Data Exit Points

- **`ResultsScreen`**: Reads all `Player` data for display. Resets `GameState` to blank state on "Main Menu" click.
- **`logging`**: Structured INFO log messages emitted at every key game event (mode selection, answer, timer expiry, handoff, results).

---

## Integration Points

### APIs Consumed (internal Python modules)

- **`questions.bank.draw_questions(questions, category, n=10) -> list[dict]`**: Called by `MenuScreen` and `SetupScreen` on game start. Returns a shuffled sample of `n` questions for the given category. No authentication. Raises `ValueError` for unknown categories or empty input.
- **`scoring.engine.GameState`**: Dataclass, constructed once by `ScreenManager`. Fields: `current_screen`, `selected_mode`, `selected_category`, `questions`, `players`, `current_question_index`, `active_player_index`.
- **`scoring.engine.Player`**: Dataclass, constructed per player by `MenuScreen`/`SetupScreen`. Fields: `name`, `score`, `correct`, `total`, `streak`. Computed property: `percentage`.
- **`scoring.engine.calculate_speed_bonus(base_score, elapsed, max_time) -> int`**: Called by `GameScreen` on correct answer.
- **`scoring.multiplier.get_multiplier(streak) -> float`**: Returns `1.0 / 1.5 / 2.0 / 3.0` based on streak count.
- **`scoring.multiplier.apply_streak_multiplier(score, streak) -> int`**: Returns `int(score * get_multiplier(streak))`.

### APIs Exposed

None — `ui/` is a leaf consumer package. No other package imports from `ui/`.

### Shared State

- **`GameState` instance**: Created by `ScreenManager`. Passed by reference to every `handle_events`, `update`, and `draw` call. All screens read and (selectively) write to it.
  - Type: `scoring.engine.GameState` dataclass
  - Accessed By: All 5 screen classes + `ScreenManager`

### Events

- **`pygame.MOUSEBUTTONDOWN` (button=1)**: Left click. Consumed by `MenuScreen`, `SetupScreen` (category stage), `GameScreen`, `HandoffScreen`, `ResultsScreen`.
- **`pygame.KEYDOWN`**: Keyboard input. Consumed by `SetupScreen` (count and names stages) and `HandoffScreen` (any key advances turn).
- **`pygame.QUIT`**: Not handled inside `ui/` — handled in `main.py`'s event loop.

### Database Access

None — question data is loaded from JSON files by `main.py` before the UI starts. The `ui/` package receives a pre-loaded list and never reads files directly.

---

## Dependency Graph

```
ui/__init__.py
  (no dependencies, no dependents)

ui/constants.py
  ← no imports
  → used by: menu_screen, setup_screen, game_screen, handoff_screen, results_screen

ui/screen_manager.py
  ← scoring.engine (GameState)
  → used by: main.py, all 5 screen files

ui/menu_screen.py
  ← questions.bank (draw_questions)
  ← scoring.engine (Player)
  ← ui.constants (*)
  ← ui.screen_manager (Screen)
  → used by: screen_manager.py (instantiated as screens["menu"])

ui/setup_screen.py
  ← questions.bank (draw_questions)
  ← scoring.engine (Player)
  ← ui.constants (*)
  ← ui.screen_manager (Screen)
  → used by: screen_manager.py (instantiated as screens["setup"])

ui/game_screen.py
  ← scoring.engine (calculate_speed_bonus)
  ← scoring.multiplier (apply_streak_multiplier, get_multiplier)
  ← ui.constants (*)
  ← ui.screen_manager (Screen)
  → used by: screen_manager.py (instantiated as screens["game"])

ui/handoff_screen.py
  ← ui.constants (*)
  ← ui.screen_manager (Screen)
  → used by: screen_manager.py (instantiated as screens["handoff"])

ui/results_screen.py
  ← ui.constants (*)
  ← ui.screen_manager (Screen)
  → used by: screen_manager.py (instantiated as screens["results"])
```

### Entry Points (instantiated by ScreenManager, not imported by other ui/ files)
- `ui/menu_screen.py`
- `ui/setup_screen.py`
- `ui/game_screen.py`
- `ui/handoff_screen.py`
- `ui/results_screen.py`

### Leaf Nodes (import nothing from within `ui/`)
- `ui/constants.py`
- `ui/__init__.py`

### Circular Dependencies

✓ No circular dependencies detected. Screen imports in `screen_manager.py` are deferred inside `__init__` specifically to prevent cycles.

---

## Testing Analysis

### Test Coverage Summary

- **Statements:** 0% (ui/ is explicitly excluded from automated testing)
- **Branches:** 0%
- **Functions:** 0%
- **Lines:** 0%

### Test Files

The `ui/` package has no test files. This is an intentional architectural decision: pygame requires a display and event loop, making standard unit testing impractical without a headless display driver or extensive mocking. The scoring and question logic that underlies the UI is tested separately.

| Tested Dependency | Test File | Tests |
|-------------------|-----------|-------|
| `scoring.engine` | `tests/test_engine.py` | 7 |
| `scoring.multiplier` | `tests/test_multiplier.py` | 13 |
| `questions.bank` | `tests/test_bank.py` | 7 |
| `questions.loader` | `tests/test_loader.py` | 10 |

### Testing Gaps

- No automated tests for any `ui/` screen class
- No tests for `MenuScreen._on_click` game state initialization
- No tests for `SetupScreen` input validation (count range, name length, empty name)
- No tests for `GameScreen` scoring integration (the actual click-to-score pipeline)
- No tests for `ResultsScreen` GameState reset completeness
- No tests for the 70% win threshold boundary
- No tests for tied-rank leaderboard rendering logic

---

## Related Code & Reuse Opportunities

### Similar Features Elsewhere

- **`questions/bank.py` `draw_questions`**: The random sampling behavior is similar in spirit to how `MenuScreen` and `SetupScreen` both call it with identical arguments — both could be refactored to share a single game-start helper if the initialization logic grows more complex.
- **`scoring/engine.py` `GameState`**: The manual field-by-field reset in `ResultsScreen` mirrors what a `GameState.reset()` method would do — this is the obvious refactor target if session management becomes more complex.

### Reusable Utilities Available

- **`GameScreen._wrap_text(text, font, max_width) -> list[str]`** (`ui/game_screen.py`): A pure word-wrap function with no pygame side effects beyond `font.size()`. Reusable by any screen that needs to render long text across multiple lines (e.g., a future help screen or question explanation screen).
- **`_ensure_fonts()` pattern**: All five screens implement identical lazy font init. Could be extracted to a mixin or `Screen` base class helper if the number of screens grows.

### Patterns to Follow

- **Adding a new screen**: Reference `ui/handoff_screen.py` — the simplest complete screen implementation, showing the minimal boilerplate (Screen subclass, `_ensure_fonts`, `handle_events`, `update`, `draw`).
- **Adding a multi-stage screen**: Reference `ui/setup_screen.py` — shows the internal `_stage` machine, per-stage draw helpers, and per-stage input handlers.
- **Scoring on user input**: Reference `ui/game_screen.py` `handle_events` click handler — the canonical pattern for calling `calculate_speed_bonus` and `apply_streak_multiplier`.

---

## Implementation Notes

### Code Quality Observations

- All five screen classes are consistently structured: `__init__`, `_ensure_fonts`, optional `reset`, `handle_events`, `update`, `draw`, private helpers. Easy to navigate.
- `game_screen.py` is the most complex file (215 lines, 5 internal state fields) and the most important to understand before any gameplay changes.
- `constants.py` has zero imports and zero pygame dependency — it can be imported and inspected in any Python environment without pygame installed.
- `_wrap_text` in `game_screen.py` is the only genuinely reusable utility function in the package; it deserves extraction to a shared utility if a second screen needs it.
- Comment coverage in `game_screen.py:draw` is excellent — each rendering section has a clear label. Other screen files have minimal comments, which is appropriate since the code is self-explanatory.

### TODOs and Future Work

No explicit `# TODO` or `# FIXME` comments found anywhere in `ui/`. Implicit areas for improvement are captured in Known Issues below.

### Known Issues

- **70% win threshold not in constants**: `results_screen.py:80` hardcodes `pct >= 70.0`. Should be `WIN_THRESHOLD` in `constants.py`.
- **No back navigation in SetupScreen**: Players cannot return to the count stage once they've confirmed a player count. Requires quitting and restarting.
- **Manual GameState reset in ResultsScreen**: `results_screen.py` resets `GameState` fields individually. New `GameState` fields added in future will silently leak into the next session unless this block is updated.
- **Multiplayer tie for first place**: `"Winner: {sorted_players[0].name}!"` only names one winner; tied-first players are not acknowledged.
- **`_last_multiplier` cosmetic stale value**: After a streak reset, the HUD still shows the last multiplier until the next correct answer. Cosmetic only — scoring is unaffected.
- **No "are you sure?" on handoff**: Any accidental tap advances the turn. Low-friction is likely intentional for the game's pace, but could be a usability issue on touchscreens.

### Optimization Opportunities

- The `_get_buttons()` / `_get_answer_rects()` / `_get_category_buttons()` methods recompute `pygame.Rect` objects every frame during `draw`. For a 60 FPS game these are trivially cheap, but they could be cached as instance variables if profiling ever shows them as hot.
- `_ensure_fonts()` is called at the start of both `handle_events` and `draw` in most screens — once fonts are initialized, this is a single `None` check per call. Negligible overhead.

### Technical Debt

- `_ensure_fonts()` is copy-pasted identically across all five screens. If the font set ever changes (e.g., adding a fourth size), all five files must be updated. A `Screen` base class method or a module-level font cache would eliminate this duplication.
- `GameState` lacks a `reset()` method. The manual reset in `ResultsScreen.handle_events` is fragile and will silently break when new `GameState` fields are added.
- The 70% win threshold belongs in `constants.py`, not embedded in `_draw_single`.

---

## Modification Guidance

### To Add New Functionality

**Adding a new screen:**
1. Create `ui/your_screen.py` subclassing `Screen`. Implement `handle_events`, `update`, `draw`. Add `reset()` if the screen has internal state.
2. In `screen_manager.py` `__init__`, add a deferred import and a `"your_key": YourScreen(...)` entry in `self.screens`.
3. Return `"your_key"` from an existing screen's `handle_events` to route to it.
4. Return some other key from `YourScreen.handle_events` to route away from it.

**Adding a new game mode:**
1. Add any new setup logic to `MenuScreen` or a new setup screen.
2. Add new `GameState` fields as needed.
3. Add the new mode's clear logic to `ResultsScreen.handle_events` reset block.

**Adding a new question category:**
1. Add the JSON file to `trivia-app/data/`.
2. Update `main.py` to load it.
3. Update `questions/loader.py` validation.
4. Add a button to `MenuScreen._get_buttons()` (category stage) and `SetupScreen._get_category_buttons()`.

**Adding a new UI constant:**
1. Add it to `constants.py` only. Never inline it in a screen file.

### To Modify Existing Functionality

**Changing the win threshold:**
1. Move `70.0` from `results_screen.py:80` to `constants.py` as `WIN_THRESHOLD = 70.0`.
2. Update `_draw_single` to use `WIN_THRESHOLD`.

**Changing the timer duration or base score:**
1. Edit `QUESTION_TIMER` or `BASE_SCORE` in `constants.py`.
2. Re-run all 37 tests — `calculate_speed_bonus` tests use these values indirectly.
3. Verify gameplay feel manually (30 seconds is tuned for the current question length).

**Changing button layout or colors:**
1. Edit `constants.py` values only. Screen files will pick up changes automatically.
2. Test all five screens visually — shared constants affect all screens.

**Changing the `Screen` base class interface:**
1. Update the base method signature.
2. Update all five subclasses.
3. Update `ScreenManager.run_frame` if the call signature changes.

### To Remove/Deprecate

**Removing a screen:**
1. Remove the entry from `self.screens` in `screen_manager.py`.
2. Remove the deferred import.
3. Ensure no other screen's `handle_events` returns the removed key.
4. Delete the screen file.

**Removing a game mode:**
1. Remove the button from `MenuScreen._get_buttons()` and `_on_click`.
2. Remove the associated screen(s) if now unreachable.
3. Remove the mode-specific draw branch in `ResultsScreen` if applicable.

### Testing Checklist for Changes

- [ ] `python -m pytest tests/ -v` passes all 37 tests
- [ ] Single-player: full round played, correct win/lose verdict shown
- [ ] Single-player: timer expiry tested (let a question run out)
- [ ] Single-player: streak multiplier visible at x1.5, x2.0, x3.0
- [ ] Multiplayer: 2-player handoff sequence, leaderboard displayed
- [ ] Multiplayer: tied-score leaderboard ranks shown correctly
- [ ] Main menu: Quit button exits cleanly
- [ ] Main menu: playing a second game after returning from results works correctly (no stale state)
- [ ] If `constants.py` changed: all five screens visually inspected for layout regressions
- [ ] If `GameState` fields added: reset block in `results_screen.py` updated and verified

---

_Generated by `document-project` workflow (deep-dive mode)_
_Base Documentation: docs/index.md_
_Scan Date: 2026-06-15_
_Analysis Mode: Exhaustive_
