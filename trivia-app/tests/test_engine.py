import sys

import pytest

from scoring.engine import calculate_speed_bonus


def test_max_bonus_at_instant_answer():
    assert calculate_speed_bonus(100, 0.0, 30.0) == 100


def test_half_bonus_at_half_time():
    assert calculate_speed_bonus(100, 15.0, 30.0) == 50


def test_zero_bonus_at_expiry():
    assert calculate_speed_bonus(100, 30.0, 30.0) == 0


def test_zero_bonus_past_expiry():
    assert calculate_speed_bonus(100, 35.0, 30.0) == 0


def test_proportional_bonus_at_10s():
    # ratio = 1.0 - 10/30 = 0.6666..., int(100 * 0.6666) = 66
    assert calculate_speed_bonus(100, 10.0, 30.0) == 66


def test_returns_int():
    result = calculate_speed_bonus(100, 5.0, 30.0)
    assert isinstance(result, int)


def test_no_pygame_in_scoring_engine():
    import scoring.engine
    src = open(scoring.engine.__file__, encoding="utf-8").read()
    assert "pygame" not in src
    assert "from ui" not in src
    assert "from questions" not in src
