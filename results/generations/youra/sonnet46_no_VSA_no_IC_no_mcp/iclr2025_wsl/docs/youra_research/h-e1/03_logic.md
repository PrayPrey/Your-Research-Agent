---
title: "Logic: H-E1 — Orbit Diameter Characterization"
hypothesis_id: H-E1
date: 2026-08-26
author: Anonymous
---

Applied: Flat-index unpacking pattern for parameterized weight tensors
Applied: Generator-seeded stateless transform pattern for reproducible orbit construction

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing codebase to analyze — new implementation from scratch.
**Base Hypothesis**: None (H-E1 is FOUNDATION).
**Findings**: All APIs designed from PRD/architecture specs and mathematical symmetry group definitions.

---

## API Signatures

### `data_loader.py`

```python
EXPECTED_DIM: int = 51_850
ARCH: dict = {"D_in": 784, "h": 64, "D_out": 10}

def load_zoo(
    hf_id: str = "ModelZoos/ModelZooDataset",
    config: str = "mnist-mlp",
    split: str = "train"
) -> list[dict]:
    """
    Load Schürholt MNIST zoo from HuggingFace.
    Falls back to local parquet if HuggingFace load fails.

    Returns:
        List of dicts, each with key "weights" (List[float], len=51850)
        and metadata keys "test_acc", "generalization_gap", "learning_rate".

    Raises:
        ValueError: if any model weight vector has dim != EXPECTED_DIM.
        RuntimeError: if both HuggingFace and local fallback fail.
    """

def sample_models(
    zoo: list[dict],
    n: int = 1000,
    seed: int = 42
) -> torch.Tensor:
    """
    Sample n models uniformly at random from zoo.

    Args:
        zoo: list of model dicts from load_zoo()
        n: number of models to sample (must be <= len(zoo))
        seed: random seed for reproducibility

    Returns:
        Tensor of shape (N, D) float32, where N=n, D=51850.

    Raises:
        ValueError: if n > len(zoo).
    """
```

---

### `orbit_construction.py`

```python
def construct_orbit_member(
    weights_flat: torch.Tensor,   # shape: (D,) where D=51850
    transform_type: str,           # "scaling" | "signflip" | "combined"
    seed: int
) -> torch.Tensor:
    """
    Construct a functionally equivalent weight vector via symmetry transform.

    Weight layout (D=51850):
        W1: indices [0 : 784*64]       → reshape to (784, 64)
        b1: indices [784*64 : 784*64+64]  → shape (64,)
        W2: indices [784*64+64 : 784*64+64+64*10] → reshape to (64, 10)
        b2: indices [-10:]              → shape (10,)

    Args:
        weights_flat: original model weight vector
        transform_type: which symmetry to apply
        seed: controls all randomness (torch.Generator)

    Returns:
        Transformed weight vector, same shape (D,).

    Raises:
        ValueError: if weights_flat.shape[0] != 51850
        ValueError: if cosine_distance(result, weights_flat) < 1e-6 (trivial transform)
    """

def build_all_orbits(
    weights: torch.Tensor,    # shape: (N, D)
    K: int = 5,
    base_seed: int = 42
) -> dict[str, torch.Tensor]:
    """
    Construct K orbit members per model for each of 3 symmetry types.

    Args:
        weights: (N, D) tensor of N sampled models
        K: number of orbit members per model per symmetry type
        base_seed: orbit member k uses seed = base_seed + k

    Returns:
        {
            "scaling":  torch.Tensor of shape (N, K, D),
            "signflip": torch.Tensor of shape (N, K, D),
            "combined": torch.Tensor of shape (N, K, D),
        }
    """
```

---

### `distance_metrics.py`

```python
def cosine_distance(
    v1: torch.Tensor,  # shape: (D,)
    v2: torch.Tensor   # shape: (D,)
) -> float:
    """
    Cosine distance = 1 - cosine_similarity.
    Range: [0, 2]. 0 = identical direction, 2 = opposite.
    Denominator guard: eps=1e-8 added before division.
    """

def l2_distance(
    v1: torch.Tensor,  # shape: (D,)
    v2: torch.Tensor   # shape: (D,)
) -> float:
    """Euclidean distance ||v1 - v2||_2."""

def compute_distances(
    weights: torch.Tensor,             # shape: (N, D)
    orbits: dict[str, torch.Tensor]   # each value: (N, K, D)
) -> dict[str, dict[str, list[float]]]:
    """
    Compute cosine and L2 distances between each original and its K orbit members.

    For each symmetry_type in orbits:
        For each model i in [0, N):
            For each orbit member k in [0, K):
                cosine_dist = cosine_distance(weights[i], orbits[sym][i, k])
                l2_dist = l2_distance(weights[i], orbits[sym][i, k])

    Also records max_scale for "scaling" type (max(alpha_i, 1/alpha_i) per model).

    Returns:
        {
            "scaling":  {"cosine": [float]*N*K, "l2": [float]*N*K, "max_scale": [float]*N*K},
            "signflip": {"cosine": [float]*N*K, "l2": [float]*N*K},
            "combined": {"cosine": [float]*N*K, "l2": [float]*N*K},
        }
    Total entries per metric per sym_type: N*K = 1000*5 = 5000.
    """
```

---

### `statistics.py`

```python
def aggregate(
    distances: list[float],
    threshold: float = 0.05,
    n_boot: int = 1000,
    seed: int = 42
) -> dict:
    """
    Compute summary statistics for a list of distances.

    Returns dict with keys:
        mean: float
        std: float
        p5: float   (5th percentile)
        p95: float  (95th percentile)
        frac_above: float  (fraction with distance > threshold)
        ci_lower: float    (bootstrap 95% CI lower bound)
        ci_upper: float    (bootstrap 95% CI upper bound)
    """

def evaluate_gate(
    stats: dict[str, dict]   # keyed by sym_type, values from aggregate()
) -> dict:
    """
    Evaluate PoC gate for H-E1 using scaling orbit stats.

    Gate condition (ALL must hold):
        stats["scaling"]["mean"] > 0.05
        stats["scaling"]["frac_above"] >= 0.90
        stats["scaling"]["ci_lower"] > 0

    Returns:
        {
            "pass": bool,
            "mean_cosine_scaling": float,
            "frac_above_scaling": float,
            "ci_lower_scaling": float,
            "gate_condition": str   # human-readable summary
        }
    """
```

---

### `visualization.py`

```python
def fig_gate_metrics(
    stats: dict[str, dict],
    out_dir: str = "docs/youra_research/h-e1/figures"
) -> None:
    """
    Bar chart: mean cosine distance per sym_type vs threshold=0.05.
    Error bars: bootstrap 95% CI (ci_lower, ci_upper from stats).
    Saves: fig_gate_metrics.png at 150 DPI.
    """

def fig_orbit_distribution(
    distances: dict[str, dict],
    out_dir: str = "docs/youra_research/h-e1/figures"
) -> None:
    """
    Overlaid histogram of cosine distances for all 3 sym_types.
    Vertical line at threshold=0.05.
    Saves: fig_orbit_distribution.png at 150 DPI.
    """

def fig_l2_vs_cosine(
    distances: dict[str, dict],
    out_dir: str = "docs/youra_research/h-e1/figures"
) -> None:
    """
    Scatter: L2 distance (y) vs cosine distance (x), color by sym_type.
    Saves: fig_l2_vs_cosine.png at 150 DPI.
    """

def fig_scale_vs_diameter(
    distances: dict[str, dict],
    out_dir: str = "docs/youra_research/h-e1/figures"
) -> None:
    """
    Scatter (scaling only): max_scale (x) vs cosine distance (y).
    Reveals relationship between transform magnitude and orbit diameter.
    Saves: fig_scale_vs_diameter.png at 150 DPI.
    """
```

---

### `main.py`

```python
def run(
    n_models: int = 1000,
    K: int = 5,
    seed: int = 42,
    results_path: str = "docs/youra_research/h-e1/results.json"
) -> dict:
    """
    Main experiment runner. Wires all modules in sequence:
        1. load_zoo() → sample_models() → weights (N, D)
        2. build_all_orbits(weights, K, seed) → orbits
        3. compute_distances(weights, orbits) → distances
        4. aggregate() per sym_type → stats
        5. evaluate_gate(stats) → gate
        6. fig_gate_metrics(), fig_orbit_distribution(), fig_l2_vs_cosine(), fig_scale_vs_diameter()
        7. Write results.json
        8. Print gate pass/fail

    Returns:
        Full results dict (same structure as results.json).

    Raises:
        SystemExit(1): if gate fails (for pipeline detection).
    """
```

---

## Tensor Shape Summary

| Variable | Shape | Dtype | Notes |
|----------|-------|-------|-------|
| `weights_flat` | `(D,)` | float32 | D=51850, single model |
| `weights` (sampled) | `(N, D)` | float32 | N=1000 |
| `W1` (unpacked) | `(784, 64)` | float32 | first layer weights |
| `b1` (unpacked) | `(64,)` | float32 | first layer bias |
| `W2` (unpacked) | `(64, 10)` | float32 | second layer weights |
| `b2` (unpacked) | `(10,)` | float32 | second layer bias |
| `scales` | `(64,)` | float32 | per-neuron scaling factors |
| `signs` | `(64,)` | float32 | per-neuron ±1 signs |
| `orbit_member` | `(D,)` | float32 | transformed, same D |
| `orbits[sym]` | `(N, K, D)` | float32 | N=1000, K=5, D=51850 |
| `distances[sym]["cosine"]` | list[float] len=N*K | float | 5000 values |

---

## Subtask 1: Scaling Transform Pseudo-code (A-2)

```python
def construct_orbit_member_scaling(weights_flat, seed):
    D_in, h, D_out = 784, 64, 10
    rng = torch.Generator().manual_seed(seed)

    # Unpack by index arithmetic
    i0 = D_in * h                    # 50176
    i1 = i0 + h                      # 50240
    i2 = i1 + h * D_out              # 50880
    # i2 to end = D_out = 10 → total 50890 ... wait: 50880+10=50890 != 51850
    # Correct: D_in*h=50176, h=64, h*D_out=640, D_out=10 → total=50890
    # NOTE: actual D=51850 per dataset. Verify with actual zoo loading.
    # If D differs, adjust ARCH constants accordingly.

    W1 = weights_flat[:i0].reshape(D_in, h)       # (784, 64)
    b1 = weights_flat[i0:i1]                       # (64,)
    W2 = weights_flat[i1:i2].reshape(h, D_out)    # (64, 10)
    b2 = weights_flat[i2:]                         # (10,)

    # Sample log-uniform scales: α_i ~ 10^U(-1,1)
    log_scales = torch.empty(h, generator=rng).uniform_(-1.0, 1.0)
    scales = 10.0 ** log_scales     # shape (64,), range [0.1, 10.0]

    # Apply: W1 scaled per column, b1 per element, W2 inverse per row
    W1_t = W1 * scales.unsqueeze(0)    # broadcast: (784,64) * (1,64)
    b1_t = b1 * scales                  # (64,) * (64,)
    W2_t = W2 / scales.unsqueeze(1)    # (64,10) / (64,1)
    b2_t = b2                           # unchanged

    result = torch.cat([W1_t.flatten(), b1_t, W2_t.flatten(), b2_t])

    # Verification
    dist = cosine_distance(result, weights_flat)
    if dist < 1e-6:
        raise ValueError(f"Trivial scaling transform (cosine_dist={dist:.2e})")

    return result
```

**Note on D=51850**: verify exact dimension at load time. The formula 784×64+64+64×10+10 = 50176+64+640+10 = 50890. If zoo stores additional metadata or padding, D may differ — load_zoo() must verify and store actual D.

---

## Subtask 2: Sign-flip Transform Pseudo-code (A-2)

```python
def construct_orbit_member_signflip(weights_flat, seed):
    D_in, h, D_out = 784, 64, 10
    rng = torch.Generator().manual_seed(seed)

    # Unpack (same indexing as scaling)
    i0, i1, i2 = D_in*h, D_in*h+h, D_in*h+h+h*D_out
    W1 = weights_flat[:i0].reshape(D_in, h)
    b1 = weights_flat[i0:i1]
    W2 = weights_flat[i1:i2].reshape(h, D_out)
    b2 = weights_flat[i2:]

    # Sample ±1 signs uniformly per hidden neuron
    signs = (torch.randint(0, 2, (h,), generator=rng) * 2 - 1).float()
    # signs[i] ∈ {-1, +1}, each with prob 0.5

    # Apply: flip W1 columns, b1, W2 rows simultaneously
    W1_t = W1 * signs.unsqueeze(0)    # (784,64) * (1,64)
    b1_t = b1 * signs                  # (64,)
    W2_t = W2 * signs.unsqueeze(1)    # (64,10) * (64,1)
    b2_t = b2                           # unchanged

    result = torch.cat([W1_t.flatten(), b1_t, W2_t.flatten(), b2_t])

    dist = cosine_distance(result, weights_flat)
    if dist < 1e-6:
        raise ValueError(f"Trivial sign-flip (all signs +1?): cosine_dist={dist:.2e}")

    return result
```

**Combined**: call scaling transform first with seed=seed, then signflip with seed=seed+1000 (to avoid same RNG state).

---

## Subtask 3: Bootstrap CI Algorithm (A-4)

```python
def bootstrap_ci(
    distances: list[float],
    n_boot: int = 1000,
    seed: int = 42,
    ci: float = 0.95
) -> tuple[float, float]:
    """Returns (ci_lower, ci_upper)."""
    rng = np.random.default_rng(seed)
    arr = np.array(distances)
    n = len(arr)

    boot_means = np.empty(n_boot)
    for b in range(n_boot):
        sample = rng.choice(arr, size=n, replace=True)
        boot_means[b] = sample.mean()

    alpha = (1.0 - ci) / 2.0         # 0.025 for 95% CI
    ci_lower = np.quantile(boot_means, alpha)
    ci_upper = np.quantile(boot_means, 1.0 - alpha)
    return float(ci_lower), float(ci_upper)
```

**Vectorized alternative** (faster, same result):
```python
    indices = rng.integers(0, n, size=(n_boot, n))
    boot_means = arr[indices].mean(axis=1)
    ci_lower = np.quantile(boot_means, alpha)
    ci_upper = np.quantile(boot_means, 1.0 - alpha)
```
