# Config: h-e1-v2
# Targeted Model Card Sampling for Documentation Feature Variance

**Hypothesis Type:** EXISTENCE (SCOPE_REFINEMENT from h-e1)
**Date:** 2026-03-17

Applied: hardcoded-constants-pattern (statistical pipeline — no neural network, no tunable hyperparameters)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Config classes verified from actual base code (h-e1/code/config.py read directly)
**Config Files Found:** `docs/youra_research/20260317_data_problems/h-e1/code/config.py`
**Pattern Used:** Hardcoded module-level constants (no dataclass — LIGHT tier statistical pipeline)

---

## Inherited Configuration

All constants verified from actual `h-e1/code/config.py`. The following are **inherited unchanged**:

```python
# Verified from: h-e1/code/config.py (actual implementation)

LEADERBOARD_DATASET: str = "open-llm-leaderboard/contents"

BENCHMARK_COLS_RAW: list = ["IFEval", "BBH", "MATH Lvl 5", "GPQA", "MUSR", "MMLU-PRO"]
BENCHMARK_COLS: list = ["ifeval", "bbh", "math_lvl5", "gpqa", "musr", "mmlu_pro"]
FEATURE_COLS: list = [
    "dedup_documented",
    "perplexity_filter_documented",
    "domain_composition_documented",
    "decontamination_documented",
]

REGEX_PATTERNS: dict = {
    "dedup_documented": r"dedup|near.?dup|minhash|exact.?dedup",
    "perplexity_filter_documented": r"perplexity.{0,20}filter|ppl.{0,10}filter",
    "domain_composition_documented": r"domain.{0,30}(%|percent|composition)|data.{0,30}mix",
    "decontamination_documented": r"decontaminat|n.?gram.{0,20}overlap|benchmark.{0,20}holdout",
}

ARCH_FAMILY_PATTERNS: dict = {
    "LLaMA": r"llama|llama2|llama-2",
    "Mistral": r"mistral|mixtral",
    "Falcon": r"falcon",
    "Pythia": r"pythia|eleuther",
    "OLMo": r"olmo",
}

PARAM_COUNT_MAP: dict = {
    r"llama.*7b": 7e9,
    r"llama.*13b": 13e9,
    r"llama.*70b": 70e9,
    r"falcon.*7b": 7e9,
    r"falcon.*40b": 40e9,
    r"mistral.*7b": 7e9,
    r"pythia.*1b": 1e9,
    r"pythia.*7b": 7e9,
    r"pythia.*12b": 12e9,
}

MIN_BENCHMARK_COVERAGE: int = 4
MIN_REGISTRY_SIZE: int = 200
MIN_FEATURES_WITH_VARIANCE: int = 3

API_BACKOFF_BASE: float = 2.0
API_MAX_RETRIES: int = 5
CHECKPOINT_INTERVAL: int = 100

RANDOM_STATE: int = 42

OLS_FORMULA_BASELINE: str = "avg_score ~ log_params + log_tokens + C(arch_family)"
OLS_FORMULA_PROPOSED: str = "avg_score ~ log_params + log_tokens + doc_score + C(arch_family)"

ALPHA: float = 0.05
PERMUTATION_SAMPLES: int = 1000
POWER_TARGET: float = 0.80
```

---

## Config Constants

Complete h-e1-v2 `config.py` (copy-paste ready):

```python
# ============================================================
# H-E1-V2 Configuration — Hardcoded constants, LIGHT tier
# SCOPE_REFINEMENT of h-e1: only DATA_DIR, FIGURES_DIR, CHECKPOINT_DIR changed
# ============================================================

# --- Data Sources ---
LEADERBOARD_DATASET: str = "open-llm-leaderboard/contents"

# --- Column Definitions ---
BENCHMARK_COLS_RAW: list = [
    "IFEval",
    "BBH",
    "MATH Lvl 5",
    "GPQA",
    "MUSR",
    "MMLU-PRO",
]

BENCHMARK_COLS: list = [
    "ifeval",
    "bbh",
    "math_lvl5",
    "gpqa",
    "musr",
    "mmlu_pro",
]

FEATURE_COLS: list = [
    "dedup_documented",
    "perplexity_filter_documented",
    "domain_composition_documented",
    "decontamination_documented",
]

# --- Keyword Regex Patterns (pre-registered, do NOT modify post-run) ---
REGEX_PATTERNS: dict = {
    "dedup_documented": r"dedup|near.?dup|minhash|exact.?dedup",
    "perplexity_filter_documented": r"perplexity.{0,20}filter|ppl.{0,10}filter",
    "domain_composition_documented": r"domain.{0,30}(%|percent|composition)|data.{0,30}mix",
    "decontamination_documented": r"decontaminat|n.?gram.{0,20}overlap|benchmark.{0,20}holdout",
}

# --- Architecture Family Patterns ---
ARCH_FAMILY_PATTERNS: dict = {
    "LLaMA": r"llama|llama2|llama-2",
    "Mistral": r"mistral|mixtral",
    "Falcon": r"falcon",
    "Pythia": r"pythia|eleuther",
    "OLMo": r"olmo",
}

# --- Parameter Count Map (hardcoded fallback) ---
PARAM_COUNT_MAP: dict = {
    r"llama.*7b": 7e9,
    r"llama.*13b": 13e9,
    r"llama.*70b": 70e9,
    r"falcon.*7b": 7e9,
    r"falcon.*40b": 40e9,
    r"mistral.*7b": 7e9,
    r"pythia.*1b": 1e9,
    r"pythia.*7b": 7e9,
    r"pythia.*12b": 12e9,
}

# --- Gate Thresholds ---
MIN_BENCHMARK_COVERAGE: int = 4
MIN_REGISTRY_SIZE: int = 200
MIN_FEATURES_WITH_VARIANCE: int = 3

# --- API / Checkpointing ---
API_BACKOFF_BASE: float = 2.0
API_MAX_RETRIES: int = 5
CHECKPOINT_INTERVAL: int = 100

# --- Reproducibility ---
RANDOM_STATE: int = 42

# --- Output Paths (CHANGED from h-e1) ---
DATA_DIR: str = "h-e1-v2/data"
FIGURES_DIR: str = "h-e1-v2/figures"
CHECKPOINT_DIR: str = "h-e1-v2/data/checkpoints"

# ============================================================
# Statistical Analysis Parameters
# ============================================================

OLS_FORMULA_BASELINE: str = (
    "avg_score ~ log_params + log_tokens + C(arch_family)"
)

OLS_FORMULA_PROPOSED: str = (
    "avg_score ~ log_params + log_tokens + doc_score + C(arch_family)"
)

ALPHA: float = 0.05
PERMUTATION_SAMPLES: int = 1000
POWER_TARGET: float = 0.80
```

### New Constant in main.py (NOT in config.py)

`TARGETED_FAMILY_PREFIXES` lives in `main.py` — it is used only by `sort_model_ids_by_family()`:

```python
# In h-e1-v2/code/main.py — module-level constant
TARGETED_FAMILY_PREFIXES: list[str] = [
    "meta-llama/", "NousResearch/Llama",   # LLaMA family
    "mistralai/",                            # Mistral
    "Qwen/",                                 # Qwen
    "tiiuae/falcon",                         # Falcon
    "EleutherAI/pythia",                     # Pythia
    "allenai/OLMo",                          # OLMo
]
```

---

## YAML Schema

```yaml
# h-e1-v2 experiment configuration
hypothesis: h-e1-v2
type: EXISTENCE_SCOPE_REFINEMENT

# Reproducibility
random_state: 42

# Gate thresholds
min_benchmark_coverage: 4
min_registry_size: 200
min_features_with_variance: 3

# API settings
api_backoff_base: 2.0
api_max_retries: 5
checkpoint_interval: 100

# Statistical parameters
alpha: 0.05
permutation_samples: 1000
power_target: 0.80

# Output paths (CHANGED from h-e1)
data_dir: "h-e1-v2/data"
figures_dir: "h-e1-v2/figures"
checkpoint_dir: "h-e1-v2/data/checkpoints"

# Targeted sampling (NEW — in main.py)
targeted_family_prefixes:
  - "meta-llama/"
  - "NousResearch/Llama"
  - "mistralai/"
  - "Qwen/"
  - "tiiuae/falcon"
  - "EleutherAI/pythia"
  - "allenai/OLMo"
```

---

## Changes from h-e1

| Item | Location | h-e1 Value | h-e1-v2 Value |
|------|----------|-----------|---------------|
| `DATA_DIR` | config.py | `"h-e1/data"` | `"h-e1-v2/data"` |
| `FIGURES_DIR` | config.py | `"h-e1/figures"` | `"h-e1-v2/figures"` |
| `CHECKPOINT_DIR` | config.py | `"h-e1/data/checkpoints"` | `"h-e1-v2/data/checkpoints"` |
| `TARGETED_FAMILY_PREFIXES` | main.py | (not present) | 7-element list (new) |
| All statistical params | config.py | — | UNCHANGED (`alpha=0.05`, `permutation_samples=1000`, `random_state=42`) |
| All regex patterns | config.py | — | UNCHANGED (pre-registered, HARKing protection) |
| All column definitions | config.py | — | UNCHANGED |
| Gate thresholds | config.py | — | UNCHANGED (`min_registry_size=200`, `min_features_with_variance=3`) |
