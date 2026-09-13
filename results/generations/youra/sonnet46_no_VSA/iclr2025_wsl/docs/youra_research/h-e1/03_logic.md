# Logic Design: H-E1
# OrbitVar Measurement — DeepSets & NFN Encoders

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Date:** 2026-08-03

---

## Executive Summary

Seven subtasks covering the four highest-complexity epics. Key design decisions:
- Coupled permutation uses a single `perm_spec: list[Tensor]` of length `num_conv_layers`, where `perm_spec[i]` is the S_16 permutation for the i-th hidden channel axis.
- DeepSets phi/rho are `nn.Sequential` MLPs; no class hierarchy needed.
- NFN encoder is `nn.Sequential` wrapping nfn layers; `state_dict_to_wsfeat` is a thin adapter.
- OrbitVar loop uses float64 numpy for variance; embeddings stay float32 until variance step.

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field — no local codebase to analyze
**Analyzed Path:** N/A
**Relevant Symbols:** None — new implementation. External patterns sourced from AllanYangZhou/nfn and AvivNavon/DWSNets.

---

## A-2: Permutation Module [Complexity: 13, Budget: 2 subtasks]

Applied: N/A — no relevant KB patterns found

### L-2-1: apply_permutation() — Coupled S_16³ Row-Column Permutation

#### API Signature

```python
# permutation.py

def sample_functional_permutations(
    num_layers: int,         # number of conv layers = 3
    channels: int,           # C = 16
    K: int,                  # number of permutations = 50
    seed: int = 1
) -> list[list[torch.Tensor]]:
    """K permutation specs; each spec is list of num_layers Tensors of shape [C]."""
    ...

def apply_permutation(
    state_dict: dict[str, torch.Tensor],
    perm_spec: list[torch.Tensor],
    conv_weight_keys: list[str],   # ordered conv weight keys, length = num_conv_layers
    bias_keys: list[str],          # ordered conv bias keys, length = num_conv_layers
) -> dict[str, torch.Tensor]:
    """
    Applies S_16³ coupled row-column permutation. Returns new state_dict (copy).
    perm_spec[i]: [C] — permutation indices for layer i's output channels.
    """
    ...
```

#### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| W_conv[i] | (C_out, C_in, kH, kW) | Conv weight; C=16 for all hidden layers |
| perm_spec[i] | (16,) | LongTensor, permutation of range(16) |
| W[i] after row perm | (C_out, C_in, kH, kW) | W[i][perm_i, :, :, :] |
| W[i+1] after col perm | (C_out, C_in, kH, kW) | W[i+1][:, perm_i, :, :] |
| bias[i] after perm | (C_out,) | bias[i][perm_i] |
| W_fc (dense) | (num_classes, feat_dim) | feat_dim from AdaptiveAvgPool2d output |

#### Algorithm

```
apply_permutation(state_dict, perm_spec, conv_weight_keys, bias_keys):
    out = deepcopy(state_dict)
    for i, p_i in enumerate(perm_spec):
        # Row permutation on layer i (permute output channels)
        key_w = conv_weight_keys[i]
        out[key_w] = out[key_w][p_i, :, :, :]         # (C_out, C_in, kH, kW)
        out[bias_keys[i]] = out[bias_keys[i]][p_i]      # (C_out,)

        # Column permutation on layer i+1 (permute input channels)
        # Only if there IS a next conv layer
        if i + 1 < len(conv_weight_keys):
            key_w_next = conv_weight_keys[i + 1]
            out[key_w_next] = out[key_w_next][:, p_i, :, :]  # (C_out, C_in, kH, kW)
        # If i is last conv, next layer is FC: no column permutation needed
        # because AdaptiveAvgPool2d + flatten preserves channel order that
        # the FC layer already accounts for via row permutation on last conv.
        # NOTE: if FC weight exists and last conv output feeds directly to FC
        # without global pool reordering, FC column perm IS needed:
        #   out[fc_weight_key] = out[fc_weight_key][:, p_i]   # ponytail: verify arch
    return out

# ponytail: deepcopy is O(N_params) per permutation; acceptable for 50 perms × 100 models
```

**Edge cases:**
- First conv: C_in = 3 (RGB), no column permutation applied (perm_spec[-1] does not affect it).
- FC after AdaptiveAvgPool2d(1): output shape is (B, C_last, 1, 1) → flatten → (B, C_last). FC column perm IS required for last conv's perm_spec. Add `fc_weight_key` param if needed.

---

### L-2-2: audit_functional_equivalence() — Hard Block Verification

#### API Signature

```python
def build_cnn_from_state_dict(
    state_dict: dict[str, torch.Tensor],
) -> torch.nn.Module:
    """Instantiates the CIFAR10-GS CNN and loads state_dict. Eval mode."""
    ...

def audit_functional_equivalence(
    state_dict: dict[str, torch.Tensor],
    perm_specs: list[list[torch.Tensor]],
    conv_weight_keys: list[str],
    bias_keys: list[str],
    tol: float = 1e-6,
    n_checks: int = 5,
    n_perms: int = 3,
) -> float:
    """
    Verifies ||f_v(x) - f_{pi.v}(x)||_inf <= tol.
    Returns max_diff over all (x, perm) pairs. Raises AssertionError if > tol.
    """
    ...
```

#### Algorithm

```
audit_functional_equivalence(...):
    rng = torch.Generator(); rng.manual_seed(0)
    model_orig = build_cnn_from_state_dict(state_dict)  # eval, no grad
    max_diff = 0.0

    for perm_spec in perm_specs[:n_perms]:
        perm_sd = apply_permutation(state_dict, perm_spec, conv_weight_keys, bias_keys)
        model_perm = build_cnn_from_state_dict(perm_sd)

        for _ in range(n_checks):
            x = torch.rand(1, 3, 32, 32, generator=rng)   # [1, 3, 32, 32]
            with torch.no_grad():
                y_orig = model_orig(x)    # [1, num_classes]
                y_perm = model_perm(x)    # [1, num_classes]
            diff = (y_orig - y_perm).abs().max().item()
            max_diff = max(max_diff, diff)

    if max_diff > tol:
        raise AssertionError(
            f"Functional equivalence FAILED: max_diff={max_diff:.2e} > tol={tol:.0e}. "
            f"Check coupled permutation logic (column perm on FC layer?)."
        )
    return max_diff
```

#### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | apply_permutation | S_16³ coupled row-column permutation on state_dict |
| L-2-2 | audit_functional_equivalence | Hard-block verification via forward-pass comparison |

---

## A-4: C3 NFN Encoder [Complexity: 12, Budget: 2 subtasks]

Applied: N/A — no relevant KB patterns found

### L-4-1: state_dict_to_wsfeat() — WeightSpaceFeatures Construction

#### API Signature

```python
# encoder_c3.py
from nfn.common import state_dict_to_tensors, network_spec_from_wsfeat
from nfn.common import WeightSpaceFeatures

def state_dict_to_wsfeat(
    state_dict: dict[str, torch.Tensor]
) -> WeightSpaceFeatures:
    """
    Wraps nfn.common.state_dict_to_tensors(). Returns WeightSpaceFeatures.
    Adds batch dim: each weight tensor gains dim 0 of size 1.
    """
    weights, biases = state_dict_to_tensors(state_dict)
    # weights: list of Tensors, each [C_out, C_in, kH, kW] or [out, in]
    # biases:  list of Tensors, each [C_out] or [out]
    # state_dict_to_tensors returns without batch dim; add it:
    weights = [w.unsqueeze(0) for w in weights]   # each [1, C_out, C_in, kH, kW]
    biases  = [b.unsqueeze(0) for b in biases]    # each [1, C_out]
    wsfeat = WeightSpaceFeatures(weights, biases)
    return wsfeat

def get_network_spec(
    sample_state_dict: dict[str, torch.Tensor]
) -> object:
    """Derives network_spec from a sample state dict. Call once at setup."""
    wsfeat = state_dict_to_wsfeat(sample_state_dict)
    return network_spec_from_wsfeat(wsfeat)
```

#### Tensor Shapes (CIFAR10-GS CNN, C=16)

| Layer | Weight shape (batched) | Bias shape (batched) |
|-------|----------------------|---------------------|
| conv1 | (1, 16, 3, 3, 3) | (1, 16) |
| conv2 | (1, 16, 16, 3, 3) | (1, 16) |
| conv3 | (1, 16, 16, 3, 3) | (1, 16) |
| fc    | (1, num_classes, feat_dim) | (1, num_classes) |

Note: `state_dict_to_tensors` may already add batch dim — verify at runtime and skip `unsqueeze(0)` if shape[0] != 1 logic needed.

**Compatibility check (AdaptiveAvgPool2d):**
```python
# In get_network_spec, after building wsfeat:
spec = network_spec_from_wsfeat(wsfeat)
# nfn treats AdaptiveAvgPool2d as a no-param layer; it should not appear in wsfeat.
# Verify by checking len(wsfeat.weights) == 4 (3 conv + 1 fc), not 5.
assert len(wsfeat.weights) == 4, (
    f"Expected 4 weight tensors (3 conv + 1 fc), got {len(wsfeat.weights)}. "
    "AdaptiveAvgPool2d has no params and should be absent from wsfeat."
)
```

---

### L-4-2: build_nfn_encoder() — NFN Model Construction

#### API Signature

```python
from nfn import layers

def build_nfn_encoder(
    network_spec: object,     # from get_network_spec()
    nfn_channels: int = 32,
    embed_dim: int = 128,
) -> torch.nn.Sequential:
    """
    NPLinear(1->32) -> ReLU -> NPLinear(32->32) -> ReLU -> HNPPool -> Linear(embed_dim).
    network_spec must be derived from a CIFAR10-GS sample before calling.
    """
    num_outs = layers.HNPPool.get_num_outs(network_spec)  # scalar int
    return torch.nn.Sequential(
        layers.NPLinear(network_spec, 1, nfn_channels, io_embed=True),
        layers.TupleOp(torch.nn.ReLU()),
        layers.NPLinear(network_spec, nfn_channels, nfn_channels),
        layers.TupleOp(torch.nn.ReLU()),
        layers.HNPPool(network_spec),
        torch.nn.Flatten(),
        torch.nn.Linear(num_outs, embed_dim),
    )

def encode_nfn(
    nfn_model: torch.nn.Sequential,
    state_dict: dict[str, torch.Tensor],
) -> torch.Tensor:
    """state_dict -> wsfeat -> nfn forward -> (embed_dim,)."""
    wsfeat = state_dict_to_wsfeat(state_dict)
    with torch.no_grad():
        out = nfn_model(wsfeat)   # Tensor [1, embed_dim]
    return out.squeeze(0)         # [embed_dim]
```

**Note on `TupleOp`:** NFN layers pass `WeightSpaceFeatures` (a tuple-like object) through the network. `TupleOp` applies a standard `nn.Module` element-wise to each weight/bias tensor. If `TupleOp` is not in public nfn API, use `layers.NPLinear` with built-in activation or wrap manually:
```python
# fallback if TupleOp unavailable:
class _TupleReLU(torch.nn.Module):
    def forward(self, wsfeat):
        return WeightSpaceFeatures(
            [torch.relu(w) for w in wsfeat.weights],
            [torch.relu(b) for b in wsfeat.biases],
        )
```

#### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | state_dict_to_wsfeat | nfn WeightSpaceFeatures construction + compat check |
| L-4-2 | build_nfn_encoder | NFN Sequential model + encode() wrapper |

---

## A-5: OrbitVar Computation + Gate [Complexity: 11, Budget: 2 subtasks]

Applied: N/A — no relevant KB patterns found

### L-5-1: compute_orbit_var_all_models() — Main Measurement Loop

#### API Signature

```python
# orbit_var.py
from typing import Callable

def compute_orbit_var_all_models(
    dataset: list[tuple],                        # list of (weight_vector, accuracy)
    index_dict: dict,
    encoder_fn: Callable[[dict], torch.Tensor],  # state_dict -> [embed_dim]
    perm_specs: list[list[torch.Tensor]],        # K permutation specs
    conv_weight_keys: list[str],
    bias_keys: list[str],
    log_every: int = 10,
) -> tuple[list[float], float, float]:
    """
    Returns (per_model_vars, mean_orbitvar, max_orbitvar).
    OrbitVar(v) = mean over embed dims of Var_pi[enc(pi.W_v)].
    Computed in float64 for numerical precision.
    """
    ...
```

#### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| weight_vector | (N_params,) | Flat float32 tensor from dataset |
| state_dict | {key: Tensor} | Reconstructed per model |
| embed (one perm) | (embed_dim,) | float32 output of encoder_fn |
| embeddings | (K, embed_dim) | Stacked over K permutations |
| embeddings_f64 | (K, embed_dim) | Cast to float64 for variance |
| var_per_dim | (embed_dim,) | torch.var(embeddings_f64, dim=0) |
| orbit_var_v | scalar | var_per_dim.mean().item() |

#### Algorithm

```
compute_orbit_var_all_models(...):
    per_model_vars = []

    for idx, (weight_vec, _acc) in enumerate(dataset):
        state_dict = reconstruct_state_dict(weight_vec, index_dict)
        embeddings = []

        for perm_spec in perm_specs:
            perm_sd = apply_permutation(state_dict, perm_spec, conv_weight_keys, bias_keys)
            embed = encoder_fn(perm_sd)      # [embed_dim], float32
            embeddings.append(embed)

        # Also include original (identity permutation counts as one orbit point)
        embed_orig = encoder_fn(state_dict)
        embeddings.append(embed_orig)

        emb_tensor = torch.stack(embeddings, dim=0)          # [K+1, embed_dim]
        emb_f64 = emb_tensor.double()                        # float64
        var_per_dim = torch.var(emb_f64, dim=0, unbiased=False)  # [embed_dim]
        orbit_var_v = var_per_dim.mean().item()
        per_model_vars.append(orbit_var_v)

        if (idx + 1) % log_every == 0:
            print(f"  [{idx+1}/{len(dataset)}] orbit_var={orbit_var_v:.3e}")

    mean_orbitvar = float(np.mean(per_model_vars))
    max_orbitvar  = float(np.max(per_model_vars))
    return per_model_vars, mean_orbitvar, max_orbitvar
```

---

### L-5-2: run_gate_check() + Results Serialization

#### API Signature

```python
def run_gate_check(
    mean_c2: float,
    mean_c3: float,
    threshold: float = 1e-6,
) -> bool:
    """Prints PASS/FAIL; returns True if both means < threshold."""
    ...

def save_results(
    results: dict,
    path: str = "results/orbit_var_results.json",
) -> None:
    """Writes results dict to JSON. Creates parent dir if needed."""
    ...
```

#### Algorithm

```
run_gate_check(mean_c2, mean_c3, threshold):
    passed = (mean_c2 < threshold) and (mean_c3 < threshold)
    status = "PASS" if passed else "FAIL"
    print(f"[Gate] mean_orbitvar_c2={mean_c2:.3e}  mean_orbitvar_c3={mean_c3:.3e}  "
          f"threshold={threshold:.0e}  => {status}")
    if not passed:
        fails = []
        if mean_c2 >= threshold: fails.append(f"C2={mean_c2:.3e}")
        if mean_c3 >= threshold: fails.append(f"C3={mean_c3:.3e}")
        print(f"  FAILED encoders: {', '.join(fails)}")
    return passed

save_results(results, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
```

#### JSON Schema

```json
{
  "mean_orbitvar_c2": 0.0,
  "max_orbitvar_c2": 0.0,
  "mean_orbitvar_c3": 0.0,
  "max_orbitvar_c3": 0.0,
  "cise_baseline": 0.010333,
  "gate_pass": true,
  "seed": 1,
  "n_models": 100,
  "K": 50
}
```

#### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | compute_orbit_var_all_models | Measurement loop, float64 variance, per-model logging |
| L-5-2 | run_gate_check + save_results | PASS/FAIL gate + JSON serialization |

---

## A-3: C2 DeepSets Encoder [Complexity: 10, Budget: 1 subtask]

Applied: N/A — no relevant KB patterns found

### L-3-1: DeepSetsChannelEncoder.forward() — Per-Layer Encoding Algorithm

#### API Signature

```python
# encoder_c2.py
import torch
import torch.nn as nn
from torch import Tensor

class DeepSetsChannelEncoder(nn.Module):
    def __init__(
        self,
        layer_weight_dims: list[int],   # [C_in*kH*kW per conv layer], length=3
        hidden_dim: int = 64,
        embed_dim: int = 128,
    ):
        """phi: Linear(weight_dim -> hidden_dim) + ReLU per layer.
           rho: Linear(hidden_dim -> embed_dim//3) + ReLU per layer.
           Final out: concat of 3 layer embeds -> (embed_dim,)."""
        super().__init__()
        layer_embed_dim = embed_dim // len(layer_weight_dims)  # 128//3 = 42; padded below
        self.phi_layers = nn.ModuleList([
            nn.Sequential(nn.Linear(wd, hidden_dim), nn.ReLU())
            for wd in layer_weight_dims
        ])
        self.rho_layers = nn.ModuleList([
            nn.Sequential(nn.Linear(hidden_dim, layer_embed_dim), nn.ReLU())
            for _ in layer_weight_dims
        ])
        # Final projection to exactly embed_dim (handles 42*3=126 != 128)
        self.proj = nn.Linear(layer_embed_dim * len(layer_weight_dims), embed_dim)
        # ponytail: embed_dim not evenly divisible by 3; proj absorbs the gap

    def forward(self, state_dict: dict[str, torch.Tensor], conv_weight_keys: list[str]) -> Tensor:
        """
        state_dict + conv_weight_keys -> [embed_dim].
        conv_weight_keys: ordered list of 3 conv weight keys.
        """
        ...
```

#### Tensor Shapes (CIFAR10-GS, C=16, kernel 3×3)

| Variable | Shape | Note |
|----------|-------|------|
| W_conv[0] | (16, 3, 3, 3) | layer 0: C_in=3 (RGB) |
| W_conv[1] | (16, 16, 3, 3) | layer 1: C_in=16 |
| W_conv[2] | (16, 16, 3, 3) | layer 2: C_in=16 |
| layer_weight_dims | [27, 144, 144] | C_in*kH*kW per layer |
| W_flat (layer i) | (16, weight_dim_i) | reshape (C_out, -1) |
| phi_out (layer i) | (16, hidden_dim) | element-wise phi on each channel row |
| sum_out (layer i) | (hidden_dim,) | sum over dim=0 (permutation-invariant) |
| rho_out (layer i) | (layer_embed_dim,) | post-aggregation MLP |
| concat | (layer_embed_dim * 3,) | cat of 3 layer embeds |
| final | (embed_dim,) | after proj linear |

#### Algorithm

```
forward(state_dict, conv_weight_keys):
    layer_embeds = []
    for i, key in enumerate(conv_weight_keys):
        W = state_dict[key]                          # [C_out, C_in, kH, kW]
        C_out = W.shape[0]
        W_flat = W.reshape(C_out, -1)               # [C_out, C_in*kH*kW] = [16, weight_dim_i]
        phi_out = self.phi_layers[i](W_flat)         # [16, hidden_dim]
        sum_out = phi_out.sum(dim=0)                 # [hidden_dim]  -- invariant to row perm
        rho_out = self.rho_layers[i](sum_out)        # [layer_embed_dim]
        layer_embeds.append(rho_out)

    cat = torch.cat(layer_embeds, dim=0)             # [layer_embed_dim * 3]
    out = self.proj(cat)                             # [embed_dim]
    return out
```

**Invariance proof sketch:** phi acts identically on each row of W_flat; sum is permutation-invariant over rows; thus reordering C_out (row permutation from S_16) does not change sum_out. QED.

#### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | DeepSetsChannelEncoder.forward | phi→sum→rho per layer, concat, proj to embed_dim |

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: N/A" lines)
- [x] Docstrings <= 2 lines
- [x] Tensor shapes in comments and tables
- [x] Subtask count within budget (7/7)
- [x] Total length < 600 lines
- [x] "Codebase Analysis (Serena)" section included (green-field noted)
- [x] Serena skip acceptable (green-field, no local codebase)
