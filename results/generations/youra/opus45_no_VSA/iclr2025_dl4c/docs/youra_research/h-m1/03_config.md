# Configuration: H-M1 (MECHANISM)

**Type**: MECHANISM (not PoC) — full config with hyperparameters, no ablation grid needed (single fixed design per PRD).

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1) referenced, but `h-e1/code/config*.py` does not exist on disk (confirmed via architecture doc's prior Serena glob — 0 files found).
**Status**: Green-field config design for h-m1. H-E1 model *paths* (not config classes) are consumed as external artifacts (`h-e1/models/ce_model/`, `h-e1/models/rl_model/`) — no config inheritance applies.
**Config Files Found**: None
**Pattern Used**: dataclass (matches architecture.md spec exactly)

---

## M-1: Config + Model Loading

**Applied**: Standard PyTorch/HF dataclass config pattern (no direct MI-config KB match found; used architecture.md spec as source of truth)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field

@dataclass
class MINEConfig:
    # H-E1 model artifacts (external dependency)
    ce_model_path: str = "h-e1/models/ce_model"
    rl_model_path: str = "h-e1/models/rl_model"
    tokenizer_id: str = "Salesforce/codet5p-220m"

    # Embedding / MINE architecture
    embed_dim: int = 256
    hidden_dim: int = 512

    # Refinement trace extraction
    refine_k: int = 3
    seeds: list = field(default_factory=lambda: [42, 43, 44])

    # MINE training
    mine_lr: float = 0.001
    mine_batch_size: int = 128
    mine_iters: int = 5000
    ema_weight: float = 0.01

    # Statistical testing
    n_permutations: int = 10000

    # Output paths
    results_json: str = "h-m1/results.json"
    results_csv: str = "h-m1/results.csv"
    figures_dir: str = "h-m1/figures/"
```

No subtasks (budget: 0).

---

## Field Notes (Non-Standard Only)

- `ema_weight=0.01`: MINE bias-correction EMA decay per Phase 2C spec / gtegner/mine-pytorch reference implementation — not a PyTorch default, required for stable DV-bound gradient estimates.
- `n_permutations=10000`: fixed per PRD success criteria (p<0.05 test power), not tunable.
- `embed_dim=256`: projected dim, decoupled from CodeT5+-220M's native hidden size via `Projector` module (see architecture.md `embed.py`).

All other fields use conventional defaults (Adam lr=1e-3, batch=128) — no rationale needed.

---

## Usage Example (Phase 4 copy-paste)

```python
cfg = MINEConfig()
# override for quick smoke test:
# cfg = MINEConfig(mine_iters=100, n_permutations=100)
```
