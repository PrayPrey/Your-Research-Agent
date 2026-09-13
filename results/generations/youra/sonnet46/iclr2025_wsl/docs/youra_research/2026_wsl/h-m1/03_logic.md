# Logic: H-M1

**hypothesis_id:** h-m1
**hypothesis_type:** MECHANISM
**generated_at:** 2026-03-16
**extends:** H-E1 (COMPLETED — PASS)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified by direct file read of H-E1 src/ (Serena project activation unavailable; all 4 source files read directly)
**Analyzed Path**: `docs/youra_research/20260316_wsl/h-e1/code/src/`
**Relevant Symbols**:
- `FlatMLPEncoder(input_dim, hidden_dim=512)` — `forward(x: Tensor) -> Tensor` — x: [B, input_dim] → [B, 1]
- `NFTEquivariantEncoder(layer_fan_ins: list, d_model=128, n_heads=4)` — `forward(weight_matrices: list) -> Tensor`
- `train_model(model, train_loader, n_epochs=50, lr=1e-3, device=None, model_type="flat", checkpoint_path=None) -> dict`
- `train_epoch(model, loader, optimizer, device, model_type="flat") -> float`
- `set_seed(seed: int = 42) -> None`
- `apply_stress_and_predict(model, test_loader, severity, device, model_type) -> tuple`
- `compute_delta_rho(model, test_loader, severity_levels, device, model_type) -> tuple`
- `bootstrap_delta_rho(model, test_loader, device, model_type, n_bootstrap=10000, seed=42) -> tuple`
- `holm_correction(p_values: list) -> list`
- `evaluate_gate_condition(flat_mlp_delta_rho, nft_delta_rho, flat_mlp_p, nft_p, results_dir="results") -> dict`
- `ZooDataset(samples, mode="flat")`, `get_dataloaders(pkl_path, batch_size=64, train_ratio=0.8, seed=42)`
- `apply_permutation_stress(weight_list, severity) -> list`

---

## External Dependencies API (Base Hypothesis)

Signatures verified from actual H-E1 code files (NOT spec).

```python
# From: h-e1/code/src/models.py
class FlatMLPEncoder(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 512) -> None: ...
    def forward(self, x: Tensor) -> Tensor: ...  # x: [B, input_dim] -> [B, 1]

class NFTEquivariantEncoder(nn.Module):
    def __init__(self, layer_fan_ins: list, d_model: int = 128, n_heads: int = 4) -> None: ...
    def forward(self, weight_matrices: list) -> Tensor: ...  # list[(B, n_units_l, fan_in_l)] -> [B, 1]
    def get_last_token_shape(self) -> tuple: ...  # returns (B, total_neurons, d_model)
    # attribute: self.d_model (int)

# From: h-e1/code/src/train.py
def set_seed(seed: int = 42) -> None: ...
def train_epoch(model, loader, optimizer, device, model_type: str = "flat") -> float: ...
def train_model(
    model: nn.Module,
    train_loader,
    n_epochs: int = 50,
    lr: float = 1e-3,
    device=None,
    model_type: str = "flat",
    checkpoint_path: str = None,
) -> dict: ...  # returns {"train_loss_history": list[float], "final_epoch": int}

# From: h-e1/code/src/evaluate.py
def apply_stress_and_predict(model, test_loader, severity, device, model_type: str) -> tuple: ...
    # returns (predictions: np.ndarray[N], labels: np.ndarray[N])
def compute_delta_rho(model, test_loader, severity_levels: list, device, model_type: str) -> tuple: ...
    # returns (delta_rho: float, rho_by_severity: dict)
def bootstrap_delta_rho(model, test_loader, device, model_type: str, n_bootstrap=10000, seed=42) -> tuple: ...
    # returns (bootstrap_samples: np.ndarray[n_bootstrap], p_value: float)
def holm_correction(p_values: list) -> list: ...
def evaluate_gate_condition(
    flat_mlp_delta_rho: float, nft_delta_rho: float,
    flat_mlp_p: float, nft_p: float, results_dir: str = "results"
) -> dict: ...

# From: h-e1/code/src/data_loader.py
def load_zoo(pkl_path: str) -> list: ...  # raises ValueError if < 500 samples
def flatten_weights(weight_list: list) -> np.ndarray: ...
def apply_permutation_stress(weight_list: list, severity: float) -> list: ...
def get_dataloaders(pkl_path, batch_size=64, train_ratio=0.8, seed=42) -> tuple: ...
    # returns (flat_train_loader, flat_test_loader, nft_train_loader, nft_test_loader)
class ZooDataset(Dataset):
    def __init__(self, samples: list, mode: str = "flat"): ...  # mode: 'flat' or 'nft'
def nft_collate_fn(batch) -> tuple: ...
    # returns (padded_by_layer: list[Tensor], labels: Tensor[B], attention_mask: Tensor[B, total_max_units])
```

**Verified from**: `docs/youra_research/20260316_wsl/h-e1/code/src/` (actual implementation)

**Key notes for H-M1**:
- `train_model` uses `model_type` param ("flat" or "nft") — H-M1 `train_encoder_one_seed` must pass correct model_type per encoder
- `get_dataloaders` returns 4 loaders; H-M1's `get_encoder_dataloaders` replaces this with per-encoder loaders
- `apply_stress_and_predict` dispatches on `model_type` string — H-M1 augmentation-aware encoders still pass "flat" or "nft"

---

## A-2: New Encoder Variants [Complexity: 14, Budget: 3]

Applied: Standard PyTorch subclass extension pattern

### API Signatures

```python
# src/models.py

import torch
import torch.nn as nn
from torch import Tensor
from typing import Optional
from src.data_loader import apply_permutation_stress
from src.config import ENCODER_CONFIG


class FlatMLPAugEncoder(FlatMLPEncoder):
    """E2: flat-MLP + training-time permutation augmentation (50% prob, s=1.0)."""

    def __init__(self, input_dim: int, hidden_dim: int = 512, aug_severity: float = 1.0) -> None:
        """Store aug_severity; architecture identical to FlatMLPEncoder."""
        ...

    def forward(self, x: Tensor, training_aug: bool = False) -> Tensor:
        """x: [B, input_dim] -> [B, 1]. Augments 50% of batch if training_aug=True."""
        ...


class FlatMLPCanonEncoder(FlatMLPEncoder):
    """E3: flat-MLP + L2-norm canonicalization (pre-applied in data_loader)."""

    def __init__(self, input_dim: int, hidden_dim: int = 512) -> None:
        """Architecture identical to FlatMLPEncoder; canonicalization is external."""
        ...

    def forward(self, x: Tensor) -> Tensor:
        """x: [B, input_dim] already canonicalized. Returns [B, 1]."""
        ...


class NFTAugEncoder(NFTEquivariantEncoder):
    """E5: NFT-base + training-time permutation augmentation (50% prob, s=1.0)."""

    def __init__(
        self,
        layer_fan_ins: list,
        d_model: int = 128,
        n_heads: int = 4,
        aug_severity: float = 1.0,
    ) -> None:
        """Store aug_severity; architecture identical to NFTEquivariantEncoder."""
        ...

    def forward(self, weight_matrices: list, training_aug: bool = False) -> Tensor:
        """weight_matrices: list[(B, n_units_l, fan_in_l)] -> [B, 1].
        Augments 50% of batch rows if training_aug=True."""
        ...


class OracleCanonEncoder(FlatMLPEncoder):
    """E6: flat-MLP with oracle-canonical input (upper bound for canonicalization)."""

    def __init__(self, input_dim: int, hidden_dim: int = 512) -> None:
        """Architecture identical to FlatMLPEncoder; oracle ordering applied externally."""
        ...

    def forward(self, x: Tensor) -> Tensor:
        """x: [B, input_dim] oracle-canonicalized. Returns [B, 1]."""
        ...


def build_encoder(
    encoder_name: str,
    flat_input_dim: int,
    layer_fan_ins: list,
) -> nn.Module:
    """Factory: instantiate encoder from ENCODER_CONFIG key.

    Returns one of: FlatMLPEncoder, FlatMLPAugEncoder, FlatMLPCanonEncoder,
    NFTEquivariantEncoder, NFTAugEncoder, OracleCanonEncoder.
    Raises KeyError if encoder_name not in ENCODER_CONFIG.
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| x (flat inputs) | [B, input_dim] | input_dim = flattened weight vector length |
| weight_matrices[l] | [B, n_units_l, fan_in_l] | NFT per-layer |
| output | [B, 1] | regression scalar |

### Pseudo-code — FlatMLPAugEncoder.forward

```
forward(x, training_aug=False):
    if training_aug and random() < 0.5:
        # augment each sample independently via apply_permutation_stress
        augmented = []
        for b in range(B):
            w_list = [x[b].cpu().numpy()]  # treat flat vec as single layer
            stressed = apply_permutation_stress(w_list, self.aug_severity)
            augmented.append(torch.tensor(stressed[0]))
        x = torch.stack(augmented).to(x.device)
    return self.head(self.net(x))  # [B, 1]
```

### Pseudo-code — NFTAugEncoder.forward

```
forward(weight_matrices, training_aug=False):
    if training_aug and random() < 0.5:
        wms_np = [wm.cpu().numpy() for wm in weight_matrices]  # list[(B, n_l, f_l)]
        stressed = []
        for l, wm_np in enumerate(wms_np):
            stressed_l = np.array([
                apply_permutation_stress([wm_np[b]], aug_severity)[0]
                for b in range(B)
            ])  # (B, n_l, f_l)
            stressed.append(torch.tensor(stressed_l).to(device))
        weight_matrices = stressed
    return super().forward(weight_matrices)  # [B, 1]
```

### Pseudo-code — build_encoder

```
build_encoder(encoder_name, flat_input_dim, layer_fan_ins):
    cfg = ENCODER_CONFIG[encoder_name]  # raises KeyError if missing
    model_type = cfg["model_type"]
    if encoder_name == "flat-MLP":
        return FlatMLPEncoder(flat_input_dim)
    elif encoder_name == "flat-MLP+aug":
        return FlatMLPAugEncoder(flat_input_dim, aug_severity=cfg["aug_severity"])
    elif encoder_name == "flat-MLP+canon":
        return FlatMLPCanonEncoder(flat_input_dim)
    elif encoder_name == "NFT-base":
        return NFTEquivariantEncoder(layer_fan_ins)
    elif encoder_name == "NFT+aug":
        return NFTAugEncoder(layer_fan_ins, aug_severity=cfg["aug_severity"])
    elif encoder_name == "Oracle-canon":
        return OracleCanonEncoder(flat_input_dim)
    else:
        raise KeyError(f"Unknown encoder: {encoder_name}")
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | FlatMLP variants | Implement FlatMLPAugEncoder + FlatMLPCanonEncoder + OracleCanonEncoder extending FlatMLPEncoder |
| L-2-2 | NFTAugEncoder | Implement NFTAugEncoder extending NFTEquivariantEncoder with training_aug forward |
| L-2-3 | build_encoder factory | Implement build_encoder dispatching all 6 encoder_names from ENCODER_CONFIG |

---

## A-3: Multi-Seed Training [Complexity: 14, Budget: 3]

Applied: Standard PyTorch training loop with validation split and checkpoint save

### API Signatures

```python
# src/train.py

import torch
import torch.nn as nn
from torch.optim.lr_scheduler import CosineAnnealingLR


def train_encoder_one_seed(
    encoder_name: str,
    seed: int,
    pkl_path: str,
    device: torch.device,
    n_epochs: int = 100,
    checkpoint_dir: str = "checkpoints/",
) -> dict:
    """Train one encoder for one seed. Saves best-val checkpoint.

    Returns {"encoder_name", "seed", "train_loss_history", "val_loss_history",
             "best_val_loss", "checkpoint_path"}.
    Raises RuntimeError on persistent NaN loss.
    """
    ...


def train_all_encoders(
    pkl_path: str,
    device: torch.device,
    seeds: list = None,           # default: SEEDS from config
    encoder_names: list = None,   # default: ENCODER_NAMES from config
    n_epochs: int = 100,
    checkpoint_dir: str = "checkpoints/",
) -> dict:
    """Orchestrate 18 training runs (6 encoders x 3 seeds). Soft-fail per run.

    Returns dict keyed by (encoder_name, seed) -> result_dict or Exception.
    """
    ...


def sanity_check_encoders(
    pkl_path: str,
    device: torch.device,
    n_samples: int = 10,
) -> bool:
    """Verify all 6 encoders produce valid output on n_samples. Fail fast if any fail.

    Returns True if all pass; raises RuntimeError on first failure.
    """
    ...
```

### Pseudo-code — train_encoder_one_seed

```
train_encoder_one_seed(encoder_name, seed, pkl_path, device, n_epochs, checkpoint_dir):
    set_seed(seed)
    train_loader, test_loader, flat_input_dim, layer_fan_ins = get_encoder_dataloaders(
        pkl_path, encoder_name, seed=seed)
    model = build_encoder(encoder_name, flat_input_dim, layer_fan_ins).to(device)
    model_type = ENCODER_CONFIG[encoder_name]["model_type"]

    optimizer = Adam(model.parameters(), lr=1e-3, betas=(0.9, 0.999), weight_decay=1e-4)
    scheduler = CosineAnnealingLR(optimizer, T_max=n_epochs, eta_min=1e-5)
    criterion = MSELoss()

    best_val_loss = inf; train_hist = []; val_hist = []
    ckpt_path = f"{checkpoint_dir}/{encoder_name}_seed{seed}/best.pt"

    for epoch in range(n_epochs):
        # training epoch (aug encoders pass training_aug=True)
        train_loss = _train_epoch_with_aug(model, train_loader, optimizer, device, encoder_name)
        val_loss = _eval_epoch(model, test_loader, device, model_type)

        if isnan(train_loss): raise RuntimeError(...)
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), ckpt_path)
        train_hist.append(train_loss); val_hist.append(val_loss)
        scheduler.step()

    return {"encoder_name": encoder_name, "seed": seed,
            "train_loss_history": train_hist, "val_loss_history": val_hist,
            "best_val_loss": best_val_loss, "checkpoint_path": ckpt_path}
```

### Pseudo-code — train_all_encoders

```
train_all_encoders(pkl_path, device, seeds=None, encoder_names=None, ...):
    seeds = seeds or SEEDS
    encoder_names = encoder_names or ENCODER_NAMES
    results = {}
    for encoder_name in encoder_names:
        for seed in seeds:
            try:
                result = train_encoder_one_seed(encoder_name, seed, pkl_path, device, ...)
                results[(encoder_name, seed)] = result
            except Exception as e:
                logger.error(f"FAILED {encoder_name} seed={seed}: {e}")
                results[(encoder_name, seed)] = e
    return results
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | _train_epoch_with_aug | Epoch loop that passes training_aug=True to aug encoders (E2, E5) |
| L-3-2 | train_encoder_one_seed | Full training loop with val tracking, best-ckpt save, NaN recovery |
| L-3-3 | train_all_encoders + sanity_check_encoders | 18-run orchestration with soft-fail + 10-sample sanity check |

---

## A-4: Evaluation Extensions [Complexity: 16, Budget: 4]

Applied: Standard PyTorch inference pattern + sklearn R² + paired bootstrap all-pairs

### API Signatures

```python
# src/evaluate.py

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import r2_score
from typing import Optional


def compute_r2_score(
    model: nn.Module,
    test_loader,
    device: torch.device,
    encoder_name: str,
    severity: float = 0.0,
) -> float:
    """Compute sklearn R² at given severity. Returns float.
    Uses apply_stress_and_predict (reused from H-E1) for predictions.
    """
    ...


def compute_mediation_delta_r2(
    r2_by_encoder: dict,
) -> tuple:
    """ΔR² = mean R²(NFT-base) - mean R²(flat-MLP+aug) across seeds.

    Parameters
    ----------
    r2_by_encoder : dict
        {encoder_name: list[float]}  — one R² value per seed

    Returns
    -------
    tuple
        (delta_r2_mean: float, delta_r2_std: float)
    """
    ...


def evaluate_all_encoders(
    models_by_encoder: dict,
    test_loaders: dict,
    device: torch.device,
    severity_levels: list = None,    # default: SEVERITY_LEVELS from config
    n_bootstrap: int = 10000,
) -> dict:
    """Full evaluation: Δρ, R², bootstrap, all-pairs (15 pairs) Holm-corrected p-values.

    Parameters
    ----------
    models_by_encoder : dict
        {encoder_name: {seed: nn.Module}}
    test_loaders : dict
        {encoder_name: DataLoader}

    Returns
    -------
    dict
        {
            encoder_name: {
                "delta_rho_by_seed": {seed: float},
                "delta_rho_mean": float, "delta_rho_std": float,
                "rho_by_severity_by_seed": {seed: {s: float}},
                "r2_by_seed": {seed: float},
                "r2_mean": float, "r2_std": float,
                "bootstrap_samples_by_seed": {seed: np.ndarray},
                "p_values_by_seed": {seed: float},
            },
            "mediation_delta_r2": float,
            "mediation_delta_r2_std": float,
            "all_pairs_bootstrap": {
                (enc_a, enc_b): {"p_raw": float, "p_corrected": float, "effect_size": float}
            },
        }
    """
    ...


def _bootstrap_all_pairs(
    models_by_encoder: dict,
    test_loaders: dict,
    device: torch.device,
    n_bootstrap: int = 10000,
) -> dict:
    """Paired bootstrap for all C(6,2)=15 encoder pairs at s=1.0.

    Returns {(enc_a, enc_b): {"p_raw": float, "bootstrap_delta": np.ndarray[n_bootstrap]}}
    """
    ...


def evaluate_gate_condition_v2(
    results: dict,
    results_dir: str = "results/",
) -> dict:
    """H-M1 gate: nft_base_delta_rho < 0.02 AND mediation_delta_r2 >= 0.10.
    Writes gate_result.json. Returns gate result dict.
    """
    ...


def verify_mechanism_activated(
    results: dict,
) -> tuple:
    """5-indicator mechanism check.

    Returns (gate_pass: bool, indicators: dict)
    indicators keys: nft_base_robust, mediation_confirmed, aug_partial,
                     architecture_sufficient, ranking_correct
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| preds (per encoder) | [N] | N = test set size (>=500) |
| labels | [N] | gen gap scalars |
| bootstrap_samples | [n_bootstrap] | per-encoder per-seed |

### Pseudo-code — compute_r2_score

```
compute_r2_score(model, test_loader, device, encoder_name, severity=0.0):
    model_type = ENCODER_CONFIG[encoder_name]["model_type"]
    preds, labels = apply_stress_and_predict(model, test_loader, severity, device, model_type)
    return float(r2_score(labels, preds))
```

### Pseudo-code — evaluate_all_encoders

```
evaluate_all_encoders(models_by_encoder, test_loaders, device, severity_levels, n_bootstrap):
    severity_levels = severity_levels or SEVERITY_LEVELS
    results = {}
    r2_by_encoder = {}

    for enc_name in ENCODER_NAMES:
        enc_results = {"delta_rho_by_seed": {}, "r2_by_seed": {}, ...}
        for seed, model in models_by_encoder[enc_name].items():
            # load best checkpoint
            model.load_state_dict(torch.load(ckpt_path))
            delta_rho, rho_by_sev = compute_delta_rho(
                model, test_loaders[enc_name], severity_levels, device,
                ENCODER_CONFIG[enc_name]["model_type"])
            r2 = compute_r2_score(model, test_loaders[enc_name], device, enc_name, severity=0.0)
            bs_samples, p_val = bootstrap_delta_rho(
                model, test_loaders[enc_name], device,
                ENCODER_CONFIG[enc_name]["model_type"], n_bootstrap=n_bootstrap, seed=seed)
            enc_results["delta_rho_by_seed"][seed] = delta_rho
            enc_results["r2_by_seed"][seed] = r2
            enc_results["bootstrap_samples_by_seed"][seed] = bs_samples
            enc_results["p_values_by_seed"][seed] = p_val
        enc_results["delta_rho_mean"] = mean(delta_rho_by_seed.values())
        enc_results["delta_rho_std"] = std(delta_rho_by_seed.values())
        enc_results["r2_mean"] = mean(r2_by_seed.values())
        r2_by_encoder[enc_name] = list(enc_results["r2_by_seed"].values())
        results[enc_name] = enc_results

    delta_r2_mean, delta_r2_std = compute_mediation_delta_r2(r2_by_encoder)
    results["mediation_delta_r2"] = delta_r2_mean
    results["mediation_delta_r2_std"] = delta_r2_std

    # all-pairs bootstrap (15 pairs), Holm correction
    all_pairs = _bootstrap_all_pairs(models_by_encoder, test_loaders, device, n_bootstrap)
    raw_p = [v["p_raw"] for v in all_pairs.values()]
    corrected_p = holm_correction(raw_p)
    for i, k in enumerate(all_pairs.keys()):
        all_pairs[k]["p_corrected"] = corrected_p[i]
    results["all_pairs_bootstrap"] = all_pairs
    return results
```

### Pseudo-code — evaluate_gate_condition_v2

```
evaluate_gate_condition_v2(results, results_dir):
    nft_base_delta_rho = results["NFT-base"]["delta_rho_mean"]
    delta_r2 = results["mediation_delta_r2"]
    flat_aug_delta_rho = results["flat-MLP+aug"]["delta_rho_mean"]
    nft_base_robust = nft_base_delta_rho < 0.02
    mediation_confirmed = delta_r2 >= 0.10
    pass_gate = nft_base_robust and mediation_confirmed
    gate = {
        "pass_gate": pass_gate,
        "nft_base_delta_rho": nft_base_delta_rho,
        "mediation_delta_r2": delta_r2,
        "nft_base_robust": nft_base_robust,
        "mediation_confirmed": mediation_confirmed,
        "aug_partial": 0.05 < flat_aug_delta_rho < 0.10,
        "gate_criteria": {"nft_threshold": 0.02, "delta_r2_threshold": 0.10}
    }
    write gate to results_dir/gate_result.json
    return gate
```

### gate_result.json schema (H-M1 v2)

```json
{
  "pass_gate": true,
  "nft_base_delta_rho": 0.008,
  "mediation_delta_r2": 0.15,
  "nft_base_robust": true,
  "mediation_confirmed": true,
  "aug_partial": true,
  "gate_criteria": {"nft_threshold": 0.02, "delta_r2_threshold": 0.10},
  "indicators": {
    "nft_base_robust": true,
    "mediation_confirmed": true,
    "aug_partial": true,
    "architecture_sufficient": true,
    "ranking_correct": true
  }
}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | compute_r2_score + compute_mediation_delta_r2 | R² via sklearn, ΔR² across seeds |
| L-4-2 | evaluate_all_encoders | 6-encoder × 3-seed loop: Δρ + R² + per-seed bootstrap |
| L-4-3 | _bootstrap_all_pairs + Holm | C(6,2)=15 paired bootstrap at s=1.0 with Holm correction |
| L-4-4 | evaluate_gate_condition_v2 + verify_mechanism_activated | Gate write + 5-indicator check |

---

*Generated by Phase 3 Logic Agent*
*Hypothesis: H-M1 | Type: MECHANISM | Tier: FULL*
*Archon KB: low domain relevance — no matching DL ablation patterns found*
*Serena: H-E1 actual code verified by direct file read (models.py, train.py, evaluate.py, data_loader.py)*
