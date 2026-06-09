---
inputDocuments: []
session_topic: 'Python trivia app (single-player and multiplayer)'
session_goals: 'Rich feature list, clear MVP scope, creative standout mechanics'
selected_approach: 'progressive-flow'
techniques_used: ['What If Scenarios', 'Mind Mapping', 'SCAMPER Method', 'Resource Constraints']
ideas_generated: 24
context_file: ''
stepsCompleted: [1, 2, 3, 4]
technique_execution_complete: true
---

# Brainstorming Session Results

**Facilitator:** A974997
**Date:** 2026-06-08

## Session Overview

**Topic:** Python trivia app supporting single-player and multiplayer modes

**Goals:** Generate a rich feature list, define a clear MVP scope, and discover creative mechanics that make the app stand out.

### Session Setup

Starting concept provided by the user:
- **Single-player:** 10 questions; player scoring >70% is the winner
- **Multiplayer:** player with the highest score percentage wins

Open space to explore: question sourcing and variety, multiplayer mechanics, scoring twists, replayability, interface, and edge cases.

## Technique Selection

**Approach:** Progressive Technique Flow
**Journey Design:** Systematic development from expansive exploration to buildable action plan

**Progressive Techniques:**

- **Phase 1 - Exploration:** What If Scenarios — break all constraints for maximum idea generation
- **Phase 2 - Pattern Recognition:** Mind Mapping — organize ideas into themes and territories
- **Phase 3 - Development:** SCAMPER Method — refine best concepts into standout mechanics
- **Phase 4 - Action Planning:** Resource Constraints — force ruthless MVP prioritization

**Journey Rationale:** Phases 1–2 build the rich feature list, Phase 3 forges standout mechanics, Phase 4 carves out a clear, buildable MVP scope.

## Ideas Generated

### Phase 1 — Expansive Exploration (What If Scenarios)

_Facilitator drove generation at user's request ("make your own decision and continue"). Domains pivoted to maintain divergence._

**Domain A — Question Content & Sourcing**

**[A1]: Type-a-Topic Quiz**
_Concept_: Player enters any subject and the app generates a 10-question quiz on the fly instead of using a fixed bank.
_Novelty_: Turns a static quiz into infinite replayable content; no two sessions identical.

**[A2]: Living Question Pool**
_Concept_: Questions auto-refresh from "today in history" or daily news so the trivia is always current.
_Novelty_: Reason to open the app daily; trivia becomes a habit, not a one-off.

**[A3]: Stump-Your-Friend**
_Concept_: In multiplayer, each player secretly authors the questions their opponent must answer.
_Novelty_: Converts trivia from a knowledge test into a social duel; players become content creators.

**[A4]: Adaptive Difficulty**
_Concept_: Correct answers escalate difficulty; misses ease it, keeping every player near their challenge edge.
_Novelty_: Single fixed "70% = winner" bar becomes a dynamic, personalized skill curve.

**Domain B — Multiplayer & Social**

**[B1]: Simultaneous Reveal**
_Concept_: All players lock answers privately, then a dramatic synchronized reveal.
_Novelty_: Removes turn-order advantage; creates game-show tension in a CLI.

**[B2]: Steal Mechanic**
_Concept_: A missed question becomes available for an opponent to "steal" for points.
_Novelty_: Keeps every player engaged on every question, even ones that aren't "theirs."

**[B3]: Team Trivia (2v2)**
_Concept_: Players pair into teams that submit one shared answer per question.
_Novelty_: Adds negotiation/debate; scales beyond head-to-head.

**[B4]: Pass-and-Play Async**
_Concept_: Leave a completed challenge with your score; a friend plays the same set later to beat it.
_Novelty_: Multiplayer without simultaneous presence — works for a single-machine CLI.

**Domain C — Scoring & Mechanics**

**[C1]: Speed Bonus**
_Concept_: Faster correct answers earn more points than slow ones.
_Novelty_: Replaces flat percentage scoring with a skill+reflex blend.

**[C2]: Wager System**
_Concept_: Bet points before seeing each question (Jeopardy-style confidence betting).
_Novelty_: Adds risk management and strategy on top of raw knowledge.

**[C3]: Streak Multiplier**
_Concept_: Consecutive correct answers compound a multiplier that resets on a miss.
_Novelty_: Creates tension and momentum; rewards consistency over luck.

**[C4]: Lifelines at a Cost**
_Concept_: 50/50, hint, or skip available — but each spends points.
_Novelty_: Introduces resource-management decisions into a simple quiz.

**Domain D — Interface & Feel**

**[D1]: Retro Game-Show CLI**
_Concept_: Terminal-first, but with ASCII art, color, and a game-show aesthetic.
_Novelty_: Personality and delight without needing a GUI.

**[D2]: Sassy Host Persona**
_Concept_: A narrator character delivers banter, taunts, and praise between questions.
_Novelty_: Emotional engagement and replay charm from a text interface.

**[D3]: Audio Countdown Cues**
_Concept_: Beep-ladder countdown and answer sounds, even in a CLI.
_Novelty_: Multi-sensory tension layered onto plain text.

**Domain E — Black Swan / Wild**

**[E1]: Sabotage Cards**
_Concept_: Spend points to shorten an opponent's answer timer or hide an option.
_Novelty_: Direct player-vs-player interference turns trivia competitive, not parallel.

**[E2]: Liar's Trivia**
_Concept_: Each question includes a convincingly plausible wrong answer; confidence is tested, not just recall.
_Novelty_: Rewards critical thinking and skepticism over memorization.

**[E3]: The Unanswerable**
_Concept_: An occasional genuinely unanswerable question rewards players for honestly saying "I don't know."
_Novelty_: Subverts the entire premise; teaches intellectual humility as a scored skill.

### Phase 2 — Pattern Recognition (Mind Mapping)

Five thematic territories emerged from the Phase 1 ideas:

- **Content Engine** (A1, A2, A4) — solves replayability; highest-leverage cluster.
- **Competition Structure** (B1–B4) — splits by whether players share presence; B4 async is the pragmatic path for a single-machine CLI.
- **Scoring System** (C1–C4) — thinnest area in the original spec; cheapest path to "game feel."
- **Feel/UX** (D1–D3) — personality and delight from a terminal interface.
- **Subversion / Wildcards** (E1–E3) — bold differentiators, optional/advanced.

**Connective insight:** A1 (type-a-topic) and A3 (stump-your-friend) are the same underlying primitive — "someone chooses the subject."

### Phase 3 — Idea Development (SCAMPER)

Running the strongest concepts through the seven SCAMPER lenses:

- **Substitute** — Replace the fixed 10-question bank with a category-driven generator; replace "70% threshold" with a relative leaderboard so single-player still has a target (beat your own best).
- **Combine** — Merge Speed Bonus (C1) + Streak Multiplier (C3) into one "momentum score" so fast, consistent play compounds; combine Wager (C2) with the final question for a Jeopardy-style "Final Trivia" climax.
- **Adapt** — Adapt Adaptive Difficulty (A4) so the >70% win condition scales: win = beating the difficulty-adjusted par, not a flat percentage.
- **Modify / Magnify** — Magnify the host persona (D2) into the emotional core; modify timer length per difficulty tier.
- **Put to other use** — Repurpose the question generator as a "study mode" (no scoring, just learning); repurpose async challenges (B4) as shareable challenge codes.
- **Eliminate** — Eliminate the need for a GUI (CLI-first); eliminate manual question authoring by leaning on a generator or a simple JSON bank for v1.
- **Reverse** — Reverse the quiz (E2 Liar's Trivia: find the lie); reverse scoring so the player sets the wager/risk before seeing difficulty.

**Forged standout mechanics (SCAMPER output):**

**[S1]: Momentum Score**
_Concept_: Speed + streak combine into a single compounding multiplier; flat percentage becomes a dynamic, exciting tally.
_Novelty_: Differentiates from every "X correct out of 10" quiz; rewards flow.

**[S2]: Final Trivia Wager**
_Concept_: A climactic last question where players wager part of their score before seeing it.
_Novelty_: Built-in dramatic comeback potential — trailing players can still win.

**[S3]: Difficulty-Adjusted Win Condition**
_Concept_: Winning means beating an adaptive "par," not a flat 70%, so the bar matches player skill.
_Novelty_: Keeps both novices and experts challenged within the same game.

**[S4]: Study Mode (Reuse)**
_Concept_: Same engine, scoring off — a no-pressure learning loop.
_Novelty_: Doubles the app's audience (learners + competitors) at near-zero extra cost.

### Phase 4 — Action Planning (Resource Constraints)

Forcing question: "One weekend, Python standard library only — what ships?"

**MVP (v1) — honors original spec:**

- 10 questions per single-player round; **>70% = winner** (original rule kept).
- Multiplayer: pass-and-play on one machine; highest percentage wins (original rule kept).
- Questions loaded from a simple `questions.json` bank with category support (no live generator yet).
- Pure CLI with ANSI color codes (stdlib-friendly).
- Two high-leverage standout mechanics included in v1:
  - **Speed bonus (C1)** — `time.time()` deltas, very low cost.
  - **Streak multiplier (C3)** — single counter, high game-feel payoff.

**Roadmap:**

| Wave | Features |
|------|----------|
| v1 (weekend) | 10-Q rounds, 70% win, pass-and-play MP, JSON bank, speed + streak |
| v2 | Category selection UI, Final Trivia Wager (S2), host persona (D2), study mode (S4) |
| v3 | Adaptive difficulty (A4), type-a-topic generator (A1), async challenge codes |
| v-wild | Liar's Trivia (E2), sabotage cards (E1), real-time multiplayer |

**Key architectural decision (decide on day one):** Separate modules for (a) question loading/management, (b) scoring logic, (c) CLI I/O. This keeps v2/v3 additive rather than requiring a rewrite.

**Immediate next steps:**

1. Define the `questions.json` schema (question, options, answer, category, difficulty).
2. Build the single-player loop with 70% win check.
3. Add speed bonus + streak multiplier to scoring.
4. Layer pass-and-play multiplayer (loop players, compare percentages).
5. Add ANSI color and a simple results screen.

## Summary

A 4-phase progressive brainstorm took the original "10-question, 70%-to-win" trivia concept and expanded it into 24 ideas across five territories (Content Engine, Competition Structure, Scoring, Feel/UX, Subversion), forged four standout mechanics via SCAMPER, and converged on a weekend-buildable, stdlib-only MVP that preserves the user's original rules while adding speed-bonus and streak mechanics for differentiation. A clear v1→v-wild roadmap and a modular architecture decision were captured to keep future waves additive.

