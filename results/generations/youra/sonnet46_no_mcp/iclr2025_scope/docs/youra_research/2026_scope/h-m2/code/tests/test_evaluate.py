import os
import sys
import csv
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from evaluate import RunResult, save_run_results
from config import LONGBENCH_TASKS, LONGBENCH_CATEGORIES


def make_run_result(model_name="gpt2", adapter_type="sequential", budget_ratio=0.5):
    categories = list(LONGBENCH_CATEGORIES.keys())
    per_task = {t: 0.42 for t in LONGBENCH_TASKS}
    cat_scores = {c: 0.42 for c in categories}
    return RunResult(
        model_name=model_name,
        adapter_type=adapter_type,
        budget_ratio=budget_ratio,
        per_task_scores=per_task,
        category_scores=cat_scores,
    )


def test_run_result_construction():
    r = make_run_result()
    assert r.model_name == "gpt2"
    assert r.adapter_type == "sequential"
    assert r.budget_ratio == 0.5
    assert len(r.per_task_scores) == 21
    assert len(r.category_scores) == 6


def test_run_result_to_dict():
    r = make_run_result()
    d = r.to_dict()
    assert "model_name" in d
    assert "adapter_type" in d
    assert "budget_ratio" in d
    assert any(k.startswith("task_") for k in d)
    assert any(k.startswith("cat_") for k in d)


def test_save_run_results_csv_format(tmp_path):
    results = [
        make_run_result("gpt2", "sequential", 0.25),
        make_run_result("gpt2", "eviction-aware", 0.25),
        make_run_result("gpt2", "sequential", 0.50),
        make_run_result("gpt2", "eviction-aware", 0.50),
        make_run_result("gpt2", "sequential", 0.75),
        make_run_result("gpt2", "eviction-aware", 0.75),
    ]
    output_dir = str(tmp_path)
    csv_path = save_run_results(results, output_dir)

    assert os.path.exists(csv_path)
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 6
    assert "model_name" in rows[0]
    assert "adapter_type" in rows[0]
    assert "budget_ratio" in rows[0]


def test_save_run_results_empty(tmp_path):
    csv_path = save_run_results([], str(tmp_path))
    assert isinstance(csv_path, str)


def test_run_result_category_scores_count():
    r = make_run_result()
    assert len(r.category_scores) == 6
    for cat in ["single-doc-qa", "multi-doc-qa", "summarization", "few-shot", "synthetic", "code"]:
        assert cat in r.category_scores
