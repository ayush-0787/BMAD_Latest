import logging

import pygame

from scoring.engine import calculate_speed_bonus
from scoring.multiplier import apply_streak_multiplier, get_multiplier
from ui.constants import (
    ACCENT, BASE_SCORE, BLACK, BUTTON_HEIGHT, BUTTON_HOVER, BUTTON_PADDING, BUTTON_WIDTH,
    FONT_LARGE, FONT_MEDIUM, FONT_SMALL, GREEN, GREY, MARGIN, QUESTION_TIMER,
    RED, SCREEN_HEIGHT, SCREEN_WIDTH, TIMER_BAR_H, WHITE,
)
from ui.screen_manager import Screen


class GameScreen(Screen):
    def __init__(self):
        self._question_timer = 0.0   # seconds elapsed on current question
        self._pause_timer = 0.0      # seconds remaining in 1s feedback pause
        self._in_pause = False       # True during post-answer/expiry feedback pause
        self._correct_index = -1     # correct answer index stored on pause entry
        self._last_multiplier = 1.0  # streak multiplier applied on last correct answer
        self._font_large = None
        self._font_medium = None
        self._font_small = None

    def _ensure_fonts(self) -> None:
        if self._font_large is None:
            self._font_large = pygame.font.SysFont(None, FONT_LARGE)
            self._font_medium = pygame.font.SysFont(None, FONT_MEDIUM)
            self._font_small = pygame.font.SysFont(None, FONT_SMALL)

    def _get_answer_rects(self) -> list:
        col0_x = SCREEN_WIDTH // 2 - BUTTON_WIDTH - BUTTON_PADDING // 2
        col1_x = SCREEN_WIDTH // 2 + BUTTON_PADDING // 2
        row0_y = SCREEN_HEIGHT - 2 * BUTTON_HEIGHT - BUTTON_PADDING - MARGIN
        row1_y = row0_y + BUTTON_HEIGHT + BUTTON_PADDING
        return [
            pygame.Rect(col0_x, row0_y, BUTTON_WIDTH, BUTTON_HEIGHT),
            pygame.Rect(col1_x, row0_y, BUTTON_WIDTH, BUTTON_HEIGHT),
            pygame.Rect(col0_x, row1_y, BUTTON_WIDTH, BUTTON_HEIGHT),
            pygame.Rect(col1_x, row1_y, BUTTON_WIDTH, BUTTON_HEIGHT),
        ]

    def _wrap_text(self, text: str, font, max_width: int) -> list:
        words = text.split()
        lines, current = [], ""
        for word in words:
            test = f"{current} {word}".strip()
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def reset(self) -> None:
        self._question_timer = 0.0
        self._pause_timer = 0.0
        self._in_pause = False
        self._correct_index = -1
        self._last_multiplier = 1.0

    def handle_events(self, events, game_state) -> str | None:
        if game_state.current_question_index >= len(game_state.questions):
            if (game_state.selected_mode == "multiplayer"
                    and game_state.active_player_index + 1 < len(game_state.players)):
                return "handoff"
            return "results"
        if not self._in_pause:
            question = game_state.questions[game_state.current_question_index]
            player = game_state.players[game_state.active_player_index]
            answer_rects = self._get_answer_rects()
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for i, rect in enumerate(answer_rects):
                        if rect.collidepoint(event.pos):
                            self._correct_index = question["correct_index"]
                            if i == self._correct_index:
                                player.streak += 1
                                speed_bonus = calculate_speed_bonus(
                                    BASE_SCORE, self._question_timer, QUESTION_TIMER
                                )
                                points = apply_streak_multiplier(
                                    BASE_SCORE + speed_bonus, player.streak
                                )
                                player.score += points
                                player.correct += 1
                                self._last_multiplier = get_multiplier(player.streak)
                                logging.info(
                                    "Correct: Q%d player=%s points=%d streak=%d mult=%.1f",
                                    game_state.current_question_index,
                                    player.name,
                                    points,
                                    player.streak,
                                    self._last_multiplier,
                                )
                            else:
                                player.streak = 0
                                logging.info(
                                    "Wrong: Q%d player=%s streak reset",
                                    game_state.current_question_index,
                                    player.name,
                                )
                            player.total += 1
                            self._question_timer = 0.0
                            self._in_pause = True
                            self._pause_timer = 1.0
                            return None
        return None

    def update(self, game_state, dt: float) -> None:
        if game_state.current_question_index >= len(game_state.questions):
            return
        if self._in_pause:
            self._pause_timer -= dt
            if self._pause_timer <= 0.0:
                self._in_pause = False
                self._pause_timer = 0.0
                game_state.current_question_index += 1
                self._question_timer = 0.0
                self._correct_index = -1
        else:
            self._question_timer += dt
            if self._question_timer >= QUESTION_TIMER:
                player = game_state.players[game_state.active_player_index]
                question = game_state.questions[game_state.current_question_index]
                player.streak = 0
                player.total += 1
                self._correct_index = question["correct_index"]
                self._question_timer = 0.0
                self._in_pause = True
                self._pause_timer = 1.0
                logging.info(
                    "Timer expired: Q%d player=%s streak reset",
                    game_state.current_question_index,
                    player.name,
                )

    def draw(self, surface, game_state) -> None:
        self._ensure_fonts()
        if game_state.current_question_index >= len(game_state.questions):
            return

        question = game_state.questions[game_state.current_question_index]
        player = game_state.players[game_state.active_player_index]
        time_remaining = max(0.0, QUESTION_TIMER - self._question_timer)

        surface.fill(BLACK)

        # HUD: question counter top-left, streak+multiplier centre, score top-right
        bar_y = MARGIN // 2
        q_label = self._font_small.render(
            f"Q {game_state.current_question_index + 1}/{len(game_state.questions)}",
            True, WHITE,
        )
        surface.blit(q_label, (MARGIN, bar_y - FONT_SMALL // 2))

        streak_label = self._font_small.render(
            f"Streak: {player.streak} | x{self._last_multiplier:.1f}",
            True, WHITE,
        )
        surface.blit(streak_label, streak_label.get_rect(
            midtop=(SCREEN_WIDTH // 2, bar_y - FONT_SMALL // 2)
        ))

        score_label = self._font_small.render(f"Score: {player.score}", True, WHITE)
        surface.blit(score_label, score_label.get_rect(
            topright=(SCREEN_WIDTH - MARGIN, bar_y - FONT_SMALL // 2)
        ))

        # Timer progress bar (full-width background, coloured fill)
        bar_full_w = SCREEN_WIDTH - 2 * MARGIN
        ratio = max(0.0, 1.0 - (self._question_timer / QUESTION_TIMER))
        bar_fill_w = int(bar_full_w * ratio)
        bar_color = GREEN if time_remaining > 10 else RED
        pygame.draw.rect(surface, GREY, pygame.Rect(MARGIN, bar_y, bar_full_w, TIMER_BAR_H))
        if bar_fill_w > 0:
            pygame.draw.rect(surface, bar_color, pygame.Rect(MARGIN, bar_y, bar_fill_w, TIMER_BAR_H))

        # Timer countdown digit (centred below bar)
        timer_center_y = bar_y + TIMER_BAR_H + MARGIN // 2
        timer_surf = self._font_large.render(str(int(time_remaining)), True, WHITE)
        surface.blit(timer_surf, timer_surf.get_rect(center=(SCREEN_WIDTH // 2, timer_center_y)))

        # Player name label (multiplayer only — single-player layout unchanged)
        text_y = timer_center_y + FONT_LARGE // 2 + MARGIN // 2
        if len(game_state.players) > 1:
            name_surf = self._font_medium.render(player.name, True, ACCENT)
            surface.blit(name_surf, name_surf.get_rect(center=(SCREEN_WIDTH // 2, text_y)))
            text_y += FONT_MEDIUM + MARGIN // 4

        # Question text (word-wrapped, centred)
        max_text_w = SCREEN_WIDTH - 2 * MARGIN
        for line in self._wrap_text(question["question_text"], self._font_medium, max_text_w):
            surf = self._font_medium.render(line, True, WHITE)
            surface.blit(surf, surf.get_rect(center=(SCREEN_WIDTH // 2, text_y)))
            text_y += FONT_MEDIUM + MARGIN // 6

        # Answer buttons (2×2 grid)
        answer_rects = self._get_answer_rects()
        mouse_pos = pygame.mouse.get_pos()
        labels = ["A", "B", "C", "D"]
        for i, rect in enumerate(answer_rects):
            if self._in_pause:
                color = GREEN if i == self._correct_index else ACCENT
            else:
                color = BUTTON_HOVER if rect.collidepoint(mouse_pos) else ACCENT
            pygame.draw.rect(surface, color, rect, border_radius=8)
            opt_text = f"{labels[i]}: {question['options'][i]}"
            label_surf = self._font_small.render(opt_text, True, WHITE)
            surface.blit(label_surf, label_surf.get_rect(center=rect.center))
