import pytest

from questions.bank import draw_questions


POLITICS_QS = [
    {
        "question_text": f"Politics Q{i}",
        "options": ["A", "B", "C", "D"],
        "correct_index": 0,
        "category": "Politics",
    }
    for i in range(12)
]
HISTORY_QS = [
    {
        "question_text": f"History Q{i}",
        "options": ["A", "B", "C", "D"],
        "correct_index": 0,
        "category": "History",
    }
    for i in range(12)
]
ALL_QS = POLITICS_QS + HISTORY_QS


def test_politics_filter_excludes_history():
    result = draw_questions(ALL_QS, "Politics", n=5)
    assert all(q["category"] == "Politics" for q in result)


def test_history_filter_excludes_politics():
    result = draw_questions(ALL_QS, "History", n=5)
    assert all(q["category"] == "History" for q in result)


def test_returns_exactly_n_questions():
    result = draw_questions(ALL_QS, "Politics", n=10)
    assert len(result) == 10


def test_no_duplicate_questions():
    result = draw_questions(ALL_QS, "Politics", n=10)
    texts = [q["question_text"] for q in result]
    assert len(texts) == len(set(texts))


def test_randomness_varies_across_draws():
    draws = set()
    for _ in range(10):
        result = draw_questions(ALL_QS, "Politics", n=10)
        draws.add(tuple(q["question_text"] for q in result))
    assert len(draws) > 1


def test_insufficient_questions_triggers_sys_exit():
    short = POLITICS_QS[:3]
    with pytest.raises(SystemExit):
        draw_questions(short, "Politics", n=10)


def test_empty_list_triggers_sys_exit():
    with pytest.raises(SystemExit):
        draw_questions([], "Politics", n=10)
