---
baseline_commit: NO_VCS
---

# Story 1.2: Question Bank Loading and Validation

Status: review

## Story

As a player,
I want the app to load trivia questions from JSON files at startup and validate each record,
so that only well-formed questions are available during gameplay and missing files are caught immediately.

## Acceptance Criteria

1. Given valid `data/questions_politics.json` and `data/questions_history.json` exist, when the app starts, then both files load successfully and `loader.py` returns a list of validated question dicts.
2. Given a question record with all required fields (`question_text`, `options` 4-element list, `correct_index` 0–3, `category` `"Politics"` or `"History"`), when `loader.py` validates it, then the record is included in the loaded list.
3. Given a question record missing the `correct_index` field, when `loader.py` encounters it, then the record is skipped, a `logging.WARNING` is emitted, and no exception is raised (FR-18).
4. Given `data/questions_politics.json` does not exist, when the app starts, then `sys.exit()` is called with a user-facing error message before the menu renders (FR-17).
5. Given category `"Politics"` is selected, when `draw_questions(all_questions, "Politics", n=10)` is called, then only records with `category == "Politics"` are returned (FR-19).
6. Given a category with ≥10 valid questions, when `draw_questions()` is called, then exactly 10 unique questions are returned with no repetitions (FR-20).
7. Given `tests/test_loader.py` and `tests/test_bank.py` exist, when the tests run without PyGame installed, then all tests pass.

## Tasks / Subtasks

- [x] Task 1: Create JSON question bank data files (AC: 1, 2, 5, 6)
  - [x] Create `data/questions_politics.json` with ≥12 valid Politics questions
  - [x] Create `data/questions_history.json` with ≥12 valid History questions
  - [x] Every record must match exact schema: `question_text` (str), `options` (4-element list), `correct_index` (int 0–3), `category` ("Politics"|"History")
- [x] Task 2: Implement `questions/loader.py` (AC: 1, 2, 3, 4)
  - [x] `load_questions(path: str) -> list` — opens JSON, validates each record, returns valid list
  - [x] Missing file → `sys.exit()` with user-facing message
  - [x] Malformed JSON → `sys.exit()` with user-facing message
  - [x] Invalid record → `logging.warning(...)` + skip, no exception (not sys.exit)
  - [x] Private `_is_valid(record: dict, index: int) -> bool` helper does field-by-field validation
- [x] Task 3: Implement `questions/bank.py` (AC: 5, 6)
  - [x] `draw_questions(questions: list, category: str, n: int = 10) -> list`
  - [x] Filter input list by `category` field
  - [x] If fewer than `n` filtered questions → `sys.exit()` with user-facing message
  - [x] Return `random.sample(filtered, n)` — exactly `n` unique questions
- [x] Task 4: Update `ui/screen_manager.py` — add `all_questions` parameter (AC: 1)
  - [x] Change `ScreenManager.__init__(self)` to `ScreenManager.__init__(self, all_questions: list)`
  - [x] Store as `self.all_questions = all_questions`
  - [x] No other changes to ScreenManager
- [x] Task 5: Update `main.py` — load questions at startup (AC: 1, 4)
  - [x] Add `from questions.loader import load_questions` import
  - [x] Load both JSON files before `pygame.init()`: `all_questions = load_questions(...) + load_questions(...)`
  - [x] Pass `all_questions` to `ScreenManager(all_questions)`
- [x] Task 6: Implement `tests/test_loader.py` (AC: 7)
  - [x] Test valid file loads and returns correct count
  - [x] Test all 4 required fields are preserved in output
  - [x] Test record missing `correct_index` is skipped with WARNING logged
  - [x] Test missing file triggers `SystemExit`
  - [x] Test no exception raised on any invalid record
  - [x] Test invalid `options` length skipped
  - [x] Test `correct_index` out of range (4) skipped
  - [x] Test invalid `category` value skipped
- [x] Task 7: Implement `tests/test_bank.py` (AC: 7)
  - [x] Test Politics filter excludes History questions
  - [x] Test History filter excludes Politics questions
  - [x] Test exactly `n=10` questions returned
  - [x] Test no duplicate questions in draw
  - [x] Test `< n` questions triggers `SystemExit`
  - [x] Test empty list triggers `SystemExit`
- [x] Task 8: Install pytest and regenerate `requirements.txt`
  - [x] Run `.venv\Scripts\pip install pytest`
  - [x] Run `.venv\Scripts\pip freeze | Out-File -Encoding utf8 requirements.txt`
- [x] Task 9: Verify all ACs via commands in Dev Notes

## Dev Notes

### Environment — CRITICAL

**Python version: 3.14.2** — `pygame` 2.6.1 has no wheel for Python 3.14. Story 1.1 already installed `pygame-ce==2.5.7` which imports as `pygame`. **Do NOT reinstall or change this.** `requirements.txt` already has `pygame-ce==2.5.7`.

**All commands must use `.venv\Scripts\python` / `.venv\Scripts\pip` / `.venv\Scripts\pytest` from `trivia-app/`.**

### File Summary — What Changes

| File | Action | Notes |
|------|--------|-------|
| `data/questions_politics.json` | NEW | ≥12 Politics questions |
| `data/questions_history.json` | NEW | ≥12 History questions |
| `questions/loader.py` | UPDATE (was stub) | Full implementation |
| `questions/bank.py` | UPDATE (was stub) | Full implementation |
| `ui/screen_manager.py` | UPDATE | Add `all_questions` param only |
| `main.py` | UPDATE | Add loader imports + startup loading |
| `tests/test_loader.py` | UPDATE (was stub) | Full pytest suite |
| `tests/test_bank.py` | UPDATE (was stub) | Full pytest suite |
| `requirements.txt` | UPDATE | Add `pytest` entry |

### Exact Code — `questions/loader.py`

```python
import json
import logging
import os
import sys


def load_questions(path: str) -> list:
    if not os.path.exists(path):
        sys.exit(f"ERROR: Question bank not found at '{path}'. Cannot start game.")

    try:
        with open(path, encoding="utf-8") as f:
            raw_records = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        sys.exit(f"ERROR: Failed to load question bank from '{path}': {e}")

    if not isinstance(raw_records, list):
        sys.exit(f"ERROR: Question bank at '{path}' must be a JSON array.")

    valid_questions = []
    for i, record in enumerate(raw_records):
        if _is_valid(record, i):
            valid_questions.append(record)

    logging.info(f"Loaded {len(valid_questions)} valid questions from '{path}'")
    return valid_questions


def _is_valid(record: dict, index: int) -> bool:
    for field in ("question_text", "options", "correct_index", "category"):
        if field not in record:
            logging.warning(f"Skipping question {index}: missing field '{field}'")
            return False

    if not isinstance(record["options"], list) or len(record["options"]) != 4:
        logging.warning(
            f"Skipping question {index}: 'options' must be a list of exactly 4 elements"
        )
        return False

    if not isinstance(record["correct_index"], int) or not (0 <= record["correct_index"] <= 3):
        logging.warning(
            f"Skipping question {index}: 'correct_index' must be an integer 0-3"
        )
        return False

    if record["category"] not in ("Politics", "History"):
        logging.warning(
            f"Skipping question {index}: 'category' must be 'Politics' or 'History',"
            f" got '{record['category']}'"
        )
        return False

    return True
```

**Module boundary:** `questions/loader.py` imports only stdlib (`json`, `logging`, `os`, `sys`). Zero imports from `ui/` or `scoring/`.

### Exact Code — `questions/bank.py`

```python
import logging
import random
import sys


def draw_questions(questions: list, category: str, n: int = 10) -> list:
    filtered = [q for q in questions if q.get("category") == category]

    if len(filtered) < n:
        sys.exit(
            f"ERROR: Not enough '{category}' questions — need {n}, found {len(filtered)}."
        )

    drawn = random.sample(filtered, n)
    logging.info(f"Drew {n} questions for category '{category}'")
    return drawn
```

**Module boundary:** `questions/bank.py` imports only stdlib (`logging`, `random`, `sys`). Zero imports from `ui/` or `scoring/`.

**Signature note:** The stub established `draw_questions(questions: list, category: str, n: int = 10)`. The full bank is passed by the caller (`ScreenManager.all_questions` in Stories 1.4–1.5), not stored as module state. This is consistent with the pure-function architecture used by `scoring/`.

### Exact Code — `ui/screen_manager.py` (minimal change only)

Change the `__init__` signature to accept `all_questions`. **Do not change anything else.**

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
    def __init__(self, all_questions: list):
        from ui.menu_screen import MenuScreen
        from ui.game_screen import GameScreen
        from ui.results_screen import ResultsScreen
        self.all_questions = all_questions
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

`self.all_questions` is stored here so Stories 1.4–1.5 can call `draw_questions(self.all_questions, category)` when a round starts.

### Exact Code — `main.py` (updated)

```python
import logging
import sys
import pygame
from questions.loader import load_questions
from ui.screen_manager import ScreenManager
from ui.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

logging.basicConfig(level=logging.DEBUG)


def main():
    all_questions = (
        load_questions("data/questions_politics.json")
        + load_questions("data/questions_history.json")
    )

    pygame.init()
    surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Python Trivia App")
    clock = pygame.time.Clock()
    manager = ScreenManager(all_questions)

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

**Key change:** `load_questions()` is called BEFORE `pygame.init()` so that a missing file triggers `sys.exit()` before any window opens. Then `all_questions` is passed to `ScreenManager(all_questions)`.

### Exact Code — `tests/test_loader.py`

```python
import json
import logging
import os
import tempfile

import pytest

from questions.loader import load_questions


VALID_Q = {
    "question_text": "Who was first?",
    "options": ["A", "B", "C", "D"],
    "correct_index": 0,
    "category": "Politics",
}


def _write_json(data):
    f = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    )
    json.dump(data, f)
    f.close()
    return f.name


def test_valid_file_loads_successfully():
    path = _write_json([VALID_Q])
    try:
        result = load_questions(path)
        assert len(result) == 1
        assert result[0]["question_text"] == "Who was first?"
    finally:
        os.unlink(path)


def test_all_required_fields_preserved():
    path = _write_json([VALID_Q])
    try:
        result = load_questions(path)
        q = result[0]
        assert q["question_text"] == VALID_Q["question_text"]
        assert q["options"] == VALID_Q["options"]
        assert q["correct_index"] == VALID_Q["correct_index"]
        assert q["category"] == VALID_Q["category"]
    finally:
        os.unlink(path)


def test_missing_correct_index_skipped_with_warning(caplog):
    bad = {"question_text": "Q?", "options": ["A", "B", "C", "D"], "category": "History"}
    path = _write_json([VALID_Q, bad])
    try:
        with caplog.at_level(logging.WARNING):
            result = load_questions(path)
        assert len(result) == 1
        assert any("correct_index" in msg for msg in caplog.messages)
    finally:
        os.unlink(path)


def test_missing_question_text_skipped(caplog):
    bad = {"options": ["A", "B", "C", "D"], "correct_index": 1, "category": "Politics"}
    path = _write_json([bad])
    try:
        with caplog.at_level(logging.WARNING):
            result = load_questions(path)
        assert result == []
    finally:
        os.unlink(path)


def test_options_wrong_length_skipped(caplog):
    bad = {
        "question_text": "Q?",
        "options": ["A", "B", "C"],
        "correct_index": 0,
        "category": "Politics",
    }
    path = _write_json([bad])
    try:
        with caplog.at_level(logging.WARNING):
            result = load_questions(path)
        assert result == []
    finally:
        os.unlink(path)


def test_correct_index_out_of_range_skipped(caplog):
    bad = {
        "question_text": "Q?",
        "options": ["A", "B", "C", "D"],
        "correct_index": 4,
        "category": "Politics",
    }
    path = _write_json([bad])
    try:
        with caplog.at_level(logging.WARNING):
            result = load_questions(path)
        assert result == []
    finally:
        os.unlink(path)


def test_invalid_category_skipped(caplog):
    bad = {
        "question_text": "Q?",
        "options": ["A", "B", "C", "D"],
        "correct_index": 0,
        "category": "Science",
    }
    path = _write_json([bad])
    try:
        with caplog.at_level(logging.WARNING):
            result = load_questions(path)
        assert result == []
    finally:
        os.unlink(path)


def test_missing_file_triggers_sys_exit():
    with pytest.raises(SystemExit):
        load_questions("data/this_file_does_not_exist_xyz123.json")


def test_no_exception_raised_on_invalid_records():
    bad = {"question_text": "Q?"}
    path = _write_json([bad])
    try:
        result = load_questions(path)  # must not raise any exception
        assert result == []
    finally:
        os.unlink(path)
```

### Exact Code — `tests/test_bank.py`

```python
import pytest

from questions.bank import draw_questions


POLITICS_QS = [
    {
        "question_text": f"Politics Q{i}",
        "options": ["A", "B", "C", "D"],
        "correct_index": 0,
        "category": "Politics",
    }
    for i in range(12)
]
HISTORY_QS = [
    {
        "question_text": f"History Q{i}",
        "options": ["A", "B", "C", "D"],
        "correct_index": 0,
        "category": "History",
    }
    for i in range(12)
]
ALL_QS = POLITICS_QS + HISTORY_QS


def test_politics_filter_excludes_history():
    result = draw_questions(ALL_QS, "Politics", n=5)
    assert all(q["category"] == "Politics" for q in result)


def test_history_filter_excludes_politics():
    result = draw_questions(ALL_QS, "History", n=5)
    assert all(q["category"] == "History" for q in result)


def test_returns_exactly_n_questions():
    result = draw_questions(ALL_QS, "Politics", n=10)
    assert len(result) == 10


def test_no_duplicate_questions():
    result = draw_questions(ALL_QS, "Politics", n=10)
    texts = [q["question_text"] for q in result]
    assert len(texts) == len(set(texts))


def test_randomness_varies_across_draws():
    draws = set()
    for _ in range(10):
        result = draw_questions(ALL_QS, "Politics", n=10)
        draws.add(tuple(q["question_text"] for q in result))
    assert len(draws) > 1


def test_insufficient_questions_triggers_sys_exit():
    short = POLITICS_QS[:3]
    with pytest.raises(SystemExit):
        draw_questions(short, "Politics", n=10)


def test_empty_list_triggers_sys_exit():
    with pytest.raises(SystemExit):
        draw_questions([], "Politics", n=10)
```

### JSON Schema (enforce exactly)

```json
{
  "question_text": "string — the question",
  "options": ["string", "string", "string", "string"],
  "correct_index": 0,
  "category": "Politics"
}
```

- `correct_index` is 0-based index into `options[]`
- `category` must be exactly `"Politics"` or `"History"` (case-sensitive)
- Each file must contain **at least 12 questions** (AC6 needs ≥10; 12 gives headroom)

### `data/questions_politics.json` Contents

```json
[
  {
    "question_text": "Who was the first President of the United States?",
    "options": ["George Washington", "John Adams", "Thomas Jefferson", "Benjamin Franklin"],
    "correct_index": 0,
    "category": "Politics"
  },
  {
    "question_text": "Which country has the world's largest democracy by population?",
    "options": ["United States", "India", "Brazil", "Indonesia"],
    "correct_index": 1,
    "category": "Politics"
  },
  {
    "question_text": "What is the name of the lower house of the UK Parliament?",
    "options": ["House of Commons", "House of Lords", "Senate", "Cabinet"],
    "correct_index": 0,
    "category": "Politics"
  },
  {
    "question_text": "Which organisation has 193 member states as of 2023?",
    "options": ["NATO", "European Union", "United Nations", "World Trade Organisation"],
    "correct_index": 2,
    "category": "Politics"
  },
  {
    "question_text": "Who was the first female Prime Minister of the United Kingdom?",
    "options": ["Theresa May", "Margaret Thatcher", "Jacinda Ardern", "Angela Merkel"],
    "correct_index": 1,
    "category": "Politics"
  },
  {
    "question_text": "What does the acronym NATO stand for?",
    "options": ["North Atlantic Treaty Organisation", "National Alliance of Trade Officials", "North American Treaty Order", "Northern Atlantic Trade Organisation"],
    "correct_index": 0,
    "category": "Politics"
  },
  {
    "question_text": "Which amendment to the US Constitution abolished slavery?",
    "options": ["13th", "14th", "15th", "19th"],
    "correct_index": 0,
    "category": "Politics"
  },
  {
    "question_text": "In which year did the Berlin Wall fall?",
    "options": ["1987", "1988", "1989", "1991"],
    "correct_index": 2,
    "category": "Politics"
  },
  {
    "question_text": "Who co-authored 'The Communist Manifesto' with Karl Marx?",
    "options": ["Vladimir Lenin", "Friedrich Engels", "Leon Trotsky", "Mao Zedong"],
    "correct_index": 1,
    "category": "Politics"
  },
  {
    "question_text": "What is the name of the main legislative body of France?",
    "options": ["Bundestag", "Diet", "National Assembly", "Riksdag"],
    "correct_index": 2,
    "category": "Politics"
  },
  {
    "question_text": "Which US president signed the Civil Rights Act of 1964?",
    "options": ["John F. Kennedy", "Dwight D. Eisenhower", "Lyndon B. Johnson", "Richard Nixon"],
    "correct_index": 2,
    "category": "Politics"
  },
  {
    "question_text": "What was the first country to grant women the right to vote nationally?",
    "options": ["United States", "New Zealand", "Australia", "Finland"],
    "correct_index": 1,
    "category": "Politics"
  }
]
```

### `data/questions_history.json` Contents

```json
[
  {
    "question_text": "In which year did World War I begin?",
    "options": ["1912", "1914", "1916", "1918"],
    "correct_index": 1,
    "category": "History"
  },
  {
    "question_text": "Which Egyptian queen formed alliances with both Julius Caesar and Mark Antony?",
    "options": ["Nefertiti", "Cleopatra", "Hatshepsut", "Ankhesenamun"],
    "correct_index": 1,
    "category": "History"
  },
  {
    "question_text": "Which empire was founded by Genghis Khan?",
    "options": ["Ottoman Empire", "Mongol Empire", "Persian Empire", "Roman Empire"],
    "correct_index": 1,
    "category": "History"
  },
  {
    "question_text": "In which year did the RMS Titanic sink?",
    "options": ["1910", "1911", "1912", "1913"],
    "correct_index": 2,
    "category": "History"
  },
  {
    "question_text": "Who invented the movable-type printing press in Europe?",
    "options": ["Leonardo da Vinci", "Johannes Gutenberg", "Galileo Galilei", "Isaac Newton"],
    "correct_index": 1,
    "category": "History"
  },
  {
    "question_text": "What ancient wonder of the world stood at Alexandria?",
    "options": ["Colossus of Rhodes", "Hanging Gardens of Babylon", "Temple of Artemis", "Lighthouse of Alexandria"],
    "correct_index": 3,
    "category": "History"
  },
  {
    "question_text": "Which country first landed humans on the Moon?",
    "options": ["Soviet Union", "United States", "China", "United Kingdom"],
    "correct_index": 1,
    "category": "History"
  },
  {
    "question_text": "In which year did World War II end?",
    "options": ["1943", "1944", "1945", "1946"],
    "correct_index": 2,
    "category": "History"
  },
  {
    "question_text": "Who was the first Roman Emperor?",
    "options": ["Julius Caesar", "Augustus", "Nero", "Constantine"],
    "correct_index": 1,
    "category": "History"
  },
  {
    "question_text": "The most preserved sections of the Great Wall of China were built during which dynasty?",
    "options": ["Han Dynasty", "Tang Dynasty", "Ming Dynasty", "Qin Dynasty"],
    "correct_index": 2,
    "category": "History"
  },
  {
    "question_text": "What city was the capital of the Byzantine Empire?",
    "options": ["Athens", "Constantinople", "Alexandria", "Antioch"],
    "correct_index": 1,
    "category": "History"
  },
  {
    "question_text": "In which year did the French Revolution begin?",
    "options": ["1776", "1783", "1789", "1799"],
    "correct_index": 2,
    "category": "History"
  }
]
```

### Module Boundary Rules (enforce all)

```
questions/loader.py  → imports: json, logging, os, sys (stdlib only)
questions/bank.py    → imports: logging, random, sys (stdlib only)
tests/test_loader.py → imports: json, logging, os, tempfile, pytest, questions.loader
tests/test_bank.py   → imports: pytest, questions.bank
```

Zero imports from `ui/` or `scoring/` in any `questions/` or `tests/` file.

### Verification Commands (run from `trivia-app/` with venv active)

```powershell
# Task 8: Install pytest
.venv\Scripts\pip install pytest

# AC1: Both files load
.venv\Scripts\python -c "
from questions.loader import load_questions
p = load_questions('data/questions_politics.json')
h = load_questions('data/questions_history.json')
assert len(p) >= 10 and len(h) >= 10
print(f'AC1 passed: Politics={len(p)}, History={len(h)}')
"

# AC3: Invalid record skipped, no exception
.venv\Scripts\python -c "
import json, tempfile, os, logging
logging.basicConfig(level=logging.WARNING)
from questions.loader import load_questions
data = [{'question_text': 'Q?', 'options': ['A','B','C','D'], 'category': 'Politics'}]
import tempfile, json, os
f = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8')
json.dump(data, f); f.close()
result = load_questions(f.name); os.unlink(f.name)
assert result == []
print('AC3 passed: skipped with no exception')
"

# AC4: Missing file sys.exit
.venv\Scripts\python -c "
from questions.loader import load_questions
try:
    load_questions('data/does_not_exist.json')
    print('FAIL')
except SystemExit as e:
    print(f'AC4 passed: sys.exit({e})')
"

# AC5-6: draw_questions category filter + 10 unique
.venv\Scripts\python -c "
from questions.loader import load_questions
from questions.bank import draw_questions
all_qs = load_questions('data/questions_politics.json') + load_questions('data/questions_history.json')
pol = draw_questions(all_qs, 'Politics', 10)
assert len(pol) == 10
assert all(q['category'] == 'Politics' for q in pol)
assert len(set(q['question_text'] for q in pol)) == 10
print('AC5-6 passed')
"

# AC7: Run pytest suite (no PyGame required)
.venv\Scripts\pytest tests/test_loader.py tests/test_bank.py -v
```

### Architecture Compliance Checklist

- [ ] `questions/loader.py` imports only stdlib
- [ ] `questions/bank.py` imports only stdlib
- [ ] `main.py` calls `load_questions()` BEFORE `pygame.init()`
- [ ] `ScreenManager.__init__` accepts `all_questions: list` and stores as `self.all_questions`
- [ ] No `print()` — only `logging.warning()` / `logging.info()`
- [ ] All imports absolute (no `from .module import ...`)
- [ ] JSON files in `data/` — exactly 12 records each, all valid schema

### References

- [Source: architecture.md#Error Handling Pattern] — startup `sys.exit()` for missing file, `logging.warning` + skip for invalid records
- [Source: architecture.md#JSON Question Schema] — required fields and types
- [Source: architecture.md#Project Structure] — `data/` folder placement, module roles
- [Source: architecture.md#Logging Pattern] — `WARNING` for skipped data, `INFO` for state transitions
- [Source: architecture.md#Import Style] — absolute imports only
- [Source: architecture.md#Decision 3 / AR-6] — `questions/` is PyGame-free (pure functions)
- [Source: epics.md#Story 1.2] — all acceptance criteria
- [Source: epics.md#FR-17] — missing JSON halts launch
- [Source: epics.md#FR-18] — invalid records skipped and logged
- [Source: epics.md#FR-19] — category filtering
- [Source: epics.md#FR-20] — no-repeat random draw
- [Source: 1-1-project-scaffold] — `pygame-ce==2.5.7` (not `pygame`) on Python 3.14; venv at `.venv\Scripts\`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- No issues encountered. All 16 pytest tests passed on first run.
- pip cache warnings during `pip install pytest` are harmless (cache deserialization issue unrelated to install).

### Completion Notes List

- AC1-2: Both JSON files load successfully — 12 Politics + 12 History questions, all valid schema
- AC3: Invalid record (missing `correct_index`) is skipped with `logging.WARNING`, no exception raised — verified manually and via `test_missing_correct_index_skipped_with_warning`
- AC4: Missing file triggers `sys.exit()` with user-facing message before `pygame.init()` — verified manually and via `test_missing_file_triggers_sys_exit`
- AC5-6: `draw_questions(all_qs, "Politics", 10)` returns exactly 10 unique Politics questions — verified manually and via `test_returns_exactly_n_questions`, `test_no_duplicate_questions`, filter tests
- AC7: 16/16 pytest tests pass without PyGame (`tests/test_loader.py` + `tests/test_bank.py`)
- Module boundary confirmed: `questions/loader.py` and `questions/bank.py` import stdlib only (json, logging, os, sys, random)
- `ScreenManager.__init__` updated to `__init__(self, all_questions: list)` — `self.all_questions` available for Stories 1.4–1.5 to call `draw_questions(self.all_questions, category)` when a round starts
- `requirements.txt` regenerated with `pytest==9.0.3` added

### File List

- trivia-app/data/questions_politics.json (NEW)
- trivia-app/data/questions_history.json (NEW)
- trivia-app/questions/loader.py (UPDATED — stub → full implementation)
- trivia-app/questions/bank.py (UPDATED — stub → full implementation)
- trivia-app/ui/screen_manager.py (UPDATED — added `all_questions` param)
- trivia-app/main.py (UPDATED — added question loading at startup)
- trivia-app/tests/test_loader.py (UPDATED — stub → 9-test suite)
- trivia-app/tests/test_bank.py (UPDATED — stub → 7-test suite)
- trivia-app/requirements.txt (UPDATED — added pytest==9.0.3)

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-06-09 | Story implemented — all 9 tasks complete, 16/16 tests pass, all ACs verified | claude-sonnet-4-6 |
