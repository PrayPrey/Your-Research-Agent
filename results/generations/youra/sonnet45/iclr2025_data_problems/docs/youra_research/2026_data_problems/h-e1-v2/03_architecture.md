# Architecture: h-e1-v2
# Targeted Model Card Sampling for Documentation Feature Variance

**Hypothesis Type:** EXISTENCE (SCOPE_REFINEMENT from h-e1)
**Date:** 2026-03-17
**Applied:** module-reuse-pattern (minimal single-function modification)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Patterns found from base code (direct file read — Serena project activation failed, files read directly)
**Analyzed Path:** `docs/youra_research/20260317_data_problems/h-e1/code/`
**Findings:** h-e1 has 7 modules (main.py, config.py, data_collection.py, feature_extraction.py, registry_builder.py, analysis.py, visualization.py) plus utils.py and tests/. `run_pipeline()` in main.py is the single modification point: line 78 derives `model_ids` from `filtered_df['model_name'].tolist()` — this is where `sort_model_ids_by_family()` is inserted. Config paths use `"h-e1/data"` and `"h-e1/figures"` — h-e1-v2 must override these to `"h-e1-v2/data"` and `"h-e1-v2/figures"`.

---

## Overview

h-e1-v2 is a minimal SCOPE_REFINEMENT. Only `main.py` is modified — one new function `sort_model_ids_by_family()` and one updated call site in `run_pipeline()`. All other modules are copied unchanged from h-e1.

**File Structure:**

- `h-e1-v2/code/main.py` — MODIFIED (adds `sort_model_ids_by_family()`)
- `h-e1-v2/code/config.py` — COPIED + path constants updated to `h-e1-v2/`
- `h-e1-v2/code/data_collection.py` — COPIED unchanged
- `h-e1-v2/code/feature_extraction.py` — COPIED unchanged
- `h-e1-v2/code/registry_builder.py` — COPIED unchanged
- `h-e1-v2/code/analysis.py` — COPIED unchanged
- `h-e1-v2/code/visualization.py` — COPIED unchanged
- `h-e1-v2/code/utils.py` — COPIED unchanged
- `h-e1-v2/data/` — output directory (registry.csv, summary_stats.json, checkpoints/)
- `h-e1-v2/figures/` — output directory (5 PNG figures)

---

## Module Definitions

### Main (`h-e1-v2/code/main.py`)

**Dependencies:** config, data_collection, feature_extraction, registry_builder, analysis, visualization

```python
TARGETED_FAMILY_PREFIXES: list[str] = [
    "meta-llama/", "NousResearch/Llama",
    "mistralai/",
    "Qwen/",
    "tiiuae/falcon",
    "EleutherAI/pythia",
    "allenai/OLMo",
]

def sort_model_ids_by_family(model_ids: list[str]) -> list[str]: ...
    # Returns: targeted family models first (insertion-order), then remainder alphabetical

def smoke_test() -> bool: ...
    # Unchanged from h-e1

def run_pipeline() -> dict: ...
    # Modified: inserts sort_model_ids_by_family() at Step 2 before retrieve_model_cards()
    # Returns: {"gate_passed": bool, "n_analyzable": int, "n_features_with_variance": int, "comparison": dict}
```

### Config (`h-e1-v2/code/config.py`)

**Dependencies:** none

```python
# All constants identical to h-e1 except output paths:
DATA_DIR: str = "h-e1-v2/data"
FIGURES_DIR: str = "h-e1-v2/figures"
CHECKPOINT_DIR: str = "h-e1-v2/data/checkpoints"

# Unchanged constants (representative):
LEADERBOARD_DATASET: str = "open-llm-leaderboard/contents"
BENCHMARK_COLS_RAW: list  # IFEval, BBH, MATH Lvl 5, GPQA, MUSR, MMLU-PRO
FEATURE_COLS: list         # 4 binary documentation features
REGEX_PATTERNS: dict       # pre-registered — do NOT modify
MIN_REGISTRY_SIZE: int = 200
MIN_FEATURES_WITH_VARIANCE: int = 3
RANDOM_STATE: int = 42
OLS_FORMULA_BASELINE: str
OLS_FORMULA_PROPOSED: str
```

### DataCollection (`h-e1-v2/code/data_collection.py`)

**Dependencies:** config

```python
# COPIED UNCHANGED from h-e1
def load_leaderboard() -> pd.DataFrame: ...
def deduplicate(df: pd.DataFrame) -> pd.DataFrame: ...
def filter_benchmark_coverage(df: pd.DataFrame) -> pd.DataFrame: ...
def retrieve_model_cards(model_ids: list[str], checkpoint_dir: str) -> dict: ...
```

### FeatureExtraction (`h-e1-v2/code/feature_extraction.py`)

**Dependencies:** config

```python
# COPIED UNCHANGED from h-e1
def extract_features(card_text: str) -> dict[str, int]: ...
def extract_training_tokens(card_text: str) -> float | None: ...
def extract_arch_family(model_id: str, card_text: str) -> str: ...
```

### RegistryBuilder (`h-e1-v2/code/registry_builder.py`)

**Dependencies:** config, feature_extraction

```python
# COPIED UNCHANGED from h-e1
def build_registry(leaderboard_df: pd.DataFrame, model_card_data: dict) -> pd.DataFrame: ...
def validate_registry(registry_df: pd.DataFrame) -> dict: ...
    # Returns: {"gate_passed": bool, "n_analyzable": int, "n_features_with_variance": int}
def export_registry(registry_df: pd.DataFrame, path: str) -> None: ...
```

### Analysis (`h-e1-v2/code/analysis.py`)

**Dependencies:** config

```python
# COPIED UNCHANGED from h-e1
def compute_descriptive_stats(registry_df: pd.DataFrame) -> dict: ...
def fit_ols_baseline(registry_df: pd.DataFrame) -> object: ...
def fit_ols_proposed(registry_df: pd.DataFrame) -> object: ...
def compare_models(baseline_result: object, proposed_result: object) -> dict: ...
    # Returns: {"baseline_r2", "proposed_r2", "delta_r2", "beta_docs", "p_value"}
def save_summary_stats(summary: dict, path: str) -> None: ...
```

### Visualization (`h-e1-v2/code/visualization.py`)

**Dependencies:** config

```python
# COPIED UNCHANGED from h-e1 (paths passed as arguments — no hardcoding)
def plot_doc_score_distribution(registry_df: pd.DataFrame, output_path: str) -> None: ...
def plot_dropout_funnel(funnel_counts: dict, output_path: str) -> None: ...
def plot_feature_coverage(registry_df: pd.DataFrame, output_path: str) -> None: ...
def plot_family_breakdown(registry_df: pd.DataFrame, output_path: str) -> None: ...
def plot_benchmark_heatmap(registry_df: pd.DataFrame, output_path: str) -> None: ...
```

---

## External Dependencies (Base Hypothesis)

**Verified from:** `docs/youra_research/20260317_data_problems/h-e1/code/` (actual implementation)

| Module | Source File | Action for h-e1-v2 |
|--------|-------------|---------------------|
| data_collection | `h-e1/code/data_collection.py` | Copy unchanged |
| feature_extraction | `h-e1/code/feature_extraction.py` | Copy unchanged |
| registry_builder | `h-e1/code/registry_builder.py` | Copy unchanged |
| analysis | `h-e1/code/analysis.py` | Copy unchanged |
| visualization | `h-e1/code/visualization.py` | Copy unchanged |
| utils | `h-e1/code/utils.py` | Copy unchanged |
| config | `h-e1/code/config.py` | Copy + update DATA_DIR, FIGURES_DIR, CHECKPOINT_DIR |
| main | `h-e1/code/main.py` | Copy + add `sort_model_ids_by_family()` + update call site |

**All modules use local imports** (no package structure — files in same directory, `sys.path.insert(0, CODE_DIR)` in main.py).

---

## Data Flow

```
load_leaderboard()
  → deduplicate()
  → filter_benchmark_coverage()
  → sort_model_ids_by_family()        ← NEW in h-e1-v2
  → retrieve_model_cards()
  → build_registry()
  → validate_registry()               ← gate: n_analyzable>=200, n_features_with_variance>=3
  → export_registry()
  → compute_descriptive_stats() + fit_ols_baseline() + fit_ols_proposed() + compare_models()
  → save_summary_stats()
  → 5x visualization plots
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment Setup | Create h-e1-v2/code/ directory, copy all h-e1 modules, update config.py paths | 5 | 1+1+1+2 |
| A-2 | Implement sort_model_ids_by_family | Add new function to main.py with TARGETED_FAMILY_PREFIXES constant and update run_pipeline() call site | 7 | 2+1+2+2 |
| A-3 | Integration Validation | Smoke test, verify pipeline orchestration with new sort step, confirm module imports resolve correctly | 6 | 1+2+1+2 |
| A-4 | Run Pipeline & Verify Gate | Execute full pipeline, confirm n_analyzable>=200 AND n_features_with_variance>=3, generate all 5 figures | 8 | 2+2+2+2 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1, A-2, A-3, A-4]

**Total complexity:** 26 (appropriate for SCOPE_REFINEMENT — minimal single-function addition)

---

## Gate Conditions

- `n_analyzable >= 200` AND `n_features_with_variance >= 3`
- Both must be TRUE; pipeline stops if either fails
- Downstream hypotheses h-m1, h-m2, h-m3 all depend on this gate passing
