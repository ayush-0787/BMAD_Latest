import sys

import pytest

from scoring.multiplier import apply_streak_multiplier, get_multiplier


def test_no_streak_multiplier():
    assert get_multiplier(0) == 1.0


def test_streak_1_multiplier():
    assert get_multiplier(1) == 1.0


def test_streak_2_multiplier():
    assert get_multiplier(2) == 1.5


def test_streak_3_multiplier():
    assert get_multiplier(3) == 2.0


def test_streak_4_multiplier():
    assert get_multiplier(4) == 2.0


def test_streak_5_multiplier():
    assert get_multiplier(5) == 3.0


def test_streak_10_multiplier():
    assert get_multiplier(10) == 3.0


def test_apply_no_streak():
    assert apply_streak_multiplier(100, 1) == 100


def test_apply_streak_2():
    assert apply_streak_multiplier(100, 2) == 150


def test_apply_streak_3():
    assert apply_streak_multiplier(100, 3) == 200


def test_apply_streak_5():
    assert apply_streak_multiplier(100, 5) == 300


def test_apply_returns_int():
    result = apply_streak_multiplier(100, 2)
    assert isinstance(result, int)


def test_apply_combined_score():
    # Story 1.6 pattern: apply_streak_multiplier(BASE_SCORE + speed_bonus, streak)
    # e.g. BASE_SCORE=100, speed_bonus=50, streak=2 → int(150 * 1.5) = 225
    assert apply_streak_multiplier(150, 2) == 225


def test_no_pygame_in_scoring_multiplier():
    import scoring.multiplier
    src = open(scoring.multiplier.__file__, encoding="utf-8").read()
    assert "pygame" not in src
    assert "from ui" not in src
    assert "from questions" not in src
