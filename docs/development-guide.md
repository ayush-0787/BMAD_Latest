# Development Guide — Python Trivia App

**Generated:** 2026-06-09 | **Scan level:** Deep

---

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.14.2 | Windows 11 |
| OS | Windows 11 | Desktop only; pygame-ce is cross-platform but project was developed on Windows |

---

## Setup

```powershell
# 1. Navigate to the project root
cd C:\Users\A974997\BMAD\trivia-app

# 2. Create virtual environment
python -m venv .venv

# 3. Activate
.venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt
```

### requirements.txt breakdown

| Package | Version | Purpose |
|---------|---------|---------|
| `pygame-ce` | 2.5.7 | Game engine — rendering, input, event loop |
| `pytest` | 9.0.3 | Test runner |
| `colorama` | 0.4.6 | Terminal color (pytest output) |
| `iniconfig` | 2.3.0 | pytest config parsing |
| `packaging` | 26.2 | pytest dependency |
| `pluggy` | 1.6.0 | pytest plugin system |
| `Pygments` | 2.20.0 | pytest syntax highlighting |

> **Important:** Install `pygame-ce`, NOT `pygame`. Both packages expose the same API, but they cannot be installed simultaneously. If `pygame` is already installed, uninstall it before installing `pygame-ce`.

---

## Running the Game

```powershell
# From trivia-app/ with .venv activated
python main.py
```

The game opens an 800×600 window. Close with the window X button or click Quit on the main menu.

---

## Running Tests

```powershell
# From trivia-app/ with .venv activated
python -m pytest tests/ -v
```

Expected output: **37 tests passed**.

```
tests/test_bank.py::test_politics_filter_excludes_history PASSED
tests/test_bank.py::test_history_filter_excludes_politics PASSED
tests/test_bank.py::test_returns_exactly_n_questions PASSED
tests/test_bank.py::test_no_duplicate_questions PASSED
tests/test_bank.py::test_randomness_varies_across_draws PASSED
tests/test_bank.py::test_insufficient_questions_triggers_sys_exit PASSED
tests/test_bank.py::test_empty_list_triggers_sys_exit PASSED
tests/test_engine.py::test_max_bonus_at_instant_answer PASSED
tests/test_engine.py::test_half_bonus_at_half_time PASSED
tests/test_engine.py::test_zero_bonus_at_expiry PASSED
tests/test_engine.py::test_zero_bonus_past_expiry PASSED
tests/test_engine.py::test_proportional_bonus_at_10s PASSED
tests/test_engine.py::test_returns_int PASSED
tests/test_engine.py::test_no_pygame_in_scoring_engine PASSED
tests/test_loader.py::test_valid_file_loads_successfully PASSED
... (22 more)
```

Tests do **not** require a display or pygame initialization. They cover `questions/` and `scoring/` only.

---

## Project Structure Rules

When making changes, follow these constraints enforced by architecture rules:

### AR-5: Screen transitions via return string only

`handle_events()` must return a string key to trigger a screen change. Never call `ScreenManager` directly from a screen, never set `game_state.current_screen` from a screen.

```python
# Correct
def handle_events(self, events, game_state) -> str | None:
    if condition:
        return "results"
    return None

# Wrong
def handle_events(self, events, game_state) -> str | None:
    if condition:
        game_state.current_screen = "results"  # AR-5 violation
```

### AR-6: Keep scoring/ PyGame-free

Never import `pygame` in `scoring/engine.py` or `scoring/multiplier.py`. This is verified by the `test_no_pygame_in_scoring_engine` and `test_no_pygame_in_scoring_multiplier` tests.

### AR-7: Constants in ui/constants.py

No numeric or color literals in screen files. Add new constants to `ui/constants.py` and import them.

### AR-8: Use logging, not print

```python
import logging
logging.info("Message: %s", value)  # correct
print("Message:", value)             # AR-8 violation
```

### AR-9: Absolute imports

```python
from scoring.engine import GameState   # correct
from ..scoring.engine import GameState  # AR-9 violation
```

### AR-11: No PyGame in tests

Tests under `tests/` must not call `pygame.init()` or import any `ui/` module. Test `scoring/` and `questions/` with pure Python only.

---

## Adding a New Question

Add a record to `data/questions_politics.json` or `data/questions_history.json` following this schema:

```json
{
  "question_text": "Your question here?",
  "options": [
    "Option A",
    "Option B",
    "Option C",
    "Option D"
  ],
  "correct_index": 0,
  "category": "Politics"
}
```

- `correct_index` is 0-based (0 = "Option A", 1 = "Option B", etc.)
- `category` must be exactly `"Politics"` or `"History"` (case-sensitive)
- Each file must contain at least 10 valid questions of its category

---

## Adding a New Screen

1. Create `ui/your_screen.py` extending `Screen`:

```python
import logging
import pygame
from ui.constants import (BLACK, SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, ...)
from ui.screen_manager import Screen

class YourScreen(Screen):
    def __init__(self):
        self._font_medium = None

    def _ensure_fonts(self) -> None:
        if self._font_medium is None:
            self._font_medium = pygame.font.SysFont(None, FONT_MEDIUM)

    def reset(self) -> None:  # optional; implement if you have per-session state
        pass

    def handle_events(self, events, game_state) -> str | None:
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                return "target_screen"
        return None

    def update(self, game_state, dt: float) -> None:
        pass

    def draw(self, surface, game_state) -> None:
        self._ensure_fonts()
        surface.fill(BLACK)
        # render here
```

2. Register in `ui/screen_manager.py`:

```python
from ui.your_screen import YourScreen

self.screens = {
    ...
    "your_screen": YourScreen(),
}
```

3. Return `"your_screen"` from an existing screen's `handle_events` to navigate to it.

---

## PowerShell Smoke Test Pattern

For verifying scoring or state logic without a display:

```powershell
.venv\Scripts\python.exe -c @'
import sys
sys.path.insert(0, '.')
from scoring.engine import GameState, Player
from scoring.multiplier import apply_streak_multiplier

gs = GameState()
gs.players = [Player('Alice'), Player('Bob')]
gs.selected_mode = 'multiplayer'
alice = gs.players[0]
alice.correct = 8
alice.total = 10
print('PASS' if alice.percentage == 80.0 else 'FAIL')
'@
```

> **Note:** Inside `@'...'@` PowerShell single-quoted heredocs, use **single quotes** for all Python string literals. Double quotes are stripped by the PowerShell parser.

---

## Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| `ModuleNotFoundError: No module named 'pygame'` | Using wrong package name | `pip install pygame-ce` (not `pygame`) |
| `SyntaxError` in PowerShell smoke test | Double-quoted string stripped by heredoc | Use single quotes in `@'...'@` blocks |
| `UnicodeEncodeError: charmap` | Unicode character in print string on CP1252 console | Replace non-ASCII characters (e.g., `→`) with ASCII equivalents |
| `sys.exit()` on startup | Question file missing or malformed | Check `data/` files match schema |
| Tests fail after adding screen import | Accidentally imported pygame in `scoring/` | Keep `scoring/` PyGame-free (AR-6) |
