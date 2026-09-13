# Configuration: H-C1

**Type:** EXISTENCE (PoC) - single fixed config, no sweeps.

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-M1, H-M2 outputs reused)
**Status:** Config classes verified from actual code in h-m1/code/config.py, h-m2/code/config.py
**Config Files Found:** h-m1/code/config.py, h-m2/code/config.py (both `@dataclass Config`, pythia-70m PoC scale)
**Pattern Used:** dataclass

**Note:** H-C1 does not retrain models — it consumes H-M2's checkpoint and TRAK/CCR scores directly. No field-name inheritance needed (different analysis, not training config); only file paths are reused (verified above).

## A-1: IFR Computation & Gate Validation [Complexity: PoC, Budget: PoC]

**Applied:** Standard PyTorch/sklearn/scipy defaults; PoC scale matches h-m1/h-m2 dataclass pattern.

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class Config:
    # Input paths (from H-M1/H-M2)
    trak_scores_path: str = "h-m2/trak_attribution_scores.npy"
    ccr_scores_path: str = "h-m1/ccr_scores.npy"
    model_checkpoint: str = "h-m2/checkpoint-final"
    output_dir: str = "h-c1/"

    # Top-attribution selection
    top_percentage: float = 0.01  # top 1% TRAK examples

    # Redundancy (k-NN)
    k_neighbors: int = 50

    # Embedding extraction
    max_seq_length: int = 512
    batch_size: int = 32

    # IFR computation
    epsilon: float = 0.01  # avoid div-by-zero in replaceability_factor

    # Statistics
    significance_level: float = 0.05  # Mann-Whitney U
    correlation_threshold: float = -0.5  # Spearman rho gate

    # PoC scope
    seed: int = 42
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Data prep | Load TRAK/CCR scores, select top 1%, label contaminated via CCR median split |
| C-1-2 | Embedding + redundancy | Extract mean-pooled embeddings (max_seq_length, batch_size), compute k-NN redundancy |
| C-1-3 | IFR + gate test | Compute IFR, Mann-Whitney U, Spearman correlation, validate both gate conditions |

## YAML Config Example

```yaml
trak_scores_path: "h-m2/trak_attribution_scores.npy"
ccr_scores_path: "h-m1/ccr_scores.npy"
model_checkpoint: "h-m2/checkpoint-final"
output_dir: "h-c1/"

top_percentage: 0.01
k_neighbors: 50
max_seq_length: 512
batch_size: 32
epsilon: 0.01

significance_level: 0.05
correlation_threshold: -0.5

seed: 42
```
