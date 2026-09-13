# Logic Design: H-E1
# Equivariant Weight-Space Encoders — API Signatures, Tensor Shapes, Algorithms

---
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
tier: LIGHT
date: 2026-08-21
author: yoon303@etri.re.kr

---

Applied: No relevant KB pattern (Archon KB contains diffusion model content only; weight-space learning queries returned similarity 0.34–0.47 to irrelevant diffusion content)

---

## Codebase Analysis (Serena)

**Green-field project** — no existing codebase to analyze with Serena.

External API signatures verified from official GitHub repositories (documented in 02c_experiment_brief.md):
- `AvivNavon/DWSNets`: `MLPModelForRegression(weight_shapes, hidden_dim)` — takes structured matrices
- `mkofinas/neural-graphs`: `GNNForRegression` — takes PyG `Data` objects with edge/node features
- `AllanYangZhou/nfn`: `layers.NPLinear(network_spec, in_ch, out_ch)` + `layers.HNPPool(network_spec)`
- `ModelZoos/ModelZooDataset`: `.pt` file loads to object with `.weights`, `.metrics['test_accuracy']`

No Serena analysis performed — no local source tree exists yet.

---

## 1. Overview

This document specifies API signatures, tensor shapes, and algorithms for the 7 logic subtasks assigned from 03_architecture.md. Subtasks cover:
- A-3 (4 subtasks): Equivariant encoder wrappers + architecture detection + permutation test
- A-6 (2 subtasks): Orchestration loop + figure generation
- A-5 (1 subtask): Bootstrap R² CI + CI overlap detection

---

## 2. Subtask Specifications

---

### L-3-1: DWSNetEncoder Wrapper API

**Parent epic**: A-3 (Equivariant Encoders, complexity 14)
**File**: `code/encoders.py`

```python
from typing import Literal
import torch
import torch.nn as nn
from torch import Tensor

class DWSNetEncoder(nn.Module):
    """
    Wraps AvivNavon/DWSNets MLPModelForRegression for zoo accuracy prediction.
    Routes to NFN library if CNN layers detected in zoo model weights.
    """

    def __init__(
        self,
        weight_shapes: list[tuple[int, ...]],   # per-layer weight shapes, e.g. [(out, in), ...]
        hidden_dim: int = 64,                    # DWS hidden channels
        num_dws_layers: int = 3,                 # number of DWS equivariant layers
        zoo_arch: Literal["mlp", "cnn"] = "mlp" # detected at dataset load time
    ) -> None:
        super().__init__()
        if zoo_arch == "mlp":
            # Direct DWSNets usage
            from nn.dws.models import MLPModelForRegression
            self.model = MLPModelForRegression(
                weight_shapes=weight_shapes,
                hidden_dim=hidden_dim,
                num_layers=num_dws_layers
            )
            self._path = "dwsnets"
        else:
            # CNN zoo: fall back to NFN library (see L-3-3)
            self.model = _build_nfn_encoder(weight_shapes, hidden_dim)
            self._path = "nfn_fallback"

    def forward(
        self,
        weights: list[Tensor],   # list of (B, n_out, n_in) per layer — structured matrices
        biases: list[Tensor]     # list of (B, n_out) per layer
    ) -> Tensor:                 # (B,) scalar accuracy predictions
        if self._path == "dwsnets":
            return self.model(weights, biases).squeeze(-1)
        else:
            wsfeat = _to_weight_space_features(weights, biases)
            return self.model(wsfeat).squeeze(-1)
```

**Tensor shapes** at each stage:
| Stage | Shape | Notes |
|-------|-------|-------|
| Input weights | `list[(B, n_out, n_in)]` | one tensor per zoo model layer |
| Input biases | `list[(B, n_out)]` | one tensor per zoo model layer |
| After DWS layers | `(B, n_neurons_total, hidden_dim)` | equivariant features per neuron |
| After invariant pool | `(B, hidden_dim)` | sum-pooled over neuron dimension |
| Output | `(B,)` | scalar accuracy prediction |

---

### L-3-2: GNNNFNEncoder Wrapper API

**Parent epic**: A-3 (Equivariant Encoders, complexity 14)
**File**: `code/encoders.py`

```python
from torch_geometric.data import Data, Batch

class GNNNFNEncoder(nn.Module):
    """
    Wraps mkofinas/neural-graphs GNNForRegression.
    Represents zoo model as computational graph: nodes=neurons, edges=weight connections.
    Supports both MLP and CNN zoo architectures natively.
    """

    def __init__(
        self,
        hidden_dim: int = 64,        # GNN hidden channels
        num_layers: int = 4,         # GNN message-passing rounds
        aggr: str = "sum"            # PNA aggregation (sum/mean/max)
    ) -> None:
        super().__init__()
        from nn.gnn import GNNForRegression
        self.model = GNNForRegression(
            hidden_dim=hidden_dim,
            num_layers=num_layers,
            aggr=aggr
        )

    def forward(self, batch: Batch) -> Tensor:
        """
        Args:
            batch: PyG Batch with fields:
                   - x: (N_total_nodes, node_feat_dim)   # node feats = biases
                   - edge_index: (2, E_total)             # connectivity
                   - edge_attr: (E_total, edge_feat_dim) # edge feats = weight values
                   - batch: (N_total_nodes,)              # batch assignment
        Returns:
            (B,) scalar predictions
        """
        return self.model(batch).squeeze(-1)

def state_dict_to_neural_graph(state_dict: dict) -> Data:
    """
    Convert zoo model state_dict to PyG Data object.

    Node features: bias vectors per layer (flattened to per-neuron)
    Edge features: weight matrix entries (each weight = one edge)
    Edge index: connectivity following feedforward topology

    Returns: torch_geometric.data.Data
    """
    node_feats, edge_index, edge_feats = [], [], []
    node_offset = 0

    layers = [(k, v) for k, v in state_dict.items() if 'weight' in k]
    bias_layers = {k.replace('weight', 'bias'): v
                   for k, v in state_dict.items() if 'bias' in k}

    for i, (wkey, W) in enumerate(layers):
        bkey = wkey.replace('weight', 'bias')
        b = bias_layers.get(bkey, torch.zeros(W.shape[0]))

        n_out, n_in = W.shape[0], W.shape[1] if W.dim() >= 2 else 1

        # Nodes = output neurons of this layer
        node_feats.append(b.unsqueeze(-1))  # (n_out, 1)

        if i > 0:
            # Edges: every input neuron → every output neuron
            src = torch.arange(node_offset - n_in, node_offset).repeat_interleave(n_out)
            dst = torch.arange(node_offset, node_offset + n_out).repeat(n_in)
            edge_index.append(torch.stack([src, dst]))
            edge_feats.append(W.flatten().unsqueeze(-1))  # (n_in*n_out, 1)

        node_offset += n_out

    return Data(
        x=torch.cat(node_feats, dim=0),
        edge_index=torch.cat(edge_index, dim=1) if edge_index else torch.zeros(2, 0, dtype=torch.long),
        edge_attr=torch.cat(edge_feats, dim=0) if edge_feats else torch.zeros(0, 1)
    )
```

**Tensor shapes**:
| Stage | Shape | Notes |
|-------|-------|-------|
| node features x | `(N_nodes_total, 1)` | bias value per neuron |
| edge_attr | `(E_total, 1)` | weight value per connection |
| After GNN layers | `(N_nodes_total, hidden_dim)` | node embeddings |
| After global pool | `(B, hidden_dim)` | graph-level embedding |
| Output | `(B,)` | scalar prediction |

---

### L-3-3: NFN Fallback Wrapper (AllanYangZhou/nfn)

**Parent epic**: A-3 (Equivariant Encoders, complexity 14)
**File**: `code/encoders.py`

```python
def _build_nfn_encoder(weight_shapes: list[tuple], hidden_dim: int) -> nn.Module:
    """
    Build NFN-based equivariant encoder for CNN zoo models.
    Uses AllanYangZhou/nfn library: NPLinear + HNPPool.
    """
    from nfn.common import network_spec_from_wsfeat
    from nfn import layers

    # Derive network_spec from weight_shapes (describes conv/linear layer dims)
    # network_spec is constructed from a sample WeightSpaceFeatures object
    # at runtime when first batch is seen (lazy init pattern)
    return _LazyNFNEncoder(weight_shapes, hidden_dim)


class _LazyNFNEncoder(nn.Module):
    """Deferred NFN construction until network_spec is known from first batch."""

    def __init__(self, weight_shapes: list[tuple], hidden_dim: int) -> None:
        super().__init__()
        self.hidden_dim = hidden_dim
        self._built = False

    def _build(self, wsfeat) -> None:
        from nfn.common import network_spec_from_wsfeat
        from nfn import layers
        network_spec = network_spec_from_wsfeat(wsfeat)
        self.net = nn.Sequential(
            layers.NPLinear(network_spec, 1, self.hidden_dim, io_embed=True),
            layers.TupleOp(nn.ReLU()),
            layers.NPLinear(network_spec, self.hidden_dim, self.hidden_dim, io_embed=True),
            layers.TupleOp(nn.ReLU()),
            layers.HNPPool(network_spec),
            nn.Flatten(start_dim=-2),
            nn.Linear(
                self.hidden_dim * layers.HNPPool.get_num_outs(network_spec), 1
            )
        )
        self._built = True

    def forward(self, wsfeat) -> Tensor:
        """
        Args:
            wsfeat: WeightSpaceFeatures namedtuple
                    (constructed via state_dict_to_tensors + default_collate)
        Returns: (B,) scalar
        """
        if not self._built:
            self._build(wsfeat)
        return self.net(wsfeat).squeeze(-1)


def state_dict_to_wsfeat(state_dicts: list[dict]):
    """Batch of state_dicts → WeightSpaceFeatures for NFN."""
    from nfn.common import state_dict_to_tensors
    from torch.utils.data.dataloader import default_collate
    tensors = [state_dict_to_tensors(sd) for sd in state_dicts]
    return default_collate(tensors)  # returns WeightSpaceFeatures namedtuple
```

---

### L-3-4: Architecture Compatibility Detection + Permutation Equivariance Test

**Parent epic**: A-3 (Equivariant Encoders, complexity 14)
**File**: `code/data.py`

```python
from typing import Literal
import torch
from torch import Tensor


def detect_zoo_arch(sample_state_dict: dict) -> Literal["mlp", "cnn"]:
    """
    Detect if zoo model weights are MLP-only or include CNN layers.

    Args:
        sample_state_dict: one zoo model's state_dict (from zoo.weights[0])
    Returns:
        "mlp"  — all Linear layers → use DWSNets directly
        "cnn"  — Conv layers present → use NFN or GNN-NFN
    """
    for key in sample_state_dict:
        if 'conv' in key.lower() or any(
            isinstance(v, Tensor) and v.dim() == 4
            for k, v in sample_state_dict.items() if k == key
        ):
            return "cnn"
    return "mlp"


def verify_permutation_equivariance(
    model: torch.nn.Module,
    sample_weights: list[Tensor],
    sample_biases: list[Tensor],
    tolerance: float = 1e-4
) -> dict:
    """
    Verify that equivariant encoder produces same output under neuron permutation.

    Algorithm:
    1. Run forward pass on original weights → out_orig
    2. Apply random neuron permutation to hidden layers
    3. Run forward pass on permuted weights → out_perm
    4. Check max |out_orig - out_perm| < tolerance

    Args:
        model: DWSNetEncoder or GNNNFNEncoder
        sample_weights: list of (1, n_out, n_in) tensors (single sample, batch=1)
        sample_biases: list of (1, n_out) tensors
        tolerance: max allowed deviation (default 1e-4)

    Returns:
        dict with keys: passed (bool), max_deviation (float), details (str)
    """
    model.eval()
    with torch.no_grad():
        out_orig = model(sample_weights, sample_biases)

        # Permute hidden layer neurons (not input/output layers)
        perm_weights = [w.clone() for w in sample_weights]
        perm_biases = [b.clone() for b in sample_biases]

        for i in range(1, len(perm_weights) - 1):  # hidden layers only
            n = perm_weights[i].shape[1]            # n_in dimension
            perm_idx = torch.randperm(n)
            # Permute columns of W_i (input connections from permuted neurons)
            perm_weights[i] = perm_weights[i][:, :, perm_idx]
            # Permute rows of W_{i-1} (output connections to permuted neurons)
            perm_weights[i - 1] = perm_weights[i - 1][:, perm_idx, :]
            perm_biases[i - 1] = perm_biases[i - 1][:, perm_idx]

        out_perm = model(perm_weights, perm_biases)
        max_dev = torch.max(torch.abs(out_orig - out_perm)).item()

    return {
        "passed": max_dev < tolerance,
        "max_deviation": max_dev,
        "details": f"max|out_orig - out_perm| = {max_dev:.2e} (tolerance {tolerance:.2e})"
    }
```

---

### L-6-1: Orchestration Loop Pseudo-code

**Parent epic**: A-6 (Orchestration + Viz, complexity 12)
**File**: `code/run_experiment.py`

```python
import json
from pathlib import Path
from config import ExperimentConfig
from data import load_zoo, subsample_dataset, detect_zoo_arch
from encoders import FlatMLP, FlatMLPPermAug, DWSNetEncoder, GNNNFNEncoder
from train import train_encoder
from evaluate import compute_r2_with_ci, verify_permutation_equivariance
from visualize import generate_all_figures

def run_experiment(cfg: ExperimentConfig) -> dict:
    """
    Full experiment loop: zoo × encoder × budget_tier × training_size

    Result key format: f"{zoo}_{encoder}_{budget}_{size}"
    e.g. "mnist_flat_mlp_medium_500" → {"r2": 0.74, "ci_low": 0.71, "ci_high": 0.77}
    """
    results = {}
    Path(cfg.figures_dir).mkdir(parents=True, exist_ok=True)
    Path(cfg.results_dir).mkdir(parents=True, exist_ok=True)

    for zoo_name in cfg.zoo_names:                          # ["mnist", "cifar10"]
        train_ds, val_ds, test_ds = load_zoo(zoo_name, cfg)

        # Diversity check (mandatory pre-experiment)
        diversity_ok = check_diversity(test_ds, threshold=0.05)
        results[f"{zoo_name}_diversity_ok"] = diversity_ok

        # Detect zoo architecture once per zoo
        zoo_arch = detect_zoo_arch(train_ds[0]["state_dict"])
        results[f"{zoo_name}_zoo_arch"] = zoo_arch

        for encoder_name in cfg.encoder_names:              # 4 conditions
            for budget_tier, target_params in cfg.budget_tiers.items():  # small/medium/large

                # Build encoder at this budget tier (grid-search hidden_dim)
                model = build_encoder(
                    encoder_name, zoo_arch, target_params, cfg
                )
                actual_params = count_params(model)
                results[f"{zoo_name}_{encoder_name}_{budget_tier}_params"] = actual_params

                # Permutation equivariance test (equivariant encoders only)
                if encoder_name in ["dwsnet", "gnn_nfn"]:
                    sample = train_ds[0]
                    eq_result = verify_permutation_equivariance(
                        model, sample["weights"], sample["biases"]
                    )
                    results[f"{zoo_name}_{encoder_name}_equivariance"] = eq_result

                for size in cfg.training_sizes:             # [100, 250, 500, 1000, "full"]
                    key = f"{zoo_name}_{encoder_name}_{budget_tier}_{size}"

                    # Subsample training set
                    sub_train = subsample_dataset(train_ds, size, seed=cfg.seed)

                    # Train
                    trained_model = train_encoder(model, sub_train, val_ds, cfg)

                    # Evaluate
                    r2, ci_low, ci_high = compute_r2_with_ci(
                        trained_model, test_ds, cfg.n_bootstrap, cfg.ci_level
                    )
                    results[key] = {"r2": r2, "ci_low": ci_low, "ci_high": ci_high}
                    print(f"[{key}] R²={r2:.4f} CI=[{ci_low:.4f}, {ci_high:.4f}]")

    # Write results JSON
    results_path = Path(cfg.results_dir) / "results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    # Generate all 4 figures
    generate_all_figures(results, cfg)

    return results
```

---

### L-6-2: Figure Generation Algorithms

**Parent epic**: A-6 (Orchestration + Viz, complexity 12)
**File**: `code/visualize.py`

```python
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def generate_all_figures(results: dict, cfg) -> None:
    """Generate all 4 required figures."""
    generate_figure1_bar(results, cfg)
    generate_figure2_learning_curves(results, cfg)
    generate_figure3_ci_overlap(results, cfg)
    generate_figure4_diversity(results, cfg)


def generate_figure1_bar(results: dict, cfg) -> None:
    """
    Figure 1 (MANDATORY): R² bar chart at training_size=500, all 4 conditions, per zoo.
    One subplot per zoo (MNIST, CIFAR-10).
    Error bars = bootstrap 95% CI.
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    encoder_labels = ["Flat-MLP", "Flat-MLP+PermAug", "DWSNets/NFN", "GNN-NFN"]
    budget_tier = "medium"  # report matched-budget comparison
    size = 500

    for ax, zoo in zip(axes, cfg.zoo_names):
        r2s, ci_lows, ci_highs = [], [], []
        for enc in cfg.encoder_names:
            key = f"{zoo}_{enc}_{budget_tier}_{size}"
            r = results.get(key, {})
            r2s.append(r.get("r2", 0))
            ci_lows.append(r.get("r2", 0) - r.get("ci_low", 0))
            ci_highs.append(r.get("ci_high", 0) - r.get("r2", 0))

        x = np.arange(len(encoder_labels))
        ax.bar(x, r2s, yerr=[ci_lows, ci_highs], capsize=5,
               color=["#4878CF", "#4878CF", "#D65F5F", "#D65F5F"],
               alpha=[0.6, 0.8, 0.8, 1.0])
        ax.set_xticks(x)
        ax.set_xticklabels(encoder_labels, rotation=20, ha="right")
        ax.set_ylabel("R²")
        ax.set_title(f"{zoo.upper()} Zoo — Training size=500")
        ax.axhline(0, color="black", linewidth=0.5)

    plt.tight_layout()
    plt.savefig(Path(cfg.figures_dir) / "fig1_r2_bar_size500.png", dpi=150)
    plt.close()


def generate_figure2_learning_curves(results: dict, cfg) -> None:
    """
    Figure 2: Learning curves — R² vs training size for all 4 conditions, both zoos.
    2 subplots (one per zoo), 4 lines each.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    colors = {"flat_mlp": "#4878CF", "flat_mlp_perm_aug": "#6ACC65",
              "dwsnet": "#D65F5F", "gnn_nfn": "#B47CC7"}
    labels = {"flat_mlp": "Flat-MLP", "flat_mlp_perm_aug": "Flat-MLP+PermAug",
              "dwsnet": "DWSNets/NFN", "gnn_nfn": "GNN-NFN"}
    budget_tier = "medium"

    for ax, zoo in zip(axes, cfg.zoo_names):
        x_vals = [str(s) for s in cfg.training_sizes]
        for enc in cfg.encoder_names:
            r2s = []
            for size in cfg.training_sizes:
                key = f"{zoo}_{enc}_{budget_tier}_{size}"
                r2s.append(results.get(key, {}).get("r2", float("nan")))
            ax.plot(x_vals, r2s, marker="o", label=labels[enc], color=colors[enc])

        ax.set_xlabel("Training set size")
        ax.set_ylabel("R²")
        ax.set_title(f"{zoo.upper()} Zoo — Learning Curves")
        ax.legend()
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(Path(cfg.figures_dir) / "fig2_learning_curves.png", dpi=150)
    plt.close()


def generate_figure3_ci_overlap(results: dict, cfg) -> None:
    """Figure 3: Bootstrap CI bands for equivariant vs Flat-MLP at each training size."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    budget_tier = "medium"

    for ax, zoo in zip(axes, cfg.zoo_names):
        x = np.arange(len(cfg.training_sizes))
        for enc, color in [("flat_mlp", "#4878CF"), ("dwsnet", "#D65F5F"), ("gnn_nfn", "#B47CC7")]:
            r2s, lows, highs = [], [], []
            for size in cfg.training_sizes:
                key = f"{zoo}_{enc}_{budget_tier}_{size}"
                r = results.get(key, {})
                r2s.append(r.get("r2", float("nan")))
                lows.append(r.get("ci_low", float("nan")))
                highs.append(r.get("ci_high", float("nan")))
            ax.plot(x, r2s, marker="o", color=color, label=enc)
            ax.fill_between(x, lows, highs, color=color, alpha=0.2)

        ax.set_xticks(x)
        ax.set_xticklabels([str(s) for s in cfg.training_sizes])
        ax.set_xlabel("Training size")
        ax.set_ylabel("R² with 95% CI")
        ax.set_title(f"{zoo.upper()} — CI Overlap")
        ax.legend()

    plt.tight_layout()
    plt.savefig(Path(cfg.figures_dir) / "fig3_ci_overlap.png", dpi=150)
    plt.close()


def generate_figure4_diversity(results: dict, cfg) -> None:
    """Figure 4: Zoo diversity histogram — test accuracy distribution per zoo."""
    # Accuracy values stored during load_zoo diversity check
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, zoo in zip(axes, cfg.zoo_names):
        accs = results.get(f"{zoo}_test_accuracies", [])
        if accs:
            ax.hist(accs, bins=30, edgecolor="black", alpha=0.7)
            ax.set_xlabel("Test accuracy")
            ax.set_ylabel("Count")
            ax.set_title(f"{zoo.upper()} Zoo — Accuracy Distribution")
            variance = float(np.var(accs))
            ax.axvline(float(np.mean(accs)), color="red", linestyle="--",
                       label=f"mean={np.mean(accs):.3f}, var={variance:.4f}")
            ax.legend()
        else:
            ax.text(0.5, 0.5, "No data", ha="center", va="center",
                    transform=ax.transAxes)
    plt.tight_layout()
    plt.savefig(Path(cfg.figures_dir) / "fig4_diversity.png", dpi=150)
    plt.close()
```

---

### L-5-1: Bootstrap R² CI + CI Overlap Detection

**Parent epic**: A-5 (Evaluation, complexity 8)
**File**: `code/evaluate.py`

```python
import numpy as np
from sklearn.metrics import r2_score
import torch
from torch import Tensor


def bootstrap_r2_ci(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    n_bootstrap: int = 1000,
    ci: float = 0.95
) -> tuple[float, float]:
    """
    Bootstrap 95% CI on R² from test-set predictions.

    Algorithm:
    1. For each bootstrap iteration:
       a. Sample n indices with replacement from [0, n)
       b. Compute R² on resampled (y_true[idx], y_pred[idx])
       c. Append to r2_samples
    2. Compute percentile CI from r2_samples

    Args:
        y_true: (N,) ground truth test accuracies
        y_pred: (N,) predicted accuracies
        n_bootstrap: number of bootstrap resamples (default 1000)
        ci: confidence level (default 0.95)

    Returns:
        (ci_low, ci_high): lower and upper bounds of CI
    """
    n = len(y_true)
    rng = np.random.default_rng(seed=42)  # reproducible bootstrap
    r2_samples = np.empty(n_bootstrap)

    for i in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)  # sample with replacement
        r2_samples[i] = r2_score(y_true[idx], y_pred[idx])

    alpha = (1 - ci) / 2
    ci_low = float(np.percentile(r2_samples, alpha * 100))
    ci_high = float(np.percentile(r2_samples, (1 - alpha) * 100))
    return ci_low, ci_high


def ci_overlap(ci_a: tuple[float, float], ci_b: tuple[float, float]) -> bool:
    """
    Check if two confidence intervals overlap.

    Args:
        ci_a: (low, high) for first CI
        ci_b: (low, high) for second CI

    Returns:
        True if CIs overlap, False if non-overlapping (gate criterion satisfied when False)
    """
    return ci_a[0] <= ci_b[1] and ci_b[0] <= ci_a[1]


def compute_r2_with_ci(
    model: torch.nn.Module,
    test_dataset,
    n_bootstrap: int = 1000,
    ci_level: float = 0.95
) -> tuple[float, float, float]:
    """
    Evaluate model on test set, compute R² and bootstrap CI.

    Returns: (r2, ci_low, ci_high)
    """
    model.eval()
    all_preds, all_targets = [], []

    with torch.no_grad():
        for batch in test_dataset:
            preds = model(batch["weights"], batch["biases"])
            all_preds.append(preds.cpu().numpy())
            all_targets.append(batch["accuracy"].cpu().numpy())

    y_pred = np.concatenate(all_preds)
    y_true = np.concatenate(all_targets)
    r2 = float(r2_score(y_true, y_pred))
    ci_low, ci_high = bootstrap_r2_ci(y_true, y_pred, n_bootstrap, ci_level)
    return r2, ci_low, ci_high
```

---

## 3. Tensor Shape Reference

| Module | Input | Output | Notes |
|--------|-------|--------|-------|
| DWSNetEncoder | `list[(B,n_out,n_in)]`, `list[(B,n_out)]` | `(B,)` | structured matrices |
| GNNNFNEncoder | PyG `Batch` | `(B,)` | node/edge features |
| NFN fallback | `WeightSpaceFeatures` | `(B,)` | nfn library format |
| FlatMLP | `(B, D_flat)` | `(B,)` | D_flat = total params |
| FlatMLPPermAug | `list[(B,n_out,n_in)]` + `list[(B,n_out)]` | `(B,)` | permutes then flattens |
| bootstrap_r2_ci | `(N,)`, `(N,)` | `(float, float)` | ci_low, ci_high |

---

## 4. Subtask Summary

| ID | Title | Parent Epic | Parent Complexity | File |
|----|-------|-------------|-------------------|------|
| L-3-1 | DWSNetEncoder wrapper API | A-3 | 14 (High) | encoders.py |
| L-3-2 | GNNNFNEncoder wrapper API | A-3 | 14 (High) | encoders.py |
| L-3-3 | NFN fallback wrapper | A-3 | 14 (High) | encoders.py |
| L-3-4 | Architecture detection + permutation test | A-3 | 14 (High) | data.py |
| L-6-1 | Orchestration loop pseudo-code | A-6 | 12 (Medium) | run_experiment.py |
| L-6-2 | Figure generation algorithms | A-6 | 12 (Medium) | visualize.py |
| L-5-1 | Bootstrap R² CI + CI overlap | A-5 | 8 (Low) | evaluate.py |
