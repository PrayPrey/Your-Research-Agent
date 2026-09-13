# H-M2 Configuration Design

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config classes verified from base code (Read tool used directly)
**Config Files Found**: h-e1/code/config.py, h-m1/code/config.py
**Pattern Used**: dataclass + module-level constants

---

## Inherited Configuration (Base Hypothesis)

Applied: h-e1-dataclass-constants-pattern
Applied: h-m1-paths-dataclass-pattern

### Config Classes (From Actual Code)

```python
# From: h-e1/code/config.py and h-m1/code/config.py (verified from actual code)

# Inherited constants (exact names from h-m1/code/config.py):
HH_RLHF_DATASET: str = "Anthropic/hh-rlhf"
N_ROUNDS: int = 3
BOOTSTRAP_ITERS: int = 1000
RANDOM_SEED: int = 42
BONFERRONI_K: int = 3
ALPHA_CORRECTED: float = 0.0167
BRIER_GATE_THRESHOLD: float = 0.02
LR_PARAMS: dict = {"C": 1.0, "max_iter": 1000, "solver": "lbfgs",
                   "class_weight": "balanced", "random_state": 42}
FIGURE_DPI: int = 150  # from h-m1
FIGURES_DIR: str = "../figures"  # from h-m1
```

---

## H-M2 Full Configuration

### config.py

```python
# h-m2/code/config.py
# H-M2: Bi-Directional Temporal Alignment Drift
# Extends H-M1 config — field names verified from h-m1/code/config.py

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml

# ---------------------------------------------------------------------------
# Inherited from H-E1 / H-M1 (verified from actual code)
# ---------------------------------------------------------------------------

HH_RLHF_DATASET: str = "Anthropic/hh-rlhf"
N_ROUNDS: int = 3
RANDOM_SEED: int = 42
BOOTSTRAP_ITERS: int = 2000  # Non-standard: 2000 for tighter CIs on directional test
ALPHA: float = 0.05
BONFERRONI_K: int = 3
ALPHA_CORRECTED: float = 0.0167
BRIER_GATE_THRESHOLD: float = 0.02
LR_PARAMS: Dict[str, Any] = {
    "C": 1.0,
    "solver": "lbfgs",
    "max_iter": 1000,
    "class_weight": "balanced",
    "random_state": 42,
}
HEDGE_WORDS: List[str] = [
    "i think", "i believe", "perhaps", "possibly", "might", "may",
    "could", "probably", "seems", "appears", "arguably", "likely",
    "uncertain", "not sure", "unclear", "i'm not certain",
]
STRUCT_MARKERS: List[str] = [
    "\n-", "\n*", "1.", "2.", "3.", "##", "**",
    "first,", "second,", "third,", "finally,",
    "in conclusion,", "to summarize,", "in summary,",
]

# ---------------------------------------------------------------------------
# New for H-M2: Data
# ---------------------------------------------------------------------------

TEST_SIZE: float = 0.25
ROUND_SIZE_MIN: int = 500
EARLY_ROUND: int = 1
LATE_ROUND: int = 3
CI_ALPHA: float = 0.05

# ---------------------------------------------------------------------------
# New for H-M2: Gate
# ---------------------------------------------------------------------------

N_DIRECTIONAL_GATE: int = 2          # min rounds with same beta direction
BETA_Q_STABILITY_THRESHOLD: float = 0.2  # Non-standard: max allowed |beta_H - beta_L| std across rounds
TOPIC_BALANCE_ALPHA: float = 0.05

# ---------------------------------------------------------------------------
# New for H-M2: Ambiguity (A-7)
# ---------------------------------------------------------------------------

AMBIGUITY_THRESHOLD: float = 0.4    # Inherited kappa threshold from h-m1
HIGH_AMBIGUITY_PREF_RATE_TARGET: float = 0.60  # Non-standard: expected longer-pref rate under high ambiguity
AUC_HELD_OUT_MIN: float = 0.55      # Minimum AUC on held-out cross-round split
AUC_HELD_OUT_TARGET: float = 0.60   # Target AUC for positive result gate

# ---------------------------------------------------------------------------
# New for H-M2: Figures (A-8)
# ---------------------------------------------------------------------------

FIGURES_DPI: int = 150
FIGURE_SIZES: Dict[str, tuple] = {
    "beta_trajectory":    (10, 6),
    "ci_comparison":      (10, 5),
    "auc_heldout":        (8, 5),
    "topic_balance":      (8, 5),
    "gate_summary":       (8, 4),
    "ambiguity_pref_rate": (9, 5),
}
COLOR_PALETTE: Dict[str, str] = {
    "early_round":   "#3498DB",   # blue for early rounds
    "late_round":    "#E74C3C",   # red for late rounds
    "neutral":       "#95A7AA",
    "ci_fill":       "#BDC3C7",
    "significant":   "#2ECC71",
    "high_ambiguity": "#E74C3C",
    "low_ambiguity":  "#3498DB",
}
CI_BAR_STYLE: Dict[str, Any] = {
    "capsize": 4,
    "elinewidth": 1.5,
    "fmt": "o",
    "markersize": 6,
}
FIGURE_FILENAMES: Dict[str, str] = {
    "beta_trajectory":    "beta_trajectory_hm2.png",
    "ci_comparison":      "ci_comparison_early_late.png",
    "auc_heldout":        "auc_heldout_crossround.png",
    "topic_balance":      "topic_balance_check.png",
    "gate_summary":       "gate_summary_hm2.png",
    "ambiguity_pref_rate": "ambiguity_pref_rate_hm2.png",
}

# ---------------------------------------------------------------------------
# New for H-M2: Output / Logging (A-9)
# ---------------------------------------------------------------------------

FIGURES_DIR: str = "../figures"
RESULTS_PATH: str = "../results/results.yaml"
LOG_LEVEL: str = "INFO"
GATE_STATUS_FORMAT: str = "PASS"    # "PASS" | "FAIL" | "WARN"

# ---------------------------------------------------------------------------
# Smoke test overrides
# ---------------------------------------------------------------------------

SMOKE_OVERRIDES: Dict[str, Any] = {
    "bootstrap_iters": 20,
    "hh_rlhf_subsample": 500,
    "round_size_min": 100,
}


@dataclass
class Paths:
    base_dir: Path
    h_e1_code_dir: Path
    h_m1_code_dir: Path
    hypothesis_dir: Path
    figures_dir: Path
    results_dir: Path
    code_dir: Path
    tests_dir: Path

    @classmethod
    def from_base(cls, base_dir: Path) -> "Paths":
        base_dir = Path(base_dir)
        bi_align_dir = base_dir / "docs" / "youra_research" / "20260503_bi_align"
        hypothesis_dir = bi_align_dir / "h-m2"
        return cls(
            base_dir=base_dir,
            h_e1_code_dir=bi_align_dir / "h-e1" / "code",
            h_m1_code_dir=bi_align_dir / "h-m1" / "code",
            hypothesis_dir=hypothesis_dir,
            figures_dir=hypothesis_dir / "figures",
            results_dir=hypothesis_dir / "results",
            code_dir=hypothesis_dir / "code",
            tests_dir=hypothesis_dir / "tests",
        )


@dataclass
class ExperimentConfig:
    # Data
    hh_rlhf_dataset: str = HH_RLHF_DATASET
    n_rounds: int = N_ROUNDS
    round_size_min: int = ROUND_SIZE_MIN
    early_round: int = EARLY_ROUND
    late_round: int = LATE_ROUND
    test_size: float = TEST_SIZE
    random_seed: int = RANDOM_SEED
    # Model
    lr_params: Dict[str, Any] = field(default_factory=lambda: LR_PARAMS.copy())
    # Bootstrap / CI
    bootstrap_iters: int = BOOTSTRAP_ITERS
    ci_alpha: float = CI_ALPHA
    # Gate
    n_directional_gate: int = N_DIRECTIONAL_GATE
    beta_q_stability_threshold: float = BETA_Q_STABILITY_THRESHOLD
    topic_balance_alpha: float = TOPIC_BALANCE_ALPHA
    # Ambiguity
    ambiguity_threshold: float = AMBIGUITY_THRESHOLD
    high_ambiguity_pref_rate_target: float = HIGH_AMBIGUITY_PREF_RATE_TARGET
    auc_held_out_min: float = AUC_HELD_OUT_MIN
    auc_held_out_target: float = AUC_HELD_OUT_TARGET
    # Output
    figures_dir: str = FIGURES_DIR
    results_path: str = RESULTS_PATH
    log_level: str = LOG_LEVEL
    # Optional subsample
    hh_rlhf_subsample: Optional[int] = None


def load_config(config_path: Optional[str] = None) -> ExperimentConfig:
    if config_path is None:
        return ExperimentConfig()
    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)
    cfg = ExperimentConfig()
    for key, val in raw.items():
        if key in ExperimentConfig.__dataclass_fields__:
            setattr(cfg, key, val)
    return cfg
```

---

## Results YAML Schema (results.yaml)

```yaml
# results/results.yaml — output schema for H-M2
gate_status: "PASS"          # PASS | FAIL | WARN
n_directional: 2             # int: rounds with consistent beta direction

beta_deltas:
  beta_L_delta: 0.0          # float: beta_low_ambiguity late - early
  beta_H_delta: 0.0          # float: beta_high_ambiguity late - early
  beta_S_delta: 0.0          # float: beta_stylistic late - early

confidence_intervals:
  beta_L_ci_low: 0.0
  beta_L_ci_high: 0.0
  beta_H_ci_low: 0.0
  beta_H_ci_high: 0.0
  beta_S_ci_low: 0.0
  beta_S_ci_high: 0.0

aucs:
  auc_early: 0.0             # float: AUC on early-round held-out split
  auc_late: 0.0              # float: AUC on late-round held-out split
  auc_heldout_crossround: 0.0  # float: cross-round held-out AUC (A-7)

topic_pvalue: 1.0            # float: chi-square p-value for topic balance

high_ambiguity_pref_rate: 0.0   # float: longer-response pref rate in high-ambiguity bin
low_ambiguity_pref_rate: 0.0

meta:
  random_seed: 42
  bootstrap_iters: 2000
  n_rounds_used: 3
  early_round: 1
  late_round: 3
  run_timestamp: ""
```

---

## A-7: Cross-Round Held-Out [Complexity: 9, Budget: 2]

Applied: Standard train/test split with held-out cross-round evaluation

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Ambiguity Threshold Config | `ambiguity_threshold=0.4`, `auc_held_out_min=0.55`, `auc_held_out_target=0.60` — defines pass/warn/fail for cross-round AUC gate |
| C-7-2 | High-Ambiguity Pref Rate Config | `high_ambiguity_pref_rate_target=0.60`, computed from held-out split with `test_size=0.25`, `random_seed=42` |

---

## A-8: Visualizations [Complexity: 11, Budget: 2]

Applied: h-m1-figure-config-pattern (FIGURE_DPI, FIGURE_SIZES, COLOR_PALETTE, FIGURE_FILENAMES)

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | Figure Layout Config | `FIGURES_DPI=150`, `FIGURE_SIZES` dict (6 figures), `COLOR_PALETTE` with early/late round colors, `CI_BAR_STYLE` dict |
| C-8-2 | Figure Filename Mapping | `FIGURE_FILENAMES` dict mapping 6 plot keys to `*_hm2.png` filenames; save path from `Paths.figures_dir` |

---

## A-9: Pipeline Orchestration [Complexity: 10, Budget: 2]

Applied: Standard results.yaml output pattern from h-m1

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | Results YAML Schema | Full results.yaml schema above; fields: gate_status, n_directional, beta_deltas, CIs, AUCs, topic_pvalue, ambiguity pref rates, meta |
| C-9-2 | Logging + Gate Reporting | `LOG_LEVEL="INFO"`, `GATE_STATUS_FORMAT` in ["PASS","FAIL","WARN"]; orchestrator logs gate result with n_directional count and CI overlap summary |
