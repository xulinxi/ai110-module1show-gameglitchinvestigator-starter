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
  4. `update_score` inconsistently penalized "Too High" guesses — on even attempts it awarded +5 points instead of the intended -5 penalty, giving players a reward for wrong guesses.

- [x] Explain what fixes you applied.
- [x] **Fixes applied:**
  - `logic_utils.py`: Corrected Normal to `(1, 50)` and Hard to `(1, 100)`.
  - `app.py`: Replaced hardcoded `"1 and 100"` in the info message with `{low} and {high}`.
  - `app.py`: Replaced `random.randint(1, 100)` in the New Game button with `random.randint(low, high)`.
  - `logic_utils.py`: Fixed `update_score` to always subtract 5 for "Too High" guesses, matching the consistent -5 penalty for "Too Low".

## 📸 Demo

- [x] [<img width="742" height="170" alt="Screenshot 2026-03-04 at 10 55 16 PM" src="https://github.com/user-attachments/assets/52851ec4-ac6e-4b5f-94d2-d2fc5b432cc1" />]  

## 🚀 Stretch Features

- [x] Challenge 1: Advanced Edge Case Testing
  - **Bugs fixed in `parse_guess`:**
    - Decimal truncation — changed `int(float(raw))` to `int(float(raw) + 0.5)` so `"5.6"` → 6 and `".5"` → 1 (round half-up).
    - Missing range validation — added post-parse checks that reject values below 1 (`"0"`, `"-3"`) and above 100 (`"999"`, `"1.5e3"`).
  - **Updated edge-case tests** — existing `parse_guess` test comments and function names updated to reflect the fixed behavior:
    - `test_parse_guess_decimal_rounds_half_up` — documents the round-half-up fix for `"5.6"` → 6
    - `test_parse_guess_dot_five_rounds_to_one` — clarifies that `".5"` → 1 via `0.5 + 0.5 = 1.0`, not truncation
    - `test_parse_guess_scientific_notation_with_dot` — now rejected by the `>100` range check (1500), not a parse error
    - `test_parse_guess_negative`, `test_parse_guess_zero` — now rejected by the `<1` range check
    - `test_parse_guess_out_of_range_high` — now rejected by the `>100` range check
  - **Total test count: 31 tests — all passing.**
  - <img width="1112" height="171" alt="Screenshot 2026-03-08 at 8 58 27 PM" src="https://github.com/user-attachments/assets/de63fefe-90b9-476b-92d5-b04bc7cda11b" />


- [x] Challenge 2: Feature Expansion via Agent Mode
  - **Feature added:** Persistent High Score Tracker — saves the best score per difficulty to `high_score.json` and displays it in the sidebar.
  - **Agent's role:** Claude Code designed and implemented the full feature end-to-end in Agent Mode: added `load_high_scores` and `save_high_score` to `logic_utils.py`, wired the sidebar display and win-branch banner into `app.py`, and wrote 8 pytest tests covering edge cases (missing file, malformed JSON, updating only when better, multiple difficulties, equal score not overwritten). The agent also diagnosed a Streamlit input-delay issue caused by file I/O on every rerun and applied a `@st.cache_data` fix, clearing the cache after a win so the sidebar always reflects the latest record.
  - <img width="281" height="260" alt="Screenshot 2026-03-08 at 2 38 00 PM" src="https://github.com/user-attachments/assets/e39679c8-9f64-4a7d-ad2c-ded30bfdac86" />


- [x] Challenge 3: Professional Documentation and Linting
  - **Docstrings:** Every function in `logic_utils.py` received a full Google-style docstring with a one-line summary, behavior description, `Args:`, `Returns:`, and `Examples:` blocks — covering all six functions: `get_range_for_difficulty`, `parse_guess`, `check_guess`, `update_score`, `load_high_scores`, and `save_high_score`.
  - **PEP 8 fixes applied across `app.py` and `tests/test_game_logic.py`:**
    - **E302** — added 2 blank lines between all top-level function definitions (affected every test function and `cached_high_scores` in `app.py`)
    - **E501** — broke long lines: split the `from logic_utils import ...` statement into a multi-line parenthesized import; wrapped the win `st.success(...)` call across two lines
    - **E712** — replaced all `== True` / `== False` comparisons with `is True` / `is False` in test assertions
    - **E401** — moved `import json` from inside `test_load_high_scores_valid_file` to the top of the test file
    - **W291** — removed trailing whitespace on two lines in the test file
  - **Agent's role:** Claude Code reviewed all three source files for PEP 8 compliance and applied all fixes using the Fix feature.


- [x] Challenge 4: Enhanced Game UI
  - **Features added (all purely presentational — core logic untouched):**
    - **Color-coded outcome messages** — `st.error` (red) for Too High, `st.warning` (yellow) for Too Low, `st.success` (green) for Win, with emojis (📉 / 📈 / 🎉) and the running score shown inline after each guess.
    - **Hot/Cold proximity indicator** — after each wrong guess, a `get_proximity_hint()` helper computes how close the guess is as a fraction of the difficulty range and returns a tiered emoji label: 🔥 Scorching! (≤5%), 🌡️ Warm (≤15%), 🧊 Chilly (≤35%), ❄️ Ice cold! (>35%). Only shown when the "Show hint" checkbox is checked.
    - **End-of-game summary table** — when the game ends (win or lose), `st.table` renders a full session log showing Attempt #, Guess, Result, Hot/Cold, and Score for every valid guess. Powered by a new `history_detail` session state list that is reset on New Game.
  - **Agent's role:** Claude Code implemented all three enhancements in `app.py`, introducing `get_proximity_hint()` as a pure helper and `history_detail` as a session state list, without modifying `check_guess`, `update_score`, `parse_guess`, or any logic in `logic_utils.py`.
  - <img width="784" height="717" alt="Screenshot 2026-03-08 at 8 52 49 PM" src="https://github.com/user-attachments/assets/875b18db-b72d-40ee-9854-fd38390f4650" />

