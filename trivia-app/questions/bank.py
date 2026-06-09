import logging
import random
import sys


def draw_questions(questions: list, category: str, n: int = 10) -> list:
    filtered = [q for q in questions if q.get("category") == category]

    if len(filtered) < n:
        sys.exit(
            f"ERROR: Not enough '{category}' questions — need {n}, found {len(filtered)}."
        )

    drawn = random.sample(filtered, n)
    logging.info(f"Drew {n} questions for category '{category}'")
    return drawn
