# Configuration: H-E1 — LLM Documentation-Benchmark Registry Construction

**Hypothesis:** H-E1
**Type:** EXISTENCE (PoC)
**Date:** 2026-03-17
**Infrastructure:** LIGHT (hardcoded constants, no dataclasses or YAML)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Config Files Found**: None - new config
**Pattern Used**: hardcoded Python constants

Applied: hardcoded-constants pattern (LIGHT tier, no dataclass/YAML overhead)

---

## E-6a: Constants, Paths, and Regex Patterns [Complexity: 5, Budget: 1]

**Applied**: Standard Python constants pattern (LIGHT tier)

### Configuration (`code/config.py`)

```python
# ============================================================
# H-E1 Configuration — Hardcoded constants, LIGHT tier
# ============================================================

# --- Data Sources ---
LEADERBOARD_DATASET: str = "open-llm-leaderboard/results"

# --- Column Definitions ---
BENCHMARK_COLS: list[str] = [
    "mmlu",
    "arc_challenge",
    "hellaswag",
    "winogrande",
    "truthfulqa",
    "gsm8k",
]

FEATURE_COLS: list[str] = [
    "dedup_documented",
    "perplexity_filter_documented",
    "domain_composition_documented",
    "decontamination_documented",
]

# --- Keyword Regex Patterns (pre-registered, do NOT modify post-run) ---
# These patterns are fixed before data collection to prevent HARKing.
REGEX_PATTERNS: dict[str, str] = {
    "dedup_documented": r"dedup|near.?dup|minhash|exact.?dedup",
    "perplexity_filter_documented": r"perplexity.{0,20}filter|ppl.{0,10}filter",
    "domain_composition_documented": r"domain.{0,30}(%|percent|composition)|data.{0,30}mix",
    "decontamination_documented": r"decontaminat|n.?gram.{0,20}overlap|benchmark.{0,20}holdout",
}

# --- Architecture Family Patterns ---
ARCH_FAMILY_PATTERNS: dict[str, str] = {
    "LLaMA": r"llama|llama2|llama-2",
    "Mistral": r"mistral|mixtral",
    "Falcon": r"falcon",
    "Pythia": r"pythia|eleuther",
    "OLMo": r"olmo",
    # Models not matching any pattern → assigned "Other"
}

# --- Gate Thresholds ---
MIN_BENCHMARK_COVERAGE: int = 4    # min non-null benchmark scores to retain a model
MIN_REGISTRY_SIZE: int = 200       # MUST_WORK gate: n_analyzable >= 200
MIN_FEATURES_WITH_VARIANCE: int = 3  # MUST_WORK gate: >=3 of 4 features have variance > 0

# --- API / Checkpointing ---
API_BACKOFF_BASE: float = 2.0   # exponential backoff base (seconds)
API_MAX_RETRIES: int = 5        # max retries per HF API call
CHECKPOINT_INTERVAL: int = 100  # save checkpoint every N models retrieved

# --- Reproducibility ---
RANDOM_STATE: int = 42

# --- Output Paths ---
DATA_DIR: str = "h-e1/data"
FIGURES_DIR: str = "h-e1/figures"
CHECKPOINT_DIR: str = "h-e1/data/checkpoints"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6a-1 | Write config.py | All constants, regex patterns, thresholds, paths as above |

---

## E-6b: OLS Model Specifications and Statistical Parameters [Complexity: 5, Budget: 1]

**Applied**: statsmodels OLS observational regression pattern

### Statistical Configuration

```python
# ============================================================
# Statistical Analysis Parameters — append to config.py
# ============================================================

# --- OLS Formula Specifications ---
# Baseline: scale controls only (no documentation signal)
OLS_FORMULA_BASELINE: str = (
    "mmlu_score ~ log_params + log_tokens + C(arch_family)"
)

# Proposed: adds doc_score (sum of 4 binary curation features, 0–4)
OLS_FORMULA_PROPOSED: str = (
    "mmlu_score ~ log_params + log_tokens + doc_score + C(arch_family)"
)

# --- Inference Parameters ---
ALPHA: float = 0.05          # significance level for beta_docs p-value test
PERMUTATION_SAMPLES: int = 1000  # permutation test iterations for delta_R2 null distribution
POWER_TARGET: float = 0.80   # minimum acceptable statistical power (informational, not a gate)

# --- Derived Feature Definitions (documentation only, computed in feature_extraction.py) ---
# doc_score = sum(dedup_documented, perplexity_filter_documented,
#                 domain_composition_documented, decontamination_documented)  # range 0-4
# log_params = log10(n_params)    # n_params in billions
# log_tokens = log10(n_tokens)    # n_tokens in billions; column may have NaN rows
```

### OLS Model Summary

| Model | Formula | Purpose |
|-------|---------|---------|
| Baseline | `mmlu_score ~ log_params + log_tokens + C(arch_family)` | Scale + family controls |
| Proposed | `mmlu_score ~ log_params + log_tokens + doc_score + C(arch_family)` | Add curation signal |

Key outputs from `compare_models()`:
- `delta_r2 = proposed_r2 - baseline_r2` — primary effect size
- `beta_docs` — OLS coefficient on `doc_score`
- `p_value` — two-sided p-value for `beta_docs`; compared against `ALPHA`
- `direction_check` — True if `beta_docs > 0` (positive association)

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6b-1 | Statistical parameters | OLS formulas, alpha, permutation samples, power target |

---

## Environment / Dependency Specification

### Python Version

```
python >= 3.10
```

### `requirements.txt`

```
# Data / leaderboard
datasets>=2.14.0
huggingface_hub>=0.20.0
pandas>=2.0.0

# Statistical analysis
statsmodels>=0.14.0
scipy>=1.11.0
numpy>=1.24.0

# Visualization
matplotlib>=3.7.0
seaborn>=0.12.0

# Utilities (standard library only beyond these)
tqdm>=4.65.0
```

No GPU dependencies — this is a pure CPU statistical analysis pipeline.

---

*Generated by Phase 3 Configuration Agent*
*Hypothesis: H-E1 | Type: EXISTENCE | Infrastructure: LIGHT*
*Date: 2026-03-17*
