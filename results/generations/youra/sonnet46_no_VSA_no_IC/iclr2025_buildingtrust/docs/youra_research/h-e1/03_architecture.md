# Architecture: H-E1
# LLM Trustworthiness Benchmark Data Availability Audit

**Hypothesis:** H-E1 (EXISTENCE / LIGHT tier)
**Date:** 2026-08-20
**Author:** Anonymous

Applied: Standard Python data pipeline pattern — no specific Archon KB match found for this NLP evaluation domain (top similarity 0.43, CV/diffusion content only).

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project — no existing codebase. Serena analysis not applicable.
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. All module interfaces designed from PRD and experiment brief specs.

---

## File Organization

```
docs/youra_research/h-e1/
├── code/
│   ├── config.py          # CANONICAL_MAP, constants, source priority
│   ├── ingest.py          # Data loaders for all sources
│   ├── matrix.py          # standardize_model_name(), build_matrix()
│   ├── audit.py           # run_h_e1_audit(), protocol consistency check
│   ├── visualize.py       # All 4 figures
│   └── run_audit.py       # Main pipeline orchestration
├── figures/
│   ├── gate_metrics.png
│   ├── coverage_heatmap.png
│   ├── source_attribution.png
│   └── protocol_consistency.png
└── results/
    ├── matrix.csv
    └── audit_results.json
```

---

## Modules

### Config (`code/config.py`)

**Dependencies**: none

```python
REQUIRED_COLS: list[str]  # ["BBQ-Disambig", "BBQ-Ambig", "GLUE", "AdvGLUE", "ANLI-R1", "ANLI-R3", "MMLU"]
SOURCE_PRIORITY: list[str]  # ["TrustLLM", "DecodingTrust", "GLUE-X", "OOD_NLP", "HF"]
BENCHMARK_PAIRS: list[tuple[str, str]]  # [("BBQ-Disambig","BBQ-Ambig"), ...]
CANONICAL_MAP: dict[str, str]  # raw_name_lower -> canonical_id
FIGURES_DIR: Path
RESULTS_DIR: Path
```

---

### Ingest (`code/ingest.py`)

**Dependencies**: config

```python
def load_trustllm(results_dir: str) -> dict[str, dict[str, float]]:
    # Returns {model_canonical: {"BBQ-Disambig": v, "BBQ-Ambig": v, "ANLI-R1": v, "ANLI-R3": v}}
    ...

def load_glue_x(data_path: str) -> dict[str, dict[str, float]]:
    # Returns {model_canonical: {"GLUE": v, "AdvGLUE": v}}
    ...

def load_hf_leaderboard(parquet_url: str = "hf://datasets/OpenEvals/leaderboard-data/data/train-00000-of-00001.parquet") -> dict[str, dict[str, float]]:
    # Returns {model_canonical: {"MMLU": v}}
    ...

def load_ood_nlp(results_dir: str) -> dict[str, dict[str, float]]:
    # Returns {model_canonical: {"ANLI-R1": v, "ANLI-R3": v}}
    ...

def load_decoding_trust(results_dir: str) -> dict[str, dict[str, float]]:
    # Returns {model_canonical: {"AdvGLUE": v, "BBQ-Disambig": v, "BBQ-Ambig": v}}
    ...
```

---

### Matrix (`code/matrix.py`)

**Dependencies**: config

```python
def standardize_model_name(raw_name: str) -> str:
    # CANONICAL_MAP lookup, case-insensitive strip; returns raw_name if no match; logs unresolved
    ...

def build_matrix(score_dicts: dict[str, dict]) -> tuple[pd.DataFrame, pd.DataFrame]:
    # Returns (matrix_df, attribution_df)
    # matrix_df: model × REQUIRED_COLS, filled by SOURCE_PRIORITY
    # attribution_df: model × REQUIRED_COLS, values = source name that filled cell
    ...
```

---

### Audit (`code/audit.py`)

**Dependencies**: config, matrix

```python
def check_protocol_consistency(score_dicts: dict[str, dict], threshold_pp: float = 5.0) -> list[dict]:
    # Returns list of {model, benchmark, source_a, source_b, delta_pp} where delta > threshold
    ...

def run_h_e1_audit(matrix: pd.DataFrame, attribution: pd.DataFrame, score_dicts: dict) -> dict:
    # Returns:
    #   N_common: int
    #   pair_counts: {"BBQ-Disambig/BBQ-Ambig": int, "GLUE/AdvGLUE": int, "ANLI-R1/ANLI-R3": int}
    #   complete_matrix: pd.DataFrame
    #   gate_passed: bool
    #   protocol_warnings: list[dict]
    #   protocol_consistency: float  # fraction of cross-source pairs within 5pp
    ...
```

---

### Visualize (`code/visualize.py`)

**Dependencies**: config

```python
def plot_gate_metrics(pair_counts: dict[str, int], out_path: Path) -> None:
    # MANDATORY: bar chart N_BBQ/N_GLUE/N_ANLI, dashed line at 10, PASS/FAIL annotations
    ...

def plot_coverage_heatmap(matrix: pd.DataFrame, out_path: Path) -> None:
    # model × 7-benchmark heatmap; score color, white=NaN
    ...

def plot_source_attribution(attribution: pd.DataFrame, out_path: Path) -> None:
    # stacked bar: fraction of cells per source per benchmark column
    ...

def plot_protocol_consistency(score_dicts: dict, warnings: list[dict], out_path: Path) -> None:
    # scatter: source-A score vs source-B score for shared model-benchmark pairs; y=x diagonal
    ...
```

---

### Main Pipeline (`code/run_audit.py`)

**Dependencies**: config, ingest, matrix, audit, visualize

```python
def parse_args() -> argparse.Namespace:
    # --trustllm-dir, --glue-x-dir, --ood-nlp-dir, --decoding-trust-dir
    ...

def main() -> None:
    # 1. Load all sources (with graceful skip if dir not provided)
    # 2. build_matrix(score_dicts)
    # 3. run_h_e1_audit(matrix, attribution, score_dicts)
    # 4. Save matrix.csv, audit_results.json
    # 5. Generate all 4 figures
    # 6. Print gate result: N_common = {n} → PASS/FAIL
    ...

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Config & scaffolding | config.py with CANONICAL_MAP, constants, directory setup | 5 | 1+1+1+2 |
| E-2 | Data ingestion | ingest.py: TrustLLM JSON parser, GLUE-X extractor, HF parquet loader, OOD_NLP + DecodingTrust fallbacks | 14 | 3+3+4+4 |
| E-3 | Name standardization + matrix | matrix.py: standardize_model_name(), build_matrix() with source priority and attribution tracking | 10 | 2+2+3+3 |
| E-4 | H-E1 audit | audit.py: run_h_e1_audit() + protocol consistency check | 8 | 2+2+2+2 |
| E-5 | Visualization | visualize.py: gate_metrics (MANDATORY) + 3 autonomous figures | 9 | 2+2+3+2 |
| E-6 | Pipeline orchestration | run_audit.py: CLI args, graceful source degradation, save outputs, print gate | 6 | 1+2+1+2 |

**Distribution**: High(12-17): [E-2], Medium(7-11): [E-3, E-4, E-5], Low(4-6): [E-1, E-6]

**Total complexity**: 52 across 6 epics (within LIGHT tier budget)

---

## External Dependencies

| Package | Version | Use |
|---------|---------|-----|
| pandas | >=1.3.0 | matrix construction, parquet loading |
| numpy | >=1.21.0 | numeric operations |
| matplotlib | >=3.4.0 | all figures |
| seaborn | >=0.11.0 | heatmap |
| huggingface_hub / datasets | >=0.12.0 / >=2.0.0 | HF leaderboard parquet |
| requests | >=2.26.0 | HTTP fallback |
| scipy | >=1.7.0 | spearmanr (preview for H-M1) |
| pingouin | >=0.5.0 | partial_corr (preview for H-M1) |

No GPU required. Runtime budget: ≤ 3 hours (dominated by repo cloning and JSON extraction).

---

## Data Flow

- `run_audit.py` calls ingest functions → `score_dicts: dict[source_name, dict[model, dict[benchmark, float]]]`
- `build_matrix(score_dicts)` → `(matrix_df, attribution_df)`
- `run_h_e1_audit(matrix_df, attribution_df, score_dicts)` → `audit_result: dict`
- `visualize.*` functions consume `pair_counts`, `matrix_df`, `attribution_df`, `score_dicts` → 4 `.png` files
- `audit_result` serialized to `results/audit_results.json`; `matrix_df` to `results/matrix.csv`
