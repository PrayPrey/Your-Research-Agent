# Logic: H-M1
## Token Entropy vs. Semantic Entropy Divergence Analysis

**Hypothesis:** H-M1 (MECHANISM — Causal Step 1)
**Date:** 2026-05-11
**Type:** INCREMENTAL on H-E1

Applied: bootstrap-ci-percentile-method, correlation-analysis-on-precomputed-signals

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from base code
**Analyzed Path**: `h-e1/code/`
**Relevant Symbols**:
- `compute_auroc(labels: List[int], scores: List[float]) -> float` — evaluate.py
- `bootstrap_auroc_ci(labels, scores, n_resamples=1000, seed=42) -> Tuple[float, float]` — evaluate.py (returns `(lower_95ci, upper_95ci)`)
- `load_dataset_from_disk(path: str) -> List[Dict[str, Any]]` — data.py
- `load_halueval_qa(cfg: ExperimentConfig) -> List[Dict[str, Any]]` — data.py
- `compute_semantic_entropy(samples, nli_pipeline, batch_size=16) -> float` — uq_signals.py
- `compute_all_semantic_entropy(outputs_dir, cfg, nli_pipeline=None) -> Dict[int, float]` — uq_signals.py

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

```python
# From: h-e1/code/evaluate.py (ACTUAL CODE)
def compute_auroc(labels: List[int], scores: List[float]) -> float:
    """Compute AUROC."""
    ...

def bootstrap_auroc_ci(
    labels: List[int],
    scores: List[float],
    n_resamples: int = 1000,
    seed: int = 42,
) -> Tuple[float, float]:
    """Return (lower_95ci, upper_95ci) from bootstrap resampling."""
    ...

# From: h-e1/code/data.py (ACTUAL CODE)
def load_dataset_from_disk(path: str) -> List[Dict[str, Any]]:
    """Load JSON list from disk."""
    ...
```

**Verified from**: `h-e1/code/` (actual implementation)

**Note**: H-M1 must add `h-e1/code/` to `sys.path` before importing these. Parameter `n_resamples` (not `n_bootstrap`) in `bootstrap_auroc_ci`.

---

## E-3: Score Loading & Degenerate Diagnosis [Complexity: 9, Budget: L-3-1]

### API Signatures

```python
# correlation.py
import json
import numpy as np
from typing import Tuple, Dict, Any

def load_uq_scores(te_path: str, se_path: str) -> Tuple[np.ndarray, np.ndarray]:
    """Load TE and SE score JSONs. Returns arrays shape (N,) each, aligned by sorted key order."""
    # te: [N,]  se: [N,]  where N == 2000
    ...

def check_degenerate(se: np.ndarray, threshold: float = 1e-6) -> bool:
    """Return True if std(se) < threshold (constant semantic entropy)."""
    ...

def inspect_cluster_distribution(
    samples_path: str,
    cluster_by_nli_fn,  # callable: (List[str], nli_pipeline) -> Dict[int, int]
    nli_pipeline,
) -> Dict[str, Any]:
    """
    Load stochastic_samples.jsonl, run cluster_by_nli per example,
    return cluster count histogram and summary stats.
    Returns: {cluster_counts: List[int], mean_clusters: float, n_singleton: int}
    """
    ...
```

### Pseudo-code: load_uq_scores

```
1. Load te_path JSON → {str_id: float}
2. Load se_path JSON → {str_id: float}
3. common_ids = sorted(set(te_keys) & set(se_keys), key=int)
4. assert len(common_ids) == 2000
5. te = np.array([te_dict[k] for k in common_ids])  # [2000,]
6. se = np.array([se_dict[k] for k in common_ids])  # [2000,]
7. return te, se
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | load_scores_degenerate | Implement load_uq_scores, check_degenerate, inspect_cluster_distribution |

---

## E-4: Pearson r + Bootstrap CI [Complexity: 10, Budget: L-4-1, L-4-2]

### API Signatures

```python
# correlation.py (continued)
from scipy import stats

def pearson_r_bootstrap_ci(
    te: np.ndarray,
    se: np.ndarray,
    n_bootstrap: int = 1000,
    seed: int = 42,
) -> Dict[str, Any]:
    """
    Pearson r with Fisher z-transform bootstrap 95% CI.
    Returns: {r_obs, ci_lower, ci_upper, r_boot: List[float], gate_pass: bool}
    gate_pass = (ci_upper < 0.9)
    te: [N,]  se: [N,]
    """
    ...

def evaluate_gate(ci_upper: float, threshold: float = 0.9) -> bool:
    """Return True if ci_upper < threshold (TE and SE are NOT interchangeable)."""
    ...

def spearman_rho(te: np.ndarray, se: np.ndarray) -> Tuple[float, float]:
    """Return (rho, p_value) via scipy.stats.spearmanr."""
    ...
```

### Pseudo-code: pearson_r_bootstrap_ci (Fisher z-transform)

```
1. r_obs = pearsonr(te, se)[0]
2. rng = np.random.default_rng(seed)
3. r_boot = []
4. for _ in range(n_bootstrap):
   a. idx = rng.integers(0, N, size=N)
   b. r_i = pearsonr(te[idx], se[idx])[0]
   c. z_i = np.arctanh(np.clip(r_i, -0.9999, 0.9999))  # Fisher z
   d. r_boot.append(z_i)
5. z_obs = np.arctanh(np.clip(r_obs, -0.9999, 0.9999))
6. z_lower, z_upper = np.percentile(r_boot, [2.5, 97.5])
7. ci_lower, ci_upper = np.tanh(z_lower), np.tanh(z_upper)
8. gate_pass = evaluate_gate(ci_upper, threshold=0.9)
9. return {r_obs, ci_lower, ci_upper, r_boot: [np.tanh(z) for z in r_boot], gate_pass}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | pearson_bootstrap | Implement pearson_r_bootstrap_ci with Fisher z-transform |
| L-4-2 | evaluate_gate | Implement evaluate_gate + degenerate gate interpretation |

---

## E-6: TTR Lexical Diversity Analysis [Complexity: 9, Budget: L-6-1]

### API Signatures

```python
# divergence.py
import numpy as np
from typing import Dict, Any, List, Tuple

def compute_pointwise_divergence(te: np.ndarray, se: np.ndarray) -> np.ndarray:
    """Return |te - se| per example. te: [N,]  se: [N,]  -> [N,]"""
    ...

def identify_high_divergence(
    divergence: np.ndarray,
    sigma_multiplier: float = 1.0,
) -> Tuple[np.ndarray, float]:
    """
    threshold = mean(divergence) + sigma_multiplier * std(divergence)
    Returns: (high_div_indices: np.ndarray of int indices, threshold: float)
    """
    ...

def load_stochastic_samples(path: str) -> List[Dict]:
    """Load stochastic_samples.jsonl. Each line: {id: int, samples: List[str]}."""
    ...

def compute_ttr(samples: List[str]) -> float:
    """
    TTR = len(unique_tokens) / len(all_tokens) across concatenated samples.
    Tokenize by whitespace split + lowercase.
    """
    ...

def compute_ttr_by_group(
    samples_data: List[Dict],
    high_div_indices: np.ndarray,
) -> Dict[str, float]:
    """
    Compute mean TTR for high-divergence vs low-divergence groups.
    Returns: {mean_ttr_high_div: float, mean_ttr_low_div: float, n_high: int, n_low: int}
    samples_data: list of {id: int, samples: List[str]}
    """
    ...
```

### Pseudo-code: compute_ttr_by_group

```
1. high_set = set(high_div_indices)
2. ttr_high, ttr_low = [], []
3. for record in samples_data:
   a. ttr = compute_ttr(record["samples"])
   b. if record["id"] in high_set: ttr_high.append(ttr)
   c. else: ttr_low.append(ttr)
4. return {mean_ttr_high_div: mean(ttr_high), mean_ttr_low_div: mean(ttr_low),
           n_high: len(ttr_high), n_low: len(ttr_low)}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | ttr_analysis | Implement compute_ttr, compute_ttr_by_group, load_stochastic_samples |

---

## E-11: End-to-End Integration [Complexity: 9, Budget: L-11-1]

### API Signatures

```python
# run_experiment.py
import json
import sys
from pathlib import Path
from typing import Dict, Any

from config import ExperimentConfig

def run(cfg: ExperimentConfig) -> Dict[str, Any]:
    """Orchestrate full pipeline. Returns complete results dict."""
    ...

def save_results(results: Dict[str, Any], results_dir: str) -> None:
    """Save results to {results_dir}/experiment_results.json."""
    ...

def write_validation_report(results: Dict[str, Any], output_path: str) -> None:
    """Write 04_validation.md gate summary table."""
    ...

if __name__ == "__main__":
    cfg = ExperimentConfig()
    results = run(cfg)
    save_results(results, cfg.results_dir)
    write_validation_report(results, "../../04_validation.md")
```

### Pseudo-code: run() with degenerate branching

```
1. te, se = load_uq_scores(cfg.te_scores_path, cfg.se_scores_path)

2. degenerate = check_degenerate(se, cfg.degenerate_threshold)
3. if degenerate:
   a. cluster_info = inspect_cluster_distribution(cfg.stochastic_samples_path, ...)
   b. results["degenerate"] = True
   c. results["cluster_distribution"] = cluster_info
   d. results["gate_pass"] = False  # degenerate → gate fails by definition
   e. return results early with degenerate report

4. # Normal path
5. pearson_result = pearson_r_bootstrap_ci(te, se, cfg.n_bootstrap, cfg.seed)
6. rho, p_val = spearman_rho(te, se)
7. divergence = compute_pointwise_divergence(te, se)          # [N,]
8. high_div_idx, div_threshold = identify_high_divergence(divergence, cfg.divergence_sigma_multiplier)
9. samples_data = load_stochastic_samples(cfg.stochastic_samples_path)
10. ttr_result = compute_ttr_by_group(samples_data, high_div_idx)

11. # Load labels for AUROC context (reuse h-e1 evaluate.py)
12. sys.path.insert(0, str(Path(cfg.te_scores_path).parents[3] / "code"))
13. from evaluate import compute_auroc, bootstrap_auroc_ci
14. dataset = load_dataset_from_disk(cfg.dataset_path)
15. labels = [int(ex["hallucination_label"]) for ex in dataset]
16. te_auroc = compute_auroc(labels, list(te))
17. se_auroc = compute_auroc(labels, list(se))

18. # Figures
19. plot_scatter_te_vs_se(te, se, pearson_result["r_obs"], ...)
20. plot_bootstrap_ci(pearson_result["r_boot"], ..., cfg.pearson_gate_threshold, ...)
21. plot_divergence_dist(divergence, div_threshold, ...)
22. plot_ttr_vs_divergence(ttr_values, divergence, high_div_idx, ...)

23. results = {
      degenerate: False,
      pearson: pearson_result,
      spearman: {rho, p_value: p_val},
      divergence: {threshold: div_threshold, n_high_div: len(high_div_idx)},
      ttr: ttr_result,
      auroc_context: {te: te_auroc, se: se_auroc},
      gate_pass: pearson_result["gate_pass"],
    }
24. return results
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-11-1 | run_orchestrator | Implement run() with degenerate branching, figure calls, results assembly |

---

## Summary: Subtask Allocation [5/5 used]

| ID | Subtask | Parent Epic | Description |
|----|---------|-------------|-------------|
| L-3-1 | load_scores_degenerate | E-3 | load_uq_scores + check_degenerate + inspect_cluster_distribution |
| L-4-1 | pearson_bootstrap | E-4 | pearson_r_bootstrap_ci with Fisher z-transform |
| L-4-2 | evaluate_gate | E-4 | evaluate_gate + degenerate gate interpretation |
| L-6-1 | ttr_analysis | E-6 | load_stochastic_samples + compute_ttr + compute_ttr_by_group |
| L-11-1 | run_orchestrator | E-11 | run() orchestrator with degenerate branching and figure calls |
