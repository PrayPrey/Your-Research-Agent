---
title: "Architecture: H-E1 — Orbit Diameter Characterization"
hypothesis_id: H-E1
date: 2026-08-26
---

Applied: Single-responsibility module pattern (one file per concern)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No base hypothesis, no existing codebase.

---

## File Organization

```
docs/youra_research/h-e1/code/
├── main.py               # experiment runner, results.json output
├── data_loader.py        # HuggingFace load + validation + sampling
├── orbit_construction.py # scaling / signflip / combined transforms
├── distance_metrics.py   # cosine distance, L2 distance
├── statistics.py         # aggregation, bootstrap CI, gate evaluation
└── visualization.py      # 4 figures to figures/
```

---

## Modules

### DataLoader (`code/data_loader.py`)

**Dependencies**: torch, datasets, tqdm

```python
EXPECTED_DIM = 51_850
ARCH = {"D_in": 784, "h": 64, "D_out": 10}

def load_zoo(hf_id: str = "ModelZoos/ModelZooDataset",
             config: str = "mnist-mlp",
             split: str = "train") -> list[dict]: ...
    # raises ValueError on dimension mismatch

def sample_models(zoo: list[dict],
                  n: int = 1000,
                  seed: int = 42) -> torch.Tensor:
    # returns (N, D) float32 tensor
    ...
```

---

### OrbitConstruction (`code/orbit_construction.py`)

**Dependencies**: torch

```python
def construct_orbit_member(weights_flat: torch.Tensor,
                           transform_type: str,  # "scaling"|"signflip"|"combined"
                           seed: int) -> torch.Tensor:
    # returns (D,) tensor; raises ValueError if shape mismatch or distance < 1e-6
    ...

def build_all_orbits(weights: torch.Tensor,
                     K: int = 5,
                     base_seed: int = 42) -> dict[str, torch.Tensor]:
    # returns {"scaling": (N,K,D), "signflip": (N,K,D), "combined": (N,K,D)}
    ...
```

---

### DistanceMetrics (`code/distance_metrics.py`)

**Dependencies**: torch

```python
def cosine_distance(v1: torch.Tensor, v2: torch.Tensor) -> float:
    # 1 - dot(v1/||v1||, v2/||v2||), eps=1e-8
    ...

def l2_distance(v1: torch.Tensor, v2: torch.Tensor) -> float: ...

def compute_distances(weights: torch.Tensor,
                      orbits: dict[str, torch.Tensor]
                      ) -> dict[str, dict[str, list[float]]]:
    # returns {sym_type: {"cosine": [...], "l2": [...], "max_scale": [...]}}
    ...
```

---

### Statistics (`code/statistics.py`)

**Dependencies**: numpy

```python
def aggregate(distances: list[float],
              threshold: float = 0.05,
              n_boot: int = 1000,
              seed: int = 42) -> dict: ...
    # keys: mean, std, p5, p95, frac_above, ci_lower, ci_upper

def evaluate_gate(stats: dict[str, dict]) -> dict:
    # returns {"pass": bool, "mean": float, "frac": float, "ci_lower": float}
    ...
```

---

### Visualization (`code/visualization.py`)

**Dependencies**: matplotlib, numpy

```python
FIGURES_DIR = "docs/youra_research/h-e1/figures"

def fig_gate_metrics(stats: dict[str, dict], out_dir: str = FIGURES_DIR) -> None: ...
def fig_orbit_distribution(distances: dict[str, dict], out_dir: str = FIGURES_DIR) -> None: ...
def fig_l2_vs_cosine(distances: dict[str, dict], out_dir: str = FIGURES_DIR) -> None: ...
def fig_scale_vs_diameter(distances: dict[str, dict], out_dir: str = FIGURES_DIR) -> None: ...
```

---

### Main (`code/main.py`)

**Dependencies**: all modules above, json, pathlib

```python
def run(n_models: int = 1000,
        K: int = 5,
        seed: int = 42,
        results_path: str = "docs/youra_research/h-e1/results.json") -> dict: ...

if __name__ == "__main__":
    run()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Loading | Load Schürholt zoo via HuggingFace, validate D=51850, sample N=1000 with seed | 8 | 2+1+2+3 |
| A-2 | Orbit Construction | Implement scaling, signflip, combined transforms; verify shape + nonzero distance | 12 | 3+2+4+3 |
| A-3 | Distance Computation | Cosine + L2 distances for all 15k pairs; store max_scale per scaling pair | 7 | 2+2+2+1 |
| A-4 | Statistical Aggregation | mean/std/percentiles/bootstrap CI per symmetry type; gate evaluation | 9 | 2+2+3+2 |
| A-5 | Visualization | 4 figures (gate bar, distribution histogram, L2-vs-cosine scatter, scale-vs-diameter) | 10 | 2+2+3+3 |
| A-6 | Main Runner | Wire all modules, write results.json, mechanism verification logging, gate pass/fail stdout | 7 | 1+3+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-4, A-5], Low(4-8): [A-1, A-3, A-6]
