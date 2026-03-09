import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from logic_utils import (
    check_guess,
    get_range_for_difficulty,
    parse_guess,
    update_score,
    load_high_scores,
    save_high_score,
)


def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"


def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"


def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"


def test_easy_mode_range():
    # Easy mode should be capped at 20, not 100
    low, high = get_range_for_difficulty("Easy")
    assert low == 1
    assert high == 20, f"Easy mode upper bound should be 20, got {high}"


def test_normal_mode_range():
    low, high = get_range_for_difficulty("Normal")
    assert low == 1
    assert high == 50


def test_hard_mode_range():
    low, high = get_range_for_difficulty("Hard")
    assert low == 1
    assert high == 100


def test_update_score_win_early():
    # Win on attempt 0 should give max points (100 - 10*(0+1) = 90)
    result = update_score(0, "Win", 0)
    assert result == 90


def test_update_score_win_late():
    # Win on attempt 9 should give minimum 10 points
    result = update_score(0, "Win", 9)
    assert result == 10


def test_update_score_too_high_even_attempt():
    # "Too High" on even attempt should subtract 5 (not add 5)
    result = update_score(100, "Too High", 0)
    assert result == 95


def test_update_score_too_high_odd_attempt():
    # "Too High" on odd attempt should also subtract 5
    result = update_score(100, "Too High", 1)
    assert result == 95


def test_update_score_too_low():
    result = update_score(100, "Too Low", 0)
    assert result == 95


def test_update_score_no_change():
    result = update_score(100, "Unknown", 0)
    assert result == 100


# --- parse_guess edge cases ---


def test_parse_guess_valid_integer():
    ok, value, err = parse_guess("42")
    assert ok is True
    assert value == 42
    assert err is None


def test_parse_guess_empty_string():
    ok, value, err = parse_guess("")
    assert ok is False
    assert err == "Enter a guess."


def test_parse_guess_none():
    ok, value, err = parse_guess(None)
    assert ok is False
    assert err == "Enter a guess."


def test_parse_guess_non_numeric():
    ok, value, err = parse_guess("abc")
    assert ok is False
    assert err == "That is not a number."


def test_parse_guess_decimal_rounds_half_up():
    # "5.6" rounds half-up to 6 via int(float(raw) + 0.5)
    ok, value, err = parse_guess("5.6")
    assert ok is True
    assert value == 6


def test_parse_guess_dot_five_rounds_to_one():
    # ".5" → float 0.5 + 0.5 = 1.0 → int 1; also passes the ≥1 range check
    ok, value, err = parse_guess(".5")
    assert ok is True
    assert value == 1


def test_parse_guess_scientific_notation_with_dot():
    # "1.5e3" has "." so goes through float path → 1500, rejected by >100 range check
    ok, value, err = parse_guess("1.5e3")
    assert ok is False
    assert value is None
    assert err is not None


def test_parse_guess_negative():
    # "-3" parses to -3, rejected by the <1 range check
    ok, value, err = parse_guess("-3")
    assert ok is False
    assert value is None
    assert err is not None


def test_parse_guess_zero():
    # "0" parses to 0, rejected by the <1 range check (minimum valid value is 1)
    ok, value, err = parse_guess("0")
    assert ok is False
    assert value is None
    assert err is not None


def test_parse_guess_out_of_range_high():
    # "999" parses to 999, rejected by the >100 range check
    ok, value, err = parse_guess("999")
    assert ok is False
    assert value is None
    assert err is not None


def test_parse_guess_whitespace_around_number():
    # Python's int() strips whitespace, so "  5  " parses as 5
    ok, value, err = parse_guess("  5  ")
    assert ok is True
    assert value == 5


# --- high score tests ---


def test_load_high_scores_missing_file(tmp_path):
    filepath = str(tmp_path / "hs.json")
    result = load_high_scores(filepath)
    assert result == {}


def test_load_high_scores_valid_file(tmp_path):
    filepath = str(tmp_path / "hs.json")
    with open(filepath, "w") as f:
        json.dump({"Easy": 80, "Hard": 50}, f)
    result = load_high_scores(filepath)
    assert result == {"Easy": 80, "Hard": 50}


def test_load_high_scores_malformed_file(tmp_path):
    filepath = str(tmp_path / "hs.json")
    with open(filepath, "w") as f:
        f.write("not valid json{{{")
    result = load_high_scores(filepath)
    assert result == {}


def test_save_high_score_creates_file(tmp_path):
    filepath = str(tmp_path / "hs.json")
    save_high_score("Normal", 70, filepath)
    result = load_high_scores(filepath)
    assert result.get("Normal") == 70


def test_save_high_score_updates_when_better(tmp_path):
    filepath = str(tmp_path / "hs.json")
    save_high_score("Easy", 50, filepath)
    save_high_score("Easy", 90, filepath)
    result = load_high_scores(filepath)
    assert result.get("Easy") == 90


def test_save_high_score_skips_when_worse(tmp_path):
    filepath = str(tmp_path / "hs.json")
    save_high_score("Hard", 80, filepath)
    save_high_score("Hard", 30, filepath)
    result = load_high_scores(filepath)
    assert result.get("Hard") == 80


def test_save_high_score_multiple_difficulties(tmp_path):
    filepath = str(tmp_path / "hs.json")
    save_high_score("Easy", 60, filepath)
    save_high_score("Normal", 75, filepath)
    save_high_score("Hard", 90, filepath)
    result = load_high_scores(filepath)
    assert result == {"Easy": 60, "Normal": 75, "Hard": 90}


def test_save_high_score_equal_not_overwritten(tmp_path):
    filepath = str(tmp_path / "hs.json")
    save_high_score("Easy", 70, filepath)
    save_high_score("Easy", 70, filepath)
    result = load_high_scores(filepath)
    assert result.get("Easy") == 70
