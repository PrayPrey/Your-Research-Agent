# Logic: H-M3 Linear Fusion Scoring

**Applied**: Linear score-fusion pattern (min-max normalize -> convex combine -> grid search AUROC)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual h-m2 code
**Analyzed Path**: `h-m2/code/stats.py`, `h-m2/code/results/h-m2_results.json`
**Relevant Symbols**: `compute_correlation(consistencies, correctness) -> dict`, `pearson_entropy_consistency(entropies, consistencies) -> float`

Verified JSON schema (`h-m2_results.json["results"][i]`): `{qid: str, question: str, entropy: float, consistency: float, correct: bool, majority_answer: str}`. `correct` field name confirmed from actual file (not `label` or `is_correct`).

---

## A-1: Results Loader [Complexity: 3, Budget: 3]

**Applied**: Standard PyTorch/numpy JSON-to-array pattern

### API Signatures

```python
# h-m3/code/load_results.py
import json
import numpy as np

def load_h_m2_results(path: str = "../../h-m2/code/results/h-m2_results.json") -> dict:
    """Load h-m2 JSON, return arrays keyed by qid order."""
    ...
    # returns {"entropy": np.ndarray[N], "consistency": np.ndarray[N],
    #          "correct": np.ndarray[N] bool, "qids": list[str]}
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| entropy | [N] | N=20 (h-m2 PoC scale) |
| consistency | [N] | float in ~[0,1] |
| correct | [N] | bool, used as AUROC labels |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | JSON read | `json.load(open(path))["results"]` |
| L-1-2 | Field extraction | pull `entropy`, `consistency`, `correct`, `qid` per row into lists |
| L-1-3 | Array conversion | `np.array(...)`, `dtype=bool` for correct |

---

## A-2: LinearFusionScorer [Complexity: 4, Budget: 4]

**Applied**: Min-max normalize + convex combination (Genest & Zidek linear opinion pool)

### API Signatures

```python
# h-m3/code/fusion.py
import numpy as np

class LinearFusionScorer:
    def __init__(self, alpha: float = 0.5, beta: float = 0.5):
        self.alpha = alpha
        self.beta = beta

    def normalize(self, values: np.ndarray) -> np.ndarray:
        """Min-max to [0,1]; zero-vector guard if range < 1e-8."""
        ...

    def compute_scores(self, entropy: np.ndarray, consistency: np.ndarray) -> np.ndarray:
        """alpha*(1-normalize(entropy)) + beta*normalize(consistency). [N] -> [N]"""
        ...
```

### Pseudo-code

```
normalize(v):
  lo, hi = v.min(), v.max()
  if hi - lo < 1e-8: return zeros_like(v)
  return (v - lo) / (hi - lo)

compute_scores(entropy, consistency):
  confidence = 1.0 - normalize(entropy)   # low entropy -> high confidence
  cons_norm = normalize(consistency)
  return alpha * confidence + beta * cons_norm
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | `__init__` | store alpha, beta |
| L-2-2 | `normalize` | min-max with zero-range guard |
| L-2-3 | `compute_scores` core | inverse-entropy + consistency combine |
| L-2-4 | Edge case test | verify constant-input array -> zeros, no NaN |

---

## A-3: Train/Val Split + Grid Search [Complexity: 6, Budget: 6]

**Applied**: Standard PyTorch/sklearn train-holdout grid search pattern

### API Signatures

```python
# h-m3/code/fusion.py (same file)

def train_test_split_idx(n: int, val_frac: float = 0.1, seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    """Shuffled index split. Returns (val_idx, test_idx)."""
    ...

def grid_search_weights(
    entropy: np.ndarray, consistency: np.ndarray, labels: np.ndarray,
    alpha_range: list[float] | None = None, beta_range: list[float] | None = None,
) -> tuple[float, float, float]:
    """Grid search alpha,beta on given (val) subset. Default ranges = 0.0..1.0 step 0.1 (121 combos).
    Returns (best_alpha, best_beta, best_val_auroc)."""
    ...
```

### Pseudo-code

```
train_test_split_idx(n, val_frac, seed):
  rng = np.random.RandomState(seed)
  idx = rng.permutation(n)
  n_val = max(1, int(n * val_frac))
  return idx[:n_val], idx[n_val:]

grid_search_weights(entropy, consistency, labels, alpha_range, beta_range):
  best_auroc = 0.0; best_alpha, best_beta = 0.5, 0.5
  for alpha in alpha_range:
    for beta in beta_range:
      scores = LinearFusionScorer(alpha, beta).compute_scores(entropy, consistency)
      auroc = roc_auc_score(labels, scores)
      if auroc > best_auroc:
        best_auroc, best_alpha, best_beta = auroc, alpha, beta
  return best_alpha, best_beta, best_auroc
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | `train_test_split_idx` | seeded permutation split |
| L-3-2 | Grid loop | nested alpha/beta loop, 121 combos |
| L-3-3 | AUROC scoring | `roc_auc_score(labels, scores)` per combo |
| L-3-4 | Best tracking | update best_auroc/alpha/beta |
| L-3-5 | Default ranges | `[round(i*0.1,1) for i in range(11)]` |
| L-3-6 | N=20 edge case | val split may be 2 rows; guard `roc_auc_score` single-class ValueError |

---

## A-4: StatsAnalyzer Extension [Complexity: 7, Budget: 7]

**Applied**: Bootstrap resampling for CI (standard uncertainty-estimation pattern)

### API Signatures

```python
# h-m3/code/stats.py
import numpy as np
from scipy import stats
from sklearn.metrics import roc_auc_score

# --- copied unchanged from h-m2/code/stats.py ---
def compute_correlation(consistencies: list[float], correctness: list[bool]) -> dict: ...
def pearson_entropy_consistency(entropies: list[float], consistencies: list[float]) -> float: ...

# --- new for h-m3 ---
def evaluate_variants(
    entropy: np.ndarray, consistency: np.ndarray, labels: np.ndarray,
    alpha_beta_pairs: dict[str, tuple[float, float]],
) -> dict:
    """Compute AUROC per named (alpha,beta) variant.
    Returns {name: {"auroc": float, "scores": np.ndarray[N]}}"""
    ...

def bootstrap_ci_improvement(
    labels: np.ndarray, scores_a: np.ndarray, scores_b: np.ndarray,
    n_boot: int = 1000, seed: int = 42,
) -> dict:
    """Bootstrap CI for AUROC(scores_a) - AUROC(scores_b).
    scores_a = combined/optimal, scores_b = best single-metric.
    Returns {"improvement": float, "ci_low": float, "ci_high": float}"""
    ...
```

### Pseudo-code

```
evaluate_variants(entropy, consistency, labels, alpha_beta_pairs):
  out = {}
  for name, (a, b) in alpha_beta_pairs.items():
    scores = LinearFusionScorer(a, b).compute_scores(entropy, consistency)
    out[name] = {"auroc": roc_auc_score(labels, scores), "scores": scores}
  return out

bootstrap_ci_improvement(labels, scores_a, scores_b, n_boot, seed):
  rng = np.random.RandomState(seed)
  n = len(labels)
  diffs = []
  for _ in range(n_boot):
    idx = rng.randint(0, n, n)          # resample with replacement
    if len(unique(labels[idx])) < 2: continue  # skip degenerate resample
    auroc_a = roc_auc_score(labels[idx], scores_a[idx])
    auroc_b = roc_auc_score(labels[idx], scores_b[idx])
    diffs.append(auroc_a - auroc_b)
  diffs = np.array(diffs)
  return {
    "improvement": float(np.mean(diffs)),
    "ci_low": float(np.percentile(diffs, 2.5)),
    "ci_high": float(np.percentile(diffs, 97.5)),
  }
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | Copy base fns | `compute_correlation`, `pearson_entropy_consistency` verbatim |
| L-4-2 | `evaluate_variants` loop | iterate named alpha/beta pairs |
| L-4-3 | Per-variant scoring | LinearFusionScorer + roc_auc_score |
| L-4-4 | `bootstrap_ci_improvement` resample loop | seeded `randint` resampling |
| L-4-5 | Degenerate-resample guard | skip single-class bootstrap draws (small N=20 risk) |
| L-4-6 | Percentile CI | 2.5/97.5 percentile of diffs |
| L-4-7 | Return dict assembly | improvement/ci_low/ci_high |

---

## A-5: Visualizer [Complexity: 7, Budget: 7]

**Applied**: Standard matplotlib bar/ROC/heatmap pattern, extends h-m2 scatter

### API Signatures

```python
# h-m3/code/visualize.py
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import roc_curve, auc

def plot_gate_metrics(auroc_entropy: float, auroc_consistency: float, auroc_combined: float, out_path: str) -> None: ...

def plot_roc_overlay(
    labels: np.ndarray, entropy_scores: np.ndarray, consistency_scores: np.ndarray,
    combined_scores: np.ndarray, out_path: str,
) -> None: ...

def plot_weight_heatmap(alpha_range: list[float], beta_range: list[float], auroc_grid: np.ndarray, out_path: str) -> None:
    """auroc_grid: [len(alpha_range), len(beta_range)]"""
    ...

def plot_entropy_vs_consistency(
    entropies: np.ndarray, consistencies: np.ndarray, correctness: np.ndarray, out_path: str,
) -> None:
    """Copied from h-m2/code/visualize.py::plot_entropy_vs_consistency"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| auroc_grid | [11, 11] | alpha rows x beta cols, from grid search sweep |

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | `plot_gate_metrics` | 3-bar chart, entropy/consistency/combined AUROC |
| L-5-2 | `plot_roc_overlay` setup | compute `roc_curve` for each of 3 score arrays |
| L-5-3 | `plot_roc_overlay` render | 3 overlaid curves + diagonal reference |
| L-5-4 | `plot_weight_heatmap` grid build | recompute or reuse AUROC per (a,b) into 2D array |
| L-5-5 | `plot_weight_heatmap` render | `imshow`/`pcolormesh` with colorbar |
| L-5-6 | `plot_entropy_vs_consistency` | copy h-m2 scatter logic, color by `correct` |
| L-5-7 | Save + close | `plt.savefig(out_path); plt.close()` for all 4 |

---

## A-6: Pipeline Integration [Complexity: 8, Budget: 8]

**Applied**: Standard orchestration script pattern (load -> split -> search -> eval -> stats -> viz -> save)

### API Signatures

```python
# h-m3/code/run_pipeline.py
def run(h_m2_results_path: str | None = None) -> dict:
    """Full H-M3 pipeline. Writes results/h-m3_results.json. Returns same dict."""
    ...
```

### Pseudo-code

```
run(h_m2_results_path=None):
  path = h_m2_results_path or config.H_M2_RESULTS_PATH
  data = load_h_m2_results(path)
  entropy, consistency, correct = data["entropy"], data["consistency"], data["correct"]

  val_idx, test_idx = train_test_split_idx(len(correct), config.VAL_FRACTION, config.SEED)
  best_alpha, best_beta, val_auroc = grid_search_weights(
      entropy[val_idx], consistency[val_idx], correct[val_idx],
      config.ALPHA_RANGE, config.BETA_RANGE)

  variants = evaluate_variants(
      entropy[test_idx], consistency[test_idx], correct[test_idx],
      {"entropy_only": (1.0, 0.0), "consistency_only": (0.0, 1.0),
       "equal": (0.5, 0.5), "optimal": (best_alpha, best_beta)})

  best_single_name = "entropy_only" if variants["entropy_only"]["auroc"] >= variants["consistency_only"]["auroc"] else "consistency_only"
  ci = bootstrap_ci_improvement(
      correct[test_idx], variants["optimal"]["scores"], variants[best_single_name]["scores"],
      config.N_BOOTSTRAP, config.SEED)

  plot_gate_metrics(variants["entropy_only"]["auroc"], variants["consistency_only"]["auroc"], variants["optimal"]["auroc"], f"{config.FIGURES_DIR}/gate_metrics.png")
  plot_roc_overlay(correct[test_idx], variants["entropy_only"]["scores"], variants["consistency_only"]["scores"], variants["optimal"]["scores"], f"{config.FIGURES_DIR}/roc_overlay.png")
  plot_weight_heatmap(config.ALPHA_RANGE, config.BETA_RANGE, auroc_grid, f"{config.FIGURES_DIR}/weight_heatmap.png")
  plot_entropy_vs_consistency(entropy, consistency, correct, f"{config.FIGURES_DIR}/entropy_vs_consistency.png")

  results = {"best_alpha": best_alpha, "best_beta": best_beta, "val_auroc": val_auroc,
             "variants": {k: v["auroc"] for k, v in variants.items()}, "bootstrap_ci": ci,
             "gate_pass": variants["optimal"]["auroc"] > max(variants["entropy_only"]["auroc"], variants["consistency_only"]["auroc"])}
  json.dump(results, open(config.OUTPUT_PATH, "w"), indent=2)
  return results
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | Load stage | call `load_h_m2_results` |
| L-6-2 | Split stage | call `train_test_split_idx` |
| L-6-3 | Grid search stage | call `grid_search_weights` on val split |
| L-6-4 | Ablation eval stage | call `evaluate_variants` on test split, 4 variants |
| L-6-5 | Best-single selection | compare entropy_only vs consistency_only AUROC |
| L-6-6 | Bootstrap CI stage | call `bootstrap_ci_improvement` |
| L-6-7 | Figures stage | call all 4 visualize functions |
| L-6-8 | Results JSON | assemble dict, write via `json.dump`, include `gate_pass` bool |

---

## A-7: Full-Run Validation [Complexity: 5, Budget: 5]

**Applied**: Standard smoke-test / self-check pattern

### API Signatures

```python
# h-m3/code/run_pipeline.py (or separate test_pipeline.py)
def main() -> None:
    results = run()
    assert results["gate_pass"] or True  # log-only per SHOULD_WORK gate, no hard fail
    print(f"Combined AUROC: {results['variants']['optimal']:.4f}, gate_pass={results['gate_pass']}")

if __name__ == "__main__":
    main()
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | Run on N=20 | invoke `run()` with default h-m2 path |
| L-7-2 | Assert no exceptions | pipeline completes end-to-end |
| L-7-3 | Check `gate_pass` | AUROC_combined > max(single) per PRD success criteria |
| L-7-4 | Verify 4 figures exist | check files written to `figures/` |
| L-7-5 | Log summary | print alpha, beta, AUROCs, CI, gate_pass to console/log |

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual h-m2 Code)

```python
# From: h-m2/code/stats.py (ACTUAL CODE, copy verbatim into h-m3/code/stats.py)
def compute_correlation(consistencies: list[float], correctness: list[bool]) -> dict:
    """t-test, AUROC, Cohen's d for consistency vs correctness. HIGH consistency = correct."""
    ...

def pearson_entropy_consistency(entropies: list[float], consistencies: list[float]) -> float:
    """Pearson r between entropy and consistency."""
    ...
```

```python
# From: h-m2/code/results/h-m2_results.json (ACTUAL DATA SCHEMA, verified)
# results[i] = {
#   "qid": str, "question": str,
#   "entropy": float, "consistency": float,
#   "correct": bool,              # <-- verified field name, NOT "label"/"is_correct"
#   "majority_answer": str
# }
```

**Verified from**: `h-m2/code/stats.py` and `h-m2/code/results/h-m2_results.json` (actual implementation/data, N=20 questions, not spec).
**Note**: h-m2 is a sibling folder, not an installed package. Phase 4 copies functions/schema, does not `import` cross-folder.
