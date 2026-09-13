# Architecture: H-M1 (MECHANISM)

**Hypothesis:** NFN equivariant layers produce permutation-invariant outputs (correlation > 0.99)
**Type:** MECHANISM — property test of trained H-E1 NFN, no new training.

Applied: PyTorch eval-mode inference pattern (no KB entries for NFN-specific permutation testing; used official AllanYangZhou/nfn `check_nfn_inv.py` pattern per experiment brief)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: Actual H-E1 code analyzed — architecture differs from PRD assumption.
**Analyzed Path**: `docs/youra_research/h-e1/code/{model.py, data.py, config.py, zoo_generator.py}`
**Findings**:
- H-E1's `NFNRegressor` (`model.py`) takes `network_spec` + `nfn_channels=32`, built from `nfn.layers.NPLinear` x2 + `HNPPool` + `Linear`. Loaded via `state_dict` from `h-e1/checkpoints/`.
- Real model zoo uses `SimpleCNN` (`zoo_generator.py`): `nn.Sequential(Linear(3072,64), ReLU, Linear(64,64), ReLU, Linear(64,10))` → state_dict keys `net.0/2/4.{weight,bias}`. Input dim is **3072** (CIFAR-10 flattened), NOT 784 as PRD/brief assumed (MNIST-style). Hidden sizes **[64, 64]** match brief.
- `data.py::get_network_spec_from_sample` builds `network_spec` via `state_dict_to_tensors` + `network_spec_from_wsfeat`; H-M1 must reuse this exact path for compatibility with the loaded checkpoint's NFN layer shapes.
- `data.py::make_collate_fn` shows canonical wsfeat construction: `WeightSpaceFeatures(*default_collate([state_dict_to_tensors(sd)]))`.

**Correction applied**: Test MLP generator uses `input_dim=3072` (not 784) to match H-E1's actual trained architecture and checkpoint.

---

## File Structure

```
h-m1/code/
  permute.py           # permutation generation + application on SimpleCNN state_dict
  test_data.py          # synthetic test MLP generator (matches H-E1 SimpleCNN shape)
  metrics.py             # invariance metrics (mean/std/max_dev/score)
  test_invariance.py     # main script: load NFN, run test, save results/figures
h-m1/figures/
h-m1/results.json
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| NFNRegressor | `from model import NFNRegressor` (add h-e1/code to sys.path) | `h-e1/code/model.py` |
| get_network_spec_from_sample | `from data import get_network_spec_from_sample` | `h-e1/code/data.py` |
| make_collate_fn / state_dict_to_tensors path | `from data import make_collate_fn` | `h-e1/code/data.py` |
| SimpleCNN (shape reference only) | `from zoo_generator import SimpleCNN` | `h-e1/code/zoo_generator.py` |
| Config (nfn_channels=32) | `from config import Config` | `h-e1/code/config.py` |
| Checkpoint | N/A (torch.load) | `h-e1/checkpoints/nfn_model.pt` |

**Verified from**: `h-e1/code/` (actual implementation, not 03_architecture.md spec).

---

## Modules

### test_data.py (`h-m1/code/test_data.py`)

**Dependencies**: torch

```python
def generate_test_mlp(hidden_sizes: list[int] = [64, 64], input_dim: int = 3072,
                       output_dim: int = 10, seed: int = 42) -> dict:
    # returns state_dict-compatible dict: {"net.0.weight":..., "net.0.bias":..., "net.2.weight":..., ...}
```

### permute.py (`h-m1/code/permute.py`)

**Dependencies**: torch

```python
def generate_permutations(hidden_sizes: list[int], seed: int) -> list[Tensor]:
    # one torch.randperm(h) per hidden layer

def permute_state_dict(state_dict: dict, hidden_layer_keys: list[str],
                        perms: list[Tensor]) -> dict:
    # permutes each hidden layer's output rows/bias, propagates perm to next layer's input cols
    # output layer (last key) only receives input-col permutation from last hidden perm
```

### metrics.py (`h-m1/code/metrics.py`)

**Dependencies**: torch

```python
def compute_invariance_metrics(predictions: list[float]) -> dict:
    # {mean, std, max_deviation, invariance_score, invariance_correlation}

def gate_passed(metrics: dict, dev_threshold: float = 1e-5, corr_threshold: float = 0.99) -> bool: ...
```

### test_invariance.py (`h-m1/code/test_invariance.py`)

**Dependencies**: permute.py, test_data.py, metrics.py, h-e1/code/{model.py, data.py, config.py}

```python
def load_nfn_model(checkpoint_path: str, network_spec, nfn_channels: int) -> nn.Module: ...
def state_dict_to_wsfeat(state_dict: dict, network_spec) -> Any: ...  # via nfn.common.state_dict_to_tensors
def run_invariance_test(nfn_model, base_state_dict: dict, hidden_sizes: list[int],
                         n_perms: int = 10) -> dict:  # {predictions, metrics, gate_passed}
def plot_predictions_bar(predictions: list[float], out_path: str) -> None: ...
def plot_deviation_heatmap(predictions: list[float], out_path: str) -> None: ...
def plot_prediction_histogram(predictions: list[float], out_path: str) -> None: ...
def main() -> None: ...  # orchestrates load -> generate -> permute -> predict -> metrics -> save/plot
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Test MLP generator | `generate_test_mlp` matching H-E1 SimpleCNN shape (3072-64-64-10, seed=42) | 5 | 1+1+2+1 |
| M-2 | Permutation generator | `generate_permutations` for hidden layers, seeds 0-9 | 4 | 1+1+1+1 |
| M-3 | Permutation application | `permute_state_dict`: propagate perm across adjacent layer weights/biases correctly | 8 | 2+2+3+1 |
| M-4 | Load H-E1 NFN + network_spec | Reuse `get_network_spec_from_sample`, load checkpoint, eval mode | 7 | 2+3+1+1 |
| M-5 | wsfeat conversion | Convert state_dict -> WeightSpaceFeatures batched tensor for NFN input | 6 | 2+2+2+0 |
| M-6 | Inference loop | Run NFN on original + 10 permuted state_dicts, collect predictions | 5 | 1+2+1+1 |
| M-7 | Invariance metrics | mean/std/max_deviation/invariance_score/correlation computation | 4 | 1+1+2+0 |
| M-8 | Visualization | Bar chart (required) + deviation heatmap + histogram | 5 | 2+1+1+1 |
| M-9 | Gate evaluation + results | Apply gate logic, write results.json, orchestrate main() | 6 | 2+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [M-1, M-2, M-3, M-4, M-5, M-6, M-7, M-8, M-9]

---

## Notes

- Permutation propagation (M-3) is the correctness-critical module: hidden layer `net.{2i}` output rows/bias permuted by `perm[i]`; hidden layer `net.{2i+2}` input cols permuted by `perm[i]`; final output layer (`net.4`) only gets input-col permutation from `perm[1]`, no output permutation (must preserve class order for valid comparison — though NFN treats output layer permutation-invariant regardless).
- No training code needed — pure inference + numerical test, matches PRD NFR-1 (<60s runtime).
- `input_dim=3072` correction is load-bearing: using PRD's 784 would produce a shape mismatch against the H-E1 checkpoint's `network_spec`.
