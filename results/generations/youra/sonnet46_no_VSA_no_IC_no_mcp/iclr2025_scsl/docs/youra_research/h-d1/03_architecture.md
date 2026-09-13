---
title: "Architecture: h-d1 — Directional Paradigm × Dataset Interaction Analysis"
hypothesis_id: h-d1
hypothesis_type: DIRECTIONAL (INCREMENTAL on H-E1)
tier: FULL
date: 2026-08-26
author: yoon303b@gmail.com
---

# Architecture: h-d1

Applied: Frozen-backbone linear probe pattern (Izmailov et al. NeurIPS 2022)
Applied: Group-balanced DFR probing protocol (5-seed sklearn LogisticRegression)
Applied: scipy.stats directional t-test + null test pattern (alternative='greater' / 'two-sided')

---

## Codebase Analysis (Serena)

**Project Type**: incremental (base hypothesis H-E1)
**Status**: green-field for code — H-E1 Phase 4 was never run; no active h-e1/code/ folder exists
**Analyzed Path**: `docs/youra_research/h-e1/` (03_architecture.md only; code only in _archive/)
**Findings**: H-E1 architecture (03_architecture.md) defines interfaces for data_utils, model_utils, probe_utils, stats_utils, viz_utils. Those archive paths are stale experiments, not canonical code. H-D1 implements its own code from scratch using H-E1's interface conventions and reuses H-E1's data artifacts (probe_results_waterbirds.json) via file path only.

---

## File Structure

```
h-d1/code/
  config.py          # paths, seeds, thresholds
  celeba_data.py     # CelebA loading + group-balanced split
  feature_extract.py # frozen ResNet-50 / MoCo-v3 feature extraction on CelebA
  probe.py           # logistic regression probe trainer + ratio computation
  wb_loader.py       # H-E1 Waterbirds results loader + validator
  analysis.py        # primary + secondary statistical tests
  viz.py             # 5 required figures
  run_experiment.py  # orchestration entry point

h-d1/
  celeba_features_erm.pt
  celeba_features_moco.pt
  celeba_probe_results.json
  h_d1_results.json
  figures/
    gate_metrics.png
    interaction_plot.png
    directional_test.png
    ratio_vs_wga.png
    seed_distributions.png
```

---

## Module Interfaces

### config (`code/config.py`)

**Dependencies**: none

```python
SEEDS: list[int] = [0, 1, 2, 3, 4]
PARADIGMS: list[str] = ['erm', 'moco', 'dino', 'barlowtwins']
PRIMARY_PARADIGMS: list[str] = ['erm', 'moco']
BATCH_SIZE: int = 256
DATA_ROOT: str = './data/'
CELEBA_MIN_GROUP_SIZE: int = 500

WB_RESULTS_PATH: str = './docs/youra_research/h-e1/results/probe_results_waterbirds.json'
RESULTS_DIR: str = './docs/youra_research/h-d1/'
FIGURES_DIR: str = './docs/youra_research/h-d1/figures/'

PROBE_C: float = 1.0
PROBE_MAX_ITER: int = 1000
FEATURE_DIM: int = 2048

ALPHA_DIRECTIONAL: float = 0.05   # WB one-tailed gate
ALPHA_NULL: float = 0.1           # CelebA two-sided gate
BOOTSTRAP_N: int = 1000           # Pearson r CI
```

---

### celeba_data (`code/celeba_data.py`)

**Dependencies**: config

```python
def load_celeba_balanced(
    root: str,
    min_per_group: int = 500,
) -> tuple[torch.utils.data.Dataset, np.ndarray, np.ndarray]:
    """
    Returns: dataset, task_labels (Blond_Hair), spurious_labels (Male)
    Groups: (Blond×Male, Blond×Female, NotBlond×Male, NotBlond×Female)
    Balanced by min-count sampling across 4 groups.
    """
    ...

def get_celeba_dataloader(
    dataset: torch.utils.data.Dataset,
    indices: np.ndarray,
    batch_size: int = 256,
) -> torch.utils.data.DataLoader: ...
```

---

### feature_extract (`code/feature_extract.py`)

**Dependencies**: config, celeba_data

```python
def load_erm_backbone() -> torch.nn.Module:
    """torchvision.models.resnet50(pretrained=True), fc=Identity, eval()"""
    ...

def load_moco_backbone() -> torch.nn.Module:
    """torch.hub.load('facebookresearch/moco-v3', 'resnet50'), eval()"""
    ...

def extract_features(
    model: torch.nn.Module,
    dataloader: torch.utils.data.DataLoader,
    device: str = 'cuda',
) -> np.ndarray:
    """Returns (N, 2048) float32 array under torch.no_grad()"""
    ...

def extract_and_save_celeba_features(
    paradigm: str,        # 'erm' | 'moco'
    save_path: str,
) -> np.ndarray:
    """Loads backbone, extracts CelebA features, saves .pt, returns array."""
    ...
```

---

### probe (`code/probe.py`)

**Dependencies**: config

```python
def train_probe(
    features: np.ndarray,
    labels: np.ndarray,
    seed: int,
) -> sklearn.linear_model.LogisticRegression:
    """C=1.0, lbfgs, max_iter=1000, random_state=seed"""
    ...

def eval_probe(
    clf: sklearn.linear_model.LogisticRegression,
    features: np.ndarray,
    labels: np.ndarray,
) -> float:
    """Returns balanced accuracy on test split."""
    ...

def compute_ratios(
    features: np.ndarray,
    task_labels: np.ndarray,
    spurious_labels: np.ndarray,
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    seeds: list[int],
) -> dict[str, list[float]]:
    """
    Returns {'spurious_acc': [...], 'task_acc': [...], 'ratio': [...]}
    for each seed. ratio = spurious_acc / task_acc.
    """
    ...

def run_celeba_probing(
    features_erm: np.ndarray,
    features_moco: np.ndarray,
    task_labels: np.ndarray,
    spurious_labels: np.ndarray,
    train_idx: np.ndarray,
    test_idx: np.ndarray,
) -> dict[str, list[float]]:
    """
    Returns {'erm': [ratio_s0..s4], 'moco': [ratio_s0..s4]}
    Also saves to RESULTS_DIR/celeba_probe_results.json.
    """
    ...
```

---

### wb_loader (`code/wb_loader.py`)

**Dependencies**: config

```python
def load_wb_results(path: str = None) -> dict[str, list[float]]:
    """
    Loads H-E1 probe_results_waterbirds.json.
    Validates: 4 paradigms present, each with 5 ratio values.
    Returns: {'erm': [...], 'moco': [...], 'dino': [...], 'barlowtwins': [...]}
    Raises ValueError if validation fails.
    """
    ...

def extract_primary(
    wb_results: dict[str, list[float]],
) -> tuple[np.ndarray, np.ndarray]:
    """Returns (erm_ratios, moco_ratios) as np.ndarray (shape 5,)."""
    ...
```

---

### analysis (`code/analysis.py`)

**Dependencies**: config, wb_loader

```python
def directional_test(
    moco_ratios: np.ndarray,
    erm_ratios: np.ndarray,
) -> dict:
    """
    ttest_ind(moco, erm, alternative='greater').
    Returns: {t, p_directional, cohen_d, diff_mean, moco_mean, erm_mean}
    """
    ...

def null_test(
    moco_ratios: np.ndarray,
    erm_ratios: np.ndarray,
) -> dict:
    """
    ttest_ind(moco, erm, alternative='two-sided').
    Returns: {t, p_two_sided, cohen_d, diff_mean, moco_mean, erm_mean}
    """
    ...

def pearson_r_with_ci(
    ratios_all: np.ndarray,
    wga_gaps_all: np.ndarray,
    n_bootstrap: int = 1000,
) -> dict:
    """
    pearsonr + bootstrap 95% CI.
    Returns: {r, p, ci_low, ci_high}
    """
    ...

def evaluate_gate(
    p_wb_directional: float,
    p_ca_two_sided: float,
) -> str:
    """Returns 'full_support' | 'partial_support' | 'no_support'."""
    ...

def run_all_analyses(
    wb_results: dict[str, list[float]],
    celeba_results: dict[str, list[float]],
    wga_gaps: dict | None = None,
) -> dict:
    """
    Runs directional_test, null_test, pearson_r (if wga_gaps provided),
    ablations A/B/C/D, gate evaluation.
    Returns full results dict; saves to h_d1_results.json.
    """
    ...
```

---

### viz (`code/viz.py`)

**Dependencies**: config, analysis

```python
def plot_gate_metrics(results: dict, save_path: str) -> None:
    """FR-8.1: Bar chart MoCo vs ERM ratio on WB + CelebA, ±1 SD error bars."""
    ...

def plot_interaction(
    wb_results: dict[str, list[float]],
    celeba_results: dict[str, list[float]],
    save_path: str,
) -> None:
    """FR-8.2: All 4 paradigms × 2 datasets with error bars."""
    ...

def plot_directional_test(results: dict, save_path: str) -> None:
    """FR-8.3: Horizontal bar MoCo−ERM diff + 95% CI, significance thresholds."""
    ...

def plot_ratio_vs_wga(
    ratios_all: np.ndarray,
    wga_gaps_all: np.ndarray,
    paradigm_labels: list[str],
    pearson_result: dict,
    save_path: str,
) -> None:
    """FR-8.4: Scatter 40 points, color by paradigm, Pearson r annotation."""
    ...

def plot_seed_distributions(
    wb_results: dict[str, list[float]],
    celeba_results: dict[str, list[float]],
    save_path: str,
) -> None:
    """FR-8.5: Violin/strip plot ratio distributions per paradigm × dataset."""
    ...

def generate_all_figures(
    wb_results: dict,
    celeba_results: dict,
    analysis_results: dict,
    wga_data: dict | None = None,
) -> None: ...
```

---

### run_experiment (`code/run_experiment.py`)

**Dependencies**: all modules

```python
def main() -> None:
    """
    1. Load WB results (wb_loader)
    2. Extract CelebA features if not cached (feature_extract)
    3. Run CelebA probing (probe)
    4. Run all analyses (analysis)
    5. Generate all figures (viz)
    6. Print gate verdict + interpretation
    """
    ...
```

---

## External Data Dependencies (H-E1 Artifacts)

| Artifact | Expected Path | Notes |
|----------|--------------|-------|
| WB probe results JSON | `docs/youra_research/h-e1/results/probe_results_waterbirds.json` | 4 paradigms × 5 seeds × {spurious_acc, task_acc, ratio} |
| WGA gaps (optional) | `docs/youra_research/h-e1/results/h-e1_stats.json` or H-E2 output | Only needed for Pearson r secondary analysis |

**Note**: If H-E1 results path differs, wb_loader searches fallback: `h-e1/h-e1_ratios.csv`.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | config.py, directory structure, data root setup | 4 | 1+1+1+1 |
| A-2 | CelebA Data Pipeline | celeba_data.py: load, group-balance 4 groups, min 500/group | 9 | 2+2+3+2 |
| A-3 | Feature Extraction | feature_extract.py: ERM + MoCo backbones, batch extract, save .pt cache | 10 | 3+2+3+2 |
| A-4 | Linear Probe (CelebA) | probe.py: 5-seed logistic regression for spurious+task labels, ratio computation | 10 | 3+2+3+2 |
| A-5 | WB Results Loader | wb_loader.py: load + validate H-E1 JSON, extract ERM/MoCo arrays | 6 | 2+1+2+1 |
| A-6 | Primary Statistical Tests | analysis.py: directional t-test, null t-test, Cohen's d, gate evaluation | 10 | 2+2+4+2 |
| A-7 | Secondary Analysis | pearson_r_with_ci: bootstrap CI + ablations A/B/C/D (reversed-direction test) | 12 | 3+2+4+3 |
| A-8 | Visualization — Required | viz.py: gate_metrics.png (FR-8.1, mandatory) + interaction_plot.png (FR-8.2) | 8 | 2+2+2+2 |
| A-9 | Visualization — Extended | directional_test.png, ratio_vs_wga.png, seed_distributions.png (FR-8.3/4/5) | 10 | 2+2+3+3 |
| A-10 | Results Persistence | Save h_d1_results.json with all p-values, effect sizes, gate verdict, interpretation strings | 7 | 2+1+2+2 |
| A-11 | Orchestration | run_experiment.py: end-to-end flow, cache checks, error handling for missing CelebA | 9 | 2+3+2+2 |
| A-12 | Validation Report | Generate 04_validation.md: gate verdict + all 4 pre-registered interpretations documented | 6 | 1+1+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-4, A-6, A-7, A-8, A-9, A-11], Low(4-8): [A-1, A-5, A-10, A-12]

**Total Complexity**: 101
