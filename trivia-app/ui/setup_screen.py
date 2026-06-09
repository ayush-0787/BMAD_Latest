import logging

import pygame

from questions.bank import draw_questions
from scoring.engine import Player
from ui.constants import (
    ACCENT, BLACK, BUTTON_HEIGHT, BUTTON_HOVER, BUTTON_PADDING, BUTTON_WIDTH,
    FONT_LARGE, FONT_MEDIUM, FONT_SMALL, GREY, MARGIN, RED, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE,
)
from ui.screen_manager import Screen


class SetupScreen(Screen):
    def __init__(self, all_questions: list):
        self._all_questions = all_questions
        self._stage = "count"          # "count" | "names" | "category"
        self._player_count = 0
        self._player_names: list[str] = []
        self._current_name_idx = 0
        self._input_text = ""
        self._error_msg = ""
        self._font_large = None
        self._font_medium = None
        self._font_small = None

    def reset(self) -> None:
        self._stage = "count"
        self._player_count = 0
        self._player_names = []
        self._current_name_idx = 0
        self._input_text = ""
        self._error_msg = ""

    def _ensure_fonts(self) -> None:
        if self._font_large is None:
            self._font_large = pygame.font.SysFont(None, FONT_LARGE)
            self._font_medium = pygame.font.SysFont(None, FONT_MEDIUM)
            self._font_small = pygame.font.SysFont(None, FONT_SMALL)

    def _get_category_buttons(self) -> dict:
        cx = SCREEN_WIDTH // 2
        half_w = BUTTON_WIDTH // 2
        y_top = SCREEN_HEIGHT // 2 - BUTTON_HEIGHT - BUTTON_PADDING // 2
        y_bot = y_top + BUTTON_HEIGHT + BUTTON_PADDING
        return {
            "Politics": pygame.Rect(cx - half_w, y_top, BUTTON_WIDTH, BUTTON_HEIGHT),
            "History":  pygame.Rect(cx - half_w, y_bot, BUTTON_WIDTH, BUTTON_HEIGHT),
        }

    def _handle_count_key(self, event) -> None:
        if event.key == pygame.K_BACKSPACE:
            self._input_text = self._input_text[:-1]
            self._error_msg = ""
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self._validate_count()
        elif event.unicode.isdigit() and len(self._input_text) < 1:
            self._input_text += event.unicode
            self._error_msg = ""

    def _validate_count(self) -> None:
        try:
            n = int(self._input_text)
        except ValueError:
            self._error_msg = "Enter a number: 2, 3, or 4"
            self._input_text = ""
            return
        if not (2 <= n <= 4):
            self._error_msg = "Must be 2, 3, or 4 players"
            self._input_text = ""
            return
        self._player_count = n
        self._input_text = ""
        self._error_msg = ""
        self._stage = "names"
        logging.info("Player count set: %d", n)

    def _handle_name_key(self, event) -> None:
        if event.key == pygame.K_BACKSPACE:
            self._input_text = self._input_text[:-1]
            self._error_msg = ""
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self._validate_name()
        elif event.unicode and event.unicode.isprintable() and len(self._input_text) < 20:
            self._input_text += event.unicode
            self._error_msg = ""

    def _validate_name(self) -> None:
        name = self._input_text.strip()
        if not name:
            self._error_msg = "Name cannot be empty"
            return
        self._player_names.append(name)
        self._current_name_idx += 1
        self._input_text = ""
        self._error_msg = ""
        logging.info("Player %d name: %s", self._current_name_idx, name)
        if self._current_name_idx == self._player_count:
            self._stage = "category"

    def _on_category_click(self, pos, game_state) -> str | None:
        for cat, rect in self._get_category_buttons().items():
            if rect.collidepoint(pos):
                game_state.selected_mode = "multiplayer"
                game_state.selected_category = cat
                game_state.players = [Player(name) for name in self._player_names]
                game_state.questions = draw_questions(self._all_questions, cat)
                game_state.active_player_index = 0
                game_state.current_question_index = 0
                logging.info(
                    "Multiplayer starting: %d players, category=%s",
                    len(self._player_names), cat,
                )
                return "game"
        return None

    def handle_events(self, events, game_state) -> str | None:
        self._ensure_fonts()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self._stage == "count":
                    self._handle_count_key(event)
                elif self._stage == "names":
                    self._handle_name_key(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._stage == "category":
                    result = self._on_category_click(event.pos, game_state)
                    if result:
                        return result
        return None

    def update(self, game_state, dt: float) -> None:
        pass

    def draw(self, surface, game_state) -> None:
        self._ensure_fonts()
        surface.fill(BLACK)
        if self._stage == "count":
            self._draw_count_stage(surface)
        elif self._stage == "names":
            self._draw_names_stage(surface)
        elif self._stage == "category":
            self._draw_category_stage(surface)

    def _draw_count_stage(self, surface) -> None:
        title = self._font_large.render("Pass-and-Play", True, WHITE)
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)))

        prompt = self._font_medium.render("Number of players? (2-4)", True, WHITE)
        prompt_y = SCREEN_HEIGHT // 4 + FONT_LARGE + MARGIN // 2
        surface.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, prompt_y)))

        box_y = SCREEN_HEIGHT // 2 - BUTTON_HEIGHT // 2
        box_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - BUTTON_WIDTH // 4,
            box_y,
            BUTTON_WIDTH // 2,
            BUTTON_HEIGHT,
        )
        pygame.draw.rect(surface, ACCENT, box_rect, border_radius=4)
        cursor = "|" if pygame.time.get_ticks() // 500 % 2 == 0 else ""
        input_surf = self._font_large.render(self._input_text + cursor, True, WHITE)
        surface.blit(input_surf, input_surf.get_rect(center=box_rect.center))

        if self._error_msg:
            err_surf = self._font_small.render(self._error_msg, True, RED)
            surface.blit(err_surf, err_surf.get_rect(
                center=(SCREEN_WIDTH // 2, box_y + BUTTON_HEIGHT + MARGIN // 2)
            ))

        hint = self._font_small.render("Press Enter to confirm", True, GREY)
        surface.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - MARGIN)))

    def _draw_names_stage(self, surface) -> None:
        title = self._font_large.render("Enter Names", True, WHITE)
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)))

        prompt_text = f"Player {self._current_name_idx + 1} of {self._player_count}:"
        prompt = self._font_medium.render(prompt_text, True, WHITE)
        prompt_y = SCREEN_HEIGHT // 4 + FONT_LARGE + MARGIN // 2
        surface.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, prompt_y)))

        box_y = SCREEN_HEIGHT // 2 - BUTTON_HEIGHT // 2
        box_rect = pygame.Rect(
            SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2,
            box_y,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
        )
        pygame.draw.rect(surface, ACCENT, box_rect, border_radius=4)
        cursor = "|" if pygame.time.get_ticks() // 500 % 2 == 0 else ""
        input_surf = self._font_medium.render(self._input_text + cursor, True, WHITE)
        surface.blit(input_surf, input_surf.get_rect(center=box_rect.center))

        if self._error_msg:
            err_surf = self._font_small.render(self._error_msg, True, RED)
            surface.blit(err_surf, err_surf.get_rect(
                center=(SCREEN_WIDTH // 2, box_y + BUTTON_HEIGHT + MARGIN // 2)
            ))

        hint = self._font_small.render("Press Enter to confirm", True, GREY)
        surface.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - MARGIN)))

    def _draw_category_stage(self, surface) -> None:
        buttons = self._get_category_buttons()
        mouse_pos = pygame.mouse.get_pos()

        title = self._font_large.render("Select Category", True, WHITE)
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)))

        for name, rect in buttons.items():
            color = BUTTON_HOVER if rect.collidepoint(mouse_pos) else ACCENT
            pygame.draw.rect(surface, color, rect, border_radius=8)
            label = self._font_medium.render(name, True, WHITE)
            surface.blit(label, label.get_rect(center=rect.center))
