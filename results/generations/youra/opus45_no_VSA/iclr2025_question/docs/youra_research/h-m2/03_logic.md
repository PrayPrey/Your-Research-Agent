# Logic: h-m2

**Applied**: Standard sklearn (roc_auc_score + percentile bootstrap)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1, VALIDATED, gate_passed=true, mean_auroc=0.5657)
**Status**: API signatures verified from actual code at `docs/youra_research/h-e1/code/`
**Analyzed Path**: `docs/youra_research/h-e1/code/{run.py,evaluate.py,model.py,data.py}`
**Relevant Symbols**: `run_cv` (evaluate.py), `main` (run.py)

**Critical finding**: h-e1's `run.py` only persists an **aggregate** `outputs/results.json`
(fold AUROCs, mean/min AUROC). It does **not** save per-sample `H_L`, `NTI`, or `labels`
arrays to disk — `scores["nti"]`, `scores["trajectory"]`, and `labels` exist only in-memory
during `run.py::main()`. The h-m2 PRD assumes a per-sample feature file exists.

**Resolution**: `load_h_e1_features` targets `outputs/features.npz` (keys: `h_l`, `nti`,
`labels`), matching the array names used internally (`cv_results`/`scores` dict keys in
h-e1's `evaluate.py` and `model.py`). This file does not currently exist — h-e1's `run.py`
must be extended with one `np.savez` call before h-m2 can run. This is a data-artifact gap,
not an API mismatch; no h-e1 code is called from h-m2, so no signature drift risk. Noting
here rather than silently assuming the file exists.

---

## A-1: Low-Entropy Subset AUROC Gate [Complexity: 3, Budget: 3]

### API Signatures

```python
import numpy as np
from sklearn.metrics import roc_auc_score
from typing import Tuple, Dict


def load_h_e1_features(path: str) -> Dict[str, np.ndarray]:
    """Load H_L, NTI, labels from h-e1 outputs/features.npz."""
    data = np.load(path)
    return {"h_l": data["h_l"], "nti": data["nti"], "labels": data["labels"]}


def filter_low_entropy(
    h_l: np.ndarray,      # [N]
    labels: np.ndarray,   # [N]
    nti: np.ndarray,      # [N]
    percentile: float = 25,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Keep samples with H_L below given percentile. Returns (h_l, labels, nti) filtered."""
    threshold = np.percentile(h_l, percentile)
    mask = h_l < threshold
    return h_l[mask], labels[mask], nti[mask]


def compute_auroc_with_ci(
    scores: np.ndarray,   # [M]
    labels: np.ndarray,   # [M]
    n_bootstrap: int = 1000,
    ci: float = 0.95,
    seed: int = 42,
) -> Tuple[float, float, float]:
    """AUROC + percentile bootstrap CI. Returns (auroc, ci_lower, ci_upper)."""
    ...


def main() -> bool:
    """Load -> filter -> AUROC+CI -> print -> figure. Returns gate_passed."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| h_l, nti, labels | [817] | Full TruthfulQA MC1 set (from h-e1) |
| h_l_lo, nti_lo, labels_lo | [~204] | After 25th-percentile filter |
| boot_aurocs | [1000] | Bootstrap resample AUROCs |

### Pseudo-code (bootstrap CI — only non-trivial part)

```
1. rng = np.random.default_rng(seed)
2. auroc = roc_auc_score(labels, scores)
3. for i in range(n_bootstrap):
       idx = rng.integers(0, len(scores), len(scores))   # resample w/ replacement
       if len(unique(labels[idx])) < 2: skip / retry      # need both classes
       boot_aurocs[i] = roc_auc_score(labels[idx], scores[idx])
4. alpha = (1 - ci) / 2
5. ci_lower, ci_upper = np.percentile(boot_aurocs, [alpha*100, (1-alpha)*100])
6. return auroc, ci_lower, ci_upper
```

### Implementation (copy-paste ready)

```python
def compute_auroc_with_ci(scores, labels, n_bootstrap=1000, ci=0.95, seed=42):
    rng = np.random.default_rng(seed)
    auroc = roc_auc_score(labels, scores)

    n = len(scores)
    boot_aurocs = []
    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, n)
        y_b, s_b = labels[idx], scores[idx]
        if len(np.unique(y_b)) < 2:
            continue  # ponytail: drop degenerate resamples, rare at n~204
        boot_aurocs.append(roc_auc_score(y_b, s_b))

    alpha = (1 - ci) / 2
    ci_lower, ci_upper = np.percentile(boot_aurocs, [alpha * 100, (1 - alpha) * 100])
    return auroc, ci_lower, ci_upper


def main():
    feats = load_h_e1_features("outputs/features.npz")
    h_l_lo, labels_lo, nti_lo = filter_low_entropy(
        feats["h_l"], feats["labels"], feats["nti"], percentile=25
    )

    auroc, ci_lo, ci_hi = compute_auroc_with_ci(nti_lo, labels_lo, n_bootstrap=1000, seed=42)

    gate_passed = auroc > 0.55 and ci_lo > 0.50
    print(f"N low-entropy samples: {len(h_l_lo)}")
    print(f"AUROC: {auroc:.4f}  95% CI: [{ci_lo:.4f}, {ci_hi:.4f}]")
    print(f"Gate: {'PASS' if gate_passed else 'FAIL'}")

    _plot_auroc_comparison(auroc, ci_lo, ci_hi, out="figures/auroc_comparison.png")
    return gate_passed


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Feature loading + filtering | `load_h_e1_features`, `filter_low_entropy` |
| L-1-2 | AUROC + bootstrap CI | `compute_auroc_with_ci` |
| L-1-3 | Orchestration + figure | `main()`, bar chart of AUROC with CI whiskers vs 0.55/0.50 thresholds |

---

## External Dependencies (Base Hypothesis)

No h-e1 **functions** are called by h-m2 — only h-e1's **output data** is consumed. No API
signature dependency exists. The only dependency is the data file `outputs/features.npz`,
which must be produced by extending h-e1's `run.py` with:

```python
# add to h-e1/code/run.py after Step 3 (Extract scores), before results are discarded
np.savez(
    os.path.join(CONFIG["outputs_dir"], "features.npz"),
    h_l=scores["trajectory"].mean(axis=-1),  # or appropriate H_L reduction — verify against model.py compute_baseline_entropy
    nti=scores["nti"],
    labels=np.array(labels),
)
```

**Verify before use**: `compute_baseline_entropy` in `docs/youra_research/h-e1/code/model.py`
defines how `H_L` is actually computed from `scores["trajectory"]` — confirm the reduction
(mean/last-token/etc.) matches h-m2's PRD definition of "H_L" before wiring this up in Phase 4.
