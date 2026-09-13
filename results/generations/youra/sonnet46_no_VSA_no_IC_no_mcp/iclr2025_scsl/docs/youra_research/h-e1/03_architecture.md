---
title: "Architecture: h-e1 — Spurious/Task Probe Accuracy Ratio Study"
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
tier: LIGHT
date: 2026-08-26
author: yoon303b@gmail.com
---

# Architecture: h-e1

Applied: Frozen-backbone linear probe pattern (Izmailov et al. NeurIPS 2022)
Applied: Group-balanced sampling for probe train split (DFR protocol)
Applied: sklearn LogisticRegression for DFR-style probing (C=1.0, lbfgs, max_iter=1000)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. Reference repos analyzed from experiment brief:
- izmailovpavel/spurious_feature_learning — frozen backbone → logistic regression probe on Waterbirds, WILDS group annotations
- facebookresearch/moco-v3 main_lincls.py — frozen ResNet-50 hub load + linear eval pattern
- facebookresearch/dino — `dino_resnet50` hub command, 2048-dim features
- facebookresearch/barlowtwins — `resnet50` hub load, fc replaced with Identity

Key patterns identified: (1) `model.fc = nn.Identity()` for 2048-dim extraction, (2) `torch.no_grad()` feature cache before probe fit, (3) group metadata via `metadata_array[:, 0]` for spurious label, (4) Bonferroni = p_raw * n_pairs

---

## File Structure

```
h-e1/code/
  config.py          # seeds, paths, hyperparameters
  data_utils.py      # WILDS loading, group-balanced sampling
  model_utils.py     # 4 model loaders, feature extraction
  probe_utils.py     # LogisticRegression probe, ratio computation
  stats_utils.py     # ANOVA, pairwise t-tests, Bonferroni, Cohen's d, gate check
  viz_utils.py       # all figure generation
  run_experiment.py  # main orchestration
h-e1/results/
  h-e1_ratios.csv
  h-e1_stats.json
h-e1/figures/
h-e1/logs/
```

---

## Module Interfaces

### config (`code/config.py`)

**Dependencies**: none

```python
SEEDS: list[int] = [0, 1, 2, 3, 4]
PARADIGMS: list[str] = ['erm', 'moco', 'dino', 'barlowtwins']
BATCH_SIZE: int = 256
DATA_ROOT: str = './data/'
RESULTS_DIR: str = './docs/youra_research/h-e1/results/'
FIGURES_DIR: str = './docs/youra_research/h-e1/figures/'
LOG_PATH: str = './docs/youra_research/h-e1/logs/h-e1_run.log'
PROBE_C: float = 1.0
PROBE_MAX_ITER: int = 1000
FEATURE_DIM: int = 2048
BONFERRONI_N: int = 6
GATE_ALPHA: float = 0.05
GATE_MIN_DIFF: float = 0.02
```

---

### data_utils (`code/data_utils.py`)

**Dependencies**: config

```python
def get_waterbirds_subsets(transform) -> tuple:
    """Returns (train_data, val_data, test_data) WILDS subsets."""

def get_probe_train_loader(val_data, seed: int, batch_size: int) -> DataLoader:
    """Group-balanced sample from val split; equal samples per group (4 * min_count)."""

def get_test_loader(test_data, batch_size: int) -> DataLoader:
    """Full test split loader, no subsampling."""
```

---

### model_utils (`code/model_utils.py`)

**Dependencies**: config

```python
def load_erm(device) -> nn.Module:
    """torchvision resnet50(pretrained=True), fc=Identity, eval, no_grad."""

def load_moco(device) -> nn.Module:
    """torch.hub.load('facebookresearch/moco-v3:main', 'resnet50'), eval."""

def load_dino(device) -> nn.Module:
    """torch.hub.load('facebookresearch/dino:main', 'dino_resnet50'), eval."""

def load_barlowtwins(device) -> nn.Module:
    """torch.hub.load('facebookresearch/barlowtwins:main', 'resnet50'), fc=Identity, eval."""

def extract_features(model: nn.Module, loader: DataLoader, device) -> tuple:
    """Returns (features: Tensor[N,2048], task_labels: Tensor[N], spurious_labels: Tensor[N]).
    Asserts features.shape[1] == FEATURE_DIM."""

LOADERS: dict[str, callable] = {
    'erm': load_erm, 'moco': load_moco,
    'dino': load_dino, 'barlowtwins': load_barlowtwins,
}
```

---

### probe_utils (`code/probe_utils.py`)

**Dependencies**: config

```python
def train_probe(features: np.ndarray, labels: np.ndarray) -> LogisticRegression:
    """LogisticRegression(C=1.0, max_iter=1000, solver='lbfgs'). fit and return."""

def eval_probe(clf: LogisticRegression, features: np.ndarray, labels: np.ndarray) -> float:
    """Returns accuracy score."""

def compute_ratio(
    model: nn.Module,
    probe_train_loader: DataLoader,
    test_loader: DataLoader,
    device,
    seed: int,
) -> dict:
    """Sets seeds, extracts features, trains 2 probes, returns
    {'ratio': float, 'spurious_acc': float, 'task_acc': float}."""
```

---

### stats_utils (`code/stats_utils.py`)

**Dependencies**: config

```python
def run_anova(ratios: dict[str, list[float]]) -> tuple[float, float]:
    """scipy.stats.f_oneway; returns (f_stat, p_value)."""

def pairwise_tests(ratios: dict[str, list[float]]) -> list[dict]:
    """6 pairwise ttest_ind with Bonferroni correction and Cohen's d.
    Returns list of dicts: {pair, t, p_raw, p_bonf, cohens_d, mean_diff}."""

def check_gate(pair_results: list[dict]) -> bool:
    """Returns True if any pair: p_bonf < GATE_ALPHA and mean_diff >= GATE_MIN_DIFF."""

def summarize(ratios: dict[str, list[float]]) -> dict:
    """Mean ± std per paradigm."""
```

---

### viz_utils (`code/viz_utils.py`)

**Dependencies**: config

```python
def plot_ratio_bar(ratios: dict, pair_results: list[dict], out_dir: str) -> None:
    """Mandatory: bar chart mean±std ratio per paradigm, p-value annotations,
    horizontal line at GATE_MIN_DIFF threshold."""

def plot_acc_heatmap(acc_records: list[dict], out_dir: str) -> None:
    """2x4 heatmap: spurious_acc and task_acc per paradigm."""

def plot_acc_scatter(acc_records: list[dict], out_dir: str) -> None:
    """Scatter spurious_acc vs task_acc, colored by paradigm, 5 seeds as points."""

def plot_pvalue_matrix(pair_results: list[dict], paradigms: list[str], out_dir: str) -> None:
    """4x4 symmetric Bonferroni p-value matrix."""

def plot_ratio_violin(ratios: dict, out_dir: str) -> None:
    """Violin/box plot of ratio distribution per paradigm."""
```

---

### run_experiment (`code/run_experiment.py`)

**Dependencies**: config, data_utils, model_utils, probe_utils, stats_utils, viz_utils

```python
def main(device: str = 'cuda') -> None:
    """Orchestrates full pipeline:
    1. Load data (once)
    2. For each paradigm: load model, extract features (train+test, cached)
    3. For each seed: compute_ratio → log
    4. Statistical analysis
    5. Gate check + log result
    6. Save results/h-e1_ratios.csv and results/h-e1_stats.json
    7. Generate all figures
    """
```

---

## Epic Tasks

| ID | Task | Description | Type | Complexity | Breakdown |
|----|------|-------------|------|------------|-----------|
| E1 | Data Pipeline | WILDS load, transform, group-balanced probe train loader, test loader | data-pipeline | 7 | 2+1+2+2 |
| E2 | Model Loading & Feature Extraction | 4 hub/torchvision loads, fc=Identity, eval, no_grad extraction, shape assert | model | 9 | 2+2+3+2 |
| E3 | Linear Probe + Ratio | Train 2 probes per (paradigm, seed), compute ratio, seed control, logging | training | 8 | 2+2+2+2 |
| E4 | Statistical Analysis & Gate | ANOVA, 6 pairwise t-tests, Bonferroni, Cohen's d, gate check, JSON export | evaluation | 9 | 2+2+3+2 |
| E5 | Visualization | Mandatory bar chart + 4 optional figures, save to figures/ | evaluation | 7 | 2+1+2+2 |
| E6 | Orchestration & Artifacts | run_experiment.py main loop, CSV/JSON output, logging, gate verdict | training | 8 | 2+2+2+2 |

**Total tasks**: 6 (within LIGHT tier 4-8 range)

**Distribution**: High(8-10): [E2, E3, E4, E6], Medium(6-8): [E1, E5]

---

## Dependencies Between Modules

```
config → data_utils → run_experiment
config → model_utils → run_experiment
config → probe_utils → run_experiment
config → stats_utils → run_experiment
config → viz_utils → run_experiment
```

All utility modules depend only on config. run_experiment imports all utils.

---

## Pre-conditions Checklist (for Phase 4)

- [ ] `assert features.shape[1] == 2048` after each model's extraction
- [ ] `assert all(acc > 0.5 for acc in [task_acc, spurious_acc])` before stats
- [ ] Gate verdict logged: PASS or FAIL → Phase 0 routing note
- [ ] All 40 probe fits complete (4 paradigms × 2 targets × 5 seeds)
