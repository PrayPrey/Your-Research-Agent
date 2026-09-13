# Config: H-M1 (MECHANISM — property test, no training)

**Applied**: Archon KB search returned no NFN/permutation-specific config pattern (generic framework configs only, low relevance) — used standard hardcoded-dict pattern for property/inference-only tests.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: Config classes verified from base code
**Config Files Found**: `docs/youra_research/h-e1/code/config.py`
**Pattern Used**: dict (this hypothesis) — H-E1 base uses dataclass (`Config`), only `nfn_channels` field reused here

---

## Configuration (Hardcoded Dict)

Single fixed config — no hyperparameter tuning, this is a numerical property test.

```python
CONFIG = {
    # Test MLP generation (M-1)
    "test_seed": 42,
    "input_dim": 3072,        # CIFAR-10 flattened; NOT 784 (PRD assumption was wrong — see architecture notes)
    "hidden_sizes": [64, 64],
    "output_dim": 10,

    # Permutations (M-2, M-3)
    "n_perms": 10,
    "perm_seeds": list(range(10)),  # 0-9

    # NFN model loading (M-4, M-5) — inherited from H-E1
    "nfn_channels": 32,
    "checkpoint_path": "../h-e1/checkpoints/nfn_model.pt",

    # Gate thresholds (M-7, M-9)
    "dev_threshold": 1e-5,
    "corr_threshold": 0.99,

    # Output paths
    "results_path": "../results.json",
    "figure_dir": "../figures",
}
```

### Subtasks
None — MECHANISM property test, no decomposition needed (per budget).

---

## Inherited Configuration (Base Hypothesis: H-E1)

Verified from `docs/youra_research/h-e1/code/config.py` (actual `@dataclass Config`):

```python
@dataclass
class Config:
    seed: int = 0
    n_models: int = 1000
    train_frac: float = 0.8
    lr: float = 1e-3
    weight_decay: float = 1e-4
    epochs: int = 50
    batch_size: int = 32
    nfn_channels: int = 32      # <- reused in H-M1 CONFIG for model loading
    mlp_hidden_dim: int = 256
    mlp_num_layers: int = 3
    scheduler_t_max: int = 50
    scheduler_eta_min: float = 1e-6
    r2_diff_threshold: float = 0.05
```

**Note**: H-M1 only reuses `nfn_channels=32` (needed to reconstruct the NFN architecture for checkpoint loading). Training-related fields (`lr`, `epochs`, `batch_size`, etc.) are irrelevant — H-M1 does no training, inference only.

**Verified from**: `docs/youra_research/h-e1/code/config.py` (actual implementation, not `03_config.md` spec).
