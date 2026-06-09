---
title: Python Trivia App
status: final
created: 2026-06-08
updated: 2026-06-08
---

# Product Brief: Python Trivia App

## Summary

A PyGame desktop trivia app built as a personal learning project. The app is the vehicle; the skills are the destination. Shipping a complete, playable product proves the learning.

**Builder goal:** Hands-on experience with PyGame's event loop, screen rendering, multi-screen state management, timers, and scorekeeping — covering the core GUI skill stack without physics or complex animation.

**Secondary audience:** Politics and history fans willing to run a Python desktop app. [ASSUMPTION: incidental; app not published or distributed in v1]

## Scope

**In for v1:**

- Three screens: main menu (mode + category selection), game screen (question, timer, live score), results screen (win/loss verdict or ranked leaderboard)
- Single-player mode: 10 random questions, >70% correct = win
- Pass-and-play multiplayer: 2–4 players on one machine, highest percentage wins [ASSUMPTION: 2–4 players]
- Politics and history categories, selectable at game start
- Multiple-choice format: 4 options per question [ASSUMPTION]
- Speed bonus: faster correct answers score more points (PyGame clock)
- Streak multiplier: consecutive correct answers compound score, reset on miss; both mechanics visible in real time
- JSON question bank (~30 questions per category) [ASSUMPTION]
- Modular code structure from day one: questions, scoring, and UI as separate modules

**Out of v1:**

- Online / networked multiplayer
- Adaptive difficulty or live question generation
- Sound effects, music, mobile, or web version
- User accounts or persistent leaderboards

## Success Criteria

- Builder can explain and replicate PyGame's core patterns (event loop, surface/rect rendering, screen transitions, clock/timer) without reference material
- Single-player and multiplayer flows complete end-to-end without crashes
- Speed bonus and streak multiplier update visibly in real time on the game screen
- Questions load from the JSON bank; category filtering works at game start

## Vision

If the learning goal is met and the app is enjoyable, v2 adds a host narrator character, a Final Trivia wager mechanic (bet points before the last question), and a study mode (no scoring). V3 adds a type-any-topic question generator. The modular architecture — questions, scoring, UI kept separate — is a deliberate day-one decision so every future addition is incremental, not a rewrite.
