# Data Models — Python Trivia App

**Generated:** 2026-06-09 | **Scan level:** Deep

---

## Question JSON Schema

Questions are stored in `data/` as UTF-8 JSON arrays. Each file is loaded independently by `questions/loader.py` at startup. The two files are concatenated into a single `all_questions` list before being passed to `ScreenManager`.

### File Locations

| File | Category |
|------|----------|
| `data/questions_politics.json` | `"Politics"` |
| `data/questions_history.json` | `"History"` |

### Record Schema

```json
{
  "question_text": "string (required)",
  "options": ["string", "string", "string", "string"],
  "correct_index": 0,
  "category": "Politics"
}
```

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `question_text` | `string` | Required, non-empty | The question shown to the player |
| `options` | `array[string]` | Required, exactly 4 elements | Answer choices A/B/C/D |
| `correct_index` | `integer` | Required, 0–3 | Index into `options` of the correct answer |
| `category` | `string` | Required, `"Politics"` or `"History"` | Used by `draw_questions()` for filtering |

### Example Record

```json
{
  "question_text": "Who was the first President of the United States?",
  "options": [
    "George Washington",
    "John Adams",
    "Thomas Jefferson",
    "Benjamin Franklin"
  ],
  "correct_index": 0,
  "category": "Politics"
}
```

### Validation Rules (enforced by `questions/loader.py`)

| Rule | Consequence on failure |
|------|----------------------|
| File does not exist | `sys.exit()` with descriptive error |
| File not valid JSON | `sys.exit()` with parse error |
| Root is not a JSON array | `sys.exit()` |
| Any required field missing | Record skipped with `logging.warning` |
| `options` not list of exactly 4 | Record skipped |
| `correct_index` not int 0–3 | Record skipped |
| `category` not `"Politics"` or `"History"` | Record skipped |

> **Minimum count:** At least 10 valid questions per category must exist. `draw_questions()` calls `sys.exit()` if fewer than `n=10` matching records are found.

---

## GameState Dataclass

Defined in `scoring/engine.py`. Instantiated once by `ScreenManager`; passed by reference to every screen's methods.

```python
@dataclass
class GameState:
    current_screen: str = "menu"
    selected_mode: str = ""
    selected_category: str = ""
    players: list = field(default_factory=list)
    active_player_index: int = 0
    current_question_index: int = 0
    questions: list = field(default_factory=list)
```

| Field | Default | Valid values | Mutated by |
|-------|---------|--------------|-----------|
| `current_screen` | `"menu"` | `"menu"`, `"setup"`, `"game"`, `"handoff"`, `"results"` | `ScreenManager.run_frame` (via transition string) |
| `selected_mode` | `""` | `"single"`, `"multiplayer"` | `MenuScreen._on_click`, `SetupScreen._on_category_click` |
| `selected_category` | `""` | `"Politics"`, `"History"` | `MenuScreen._on_click`, `SetupScreen._on_category_click` |
| `players` | `[]` | `list[Player]` | `MenuScreen._on_click`, `SetupScreen._on_category_click`, `ResultsScreen.handle_events` |
| `active_player_index` | `0` | `0 ≤ n < len(players)` | `HandoffScreen._advance_turn`, `MenuScreen._on_click`, `SetupScreen._on_category_click`, `ResultsScreen.handle_events` |
| `current_question_index` | `0` | `0 ≤ n ≤ len(questions)` | `GameScreen.update` (advance), `HandoffScreen._advance_turn` (reset), `MenuScreen`, `SetupScreen`, `ResultsScreen` (reset) |
| `questions` | `[]` | `list[dict]` (question records) | `MenuScreen._on_click`, `SetupScreen._on_category_click`, `ResultsScreen.handle_events` (clear) |

**Full reset** (on return to main menu from `ResultsScreen.handle_events`):
```python
game_state.players = []
game_state.active_player_index = 0
game_state.current_question_index = 0
game_state.questions = []
game_state.selected_mode = ""
game_state.selected_category = ""
```

---

## Player Dataclass

Defined in `scoring/engine.py`. One instance per player, stored in `GameState.players`.

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

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Player's display name (max 20 chars, from SetupScreen) |
| `score` | `int` | Accumulated points (base + speed bonus × streak multiplier) |
| `streak` | `int` | Current consecutive correct answer count; resets on wrong answer or timer expiry |
| `correct` | `int` | Total correct answers this round |
| `total` | `int` | Total questions answered (including wrong and expired) |
| `.percentage` | `float` (property) | `correct / total × 100`, or `0.0` if `total == 0` |

**Mutation pattern** (in `GameScreen.handle_events` on correct answer):
```python
player.streak += 1
speed_bonus = calculate_speed_bonus(BASE_SCORE, self._question_timer, QUESTION_TIMER)
points = apply_streak_multiplier(BASE_SCORE + speed_bonus, player.streak)
player.score += points
player.correct += 1
```

**Mutation pattern** (on wrong answer or timer expiry):
```python
player.streak = 0
player.total += 1
```

---

## State Lifecycle Diagram

```
App start
    ↓
GameState created (all defaults)
    ↓
MenuScreen: mode = "single" or "multiplayer"
    ↓
[Single] MenuScreen: players=[Player("Player 1")], questions=draw(), mode="single"
[Multi]  SetupScreen: players=[Player(n1),...], questions=draw(), mode="multiplayer"
    ↓
GameScreen (per player): mutates players[active_player_index].score/streak/correct/total
                          advances current_question_index
    ↓
[More players] HandoffScreen: active_player_index++, current_question_index=0
    ↓
ResultsScreen: reads players[], selected_mode
    → Main Menu → reset all fields → back to start
```
