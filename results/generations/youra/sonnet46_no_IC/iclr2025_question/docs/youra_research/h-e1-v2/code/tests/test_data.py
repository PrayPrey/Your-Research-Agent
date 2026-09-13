"""Smoke checks for data.py (task-002, LIGHT tier)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from data import label_response, stratified_split, format_prompt


def test_stratified_split_sizes_1000():
    labels = [0] * 400 + [1] * 600
    sel, test = stratified_split(labels)
    assert len(sel) == 500 and len(test) == 500
    assert {labels[i] for i in sel} == {0, 1}


def test_stratified_split_sizes_817():
    labels = [0] * 300 + [1] * 517
    sel, test = stratified_split(labels)
    assert len(sel) == 408 and len(test) == 409
    assert {labels[i] for i in sel} == {0, 1}
    assert set(sel) | set(test) == set(range(817))
    assert not set(sel) & set(test)


def test_stratified_split_deterministic():
    labels = [0, 1] * 100
    assert stratified_split(labels) == stratified_split(labels)


def test_label_triviaqa():
    ex = {"answer": {"aliases": ["Paris"], "normalized_aliases": ["paris"]}}
    assert label_response(ex, " Paris\nQ: next", "triviaqa") == 0
    assert label_response(ex, " London", "triviaqa") == 1


def test_label_truthfulqa_substring():
    ex = {"best_answer": "Nothing happens",
          "correct_answers": ["Nothing happens", "You digest it"]}
    assert label_response(ex, " nothing happens if you eat it", "truthfulqa") == 0
    assert label_response(ex, " you will die", "truthfulqa") == 1


def test_format_prompt():
    assert format_prompt({"question": "Who?"}, "triviaqa") == "Q: Who?\nA:"
