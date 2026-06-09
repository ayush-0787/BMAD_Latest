import logging
import sys

import pygame

from questions.bank import draw_questions
from scoring.engine import Player
from ui.constants import (
    ACCENT, BLACK, BUTTON_HEIGHT, BUTTON_HOVER, BUTTON_PADDING, BUTTON_WIDTH,
    FONT_LARGE, FONT_MEDIUM, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE,
)
from ui.screen_manager import Screen


class MenuScreen(Screen):
    def __init__(self, all_questions: list):
        self._all_questions = all_questions
        self._stage = "mode"   # "mode" | "category"
        self._font_large = None
        self._font_medium = None

    def _ensure_fonts(self) -> None:
        if self._font_large is None:
            self._font_large = pygame.font.SysFont(None, FONT_LARGE)
            self._font_medium = pygame.font.SysFont(None, FONT_MEDIUM)

    def _get_buttons(self) -> dict:
        cx = SCREEN_WIDTH // 2
        half_w = BUTTON_WIDTH // 2
        if self._stage == "mode":
            total_h = 3 * BUTTON_HEIGHT + 2 * BUTTON_PADDING
            y = SCREEN_HEIGHT // 2 - total_h // 2
            return {
                "single": pygame.Rect(cx - half_w, y, BUTTON_WIDTH, BUTTON_HEIGHT),
                "multi":  pygame.Rect(cx - half_w, y + BUTTON_HEIGHT + BUTTON_PADDING, BUTTON_WIDTH, BUTTON_HEIGHT),
                "quit":   pygame.Rect(cx - half_w, y + 2 * (BUTTON_HEIGHT + BUTTON_PADDING), BUTTON_WIDTH, BUTTON_HEIGHT),
            }
        y_top = SCREEN_HEIGHT // 2 - BUTTON_HEIGHT - BUTTON_PADDING // 2
        y_bot = y_top + BUTTON_HEIGHT + BUTTON_PADDING
        return {
            "Politics": pygame.Rect(cx - half_w, y_top, BUTTON_WIDTH, BUTTON_HEIGHT),
            "History":  pygame.Rect(cx - half_w, y_bot, BUTTON_WIDTH, BUTTON_HEIGHT),
        }

    def reset(self) -> None:
        self._stage = "mode"

    def handle_events(self, events, game_state) -> str | None:
        self._ensure_fonts()
        if not game_state.selected_mode and self._stage != "mode":
            self._stage = "mode"
        buttons = self._get_buttons()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for name, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        return self._on_click(name, game_state)
        return None

    def _on_click(self, name: str, game_state) -> str | None:
        if self._stage == "mode":
            if name == "single":
                game_state.selected_mode = "single"
                self._stage = "category"
                logging.info("Mode selected: single")
            elif name == "multi":
                logging.info("Mode selected: multiplayer -> setup screen")
                return "setup"
            elif name == "quit":
                logging.info("Quit selected from main menu")
                pygame.quit()
                sys.exit(0)
        elif self._stage == "category":
            game_state.selected_category = name
            game_state.players = [Player("Player 1")]
            game_state.questions = draw_questions(self._all_questions, name)
            game_state.current_question_index = 0
            game_state.active_player_index = 0
            logging.info("Category selected: %s — game starting", name)
            return "game"
        return None

    def update(self, game_state, dt: float) -> None:
        pass

    def draw(self, surface, game_state) -> None:
        self._ensure_fonts()
        buttons = self._get_buttons()
        mouse_pos = pygame.mouse.get_pos()

        surface.fill(BLACK)

        if self._stage == "mode":
            title_text = "Python Trivia"
            labels = {"single": "Single Player", "multi": "Pass-and-Play", "quit": "Quit"}
        else:
            title_text = "Select Category"
            labels = {"Politics": "Politics", "History": "History"}

        title = self._font_large.render(title_text, True, WHITE)
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)))

        for name, rect in buttons.items():
            color = BUTTON_HOVER if rect.collidepoint(mouse_pos) else ACCENT
            pygame.draw.rect(surface, color, rect, border_radius=8)
            label = self._font_medium.render(labels[name], True, WHITE)
            surface.blit(label, label.get_rect(center=rect.center))
