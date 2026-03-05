import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from logic_utils import check_guess, get_range_for_difficulty

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
