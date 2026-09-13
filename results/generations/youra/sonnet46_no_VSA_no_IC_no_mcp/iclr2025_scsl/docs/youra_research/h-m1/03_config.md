# Config: H-M1
# SimCLR Background-Replacement Augmentation — Mechanism Hypothesis

---
stepsCompleted:
  - config
hypothesis_id: h-m1
hypothesis_type: MECHANISM
tier: FULL
generated_at: "2026-08-26"
---

Applied: frozen-dataclass experiment config pattern
Applied: SimCLR linear LR scaling rule (Chen et al. 2020)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field experiment — no existing codebase analyzed
**Config Files Found**: None — new config design
**Pattern Used**: dataclass (frozen=False, single file `config.py`)

---

## Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-E1-1 | ExperimentConfig dataclass | All path, training, dataset hyperparameters with defaults |
| C-E4-1 | Hyperparameter rationale | lr, batch, epochs, τ, momentum, weight_decay sources |
| C-E8-1 | Visualization config | Figure sizes, DPI, colors, output paths, rcParams |
| C-E7-1 | Statistical test config | α, effect size thresholds, confound threshold, alternative |

---

## C-E1-1: ExperimentConfig Dataclass [Complexity: 13, Budget: 1]

**Applied**: frozen-dataclass experiment config pattern

### Configuration

```python
# config.py
from dataclasses import dataclass, field
from typing import List


@dataclass
class ExperimentConfig:
    # --- Paths ---
    data_root: str = "./data"
    waterbirds_root: str = "./data"                          # wilds downloads here
    cub_root: str = "./data/CUB_200_2011"
    places365_root: str = "./data/places365"
    checkpoint_dir: str = "./checkpoints/h-m1"
    results_dir: str = "./results/h-m1"
    figures_dir: str = "./docs/youra_research/h-m1/figures"

    # --- Dataset ---
    image_size: int = 224
    # Preprocessing: Resize(256) → CenterCrop(224) → Normalize(ImageNet)
    normalize_mean: List[float] = field(default_factory=lambda: [0.485, 0.456, 0.406])
    normalize_std: List[float] = field(default_factory=lambda: [0.229, 0.224, 0.225])
    n_places365: int = 10000                                 # pool size for background replacement

    # --- Training ---
    seeds: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])
    epochs: int = 50
    batch_size: int = 256
    lr: float = 0.03                                         # 0.3 × batch/1024 = 0.3 × 256/1024
    momentum: float = 0.9
    weight_decay: float = 1e-4
    temperature: float = 0.5                                 # Chen et al. 2020, Table B.8

    # --- Model ---
    proj_hidden_dim: int = 2048
    proj_out_dim: int = 128
    backbone_out_dim: int = 2048                             # ResNet-50 global avg pool

    # --- Linear Probe ---
    probe_C: float = 1.0
    probe_max_iter: int = 1000
    probe_solver: str = "lbfgs"

    # --- Mechanism Verification ---
    mechanism_pixel_diff_threshold: float = 0.05            # verify_mechanism_activated

    # --- Device ---
    device: str = "cuda"

    # --- Collapse Detection ---
    collapse_task_acc_threshold: float = 0.53               # below → mark seed FAILED

    def checkpoint_path(self, condition: str, seed: int) -> str:
        return f"{self.checkpoint_dir}/{condition}_seed{seed}_epoch{self.epochs}.pt"

    def result_path(self, condition: str, seed: int) -> str:
        return f"{self.results_dir}/{condition}_seed{seed}.json"
```

**Validation notes**:
- `condition` must be one of `{"original", "no_background"}`
- `cub_root` must contain `segmentations/` subdirectory before running NoBackground condition
- `n_places365` must be ≤ total Places365-Standard small split (~1.8M); 10K is safe

---

## C-E4-1: Hyperparameter Rationale [Complexity: 13, Budget: 1]

**Applied**: SimCLR linear LR scaling rule (Chen et al. 2020)

### Hyperparameter Table

| Param | Value | Source | Sensitivity |
|-------|-------|--------|-------------|
| `lr` | 0.03 | Linear scaling: 0.3 × 256/1024 (Chen et al. 2020 §B) | Medium — scales with batch; do not tune independently |
| `batch_size` | 256 | Hardware constraint (16GB VRAM, ResNet-50) | Low for this range; smaller batch needs LR adjustment |
| `epochs` | 50 | Sufficient for convergence signal on 4,795-image dataset; Chen et al. use 200–1000 on ImageNet | High on smaller data — 50 is PoC budget; increase to 200 if signal weak |
| `temperature` | 0.5 | Chen et al. 2020, Table B.8 optimal for SimCLR | Medium — 0.1 collapses, 1.0 under-trains; 0.5 is canonical |
| `momentum` | 0.9 | Standard SGD default (Chen et al. 2020) | Low |
| `weight_decay` | 1e-4 | Chen et al. 2020 SGD config | Low |
| `seeds` | [0,1,2,3,4] | Paired design, 5 seeds for t-test df=4 | Fixed — fewer seeds lose statistical power |
| `n_places365` | 10000 | Diversity floor; diminishing returns above 50K | Low — 10K provides adequate diversity for 4,795 images |
| `probe_C` | 1.0 | sklearn LogisticRegression default | Low for linear probe |
| `probe_max_iter` | 1000 | Ensures convergence for 2048-dim features | Low |

**When to change**:
- `epochs`: increase to 200 if task_probe_acc < 0.60 at epoch 50 (underfitting signal)
- `lr`: recompute as `0.3 × batch_size / 1024` if batch_size changes
- `temperature`: keep at 0.5 unless ablation is specifically requested

---

## C-E8-1: Visualization Config [Complexity: 10, Budget: 1]

**Applied**: Standard matplotlib publication config pattern

### Configuration

```python
# src/visualization/figures.py — top of file

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Global rcParams
RCPARAMS = {
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "font.size": 12,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "legend.fontsize": 10,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.facecolor": "white",
    "axes.spines.top": False,
    "axes.spines.right": False,
}

# Color palette — condition assignment
COLORS = {
    "original": "#2196F3",       # blue
    "no_background": "#FF5722",  # orange
}

# Figure sizes (width, height) in inches
FIG_SIZES = {
    "gate_metrics_comparison": (8, 5),    # FR-6.1: bar chart
    "spurious_task_scatter": (6, 6),      # FR-6.2: scatter (square)
    "paired_ratio_plot": (6, 5),          # FR-6.3: paired lines
    "background_replacement_examples": (14, 4),  # FR-6.4: qualitative grid
}

# Output filenames (relative to figures_dir from ExperimentConfig)
FIG_FILENAMES = {
    "gate_metrics_comparison": "gate_metrics_comparison.png",
    "spurious_task_scatter": "spurious_task_scatter.png",
    "paired_ratio_plot": "paired_ratio_plot.png",
    "background_replacement_examples": "background_replacement_examples.png",
}

N_EXAMPLE_IMAGES = 5   # FR-6.4: show 5 original + 5 replaced
```

**Usage pattern in each figure function**:
```python
def plot_gate_metrics_comparison(results: dict, out_dir: str) -> None:
    plt.rcParams.update(RCPARAMS)
    fig, ax = plt.subplots(figsize=FIG_SIZES["gate_metrics_comparison"])
    # ... plot logic ...
    fig.savefig(f"{out_dir}/{FIG_FILENAMES['gate_metrics_comparison']}", bbox_inches="tight")
    plt.close(fig)
```

---

## C-E7-1: Statistical Analysis Config [Complexity: 9, Budget: 1]

**Applied**: Standard frequentist hypothesis testing config pattern

### Configuration

```python
# src/evaluation/stats.py — top of file

# Significance threshold
ALPHA = 0.05                    # one-sided paired t-test rejection threshold

# Effect size thresholds (Cohen's d, for reporting only)
COHEN_D_SMALL = 0.2
COHEN_D_MEDIUM = 0.5
COHEN_D_LARGE = 0.8

# Confound threshold
CONFOUND_THRESHOLD = 0.05       # |task_acc_diff| > this → INCONCLUSIVE

# Primary effect threshold
RATIO_DIFF_THRESHOLD = 0.05     # mean(ratio_original) - mean(ratio_no_background) ≥ this → PASS

# Paired t-test direction
ALTERNATIVE = "less"            # ratios_no_background < ratios_original

# Collapse detection (used in trainer, referenced here for consistency)
COLLAPSE_TASK_ACC_THRESHOLD = 0.53   # random chance for binary = 0.50; 0.53 = minimal signal
```

### Verdict Logic

```python
def compute_verdict(
    ratio_diff_mean: float,
    p_value: float,
    task_acc_diff: float,
) -> str:
    if task_acc_diff > CONFOUND_THRESHOLD:
        return "INCONCLUSIVE"
    if ratio_diff_mean >= RATIO_DIFF_THRESHOLD and p_value < ALPHA:
        return "CONFIRMED"
    return "FAIL"
```

**Validation notes**:
- `alternative='less'` in `scipy.stats.ttest_rel` means H1: no_background ratios < original ratios
- Cohen's d is reported descriptively only; not used in verdict logic
- `CONFOUND_THRESHOLD = 0.05` matches the 5% task accuracy tolerance in FR-5.2
- With n=5 seeds, df=4; minimum detectable effect at α=0.05 (one-sided) requires large Cohen's d (~1.0); interpret borderline p-values cautiously

**When to change**:
- `ALPHA`: keep at 0.05; lowering to 0.01 risks false negatives with n=5
- `RATIO_DIFF_THRESHOLD`: 0.05 is specified by PRD success criteria; do not lower
- `CONFOUND_THRESHOLD`: matches PRD FR-5.2; do not change without updating hypothesis
