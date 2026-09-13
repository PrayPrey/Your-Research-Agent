# Configuration: h-e1 Prescreening Validation

**Hypothesis:** h-e1 (EXISTENCE)
**Type:** Prescreening inference pipeline — NO training
**Generated:** 2026-03-15

Applied: flat-dataclass-with-defaults (pytorch inductor config pattern), YAML-nested-config

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - no existing code to analyze
**Config Files Found:** None - new config
**Pattern Used:** dataclass

---

## A-6: Main Orchestration [Complexity: 12, Budget: 2 subtasks]

**Applied**: flat-dataclass-with-defaults, argparse-flag-overrides

---

### C-6-1: Experiment Configuration Dataclass [Subtask 1/2]

```python
from dataclasses import dataclass, field
import os


@dataclass
class PrescrееningConfig:
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

    # --- Paths ---
    output_dir: str = "h-e1/results/"
    figures_dir: str = "h-e1/figures/"
    resume_file: str = "h-e1/results/processed_problem_ids.json"
    log_file: str = "h-e1/results/prescreening.log"
    config_dump_path: str = "h-e1/results/config_used.yaml"

    # --- Optional rollout persistence ---
    save_rollouts: bool = False   # rollouts.json can be large (~GB); off by default


def validate_config(cfg: PrescrееningConfig) -> None:
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
```

---

### C-6-2: Output Path Configuration and Results Formats [Subtask 2/2]

```python
# --- gate_metrics.json schema ---
GATE_METRICS_SCHEMA = {
    "fraction_k_pass_ge1": float,       # mean over groups: any(r_binary > 0)
    "mean_var_ratio": float,             # mean variance_ratio across eligible groups
    "pct_groups_above_1_5x": float,      # fraction of groups with variance_ratio >= 1.5
    "gate_pass": bool,                   # True if both gate thresholds met
    "gate_message": str,                 # human-readable pass/fail reason
    "n_problems_total": int,             # after difficulty=0 filter
    "n_problems_after_t_filter": int,    # after T>=3 filter
    "n_problems_prescreened": int,       # after S_term [0.3, 0.55] filter
    "n_groups_eligible_variance": int,   # groups where var_binary > eps
    "run_seed": int,
    "run_timestamp": str,                # ISO 8601
    "sft_checkpoint_used": bool,         # True if SFT checkpoint found; False if fallback
    "model_used": str,                   # actual model path/id used
}

# --- per_problem_results.csv column spec ---
PER_PROBLEM_CSV_COLUMNS = [
    "problem_id",       # int — APPS dataset index
    "s_term",           # float — fraction of rollouts with tests_passed >= 1
    "prescreened",      # bool — True if s_term in [s_term_min, s_term_max]
    "T",                # int — number of test cases for this problem
    "var_ratio",        # float — np.var(r_ratio_vec); -1.0 if not computed
    "var_binary",       # float — np.var(r_binary_vec); -1.0 if not computed
    "variance_ratio",   # float — var_ratio / var_binary; NaN if var_binary <= eps
    "k_pass_any",       # bool — any rollout had tests_passed >= 1
    "mean_r_ratio",     # float — mean of r_ratio_vec
    "mean_r_binary",    # float — mean of r_binary_vec
]

# --- Logging configuration ---
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    "datefmt": "%Y-%m-%d %H:%M:%S",
    "handlers": ["console", "file"],    # file handler writes to cfg.log_file
}

# --- Resume file format (processed_problem_ids.json) ---
# List of integer problem_ids already processed in a previous partial run.
# Example content: [0, 1, 2, ..., 499]
# Written atomically after each batch to allow safe interruption.
RESUME_FILE_SCHEMA = {
    "processed_ids": list,   # list[int]
    "last_saved": str,       # ISO 8601 timestamp
    "total_processed": int,
}
```

---

## YAML Configuration (`h-e1/config.yaml`)

```yaml
# h-e1/config.yaml
# Equivalent to PrescrееningConfig dataclass defaults.
# Override individual fields via --config flag in prescreening.py.

model:
  sft_checkpoint_path: "h-e1/code/sft_checkpoint/"
  base_model_id: "Qwen/Qwen2.5-Coder-7B-Instruct"
  dtype: "bfloat16"

inference:
  temperature: 0.8
  max_new_tokens: 1024
  k_rollouts: 8
  batch_size: 4
  seed: 42
  do_sample: true

dataset:
  dataset_id: "codeparrot/apps"
  dataset_split: "train"
  difficulty: "introductory"
  min_test_cases: 3

prescreening:
  s_term_min: 0.3
  s_term_max: 0.55

gate:
  gate_fraction_k_pass_threshold: 0.10
  gate_pct_groups_threshold: 0.80
  variance_ratio_threshold: 1.5
  var_binary_eps: 1.0e-8

execution:
  execution_timeout: 5.0
  min_prescreened_problems: 50

diagnostics:
  log_every_n_problems: 100
  print_gate_estimates_every_n: 500

paths:
  output_dir: "h-e1/results/"
  figures_dir: "h-e1/figures/"
  resume_file: "h-e1/results/processed_problem_ids.json"
  log_file: "h-e1/results/prescreening.log"
  config_dump_path: "h-e1/results/config_used.yaml"
  save_rollouts: false
```

---

## Argument Parser (`prescreening.py`)

```python
import argparse


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="h-e1 Prescreening Inference — EXISTENCE validation"
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed (default: 42; Phase 2A controlled variable)"
    )
    parser.add_argument(
        "--batch_size", type=int, default=4,
        help="Inference batch size (default: 4; adjust for GPU memory)"
    )
    parser.add_argument(
        "--config", type=str, default=None,
        help="Path to YAML config file to override dataclass defaults"
    )
    parser.add_argument(
        "--resume", action="store_true", default=False,
        help="Resume from processed_problem_ids.json if it exists"
    )
    parser.add_argument(
        "--save_rollouts", action="store_true", default=False,
        help="Save all rollouts to rollouts.json (large file, off by default)"
    )
    return parser


def load_config_from_yaml(yaml_path: str, cfg: PrescrееningConfig) -> PrescrееningConfig:
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
```

---

## Environment Variables

```bash
# Required before launching prescreening.py
export CUDA_VISIBLE_DEVICES=<gpu_id>   # single GPU with lowest memory usage
export HF_HOME=~/.cache/huggingface    # optional; default cache location
```

---

## Subtask Summary

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | PrescrееningConfig Dataclass | Full experiment config dataclass with all hyperparameters, gate thresholds, paths, and validate_config() |
| C-6-2 | Output Path Configuration | gate_metrics.json schema, per_problem_results.csv columns, logging config, resume file format |
