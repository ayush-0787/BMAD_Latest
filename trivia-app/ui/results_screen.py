import logging

import pygame

from ui.constants import (
    ACCENT, BLACK, BUTTON_HEIGHT, BUTTON_HOVER, BUTTON_WIDTH,
    FONT_LARGE, FONT_MEDIUM, FONT_SMALL, GREEN, MARGIN,
    RED, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE,
)
from ui.screen_manager import Screen


class ResultsScreen(Screen):
    def __init__(self):
        self._font_large = None
        self._font_medium = None
        self._font_small = None

    def _ensure_fonts(self) -> None:
        if self._font_large is None:
            self._font_large = pygame.font.SysFont(None, FONT_LARGE)
            self._font_medium = pygame.font.SysFont(None, FONT_MEDIUM)
            self._font_small = pygame.font.SysFont(None, FONT_SMALL)

    def _get_menu_button_rect(self) -> pygame.Rect:
        return pygame.Rect(
            SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
            SCREEN_HEIGHT - BUTTON_HEIGHT - MARGIN,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
        )

    def handle_events(self, events, game_state) -> str | None:
        if not game_state.players:
            return None
        menu_rect = self._get_menu_button_rect()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if menu_rect.collidepoint(event.pos):
                    if game_state.selected_mode == "multiplayer":
                        winner = max(game_state.players, key=lambda p: p.percentage)
                        logging.info(
                            "Results: %d players, winner=%s pct=%.1f%% → main menu",
                            len(game_state.players),
                            winner.name,
                            winner.percentage,
                        )
                    else:
                        player = game_state.players[0]
                        logging.info(
                            "Results: player=%s score=%d pct=%.1f%% → main menu",
                            player.name,
                            player.score,
                            player.percentage,
                        )
                    game_state.players = []
                    game_state.active_player_index = 0
                    game_state.current_question_index = 0
                    game_state.questions = []
                    game_state.selected_mode = ""
                    game_state.selected_category = ""
                    return "menu"
        return None

    def update(self, game_state, dt: float) -> None:
        pass

    def draw(self, surface, game_state) -> None:
        self._ensure_fonts()
        if not game_state.players:
            return
        if game_state.selected_mode == "multiplayer":
            self._draw_multiplayer(surface, game_state)
        else:
            self._draw_single(surface, game_state)

    def _draw_single(self, surface, game_state) -> None:
        player = game_state.players[0]
        pct = player.percentage
        verdict = "You Win!" if pct >= 70.0 else "You Lose"
        verdict_color = GREEN if pct >= 70.0 else RED

        surface.fill(BLACK)

        y = SCREEN_HEIGHT // 6

        title_surf = self._font_large.render("Results", True, WHITE)
        surface.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, y)))

        y += FONT_LARGE + MARGIN // 2
        score_surf = self._font_medium.render(f"Score: {player.score}", True, WHITE)
        surface.blit(score_surf, score_surf.get_rect(center=(SCREEN_WIDTH // 2, y)))

        y += FONT_MEDIUM + MARGIN // 2
        pct_surf = self._font_medium.render(f"{pct:.0f}%", True, WHITE)
        surface.blit(pct_surf, pct_surf.get_rect(center=(SCREEN_WIDTH // 2, y)))

        y += FONT_MEDIUM + MARGIN
        verdict_surf = self._font_large.render(verdict, True, verdict_color)
        surface.blit(verdict_surf, verdict_surf.get_rect(center=(SCREEN_WIDTH // 2, y)))

        y += FONT_LARGE + MARGIN // 2
        count_surf = self._font_small.render(
            f"{player.correct} / {player.total} correct", True, WHITE
        )
        surface.blit(count_surf, count_surf.get_rect(center=(SCREEN_WIDTH // 2, y)))

        menu_rect = self._get_menu_button_rect()
        mouse_pos = pygame.mouse.get_pos()
        color = BUTTON_HOVER if menu_rect.collidepoint(mouse_pos) else ACCENT
        pygame.draw.rect(surface, color, menu_rect, border_radius=8)
        label_surf = self._font_medium.render("Main Menu", True, WHITE)
        surface.blit(label_surf, label_surf.get_rect(center=menu_rect.center))

    def _draw_multiplayer(self, surface, game_state) -> None:
        sorted_players = sorted(game_state.players, key=lambda p: p.percentage, reverse=True)
        top_pct = sorted_players[0].percentage

        surface.fill(BLACK)

        y = SCREEN_HEIGHT // 8

        title_surf = self._font_large.render("Results", True, WHITE)
        surface.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, y)))

        y += FONT_LARGE + MARGIN // 2
        winner_surf = self._font_large.render(f"Winner: {sorted_players[0].name}!", True, GREEN)
        surface.blit(winner_surf, winner_surf.get_rect(center=(SCREEN_WIDTH // 2, y)))

        y += FONT_LARGE + MARGIN
        prev_pct = None
        rank = 0
        for player in sorted_players:
            pct = player.percentage
            if pct != prev_pct:
                rank += 1
                prev_pct = pct
            row_color = GREEN if pct == top_pct else WHITE
            row_text = f"{rank}.  {player.name}   {player.score}   {pct:.0f}%"
            row_surf = self._font_medium.render(row_text, True, row_color)
            surface.blit(row_surf, row_surf.get_rect(center=(SCREEN_WIDTH // 2, y)))
            y += FONT_MEDIUM + MARGIN // 4

        menu_rect = self._get_menu_button_rect()
        mouse_pos = pygame.mouse.get_pos()
        color = BUTTON_HOVER if menu_rect.collidepoint(mouse_pos) else ACCENT
        pygame.draw.rect(surface, color, menu_rect, border_radius=8)
        label_surf = self._font_medium.render("Main Menu", True, WHITE)
        surface.blit(label_surf, label_surf.get_rect(center=menu_rect.center))
