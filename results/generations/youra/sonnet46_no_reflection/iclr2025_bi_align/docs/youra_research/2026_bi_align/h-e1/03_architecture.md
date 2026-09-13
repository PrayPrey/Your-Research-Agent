# Architecture: H-E1
# AIFS Conditional Preference Shift Detection in HH-RLHF

**Hypothesis:** H-E1 (EXISTENCE / FOUNDATION)
**Type:** Statistical analysis pipeline — no neural network training
**Date:** 2026-05-12
**Gate:** MUST_WORK — β₄ > 0, OR ≥ 1.10, p < 0.01

Applied: modular-pipeline pattern (single-responsibility modules with explicit data contracts)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — no existing code to analyze
**Analyzed Path:** N/A (Serena returned no active project at working directory; project is new)
**Findings:** New implementation from scratch. All modules designed de novo per PRD specifications.

---

## Module Structure

```
h-e1/
├── code/
│   ├── data_prep.py        # FR-1, FR-2, FR-3: load, extract, cluster
│   ├── experiment.py       # FR-4, FR-5: model fitting + mechanism verification
│   ├── evaluate.py         # FR-6: metrics extraction + gate check
│   ├── visualize.py        # FR-7: 5 figures
│   └── run_experiment.py   # Orchestration entry point
├── figures/
└── results/
    ├── metrics.json
    ├── model_summary.txt
    ├── pairs_df.parquet
    └── experiment.log
```

---

## Component Responsibilities

### DataPrep (`code/data_prep.py`)

**Dependencies:** datasets, pandas, numpy, sentence-transformers, re

```python
AIFS_PATTERNS: dict[str, re.Pattern]  # 4 regex patterns (constants)
COSINE_THRESHOLD: float = 0.85
MIN_TOKEN_COUNT: int = 20
BATCH_SIZE: int = 512
RANDOM_SEED: int = 1

def load_hh_rlhf() -> tuple[pd.DataFrame, pd.DataFrame]: ...
    # Returns (df_base, df_online) with columns: chosen, rejected

def extract_dialogue(example: dict) -> dict: ...
    # TRL common-prefix pattern: returns {prompt, chosen, rejected}

def filter_pairs(df: pd.DataFrame, min_tokens: int = MIN_TOKEN_COUNT) -> pd.DataFrame: ...
    # Keep only rows where both chosen and rejected >= min_tokens

def compute_aifs_score(text: str) -> float: ...
    # Returns normalized AIFS density per 100 tokens

def build_pairs_df(df_base: pd.DataFrame, df_online: pd.DataFrame,
                   cluster_ids: np.ndarray) -> pd.DataFrame: ...
    # Columns: chosen, delta_aifs, delta_length, delta_aifs_x_split, split, cluster_id

def cluster_prompts(prompts: list[str],
                    threshold: float = COSINE_THRESHOLD,
                    batch_size: int = BATCH_SIZE) -> np.ndarray: ...
    # Returns cluster_id array (len == len(prompts))

def validate_clusters(df_pairs: pd.DataFrame) -> None: ...
    # Aborts if < 100 clusters with >= 2 pairs each
```

---

### Experiment (`code/experiment.py`)

**Dependencies:** statsmodels, pandas, numpy, data_prep

```python
ModelResult = statsmodels.discrete.conditional_models.ConditionalLogitResults

def fit_baseline_model(df_pairs: pd.DataFrame) -> ModelResult: ...
    # Formula: chosen ~ delta_aifs + delta_length, groups=cluster_id

def fit_proposed_model(df_pairs: pd.DataFrame) -> ModelResult: ...
    # Formula: chosen ~ delta_aifs + delta_length + delta_aifs_x_split, groups=cluster_id

def fit_extended_model(df_pairs: pd.DataFrame) -> ModelResult: ...
    # Adds supply_prop covariate per cluster (supply control)

def fit_perplexity_model(df_pairs: pd.DataFrame) -> ModelResult: ...
    # Adds delta_perplexity (token length proxy) covariate

def compute_supply_prop(df_pairs: pd.DataFrame) -> pd.DataFrame: ...
    # Returns df_pairs with supply_prop column added per cluster

def verify_mechanism_activated(result: ModelResult,
                                df_pairs: pd.DataFrame) -> tuple[bool, dict]: ...
    # 5 indicators: beta4_fitted, data_variance, split_balanced,
    #               clusters_valid, effect_nonzero
    # Aborts pipeline if any indicator is False
```

---

### Evaluate (`code/evaluate.py`)

**Dependencies:** numpy, scipy, json, statsmodels, experiment

```python
GATE_BETA4_MIN: float = 0.0
GATE_OR_MIN: float = 1.10
GATE_PVAL_MAX: float = 0.01
RESULTS_DIR: str = "h-e1/results"

def compute_metrics(result_baseline: ModelResult,
                    result_proposed: ModelResult) -> dict: ...
    # Returns: {beta4, OR, CI_lo, CI_hi, pval, mcfadden_r2_baseline,
    #           mcfadden_r2_proposed, lrt_stat, lrt_pval}

def check_gate(metrics: dict) -> bool: ...
    # Returns True if β₄>0 AND OR>=1.10 AND pval<0.01 AND CI_lo>1.0

def save_metrics(metrics: dict, gate_passed: bool) -> None: ...
    # Writes h-e1/results/metrics.json

def save_model_summary(result_proposed: ModelResult) -> None: ...
    # Writes h-e1/results/model_summary.txt

def save_pairs_df(df_pairs: pd.DataFrame) -> None: ...
    # Writes h-e1/results/pairs_df.parquet
```

---

### Visualize (`code/visualize.py`)

**Dependencies:** matplotlib, pandas, numpy, evaluate

```python
FIGURES_DIR: str = "h-e1/figures"
SENSITIVITY_THRESHOLDS: list[float] = [0.75, 0.80, 0.85, 0.90]

def plot_or_comparison(metrics: dict) -> None: ...
    # Fig 1: Bar chart OR (proposed) vs OR=1.0 (null), 95% CI error bars
    # Saves: figures/fig1_or_comparison.png

def plot_forest(results: dict[str, ModelResult]) -> None: ...
    # Fig 2: β₄ forest plot across model specs (baseline, supply, perplexity)
    # Saves: figures/fig2_forest_plot.png

def plot_aifs_distribution(df_pairs: pd.DataFrame) -> None: ...
    # Fig 3: Violin plot AIFS scores chosen vs rejected by split
    # Saves: figures/fig3_aifs_distribution.png

def plot_cluster_histogram(df_pairs: pd.DataFrame) -> None: ...
    # Fig 4: Histogram of semantic cluster sizes
    # Saves: figures/fig4_cluster_histogram.png

def plot_or_sensitivity(df_base: pd.DataFrame, df_online: pd.DataFrame,
                        thresholds: list[float] = SENSITIVITY_THRESHOLDS) -> None: ...
    # Fig 5: OR estimates across cosine thresholds [0.75, 0.80, 0.85, 0.90]
    # Saves: figures/fig5_or_sensitivity.png
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies:** data_prep, experiment, evaluate, visualize, argparse, logging

```python
def parse_args() -> argparse.Namespace: ...
    # --smoke-test flag: run on 1000 pairs only

def setup_logging(log_path: str = "h-e1/results/experiment.log") -> None: ...
    # Print + file logging with timestamps

def smoke_test(df_pairs: pd.DataFrame) -> None: ...
    # Verifies data loads, model fits on 1000 pairs, metrics non-null

def main() -> None: ...
    # Full pipeline: load → filter → cluster → build_pairs → verify →
    #                fit_models → evaluate → gate_check → visualize → save
```

---

## Data Flow

```
HuggingFace (Anthropic/hh-rlhf)
    ↓ load_hh_rlhf()
(df_base, df_online)  [raw JSONL rows]
    ↓ extract_dialogue() + filter_pairs()
(df_base_clean, df_online_clean)  [prompt, chosen, rejected columns]
    ↓ cluster_prompts()
cluster_ids  [int array, len = total unique prompts]
    ↓ build_pairs_df()
df_pairs  [chosen, delta_aifs, delta_length, delta_aifs_x_split, split, cluster_id]
    ↓ verify_mechanism_activated()
(pass/abort)
    ↓ fit_baseline_model() + fit_proposed_model() + fit_extended_model()
(result_baseline, result_proposed, result_extended)  [ModelResult objects]
    ↓ compute_metrics()
metrics  [dict: beta4, OR, CI_lo, CI_hi, pval, mcfadden_r2, lrt]
    ↓ check_gate()
gate_passed  [bool]
    ↓ save_metrics() + save_model_summary() + save_pairs_df()
h-e1/results/  [metrics.json, model_summary.txt, pairs_df.parquet]
    ↓ plot_or_comparison() + plot_forest() + plot_aifs_distribution()
      + plot_cluster_histogram() + plot_or_sensitivity()
h-e1/figures/  [fig1..fig5 .png]
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Loading & Preprocessing | Implement `data_prep.py`: load HH-RLHF splits, extract dialogue (TRL pattern), filter ≥20 tokens, build combined DataFrame with split labels | 8 | 2+2+2+2 |
| A-2 | AIFS Feature Extraction & Clustering | Implement AIFS regex extraction (4 patterns), normalized scoring, `build_pairs_df()`, sentence-transformer clustering at cosine 0.85, cluster validation | 12 | 3+2+4+3 |
| A-3 | Statistical Model Fitting | Implement `experiment.py`: baseline, proposed, extended, perplexity models via statsmodels ConditionalLogit; mechanism verification (5 indicators) | 13 | 3+3+4+3 |
| A-4 | Evaluation & Gate Check | Implement `evaluate.py`: extract β₄, OR, CI, p-value, McFadden R², LRT, gate logic, save JSON/parquet/txt | 9 | 2+2+3+2 |
| A-5 | Visualization (5 Figures) | Implement `visualize.py`: OR comparison bar, forest plot, AIFS violin, cluster histogram, OR sensitivity across thresholds | 10 | 2+2+3+3 |
| A-6 | Orchestration & Smoke Test | Implement `run_experiment.py`: end-to-end pipeline runner, argparse, timestamped logging, smoke test on 1000 pairs | 7 | 2+1+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-4, A-5], Low(4-8): [A-1, A-6]

### Acceptance Criteria

**A-1:** `load_hh_rlhf()` returns two DataFrames; combined size ~80K rows; split column = {0, 1}; filter removes rows where either response < 20 tokens.

**A-2:** `cluster_prompts()` returns array with ≥ 100 unique cluster IDs; `validate_clusters()` passes; `build_pairs_df()` has `delta_aifs_x_split` column = `delta_aifs * split`.

**A-3:** All 4 models converge without exception; `verify_mechanism_activated()` returns (True, all_true_dict) on valid data; prints β₄ interaction coefficient.

**A-4:** `metrics.json` contains keys: beta4, OR, CI_lo, CI_hi, pval, mcfadden_r2_baseline, mcfadden_r2_proposed, gate_passed; gate logic matches: β₄>0 AND OR≥1.10 AND pval<0.01 AND CI_lo>1.0.

**A-5:** 5 PNG files written to `h-e1/figures/`; no matplotlib errors; OR comparison figure includes error bars.

**A-6:** `python run_experiment.py --smoke-test` completes without error in < 2 minutes; full pipeline run completes in < 60 minutes on CPU.

---

## Dependencies

```
Python >= 3.9
datasets >= 2.0          # HuggingFace HH-RLHF loading
sentence-transformers >= 2.2  # all-MiniLM-L6-v2 semantic clustering
statsmodels >= 0.14      # ConditionalLogit
pandas >= 1.5
numpy >= 1.23
scipy >= 1.9             # CI computation
matplotlib >= 3.6        # All 5 figures
scikit-learn             # cosine_similarity (fallback)
torch (CPU-only acceptable)
```

---

*Generated by Phase 3 Architecture — H-E1 | EXISTENCE | LIGHT tier*
*Archon KB: no domain-specific content found (similarity < 0.53 for all queries)*
*Serena: green-field project — no existing codebase to analyze*
