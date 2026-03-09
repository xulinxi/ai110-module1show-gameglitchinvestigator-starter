import json
import os


def get_range_for_difficulty(difficulty: str):
    """Return the inclusive (low, high) number range for a given difficulty level.

    Args:
        difficulty: One of "Easy", "Normal", or "Hard". Any unrecognized value
            falls back to the Hard range.

    Returns:
        A tuple (low, high) of ints representing the inclusive bounds of the
        secret number range for that difficulty.

    Examples:
        >>> get_range_for_difficulty("Easy")
        (1, 20)
        >>> get_range_for_difficulty("Hard")
        (1, 100)
    """
    if difficulty == "Easy":
        return 1, 20
    # FIX: Normal and Hard upper bounds were swapped (Normal had 100, Hard had 50).
    # Corrected to Normal=50, Hard=100 after user clarified intended ranges with Claude Code.
    if difficulty == "Normal":
        return 1, 50
    if difficulty == "Hard":
        return 1, 100
    return 1, 100


def parse_guess(raw: str):
    """Parse raw user input into an integer guess.

    Accepts plain integers ("42") and decimal strings ("5.6"), truncating
    decimals toward zero via ``int(float(raw))``. Rejects None, empty strings,
    and non-numeric input.

    Args:
        raw: The raw string entered by the user, or None if no input was given.

    Returns:
        A 3-tuple ``(ok, guess_int, error_message)`` where:
        - ``ok`` (bool): True if parsing succeeded, False otherwise.
        - ``guess_int`` (int | None): The parsed integer on success, else None.
        - ``error_message`` (str | None): A human-readable error on failure, else None.

    Examples:
        >>> parse_guess("42")
        (True, 42, None)
        >>> parse_guess("abc")
        (False, None, 'That is not a number.')
        >>> parse_guess("")
        (False, None, 'Enter a guess.')
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    """Compare a guess against the secret number and return the outcome.

    Prefers numeric comparison (both values converted to int) to avoid
    incorrect lexicographic ordering (e.g. ``"9" > "50"`` as strings).
    Falls back to string comparison only if either value cannot be converted
    to an integer.

    Args:
        guess: The player's guess. Accepts int or numeric string.
        secret: The secret number to guess. Accepts int or numeric string.

    Returns:
        One of three outcome strings:
        - ``"Win"`` if guess equals secret.
        - ``"Too High"`` if guess is greater than secret.
        - ``"Too Low"`` if guess is less than secret.

    Examples:
        >>> check_guess(50, 50)
        'Win'
        >>> check_guess(60, 50)
        'Too High'
        >>> check_guess(40, 50)
        'Too Low'
    """
    # Prefer numeric comparison when both can be converted to int
    try:
        g = int(guess)
        s = int(secret)
    except Exception:
        # Fall back to string comparison
        g = str(guess)
        s = str(secret)

        if g == s:
            return "Win"
        if g > s:
            return "Too High"
        return "Too Low"

    # Numeric comparison
    if g == s:
        return "Win"
    if g > s:
        return "Too High"
    return "Too Low"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Calculate and return the updated score after a guess.

    Scoring rules:
    - **Win**: awards ``100 - 10 * (attempt_number + 1)`` points, floored at 10.
      Earlier wins earn more points.
    - **Too High** or **Too Low**: deducts 5 points as a wrong-guess penalty.
    - Any other outcome: score is unchanged.

    Args:
        current_score: The player's score before this guess.
        outcome: The result string from ``check_guess`` — one of ``"Win"``,
            ``"Too High"``, or ``"Too Low"``.
        attempt_number: The 0-based index of the current attempt (e.g. 0 for
            the first guess, 1 for the second).

    Returns:
        The new integer score after applying the outcome.

    Examples:
        >>> update_score(0, "Win", 0)
        90
        >>> update_score(100, "Too High", 3)
        95
        >>> update_score(100, "Unknown", 0)
        100
    """
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score


# FEATURE: High Score Tracker added by Claude Code (Agent Mode).
# Persists the best score per difficulty to high_score.json so records survive
# across sessions. load_high_scores returns {} safely on missing or corrupt files;
# save_high_score only writes when the new score beats the stored record.
HIGH_SCORE_FILE = os.path.join(os.path.dirname(__file__), "high_score.json")


def load_high_scores(filepath: str = HIGH_SCORE_FILE) -> dict:
    """Load the high score table from a JSON file.

    Returns an empty dict safely if the file does not exist, cannot be read,
    or contains non-dict JSON (e.g. a corrupted file).

    Args:
        filepath: Path to the JSON file storing high scores. Defaults to
            ``high_score.json`` in the same directory as this module.

    Returns:
        A dict mapping difficulty name (str) to best score (int), e.g.
        ``{"Easy": 80, "Normal": 60, "Hard": 90}``. Returns ``{}`` on any
        error.

    Examples:
        >>> load_high_scores("/nonexistent/path.json")
        {}
    """
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
        return {}
    except Exception:
        return {}


def save_high_score(difficulty: str, score: int, filepath: str = HIGH_SCORE_FILE) -> None:
    """Persist a new high score for a difficulty if it beats the current record.

    Reads the existing high score table, updates the entry for ``difficulty``
    only if ``score`` strictly exceeds the stored value, then writes the table
    back to disk. Does nothing if the score is equal to or lower than the
    current record.

    Args:
        difficulty: The difficulty level the score was achieved on (e.g.
            ``"Easy"``, ``"Normal"``, ``"Hard"``).
        score: The player's final score to compare against the stored record.
        filepath: Path to the JSON file storing high scores. Defaults to
            ``high_score.json`` in the same directory as this module.

    Returns:
        None

    Examples:
        >>> save_high_score("Easy", 90)   # writes if 90 > current Easy record
        >>> save_high_score("Easy", 50)   # no-op if 50 <= current Easy record
    """
    scores = load_high_scores(filepath)
    if score > scores.get(difficulty, 0):
        scores[difficulty] = score
        with open(filepath, "w") as f:
            json.dump(scores, f)
