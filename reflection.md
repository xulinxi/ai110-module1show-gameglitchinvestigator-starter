# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the secret number kept changing" or "the hints were backwards").

  1. When the guess is lower than the secret number, the hint incorrectly says to go lower instead of higher.  
  2. Easy mode go over 20. Need to check other modes' ranges too.
  3. The hints do not update immediately — you have to guess twice before the feedback appears.

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

I used Claude Code (Anthropic) as my AI teammate throughout this project.

**Correct suggestion — identifying the every-other-guess hint bug:**
Claude analyzed `app.py` lines 101–104 and correctly identified that on even-numbered attempts, the secret number was being cast to a string (`secret = str(st.session_state.secret)`), which caused `check_guess` to fall back to lexicographic string comparison instead of numeric comparison. This produced wrong hints on every other guess. I verified this by reading the code myself and confirming that `"9" > "50"` evaluates to `True` in Python string comparison, which would flip the hint direction.

**Incorrect/misleading suggestion — swapping Normal and Hard test expectations:**
When I reported that the difficulty ranges were wrong, Claude assumed the bug was in the *test file* and "corrected" the expected values — changing Normal's expected upper bound from 50 to 100, and Hard's from 100 to 50 — to match the buggy `logic_utils.py`. This was backwards: the tests were right and `logic_utils.py` was the source of the bug. I caught this by re-reading `logic_utils.py` directly and confirming that Normal and Hard ranges were swapped there, not in the tests.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

I decided a bug was really fixed when the game behavior matched the expected outcome — correct hints, correct ranges displayed in the UI, and consistent results across attempts — not just when the code looked right.

For the difficulty range bug, I wrote and ran three pytest tests in `tests/test_game_logic.py`: `test_easy_mode_range`, `test_normal_mode_range`, and `test_hard_mode_range`. Each called `get_range_for_difficulty()` directly and asserted the correct `(low, high)` tuple. When the Normal and Hard values were still swapped in `logic_utils.py`, the tests for those two modes failed, which confirmed exactly where the bug lived. Once I corrected the return values in `logic_utils.py`, all three tests passed.

For the every-other-guess hint bug, I verified it by reading `app.py` and tracing through the logic manually: on odd attempts `secret` is an `int`, on even attempts it becomes a `str`, and Python's string comparison (`"9" > "50"` is `True`) produces the wrong result. I also visually confirmed the fix by running the game and submitting multiple guesses in a row to check that hints were consistent on every attempt, not just every other one.

Claude helped design the range tests by suggesting `get_range_for_difficulty` as the right function to target and generating the initial test stubs. However, I had to verify and correct the expected values myself after Claude mistakenly swapped them, which reinforced the importance of reading test assertions carefully rather than trusting generated test code at face value.

---

## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app.
The secret number kept changing because every time you clicked a button in Streamlit, the entire Python script re-ran from the top. That meant `random.randint()` was called again on every button click, generating a new secret number each time — so you could never actually win since the target kept moving.

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
Streamlit reruns your whole script every time the user interacts with anything — a button click, a text input, anything. Think of it like refreshing a webpage: all your variables reset. Session state (`st.session_state`) is how you save values across those reruns — it's like a small notebook Streamlit keeps for you between reloads. Anything stored in `st.session_state` survives the rerun, while regular variables get wiped.

- What change did you make that finally gave the game a stable secret number?
The fix was wrapping the secret number generation in a guard: `if "secret" not in st.session_state: st.session_state.secret = random.randint(low, high)`. This means the secret is only generated once — the first time the app loads — and stays the same for the rest of the game.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
Writing unit tests alongside code changes is a habit I want to carry forward. This project showed that tests are most useful when written at the same time as the fix, because they force you to think precisely about the correct behavior. I also learned to be very specific in prompts, vague descriptions like "the ranges are wrong" led the AI to fix the wrong thing, while pointing directly at the file and function got faster, more accurate results. One more lesson: tests can pass even when functions are wrong, especially when they involve random numbers or when the expected values themselves are incorrect, so always verify assertions by hand.

- What is one thing you would do differently next time you work with AI on a coding task?
Next time I work with AI on a coding task, I would verify every generated test's expected values by hand before running them. This project had a case where the AI wrote tests that would pass even against buggy code because the expected values were wrong, tests that always pass give false confidence.

- In one or two sentences, describe how this project changed the way you think about AI generated code.
This project changed how I think about AI-generated code by showing that AI can introduce subtle bugs that look correct at first glance. AI is a useful starting point, but every suggestion needs to be read critically and verified, not just accepted because it looks reasonable.
