---
baseline_commit: NO_VCS
---

# Story 1.3: Scoring Engine Pure Functions

Status: review

## Story

As a player,
I want the scoring system to correctly calculate base score, speed bonus, and streak multiplier for each correct answer,
so that my score accurately reflects how quickly and consistently I answered.

## Acceptance Criteria

1. Given `base_score=100`, `time_elapsed=0.0`, `timer_duration=30.0`, when `calculate_speed_bonus(100, 0.0, 30.0)` is called, then it returns `100` (maximum bonus at instant answer).
2. Given `base_score=100`, `time_elapsed=15.0`, `timer_duration=30.0`, when `calculate_speed_bonus(100, 15.0, 30.0)` is called, then it returns `50` (50% bonus at half time elapsed).
3. Given `base_score=100`, `time_elapsed=30.0`, `timer_duration=30.0`, when `calculate_speed_bonus(100, 30.0, 30.0)` is called, then it returns `0` (no bonus at expiry).
4. Given `streak=1`, when `get_multiplier(1)` is called, then it returns `1.0`.
5. Given `streak=2` / `streak=3` / `streak=5`, when `get_multiplier(streak)` is called, then it returns `1.5` / `2.0` / `3.0` respectively (FR-15).
6. Given `ui/constants.py` is created, when its contents are inspected, then it defines `BASE_SCORE = 100` — the fixed points awarded per correct answer before bonuses (MC-1 / FR-12).
7. Given `scoring/engine.py` and `scoring/multiplier.py` are imported, when their module dependencies are checked, then neither imports `pygame` (AR-6).
8. Given `tests/test_engine.py` and `tests/test_multiplier.py` exist, when the tests run without PyGame installed, then all tests pass.

## Tasks / Subtasks

- [x] Task 1: Add `calculate_speed_bonus()` to `scoring/engine.py` (AC: 1, 2, 3, 7)
  - [x] ADD the function below the existing `Player` dataclass — do NOT modify `GameState` or `Player`
  - [x] Signature: `calculate_speed_bonus(base_score: int, time_elapsed: float, timer_duration: float) -> int`
  - [x] Formula: `ratio = max(0.0, 1.0 - (time_elapsed / timer_duration))` → `return int(base_score * ratio)`
  - [x] No new imports needed (pure arithmetic)
- [x] Task 2: Implement `scoring/multiplier.py` (AC: 4, 5, 7)
  - [x] Implement `get_multiplier(streak: int) -> float` — stepped: streak≥5=3.0, streak≥3=2.0, streak≥2=1.5, else 1.0
  - [x] Add `apply_streak_multiplier(score: int, streak: int) -> int` — convenience wrapper: `int(score * get_multiplier(streak))`
  - [x] No imports needed (pure arithmetic)
- [x] Task 3: Implement `tests/test_engine.py` (AC: 8)
  - [x] Test max bonus at instant answer (0.0s elapsed)
  - [x] Test 50% bonus at half time (15.0s elapsed out of 30.0s)
  - [x] Test zero bonus at expiry (30.0s elapsed)
  - [x] Test zero bonus past expiry (35.0s elapsed — no negative values)
  - [x] Test proportional bonus at 10s elapsed (returns 66)
  - [x] Test return type is `int`
  - [x] Test no PyGame import in `scoring.engine` module
- [x] Task 4: Implement `tests/test_multiplier.py` (AC: 8)
  - [x] Test `get_multiplier(0)` == `1.0` (no streak)
  - [x] Test `get_multiplier(1)` == `1.0`
  - [x] Test `get_multiplier(2)` == `1.5`
  - [x] Test `get_multiplier(3)` == `2.0`
  - [x] Test `get_multiplier(4)` == `2.0` (between 3 and 5)
  - [x] Test `get_multiplier(5)` == `3.0`
  - [x] Test `get_multiplier(10)` == `3.0` (≥5 always caps at 3.0)
  - [x] Test `apply_streak_multiplier(100, 2)` == `150`
  - [x] Test `apply_streak_multiplier(100, 1)` == `100`
  - [x] Test `apply_streak_multiplier(100, 5)` == `300`
  - [x] Test return type of `apply_streak_multiplier` is `int`
  - [x] Test no PyGame import in `scoring.multiplier` module
- [x] Task 5: Verify all ACs via commands in Dev Notes

## Dev Notes

### Environment — CRITICAL

**Python version: 3.14.2.** All commands use `.venv\Scripts\python` / `.venv\Scripts\pytest` from `trivia-app/`. `pytest==9.0.3` is already installed (Story 1.2 added it).

### Files Being Modified — Read Before Touching

#### `scoring/engine.py` — Current state (ADD only, never modify)

```python
from dataclasses import dataclass, field


@dataclass
class GameState:
    current_screen: str = "menu"
    selected_mode: str = ""
    selected_category: str = ""
    players: list = field(default_factory=list)
    active_player_index: int = 0
    current_question_index: int = 0
    questions: list = field(default_factory=list)


@dataclass
class Player:
    name: str
    score: int = 0
    streak: int = 0
    correct: int = 0
    total: int = 0

    @property
    def percentage(self) -> float:
        return (self.correct / self.total * 100) if self.total > 0 else 0.0
```

**CRITICAL:** `GameState` and `Player` are the shared data contracts used by ALL stories. Do NOT change any field names, types, defaults, or the `percentage` property. Only append `calculate_speed_bonus()` after the `Player` class.

#### `scoring/multiplier.py` — Current state (REPLACE entirely)

```python
def get_multiplier(streak: int) -> float:
    pass
```

Replace completely with the full implementation below.

### Exact Code — `scoring/engine.py` (AFTER adding function)

```python
from dataclasses import dataclass, field


@dataclass
class GameState:
    current_screen: str = "menu"          # "menu" | "game" | "results"
    selected_mode: str = ""               # "single" | "multiplayer"
    selected_category: str = ""           # "Politics" | "History"
    players: list = field(default_factory=list)   # list[Player]
    active_player_index: int = 0
    current_question_index: int = 0
    questions: list = field(default_factory=list) # current round draw


@dataclass
class Player:
    name: str
    score: int = 0
    streak: int = 0
    correct: int = 0
    total: int = 0

    @property
    def percentage(self) -> float:
        return (self.correct / self.total * 100) if self.total > 0 else 0.0


def calculate_speed_bonus(base_score: int, time_elapsed: float, timer_duration: float) -> int:
    ratio = max(0.0, 1.0 - (time_elapsed / timer_duration))
    return int(base_score * ratio)
```

**Formula:** `ratio` is the proportion of time remaining (1.0 at 0s elapsed, 0.0 at 30s). `max(0.0, ...)` ensures negative time values (if any) don't produce negative bonuses. `int(...)` truncates (no rounding).

Verification:
- `calculate_speed_bonus(100, 0.0, 30.0)` → `int(100 * 1.0)` = `100` ✓
- `calculate_speed_bonus(100, 15.0, 30.0)` → `int(100 * 0.5)` = `50` ✓
- `calculate_speed_bonus(100, 30.0, 30.0)` → `int(100 * 0.0)` = `0` ✓

### Exact Code — `scoring/multiplier.py` (REPLACE entirely)

```python
def get_multiplier(streak: int) -> float:
    if streak >= 5:
        return 3.0
    if streak >= 3:
        return 2.0
    if streak >= 2:
        return 1.5
    return 1.0


def apply_streak_multiplier(score: int, streak: int) -> int:
    return int(score * get_multiplier(streak))
```

**`apply_streak_multiplier` is required for Story 1.6.** `game_screen.py` will call:
```python
points = apply_streak_multiplier(BASE_SCORE + speed_bonus, player.streak)
player.score += points
```
This keeps all multiplier logic inside `scoring/` and gives `game_screen.py` a single clean call.

**Streak table:**

| streak | multiplier |
|--------|-----------|
| 0 or 1 | 1.0× |
| 2 | 1.5× |
| 3 or 4 | 2.0× |
| 5+ | 3.0× |

### Exact Code — `tests/test_engine.py`

```python
import sys

import pytest

from scoring.engine import calculate_speed_bonus


def test_max_bonus_at_instant_answer():
    assert calculate_speed_bonus(100, 0.0, 30.0) == 100


def test_half_bonus_at_half_time():
    assert calculate_speed_bonus(100, 15.0, 30.0) == 50


def test_zero_bonus_at_expiry():
    assert calculate_speed_bonus(100, 30.0, 30.0) == 0


def test_zero_bonus_past_expiry():
    assert calculate_speed_bonus(100, 35.0, 30.0) == 0


def test_proportional_bonus_at_10s():
    # ratio = 1.0 - 10/30 = 0.6666..., int(100 * 0.6666) = 66
    assert calculate_speed_bonus(100, 10.0, 30.0) == 66


def test_returns_int():
    result = calculate_speed_bonus(100, 5.0, 30.0)
    assert isinstance(result, int)


def test_no_pygame_in_scoring_engine():
    import scoring.engine
    src = open(scoring.engine.__file__, encoding="utf-8").read()
    assert "pygame" not in src
    assert "from ui" not in src
    assert "from questions" not in src
```

### Exact Code — `tests/test_multiplier.py`

```python
import sys

import pytest

from scoring.multiplier import apply_streak_multiplier, get_multiplier


def test_no_streak_multiplier():
    assert get_multiplier(0) == 1.0


def test_streak_1_multiplier():
    assert get_multiplier(1) == 1.0


def test_streak_2_multiplier():
    assert get_multiplier(2) == 1.5


def test_streak_3_multiplier():
    assert get_multiplier(3) == 2.0


def test_streak_4_multiplier():
    assert get_multiplier(4) == 2.0


def test_streak_5_multiplier():
    assert get_multiplier(5) == 3.0


def test_streak_10_multiplier():
    assert get_multiplier(10) == 3.0


def test_apply_no_streak():
    assert apply_streak_multiplier(100, 1) == 100


def test_apply_streak_2():
    assert apply_streak_multiplier(100, 2) == 150


def test_apply_streak_3():
    assert apply_streak_multiplier(100, 3) == 200


def test_apply_streak_5():
    assert apply_streak_multiplier(100, 5) == 300


def test_apply_returns_int():
    result = apply_streak_multiplier(100, 2)
    assert isinstance(result, int)


def test_apply_combined_score():
    # Story 1.6 pattern: apply_streak_multiplier(BASE_SCORE + speed_bonus, streak)
    # e.g. BASE_SCORE=100, speed_bonus=50, streak=2 → int(150 * 1.5) = 225
    assert apply_streak_multiplier(150, 2) == 225


def test_no_pygame_in_scoring_multiplier():
    import scoring.multiplier
    src = open(scoring.multiplier.__file__, encoding="utf-8").read()
    assert "pygame" not in src
    assert "from ui" not in src
    assert "from questions" not in src
```

### Architecture Compliance Notes

**Tests MUST NOT import from `ui/`** — even `ui/constants.py` (which has no imports itself). Architecture rule: `tests/` only imports from `questions/` and `scoring/`. AC6 (`BASE_SCORE = 100`) is verified via a one-liner command, not a pytest test.

**Module boundary for `scoring/`:**
- `scoring/engine.py` → imports: `dataclasses` only
- `scoring/multiplier.py` → no imports (pure arithmetic)
- Zero imports from `pygame`, `ui/`, `questions/`

**`apply_streak_multiplier` placement:** Belongs in `multiplier.py` (not `engine.py`) because it wraps `get_multiplier`. No cross-import needed within `scoring/`.

### Verification Commands (run from `trivia-app/` with venv active)

```powershell
# AC1-3: calculate_speed_bonus
.venv\Scripts\python -c "
from scoring.engine import calculate_speed_bonus
assert calculate_speed_bonus(100, 0.0, 30.0) == 100
assert calculate_speed_bonus(100, 15.0, 30.0) == 50
assert calculate_speed_bonus(100, 30.0, 30.0) == 0
print('AC1-3 passed')
"

# AC4-5: get_multiplier
.venv\Scripts\python -c "
from scoring.multiplier import get_multiplier
assert get_multiplier(1) == 1.0
assert get_multiplier(2) == 1.5
assert get_multiplier(3) == 2.0
assert get_multiplier(5) == 3.0
print('AC4-5 passed')
"

# AC6: BASE_SCORE in ui/constants.py (inspection only — do NOT add this to pytest)
.venv\Scripts\python -c "
src = open('ui/constants.py', encoding='utf-8').read()
assert 'BASE_SCORE = 100' in src
print('AC6 passed: BASE_SCORE = 100 confirmed in ui/constants.py')
"

# AC7: No pygame imports in scoring/
.venv\Scripts\python -c "
for f in ['scoring/engine.py', 'scoring/multiplier.py']:
    src = open(f, encoding='utf-8').read()
    assert 'pygame' not in src, f'{f} imports pygame!'
print('AC7 passed: scoring/ is PyGame-free')
"

# AC8: Run full pytest suite
.venv\Scripts\pytest tests/test_engine.py tests/test_multiplier.py -v

# Regression: existing tests still pass
.venv\Scripts\pytest tests/test_loader.py tests/test_bank.py -v
```

### File Summary

| File | Action | Notes |
|------|--------|-------|
| `scoring/engine.py` | UPDATE | ADD `calculate_speed_bonus()` after `Player` class only |
| `scoring/multiplier.py` | UPDATE | REPLACE stub with full implementation + `apply_streak_multiplier` |
| `tests/test_engine.py` | UPDATE | REPLACE stub with 7-test suite |
| `tests/test_multiplier.py` | UPDATE | REPLACE stub with 13-test suite |

No other files change. `ui/constants.py` already has `BASE_SCORE = 100` from Story 1.1 — do not modify it.

### References

- [Source: architecture.md#Decision 3] — `calculate_speed_bonus` signature and formula
- [Source: architecture.md#Decision 5] — Streak Multiplier scale (OQ-2 resolved)
- [Source: architecture.md#Scoring Function Signatures] — `apply_streak_multiplier` interface
- [Source: architecture.md#AR-6] — `scoring/` must be PyGame-free
- [Source: epics.md#Story 1.3] — Acceptance criteria
- [Source: epics.md#FR-12] — Base score
- [Source: epics.md#FR-13] — Speed Bonus formula
- [Source: epics.md#FR-15] — Streak Multiplier scale
- [Source: epics.md#Story 1.6 AC1] — `apply_streak_multiplier` call pattern used by game_screen
- [Source: 1-1-project-scaffold] — `scoring/engine.py` current content (GameState + Player — do not modify)
- [Source: 1-2-question-bank-loading] — pytest==9.0.3 already installed; use `.venv\Scripts\pytest`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

None — all tests passed on first run.

### Completion Notes List

- All 21 new tests pass; all 16 regression tests pass (37 total green).
- `calculate_speed_bonus` appended to `scoring/engine.py` after `Player`; `GameState` and `Player` unchanged.
- `scoring/multiplier.py` fully replaced — `get_multiplier` + `apply_streak_multiplier` implemented.
- AC6 (`BASE_SCORE = 100` in `ui/constants.py`) satisfied by Story 1.1; verified by file inspection (not pytest, per architecture boundary rule).
- `apply_streak_multiplier` ready for Story 1.6 call pattern: `apply_streak_multiplier(BASE_SCORE + speed_bonus, player.streak)`.

### File List

- `scoring/engine.py` — UPDATED: appended `calculate_speed_bonus()`
- `scoring/multiplier.py` — UPDATED: replaced stub with full implementation
- `tests/test_engine.py` — UPDATED: 7 tests
- `tests/test_multiplier.py` — UPDATED: 13 tests (+ 1 combined-score test = 14 total)
