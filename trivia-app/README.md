# Python Trivia App

A desktop trivia game for 1–4 players. Test your knowledge of Politics and History,
race the clock, and chain correct answers to build massive score multipliers.

---

## Requirements

- Windows 10 or 11
- Python 3.14 or later — [download at python.org](https://www.python.org/downloads/)
  - During installation, check **"Add Python to PATH"** — this is required.

---

## Installation

> **First time only.** Do these steps once after downloading and unzipping the game folder.

1. Open **PowerShell** (search "PowerShell" in the Start menu).
2. Navigate into the game folder:

```powershell
cd trivia-app
```

3. Run the following commands one at a time:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

You should see packages downloading and installing. When it finishes, you are ready to play.

---

## Starting the Game

Every time you want to play, open PowerShell, navigate to the game folder, activate
the environment, and launch the game:

```powershell
cd trivia-app
.venv\Scripts\Activate.ps1
python main.py
```

> **Why the second step?** The `.venv\Scripts\Activate.ps1` line activates the game's
> private set of software. It is needed each time you open a fresh PowerShell window.
> Once activated, you will see `(.venv)` at the start of the prompt.

The game window will open. Use your mouse to navigate menus and click answers.

---

## Game Modes

### Single Player
Pick a category, answer 10 questions, and see if you can hit 70% correct or better to win.

### Pass-and-Play (2–4 players)
Share one device. Players take turns answering the same 10 questions. A handoff screen
appears between each turn so the next player cannot see the previous player's answers.
When everyone is done, a ranked leaderboard shows the final standings.

---

## How to Play

1. **Choose a mode** — Single Player or Pass-and-Play.

2. **If Pass-and-Play:** enter the number of players (2–4), then type each player's
   name and press **Enter** to confirm.

3. **Choose a category** — Politics or History.
   > Each category contains 12 questions; 10 are selected each round, so questions
   > may vary between games.

4. **Answer questions** — four options appear on screen. Click your answer before the
   30-second timer runs out.
   > If the timer expires, the question is marked wrong and your streak resets.

5. **See your results:**
   - **Single Player:** your final score and a Win (≥70% correct) or Lose (<70%) verdict.
   - **Pass-and-Play:** a leaderboard ranked by percentage correct. If two players tie,
     they share the same rank (for example, two players at 80% both receive 1st place,
     and the next player receives 3rd).

6. Click **Main Menu** to start a new game.

---

## Scoring

Every correct answer earns points in three layers that multiply together:

| What happened | Points |
|---|---|
| Correct answer | 100 base points |
| Answer quickly | Up to 100 bonus points (the more time remaining, the higher the bonus) |
| No streak yet (or after a wrong answer) | ×1.0 — no change |
| 2 correct in a row | ×1.5 multiplier on that answer's total |
| 3 or 4 correct in a row | ×2.0 multiplier |
| 5 or more correct in a row | ×3.0 multiplier |
| Wrong answer or timer expires | Streak resets to 0 |

**How the math works:** base points + speed bonus = subtotal, then the streak multiplier is applied to that subtotal.

> **Example:** Answer correctly with 5 seconds remaining on a 3-answer streak →
> 100 base + ~83 speed bonus = 183 × 2.0 = **366 points**.

---

## Controls

| Action | How |
|---|---|
| Select an answer or click a button | Left-click |
| Enter player count or a player's name | Type on keyboard, press **Enter** to confirm |
| Fix a typo in a name | **Backspace** |
| Advance the handoff screen (Pass-and-Play) | Click anywhere or press any key |

---

## Troubleshooting

**"python is not recognized as the name of a cmdlet..."**
Python is not installed or was not added to PATH. Reinstall Python from [python.org](https://www.python.org/downloads/) and check the **"Add Python to PATH"** box on the first screen of the installer.

**Game window does not open, or "ERROR: Question bank not found"**
You are likely running the command from the wrong folder. Make sure you have run `cd trivia-app` first so PowerShell is inside the game folder before running `python main.py`.

**Error about "running scripts is disabled" when activating `.venv`**
Run this once to allow it, then try again:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**Game starts but looks wrong or crashes immediately**
Make sure `(.venv)` appears in your PowerShell prompt before running `python main.py`. If not, run `.venv\Scripts\Activate.ps1` first.
