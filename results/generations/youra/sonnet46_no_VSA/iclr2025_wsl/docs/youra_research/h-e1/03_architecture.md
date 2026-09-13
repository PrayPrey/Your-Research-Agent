# Architecture: H-E1
# OrbitVar Measurement — DeepSets & NFN Encoders on ModelZooDataset CIFAR10-GS

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Date:** 2026-08-03

Applied: N/A — Archon KB contains diffusion model docs only; no relevant weight-space patterns found (max sim ~0.49)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field — no local codebase to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch. External patterns sourced from AllanYangZhou/nfn (official, pip-installable), AvivNavon/DWSNets (S_16³ permutation definition), and dpernes/deepsets-digitsum (DeepSets φ→sum→ρ pattern).

---

## Overview

Minimal measurement experiment. No training. 5,000 forward passes (100 models × 50 permutations). Seven files; single entry point `run_experiment.py`.

Architecture invariants:
- C2 OrbitVar = 0 guaranteed by Deep Sets Theorem 2 (sum pooling)
- C3 OrbitVar ≈ 0 by NFN structured equivariance (HNPPool)
- Functional audit MUST pass before any encoding runs

---

## File Organization

```
h-e1/
  code/
    data_loader.py      # ModelZooDataset loading + CNN state dict reconstruction
    permutation.py      # S_16³ coupled row-column permutations + audit
    encoder_c2.py       # DeepSetsChannelEncoder
    encoder_c3.py       # NFN encoder via nfn library
    orbit_var.py        # OrbitVar computation loop
    visualization.py    # Bar chart, PCA scatter, violin plot
    run_experiment.py   # Entry point: wires all modules
  data/                 # gitignored — dataset_cifar_small_hyp_rand.pt goes here
  figures/              # output figures
  results/              # orbit_var_results.json
```

---

## Module Interfaces

### DataLoader (`code/data_loader.py`)

**Dependencies:** torch, json

```python
def load_dataset(pt_path: str) -> list[tuple]:
    """Returns list of (weight_vector, accuracy) tuples."""
    ...

def reconstruct_state_dict(
    weight_vector: torch.Tensor,
    index_dict: dict
) -> dict[str, torch.Tensor]:
    """Maps flat weight vector → CNN layer state dict using index_dict.json."""
    ...

def load_index_dict(json_path: str) -> dict:
    ...

# CNN architecture reference (3 conv C=16, 1 dense, AdaptiveAvgPool2d)
CNN_LAYER_NAMES: list[str]  # ordered list of weight keys
```

---

### Permutation (`code/permutation.py`)

**Dependencies:** torch, numpy

```python
def sample_functional_permutations(
    num_layers: int,
    channels: int,
    K: int,
    seed: int = 1
) -> list[list[torch.Tensor]]:
    """
    Returns K permutation specs. Each spec is a list of per-layer
    channel permutation indices implementing S_16³ (DWSNet Eq. 5).
    Couples rows of W^(i) with columns of W^(i+1).
    """
    ...

def apply_permutation(
    state_dict: dict[str, torch.Tensor],
    perm_spec: list[torch.Tensor]
) -> dict[str, torch.Tensor]:
    """Applies coupled row-column permutation to CNN state dict."""
    ...

def audit_functional_equivalence(
    state_dict: dict[str, torch.Tensor],
    perm_specs: list[list[torch.Tensor]],
    cnn_class,
    tol: float = 1e-6,
    n_checks: int = 5
) -> float:
    """
    Verifies ||f_v(x) - f_{π·v}(x)||_∞ ≤ tol for random x ∈ [0,1]^(3,32,32).
    Returns max_diff. Raises AssertionError if any check fails.
    """
    ...
```

---

### C2 Encoder (`code/encoder_c2.py`)

**Dependencies:** torch, torch.nn

```python
class DeepSetsChannelEncoder(nn.Module):
    def __init__(
        self,
        layer_weight_dims: list[int],   # flattened weight dim per conv layer
        hidden_dim: int = 64,
        embed_dim: int = 128
    ): ...

    def forward(self, state_dict: dict[str, torch.Tensor]) -> torch.Tensor:
        """
        Per layer: phi(W_layer) → sum over C_out dim → rho → layer_embed.
        Concatenate layer embeds → (embed_dim,).
        Input channel order is irrelevant by construction.
        """
        ...

# ponytail: hidden_dim/embed_dim fixed constants; add config dict if tuning needed
```

---

### C3 Encoder (`code/encoder_c3.py`)

**Dependencies:** torch, torch.nn, nfn

```python
def build_nfn_encoder(
    sample_state_dict: dict[str, torch.Tensor],
    nfn_channels: int = 32,
    embed_dim: int = 128
) -> nn.Sequential:
    """
    Constructs NFN encoder:
      NPLinear → ReLU → NPLinear → ReLU → HNPPool → Flatten → Linear(embed_dim)
    network_spec derived from sample WeightSpaceFeatures.
    """
    ...

def state_dict_to_wsfeat(
    state_dict: dict[str, torch.Tensor]
) -> object:
    """Wraps nfn.common.state_dict_to_tensors(); returns WeightSpaceFeatures."""
    ...

def encode(
    nfn_model: nn.Sequential,
    state_dict: dict[str, torch.Tensor]
) -> torch.Tensor:
    """Converts state_dict → WeightSpaceFeatures → nfn forward → (embed_dim,)."""
    ...
```

---

### OrbitVar (`code/orbit_var.py`)

**Dependencies:** torch, numpy, encoder_c2, encoder_c3, permutation

```python
def compute_orbit_var_all_models(
    dataset: list[tuple],
    index_dict: dict,
    encoder_fn,           # callable: state_dict -> Tensor
    perm_specs: list,
    dtype=torch.float64
) -> tuple[list[float], float, float]:
    """
    Returns (per_model_vars, mean_orbitvar, max_orbitvar).
    Iterates 100 models × 50 permutations; variance over embedding dim mean.
    """
    ...

def run_gate_check(
    mean_c2: float,
    mean_c3: float,
    threshold: float = 1e-6
) -> bool:
    """Prints PASS/FAIL; returns True if both means < threshold."""
    ...
```

---

### Visualization (`code/visualization.py`)

**Dependencies:** matplotlib, numpy

```python
def plot_orbitvar_bar(
    results: dict,          # {"C2": mean_c2, "C3": mean_c3, "CISE": 0.010333}
    threshold: float = 1e-6,
    save_path: str = "figures/orbitvar_comparison.png"
) -> None:
    """Log-scale bar chart with horizontal threshold line."""
    ...

def plot_pca_scatter(
    embeddings: dict[str, list[torch.Tensor]],   # encoder_name -> list of (K, embed_dim)
    n_models: int = 10,
    save_path: str = "figures/pca_scatter.png"
) -> None:
    """PCA of encoder outputs for n_models × 50 permutations."""
    ...

def plot_violin(
    per_model_vars: dict[str, list[float]],      # {"C2": [...], "C3": [...]}
    save_path: str = "figures/violin_orbitvar.png"
) -> None:
    """Violin plot of per-model OrbitVar distributions."""
    ...
```

---

### Run Experiment (`code/run_experiment.py`)

**Dependencies:** all modules above

```python
def main() -> None:
    """
    1. load_dataset + load_index_dict
    2. sample_functional_permutations (seed=1)
    3. audit_functional_equivalence (HARD BLOCK if fails)
    4. Build C2 (DeepSetsChannelEncoder) + C3 (build_nfn_encoder)
    5. compute_orbit_var_all_models for C2 and C3
    6. run_gate_check → print PASS/FAIL
    7. Save results/orbit_var_results.json
    8. Generate all figures
    """
    ...

if __name__ == "__main__":
    main()
```

**Results JSON schema:**
```json
{
  "mean_orbitvar_c2": float,
  "max_orbitvar_c2": float,
  "mean_orbitvar_c3": float,
  "max_orbitvar_c3": float,
  "cise_baseline": 0.010333,
  "gate_pass": bool,
  "seed": 1,
  "n_models": 100,
  "K": 50
}
```

---

## External Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| torch | >=1.12.0 | Tensors, CNN forward pass |
| numpy | >=1.21.0 | float64 variance computation |
| nfn | latest | NPLinear, HNPPool, WeightSpaceFeatures |
| matplotlib | >=3.5.0 | Figures |
| scipy | >=1.7.0 | PCA (scipy.linalg or sklearn fallback) |

---

## Proposed Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment + Data Setup | Install deps (nfn, torch), download dataset from Zenodo, verify load, reconstruct state dicts, implement `data_loader.py` | 9 | 2+2+2+3 |
| A-2 | Permutation Module | Implement S_16³ coupled row-column permutations + functional audit; verify ||f_v - f_{π·v}||_∞ ≤ 1e-6 | 13 | 3+2+4+4 |
| A-3 | C2 DeepSets Encoder | Implement `DeepSetsChannelEncoder` (phi→sum→rho per layer, concat); verify shape invariance | 10 | 3+2+3+2 |
| A-4 | C3 NFN Encoder | Build NFN encoder via `nfn` library (NPLinear+HNPPool); verify CNN spatial folding compatibility | 12 | 3+4+3+2 |
| A-5 | OrbitVar Computation + Gate | Implement measurement loop (100×50 forward passes), compute mean/max OrbitVar, PASS/FAIL gate, save JSON | 11 | 3+3+3+2 |
| A-6 | Visualization + Integration | Bar chart (log scale), PCA scatter, violin plot; wire `run_experiment.py` end-to-end | 9 | 2+2+2+3 |

**Distribution:** Very High (18-20): [] | High (14-17): [] | Medium (9-13): [A-1, A-2, A-3, A-4, A-5, A-6] | Low (4-8): []

**Total Complexity:** 64 | **Task Count:** 6 (within EXISTENCE LIGHT range 4-8)

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: N/A" line)
- [x] Module sections = interface code only
- [x] 6 Epic tasks with complexity scores (EXISTENCE LIGHT: 4-8 range)
- [x] Codebase Analysis (Serena) section included
- [x] Green-field — Serena skip acceptable
