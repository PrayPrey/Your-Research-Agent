# Architecture: h-m2

**Applied**: Bootstrap-CI evaluation pattern (sklearn `roc_auc_score` + percentile bootstrap) — Archon KB

**Type**: MECHANISM (evaluation-only, single-script)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: Patterns found from base code, but **h-e1 does NOT persist per-sample arrays**.
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**:
- `h-e1/code/run.py` computes `scores["nti"]`, `scores["baseline_entropy"]`, `labels` in-memory via `model.extract_all_scores()` and only writes aggregate CV metrics to `outputs/results.json` (no raw per-sample `.npy`/`.csv`).
- `h-e1/code/model.py::extract_all_scores(model, prompts)` returns `{"nti": (N,), "trajectory": (N, L), "baseline_entropy": (N,)}`; `h-e1/code/data.py::build_prompts(samples)` returns `(prompts, labels)`.
- `h-e1/code/config.py`: `target_layers=(24,31)`, `seed=42`, `model_id="meta-llama/Llama-2-7b-hf"`.

**Consequence for h-m2**: PRD requires "reuse h-e1 features, no recomputation," but no cached raw array file exists. Resolution: h-m2's `run_h_m2.py` first checks for a cached raw-features file (`h-m2/code/outputs/h_e1_features.npz`); if absent, it imports h-e1's `data.py`/`model.py`/`config.py` directly (via `sys.path` insert to `h-e1/code`) to regenerate `H_L` (= `baseline_entropy`), `NTI`, `labels` **once**, and caches them to `.npz` for all subsequent runs. This is a one-time reuse of h-e1's validated pipeline, not new feature engineering.

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| load_truthfulqa_mc1, build_prompts | `from data import load_truthfulqa_mc1, build_prompts` | `h-e1/code/data.py` |
| load_model, extract_all_scores | `from model import load_model, extract_all_scores` | `h-e1/code/model.py` |
| CONFIG (h-e1) | `from config import CONFIG as H_E1_CONFIG` | `h-e1/code/config.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation, not specs)

---

## Module Structure (Single Script)

### `run_h_m2.py` (`h-m2/code/run_h_m2.py`)

**Dependencies**: h-e1 code (fallback only), numpy, sklearn, scipy, matplotlib

```python
def load_or_build_features(cache_path: str, h_e1_code_dir: str) -> dict: ...
    # returns {"H_L": (817,), "NTI": (817,), "labels": (817,)}

def filter_low_entropy(H_L: np.ndarray, labels: np.ndarray, nti: np.ndarray,
                        percentile: float = 25) -> tuple: ...
    # returns (H_L_sub, labels_sub, nti_sub, mask)

def bootstrap_auroc_ci(y_true: np.ndarray, y_score: np.ndarray,
                        n_bootstrap: int = 1000, ci: float = 0.95,
                        seed: int = 42) -> dict: ...
    # returns {"auroc": float, "ci_lower": float, "ci_upper": float}

def check_gate(result: dict, auroc_threshold: float = 0.55,
                ci_lb_threshold: float = 0.50) -> bool: ...

def plot_auroc_comparison(full_result: dict, subset_result: dict, out_path: str) -> str: ...
def plot_entropy_histogram(H_L: np.ndarray, threshold: float, out_path: str) -> str: ...
def plot_roc_subset(y_true: np.ndarray, y_score: np.ndarray, out_path: str) -> str: ...

def main() -> bool: ...
```

### `config.py` (`h-m2/code/config.py`)

```python
CONFIG = {
    "seed": 42,
    "percentile": 25,
    "n_bootstrap": 1000,
    "ci": 0.95,
    "auroc_threshold": 0.55,
    "ci_lb_threshold": 0.50,
    "h_e1_code_dir": "<abs path to h-e1/code>",
    "feature_cache": "outputs/h_e1_features.npz",
    "outputs_dir": "outputs",
    "figures_dir": "figures",
}
```

No `model.py` / `train.py` — evaluation-only, no gradient computation.

---

## Data Flow

1. **Load/cache features** — `load_or_build_features()`:
   - If `outputs/h_e1_features.npz` exists → `np.load()` directly (fast path, no recomputation).
   - Else → import `h-e1/code/{data,model,config}.py`, run `load_truthfulqa_mc1()` → `build_prompts()` → `load_model()` → `extract_all_scores()`, save `{H_L: baseline_entropy, NTI: nti, labels}` to `.npz`.
2. **Filter** — `filter_low_entropy(H_L, labels, NTI, percentile=25)` → boolean mask, ~204/817 samples where `H_L < np.percentile(H_L, 25)`.
3. **Evaluate** — `bootstrap_auroc_ci(labels_sub, NTI_sub, n_bootstrap=1000, seed=42)` → point AUROC + 95% CI via 1000 resamples with replacement.
4. **Gate check** — `check_gate()`: pass iff `auroc > 0.55` and `ci_lower > 0.50`.
5. **Visualize** — 3 figures (gate comparison bar chart, H_L histogram w/ cutoff line, ROC curve on subset).
6. **Persist** — write `outputs/results.json` with metrics, threshold, gate_passed, mask size, figure paths.

---

## File I/O

| Path | Role |
|------|------|
| `h-e1/code/data.py`, `model.py`, `config.py` | Read-only import (fallback feature regeneration) |
| `h-m2/code/outputs/h_e1_features.npz` | Cached `{H_L, NTI, labels}` arrays (817,) each |
| `h-m2/code/outputs/results.json` | Final metrics: `auroc`, `ci_lower`, `ci_upper`, `n_subset`, `gate_passed` |
| `h-m2/figures/auroc_comparison.png` | Required deliverable |
| `h-m2/figures/entropy_histogram.png` | Optional |
| `h-m2/figures/roc_curve_subset.png` | Optional |

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Feature loader | `load_or_build_features()` with cache + h-e1 fallback import | 8 | 3+2+2+1 |
| A-2 | Low-entropy filter | `filter_low_entropy()`, verify ~204 samples | 4 | 1+1+1+1 |
| A-3 | Bootstrap AUROC+CI | `bootstrap_auroc_ci()`, 1000 iters, seed 42 | 6 | 2+1+2+1 |
| A-4 | Gate check | `check_gate()` against thresholds | 3 | 1+1+1+0 |
| A-5 | Figures | 3 plotting functions | 6 | 2+2+1+1 |
| A-6 | Orchestration + results.json | `main()` wiring + JSON output | 5 | 2+1+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1, A-2, A-3, A-4, A-5, A-6]
