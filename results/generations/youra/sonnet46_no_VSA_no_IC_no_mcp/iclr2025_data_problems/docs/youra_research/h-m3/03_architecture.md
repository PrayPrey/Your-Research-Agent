# Architecture: H-M3 — Contamination-Accuracy Correlation Analysis

**Date:** 2026-08-25
**Author:** yoon303@ust.ac.kr
**Hypothesis:** H-M3 (MECHANISM — SHOULD_WORK)

Applied: scipy.stats correlation pipeline pattern (Shi et al. 2023)
Applied: bootstrap resampling CI pattern (standard practice, seed=42)
Applied: model-size aggregation for statistical power (Biderman et al. 2023)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field analysis experiment; no existing codebase to analyze with Serena. All inputs are JSON result files from prior hypotheses.
**Analyzed Path:** N/A
**Findings:** New implementation from scratch. Prior hypotheses (H-E1, H-M1, H-M2) produced only result JSON files; no reusable module code exists.

---

## File Organization

```
docs/youra_research/h-m3/code/
├── analyze.py           # Main pipeline — entry point
├── data_loader.py       # Load + validate H-E1/H-M1/H-M2 JSONs
├── correlation.py       # Pearson/Spearman + bootstrap CI
├── ablations.py         # 4 ablation runners
├── visualize.py         # 5 figures
└── report_generator.py  # Markdown report + gate verdict JSON

docs/youra_research/h-m3/
├── results/
│   ├── correlation_results.json
│   ├── ablation_results.json
│   ├── per_benchmark_summary.json
│   ├── gate_verdict.json
│   └── report.md
└── figures/
    ├── scatter_contamination_vs_differential.png
    ├── correlation_heatmap.png
    ├── per_benchmark_differential.png
    ├── bootstrap_ci.png
    └── spearman_ranks.png
```

---

## Module Structure

### DataLoader (`code/data_loader.py`)

**Dependencies:** json, numpy

```python
BENCHMARKS = ["mmlu", "hellaswag", "arc_challenge", "winogrande"]
MODEL_SIZES = ["160m", "410m", "1b", "6.9b"]

def load_accuracy_differentials(path: str) -> dict[str, dict[str, float]]: ...
    # Returns {model_size: {benchmark: float}}

def load_contamination_estimates(path: str) -> dict[str, float]: ...
    # Returns {benchmark: float}

def load_mink_differentials(path: str) -> dict[str, float] | None: ...
    # Returns {benchmark: float} or None if file missing

def validate_inputs(
    acc_diff: dict,
    cont_est: dict,
    mink_diff: dict | None
) -> None: ...
    # Raises ValueError on missing keys or NaN values

def build_analysis_vectors(
    acc_diff: dict,
    cont_est: dict
) -> tuple[np.ndarray, np.ndarray, np.ndarray]: ...
    # Returns (cont_repeated (16,), diff_flat (16,), diff_matrix (4,4))
```

---

### CorrelationAnalyzer (`code/correlation.py`)

**Dependencies:** numpy, scipy.stats

```python
def pearson_spearman(
    x: np.ndarray,
    y: np.ndarray
) -> dict[str, float]: ...
    # Returns {pearson_r, pearson_p, spearman_rho, spearman_p}

def bootstrap_pearson_ci(
    x: np.ndarray,
    y: np.ndarray,
    n_resamples: int = 1000,
    seed: int = 42
) -> tuple[float, float]: ...
    # Returns (ci_lower, ci_upper) — 95% CI on Pearson r

def directional_check(
    cont_vec: np.ndarray,
    diff_vec: np.ndarray,
    benchmarks: list[str]
) -> dict[str, int]: ...
    # Returns {benchmark: 1 if sign matches contamination prediction, else 0}
    # Expected: high contamination → negative differential

def per_benchmark_summary(
    acc_diff: dict,
    cont_est: dict
) -> list[dict]: ...
    # Returns [{benchmark, contamination, mean_diff, std_diff}, ...]
```

---

### AblationRunner (`code/ablations.py`)

**Dependencies:** correlation.py, numpy

```python
def ablation_estimator_comparison(
    cont_13gram: np.ndarray,
    mink_diff: dict | None,
    diff_flat: np.ndarray
) -> dict: ...
    # Ablation 1: Pearson with 13-gram vs min-k% as predictor
    # Returns {r_13gram, r_mink, delta, flag_disagreement}

def ablation_aggregation_strategy(
    cont_vec: np.ndarray,
    diff_matrix: np.ndarray
) -> dict: ...
    # Ablation 2: n=16 flattened vs n=4 benchmark-level
    # Returns {r_n16, p_n16, r_n4, p_n4}

def ablation_token_vs_step(
    acc_diff_token: dict,
    acc_diff_step: dict | None,
    cont_est: dict
) -> dict: ...
    # Ablation 3: token-count vs step matching
    # Returns {r_token, r_step} or notes step data unavailable

def ablation_per_model_size(
    cont_vec: np.ndarray,
    diff_matrix: np.ndarray
) -> dict[str, dict]: ...
    # Ablation 4: Pearson per model size (n=4 each)
    # Returns {model_size: {pearson_r, pearson_p}}
```

---

### Visualizer (`code/visualize.py`)

**Dependencies:** matplotlib, seaborn, numpy

```python
def scatter_contamination_vs_differential(
    cont_est: dict,
    per_benchmark_summary: list[dict],
    pearson_r: float,
    pearson_p: float,
    out_path: str
) -> None: ...

def correlation_heatmap(
    ablation_results: dict,
    out_path: str
) -> None: ...
    # 2 estimators × 4 model sizes

def per_benchmark_bar_chart(
    acc_diff: dict,
    cont_est: dict,
    out_path: str
) -> None: ...

def bootstrap_ci_plot(
    bootstrap_rs: np.ndarray,
    ci: tuple[float, float],
    out_path: str
) -> None: ...

def spearman_rank_plot(
    cont_est: dict,
    per_benchmark_summary: list[dict],
    spearman_rho: float,
    out_path: str
) -> None: ...
```

---

### ReportGenerator (`code/report_generator.py`)

**Dependencies:** json, pathlib

```python
def determine_gate_verdict(
    pearson_r: float,
    pearson_p: float,
    spearman_rho: float,
    spearman_p: float,
    n_correct_direction: int
) -> dict: ...
    # Returns {gate_type, primary_pass, spearman_pass, directional_pass, overall_verdict, notes}

def save_correlation_results(results: dict, out_path: str) -> None: ...
def save_ablation_results(results: dict, out_path: str) -> None: ...
def save_per_benchmark_summary(summary: list[dict], out_path: str) -> None: ...
def save_gate_verdict(verdict: dict, out_path: str) -> None: ...
def generate_markdown_report(
    correlation: dict,
    ablations: dict,
    verdict: dict,
    figures_dir: str,
    out_path: str
) -> None: ...
```

---

### Main Pipeline (`code/analyze.py`)

**Dependencies:** all modules above, pathlib

```python
BASE_DIR = Path("docs/youra_research")
H_E1_ACC_DIFF = BASE_DIR / "h-e1/results/accuracy_differentials.json"
H_M1_CONT_EST = BASE_DIR / "h-m1/results/contamination_estimates.json"
H_M2_MINK     = BASE_DIR / "h-m2/results/mink_differentials.json"
OUT_RESULTS    = BASE_DIR / "h-m3/results"
OUT_FIGURES    = BASE_DIR / "h-m3/figures"

def run_pipeline() -> None: ...
    # Orchestrates: load → validate → build vectors → correlate →
    # bootstrap → ablations → visualize → serialize → report

if __name__ == "__main__":
    run_pipeline()
```

---

## External Dependencies (Prior Hypothesis Result Files)

| File | Path | Required |
|------|------|----------|
| H-E1 accuracy differentials | `docs/youra_research/h-e1/results/accuracy_differentials.json` | MUST EXIST |
| H-M1 contamination estimates | `docs/youra_research/h-m1/results/contamination_estimates.json` | MUST EXIST |
| H-M2 min-k% differentials | `docs/youra_research/h-m2/results/mink_differentials.json` | OPTIONAL |

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Loading & Validation | Implement data_loader.py: load 3 JSONs, validate schema + values, build 16-obs vectors | 7 | 2+1+2+2 |
| A-2 | Primary Correlation Analysis | Implement correlation.py: Pearson, Spearman, bootstrap CI (seed=42), directional check | 10 | 2+1+4+3 |
| A-3 | Ablation Studies | Implement ablations.py: 4 ablations (estimator, aggregation, token/step, per-size) | 11 | 3+2+3+3 |
| A-4 | Visualization | Implement visualize.py: 5 figures with annotations, regression lines, colormaps | 12 | 3+2+4+3 |
| A-5 | Results Serialization & Report | Implement report_generator.py: JSON outputs, gate verdict logic, markdown report | 9 | 2+2+2+3 |
| A-6 | Main Pipeline & Integration | Implement analyze.py: orchestrate all modules, error handling, graceful H-M2 degradation | 9 | 2+3+2+2 |

**Distribution**: High(10-13): [A-2, A-3, A-4], Medium(7-9): [A-1, A-5, A-6], Low(4-6): []

**Total budget allocation:** 6 epics, estimated 2-3 days CPU-only development, <60s runtime.
