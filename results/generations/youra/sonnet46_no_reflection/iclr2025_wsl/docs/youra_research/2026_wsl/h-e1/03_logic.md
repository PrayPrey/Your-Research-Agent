# Logic: H-E1 — Canonical Channel Permutation Invariance & Orbit-PE Computability

**Hypothesis Type**: EXISTENCE (PoC)
**Applied**: Standard PyTorch nn.Module pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-3: Permutation [Complexity: 15, Budget: 4 subtasks]

**Applied**: Standard PyTorch tensor indexing pattern

### API Signatures

```python
# code/permutation.py
from torch import Tensor
import torch
from typing import Optional

def apply_canonical_channel_permutation(
    state_dict: dict[str, Tensor],
    perm_seed: int,
) -> dict[str, Tensor]:
    """Apply S_{c_in} x S_{c_out} per layer; propagate BN by pi_out of preceding layer."""
    ...

def apply_transformer_head_permutation(
    state_dict: dict[str, Tensor],
    perm_seed: int,
    n_heads: int,
    head_dim: int,
) -> dict[str, Tensor]:
    """Apply S_h head permutation to MultiheadAttention; propagate LN by channel pi."""
    ...

def _permute_linear(
    weight: Tensor,   # [c_out, c_in]
    bias: Optional[Tensor],  # [c_out]
    pi_out: Tensor,   # [c_out] int64 index permutation
    pi_in: Tensor,    # [c_in] int64 index permutation
) -> tuple[Tensor, Optional[Tensor]]:
    """Returns (permuted_weight [c_out, c_in], permuted_bias [c_out])."""
    ...

def _permute_conv2d(
    weight: Tensor,   # [c_out, c_in, H, W]
    bias: Optional[Tensor],  # [c_out]
    pi_out: Tensor,   # [c_out] int64
    pi_in: Tensor,    # [c_in] int64
) -> tuple[Tensor, Optional[Tensor]]:
    """Returns (permuted_weight [c_out, c_in, H, W], permuted_bias [c_out])."""
    ...

def _permute_batchnorm(
    state_dict: dict[str, Tensor],
    bn_prefix: str,
    pi_out: Tensor,   # [c] int64 — pi_out of preceding layer
) -> dict[str, Tensor]:
    """Permutes running_mean [c], running_var [c], weight [c], bias [c] by pi_out."""
    ...

def _permute_layernorm(
    state_dict: dict[str, Tensor],
    ln_prefix: str,
    pi: Tensor,       # [d] int64 — channel permutation of preceding layer
) -> dict[str, Tensor]:
    """Permutes weight [d] and bias [d] by pi."""
    ...

def _make_perm(size: int, seed: int) -> Tensor:
    """Returns random permutation index tensor of shape [size], dtype=torch.long."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| Conv2d weight | [c_out, c_in, H, W] | after: weight[pi_out][:, pi_in] |
| Linear weight | [c_out, c_in] | after: weight[pi_out][:, pi_in] |
| in_proj_weight | [3*d_model, d_model] | QKV stacked; split by head blocks |
| BN stats | [c] each | running_mean, running_var, weight, bias |
| LN params | [d] each | weight, bias |

### Pseudo-code

**CNN channel permutation:**
```
1. Parse layer order from state_dict keys (detect conv/linear by key suffix)
2. For each layer i (in forward order):
   a. pi_in  = pi_out of layer (i-1)  [c_in of layer i]
   b. pi_out = _make_perm(c_out, seed + i)
   c. permuted_w = weight[pi_out][:, pi_in]    # Conv2d: [c_out,c_in,H,W]
   d. permuted_b = bias[pi_out] if bias exists
   e. If next key is BN: _permute_batchnorm(state_dict, bn_prefix, pi_out)
3. Return new state_dict (copy, no in-place)
```

**Transformer head permutation:**
```
1. pi_heads = _make_perm(n_heads, seed)        # [n_heads]
2. For in_proj_weight [3*d_model, d_model]:
   a. Split into Q [d_model, d_model], K, V blocks
   b. Reshape Q -> [n_heads, head_dim, d_model]
   c. Q_perm = Q[pi_heads]                      # [n_heads, head_dim, d_model]
   d. Repeat for K, V; concatenate -> [3*d_model, d_model]
3. For out_proj weight [d_model, d_model]:
   a. Reshape -> [d_model, n_heads, head_dim]
   b. Permute head dim: [:, pi_heads, :]
   c. Reshape -> [d_model, d_model]
4. For LayerNorm after attention: _permute_layernorm with pi = identity
   (head permutation preserves d_model channel order at LN boundary)
5. If separate Q/K/V projections: apply pi_heads to each independently
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | CNN channel permutation | `_permute_linear`, `_permute_conv2d`, `_make_perm`, `apply_canonical_channel_permutation` |
| L-3-2 | Transformer head permutation | `apply_transformer_head_permutation` with in_proj/separate QKV handling |
| L-3-3 | BN propagation | `_permute_batchnorm`: permute running_mean, running_var, weight, bias by pi_out |
| L-3-4 | LN propagation | `_permute_layernorm`: permute weight, bias by pi |

---

## A-2: Data Loading [Complexity: 12, Budget: 1 subtask]

**Applied**: Standard PyTorch DataLoader pattern

### API Signatures

```python
# code/data_loader.py
import torch
from torch import Tensor
from torch.utils.data import DataLoader
import torch.nn as nn
from typing import Any

class CNNZooLoader:
    def __init__(self, zoo_dir: str, n_checkpoints: int = 500, seed: int = 42):
        """Initializes loader; sets rng for reproducible sampling."""
        ...

    def load_checkpoints(self) -> list[dict[str, Any]]:
        """Sample n_checkpoints uniformly. Returns list of:
           {state_dict: dict[str,Tensor], val_acc: float,
            checkpoint_id: str, task: str}
        """
        ...

    def get_val_loader(self, task: str, batch_size: int = 256) -> DataLoader:
        """Returns validation DataLoader for 'cifar10'|'svhn'|'mnist' task."""
        ...

    def _sample_checkpoint_paths(self) -> list[str]:
        """Glob zoo_dir, shuffle with seed, return first n_checkpoints paths."""
        ...


class TransformerZooLoader:
    def __init__(
        self,
        mnist_dir: str,
        agnews_dir: str,
        n_mnist: int = 250,
        n_agnews: int = 250,
        seed: int = 42,
    ):
        """Initializes loader for both MNIST and AG-News Transformer splits."""
        ...

    def load_checkpoints(self) -> list[dict[str, Any]]:
        """Returns list of:
           {state_dict: dict[str,Tensor], val_acc: float,
            checkpoint_id: str, task: str, arch_config: dict}
        """
        ...

    def get_val_loader(self, task: str, batch_size: int = 256) -> DataLoader:
        """Returns DataLoader for 'mnist'|'agnews' task."""
        ...

    def build_model(self, arch_config: dict[str, Any]) -> nn.Module:
        """Builds minimal Transformer from arch_config dict
           (n_layers, d_model, n_heads, d_ff, num_classes).
        """
        ...

    def _load_split(
        self, split_dir: str, n_samples: int, task: str
    ) -> list[dict[str, Any]]:
        """Load from zip-extracted directory; parse metadata YAML/JSON per checkpoint."""
        ...
```

### Pseudo-code

**Checkpoint sampling (reproducible):**
```
1. paths = sorted(glob(zoo_dir + "/**/*.pt"))
2. rng = np.random.default_rng(seed)
3. indices = rng.choice(len(paths), size=n_checkpoints, replace=False)
4. selected = [paths[i] for i in sorted(indices)]
5. For each path: load {state_dict, val_acc, task} from .pt or sibling .json
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Checkpoint sampling + val loader | `_sample_checkpoint_paths`, `load_checkpoints`, `get_val_loader` for both CNN and Transformer loaders |

---

## A-4: Orbit-PE Check [Complexity: 12, Budget: 1 subtask]

**Applied**: Standard PyTorch tensor pattern

### API Signatures

```python
# code/orbit_pe.py
from torch import Tensor
import torch.nn as nn

SUPPORTED_LAYER_TYPES: list[str] = ["Linear", "Conv2d", "MultiheadAttention"]

def compute_orbit_pe(
    state_dict: dict[str, Tensor],
    layer_type_map: dict[str, str],  # param_name -> "Linear"|"Conv2d"|"MultiheadAttention"
) -> tuple[dict[str, Tensor], dict[str, bool]]:
    """Compute orbit-PE vectors for all weight params.
    orbit_vector encodes (layer_index, orbit_size, position_in_orbit).
    Returns (orbit_vectors, success_flags) per weight name.
    orbit_vector shape: [3] — [layer_idx, orbit_size, pos_in_orbit]
    """
    ...

def get_layer_type_map(model: nn.Module) -> dict[str, str]:
    """Map param name -> layer type string for all supported layers."""
    ...

def compute_orbit_pe_success_rate(success_flags: dict[str, bool]) -> float:
    """Return fraction of layer types (not params) with all-True flags."""
    ...

def _compute_orbit_vector_linear(
    weight: Tensor,   # [c_out, c_in]
    layer_idx: int,
) -> Tensor:
    """Returns orbit-PE vector [3]: [layer_idx, c_out*c_in, position_flat]."""
    ...

def _compute_orbit_vector_conv2d(
    weight: Tensor,   # [c_out, c_in, H, W]
    layer_idx: int,
) -> Tensor:
    """Returns orbit-PE vector [3]: [layer_idx, c_out*c_in, position_flat].
    Treats (c_out, c_in) as orbit axes; H*W positions within orbit.
    """
    ...

def _compute_orbit_vector_mha(
    weight: Tensor,   # [3*d_model, d_model] or [d_model, d_model]
    layer_idx: int,
    n_heads: int,
) -> Tensor:
    """Returns orbit-PE vector [3]: [layer_idx, n_heads*head_dim, position_flat]."""
    ...
```

### Pseudo-code

**Orbit-PE computation (arch-agnostic):**
```
1. layer_idx_counter = 0
2. For param_name in state_dict (sorted by layer order):
   a. layer_type = layer_type_map.get(param_name, None)
   b. If layer_type not in SUPPORTED_LAYER_TYPES: skip
   c. Try:
      - dispatch to _compute_orbit_vector_{layer_type.lower()}(weight, layer_idx)
      - orbit_vectors[param_name] = vector  # shape [3]
      - success_flags[param_name] = True
      - log: f"Orbit-PE computed for {param_name} ({layer_type}): shape {vector.shape}"
   d. Except Exception:
      - success_flags[param_name] = False
      - log failure
   e. layer_idx_counter += 1
3. Return orbit_vectors, success_flags
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Orbit-PE vector computation | `compute_orbit_pe`, `_compute_orbit_vector_linear/conv2d/mha`, `get_layer_type_map`, `compute_orbit_pe_success_rate` |

---

*Logic for H-E1 | EXISTENCE (PoC) | LIGHT Tier | Green-field*
