# Architecture: H-E1

**hypothesis_id:** h-e1
**hypothesis_type:** EXISTENCE (PoC)
**generated_at:** 2026-03-16
**Applied:** PyTorch canonical attention pattern (scaled_dot_product_attention basis for NFT)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - no code to analyze
**Analyzed Path:** N/A (Serena returned no active project; confirmed no existing `src/` or `code/` directory)
**Findings:** New implementation from scratch. All interfaces designed from PRD + literature (Zhou et al. 2023, Unterthiner et al. 2020).

---

## File Organization

```
h-e1/
├── data/
│   └── unterthiner_mnist_zoo.pkl
├── src/
│   ├── data_loader.py
│   ├── models.py
│   ├── train.py
│   ├── evaluate.py
│   └── visualize.py
├── tests/
│   ├── test_data_loader.py
│   ├── test_models.py
│   └── test_evaluate.py
├── figures/
├── checkpoints/
├── results/
│   ├── h-e1_results.json
│   └── gate_result.json
└── run_experiment.py
```

---

## Module Structure

### DataLoader (`src/data_loader.py`)

**Dependencies:** torch, numpy, pickle, urllib

```python
def download_zoo(url: str, save_path: str) -> None: ...

def load_zoo(pkl_path: str) -> list[dict]: ...
    # Returns list of dicts with keys: 'weights', 'train_acc', 'test_acc'
    # Raises ValueError if len(zoo_data) < 500

def compute_gen_gap(sample: dict) -> float: ...
    # Returns train_acc - test_acc

def apply_permutation_stress(weight_matrices: list[Tensor], severity: float) -> list[Tensor]: ...
    # severity in {0, 0.25, 0.5, 1.0}

class ZooDataset(Dataset):
    def __init__(self, samples: list[dict], mode: str = "flat"): ...
        # mode: "flat" | "nft"
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> tuple[Tensor | list[Tensor], Tensor]: ...
        # flat mode: returns (flat_vec, gap_scalar)
        # nft mode: returns (list_of_weight_matrices, gap_scalar)

def get_dataloaders(
    pkl_path: str,
    batch_size: int = 64,
    train_ratio: float = 0.8,
    seed: int = 42,
) -> tuple[DataLoader, DataLoader]:
    # Returns (train_loader, test_loader)
    # Each loader yields both flat and nft formats via collate_fn
    ...

def nft_collate_fn(batch: list) -> tuple[list[Tensor], Tensor]: ...
    # Pads variable-length weight matrices for batch assembly
```

---

### Models (`src/models.py`)

**Dependencies:** torch, torch.nn

```python
class FlatMLPEncoder(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 512): ...
        # 3 x hidden_dim hidden layers, ReLU, output Linear(hidden_dim, 1)
    def forward(self, x: Tensor) -> Tensor: ...
        # x: (B, input_dim) -> (B, 1)

class NFTEquivariantEncoder(nn.Module):
    def __init__(
        self,
        layer_fan_ins: list[int],
        d_model: int = 128,
        n_heads: int = 4,
    ): ...
        # layer_fan_ins: list of fan_in per layer, e.g. [784, 256, 128]
        # Creates separate nn.Linear(fan_in_l, d_model) per layer
        # Raises ValueError if any fan_in <= 0

    def forward(self, weight_matrices: list[Tensor]) -> Tensor: ...
        # weight_matrices: list of (B, n_neurons_l, fan_in_l), one per layer
        # Returns: (B, 1)
        # Logs token shape: "NFT tokens: (B, total_neurons, d_model)"

    def get_last_token_shape(self) -> tuple[int, int, int]: ...
        # Returns shape of last all_tokens tensor for mechanism verification
```

---

### Train (`src/train.py`)

**Dependencies:** torch, torch.optim, tqdm, src.models, src.data_loader

```python
def set_seed(seed: int = 42) -> None: ...
    # Sets torch, numpy, random seeds

def train_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: Optimizer,
    device: torch.device,
    model_type: str,  # "flat" | "nft"
) -> float: ...
    # Returns mean MSE loss for epoch

def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    n_epochs: int = 100,
    lr: float = 1e-3,
    device: torch.device = None,
    model_type: str = "flat",
    checkpoint_path: str = None,
) -> dict: ...
    # Uses Adam(lr=lr, weight_decay=1e-4) + CosineAnnealingLR(T_max=n_epochs)
    # Handles NaN: reduces lr to 1e-4 and retries once
    # Returns {"train_loss_history": list[float], "final_epoch": int}
```

---

### Evaluate (`src/evaluate.py`)

**Dependencies:** torch, scipy.stats, numpy, src.data_loader

```python
def apply_stress_and_predict(
    model: nn.Module,
    test_loader: DataLoader,
    severity: float,
    device: torch.device,
    model_type: str,  # "flat" | "nft"
) -> tuple[np.ndarray, np.ndarray]: ...
    # Returns (predictions, labels)

def compute_delta_rho(
    model: nn.Module,
    test_loader: DataLoader,
    severity_levels: list[float],
    device: torch.device,
    model_type: str,
) -> tuple[float, dict[float, float]]: ...
    # Returns (delta_rho, rho_by_severity)
    # delta_rho = rho(s=0) - rho(s=1.0)

def bootstrap_delta_rho(
    model: nn.Module,
    test_loader: DataLoader,
    device: torch.device,
    model_type: str,
    n_bootstrap: int = 10000,
    seed: int = 42,
) -> tuple[np.ndarray, float]: ...
    # Returns (bootstrap_delta_rho_samples, p_value)

def holm_correction(p_values: list[float]) -> list[float]: ...
    # Returns Holm-corrected p-values

def evaluate_gate_condition(
    flat_mlp_delta_rho: float,
    nft_delta_rho: float,
    flat_mlp_p: float,
    nft_p: float,
) -> dict: ...
    # Returns {"pass": bool, "flat_mlp_delta_rho": float, "nft_delta_rho": float,
    #          "flat_threshold_met": bool, "nft_threshold_met": bool}

def verify_mechanism_activated(
    model: nn.Module,
    sample_batch,
    results: dict,
) -> tuple[bool, dict]: ...
    # Returns (all_pass, indicators_dict)
    # Checks token shape, permutation changes output, NFT less degraded than flat-MLP
```

---

### Visualize (`src/visualize.py`)

**Dependencies:** matplotlib, seaborn, numpy

```python
def plot_delta_rho_bar(
    flat_mlp_delta_rho: float,
    nft_delta_rho: float,
    save_path: str,
) -> None: ...
    # MANDATORY: bar chart with Δρ=0.10 (flat threshold) and Δρ=0.02 (NFT threshold) lines

def plot_rho_vs_severity(
    flat_rho_by_severity: dict[float, float],
    nft_rho_by_severity: dict[float, float],
    save_path: str,
) -> None: ...

def plot_pred_vs_actual(
    flat_preds_s0: np.ndarray, flat_labels: np.ndarray,
    nft_preds_s0: np.ndarray,
    flat_preds_s1: np.ndarray,
    nft_preds_s1: np.ndarray,
    save_path: str,
) -> None: ...

def plot_bootstrap_distribution(
    flat_bootstrap: np.ndarray,
    nft_bootstrap: np.ndarray,
    save_path: str,
) -> None: ...

def generate_all_figures(results: dict, figures_dir: str) -> None: ...
    # Calls all 4 plot functions; saves to figures_dir/
```

---

### Experiment Runner (`run_experiment.py`)

**Dependencies:** src.data_loader, src.models, src.train, src.evaluate, src.visualize, json, os

```python
def main(
    data_path: str = "data/unterthiner_mnist_zoo.pkl",
    figures_dir: str = "figures",
    checkpoints_dir: str = "checkpoints",
    results_dir: str = "results",
    device_str: str = "cuda",
    seed: int = 42,
) -> None: ...
    # 1. Download data if missing
    # 2. Build dataloaders (flat + nft)
    # 3. Infer input_dim (flat) and layer_fan_ins (NFT) from first sample
    # 4. Train FlatMLPEncoder, save checkpoint
    # 5. Train NFTEquivariantEncoder, save checkpoint
    # 6. Evaluate both: compute_delta_rho, bootstrap, gate
    # 7. verify_mechanism_activated
    # 8. generate_all_figures
    # 9. Write results/h-e1_results.json + results/gate_result.json

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

### Epic E-1: Data Pipeline
**Complexity Score:** 10/20
- Module_Size: 3/5
- Dependencies: 2/5
- Algorithm: 2/5
- Integration: 3/5

**Description:** Download Unterthiner zoo, load and parse weight matrices + gen-gap labels, implement flat/NFT preprocessing, permutation stress function, ZooDataset, and get_dataloaders with nft_collate_fn. Validate >= 500 models.

**Target Files:** `src/data_loader.py`, `data/` directory

**Dependencies:** None (foundation)

---

### Epic E-2: Model Implementation
**Complexity Score:** 14/20
- Module_Size: 3/5
- Dependencies: 2/5
- Algorithm: 4/5
- Integration: 5/5

**Description:** Implement FlatMLPEncoder (3x512 ReLU MLP) and NFTEquivariantEncoder with per-layer fan_in projections, nn.MultiheadAttention(d_model=128, n_heads=4, batch_first=True), mean pooling, regression head. NFT must handle variable layer count (2-4) via padding/masking. Fail fast on fan_in incompatibility. Log token shapes.

**Target Files:** `src/models.py`

**Dependencies:** E-1 (need fan_in values from actual data samples)

---

### Epic E-3: Training Loop
**Complexity Score:** 10/20
- Module_Size: 2/5
- Dependencies: 3/5
- Algorithm: 3/5
- Integration: 2/5

**Description:** Adam optimizer (lr=1e-3, weight_decay=1e-4), CosineAnnealingLR (T_max=100), MSE loss, 100 epochs, batch_size=64, seed=42. NaN handling (reduce lr to 1e-4, retry once). Checkpoint saving per model. Progress logging (loss per epoch).

**Target Files:** `src/train.py`

**Dependencies:** E-1, E-2

---

### Epic E-4: Evaluation & Gate
**Complexity Score:** 14/20
- Module_Size: 3/5
- Dependencies: 3/5
- Algorithm: 4/5
- Integration: 4/5

**Description:** compute_delta_rho() across s in {0, 0.25, 0.5, 1.0}. Paired bootstrap (n=10,000) Δρ estimation with p-value. Holm correction. evaluate_gate_condition() writing gate_result.json. verify_mechanism_activated() with 3 indicators. Write h-e1_results.json.

**Target Files:** `src/evaluate.py`

**Dependencies:** E-1, E-2, E-3

---

### Epic E-5: Visualization
**Complexity Score:** 8/20
- Module_Size: 2/5
- Dependencies: 2/5
- Algorithm: 2/5
- Integration: 2/5

**Description:** 4 figures: mandatory Δρ bar chart with threshold lines, ρ(s) line plot, pred vs actual scatter, bootstrap distribution histogram. Save to figures/.

**Target Files:** `src/visualize.py`

**Dependencies:** E-4 (results dict)

---

### Epic E-6: Experiment Runner & Tests
**Complexity Score:** 10/20
- Module_Size: 2/5
- Dependencies: 4/5
- Algorithm: 1/5
- Integration: 3/5

**Description:** run_experiment.py orchestrating E-1 through E-5. Unit tests for data_loader (download/parse/stress), models (forward shapes, fan_in error), evaluate (delta_rho, gate logic). Minimum 3 test methods with real assertions per test file.

**Target Files:** `run_experiment.py`, `tests/test_data_loader.py`, `tests/test_models.py`, `tests/test_evaluate.py`

**Dependencies:** E-1, E-2, E-3, E-4, E-5

---

## Task Distribution

**Distribution:**
- VeryHigh (18-20): []
- High (14-17): [E-2, E-4]
- Medium (9-13): [E-1, E-3, E-6]
- Low (4-8): [E-5]

---

## Key Technical Notes

- NFT per-layer projections: `self.layer_projections = nn.ModuleList([nn.Linear(fan_in, d_model) for fan_in in layer_fan_ins])` — one Linear per layer, resolves variable fan_in
- Variable layer count (2-4): concatenate tokens from available layers only; no padding needed if mean pooling is the aggregator (token count varies, pooling handles it)
- `nft_collate_fn` must handle variable total neuron counts across batch items — pad to max total neurons per batch, use attention mask
- Permutation stress applied at test-time inference only (not during training)
- Single GPU: `CUDA_VISIBLE_DEVICES` set before launch, device inferred in `run_experiment.py`
- PoC pass condition: code runs + `nft_delta_rho < flat_mlp_delta_rho`

---

*Generated by Phase 3 Architecture Agent*
*Hypothesis: H-E1 | Type: EXISTENCE | Tier: LIGHT*
*Archon KB: low domain relevance (diffusion model content), design grounded in Zhou et al. 2023 + Unterthiner et al. 2020*
