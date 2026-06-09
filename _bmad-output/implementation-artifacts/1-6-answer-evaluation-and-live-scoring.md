---
baseline_commit: NO_VCS
---

# Story 1.6: Answer Evaluation and Live Scoring

Status: review

## Story

As a player,
I want my score, streak, and last multiplier to update instantly when I click an answer,
So that I get immediate feedback and can track my progress through the round.

## Acceptance Criteria

1. Given the player clicks the correct answer button, when the answer is evaluated, then `player.score` increases by `int((BASE_SCORE + speed_bonus) * streak_multiplier)`, `player.correct` increments by 1, and `player.streak` increments by 1.
2. Given the player clicks an incorrect answer button, when the answer is evaluated, then `player.score` does not change, `player.streak` resets to 0, and the correct answer is highlighted for 1 second before advancing (same 1s pause + GREEN highlight as timer expiry — OQ-4 behaviour).
3. Given the player just answered correctly with `streak == 2`, when the game screen redraws, then displayed score, streak (2), and last multiplier (1.5×) all reflect updated values within the same rendered frame (NFR-2 / SM-2). Handle_events runs before draw in run_frame — this is automatic.
4. Given answer evaluation triggers scoring calls, when `calculate_speed_bonus` and `get_multiplier` are invoked, then `self._question_timer` is passed as `time_elapsed` — `scoring/` never accesses the PyGame clock directly (AR-6). Note: epics.md says "pygame.time.get_ticks()" but the correct implementation is `self._question_timer` per Story 1.5 architecture.
5. Given all 10 questions are answered, when `player.total == 10`, then the screen transitions to the results screen with `GameState` intact (transition already handled by the existing `current_question_index >= len(questions)` guard in `handle_events`).

## Tasks / Subtasks

- [x] Task 1: Add new imports to `ui/game_screen.py` (AC: 1, 4)
  - [x] Add `from scoring.engine import calculate_speed_bonus` after the `import logging` block
  - [x] Add `from scoring.multiplier import apply_streak_multiplier, get_multiplier` after the scoring.engine import
  - [x] Add `BASE_SCORE` to the existing `from ui.constants import (...)` block (alphabetical order: after `ACCENT,`)
- [x] Task 2: Add `_last_multiplier` state attribute (AC: 3)
  - [x] In `__init__`: add `self._last_multiplier: float = 1.0` after `self._correct_index = -1`
  - [x] In `reset()`: add `self._last_multiplier = 1.0` after `self._correct_index = -1`
- [x] Task 3: Implement answer click handling in `handle_events` (AC: 1, 2, 4, 5)
  - [x] Replace the `# Story 1.6 adds answer click handling here` comment with the click logic block
  - [x] Guard: only process clicks when `not self._in_pause`
  - [x] On left-click hitting a button rect: set `_correct_index`, evaluate correctness, update player state, enter 1s pause
  - [x] Correct path: `player.streak += 1`, compute speed_bonus and points, `player.score += points`, `player.correct += 1`, `self._last_multiplier = get_multiplier(player.streak)`
  - [x] Incorrect path: `player.streak = 0` (do NOT touch `_last_multiplier`)
  - [x] Both paths: `player.total += 1`, `self._question_timer = 0.0`, `self._in_pause = True`, `self._pause_timer = 1.0`
  - [x] Add `logging.info` for both correct and incorrect paths
- [x] Task 4: Update `draw()` HUD to show streak and last multiplier (AC: 3)
  - [x] Add a centred `FONT_SMALL` label between the Q counter and Score: `f"Streak: {player.streak} | x{self._last_multiplier:.1f}"`
  - [x] Position: `midtop=(SCREEN_WIDTH // 2, bar_y - FONT_SMALL // 2)` — same row as other HUD elements
- [x] Task 5: Verify ACs by running the app and programmatic checks
  - [x] `python main.py` → play through: answer correctly twice → streak=2, score >0, HUD shows "x1.5"
  - [x] Answer incorrectly → streak resets to 0 on HUD, score unchanged
  - [x] Correct answer highlights GREEN during 1s pause; incorrect answer also highlights correct answer GREEN
  - [x] After all 10 answered, results screen appears with final score intact
  - [x] Run programmatic smoke test (see Verification Commands section)

## Dev Notes

### Environment — CRITICAL

**Python 3.14.2, Windows, `pygame-ce==2.5.7`** (NOT `pygame`). All commands from `trivia-app/` with venv active.

No new test files — `tests/` covers only `questions/` and `scoring/` (AR-11). ACs verified by running the app and programmatic headless checks.

### Scope — Single File Only

This story modifies **only `ui/game_screen.py`**. No other file changes.

- `ui/constants.py` — unchanged (BASE_SCORE already defined there)
- `scoring/engine.py` — unchanged
- `scoring/multiplier.py` — unchanged
- `tests/` — unchanged (no new tests, existing 37 must still pass)

### Scoring Formula — Exact Implementation

```
new_streak = player.streak + 1          # increment FIRST
speed_bonus = calculate_speed_bonus(BASE_SCORE, self._question_timer, QUESTION_TIMER)
points = apply_streak_multiplier(BASE_SCORE + speed_bonus, new_streak)
player.score += points
player.correct += 1
player.streak = new_streak
self._last_multiplier = get_multiplier(new_streak)
```

In code this is just:
```python
player.streak += 1
speed_bonus = calculate_speed_bonus(BASE_SCORE, self._question_timer, QUESTION_TIMER)
points = apply_streak_multiplier(BASE_SCORE + speed_bonus, player.streak)
player.score += points
player.correct += 1
self._last_multiplier = get_multiplier(player.streak)
```

**Why streak += 1 first:** AC3 says after answering correctly with `streak==2` (the post-increment value), the multiplier is 1.5×. `get_multiplier(2) = 1.5`. So the multiplier is computed against the new streak value.

**Worked example:**
- streak was 1, answer correct: `player.streak → 2`, `get_multiplier(2) = 1.5`, points = `int((100 + speed_bonus) * 1.5)`
- streak was 4, answer correct: `player.streak → 5`, `get_multiplier(5) = 3.0`, points = `int((100 + speed_bonus) * 3.0)`
- streak was 0, answer correct: `player.streak → 1`, `get_multiplier(1) = 1.0`, points = `int((100 + speed_bonus) * 1.0)` = 100 + speed_bonus

**`_last_multiplier` on incorrect:** Do NOT reset `_last_multiplier` when wrong. It shows the last actually-applied multiplier, which doesn't change on incorrect answers. This way the player can see what they had before the streak broke.

### Architecture Points

**NFR-2 / Same-frame update (AC3):** `run_frame` in `screen_manager.py` calls `handle_events → update → draw` in that order within one frame. Score/streak/multiplier are mutated in `handle_events`, so `draw` in the same frame immediately sees the updated values. No additional work needed.

**AR-6 compliance:** `calculate_speed_bonus` and `apply_streak_multiplier` receive plain Python values (`int`, `float`). `scoring/` never imports or touches pygame. `self._question_timer` (accumulated via `dt` in `update()`) is the elapsed time — do NOT use `pygame.time.get_ticks()`.

**AR-5 compliance:** `handle_events` returns `None` after processing a click (never returns "results" mid-click). The transition to results happens on the next frame when `current_question_index >= len(questions)` after the pause ends and `update()` increments the index past 10.

**`_question_timer` reset on click:** Reset to 0.0 when entering pause. Keeps the timer bar frozen at "full" during the 1s feedback pause (same as timer expiry path in Story 1.5 `update()`).

**Pause state shared with `update()` + `draw()`:** Both `_in_pause=True` / `_pause_timer=1.0` / `_correct_index` are already consumed correctly by `update()` (advances index after pause) and `draw()` (shows correct answer GREEN). No changes needed to those methods.

**`player.total` in both paths:** Increment `player.total` unconditionally after the correct/incorrect branch. Timer expiry already does this in `update()` for missed questions.

### Current State of `ui/game_screen.py` (Story 1.5 complete)

```python
import logging

import pygame

from ui.constants import (
    ACCENT, BLACK, BUTTON_HEIGHT, BUTTON_HOVER, BUTTON_PADDING, BUTTON_WIDTH,
    FONT_LARGE, FONT_MEDIUM, FONT_SMALL, GREEN, GREY, MARGIN, QUESTION_TIMER,
    RED, SCREEN_HEIGHT, SCREEN_WIDTH, TIMER_BAR_H, WHITE,
)
from ui.screen_manager import Screen


class GameScreen(Screen):
    def __init__(self):
        self._question_timer = 0.0
        self._pause_timer = 0.0
        self._in_pause = False
        self._correct_index = -1
        self._font_large = None
        self._font_medium = None
        self._font_small = None

    ...

    def reset(self) -> None:
        self._question_timer = 0.0
        self._pause_timer = 0.0
        self._in_pause = False
        self._correct_index = -1

    def handle_events(self, events, game_state) -> str | None:
        if game_state.current_question_index >= len(game_state.questions):
            return "results"
        # Story 1.6 adds answer click handling here (between guard and return None)
        return None

    def update(self, game_state, dt: float) -> None:
        ...  # unchanged — handles pause countdown and timer expiry

    def draw(self, surface, game_state) -> None:
        ...
        # HUD: Q counter top-left, score top-right (no streak/multiplier yet)
        bar_y = MARGIN // 2
        q_label = ...
        score_label = ...
        ...
```

### Exact Code — `ui/game_screen.py` (REPLACE entirely)

```python
import logging

import pygame

from scoring.engine import calculate_speed_bonus
from scoring.multiplier import apply_streak_multiplier, get_multiplier
from ui.constants import (
    ACCENT, BASE_SCORE, BLACK, BUTTON_HEIGHT, BUTTON_HOVER, BUTTON_PADDING, BUTTON_WIDTH,
    FONT_LARGE, FONT_MEDIUM, FONT_SMALL, GREEN, GREY, MARGIN, QUESTION_TIMER,
    RED, SCREEN_HEIGHT, SCREEN_WIDTH, TIMER_BAR_H, WHITE,
)
from ui.screen_manager import Screen


class GameScreen(Screen):
    def __init__(self):
        self._question_timer = 0.0   # seconds elapsed on current question
        self._pause_timer = 0.0      # seconds remaining in 1s feedback pause
        self._in_pause = False       # True during post-answer/expiry feedback pause
        self._correct_index = -1     # correct answer index stored on pause entry
        self._last_multiplier = 1.0  # streak multiplier applied on last correct answer
        self._font_large = None
        self._font_medium = None
        self._font_small = None

    def _ensure_fonts(self) -> None:
        if self._font_large is None:
            self._font_large = pygame.font.SysFont(None, FONT_LARGE)
            self._font_medium = pygame.font.SysFont(None, FONT_MEDIUM)
            self._font_small = pygame.font.SysFont(None, FONT_SMALL)

    def _get_answer_rects(self) -> list:
        col0_x = SCREEN_WIDTH // 2 - BUTTON_WIDTH - BUTTON_PADDING // 2
        col1_x = SCREEN_WIDTH // 2 + BUTTON_PADDING // 2
        row0_y = SCREEN_HEIGHT - 2 * BUTTON_HEIGHT - BUTTON_PADDING - MARGIN
        row1_y = row0_y + BUTTON_HEIGHT + BUTTON_PADDING
        return [
            pygame.Rect(col0_x, row0_y, BUTTON_WIDTH, BUTTON_HEIGHT),
            pygame.Rect(col1_x, row0_y, BUTTON_WIDTH, BUTTON_HEIGHT),
            pygame.Rect(col0_x, row1_y, BUTTON_WIDTH, BUTTON_HEIGHT),
            pygame.Rect(col1_x, row1_y, BUTTON_WIDTH, BUTTON_HEIGHT),
        ]

    def _wrap_text(self, text: str, font, max_width: int) -> list:
        words = text.split()
        lines, current = [], ""
        for word in words:
            test = f"{current} {word}".strip()
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def reset(self) -> None:
        self._question_timer = 0.0
        self._pause_timer = 0.0
        self._in_pause = False
        self._correct_index = -1
        self._last_multiplier = 1.0

    def handle_events(self, events, game_state) -> str | None:
        if game_state.current_question_index >= len(game_state.questions):
            return "results"
        if not self._in_pause:
            question = game_state.questions[game_state.current_question_index]
            player = game_state.players[game_state.active_player_index]
            answer_rects = self._get_answer_rects()
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for i, rect in enumerate(answer_rects):
                        if rect.collidepoint(event.pos):
                            self._correct_index = question["correct_index"]
                            if i == self._correct_index:
                                player.streak += 1
                                speed_bonus = calculate_speed_bonus(
                                    BASE_SCORE, self._question_timer, QUESTION_TIMER
                                )
                                points = apply_streak_multiplier(
                                    BASE_SCORE + speed_bonus, player.streak
                                )
                                player.score += points
                                player.correct += 1
                                self._last_multiplier = get_multiplier(player.streak)
                                logging.info(
                                    "Correct: Q%d player=%s points=%d streak=%d mult=%.1f",
                                    game_state.current_question_index,
                                    player.name,
                                    points,
                                    player.streak,
                                    self._last_multiplier,
                                )
                            else:
                                player.streak = 0
                                logging.info(
                                    "Wrong: Q%d player=%s streak reset",
                                    game_state.current_question_index,
                                    player.name,
                                )
                            player.total += 1
                            self._question_timer = 0.0
                            self._in_pause = True
                            self._pause_timer = 1.0
                            return None
        return None

    def update(self, game_state, dt: float) -> None:
        if game_state.current_question_index >= len(game_state.questions):
            return
        if self._in_pause:
            self._pause_timer -= dt
            if self._pause_timer <= 0.0:
                self._in_pause = False
                self._pause_timer = 0.0
                game_state.current_question_index += 1
                self._question_timer = 0.0
                self._correct_index = -1
        else:
            self._question_timer += dt
            if self._question_timer >= QUESTION_TIMER:
                player = game_state.players[game_state.active_player_index]
                question = game_state.questions[game_state.current_question_index]
                player.streak = 0
                player.total += 1
                self._correct_index = question["correct_index"]
                self._question_timer = 0.0
                self._in_pause = True
                self._pause_timer = 1.0
                logging.info(
                    "Timer expired: Q%d player=%s streak reset",
                    game_state.current_question_index,
                    player.name,
                )

    def draw(self, surface, game_state) -> None:
        self._ensure_fonts()
        if game_state.current_question_index >= len(game_state.questions):
            return

        question = game_state.questions[game_state.current_question_index]
        player = game_state.players[game_state.active_player_index]
        time_remaining = max(0.0, QUESTION_TIMER - self._question_timer)

        surface.fill(BLACK)

        # HUD: question counter top-left, streak+multiplier centre, score top-right
        bar_y = MARGIN // 2
        q_label = self._font_small.render(
            f"Q {game_state.current_question_index + 1}/{len(game_state.questions)}",
            True, WHITE,
        )
        surface.blit(q_label, (MARGIN, bar_y - FONT_SMALL // 2))

        streak_label = self._font_small.render(
            f"Streak: {player.streak} | x{self._last_multiplier:.1f}",
            True, WHITE,
        )
        surface.blit(streak_label, streak_label.get_rect(
            midtop=(SCREEN_WIDTH // 2, bar_y - FONT_SMALL // 2)
        ))

        score_label = self._font_small.render(f"Score: {player.score}", True, WHITE)
        surface.blit(score_label, score_label.get_rect(
            topright=(SCREEN_WIDTH - MARGIN, bar_y - FONT_SMALL // 2)
        ))

        # Timer progress bar (full-width background, coloured fill)
        bar_full_w = SCREEN_WIDTH - 2 * MARGIN
        ratio = max(0.0, 1.0 - (self._question_timer / QUESTION_TIMER))
        bar_fill_w = int(bar_full_w * ratio)
        bar_color = GREEN if time_remaining > 10 else RED
        pygame.draw.rect(surface, GREY, pygame.Rect(MARGIN, bar_y, bar_full_w, TIMER_BAR_H))
        if bar_fill_w > 0:
            pygame.draw.rect(surface, bar_color, pygame.Rect(MARGIN, bar_y, bar_fill_w, TIMER_BAR_H))

        # Timer countdown digit (centred below bar)
        timer_center_y = bar_y + TIMER_BAR_H + MARGIN // 2
        timer_surf = self._font_large.render(str(int(time_remaining)), True, WHITE)
        surface.blit(timer_surf, timer_surf.get_rect(center=(SCREEN_WIDTH // 2, timer_center_y)))

        # Question text (word-wrapped, centred)
        text_y = timer_center_y + FONT_LARGE // 2 + MARGIN // 2
        max_text_w = SCREEN_WIDTH - 2 * MARGIN
        for line in self._wrap_text(question["question_text"], self._font_medium, max_text_w):
            surf = self._font_medium.render(line, True, WHITE)
            surface.blit(surf, surf.get_rect(center=(SCREEN_WIDTH // 2, text_y)))
            text_y += FONT_MEDIUM + MARGIN // 6

        # Answer buttons (2×2 grid)
        answer_rects = self._get_answer_rects()
        mouse_pos = pygame.mouse.get_pos()
        labels = ["A", "B", "C", "D"]
        for i, rect in enumerate(answer_rects):
            if self._in_pause:
                color = GREEN if i == self._correct_index else ACCENT
            else:
                color = BUTTON_HOVER if rect.collidepoint(mouse_pos) else ACCENT
            pygame.draw.rect(surface, color, rect, border_radius=8)
            opt_text = f"{labels[i]}: {question['options'][i]}"
            label_surf = self._font_small.render(opt_text, True, WHITE)
            surface.blit(label_surf, label_surf.get_rect(center=rect.center))
```

### Verification Commands (run from `trivia-app/` with venv active)

```powershell
# Regression — all 37 existing tests still pass
.venv\Scripts\pytest tests/ -v

# AC1-5: Visual verification
.venv\Scripts\python main.py
# 1. Select Single Player → Politics
# 2. Click correct answer on Q1: score > 0, HUD "Streak: 1 | x1.0"
# 3. Click correct on Q2: "Streak: 2 | x1.5", score increased by ~150+
# 4. Click correct on Q3: "Streak: 3 | x2.0"
# 5. Click wrong answer: streak resets "Streak: 0 | x2.0" (last_mult unchanged), correct button GREEN for 1s
# 6. Let timer expire: same 1s pause + GREEN highlight + streak/total update
# 7. Answer all 10: results screen appears with final score intact

# Programmatic smoke test (headless pygame)
.venv\Scripts\python -c "
import pygame
pygame.init()
surface = pygame.display.set_mode((800, 600))

from scoring.engine import GameState, Player
from questions.loader import load_questions
from questions.bank import draw_questions
from ui.game_screen import GameScreen

qs = load_questions('data/questions_politics.json')
drawn = draw_questions(qs, 'Politics')

gs = GameState()
gs.players = [Player('P1')]
gs.questions = drawn
gs.current_question_index = 0

g = GameScreen()

# --- AC1: Correct answer click ---
correct_idx = drawn[0]['correct_index']
# Map button index to pixel position (2x2 grid)
col0_x = 800//2 - 300 - 10  # 90
col1_x = 800//2 + 10         # 410
row0_y = 600 - 120 - 20 - 60 # 400
row1_y = row0_y + 60 + 20    # 480
centres = [
    (col0_x + 150, row0_y + 30),
    (col1_x + 150, row0_y + 30),
    (col0_x + 150, row1_y + 30),
    (col1_x + 150, row1_y + 30),
]
g._question_timer = 10.0  # simulate 10s elapsed
click_pos = centres[correct_idx]
event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=click_pos)
result = g.handle_events([event], gs)
assert result is None
assert gs.players[0].correct == 1
assert gs.players[0].total == 1
assert gs.players[0].streak == 1
assert gs.players[0].score > 0
assert g._in_pause is True
assert g._last_multiplier == 1.0
print(f'AC1 correct click: score={gs.players[0].score}, streak=1, mult=1.0 OK')

# --- Pause end: advance to Q2 ---
g._pause_timer = 0.0
g.update(gs, 0.0)
assert gs.current_question_index == 1
assert g._in_pause is False

# --- AC1 again: Q2 correct → streak=2, mult=1.5 ---
correct_idx2 = drawn[1]['correct_index']
g._question_timer = 5.0
event2 = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=centres[correct_idx2])
g.handle_events([event2], gs)
assert gs.players[0].streak == 2
assert g._last_multiplier == 1.5
print(f'AC3 streak=2 mult=1.5: score={gs.players[0].score} OK')

# --- Pause end: advance to Q3 ---
g._pause_timer = 0.0
g.update(gs, 0.0)

# --- AC2: Wrong answer click ---
score_before = gs.players[0].score
wrong_idx = (drawn[2]['correct_index'] + 1) % 4
event3 = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=centres[wrong_idx])
g.handle_events([event3], gs)
assert gs.players[0].score == score_before
assert gs.players[0].streak == 0
assert gs.players[0].total == 3
assert g._in_pause is True
assert g._correct_index == drawn[2]['correct_index']
print(f'AC2 wrong click: score unchanged={score_before}, streak=0, correct_index set OK')

# --- AC5: All 10 answered → results ---
gs.current_question_index = 10
result_final = g.handle_events([], gs)
assert result_final == 'results'
assert len(gs.players) == 1  # GameState intact
print('AC5 results transition with GameState intact OK')

pygame.quit()
print('All programmatic checks passed')
"
```

### File Summary

| File | Action | Notes |
|------|--------|-------|
| `ui/game_screen.py` | UPDATE | Add imports, `_last_multiplier` state, answer click logic, HUD streak+multiplier label |

No other files change. No test files added.

### Architecture Compliance

| Rule | Compliance |
|------|-----------|
| AR-5 (transitions via return value) | Returns `None` after click; "results" only from transition guard — never direct mutation |
| AR-6 (scoring/ free of pygame) | `calculate_speed_bonus` and `apply_streak_multiplier` receive `float`/`int` — no pygame objects |
| AR-7 (constants in ui/constants.py) | `BASE_SCORE`, `QUESTION_TIMER` imported from constants — no magic numbers |
| AR-8 (logging not print) | `logging.info()` on correct and wrong answer paths |
| AR-9 (absolute imports) | `from scoring.engine import ...`, `from scoring.multiplier import ...` — absolute |
| AR-11 (tests/ no pygame) | No test files added or modified |

### Cross-Story Notes

- **Story 1.7** reads `game_state.players[0].score`, `.correct`, `.total`, `.percentage` from results screen — all correctly populated here.
- **Story 2.2** calls `game_screen.reset()` between multiplayer turns — `_last_multiplier = 1.0` is now included in reset.

### References

- [Source: epics.md#Story 1.6] — Acceptance criteria (FR-6, FR-12, FR-13, FR-14, FR-15, FR-16, NFR-2, AR-6)
- [Source: architecture.md#Decision 3] — Timer ownership: game_screen owns clock, passes `time_elapsed` to scoring
- [Source: 1.5 dev notes] — `_question_timer` is `time_elapsed`; `_in_pause`/`_correct_index` shared state contract
- [Source: scoring/engine.py] — `calculate_speed_bonus(base_score, time_elapsed, timer_duration) -> int`
- [Source: scoring/multiplier.py] — `apply_streak_multiplier(score, streak) -> int`; `get_multiplier(streak) -> float`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

None — all checks passed on first run.

### Completion Notes List

- 37/37 regression tests pass — no regressions.
- Added imports: `calculate_speed_bonus` from `scoring.engine`, `apply_streak_multiplier` / `get_multiplier` from `scoring.multiplier`, `BASE_SCORE` added to constants import.
- `_last_multiplier: float = 1.0` added to `__init__` and `reset()`.
- `handle_events` click logic: MOUSEBUTTONDOWN → find button rect → correct path increments streak first, then computes speed_bonus and points via scoring functions, updates score/correct/last_multiplier; wrong path resets streak only; both paths enter 1s pause.
- `draw()` HUD now shows `"Streak: {n} | x{mult:.1f}"` centred between Q counter and Score.
- Programmatic smoke test confirmed: AC1 score=166 at 10s elapsed (streak 1, 1.0×); AC3 score=440 at 5s elapsed (streak 2, 1.5×); AC2 wrong click leaves score unchanged, streak=0, _last_multiplier stays 1.5; AC4 scoring/ confirmed free of pygame; AC5 results transition with GameState intact.
- `_last_multiplier` deliberately NOT reset on incorrect answers — shows last-applied value so player knows what multiplier they had.

### File List

- `ui/game_screen.py` — UPDATED: added scoring imports, `_last_multiplier` state, answer click logic in `handle_events`, streak+multiplier HUD label in `draw()`
