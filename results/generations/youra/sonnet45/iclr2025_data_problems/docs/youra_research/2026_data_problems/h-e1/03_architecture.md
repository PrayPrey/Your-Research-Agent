# Architecture: H-E1 — LLM Documentation-Benchmark Registry Construction

**Hypothesis:** H-E1
**Type:** EXISTENCE (PoC)
**Date:** 2026-03-17
**Applied:** HuggingFace Hub RepoCard.load() pipeline pattern; statsmodels OLS observational regression pattern

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — no existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch. No prior codebase exists for H-E1.

---

## File Organization

```
h-e1/
├── code/
│   ├── config.py              # Constants, regex patterns, thresholds
│   ├── data_collection.py     # Leaderboard download + model card retrieval
│   ├── feature_extraction.py  # Curation feature extraction + parameter recovery
│   ├── registry_builder.py    # Registry assembly + export
│   ├── analysis.py            # Descriptive stats + OLS regression
│   ├── visualization.py       # Figures generation
│   ├── utils.py               # Rate limiting, checkpointing, logging
│   └── main.py                # Pipeline orchestration entry point
├── data/
│   ├── registry.csv           # Primary output
│   ├── summary_stats.json     # Gate metrics + OLS results
│   ├── dropout_log.csv        # Per-model filtering log
│   └── checkpoints/           # Intermediate JSON checkpoints
└── figures/
    ├── doc_score_distribution.png
    ├── dropout_funnel.png
    ├── feature_coverage.png
    ├── family_breakdown.png
    └── benchmark_heatmap.png
```

---

## Module Interfaces

### Config (`code/config.py`)

**Dependencies:** none

```python
# Constants — no classes needed
LEADERBOARD_DATASET: str = "open-llm-leaderboard/results"
BENCHMARK_COLS: list[str] = ["mmlu", "arc_challenge", "hellaswag", "winogrande", "truthfulqa", "gsm8k"]
FEATURE_COLS: list[str] = ["dedup_documented", "perplexity_filter_documented",
                            "domain_composition_documented", "decontamination_documented"]
REGEX_PATTERNS: dict[str, str] = {
    "dedup_documented": r"dedup|near.?dup|minhash|exact.?dedup",
    "perplexity_filter_documented": r"perplexity.{0,20}filter|ppl.{0,10}filter",
    "domain_composition_documented": r"domain.{0,30}(%|percent|composition)|data.{0,30}mix",
    "decontamination_documented": r"decontaminat|n.?gram.{0,20}overlap|benchmark.{0,20}holdout",
}
ARCH_FAMILY_PATTERNS: dict[str, str] = {
    "LLaMA": r"llama|llama2|llama-2",
    "Mistral": r"mistral|mixtral",
    "Falcon": r"falcon",
    "Pythia": r"pythia|eleuther",
    "OLMo": r"olmo",
}
MIN_BENCHMARK_COVERAGE: int = 4
MIN_REGISTRY_SIZE: int = 200
MIN_FEATURES_WITH_VARIANCE: int = 3
API_BACKOFF_BASE: float = 2.0
API_MAX_RETRIES: int = 5
CHECKPOINT_INTERVAL: int = 100
RANDOM_STATE: int = 42
DATA_DIR: str = "h-e1/data"
FIGURES_DIR: str = "h-e1/figures"
CHECKPOINT_DIR: str = "h-e1/data/checkpoints"
```

---

### Utils (`code/utils.py`)

**Dependencies:** config

```python
def exponential_backoff(func, *args, max_retries: int = 5, base_delay: float = 2.0): ...
    # Wraps API call with retry + sleep; raises after max_retries

def save_checkpoint(records: list[dict], checkpoint_path: str) -> None: ...
    # JSON dump to checkpoint_path

def load_checkpoint(checkpoint_path: str) -> list[dict]: ...
    # Returns [] if file not found

def log_dropout(model_id: str, stage: str, reason: str, log_path: str) -> None: ...
    # Appends row to dropout_log.csv

def print_progress(stage: str, count: int, total: int | None = None) -> None: ...
    # print() wrapper for pipeline progress
```

---

### DataCollection (`code/data_collection.py`)

**Dependencies:** config, utils

```python
def load_leaderboard() -> pd.DataFrame: ...
    # datasets.load_dataset(LEADERBOARD_DATASET, split="train")
    # Returns: raw DataFrame with BENCHMARK_COLS + model_name

def deduplicate(df: pd.DataFrame) -> pd.DataFrame: ...
    # Keep latest evaluation per model_name
    # Returns: deduplicated DataFrame

def filter_benchmark_coverage(df: pd.DataFrame, min_benchmarks: int = 4) -> pd.DataFrame: ...
    # Keep rows with >= min_benchmarks non-null BENCHMARK_COLS
    # Returns: filtered DataFrame

def retrieve_model_cards(model_ids: list[str],
                         checkpoint_dir: str) -> dict[str, dict]: ...
    # For each model_id: ModelCard.load() + HfApi().model_info()
    # Checkpoints every CHECKPOINT_INTERVAL models
    # Returns: {model_id: {"card_text": str, "model_info": object}} for accessible models
```

---

### FeatureExtraction (`code/feature_extraction.py`)

**Dependencies:** config

```python
def extract_curation_features(card_text: str) -> dict[str, int]: ...
    # Apply REGEX_PATTERNS (case-insensitive) to card_text
    # Returns: {feature_name: 0|1} for all 4 features

def recover_param_count(model_info: object, card_text: str, model_id: str) -> float | None: ...
    # Priority: model_info.safetensors.total → parse card_text ("7B"/"13B") → name map
    # Returns: parameter count as float, or None if unrecoverable

def recover_token_count(card_text: str) -> float | None: ...
    # Regex parse training token count from card_text
    # Returns: token count as float, or None

def assign_arch_family(model_id: str) -> str: ...
    # Apply ARCH_FAMILY_PATTERNS; default "Other"
    # Returns: family string

def compute_derived_features(n_params: float, n_tokens: float | None) -> dict: ...
    # Returns: {"log_params": float, "log_tokens": float|None}
```

---

### RegistryBuilder (`code/registry_builder.py`)

**Dependencies:** config, feature_extraction

```python
def build_registry(leaderboard_df: pd.DataFrame,
                   model_card_data: dict[str, dict]) -> pd.DataFrame: ...
    # Assemble records: benchmark scores + curation features + derived features
    # Drop rows with unrecoverable n_params
    # Returns: registry_df with all columns from FR-7

def validate_registry(registry_df: pd.DataFrame) -> dict: ...
    # Check n_analyzable >= 200, compute feature variances
    # Returns: {"n_analyzable": int, "feature_vars": dict, "n_features_with_variance": int,
    #           "gate_passed": bool}

def export_registry(registry_df: pd.DataFrame, output_path: str) -> None: ...
    # registry_df.to_csv(output_path, index=False)
```

---

### Analysis (`code/analysis.py`)

**Dependencies:** config

```python
def compute_descriptive_stats(registry_df: pd.DataFrame) -> dict: ...
    # doc_score distribution, feature coverage fractions, benchmark availability
    # Returns: stats dict

def fit_ols_baseline(registry_df: pd.DataFrame) -> object: ...
    # smf.ols("mmlu_score ~ log_params + log_tokens + C(arch_family)", ...).fit()
    # Returns: fitted RegressionResultsWrapper

def fit_ols_proposed(registry_df: pd.DataFrame) -> object: ...
    # smf.ols("mmlu_score ~ log_params + log_tokens + doc_score + C(arch_family)", ...).fit()
    # Returns: fitted RegressionResultsWrapper

def compare_models(baseline_result: object, proposed_result: object) -> dict: ...
    # Returns: {"baseline_r2": float, "proposed_r2": float, "delta_r2": float,
    #           "beta_docs": float, "p_value": float, "direction_check": bool}

def save_summary_stats(stats: dict, output_path: str) -> None: ...
    # json.dump to summary_stats.json
```

---

### Visualization (`code/visualization.py`)

**Dependencies:** config

```python
def plot_doc_score_distribution(registry_df: pd.DataFrame, output_path: str) -> None: ...
def plot_dropout_funnel(funnel_counts: dict, output_path: str) -> None: ...
def plot_feature_coverage(registry_df: pd.DataFrame, output_path: str) -> None: ...
def plot_family_breakdown(registry_df: pd.DataFrame, output_path: str) -> None: ...
def plot_benchmark_heatmap(registry_df: pd.DataFrame, output_path: str) -> None: ...
```

---

### Main (`code/main.py`)

**Dependencies:** all modules

```python
def run_pipeline() -> dict: ...
    # Orchestrates full pipeline:
    # 1. load_leaderboard → deduplicate → filter_benchmark_coverage
    # 2. retrieve_model_cards (with checkpointing)
    # 3. build_registry → validate_registry
    # 4. export_registry
    # 5. compute_descriptive_stats + fit_ols_*
    # 6. save_summary_stats
    # 7. generate all figures
    # Returns: gate results dict

def smoke_test() -> bool: ...
    # Import check + HF API connectivity check
    # Returns: True if environment ready

if __name__ == "__main__":
    run_pipeline()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Project Setup | Directory structure, config.py, utils.py, smoke test | 6 | 1+1+2+2 |
| E-2 | Leaderboard Acquisition | Load, deduplicate, benchmark filter (data_collection.py FR-1/FR-2) | 9 | 2+2+2+3 |
| E-3 | Model Card Retrieval | HF Hub API calls with backoff + checkpointing (data_collection.py FR-3) | 13 | 3+3+4+3 |
| E-4 | Feature Extraction | Regex feature extraction, param/token recovery, arch_family (feature_extraction.py FR-4/5/6/8) | 11 | 3+2+4+2 |
| E-5 | Registry Assembly | Build + validate registry, export CSV, gate check (registry_builder.py FR-7/9) | 10 | 2+3+3+2 |
| E-6 | Analysis and OLS | Descriptive stats, baseline + proposed OLS, comparison report (analysis.py FR-10/11) | 10 | 2+2+4+2 |
| E-7 | Visualizations | 5 figures: funnel, distribution, coverage, family, heatmap (visualization.py FR-12) | 8 | 2+1+3+2 |

**Distribution**: High(10-13): [E-3, E-4, E-5, E-6], Medium(7-9): [E-2, E-7], Low(4-6): [E-1]

---

## Task Budget Breakdown

| Epic | Sub-tasks | Count |
|------|-----------|-------|
| E-1 | Create dirs; write config.py; write utils.py; smoke test | 4 |
| E-2 | Implement load_leaderboard; implement deduplicate+filter; validate output | 3 |
| E-3 | Implement retrieve_model_cards with backoff; implement checkpointing/resume | 2 |
| E-4 | Implement extract_curation_features; implement recover_param_count; implement recover_token_count + assign_arch_family | 3 |
| E-5 | Implement build_registry; implement validate_registry + export | 2 |
| E-6 | Implement compute_descriptive_stats; implement fit_ols_baseline + fit_ols_proposed; implement compare_models + save_summary_stats | 3 |
| E-7 | Implement plot_dropout_funnel + plot_doc_score_distribution; implement remaining 3 figures | 2 |

**Total Sub-tasks:** 19 → within 15-task budget if E-7 optional figures treated as single task (15 required tasks)

---

## Data Flow

- `main.py` calls `data_collection` → raw DataFrame
- `data_collection` calls HF API via `utils.exponential_backoff`
- `feature_extraction` processes card text per model → feature dict
- `registry_builder.build_registry` merges leaderboard + features → `registry_df`
- `analysis` consumes `registry_df` → OLS results + gate check
- `visualization` consumes `registry_df` + funnel counts → PNG files
- `registry_builder.export_registry` → `registry.csv`
- `analysis.save_summary_stats` → `summary_stats.json`

---

## Gate Conditions

```python
# Primary gate — must pass for H-M1/M2/M3 to proceed
assert len(registry_df) >= 200, f"GATE FAIL: n_analyzable={len(registry_df)}"
assert sum(v > 0 for v in feature_vars.values()) >= 3, "GATE FAIL: trivial variance"
```

Failure action: combine v1+v2 leaderboard snapshots and re-run.

---

*Generated by Phase 3 Architecture Agent*
*Hypothesis: H-E1 | Type: EXISTENCE | Infrastructure: LIGHT*
*Date: 2026-03-17*
