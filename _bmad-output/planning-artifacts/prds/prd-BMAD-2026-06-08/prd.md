---
title: Python Trivia App
status: final
created: 2026-06-08
updated: 2026-06-08
---

# PRD: Python Trivia App

## 0. Document Purpose

This PRD defines what the Python Trivia App must do — not how to build it. Written for the builder (A974997) and downstream workflows (architecture, epics). Glossary terms are used verbatim throughout. Assumptions are tagged `[ASSUMPTION]` inline and indexed in §9. Primary input: `_bmad-output/planning-artifacts/briefs/brief-BMAD-2026-06-08/brief.md`.

---

## 1. Vision

A PyGame desktop trivia game supporting single-player and pass-and-play multiplayer, with Questions drawn from Politics and History categories. The builder's goal is hands-on mastery of PyGame's core patterns — event loop, screen rendering, multi-screen state management, clock/timers, and scorekeeping — through a project that ships a real, playable artifact. Shipping a complete, working product is the proof of learning. The app is the vehicle; the skills are the destination.

---

## 2. Target User

**Jobs To Be Done**

- *Functional:* Play a trivia game on a desktop, alone or with friends nearby.
- *Learning:* Build a complete GUI application in Python and understand every layer of it.
- *Demonstrative:* Produce a portfolio artifact proving end-to-end PyGame competence.

**Key User Journeys**

- **UJ-1.** Builder launches the app, selects single-player + History, answers 10 Questions under a timer, and sees a win/loss result with final score.
- **UJ-2.** Two players sit at one machine, each takes a turn through the same 10-Question draw, and a ranked results screen declares the winner.

---

## 3. Glossary

- **Round** — A single completed game session of 10 Questions for one Player.
- **Question** — A trivia item comprising question text, four Answer Options, and one correct answer, belonging to one Category.
- **Question Bank** — The JSON file containing all Questions, loaded at app startup.
- **Category** — A thematic filter for Questions. Valid values: `Politics`, `History`.
- **Answer Option** — One of four selectable choices presented per Question.
- **Base Score** — Points awarded for a correct answer before Speed Bonus or Streak Multiplier are applied.
- **Speed Bonus** — Additional points scaled inversely to the time taken to answer correctly within a Round.
- **Streak** — A counter incremented by consecutive correct answers; resets to zero on any miss.
- **Streak Multiplier** — A score multiplier derived from the current Streak value, applied to Base Score + Speed Bonus.
- **Pass-and-Play** — Multiplayer mode in which 2–4 Players share one device and take turns sequentially.
- **Session** — One full execution of the app from launch to quit, potentially containing multiple Rounds.

---

## 4. Features

*FRs are numbered globally (FR-1 through FR-20) for stable downstream references.*

### 4.1 Main Menu & Navigation

Entry screen where Players select game mode and Category before starting a Round. Realizes UJ-1, UJ-2.

#### FR-1: Mode selection
Player selects Single-Player or Pass-and-Play mode from the Main Menu.
- Selecting Single-Player routes to a single Round for one Player.
- Selecting Pass-and-Play prompts for player count before the Round begins.

#### FR-2: Category selection
Player selects one Category (Politics or History); the Round draws only from that Category's Questions.
- Only Questions matching the selected Category are eligible for the draw.
- Both Categories must be populated in the Question Bank at startup; a missing Category surfaces an error.

#### FR-3: Quit
Player can exit the app from the Main Menu without starting a Round.

---

### 4.2 Single-Player Mode

A solo Round of 10 Questions. The app evaluates correctness and delivers a win/loss verdict at Round end. Realizes UJ-1.

#### FR-4: Question draw
System randomly draws 10 Questions from the selected Category without repetition within a Round.
- If the selected Category has fewer than 10 Questions in the Question Bank, the app surfaces an error rather than repeating Questions.

#### FR-5: Question display
System displays one Question at a time with its four Answer Options, a visible countdown timer, and the Player's live score.
- Timer counts down from a fixed duration per Question. [ASSUMPTION: 30 seconds per Question — see OQ-1]
- Timer expiry counts as an incorrect answer.

#### FR-6: Answer evaluation
System evaluates the Player's selected Answer Option immediately on selection.
- Correct: Base Score, Speed Bonus, and Streak Multiplier are calculated and added to the live score.
- Incorrect: Streak resets to zero; no points awarded.

#### FR-7: Win/loss determination
System determines win or loss at Round end: ≥70% correct answers = win; <70% = loss.
- Win/loss verdict displays on the Results screen alongside final score and percentage.

#### FR-8: Results screen (single-player)
System displays final score, percentage correct, and win/loss verdict on a dedicated Results screen, with navigation back to the Main Menu.

---

### 4.3 Pass-and-Play Multiplayer

2–4 Players share one device, each completing the same 10-Question draw in sequence. Highest score percentage wins. Realizes UJ-2.

#### FR-9: Player count entry
System prompts for the number of Players (2–4) before a Pass-and-Play Round begins. [ASSUMPTION: 2–4 players]
- A player count outside 2–4 is rejected with an inline error.

#### FR-10: Sequential turns
System presents each Player's turn in sequence and prompts the next Player before their turn begins, so the previous Player's answers are not visible.
- All Players answer the same 10-Question draw. [ASSUMPTION: shared draw for fairness — see OQ-3]

#### FR-11: Multiplayer results screen
System displays a ranked leaderboard of all Players by score percentage after all turns complete; the highest-percentage Player is declared the winner.
- Tied players are listed together; no tiebreaker in v1. [ASSUMPTION]
- Results screen offers navigation back to the Main Menu.

---

### 4.4 Scoring Engine

Computes the score for each correct answer using Base Score, Speed Bonus, and Streak Multiplier, all displayed in real time on the Game Screen. Realizes UJ-1, UJ-2.

#### FR-12: Base score
System awards a fixed Base Score for each correct answer; incorrect answers and timer expiry award zero.

#### FR-13: Speed Bonus
System awards Speed Bonus points scaled inversely with elapsed time between Question display and the Player's answer, using PyGame's clock.
- Maximum Speed Bonus at near-zero elapsed time; zero at or after timer expiry.
- Applies only to correct answers.
- [ASSUMPTION: Speed Bonus = Base Score × (time_remaining / timer_duration), yielding a 0–100% bonus proportional to answer speed — confirm or adjust at architecture phase; see OQ-1]

#### FR-14: Streak tracking
System increments the Streak counter on each consecutive correct answer and resets it to zero on any incorrect answer or timer expiry.
- Streak counter is visible on the Game Screen in real time.

#### FR-15: Streak Multiplier application
System applies the Streak Multiplier to (Base Score + Speed Bonus) for each correct answer while Streak > 0.
- [ASSUMPTION: Streak 2 = 1.5×, Streak 3 = 2×, Streak 5+ = 3× — confirm or adjust at architecture phase; see OQ-2]
- Resulting score is added to the Player's cumulative Round score.

#### FR-16: Live score display
System displays the Player's current score, active Streak count, and last-applied Streak Multiplier on the Game Screen, updating within one rendered frame of answer submission.

---

### 4.5 Question Bank

All Questions load from a JSON file at app startup, carrying category metadata that enables filtered draws. Realizes FR-2, FR-4.

#### FR-17: JSON loading
System loads the Question Bank from a JSON file at startup before the Main Menu renders.
- A missing or malformed JSON file surfaces a startup error and halts launch.

#### FR-18: Question schema
Each Question record contains: question text, four Answer Options, correct answer index (0–3), and Category.
- Records missing any required field are skipped and logged; they are not presented to the Player.

#### FR-19: Category filtering
System filters the Question Bank to the selected Category when drawing Questions for a Round; Questions from unselected Categories are excluded entirely.

#### FR-20: No-repeat draw
System draws Questions without repetition within a single Round using a randomised sample; a fresh draw is performed at the start of each Round, not per Session.

---

## 5. Non-Goals (Explicit)

- No online or networked multiplayer — single-device only.
- No adaptive difficulty — fixed Question pool, no player-skill tracking.
- No live or AI-generated Questions — static JSON bank only.
- No sound effects or music.
- No user accounts, login, or persistent leaderboards across Sessions.
- No mobile or web version — desktop PyGame only.
- No localisation — English only.

---

## 6. MVP Scope

**In Scope**

- PyGame desktop app: Main Menu, Game Screen, Results Screen
- Single-player mode (10 Questions, ≥70% = win)
- Pass-and-Play multiplayer (2–4 players, ranked by percentage)
- Politics and History categories, selectable at game start
- Multiple-choice format (4 Answer Options per Question)
- Speed Bonus and Streak Multiplier, rendered live on Game Screen
- JSON Question Bank (~30 Questions per Category) [ASSUMPTION]
- Modular code structure — three named modules as a design constraint from day one: `questions` (bank loading and draw), `scoring` (base score, speed bonus, streak), `ui` (screens and rendering)

**Out of Scope for MVP**

- Online multiplayer — deferred to v3+
- Adaptive difficulty — deferred to v3
- Type-any-topic question generator — deferred to v3
- Host narrator character — deferred to v2
- Final Trivia wager mechanic — deferred to v2
- Study mode (no-scoring) — deferred to v2
- Sound, music, accounts, leaderboards — deferred indefinitely

*The three-module boundary above is the reason every v2/v3 item is listed as additive rather than a rewrite.*

---

## 7. Success Metrics

**Primary**
- **SM-1:** Both game modes complete end-to-end without unhandled exceptions. Validates FR-4 through FR-11.
- **SM-2:** Speed Bonus and Streak Multiplier values update on the Game Screen within one frame of each answer. Validates FR-13 through FR-16.
- **SM-3:** Questions load and filter correctly by Category at game start. Validates FR-17 through FR-20.

**Secondary**
- **SM-4:** Builder can explain and reproduce PyGame's event loop, surface/rect rendering, screen transition pattern, and clock/timer without reference material (self-assessed). A shipped, playable product is the primary evidence. Validates the learning goal.

**Counter-metric (do not optimise)**
- **SM-C1:** Session count after one week of completion — if zero, the app was abandoned and the learning vehicle failed its purpose. Counterbalances SM-4.

---

## 8. Open Questions

1. **OQ-1:** What is the per-Question timer duration? (Assumed 30 seconds; affects Speed Bonus scale in FR-13 — confirm.)
2. **OQ-2:** What is the Streak Multiplier scale? (Assumed 1.5× / 2× / 3× at streaks 2 / 3 / 5+ — confirm or adjust at architecture phase.)
3. **OQ-3:** Should all Pass-and-Play players answer the same 10-Question draw, or get independent random draws? (Assumed shared draw for fairness — confirm.)
4. **OQ-4:** On timer expiry, does the Game Screen auto-advance or wait for the Player to acknowledge the miss?

---

## 9. Assumptions Index

- **§2 / Brief** — Secondary audience is incidental; app not published or distributed in v1.
- **§4.2 / FR-5** — 30-second timer per Question (OQ-1).
- **§4.3 / FR-9** — Pass-and-Play supports 2–4 players.
- **§4.3 / FR-10** — All Pass-and-Play players answer the same draw (OQ-3).
- **§4.3 / FR-11** — Tied players share rank; no tiebreaker in v1.
- **§4.4 / FR-13** — Speed Bonus formula: Base Score × (time_remaining / timer_duration) (OQ-1, OQ-2).
- **§4.4 / FR-15** — Streak Multiplier scale: 1.5× / 2× / 3× at streaks 2 / 3 / 5+ (OQ-2).
- **§6.1** — ~30 Questions per Category in the initial JSON bank.
- **§6.1** — 4 Answer Options per Question.
- **Platform** — Windows is the primary dev/test platform; PyGame is cross-platform by nature.
