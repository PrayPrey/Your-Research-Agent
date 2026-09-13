# Logic Design: H-M3
# AUROC Bootstrap CI on Aggregation Differences

**Hypothesis:** H-M3 (MECHANISM — Statistical Re-analysis)
**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr

Applied: None — Archon KB no relevant content (diffusion model content only, similarity < 0.33)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M2)
**Status**: API signatures verified from actual base code (Read tool used; Serena project activation unavailable)
**Analyzed Path**: `docs/youra_research/h-m2/code/`
**Relevant Symbols**:
- `compute_auroc(scores, labels)` in `analysis.py:28` — uses `roc_auc_score(labels, -scores)`
- `load_scores_from_cache(model_key, dataset_name)` in `run_hm2.py:30` — negates H-E1 positive scores back to negative
- `bootstrap((scores, labels), stat, n_resamples, confidence_level, paired=True, method="percentile")` pattern in `analysis.py:18`
- `gate_check(results)` returns `{"gate", "p1_met", "p2_met"}` in `analysis.py:63`

**Critical finding**: H-M2 `load_scores_from_cache` negates H-E1 scores (positive → negative) at load time.
H-M3 inverts this: keep H-E1 scores POSITIVE and use `roc_auc_score(labels, +scores)` directly.

---

## External Dependencies API

### From H-M2 actual code (`h-m2/code/analysis.py`)

```python
# H-M2 analysis.py — ACTUAL signatures (verified)
def compute_auroc(scores: np.ndarray, labels: np.ndarray) -> float:
    """Negates scores: roc_auc_score(labels, -scores)"""
    # H-M3 does NOT use this function — reimplements inline with +scores

def compute_spearman_with_ci(
    scores: np.ndarray, labels: np.ndarray,
    n_resamples: int = 1000, ci: float = 0.95
) -> Tuple[float, float, object]:
    """Returns (rho, p_value, bootstrap_ci)"""
    # H-M3 does NOT use this — uses AUROC not Spearman

def gate_check(results: Dict) -> Dict:
    """Returns {"gate", "p1_met", "p2_met"}"""
    # H-M3 reimplements with stricter CI-based gates (P1/P2/P3)
```

### From H-M2 actual code (`h-m2/code/run_hm2.py`)

```python
# load_scores_from_cache — ACTUAL behavior (verified from run_hm2.py:44-48)
# H-E1 npz stores POSITIVE negated log-probs (mean > 0)
# H-M2 negates them back to negative for Spearman analysis
# H-M3 keeps them POSITIVE and passes directly to roc_auc_score(labels, +scores)

# npz keys (verified from run_hm2.py:35-39):
#   "min_scores", "mean_scores", "sum_scores", "labels"
```

### From scipy / sklearn

```python
from scipy.stats import bootstrap
# bootstrap((a, b), statistic, n_resamples=1000, paired=True, method="percentile")
# .confidence_interval.low, .confidence_interval.high

from sklearn.metrics import roc_auc_score
# roc_auc_score(y_true, y_score) -> float
```

---

## A-2: Score Loader [Complexity: 9, Budget: 2 subtasks]

### API Signatures

```python
# score_loader.py
import numpy as np
from typing import Dict, Optional, Tuple

def load_scores(
    model_key: str,
    dataset_name: str,
    h_e1_dir: str,
    h_m2_dir: str,
) -> Tuple[Optional[Dict[str, np.ndarray]], Optional[np.ndarray]]:
    """Load scores from H-E1 npz (primary) or H-M2 npz (fallback).
    Returns (scores_dict, labels) or (None, None). scores_dict keys: "min","mean","raw_sum".
    Scores are POSITIVE (H-E1 convention: negated log-probs). Pass directly to roc_auc_score.
    """

def _load_npz(
    path: str,
) -> Tuple[Dict[str, np.ndarray], np.ndarray]:
    """Load npz, remap keys, validate. Raises FileNotFoundError or ValueError."""
    # keys in file: min_scores, mean_scores, sum_scores, labels
    # out keys:     min,        mean,         raw_sum,    labels
    # validation: n >= 100, both classes present in labels
    # sign check: if scores["min"].mean() < 0 → negate (H-M2 convention → H-E1 convention)
```

### Pseudo-code

```
load_scores(model_key, dataset_name, h_e1_dir, h_m2_dir):
    h_e1_path = f"{h_e1_dir}/scores_{model_key}_{dataset_name}.npz"
    h_m2_path = f"{h_m2_dir}/scores_{model_key}_{dataset_name}.npz"

    for path in [h_e1_path, h_m2_path]:
        if exists(path):
            scores, labels = _load_npz(path)
            return scores, labels

    return None, None

_load_npz(path):
    data = np.load(path)
    scores = {"min": data["min_scores"], "mean": data["mean_scores"], "raw_sum": data["sum_scores"]}
    labels = data["labels"].astype(int)
    assert len(labels) >= 100 and labels.min() == 0 and labels.max() == 1
    # Normalize to positive convention (H-E1 stores positive; H-M2 may store negative)
    if scores["min"].mean() < 0:
        scores = {k: -v for k, v in scores.items()}  # negate to positive
    return scores, labels
```

### Subtasks

### L-2-1: NPZ key remapping and sign normalization
Load npz, remap keys (`min_scores`→`min`, `sum_scores`→`raw_sum`), detect and normalize sign convention.
Reference: architecture §ScoreLoader

### L-2-2: Fallback path logic and validation
Implement H-E1→H-M2 fallback, n>=100 check, both-class check, warn on missing.
Reference: architecture §ScoreLoader

---

## A-3: Bootstrap CI Core [Complexity: 12, Budget: 2 subtasks]

### API Signatures

```python
# bootstrap_ci.py
import numpy as np
from scipy.stats import bootstrap
from sklearn.metrics import roc_auc_score
from typing import Dict, List, Tuple

def compute_auroc_with_ci(
    y_true: np.ndarray,       # (N,) int
    scores: np.ndarray,       # (N,) float, POSITIVE convention
    n_bootstrap: int = 1000,
    seed: int = 42,
    confidence_level: float = 0.95,
) -> Tuple[float, float, float]:
    """Returns (auroc, ci_lower, ci_upper). Uses percentile bootstrap."""

def compute_diff_ci(
    y_true: np.ndarray,       # (N,) int
    scores_a: np.ndarray,     # (N,) float, POSITIVE
    scores_b: np.ndarray,     # (N,) float, POSITIVE
    n_bootstrap: int = 1000,
    seed: int = 42,
    confidence_level: float = 0.95,
) -> Dict[str, float]:
    """Paired bootstrap CI on AUROC(a) - AUROC(b).
    Returns {"diff": float, "ci_lower": float, "ci_upper": float}.
    Same resample indices applied to both arrays (paired=True).
    """

def compute_auroc_table(
    data: Dict[Tuple[str, str, str], Tuple[np.ndarray, np.ndarray]],
    n_bootstrap: int = 1000,
    seed: int = 42,
    confidence_level: float = 0.95,
) -> Dict:
    """
    data keys: (model_key, dataset_name, agg_method)  e.g. ("llama2","trivia_qa","min")
    data values: (scores, labels)

    Returns {
        "auroc": {(model, dataset, agg): {"auroc", "ci_lower", "ci_upper"}},
        "diff":  {(model, dataset):      {"diff_min_mean", "ci_lower", "ci_upper"}},
        "bootstrap_samples": {(model, dataset, agg): np.ndarray shape (n_bootstrap,)},
    }
    bootstrap_samples stored for fig3 histogram.
    """
```

### Pseudo-code: compute_auroc_with_ci

```
def compute_auroc_with_ci(y_true, scores, n_bootstrap, seed, confidence_level):
    auroc = roc_auc_score(y_true, scores)  # +scores, POSITIVE convention

    def stat(yt, sc):
        return roc_auc_score(yt, sc)

    res = bootstrap(
        (y_true, scores), stat,
        n_resamples=n_bootstrap,
        confidence_level=confidence_level,
        paired=True,
        method="percentile",
        random_state=seed,
    )
    return auroc, res.confidence_interval.low, res.confidence_interval.high
```

### Pseudo-code: compute_diff_ci

```
def compute_diff_ci(y_true, scores_a, scores_b, n_bootstrap, seed, confidence_level):
    diff = roc_auc_score(y_true, scores_a) - roc_auc_score(y_true, scores_b)

    def stat(yt, sa, sb):
        return roc_auc_score(yt, sa) - roc_auc_score(yt, sb)

    res = bootstrap(
        (y_true, scores_a, scores_b), stat,
        n_resamples=n_bootstrap,
        confidence_level=confidence_level,
        paired=True,
        method="percentile",
        random_state=seed,
    )
    return {"diff": diff, "ci_lower": res.confidence_interval.low, "ci_upper": res.confidence_interval.high}
```

### Pseudo-code: compute_auroc_table

```
def compute_auroc_table(data, n_bootstrap, seed, confidence_level):
    auroc_out = {}
    bootstrap_samples = {}

    # 1. AUROC + CI for each (model, dataset, agg)
    for (model, dataset, agg), (scores, labels) in data.items():
        auroc, ci_lo, ci_hi = compute_auroc_with_ci(labels, scores, n_bootstrap, seed, confidence_level)
        auroc_out[(model, dataset, agg)] = {"auroc": auroc, "ci_lower": ci_lo, "ci_upper": ci_hi}
        # collect bootstrap distribution for fig3
        bootstrap_samples[(model, dataset, agg)] = _collect_bootstrap_dist(labels, scores, n_bootstrap, seed)

    # 2. Paired diff CI for each (model, dataset): AUROC(min) - AUROC(mean)
    diff_out = {}
    for (model, dataset) in set((m, d) for (m, d, _) in data.keys()):
        scores_min  = data[(model, dataset, "min")][0]
        scores_mean = data[(model, dataset, "mean")][0]
        labels      = data[(model, dataset, "min")][1]
        diff_out[(model, dataset)] = compute_diff_ci(labels, scores_min, scores_mean, n_bootstrap, seed)

    return {"auroc": auroc_out, "diff": diff_out, "bootstrap_samples": bootstrap_samples}

def _collect_bootstrap_dist(labels, scores, n_bootstrap, seed):
    """Returns (n_bootstrap,) array of bootstrap AUROC values for histogram."""
    rng = np.random.default_rng(seed)
    n = len(labels)
    vals = []
    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, n)
        vals.append(roc_auc_score(labels[idx], scores[idx]))
    return np.array(vals)
```

### Subtasks

### L-3-1: compute_auroc_with_ci and compute_diff_ci
Single-AUROC and paired-diff bootstrap using scipy.stats.bootstrap(paired=True, method="percentile").
Reference: architecture §BootstrapCI

### L-3-2: compute_auroc_table and _collect_bootstrap_dist
Loop over all (model, dataset, agg) combos; collect bootstrap distributions for fig3.
Reference: architecture §BootstrapCI

---

## A-5: Gate Evaluator [Complexity: 9, Budget: 2 subtasks]

### API Signatures

```python
# gate_check.py
from typing import Dict

def evaluate_gates(
    auroc_table: Dict,          # from compute_auroc_table()
    p1_threshold: float = 0.02,
    p2_threshold: float = 0.02,
) -> Dict:
    """
    Returns {
        "p1_met": bool,
        "p1_evidence": {"llama2": {dataset: diff_dict}, "mistral": {...}},
        "p2_met": bool,
        "p2_evidence": {"llama2": {dataset: diff_dict}, "mistral": {...}},
        "p3_met": bool,
        "p3_evidence": {(model, dataset): {"raw_sum_vs_min": float, "raw_sum_vs_mean": float}},
        "gate": "PASS" | "PARTIAL_PASS" | "FAIL",
        "n_gates_met": int,   # 0, 1, 2, or 3
    }

    P1: diff_min_mean >= p1_threshold AND ci_lower > 0, on trivia_qa AND nq, BOTH models
    P2: diff_mean_min >= p2_threshold AND ci_lower > 0, on truthful_qa, BOTH models
    P3: AUROC(raw_sum) < AUROC(min) AND AUROC(raw_sum) < AUROC(mean), ALL datasets, directional only
    """
```

### Pseudo-code

```
evaluate_gates(auroc_table, p1_threshold, p2_threshold):
    auroc  = auroc_table["auroc"]
    diff   = auroc_table["diff"]
    MODELS   = ["llama2", "mistral"]
    P1_DS    = ["trivia_qa", "nq"]
    P2_DS    = ["truthful_qa"]
    ALL_DS   = ["trivia_qa", "nq", "truthful_qa"]

    # P1: min beats mean on trivia_qa AND nq, both models
    p1_evidence = {}
    p1_checks = []
    for model in MODELS:
        p1_evidence[model] = {}
        for ds in P1_DS:
            d = diff.get((model, ds), {})
            ok = d.get("diff", 0) >= p1_threshold and d.get("ci_lower", -1) > 0
            p1_evidence[model][ds] = {**d, "met": ok}
            p1_checks.append(ok)
    p1_met = all(p1_checks)  # ALL 4 (2 models × 2 datasets)

    # P2: mean beats min on truthful_qa, both models
    p2_evidence = {}
    p2_checks = []
    for model in MODELS:
        p2_evidence[model] = {}
        ds = "truthful_qa"
        d_fwd = diff.get((model, ds), {})  # diff = AUROC(min) - AUROC(mean)
        # P2 requires mean > min, so diff_mean_min = -diff_min_mean
        diff_mean_min = -d_fwd.get("diff", 0)
        ci_lo_mean_min = -d_fwd.get("ci_upper", 1)  # flip CI bounds
        ok = diff_mean_min >= p2_threshold and ci_lo_mean_min > 0
        p2_evidence[model][ds] = {"diff": diff_mean_min, "ci_lower": ci_lo_mean_min, "met": ok}
        p2_checks.append(ok)
    p2_met = all(p2_checks)

    # P3: raw_sum < min AND raw_sum < mean, all datasets, directional
    p3_evidence = {}
    p3_checks = []
    for model in MODELS:
        for ds in ALL_DS:
            a_sum  = auroc.get((model, ds, "raw_sum"), {}).get("auroc", 1.0)
            a_min  = auroc.get((model, ds, "min"),     {}).get("auroc", 0.0)
            a_mean = auroc.get((model, ds, "mean"),    {}).get("auroc", 0.0)
            ok = a_sum < a_min and a_sum < a_mean
            p3_evidence[(model, ds)] = {"raw_sum_vs_min": a_sum - a_min, "raw_sum_vs_mean": a_sum - a_mean, "met": ok}
            p3_checks.append(ok)
    p3_met = all(p3_checks)

    n = sum([p1_met, p2_met, p3_met])
    gate = "PASS" if n == 3 else ("PARTIAL_PASS" if n >= 1 else "FAIL")

    return {
        "p1_met": p1_met, "p1_evidence": p1_evidence,
        "p2_met": p2_met, "p2_evidence": p2_evidence,
        "p3_met": p3_met, "p3_evidence": p3_evidence,
        "gate": gate, "n_gates_met": n,
    }
```

### Subtasks

### L-5-1: P1 and P2 gate logic with CI-based thresholds
Implement P1 (min beats mean, both datasets, both models, CI lower > 0) and P2 (mean beats min on TruthfulQA). Use diff table from compute_auroc_table; flip sign for P2.
Reference: architecture §GateCheck

### L-5-2: P3 gate logic and gate string resolution
Implement P3 directional check (raw_sum < min AND raw_sum < mean), all 6 combos. Resolve gate string from n_gates_met.
Reference: architecture §GateCheck

---

## A-7: Figures [Complexity: 14, Budget: 4 subtasks]

### API Signatures

```python
# figures.py
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict

def fig1_auroc_bar(auroc_table: Dict, out_dir: str) -> str:
    """Bar chart: 3 datasets × 2 models = 6 groups; bars per group = min/mean/raw_sum.
    CI error bars from auroc_table["auroc"][...]["ci_lower/upper"].
    Returns saved figure path.
    """

def fig2_diff_heatmap(auroc_table: Dict, out_dir: str) -> str:
    """Heatmap 2×3 (rows=model, cols=dataset); cell = AUROC(min)-AUROC(mean).
    Diverging colormap (RdBu_r), center=0. Annotate each cell with diff value and CI.
    Returns saved figure path.
    """

def fig3_bootstrap_dists(auroc_table: Dict, out_dir: str) -> str:
    """4-panel histogram of bootstrap AUROC diff distributions (min - mean).
    Panels: [llama2×trivia_qa, llama2×nq, mistral×trivia_qa, mistral×nq].
    Vertical line at diff=0; shade CI region.
    Returns saved figure path.
    """

def fig4_summary_table(gate_result: Dict, auroc_table: Dict, out_dir: str) -> str:
    """Matplotlib table: rows = P1/P2/P3 conditions; cols = model/dataset/diff/CI/met.
    Color rows green (met) or red (not met).
    Returns saved figure path.
    """

def save_all_figures(auroc_table: Dict, gate_result: Dict, out_dir: str) -> None:
    """Call all four fig functions; print saved paths."""
```

### Figure Layout Notes

fig1: `figsize=(12, 5)`. `ax.bar` with `x = np.arange(3)` per model subplot (2 subplots side by side). Bar width 0.25 per agg method. `ax.errorbar` for CI. Legend: min/mean/raw_sum.

fig2: `figsize=(8, 4)`. `ax.imshow(data, cmap="RdBu_r", vmin=-0.1, vmax=0.1)`. Annotate each cell: `f"{diff:+.3f}\n[{ci_lo:.3f},{ci_hi:.3f}]"`. xticklabels=datasets, yticklabels=models.

fig3: `figsize=(10, 8)`, 2×2 grid. Per panel: `ax.hist(samples, bins=50)`. Vertical `ax.axvline(x=0, color="red")`. Shade CI with `ax.axvspan(ci_lo, ci_hi, alpha=0.2)`.

fig4: `figsize=(12, 4)`. `ax.axis("off")`. `ax.table(cellText=rows, colLabels=cols, loc="center")`. Color rows via `table[row, col].set_facecolor`.

### Subtasks

### L-7-1: fig1_auroc_bar
Grouped bar chart; 6 groups (3 datasets × 2 models); 3 bars per group; CI error bars from auroc_table.
Reference: architecture §Figures

### L-7-2: fig2_diff_heatmap
2×3 heatmap of AUROC(min)-AUROC(mean); diverging colormap centered at 0; per-cell annotation with diff and CI.
Reference: architecture §Figures

### L-7-3: fig3_bootstrap_dists
4-panel histogram of bootstrap diff distributions (from `auroc_table["bootstrap_samples"]`); zero line; CI shading.
Reference: architecture §Figures

### L-7-4: fig4_summary_table and save_all_figures
Matplotlib table rendering gate evidence; row coloring by met/not-met; save_all_figures orchestration.
Reference: architecture §Figures

---

## Supporting Modules (Low Complexity, No Subtasks)

### config.py

```python
# config.py
import os

_THIS  = os.path.dirname(os.path.abspath(__file__))
_HM3   = os.path.dirname(_THIS)
_YOURA = os.path.dirname(os.path.dirname(_HM3))

H_E1_RESULTS_DIR: str = os.path.join(_YOURA, "h-e1", "results")
H_M2_RESULTS_DIR: str = os.path.join(_YOURA, "h-m2", "results")
RESULTS_DIR: str       = os.path.join(_HM3, "results")
FIGURES_DIR: str       = os.path.join(_HM3, "figures")

DATASETS: list              = ["trivia_qa", "nq", "truthful_qa"]
MODELS_TO_RUN: list         = ["llama2", "mistral"]
AGGREGATION_METHODS: list   = ["min", "mean", "raw_sum"]
N_RESAMPLES_BOOTSTRAP: int  = 1000
SEED: int                   = 42
CONFIDENCE_LEVEL: float     = 0.95
P1_THRESHOLD: float         = 0.02
P2_THRESHOLD: float         = 0.02
```

### run_experiment.py

```python
# run_experiment.py
import argparse, json, os
import numpy as np
import config as cfg
from score_loader import load_scores
from bootstrap_ci import compute_auroc_table
from gate_check import evaluate_gates
from figures import save_all_figures

def main(args) -> None:
    os.makedirs(cfg.RESULTS_DIR, exist_ok=True)
    os.makedirs(cfg.FIGURES_DIR, exist_ok=True)

    # 1. Load scores — build data dict for compute_auroc_table
    data = {}  # {(model, dataset, agg): (scores_arr, labels)}
    for model in cfg.MODELS_TO_RUN:
        for dataset in cfg.DATASETS:
            scores_dict, labels = load_scores(model, dataset, args.h_e1_dir, args.h_m2_dir)
            if scores_dict is None:
                print(f"[WARN] missing: {model} × {dataset} — skip")
                continue
            for agg in cfg.AGGREGATION_METHODS:
                data[(model, dataset, agg)] = (scores_dict[agg], labels)

    # 2. Compute AUROC + CI table
    auroc_table = compute_auroc_table(data, args.n_bootstrap, args.seed, cfg.CONFIDENCE_LEVEL)

    # 3. Gate evaluation
    gate_result = evaluate_gates(auroc_table, cfg.P1_THRESHOLD, cfg.P2_THRESHOLD)

    # 4. Serialize results
    # auroc_table["auroc"] has tuple keys → convert to str for JSON
    auroc_json = {str(k): v for k, v in auroc_table["auroc"].items()}
    diff_json  = {str(k): v for k, v in auroc_table["diff"].items()}
    with open(os.path.join(cfg.RESULTS_DIR, "auroc_table.json"), "w") as f:
        json.dump({"auroc": auroc_json, "diff": diff_json}, f, indent=2)
    with open(os.path.join(cfg.RESULTS_DIR, "gate_conditions.json"), "w") as f:
        json.dump(gate_result, f, indent=2, default=str)

    # 5. Figures
    save_all_figures(auroc_table, gate_result, cfg.FIGURES_DIR)

    # 6. Print gate
    print(f"\n=== Gate: {gate_result['gate']} ({gate_result['n_gates_met']}/3 met) ===")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--h_e1_dir", default=cfg.H_E1_RESULTS_DIR)
    parser.add_argument("--h_m2_dir", default=cfg.H_M2_RESULTS_DIR)
    parser.add_argument("--seed", type=int, default=cfg.SEED)
    parser.add_argument("--n_bootstrap", type=int, default=cfg.N_RESAMPLES_BOOTSTRAP)
    main(parser.parse_args())
```

---

## Subtask Summary

| ID | Task | Description |
|----|------|-------------|
| L-2-1 | NPZ key remap + sign normalize | `_load_npz`: remap keys, detect/negate sign |
| L-2-2 | Fallback + validation | H-E1→H-M2 fallback, n>=100, both-class check |
| L-3-1 | compute_auroc_with_ci + compute_diff_ci | scipy.stats.bootstrap, paired, percentile |
| L-3-2 | compute_auroc_table + _collect_bootstrap_dist | Loop all combos; collect bootstrap arrays |
| L-5-1 | P1 + P2 gate logic | CI-based thresholds; P2 sign flip |
| L-5-2 | P3 gate + gate string | Directional raw_sum check; resolve PASS/PARTIAL/FAIL |
| L-7-1 | fig1_auroc_bar | Grouped bar chart with CI error bars |
| L-7-2 | fig2_diff_heatmap | 2×3 diverging heatmap |
| L-7-3 | fig3_bootstrap_dists | 4-panel bootstrap dist histograms |
| L-7-4 | fig4_summary_table + save_all_figures | Table rendering + orchestration |

Total: 10 subtasks (within budget)

---

## Key Implementation Notes

1. **Sign convention**: H-E1 npz → POSITIVE scores (negated log-probs). H-M3 uses `roc_auc_score(labels, +scores)`. H-M2 negated them back to negative — do NOT reuse H-M2's `compute_auroc`.

2. **Paired bootstrap for diff CI**: Must pass `(y_true, scores_a, scores_b)` together with `paired=True` so same indices resample all three arrays.

3. **P2 sign flip**: `auroc_table["diff"]` stores `AUROC(min)-AUROC(mean)`. P2 needs `AUROC(mean)-AUROC(min)`, so negate diff and flip CI bounds (`ci_lower = -old_ci_upper`).

4. **bootstrap_samples storage**: `compute_auroc_table` must also store per-key bootstrap arrays for fig3. Use manual loop (`_collect_bootstrap_dist`) rather than scipy.stats.bootstrap to get the raw samples array.

5. **Missing data handling**: If a (model, dataset) pair is missing, skip it in gate checks rather than raising. Gate P1 requires all 4 checks to pass — missing = automatic fail for that gate.
