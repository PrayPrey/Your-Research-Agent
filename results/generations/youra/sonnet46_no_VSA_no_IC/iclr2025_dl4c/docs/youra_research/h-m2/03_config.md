# H-M2 Configuration

Applied: Standard dataclass pattern (consistent with H-M1 actual code)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: config classes verified from actual code (`h-m1/code/compare_variance_selection.py`)
**Config Files Found**: `compare_variance_selection.py` — `H_M1Config` dataclass
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

From `/h-m1/code/compare_variance_selection.py` (actual code, verified):

```python
@dataclass
class H_M1Config:
    profiling_json: str = "docs/youra_research/h-e1/results/mbpp_variance_profile.json"
    fallback_script: str = "docs/youra_research/h-e1/code/profile_mbpp.py"
    k: int = 50
    seed: int = 42
    results_dir: str = "docs/youra_research/h-m1/results"
    figures_dir: str = "docs/youra_research/h-m1/figures"
    min_mean_var_difference: float = 0.0
```

Figure dicts: `FIG1`, `FIG2`, `FIG3`, `FIG4`, `FIGURE_DEFAULTS = {"dpi": 150, "tight_layout": True}`

---

## Full H_M2Config Dataclass

```python
from dataclasses import dataclass, field
from typing import List
import os


@dataclass
class H_M2Config:
    # --- Inputs from H-M1 ---
    h_m1_results_json: str = "docs/youra_research/h-m1/results/selection_results.json"
    profiling_json: str = "docs/youra_research/h-e1/results/mbpp_variance_profile.json"

    # --- Model ---
    model_id: str = "deepseek-ai/deepseek-coder-7b-instruct-v1.5"

    # --- Dataset ---
    mbpp_dataset_id: str = "google-research-datasets/mbpp"
    mbpp_subset: str = "sanitized"
    mbpp_split: str = "train"
    k: int = 50
    seed: int = 42  # used for random-50 sampling and training

    # --- GRPO Training (same for both conditions) ---
    learning_rate: float = 5e-7
    num_generations: int = 4
    generation_batch_size: int = 4
    max_steps: int = 50
    beta: float = 0.0       # Non-standard: 0.0 avoids spurious KL grads on zero-std groups (TRL #5588)
    logging_steps: int = 1  # required for per-step frac_reward_zero_std
    use_vllm: bool = False
    save_steps: List[int] = field(default_factory=lambda: [10, 20, 50])

    # --- Checkpoints for gate evaluation ---
    gate_checkpoints: List[int] = field(default_factory=lambda: [10, 20, 50])
    gap_threshold_pp: float = 0.05  # secondary gate: gap >= 5pp at step 10

    # --- Output ---
    results_dir: str = "docs/youra_research/h-m2/results"
    figures_dir: str = "docs/youra_research/h-m2/figures"

    # --- TRL version requirement ---
    min_trl_version: str = "0.15.0"

    def __post_init__(self):
        assert self.k == 50, "k must be 50 (variance-50 vs random-50)"
        assert self.num_generations == self.generation_batch_size == 4, "G=4 required"
        assert self.logging_steps == 1, "logging_steps=1 required for per-step metrics"
        assert self.beta == 0.0, "beta must be 0.0 (see TRL issue #5588)"
        assert len(self.save_steps) > 0
```

YAML equivalent schema:

```yaml
# h_m2_config.yaml
model_id: "deepseek-ai/deepseek-coder-7b-instruct-v1.5"
mbpp_dataset_id: "google-research-datasets/mbpp"
mbpp_subset: "sanitized"
mbpp_split: "train"
k: 50
seed: 42
learning_rate: 5.0e-7
num_generations: 4
generation_batch_size: 4
max_steps: 50
beta: 0.0
logging_steps: 1
use_vllm: false
save_steps: [10, 20, 50]
gate_checkpoints: [10, 20, 50]
gap_threshold_pp: 0.05
results_dir: "docs/youra_research/h-m2/results"
figures_dir: "docs/youra_research/h-m2/figures"
min_trl_version: "0.15.0"
```

---

## A-5: Analysis & Gate [Complexity: 1, Budget: 2]

Applied: Standard dataclass defaults

### C-5-1: Gate Metrics Computation Schema

Input contract:
- `frac_var: list[float]` — len=50, `frac_var[i]` = `frac_reward_zero_std` at step i+1 (variance-50)
- `frac_rnd: list[float]` — len=50, same for random-50
- `checkpoints: list[int]` — `[10, 20, 50]` (1-indexed steps; slices `[0:N]`)

Computation:
```python
def compute_gate_metrics(frac_var, frac_rnd, checkpoints=[10, 20, 50]):
    results = {}
    for N in checkpoints:
        mean_var = float(np.mean(frac_var[0:N]))
        mean_rnd = float(np.mean(frac_rnd[0:N]))
        gap = mean_rnd - mean_var  # positive = variance-50 wins
        results[f"checkpoint_{N}"] = {
            "mean_frac_var": mean_var,
            "mean_frac_rnd": mean_rnd,
            "gap_pp": gap,
            "gate_pass": mean_var < mean_rnd,
        }
    results["primary_gate_pass"] = all(
        results[f"checkpoint_{N}"]["gate_pass"] for N in checkpoints
    )
    results["secondary_gate_pass"] = results["checkpoint_10"]["gap_pp"] >= 0.05
    return results
```

Gap formula: `gap_at_10_pp = mean_frac_10_rnd - mean_frac_10_var`

### C-5-2: Results JSON Schema

`gate_results.json` full schema:

```python
GATE_RESULTS_SCHEMA = {
    "hypothesis": "H-M2",
    "checkpoint_10": {
        "mean_frac_var": float,   # mean frac_reward_zero_std steps 1-10, variance-50
        "mean_frac_rnd": float,   # mean frac_reward_zero_std steps 1-10, random-50
        "gap_pp": float,          # mean_frac_rnd - mean_frac_var
        "gate_pass": bool,
    },
    "checkpoint_20": {
        "mean_frac_var": float,
        "mean_frac_rnd": float,
        "gap_pp": float,
        "gate_pass": bool,
    },
    "checkpoint_50": {
        "mean_frac_var": float,
        "mean_frac_rnd": float,
        "gap_pp": float,
        "gate_pass": bool,
    },
    "primary_gate_pass": bool,    # True iff gate_pass at ALL three checkpoints
    "secondary_gate_pass": bool,  # True iff gap_pp at checkpoint_10 >= 0.05
    "frac_zero_std_variance50": list,   # len=50, raw per-step values
    "frac_zero_std_random50": list,     # len=50, raw per-step values
}
```

Directory structure:
```
docs/youra_research/h-m2/results/
    variance50/          # GRPOTrainer output for variance-50 condition
    random50/            # GRPOTrainer output for random-50 condition
    gate_results.json    # computed gate metrics (schema above)
docs/youra_research/h-m2/figures/
    gate_comparison.png
    learning_curves.png
    gap_trajectory.png
    reward_std_histograms.png
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | GateMetricsSchema | Input/output contract + `compute_gate_metrics` function spec |
| C-5-2 | ResultsJSONSchema | Full `gate_results.json` field types + directory layout |

---

## A-8: End-to-End Validation [Complexity: 1, Budget: 2]

Applied: Standard assert-based validation pattern

### C-8-1: Environment Validation Checks

```python
def validate_environment(cfg: H_M2Config):
    import trl
    from packaging.version import Version
    import torch
    import json
    from pathlib import Path
    from datasets import load_dataset

    # TRL version
    assert Version(trl.__version__) >= Version(cfg.min_trl_version), (
        f"TRL >= {cfg.min_trl_version} required for frac_reward_zero_std; got {trl.__version__}"
    )

    # CUDA
    assert torch.cuda.is_available(), "CUDA not available"

    # H-E1 profiling JSON
    assert Path(cfg.profiling_json).exists(), (
        f"H-E1 profiling JSON not found: {cfg.profiling_json}"
    )

    # MBPP dataset (triggers download if not cached)
    mbpp = load_dataset(cfg.mbpp_dataset_id, cfg.mbpp_subset, split=cfg.mbpp_split)
    assert len(mbpp) >= 374, f"Expected >= 374 MBPP train problems, got {len(mbpp)}"
```

### C-8-2: Experiment Validation Asserts

```python
def validate_experiment_results(
    trainer_var,       # trained GRPOTrainer for variance-50
    trainer_rnd,       # trained GRPOTrainer for random-50
    gate_results: dict,
    figures_dir: str,
):
    from pathlib import Path

    # frac_reward_zero_std present in log_history
    frac_var = [
        log["frac_reward_zero_std"]
        for log in trainer_var.state.log_history
        if "frac_reward_zero_std" in log
    ]
    frac_rnd = [
        log["frac_reward_zero_std"]
        for log in trainer_rnd.state.log_history
        if "frac_reward_zero_std" in log
    ]

    assert len(frac_var) == 50, f"Expected 50 steps, got {len(frac_var)} for variance-50"
    assert len(frac_rnd) == 50, f"Expected 50 steps, got {len(frac_rnd)} for random-50"

    # Gate assertion (mechanism working)
    import numpy as np
    gap_at_10 = np.mean(frac_rnd[:10]) - np.mean(frac_var[:10])
    assert gap_at_10 > 0, (
        f"FAIL: variance-50 not showing lower frac_zero_std at step 10 (gap={gap_at_10:.4f})"
    )

    # Primary gate
    assert gate_results["primary_gate_pass"], (
        "FAIL: primary gate not passed (variance-50 >= random-50 at some checkpoint)"
    )

    # Figure files
    for fname in ["gate_comparison.png", "learning_curves.png"]:
        assert Path(figures_dir, fname).exists(), f"Missing figure: {fname}"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | EnvValidation | TRL version, CUDA, H-E1 JSON, MBPP dataset checks |
| C-8-2 | ExperimentAsserts | Post-training frac_zero_std length, gap > 0, figure existence |
