# Logic: H-M1 (Weight Matrices Encode Behavioral Information)

Applied: weight-statistics-extraction pattern (Unterthiner et al. 2020, per-layer mean/std/min/max/norm)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: Serena MCP had no registered project for this path; verified API signatures via direct `Read` of actual h-e1 source files (not specs).
**Analyzed Path**: `docs/youra_research/h-e1/code/model_zoo_loader.py`, `docs/youra_research/h-e1/code/analysis.py`
**Relevant Symbols**:
- `load_model_zoo_final_epoch(path, max_models=None) -> list[(model_id, state_dict, test_acc)]`
- `get_model_predictions_from_weights(model_entries, cifar_root, device='cpu', batch_size=256) -> dict[str, np.ndarray]`
- `compute_class_wise_accuracy(predictions, ground_truth, n_classes) -> (class_wise_acc, overall_acc, model_ids)`
- `stratified_baseline(class_wise_acc, overall_acc) -> (baseline_pred, class_difficulty)`

**Key deviation from PRD/brief**: PRD assumes flat `(N, 4970)` weight arrays; actual data is `OrderedDict` state_dicts with 5 named tensors (`module_list.{0,3,6,9,11}.weight`). `extract_layer_statistics` below operates on real state_dict format.

---

## External Dependencies API (From Actual h-e1 Code)

```python
# From: h-e1/code/model_zoo_loader.py (ACTUAL CODE, copied into h-m1/code/base/)
def load_model_zoo_final_epoch(path: str, max_models: int = None) -> list:
    """Returns [(model_id: str, state_dict: OrderedDict, test_acc: float), ...]"""
    ...

def get_model_predictions_from_weights(
    model_entries: list, cifar_root: str, device: str = 'cpu', batch_size: int = 256
) -> dict:
    """Returns {model_id: preds}, preds shape (10000,) int array"""
    ...

# From: h-e1/code/analysis.py (ACTUAL CODE, copied into h-m1/code/base/)
def compute_class_wise_accuracy(
    predictions: dict, ground_truth: np.ndarray, n_classes: int
) -> tuple:
    """Returns (class_wise_acc [N,10], overall_acc [N,], model_ids: list[str])"""
    ...

def stratified_baseline(class_wise_acc: np.ndarray, overall_acc: np.ndarray) -> tuple:
    """Returns (baseline_pred [N,10], class_difficulty [10,]).
    baseline_pred[i,c] = overall_acc[i] * class_difficulty[c] / mean(class_difficulty)"""
    ...
```

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation). `stratified_baseline` already produces the baseline prediction directly — H-M1's Ridge "baseline" model is a Ridge fit on `[overall_acc, class_difficulty]` features per class, evaluated against the same `class_wise_acc` targets used for the proposed model (see M-6).

---

## M-4: Weight Statistics Extraction [Complexity: 9, Budget: 9]

**Applied**: weight-statistics-extraction pattern (Unterthiner et al. 2020)

### API Signatures

```python
# weight_features.py
LAYER_KEYS = [
    "module_list.0.weight",   # (8, 3, 5, 5)
    "module_list.3.weight",   # (6, 8, 5, 5)
    "module_list.6.weight",   # (4, 6, 2, 2)
    "module_list.9.weight",   # (20, 36)
    "module_list.11.weight",  # (10, 20)
]

def extract_layer_statistics(state_dict: dict) -> np.ndarray:
    """Flatten each of 5 layers, compute [mean,std,min,max,norm]. Returns (25,) vector."""
    ...

def build_weight_feature_matrix(model_entries: list) -> tuple:
    """model_entries: [(model_id, state_dict, test_acc), ...]
    Returns (features [N,25], model_ids: list[str]) aligned by iteration order."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| state_dict[layer] | varies (see LAYER_KEYS) | raw conv/linear weight tensor |
| layer_flat | (num_params,) | `.detach().cpu().numpy().ravel()` per layer |
| per-layer stats | (5,) | mean, std, min, max, L2 norm |
| extract_layer_statistics output | (25,) | 5 layers x 5 stats, concatenated in LAYER_KEYS order |
| build_weight_feature_matrix output | (N, 25) | N = len(model_entries) |

### Pseudo-code

```
extract_layer_statistics(state_dict):
    feats = []
    for key in LAYER_KEYS:
        w = state_dict[key].detach().cpu().numpy().ravel()   # (num_params,)
        feats += [w.mean(), w.std(), w.min(), w.max(), np.linalg.norm(w)]
    return np.array(feats)  # (25,)

build_weight_feature_matrix(model_entries):
    rows, ids = [], []
    for model_id, state_dict, _ in model_entries:
        rows.append(extract_layer_statistics(state_dict))
        ids.append(model_id)
    return np.stack(rows), ids  # (N, 25), N ids
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M-4-1 | extract_layer_statistics | Per-layer mean/std/min/max/norm over 5 real state_dict tensors -> (25,) |
| L-M-4-2 | build_weight_feature_matrix | Loop model_entries, stack into (N,25) feature matrix aligned to model_ids |

---

## Probe API (probe.py)

**Applied**: Standard PyTorch/sklearn Ridge probe pattern

### API Signatures

```python
def train_test_split_indices(n: int, test_frac: float, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Fixed-seed shuffle split. Returns (train_idx, test_idx)."""
    ...

def fit_stratified_baseline(
    overall_acc: np.ndarray, class_difficulty: np.ndarray, class_wise_acc: np.ndarray, train_idx: np.ndarray
) -> Ridge:
    """Fit Ridge(alpha=1.0) on X=[overall_acc, tile(class_difficulty)] per (model,class) row -> y=class_wise_acc.
    X: (N_train*10, 2), y: (N_train*10,) OR fit as (N_train,10) multi-output with 2 broadcasted features per row."""
    ...

class WeightToClassAccuracyProbe:
    def __init__(self, alpha: float = 1.0):
        self.scaler = StandardScaler()
        self.probe = Ridge(alpha=alpha)

    def fit(self, weight_features: np.ndarray, class_accuracies: np.ndarray) -> None:
        """weight_features: (N,25), class_accuracies: (N,10)"""
        ...

    def predict(self, weight_features: np.ndarray) -> np.ndarray:
        """Returns (N,10) predicted class accuracies"""
        ...

def evaluate_r2(y_true: np.ndarray, y_pred: np.ndarray) -> tuple[list[float], float]:
    """y_true, y_pred: (N,10). Returns (per_class_r2: list[10 floats], mean_r2: float)"""
    ...

def run_gate_comparison(
    weight_features: np.ndarray, class_wise_acc: np.ndarray, overall_acc: np.ndarray,
    train_idx: np.ndarray, test_idx: np.ndarray
) -> dict:
    """Returns {baseline_r2_mean, proposed_r2_mean, baseline_r2_per_class, proposed_r2_per_class, gate_pass}"""
    ...
```

### Pseudo-code (run_gate_comparison)

```
run_gate_comparison(weight_features, class_wise_acc, overall_acc, train_idx, test_idx):
    baseline_pred_all, class_difficulty = stratified_baseline(class_wise_acc, overall_acc)  # reuse base.analysis
    baseline_r2_per_class, baseline_r2_mean = evaluate_r2(class_wise_acc[test_idx], baseline_pred_all[test_idx])

    probe = WeightToClassAccuracyProbe(alpha=RIDGE_ALPHA)
    probe.fit(weight_features[train_idx], class_wise_acc[train_idx])
    proposed_pred = probe.predict(weight_features[test_idx])
    proposed_r2_per_class, proposed_r2_mean = evaluate_r2(class_wise_acc[test_idx], proposed_pred)

    gate_pass = proposed_r2_mean > baseline_r2_mean
    return {baseline_r2_mean, proposed_r2_mean, baseline_r2_per_class, proposed_r2_per_class, gate_pass}
```

### Subtasks (M-5..M-8, budgets per architecture table: 4/6/7/6)

| ID | Subtask | Description |
|----|---------|--------------|
| L-M-5-1 | train_test_split_indices | Fixed-seed 80/20 split shared across baseline & proposed |
| L-M-6-1 | fit_stratified_baseline | Ridge on [overall_acc, class_difficulty] using base.analysis.stratified_baseline for class_difficulty |
| L-M-7-1 | WeightToClassAccuracyProbe | StandardScaler + Ridge(alpha=1.0), fit/predict on (N,25)->(N,10) |
| L-M-8-1 | evaluate_r2 + run_gate_comparison | Per-class/mean R², proposed_r2_mean > baseline_r2_mean assertion |

---

## Pipeline Flow (run.py)

```python
def main() -> None:
    # 1. base.model_zoo_loader.load_model_zoo_final_epoch(DATA_PATH) -> model_entries (n=193)
    # 2. base.model_zoo_loader.get_model_predictions_from_weights(model_entries, CIFAR_ROOT) -> predictions dict
    # 3. base.analysis.compute_class_wise_accuracy(predictions, ground_truth, N_CLASSES)
    #    -> class_wise_acc (N,10), overall_acc (N,), model_ids
    # 4. weight_features.build_weight_feature_matrix(model_entries) -> weight_feats (N,25), ids
    #    (assert ids order matches model_ids from step 3, or reindex by model_id)
    # 5. probe.train_test_split_indices(N, TEST_SPLIT, SEED) -> train_idx, test_idx
    # 6. probe.run_gate_comparison(weight_feats, class_wise_acc, overall_acc, train_idx, test_idx) -> gate_result
    # 7. visualize.plot_gate_metric(...) [required]; optional plots
    # 8. build_report(gate_result, figure_paths, n_models) -> json.dump to RESULTS_PATH
    ...
```

**Note**: model_ids alignment between `compute_class_wise_accuracy` (order = `predictions.keys()`) and `build_weight_feature_matrix` (order = `model_entries`) must be verified/reindexed since dict key order and list order can diverge if any model failed inference in step 2.
