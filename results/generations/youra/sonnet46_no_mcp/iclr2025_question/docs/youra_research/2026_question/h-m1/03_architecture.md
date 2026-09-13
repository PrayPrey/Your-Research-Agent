# Architecture: H-M1
## Token Entropy vs. Semantic Entropy Divergence Analysis

**Hypothesis:** H-M1 (MECHANISM — Causal Step 1)
**Date:** 2026-05-11
**Type:** INCREMENTAL on H-E1

Applied: correlation-analysis-on-precomputed-signals

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code
**Analyzed Path**: `h-e1/code/`
**Findings**: Flat single-directory structure. Key files: `data.py` (load_dataset_from_disk, load_halueval_qa), `evaluate.py` (compute_auroc, bootstrap_auroc_ci, save_results), `visualize.py` (matplotlib plots). No subdirectory modules. All imports are direct (`from data import ...`, `from evaluate import ...`).

---

## File Organization

```
h-m1/
  code/
    run_experiment.py       # Main entry point — orchestrates all analysis steps
    correlation.py          # Pearson r, Spearman rho, bootstrap CI
    divergence.py           # Pointwise divergence, high-divergence detection, TTR
    visualize.py            # All figure generation (5 plots)
    config.py               # ExperimentConfig dataclass
    outputs/
      experiment_results.json
    figures/
      scatter_te_vs_se.png
      cluster_count_dist.png
      divergence_dist.png
      ttr_vs_divergence.png
      bootstrap_ci.png
  04_validation.md          # Gate evaluation report
```

---

## Module Structure

### Config (`code/config.py`)

**Dependencies**: none

```python
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    seed: int = 42
    n_bootstrap: int = 1000
    pearson_gate_threshold: float = 0.9
    degenerate_threshold: float = 1e-6
    divergence_sigma_multiplier: float = 1.0
    # Paths to H-E1 outputs (relative to h-m1/code/)
    te_scores_path: str = "../../h-e1/code/outputs/uq_scores/token_entropy_mean.json"
    se_scores_path: str = "../../h-e1/code/outputs/uq_scores/semantic_entropy.json"
    stochastic_samples_path: str = "../../h-e1/code/outputs/stochastic_samples.jsonl"
    dataset_path: str = "../../h-e1/code/data/halueval_qa_2k.json"
    results_dir: str = "outputs"
    figures_dir: str = "../figures"
```

---

### Correlation (`code/correlation.py`)

**Dependencies**: config.py

```python
import numpy as np
from typing import Tuple, Dict, Any

def load_uq_scores(te_path: str, se_path: str) -> Tuple[np.ndarray, np.ndarray]:
    """Load token_entropy_mean.json and semantic_entropy.json. Asserts len==2000."""
    ...

def check_degenerate(se: np.ndarray, threshold: float = 1e-6) -> bool:
    """Return True if std(se) < threshold (constant semantic entropy)."""
    ...

def pearson_r_bootstrap_ci(
    te: np.ndarray,
    se: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Returns: {r_obs, ci_lower, ci_upper, r_boot (list), gate_pass}
    gate_pass = (ci_upper < 0.9)
    """
    ...

def spearman_rho(te: np.ndarray, se: np.ndarray) -> Tuple[float, float]:
    """Return (rho, p_value) using scipy.stats.spearmanr."""
    ...
```

---

### Divergence (`code/divergence.py`)

**Dependencies**: config.py

```python
import numpy as np
from typing import Dict, Any, List, Tuple

def compute_pointwise_divergence(te: np.ndarray, se: np.ndarray) -> np.ndarray:
    """Return |te - se| per example, shape (2000,)."""
    ...

def identify_high_divergence(
    divergence: np.ndarray,
    sigma_multiplier: float = 1.0,
) -> Tuple[np.ndarray, float]:
    """
    Returns: (high_div_indices, threshold) where threshold = mean + sigma_multiplier * std.
    """
    ...

def load_stochastic_samples(path: str) -> List[Dict]:
    """Load stochastic_samples.jsonl — one JSON object per line."""
    ...

def compute_ttr(samples: List[str]) -> float:
    """Type-Token Ratio: unique_tokens / total_tokens across N samples."""
    ...

def compute_ttr_by_group(
    samples_data: List[Dict],
    high_div_indices: np.ndarray,
) -> Dict[str, float]:
    """
    Returns: {mean_ttr_high_div, mean_ttr_low_div}
    """
    ...
```

---

### Visualize (`code/visualize.py`)

**Dependencies**: correlation.py, divergence.py

```python
import numpy as np
from typing import Dict, Any, List

def plot_scatter_te_vs_se(
    te: np.ndarray,
    se: np.ndarray,
    r_obs: float,
    save_path: str,
) -> None:
    """Scatter plot with identity line (y=x) and Pearson r annotation."""
    ...

def plot_cluster_count_dist(cluster_counts: List[int], save_path: str) -> None:
    """Histogram of NLI cluster counts (1–5) across 2000 examples."""
    ...

def plot_divergence_dist(divergence: np.ndarray, threshold: float, save_path: str) -> None:
    """Histogram/KDE of |TE-SE| with threshold line."""
    ...

def plot_ttr_vs_divergence(
    ttr_values: np.ndarray,
    divergence: np.ndarray,
    high_div_indices: np.ndarray,
    save_path: str,
) -> None:
    """Scatter plot of TTR vs |TE-SE| with high-divergence highlighted."""
    ...

def plot_bootstrap_ci(
    r_boot: List[float],
    r_obs: float,
    ci_lower: float,
    ci_upper: float,
    gate_threshold: float,
    save_path: str,
) -> None:
    """CDF of bootstrap Pearson r distribution with 95% CI bounds and gate threshold."""
    ...
```

---

### Run Experiment (`code/run_experiment.py`)

**Dependencies**: config.py, correlation.py, divergence.py, visualize.py

```python
from config import ExperimentConfig

def run(cfg: ExperimentConfig) -> Dict[str, Any]: ...
def save_results(results: Dict[str, Any], results_dir: str) -> None: ...
def write_validation_report(results: Dict[str, Any], output_path: str) -> None: ...

if __name__ == "__main__":
    cfg = ExperimentConfig()
    results = run(cfg)
    save_results(results, cfg.results_dir)
    write_validation_report(results, "../../04_validation.md")
```

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_dataset_from_disk | `sys.path.insert; from data import load_dataset_from_disk` | `h-e1/code/data.py` |
| load_halueval_qa | `from data import load_halueval_qa` | `h-e1/code/data.py` |
| compute_auroc | `from evaluate import compute_auroc` | `h-e1/code/evaluate.py` |
| bootstrap_auroc_ci | `from evaluate import bootstrap_auroc_ci` | `h-e1/code/evaluate.py` |

**Verified from**: `h-e1/code/` (actual implementation)

**Note**: h-e1 modules use flat imports (`from data import ...`, `from evaluate import ...`) without package prefix. H-M1 must add `h-e1/code/` to sys.path when reusing these, or copy the relevant utility functions inline.

**H-E1 Output Files (data only, no import)**:
| File | Path |
|------|------|
| token_entropy_mean.json | `h-e1/code/outputs/uq_scores/token_entropy_mean.json` |
| semantic_entropy.json | `h-e1/code/outputs/uq_scores/semantic_entropy.json` |
| stochastic_samples.jsonl | `h-e1/code/outputs/stochastic_samples.jsonl` |
| halueval_qa_2k.json | `h-e1/code/data/halueval_qa_2k.json` |

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Environment Setup & H-E1 Output Verification | Create h-m1/code/ structure, verify all H-E1 output files exist and have correct length (2000), install dependencies | 6 | 2+1+1+2 |
| E-2 | Config Module | Implement ExperimentConfig with all paths and hyperparameters | 4 | 1+1+1+1 |
| E-3 | Score Loading & Degenerate Diagnosis | Implement load_uq_scores(), check_degenerate(), cluster count inspection if SE is constant | 9 | 2+2+3+2 |
| E-4 | Pearson r + Bootstrap CI | Implement pearson_r_bootstrap_ci() with Fisher z-transform variant and percentile CI; gate check | 10 | 2+2+4+2 |
| E-5 | Spearman rho + Divergence Analysis | Implement spearman_rho(), compute_pointwise_divergence(), identify_high_divergence() | 8 | 2+2+2+2 |
| E-6 | TTR Lexical Diversity Analysis | Implement load_stochastic_samples(), compute_ttr(), compute_ttr_by_group() for high-divergence examples | 9 | 2+2+3+2 |
| E-7 | AUROC Context Recomputation | Load labels from dataset, reuse h-e1 compute_auroc/bootstrap_auroc_ci for TE and SE context report | 7 | 2+2+2+1 |
| E-8 | Visualization (5 figures) | Implement all 5 plot functions: scatter, cluster_count_dist, divergence_dist, ttr_vs_divergence, bootstrap_ci | 10 | 3+1+3+3 |
| E-9 | Gate Evaluation & Results Serialization | Assemble all metrics into experiment_results.json; evaluate MUST_WORK gate; handle degenerate case | 8 | 2+2+2+2 |
| E-10 | Validation Report (04_validation.md) | Write 04_validation.md with gate decision, metric tables, degenerate case documentation | 7 | 2+1+2+2 |
| E-11 | End-to-End Integration & run_experiment.py | Wire all modules in run() orchestrator; test full pipeline runs < 2 min on CPU | 9 | 2+3+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [E-3, E-4, E-5, E-6, E-8, E-11], Low(4-8): [E-1, E-2, E-7, E-9, E-10]

---

## Data Flow

- H-E1 JSON files (read-only) → `correlation.py:load_uq_scores()` → numpy arrays (2000,)
- `check_degenerate()` → branch: degenerate path uses stochastic_samples.jsonl for cluster count diagnosis
- numpy arrays → `pearson_r_bootstrap_ci()` + `spearman_rho()` → correlation metrics
- numpy arrays → `compute_pointwise_divergence()` → `identify_high_divergence()` → high_div_indices
- high_div_indices + stochastic_samples.jsonl → `compute_ttr_by_group()` → TTR metrics
- labels + UQ scores → h-e1 `compute_auroc()` → AUROC context
- all metrics → `run_experiment.py:save_results()` → `outputs/experiment_results.json`
- all metrics → `write_validation_report()` → `04_validation.md`
- all metrics → `visualize.py` → `figures/*.png`
