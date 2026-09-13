import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch, MagicMock
from config import Config, load_config
from data_loader import DataLoader


def _make_mmlu_item(question="What is 2+2?", choices=["1", "2", "3", "4"]):
    return {"question": question, "choices": choices}


def _make_hellaswag_item(ctx="A man walks", endings=["fast", "slow", "run", "jump"]):
    return {"ctx": ctx, "endings": endings}


def _make_bbh_item(inp="Is it true?"):
    return {"input": inp}


def test_format_text_mmlu_question_choices():
    cfg = load_config()
    dl = DataLoader(cfg)
    item = _make_mmlu_item("What is 2+2?", ["1", "2", "3", "4"])
    result = dl.format_text(item, "mmlu")
    assert result == "What is 2+2? 1 2 3 4"


def test_format_text_mmlu_question_only():
    cfg = Config(text_format="question_only")
    dl = DataLoader(cfg)
    item = _make_mmlu_item("What is 2+2?", ["1", "2", "3", "4"])
    result = dl.format_text(item, "mmlu")
    assert result == "What is 2+2?"


def test_format_text_hellaswag_question_choices():
    cfg = load_config()
    dl = DataLoader(cfg)
    item = _make_hellaswag_item("A man walks", ["fast", "slow", "run", "jump"])
    result = dl.format_text(item, "hellaswag")
    assert result == "A man walks fast slow run jump"


def test_format_text_hellaswag_question_only():
    cfg = Config(text_format="question_only")
    dl = DataLoader(cfg)
    item = _make_hellaswag_item("A man walks", ["fast", "slow"])
    result = dl.format_text(item, "hellaswag")
    assert result == "A man walks"


def test_format_text_bbh_both_formats():
    for fmt in ["question_choices", "question_only"]:
        cfg = Config(text_format=fmt)
        dl = DataLoader(cfg)
        item = _make_bbh_item("Is it true?")
        result = dl.format_text(item, "bbh")
        assert result == "Is it true?"


def _mock_dataset(items):
    return items


def test_load_all_returns_59_keys():
    cfg = load_config()
    dl = DataLoader(cfg)

    mmlu_mock = {task: [f"q {task}"] for task in cfg.mmlu_tasks}
    hellaswag_mock = {"hellaswag": ["hs text"]}
    bbh_mock = {"bbh": ["bbh text"]}

    with patch.object(dl, "load_mmlu", return_value=mmlu_mock), \
         patch.object(dl, "load_hellaswag", return_value=hellaswag_mock), \
         patch.object(dl, "load_bbh", return_value=bbh_mock):
        result = dl.load_all()

    assert len(result) == 59
    assert "hellaswag" in result
    assert "bbh" in result
    assert len([k for k in result if k not in ("hellaswag", "bbh")]) == 57


def test_bbh_merge_produces_single_key():
    cfg = load_config()
    dl = DataLoader(cfg)

    fake_ds = [{"input": f"item {i}"} for i in range(5)]

    with patch("data_loader.load_dataset", return_value=fake_ds):
        result = dl.load_bbh()

    assert list(result.keys()) == ["bbh"]
    assert isinstance(result["bbh"], list)
