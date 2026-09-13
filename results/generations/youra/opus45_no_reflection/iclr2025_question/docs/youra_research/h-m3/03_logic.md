# Logic: H-M3 (Linear Correctness Probe)

Applied: sklearn LogisticRegression linear probe (SEP / concept-probes / OpenInterpretability pattern)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze (H-M2 provides data artifacts `.pt` only, no code)
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Data loading [Complexity: 6, Budget: 6]

**Applied**: torch.load + numpy conversion

### API Signatures

```python
def load_hidden_states(h_m2_folder: str) -> tuple[np.ndarray, np.ndarray]:
    """Load hidden states/labels from H-M2 .pt files. Returns (X, y)."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| X | (11200, 4096) | float32, from `hidden_states_l15.pt` |
| y | (11200,) | int, binary labels from `correctness_labels.pt` |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | torch.load hidden states | `torch.load(f"{h_m2_folder}/hidden_states_l15.pt")` -> `.numpy()` |
| L-1-2 | torch.load labels | `torch.load(f"{h_m2_folder}/correctness_labels.pt")` -> `.numpy()` |
| L-1-3 | Shape assertion | `assert X.shape == (11200, 4096)`, `assert y.shape == (11200,)` |
| L-1-4 | dtype cast | `X.astype(np.float32)`, `y.astype(np.int64)` |

---

## A-2: Train/val split + scaling [Complexity: 5, Budget: 5]

**Applied**: Fixed-index split (no shuffling, deterministic per PRD) + sklearn StandardScaler

### API Signatures

```python
def split_train_val(X: np.ndarray, y: np.ndarray, n_train: int = 9500) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Fixed split: first n_train rows -> train, remainder -> val."""
    ...  # returns X_train, y_train, X_val, y_val

def scale_features(X_train: np.ndarray, X_val: np.ndarray) -> tuple[np.ndarray, np.ndarray, StandardScaler]:
    """Fit StandardScaler on train, transform both."""
    ...
```

### Tensor Shapes

| Variable | Shape |
|----------|-------|
| X_train | (9500, 4096) |
| X_val | (1700, 4096) |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | Split logic | `X[:n_train], X[n_train:]` slicing |
| L-2-2 | Scaler fit/transform | `scaler.fit_transform(X_train)`, `scaler.transform(X_val)` |
| L-2-3 | Shape verify | assert train=9500, val=1700 rows |
| L-2-4 | Return scaler | pass fitted `StandardScaler` object onward for reuse in probe |

---

## A-3: Random baseline [Complexity: 6, Budget: 6]

**Applied**: random-direction dot-product baseline (OpenInterpretability probes.py pattern)

### API Signatures

```python
class RandomBaseline:
    def __init__(self, d_model: int = 4096, seed: int = 42):
        """Generates unit-norm random direction."""
        ...

    def score(self, X: np.ndarray) -> np.ndarray:
        """X: [N, 4096] -> scores: [N]. scores = X @ random_direction."""
        ...
```

### Pseudo-code (5-seed CI)

```
aurocs = []
for seed in [42, 43, 44, 45, 46]:
    rng = np.random.default_rng(seed)
    direction = rng.standard_normal(d_model).astype(np.float32)
    direction /= np.linalg.norm(direction) + 1e-8
    scores = X_val @ direction
    aurocs.append(roc_auc_score(y_val, scores))
mean_auroc, std_auroc = np.mean(aurocs), np.std(aurocs)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Direction init | `rng.standard_normal(d_model)`, unit-normalize |
| L-3-2 | score() method | `X @ self.direction` |
| L-3-3 | 5-seed loop | seeds 42-46, collect AUROC list |
| L-3-4 | CI summary | mean/std dict `{"mean": .., "std": ..}` |

---

## A-4: Linear probe implementation [Complexity: 7, Budget: 7]

**Applied**: sklearn LogisticRegression probe (SEP/concept-probes pattern, verified in experiment brief)

### API Signatures

```python
class LinearCorrectnessProbe:
    def __init__(self, C: float = 1e-3, max_iter: int = 2000):
        """clf = LogisticRegression(C=C, max_iter=max_iter, class_weight='balanced', solver='lbfgs')"""
        ...

    def fit(self, X_train: np.ndarray, y_train: np.ndarray) -> "LinearCorrectnessProbe":
        """X_train: [N_train, 4096] (already scaled). Fits internal clf."""
        ...

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """X: [N, 4096] (scaled) -> probs: [N]. Returns clf.predict_proba(X)[:, 1]."""
        ...

    def evaluate(self, X_val: np.ndarray, y_val: np.ndarray) -> float:
        """Returns roc_auc_score(y_val, self.predict_proba(X_val))."""
        ...
```

Note: scaling is done externally by `scale_features` (A-2) per architecture's data-flow; probe operates on pre-scaled arrays.

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | `__init__` | instantiate `LogisticRegression(C, max_iter, class_weight='balanced', solver='lbfgs')` |
| L-4-2 | `fit()` | `self.clf.fit(X_train, y_train)`, return self |
| L-4-3 | `predict_proba()` | `self.clf.predict_proba(X)[:, 1]` |
| L-4-4 | `evaluate()` | wrap `roc_auc_score` |

---

## A-5: Probe training run [Complexity: 6, Budget: 6]

### API Signatures

```python
def train_probe(X_train: np.ndarray, y_train: np.ndarray, C: float = 1e-3, max_iter: int = 2000) -> tuple[LinearCorrectnessProbe, dict]:
    """Fits probe, returns (probe, convergence_info)."""
    ...  # convergence_info: {"n_iter": int, "converged": bool}
```

### Pseudo-code

```
probe = LinearCorrectnessProbe(C=C, max_iter=max_iter).fit(X_train, y_train)
n_iter = probe.clf.n_iter_[0]
converged = n_iter < max_iter
log(f"Probe training completed with {n_iter} iterations")
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | Instantiate + fit | call A-4 probe |
| L-5-2 | Extract n_iter | `probe.clf.n_iter_[0]` |
| L-5-3 | Convergence check | `n_iter < max_iter` |
| L-5-4 | Log message | per mechanism_log_message spec |

---

## A-6: Evaluation metrics [Complexity: 6, Budget: 6]

### API Signatures

```python
def compute_metrics(y_val: np.ndarray, probs: np.ndarray) -> dict:
    """Returns {"auroc": float, "accuracy": float}. Accuracy at threshold 0.5."""
    ...

def compare_to_baseline(probe_auroc: float, baseline_auroc: float) -> dict:
    """Returns {"delta": float, "exceeds_baseline": bool}."""
    ...
```

### Pseudo-code

```
auroc = roc_auc_score(y_val, probs)
y_pred = (probs >= 0.5).astype(int)
accuracy = accuracy_score(y_val, y_pred)
delta = probe_auroc - baseline_auroc
exceeds_baseline = delta > 0.20
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | AUROC calc | `roc_auc_score` |
| L-6-2 | Accuracy calc | threshold at 0.5, `accuracy_score` |
| L-6-3 | Baseline delta | `probe_auroc - baseline_auroc` |
| L-6-4 | Gate check dict | `{"auroc": .., "accuracy": .., "gate_pass": auroc >= 0.70}` |

---

## A-7: Mechanism verification [Complexity: 5, Budget: 5]

**Applied**: assertion-based mechanism check (per experiment brief `verify_mechanism`)

### API Signatures

```python
def verify_mechanism(probe: LinearCorrectnessProbe, X_val: np.ndarray, y_val: np.ndarray) -> dict:
    """Returns {"weight_norm": float, "pred_std": float, "auroc": float}. Raises AssertionError on failure."""
    ...
```

### Pseudo-code

```
weights = probe.clf.coef_[0]                    # [4096]
weight_norm = np.linalg.norm(weights)
assert weight_norm > 1e-6, "Weights collapsed to zero"

probs = probe.predict_proba(X_val)               # [N]
assert probs.std() > 0.01, "Predictions are constant"

auroc = roc_auc_score(y_val, probs)
assert auroc > 0.55, f"AUROC {auroc} not significantly above random"

return {"weight_norm": weight_norm, "pred_std": probs.std(), "auroc": auroc}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | weight_norm check | `np.linalg.norm(clf.coef_[0]) > 1e-6` |
| L-7-2 | pred_std check | `probs.std() > 0.01` |
| L-7-3 | AUROC>0.55 check | assert against random floor |
| L-7-4 | Return dict | consolidate 3 metrics |

---

## A-8: Fallback MLP protocol [Complexity: 7, Budget: 7]

**Applied**: conditional 2-layer MLP fallback (per PRD FR-7)

### API Signatures

```python
class MLPFallbackProbe:
    def __init__(self, hidden_layer_sizes: tuple = (256,), max_iter: int = 500):
        """MLPClassifier(hidden_layer_sizes, max_iter, early_stopping=True)"""
        ...

    def fit(self, X_train: np.ndarray, y_train: np.ndarray) -> "MLPFallbackProbe":
        ...

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Returns probs: [N] (positive class column)."""
        ...
```

### Pseudo-code (conditional trigger)

```
if linear_auroc < 0.70:
    mlp = MLPFallbackProbe(hidden_layer_sizes=(256,), max_iter=500).fit(X_train, y_train)
    mlp_probs = mlp.predict_proba(X_val)
    mlp_auroc = roc_auc_score(y_val, mlp_probs)
    results["mlp_auroc"] = mlp_auroc
    results["fallback_triggered"] = True
else:
    results["fallback_triggered"] = False
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | `__init__` | `MLPClassifier(hidden_layer_sizes, max_iter, early_stopping=True)` |
| L-8-2 | `fit`/`predict_proba` | mirror LinearCorrectnessProbe interface |
| L-8-3 | Trigger condition | `if linear_auroc < 0.70` |
| L-8-4 | Result merge | add `mlp_auroc`, `fallback_triggered` to results dict |

---

## A-9: Visualization [Complexity: 6, Budget: 6]

### API Signatures

```python
def plot_gate_comparison(achieved_auroc: float, threshold: float, out_path: str) -> None:
    """Bar chart: achieved vs threshold (0.70). Saves to out_path."""
    ...

def plot_roc_curve(y_val: np.ndarray, probs: np.ndarray, auroc: float, out_path: str) -> None:
    """ROC curve via sklearn.metrics.roc_curve, annotated with AUC."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-9-1 | Gate bar chart | matplotlib bar: `["achieved", "threshold"]` vs `[achieved_auroc, 0.70]` |
| L-9-2 | Save gate fig | `fig.savefig(out_path)` |
| L-9-3 | ROC curve calc | `fpr, tpr, _ = roc_curve(y_val, probs)` |
| L-9-4 | Save ROC fig | plot + annotate AUC + `savefig` |

---

## A-10: End-to-end orchestration [Complexity: 7, Budget: 7]

### API Signatures

```python
def main(h_m2_folder: str, hypothesis_folder: str) -> dict:
    """Runs full pipeline: load->split->scale->baseline->probe->eval->verify->[fallback]->visualize->save.
    Returns final results dict, writes results.json to hypothesis_folder."""
    ...
```

### Pseudo-code

```
1. X, y = load_hidden_states(h_m2_folder)
2. X_train, y_train, X_val, y_val = split_train_val(X, y, N_TRAIN)
3. X_train_s, X_val_s, scaler = scale_features(X_train, X_val)
4. baseline_stats = RandomBaseline(...).score(X_val_s) -> 5-seed AUROC CI
5. probe, conv_info = train_probe(X_train_s, y_train, PROBE_C, PROBE_MAX_ITER)
6. probs = probe.predict_proba(X_val_s)
7. metrics = compute_metrics(y_val, probs)
8. mech = verify_mechanism(probe, X_val_s, y_val)
9. cmp = compare_to_baseline(metrics["auroc"], baseline_stats["mean"])
10. if metrics["auroc"] < AUROC_GATE: run MLP fallback (A-8)
11. plot_gate_comparison(metrics["auroc"], AUROC_GATE, f"{hypothesis_folder}/figures/gate_comparison.png")
12. plot_roc_curve(y_val, probs, metrics["auroc"], f"{hypothesis_folder}/figures/roc_curve.png")
13. results = {**metrics, **mech, **cmp, "baseline": baseline_stats, "convergence": conv_info}
14. json.dump(results, open(f"{hypothesis_folder}/results.json", "w"))
15. return results
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-10-1 | Pipeline wiring | steps 1-9 above, calling A-1..A-7 |
| L-10-2 | Fallback branch | step 10, calls A-8 |
| L-10-3 | Figure generation | steps 11-12, calls A-9 |
| L-10-4 | Results persistence | steps 13-15, JSON dump |

---

## External Data Dependencies

No prior hypothesis code to call (H-M2 = data artifacts only). Green-field APIs above are self-contained.

| Artifact | Path | Shape |
|----------|------|-------|
| Hidden states | `{h_m2_folder}/hidden_states_l15.pt` | (11200, 4096) |
| Labels | `{h_m2_folder}/correctness_labels.pt` | (11200,) |
