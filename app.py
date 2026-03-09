import random

import streamlit as st

from logic_utils import (
    get_range_for_difficulty,
    parse_guess,
    check_guess,
    update_score,
    load_high_scores,
    save_high_score,
)

# FEATURE: High Score Tracker added by Claude Code (Agent Mode).
# @st.cache_data prevents re-reading high_score.json on every keystroke rerun,
# eliminating the input delay caused by file I/O on each Streamlit interaction.
# cached_high_scores.clear() is called after a win so the sidebar updates immediately.
@st.cache_data
def cached_high_scores():
    return load_high_scores()


# FEATURE: Hot/Cold proximity hint added by Claude Code (Agent Mode).
# Computes how close the guess is as a fraction of the total difficulty range,
# returning an emoji label without touching any core game logic.
def get_proximity_hint(guess, secret, low, high):
    """Return a hot/cold emoji label based on proximity to the secret number."""
    range_size = high - low
    distance = abs(guess - secret)
    ratio = distance / range_size if range_size > 0 else 1.0
    if ratio <= 0.05:
        return "🔥 Scorching!"
    if ratio <= 0.15:
        return "🌡️ Warm"
    if ratio <= 0.35:
        return "🧊 Chilly"
    return "❄️ Ice cold!"


st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")
# FEATURE: Sidebar best-score display added by Claude Code (Agent Mode).
# Shows the all-time best score for the current difficulty, or "—" if none recorded yet.
high_scores = cached_high_scores()
best = high_scores.get(difficulty)
if best is not None:
    st.sidebar.caption(f"Best score on {difficulty}: {best}")
else:
    st.sidebar.caption(f"Best score on {difficulty}: —")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    st.session_state.attempts = 1

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

# FEATURE: Detailed history for summary table, added by Claude Code (Agent Mode).
# Tracks each valid guess with its outcome, hot/cold label, and running score
# so the end-of-game summary table can be built without re-computing anything.
if "history_detail" not in st.session_state:
    st.session_state.history_detail = []

st.subheader("Make a guess")

# FIX: Replaced hardcoded "1 and 100" with {low} and {high} so the message
# reflects the actual difficulty range. Identified by user testing, fixed with Claude Code.
st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    st.session_state.attempts = 0
    # FIX: Replaced hardcoded randint(1, 100) with randint(low, high) so New Game
    # respects the selected difficulty range. Identified by user testing, fixed with Claude Code.
    st.session_state.secret = random.randint(low, high)
    st.session_state.history_detail = []
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")

    # FEATURE: End-of-game summary table, added by Claude Code (Agent Mode).
    # Displayed after the game ends so the player can review every guess at a glance.
    if st.session_state.history_detail:
        st.subheader("📊 Session Summary")
        st.table(st.session_state.history_detail)

    st.stop()

if submit:
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(raw_guess)
        st.error(f"⚠️ {err}")
    else:
        st.session_state.history.append(guess_int)

        outcome = check_guess(guess_int, st.session_state.secret)

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        # FEATURE: Color-coded outcome hints with hot/cold emojis,
        # added by Claude Code (Agent Mode). Outcome display is purely presentational —
        # check_guess and update_score are called unchanged before this block.
        proximity = get_proximity_hint(
            guess_int, st.session_state.secret, low, high
        )
        hot_cold = proximity if show_hint and outcome != "Win" else ""

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            # FEATURE: Save and compare high score on win, added by Claude Code (Agent Mode).
            # Compares final score to the previous best before saving, so the
            # "New high score!" banner is only shown when the record is actually broken.
            previous_best = high_scores.get(difficulty, 0)
            save_high_score(difficulty, st.session_state.score)
            cached_high_scores.clear()
            st.success(
                f"🎉 You won! The secret was **{st.session_state.secret}**. "
                f"Final score: **{st.session_state.score}**"
            )
            if st.session_state.score > previous_best:
                st.info("🏆 New high score!")
        elif outcome == "Too High":
            st.error(f"📉 Too High! {hot_cold}  |  Score: {st.session_state.score}")
        else:
            st.warning(f"📈 Too Low! {hot_cold}  |  Score: {st.session_state.score}")

        st.session_state.history_detail.append({
            "Attempt": st.session_state.attempts,
            "Guess": guess_int,
            "Result": outcome,
            "Hot / Cold": hot_cold if hot_cold else "—",
            "Score": st.session_state.score,
        })

        if outcome != "Win" and st.session_state.attempts >= attempt_limit:
            st.session_state.status = "lost"
            st.error(
                f"💀 Out of attempts! "
                f"The secret was **{st.session_state.secret}**. "
                f"Final score: {st.session_state.score}"
            )

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
