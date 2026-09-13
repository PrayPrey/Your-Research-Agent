---
title: "Logic: H-M2 — PCA Concentration Test"
hypothesis_id: H-M2
hypothesis_type: MECHANISM
date: 2026-08-27
author: Anonymous
budget_subtasks: 5
base_hypothesis: H-M1
---

# Logic Design: H-M2

Applied: Linear probe evaluation pattern (PCA → LinearRegression → R² as concentration metric)
Applied: Bootstrap CI pattern (index resampling on test split, consistent with H-M1 statistics.py)

---

## Codebase Analysis (Serena)

**Status:** Serena MCP unavailable (NO_MCP session). Analysis performed via Read/Glob tools on H-M1 codebase.
**Analyzed:** `docs/youra_research/h-m1/code/`

**Key findings (authoritative — from actual code):**

| Finding | Source File | Impact on H-M2 |
|---------|-------------|----------------|
| `EXPECTED_DIM = sum([784*64, 64, 10*64, 10]) = 51850` | `data_loader.py:10` | Weight dim = 51850, NOT 50890 as in experiment brief |
| `SPLITS = [784*64, 64, 10*64, 10]` | `data_loader.py:9` | Layer boundary offsets for canonicalization |
| `load_zoo()` returns list of dicts with `"test_accuracy"`, `"generalization_gap"`, `"learning_rate"` keys | `data_loader.py:45-80` | Direct reuse; key names are exact |
| `bootstrap_ci(data, n_boot, seed, level)` uses `scipy.stats.bootstrap` with `method="percentile"` | `statistics.py:6-15` | H-M2 uses same pattern; adapt for R² (not mean) |
| `construct_scaling_orbit()` / `construct_signflip_orbit()` operate on weight dicts, not numpy arrays | `orbit_construction.py` | Cannot import directly; adapt logic to numpy arrays |
| No `apply_scaling_canon()` or `apply_sign_flip_canon()` in H-M1 | entire codebase | Must implement from scratch in `data_prep.py` |

---

## External Dependencies API

Verified signatures from H-M1 `data_loader.py` (actual code):

```python
# H-M1 data_loader.py — verified
SPLITS = [784 * 64, 64, 10 * 64, 10]   # [50176, 64, 640, 10] → sum = 51850
EXPECTED_DIM = 51850

def load_zoo(
    hf_id: str = "ModelZoos/ModelZooDataset",
    config: str = "mnist-mlp",
    split: str = "train+validation",
) -> list[dict]:
    """
    Returns list of dicts. Each dict has:
      - "weights": flat torch.Tensor of shape (51850,)
      - "test_accuracy": float
      - "generalization_gap": float  (= train_acc - test_acc)
      - "learning_rate": float
    Falls back to local archive automatically.
    """

# H-M1 statistics.py — verified
from scipy.stats import bootstrap as scipy_bootstrap

def bootstrap_ci(
    data: np.ndarray,
    n_boot: int = 1000,
    seed: int = 42,
    level: float = 0.95,
) -> tuple[float, float]:
    """Returns (ci_low, ci_high) for mean of data. NOT directly usable for R² — adapt."""
```

**Import path for H-M2:**
```python
import sys
from pathlib import Path
H_M1_CODE = Path(__file__).parent.parent.parent / "h-m1" / "code"
sys.path.insert(0, str(H_M1_CODE))
from data_loader import load_zoo, SPLITS, EXPECTED_DIM
```

---

## Subtask Specifications

### L-2-1: `load_and_flatten()` (parent: E-2, data_prep.py)

**Purpose:** Load zoo via H-M1 `load_zoo()` and extract (X, Y) arrays.

**Signature:**
```python
def load_and_flatten() -> tuple[np.ndarray, np.ndarray, list[str]]:
    """
    Returns:
        X:            np.ndarray, shape (N, 51850), dtype float32
        Y:            np.ndarray, shape (N, 3),     dtype float32
        label_names:  list[str] = ['test_accuracy', 'generalization_gap', 'learning_rate']
    """
```

**Tensor shapes:**
```
records = load_zoo()           → list of N dicts
X: (N, 51850)  float32         ← stack [r["weights"].numpy() for r in records]
Y: (N, 3)      float32         ← columns: [test_accuracy, gen_gap, lr]
```

**Pseudo-code:**
```python
def load_and_flatten():
    records = load_zoo()
    X = np.stack([r["weights"].float().numpy() for r in records])  # (N, 51850)
    y_acc = np.array([r["test_accuracy"] for r in records], dtype=np.float32)
    y_gap = np.array([r["generalization_gap"] for r in records], dtype=np.float32)
    y_lr  = np.array([r["learning_rate"] for r in records], dtype=np.float32)
    Y = np.stack([y_acc, y_gap, y_lr], axis=1)  # (N, 3)
    label_names = ["test_accuracy", "generalization_gap", "learning_rate"]
    return X.astype(np.float32), Y, label_names
```

---

### L-2-2: `apply_condition_d()` (parent: E-2, data_prep.py)

**Purpose:** Apply scaling + sign-flip canonicalization (Condition D) to raw weight matrix.

**Signature:**
```python
def apply_condition_d(X: np.ndarray) -> np.ndarray:
    """
    Args:
        X: np.ndarray, shape (N, 51850), raw weight vectors
    Returns:
        X_canon: np.ndarray, shape (N, 51850), Condition D canonical vectors
    Step 1: Scaling — divide each layer block by its Frobenius norm per model
    Step 2: Sign-flip (M=2) — flip hidden neuron signs if majority incoming sign negative
    """
```

**Layer boundaries** (from H-M1 `SPLITS = [50176, 64, 640, 10]`):
```
Layer 0 weights (W1): indices [0:50176]       → reshape (N, 784, 64)
Layer 0 bias   (b1): indices [50176:50240]
Layer 1 weights (W2): indices [50240:50880]   → reshape (N, 64, 10)
Layer 1 bias   (b2): indices [50880:51850]
```
Note: for canonicalization, biases are included in the block for norm computation but sign-flip only touches W1 columns and W2 rows (not biases).

**Pseudo-code:**
```python
def apply_condition_d(X):
    N = X.shape[0]
    X_c = X.copy()

    # --- Step 1: Scaling (Frobenius norm per layer per model) ---
    # W1 block
    W1_flat = X_c[:, :50176]                              # (N, 50176)
    norms_W1 = np.linalg.norm(W1_flat, axis=1, keepdims=True) + 1e-8
    X_c[:, :50176] = W1_flat / norms_W1

    # b1 block (normalize by same W1 norm for consistency)
    b1_flat = X_c[:, 50176:50240]
    X_c[:, 50176:50240] = b1_flat / norms_W1

    # W2 block
    W2_flat = X_c[:, 50240:50880]                         # (N, 640)
    norms_W2 = np.linalg.norm(W2_flat, axis=1, keepdims=True) + 1e-8
    X_c[:, 50240:50880] = W2_flat / norms_W2

    # b2 block
    b2_flat = X_c[:, 50880:51850]
    X_c[:, 50880:51850] = b2_flat / norms_W2

    # --- Step 2: Sign-flip (M=2, majority-sign on hidden neurons) ---
    W1 = X_c[:, :50176].reshape(N, 784, 64)              # (N, 784, 64)
    W2 = X_c[:, 50240:50880].reshape(N, 64, 10)          # (N, 64, 10)

    # For each hidden neuron h: majority sign of incoming column W1[:, :, h]
    col_sums = W1.sum(axis=1)                             # (N, 64) sum over input dim
    signs = np.sign(col_sums)                             # (N, 64)
    signs[signs == 0] = 1.0                               # tie-breaking: positive

    # Flip: W1 column h *= signs[:, h]; W2 row h *= signs[:, h]
    W1 *= signs[:, np.newaxis, :]                         # broadcast over 784
    W2 *= signs[:, :, np.newaxis]                         # broadcast over 10

    X_c[:, :50176] = W1.reshape(N, 50176)
    X_c[:, 50240:50880] = W2.reshape(N, 640)
    return X_c
```

---

### L-3-1: `evaluate_pca_concentration()` (parent: E-3, evaluate.py)

**Purpose:** PCA sweep + LinearRegression R² with bootstrap 95% CI for one condition.

**Signature:**
```python
def evaluate_pca_concentration(
    X_train: np.ndarray,   # (450, 51850)
    X_test:  np.ndarray,   # (50, 51850)
    y_train: np.ndarray,   # (450,)
    y_test:  np.ndarray,   # (50,)
    k_values: list[int] = [10, 20, 50],
    n_boot: int = 1000,
    seed: int = 42,
) -> dict:
    """
    Returns:
        {k: {'r2': float, 'ci': [ci_low, ci_high], 'y_pred': np.ndarray(50,)}}
        for each k in k_values
    """
```

**Tensor shapes at each step:**
```
X_train:          (450, 51850)  float32
X_test:           (50,  51850)  float32
pca.fit(X_train)  → explained_variance_ratio_: (k,)
X_tr_pca:         (450, k)      after fit_transform
X_te_pca:         (50,  k)      after transform
reg.fit(X_tr_pca, y_train)
y_pred:           (50,)
r2_score(y_test, y_pred) → float
boot_idx:         (50,)  per bootstrap iteration
boot_r2:          list of n_boot floats
ci:               [np.percentile(boot_r2, 2.5), np.percentile(boot_r2, 97.5)]
```

**Pseudo-code:**
```python
def evaluate_pca_concentration(X_train, X_test, y_train, y_test,
                                k_values, n_boot=1000, seed=42):
    rng = np.random.default_rng(seed)
    results = {}
    for k in k_values:
        pca = PCA(n_components=k, random_state=42)
        X_tr_pca = pca.fit_transform(X_train)              # (450, k)
        X_te_pca = pca.transform(X_test)                   # (50, k)

        reg = LinearRegression()
        reg.fit(X_tr_pca, y_train)
        y_pred = reg.predict(X_te_pca)                     # (50,)
        r2 = r2_score(y_test, y_pred)

        boot_r2 = []
        for _ in range(n_boot):
            idx = rng.integers(0, len(y_test), size=len(y_test))
            boot_r2.append(r2_score(y_test[idx], y_pred[idx]))

        ci = list(np.percentile(boot_r2, [2.5, 97.5]))
        results[k] = {'r2': float(r2), 'ci': ci, 'y_pred': y_pred}
    return results
```

**Called per (condition × label): 2 × 3 × 3 k_values = 18 times total.**

---

### L-3-2: `verify_mechanism_preconditions()` (parent: E-3, evaluate.py)

**Purpose:** Assert H-M2 mechanism can activate before running full experiment.

**Signature:**
```python
def verify_mechanism_preconditions(
    X_A_train: np.ndarray,    # (450, 51850) raw
    X_D_train: np.ndarray,    # (450, 51850) canonical
) -> None:
    """Raises AssertionError with message if any precondition fails. Prints summary on pass."""
```

**Assertions:**
```python
def verify_mechanism_preconditions(X_A_train, X_D_train):
    # 1. Canonicalization has effect
    assert not np.allclose(X_A_train, X_D_train), \
        "FAIL: Condition D == Condition A (canonicalization has no effect)"

    # 2. PCA non-degenerate for both conditions
    for label, X in [("A", X_A_train), ("D", X_D_train)]:
        pca = PCA(n_components=20, random_state=42).fit(X)
        evr_sum = pca.explained_variance_ratio_.sum()
        assert evr_sum > 0.01, \
            f"FAIL: PCA degenerate for Condition {label} (EVR sum={evr_sum:.4f})"

    # 3. LinearRegression finite coefficients
    pca_check = PCA(n_components=20, random_state=42).fit(X_A_train)
    dummy_y = np.random.default_rng(0).standard_normal(len(X_A_train))
    reg_check = LinearRegression().fit(pca_check.transform(X_A_train), dummy_y)
    assert np.isfinite(reg_check.coef_).all(), \
        "FAIL: LinearRegression produces non-finite coefficients"

    # Print summary
    diff = np.mean(np.abs(X_A_train - X_D_train))
    pca_a = PCA(n_components=20, random_state=42).fit(X_A_train)
    pca_d = PCA(n_components=20, random_state=42).fit(X_D_train)
    print("✅ All H-M2 mechanism preconditions satisfied")
    print(f"  Mean |X_A - X_D|: {diff:.4f}")
    print(f"  PCA-A top-20 EVR: {pca_a.explained_variance_ratio_[:20].sum():.3f}")
    print(f"  PCA-D top-20 EVR: {pca_d.explained_variance_ratio_[:20].sum():.3f}")
```

---

### L-5-1: `run_h_m2_experiment()` (parent: E-5, main.py)

**Purpose:** Main orchestration — end-to-end pipeline from load to gate result.

**Signature:**
```python
def run(
    k_values: list[int] = [10, 20, 50],
    seed: int = 42,
    figures_dir: str = FIGURES_DIR,
    results_path: str = RESULTS_PATH,
    n_boot: int = 1000,
) -> dict:
    """
    Returns:
        {
          'gate_pass': bool,
          'per_label': {
              label_name: {
                  'condition_a': {k: {'r2': float, 'ci': [lo, hi]}},
                  'condition_d': {k: {'r2': float, 'ci': [lo, hi]}},
              }
          },
          'gate_details': {label_name: {'delta_r2': float, 'ci_nonoverlap': bool, 'pass': bool}},
          'n_pass': int,
          'n_required': int,
        }
    """
```

**Call sequence:**
```python
def run(k_values, seed, figures_dir, results_path, n_boot):
    # 1. Load and flatten
    X, Y, label_names = load_and_flatten()          # X: (N, 51850), Y: (N, 3)

    # 2. Condition A / D
    X_A = X                                          # (N, 51850) raw
    X_D = apply_condition_d(X)                       # (N, 51850) canonical

    # 3. Verify preconditions
    X_tr_A, X_te_A, Y_tr, Y_te = train_test_split_fixed(X_A, Y, seed=seed)
    X_tr_D, X_te_D, _, _       = train_test_split_fixed(X_D, Y, seed=seed)
    verify_mechanism_preconditions(X_tr_A, X_tr_D)

    # 4. PCA concentration eval per label
    results_a, results_d = {}, {}
    for i, lname in enumerate(label_names):
        results_a[lname] = evaluate_pca_concentration(
            X_tr_A, X_te_A, Y_tr[:, i], Y_te[:, i], k_values, n_boot, seed)
        results_d[lname] = evaluate_pca_concentration(
            X_tr_D, X_te_D, Y_tr[:, i], Y_te[:, i], k_values, n_boot, seed)

    # 5. Gate comparison
    gate = compare_conditions(results_a, results_d, k_gate=20, n_tasks_required=2)

    # 6. Figures
    pca_a_k50 = PCA(n_components=50, random_state=42).fit(X_tr_A)
    pca_d_k50 = PCA(n_components=50, random_state=42).fit(X_tr_D)
    X_te_A_pca = pca_a_k50.transform(X_te_A)
    X_te_D_pca = pca_d_k50.transform(X_te_D)
    Path(figures_dir).mkdir(parents=True, exist_ok=True)
    generate_all_figures(results_a, results_d, pca_a_k50, pca_d_k50,
                         X_te_A_pca, X_te_D_pca, Y_te, label_names, figures_dir)

    # 7. Save results
    output = {
        'gate_pass': gate['gate_pass'],
        'n_pass': gate['n_pass'],
        'n_required': gate['n_required'],
        'gate_details': gate['per_task'],
        'per_label': {'condition_a': results_a, 'condition_d': results_d},
    }
    # Strip non-serializable y_pred arrays before JSON dump
    import json, copy
    serializable = copy.deepcopy(output)
    for lname in label_names:
        for cond in ['condition_a', 'condition_d']:
            for k in k_values:
                serializable['per_label'][cond][lname][k].pop('y_pred', None)
    Path(results_path).parent.mkdir(parents=True, exist_ok=True)
    with open(results_path, 'w') as f:
        json.dump(serializable, f, indent=2)
    print(f"Results saved to {results_path}")
    print(f"Gate: {'PASS' if gate['gate_pass'] else 'FAIL'} "
          f"({gate['n_pass']}/{gate['n_required']} tasks with non-overlapping CI)")
    return output
```

**results.json schema:**
```json
{
  "gate_pass": true,
  "n_pass": 2,
  "n_required": 2,
  "gate_details": {
    "test_accuracy":       {"delta_r2": 0.12, "ci_nonoverlap": true,  "pass": true},
    "generalization_gap":  {"delta_r2": 0.05, "ci_nonoverlap": false, "pass": false},
    "learning_rate":       {"delta_r2": 0.08, "ci_nonoverlap": true,  "pass": true}
  },
  "per_label": {
    "condition_a": {
      "test_accuracy": {10: {"r2": 0.04, "ci": [0.0, 0.09]}, ...}
    },
    "condition_d": {...}
  }
}
```

---

*Logic design generated: 2026-08-27 | Phase 3 Step 5 | Unattended mode*
*MCP: unavailable (NO_MCP session) — codebase analysis via direct Read tools*
