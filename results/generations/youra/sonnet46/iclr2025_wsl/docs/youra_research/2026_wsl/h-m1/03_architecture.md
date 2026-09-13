# Architecture: H-M1

**hypothesis_id:** h-m1
**hypothesis_type:** MECHANISM
**generated_at:** 2026-03-16
**extends:** H-E1 (COMPLETED — PASS)

Applied: ablation-suite multi-encoder pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code (direct file read — Serena project activation failed; read all 5 H-E1 src files directly)
**Analyzed Path**: `docs/youra_research/20260316_wsl/h-e1/code/src/`
**Findings**: H-E1 implements `FlatMLPEncoder` (input_dim, hidden_dim=512) and `NFTEquivariantEncoder` (layer_fan_ins, d_model=128, n_heads=4) in `src/models.py`; `apply_permutation_stress`, `ZooDataset`, `get_dataloaders`, `nft_collate_fn` in `src/data_loader.py`; `compute_delta_rho`, `bootstrap_delta_rho`, `holm_correction`, `evaluate_gate_condition` in `src/evaluate.py`; `train_model`, `train_epoch`, `set_seed` in `src/train.py`. The `get_dataloaders` returns 4 loaders (flat_train, flat_test, nft_train, nft_test) and uses `model_type` string ('flat' or 'nft') throughout — H-M1 must generalize this to 6 encoder variants.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| FlatMLPEncoder | `from h_e1.src.models import FlatMLPEncoder` | `h-e1/code/src/models.py` |
| NFTEquivariantEncoder | `from h_e1.src.models import NFTEquivariantEncoder` | `h-e1/code/src/models.py` |
| apply_permutation_stress | `from h_e1.src.data_loader import apply_permutation_stress` | `h-e1/code/src/data_loader.py` |
| ZooDataset | `from h_e1.src.data_loader import ZooDataset` | `h-e1/code/src/data_loader.py` |
| load_zoo | `from h_e1.src.data_loader import load_zoo` | `h-e1/code/src/data_loader.py` |
| nft_collate_fn | `from h_e1.src.data_loader import nft_collate_fn` | `h-e1/code/src/data_loader.py` |
| compute_delta_rho | `from h_e1.src.evaluate import compute_delta_rho` | `h-e1/code/src/evaluate.py` |
| bootstrap_delta_rho | `from h_e1.src.evaluate import bootstrap_delta_rho` | `h-e1/code/src/evaluate.py` |
| holm_correction | `from h_e1.src.evaluate import holm_correction` | `h-e1/code/src/evaluate.py` |
| train_model | `from h_e1.src.train import train_model` | `h-e1/code/src/train.py` |
| set_seed | `from h_e1.src.train import set_seed` | `h-e1/code/src/train.py` |

**Verified from**: `docs/youra_research/20260316_wsl/h-e1/code/src/` (actual implementation)

**Note on import strategy**: H-M1 copies H-E1 `src/` into its own `src/` and extends locally. Actual import paths in H-M1 code use `from src.models import ...` within the h-m1 codebase (same pattern as H-E1).

---

## File Organization

```
h-m1/
├── data/
│   └── unterthiner_mnist_zoo.pkl
├── src/
│   ├── __init__.py
│   ├── config.py          # ENCODER_CONFIG, training hyperparams, seed list
│   ├── data_loader.py     # Extends H-E1: adds canonicalize_weights, per-encoder DataLoader
│   ├── models.py          # All 6 encoder classes (E1-E6); E1/E4 copied from H-E1
│   ├── train.py           # Extends H-E1: multi-encoder, multi-seed orchestration
│   ├── evaluate.py        # Extends H-E1: adds R², ΔR², mediation, gate v2, bootstrap all-pairs
│   └── visualize.py       # 5 figure types
├── tests/
│   ├── test_data_loader.py
│   ├── test_models.py
│   └── test_evaluate.py
├── figures/
├── checkpoints/
│   └── {encoder_name}_seed{s}/
├── results/
│   ├── h-m1_results.json
│   └── gate_result.json
└── run_experiment.py
```

---

## Module Definitions

### config (`src/config.py`)

**Dependencies**: none

```python
SEEDS: list[int] = [42, 123, 456]
SEVERITY_LEVELS: list[float] = [0.0, 0.25, 0.5, 1.0]
N_EPOCHS: int = 100
BATCH_SIZE: int = 64
LR: float = 1e-3
WEIGHT_DECAY: float = 1e-4
N_BOOTSTRAP: int = 10000

ENCODER_CONFIG: dict = {
    "flat-MLP":        {"aug_severity": None, "canon": False,       "model_type": "flat"},
    "flat-MLP+aug":    {"aug_severity": 1.0,  "canon": False,       "model_type": "flat"},
    "flat-MLP+canon":  {"aug_severity": None, "canon": "l2_norm",   "model_type": "flat"},
    "NFT-base":        {"aug_severity": None, "canon": False,       "model_type": "nft"},
    "NFT+aug":         {"aug_severity": 1.0,  "canon": False,       "model_type": "nft"},
    "Oracle-canon":    {"aug_severity": None, "canon": "oracle",    "model_type": "flat"},
}

ENCODER_NAMES: list[str]   # ordered list of 6 encoder names
DATA_PATH: str             # default "data/unterthiner_mnist_zoo.pkl"
RESULTS_DIR: str           # default "results/"
FIGURES_DIR: str           # default "figures/"
CHECKPOINT_DIR: str        # default "checkpoints/"
```

---

### data_loader (`src/data_loader.py`)

**Dependencies**: config

**Reused from H-E1** (copied): `load_zoo`, `compute_gen_gap`, `flatten_weights`, `_weight_to_2d`, `apply_permutation_stress`, `ZooDataset`, `nft_collate_fn`

**New additions**:

```python
def canonicalize_weights(
    weight_list: list,
    method: str,
    unpermuted_weight_list: list = None,
) -> list:
    """Sort neurons per layer by L2 norm.

    Parameters
    ----------
    weight_list : list[np.ndarray]
        Each array reshaped to (n_units, fan_in).
    method : str
        'l2_norm' — sort by L2 norm of stressed weights.
        'oracle'  — sort by L2 norm of unpermuted_weight_list.
    unpermuted_weight_list : list[np.ndarray] or None
        Required when method='oracle'.

    Returns
    -------
    list[np.ndarray]
        Canonicalized weight arrays, same shapes as input.
    """
    ...


def get_encoder_dataloaders(
    pkl_path: str,
    encoder_name: str,
    seed: int = 42,
    batch_size: int = 64,
    train_ratio: float = 0.8,
) -> tuple:
    """Return (train_loader, test_loader) for a specific encoder variant.

    Handles mode selection (flat vs nft), collate function, augmentation config.

    Returns
    -------
    tuple
        (train_loader, test_loader, flat_input_dim, layer_fan_ins)
        flat_input_dim: int (for flat encoders)
        layer_fan_ins: list[int] (for nft encoders)
    """
    ...
```

---

### models (`src/models.py`)

**Dependencies**: config

**Reused from H-E1** (copied verbatim): `FlatMLPEncoder`, `NFTEquivariantEncoder`

**New encoder variants**:

```python
class FlatMLPAugEncoder(FlatMLPEncoder):
    """E2: flat-MLP + training-time permutation augmentation (50% prob, s=1.0)."""

    def __init__(self, input_dim: int, hidden_dim: int = 512, aug_severity: float = 1.0) -> None: ...

    def forward(self, x: Tensor, weight_list: list = None, training_aug: bool = False) -> Tensor:
        """x: (B, input_dim). Returns (B, 1)."""
        ...


class FlatMLPCanonEncoder(FlatMLPEncoder):
    """E3: flat-MLP + L2-norm canonicalization (applied at both train and eval)."""

    def __init__(self, input_dim: int, hidden_dim: int = 512) -> None: ...

    def forward(self, x: Tensor) -> Tensor:
        """x: (B, input_dim) — already canonicalized before this call. Returns (B, 1)."""
        ...


class NFTAugEncoder(NFTEquivariantEncoder):
    """E5: NFT-base + training-time permutation augmentation (50% prob, s=1.0)."""

    def __init__(
        self,
        layer_fan_ins: list,
        d_model: int = 128,
        n_heads: int = 4,
        aug_severity: float = 1.0,
    ) -> None: ...

    def forward(self, weight_matrices: list, training_aug: bool = False) -> Tensor:
        """weight_matrices: list[(B, n_units_l, fan_in_l)]. Returns (B, 1)."""
        ...


class OracleCanonEncoder(FlatMLPEncoder):
    """E6: flat-MLP with ground-truth canonical ordering (upper bound).
    Architecture identical to FlatMLPEncoder; canonicalization applied in data_loader.
    """

    def __init__(self, input_dim: int, hidden_dim: int = 512) -> None: ...

    def forward(self, x: Tensor) -> Tensor:
        """x: (B, input_dim) — oracle-canonicalized input. Returns (B, 1)."""
        ...


def build_encoder(encoder_name: str, flat_input_dim: int, layer_fan_ins: list) -> nn.Module:
    """Factory: instantiate correct encoder class from ENCODER_CONFIG name.

    Returns
    -------
    nn.Module
        One of FlatMLPEncoder, FlatMLPAugEncoder, FlatMLPCanonEncoder,
        NFTEquivariantEncoder, NFTAugEncoder, OracleCanonEncoder.
    """
    ...
```

---

### train (`src/train.py`)

**Dependencies**: config, models, data_loader

**Reused from H-E1** (copied): `set_seed`, `train_epoch`

**Extended/new**:

```python
def train_encoder_one_seed(
    encoder_name: str,
    seed: int,
    pkl_path: str,
    device: torch.device,
    n_epochs: int = 100,
    checkpoint_dir: str = "checkpoints/",
) -> dict:
    """Train one encoder for one seed. Saves best-val checkpoint.

    Returns
    -------
    dict
        {"encoder_name", "seed", "train_loss_history", "val_loss_history",
         "best_val_loss", "checkpoint_path"}
    """
    ...


def train_all_encoders(
    pkl_path: str,
    device: torch.device,
    seeds: list = None,
    encoder_names: list = None,
    n_epochs: int = 100,
    checkpoint_dir: str = "checkpoints/",
) -> dict:
    """Orchestrate 18 training runs (6 encoders × 3 seeds). Fails soft per encoder.

    Returns
    -------
    dict
        Keyed by (encoder_name, seed) -> train result dict.
    """
    ...


def sanity_check_encoders(
    pkl_path: str,
    device: torch.device,
    n_samples: int = 10,
) -> bool:
    """Verify all 6 encoders produce valid output on n_samples. Fail fast if any fail.

    Returns
    -------
    bool
        True if all pass.
    """
    ...
```

---

### evaluate (`src/evaluate.py`)

**Dependencies**: config, models, data_loader, train

**Reused from H-E1** (copied): `apply_stress_and_predict`, `compute_delta_rho`, `bootstrap_delta_rho`, `holm_correction`, `_apply_flat_stress_batch`, `_apply_nft_stress_batch`

**New additions**:

```python
def compute_r2_score(
    model: nn.Module,
    test_loader,
    device: torch.device,
    encoder_name: str,
    severity: float = 0.0,
) -> float:
    """Compute sklearn R² score at given severity. Returns float."""
    ...


def compute_mediation_delta_r2(
    r2_by_encoder: dict,
) -> tuple:
    """ΔR² = R²(NFT-base) − R²(flat-MLP+aug).

    Parameters
    ----------
    r2_by_encoder : dict
        Keys: encoder_name -> list[float] (one per seed).

    Returns
    -------
    tuple
        (delta_r2_mean, delta_r2_std)
    """
    ...


def evaluate_all_encoders(
    models_by_encoder: dict,
    test_loaders: dict,
    device: torch.device,
    severity_levels: list = None,
    n_bootstrap: int = 10000,
) -> dict:
    """Full evaluation: Δρ, R², bootstrap, all-pairs Holm-corrected p-values.

    Parameters
    ----------
    models_by_encoder : dict
        {encoder_name: {seed: nn.Module}}
    test_loaders : dict
        {encoder_name: DataLoader}

    Returns
    -------
    dict
        Per-encoder and aggregate metrics including mediation_delta_r2.
    """
    ...


def evaluate_gate_condition_v2(results: dict, results_dir: str = "results/") -> dict:
    """H-M1 gate: nft_base_delta_rho < 0.02 AND mediation_delta_r2 >= 0.10.

    Writes gate_result.json. Returns gate result dict.
    """
    ...


def verify_mechanism_activated(results: dict) -> tuple:
    """5-indicator mechanism check.

    Returns
    -------
    tuple
        (gate_pass: bool, indicators: dict)
        indicators keys: nft_base_robust, mediation_confirmed, aug_partial,
                         architecture_sufficient, ranking_correct
    """
    ...
```

---

### visualize (`src/visualize.py`)

**Dependencies**: config, evaluate

```python
def plot_delta_rho_bar(
    results: dict,
    save_path: str = "figures/fig1_delta_rho_bar.png",
) -> None:
    """FR-13.1 (MANDATORY): Bar chart of Δρ at s=1.0 for 6 encoders with gate lines."""
    ...


def plot_delta_rho_curves(
    results: dict,
    save_path: str = "figures/fig2_delta_rho_curves.png",
) -> None:
    """FR-13.2: Multi-line Δρ(s) for 6 encoders across severity levels."""
    ...


def plot_mediation_bar(
    results: dict,
    save_path: str = "figures/fig3_mediation_bar.png",
) -> None:
    """FR-13.3: ΔR² breakdown bar chart (augmentation effect vs. architectural equivariance)."""
    ...


def plot_rho_heatmap(
    results: dict,
    save_path: str = "figures/fig4_rho_heatmap.png",
) -> None:
    """FR-13.4: 6-encoder × 4-severity Spearman ρ heatmap."""
    ...


def plot_bootstrap_distributions(
    bootstrap_samples: dict,
    save_path: str = "figures/fig5_bootstrap_dist.png",
) -> None:
    """FR-13.5: Bootstrap Δρ distribution comparison: NFT-base vs. flat-MLP+aug."""
    ...


def generate_all_figures(results: dict, figures_dir: str = "figures/") -> None:
    """Generate and save all 5 figures."""
    ...
```

---

### run_experiment (`run_experiment.py`)

**Dependencies**: config, data_loader, models, train, evaluate, visualize

```python
def parse_args() -> argparse.Namespace:
    """--encoder, --seed, --data-path, --device, --epochs flags."""
    ...


def main() -> None:
    """Orchestrate full H-M1 experiment:
    1. Sanity check all 6 encoders (10 samples).
    2. Train 18 runs (6 × 3 seeds).
    3. Evaluate all encoders (Δρ, R², mediation ΔR²).
    4. Bootstrap all-pairs (15 pairs), Holm correction.
    5. Gate evaluation → gate_result.json.
    6. Write h-m1_results.json.
    7. Generate 5 figures.
    """
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data & Config Setup | Copy H-E1 data loader, add `canonicalize_weights`, `get_encoder_dataloaders`, and `config.py` with ENCODER_CONFIG | 9 | 2+2+3+2 |
| A-2 | New Encoder Variants | Implement E2 (FlatMLPAugEncoder), E3 (FlatMLPCanonEncoder), E5 (NFTAugEncoder), E6 (OracleCanonEncoder) extending H-E1 base classes; `build_encoder` factory | 14 | 3+3+4+4 |
| A-3 | Multi-Seed Training Orchestration | Extend H-E1 `train_model` → `train_encoder_one_seed` + `train_all_encoders` with validation loop, best-ckpt save, soft-fail per encoder; `sanity_check_encoders` | 14 | 3+4+4+3 |
| A-4 | Evaluation Extensions | Add `compute_r2_score`, `compute_mediation_delta_r2`, `evaluate_all_encoders` (6 encoders × 3 seeds), all-pairs bootstrap (15 pairs), Holm correction | 16 | 3+4+5+4 |
| A-5 | Gate v2 & Mechanism Verification | `evaluate_gate_condition_v2` (ΔR² ≥ 0.10 AND NFT Δρ < 0.02), `verify_mechanism_activated` 5-indicator check, write gate_result.json | 10 | 2+3+3+2 |
| A-6 | Visualization (5 Figures) | Implement all 5 figure generators (bar chart, severity curves, mediation bar, heatmap, bootstrap dist) + `generate_all_figures` | 12 | 2+2+4+4 |
| A-7 | Experiment Runner & Tests | `run_experiment.py` orchestration with --encoder/--seed flags; unit tests for new encoder variants (≥3 per variant), data_loader, evaluate | 13 | 2+3+4+4 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2, A-3, A-4], Medium(9-13): [A-1, A-5, A-6, A-7], Low(4-8): []

---

## Reuse vs. Extend vs. New Summary

| Module | Strategy | Source |
|--------|----------|--------|
| `FlatMLPEncoder` | Copy verbatim | H-E1 `src/models.py` |
| `NFTEquivariantEncoder` | Copy verbatim | H-E1 `src/models.py` |
| `apply_permutation_stress` | Copy verbatim | H-E1 `src/data_loader.py` |
| `ZooDataset`, `load_zoo`, `nft_collate_fn` | Copy verbatim | H-E1 `src/data_loader.py` |
| `compute_delta_rho`, `bootstrap_delta_rho`, `holm_correction` | Copy verbatim | H-E1 `src/evaluate.py` |
| `set_seed`, `train_epoch` | Copy verbatim | H-E1 `src/train.py` |
| `canonicalize_weights`, `get_encoder_dataloaders` | New | H-M1 `src/data_loader.py` |
| `FlatMLPAugEncoder`, `FlatMLPCanonEncoder`, `NFTAugEncoder`, `OracleCanonEncoder` | New (extend base) | H-M1 `src/models.py` |
| `train_encoder_one_seed`, `train_all_encoders`, `sanity_check_encoders` | New (extend) | H-M1 `src/train.py` |
| `compute_r2_score`, `compute_mediation_delta_r2`, `evaluate_all_encoders`, `evaluate_gate_condition_v2`, `verify_mechanism_activated` | New | H-M1 `src/evaluate.py` |
| `visualize.py` (all 5 figures) | New | H-M1 `src/visualize.py` |
