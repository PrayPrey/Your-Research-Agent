# Logic: H-E1

**hypothesis_id:** h-e1
**hypothesis_type:** EXISTENCE (PoC)
**generated_at:** 2026-03-16

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - no code to analyze
**Analyzed Path:** N/A (Serena returned no active project for TEST_wsl; no `src/` or `code/` directory exists)
**Relevant Symbols:** None - new implementation

---

## E-2: Model Implementation [Complexity: 14, Budget: 4]

**Applied:** PyTorch canonical attention pattern (nn.MultiheadAttention with batch_first=True)

### API Signatures

```python
# src/models.py

import torch
import torch.nn as nn
from torch import Tensor
from typing import Optional

class FlatMLPEncoder(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 512) -> None:
        """3-layer ReLU MLP for flattened weight vectors. Kaiming init applied."""
        ...

    def forward(self, x: Tensor) -> Tensor:
        """x: [B, input_dim] -> [B, 1]"""
        ...


class NFTEquivariantEncoder(nn.Module):
    def __init__(
        self,
        layer_fan_ins: list[int],   # e.g. [784, 256, 128] — one per layer
        d_model: int = 128,
        n_heads: int = 4,
    ) -> None:
        """NFT encoder with per-layer projections + equivariant attention.
        Raises ValueError if any fan_in <= 0."""
        ...

    def forward(self, weight_matrices: list[Tensor]) -> Tensor:
        """weight_matrices: list of [B, n_neurons_l, fan_in_l] -> [B, 1]
        Logs: 'NFT tokens: (B={B}, N_neurons={total_neurons}, d_model={d_model})'
        Stores last_token_shape = (B, total_neurons, d_model)."""
        ...

    def get_last_token_shape(self) -> tuple[int, int, int]:
        """Returns (B, total_neurons, d_model) from last forward call."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| x (FlatMLP input) | [B, input_dim] | input_dim = sum of all flattened layer elements |
| weight_matrices[l] | [B, n_neurons_l, fan_in_l] | one tensor per layer |
| tokens_l | [B, n_neurons_l, d_model] | after layer_projections[l] |
| all_tokens | [B, total_neurons, d_model] | concat across all layers on dim=1 |
| attn_out | [B, total_neurons, d_model] | after MultiheadAttention + residual + LN |
| pooled | [B, d_model] | mean over dim=1 |
| output | [B, 1] | regression head |

---

### Subtask L-2-1: FlatMLPEncoder

**Parent Epic:** E-2
**Title:** Implement FlatMLPEncoder with 3x512 ReLU MLP
**Description:** Build `FlatMLPEncoder.__init__` using `nn.Sequential` with 3 hidden layers of 512 units and ReLU activations, plus output `nn.Linear(512, 1)`. Apply `nn.init.kaiming_uniform_` to all Linear weights.
**API Target:** `FlatMLPEncoder.__init__`, `FlatMLPEncoder.forward`
**Acceptance Criteria:** `model = FlatMLPEncoder(5000); out = model(torch.randn(32, 5000)); assert out.shape == (32, 1)`

---

### Subtask L-2-2: NFTEquivariantEncoder — Per-Layer Projection

**Parent Epic:** E-2
**Title:** Build layer_fan_ins discovery and ModuleList projections
**Description:** In `__init__`, validate all fan_in > 0 (raise `ValueError("fan_in must be > 0, got {fan_in}")`). Build `self.layer_projections = nn.ModuleList([nn.Linear(fan_in, d_model) for fan_in in layer_fan_ins])`. `layer_fan_ins` is constructed in `run_experiment.py` by inspecting the first dataset sample: `layer_fan_ins = [wm.shape[1] for wm in sample_nft_item[0]]`.
**API Target:** `NFTEquivariantEncoder.__init__`
**Acceptance Criteria:** `NFTEquivariantEncoder([784, 256]) ` creates `len(model.layer_projections) == 2`; `NFTEquivariantEncoder([-1])` raises `ValueError`

---

### Subtask L-2-3: NFTEquivariantEncoder — Attention Forward Pass

**Parent Epic:** E-2
**Title:** Implement equivariant attention forward with token shape logging
**Description:** Implement `forward()` with the following steps. Also build `self.attn = nn.MultiheadAttention(d_model, n_heads, batch_first=True)`, `self.norm = nn.LayerNorm(d_model)`, `self.head = nn.Linear(d_model, 1)` in `__init__`.
**API Target:** `NFTEquivariantEncoder.forward`, `NFTEquivariantEncoder.get_last_token_shape`
**Acceptance Criteria:** With `layer_fan_ins=[784, 256]`, forward on `[torch.randn(8, 32, 784), torch.randn(8, 64, 256)]` returns shape `(8, 1)` and `model.get_last_token_shape() == (8, 96, 128)`

**Pseudo-code:**
```
forward(weight_matrices):
    token_seqs = []
    for l, W_l in enumerate(weight_matrices):          # W_l: [B, n_neurons_l, fan_in_l]
        tokens_l = self.layer_projections[l](W_l)      # [B, n_neurons_l, d_model]
        token_seqs.append(tokens_l)

    all_tokens = torch.cat(token_seqs, dim=1)          # [B, total_neurons, d_model]
    B, N, D = all_tokens.shape
    self.last_token_shape = (B, N, D)
    logger.info(f"NFT tokens: (B={B}, N_neurons={N}, d_model={D})")

    attn_out, _ = self.attn(all_tokens, all_tokens, all_tokens)  # [B, N, d_model]
    attn_out = self.norm(attn_out + all_tokens)                   # residual + LN

    pooled = attn_out.mean(dim=1)                      # [B, d_model]
    return self.head(pooled)                            # [B, 1]
```

---

### Subtask L-2-4: nft_collate_fn — Variable Sequence Padding

**Parent Epic:** E-2
**Title:** Implement nft_collate_fn with per-layer padding and attention mask
**Description:** Each batch item has a different total neuron count (sum of n_neurons across layers). Pad each layer's weight matrices to max n_neurons for that layer in the batch. Generate a boolean attention mask for masked MultiheadAttention.
**API Target:** `nft_collate_fn` in `src/data_loader.py`
**Acceptance Criteria:** Collating a batch with items having `[32, 64]` and `[16, 128]` neurons per layer produces padded tensors and `attention_mask` shape `[B, max_total_neurons]` with correct False (attend) / True (ignore) values.

**Pseudo-code:**
```
nft_collate_fn(batch):
    # batch: list of (list_of_weight_matrices, label)
    # Step 1: find max n_neurons per layer across batch
    n_layers = len(batch[0][0])
    max_neurons_per_layer = [max(item[0][l].shape[0] for item in batch) for l in range(n_layers)]

    padded_by_layer = []
    mask_by_layer = []
    for l in range(n_layers):
        max_n = max_neurons_per_layer[l]
        fan_in = batch[0][0][l].shape[1]
        padded_l = torch.zeros(B, max_n, fan_in)   # [B, max_n_l, fan_in_l]
        mask_l = torch.ones(B, max_n, dtype=torch.bool)  # True = ignore (padding)
        for b, (wms, _) in enumerate(batch):
            n = wms[l].shape[0]
            padded_l[b, :n, :] = wms[l]
            mask_l[b, :n] = False  # attend to real neurons
        padded_by_layer.append(padded_l)
        mask_by_layer.append(mask_l)

    attention_mask = torch.cat(mask_by_layer, dim=1)   # [B, total_neurons]
    labels = torch.stack([item[1] for item in batch])  # [B]
    return padded_by_layer, labels, attention_mask
    # Returns: (list[Tensor([B, max_n_l, fan_in_l])], Tensor([B]), Tensor([B, total_neurons]))
```

---

## E-4: Evaluation & Gate [Complexity: 14, Budget: 4]

**Applied:** Standard PyTorch inference pattern + scipy.stats.spearmanr

### API Signatures

```python
# src/evaluate.py

import numpy as np
from scipy.stats import spearmanr
from typing import TypedDict

class GateResult(TypedDict):
    pass_gate: bool
    flat_mlp_delta_rho: float
    nft_delta_rho: float
    flat_threshold_met: bool   # flat_mlp_delta_rho > 0.10
    nft_threshold_met: bool    # nft_delta_rho < 0.02
    flat_mlp_p_corrected: float
    nft_p_corrected: float


def apply_stress_and_predict(
    model: nn.Module,
    test_loader: DataLoader,
    severity: float,
    device: torch.device,
    model_type: str,          # "flat" | "nft"
) -> tuple[np.ndarray, np.ndarray]:
    """Run inference with permutation stress. Returns (predictions [N], labels [N])."""
    ...


def compute_delta_rho(
    model: nn.Module,
    test_loader: DataLoader,
    severity_levels: list[float],  # e.g. [0, 0.25, 0.5, 1.0]
    device: torch.device,
    model_type: str,
) -> tuple[float, dict[float, float]]:
    """Returns (delta_rho, rho_by_severity). Raises ValueError if n_samples < 2."""
    ...


def bootstrap_delta_rho(
    model: nn.Module,
    test_loader: DataLoader,
    device: torch.device,
    model_type: str,
    n_bootstrap: int = 10000,
    seed: int = 42,
) -> tuple[np.ndarray, float]:
    """Returns (bootstrap_samples [n_bootstrap], p_value).
    p_value = fraction of bootstrap_samples <= 0 (one-sided: H1: delta_rho > 0)."""
    ...


def holm_correction(p_values: list[float]) -> list[float]:
    """Holm step-down correction. Returns corrected p-values (same order as input)."""
    ...


def evaluate_gate_condition(
    flat_mlp_delta_rho: float,
    nft_delta_rho: float,
    flat_mlp_p: float,
    nft_p: float,
) -> GateResult:
    """Gate PASS iff flat_mlp_delta_rho > 0.10 AND nft_delta_rho < 0.02."""
    ...


def verify_mechanism_activated(
    model: nn.Module,
    sample_batch: tuple,
    results: dict,
) -> tuple[bool, dict[str, bool]]:
    """3-indicator check. Returns (all_pass, indicators)."""
    ...
```

---

### Subtask L-4-1: compute_delta_rho

**Parent Epic:** E-4
**Title:** Implement Spearman rho computation across severity levels
**Description:** For each severity in `severity_levels`, call `apply_stress_and_predict` to get all predictions and labels over the test set, then compute `spearmanr`. Compute `delta_rho = rho[0] - rho[1.0]`. Raise `ValueError` if total collected samples < 2.
**API Target:** `compute_delta_rho`, `apply_stress_and_predict`
**Acceptance Criteria:** On a mock model returning constants, `compute_delta_rho` returns a float delta and dict with keys `{0, 0.25, 0.5, 1.0}`.

**Pseudo-code:**
```
compute_delta_rho(model, test_loader, severity_levels, device, model_type):
    rho_by_severity = {}
    for s in severity_levels:
        preds, labels = apply_stress_and_predict(model, test_loader, s, device, model_type)
        if len(preds) < 2:
            raise ValueError(f"n_samples={len(preds)} < 2")
        rho, _ = spearmanr(preds, labels)
        rho_by_severity[s] = float(rho)
    delta_rho = rho_by_severity[0.0] - rho_by_severity[1.0]
    return delta_rho, rho_by_severity

apply_stress_and_predict(model, test_loader, severity, device, model_type):
    model.eval()
    all_preds, all_labels = [], []
    with torch.no_grad():
        for batch in test_loader:
            if model_type == "flat":
                x, labels = batch[0].to(device), batch[1]
                if severity > 0:
                    x = apply_flat_stress(x, severity)  # reshape->permute->reshape
                preds = model(x).cpu().squeeze(-1)
            else:  # nft
                wms, labels, mask = [t.to(device) for t in batch[0]], batch[1], batch[2].to(device)
                if severity > 0:
                    wms = [apply_permutation_stress_batch(wm, severity) for wm in wms]
                preds = model(wms).cpu().squeeze(-1)
            all_preds.append(preds.numpy())
            all_labels.append(labels.numpy())
    return np.concatenate(all_preds), np.concatenate(all_labels)
```

---

### Subtask L-4-2: bootstrap_delta_rho

**Parent Epic:** E-4
**Title:** Implement paired bootstrap with p-value and seed management
**Description:** Pre-collect all (preds_s0, preds_s1, labels) arrays. For each of n_bootstrap iterations, resample indices with replacement, compute delta_rho on the subsample. p_value = fraction of bootstrap samples <= 0 (one-sided test that delta_rho > 0).
**API Target:** `bootstrap_delta_rho`
**Acceptance Criteria:** Returns `(np.ndarray shape (10000,), float p_value)` with deterministic output given same seed.

**Pseudo-code:**
```
bootstrap_delta_rho(model, test_loader, device, model_type, n_bootstrap=10000, seed=42):
    rng = np.random.default_rng(seed)

    # collect all predictions at s=0 and s=1.0
    preds_s0, labels = apply_stress_and_predict(model, test_loader, 0.0, device, model_type)
    preds_s1, _      = apply_stress_and_predict(model, test_loader, 1.0, device, model_type)
    n = len(labels)

    bootstrap_samples = np.empty(n_bootstrap, dtype=np.float64)
    for i in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)                    # resample with replacement
        rho0, _ = spearmanr(preds_s0[idx], labels[idx])
        rho1, _ = spearmanr(preds_s1[idx], labels[idx])
        bootstrap_samples[i] = rho0 - rho1

    p_value = float(np.mean(bootstrap_samples <= 0))        # fraction <= 0
    return bootstrap_samples, p_value                       # [n_bootstrap], float
```

---

### Subtask L-4-3: evaluate_gate_condition & holm_correction

**Parent Epic:** E-4
**Title:** Implement gate logic, Holm correction, and gate_result.json writer
**Description:** `holm_correction` implements the step-down Holm procedure. `evaluate_gate_condition` applies thresholds and writes `results/gate_result.json`.
**API Target:** `evaluate_gate_condition`, `holm_correction`
**Acceptance Criteria:** `evaluate_gate_condition(0.15, 0.01, 0.001, 0.001)` returns `GateResult` with `pass_gate=True`; `evaluate_gate_condition(0.05, 0.01, 0.1, 0.1)` returns `pass_gate=False`.

**Holm correction pseudo-code:**
```
holm_correction(p_values: list[float]) -> list[float]:
    m = len(p_values)
    sorted_idx = np.argsort(p_values)          # ascending
    corrected = np.array(p_values, dtype=float)
    for rank, idx in enumerate(sorted_idx):
        corrected[idx] = p_values[idx] * (m - rank)
    # enforce monotonicity (step-down)
    corrected = np.minimum.accumulate(corrected[sorted_idx][::-1])[::-1]
    result = np.empty(m)
    result[sorted_idx] = corrected
    return np.clip(result, 0.0, 1.0).tolist()
```

**gate_result.json schema:**
```json
{
  "pass_gate": true,
  "flat_mlp_delta_rho": 0.23,
  "nft_delta_rho": 0.008,
  "flat_threshold_met": true,
  "nft_threshold_met": true,
  "flat_mlp_p_corrected": 0.0012,
  "nft_p_corrected": 0.0034,
  "gate_criteria": {
    "flat_mlp_threshold": 0.10,
    "nft_threshold": 0.02,
    "significance_threshold": 0.05
  }
}
```

---

### Subtask L-4-4: verify_mechanism_activated

**Parent Epic:** E-4
**Title:** Implement 3-indicator mechanism verification
**Description:** Check 3 indicators using `model.get_last_token_shape()`, comparison of `rho_s0 != rho_s1` from results dict, and `nft_delta_rho < flat_mlp_delta_rho` from results dict. Called in `run_experiment.py` after evaluation.
**API Target:** `verify_mechanism_activated`
**Acceptance Criteria:** Returns `(True, {"tokens_shaped_correctly": True, "permutation_changes_output": True, "nft_more_robust": True})` when all conditions hold.

```python
def verify_mechanism_activated(
    model: nn.Module,
    sample_batch: tuple,
    results: dict,
) -> tuple[bool, dict[str, bool]]:
    """
    results keys expected: rho_s0_nft, rho_s1_nft, nft_delta_rho, flat_mlp_delta_rho
    model must be NFTEquivariantEncoder with get_last_token_shape().
    """
    # run one forward to populate last_token_shape
    with torch.no_grad():
        wms = sample_batch[0]
        _ = model(wms)

    B, N, D = model.get_last_token_shape()
    d_model = model.d_model  # stored as attribute in __init__

    indicators = {
        "tokens_shaped_correctly": (
            N > 0 and D == d_model
        ),
        "permutation_changes_output": (
            results.get("rho_s0_nft") != results.get("rho_s1_nft")
        ),
        "nft_more_robust": (
            results["nft_delta_rho"] < results["flat_mlp_delta_rho"]
        ),
    }
    all_pass = all(indicators.values())
    return all_pass, indicators
```

**Integration in run_experiment.py:**
```python
# After evaluate both models:
all_pass, indicators = verify_mechanism_activated(nft_model, sample_nft_batch, results)
results["mechanism_verified"] = all_pass
results["mechanism_indicators"] = indicators
```

---

*Generated by Phase 3 Logic Agent*
*Hypothesis: H-E1 | Type: EXISTENCE | Tier: LIGHT*
*Archon KB: low domain relevance — design grounded in Zhou et al. 2023 + Unterthiner et al. 2020*
*Serena: green-field confirmed (no active project code found)*
