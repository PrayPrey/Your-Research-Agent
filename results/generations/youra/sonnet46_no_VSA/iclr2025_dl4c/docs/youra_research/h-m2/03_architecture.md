# Architecture: H-M2
# Spearman Correlation — Embedding Alignment vs Pass@1 Rank

Applied: scipy-permutation-test pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (reading H-E1 + H-E2 outputs)
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-e1/code/`, `docs/youra_research/h-e2/code/`
**Findings**:
- H-E1 outputs `experiment_results.json` (NOT `.npy` files). Similarity matrices live under `sim_matrices.codebert` and `sim_matrices.minilm` as nested lists, shape (4,2). Source order: `["humaneval_train","mbpp_train","leetcode","equal_mix"]`. Benchmark order: `["humaneval_plus","mbpp_plus"]`.
- H-E2 outputs `results/all_results.csv` with columns `[condition, seed, benchmark, pass1, n_problems]`. Only `humaneval` benchmark rows exist (no `mbpp_plus` eval results). No `pass_at_1_1b.json` file exists.
- H-C1 optional 7B data: not present, skip gracefully.

**Critical data reality vs PRD spec**:
- PRD assumed `.npy` files at `h-e1/results/similarity_matrix_*.npy` — DOES NOT EXIST
- PRD assumed `h-e2/results/pass_at_1_1b.json` — DOES NOT EXIST
- Actual paths: `h-e1/experiment_results.json` and `h-e2/results/all_results.csv`
- Only `humaneval` benchmark available in H-E2 (not `mbpp_plus`) — analysis will be 1 benchmark × 2 encoders = 2 required cells (C1, C3); mbpp cells marked CANNOT_TEST

---

## File Structure

```
docs/youra_research/h-m2/
  code/
    data_loader.py      # load H-E1 sim matrices + H-E2 pass@1
    analysis.py         # Spearman permutation test + bootstrap CI + Kendall tau
    visualize.py        # 5 figures
    run_experiment.py   # main entry point
  results/              # created at runtime
  figures/              # created at runtime
```

---

## Module Definitions

### DataLoader (`code/data_loader.py`)

**Dependencies**: numpy, json, pandas, pathlib

```python
# Constants
H_E1_RESULTS = "docs/youra_research/h-e1/experiment_results.json"
H_E2_CSV     = "docs/youra_research/h-e2/results/all_results.csv"
H_C1_JSON    = "docs/youra_research/h-c1/results/pass_at_1_7b.json"  # optional

SOURCES     = ["humaneval_train", "mbpp_train", "leetcode", "equal_mix"]
BENCHMARKS  = ["humaneval_plus", "mbpp_plus"]
CONDITIONS  = ["humaneval_only", "mbpp_only", "leetcode_only", "equal_mix"]
# SOURCES[i] maps to CONDITIONS[i] for cross-dataset alignment

def load_sim_matrices() -> dict:
    """Returns {"codebert": np.ndarray(4,2), "minilm": np.ndarray(4,2)}.
    Reads from H_E1_RESULTS['sim_matrices']. Validates shape==(4,2), no NaN."""
    ...

def load_pass_at_1_1b() -> np.ndarray:
    """Returns ndarray shape (4, 2): [condition × benchmark].
    Reads H_E2_CSV, averages pass1 across seeds per (condition, benchmark).
    Benchmark dim 0=humaneval, dim 1=mbpp_plus (NaN if unavailable).
    Condition order matches CONDITIONS list."""
    ...

def load_pass_at_1_7b() -> np.ndarray | None:
    """Returns ndarray shape (4, 2) or None if H-C1 not available."""
    ...

def validate_inputs(sim: dict, pass_mat: np.ndarray) -> None:
    """Asserts shapes, no NaN in sim, logs available vs CANNOT_TEST cells."""
    ...
```

### Analysis (`code/analysis.py`)

**Dependencies**: numpy, scipy.stats

```python
def run_permutation_test(
    sim_vec: np.ndarray,   # shape (4,)
    pass_vec: np.ndarray,  # shape (4,)
    n_resamples: int = 10000,
    seed: int = 42,
) -> dict:
    """Returns {rho, pvalue, significant, null_distribution, can_test}."""
    ...

def bootstrap_ci(
    sim_vec: np.ndarray,
    pass_vec: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> tuple[float, float]:
    """Returns (ci_lo, ci_hi) 95% CI for Spearman rho."""
    ...

def kendall_tau(sim_vec: np.ndarray, pass_vec: np.ndarray) -> tuple[float, float]:
    """Returns (tau, pvalue) one-sided greater."""
    ...

def run_all_cells(
    sim_matrices: dict,
    pass_matrices: dict,   # {"1b": ndarray(4,2), "7b": ndarray(4,2)|None}
) -> list[dict]:
    """Iterates (benchmark × encoder × model_size), calls run_permutation_test.
    Marks cells CANNOT_TEST if pass_vec has no rank variation or all NaN."""
    ...

def evaluate_gate(cell_results: list[dict]) -> dict:
    """Returns {gate_status, supporting_cells, concordant_benchmarks}."""
    ...
```

### Visualize (`code/visualize.py`)

**Dependencies**: matplotlib, seaborn, numpy

```python
FIGURES_DIR = "docs/youra_research/h-m2/figures"

def fig1_rho_bar_chart(cell_results: list[dict]) -> None:
    """Bar chart of rho per cell, * for p<0.05. Saves fig1_rho_bar_chart.png."""
    ...

def fig2_scatter_panels(
    sim_matrices: dict,
    pass_matrices: dict,
    cell_results: list[dict],
) -> None:
    """Scatter embedding rank vs pass@1 rank, one panel per cell. Saves fig2_scatter_panels.png."""
    ...

def fig3_null_distribution(cell_results: list[dict]) -> None:
    """Null rho histogram for most significant cell, observed rho marked. Saves fig3_null_distribution.png."""
    ...

def fig4_rank_heatmap(
    sim_matrices: dict,
    pass_matrices: dict,
) -> None:
    """Heatmap of condition rankings (embedding vs performance). Saves fig4_rank_heatmap.png."""
    ...

def fig5_dual_encoder(cell_results: list[dict]) -> None:
    """Scatter CodeBERT rho vs MiniLM rho per benchmark. Saves fig5_dual_encoder.png."""
    ...

def save_all_figures(sim_matrices: dict, pass_matrices: dict, cell_results: list[dict]) -> None:
    """Calls all fig* functions after creating FIGURES_DIR."""
    ...
```

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: DataLoader, Analysis, Visualize, json, csv, pathlib, logging

```python
RESULTS_DIR = "docs/youra_research/h-m2/results"

def save_results(cell_results: list[dict], gate: dict) -> None:
    """Writes correlation_results.json, rank_comparison_table.csv,
    gate_evaluation.json, null_distributions/cell_*.npy."""
    ...

def main() -> None:
    """Entry point. Load → validate → analyze → save → visualize."""
    ...
```

---

## External Dependencies (Base Hypothesis)

| Input | Actual Path | Format | Notes |
|-------|-------------|--------|-------|
| H-E1 sim matrices | `docs/youra_research/h-e1/experiment_results.json` | JSON, `sim_matrices.{encoder}` list(4×list(2)) | NOT .npy |
| H-E2 pass@1 | `docs/youra_research/h-e2/results/all_results.csv` | CSV: condition,seed,benchmark,pass1 | Only humaneval rows present; mbpp cells → CANNOT_TEST |
| H-C1 pass@1 (opt) | `docs/youra_research/h-c1/results/pass_at_1_7b.json` | JSON | Skip gracefully if absent |

**Verified from**: `h-e1/experiment_results.json` and `h-e2/results/all_results.csv` (actual data files)

**Source-to-condition name mapping** (verified from H-E1 `sources` key and H-E2 CSV `condition` values):

| Row index | H-E1 source key | H-E2 condition value |
|-----------|-----------------|----------------------|
| 0 | `humaneval_train` | `humaneval_only` |
| 1 | `mbpp_train` | `mbpp_only` |
| 2 | `leetcode` | `leetcode_only` |
| 3 | `equal_mix` | `equal_mix` |

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Create dirs, confirm scipy version, verify input files exist | 5 | 1+1+1+2 |
| A-2 | Data Loader | Load H-E1 JSON sim matrices + H-E2 CSV pass@1, align condition ordering, validate | 9 | 2+2+3+2 |
| A-3 | Statistical Analysis | Spearman permutation test + bootstrap CI + Kendall tau across all cells | 11 | 3+2+4+2 |
| A-4 | Gate Evaluation | Evaluate SATISFIED/FALSIFIED/CANNOT_TEST, dual-encoder concordance check | 7 | 2+2+2+1 |
| A-5 | Results Persistence | Save JSON/CSV/npy outputs to results dir | 6 | 2+1+1+2 |
| A-6 | Visualization | 5 figures (bar chart, scatter panels, null dist, rank heatmap, dual-encoder) | 10 | 3+2+2+3 |
| A-7 | Main Entrypoint | Wire all modules, logging per-cell format, run end-to-end | 7 | 2+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-6], Low(4-8): [A-1, A-2, A-4, A-5, A-7]

---

## Implementation Notes for Phase 4

- **No `.npy` sim files exist**: read from `h-e1/experiment_results.json["sim_matrices"]` and convert with `np.array(..., dtype=np.float32)`
- **No aggregated pass@1 JSON**: compute from `all_results.csv` via `df.groupby(["condition","benchmark"])["pass1"].mean()`
- **Only humaneval benchmark has H-E2 data**: mbpp_plus cells must be marked `CANNOT_TEST` automatically; do not hard-fail
- **Condition row alignment**: use explicit index mapping table above — do not rely on sort order
- **Permutation test scipy note**: `permutation_type='pairings'` with `n_resamples=10000`, `alternative='greater'`, `random_state=42`
- **Tie fallback**: if `spearmanr` returns NaN, use `kendalltau(..., alternative='greater')` as primary for that cell
