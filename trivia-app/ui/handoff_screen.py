import logging

import pygame

from ui.constants import (
    ACCENT, BLACK, FONT_LARGE, FONT_MEDIUM, FONT_SMALL, GREY, MARGIN,
    SCREEN_HEIGHT, SCREEN_WIDTH, WHITE,
)
from ui.screen_manager import Screen


class HandoffScreen(Screen):
    def __init__(self):
        self._font_large = None
        self._font_medium = None
        self._font_small = None

    def _ensure_fonts(self) -> None:
        if self._font_large is None:
            self._font_large = pygame.font.SysFont(None, FONT_LARGE)
            self._font_medium = pygame.font.SysFont(None, FONT_MEDIUM)
            self._font_small = pygame.font.SysFont(None, FONT_SMALL)

    def _advance_turn(self, game_state) -> str:
        game_state.active_player_index += 1
        game_state.current_question_index = 0
        logging.info(
            "Handoff: advancing to player %d (%s)",
            game_state.active_player_index,
            game_state.players[game_state.active_player_index].name,
        )
        return "game"

    def handle_events(self, events, game_state) -> str | None:
        if not game_state.players:
            return None
        for event in events:
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or event.type == pygame.KEYDOWN:
                return self._advance_turn(game_state)
        return None

    def update(self, game_state, dt: float) -> None:
        pass

    def draw(self, surface, game_state) -> None:
        self._ensure_fonts()
        if not game_state.players or game_state.active_player_index + 1 >= len(game_state.players):
            surface.fill(BLACK)
            return

        curr_player = game_state.players[game_state.active_player_index]
        next_player = game_state.players[game_state.active_player_index + 1]

        surface.fill(BLACK)

        y = SCREEN_HEIGHT // 6

        title_surf = self._font_large.render("Turn Complete!", True, WHITE)
        surface.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, y)))

        y += FONT_LARGE + MARGIN // 2
        done_surf = self._font_medium.render(f"{curr_player.name} is done", True, GREY)
        surface.blit(done_surf, done_surf.get_rect(center=(SCREEN_WIDTH // 2, y)))

        y += FONT_MEDIUM + MARGIN
        pass_surf = self._font_large.render(f"Pass to {next_player.name}", True, ACCENT)
        surface.blit(pass_surf, pass_surf.get_rect(center=(SCREEN_WIDTH // 2, y)))

        y += FONT_LARGE + MARGIN
        prompt_surf = self._font_small.render("Tap or click anywhere to begin", True, WHITE)
        surface.blit(prompt_surf, prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, y)))
