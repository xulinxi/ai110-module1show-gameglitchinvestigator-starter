def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
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
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
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
    """
    Compare guess to secret and return outcome string only: "Win", "Too High", or "Too Low".

    This function prefers numeric comparison when possible to avoid TypeError from
    comparing ints and strings. If numeric conversion fails it falls back to string
    comparison.
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
    """Update score based on outcome and attempt number."""
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score
