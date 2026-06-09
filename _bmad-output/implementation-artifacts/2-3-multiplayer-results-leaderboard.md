---
baseline_commit: NO_VCS
---

# Story 2.3: Multiplayer Results Leaderboard

Status: review

## Story

As players,
I want to see a ranked leaderboard of all players by score percentage with the winner declared,
So that we know who performed best and can celebrate the outcome.

## Acceptance Criteria

1. Given 3 players finished with percentages 80%, 60%, 70%, when the multiplayer results screen renders, then players are listed in descending percentage order: 80% → 70% → 60% (FR-11).

2. Given the leaderboard is displayed, when the top player is identified, then the highest-percentage player is highlighted (GREEN) and declared "Winner!" in a large header (FR-11).

3. Given two players tie with equal percentages, when the results screen renders, then both are listed at the same rank number with no tiebreaker applied — the next player gets the next sequential rank (dense ranking, FR-11 assumption).

4. Given the player clicks "Main Menu", when navigation is triggered, then all 6 `GameState` mutable fields reset (`players=[]`, `active_player_index=0`, `current_question_index=0`, `questions=[]`, `selected_mode=""`, `selected_category=""`) and the screen transitions to `"menu"`.

5. Given `GameState.selected_mode == "multiplayer"`, when `results_screen.py` renders, then it displays the leaderboard layout (not the single-player win/loss layout) — mode branch confirmed.

6. Given `GameState.selected_mode == "single"` (or anything other than `"multiplayer"`), when `results_screen.py` renders, then it displays the existing single-player layout unchanged — no regression.

## Tasks / Subtasks

- [x] Task 1: Refactor `ui/results_screen.py` — add multiplayer leaderboard path (AC: 1–6)
  - [x] Extract existing `draw()` single-player logic into `_draw_single(surface, game_state)` (no logic change, just encapsulation)
  - [x] Add `_draw_multiplayer(surface, game_state)` — see Dev Notes for full layout spec
  - [x] Update `draw()` to branch: `if game_state.selected_mode == "multiplayer": self._draw_multiplayer(...)` else `self._draw_single(...)`
  - [x] Update `handle_events()` logging: multiplayer branch logs winner name + player count; single-player branch unchanged
  - [x] GameState reset block in `handle_events()` — must remain identical to current (all 6 fields), regardless of mode

- [x] Task 2: Verify ACs by smoke test
  - [x] Programmatic: sort + rank correctness with 3 players (80/60/70 → order 80/70/60, ranks 1/2/3)
  - [x] Programmatic: tie detection — two players at 70%, one at 80% → top two show rank 1 and 2, no rank 3 skipped (dense ranking)
  - [x] Programmatic: mode branch — `selected_mode == "multiplayer"` hits `_draw_multiplayer`; `"single"` hits `_draw_single`
  - [x] Regression: 37/37 existing tests still pass

## Dev Notes

### Architecture Rules in Force

- **AR-5 (Transitions via return string):** `handle_events` returns `"menu"` — no change. ✓
- **AR-6 (PyGame-free scoring):** No `scoring/` changes. `player.percentage` is a pure Python property. ✓
- **AR-7 (Constants in `ui/constants.py`):** No magic numbers. All sizes/colors from constants.
- **AR-8 (logging):** Multiplayer log: `"Results: %d players, winner=%s pct=%.1f%% → main menu"`. Single log: unchanged.
- **AR-9 (Absolute imports):** No new imports needed — existing `results_screen.py` imports already cover all required constants.
- **AR-11 (No PyGame tests):** Sorting/rank logic tested via programmatic smoke test. No test files to create/modify.

### Only one file changes — results_screen.py

Story 2.3 touches **only** `ui/results_screen.py`. No changes to:
- `ui/game_screen.py` — transitions to "results" already correct from Story 2.2
- `ui/screen_manager.py` — no new screens
- `ui/handoff_screen.py` — Story 2.2, complete
- `ui/setup_screen.py`, `ui/menu_screen.py` — Stories 2.1/2.2, complete
- `scoring/`, `questions/`, `tests/` — AR-6 / AR-11

### Current `results_screen.py` complete state (read before implementing)

The current file (`ui/results_screen.py`) — full content preserved here so the dev doesn't re-read:

```python
class ResultsScreen(Screen):
    def __init__(self):
        self._font_large = None; self._font_medium = None; self._font_small = None

    def _ensure_fonts(self): ...  # lazy pygame.font.SysFont(None, size) for all three

    def _get_menu_button_rect(self) -> pygame.Rect:
        return pygame.Rect(
            SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
            SCREEN_HEIGHT - BUTTON_HEIGHT - MARGIN,   # y = 600 - 60 - 60 = 480
            BUTTON_WIDTH, BUTTON_HEIGHT,
        )

    def handle_events(self, events, game_state) -> str | None:
        if not game_state.players: return None
        menu_rect = self._get_menu_button_rect()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if menu_rect.collidepoint(event.pos):
                    player = game_state.players[0]  # ← log line uses players[0] — update for multi
                    logging.info("Results: player=%s score=%d pct=%.1f%% → main menu", ...)
                    game_state.players = []
                    game_state.active_player_index = 0
                    game_state.current_question_index = 0
                    game_state.questions = []
                    game_state.selected_mode = ""
                    game_state.selected_category = ""
                    return "menu"
        return None

    def update(self, game_state, dt): pass

    def draw(self, surface, game_state) -> None:
        self._ensure_fonts()
        if not game_state.players: return
        player = game_state.players[0]
        pct = player.percentage
        verdict = "You Win!" if pct >= 70.0 else "You Lose"
        verdict_color = GREEN if pct >= 70.0 else RED
        surface.fill(BLACK)
        y = SCREEN_HEIGHT // 6
        # title "Results" → score → pct → verdict → correct count → menu button
```

### Task 1 — Exact implementation plan

**Step A: Extract `_draw_single`** — move ALL existing `draw()` body (after the `if not game_state.players: return` guard) into `_draw_single(self, surface, game_state)`. Zero logic change. This preserves single-player behaviour exactly.

**Step B: Write `_draw_multiplayer`** per layout below.

**Step C: Update `draw()`**:
```python
def draw(self, surface, game_state) -> None:
    self._ensure_fonts()
    if not game_state.players:
        return
    if game_state.selected_mode == "multiplayer":
        self._draw_multiplayer(surface, game_state)
    else:
        self._draw_single(surface, game_state)
```

**Step D: Update `handle_events()` log line** — branch on `selected_mode`:
```python
if game_state.selected_mode == "multiplayer":
    winner = max(game_state.players, key=lambda p: p.percentage)
    logging.info(
        "Results: %d players, winner=%s pct=%.1f%% → main menu",
        len(game_state.players), winner.name, winner.percentage,
    )
else:
    player = game_state.players[0]
    logging.info(
        "Results: player=%s score=%d pct=%.1f%% → main menu",
        player.name, player.score, player.percentage,
    )
# reset block follows — unchanged for both modes
game_state.players = []
game_state.active_player_index = 0
game_state.current_question_index = 0
game_state.questions = []
game_state.selected_mode = ""
game_state.selected_category = ""
return "menu"
```

### `_draw_multiplayer` full layout spec

```
y = SCREEN_HEIGHT // 8            → 75
"Results"                           WHITE,  font_large,  center-x

y += FONT_LARGE + MARGIN // 2     → 75 + 48 + 30 = 153
"Winner: {sorted[0].name}!"         GREEN,  font_large,  center-x

y += FONT_LARGE + MARGIN          → 153 + 48 + 60 = 261
[leaderboard rows, one per player, sorted descending by percentage]
  row text: "{rank}.  {name}   {score}   {pct:.0f}%"
  row color: GREEN if player.percentage == top_pct else WHITE
  y += FONT_MEDIUM + MARGIN // 4  → +32+15 = +47 per row

"Main Menu" button at y=480 (existing _get_menu_button_rect())
```

**Space check (4-player worst case):**
- Last row at y = 261 + 3 × 47 = 402. Button at y = 480. Gap = 78 px. ✓

### Dense ranking algorithm (AC3)

```python
sorted_players = sorted(game_state.players, key=lambda p: p.percentage, reverse=True)
top_pct = sorted_players[0].percentage

prev_pct = None
rank = 0
for player in sorted_players:
    pct = player.percentage
    if pct != prev_pct:
        rank += 1
        prev_pct = pct
    row_color = GREEN if pct == top_pct else WHITE
    row_text = f"{rank}.  {player.name}   {player.score}   {pct:.0f}%"
    ...
```

Dense ranking examples:
- `[80, 70, 60]` → ranks `[1, 2, 3]` ✓
- `[80, 70, 70]` → ranks `[1, 2, 2]` ✓ (both 70% at rank 2)
- `[80, 80, 60]` → ranks `[1, 1, 2]` ✓ (both 80% highlighted GREEN, rank 2 for 60%)

### Tie-at-top highlight rule

Use `pct == top_pct` (not `player is sorted_players[0]`) to correctly highlight ALL tied winners in GREEN. The "Winner: {name}!" header still names only `sorted_players[0]` — acceptable per the AC ("no tiebreaker in v1").

### Winner header when no tie

`sorted_players[0].name` is the player with the highest percentage. In the 3-player AC example (80%, 70%, 60%), `sorted_players[0]` is the 80% player. ✓

### PowerShell smoke test quoting rule (recurring — from Stories 2.1 + 2.2)

Use **single quotes** for all Python string literals inside `.venv\Scripts\python.exe -c @'...'@` heredocs. Double quotes are stripped by the PowerShell parser.

### Constants import (no changes needed)

Current `results_screen.py` already imports:
```python
from ui.constants import (
    ACCENT, BLACK, BUTTON_HEIGHT, BUTTON_HOVER, BUTTON_WIDTH,
    FONT_LARGE, FONT_MEDIUM, FONT_SMALL, GREEN, MARGIN,
    RED, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE,
)
```
All required constants are present. No import changes needed.

## Dev Agent Record

### Debug Log

- PowerShell print with Unicode arrow `→` (U+2192) caused UnicodeEncodeError on CP1252 console. Fixed by using plain ASCII `->` in all print strings.

### Completion Notes

- Refactored `ui/results_screen.py`: existing `draw()` single-player body extracted unchanged into `_draw_single()`; new `_draw_multiplayer()` added with sorted leaderboard, dense ranking, and winner highlight via `pct == top_pct` (tie-safe); `draw()` branches on `selected_mode == "multiplayer"`.
- `handle_events()` logging split: multiplayer path logs `winner.name + player count`; single-player path unchanged. Reset block (all 6 fields) is mode-agnostic and identical for both paths.
- 9 programmatic AC checks passed; 37/37 regression tests green.

## File List

- `ui/results_screen.py` — UPDATED

## Change Log

- 2026-06-09: Story 2.3 implemented — added multiplayer leaderboard path to ResultsScreen with sorted ranking, winner declaration, and mode branch; single-player path preserved unchanged.
