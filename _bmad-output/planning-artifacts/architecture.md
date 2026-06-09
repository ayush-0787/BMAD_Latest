---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
lastStep: 8
status: 'complete'
completedAt: '2026-06-09'
inputDocuments:
  - _bmad-output/planning-artifacts/prds/prd-BMAD-2026-06-08/prd.md
  - _bmad-output/planning-artifacts/briefs/brief-BMAD-2026-06-08/brief.md
workflowType: 'architecture'
project_name: 'Python Trivia App'
user_name: 'A974997'
date: '2026-06-08'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements (20 total):**
Five feature groups — Main Menu (FR-1–3), Single-Player (FR-4–8), Pass-and-Play Multiplayer (FR-9–11), Scoring Engine (FR-12–16), Question Bank (FR-17–20). Core loop: load data → select mode/category → run round(s) → show results.

**Non-Functional Requirements:**
- Live score display must update within one rendered frame of answer submission (FR-16 / SM-2) — hard real-time rendering constraint.
- Missing or malformed JSON halts launch with a user-facing error (FR-17) — startup validation required.
- Malformed question records skipped and logged, not surfaced to player (FR-18) — silent degradation with logging.

**Scale & Complexity:**
- Primary domain: Desktop GUI game (PyGame, Python 3)
- Complexity level: Low-medium
- No networking, persistence, auth, or external APIs
- Complexity concentrated in: event loop design, screen state machine, real-time scoring, and turn isolation for multiplayer

### Technical Constraints & Dependencies

- **PyGame** — sole UI/rendering/input/clock framework; no other GUI lib
- **Python stdlib + PyGame only** — no additional runtime dependencies for v1
- **Three-module boundary (hard constraint from PRD §6.1):** `questions`, `scoring`, `ui` as separate Python modules from day one
- **JSON question bank** — static file, loaded at startup; ~30 questions per category (Politics, History) assumed
- **Windows primary dev/test platform** — PyGame is cross-platform by nature

### Cross-Cutting Concerns Identified

- **Game state ownership** — active player, current question index, per-player scores, and round completion status are needed by UI, scoring, and multiplayer turn management simultaneously
- **Timer shared across modules** — the countdown timer feeds both the UI renderer and the Speed Bonus calculator; must have a single source of truth
- **Open questions to resolve in architecture (OQ-1–4):**
  - OQ-1: Per-question timer duration (assumed 30s)
  - OQ-2: Streak Multiplier scale
  - OQ-3: Shared vs. independent question draw in multiplayer
  - OQ-4: Timer expiry behaviour (auto-advance vs. acknowledge)

## Starter Template Evaluation

### Primary Technology Domain

Python desktop game (PyGame) — no standard boilerplate generator exists. Project scaffold is defined here and becomes Story 1.1.

### Starter Options Considered

No maintained PyGame starter templates exist equivalent to web/mobile generators (create-react-app, expo init, etc.). The correct approach is a manually defined scaffold that enforces the three-module boundary required by PRD §6.1.

### Selected Approach: Manual PyGame Scaffold

**Rationale:** Provides full control over module boundaries, avoids pulling in unnecessary dependencies, and directly implements the hard architectural constraint from the PRD.

**Initialization Commands:**

```bash
mkdir trivia-app && cd trivia-app
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install pygame
```

**Project Structure:**

```
trivia-app/
├── main.py                   # Entry point — initialises PyGame, runs game loop
├── questions/
│   ├── __init__.py
│   ├── loader.py             # JSON loading, validation, startup error handling
│   └── bank.py               # Category filtering, no-repeat random draw
├── scoring/
│   ├── __init__.py
│   ├── engine.py             # Base score, Speed Bonus (clock-based), Streak counter
│   └── multiplier.py         # Streak Multiplier application
├── ui/
│   ├── __init__.py
│   ├── screen_manager.py     # Screen state machine (MENU → GAME → RESULTS)
│   ├── menu_screen.py        # Main Menu rendering + input
│   ├── game_screen.py        # Question display, timer, live score rendering
│   └── results_screen.py     # Single-player verdict / multiplayer leaderboard
├── data/
│   ├── questions_politics.json
│   └── questions_history.json
└── requirements.txt          # pygame==<current>
```

**Architectural Decisions Established by Scaffold:**

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Package structure | 3 packages (`questions`, `scoring`, `ui`) | Hard PRD constraint; keeps v2/v3 additive |
| Entry point | `main.py` | Owns PyGame init, game loop, and screen_manager wiring |
| Data location | `data/` folder | Separate from code; easy to expand |
| Screen management | `screen_manager.py` in `ui/` | Single owner of screen state and game state |
| JSON split by category | Two files | Simpler filtering; no runtime category queries |
| `requirements.txt` | Yes | Reproducible environment |

**Key boundary rules established:**
- `main.py` is the only file that calls `pygame.init()`, manages the display, and drives the main loop tick
- `screen_manager` is the authoritative owner of game state (current screen, active player, scores)
- `scoring.engine` receives the timer value as a parameter — it never reads PyGame's clock directly

**Note:** Project initialization using this scaffold is the first implementation story (Story 1.1).

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- Game state container pattern — `GameState` dataclass (Decision 1)
- Screen state machine pattern — base `Screen` class hierarchy (Decision 2)
- Timer ownership — `game_screen` owns, passes to scoring (Decision 3)
- OQ-1–4 resolved — all PRD open questions closed (Decision 5)

**Important Decisions (Shape Architecture):**
- Player data model — `Player` dataclass (Decision 4)

**Deferred Decisions (Post-MVP):**
- Sound/audio architecture — deferred to v2+
- Persistent leaderboard storage — deferred to v3+
- Online multiplayer transport — deferred to v3+

---

### Decision 1: Game State Container

**Decision:** `GameState` dataclass owned by `screen_manager`, injected into active screen instances.

**Rationale:** Single authoritative source of truth for cross-cutting state. Named fields provide clarity; `@dataclass` gives type safety and zero boilerplate. Solves the shared-state problem identified in Step 2 without global variables.

**Data model:**
```python
@dataclass
class GameState:
    current_screen: str = "menu"          # "menu" | "game" | "results"
    selected_mode: str = ""               # "single" | "multiplayer"
    selected_category: str = ""           # "Politics" | "History"
    players: list = field(default_factory=list)  # list[Player]
    active_player_index: int = 0
    current_question_index: int = 0
    questions: list = field(default_factory=list) # current round draw
```

**Affects:** All three modules read from `GameState`; only `screen_manager` writes to it.

---

### Decision 2: Screen State Machine Pattern

**Decision:** Base `Screen` abstract class with `handle_events()`, `update()`, `draw()` interface. `ScreenManager` holds a dict of screen instances and delegates to the active one each frame.

**Rationale:** Each screen is self-contained. Adding a v2 narrator screen or v3 topic-select screen means one new subclass, zero changes to the game loop. Clean, testable, extensible.

**Pattern:**
```python
class Screen:
    def handle_events(self, events, game_state): ...
    def update(self, game_state, dt): ...
    def draw(self, surface, game_state): ...

class ScreenManager:
    def __init__(self):
        self.screens = {
            "menu": MenuScreen(),
            "game": GameScreen(),
            "results": ResultsScreen(),
        }
    def run_frame(self, events, game_state, surface, dt):
        screen = self.screens[game_state.current_screen]
        screen.handle_events(events, game_state)
        screen.update(game_state, dt)
        screen.draw(surface, game_state)
```

**Affects:** `ui/` package; `main.py` game loop delegates entirely to `ScreenManager`.

---

### Decision 3: Timer Ownership

**Decision:** Timer lives in `game_screen.py`. On each frame it calculates `time_elapsed` using PyGame's clock. On answer submission, it passes `time_elapsed` and `timer_duration` to `scoring.engine.calculate_speed_bonus()` as plain parameters.

**Rationale:** Keeps `scoring` module completely free of PyGame imports — purely functional, independently testable. One-way dependency: UI → scoring. Scoring never reads the clock directly.

**Interface:**
```python
# scoring/engine.py
def calculate_speed_bonus(base_score: int, time_elapsed: float, timer_duration: float) -> int:
    ratio = max(0.0, 1.0 - (time_elapsed / timer_duration))
    return int(base_score * ratio)
```

**Affects:** `ui/game_screen.py` (owns clock), `scoring/engine.py` (receives values as args).

---

### Decision 4: Player Data Model

**Decision:** `Player` dataclass defined in `scoring/engine.py`.

**Rationale:** Named, typed fields. Zero boilerplate. Easy to extend (add `wager` field for v2 Final Trivia mechanic without breaking existing code).

**Data model:**
```python
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

**Affects:** `scoring/engine.py` (definition), `GameState.players` (usage), `ui/results_screen.py` (display).

---

### Decision 5: Open Questions Resolution (OQ-1–4)

All four PRD open questions are resolved here:

| OQ | Question | Decision |
|----|----------|----------|
| OQ-1 | Per-question timer duration | **30 seconds** — constant `QUESTION_TIMER = 30` in `ui/game_screen.py` |
| OQ-2 | Streak Multiplier scale | **Stepped:** streak 2 = 1.5×, streak 3 = 2×, streak 5+ = 3× |
| OQ-3 | Shared vs. independent draw | **Shared draw** — same 10 questions for all players; ensures fair comparison |
| OQ-4 | Timer expiry behaviour | **Auto-advance after 1 second** — correct answer briefly shown, then next question |

**Streak Multiplier implementation:**
```python
# scoring/multiplier.py
def get_multiplier(streak: int) -> float:
    if streak >= 5: return 3.0
    if streak >= 3: return 2.0
    if streak >= 2: return 1.5
    return 1.0
```

---

### Decision Impact Analysis

**Implementation Sequence:**
1. Project scaffold + `GameState` + `Player` dataclasses (foundation)
2. `questions/loader.py` + `questions/bank.py` (data layer, no PyGame dependency)
3. `scoring/engine.py` + `scoring/multiplier.py` (pure logic, no PyGame dependency)
4. `ui/` base `Screen` class + `ScreenManager` + `main.py` game loop
5. `ui/menu_screen.py` (mode + category selection)
6. `ui/game_screen.py` (question display, timer, answer handling, live score)
7. `ui/results_screen.py` (single-player verdict + multiplayer leaderboard)

**Cross-Component Dependencies:**
- `GameState` is the shared contract between all modules — defined first, frozen before implementation
- `scoring` has zero imports from `ui` or `questions` — purely functional
- `questions` has zero imports from `ui` or `scoring` — data layer only
- `ui` imports from both `scoring` (to calculate scores) and `questions` (to get the draw) via `GameState`

## Implementation Patterns & Consistency Rules

**Critical conflict points identified:** 7 areas where agents could diverge.

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Classes | `PascalCase` | `GameState`, `MenuScreen`, `Player` |
| Functions & methods | `snake_case` | `calculate_speed_bonus()`, `handle_events()` |
| Variables | `snake_case` | `active_player_index`, `time_elapsed` |
| Constants | `UPPER_SNAKE_CASE` | `QUESTION_TIMER`, `SCREEN_WIDTH`, `WHITE` |
| Module files | `snake_case.py` | `screen_manager.py`, `game_screen.py` |
| JSON fields | `snake_case` | `"question_text"`, `"correct_index"`, `"category"` |

### Screen Transition Pattern

Screens **never mutate `GameState.current_screen` directly**. `handle_events()` returns `str | None` — a screen name to transition to, or `None` for no change. `ScreenManager.run_frame()` applies the transition.

```python
# CORRECT
class MenuScreen(Screen):
    def handle_events(self, events, game_state) -> str | None:
        if start_clicked:
            return "game"
        return None

# WRONG
class MenuScreen(Screen):
    def handle_events(self, events, game_state):
        game_state.current_screen = "game"  # ❌ direct mutation
```

### Constants Location

All shared UI constants (colors, dimensions, fonts, timing) live in `ui/constants.py`. No magic numbers in screen files.

```python
# ui/constants.py
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
QUESTION_TIMER = 30       # seconds (resolves OQ-1)
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ACCENT = (70, 130, 180)
FONT_LARGE = 48
FONT_MEDIUM = 32
FONT_SMALL = 24
```

### Error Handling Pattern

Two tiers — startup errors halt; runtime errors are caught, logged, and degrade gracefully.

```python
# Startup error — halt (questions/loader.py)
def load_questions(path: str) -> list:
    if not os.path.exists(path):
        sys.exit(f"ERROR: Question bank not found at {path}")

# Runtime error — catch, log, continue
try:
    record = validate_question(raw)
except KeyError as e:
    logging.warning(f"Skipping malformed question: {e}")
    continue
```

### Logging Pattern

Use Python's `logging` module throughout — never bare `print()` except in `main.py` startup messages.

- `DEBUG` — frame-level events
- `INFO` — state transitions
- `WARNING` — skipped/degraded data
- `ERROR` — unexpected failures

### Scoring Function Signatures

All `scoring/engine.py` functions are **pure functions** — no side effects, no PyGame imports, no global state.

```python
# CORRECT
def calculate_speed_bonus(base_score: int, time_elapsed: float, timer_duration: float) -> int: ...
def apply_streak_multiplier(score: int, streak: int) -> int: ...

# WRONG
def calculate_speed_bonus():
    pygame.time.get_ticks()  # ❌ PyGame in scoring module
```

### Import Style

Use absolute imports within packages. No relative imports.

```python
# CORRECT
from scoring.engine import calculate_speed_bonus
from questions.bank import draw_questions

# WRONG
from .engine import calculate_speed_bonus  # ❌
```

### JSON Question Schema

Every question record must match this exact schema — any other shape is skipped and logged:

```json
{
  "question_text": "Who was the first US President?",
  "options": ["Washington", "Adams", "Jefferson", "Hamilton"],
  "correct_index": 0,
  "category": "Politics"
}
```

`category` must be exactly `"Politics"` or `"History"`.

### Enforcement — All AI Agents MUST:


- Follow naming conventions in the table above
- Return transition strings from `handle_events()` — never mutate `GameState.current_screen` directly
- Put all UI constants in `ui/constants.py` — no magic numbers in screen files
- Keep `scoring/` completely free of PyGame imports
- Use `logging`, not `print()`, for all diagnostic output
- Use absolute imports throughout
- Validate question records against the schema before use

## Project Structure & Boundaries

### Complete Project Directory Structure

```
trivia-app/
├── main.py                        # Entry point: PyGame init, game loop, ScreenManager wiring
├── requirements.txt               # pygame==<current>
├── README.md                      # Setup and run instructions
├── .gitignore
│
├── data/
│   ├── questions_politics.json    # FR-17, FR-18, FR-19 — Politics category bank
│   └── questions_history.json     # FR-17, FR-18, FR-19 — History category bank
│
├── questions/
│   ├── __init__.py
│   ├── loader.py                  # FR-17: JSON loading + startup validation
│   └── bank.py                    # FR-19: category filter, FR-20: no-repeat random draw
│
├── scoring/
│   ├── __init__.py
│   ├── engine.py                  # FR-12: base score, FR-13: speed bonus, FR-14: streak tracking
│   │                              # Also defines: GameState, Player dataclasses
│   └── multiplier.py              # FR-15: streak multiplier scale (1.5×/2×/3×)
│
├── ui/
│   ├── __init__.py
│   ├── constants.py               # SCREEN_WIDTH, SCREEN_HEIGHT, QUESTION_TIMER, FPS, colors, fonts
│   ├── screen_manager.py          # FR-1–3: screen state machine, GameState owner, transition logic
│   ├── menu_screen.py             # FR-1: mode select, FR-2: category select, FR-3: quit
│   ├── game_screen.py             # FR-4–6: question display + answer eval, FR-5: timer,
│   │                              # FR-10: sequential turns, FR-13/16: live score + speed bonus
│   └── results_screen.py         # FR-7–8: single-player verdict, FR-11: multiplayer leaderboard
│
└── tests/
    ├── test_loader.py             # Tests for FR-17, FR-18
    ├── test_bank.py               # Tests for FR-19, FR-20
    ├── test_engine.py             # Tests for FR-12, FR-13, FR-14
    └── test_multiplier.py         # Tests for FR-15
```

### Architectural Boundaries

**Module dependency rules (strictly enforced):**

```
questions/   ──────────────────────────────▶  (no imports from ui/ or scoring/)
scoring/     ──────────────────────────────▶  (no imports from ui/ or questions/)
ui/          ──▶ questions/   ──▶ scoring/
main.py      ──▶ ui/screen_manager  (composition root only)
```

**Shared contracts (defined in `scoring/engine.py`, used everywhere):**
- `GameState` dataclass — game state shared across all modules
- `Player` dataclass — per-player score/streak/correct tracking

### Requirements to Structure Mapping

| FR Group | FRs | Primary Files |
|----------|-----|---------------|
| Main Menu | FR-1, FR-2, FR-3 | `ui/menu_screen.py`, `ui/screen_manager.py` |
| Single-Player | FR-4, FR-5, FR-6, FR-7, FR-8 | `ui/game_screen.py`, `ui/results_screen.py` |
| Multiplayer | FR-9, FR-10, FR-11 | `ui/game_screen.py`, `ui/results_screen.py`, `ui/screen_manager.py` |
| Scoring Engine | FR-12, FR-13, FR-14, FR-15, FR-16 | `scoring/engine.py`, `scoring/multiplier.py`, `ui/game_screen.py` |
| Question Bank | FR-17, FR-18, FR-19, FR-20 | `questions/loader.py`, `questions/bank.py` |

### Data Flow

```
Startup:
  main.py
    └─▶ questions/loader.py   loads JSON → list[dict]
    └─▶ questions/bank.py     validates records → stores in GameState.questions (on round start)

Per question (game_screen.py owns the frame loop):
  PyGame clock ──▶ game_screen.py (time_elapsed)
                        └─▶ scoring/engine.calculate_speed_bonus(base, elapsed, duration) → int
                        └─▶ scoring/multiplier.get_multiplier(streak) → float
                        └─▶ GameState.players[i].score updated
                        └─▶ UI re-renders live score (FR-16)

Round end:
  game_screen.py ──▶ returns "results" transition
  screen_manager.py ──▶ activates results_screen.py
  results_screen.py ──▶ reads GameState.players → renders verdict / leaderboard
```

### Integration Points

**Internal communication:** Via `GameState` object passed to every `Screen.handle_events()`, `update()`, and `draw()` call. No direct screen-to-screen communication.

**External integrations:** None in v1 — local JSON files only.

**Test boundaries:** `tests/` only imports from `questions/` and `scoring/` — no PyGame required to run the test suite. `ui/` is not unit-tested (requires display); covered by manual play-through (SM-1).

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**
All five decisions use Python stdlib + PyGame exclusively. No version conflicts are possible.
`GameState` is the shared contract across all modules, eliminating implicit coupling. `scoring/`
and `questions/` are PyGame-free by design and confirmed by module boundary rules.

**Pattern Consistency:**
Naming conventions apply uniformly across all files and modules. The `handle_events()` → `str|None`
transition contract is consistent across all three screen classes. Pure-function rule in `scoring/`
directly reinforces Decision 3 (timer ownership in `game_screen.py`).

**Structure Alignment:**
The three-module directory boundary exactly implements PRD §6.1. `tests/` is scoped to
`questions/` and `scoring/` only — no PyGame install required for the test suite. `main.py`
as composition root is consistent with `ScreenManager` owning `GameState`.

### Requirements Coverage Validation ✅

**Functional Requirements Coverage:**

| FR Group | FRs | Status | Covered By |
|----------|-----|--------|------------|
| Main Menu | FR-1–3 | ✅ | `ui/menu_screen.py`, `ui/screen_manager.py` |
| Single-Player | FR-4–8 | ✅ | `ui/game_screen.py`, `ui/results_screen.py` |
| Multiplayer | FR-9–11 | ✅ | `ui/game_screen.py` (turn rotation via `active_player_index`) |
| Scoring Engine | FR-12–16 | ✅ | `scoring/engine.py`, `scoring/multiplier.py`, `ui/game_screen.py` |
| Question Bank | FR-17–20 | ✅ | `questions/loader.py`, `questions/bank.py` |

**Non-Functional Requirements Coverage:**
- FR-16 / SM-2 (live score within one frame): Guaranteed — `game_screen.draw()` reads `GameState.players[i].score` directly on every frame tick.
- FR-17 (halt on missing JSON): `sys.exit()` in `questions/loader.py`.
- FR-18 (silent skip on malformed record): `logging.warning` + `continue` in `loader.py`.

**Implementation Note:** Multiplayer player name entry is not an explicit FR. It is handled within the multi-step flow of `MenuScreen` before populating `GameState.players`. No additional screen is required — this is a Story-level design concern.

### Implementation Readiness Validation ✅

**Decision Completeness:**
All five critical decisions are documented with explicit code patterns and rationale. All four PRD open questions (OQ-1–4) are closed with specific values (30s timer, stepped multiplier, shared draw, 1s auto-advance).

**Structure Completeness:**
Every file in the project tree is defined with its purpose and FR mapping. `tests/` structure mirrors the testable modules. Data files are placed in `data/` separate from code.

**Pattern Completeness:**
Seven conflict-prone areas are covered: naming, screen transitions, constants location, error handling (two tiers), logging levels, scoring function signatures, and import style. Examples provided for both correct and forbidden patterns.

### Gap Analysis Results

**Critical Gaps:** None.

**Important Gaps:** None.

**Nice-to-Have:**
- PyGame version pin in `requirements.txt` — recommended to add `pygame==2.x.x` once installed, for reproducibility (not blocking).
- `.gitignore` contents not specified — standard Python `.gitignore` is sufficient (not blocking).

### Architecture Completeness Checklist

**Requirements Analysis**

- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed (low-medium, desktop GUI game)
- [x] Technical constraints identified (PyGame-only, Windows primary, 3-module hard constraint)
- [x] Cross-cutting concerns mapped (game state, timer ownership, multiplayer turn isolation)

**Architectural Decisions**

- [x] Critical decisions documented with versions
- [x] Technology stack fully specified (Python 3 + PyGame, stdlib only)
- [x] Integration patterns defined (`GameState` injection, `handle_events()` return contract)
- [x] Performance considerations addressed (one-frame score update, FR-16 / SM-2)

**Implementation Patterns**

- [x] Naming conventions established (7-row table, all element types covered)
- [x] Structure patterns defined (screen state machine, `ScreenManager.run_frame()`)
- [x] Communication patterns specified (transition via return value, `GameState` as shared contract)
- [x] Process patterns documented (error handling, logging levels, import style)

**Project Structure**

- [x] Complete directory structure defined (all files named and annotated)
- [x] Component boundaries established (dependency rules table, zero cross-imports enforced)
- [x] Integration points mapped (startup flow, per-question flow, round-end flow)
- [x] Requirements to structure mapping complete (all 20 FRs assigned to files)

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION

**Confidence Level:** High — all 16 checklist items confirmed, no critical or important gaps.

**Key Strengths:**
- Hard PRD constraint (3-module boundary) is architecturally enforced from day one
- `GameState` dataclass eliminates global variable risk and gives AI agents a clear shared contract
- `scoring/` module is PyGame-free and fully unit-testable without a display
- All four PRD open questions resolved with specific values — no ambiguity for implementation
- Screen transition contract (`handle_events()` → `str|None`) prevents direct state mutation

**Areas for Future Enhancement:**
- Sound/audio architecture (v2) — no hooks needed now, `game_screen.py` can add `pygame.mixer` calls
- Persistent leaderboard (v3) — `Player` dataclass can be serialized to JSON; `data/` folder ready
- Online multiplayer (v3) — `GameState` serializable; transport layer would wrap existing turn logic

### Implementation Handoff

**AI Agent Guidelines:**
- Follow all architectural decisions exactly as documented
- Use implementation patterns consistently across all components
- Respect the module boundary rules — `scoring/` and `questions/` must never import from `ui/`
- Refer to the Requirements to Structure Mapping table for every story implementation
- Use the enforcement checklist in Implementation Patterns as a pre-commit verification list

**First Implementation Priority:**
```bash
mkdir trivia-app && cd trivia-app
python -m venv .venv
.venv\Scripts\activate
pip install pygame
pip freeze > requirements.txt
```
Then create all `__init__.py` files and the `GameState` + `Player` dataclasses in `scoring/engine.py` — these are the foundation every other story depends on.
