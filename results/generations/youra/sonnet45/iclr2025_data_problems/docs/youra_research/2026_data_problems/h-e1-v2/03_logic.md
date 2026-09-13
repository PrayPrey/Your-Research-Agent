# Logic: h-e1-v2
# Targeted Model Card Sampling for Documentation Feature Variance

**Hypothesis Type:** EXISTENCE (SCOPE_REFINEMENT from h-e1)
**Date:** 2026-03-17
**Budget:** 0 subtasks (all Low complexity)

Applied: module-reuse-pattern (single-function addition to pipeline orchestrator)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** API signatures verified from actual h-e1 code (direct file read)
**Analyzed Path:** `docs/youra_research/20260317_data_problems/h-e1/code/`
**Relevant Symbols:**

- `run_pipeline()` in `main.py` — modification point at line 78: `model_ids = filtered_df['model_name'].tolist()`
- `smoke_test() -> bool` — unchanged, reused verbatim
- `retrieve_model_cards(model_ids, checkpoint_dir, max_retries, base_delay)` — actual param names verified
- `validate_registry(registry_df) -> dict` — returns `{"n_analyzable": int, "feature_vars": dict, "n_features_with_variance": int, "gate_passed": bool}`
- `compare_models(baseline_result, proposed_result) -> dict` — returns `{"baseline_r2", "proposed_r2", "delta_r2", "beta_docs", "p_value", "direction_check"}`
- `config.DATA_DIR = "h-e1/data"` — must update to `"h-e1-v2/data"`
- `config.FIGURES_DIR = "h-e1/figures"` — must update to `"h-e1-v2/figures"`
- `config.CHECKPOINT_DIR = "h-e1/data/checkpoints"` — must update to `"h-e1-v2/data/checkpoints"`

---

## External Dependencies API (Base Hypothesis)

**Verified from:** `docs/youra_research/20260317_data_problems/h-e1/code/` (actual implementation, NOT spec)

```python
# From: h-e1/code/data_collection.py (ACTUAL CODE)
def load_leaderboard() -> pd.DataFrame: ...
def deduplicate(df: pd.DataFrame) -> pd.DataFrame: ...
def filter_benchmark_coverage(df: pd.DataFrame) -> pd.DataFrame: ...
def retrieve_model_cards(
    model_ids: list,
    checkpoint_dir: str,
    max_retries: int = 5,        # verified — default 5
    base_delay: float = 2.0,     # verified — default 2.0
) -> dict: ...                   # {model_id: {"card_text": str, "model_info": object}}

# From: h-e1/code/registry_builder.py (ACTUAL CODE)
def build_registry(leaderboard_df: pd.DataFrame, model_card_data: dict) -> pd.DataFrame: ...
def validate_registry(registry_df: pd.DataFrame) -> dict:
    # Actual return: {"n_analyzable": int, "feature_vars": dict[str, float],
    #                 "n_features_with_variance": int, "gate_passed": bool}
    # NOTE: "feature_vars" key present in actual code — spec omits it
    ...
def export_registry(registry_df: pd.DataFrame, path: str) -> None: ...

# From: h-e1/code/analysis.py (ACTUAL CODE)
def compute_descriptive_stats(registry_df: pd.DataFrame) -> dict: ...
def fit_ols_baseline(registry_df: pd.DataFrame) -> object: ...   # RegressionResultsWrapper
def fit_ols_proposed(registry_df: pd.DataFrame) -> object: ...   # RegressionResultsWrapper
def compare_models(baseline_result: object, proposed_result: object) -> dict:
    # Actual return: {"baseline_r2": float, "proposed_r2": float, "delta_r2": float,
    #                 "beta_docs": float, "p_value": float, "direction_check": bool}
    # NOTE: "direction_check" key present in actual code — spec omits it
    ...
def save_summary_stats(summary: dict, path: str) -> None: ...

# From: h-e1/code/visualization.py (ACTUAL CODE)
def plot_doc_score_distribution(registry_df: pd.DataFrame, output_path: str) -> None: ...
def plot_dropout_funnel(funnel_counts: dict, output_path: str) -> None: ...
def plot_feature_coverage(registry_df: pd.DataFrame, output_path: str) -> None: ...
def plot_family_breakdown(registry_df: pd.DataFrame, output_path: str) -> None: ...
def plot_benchmark_heatmap(registry_df: pd.DataFrame, output_path: str) -> None: ...
```

---

## A-1: Environment Setup [Complexity: 5]

**Applied**: module-reuse-pattern

### API Signatures

```python
# h-e1-v2/code/config.py — COPIED from h-e1 + 3 path constants updated
DATA_DIR: str = "h-e1-v2/data"                   # was "h-e1/data"
FIGURES_DIR: str = "h-e1-v2/figures"             # was "h-e1/figures"
CHECKPOINT_DIR: str = "h-e1-v2/data/checkpoints" # was "h-e1/data/checkpoints"

# All other constants identical to h-e1/code/config.py:
# LEADERBOARD_DATASET, BENCHMARK_COLS_RAW, BENCHMARK_COLS, FEATURE_COLS,
# REGEX_PATTERNS, ARCH_FAMILY_PATTERNS, MIN_REGISTRY_SIZE (200),
# MIN_FEATURES_WITH_VARIANCE (3), RANDOM_STATE (42), OLS_FORMULA_BASELINE,
# OLS_FORMULA_PROPOSED, ALPHA (0.05), PERMUTATION_SAMPLES (1000)
```

---

## A-2: Implement sort_model_ids_by_family [Complexity: 7]

**Applied**: module-reuse-pattern

### API Signatures

```python
# h-e1-v2/code/main.py — new constant + new function + updated call site

TARGETED_FAMILY_PREFIXES: list[str] = [
    "meta-llama/",
    "NousResearch/Llama",
    "mistralai/",
    "Qwen/",
    "tiiuae/falcon",
    "EleutherAI/pythia",
    "allenai/OLMo",
]


def sort_model_ids_by_family(model_ids: list[str]) -> list[str]:
    """Sort: targeted families first (by prefix order), remainder alphabetical."""
    ...


def smoke_test() -> bool:
    """Check imports + HF API connectivity. Unchanged from h-e1."""
    ...


def run_pipeline() -> dict:
    """Orchestrate full h-e1-v2 pipeline with targeted family sort at Step 2.

    Returns: {"gate_passed": bool, "n_analyzable": int,
              "n_features_with_variance": int, "comparison": dict}
    """
    ...
```

### Key Algorithm: sort_model_ids_by_family

```
Input:  model_ids: list[str]
Output: list[str]  — targeted families first, remainder alphabetical

1. targeted = []
   remainder = []

2. For each model_id in model_ids:
       If any(model_id.startswith(prefix) for prefix in TARGETED_FAMILY_PREFIXES):
           targeted.append(model_id)
       Else:
           remainder.append(model_id)

3. targeted_sorted = sorted(targeted, key=lambda m:
       next(i for i, p in enumerate(TARGETED_FAMILY_PREFIXES) if m.startswith(p)))
   # Sorts within targeted by family prefix order (meta-llama first, etc.)

4. remainder_sorted = sorted(remainder)

5. Return targeted_sorted + remainder_sorted
```

### Call Site Update in run_pipeline()

```python
# BEFORE (h-e1 main.py line 78):
model_ids = filtered_df['model_name'].tolist() if 'model_name' in filtered_df.columns \
    else filtered_df.index.tolist()

# AFTER (h-e1-v2):
raw_model_ids = filtered_df['model_name'].tolist() if 'model_name' in filtered_df.columns \
    else filtered_df.index.tolist()
model_ids = sort_model_ids_by_family(raw_model_ids)
n_targeted = sum(any(m.startswith(p) for p in TARGETED_FAMILY_PREFIXES) for m in model_ids)
print(f"  Targeted families: {n_targeted} models prioritized")
```

---

## A-3: Integration Validation [Complexity: 6]

No new API. `smoke_test()` unchanged from h-e1. Validation confirms:
- All 7 module imports resolve (`config`, `utils`, `data_collection`, `feature_extraction`, `registry_builder`, `analysis`, `visualization`)
- `sort_model_ids_by_family` callable from `main`
- `config.DATA_DIR == "h-e1-v2/data"` (updated path)

---

## A-4: Run Pipeline & Verify Gate [Complexity: 8]

All APIs unchanged from h-e1 except insertion of `sort_model_ids_by_family()` at Step 2.

Gate assertion:
```python
result = run_pipeline()
assert result["gate_passed"] is True           # n_analyzable>=200 AND n_features_with_variance>=3
assert result["n_analyzable"] >= 200
assert result["n_features_with_variance"] >= 3
```

Gate log line:
```python
print(f"Targeted families: {n_targeted} models; n_analyzable={n_analyzable}, n_features_variance={n_features_with_variance}/4")
```

---

## DataFrame Shapes

| Variable | Shape | Note |
|----------|-------|------|
| `raw_df` | (~4576, 8+) | load_leaderboard() |
| `dedup_df` | (~4576, 8+) | minimal drop |
| `filtered_df` | (~4488, 8+) | >=4/6 benchmarks non-null |
| `model_ids` (unsorted) | list[~4488] | from filtered_df['model_name'] |
| `model_ids` (sorted) | list[~4488] | ~300-600 targeted first, rest alphabetical |
| `model_card_data` | dict[~300-600] | {model_id: {"card_text": str, "model_info": obj}} |
| `registry_df` | (>=200, 16+) | cols: model_name, avg_score, log_params, log_tokens, doc_score, dedup_documented, perplexity_filter_documented, domain_composition_documented, decontamination_documented, arch_family, ifeval, bbh, math_lvl5, gpqa, musr, mmlu_pro |

### Gate Metric Computation

```
registry_df (n rows)
  -> n_analyzable = len(registry_df)
  -> feature_vars = registry_df[FEATURE_COLS].var()    # Series[float], shape (4,)
  -> n_features_with_variance = (feature_vars > 0).sum()
  -> gate_passed = (n_analyzable >= 200) and (n_features_with_variance >= 3)
```

---

## Subtasks

Budget: 0 subtasks (all epics Low complexity — no breakdown required)
