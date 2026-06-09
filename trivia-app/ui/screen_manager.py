from scoring.engine import GameState


class Screen:
    def handle_events(self, events, game_state) -> str | None:
        return None

    def update(self, game_state: GameState, dt: float) -> None:
        pass

    def draw(self, surface, game_state: GameState) -> None:
        pass


class ScreenManager:
    def __init__(self, all_questions: list):
        from ui.menu_screen import MenuScreen
        from ui.game_screen import GameScreen
        from ui.results_screen import ResultsScreen
        from ui.setup_screen import SetupScreen
        from ui.handoff_screen import HandoffScreen
        self.all_questions = all_questions
        self.screens = {
            "menu": MenuScreen(all_questions),
            "game": GameScreen(),
            "results": ResultsScreen(),
            "setup": SetupScreen(all_questions),
            "handoff": HandoffScreen(),
        }
        self.game_state = GameState()

    def run_frame(self, events, surface, dt: float) -> None:
        screen = self.screens[self.game_state.current_screen]
        next_screen = screen.handle_events(events, self.game_state)
        if next_screen:
            incoming = self.screens.get(next_screen)
            if incoming and hasattr(incoming, "reset"):
                incoming.reset()
            self.game_state.current_screen = next_screen
        screen.update(self.game_state, dt)
        screen.draw(surface, self.game_state)
