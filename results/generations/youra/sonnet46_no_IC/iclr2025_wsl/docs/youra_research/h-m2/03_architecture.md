# Architecture: H-M2
# Scale vs Permutation Equivariance Ablation in EquiSSL

Applied: standard-DL-experiment-pipeline (no relevant Archon KB patterns for weight-space domain)

---

## Codebase Analysis (Serena)

**Project Type**: incremental (H-M1 extension)
**Status**: Patterns verified from actual H-M1 code
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Findings**:
H-M1 has the following actual modules (verified from filesystem):
- `code/config.py` — EquiSSLPermConfig, LinearProbeConfig, PathConfig, ExperimentConfig dataclasses
- `code/run_experiment.py` — main pipeline orchestrator
- `code/data/` — real_vit_zoo_dataset.py (RealViTZooDataset + vit_checkpoint_to_graph)
- `code/models/equissl_encoder.py` — EquiSSLEncoder(symmetry='monomial'|'permutation')
- `code/models/equissl_objective.py` — EquiSSLObjective (NT-Xent + MSE)
- `code/models/graph_decoder.py` — GraphDecoder for reconstruction
- `code/training/train_equi_perm.py` — train_equi_perm(cfg, seed, path_cfg)
- `code/evaluation/extract_embeddings.py` — extract_graph_embeddings, extract_all_embeddings
- `code/evaluation/linear_probe.py` — evaluate_linear_probe, paired_ttest, evaluate_gate
- `code/evaluation/figures.py` — plot_r2_bar_chart, plot_tsne_comparison, generate_all_figures
- `code/evaluation/mmd_eval.py` — MMD ratio computation

**H-M2 Reuse Strategy**: Maximum reuse from h-m1/code/. H-M2 adds only:
1. `h-m2/run_hm2.py` — thin orchestration script for ablation
2. `h-m2/code/evaluation/delta_r2_analysis.py` — ΔR² statistics + ablation figures
3. Updated PathConfig pointing to h-m2 outputs

**Key verified import paths**:
- `sys.path.insert(0, 'docs/youra_research/h-m1/code')` then import directly
- Models: `from models.equissl_encoder import EquiSSLEncoder`
- Training: `from training.train_equi_perm import train_equi_perm`
- Evaluation: `from evaluation.extract_embeddings import extract_graph_embeddings`
- Evaluation: `from evaluation.linear_probe import evaluate_linear_probe, paired_ttest`
- Data: `from data.real_vit_zoo_dataset import RealViTZooDataset`

---

## External Dependencies

### Module Paths (From Actual H-M1 Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| EquiSSLEncoder | `from models.equissl_encoder import EquiSSLEncoder` | `h-m1/code/models/equissl_encoder.py` |
| EquiSSLObjective | `from models.equissl_objective import EquiSSLObjective` | `h-m1/code/models/equissl_objective.py` |
| train_equi_perm | `from training.train_equi_perm import train_equi_perm` | `h-m1/code/training/train_equi_perm.py` |
| RealViTZooDataset | `from data.real_vit_zoo_dataset import RealViTZooDataset` | `h-m1/code/data/real_vit_zoo_dataset.py` |
| extract_graph_embeddings | `from evaluation.extract_embeddings import extract_graph_embeddings` | `h-m1/code/evaluation/extract_embeddings.py` |
| evaluate_linear_probe | `from evaluation.linear_probe import evaluate_linear_probe` | `h-m1/code/evaluation/linear_probe.py` |
| compute_mmd_ratio | `from evaluation.mmd_eval import compute_mmd_ratio` | `h-m1/code/evaluation/mmd_eval.py` |
| FigureGenerator | `from evaluation.figures import generate_all_figures` | `h-m1/code/evaluation/figures.py` |
| ExperimentConfig | `from config import ExperimentConfig, PathConfig` | `h-m1/code/config.py` |

**Verified from**: `docs/youra_research/h-m1/code/` (actual filesystem listing)

---

## Module Definitions

### H-M2 Config Override (`h-m2/code/config_hm2.py`)

**Dependencies**: h-m1/code/config.py

```python
from dataclasses import dataclass, field
from typing import List
import sys
sys.path.insert(0, 'docs/youra_research/h-m1/code')
from config import EquiSSLPermConfig, LinearProbeConfig, ExperimentConfig

@dataclass
class HM2PathConfig:
    """H-M2-specific paths, inheriting h-m1 structure."""
    # H-E1 checkpoints (EquiSSL, scale+perm)
    he1_checkpoint_dir: str = "docs/youra_research/h-e1/checkpoints"
    # H-M1 checkpoints (EquiSSL-perm seed 0)
    hm1_checkpoint_dir: str = "docs/youra_research/h-m1/checkpoints"
    # H-M2 outputs
    checkpoint_dir: str = "docs/youra_research/h-m2/checkpoints"
    results_dir: str = "docs/youra_research/h-m2/results"
    figures_dir: str = "docs/youra_research/h-m2/figures"
    # Shared datasets (reuse H-M1 cache)
    vit_zoo_root: str = "data/vitzoo"
    multizoo_root: str = "data/multizoo"

@dataclass
class AblationConfig:
    """H-M2 ablation-specific settings."""
    experiment_id: str = "h-m2"
    ablation_mode: bool = True
    seeds: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])
    gate_threshold: float = 0.05   # ΔR² SHOULD_WORK threshold
    gate_type: str = "SHOULD_WORK"
    # Pre-observed seed 0 result from H-M1
    seed0_equissl_r2: float = 0.2098
    seed0_equi_perm_r2: float = 0.2305
```

---

### DeltaR2Analyzer (`h-m2/code/evaluation/delta_r2_analysis.py`)

**Dependencies**: scipy, numpy

```python
import numpy as np
from scipy import stats

def compute_delta_r2_stats(r2_scale: list, r2_perm: list) -> dict:
    """ΔR² statistics over 5 seeds."""
    ...

def evaluate_should_work_gate(delta_r2_mean: float, gate_threshold: float = 0.05) -> str:
    """Returns 'PASS' or 'DOCUMENT'."""
    ...

def generate_ablation_figures(results: dict, output_dir: str) -> None:
    """4 figures specific to H-M2 ablation."""
    ...
```

---

### RunHM2 (`h-m2/run_hm2.py`)

**Dependencies**: all h-m1 modules + delta_r2_analysis

```python
def main():
    """H-M2 ablation pipeline:
    1. Train EquiSSL-perm seeds 1-4 (reuse h-m1 train_equi_perm)
    2. Extract embeddings: EquiSSL (h-e1 ckpts) + EquiSSL-perm (seed0 from h-m1, seeds1-4 new)
    3. Linear probe (RidgeCV, paired 80/20 splits per seed)
    4. ΔR² statistics + paired t-test
    5. MMD ratio comparison (secondary)
    6. 4 figures
    7. 04_validation.md
    """
```

---

## File Organization

```
h-m2/
├── run_hm2.py               ← main script (thin wrapper over h-m1 modules)
├── checkpoints/
│   └── equi_perm_seed{1..4}.pt
├── results/
│   └── hm2_results.json
├── figures/
│   ├── gate_metrics_bar.png
│   ├── delta_r2_distribution.png
│   ├── tsne_2x2_panel.png
│   └── ablation_ladder.png
└── code/
    ├── config_hm2.py
    └── evaluation/
        └── delta_r2_analysis.py

Reused from H-M1 (direct import, no copy):
- h-m1/code/config.py
- h-m1/code/models/equissl_encoder.py
- h-m1/code/training/train_equi_perm.py
- h-m1/code/data/real_vit_zoo_dataset.py
- h-m1/code/evaluation/extract_embeddings.py
- h-m1/code/evaluation/linear_probe.py
- h-m1/code/evaluation/mmd_eval.py
- h-m1/code/evaluation/figures.py
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Config | H-M2 folder structure, config_hm2.py, path setup, verify h-m1 imports work | 5 | 1+1+1+2 |
| A-2 | EquiSSL-perm Training (Seeds 1-4) | Call h-m1 train_equi_perm for seeds 1,2,3,4 with scale_augment=False; save to h-m2/checkpoints/ | 12 | 3+3+3+3 |
| A-3 | Embedding Extraction (Both Models) | Extract EquiSSL embeddings (5 seeds from h-e1 ckpts) + EquiSSL-perm (seed0 from h-m1, seeds1-4 new); paired same ViT models | 13 | 3+3+4+3 |
| A-4 | Paired Linear Probe Evaluation | RidgeCV per seed with identical train/test splits for both models; collect per-seed R² | 10 | 2+2+3+3 |
| A-5 | ΔR² Statistical Analysis | delta_r2_analysis.py: mean/std/95%CI, ttest_1samp, SHOULD_WORK gate evaluation | 11 | 2+2+4+3 |
| A-6 | MMD Ratio Comparison | Reuse h-m1 mmd_eval; compute for EquiSSL vs EquiSSL-perm on high/low accuracy ViT splits | 8 | 2+2+2+2 |
| A-7 | Ablation Visualization (4 Figures) | Bar chart, ΔR² distribution, t-SNE 2×2, ablation ladder; save to h-m2/figures/ | 12 | 3+2+4+3 |
| A-8 | Results Report & Orchestration | run_hm2.py main pipeline, write 04_validation.md with R² table/stats/gate/figures | 9 | 2+2+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-4, A-5, A-7, A-8], Low(4-8): [A-1, A-6]

**Total Complexity**: 80
**Task Count**: 8 (within MECHANISM 6-12 range ✓)
