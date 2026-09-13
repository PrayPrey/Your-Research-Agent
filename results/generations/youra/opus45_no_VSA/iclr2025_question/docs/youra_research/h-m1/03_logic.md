# Logic: h-m1 (MECHANISM)

**Applied**: Standard PyTorch/sklearn (no diffusion-model KB match relevant; scipy.stats.chi2 LRT gist pattern per experiment brief)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: API signatures verified from actual code in `h-e1/code/` (not spec) — all match architecture.md exactly, no deviations found beyond the CONFIG-dict note already captured in 03_architecture.md.
**Analyzed Path**: `docs/youra_research/h-e1/code/{model.py, data.py, config.py}`
**Relevant Symbols**: `load_model`, `extract_all_scores`, `load_truthfulqa_mc1`, `build_prompts`, `stratified_folds`, `CONFIG`

---

## External Dependencies (Base Hypothesis)

```python
# From: h-e1/code/config.py (ACTUAL CODE)
CONFIG = {
    "seed": 42, "model_id": "meta-llama/Llama-2-7b-hf", "device": "cuda",
    "target_layers": (24, 31), "n_folds": 5, "dataset": "truthful_qa",
    "dataset_config": "multiple_choice", "batch_size": 4, ...
}

# From: h-e1/code/data.py (ACTUAL CODE)
def load_truthfulqa_mc1() -> list[dict]: ...
    # returns [{"question": str, "choices": list[str], "labels": list[int]}]

def build_prompts(samples: list[dict]) -> tuple[list[str], "np.ndarray"]: ...
    # flattens to (prompt, label) pairs -> (prompts, labels[N])

def stratified_folds(labels, n_folds=None, seed=None):
    # returns StratifiedKFold.split() generator -> yields (train_idx, test_idx)

# From: h-e1/code/model.py (ACTUAL CODE)
def load_model(model_id=None, device=None) -> "HookedTransformer": ...

def extract_all_scores(model, prompts, batch_size=None) -> dict: ...
    # returns {"nti": [N], "trajectory": [N, num_layers], "baseline_entropy": [N]}
    # num_layers = target_layers[1]-target_layers[0]+1 = 8 (layers 24-31)
```

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation, Serena `find_symbol` inspection). No parameter-name deviations from `03_architecture.md`.

---

## B-1/B-2: Setup & Config, Data/Model Reuse [Complexity: 4+5, Budget: 0 new subtasks]

**Applied**: dict-merge config extension (stdlib)

```python
# config.py
from h_e1.code.config import CONFIG as BASE_CONFIG

CONFIG = {
    **BASE_CONFIG,
    "lrt_df": 2,
    "auroc_gain_threshold": 0.03,
    "lrt_pvalue_threshold": 0.05,
    "falsify_gain": 0.02,
    "falsify_pvalue": 0.10,
    "figures_dir": "figures/",
}
```

No new data/model code — `load_truthfulqa_mc1`, `build_prompts`, `stratified_folds`, `load_model`, `extract_all_scores` imported directly from `h_e1.code.{data,model}` per External Dependencies above. B-2 is pure import wiring in `run.py`, no subtask needed.

---

## B-3: CMI Implementation [Complexity: 8, Budget: 1 subtask]

**Applied**: numpy vectorized diff (stdlib numpy, no new dependency)

```python
def compute_cmi(trajectory: "np.ndarray") -> "np.ndarray":
    """Convergence Monotonicity Index. trajectory: [N, L] -> cmi: [N]"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| trajectory | [N, 8] | per-layer entropy, layers 24-31 |
| cmi | [N] | higher = more monotonic entropy decrease |

### Pseudo-code

```
diffs = trajectory[:, 1:] - trajectory[:, :-1]   # [N, L-1]
cmi = -mean(diffs, axis=1)                       # negative mean slope = convergence
# optional refinement: replace with per-row Spearman corr(layer_idx, entropy) if
# mean-diff saturates (ablation decision, not required for MECHANISM gate)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-B3-1 | cmi.py | `compute_cmi` via negative mean layer-to-layer entropy diff |

---

## B-4/B-5/B-6: Feature Matrix, Fit+LRT, CV Aggregation [Complexity: 3+9+8, Budget: 2 subtasks]

**Applied**: sklearn LogisticRegression + scipy.stats.chi2 LRT (standard pattern, no new dep)

```python
def build_feature_matrices(h_l: "np.ndarray", nti: "np.ndarray", cmi: "np.ndarray"):
    # h_l, nti, cmi: [N] each -> X_null [N,1], X_full [N,3]
    ...

def fit_and_compare(X_null, X_full, y, C: float = 1.0, max_iter: int = 1000) -> dict:
    """Fit null vs full LogisticRegression, compute AUROC + LRT G/p."""
    ...

def run_cv_lrt(X_null, X_full, y, n_folds: int = 5, seed: int = 42) -> dict:
    """Per-fold fit_and_compare via stratified_folds, aggregate."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| X_null | [N, 1] | H_L only |
| X_full | [N, 3] | H_L, NTI, CMI |
| y | [N] | binary correctness label |

### Pseudo-code (fit_and_compare — LRT)

```
clf_null = LogisticRegression(C=C, max_iter=max_iter).fit(X_null_train, y_train)
clf_full = LogisticRegression(C=C, max_iter=max_iter).fit(X_full_train, y_train)
prob_null = clf_null.predict_proba(X_null_test)[:, 1]
prob_full = clf_full.predict_proba(X_full_test)[:, 1]
LL_null = sum(y*log(prob_null) + (1-y)*log(1-prob_null))
LL_full = sum(y*log(prob_full) + (1-y)*log(1-prob_full))
G = 2 * (LL_full - LL_null)
p_value = chi2.sf(G, df=CONFIG["lrt_df"])
auroc_gain = roc_auc_score(y, prob_full) - roc_auc_score(y, prob_null)
return {"null_auroc", "full_auroc", "auroc_gain", "G", "p_value",
        "null_coef", "full_coef", "null_prob", "full_prob"}
```

`run_cv_lrt` loops `stratified_folds(y)`, calls `fit_and_compare` per fold, aggregates `mean_auroc_gain` and combines p-values via Fisher's method (`scipy.stats.combine_pvalues`) into `combined_p_value`.

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-B5-1 | evaluate.py fit | `build_feature_matrices` + `fit_and_compare` (null/full LR, LRT G/p) |
| L-B6-1 | evaluate.py cv | `run_cv_lrt` fold loop + Fisher combined p-value aggregation |

---

## B-7: Gate Check [Complexity: 3, Budget: 0 new subtasks]

```python
def check_gate(cv_results: dict, config: dict) -> tuple[bool, str]:
    # PASS: mean_auroc_gain >= config["auroc_gain_threshold"] and combined_p_value < config["lrt_pvalue_threshold"]
    # FALSIFY: mean_auroc_gain < config["falsify_gain"] or combined_p_value >= config["falsify_pvalue"]
    ...
```

Trivial threshold comparison — folded into B-6 subtask, no separate subtask needed.

---

## B-8: Visualization [Complexity: 7, Budget: 1 subtask]

**Applied**: matplotlib standard plotting (stdlib-adjacent, already a dependency)

```python
def plot_gate_metrics(cv_results: dict, save_path: str) -> None: ...   # required
def plot_lrt_pvalue(cv_results: dict, save_path: str) -> None: ...      # required
def plot_roc_overlay(cv_results: dict, save_path: str) -> None: ...
def plot_fold_auroc_bars(cv_results: dict, save_path: str) -> None: ...
def plot_coefficients(cv_results: dict, save_path: str) -> None: ...
def plot_nti_cmi_scatter(nti, cmi, labels, save_path: str) -> None: ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-B8-1 | visualize.py | 6 plot functions (2 required: gate_metrics, lrt_pvalue) |

---

## B-9: Integration Run [Complexity: 6, Budget: 0 new subtasks]

```python
def main() -> None:
    samples = load_truthfulqa_mc1()
    prompts, y = build_prompts(samples)
    model = load_model()
    scores = extract_all_scores(model, prompts)          # nti, trajectory, baseline_entropy
    cmi = compute_cmi(scores["trajectory"])
    X_null, X_full = build_feature_matrices(scores["baseline_entropy"], scores["nti"], cmi)
    cv_results = run_cv_lrt(X_null, X_full, y, n_folds=CONFIG["n_folds"], seed=CONFIG["seed"])
    passed, reason = check_gate(cv_results, CONFIG)
    plot_gate_metrics(cv_results, f"{CONFIG['figures_dir']}/gate.png")
    plot_lrt_pvalue(cv_results, f"{CONFIG['figures_dir']}/lrt.png")
    print(f"PASS={passed}: {reason}")
```

Orchestration only, folded into B-6/B-8 subtasks — no separate subtask.

---

## Subtask Budget Summary [4/4 used]

| ID | File | Task |
|----|------|------|
| L-B3-1 | cmi.py | compute_cmi |
| L-B5-1 | evaluate.py | build_feature_matrices + fit_and_compare |
| L-B6-1 | evaluate.py | run_cv_lrt (+ check_gate, folded) |
| L-B8-1 | visualize.py | 6 plot functions |
