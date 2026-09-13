"""Configuration dataclass for h-e1 prescreening inference pipeline."""
from dataclasses import dataclass, field
import os


@dataclass
class PrescreeningConfig:
    """Full experiment configuration for h-e1 prescreening inference.

    All controlled variables from Phase 2A are fixed here.
    Do NOT modify inference settings without Phase 2A re-approval.
    """

    # --- Model ---
    sft_checkpoint_path: str = "h-e1/code/sft_checkpoint/"
    base_model_id: str = "Qwen/Qwen2.5-Coder-7B-Instruct"
    dtype: str = "bfloat16"  # Phase 2A controlled variable

    # --- Inference (ALL Phase 2A controlled variables — do not tune) ---
    temperature: float = 0.8
    max_new_tokens: int = 1024
    k_rollouts: int = 8        # group size G=8 from Phase 2A
    batch_size: int = 4        # GPU-memory dependent; 4-8 on H100 NVL
    seed: int = 42
    do_sample: bool = True

    # --- Dataset ---
    dataset_id: str = "codeparrot/apps"
    dataset_split: str = "train"
    difficulty: str = "introductory"
    min_test_cases: int = 3    # T>=3 filter (Risk R1 mitigation)

    # --- Prescreening filter ---
    s_term_min: float = 0.3
    s_term_max: float = 0.55

    # --- Gate thresholds (Phase 2B success criteria) ---
    gate_fraction_k_pass_threshold: float = 0.10
    gate_pct_groups_threshold: float = 0.80
    variance_ratio_threshold: float = 1.5
    var_binary_eps: float = 1e-8   # denominator guard for variance ratio

    # --- Execution sandbox ---
    execution_timeout: float = 5.0    # seconds per test case
    min_prescreened_problems: int = 50  # fail-early if fewer survive T>=3 filter

    # --- Diagnostics ---
    log_every_n_problems: int = 100
    print_gate_estimates_every_n: int = 500
    log_level: str = "INFO"

    # --- Paths ---
    output_dir: str = "h-e1/results/"
    figures_dir: str = "h-e1/figures/"
    resume_file: str = "h-e1/results/processed_problem_ids.json"
    log_file: str = "h-e1/results/prescreening.log"
    config_dump_path: str = "h-e1/results/config_used.yaml"

    # --- Optional rollout persistence ---
    save_rollouts: bool = False   # rollouts.json can be large (~GB); off by default


def validate_config(cfg: PrescreeningConfig) -> None:
    """Raise ValueError on invalid combinations."""
    if not (0.0 < cfg.s_term_min < cfg.s_term_max < 1.0):
        raise ValueError(
            f"s_term range invalid: [{cfg.s_term_min}, {cfg.s_term_max}]"
        )
    if cfg.k_rollouts < 1:
        raise ValueError("k_rollouts must be >= 1")
    if cfg.batch_size < 1:
        raise ValueError("batch_size must be >= 1")
    if cfg.min_test_cases < 1:
        raise ValueError("min_test_cases must be >= 1")
    if not (0.0 < cfg.gate_fraction_k_pass_threshold <= 1.0):
        raise ValueError("gate_fraction_k_pass_threshold must be in (0, 1]")
    if not (0.0 < cfg.gate_pct_groups_threshold <= 1.0):
        raise ValueError("gate_pct_groups_threshold must be in (0, 1]")


def load_config_from_yaml(yaml_path: str, cfg: PrescreeningConfig) -> PrescreeningConfig:
    """Override dataclass fields from a YAML file. Returns updated config."""
    import yaml
    from dataclasses import fields

    with open(yaml_path) as f:
        raw = yaml.safe_load(f)

    flat: dict = {}
    for section in raw.values():
        if isinstance(section, dict):
            flat.update(section)

    field_names = {f.name for f in fields(cfg)}
    for k, v in flat.items():
        if k in field_names:
            object.__setattr__(cfg, k, v)
    return cfg
