# Logic: H-M1 — Flat MLP Encoder Permutation Sensitivity Probing

**Applied**: stratified-analysis-pipeline pattern (load → train → probe → gate)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from base code
**Analyzed Path**: `docs/youra_research/20260505_wsl/h-e1/code/`
**Relevant Symbols**:
- `flatten_weights(state_dict: Dict[str, Tensor]) -> Tensor` — handles `_flat_weights` pre-vectorized format
- `stratified_pair_sample(checkpoints, n_per_decile, acc_threshold, seed) -> List[Tuple[Dict, Dict, int]]`
- `load_zoo_checkpoints(cfg: ExperimentConfig) -> List[Dict[str, Any]]` — 3-path fallback chain
- h-e1 `ExperimentConfig` has `data_dir`, `zoo_name`, `seed`, `n_per_decile`, `acc_threshold`

Note: MCP unavailable in TEST environment — verified from direct file reads.

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual h-e1 Code)

```python
# From: h-e1/code/weight_analysis.py (ACTUAL CODE)
def flatten_weights(state_dict: Dict[str, torch.Tensor]) -> torch.Tensor:
    """Handles _flat_weights and standard weight/bias dicts. Returns [N_params] float32 cpu."""
    ...

def stratified_pair_sample(
    checkpoints: List[Dict[str, Any]],
    n_per_decile: int = 50,
    acc_threshold: float = 0.01,
    seed: int = 42,
) -> List[Tuple[Dict, Dict, int]]:
    """Returns List of (checkpoint_i, checkpoint_j, decile_index)."""
    ...

# From: h-e1/code/data_loader.py (ACTUAL CODE)
def load_zoo_checkpoints(cfg: ExperimentConfig) -> List[Dict[str, Any]]:
    """3-path fallback: pip package -> dataset .pt -> file glob.
    Each item: {'state_dict': OrderedDict, 'test_accuracy': float}"""
    ...

# From: h-e1/code/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    data_dir: Path = Path("./data/model_zoo")
    zoo_name: str = "mnist_cnn"
    seed: int = 42
    n_per_decile: int = 50
    acc_threshold: float = 0.01
    ...
```

**Import pattern for h-m1**:
```python
import sys
from pathlib import Path
HE1_CODE = Path(__file__).parent.parent.parent / "h-e1" / "code"
sys.path.insert(0, str(HE1_CODE))
from weight_analysis import flatten_weights, stratified_pair_sample
from data_loader import load_zoo_checkpoints
from config import ExperimentConfig as HE1Config
```

**Verified from**: `h-e1/code/weight_analysis.py`, `h-e1/code/data_loader.py`, `h-e1/code/config.py`

---

## A-5: Permutation Generation [Complexity: 14, Budget: 3 subtasks]

**Applied**: functional-equivalence permutation pattern (row/col shuffle)

### API Signatures

```python
# h-m1/code/probe.py
from typing import Dict, List, Optional, Tuple
import torch

LayerOrder = List[Tuple[str, str, int]]
# Each tuple: (outgoing_weight_key, incoming_weight_key, n_neurons)
# For conv layers: outgoing perm applies to dim-0; incoming perm to dim-1
# For fc layers: same convention

def get_mnist_cnn_layer_order() -> LayerOrder:
    """Return permutation spec for Conv(32)-Conv(64)-FC(128)-FC(10) MNIST-CNN.
    Returns list of (out_key, in_key, n_neurons) for each permutable layer boundary."""
    ...

def _permute_conv_out(weight: torch.Tensor, perm: torch.Tensor) -> torch.Tensor:
    """Permute conv output channels. weight: [C_out, C_in, kH, kW] -> [C_out, C_in, kH, kW]"""
    ...

def _permute_conv_in(weight: torch.Tensor, perm: torch.Tensor) -> torch.Tensor:
    """Permute conv input channels. weight: [C_out, C_in, kH, kW] -> [C_out, C_in, kH, kW]"""
    ...

def _permute_fc_out(weight: torch.Tensor, perm: torch.Tensor) -> torch.Tensor:
    """Permute FC output rows. weight: [N_out, N_in] -> [N_out, N_in]"""
    ...

def _permute_fc_in(weight: torch.Tensor, perm: torch.Tensor) -> torch.Tensor:
    """Permute FC input cols. weight: [N_out, N_in] -> [N_out, N_in]"""
    ...

def generate_permuted_weights(
    state_dict: Dict[str, torch.Tensor],
    layer_order: LayerOrder,
    seed: Optional[int] = None,
) -> Dict[str, torch.Tensor]:
    """Apply random neuron permutation; preserves functional equivalence.
    Returns new state_dict with permuted tensors (same keys, same shapes)."""
    ...
```

### Pseudo-code

```
get_mnist_cnn_layer_order():
    return [
        ('conv1.weight', 'conv2.weight', 32),   # permute conv1 output / conv2 input channels
        ('conv2.weight', 'fc1.weight',  64),    # permute conv2 output / fc1 input channels (flattened)
        ('fc1.weight',   'fc2.weight',  128),   # permute fc1 output / fc2 input neurons
    ]
    # Note: biases follow the outgoing layer permutation

generate_permuted_weights(state_dict, layer_order, seed):
    rng = torch.Generator(); rng.manual_seed(seed) if seed else None
    new_sd = {k: v.clone() for k, v in state_dict.items()}
    for (out_key, in_key, n) in layer_order:
        perm = torch.randperm(n, generator=rng)
        # Permute outgoing weight dim-0 and corresponding bias
        new_sd[out_key] = permute_dim0(new_sd[out_key], perm)
        bias_key = out_key.replace('weight', 'bias')
        if bias_key in new_sd:
            new_sd[bias_key] = new_sd[bias_key][perm]
        # Permute incoming weight dim-1 (or spatial-flattened dim-1 for conv->fc boundary)
        w_in = new_sd[in_key]
        if w_in.dim() == 2:  # FC layer
            # For conv->fc boundary, in_key input dim is n * spatial_size
            spatial = w_in.shape[1] // n
            w_in = w_in.view(w_in.shape[0], n, spatial)
            w_in = w_in[:, perm, :]
            new_sd[in_key] = w_in.view(w_in.shape[0], -1)
        else:  # Conv layer
            new_sd[in_key] = w_in[:, perm, :, :]
    return new_sd
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | get_layer_order | Implement get_mnist_cnn_layer_order with correct key names and neuron counts |
| L-5-2 | permute_helpers | Implement _permute_conv_out/in, _permute_fc_out/in helper functions |
| L-5-3 | generate_permuted | Implement generate_permuted_weights with conv->fc spatial reshape handling |

---

## A-6: Sensitivity Probing [Complexity: 15, Budget: 4 subtasks]

**Applied**: embedding-distance-ratio sensitivity pattern

### API Signatures

```python
# h-m1/code/probe.py (continued)
import torch
import numpy as np
from typing import Dict, List

def _embed_state_dict(
    encoder: "FlatMLPEncoder",
    state_dict: Dict[str, torch.Tensor],
    mean: torch.Tensor,
    std: torch.Tensor,
    device: torch.device,
) -> torch.Tensor:
    """Flatten, normalize, encode one state_dict. Returns [embed_dim] on CPU."""
    ...

def compute_permutation_sensitivity(
    encoder: "FlatMLPEncoder",
    checkpoints: List[Dict],
    mean: torch.Tensor,
    std: torch.Tensor,
    cfg: "ExperimentConfig",
    device: torch.device,
) -> Dict[str, float]:
    """Compute sensitivity_score = mean_equiv_L2 / mean_random_L2.
    Returns dict with sensitivity_score, mean_equiv_L2, mean_random_L2, n_pairs,
    equiv_dists (List[float]), random_dists (List[float])."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| flat_w | [N_params] | ~500K float32, output of flatten_weights |
| norm_w | [N_params] | z-score normalized: (flat_w - mean) / (std + eps) |
| embedding | [embed_dim] | 128-dim encoder output, CPU |
| equiv_dists | [n_pairs] | L2 distances for permutation-equivalent pairs |
| random_dists | [n_pairs] | L2 distances for random pairs |

### Pseudo-code

```
compute_permutation_sensitivity(encoder, checkpoints, mean, std, cfg, device):
    encoder.eval()
    layer_order = get_mnist_cnn_layer_order()

    # Get equiv pairs via h-e1 stratified_pair_sample
    pairs = stratified_pair_sample(
        checkpoints,
        n_per_decile=cfg.n_pairs // 10,
        acc_threshold=cfg.acc_threshold,
        seed=cfg.seed,
    )
    if len(pairs) < cfg.min_pairs:
        raise RuntimeError(f"Only {len(pairs)} pairs found, need {cfg.min_pairs}")

    equiv_dists = []
    random_dists = []
    with torch.no_grad():
        for (ckpt_i, ckpt_j, decile) in tqdm(pairs):
            # Equiv pair: original vs permuted version of same model
            e_orig = _embed_state_dict(encoder, ckpt_i['state_dict'], mean, std, device)
            perm_sd = generate_permuted_weights(ckpt_i['state_dict'], layer_order, seed=cfg.seed)
            e_perm = _embed_state_dict(encoder, perm_sd, mean, std, device)
            equiv_dists.append(torch.norm(e_orig - e_perm).item())

            # Random pair: two different models
            e_j = _embed_state_dict(encoder, ckpt_j['state_dict'], mean, std, device)
            random_dists.append(torch.norm(e_orig - e_j).item())

    mean_equiv = float(np.mean(equiv_dists))
    mean_random = float(np.mean(random_dists))
    sensitivity_score = mean_equiv / (mean_random + 1e-8)

    return {
        'sensitivity_score': sensitivity_score,
        'mean_equiv_L2': mean_equiv,
        'mean_random_L2': mean_random,
        'n_pairs': len(pairs),
        'equiv_dists': equiv_dists,
        'random_dists': random_dists,
    }
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | embed_helper | Implement _embed_state_dict: flatten -> normalize -> encoder forward |
| L-6-2 | equiv_distances | Compute equiv L2 loop: original vs generate_permuted_weights |
| L-6-3 | random_distances | Compute random L2 loop: pairs from stratified_pair_sample |
| L-6-4 | sensitivity_ratio | Aggregate mean_equiv / mean_random, return full result dict |

---

## A-4: Training Loop [Complexity: 12, Budget: 2 subtasks]

**Applied**: Standard PyTorch Adam + CosineAnnealingLR pattern

### API Signatures

```python
# h-m1/code/train.py
from dataclasses import dataclass, field
from typing import Tuple
import torch
from torch.utils.data import DataLoader

@dataclass
class TrainHistory:
    train_loss: list = field(default_factory=list)
    val_loss: list = field(default_factory=list)
    train_spearman: list = field(default_factory=list)
    val_spearman: list = field(default_factory=list)

def set_seed(seed: int) -> None:
    """Set random seeds for torch, numpy, python random."""
    ...

def train_encoder(
    model: "FlatMLPWithHead",
    train_loader: DataLoader,
    val_loader: DataLoader,
    cfg: "ExperimentConfig",
    device: torch.device,
) -> Tuple["FlatMLPWithHead", TrainHistory]:
    """Train with Adam+CosineAnnealingLR, MSE loss, per-epoch Spearman logging.
    model: FlatMLPWithHead  x: [B, N_params] -> pred: [B, 1]
    Logs prefix [H-M1] each epoch. Returns best-val-loss model + history."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | optimizer_setup | Adam(lr, weight_decay, betas) + CosineAnnealingLR(T_max, eta_min) |
| L-4-2 | train_loop | Epoch loop: forward, MSE loss, backward, Spearman eval, history append, best-model save |

---

## A-9: Integration & End-to-End Run [Complexity: 12, Budget: 2 subtasks]

**Applied**: Standard PyTorch pipeline orchestration pattern

### API Signatures

```python
# h-m1/code/run_experiment.py
import argparse
from pathlib import Path
import torch

def parse_args() -> argparse.Namespace:
    """Parse --data-dir, --results-dir, --device, --epochs CLI args."""
    ...

def setup_device(device_str: str = "auto") -> torch.device:
    """Return cuda if available else cpu; log selection."""
    ...

def main() -> None:
    """Full pipeline:
    1. parse_args + set_seed(42)
    2. load_and_split_dataset -> train/val/test + mean/std + all_checkpoints
    3. grid_search_architecture -> encoder + hidden_dims + param_count
    4. FlatMLPWithHead(encoder) -> train_encoder -> model + history
    5. compute_spearman on test loader
    6. compute_permutation_sensitivity -> sensitivity dict
    7. run_gate_check -> gate dict; log [H-M1] PASS/FAIL
    8. save_results(gate_dict + sensitivity_dict + spearman)
    9. generate all 5 figures
    """
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | sys_path_wiring | h-e1 sys.path insert, CUDA_VISIBLE_DEVICES setup, argparse |
| L-9-2 | pipeline_orchestration | main() sequencing all modules, error handling, results/figures save |

---

## A-8: Visualization [Complexity: 11, Budget: 1 subtask]

**Applied**: Standard matplotlib figure pattern

### API Signatures

```python
# h-m1/code/visualize.py
from typing import Dict, List
import numpy as np

def plot_training_curve(history: "TrainHistory", cfg: "ExperimentConfig") -> None:
    """Line chart: train/val loss + Spearman ρ over epochs. Saves to figures_dir."""
    ...

def plot_l2_distribution(equiv_dists: List[float], random_dists: List[float], cfg: "ExperimentConfig") -> None:
    """Histogram: equiv-pair L2 vs random-pair L2. Saves to figures_dir."""
    ...

def plot_gate_metrics(sensitivity_score: float, spearman_rho: float, cfg: "ExperimentConfig") -> None:
    """Bar chart: sensitivity_score vs 0.3 gate, Spearman ρ vs 0.5. Saves to figures_dir."""
    ...

def plot_sensitivity_by_decile(decile_scores: List[float], cfg: "ExperimentConfig") -> None:
    """Bar chart: mean equiv L2 per accuracy decile (10 bars). Saves to figures_dir."""
    ...

def plot_embedding_scatter(
    embeddings: np.ndarray,       # [N, embed_dim]
    accuracies: np.ndarray,       # [N]
    equiv_pair_indices: List[Tuple[int, int]],
    cfg: "ExperimentConfig",
    method: str = "pca",
) -> None:
    """2D PCA scatter colored by accuracy; lines connecting equiv pairs. Saves to figures_dir."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | all_5_figures | Implement all 5 plot functions with matplotlib; save to cfg.figures_dir |

---

## Summary

| Task | Module | Subtasks |
|------|--------|----------|
| A-5 Permutation Generation | probe.py (partial) | L-5-1, L-5-2, L-5-3 |
| A-6 Sensitivity Probing | probe.py (continued) | L-6-1, L-6-2, L-6-3, L-6-4 |
| A-4 Training Loop | train.py | L-4-1, L-4-2 |
| A-9 Integration | run_experiment.py | L-9-1, L-9-2 |
| A-8 Visualization | visualize.py | L-8-1 |

**Total subtasks**: 12/12
