---
hypothesis_id: H-M2
phase: architecture
date: 2026-08-20
author: yoon303b@gmail.com
---

# Architecture: H-M2 — Domain Exposure–Benchmark Correlation Analysis

Applied: pipeline-module pattern (data_loader → evaluator → correlation_analysis → statistical_test → visualization → reporter)

---

## Codebase Analysis (Serena)

**Project Type**: existing_codebase (H-E1 code present, directly reused for exposure data format)
**Status**: H-E1 code found at `docs/youra_research/h-e1/code/`; trajectories.py outputs `np.ndarray` shape `(22, 154)` per model size (domains × checkpoints), dtype float64
**Analyzed Path**: `docs/youra_research/h-e1/code/src/compute/trajectories.py`
**Findings**: H-E1 `compute_domain_exposure_trajectories()` returns `(22, 154)` float64 arrays. H-M2 data_loader reads these saved outputs (transposed to `(154, 22)` for checkpoint-first indexing). No H-E1 modules imported at runtime — file-based reuse only.

---

## File Structure

```
docs/youra_research/h-m2/code/
├── src/
│   ├── __init__.py
│   ├── data_loader.py         # Load H-E1 exposure arrays + align checkpoint indices
│   ├── evaluator.py           # lm-eval-harness batch runner, resume-capable
│   ├── correlation_analysis.py # Spearman rho + floor filtering
│   ├── statistical_test.py    # Fisher z-test + Holm-Bonferroni + gate check
│   ├── visualization.py       # 5 required figures
│   └── reporter.py            # JSON/MD output generation
├── config.py                  # All constants
├── run_experiment.py          # CLI entrypoint
results/h-m2/
├── eval_cache/{model_size}/step{N}.json
├── correlation_matrix.json
├── gate_summary.json
├── fisher_tests.json
└── decontamination_report.json
docs/youra_research/h-m2/figures/   # fig1–fig5 PNGs
```

---

## Modules

### Config (`config.py`)

**Dependencies**: stdlib only

```python
MODEL_SIZES: list[str] = ["70m", "1b", "6.9b"]
MODEL_IDS: dict[str, str] = {
    "70m": "EleutherAI/pythia-70m",
    "1b": "EleutherAI/pythia-1b",
    "6.9b": "EleutherAI/pythia-6.9b",
}
CHECKPOINT_STEPS: list[int]  # [0,1,2,4,8,...,143000], len=154
PILE_DOMAINS: list[str]       # 22 domain names from H-E1
FOCAL_DOMAINS: dict[str, str] = {
    "wikipedia": "Wikipedia (en)",
    "books": "Books3",
}
TASKS: dict[str, dict] = {
    "mmlu": {"num_fewshot": 5, "metric": "acc,none"},
    "hellaswag": {"num_fewshot": 10, "metric": "acc_norm,none"},
}
FLOOR_THRESHOLD: float = 0.30
FISHER_ALPHA: float = 0.10
SEED: int = 42
EVAL_CACHE_DIR: str = "results/h-m2/eval_cache"
RESULTS_DIR: str = "results/h-m2"
FIGURES_DIR: str = "docs/youra_research/h-m2/figures"
H_E1_EXPOSURE_DIR: str = "docs/youra_research/h-e1"
```

---

### DataLoader (`src/data_loader.py`)

**Dependencies**: config, numpy

```python
def load_exposure_arrays(model_size: str) -> np.ndarray:
    """Load H-E1 output for one model size.
    Returns shape (154, 22) — checkpoints × domains, float64."""
    ...

def align_checkpoint_indices(
    exposure: np.ndarray,
    eval_steps: list[int],
    reference_steps: list[int] = CHECKPOINT_STEPS,
) -> np.ndarray:
    """Reindex exposure to match eval result steps. Returns (T, 22)."""
    ...

def verify_coverage(exposure: np.ndarray, model_size: str) -> None:
    """Assert shape (154, 22), all finite, domain names match PILE_DOMAINS. Raise on mismatch."""
    ...

def filter_floor(
    exposure: np.ndarray,
    scores: dict[str, np.ndarray],
    threshold: float = FLOOR_THRESHOLD,
) -> tuple[np.ndarray, dict[str, np.ndarray], np.ndarray]:
    """Apply floor mask on all benchmarks simultaneously.
    Returns (exposure_filtered, scores_filtered, valid_mask). Raises if N_valid < 100."""
    ...
```

---

### Evaluator (`src/evaluator.py`)

**Dependencies**: config, lm_eval, json, pathlib, logging

```python
def is_cached(model_size: str, step: int) -> bool:
    """True if cache file exists and is valid JSON."""
    ...

def evaluate_checkpoint(
    model_size: str,
    step: int,
    tasks: list[str] = list(TASKS.keys()),
    device: str = "cuda",
) -> dict:
    """Run lm_eval.simple_evaluate for one (model_size, step). Saves JSON to cache. Skips if cached."""
    ...

def run_batch_evaluation(
    model_size: str,
    steps: list[int] = CHECKPOINT_STEPS,
    device: str = "cuda",
) -> dict[int, dict]:
    """Run evaluate_checkpoint for all steps; returns {step: scores_dict}."""
    ...

def load_scores_array(model_size: str) -> dict[str, np.ndarray]:
    """Load all cached JSONs for model_size; return {"mmlu": (154,), "hellaswag": (154,)}."""
    ...

def load_fallback_scores(model_size: str) -> dict[str, np.ndarray]:
    """Load pre-cached scores from EleutherAI/pythia evals/pythia-v1/ as fallback."""
    ...
```

---

### CorrelationAnalysis (`src/correlation_analysis.py`)

**Dependencies**: config, numpy, scipy.stats, data_loader

```python
def compute_spearman_matrix(
    exposure: np.ndarray,    # (T_valid, 22)
    scores: dict[str, np.ndarray],  # {"mmlu": (T_valid,), "hellaswag": (T_valid,)}
    domain_names: list[str] = PILE_DOMAINS,
) -> dict[tuple[str, str], dict]:
    """Compute rho + p-value + 95% CI for all 22 domains × 2 benchmarks.
    Returns {(domain, benchmark): {"rho": float, "p": float, "ci": [lo, hi]}}."""
    ...

def compute_ci(rho: float, n: int) -> tuple[float, float]:
    """Fisher z-transform 95% CI for Spearman rho."""
    ...

def get_focal_correlations(
    corr_matrix: dict,
    model_size: str,
) -> dict:
    """Extract the 4 focal (domain, benchmark) pairs + n_valid for gate evaluation."""
    ...
```

---

### StatisticalTest (`src/statistical_test.py`)

**Dependencies**: config, numpy, scipy.stats

```python
def fisher_z_test(rho1: float, rho2: float, n: int) -> tuple[float, float]:
    """One-tailed Fisher z-test. H1: rho1 > rho2. Returns (z_stat, p_one_tailed)."""
    ...

def holm_bonferroni(p_values: list[float], alpha: float = FISHER_ALPHA) -> list[bool]:
    """Holm-Bonferroni correction. Returns list of reject-null booleans."""
    ...

def verify_mechanism_activated(
    results_by_model_size: dict[str, dict],
) -> tuple[bool, dict]:
    """Per spec in 02c_experiment_brief.md. Returns (mechanism_activated, indicators)."""
    ...

def run_all_tests(
    focal_by_model: dict[str, dict],
) -> dict:
    """Run P1 + P2 Fisher z-tests for all 3 model sizes, apply Holm-Bonferroni.
    Returns full test results dict for fisher_tests.json."""
    ...
```

---

### Visualization (`src/visualization.py`)

**Dependencies**: config, matplotlib, seaborn, numpy

```python
def fig1_gate_metrics_bar(
    focal_by_model: dict[str, dict],
    out_path: str,
) -> None:
    """Bar chart: rho(Wikipedia→MMLU) vs rho(Wikipedia→HellaSwag) × 3 sizes, 95% CIs."""
    ...

def fig2_domain_benchmark_heatmap(
    corr_by_model: dict[str, dict],
    out_path: str,
    top_k: int = 8,
) -> None:
    """3-panel heatmap: top-8 domains × 2 benchmarks per model size."""
    ...

def fig3_trajectories(
    exposure_by_model: dict[str, np.ndarray],
    scores_by_model: dict[str, dict[str, np.ndarray]],
    out_path: str,
) -> None:
    """6 dual-axis line plots: Wikipedia exposure vs MMLU/HellaSwag over 154 checkpoints × 3 sizes."""
    ...

def fig4_fisher_forest(
    test_results: dict,
    out_path: str,
) -> None:
    """Forest plot: P1 and P2 point estimates + 95% CIs per model size."""
    ...

def fig5_floor_filter_diagnostic(
    valid_masks: dict[str, np.ndarray],
    steps: list[int],
    out_path: str,
) -> None:
    """Show filtered vs kept checkpoints per model size, N_valid annotation."""
    ...
```

---

### Reporter (`src/reporter.py`)

**Dependencies**: config, json, pathlib

```python
def save_correlation_matrix(
    corr_by_model: dict[str, dict],
    out_path: str,
) -> None:
    """Serialize all 132 rho values + CIs + p-values to JSON."""
    ...

def save_gate_summary(
    mechanism_activated: bool,
    indicators: dict,
    out_path: str,
) -> None:
    """Serialize gate evaluation result to JSON."""
    ...

def save_fisher_tests(test_results: dict, out_path: str) -> None: ...

def save_decontamination_report(report: dict, out_path: str) -> None: ...

def write_results_summary(
    indicators: dict,
    corr_by_model: dict,
    test_results: dict,
    out_path: str,
) -> None:
    """Write docs/youra_research/h-m2/04_results_summary.md."""
    ...
```

---

### RunExperiment (`run_experiment.py`)

**Dependencies**: all src modules, argparse, logging

```python
def main(model_sizes: list[str], device: str, skip_eval: bool) -> None:
    """
    Pipeline:
    1. run_batch_evaluation (per model size, resume-capable)
    2. load_exposure_arrays + verify_coverage
    3. filter_floor → valid_mask
    4. compute_spearman_matrix
    5. run_all_tests + verify_mechanism_activated
    6. fig1–fig5 generation
    7. save all JSON outputs + write_results_summary
    """
    ...

if __name__ == "__main__":
    # argparse: --model-sizes, --device, --skip-eval
    ...
```

---

## External Dependencies (Base Hypothesis)

### H-E1 Output Format (From Actual Code)

| Data | Format | Source Path |
|------|--------|-------------|
| Domain exposure trajectories | `.npy` or structured JSON, shape `(22, 154)` per model size | `docs/youra_research/h-e1/` |
| Pile domain names (22) | `PILE_DOMAINS` list in H-E1 config | `docs/youra_research/h-e1/code/src/data/loader.py` |

**Verified from**: `docs/youra_research/h-e1/code/src/compute/trajectories.py` — `compute_domain_exposure_trajectories()` returns `(n_domains, n_checkpoints)` float64; H-M2 loads and transposes to `(154, 22)`.

Note: H-M2 reads H-E1 output as files only — no runtime imports from H-E1 code.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | File structure, config.py, requirements.txt, checkpoint step list | 5 | 1+1+1+2 |
| A-2 | Data Loader | Load H-E1 exposure arrays, verify shape/domain coverage, floor filter | 8 | 2+2+2+2 |
| A-3 | Checkpoint Evaluator | lm-eval-harness batch runner with resume capability + fallback loader | 14 | 3+3+4+4 |
| A-4 | Decontamination Audit | 13-gram overlap check MMLU/HellaSwag vs Pile training docs | 13 | 3+3+4+3 |
| A-5 | Correlation Analysis | Spearman rho matrix (132 pairs) + 95% CIs + focal extraction | 10 | 3+2+3+2 |
| A-6 | Statistical Tests | Fisher z-test, Holm-Bonferroni, verify_mechanism_activated gate | 9 | 2+2+3+2 |
| A-7 | Visualization | fig1–fig5 (bar, heatmap, trajectories, forest, floor diagnostic) | 11 | 3+2+3+3 |
| A-8 | Reporter | JSON serialization + 04_results_summary.md generation | 6 | 2+1+1+2 |
| A-9 | Integration + Run | Wire pipeline in run_experiment.py, end-to-end test with mock data | 9 | 2+3+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3], Medium(9-13): [A-4, A-5, A-6, A-7, A-9], Low(4-8): [A-1, A-2, A-8]
