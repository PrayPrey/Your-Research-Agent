# Architecture: H-M1
# SimCLR Background-Replacement Augmentation — Mechanism Hypothesis

---
stepsCompleted:
  - architecture
hypothesis_id: h-m1
hypothesis_type: MECHANISM
tier: FULL
generated_at: "2026-08-26"
---

Applied: SimCLR two-condition ablation with causal isolation pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field experiment — no existing codebase analyzed
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No prior code to reuse.

---

## File Organization

```
code/
  src/
    data/
      waterbirds.py         # Waterbirds WILDS loading + mask alignment
      places365_pool.py     # Places365 background pool loader
    augmentation/
      simclr_augment.py     # Standard SimCLR augmentation pipeline
      background_replace.py # BackgroundReplacementTransform + verify_mechanism_activated
    models/
      simclr.py             # ResNet-50 backbone + projection head + SimCLR wrapper
    training/
      loss.py               # NT-Xent loss
      trainer.py            # Training loop (single condition, single seed)
    evaluation/
      probes.py             # Feature extraction + linear probes (spurious + task)
      stats.py              # Paired t-test, Cohen's d, confound check
    visualization/
      figures.py            # All 4 required figures
  run_experiment.py         # Single-seed entrypoint (--seed N --condition {original|no_background})
  aggregate_results.py      # Multi-seed aggregation + statistical analysis
  config.py                 # Fixed experiment config (dataclass)
```

---

## Modules

### WaterbirdsDataset (`src/data/waterbirds.py`)

**Dependencies**: wilds, torchvision, PIL, numpy

```python
class WaterbirdsDataset:
    def __init__(self, root: str, split: str, transform=None): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> tuple[Tensor, int, int, int]: ...
    # returns: (image, bird_label, background_label, group_id)

def load_cub_mask(cub_root: str, cub_image_id: str) -> Image.Image: ...
# Returns binary PIL Image: 1=bird foreground, 0=background

def build_mask_index(waterbirds_metadata_csv: str, cub_root: str) -> dict[int, str]: ...
# Maps Waterbirds dataset index -> CUB segmentation mask file path
```

---

### Places365Pool (`src/data/places365_pool.py`)

**Dependencies**: torchvision, PIL

```python
class Places365Pool:
    def __init__(self, root: str, n_images: int = 10000): ...
    def sample(self) -> Image.Image: ...
    # Returns random PIL Image from pre-loaded pool
```

---

### SimCLRAugmentation (`src/augmentation/simclr_augment.py`)

**Dependencies**: torchvision.transforms

```python
def get_simclr_transform(image_size: int = 224) -> transforms.Compose: ...
# Returns standard SimCLR augmentation pipeline (crop, jitter, grayscale, blur, flip, normalize)
```

---

### BackgroundReplacementTransform (`src/augmentation/background_replace.py`)

**Dependencies**: PIL, numpy, Places365Pool, simclr_augment

```python
class BackgroundReplacementTransform:
    def __init__(self, places_pool: Places365Pool, simclr_transform): ...
    def __call__(self, image: Image.Image, seg_mask: Image.Image) -> tuple[Tensor, Tensor]: ...
    # Each call samples two independent Places365 backgrounds (view1, view2)

def verify_mechanism_activated(
    augmented_view: Tensor,
    original_image: Tensor,
    seg_mask: Tensor,
    threshold: float = 0.05,
) -> dict: ...
# Asserts pixel_diff > threshold in background region; raises if not
```

---

### SimCLRModel (`src/models/simclr.py`)

**Dependencies**: torch, torchvision.models

```python
class ProjectionHead(nn.Module):
    def __init__(self, in_dim: int = 2048, hidden_dim: int = 2048, out_dim: int = 128): ...
    def forward(self, x: Tensor) -> Tensor: ...  # L2-normalized output

class SimCLRModel(nn.Module):
    def __init__(self): ...
    def forward(self, x: Tensor) -> tuple[Tensor, Tensor]: ...
    # Returns (backbone_features, projected_features)
    def get_backbone(self) -> nn.Module: ...
```

---

### NTXentLoss (`src/training/loss.py`)

**Dependencies**: torch

```python
class NTXentLoss(nn.Module):
    def __init__(self, temperature: float = 0.5): ...
    def forward(self, z1: Tensor, z2: Tensor) -> Tensor: ...
    # z1, z2: (N, D) L2-normalized projections
```

---

### SimCLRTrainer (`src/training/trainer.py`)

**Dependencies**: torch, SimCLRModel, NTXentLoss, WaterbirdsDataset, augmentation

```python
class SimCLRTrainer:
    def __init__(self, config: ExperimentConfig, condition: str, seed: int): ...
    def train(self) -> str: ...
    # Returns checkpoint path; logs per-epoch loss
    def _set_seed(self, seed: int) -> None: ...
    def _verify_mechanism(self, loader) -> None: ...
    # Called before NoBackground training; halts on failure
```

---

### LinearProbeEvaluator (`src/evaluation/probes.py`)

**Dependencies**: torch, sklearn, numpy

```python
def extract_features(
    backbone: nn.Module,
    dataset: WaterbirdsDataset,
    device: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]: ...
# Returns: (features N×2048, bird_labels, background_labels)

def train_and_eval_probe(
    train_features: np.ndarray,
    train_labels: np.ndarray,
    test_features: np.ndarray,
    test_labels: np.ndarray,
) -> float: ...
# LogisticRegression(C=1.0, max_iter=1000, solver='lbfgs')

def run_probes(
    checkpoint_path: str,
    waterbirds_root: str,
    device: str,
) -> dict: ...
# Returns: {spurious_probe_acc, task_probe_acc, ratio}
```

---

### StatisticalAnalysis (`src/evaluation/stats.py`)

**Dependencies**: scipy, numpy

```python
def paired_ttest(
    ratios_no_bg: list[float],
    ratios_original: list[float],
) -> dict: ...
# Returns: {t_stat, p_value, cohen_d}

def confound_check(
    task_accs_no_bg: list[float],
    task_accs_original: list[float],
    threshold: float = 0.05,
) -> dict: ...
# Returns: {task_acc_diff, is_confounded, verdict}

def compute_verdict(
    ratio_diff_mean: float,
    p_value: float,
    task_acc_diff: float,
) -> str: ...
# Returns: "CONFIRMED" | "INCONCLUSIVE" | "FAIL"
```

---

### Figures (`src/visualization/figures.py`)

**Dependencies**: matplotlib, numpy

```python
def plot_gate_metrics_comparison(results: dict, out_dir: str) -> None: ...
# FR-6.1: bar chart spurious/task acc per condition ± std

def plot_spurious_task_scatter(results: dict, out_dir: str) -> None: ...
# FR-6.2: scatter x=task_acc, y=spurious_acc, 10 points, colored by condition

def plot_paired_ratio(results: dict, out_dir: str) -> None: ...
# FR-6.3: lines connecting original→no_background ratio per seed

def plot_background_replacement_examples(
    waterbirds_dataset,
    bg_transform: BackgroundReplacementTransform,
    out_dir: str,
    n: int = 5,
) -> None: ...
# FR-6.4: qualitative grid original vs replaced
```

---

### ExperimentConfig (`config.py`)

**Dependencies**: dataclasses

```python
@dataclass
class ExperimentConfig:
    # Paths
    data_root: str = "./data"
    cub_root: str = "./data/CUB_200_2011"
    checkpoint_dir: str = "./checkpoints/h-m1"
    results_dir: str = "./results/h-m1"
    figures_dir: str = "./docs/youra_research/h-m1/figures"
    # Training
    seeds: list[int] = field(default_factory=lambda: [0,1,2,3,4])
    epochs: int = 50
    batch_size: int = 256
    lr: float = 0.03
    momentum: float = 0.9
    weight_decay: float = 1e-4
    temperature: float = 0.5
    image_size: int = 224
    # Places365 pool
    n_places365: int = 10000
    # Device
    device: str = "cuda"
```

---

### Entrypoints

**`run_experiment.py`**
```python
# CLI: python run_experiment.py --seed 0 --condition original
# CLI: python run_experiment.py --seed 0 --condition no_background
def main(seed: int, condition: str) -> None: ...
# 1. Load config, set seeds
# 2. Build dataset + augmentation for condition
# 3. Train SimCLR (SimCLRTrainer)
# 4. Run linear probes (run_probes)
# 5. Save per-seed JSON: results/h-m1/{condition}_seed{seed}.json
```

**`aggregate_results.py`**
```python
# CLI: python aggregate_results.py
def main() -> None: ...
# 1. Load all per-seed JSONs
# 2. Run paired t-test + confound check (stats.py)
# 3. Save probe_results.json
# 4. Generate all 4 figures (figures.py)
# 5. Print summary table
```

---

## Epic Tasks

| ID | Task | Description | Files | Complexity | Breakdown |
|----|------|-------------|-------|------------|-----------|
| E1 | Data Pipeline + Mask Alignment | Load Waterbirds via WILDS; build index mapping Waterbirds indices to CUB mask paths; handle missing mask errors. Mask alignment from metadata.csv is the core complexity. | `src/data/waterbirds.py`, `config.py` | 13 | 3+3+3+4 |
| E2 | Places365 Background Pool | Load and cache N=10,000 Places365 images as PIL pool; handle download/disk failures; expose sample() API. | `src/data/places365_pool.py` | 7 | 2+2+1+2 |
| E3 | Background Replacement Augmentation | Implement BackgroundReplacementTransform (pixel-level mask compositing, two independent backgrounds per call) and verify_mechanism_activated (asserts pixel_diff > 0.05). This is the novel mechanism. | `src/augmentation/background_replace.py`, `src/augmentation/simclr_augment.py` | 16 | 4+4+4+4 |
| E4 | SimCLR Model + NT-Xent Loss | ResNet-50 backbone (fc→Identity), 2-layer projection head with L2-norm, NT-Xent loss with temperature scaling and diagonal masking. | `src/models/simclr.py`, `src/training/loss.py` | 13 | 3+3+4+3 |
| E5 | SimCLR Training Loop | Two-condition training loop per seed: seed control, optimizer + cosine LR schedule, mechanism verification before NoBackground run, checkpoint saving, collapse detection. | `src/training/trainer.py` | 15 | 4+4+3+4 |
| E6 | Linear Probe Evaluation | Feature extraction (frozen backbone, no grad), train logistic regression for spurious and task probes, compute ratio per seed, save per-seed JSON. | `src/evaluation/probes.py` | 11 | 3+3+2+3 |
| E7 | Statistical Analysis | Paired t-test (one-sided), Cohen's d, confound check, verdict logic (CONFIRMED/INCONCLUSIVE/FAIL). | `src/evaluation/stats.py` | 9 | 2+2+3+2 |
| E8 | Visualization (4 Figures) | Implement all four required figures: gate metrics bar chart, spurious/task scatter, paired ratio lines, qualitative background replacement grid. | `src/visualization/figures.py` | 10 | 3+2+2+3 |
| E9 | Entrypoints + Orchestration | run_experiment.py CLI (single seed/condition), aggregate_results.py (multi-seed aggregation + stats + figures + JSON output), error handling for all NFR-4 failure modes. | `run_experiment.py`, `aggregate_results.py` | 12 | 3+3+2+4 |

**Distribution**:
- VeryHigh (18-20): []
- High (14-17): [E3, E5]
- Medium (9-13): [E1, E4, E6, E8, E9]
- Low (4-8): [E2, E7]

---

## Module Dependency Graph

- `run_experiment.py` → `config`, `data/waterbirds`, `data/places365_pool`, `augmentation/*`, `models/simclr`, `training/*`, `evaluation/probes`
- `aggregate_results.py` → `evaluation/stats`, `visualization/figures`
- `training/trainer` → `models/simclr`, `training/loss`, `data/waterbirds`, `augmentation/*`
- `evaluation/probes` → `models/simclr`, `data/waterbirds`
- `augmentation/background_replace` → `data/places365_pool`, `augmentation/simclr_augment`
