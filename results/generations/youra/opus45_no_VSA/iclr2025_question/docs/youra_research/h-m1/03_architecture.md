# Architecture: h-m1 (MECHANISM)

**Hypothesis**: [H_L + NTI + CMI] improves AUROC >= 0.03 over H_L alone, LRT p < 0.05

Applied: no direct KB match (diffusion-model docs only); using standard sklearn LogisticRegression + scipy.stats.chi2 LRT pattern per experiment brief.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1, VALIDATED)
**Status**: Actual code inspected in `h-e1/code/`; matches its 03_architecture.md specs closely, with one deviation noted below.
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**:
- `model.py::extract_all_scores(model, prompts, batch_size=None)` returns `{"nti", "trajectory", "baseline_entropy"}` — **no CMI**, must be computed new from `trajectory` (per-layer entropy array, layers 24-32).
- `config.py` exports a single dict constant `CONFIG` (not flat module-level vars as h-e1's own spec doc implied) — h-m1 must `from h_e1.code.config import CONFIG` and read keys, not `import SEED, MODEL_ID`.
- `data.py` (`load_truthfulqa_mc1`, `build_prompts`, `stratified_folds`) and `evaluate.py` (`run_cv`, `check_gate`) signatures confirmed as specced — safe to reuse directly for data loading; `run_cv`/`check_gate` are EXISTENCE-specific (single-feature gate) and NOT reused, h-m1 needs its own CV+LRT evaluator.

---

## File Structure (MECHANISM - full)

```
h-m1/code/
├── config.py       # CONFIG dict extending h-e1's (adds CMI params, LRT df)
├── cmi.py          # NEW: Convergence Monotonicity Index from trajectory
├── evaluate.py      # null vs full LogisticRegression, AUROC gain, LRT
├── visualize.py     # ROC overlay, per-fold bars, coefficients, gate/LRT figs
└── run.py           # orchestrates: h-e1 data/model reuse -> cmi -> evaluate -> visualize
```

No new `data.py` or `model.py` — imported directly from `h-e1/code/`.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| CONFIG | `from h_e1.code.config import CONFIG` | `h-e1/code/config.py` |
| load_truthfulqa_mc1 | `from h_e1.code.data import load_truthfulqa_mc1` | `h-e1/code/data.py` |
| build_prompts | `from h_e1.code.data import build_prompts` | `h-e1/code/data.py` |
| stratified_folds | `from h_e1.code.data import stratified_folds` | `h-e1/code/data.py` |
| load_model | `from h_e1.code.model import load_model` | `h-e1/code/model.py` |
| extract_all_scores | `from h_e1.code.model import extract_all_scores` | `h-e1/code/model.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation, via Serena symbol inspection)

**Note**: `extract_all_scores` output dict has keys `nti`, `trajectory`, `baseline_entropy`. `baseline_entropy` = H_L. `trajectory` (shape `[N, num_layers]`) is the input to CMI computation.

---

## Module Interfaces

### config.py (`code/config.py`)

**Dependencies**: h_e1.code.config.CONFIG

```python
from h_e1.code.config import CONFIG as BASE_CONFIG

CONFIG = {
    **BASE_CONFIG,
    "lrt_df": 2,                # NTI + CMI added params
    "auroc_gain_threshold": 0.03,
    "lrt_pvalue_threshold": 0.05,
    "falsify_gain": 0.02,
    "falsify_pvalue": 0.10,
    "figures_dir": "figures/",
}
```

### cmi.py (`code/cmi.py`)

**Dependencies**: numpy

```python
def compute_cmi(trajectory: "np.ndarray") -> "np.ndarray": ...
    # trajectory: [N, num_layers] per-layer entropy (from h-e1 extract_all_scores)
    # returns cmi[N]: monotonicity of entropy decrease across layers
    # e.g. cmi = -mean(diff(trajectory, axis=1)) or Spearman corr(layer_idx, entropy)
```

### evaluate.py (`code/evaluate.py`)

**Dependencies**: config, sklearn, scipy.stats

```python
def build_feature_matrices(h_l: "np.ndarray", nti: "np.ndarray", cmi: "np.ndarray"):
    # -> X_null [N,1] (H_L only), X_full [N,3] (H_L, NTI, CMI)

def fit_and_compare(X_null, X_full, y, C=1.0, max_iter=1000) -> dict: ...
    # returns {"null_auroc", "full_auroc", "auroc_gain", "G", "p_value",
    #          "null_coef", "full_coef", "null_prob", "full_prob"}

def run_cv_lrt(X_null, X_full, y, n_folds=5, seed=42) -> dict: ...
    # per-fold fit_and_compare, aggregate
    # returns {"fold_results": list[dict], "mean_auroc_gain": float,
    #          "combined_p_value": float, "pass": bool}

def check_gate(cv_results: dict, config: dict) -> tuple[bool, str]: ...
    # applies auroc_gain_threshold / lrt_pvalue_threshold vs falsification bounds
```

### visualize.py (`code/visualize.py`)

**Dependencies**: config, matplotlib

```python
def plot_gate_metrics(cv_results: dict, save_path: str) -> None: ...   # required
def plot_lrt_pvalue(cv_results: dict, save_path: str) -> None: ...      # required
def plot_roc_overlay(cv_results: dict, save_path: str) -> None: ...
def plot_fold_auroc_bars(cv_results: dict, save_path: str) -> None: ...
def plot_coefficients(cv_results: dict, save_path: str) -> None: ...
def plot_nti_cmi_scatter(nti, cmi, labels, save_path: str) -> None: ...
```

### run.py (`code/run.py`)

**Dependencies**: h_e1.code.{config,data,model}, cmi, evaluate, visualize

```python
def main() -> None: ...
    # load h-e1 data+folds -> load_model -> extract_all_scores (nti, trajectory, H_L)
    # -> compute_cmi(trajectory) -> build_feature_matrices -> run_cv_lrt
    # -> check_gate -> visualize -> print summary
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| B-1 | Setup & config | config.py extending h-e1 CONFIG, import wiring | 4 | 1+2+1+0 |
| B-2 | Reuse h-e1 data/model | Verify imports of load_truthfulqa_mc1, build_prompts, stratified_folds, load_model, extract_all_scores | 5 | 1+3+0+1 |
| B-3 | CMI implementation | compute_cmi from trajectory array (monotonicity metric) | 8 | 2+1+4+1 |
| B-4 | Feature matrix build | build_feature_matrices (H_L, NTI, CMI concat) | 3 | 1+1+1+0 |
| B-5 | Null/full model fit + LRT | fit_and_compare (LogisticRegression x2, chi2 LRT) | 9 | 2+2+4+1 |
| B-6 | 5-fold CV aggregation | run_cv_lrt across folds, combined p-value | 8 | 2+3+2+1 |
| B-7 | Gate check | check_gate vs success/falsification thresholds | 3 | 1+1+1+0 |
| B-8 | Visualization | 6 figures (2 required + 4 optional) | 7 | 2+1+2+2 |
| B-9 | Integration run | run.py end-to-end + smoke test | 6 | 2+3+1+0 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [B-5, B-6], Low(4-8): [B-1, B-2, B-3, B-4, B-7, B-8, B-9]

---

## Notes

- No new model/data loading code — full reuse of h-e1 via cross-hypothesis import.
- CMI is the only genuinely new algorithmic component; scored highest complexity accordingly.
- LRT statistical logic follows Exa-sourced gist pattern cited in experiment brief (sklearn + scipy.stats.chi2), no new dependency needed.
