import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import (
    BudgetSweepConfig, AdapterSpec, get_default_config, validate_config,
    LONGBENCH_TASKS, LONGBENCH_CATEGORIES, TASK_SCORER_MAP, BUDGET_RATIOS,
)


def test_budget_sweep_config_defaults():
    cfg = BudgetSweepConfig()
    assert cfg.experiment_id == "h-m2"
    assert cfg.budget_ratios == [0.25, 0.50, 0.75]
    assert cfg.max_seq_length == 4096
    assert cfg.batch_size == 1
    assert cfg.seed == 1
    assert cfg.attn_implementation == "eager"
    assert cfg.spearman_gate_threshold == -0.8


def test_get_default_config_returns_adapters():
    cfg = get_default_config()
    assert len(cfg.adapters) >= 2
    adapter_types = {a.adapter_type for a in cfg.adapters}
    assert "sequential" in adapter_types
    assert "eviction-aware" in adapter_types


def test_get_default_config_adapter_types():
    cfg = get_default_config()
    for a in cfg.adapters:
        assert a.adapter_type in ("sequential", "eviction-aware")
        assert a.model_name != ""


def test_adapter_spec_fields():
    spec = AdapterSpec(model_name="gpt2", adapter_path="/tmp", adapter_type="sequential")
    assert spec.model_name == "gpt2"
    assert spec.adapter_path == "/tmp"
    assert spec.adapter_type == "sequential"


def test_validate_config_raises_for_missing_path(tmp_path):
    cfg = BudgetSweepConfig(
        adapters=[AdapterSpec(model_name="gpt2", adapter_path="/nonexistent/path", adapter_type="sequential")],
        figures_dir=str(tmp_path / "figs"),
        results_dir=str(tmp_path / "results"),
    )
    with pytest.raises((ValueError, AssertionError)):
        validate_config(cfg)


def test_longbench_tasks_count():
    assert len(LONGBENCH_TASKS) == 21


def test_longbench_categories_count():
    assert len(LONGBENCH_CATEGORIES) == 6


def test_longbench_categories_hyphenated_keys():
    expected_keys = {"single-doc-qa", "multi-doc-qa", "summarization", "few-shot", "synthetic", "code"}
    assert set(LONGBENCH_CATEGORIES.keys()) == expected_keys


def test_all_tasks_in_categories():
    all_cat_tasks = set()
    for tasks in LONGBENCH_CATEGORIES.values():
        all_cat_tasks.update(tasks)
    for task in LONGBENCH_TASKS:
        assert task in all_cat_tasks, f"Task {task} not in any category"


def test_task_scorer_map_completeness():
    for task in LONGBENCH_TASKS:
        assert task in TASK_SCORER_MAP, f"Task {task} missing from TASK_SCORER_MAP"
        assert TASK_SCORER_MAP[task] in ("f1", "rouge-l", "accuracy", "edit-distance")


def test_budget_ratios_valid():
    for r in BUDGET_RATIOS:
        assert 0.0 < r < 1.0
