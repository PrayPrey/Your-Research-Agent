# Architecture: H-M3
# Latent Space Interpolation via EquiSSL-perm Decoder

**Hypothesis ID:** H-M3
**Type:** MECHANISM (SHOULD_WORK)
**Date:** 2026-08-05

Applied: graph-encoder evaluation pipeline (stateless, frozen-model pattern)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (incremental on H-M1 + H-E1)
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-m1/code/`, `docs/youra_research/h-e1/code/`

**Findings**:
- `EquiSSLEncoder` in `h-m1/code/models/equissl_encoder.py` (lines 65-130); `__init__` takes `node_in_dim=4, edge_in_dim=4, hidden_dim=256, latent_dim=128, num_layers=4, symmetry='monomial', pool='mean'`
- `GraphDecoder` in `h-m1/code/models/graph_decoder.py`; `forward(z, structure)` returns `(B, max_edge_dim)` vector — **NOT a full state_dict**; decoder reconstructs only edge_attr statistics, not raw weights
- `checkpoint_to_graph(state_dict)` in `h-m1/code/data/multizoo_graph_dataset.py` — converts state_dict to PyG `Data` with node/edge statistical features (mean, std, norm, max_abs per layer)
- `MultiZooGraphDataset` in same file; `__init__(root_dir, normalize, split, val_fraction, seed)`
- H-M1 `config.py`: `LATENT_DIM=128`, `HIDDEN_DIM=256`, `NUM_LAYERS=4`, checkpoint at `docs/youra_research/h-m1/checkpoints/`
- H-M1 `run_experiment.py` uses `sys.path.insert(0, H_E1_CODE)` pattern — H-E1 code imported via path injection

**Critical Note**: `GraphDecoder.forward()` outputs a fixed-size edge_attr reconstruction vector, NOT decoded weight tensors. H-M3 must reconstruct an MLP state_dict from this output using the `structure` dict + stored layer dimensions. This is a non-trivial mapping step that must be implemented in the interpolation module.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| EquiSSLEncoder | `from models.equissl_encoder import EquiSSLEncoder` | `h-m1/code/models/equissl_encoder.py` |
| GraphDecoder | `from models.graph_decoder import GraphDecoder` | `h-m1/code/models/graph_decoder.py` |
| checkpoint_to_graph | `from data.multizoo_graph_dataset import checkpoint_to_graph` | `h-m1/code/data/multizoo_graph_dataset.py` |
| MultiZooGraphDataset | `from data.multizoo_graph_dataset import MultiZooGraphDataset` | `h-m1/code/data/multizoo_graph_dataset.py` |

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation)

**Path injection pattern** (from `h-m1/run_experiment.py`):
```python
H_M1_CODE = os.path.join(PROJECT_ROOT, 'docs/youra_research/h-m1/code')
H_E1_CODE = os.path.join(PROJECT_ROOT, 'docs/youra_research/h-e1/code')
sys.path.insert(0, H_M1_CODE)
sys.path.insert(0, H_E1_CODE)
```

**Checkpoint paths** (from `h-m1/config.py`):
- Encoder: `docs/youra_research/h-m1/checkpoints/equi_perm_seed0.pt`
- Decoder: `docs/youra_research/h-e1/checkpoints/decoder_seed0.pt`

---

## File Organization

```
docs/youra_research/h-m3/
├── run_hm3.py              # Main runner (orchestrates full experiment)
├── config.py               # Paths, constants, experiment settings
├── data/
│   ├── pair_builder.py     # MLP pair construction from MultiZoo
│   └── mlp_pairs.json      # Generated: 500+ pairs (output artifact)
├── models/
│   └── model_loader.py     # Frozen encoder+decoder loading
├── interpolation/
│   └── interpolator.py     # Encode→midpoint→decode + weight-space avg
├── evaluation/
│   ├── task_eval.py        # MLP task accuracy evaluation
│   └── statistics.py       # Paired t-test, Cohen's d, task breakdown
├── visualization/
│   └── figures.py          # 4 required figures
├── results/
│   └── hm3_results.json    # Generated: per-pair results (output artifact)
└── figures/                # Generated: figure PNGs (output artifacts)
```

---

## Module Definitions

### Config (`config.py`)

**Dependencies**: none

```python
PROJECT_ROOT: str
H_M1_CODE: str    # docs/youra_research/h-m1/code
H_M1_CKPT: str    # docs/youra_research/h-m1/checkpoints
H_E1_CODE: str    # docs/youra_research/h-e1/code
H_E1_CKPT: str    # docs/youra_research/h-e1/checkpoints
MULTIZOO_ROOT: str # data/multizoo or h-e1/code/data/multizoo
DATA_DIR: str      # h-m3/data/
RESULTS_DIR: str   # h-m3/results/
FIGURES_DIR: str   # h-m3/figures/

ENCODER_CKPT: str  # equi_perm_seed0.pt
DECODER_CKPT: str  # decoder_seed0.pt
LATENT_DIM: int = 128
HIDDEN_DIM: int = 256
MAX_EDGE_DIM: int = 512
PAIR_SEED: int = 42
MIN_PAIRS: int = 500
TASKS: list = ['mnist', 'svhn', 'cifar10']

# MLP architecture dims per task (must match zoo training configs)
TASK_MLP_CONFIGS: dict  # {task: {in_dim, hidden_dims, out_dim}}
```

---

### PairBuilder (`data/pair_builder.py`)

**Dependencies**: `checkpoint_to_graph` (h-m1), `MultiZooGraphDataset` (h-m1), `config`

```python
def build_mlp_pairs(
    multizoo_root: str,
    min_pairs: int = 500,
    seed: int = 42,
    tasks: list = None
) -> list[dict]: ...
# Returns list of {pair_id, task, path_a, path_b, acc_a, acc_b}
# Groups by (task, architecture), enumerates unordered pairs, samples to min_pairs
# ponytail: simple itertools.combinations enumeration; upgrade to stratified if task imbalance matters

def save_pairs(pairs: list[dict], out_path: str) -> None: ...

def load_pairs(json_path: str) -> list[dict]: ...
```

---

### ModelLoader (`models/model_loader.py`)

**Dependencies**: `EquiSSLEncoder` (h-m1), `GraphDecoder` (h-m1), `config`

```python
def load_frozen_encoder(
    ckpt_path: str,
    device: str,
    latent_dim: int = 128,
    hidden_dim: int = 256
) -> EquiSSLEncoder: ...
# Loads state_dict, sets .eval(), wraps in torch.no_grad context

def load_frozen_decoder(
    ckpt_path: str,
    device: str,
    latent_dim: int = 128,
    hidden_dim: int = 256,
    max_edge_dim: int = 512
) -> GraphDecoder: ...

def load_mlp_checkpoint(path: str, device: str) -> dict: ...
# torch.load with map_location; returns state_dict
```

---

### Interpolator (`interpolation/interpolator.py`)

**Dependencies**: `EquiSSLEncoder` (h-m1), `GraphDecoder` (h-m1), `checkpoint_to_graph` (h-m1), `ModelLoader`

```python
def encode_checkpoint(
    encoder: EquiSSLEncoder,
    state_dict: dict,
    device: str
) -> torch.Tensor: ...
# checkpoint_to_graph(state_dict) → Data → encoder(graph) → z [latent_dim]

def decode_latent_to_state_dict(
    decoder: GraphDecoder,
    z: torch.Tensor,
    reference_state_dict: dict,
    device: str
) -> dict: ...
# decoder(z, structure) → edge_attr vector → reconstruct state_dict
# Uses reference_state_dict key names + shapes for mapping
# ponytail: linear mapping from max_edge_dim output to flattened weight params;
#           upgrade to per-layer decoder if shape mismatch causes accuracy collapse

def latent_interpolate(
    encoder: EquiSSLEncoder,
    decoder: GraphDecoder,
    state_dict_a: dict,
    state_dict_b: dict,
    device: str,
    alpha: float = 0.5
) -> dict: ...
# encode both → z_mid = (1-alpha)*z_a + alpha*z_b → decode → state_dict

def weight_space_average(
    state_dict_a: dict,
    state_dict_b: dict
) -> dict: ...
# {k: (a[k] + b[k]) / 2.0 for k in a}
```

---

### TaskEvaluator (`evaluation/task_eval.py`)

**Dependencies**: `torchvision`, `config`

```python
class SimpleMLP(nn.Module):
    def __init__(self, in_dim: int, hidden_dims: list[int], out_dim: int): ...
    def forward(self, x: torch.Tensor) -> torch.Tensor: ...

def get_test_loader(task: str, data_root: str, batch_size: int = 256) -> DataLoader: ...
# torchvision MNIST/SVHN/CIFAR10 test split; downloads if not present

def evaluate_state_dict(
    state_dict: dict,
    task: str,
    test_loader: DataLoader,
    device: str,
    task_configs: dict
) -> float: ...
# Load state_dict into SimpleMLP(task_configs[task]); top-1 accuracy; no_grad
```

---

### Statistics (`evaluation/statistics.py`)

**Dependencies**: `scipy.stats`, `numpy`

```python
def compute_statistics(results: list[dict]) -> dict: ...
# results: [{task, acc_latent, acc_ws, delta}, ...]
# Returns: {mean_delta, std_delta, n_pairs, t_stat, p_value, cohen_d,
#           pct_pairs_positive, gate_pass, per_task: {task: {mean_delta, n}}}

def format_report(stats: dict, results: list[dict]) -> str: ...
# Markdown table: mean±std per task + overall; t-stat, p-value, Cohen's d
# Gate result: PASS or DOCUMENT with interpretation
```

---

### Figures (`visualization/figures.py`)

**Dependencies**: `matplotlib`, `seaborn`, `numpy`

```python
def plot_gate_comparison(results: list[dict], stats: dict, out_path: str) -> None: ...
# Fig 1: Bar chart mean acc_latent vs acc_ws, error bars=std, annotated p-value

def plot_task_stratified(stats: dict, out_path: str) -> None: ...
# Fig 2: Bar chart mean delta per MNIST/SVHN/CIFAR-10

def plot_delta_histogram(results: list[dict], stats: dict, out_path: str) -> None: ...
# Fig 3: Histogram of per-pair delta, vline at 0, annotated mean

def plot_pair_scatter(results: list[dict], out_path: str) -> None: ...
# Fig 4: Scatter (acc_a, acc_b) colored by delta sign

def generate_all_figures(results: list[dict], stats: dict, figures_dir: str) -> None: ...
```

---

### Main Runner (`run_hm3.py`)

**Dependencies**: all modules above + `config`

```python
def main() -> None: ...
# 1. Build or load pair list (500+ pairs)
# 2. Load frozen encoder + decoder
# 3. Build task test loaders (MNIST/SVHN/CIFAR-10)
# 4. For each pair: latent_interpolate + weight_space_average + evaluate both
# 5. compute_statistics(results)
# 6. generate_all_figures(results, stats)
# 7. Save results JSON + write 04_validation.md
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config & scaffold | Paths, task MLP configs, directory setup | 5 | 1+1+1+2 |
| A-2 | Pair builder | MultiZoo enumeration, pair sampling, JSON save | 9 | 2+2+2+3 |
| A-3 | Model loader | Load frozen encoder+decoder, eval mode, device | 7 | 2+2+1+2 |
| A-4 | Interpolator | Encode→midpoint→decode + weight-space avg; decoder-to-state_dict mapping | 15 | 4+3+4+4 |
| A-5 | Task evaluator | SimpleMLP + torchvision test loaders + accuracy loop | 9 | 3+2+2+2 |
| A-6 | Statistics | Paired t-test, Cohen's d, task breakdown, gate eval | 8 | 2+1+3+2 |
| A-7 | Visualization | 4 figures (gate bar, task stratified, histogram, scatter) | 8 | 2+1+2+3 |
| A-8 | Main runner | 500+ pair loop, result aggregation, report generation | 11 | 3+3+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4], Medium(9-13): [A-2, A-5, A-8], Low(4-8): [A-1, A-3, A-6, A-7]

**Total tasks**: 8 Epics (within FULL tier budget of ≤30)

---

## Implementation Notes

**Decoder output mapping (A-4 critical path)**: `GraphDecoder.forward()` returns a `(max_edge_dim,)` vector reconstructing edge_attr statistics — it does NOT return a weight tensor directly. To reconstruct an MLP state_dict from decoder output, `decode_latent_to_state_dict` must map the output vector back to per-layer weight shapes using the reference state_dict's key structure. This is the experiment's highest-risk implementation step; if reconstruction accuracy is poor, the latent interpolation baseline will underperform trivially regardless of latent geometry quality. Verify decoder reconstruction fidelity on single checkpoints before running the 500-pair loop.

**Path injection**: Follow `h-m1/run_experiment.py` pattern — `sys.path.insert(0, H_M1_CODE)` before any h-m1 imports.

**Reproducibility**: Save `mlp_pairs.json` before the evaluation loop; all 500+ pairs must be fixed at pair-construction time (seed=42).
