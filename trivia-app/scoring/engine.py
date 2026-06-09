from dataclasses import dataclass, field


@dataclass
class GameState:
    current_screen: str = "menu"          # "menu" | "game" | "results"
    selected_mode: str = ""               # "single" | "multiplayer"
    selected_category: str = ""           # "Politics" | "History"
    players: list = field(default_factory=list)   # list[Player]
    active_player_index: int = 0
    current_question_index: int = 0
    questions: list = field(default_factory=list) # current round draw


@dataclass
class Player:
    name: str
    score: int = 0
    streak: int = 0
    correct: int = 0
    total: int = 0

    @property
    def percentage(self) -> float:
        return (self.correct / self.total * 100) if self.total > 0 else 0.0


def calculate_speed_bonus(base_score: int, time_elapsed: float, timer_duration: float) -> int:
    ratio = max(0.0, 1.0 - (time_elapsed / timer_duration))
    return int(base_score * ratio)
