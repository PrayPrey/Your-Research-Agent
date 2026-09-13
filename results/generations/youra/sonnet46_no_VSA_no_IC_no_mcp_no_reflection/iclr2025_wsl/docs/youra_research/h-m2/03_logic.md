# Logic: h-m2
# Differential Advantage of Permutation-Equivariant Encoders

**Date:** 2026-08-31
**Author:** yoon303@etri.re.kr

Applied: Dual-target controlled comparison pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual h-m1 code
**Analyzed Path**: `h-m1/code/run_analysis.py`
**Relevant Symbols**:
- `random_search(encoder_cls, arch_kwargs, zoo, lr_candidates, batch_size, epochs, n_trials, device, lr_schedule, encoder_name)` → `(best_model, best_hp, _)`
- `eval_spearman(model, zoo, split, batch_size, device)` → `(r, p)`
- `load_zoo(zoo_path, idx_train, idx_val, idx_test)` → `ZooData`
- `compute_split(n_models, seed, ratios)` → `(idx_train, idx_val, idx_test)`
- `make_loader(zoo, split, batch_size, shuffle, num_workers)` → DataLoader
- `torch.save({"model_state_dict": ..., "best_hp": ...}, path)` — checkpoint format
- `torch.load(path, map_location, weights_only=False)` → dict with `"model_state_dict"`

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code — h-m1/code/run_analysis.py)

```python
# From: h-m1/code/run_analysis.py lines 83-93 (ACTUAL CODE)
best_model, best_hp, _ = random_search(
    encoder_cls=ENCODER_CLS[name],   # type: Type[nn.Module]
    arch_kwargs=kwargs,               # type: dict
    zoo=zoo,                          # type: ZooData
    lr_candidates=cfg.lr_candidates,  # type: list[float]
    batch_size=cfg.batch_size,        # type: int
    epochs=cfg.epochs,                # type: int
    n_trials=3,                       # type: int
    device=device,                    # type: str
    lr_schedule=cfg.lr_schedule,      # type: str
    encoder_name=name,                # type: str
)

# From: h-m1/code/run_analysis.py line 96 (ACTUAL CODE)
val_r, _ = eval_spearman(
    model,        # type: nn.Module
    zoo,          # type: ZooData
    "val",        # split: str
    cfg.batch_size,  # batch_size: int
    device,       # device: str
)  # returns (r: float, p: float)

# Checkpoint save/load pattern (lines 95, 105-108):
torch.save({"model_state_dict": best_model.state_dict(), "best_hp": str(best_hp)}, save_path)
ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
state = ckpt["model_state_dict"] if "model_state_dict" in ckpt else ckpt
model.load_state_dict(state)
```

**Verified from**: `h-m1/code/run_analysis.py` (actual implementation, NOT spec)

---

## A-4: Train DWSNet/NFT/GNN on test_acc [Complexity: 12, Budget: 4]

Applied: Standard PyTorch

### API Signatures

```python
# run_experiment.py

CHECKPOINT_DIR: str  # h-m2/checkpoints/
TESTACC_CHECKPOINT_FILES = {
    "FlatMLP": "flat_mlp_testacc_best.pt",
    "DWSNet":  "dws_net_testacc_best.pt",
    "NFT":     "nft_testacc_best.pt",
    "GNN":     "gnn_testacc_best.pt",
}
H_M1_GAP_RESULTS: dict[str, float] = {
    "FlatMLP": 0.5330, "DWSNet": 0.4881, "NFT": 0.5752, "GNN": 0.3747
}
N_TRIALS: int = 3
SEED: int = 42
BOOTSTRAP_N: int = 1000


def build_encoder(name: str, input_dim: int) -> torch.nn.Module:
    """Instantiate encoder from ENCODER_CLS and ENCODER_CONFIGS."""
    ...


def train_testacc(name: str, zoo: ZooData, device: str) -> tuple[float, dict]:
    """3-trial random_search on test_acc; returns (best_val_r, best_state_dict)."""
    ...


def evaluate_testacc(name: str, model: torch.nn.Module, zoo: ZooData,
                     device: str) -> np.ndarray:
    """Run test-split inference; returns preds array. Shape: [N_test]"""
    ...


def save_checkpoint_testacc(name: str, state_dict: dict, best_hp: str) -> str:
    """Save to CHECKPOINT_DIR/TESTACC_CHECKPOINT_FILES[name]; return path."""
    ...


def load_checkpoint_testacc(name: str, input_dim: int, device: str) -> torch.nn.Module:
    """Load checkpoint; return model in eval mode."""
    ...
```

### Pseudo-code: train_testacc()

```
cfg = ENCODER_CONFIGS[name]
# Patch zoo to expose test_acc as regression target (zoo.gap field used by random_search)
zoo_acc = replace(zoo, gap=zoo.test_acc)  # or equivalent field swap

best_model, best_hp, _ = random_search(
    encoder_cls=ENCODER_CLS[name],
    arch_kwargs=_get_arch_kwargs(name, input_dim),
    zoo=zoo_acc,
    lr_candidates=cfg.lr_candidates,
    batch_size=cfg.batch_size,
    epochs=cfg.epochs,
    n_trials=N_TRIALS,
    device=device,
    lr_schedule=cfg.lr_schedule,
    encoder_name=name,
)
save_checkpoint_testacc(name, best_model.state_dict(), str(best_hp))
val_r, _ = eval_spearman(best_model, zoo_acc, "val", cfg.batch_size, device)
return val_r, best_model.state_dict()
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | train_testacc | Full function with 3-trial loop via random_search |
| L-4-2 | random_search wrapper | zoo field swap for test_acc target; use verified signature |
| L-4-3 | eval_spearman call | eval_spearman(model, zoo_acc, "test", batch_size, device) |
| L-4-4 | checkpoint save/load | torch.save/load with `{"model_state_dict": ..., "best_hp": ...}` |

---

## A-5: Δ Computation & Gate Check [Complexity: 10, Budget: 4]

Applied: Bootstrap resampling pattern

### API Signatures

```python
# compute_delta.py
from __future__ import annotations
import numpy as np
from scipy.stats import spearmanr

H_M1_GAP: dict[str, float] = {
    "FlatMLP": 0.5330, "DWSNet": 0.4881, "NFT": 0.5752, "GNN": 0.3747
}
EQUIVARIANT = ["DWSNet", "NFT", "GNN"]
GATE_THRESHOLD: float = 0.02
GATE_MIN_PASS: int = 2
BOOTSTRAP_N: int = 1000


def compute_delta(
    gap_results: dict[str, float],    # {name: Spearman(gap)}
    testacc_results: dict[str, float], # {name: Spearman(test_acc)}
) -> dict[str, float]:
    """Δ(enc) = (gap[enc]-gap[FlatMLP]) - (acc[enc]-acc[FlatMLP]). FlatMLP excluded."""
    ...


def gate_check(
    delta: dict[str, float],
    threshold: float = GATE_THRESHOLD,
    min_pass: int = GATE_MIN_PASS,
) -> tuple[int, bool]:
    """Returns (n_pass, passed). Counts encoders in EQUIVARIANT with Δ > threshold."""
    ...


def bootstrap_delta_ci(
    gap_preds: dict[str, np.ndarray],      # {name: preds} shape [N_test] each
    testacc_preds: dict[str, np.ndarray],  # {name: preds} shape [N_test] each
    true_gap: np.ndarray,                  # [N_test]
    true_testacc: np.ndarray,              # [N_test]
    n_boot: int = BOOTSTRAP_N,
    seed: int = 42,
) -> dict[str, tuple[float, float]]:
    """Returns {enc: (ci_low, ci_high)} 95% CI on Δ for equivariant encoders."""
    ...
```

### Pseudo-code: compute_delta()

```
baseline_gap = gap_results["FlatMLP"]
baseline_acc = testacc_results["FlatMLP"]
delta = {}
for enc in EQUIVARIANT:
    gap_imp = gap_results[enc] - baseline_gap
    acc_imp = testacc_results[enc] - baseline_acc
    delta[enc] = gap_imp - acc_imp
return delta
```

### Pseudo-code: bootstrap_delta_ci()

```
rng = np.random.RandomState(seed)
boot_deltas = {enc: [] for enc in EQUIVARIANT}
for _ in range(n_boot):
    idx = rng.randint(0, N_test, size=N_test)
    # Compute per-encoder Spearman on resampled indices
    gap_flat_r, _ = spearmanr(gap_preds["FlatMLP"][idx], true_gap[idx])
    acc_flat_r, _ = spearmanr(testacc_preds["FlatMLP"][idx], true_testacc[idx])
    for enc in EQUIVARIANT:
        gap_r, _ = spearmanr(gap_preds[enc][idx], true_gap[idx])
        acc_r, _ = spearmanr(testacc_preds[enc][idx], true_testacc[idx])
        d = (gap_r - gap_flat_r) - (acc_r - acc_flat_r)
        boot_deltas[enc].append(d)
return {enc: (np.percentile(v, 2.5), np.percentile(v, 97.5))
        for enc, v in boot_deltas.items()}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | compute_delta | Δ formula; FlatMLP excluded from equivariant set |
| L-5-2 | gate_check | (n_pass, passed); threshold=0.02, min_pass=2 |
| L-5-3 | bootstrap_delta_ci | Resample idx, Spearman per resample, percentiles |
| L-5-4 | bootstrap_spearman_ci | In metrics.py; resample (preds, targets), Spearman, 95% CI |

---

## A-6: Partial Spearman P3 [Complexity: 9, Budget: 3]

Applied: Standard PyTorch / scipy rank-based partial correlation

### API Signatures

```python
# metrics.py
import numpy as np
from scipy.stats import spearmanr, rankdata
from sklearn.linear_model import LinearRegression


def rank_residuals(x: np.ndarray, z: np.ndarray) -> np.ndarray:
    """Residuals of regressing rank(x) on rank(z). x,z: [N] -> [N]"""
    ...


def partial_spearman(
    pred_gap: np.ndarray,      # [N] NFT gap predictions
    true_gap: np.ndarray,      # [N]
    true_testacc: np.ndarray,  # [N] covariate to partial out
) -> tuple[float, float]:
    """Spearman(resid(pred_gap|rank(true_testacc)), resid(true_gap|rank(true_testacc))).
    Returns (r, p_value)."""
    ...


def bootstrap_spearman_ci(
    preds: np.ndarray,    # [N]
    targets: np.ndarray,  # [N]
    n_boot: int = 1000,
    seed: int = 42,
) -> tuple[float, float]:
    """Bootstrap 95% CI on Spearman r. Returns (ci_low, ci_high)."""
    ...


def verify_h_m2_mechanism(
    testacc_results: dict[str, float],  # {name: Spearman(test_acc)}
    gap_results: dict[str, float],      # {name: Spearman(gap)}  — from h-m1
    delta: dict[str, float],            # from compute_delta()
    p3: tuple[float, float],            # (r, p_value) from partial_spearman()
) -> bool:
    """4 sanity checks; returns True if all pass."""
    ...
```

### Pseudo-code: partial_spearman()

```
z_rank = rankdata(true_testacc)                  # [N]
pred_resid = rank_residuals(pred_gap, z_rank)    # [N]
true_resid = rank_residuals(true_gap, z_rank)    # [N]
r, p = spearmanr(pred_resid, true_resid)
return float(r), float(p)
```

### Pseudo-code: rank_residuals()

```
x_rank = rankdata(x).reshape(-1, 1)   # [N, 1]
z_rank = z.reshape(-1, 1)             # [N, 1] (already ranked if called from partial_spearman)
lr = LinearRegression().fit(z_rank, x_rank)
resid = x_rank.ravel() - lr.predict(z_rank).ravel()  # [N]
return resid
```

### Pseudo-code: verify_h_m2_mechanism()

```
check1: all testacc_results values are finite and non-NaN
check2: testacc_results["FlatMLP"] in [0.75, 0.95]
check3: abs(gap_results["NFT"] - 0.5752) < 0.05
check4: all delta values are finite and non-NaN
return all(check1, check2, check3, check4)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | partial_spearman | Rank-based residual regression then Spearman |
| L-6-2 | rank_residuals | LinearRegression on ranks, return residuals |
| L-6-3 | verify_h_m2_mechanism | 4 sanity checks: finite preds, FlatMLP range, NFT gap consistency, Δ finite |
