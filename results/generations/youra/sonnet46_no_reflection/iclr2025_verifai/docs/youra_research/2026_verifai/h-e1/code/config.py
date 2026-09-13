from dataclasses import dataclass, field
from typing import List, Dict, Tuple


@dataclass
class ExperimentConfig:
    # Model
    model_id: str = "ByteDance-Seed/BFS-Prover-V2-7B"
    dtype: str = "bfloat16"

    # DPO Training Hyperparameters
    # beta=10.0: high for conservative SFT deviation in theorem proving (BFS-Prover arXiv:2502.03438)
    beta: float = 10.0
    lr_start: float = 5e-6
    lr_end: float = 5e-7
    batch_size: int = 16
    grad_accum_steps: int = 1
    num_epochs: int = 1
    seed: int = 1
    weight_decay: float = 0.01
    adam_betas: Tuple[float, float] = (0.9, 0.999)

    # Hard subset
    pass_at_1_threshold: float = 0.20
    cold_start_rollouts: int = 16

    # DPO conditions
    conditions: List[str] = field(default_factory=lambda: ["A", "B", "P"])

    # Tactic Taxonomy — IMMUTABLE, pre-specified before any training (NFR-4)
    taxonomy: Dict[str, List[str]] = field(default_factory=lambda: {
        "type_error":     ["type mismatch", "application type mismatch"],
        "undefined_name": ["unknown identifier", "unknown tactic"],
        "tactic_failure": ["tactic failed", "simp made no progress"],
    })

    # Gate
    gate_alpha: float = 0.05
    gate_direction: str = "greater"

    # BFS parameters (reference only)
    bfs_alpha_levels: List[float] = field(default_factory=lambda: [0.0, 0.5, 1.0])
    tactic_budget: str = "2048x2x600"

    # Paths
    output_dir: str = "h-e1/results"
    figures_dir: str = "h-e1/figures"
    checkpoint_dir: str = "h-e1/checkpoints"
    minif2f_dataset_id: str = "Tonic/MiniF2F"
    vericoding_data_path: str = "data/vericoding"

    # GPU / Compute
    cuda_visible_devices: str = ""
    mixed_precision: str = "bf16"
    max_seq_len: int = 2048


def validate_config(cfg: ExperimentConfig) -> None:
    assert cfg.beta > 0.0, "DPO beta must be positive"
    assert cfg.lr_start > cfg.lr_end > 0.0, "lr_start must be > lr_end > 0"
    assert 0.0 < cfg.pass_at_1_threshold < 1.0, "pass_at_1_threshold must be in (0, 1)"
    assert cfg.cold_start_rollouts >= 1, "cold_start_rollouts must be >= 1"
    assert cfg.num_epochs >= 1, "num_epochs must be >= 1"
    assert set(cfg.conditions) <= {"A", "B", "P"}, "conditions must be subset of {A, B, P}"
    assert set(cfg.taxonomy.keys()) == {"type_error", "undefined_name", "tactic_failure"}, \
        "taxonomy keys must not change (NFR-4 immutability)"
    assert cfg.gate_direction == "greater", "gate_direction must be 'greater'"


import yaml
from dataclasses import fields, asdict


def config_from_yaml(path: str) -> ExperimentConfig:
    with open(path) as f:
        d = yaml.safe_load(f)
    if "adam_betas" in d:
        d["adam_betas"] = tuple(d["adam_betas"])
    if "conditions" in d:
        d["conditions"] = list(d["conditions"])
    if "bfs_alpha_levels" in d:
        d["bfs_alpha_levels"] = list(d["bfs_alpha_levels"])
    valid_keys = {f.name for f in fields(ExperimentConfig)}
    filtered = {k: v for k, v in d.items() if k in valid_keys}
    cfg = ExperimentConfig(**filtered)
    validate_config(cfg)
    return cfg


def _tuples_to_lists(obj):
    if isinstance(obj, dict):
        return {k: _tuples_to_lists(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_tuples_to_lists(i) for i in obj]
    return obj


def config_to_yaml(cfg: ExperimentConfig, path: str) -> None:
    d = _tuples_to_lists(asdict(cfg))
    with open(path, "w") as f:
        yaml.dump(d, f, default_flow_style=False)
