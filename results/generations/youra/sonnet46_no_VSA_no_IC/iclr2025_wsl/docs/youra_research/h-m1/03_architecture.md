---
hypothesis_id: h-m1
hypothesis_type: MECHANISM
architect: yoon303@etri.re.kr
generated_at: "2026-08-21"
---

# Architecture: H-M1 — Permutation Equivariance Verification

Applied: inference-only verification pipeline (no training loop)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Serena MCP requires active project selection (tool error); fallback to direct Read  
**Analyzed Path**: `docs/youra_research/h-e1/code/`  
**Findings**: H-E1 codebase uses `ZooDataset` wrapping ModelZooDataset; `state_dict_to_graph()` for GNN collation; `GNNNFNEncoder` (custom GNN, hidden_dim=64, num_layers=4) and `FlatMLP` as primary encoders. NFN encoder dropped due to shape mismatch with CNN zoo. CIFAR-10 zoo loaded from `/home/PrayPrey/.cache/model_zoos/cifar10/dataset_cifar_small_hyp_fix.pt`. H-M1 reuses these data patterns directly; DWSNets added as new encoder.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual H-E1 Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| ZooDataset | `from h_e1_code.data import ZooDataset, load_zoo` | `h-e1/code/data.py` |
| state_dict_to_graph | `from h_e1_code.data import state_dict_to_graph` | `h-e1/code/data.py` |
| GNNNFNEncoder | `from h_e1_code.encoders import GNNNFNEncoder` | `h-e1/code/encoders.py` |
| FlatMLP | `from h_e1_code.encoders import FlatMLP` | `h-e1/code/encoders.py` |

**Zoo path (actual)**: `/home/PrayPrey/.cache/model_zoos/cifar10/dataset_cifar_small_hyp_fix.pt`  
**H-E1 checkpoints**: `docs/youra_research/h-e1/results/` (look for `gnn_nfn_best.pt`, `flat_mlp_best.pt`)  
**Verified from**: `docs/youra_research/h-e1/code/config.py`, `encoders.py`, `data.py`

**Critical notes from H-E1 actual code**:
- `ZooDataset.__getitem__` returns `(state_dict, target)` where `state_dict` is an `OrderedDict`
- `state_dict_to_graph()` handles both conv (4D) and linear (2D) weight tensors
- NFN encoder was dropped in H-E1 (CNN zoo shape mismatch); do NOT use `NFNEncoder`
- CIFAR-10 zoo is a `.pt` file with `{"trainset": ..., "valset": ..., "testset": ...}` splits
- `GNNNFNEncoder` uses `hidden_dim=64` in H-E1 (not 128 as PRD states); load checkpoint accordingly

---

## File Organization

```
docs/youra_research/h-m1/code/
├── config.py          # paths, constants
├── data_loader.py     # load N=200 zoo models
├── encoder_loader.py  # load DWSNets, GNNNFNEncoder, FlatMLP
├── permute.py         # permute_weights()
├── verify.py          # verify_equivariance(), verify_mechanism_activated()
├── visualize.py       # bar chart, CDF, histograms
├── reporter.py        # JSON + markdown results
└── run_experiment.py  # main entry point

docs/youra_research/h-m1/
├── figures/
│   ├── gate_metrics_bar.png
│   ├── cdf_comparison.png
│   └── diff_histograms.png
└── results/
    └── equivariance_results.json
```

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: none

```python
import os
import sys

# Reuse H-E1 zoo path (from h-e1/code/config.py)
ZOO_PT_PATH = "/home/PrayPrey/.cache/model_zoos/cifar10/dataset_cifar_small_hyp_fix.pt"
MZDATASET_CODE_PATH = "/home/PrayPrey/YOURA_camera_ready/YouRA/results/generations/youra/opus45_no_IC/iclr2025_wsl/docs/youra_research/h-m4/data/ModelZooDataset/code"

# H-E1 checkpoint dir — adjust if needed
H_E1_RESULTS_DIR = os.path.join(os.path.dirname(__file__), "../../h-e1/results")
GNN_CKPT = os.path.join(H_E1_RESULTS_DIR, "gnn_nfn_best.pt")
FLAT_CKPT = os.path.join(H_E1_RESULTS_DIR, "flat_mlp_best.pt")

# H-M1 output dirs
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_H_M1_DIR = os.path.dirname(_THIS_DIR)
FIGURES_DIR = os.path.join(_H_M1_DIR, "figures")
RESULTS_DIR = os.path.join(_H_M1_DIR, "results")

# Verification constants
SEED = 42
N_MODELS = 200        # zoo models to sample
N_PERMS = 50          # permutations per model
TOL_EQUIV = 1e-5      # equivariance threshold (DWSNets, GNN-NFN)
TOL_NON_EQUIV = 1e-3  # non-equivariance threshold (Flat-MLP)

# GNN-NFN config matching H-E1 actual code
GNN_HIDDEN_DIM = 64
GNN_NUM_LAYERS = 4
FLAT_INPUT_DIM = None   # inferred at runtime from zoo model flat size
```

---

### DataLoader (`code/data_loader.py`)

**Dependencies**: Config, H-E1 data.py patterns, ModelZooDataset

```python
import sys
import torch
import numpy as np
from pathlib import Path
from torch.utils.data import Dataset
import config

sys.path.insert(0, config.MZDATASET_CODE_PATH)

def load_zoo_models(n: int = config.N_MODELS, seed: int = config.SEED) -> list[dict]:
    """Load N random state_dicts from CIFAR-10 zoo. Returns list of OrderedDicts."""
    ...

def get_weight_dim(state_dicts: list[dict]) -> int:
    """Compute flat weight dimension (for FlatMLP input_dim)."""
    ...

def detect_hidden_layers(state_dict: dict) -> list[str]:
    """Return sorted list of hidden-layer weight keys (exclude first + last)."""
    ...
```

---

### EncoderLoader (`code/encoder_loader.py`)

**Dependencies**: Config, H-E1 encoders.py (GNNNFNEncoder, FlatMLP), DWSNets (external)

```python
import torch
import torch.nn as nn
import config

def load_gnn_nfn(ckpt_path: str = config.GNN_CKPT,
                 hidden_dim: int = config.GNN_HIDDEN_DIM,
                 num_layers: int = config.GNN_NUM_LAYERS) -> nn.Module:
    """Load GNNNFNEncoder from H-E1 checkpoint. Falls back to random init."""
    ...

def load_flat_mlp(input_dim: int, ckpt_path: str = config.FLAT_CKPT) -> nn.Module:
    """Load FlatMLP from H-E1 checkpoint. Falls back to random init."""
    ...

def load_dwsnet(network_spec) -> nn.Module:
    """Load DWSNets from official repo (AvivNavon/DWSNets). Random init (structural property)."""
    ...

def build_dwsnet_spec(sample_state_dict: dict):
    """Build DWSNets network_spec from a zoo model state_dict. Handles conv→FC flatten."""
    ...

def get_all_encoders(weight_dim: int, sample_state_dict: dict) -> dict[str, nn.Module]:
    """Returns {'dwsnet': ..., 'gnn_nfn': ..., 'flat_mlp': ...} all in eval() mode."""
    ...
```

---

### PermuteFn (`code/permute.py`)

**Dependencies**: torch

```python
import torch
from torch import Tensor

def permute_weights(weight_dict: dict, layer_key: str, perm: Tensor) -> dict:
    """Apply neuron permutation to a single hidden layer.

    Permutes rows of weight_dict[layer_key] and cols of next weight matrix.
    Permutes bias of layer_key. Handles both conv (4D) and linear (2D) weights.
    Does NOT permute input or output layer.
    """
    ...

def permute_all_hidden_layers(weight_dict: dict, hidden_keys: list[str],
                               perm: Tensor) -> dict:
    """Apply same permutation perm to all hidden layers sequentially."""
    ...

def get_perm(size: int, device: torch.device = torch.device("cpu")) -> Tensor:
    """torch.randperm(size, device=device)"""
    ...
```

---

### Verify (`code/verify.py`)

**Dependencies**: PermuteFn, data.py (state_dict_to_graph for GNN collation)

```python
import torch
import numpy as np
from torch import Tensor
import config

def verify_equivariance(
    encoder_name: str,
    encoder,
    weight_samples: list[dict],
    hidden_keys: list[list[str]],
    num_perms: int = config.N_PERMS,
    tol: float = config.TOL_EQUIV,
) -> dict:
    """Run 200×50 permutation checks. Returns stats dict.

    Handles three encoder types differently:
    - 'flat_mlp': flatten state_dict → (1, D) tensor
    - 'gnn_nfn': state_dict_to_graph → PyG Batch
    - 'dwsnet': state_dict → DWSNets-format input

    Returns:
        {max_diff, mean_diff, median_diff, p95_diff, all_diffs: list[float], pass: bool}
    """
    ...

def verify_mechanism_activated(results: dict[str, dict]) -> tuple[bool, dict]:
    """Check all gate conditions. results keys: 'dwsnet', 'gnn_nfn', 'flat_mlp'."""
    indicators = {
        "dwsnet_equivariant": results["dwsnet"]["max_diff"] < 1e-5,
        "gnn_equivariant": results["gnn_nfn"]["max_diff"] < 1e-5,
        "flat_not_equivariant": results["flat_mlp"]["max_diff"] > 1e-3,
        "gap_exists": results["flat_mlp"]["max_diff"] / (results["dwsnet"]["max_diff"] + 1e-10) > 100,
    }
    ...
```

---

### Visualize (`code/visualize.py`)

**Dependencies**: Config, matplotlib, numpy

```python
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import config

def plot_gate_metrics_bar(results: dict[str, dict], save_path: Path) -> None:
    """Bar chart: max_abs_diff per encoder + 1e-5 threshold line (log y-scale)."""
    ...

def plot_cdf(results: dict[str, dict], save_path: Path) -> None:
    """CDF of per-permutation max abs diffs (log x-axis), one line per encoder."""
    ...

def plot_diff_histograms(results: dict[str, dict], save_path: Path) -> None:
    """3-panel histogram: one panel per encoder, 10000 max abs diffs."""
    ...

def save_all_figures(results: dict[str, dict]) -> None:
    """Generate and save all three figures to FIGURES_DIR."""
    ...
```

---

### Reporter (`code/reporter.py`)

**Dependencies**: Config, json

```python
import json
from pathlib import Path
import config

def print_summary_table(results: dict[str, dict], activated: bool, indicators: dict) -> None:
    """Print tabular summary: encoder | max_diff | mean_diff | median_diff | p95 | PASS/FAIL"""
    ...

def save_json(results: dict[str, dict], activated: bool, indicators: dict,
              path: Path = None) -> Path:
    """Save equivariance_results.json to RESULTS_DIR."""
    ...
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: All modules above

```python
import torch
import config
from data_loader import load_zoo_models, get_weight_dim, detect_hidden_layers
from encoder_loader import get_all_encoders
from verify import verify_equivariance, verify_mechanism_activated
from visualize import save_all_figures
from reporter import print_summary_table, save_json
from pathlib import Path

def main() -> None:
    torch.manual_seed(config.SEED)

    # 1. Load data
    weight_samples: list[dict] = load_zoo_models(n=config.N_MODELS)
    weight_dim: int = get_weight_dim(weight_samples)
    hidden_keys_per_model: list[list[str]] = [detect_hidden_layers(w) for w in weight_samples]

    # 2. Load encoders
    encoders: dict[str, nn.Module] = get_all_encoders(weight_dim, weight_samples[0])

    # 3. Verify (no_grad, eval mode)
    results: dict[str, dict] = {}
    with torch.no_grad():
        for name, enc in encoders.items():
            results[name] = verify_equivariance(name, enc, weight_samples,
                                                hidden_keys_per_model)

    # 4. Gate check
    activated, indicators = verify_mechanism_activated(results)

    # 5. Report + visualize
    print_summary_table(results, activated, indicators)
    save_json(results, activated, indicators)
    save_all_figures(results)

    assert results["dwsnet"]["max_diff"] < 1e-5
    assert results["gnn_nfn"]["max_diff"] < 1e-5
    assert results["flat_mlp"]["max_diff"] > 1e-3

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment Setup | Install DWSNets (`git clone AvivNavon/DWSNets && pip install -e .`); verify import; confirm H-E1 imports (GNNNFNEncoder, FlatMLP, state_dict_to_graph) work | 7 | 2+1+1+3 |
| A-2 | Config Module | Write `config.py` with all paths, thresholds, constants; verify zoo .pt file exists at known path | 4 | 1+1+1+1 |
| A-3 | Data Loader | Implement `load_zoo_models()` loading from zoo .pt splits; subsample N=200 with seed=42; `detect_hidden_layers()` for permute targets | 9 | 2+2+3+2 |
| A-4 | Encoder Loader | Implement `load_gnn_nfn()`, `load_flat_mlp()` with checkpoint fallback to random init; `build_dwsnet_spec()` from state_dict; `load_dwsnet()` with DWSNets API | 14 | 3+3+4+4 |
| A-5 | Permute Function | Implement `permute_weights()` correctly handling rows/cols for both 2D (linear) and 4D (conv) weights; bias reorder; validate with manual test | 12 | 2+1+5+4 |
| A-6 | Verify Loop | Implement `verify_equivariance()` dispatching by encoder type (flat/gnn/dwsnet input formats); run 200×50=10,000 checks; collect all_diffs; compute stats | 15 | 3+4+4+4 |
| A-7 | Mechanism Gate | Implement `verify_mechanism_activated()` with all 4 indicator checks; assert pass conditions | 5 | 1+1+2+1 |
| A-8 | Visualization | Implement 3 figures: bar chart (log y), CDF (log x), 3-panel histogram; save to figures/ | 9 | 2+1+4+2 |
| A-9 | Reporter | `print_summary_table()` + `save_json()` with full stats per encoder | 5 | 1+1+2+1 |
| A-10 | Main Runner | Wire all modules in `run_experiment.py`; end-to-end test; fix encoder input format bugs | 10 | 2+3+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4, A-6], Medium(9-13): [A-3, A-5, A-8, A-10], Low(4-8): [A-1, A-2, A-7, A-9]

---

## Implementation Notes for Phase 4

**Encoder input format dispatch** (critical — all three encoders take different inputs):
- `flat_mlp`: needs `_flatten_state_dict(sd)` → `(1, D)` tensor (import from h-e1 data.py)
- `gnn_nfn`: needs `state_dict_to_graph(sd)` → `Batch.from_data_list([graph])` (import from h-e1 data.py)
- `dwsnet`: needs DWSNets-specific format; check `AvivNavon/DWSNets` README for exact input spec

**DWSNets network_spec**: CIFAR-10 zoo uses CNN architecture (4D conv weights). DWSNets originally designed for MLP weight spaces. If DWSNets does not support CNN spec, restrict to FC layers only or use random MLP spec as a standalone test (equivariance is structural — valid with any valid spec).

**H-E1 checkpoint discovery**: H-E1 results dir may store checkpoints under different names. Implement checkpoint fallback: try known paths, else random init (valid for mechanism check).

**permute_weights for conv layers**: Conv weight shape is `(out, in, kH, kW)`. Permuting output neurons of layer i: permute dim=0. Permuting input neurons of layer i+1 (conv): permute dim=1. This preserves the represented function.
