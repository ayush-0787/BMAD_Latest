def get_multiplier(streak: int) -> float:
    if streak >= 5:
        return 3.0
    if streak >= 3:
        return 2.0
    if streak >= 2:
        return 1.5
    return 1.0


def apply_streak_multiplier(score: int, streak: int) -> int:
    return int(score * get_multiplier(streak))
