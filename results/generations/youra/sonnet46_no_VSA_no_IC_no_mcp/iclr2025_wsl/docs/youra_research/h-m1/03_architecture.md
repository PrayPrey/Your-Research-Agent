---
title: "Architecture: H-M1 — NFT Orbit Invariance Probe"
hypothesis_id: H-M1
hypothesis_type: MECHANISM
tier: FULL
date: 2026-08-26
author: Anonymous
base_hypothesis: H-E1
---

Applied: Single-responsibility module pattern (one file per concern)
Applied: Checkpoint-first pattern (load pre-trained; train only as fallback)
Applied: Incremental extension pattern (reuse base modules; add probing-specific components)
Applied: Fail-fast pre-flight assertions (v2) — zoo size ≥ 10k, CLS pooling verified before probe

## Codebase Analysis (Serena)

**Project Type**: INCREMENTAL (extends H-E1 codebase)
**Base Hypothesis Folder**: `docs/youra_research/h-e1/code/`
**Status**: Prior implementation verified from H-E1 architecture and Phase 4 validation (COMPLETED, PASS)

**Existing modules in H-E1 codebase:**
- `data_loader.py` — HuggingFace zoo loading, weight validation, model sampling; returns flat tensors + dict format
- `orbit_construction.py` — scaling/signflip/combined transforms; verified oracle correctness in H-E1
- `distance_metrics.py` — cosine distance, L2 distance; batch-compatible
- `statistics.py` — bootstrap CI, gate evaluation
- `visualization.py` — matplotlib figure generation

**Key H-E1 API patterns (from 03_architecture.md):**
```python
# data_loader.py
load_zoo(hf_id, config, split) -> list[dict]  # per-model weight dicts
sample_models(zoo, n=1000, seed=42) -> Tensor  # (N, D) flat tensors

# orbit_construction.py
build_all_orbits(weights, K=5, base_seed=42) -> {sym_type: (N,K,D)}
# H-M1 needs per-pair (not batch K) orbit member construction
```

**What H-M1 REUSES from H-E1 (no modification):**
- `data_loader.py` — zoo loading and weight validation unchanged
- `orbit_construction.py` — `construct_orbit_member()` reused directly for oracle pair construction
- `statistics.py` — bootstrap CI computation reused

**What H-M1 ADDS (new files):**
- `nft_encoder.py` — NFT checkpoint loading + batched embedding extraction
- `similarity_analysis.py` — orbit invariance probe logic (within-orbit vs. cross-orbit similarity)
- `visualization.py` (H-M1 version) — 5 new figures; different from H-E1's 4 figures

**Import paths verified from H-E1 actual implementation:**
```python
# In H-M1 code, import H-E1 modules as:
import sys
sys.path.insert(0, "../../h-e1/code")
from data_loader import load_zoo, sample_models
from orbit_construction import construct_orbit_member
from statistics import bootstrap_ci
```

---

## External Dependencies (from H-E1 actual code)

| Dependency | Source Path | API Used | Notes |
|-----------|-------------|----------|-------|
| `load_zoo` | `h-e1/code/data_loader.py` | `load_zoo(hf_id="schurholt/model_zoos_dataset", config="mnist", split="train+validation+test") -> list[dict]` | Returns per-model weight dicts; v2 corrected identifier |
| `sample_models` | `h-e1/code/data_loader.py` | `sample_models(zoo, n=1000, seed=42) -> Tensor` | Returns (N,D) flat; H-M1 needs dict format — extract after |
| `construct_orbit_member` | `h-e1/code/orbit_construction.py` | `construct_orbit_member(weights_flat, transform_type, seed)` | Takes flat tensor; returns (D,) |
| `bootstrap_ci` | `h-e1/code/statistics.py` | `aggregate(distances, threshold=0.05, n_boot=1000, seed=42) -> dict` | Returns ci_lower, ci_upper |
| NFT checkpoint | `h-e1/code/checkpoints/nft_condition_a.pt` | `torch.load(path)` | state_dict for NFT Condition A |

---

## File Organization

```
docs/youra_research/h-m1/code/
├── main.py                    # experiment runner: orchestrates probe, writes results.json
├── nft_encoder.py             # NFT checkpoint load + batched embedding extraction (NEW)
├── similarity_analysis.py     # within-orbit vs. cross-orbit similarity probe (NEW)
├── visualization.py           # 5 figures for H-M1 (NEW — different from H-E1)
└── [H-E1 modules reused via sys.path]
    # data_loader.py          → h-e1/code/data_loader.py
    # orbit_construction.py   → h-e1/code/orbit_construction.py
    # statistics.py           → h-e1/code/statistics.py
```

---

## Modules

### NftEncoder (`code/nft_encoder.py`) — NEW

**Dependencies**: torch, sys.path (H-E1 codebase for NFT class)
**Complexity**: 15 (High)

```python
CHECKPOINT_PATH = "../../h-e1/code/checkpoints/nft_condition_a.pt"
FALLBACK_CKPT = "checkpoints/nft_condition_a_hm1.pt"
EMBED_DIM = 256
BATCH_SIZE = 64

def load_nft_encoder(checkpoint_path: str = CHECKPOINT_PATH) -> torch.nn.Module:
    """Load NFT from H-E1 checkpoint; fallback to training if missing."""
    ...

def train_nft_fallback(zoo_weights, zoo_properties, epochs=100) -> torch.nn.Module:
    """Train NFT from scratch on Condition A (raw weights). Called only if checkpoint missing."""
    ...

def extract_embeddings(nft_encoder: torch.nn.Module,
                       weights_list: list[dict],
                       batch_size: int = BATCH_SIZE,
                       device: str = "cpu") -> torch.Tensor:
    """Batched embedding extraction. Returns (N, EMBED_DIM) tensor."""
    ...
```

---

### SimilarityAnalysis (`code/similarity_analysis.py`) — NEW

**Dependencies**: torch, torch.nn.functional, sys.path → orbit_construction, statistics
**Complexity**: 18 (Very High)

```python
N_ORBIT_PAIRS = 1000

def build_orbit_pairs(zoo_weights: list[dict],
                      n_pairs: int = N_ORBIT_PAIRS,
                      orbit_type: str = "scaling",
                      seed: int = 42) -> tuple[list[dict], list[dict]]:
    """Sample n_pairs base models; construct oracle orbit members. Returns (base_list, orbit_list)."""
    ...

def build_cross_orbit_pairs(zoo_weights: list[dict],
                             zoo_properties: torch.Tensor,
                             base_indices: list[int],
                             seed: int = 42) -> tuple[list[dict], list[int]]:
    """For each base model, sample j ≠ i from same test_accuracy decile. Returns (cross_list, cross_idx)."""
    ...

def compute_similarity_vectors(
    emb_base: torch.Tensor,   # (N, D)
    emb_orbit: torch.Tensor,  # (N, D)
    emb_cross: torch.Tensor,  # (N, D)
) -> dict[str, torch.Tensor]:
    """Returns {'within_sim': (N,), 'cross_sim': (N,), 'gap': (N,)}."""
    ...

def probe_orbit_invariance(
    nft_encoder: torch.nn.Module,
    zoo_weights: list[dict],
    zoo_properties: torch.Tensor,
    orbit_type: str,  # "scaling" | "signflip"
    n_pairs: int = N_ORBIT_PAIRS,
    seed: int = 42,
) -> dict:
    """Full probe for one orbit type. Returns {within_sim, cross_sim, gap, gate_pass, ci_lower, stats}."""
    ...

def evaluate_gate(results: dict[str, dict]) -> dict:
    """Aggregate across orbit types; return overall PASS/FAIL + per-type results.
    v2 asymmetric: scaling PASS required; sign-flip FAIL → EXPLORE (non-blocking)."""
    ...

def verify_signflip_equiv(original_dict: dict, orbit_dict: dict,
                          n_test: int = 100, tol: float = 1e-4) -> bool:
    """v2 NEW: Verify sign-flip orbit pair is functionally equivalent on random inputs.
    Returns True if all n_test random inputs produce |Δ output| < tol."""
    ...
```

---

### Visualization (`code/visualization.py`) — NEW (H-M1 version)

**Dependencies**: matplotlib, numpy, sklearn.decomposition.PCA
**Complexity**: 12 (Medium)

```python
FIGURES_DIR = "docs/youra_research/h-m1/figures"

def fig_gate_metrics(results: dict[str, dict], out_dir: str = FIGURES_DIR) -> None:
    """Grouped bar chart: mean within_sim vs. cross_sim per orbit type with CI error bars."""
    ...

def fig_sim_distributions(results: dict[str, dict], out_dir: str = FIGURES_DIR) -> None:
    """Overlapping histograms: within_sim vs. cross_sim per orbit type (2 subplots)."""
    ...

def fig_per_model_scatter(results: dict[str, dict],
                          zoo_properties: torch.Tensor,
                          base_indices: list,
                          out_dir: str = FIGURES_DIR) -> None:
    """Scatter: within-orbit similarity vs. model test_accuracy."""
    ...

def fig_embedding_pca(emb_base: torch.Tensor,
                      emb_orbit: torch.Tensor,
                      out_dir: str = FIGURES_DIR) -> None:
    """2D PCA of base + orbit embeddings, colored by orbit membership (50 pairs shown)."""
    ...

def fig_similarity_heatmap(emb_base: torch.Tensor,
                            emb_orbit: torch.Tensor,
                            out_dir: str = FIGURES_DIR) -> None:
    """N×N cosine similarity matrix for 50 models (25 base + 25 orbit members), sorted by orbit."""
    ...
```

---

### Main (`code/main.py`)

**Dependencies**: all modules above, json, pathlib
**Complexity**: 10 (Medium)

```python
def run(n_orbit_pairs: int = 1000,
        seed: int = 42,
        checkpoint_path: str = CHECKPOINT_PATH,
        results_path: str = "docs/youra_research/h-m1/results.json",
        device: str = "cpu") -> dict:
    """
    1. Load zoo + NFT checkpoint
    2. Probe scaling orbit invariance
    3. Probe sign-flip orbit invariance
    4. Evaluate combined gate
    5. Generate 5 figures
    6. Write results.json
    7. Print gate PASS/FAIL
    """
    ...

if __name__ == "__main__":
    run()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown (Module+Deps+Algo+Integration) |
|----|------|-------------|------------|------------------------------------------|
| A-1 | Zoo + Properties Load | Load full Schürholt zoo (50k models) via H-E1 data_loader; extract per-layer weight dicts + property matrix (N×3); verify D=51850 | 8 | 2+1+2+3 |
| A-2 | NFT Encoder Module | Implement `nft_encoder.py`: checkpoint load from H-E1, batched embedding extraction, fallback training path | 15 | 4+3+4+4 |
| A-3 | Oracle Orbit Pair Construction | Implement `build_orbit_pairs()` in similarity_analysis.py: sample 1,000 base models, construct scaling + sign-flip oracle orbit members via H-E1 construct_orbit_member | 12 | 3+2+4+3 |
| A-4 | Cross-Orbit Pair Sampling | Implement `build_cross_orbit_pairs()`: decile-bucket test_accuracy, sample j≠i from same decile per base model, seed-controlled | 11 | 3+2+3+3 |
| A-5 | Orbit Invariance Probe | Implement `probe_orbit_invariance()` and `compute_similarity_vectors()`: extract embeddings for base/orbit/cross, compute within_sim / cross_sim / gap | 18 | 5+3+5+5 |
| A-6 | Statistical Evaluation | Implement `evaluate_gate()`: bootstrap 95% CI on gap (n_boot=1000, scipy.stats.bootstrap), PASS/FAIL evaluation, per-type + combined reporting | 13 | 3+2+4+4 |
| A-7 | Gate Metrics Figure | `fig_gate_metrics()`: grouped bar chart, mean within_sim vs. cross_sim with CI error bars per orbit type | 8 | 2+1+3+2 |
| A-8 | Diagnostic Figures | `fig_sim_distributions()` + `fig_per_model_scatter()`: histogram overlap + accuracy scatter (2 figures) | 9 | 2+2+3+2 |
| A-9 | Embedding Visualization | `fig_embedding_pca()` + `fig_similarity_heatmap()`: PCA of embeddings + NxN cosine similarity heatmap (2 figures) | 11 | 3+2+3+3 |
| A-10 | Main Runner | `main.py`: orchestrate all steps, mechanism verification logging, results.json output, gate PASS/FAIL stdout | 9 | 2+3+2+2 |

**Complexity Distribution:**
- Very High (18–20): [A-5]
- High (14–17): [A-2]
- Medium (9–13): [A-3, A-4, A-6, A-8, A-9, A-10]
- Low (4–8): [A-1, A-7]

**Epic Count: 10** (within FULL tier epic range 6–12 ✓)
