import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config


def test_models_count():
    assert len(config.MODELS) == 30


def test_models_schema():
    for m in config.MODELS:
        assert "id" in m
        assert "hf_id" in m
        assert "params" in m
        assert "family" in m
        assert isinstance(m["requires_4bit"], bool)


def test_70b_requires_4bit():
    for m in config.MODELS:
        if m["params"] == "70B":
            assert m["requires_4bit"] is True


def test_tasks():
    assert "mmlu" in config.TASKS
    assert "truthfulqa_mc1" in config.TASKS
    assert "adv_glue" in config.TASKS
    assert "anli_r3" in config.TASKS
    assert "humaneval" in config.TASKS


def test_gate_pairs():
    assert ("ECE", "TruthfulQA_pct") in config.GATE_PAIRS
    assert ("ECE", "AdvGLUE_drop") in config.GATE_PAIRS


def test_gate_threshold():
    assert config.GATE_THRESHOLD == 0.40


def test_min_models():
    assert config.MIN_MODELS == 25


def test_figure_names():
    assert len(config.FIGURE_NAMES) >= 6
    for k, v in config.FIGURE_NAMES.items():
        assert v.endswith(".png")


def test_batch_sizes():
    assert "7B" in config.BATCH_SIZE
    assert "70B" in config.BATCH_SIZE
    assert config.BATCH_SIZE["7B"] >= 1


def test_indicators():
    for ind in ["ECE", "Brier", "TruthfulQA_pct", "AdvGLUE_drop", "ANLI_drop"]:
        assert ind in config.INDICATORS
