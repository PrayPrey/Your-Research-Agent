# Architecture: H-E1 — Canonical Channel Permutation Invariance & Orbit-PE Computability

**Hypothesis Type**: EXISTENCE (PoC)
**Tier**: LIGHT
**Applied**: minimal evaluation-only pipeline pattern (no training)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No base hypothesis or existing codebase.

---

## File Organization

```
h-e1/
  code/
    config.py          - experiment constants and paths
    data_loader.py     - CNN Zoo + Transformer Zoo checkpoint loaders
    permutation.py     - canonical channel and head permutation logic
    orbit_pe.py        - orbit-PE computability checker
    evaluate.py        - model accuracy evaluation
    visualize.py       - figure generation
    run_experiment.py  - single entry-point
  figures/             - output figures (auto-created)
  results.json         - output metrics
```

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: None

```python
DATA_DIR: str = "data/"
CNN_ZOO_DIR: str = "data/cnn_zoo/"
TRANSFORMER_ZOO_DIR: str = "data/transformer_zoo/"
FIGURES_DIR: str = "h-e1/figures/"
RESULTS_PATH: str = "h-e1/results.json"

N_CNN_CHECKPOINTS: int = 500
N_TRANSFORMER_CHECKPOINTS: int = 500
N_TRANSFORMER_MNIST: int = 250
N_TRANSFORMER_AGNEWS: int = 250
N_PERMUTATIONS: int = 10
PERM_SEEDS: list[int] = list(range(10))
SAMPLE_SEED: int = 42
EVAL_BATCH_SIZE: int = 256
DELTA_ACC_THRESHOLD: float = 0.001
```

---

### DataLoader (`code/data_loader.py`)

**Dependencies**: config, torch, nfn.common

```python
class CNNZooLoader:
    def __init__(self, zoo_dir: str, n_checkpoints: int, seed: int): ...
    def load_checkpoints(self) -> list[dict]:
        """Returns list of {state_dict, val_acc, checkpoint_id, task}"""
        ...
    def get_val_loader(self, task: str, batch_size: int) -> DataLoader: ...

class TransformerZooLoader:
    def __init__(self, mnist_dir: str, agnews_dir: str,
                 n_mnist: int, n_agnews: int, seed: int): ...
    def load_checkpoints(self) -> list[dict]:
        """Returns list of {state_dict, val_acc, checkpoint_id, task, arch_config}"""
        ...
    def get_val_loader(self, task: str, batch_size: int) -> DataLoader: ...
    def build_model(self, arch_config: dict) -> nn.Module: ...
```

---

### Permutation (`code/permutation.py`)

**Dependencies**: torch

```python
def apply_canonical_channel_permutation(
    state_dict: dict[str, Tensor],
    perm_seed: int
) -> dict[str, Tensor]:
    """CNN/Linear: G = S_{c_in} x S_{c_out} per layer.
    Propagates bias by pi_out; propagates BatchNorm by pi_out of preceding layer."""
    ...

def apply_transformer_head_permutation(
    state_dict: dict[str, Tensor],
    perm_seed: int,
    n_heads: int
) -> dict[str, Tensor]:
    """S_h group action on MultiheadAttention in_proj_weight or separate Q/K/V.
    Propagates LayerNorm gamma/beta by preceding channel permutation."""
    ...

def _permute_batchnorm(
    state_dict: dict[str, Tensor],
    bn_prefix: str,
    pi_out: Tensor
) -> dict[str, Tensor]:
    """Permutes running_mean, running_var, weight, bias by pi_out."""
    ...

def _permute_layernorm(
    state_dict: dict[str, Tensor],
    ln_prefix: str,
    pi: Tensor
) -> dict[str, Tensor]: ...
```

---

### OrbitPE (`code/orbit_pe.py`)

**Dependencies**: torch

```python
SUPPORTED_LAYER_TYPES: list[str] = ["Linear", "Conv2d", "MultiheadAttention"]

def compute_orbit_pe(
    state_dict: dict[str, Tensor],
    layer_type_map: dict[str, str]
) -> tuple[dict[str, Tensor], dict[str, bool]]:
    """Returns (orbit_vectors, success_flags) per weight name.
    Encodes (layer_index, orbit_size, position_in_orbit) without arch-specific branches."""
    ...

def get_layer_type_map(model: nn.Module) -> dict[str, str]:
    """Maps weight param names -> layer type string."""
    ...

def compute_orbit_pe_success_rate(success_flags: dict[str, bool]) -> float:
    """Returns fraction of layer types with successful orbit-PE computation."""
    ...
```

---

### Evaluate (`code/evaluate.py`)

**Dependencies**: torch, config

```python
def evaluate_accuracy(
    model: nn.Module,
    val_loader: DataLoader,
    device: torch.device
) -> float:
    """Returns top-1 accuracy in [0,1]. Uses model.eval() + no_grad."""
    ...

def measure_delta_acc(
    model: nn.Module,
    original_state_dict: dict[str, Tensor],
    permuted_state_dict: dict[str, Tensor],
    val_loader: DataLoader,
    device: torch.device
) -> tuple[float, float, float]:
    """Returns (acc_before, acc_after, abs_delta)."""
    ...

def run_cnn_evaluation(
    checkpoints: list[dict],
    perm_seeds: list[int],
    device: torch.device
) -> list[dict]:
    """Returns list of {checkpoint_id, seed, acc_before, acc_after, delta_acc}."""
    ...

def run_transformer_evaluation(
    checkpoints: list[dict],
    perm_seeds: list[int],
    device: torch.device
) -> list[dict]: ...
```

---

### Visualize (`code/visualize.py`)

**Dependencies**: matplotlib, numpy, config

```python
def plot_gate_metrics_comparison(
    mean_delta_cnn: float,
    mean_delta_transformer: float,
    threshold: float,
    save_path: str
) -> None:
    """Bar chart: mean |Δacc| CNN vs Transformer with threshold line."""
    ...

def plot_delta_acc_distribution(
    cnn_deltas: list[float],
    transformer_deltas: list[float],
    save_path: str
) -> None:
    """Histogram of all |Δacc| values (log-scale x-axis)."""
    ...

def plot_orbit_pe_success_table(
    success_flags: dict[str, bool],
    save_path: str
) -> None:
    """Table figure: orbit-PE computability per layer type."""
    ...

def plot_per_seed_stability(
    cnn_results: list[dict],
    transformer_results: list[dict],
    save_path: str
) -> None:
    """Box plot of |Δacc| across 10 permutation seeds."""
    ...
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: config, data_loader, permutation, orbit_pe, evaluate, visualize, json, torch

```python
def main() -> None:
    """Single entry-point. Orchestrates full pipeline:
    1. Load CNN + Transformer checkpoints
    2. Apply permutations (10 per checkpoint)
    3. Measure |Δacc| for each
    4. Run orbit-PE computability check
    5. Aggregate metrics
    6. Generate all 4 figures
    7. Save results.json
    8. Print PASS/FAIL gate verdict
    """
    ...

def compute_summary_metrics(results: list[dict]) -> dict: ...

def evaluate_gate(metrics: dict) -> bool:
    """Returns True if PASS: mean_delta_cnn < 0.001 AND mean_delta_transformer < 0.001
    AND orbit_pe_success_rate == 1.0"""
    ...

def save_results(metrics: dict, gate_pass: bool, path: str) -> None: ...

if __name__ == "__main__":
    main()
```

---

## Data Flow

- `run_experiment.py` → `data_loader.py` → loads checkpoints (state_dicts + val sets)
- `run_experiment.py` → `permutation.py` → produces permuted state_dicts
- `run_experiment.py` → `evaluate.py` → measures acc_before / acc_after per checkpoint × seed
- `run_experiment.py` → `orbit_pe.py` → checks computability per layer type
- `run_experiment.py` → `visualize.py` → saves 4 figures
- `run_experiment.py` → `results.json` (metrics + gate verdict)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Create file structure, config.py, requirements.txt, data download scripts | 5 | 1+1+1+2 |
| A-2 | Data Loading | Implement CNNZooLoader + TransformerZooLoader; sample 500 each with seed=42 | 12 | 3+2+4+3 |
| A-3 | Permutation | Implement CNN channel permutation + Transformer head permutation (S_h); BN/LN propagation | 15 | 4+3+5+3 |
| A-4 | Orbit-PE Check | Implement compute_orbit_pe for Linear/Conv2d/MultiheadAttention without arch-specific branches | 12 | 3+2+4+3 |
| A-5 | Evaluation Loop | measure_delta_acc + run_cnn_evaluation + run_transformer_evaluation (500×10 each) | 11 | 3+2+3+3 |
| A-6 | Visualization & Results | 4 figures + results.json + PASS/FAIL gate verdict | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3], Medium(9-13): [A-2, A-4, A-5], Low(4-8): [A-1, A-6]

**Total tasks**: 6 (within EXISTENCE PoC range of 4-8)
**Total complexity**: 63

---

## External Dependencies

| Library | Usage |
|---------|-------|
| `nfn` (AllanYangZhou/nfn) | `state_dict_to_tensors`, `WeightSpaceFeatures`, orbit primitives |
| `torch`, `torchvision` | Model loading, eval loop, DataLoader |
| `transformers` | Transformer checkpoint loading |
| `datasets` | HuggingFace dataset access for AG-News |
| `matplotlib`, `numpy` | Figures |
| `tqdm` | Progress bars over 5000 evaluations |

---

## Requirements File

```
# h-e1/code/requirements.txt
torch>=2.0.0
torchvision>=0.15.0
numpy>=1.24.0
matplotlib>=3.7.0
pyyaml>=6.0
tqdm>=4.65.0
nfn
transformers>=4.30.0
datasets>=2.12.0
pillow>=9.5.0
```

---

*Architecture for H-E1 | EXISTENCE (PoC) | LIGHT Tier | Green-field*
