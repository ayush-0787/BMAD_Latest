import logging
import sys
import pygame
from questions.loader import load_questions
from ui.screen_manager import ScreenManager
from ui.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

logging.basicConfig(level=logging.DEBUG)


def main():
    all_questions = (
        load_questions("data/questions_politics.json")
        + load_questions("data/questions_history.json")
    )

    pygame.init()
    surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Python Trivia App")
    clock = pygame.time.Clock()
    manager = ScreenManager(all_questions)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        manager.run_frame(events, surface, dt)
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
