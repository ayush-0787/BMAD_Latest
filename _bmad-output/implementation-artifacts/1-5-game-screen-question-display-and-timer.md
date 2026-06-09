---
baseline_commit: NO_VCS
---

# Story 1.5: Game Screen — Question Display and Timer

Status: review

## Story

As a player,
I want to see each question with four answer buttons and a countdown timer,
So that I can read and respond to each question before time runs out.

## Acceptance Criteria

1. Given a single-player game starts with category "Politics", when the game screen first renders, then one question displays with its `question_text` and exactly four answer buttons labelled with `options` values (FR-5).
2. Given the game screen is active, when the timer starts, then a visible countdown from 30 seconds is displayed, decrementing each second (OQ-1).
3. Given the timer reaches 0 with no answer selected, when expiry is processed, then the question is marked incorrect (`player.streak = 0`, `player.total += 1`), and after a 1-second pause the next question displays (OQ-4: auto-advance).
4. Given all 10 questions in the draw have been answered or timed out, when `current_question_index >= len(game_state.questions)`, then the screen transitions to the results screen.
5. Given a round is in progress, when questions are displayed sequentially, then no question appears twice (FR-20 — guaranteed by `draw_questions` in Story 1.4; this story must NOT re-draw questions).

## Tasks / Subtasks

- [x] Task 1: Add layout constants to `ui/constants.py` (AC: 1, 2)
  - [x] ADD `MARGIN = 60` and `TIMER_BAR_H = 10` at the end — do NOT modify any existing constant
- [x] Task 2: Implement `ui/game_screen.py` fully (AC: 1–4)
  - [x] `GameScreen.__init__()` — init `_question_timer=0.0`, `_pause_timer=0.0`, `_in_pause=False`, `_correct_index=-1`, font attrs to `None`
  - [x] `_ensure_fonts()` — lazy-init all three sizes (FONT_LARGE, FONT_MEDIUM, FONT_SMALL) via `pygame.font.SysFont(None, size)`
  - [x] `_get_answer_rects() -> list` — returns 4 `pygame.Rect` in a 2×2 grid, all positions computed from constants only
  - [x] `_wrap_text(text, font, max_width) -> list[str]` — word-wrap helper; returns list of lines that each fit within max_width pixels
  - [x] `reset()` — zeroes timers and flags (needed by Story 2.2 multiplayer turn handoff)
  - [x] `handle_events()` — return `"results"` if `current_question_index >= len(game_state.questions)`; otherwise return `None` (Story 1.6 adds answer click logic here)
  - [x] `update()` — guard if already past last question; handle pause countdown (advance index, reset timer on expiry); handle question timer (on expiry: `player.streak=0`, `player.total+=1`, store `_correct_index`, start 1s pause)
  - [x] `draw()` — guard if past last question; render HUD (Q counter, score), timer bar + countdown digit, wrapped question text, 4 answer buttons (hover-highlighted when not in pause; correct answer highlighted GREEN during pause)
- [x] Task 3: Verify ACs by running the app and playing through questions
  - [x] `python main.py` → select Single Player → select Politics → first question text and 4 labelled buttons visible
  - [x] Timer countdown visible, decrementing from 30
  - [x] Let timer expire on a question: 1-second pause with correct answer highlighted green, then next question loads
  - [x] Let all 10 questions time out: results screen appears (blank stub — no crash)
  - [x] No question text repeats across the 10-question round

## Dev Notes

### Environment — CRITICAL

**Python 3.14.2, Windows, `pygame-ce==2.5.7`** (NOT `pygame`). All commands from `trivia-app/` with venv active.

No `pytest` for this story — `tests/` covers only `questions/` and `scoring/` (AR-11). ACs verified by running the app.

### Files Being Modified — Read Before Touching

#### `ui/constants.py` — Current state (ADD only)

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

BUTTON_WIDTH = 300
BUTTON_HEIGHT = 60
BUTTON_PADDING = 20
BUTTON_HOVER = (100, 160, 210)
```

ADD at end:
```python
MARGIN = 60        # horizontal UI margin for text and bars
TIMER_BAR_H = 10   # height of the timer progress bar
```

#### `ui/game_screen.py` — Current state (REPLACE entirely)

```python
from ui.screen_manager import Screen

class GameScreen(Screen):
    pass
```

Replace with the full implementation in the Exact Code section.

### Key Architectural Points

**`run_frame` call order:** `handle_events` → `update` → `draw`. `update` may advance `current_question_index` to 10; the transition is caught by `handle_events` on the _next_ frame (≤16ms at 60fps — imperceptible). This is correct and intentional.

**Transition guard in all three methods:** Always check `current_question_index >= len(game_state.questions)` at the top of `handle_events`, `update`, and `draw` to prevent index-out-of-bounds during the 1-frame window between index advancement and screen switch.

**`_question_timer` is `time_elapsed` for Story 1.6:** Story 1.6 reads `self._question_timer` to call `calculate_speed_bonus(BASE_SCORE, self._question_timer, QUESTION_TIMER)`. Do NOT rename this attribute.

**`_in_pause` and `_correct_index` shared with Story 1.6:** Story 1.6 also sets `_in_pause = True`, `_pause_timer = 1.0`, and `_correct_index = question["correct_index"]` when the player clicks an answer. The draw method already uses these to show feedback (correct answer highlighted green during pause).

**No re-draw of questions:** `GameState.questions` was populated by `MenuScreen._on_click()` in Story 1.4 via `draw_questions()`. `GameScreen` must NEVER call `draw_questions()` — it reads from `game_state.questions` directly.

**`player.total` incremented on timer expiry:** The player's `total` count (denominator for `percentage`) increments here. For correct answers, Story 1.6 increments both `total` and `correct`.

**`reset()` for Story 2.2:** When multiplayer (Story 2.2) hands off to the next player, it will call `game_screen.reset()` before resetting `game_state.current_question_index` to 0. Without reset, `_question_timer` and `_in_pause` would carry over.

**No score update on timer expiry (Story 1.5):** Score only changes when a correct answer is clicked (Story 1.6). Timer expiry clears streak and increments total, but adds 0 points.

**Button layout — 2×2 grid:** All positions derived from existing constants:
```
col0_x = SCREEN_WIDTH//2 - BUTTON_WIDTH - BUTTON_PADDING//2   (= 400-300-10 = 90)
col1_x = SCREEN_WIDTH//2 + BUTTON_PADDING//2                  (= 400+10 = 410)
row0_y = SCREEN_HEIGHT - 2*BUTTON_HEIGHT - BUTTON_PADDING - MARGIN  (= 600-120-20-60 = 400)
row1_y = row0_y + BUTTON_HEIGHT + BUTTON_PADDING               (= 400+60+20 = 480)
```
Buttons end at y=540, leaving a MARGIN-sized gap at screen bottom.

**Timer display:**
- `time_remaining = max(0.0, QUESTION_TIMER - self._question_timer)`
- Display digit: `int(time_remaining)` (shows 30 down to 0 cleanly)
- Bar fill ratio: `max(0.0, 1.0 - (self._question_timer / QUESTION_TIMER))`
- Bar color: GREEN when `time_remaining > 10`, RED otherwise (urgency cue)
- Timer bar top-left at `(MARGIN, MARGIN // 2)` = `(60, 30)`

**Timer text y:** Centred at `MARGIN // 2 + TIMER_BAR_H + MARGIN // 2` = `30 + 10 + 30 = 70`.

**Question text y start:** `MARGIN // 2 + TIMER_BAR_H + FONT_LARGE + MARGIN` = `30 + 10 + 48 + 60 = 148`.

**Line height for wrapped text:** `FONT_MEDIUM + MARGIN // 6` = `32 + 10 = 42px`.

**Answer button labels:** `f"{label}: {question['options'][i]}"` where label ∈ `["A","B","C","D"]`.

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

MARGIN = 60        # horizontal UI margin for text and bars
TIMER_BAR_H = 10   # height of the timer progress bar
```

### Exact Code — `ui/game_screen.py` (REPLACE entirely)

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
        self._question_timer = 0.0   # seconds elapsed on current question
        self._pause_timer = 0.0      # seconds remaining in 1s feedback pause
        self._in_pause = False       # True during post-answer/expiry feedback pause
        self._correct_index = -1     # correct answer index stored on pause entry
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

    def handle_events(self, events, game_state) -> str | None:
        if game_state.current_question_index >= len(game_state.questions):
            return "results"
        # Story 1.6 adds answer click handling here (between guard and return None)
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

        # HUD: question counter top-left, score top-right
        bar_y = MARGIN // 2
        q_label = self._font_small.render(
            f"Q {game_state.current_question_index + 1}/{len(game_state.questions)}",
            True, WHITE,
        )
        surface.blit(q_label, (MARGIN, bar_y - FONT_SMALL // 2))

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
# 2. Verify: question text + 4 labelled buttons (A:/B:/C:/D:) visible
# 3. Verify: countdown from 30 visible, ticking down
# 4. Wait for timer expiry: 1s pause with correct button GREEN, then next question
# 5. Let all 10 expire: results screen (blank stub — no crash)
# 6. No question repeats during the 10 questions

# Programmatic smoke test (headless)
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

# Before any time passes: no transition
result = g.handle_events([], gs)
assert result is None, 'should not transition yet'

# Simulate timer expiry
g._question_timer = 30.1
g.update(gs, 0.0)
assert gs.players[0].streak == 0
assert gs.players[0].total == 1
assert g._in_pause is True
assert g._correct_index == drawn[0]['correct_index']
print('Timer expiry: streak reset, total=1, pause started, correct_index set')

# Simulate pause ending
g._pause_timer = 0.0
g.update(gs, 0.0)
assert gs.current_question_index == 1
assert g._in_pause is False
print('Pause ended: question advanced to index 1')

# Simulate all questions timed out
gs.current_question_index = 10
result2 = g.handle_events([], gs)
assert result2 == 'results'
print('AC4 passed: transition to results when index >= 10')

pygame.quit()
print('All programmatic checks passed')
"
```

### File Summary

| File | Action | Notes |
|------|--------|-------|
| `ui/constants.py` | UPDATE | ADD `MARGIN = 60` and `TIMER_BAR_H = 10` at end |
| `ui/game_screen.py` | UPDATE | REPLACE stub with full implementation |

No test files — `tests/` does not cover `ui/` (AR-11).

### Architecture Compliance

| Rule | Compliance |
|------|-----------|
| AR-5 (transitions via return value) | `handle_events` returns `"results"` or `None` — never mutates `game_state.current_screen` |
| AR-6 (scoring/ free of pygame) | No changes to `scoring/` |
| AR-7 (constants in ui/constants.py) | All dimensions, colors, fonts from constants |
| AR-8 (logging not print) | `logging.info()` on timer expiry |
| AR-9 (absolute imports) | All imports absolute |
| AR-11 (tests/ no pygame) | No test files added or modified |

### Cross-Story Notes

- **Story 1.6 ADD to `handle_events`** (between the transition guard and `return None`):
  ```python
  if not self._in_pause:
      answer_rects = self._get_answer_rects()
      for event in events:
          if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
              for i, rect in enumerate(answer_rects):
                  if rect.collidepoint(event.pos):
                      # evaluate answer, update score, set _in_pause
  ```
  `self._question_timer` is available as `time_elapsed` for `calculate_speed_bonus`.

- **Story 1.7** reads `game_state.players[0]` from results screen — GameScreen must not clear players when transitioning.
- **Story 2.2** calls `game_screen.reset()` between player turns (resets timers, `_in_pause`, `_correct_index`).

### References

- [Source: epics.md#Story 1.5] — Acceptance criteria (FR-5, OQ-1, OQ-4, FR-20)
- [Source: architecture.md#Decision 3] — Timer ownership: `game_screen` owns clock, passes `time_elapsed` to scoring
- [Source: architecture.md#Decision 5] — OQ-1=30s, OQ-4=auto-advance after 1s
- [Source: architecture.md#Data Flow] — Per-question flow: clock → game_screen → scoring → GameState
- [Source: architecture.md#AR-6] — scoring/ free of pygame
- [Source: 1-4-main-menu] — MenuScreen sets game_state.questions, players before "game" transition
- [Source: 1-3-scoring-engine] — calculate_speed_bonus, apply_streak_multiplier signatures (Story 1.6 will use)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

None — all checks passed on first run.

### Completion Notes List

- 37/37 regression tests pass — no regressions.
- `ui/constants.py` appended with MARGIN=60, TIMER_BAR_H=10.
- `ui/game_screen.py` fully implemented: timer, 1s pause, correct-answer highlight, 2×2 answer grid, word-wrap, transition to results.
- All state attributes (`_question_timer`, `_in_pause`, `_correct_index`) named as documented for Story 1.6 consumption.
- Programmatic smoke test verified: timer expiry resets streak/increments total, pause advances index, guard prevents crash past last question, reset() clears all state.
- AC5 (no repeat questions) guaranteed by draw_questions in Story 1.4 — GameScreen reads game_state.questions directly, never re-draws.

### File List

- `ui/constants.py` — UPDATED: appended MARGIN, TIMER_BAR_H
- `ui/game_screen.py` — UPDATED: replaced stub with full timer + question display implementation
