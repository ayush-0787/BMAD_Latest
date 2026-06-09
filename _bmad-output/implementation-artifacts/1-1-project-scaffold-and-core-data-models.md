# Story 1.1: Project Scaffold and Core Data Models

Status: review

## Story

As a developer,
I want the complete project scaffold created with all packages, `__init__.py` files, `GameState` dataclass, and `Player` dataclass implemented,
so that every subsequent story has the correct module structure and shared data contracts to build on.

## Acceptance Criteria

1. Given the project root `trivia-app/` with all directories and `__init__.py` files created, when I run `python main.py`, then the app starts without import errors.
2. Given `scoring/engine.py` is implemented, when I import `GameState` and `Player`, then `GameState()` defaults to `current_screen="menu"`, `players=[]`; `Player(name="Test")` defaults to `score=0`, `streak=0`, `correct=0`, `total=0`.
3. Given a `Player` with `correct=7` and `total=10`, when `player.percentage` is accessed, then it returns `70.0`.
4. Given a `Player` with `total=0`, when `player.percentage` is accessed, then it returns `0.0` with no `ZeroDivisionError`.
5. Given the full project structure, when module dependencies are inspected, then `scoring/` imports nothing from `ui/` or `questions/`; `questions/` imports nothing from `ui/` or `scoring/`; all imports are absolute.

## Tasks / Subtasks

- [x] Task 1: Create directory structure and all `__init__.py` stubs (AC: 1, 5)
  - [x] Create `trivia-app/` root directory
  - [x] Create `trivia-app/questions/__init__.py` (empty)
  - [x] Create `trivia-app/scoring/__init__.py` (empty)
  - [x] Create `trivia-app/ui/__init__.py` (empty)
  - [x] Create `trivia-app/tests/__init__.py` (empty)
  - [x] Create `trivia-app/data/` directory (empty, populated in Story 1.2)
- [x] Task 2: Implement `scoring/engine.py` with `GameState` and `Player` dataclasses (AC: 2, 3, 4)
  - [x] Define `GameState` dataclass with all fields and defaults
  - [x] Define `Player` dataclass with `percentage` property
  - [x] Verify no imports from `ui/` or `questions/`
- [x] Task 3: Create `ui/constants.py` with all shared constants (AC: 1, 5)
  - [x] Define screen dimensions, FPS, timer, colours, font sizes, BASE_SCORE
- [x] Task 4: Create stub files for all remaining modules (AC: 1, 5)
  - [x] `questions/loader.py` — function stub
  - [x] `questions/bank.py` — function stub
  - [x] `scoring/multiplier.py` — function stub
  - [x] `ui/screen_manager.py` — `Screen` base class + `ScreenManager` stub
  - [x] `ui/menu_screen.py` — `MenuScreen` stub
  - [x] `ui/game_screen.py` — `GameScreen` stub
  - [x] `ui/results_screen.py` — `ResultsScreen` stub
- [x] Task 5: Implement `main.py` (AC: 1)
  - [x] `pygame.init()`, create display surface, instantiate `ScreenManager`, run one frame, exit cleanly
- [x] Task 6: Create `requirements.txt` and `.gitignore`
  - [x] `pip install pygame` then `pip freeze > requirements.txt`
  - [x] Standard Python `.gitignore`
- [x] Task 7: Verify AC5 — no cross-module imports
  - [x] Confirm `scoring/` has zero imports from `ui/` or `questions/`
  - [x] Confirm `questions/` has zero imports from `ui/` or `scoring/`
  - [x] Confirm all imports are absolute (no `from .module import ...`)

## Dev Notes

### Project Location

Create `trivia-app/` as a subdirectory of the current working directory (i.e., alongside `_bmad-output/`).

### Exact File Contents Required

#### `scoring/engine.py` — FULLY IMPLEMENT THIS FILE

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
```

**CRITICAL:** `scoring/engine.py` must NOT import `pygame`, `ui`, or `questions`. Only stdlib imports allowed (`dataclasses`).

#### `ui/constants.py` — FULLY IMPLEMENT THIS FILE

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
```

All screen files in `ui/` must import constants from here. **No magic numbers anywhere in `ui/`.**

#### `ui/screen_manager.py` — STUB (implement interface only)

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
    def __init__(self):
        from ui.menu_screen import MenuScreen
        from ui.game_screen import GameScreen
        from ui.results_screen import ResultsScreen
        self.screens = {
            "menu": MenuScreen(),
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

**CRITICAL TRANSITION RULE:** `handle_events()` returns a screen name string (or `None`). `ScreenManager.run_frame()` is the ONLY place that sets `game_state.current_screen`. Screen classes MUST NEVER mutate `game_state.current_screen` directly — they only return the target screen name.

#### `ui/menu_screen.py` — STUB

```python
from ui.screen_manager import Screen


class MenuScreen(Screen):
    pass
```

#### `ui/game_screen.py` — STUB

```python
from ui.screen_manager import Screen


class GameScreen(Screen):
    pass
```

#### `ui/results_screen.py` — STUB

```python
from ui.screen_manager import Screen


class ResultsScreen(Screen):
    pass
```

#### `questions/loader.py` — STUB

```python
import logging


def load_questions(path: str) -> list:
    pass
```

#### `questions/bank.py` — STUB

```python
def draw_questions(questions: list, category: str, n: int = 10) -> list:
    pass
```

#### `scoring/multiplier.py` — STUB

```python
def get_multiplier(streak: int) -> float:
    pass
```

#### `main.py` — MINIMAL WORKING ENTRY POINT

```python
import logging
import sys
import pygame
from ui.screen_manager import ScreenManager
from ui.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

logging.basicConfig(level=logging.DEBUG)


def main():
    pygame.init()
    surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Python Trivia App")
    clock = pygame.time.Clock()
    manager = ScreenManager()

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        manager.run_frame(events, surface, dt)
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
```

### Project Structure — Complete Expected Tree

```
trivia-app/
├── main.py
├── requirements.txt
├── .gitignore
├── data/                          # empty for now; Story 1.2 adds JSON files
├── questions/
│   ├── __init__.py                # empty
│   ├── loader.py                  # stub
│   └── bank.py                    # stub
├── scoring/
│   ├── __init__.py                # empty
│   ├── engine.py                  # FULLY IMPLEMENTED (GameState + Player)
│   └── multiplier.py              # stub
├── ui/
│   ├── __init__.py                # empty
│   ├── constants.py               # FULLY IMPLEMENTED
│   ├── screen_manager.py          # Screen base class + ScreenManager (implemented)
│   ├── menu_screen.py             # stub
│   ├── game_screen.py             # stub
│   └── results_screen.py         # stub
└── tests/
    ├── __init__.py                # empty
    ├── test_loader.py             # stub (Story 1.2 fills this)
    ├── test_bank.py               # stub (Story 1.2 fills this)
    ├── test_engine.py             # stub (Story 1.3 fills this)
    └── test_multiplier.py         # stub (Story 1.3 fills this)
```

### Architecture Compliance Rules (ENFORCE ALL)

**Module boundary rules — zero exceptions:**
- `scoring/` → may only import stdlib (`dataclasses`, `logging`, etc.) and other `scoring/` modules
- `questions/` → may only import stdlib and other `questions/` modules
- `ui/` → may import from `scoring/` and `questions/`, but NOT vice versa
- `main.py` → composition root; imports only from `ui/`

**Import style — absolute only:**
```python
# CORRECT
from scoring.engine import GameState, Player
from ui.constants import SCREEN_WIDTH

# WRONG — never use relative imports
from .engine import GameState
```

**Logging — never use print():**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
# Use logging.debug(), logging.info(), logging.warning(), logging.error()
# Never: print("debug message")
```

### Setup Commands

```bash
# Run from project root (same level as trivia-app/)
mkdir trivia-app
cd trivia-app
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install pygame
pip freeze > requirements.txt
```

### `.gitignore` Contents

```
.venv/
__pycache__/
*.pyc
*.pyo
.pytest_cache/
*.egg-info/
dist/
build/
```

### Verification Commands (run from `trivia-app/` with venv active)

```bash
# AC1: App launches without import errors
python main.py

# AC2-4: Dataclass behaviour
python -c "
from scoring.engine import GameState, Player
g = GameState()
assert g.current_screen == 'menu'
assert g.players == []
p = Player(name='Test')
assert p.score == 0 and p.streak == 0 and p.correct == 0 and p.total == 0
p2 = Player(name='X', correct=7, total=10)
assert p2.percentage == 70.0
p3 = Player(name='Y', correct=0, total=0)
assert p3.percentage == 0.0
print('All dataclass assertions passed')
"

# AC5: No cross-module imports
python -c "
import scoring.engine, scoring.multiplier
import questions.loader, questions.bank
import sys
mods = sys.modules
assert 'pygame' not in str(mods.get('scoring.engine', '').__file__ or '')
print('Module boundary check passed')
"
```

### Project Structure Notes

- `trivia-app/` is the Python project root — run all commands from inside it
- `data/` directory is created empty now; Story 1.2 creates the JSON question files
- `tests/` stubs are created now so the test runner can discover them; Stories 1.2 and 1.3 fill in actual test cases
- The `Screen` base class and `ScreenManager` wiring are implemented here (not stubbed) because `main.py` depends on them to avoid import errors

### References

- [Source: architecture.md#Starter Template Evaluation] — Manual scaffold, init commands
- [Source: architecture.md#Decision 1] — GameState dataclass definition
- [Source: architecture.md#Decision 4] — Player dataclass definition
- [Source: architecture.md#Decision 2] — Screen base class and ScreenManager pattern
- [Source: architecture.md#Implementation Patterns] — Naming conventions, import style, logging, constants location
- [Source: architecture.md#Project Structure & Boundaries] — Complete directory tree, module dependency rules
- [Source: epics.md#Story 1.1] — Acceptance criteria
- [Source: epics.md#Story 1.3] — BASE_SCORE = 100 must be in ui/constants.py (MC-1 fix)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- pygame 2.6.1 has no pre-built wheel for Python 3.14; used `pygame-ce==2.5.7` (community edition, same API, same import name `pygame`)

### Completion Notes List

- AC1: `python main.py` launches without import errors (headless import chain verified via ScreenManager instantiation test)
- AC2-4: All dataclass assertions passed via verification script
- AC5: Module boundary check passed — `scoring/` and `questions/` import nothing from `ui/`
- `pygame-ce` used instead of `pygame` due to Python 3.14 wheel availability; `requirements.txt` lists `pygame-ce==2.5.7`

### File List

- trivia-app/main.py (NEW)
- trivia-app/requirements.txt (NEW)
- trivia-app/.gitignore (NEW)
- trivia-app/questions/__init__.py (NEW)
- trivia-app/questions/loader.py (NEW)
- trivia-app/questions/bank.py (NEW)
- trivia-app/scoring/__init__.py (NEW)
- trivia-app/scoring/engine.py (NEW)
- trivia-app/scoring/multiplier.py (NEW)
- trivia-app/ui/__init__.py (NEW)
- trivia-app/ui/constants.py (NEW)
- trivia-app/ui/screen_manager.py (NEW)
- trivia-app/ui/menu_screen.py (NEW)
- trivia-app/ui/game_screen.py (NEW)
- trivia-app/ui/results_screen.py (NEW)
- trivia-app/tests/__init__.py (NEW)
- trivia-app/tests/test_loader.py (NEW)
- trivia-app/tests/test_bank.py (NEW)
- trivia-app/tests/test_engine.py (NEW)
- trivia-app/tests/test_multiplier.py (NEW)

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-06-09 | Story implemented — all 7 tasks complete, all ACs verified | claude-sonnet-4-6 |
