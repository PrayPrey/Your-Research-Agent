import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import Config, load_config

def test_config_defaults():
    cfg = Config()
    assert cfg.ngram_n == 13
    assert cfg.num_perm == 128
    assert cfg.lsh_threshold == 0.5
    assert cfg.gate_p_threshold == 0.05
    assert len(cfg.mmlu_tasks) == 57
    assert "pile" in cfg.corpus_configs
    assert "c4" in cfg.corpus_configs
    assert "redpajama" in cfg.corpus_configs

def test_load_config_returns_config():
    cfg = load_config()
    assert isinstance(cfg, Config)

def test_env_var_override(monkeypatch):
    monkeypatch.setenv("H_M1_INDICES_DIR", "/tmp/test_indices")
    cfg = load_config()
    assert cfg.indices_dir == "/tmp/test_indices"
