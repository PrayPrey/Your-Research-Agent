"""Tests for config_v2.py — spec compliance."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config_v2 import CONFIG_V2, CURATION_CONDITIONS, CURATION_CONDITIONS_BY_ID, SCALE_OVERRIDES


def test_config_scales():
    assert CONFIG_V2.scales == [14, 31]


def test_config_total_tokens():
    assert CONFIG_V2.total_tokens == 1_000_000_000


def test_config_train_steps():
    assert CONFIG_V2.train_steps == 500


def test_config_checkpoint_interval():
    assert CONFIG_V2.checkpoint_interval_tokens == 100_000_000


def test_config_seeds():
    assert CONFIG_V2.seeds == [1, 2]


def test_config_corpora():
    assert CONFIG_V2.corpora == ["fineweb"]


def test_config_eval_tasks():
    assert CONFIG_V2.eval_tasks == ["hellaswag"]


def test_config_eval_fewshot():
    assert CONFIG_V2.eval_num_fewshot == 0


def test_pythia_configs_keys():
    assert 14 in CONFIG_V2.pythia_configs
    assert 31 in CONFIG_V2.pythia_configs


def test_pythia_14m_hidden_size():
    assert CONFIG_V2.pythia_configs[14]["hidden_size"] == 128


def test_pythia_31m_hidden_size():
    assert CONFIG_V2.pythia_configs[31]["hidden_size"] == 256


def test_curation_conditions_count():
    assert len(CURATION_CONDITIONS) == 6


def test_curation_conditions_ids():
    ids = {c["condition_id"] for c in CURATION_CONDITIONS}
    expected = {"ppl20_j07", "ppl20_j09", "ppl35_j07", "ppl35_j09", "ppl50_j07", "ppl50_j09"}
    assert ids == expected


def test_curation_conditions_by_id():
    assert "ppl35_j07" in CURATION_CONDITIONS_BY_ID
    assert CURATION_CONDITIONS_BY_ID["ppl35_j07"]["ppl_threshold"] == 35
    assert CURATION_CONDITIONS_BY_ID["ppl35_j07"]["jaccard_threshold"] == 0.7


def test_scale_overrides_keys():
    assert 14 in SCALE_OVERRIDES
    assert 31 in SCALE_OVERRIDES


def test_scale_overrides_train_iters():
    assert SCALE_OVERRIDES[14]["train_iters"] == 500
    assert SCALE_OVERRIDES[31]["train_iters"] == 500
