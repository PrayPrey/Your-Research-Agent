# Configuration: H-E1
# AIFS Conditional Preference Shift Detection in HH-RLHF

**Hypothesis:** H-E1 (EXISTENCE / FOUNDATION)
**Date:** 2026-05-12
**Gate:** MUST_WORK — β₄ > 0, OR ≥ 1.10, p < 0.01

Applied: modular-pipeline pattern (hardcoded module-level constants, single-responsibility modules)
Applied: argparse CLI pattern for statistical analysis entry point

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Config Files Found**: None - new config design
**Pattern Used**: hardcoded module-level constants (LIGHT tier per NFR-2)

---

## Overview

H-E1 is a LIGHT-tier statistical analysis pipeline. Per NFR-2:
- Configuration via hardcoded module-level constants and argparse (no YAML/dataclass required)
- Logging via print statements and CSV/JSON file output (no WandB)
- Testing via smoke test only
- No neural network training — statistical regression only

Each Python module defines its own constants at module level for locality and clarity.

---

## Constants: data_prep.py

```python
import re

# --- Regex patterns for AIFS feature extraction ---
AIFS_PATTERNS: dict[str, re.Pattern] = {
    "structured_list": re.compile(r"^\s*(\d+\.|\*|-)\s", re.MULTILINE),
    "safety_preface": re.compile(
        r"\b(I (cannot|should not|must not)|please note|important:)\b",
        re.IGNORECASE
    ),
    "cot_marker": re.compile(
        r"\b(step \d+|first,|second,|finally,|let('s| us))\b",
        re.IGNORECASE
    ),
    "hedging": re.compile(
        r"\b(however,|that said,|it depends|on the other hand)\b",
        re.IGNORECASE
    ),
}

# --- Clustering ---
COSINE_THRESHOLD: float = 0.85   # Greedy cosine clustering cutoff
MIN_TOKEN_COUNT: int = 20        # Min tokens for both chosen/rejected to keep pair

# --- Embedding ---
MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
MAX_SEQ_LENGTH: int = 256
BATCH_SIZE: int = 512            # Encoding batch size for sentence-transformers

# --- Reproducibility ---
RANDOM_SEED: int = 1
```

**Non-standard rationale:**
- `COSINE_THRESHOLD=0.85`: balances cluster granularity vs. coverage; lower risks over-merging, higher risks too many singleton clusters
- `BATCH_SIZE=512`: GPU-friendly for sentence-transformers; fits typical 8GB VRAM
- `RANDOM_SEED=1`: fixed for reproducibility; 42 is common but 1 is used here to avoid any implicit convention bias

---

## Constants: evaluate.py

```python
# --- Success gate thresholds (MUST_WORK criteria) ---
GATE_BETA4_MIN: float = 0.0      # β₄ must be strictly positive
GATE_OR_MIN: float = 1.10        # Odds ratio must be >= 1.10 (10% lift minimum)
GATE_PVAL_MAX: float = 0.01      # p-value must be < 0.01 (1% significance)
GATE_CI_LO_MIN: float = 1.0      # 95% CI lower bound must exceed 1.0 (excludes null)

# --- Cluster validation for conditional logit feasibility ---
MIN_CLUSTER_COUNT: int = 100     # Minimum number of valid clusters
MIN_PAIRS_PER_CLUSTER: int = 2   # Each cluster must have >= 2 pairs (conditional logit requirement)

# --- Mechanism pre-checks ---
MIN_SPLIT_SIZE: int = 1000       # Minimum pairs per split for split_balanced check
MIN_DELTA_AIFS_STD: float = 0.01 # Minimum std of delta_aifs for data_variance check
MIN_EFFECT_SIZE: float = 1e-6    # Minimum |β₄| to consider effect non-zero
```

**Non-standard rationale:**
- `GATE_OR_MIN=1.10`: requires minimum 10% odds lift — chosen to be practically meaningful, not just statistically significant
- `GATE_PVAL_MAX=0.01`: stricter than conventional 0.05 because this is a MUST_WORK gate (not exploratory)
- `MIN_DELTA_AIFS_STD=0.01`: near-zero std would cause near-singular design matrix in ConditionalLogit

---

## Constants: visualize.py

```python
# --- Output directories ---
FIGURES_DIR: str = "h-e1/figures"

# --- Sensitivity analysis thresholds to sweep ---
SENSITIVITY_THRESHOLDS: list[float] = [0.75, 0.80, 0.85, 0.90]
# Non-standard: 4-point sweep around default 0.85 to show robustness of clustering choice
```

---

## Path Configuration

```python
# --- Output paths (relative to project root) ---
RESULTS_DIR: str = "h-e1/results"
METRICS_FILE: str = "h-e1/results/metrics.json"
MODEL_SUMMARY_FILE: str = "h-e1/results/model_summary.txt"
PAIRS_DF_FILE: str = "h-e1/results/pairs_df.parquet"
LOG_FILE: str = "h-e1/results/experiment.log"
FIGURES_DIR: str = "h-e1/figures"
```

All paths are relative to the project working directory. `run_experiment.py` creates directories with `os.makedirs(..., exist_ok=True)` before writing.

---

## Dataset Configuration

```python
# --- HH-RLHF dataset ---
DATASET_NAME: str = "Anthropic/hh-rlhf"
SPLIT_BASE_DIR: str = "helpful-base"    # split=0, naive annotators
SPLIT_ONLINE_DIR: str = "helpful-online" # split=1, deployed-condition annotators

# Expected sizes (informational, not enforced as hard constraints)
EXPECTED_BASE_SIZE: int = 43_835
EXPECTED_ONLINE_SIZE: int = 36_169

# Split labels
LABEL_BASE: int = 0     # helpful-base
LABEL_ONLINE: int = 1   # helpful-online
```

Loading pattern:
```python
load_dataset("Anthropic/hh-rlhf", data_dir="helpful-base", split="train")
load_dataset("Anthropic/hh-rlhf", data_dir="helpful-online", split="train")
```

---

## Statistical Model Configuration

```python
# --- ConditionalLogit model settings ---
STAT_FRAMEWORK: str = "statsmodels.discrete.conditional_models.ConditionalLogit"
OPTIMIZER: str = "bfgs"          # scipy BFGS (statsmodels default)
MAX_ITER: int = 200              # Sufficient for typical logit convergence
SIGNIFICANCE_LEVEL: float = 0.01 # Alpha for hypothesis test

# --- Model formula components ---
BASELINE_FORMULA: str = "chosen ~ delta_aifs + delta_length"
PROPOSED_FORMULA: str = "chosen ~ delta_aifs + delta_length + delta_aifs_x_split"
EXTENDED_FORMULA: str = "chosen ~ delta_aifs + delta_length + delta_aifs_x_split + supply_prop"

# --- Key coefficient ---
INTERACTION_TERM: str = "delta_aifs_x_split"  # β₄ — annotator condition interaction
```

**Non-standard rationale:**
- `MAX_ITER=200`: statsmodels default is 35; 200 prevents premature non-convergence warnings on larger datasets (~80K pairs)

---

## Validation Thresholds

```python
# --- Cluster feasibility checks (in evaluate.py / experiment.py) ---
MIN_CLUSTER_COUNT: int = 100         # ConditionalLogit requires many groups
MIN_PAIRS_PER_CLUSTER: int = 2       # Minimum discordant pairs per cluster

# --- Mechanism pre-checks (abort-early conditions) ---
MIN_SPLIT_SIZE: int = 1_000          # Both splits must have >= 1000 pairs
MIN_DELTA_AIFS_STD: float = 0.01     # Data variance check
MIN_EFFECT_SIZE: float = 1e-6        # Effect non-zero check (post-fit)

# --- Mechanism check names (for logging) ---
MECHANISM_CHECKS: list[str] = [
    "beta4_fitted",    # delta_aifs_x_split in result.params.index
    "data_variance",   # df_pairs["delta_aifs"].std() > MIN_DELTA_AIFS_STD
    "split_balanced",  # both splits have >= MIN_SPLIT_SIZE pairs
    "effect_nonzero",  # abs(beta4) > MIN_EFFECT_SIZE
]
```

---

## CLI Configuration (argparse)

`run_experiment.py` accepts:

```python
import argparse

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="H-E1: AIFS Conditional Preference Shift Detection"
    )
    parser.add_argument(
        "--results-dir",
        type=str,
        default="h-e1/results",
        help="Directory for output files (default: h-e1/results)"
    )
    parser.add_argument(
        "--figures-dir",
        type=str,
        default="h-e1/figures",
        help="Directory for figures (default: h-e1/figures)"
    )
    parser.add_argument(
        "--cosine-threshold",
        type=float,
        default=0.85,
        help="Cosine similarity threshold for greedy clustering (default: 0.85)"
    )
    parser.add_argument(
        "--max-iter",
        type=int,
        default=200,
        help="Max iterations for ConditionalLogit optimizer (default: 200)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=1,
        help="Random seed (default: 1)"
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Run smoke test: use 500-row subsample per split"
    )
    return parser.parse_args()
```

Smoke test mode subsamples 500 rows per split (helpful-base, helpful-online) to verify end-to-end pipeline without full runtime.

---

## Environment Configuration

**Python version:** 3.10+

**pip dependencies (pinned versions):**

```
datasets==2.19.0
pandas==2.2.2
numpy==1.26.4
scikit-learn==1.4.2
statsmodels==0.14.2
sentence-transformers==2.7.0
torch==2.3.0
transformers==4.41.0
pyarrow==16.1.0
scipy==1.13.0
matplotlib==3.9.0
seaborn==0.13.2
```

**requirements.txt location:** `h-e1/requirements.txt`

**No GPU required** for statistical model fitting. GPU accelerates sentence-transformers encoding only (optional; falls back to CPU).

---

## Hyperparameter Rationale Table

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `COSINE_THRESHOLD` | 0.85 | Standard high-similarity cutoff for semantic deduplication; enables 100+ valid clusters |
| `MIN_TOKEN_COUNT` | 20 | Excludes near-empty responses; below 20 tokens AIFS density is unreliable |
| `BATCH_SIZE` | 512 | Efficient GPU batch for all-MiniLM-L6-v2; fits 8GB VRAM |
| `MAX_SEQ_LENGTH` | 256 | all-MiniLM-L6-v2 native max; truncation beyond this is model default |
| `RANDOM_SEED` | 1 | Fixed for reproducibility |
| `GATE_BETA4_MIN` | 0.0 | Null hypothesis boundary; β₄ must be strictly positive |
| `GATE_OR_MIN` | 1.10 | 10% odds lift is minimum practically meaningful effect |
| `GATE_PVAL_MAX` | 0.01 | Strict alpha for MUST_WORK gate (not exploratory analysis) |
| `GATE_CI_LO_MIN` | 1.0 | 95% CI must exclude the null OR=1.0 |
| `MIN_CLUSTER_COUNT` | 100 | ConditionalLogit requires many groups for stable estimation |
| `MIN_PAIRS_PER_CLUSTER` | 2 | Minimum for within-cluster discordance (conditional logit requirement) |
| `MAX_ITER` | 200 | Prevents premature non-convergence on ~80K pairs (statsmodels default=35) |
| `SIGNIFICANCE_LEVEL` | 0.01 | Matches GATE_PVAL_MAX for consistent reporting |
| `MIN_SPLIT_SIZE` | 1000 | Ensures both annotator conditions have sufficient power |
| `MIN_DELTA_AIFS_STD` | 0.01 | Guards against near-singular design matrix |
| `SENSITIVITY_THRESHOLDS` | [0.75, 0.80, 0.85, 0.90] | 4-point sweep to show clustering robustness |

---

## Subtask Breakdown

Config is integrated into epic tasks (LIGHT tier — no separate config service). Subtasks document the configuration surface per module.

| ID | Subtask | Description |
|----|---------|-------------|
| C-E1-1 | data_prep constants | AIFS_PATTERNS, COSINE_THRESHOLD, MODEL_NAME, BATCH_SIZE, RANDOM_SEED, MIN_TOKEN_COUNT |
| C-E1-2 | evaluate/experiment constants | Gate thresholds, mechanism check names, cluster validation thresholds, statistical model settings |
| C-E1-3 | path and dataset constants | RESULTS_DIR, METRICS_FILE, PAIRS_DF_FILE, LOG_FILE, FIGURES_DIR, dataset name/split labels |
| C-E1-4 | CLI argparse | run_experiment.py argument parser with smoke-test mode, overridable defaults for threshold/seed/dirs |
