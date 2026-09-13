# Configuration: h-m4
# Difficulty-Stratified ECE + DELTA_ECE Gate + Temperature Scaling Probe

**Date:** 2026-03-18
**Hypothesis:** h-m4 (MECHANISM — Step 4 of 4)
**Gate:** MUST_WORK — DELTA_ECE >= 0.03 in >= 2/3 models, CI excludes zero, persists post-T

Applied: Standard Python dataclass config pattern (Archon KB returned domain-mismatched results; standard defaults used)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config classes verified from actual h-m3 code
**Config Files Found**: `docs/youra_research/20260316_verifia/h-m3/code/src/h_m3/config.py`
**Pattern Used**: dataclass (inherited and extended from h-m3)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual h-m3 Code)

```python
# From: h-m3/code/src/h_m3/config.py (ACTUAL CODE — verified line by line)

MODEL_IDS: list[str] = [
    "NousResearch/Meta-Llama-3-8B",
    "codellama/CodeLlama-7b-hf",
    "deepseek-ai/deepseek-coder-6.7b-base",
]

MODEL_SHORT_NAMES: dict[str, str] = {
    "NousResearch/Meta-Llama-3-8B": "llama3_8b",
    "codellama/CodeLlama-7b-hf": "codellama_7b",
    "deepseek-ai/deepseek-coder-6.7b-base": "deepseek_6.7b",
}

HARD_THRESHOLD: float = 0.0   # pass@1 <= 0.0 -> hard tier
EASY_THRESHOLD: float = 0.6   # pass@1 >= 0.6 -> easy tier
SEED: int = 42

# h-m3 FigureConfig (reference — h-m4 adapts filenames, adds fig6):
# dpi=150, figures_dir="figures", fig1..fig5 filenames differ from h-m4
```

**Verified from**: `/home/anonymous/YouRA_results_new_4/TEST_verifiai/docs/youra_research/20260316_verifia/h-m3/code/src/h_m3/config.py` (actual implementation)

**Path depth note**: h-m3 uses `../../h-m2/results` (nested at `code/src/h_m3/`). h-m4 uses `../h-m2/results` (anchored at `h-m4/` folder root per architecture).

---

## A-9: Figures 4-6 [Complexity: 10, Budget: 2 subtasks]

### Configuration (Python Dataclass)

```python
@dataclass
class FigureConfig:
    figures_dir: str = "figures"
    dpi: int = 150                                         # matches h-m3 convention
    fig1_filename: str = "fig1_delta_ece_gate.png"
    fig2_filename: str = "fig2_reliability_diagrams.png"
    fig3_filename: str = "fig3_temperature_scaling.png"
    fig4_filename: str = "fig4_null_baseline.png"
    fig5_filename: str = "fig5_m_sensitivity.png"
    fig6_filename: str = "fig6_bootstrap_distribution.png"
    # Non-standard: reliability_bins matches M_PRIMARY so visual bins align with ECE computation
    reliability_bins: int = 15
    bootstrap_hist_bins: int = 30
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | FigureConfig dataclass | All 6 filenames, dpi, reliability_bins, bootstrap_hist_bins |
| C-9-2 | Figure path resolution | Helper resolving figures_dir + filename to absolute Path |

---

## A-11: Orchestration [Complexity: 10, Budget: 2 subtasks]

### Configuration (Python Dataclass + CLI)

```python
@dataclass
class ExperimentConfig:
    hm3_results: str = "../h-m3/results"
    hm2_results: str = "../h-m2/results"
    he1_results: str = "../h-e1/results"
    output_dir: str = "results"
    figures_dir: str = "figures"
    seed: int = 42
    n_boot: int = 1000
    m_primary: int = 15


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="h-m4: Difficulty-Stratified ECE experiment")
    p.add_argument("--hm3-results",  default="../h-m3/results", help="h-m3 results dir")
    p.add_argument("--hm2-results",  default="../h-m2/results", help="h-m2 results dir")
    p.add_argument("--he1-results",  default="../h-e1/results",  help="h-e1 results dir")
    p.add_argument("--output-dir",   default="results",          help="Output dir for JSON")
    p.add_argument("--figures-dir",  default="figures",          help="Output dir for figures")
    p.add_argument("--seed",         type=int, default=42)
    p.add_argument("--n-boot",       type=int, default=1000)
    p.add_argument("--m-primary",    type=int, default=15)
    return p


def cfg_from_args(args: argparse.Namespace) -> ExperimentConfig:
    return ExperimentConfig(
        hm3_results=args.hm3_results,
        hm2_results=args.hm2_results,
        he1_results=args.he1_results,
        output_dir=args.output_dir,
        figures_dir=args.figures_dir,
        seed=args.seed,
        n_boot=args.n_boot,
        m_primary=args.m_primary,
    )
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-11-1 | ExperimentConfig dataclass | All path fields and numeric params with defaults |
| C-11-2 | CLI argparse schema | build_parser() + cfg_from_args() mapping |

---

## A-4: Null Baseline [Complexity: 9, Budget: 2 subtasks]

### Configuration (Constants)

```python
# P2 gate (informational — not required for MUST_WORK pass)
P2_MIN_PASSING_MODELS: int = 2           # excess_ece_hard > excess_ece_easy in >= 2/3 models
P2_BOOTSTRAP_P_THRESHOLD: float = 0.05  # one-sided bootstrap p-value threshold

# Null baseline is data-derived (no fixed config):
#   null_conf_hard = mean(y_hard)  ~ 0.0 by tier definition
#   null_conf_easy = mean(y_easy)  ~ 0.6+
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | P2 gate constants | P2_MIN_PASSING_MODELS, P2_BOOTSTRAP_P_THRESHOLD |
| C-4-2 | Null output keys | Output dict schema: null_conf_hard/easy, ece_null_hard/easy, excess_ece_hard/easy |

---

## A-7: Gate Evaluation [Complexity: 9, Budget: 2 subtasks]

### Configuration (Constants)

```python
# P1 and P3 gate (both REQUIRED for MUST_WORK combined pass)
DELTA_ECE_THRESHOLD: float = 0.03  # minimum DELTA_ECE for a model to count as passing
MIN_TIER_SIZE: int = 20             # model excluded from gate if n_hard < 20 or n_easy < 20
P1_MIN_PASSING: int = 2             # gate PASS if >= 2/3 models satisfy P1

# Non-standard: ci_lower > 0 is an additional P1 constraint beyond threshold
P1_REQUIRE_CI_EXCLUDES_ZERO: bool = True

# P3: temperature scaling robustness
HOLDOUT_FRAC: float = 0.2                      # 20% holdout for T-fitting
T_BOUNDS: tuple[float, float] = (0.01, 10.0)  # bounds for scipy.optimize.minimize_scalar

# M-sensitivity
M_SENSITIVITY: list[int] = [10, 15, 20]
```

**Gate summary:**

| Gate | Required | Condition |
|------|----------|-----------|
| P1 | YES | DELTA_ECE >= 0.03 AND ci_lower > 0 in >= 2 models |
| P2 | No (informational) | excess_ece_hard > excess_ece_easy AND p < 0.05 in >= 2 models |
| P3 | YES | post_T_delta_ece >= 0.03 AND post_T_ci_lower > 0 in >= 2 models |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | P1/P3 gate constants | DELTA_ECE_THRESHOLD, MIN_TIER_SIZE, P1_MIN_PASSING, HOLDOUT_FRAC, T_BOUNDS |
| C-7-2 | Diagnostic log format | stdout template matching FR-6.2 (Model, n_hard, n_easy, ECE, DELTA_ECE, CI, T*, gates) |

---

## Complete config.py (Copy-Paste Ready)

```python
"""config.py — h-m4 constants and dataclasses for difficulty-stratified ECE analysis."""
from __future__ import annotations
from dataclasses import dataclass, field

# ── Inherited from h-m3 (verified from h-m3/code/src/h_m3/config.py) ──────────

MODEL_IDS: list[str] = [
    "NousResearch/Meta-Llama-3-8B",
    "codellama/CodeLlama-7b-hf",
    "deepseek-ai/deepseek-coder-6.7b-base",
]

MODEL_SHORT_NAMES: dict[str, str] = {
    "NousResearch/Meta-Llama-3-8B": "llama3_8b",
    "codellama/CodeLlama-7b-hf": "codellama_7b",
    "deepseek-ai/deepseek-coder-6.7b-base": "deepseek_6.7b",
}

HARD_THRESHOLD: float = 0.0
EASY_THRESHOLD: float = 0.6
SEED: int = 42

# ── h-m4 specific constants ───────────────────────────────────────────────────

N_BOOT: int = 1000
M_PRIMARY: int = 15
M_SENSITIVITY: list[int] = [10, 15, 20]
DELTA_ECE_THRESHOLD: float = 0.03
MIN_TIER_SIZE: int = 20
# Non-standard: 0.2 preserves 80% eval set while providing enough holdout data for T-fitting
HOLDOUT_FRAC: float = 0.2
T_BOUNDS: tuple[float, float] = (0.01, 10.0)

P1_MIN_PASSING: int = 2
P1_REQUIRE_CI_EXCLUDES_ZERO: bool = True
P2_MIN_PASSING: int = 2
P2_BOOTSTRAP_P_THRESHOLD: float = 0.05

CONFIDENCE_SCORES_FILENAME: str = "ptrue_confidence_scores.json"
TIER_ASSIGNMENTS_FILENAME: str = "tier_assignments.csv"

DEFAULT_HM3_RESULTS: str = "../h-m3/results"
DEFAULT_HM2_RESULTS: str = "../h-m2/results"
DEFAULT_HE1_RESULTS: str = "../h-e1/results"
DEFAULT_OUTPUT_DIR: str = "results"
DEFAULT_FIGURES_DIR: str = "figures"

RESULTS_FILENAME: str = "delta_ece_results.json"
RESULTS_SCHEMA_VERSION: str = "FR-8.1"


@dataclass
class ExperimentConfig:
    hm3_results: str = DEFAULT_HM3_RESULTS
    hm2_results: str = DEFAULT_HM2_RESULTS
    he1_results: str = DEFAULT_HE1_RESULTS
    output_dir: str = DEFAULT_OUTPUT_DIR
    figures_dir: str = DEFAULT_FIGURES_DIR
    seed: int = SEED
    n_boot: int = N_BOOT
    m_primary: int = M_PRIMARY


@dataclass
class FigureConfig:
    figures_dir: str = DEFAULT_FIGURES_DIR
    dpi: int = 150
    fig1_filename: str = "fig1_delta_ece_gate.png"
    fig2_filename: str = "fig2_reliability_diagrams.png"
    fig3_filename: str = "fig3_temperature_scaling.png"
    fig4_filename: str = "fig4_null_baseline.png"
    fig5_filename: str = "fig5_m_sensitivity.png"
    fig6_filename: str = "fig6_bootstrap_distribution.png"
    # Non-standard: reliability_bins matches M_PRIMARY so visual bins align with ECE computation
    reliability_bins: int = 15
    bootstrap_hist_bins: int = 30
```

---

## YAML Schema: delta_ece_results.json (FR-8.1)

```yaml
# Schema for h-m4/results/delta_ece_results.json — Version FR-8.1
schema_version: "FR-8.1"
gate_overall: bool           # P1 AND P3 both satisfied
n_models_passing_p1: int     # 0-3
gate_p2_count: int           # 0-3 (informational)
gate_p3_count: int           # 0-3
seed: 42
n_boot: 1000
M_primary: 15

models:
  <model_short>:             # "llama3_8b" | "codellama_7b" | "deepseek_6.7b"
    n_hard: int
    n_easy: int
    ece_hard: float          # null if degenerate (all bins empty)
    ece_easy: float
    delta_ece: float
    ci_lower: float
    ci_upper: float
    p_value: float
    gate_p1: bool
    null_conf_hard: float
    null_conf_easy: float
    ece_null_hard: float
    ece_null_easy: float
    excess_ece_hard: float
    excess_ece_easy: float
    T_star: float
    post_T_delta_ece: float
    post_T_ci_lower: float
    post_T_ci_upper: float
    post_T_p_value: float
    gate_p3: bool

m_sensitivity:
  <model_short>:
    M10: float
    M15: float
    M20: float
```

---

## Self-Validation

- [x] ONE format only (dataclass throughout — no dict alternatives)
- [x] No ASCII diagrams
- [x] Rationale only for non-standard values (HOLDOUT_FRAC, reliability_bins, P1_REQUIRE_CI_EXCLUDES_ZERO)
- [x] Subtask count within budget: 8 total (2+2+2+2 for A-9, A-11, A-4, A-7)
- [x] "Codebase Analysis (Serena)" section included
- [x] Inherited Configuration section included with field names from actual h-m3 code
- [x] MODEL_IDS, MODEL_SHORT_NAMES, HARD_THRESHOLD, EASY_THRESHOLD verified from h-m3/code/src/h_m3/config.py
