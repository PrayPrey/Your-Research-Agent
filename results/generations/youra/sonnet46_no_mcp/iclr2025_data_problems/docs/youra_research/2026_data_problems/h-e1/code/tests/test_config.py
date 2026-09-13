import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import Config, load_config


def test_load_config_returns_config_instance():
    cfg = load_config()
    assert isinstance(cfg, Config)


def test_mmlu_tasks_has_57_items():
    cfg = load_config()
    assert len(cfg.mmlu_tasks) == 57


def test_gate_p_threshold():
    cfg = load_config()
    assert cfg.gate_p_threshold == 0.05


def test_ngram_n():
    cfg = load_config()
    assert cfg.ngram_n == 13


def test_text_format_default():
    cfg = load_config()
    assert cfg.text_format == "question_choices"


def test_seed():
    cfg = load_config()
    assert cfg.seed == 1
