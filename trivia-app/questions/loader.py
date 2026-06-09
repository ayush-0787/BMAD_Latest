import json
import logging
import os
import sys


def load_questions(path: str) -> list:
    if not os.path.exists(path):
        sys.exit(f"ERROR: Question bank not found at '{path}'. Cannot start game.")

    try:
        with open(path, encoding="utf-8") as f:
            raw_records = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        sys.exit(f"ERROR: Failed to load question bank from '{path}': {e}")

    if not isinstance(raw_records, list):
        sys.exit(f"ERROR: Question bank at '{path}' must be a JSON array.")

    valid_questions = []
    for i, record in enumerate(raw_records):
        if _is_valid(record, i):
            valid_questions.append(record)

    logging.info(f"Loaded {len(valid_questions)} valid questions from '{path}'")
    return valid_questions


def _is_valid(record: dict, index: int) -> bool:
    for field in ("question_text", "options", "correct_index", "category"):
        if field not in record:
            logging.warning(f"Skipping question {index}: missing field '{field}'")
            return False

    if not isinstance(record["options"], list) or len(record["options"]) != 4:
        logging.warning(
            f"Skipping question {index}: 'options' must be a list of exactly 4 elements"
        )
        return False

    if not isinstance(record["correct_index"], int) or not (0 <= record["correct_index"] <= 3):
        logging.warning(
            f"Skipping question {index}: 'correct_index' must be an integer 0-3"
        )
        return False

    if record["category"] not in ("Politics", "History"):
        logging.warning(
            f"Skipping question {index}: 'category' must be 'Politics' or 'History',"
            f" got '{record['category']}'"
        )
        return False

    return True
