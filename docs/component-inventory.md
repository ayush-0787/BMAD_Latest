# Component Inventory — Python Trivia App

**Generated:** 2026-06-09 | **Scan level:** Deep

---

## UI Screens

All screens extend `ui.screen_manager.Screen` and implement the same three-method lifecycle.

### Screen Base Class (`ui/screen_manager.py`)

```python
class Screen:
    def handle_events(self, events, game_state) -> str | None: ...
    def update(self, game_state: GameState, dt: float) -> None: ...
    def draw(self, surface, game_state: GameState) -> None: ...
```

- `handle_events` returns a screen key string to trigger a transition, or `None` to stay on the current screen.
- `update` is called after `handle_events` in every frame (regardless of transition).
- `draw` is called after `update` in every frame.

Screens that carry per-session state implement an optional `reset()` method. `ScreenManager` calls it automatically on the incoming screen at every transition via `hasattr(incoming, "reset")`.

---

### MenuScreen (`ui/menu_screen.py`)

**Screen key:** `"menu"`

**Stages:** `"mode"` → `"category"` (single-player path only; multiplayer routes directly to `"setup"`)

**Internal state:**
| Field | Type | Description |
|-------|------|-------------|
| `_stage` | `str` | `"mode"` or `"category"` |
| `_all_questions` | `list` | Full question bank (passed at construction) |
| `_font_large`, `_font_medium` | `pygame.font.Font` | Lazy-initialized fonts |

**Buttons (mode stage):** Single Player, Pass-and-Play, Quit
**Buttons (category stage):** Politics, History

**Transitions:**
- Single Player → category stage (internal; no transition yet)
- Single Player + category → `"game"` (sets `GameState.questions`, `players`, `selected_mode = "single"`)
- Pass-and-Play → `"setup"`
- Quit → `pygame.quit()` + `sys.exit(0)`

**reset():** Resets `_stage = "mode"`.

---

### SetupScreen (`ui/setup_screen.py`)

**Screen key:** `"setup"`

**Stages:** `"count"` → `"names"` → `"category"`

**Internal state:**
| Field | Type | Description |
|-------|------|-------------|
| `_stage` | `str` | Current sub-stage |
| `_player_count` | `int` | Validated player count (2–4) |
| `_player_names` | `list[str]` | Accumulated names |
| `_current_name_idx` | `int` | Index of name currently being entered |
| `_input_text` | `str` | Live keyboard input buffer |
| `_error_msg` | `str` | Validation error shown on screen |

**Input:** Keyboard-driven. Enter confirms each step; Backspace edits input.

**Validation:**
- Player count: integer 2–4.
- Player name: 1–20 printable characters, not blank.

**Transition:** On category click → `"game"` (sets `GameState.selected_mode = "multiplayer"`, `players`, `questions`, resets indices).

**reset():** Zeros all internal state (stage, count, names, index, buffers).

---

### GameScreen (`ui/game_screen.py`)

**Screen key:** `"game"`

**Internal state:**
| Field | Type | Description |
|-------|------|-------------|
| `_question_timer` | `float` | Seconds elapsed on the current question |
| `_pause_timer` | `float` | Countdown for the 1-second post-answer feedback pause |
| `_in_pause` | `bool` | True during feedback pause |
| `_correct_index` | `int` | Correct answer index stored on pause entry; -1 otherwise |
| `_last_multiplier` | `float` | Streak multiplier shown in HUD |

**Layout:**
- HUD bar: question counter (top-left), streak + multiplier (centre), score (top-right)
- Timer bar (full-width, green/red based on time remaining)
- Timer countdown digit (large, centred)
- Player name label (multiplayer only)
- Question text (word-wrapped)
- 2×2 answer button grid (A/B/C/D)
- During pause: correct answer highlighted GREEN; wrong buttons stay blue

**handle_events logic:**
- Guard: if `current_question_index >= len(questions)` → return `"handoff"` (multiplayer + players remain) or `"results"`.
- During pause: no input accepted.
- On answer click: update `player.streak`, `player.score`, `player.correct`, `player.total`; enter 1-second pause.

**update logic:**
- During pause: decrement `_pause_timer`; on expiry, advance `current_question_index`.
- Not in pause: increment `_question_timer`; on 30s expiry, count as wrong, enter pause.

**reset():** Zeros all internal timer and state fields.

---

### HandoffScreen (`ui/handoff_screen.py`)

**Screen key:** `"handoff"`

**Purpose:** Privacy barrier between players in pass-and-play. Prevents the next player from seeing the previous player's answers.

**Internal state:** Font refs only (lazy-initialized). No per-session state.

**Layout:**
```
"Turn Complete!"                  (WHITE, large, centred)
"{curr_player.name} is done"      (GREY, medium, centred)
"Pass to {next_player.name}"      (ACCENT/blue, large, centred)
"Tap or click anywhere to begin"  (WHITE, small, centred)
```

**handle_events:** On any `MOUSEBUTTONDOWN` (button 1) or `KEYDOWN` → calls `_advance_turn(game_state)`:
- Increments `game_state.active_player_index`
- Resets `game_state.current_question_index = 0`
- Returns `"game"`

**draw() guard:** If `active_player_index + 1 >= len(players)`, fills BLACK and returns. This handles the one-frame draw call that occurs after the transition fires in the same `run_frame` invocation.

**reset():** Not implemented (not needed; no per-session state).

---

### ResultsScreen (`ui/results_screen.py`)

**Screen key:** `"results"`

**Modes:**
- `selected_mode == "multiplayer"` → `_draw_multiplayer()`: ranked leaderboard
- Other → `_draw_single()`: win/lose verdict

**_draw_single layout:**
```
"Results"                          (WHITE, large, centred)
"Score: {score}"                   (WHITE, medium, centred)
"{pct:.0f}%"                       (WHITE, medium, centred)
"You Win!" or "You Lose"           (GREEN or RED, large, centred)
"{correct} / {total} correct"      (WHITE, small, centred)
[Main Menu button]
```
Win condition: `player.percentage >= 70.0`.

**_draw_multiplayer layout:**
```
"Results"                          (WHITE, large, centred)
"Winner: {sorted[0].name}!"        (GREEN, large, centred)
[leaderboard rows, dense-ranked]   (GREEN if tied-top, WHITE otherwise)
[Main Menu button]
```

**Leaderboard ranking:** Dense ranking — players with equal percentage share the same rank; the next distinct percentage gets the next rank number (no rank skipped). Players sorted descending by `.percentage`.

**handle_events:** On Main Menu click:
- Logs winner (multiplayer) or player stats (single).
- Resets all 6 mutable `GameState` fields.
- Returns `"menu"`.

---

## Scoring Components

### `scoring/engine.py`

**`GameState`** — see [Architecture: GameState Schema](./architecture.md#gamestate-schema)

**`Player`** — see [Architecture: Player Schema](./architecture.md#player-schema)

**`calculate_speed_bonus(base_score, time_elapsed, timer_duration) → int`**
```
ratio = max(0.0, 1.0 - time_elapsed / timer_duration)
return int(base_score * ratio)
```
Range: 0 → `base_score`. Linear decay from full bonus at t=0 to zero at t=timer_duration.

---

### `scoring/multiplier.py`

**`get_multiplier(streak: int) → float`**

| Streak | Multiplier |
|--------|-----------|
| 0–1 | 1.0 |
| 2 | 1.5 |
| 3–4 | 2.0 |
| 5+ | 3.0 |

**`apply_streak_multiplier(score: int, streak: int) → int`**
```
return int(score * get_multiplier(streak))
```

---

## Questions Components

### `questions/loader.py`

**`load_questions(path: str) → list[dict]`**
- Reads UTF-8 JSON file at `path`.
- Validates each record has required fields: `question_text`, `options` (list of 4), `correct_index` (int 0–3), `category` (`"Politics"` or `"History"`).
- Silently skips invalid records with a `logging.warning`.
- Calls `sys.exit()` on file-not-found, parse failure, or non-array root.

### `questions/bank.py`

**`draw_questions(questions: list, category: str, n: int = 10) → list`**
- Filters by `category`.
- Calls `sys.exit()` if fewer than `n` matching questions exist.
- Returns `random.sample(filtered, n)` — no duplicates.

---

## Design Patterns

| Pattern | Where used |
|---------|-----------|
| Template Method | `Screen` base class with `handle_events / update / draw` |
| State Object | `GameState` dataclass shared across all screens |
| Lazy Initialization | `_ensure_fonts()` pattern in every screen |
| Guard Clause | `draw()` early-returns on invalid state (e.g., `if not game_state.players: return`) |
| Strategy (implicit) | `ResultsScreen` branches on `selected_mode` for draw strategy |
