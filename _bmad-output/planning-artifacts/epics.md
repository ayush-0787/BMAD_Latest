---
stepsCompleted: [1, 2, 3, 4]
status: 'complete'
completedAt: '2026-06-09'
inputDocuments:
  - _bmad-output/planning-artifacts/prds/prd-BMAD-2026-06-08/prd.md
  - _bmad-output/planning-artifacts/architecture.md
---

# Python Trivia App - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for the Python Trivia App, decomposing the requirements from the PRD and Architecture into implementable stories.

## Requirements Inventory

### Functional Requirements

FR-1: Player selects Single-Player or Pass-and-Play mode from the Main Menu. Single-Player routes to one Round; Pass-and-Play prompts for player count.
FR-2: Player selects one Category (Politics or History); the Round draws only from that Category's Questions. A missing Category at startup surfaces an error.
FR-3: Player can exit the app from the Main Menu without starting a Round.
FR-4: System randomly draws 10 Questions from the selected Category without repetition within a Round. Fewer than 10 available Questions surfaces an error.
FR-5: System displays one Question at a time with four Answer Options, a visible countdown timer (30s), and the Player's live score. Timer expiry counts as incorrect.
FR-6: System evaluates the Player's selected Answer Option immediately. Correct: Base Score + Speed Bonus × Streak Multiplier added to score. Incorrect: Streak resets to zero, no points.
FR-7: System determines win or loss at Round end: ≥70% correct = win; <70% = loss.
FR-8: System displays final score, percentage correct, and win/loss verdict on a dedicated Results screen with navigation back to Main Menu.
FR-9: System prompts for player count (2–4) before a Pass-and-Play Round begins. Count outside 2–4 is rejected with an inline error.
FR-10: System presents each Player's turn in sequence and prompts the next Player before their turn begins, hiding the previous Player's answers. All Players answer the same 10-Question draw.
FR-11: System displays a ranked leaderboard of all Players by score percentage after all turns complete; highest-percentage Player is declared winner. Tied players share rank; no tiebreaker in v1. Results screen offers navigation back to Main Menu.
FR-12: System awards a fixed Base Score for each correct answer; incorrect answers and timer expiry award zero.
FR-13: System awards Speed Bonus = Base Score × (time_remaining / timer_duration), proportional to answer speed. Applies to correct answers only.
FR-14: System increments the Streak counter on each consecutive correct answer and resets it to zero on any incorrect answer or timer expiry. Streak counter visible on Game Screen in real time.
FR-15: System applies Streak Multiplier to (Base Score + Speed Bonus): Streak 2 = 1.5×, Streak 3 = 2×, Streak 5+ = 3×. Result added to cumulative Round score.
FR-16: System displays current score, active Streak count, and last-applied Streak Multiplier on the Game Screen, updating within one rendered frame of answer submission.
FR-17: System loads the Question Bank from a JSON file at startup before the Main Menu renders. Missing or malformed JSON file surfaces a startup error and halts launch.
FR-18: Each Question record must contain: question text, four Answer Options, correct answer index (0–3), and Category. Records missing any required field are skipped and logged; not presented to the Player.
FR-19: System filters the Question Bank to the selected Category when drawing Questions; Questions from unselected Categories are excluded entirely.
FR-20: System draws Questions without repetition within a single Round using a randomised sample; fresh draw performed at Round start, not per Session.

### NonFunctional Requirements

NFR-1: Both game modes (single-player and multiplayer) must complete end-to-end without unhandled exceptions (SM-1).
NFR-2: Speed Bonus and Streak Multiplier values must update on the Game Screen within one rendered frame of each answer submission (SM-2 / FR-16).
NFR-3: Questions must load and filter correctly by Category at game start; incorrect filtering is a critical failure (SM-3).
NFR-4: Desktop-only PyGame application — no web, mobile, or terminal output. Windows is the primary dev/test platform.
NFR-5: Python stdlib + PyGame only — no additional runtime dependencies for v1.
NFR-6: English only — no localisation.

### Additional Requirements

- AR-1: Three-module boundary is a hard constraint from PRD §6.1: `questions` (bank loading and draw), `scoring` (base score, speed bonus, streak), `ui` (screens and rendering). Must be enforced from day one.
- AR-2: Project scaffold (directory tree with all files and `__init__.py` stubs) must be created as the first implementation story before any feature code is written.
- AR-3: `GameState` dataclass (defined in `scoring/engine.py`) is the single authoritative source of truth for all shared state — current screen, mode, category, players list, active player index, question index, current draw.
- AR-4: `Player` dataclass (defined in `scoring/engine.py`) holds name, score, streak, correct, total, and a computed `percentage` property.
- AR-5: Screen transitions are performed by returning a screen-name string from `handle_events()` — never by direct mutation of `GameState.current_screen`.
- AR-6: `scoring/` module must be completely free of PyGame imports — all functions are pure with no side effects, accepting timer values as explicit parameters.
- AR-7: All shared UI constants (colours, dimensions, font sizes, QUESTION_TIMER, FPS) live exclusively in `ui/constants.py` — no magic numbers in screen files.
- AR-8: Python `logging` module throughout — no bare `print()` calls for diagnostic output.
- AR-9: Absolute imports throughout — no relative imports within packages.
- AR-10: JSON question schema enforced: `question_text`, `options` (4-element list), `correct_index` (0–3), `category` (`"Politics"` or `"History"`). Any other shape is skipped and logged.
- AR-11: Tests directory (`tests/`) covers `questions/` and `scoring/` only — no PyGame required to run the test suite.

### UX Design Requirements

None — no UX design document exists for this project. The app is a PyGame desktop game; all UI layout and rendering decisions are captured in the Architecture document (screen state machine, Screen base class, constants).

### FR Coverage Map

FR-1:  Epic 1 — Mode selection on main menu
FR-2:  Epic 1 — Category selection on main menu
FR-3:  Epic 1 — Quit from main menu
FR-4:  Epic 1 — 10-question random draw, no repeat
FR-5:  Epic 1 — Question display with timer and live score
FR-6:  Epic 1 — Answer evaluation
FR-7:  Epic 1 — Win/loss determination (≥70%)
FR-8:  Epic 1 — Single-player results screen
FR-9:  Epic 2 — Player count entry (2–4)
FR-10: Epic 2 — Sequential turns, hide previous answers
FR-11: Epic 2 — Multiplayer leaderboard results screen
FR-12: Epic 1 — Base score
FR-13: Epic 1 — Speed Bonus formula
FR-14: Epic 1 — Streak counter
FR-15: Epic 1 — Streak Multiplier (1.5×/2×/3×)
FR-16: Epic 1 — Live score display (within one frame)
FR-17: Epic 1 — JSON loading at startup
FR-18: Epic 1 — Question schema validation
FR-19: Epic 1 — Category filtering
FR-20: Epic 1 — No-repeat draw

## Epic List

### Epic 1: Playable Single-Player Trivia App
A complete, fully-scored single-player game. The player can launch the app, navigate the menu, select a category, answer 10 questions under a timer with speed bonus and streak multiplier applied, and see a win/loss result with final score.
**FRs covered:** FR-1, FR-2, FR-3, FR-4, FR-5, FR-6, FR-7, FR-8, FR-12, FR-13, FR-14, FR-15, FR-16, FR-17, FR-18, FR-19, FR-20
**Architecture requirements:** AR-1 through AR-11

### Epic 2: Pass-and-Play Multiplayer
2–4 players share one device, each completing the same 10-question draw in sequence. A ranked leaderboard displays the winner by percentage after all turns complete.
**FRs covered:** FR-9, FR-10, FR-11

---

## Epic 1: Playable Single-Player Trivia App

A complete, fully-scored single-player game. The player can launch the app, navigate the menu, select a category, answer 10 questions under a timer with speed bonus and streak multiplier applied, and see a win/loss result with final score.

### Story 1.1: Project Scaffold and Core Data Models

As a developer,
I want the complete project scaffold created with all packages, `__init__.py` files, `GameState` dataclass, and `Player` dataclass implemented,
So that every subsequent story has the correct module structure and shared data contracts to build on.

**Acceptance Criteria:**

**Given** the project root `trivia-app/` with all directories and `__init__.py` files created
**When** I run `python main.py`
**Then** the app starts without import errors

**Given** `scoring/engine.py` is implemented
**When** I import `GameState` and `Player`
**Then** `GameState()` defaults to `current_screen="menu"`, `players=[]`; `Player(name="Test")` defaults to `score=0`, `streak=0`, `correct=0`, `total=0`

**Given** a `Player` with `correct=7` and `total=10`
**When** `player.percentage` is accessed
**Then** it returns `70.0`

**Given** a `Player` with `total=0`
**When** `player.percentage` is accessed
**Then** it returns `0.0` with no `ZeroDivisionError`

**Given** the full project structure
**When** module dependencies are inspected
**Then** `scoring/` imports nothing from `ui/` or `questions/`; `questions/` imports nothing from `ui/` or `scoring/`; all imports are absolute

---

### Story 1.2: Question Bank Loading and Validation

As a player,
I want the app to load trivia questions from JSON files at startup and validate each record,
So that only well-formed questions are available during gameplay and missing files are caught immediately.

**Acceptance Criteria:**

**Given** valid `data/questions_politics.json` and `data/questions_history.json` exist
**When** the app starts
**Then** both files load successfully and `loader.py` returns a list of validated question dicts

**Given** a question record with all required fields (`question_text`, `options` 4-element list, `correct_index` 0–3, `category` `"Politics"` or `"History"`)
**When** `loader.py` validates it
**Then** the record is included in the loaded list

**Given** a question record missing the `correct_index` field
**When** `loader.py` encounters it
**Then** the record is skipped, a `logging.WARNING` is emitted, and no exception is raised (FR-18)

**Given** `data/questions_politics.json` does not exist
**When** the app starts
**Then** `sys.exit()` is called with a user-facing error message before the menu renders (FR-17)

**Given** category `"Politics"` is selected
**When** `bank.draw_questions("Politics", n=10)` is called
**Then** only records with `category == "Politics"` are returned (FR-19)

**Given** a category with ≥10 valid questions
**When** `bank.draw_questions()` is called
**Then** exactly 10 unique questions are returned with no repetitions (FR-20)

**Given** `tests/test_loader.py` and `tests/test_bank.py` exist
**When** the tests run without PyGame installed
**Then** all tests pass

---

### Story 1.3: Scoring Engine Pure Functions

As a player,
I want the scoring system to correctly calculate base score, speed bonus, and streak multiplier for each correct answer,
So that my score accurately reflects how quickly and consistently I answered.

**Acceptance Criteria:**

**Given** `base_score=100`, `time_elapsed=0.0`, `timer_duration=30.0`
**When** `calculate_speed_bonus(100, 0.0, 30.0)` is called
**Then** it returns `100` (maximum bonus at instant answer)

**Given** `base_score=100`, `time_elapsed=15.0`, `timer_duration=30.0`
**When** `calculate_speed_bonus(100, 15.0, 30.0)` is called
**Then** it returns `50` (50% bonus at half time elapsed)

**Given** `base_score=100`, `time_elapsed=30.0`, `timer_duration=30.0`
**When** `calculate_speed_bonus(100, 30.0, 30.0)` is called
**Then** it returns `0` (no bonus at expiry)

**Given** `streak=1`
**When** `get_multiplier(1)` is called
**Then** it returns `1.0`

**Given** `streak=2` / `streak=3` / `streak=5`
**When** `get_multiplier(streak)` is called
**Then** it returns `1.5` / `2.0` / `3.0` respectively (FR-15)

**Given** `ui/constants.py` is created
**When** its contents are inspected
**Then** it defines `BASE_SCORE = 100` — the fixed points awarded per correct answer before bonuses (MC-1 / FR-12)

**Given** `scoring/engine.py` and `scoring/multiplier.py` are imported
**When** their module dependencies are checked
**Then** neither imports `pygame` (AR-6)

**Given** `tests/test_engine.py` and `tests/test_multiplier.py` exist
**When** the tests run without PyGame installed
**Then** all tests pass

---

### Story 1.4: Main Menu — Mode and Category Selection

As a player,
I want to see a main menu where I can choose single-player mode, select a category, and quit,
So that I can configure and start a game or exit on my terms.

**Acceptance Criteria:**

**Given** the app starts
**When** the main menu renders
**Then** a PyGame window displays a "Single Player" button and a "Quit" button

**Given** the player clicks "Single Player"
**When** the screen updates
**Then** category selection renders with "Politics" and "History" buttons visible

**Given** the player clicks "Politics" on the category screen
**When** the selection is confirmed
**Then** `GameState.selected_mode == "single"`, `GameState.selected_category == "Politics"`, and the screen transitions to the game screen

**Given** the player clicks "Quit" from the main menu
**When** the event is processed
**Then** the PyGame window closes and the process exits cleanly (FR-3)

**Given** the menu screen renders
**When** any colour, font size, or dimension is applied
**Then** all values come from `ui/constants.py` — no magic numbers in `menu_screen.py`

---

### Story 1.5: Game Screen — Question Display and Timer

As a player,
I want to see each question with four answer buttons and a countdown timer,
So that I can read and respond to each question before time runs out.

**Acceptance Criteria:**

**Given** a single-player game starts with category "Politics"
**When** the game screen first renders
**Then** one question displays with its `question_text` and exactly four answer buttons labelled with `options` values

**Given** the game screen is active
**When** the timer starts
**Then** a visible countdown from 30 seconds is displayed, decrementing each second (OQ-1)

**Given** the timer reaches 0 with no answer selected
**When** expiry is processed
**Then** the question is marked incorrect, streak resets to 0, and after a 1-second pause the next question displays (OQ-4: auto-advance)

**Given** all 10 questions in the draw have been answered or timed out
**When** `current_question_index == 10`
**Then** the screen transitions to the results screen

**Given** a round is in progress
**When** questions are displayed sequentially
**Then** no question appears twice in the same round (FR-20)

---

### Story 1.6: Answer Evaluation and Live Scoring

As a player,
I want my score, streak, and last multiplier to update instantly when I click an answer,
So that I get immediate feedback and can track my progress through the round.

**Acceptance Criteria:**

**Given** the player clicks the correct answer button
**When** the answer is evaluated
**Then** `player.score` increases by `int((base_score + speed_bonus) * streak_multiplier)`, `player.correct` increments by 1, and `player.streak` increments by 1

**Given** the player clicks an incorrect answer button
**When** the answer is evaluated
**Then** `player.score` does not change, `player.streak` resets to 0, and the correct answer is highlighted for 1 second before advancing (consistent with OQ-4 timer expiry behaviour)

**Given** the player just answered correctly with `streak == 2`
**When** the game screen redraws
**Then** displayed score, streak (2), and last multiplier (1.5×) all reflect updated values within the same rendered frame (NFR-2 / SM-2)

**Given** answer evaluation triggers scoring calls
**When** `calculate_speed_bonus` and `get_multiplier` are invoked
**Then** `game_screen.py` reads `pygame.time.get_ticks()` and passes elapsed time as a parameter — `scoring/` is never called with PyGame clock access (AR-6)

**Given** all 10 questions are answered
**When** `player.total == 10`
**Then** the screen transitions to the results screen with `GameState` intact

---

### Story 1.7: Single-Player Results Screen

As a player,
I want to see my final score, percentage correct, and a win/loss verdict after the round ends,
So that I know how I performed and can return to the main menu.

**Acceptance Criteria:**

**Given** a player answered 8 of 10 correctly
**When** the results screen renders
**Then** it displays the cumulative score, "80%", and "You Win!"

**Given** a player answered 6 of 10 correctly
**When** the results screen renders
**Then** it displays the cumulative score, "60%", and "You Lose"

**Given** a player answered exactly 7 of 10 correctly
**When** the results screen renders
**Then** it displays "70%" and "You Win!" (≥70% = win boundary, FR-7)

**Given** the player clicks "Main Menu"
**When** navigation is triggered
**Then** `GameState` resets (players cleared, indices zeroed) and the screen transitions to the main menu

---

## Epic 2: Pass-and-Play Multiplayer

2–4 players share one device, each completing the same 10-question draw in sequence. A ranked leaderboard displays the winner by percentage after all turns complete.

### Story 2.1: Multiplayer Setup — Player Count and Names

As players,
I want to select "Pass-and-Play" from the main menu, enter the number of players and each player's name,
So that we can set up a multiplayer session with clearly identified participants.

**Acceptance Criteria:**

**Given** the main menu is displayed
**When** the player clicks the "Pass-and-Play" button (added in this story)
**Then** a player count entry screen renders with a numeric input accepting values 2–4

**Given** the player count screen is displayed
**When** a value outside 2–4 is submitted
**Then** an inline error message is shown and the entry is rejected without navigating away (FR-9)

**Given** a valid player count (e.g., 3) is confirmed
**When** the count is accepted
**Then** a name entry screen prompts sequentially for each player's name (Player 1, Player 2, Player 3)

**Given** a player submits an empty or whitespace-only name
**When** the name is confirmed
**Then** an inline error is shown and the name field is not accepted — the player must enter a non-empty name (MC-2)

**Given** all player names are entered and confirmed
**When** the last name is submitted
**Then** `GameState.players` is populated with a `Player` object for each name, `GameState.selected_mode == "multiplayer"`, and the screen transitions to the game screen

**Given** the game screen starts in multiplayer mode
**When** the first question is displayed
**Then** the active player's name (`GameState.players[0].name`) is prominently shown on screen (FR-10)

---

### Story 2.2: Sequential Turn Management

As players,
I want each player's turn to follow the previous one with a handoff screen between turns,
So that we take turns fairly without seeing each other's answers.

**Acceptance Criteria:**

**Given** it is Player 1's turn and they answer all 10 questions
**When** `current_question_index` reaches 10 for Player 1
**Then** a "Pass to [Player 2 name]" handoff screen is displayed and the game pauses until the next player confirms

**Given** the handoff screen is shown
**When** the next player taps to begin
**Then** the game screen resets (question index back to 0, same 10-question draw reused, Player 1's score not visible) and the active player's name updates (FR-10)

**Given** Player 2 answers question 1
**When** the question object is inspected
**Then** it is the same object as the one Player 1 answered at index 0 — shared draw confirmed (FR-10, OQ-3)

**Given** all players have completed their turns
**When** `active_player_index` exceeds the last player index
**Then** the screen transitions to the multiplayer results screen

---

### Story 2.3: Multiplayer Results Leaderboard

As players,
I want to see a ranked leaderboard of all players by score percentage with the winner declared,
So that we know who performed best and can celebrate the outcome.

**Acceptance Criteria:**

**Given** 3 players finished with percentages 80%, 60%, 70%
**When** the multiplayer results screen renders
**Then** players are listed in descending percentage order: 80% → 70% → 60% (FR-11)

**Given** the leaderboard is displayed
**When** the top player is identified
**Then** the highest-percentage player is highlighted and declared "Winner!" (FR-11)

**Given** two players tie with equal percentages
**When** the results screen renders
**Then** both are listed at the same rank with no tiebreaker applied (FR-11 assumption)

**Given** the player clicks "Main Menu"
**When** navigation is triggered
**Then** `GameState` fully resets and the screen transitions to the main menu

**Given** `GameState.selected_mode == "multiplayer"`
**When** `results_screen.py` renders
**Then** it displays the leaderboard layout, not the single-player win/loss layout — mode branch confirmed
