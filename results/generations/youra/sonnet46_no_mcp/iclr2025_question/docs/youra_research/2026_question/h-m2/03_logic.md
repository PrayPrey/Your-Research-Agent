# Logic: H-M2 — NLI Clustering Aggregation Behavior Analysis

**Date:** 2026-05-11
**Type:** INCREMENTAL on H-M1 + H-E1

Applied: bootstrap-percentile-CI pattern
Applied: priority-loader-with-fallback pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1 + H-E1)
**Status**: API signatures verified from actual code
**Analyzed Path**: `h-m1/code/` and `h-e1/code/`
**Relevant Symbols**:
- `h-e1/code/uq_signals.py`: `load_nli_pipeline(cfg)`, `cluster_by_nli(samples, nli_pipeline, batch_size)`, `_build_nli_pairs(samples)`, `_run_nli_batch(pairs, nli_pipeline, batch_size)`
- `h-m1/code/correlation.py`: `inspect_cluster_distribution(samples_path)` — returns `{cluster_counts, mean_clusters, std_clusters, n_singleton, histogram}`
- `h-m1/code/correlation.py`: `pearson_r_bootstrap_ci(te, se, n_bootstrap, seed)` — uses `np.random.default_rng(seed)` + percentile method

**Key findings**:
- `semantic_entropy.json` stores `{str_id: float}` (entropy scores only, NOT per-example cluster counts) → primary path will fail → fallback to re-clustering is expected
- `inspect_cluster_distribution()` uses unique-string proxy, NOT true NLI clustering → H-M2 fallback must use `cluster_by_nli()` for correct cluster counts
- `load_nli_pipeline(cfg)` requires `cfg.nli_model_id` — H-M2 config must include this field or pass model_id directly
- `cluster_by_nli()` returns `Dict[int, int]` ({sample_idx: cluster_id}), so `len(set(values))` = cluster count

---

## External Dependencies API

### Verified from `h-e1/code/uq_signals.py` (actual code)

```python
# From: h-e1/code/uq_signals.py
def load_nli_pipeline(cfg: ExperimentConfig):
    """Load deberta-large-mnli pipeline. cfg must have .nli_model_id attr."""
    # device = 0 if cuda available else -1
    # returns transformers pipeline("text-classification", top_k=None)
    ...

def cluster_by_nli(
    samples: List[str],
    nli_pipeline,
    batch_size: int = 16,
) -> Dict[int, int]:
    """Bidirectional NLI clustering. Returns {sample_idx: cluster_id}."""
    # len(set(result.values())) == cluster_count for this example
    ...
```

### Verified from `h-m1/code/correlation.py` (actual code)

```python
# From: h-m1/code/correlation.py
def inspect_cluster_distribution(samples_path: str) -> Dict[str, Any]:
    """Unique-string proxy (NOT true NLI). Returns {cluster_counts: List[int], mean_clusters, std_clusters, n_singleton, histogram}."""
    # cluster_counts is Python List[int], NOT np.ndarray
    ...

def pearson_r_bootstrap_ci(
    te: np.ndarray,
    se: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> Dict[str, Any]:
    """Uses np.random.default_rng(seed), percentile [2.5, 97.5]. Returns {r_obs, ci_lower, ci_upper, r_boot, gate_pass}."""
    ...
```

---

## A-3: Data Loader — Fallback NLI Re-clustering [Complexity: 14, Budget: 3 subtasks]

Applied: sys-path-injection pattern

### API Signatures

```python
# code/data_loader.py

import sys
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from config import ExperimentConfig


def load_stochastic_samples(path: str) -> List[Dict[str, Any]]:
    """Load stochastic_samples.jsonl. Returns list of {id, samples: List[str]}."""
    # path: str pointing to stochastic_samples.jsonl
    # returns: List[Dict] each with keys "id" (int) and "samples" (List[str], len=5)
    # raises: FileNotFoundError if path missing
    ...


def _get_nli_pipeline_for_recluster(cfg: ExperimentConfig):
    """Inject h-e1/code to sys.path, load NLI pipeline. Returns pipeline object."""
    # sys.path.insert(0, cfg.h_e1_code_dir) then import load_nli_pipeline
    # creates a minimal cfg-like object with nli_model_id if cfg lacks it
    # returns: transformers pipeline (text-classification, top_k=None)
    ...


def _cluster_count_for_example(
    samples: List[str],
    nli_pipeline,
    batch_size: int = 16,
) -> int:
    """Run cluster_by_nli, return len(set(cluster_ids.values())). Range [1, 5]."""
    # imports cluster_by_nli from uq_signals (after sys.path injection)
    # returns: int in [1, 5]
    ...


def load_cluster_counts_from_stochastic_samples(
    samples_path: str,
    nli_pipeline,
    cfg: ExperimentConfig,
) -> np.ndarray:
    """Fallback: re-run NLI clustering on stochastic_samples.jsonl.
    Returns shape (2000,) int array, values in [1, 5]."""
    # 1. load_stochastic_samples(samples_path) → records
    # 2. sort by record["id"]
    # 3. for each record: count = _cluster_count_for_example(record["samples"], nli_pipeline)
    # 4. tqdm progress bar
    # returns: np.array(counts, dtype=int)  # shape (2000,)
    ...
```

### Tensor Shapes

| Variable | Shape | Dtype | Note |
|----------|-------|-------|------|
| stochastic samples (per example) | `[5]` List[str] | str | 5 samples |
| cluster_ids dict | `{0..4: 0..4}` | int | from cluster_by_nli |
| cluster_count (per example) | scalar | int | `len(set(values))` |
| output array | `(2000,)` | int | all examples |

### Pseudo-code

```
load_cluster_counts_from_stochastic_samples(samples_path, nli_pipeline, cfg):
  records = load_stochastic_samples(samples_path)   # 2000 dicts
  records = sorted(records, key=lambda r: r["id"])
  counts = []
  for record in tqdm(records, desc="NLI re-clustering"):
      samples = record["samples"][:cfg.n_samples_per_example]
      cluster_ids = cluster_by_nli(samples, nli_pipeline, batch_size=16)
      counts.append(len(set(cluster_ids.values())))
  return np.array(counts, dtype=int)  # (2000,)
```

### Subtasks

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | `load_stochastic_samples` + `_get_nli_pipeline_for_recluster` | File loader + sys.path injection + pipeline load |
| L-3-2 | `_cluster_count_for_example` + NLI batch helper wiring | Per-example NLI call, cluster count extraction |
| L-3-3 | `load_cluster_counts_from_stochastic_samples` orchestration | Full loop with tqdm, sort by id, return ndarray |

---

## A-4: Aggregation Rate + Bootstrap CI [Complexity: 10, Budget: 2 subtasks]

Applied: bootstrap-percentile-CI pattern

### API Signatures

```python
# code/analysis.py

import numpy as np
from typing import Dict, Any
from config import ExperimentConfig


def compute_aggregation_rate(
    cluster_counts: np.ndarray,
    n_samples: int = 5,
) -> float:
    """Fraction of examples with cluster_count < n_samples.
    cluster_counts: (2000,) int → float in [0.0, 1.0]
    """
    # return float(np.mean(cluster_counts < n_samples))
    ...


def bootstrap_aggregation_ci(
    cluster_counts: np.ndarray,
    n_resamples: int = 1000,
    seed: int = 42,
    n_samples: int = 5,
) -> Dict[str, Any]:
    """Percentile bootstrap 95% CI on aggregation_rate.
    cluster_counts: (2000,) int
    Returns: {aggregation_rate: float, ci_lower: float, ci_upper: float, gate_pass: bool}
    gate_pass = (aggregation_rate >= 0.50) AND (ci_lower >= 0.30)
    """
    ...
```

### Pseudo-code

```
bootstrap_aggregation_ci(cluster_counts, n_resamples=1000, seed=42, n_samples=5):
  N = len(cluster_counts)                          # 2000
  rate_obs = np.mean(cluster_counts < n_samples)  # scalar float

  rng = np.random.default_rng(seed)               # reproducible
  boot_rates = np.empty(n_resamples)
  for i in range(n_resamples):
      idx = rng.integers(0, N, size=N)            # with-replacement
      boot_rates[i] = np.mean(cluster_counts[idx] < n_samples)

  ci_lower, ci_upper = np.percentile(boot_rates, [2.5, 97.5])
  gate_pass = bool(rate_obs >= 0.50 and ci_lower >= 0.30)

  return {
      "aggregation_rate": float(rate_obs),
      "ci_lower": float(ci_lower),
      "ci_upper": float(ci_upper),
      "gate_pass": gate_pass,
  }
```

### Subtasks

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | `compute_aggregation_rate` | Single np.mean call, validated inputs |
| L-4-2 | `bootstrap_aggregation_ci` | Bootstrap loop with default_rng, percentile CI, gate_pass logic |

---

## A-12: End-to-End Integration [Complexity: 9, Budget: 2 subtasks]

### API Signatures

```python
# code/run_experiment.py

import sys
from pathlib import Path
from typing import Dict, Any
from config import ExperimentConfig


def run(cfg: ExperimentConfig) -> Dict[str, Any]:
    """Full H-M2 pipeline. Returns results dict matching experiment_results.json schema."""
    ...


def save_results(results: Dict[str, Any], results_dir: str) -> None:
    """Serialize results to {results_dir}/experiment_results.json."""
    ...


def write_validation_report(results: Dict[str, Any], output_path: str) -> None:
    """Write 04_validation.md with gate decision, metrics, figure references."""
    ...
```

### Results Dict Schema

```python
results: Dict[str, Any] = {
    "hypothesis_id": "h-m2",
    "cluster_count_source": str,           # "se_json" | "hm1_summary" | "nli_recluster"
    "n_examples": int,                     # 2000
    "mean_cluster_count": float,
    "std_cluster_count": float,
    "median_cluster_count": float,
    "histogram": Dict[str, int],           # {"1": int, ..., "5": int}
    "aggregation_rate": float,
    "collapse_rate": float,
    "bootstrap_ci_lower": float,
    "bootstrap_ci_upper": float,
    "gate_pass": bool,
    "gate_result": str,                    # "PASS" | "PARTIAL" | "PIVOT"
    "r_pb": float,
    "p_value": float,
    "stratified_aggregation": Dict[str, float] | None,
    "timestamp": str,                      # ISO 8601
}
```

### Pseudo-code

```
run(cfg):
  # [1/6] Load cluster counts (priority: se_json → hm1_summary → nli_recluster)
  cluster_counts, source = load_cluster_counts(cfg)
  # cluster_counts: (2000,) int

  # [2/6] Load labels
  labels = load_labels(cfg)
  # labels: (2000,) int, values {0, 1}

  # [3/6] Validate
  cluster_counts = validate_cluster_counts(cluster_counts, n=2000)

  # [4/6] Compute statistics
  bootstrap_result = bootstrap_aggregation_ci(
      cluster_counts, cfg.n_bootstrap, cfg.seed, cfg.n_samples_per_example
  )
  dist_stats = compute_distribution_stats(cluster_counts)
  collapse_rate = compute_collapse_rate(cluster_counts)
  corr_result = compute_pointbiserial_correlation(labels, cluster_counts)
  dataset = json.load(open(cfg.dataset_path))
  strat = stratified_aggregation_by_type(cluster_counts, dataset, cfg.n_samples_per_example)

  # [5/6] Gate evaluation
  gate_result = evaluate_gate(bootstrap_result, cfg)
  # "PASS" | "PARTIAL" | "PIVOT"

  # [6/6] Figures
  figures_dir = Path(cfg.figures_dir); figures_dir.mkdir(parents=True, exist_ok=True)
  plot_aggregation_rate(bootstrap_result["aggregation_rate"],
                        bootstrap_result["ci_lower"], bootstrap_result["ci_upper"],
                        cfg.aggregation_gate_threshold,
                        str(figures_dir / "aggregation_rate.png"))
  plot_cluster_count_dist(cluster_counts, str(figures_dir / "cluster_count_dist.png"))
  plot_cluster_count_by_label(cluster_counts, labels, str(figures_dir / "cluster_count_by_label.png"))
  plot_cluster_count_cdf(cluster_counts, threshold=4, str(figures_dir / "cluster_count_cdf.png"))
  if strat: plot_aggregation_by_type(strat, str(figures_dir / "aggregation_by_type.png"))

  results = {
      "hypothesis_id": "h-m2",
      "cluster_count_source": source,
      "n_examples": len(cluster_counts),
      **dist_stats,               # mean, std, median, histogram
      **bootstrap_result,         # aggregation_rate, ci_lower, ci_upper, gate_pass
      "collapse_rate": collapse_rate,
      "bootstrap_ci_lower": bootstrap_result["ci_lower"],
      "bootstrap_ci_upper": bootstrap_result["ci_upper"],
      "r_pb": corr_result["r_pb"],
      "p_value": corr_result["p_value"],
      "gate_result": gate_result,
      "stratified_aggregation": strat,
      "timestamp": datetime.utcnow().isoformat(),
  }
  return results

# Error handling:
# FileNotFoundError from load_cluster_counts → re-raise with clear message
# cluster_counts shape != (2000,) → ValueError in validate_cluster_counts
# All fallback paths exhausted → FileNotFoundError("stochastic_samples.jsonl not found at ...")
```

### Subtasks

| ID | Subtask | Description |
|----|---------|-------------|
| L-12-1 | `run()` orchestration + `load_cluster_counts()` priority loader | Steps 1–5: load, validate, compute all metrics, gate |
| L-12-2 | Figure generation + `save_results()` + `write_validation_report()` | Step 6 + serialization + 04_validation.md |

---

## Subtask Summary

| ID | Task | Subtask | Description |
|----|------|---------|-------------|
| L-3-1 | A-3 | load_stochastic_samples + pipeline load | File loader, sys.path injection, NLI pipeline |
| L-3-2 | A-3 | _cluster_count_for_example | Per-example NLI call, cluster count |
| L-3-3 | A-3 | load_cluster_counts_from_stochastic_samples | Full re-clustering loop, return ndarray |
| L-4-1 | A-4 | compute_aggregation_rate | np.mean(counts < n_samples) |
| L-4-2 | A-4 | bootstrap_aggregation_ci | Bootstrap loop, percentile CI, gate_pass |
| L-12-1 | A-12 | run() + load_cluster_counts priority loader | Orchestration steps 1–5 |
| L-12-2 | A-12 | Figures + save_results + write_validation_report | Step 6, serialization, report |
