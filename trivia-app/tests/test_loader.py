import json
import logging
import os
import tempfile

import pytest

from questions.loader import load_questions


VALID_Q = {
    "question_text": "Who was first?",
    "options": ["A", "B", "C", "D"],
    "correct_index": 0,
    "category": "Politics",
}


def _write_json(data):
    f = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    )
    json.dump(data, f)
    f.close()
    return f.name


def test_valid_file_loads_successfully():
    path = _write_json([VALID_Q])
    try:
        result = load_questions(path)
        assert len(result) == 1
        assert result[0]["question_text"] == "Who was first?"
    finally:
        os.unlink(path)


def test_all_required_fields_preserved():
    path = _write_json([VALID_Q])
    try:
        result = load_questions(path)
        q = result[0]
        assert q["question_text"] == VALID_Q["question_text"]
        assert q["options"] == VALID_Q["options"]
        assert q["correct_index"] == VALID_Q["correct_index"]
        assert q["category"] == VALID_Q["category"]
    finally:
        os.unlink(path)


def test_missing_correct_index_skipped_with_warning(caplog):
    bad = {"question_text": "Q?", "options": ["A", "B", "C", "D"], "category": "History"}
    path = _write_json([VALID_Q, bad])
    try:
        with caplog.at_level(logging.WARNING):
            result = load_questions(path)
        assert len(result) == 1
        assert any("correct_index" in msg for msg in caplog.messages)
    finally:
        os.unlink(path)


def test_missing_question_text_skipped(caplog):
    bad = {"options": ["A", "B", "C", "D"], "correct_index": 1, "category": "Politics"}
    path = _write_json([bad])
    try:
        with caplog.at_level(logging.WARNING):
            result = load_questions(path)
        assert result == []
    finally:
        os.unlink(path)


def test_options_wrong_length_skipped(caplog):
    bad = {
        "question_text": "Q?",
        "options": ["A", "B", "C"],
        "correct_index": 0,
        "category": "Politics",
    }
    path = _write_json([bad])
    try:
        with caplog.at_level(logging.WARNING):
            result = load_questions(path)
        assert result == []
    finally:
        os.unlink(path)


def test_correct_index_out_of_range_skipped(caplog):
    bad = {
        "question_text": "Q?",
        "options": ["A", "B", "C", "D"],
        "correct_index": 4,
        "category": "Politics",
    }
    path = _write_json([bad])
    try:
        with caplog.at_level(logging.WARNING):
            result = load_questions(path)
        assert result == []
    finally:
        os.unlink(path)


def test_invalid_category_skipped(caplog):
    bad = {
        "question_text": "Q?",
        "options": ["A", "B", "C", "D"],
        "correct_index": 0,
        "category": "Science",
    }
    path = _write_json([bad])
    try:
        with caplog.at_level(logging.WARNING):
            result = load_questions(path)
        assert result == []
    finally:
        os.unlink(path)


def test_missing_file_triggers_sys_exit():
    with pytest.raises(SystemExit):
        load_questions("data/this_file_does_not_exist_xyz123.json")


def test_no_exception_raised_on_invalid_records():
    bad = {"question_text": "Q?"}
    path = _write_json([bad])
    try:
        result = load_questions(path)  # must not raise any exception
        assert result == []
    finally:
        os.unlink(path)
