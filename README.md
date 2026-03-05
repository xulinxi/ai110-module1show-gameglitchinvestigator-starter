# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience
- [x] Describe the game's purpose.
- [x] **Game purpose:** A number guessing game where the player tries to guess a secret number within a limited number of attempts. The difficulty setting controls the range of possible numbers and attempts allowed. The game gives hints after each guess to guide the player toward the answer.

- [x] Detail which bugs you found.
- [x] **Bugs found:**
  1. Wrong hint direction on every other guess — the secret was cast to a string on even attempts, causing lexicographic comparison instead of numeric (e.g. `"9" > "50"` is `True` as strings), which flipped the hint.
  2. Difficulty ranges were swapped — `logic_utils.py` returned `(1, 100)` for Normal and `(1, 50)` for Hard when the intended ranges are Normal = 1–50 and Hard = 1–100.
  3. UI message and New Game button ignored difficulty — both hardcoded `1–100` regardless of the selected difficulty, so Easy mode (1–20) could still generate secrets up to 100.

- [x] Explain what fixes you applied.
- [x] **Fixes applied:**
  - `logic_utils.py`: Corrected Normal to `(1, 50)` and Hard to `(1, 100)`.
  - `app.py`: Replaced hardcoded `"1 and 100"` in the info message with `{low} and {high}`.
  - `app.py`: Replaced `random.randint(1, 100)` in the New Game button with `random.randint(low, high)`.

## 📸 Demo

- [x] [<img width="742" height="170" alt="Screenshot 2026-03-04 at 10 55 16 PM" src="https://github.com/user-attachments/assets/52851ec4-ac6e-4b5f-94d2-d2fc5b432cc1" />]  

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, insert a screenshot of your Enhanced Game UI here]
