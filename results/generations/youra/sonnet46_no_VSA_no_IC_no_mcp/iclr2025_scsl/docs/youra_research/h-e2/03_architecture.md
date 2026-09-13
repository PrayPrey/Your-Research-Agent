# Architecture: H-E2

**Date:** 2026-08-26
**Hypothesis:** H-E2 — CelebA replication of H-E1 paradigm effect

Applied: dataset-swap replication pattern (single new loader, all downstream reused)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: patterns found from base code (manual file read — no-MCP session)
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: H-E1 is flat 6-file structure; dataset loaded in `data_utils.py` via WILDS; all downstream (probe, stats, viz) is dataset-agnostic. Only `data_utils.py` and `config.py` are H-E1-specific; everything else imports cleanly.

---

## File Organization

H-E2 code lives at `docs/youra_research/h-e2/code/`:

- `data/celeba_loader.py` — NEW: CelebA loading + balanced sampler
- `config.py` — NEW: H-E2 config (paths, CelebA attrs, cache dir)
- `run_experiment.py` — NEW: orchestrator (mirrors H-E1, imports H-E1 modules)
- `results/` — output CSVs
- `figures/` — output plots
- `logs/` — run log

H-E1 modules imported directly (no copy):
- `probe_utils.py`, `stats_utils.py`, `viz_utils.py`, `model_utils.py`

---

## Modules

### CelebALoader (`data/celeba_loader.py`)

**Dependencies**: torchvision, numpy, config

```python
def get_celeba_loaders(
    root: str,
    batch_size: int,
    download: bool = True,
) -> tuple:
    """Returns (train_loader, test_loader, test_dataset)."""
    ...

def get_balanced_celeba_indices(
    dataset,          # torchvision CelebA
    blond_attr: int,  # 9
    male_attr: int,   # 20
    n_per_group: int, # 180
    seed: int,
) -> np.ndarray:
    """Balanced indices: equal n from 4 groups (blond x male)."""
    ...

def get_balanced_test_loader(
    dataset,
    indices: np.ndarray,
    batch_size: int,
) -> DataLoader:
    ...
```

### Config (`config.py`)

**Dependencies**: os

```python
# Experiment
SEEDS: list[int]        # [0,1,2,3,4]
PARADIGMS: list[str]    # ['erm','moco','dino','barlowtwins']
BATCH_SIZE: int         # 256
N_PER_GROUP: int        # 180

# CelebA attribute indices
BLOND_ATTR: int         # 9
MALE_ATTR: int          # 20

# Paths
DATA_ROOT: str          # './data'
RESULTS_DIR: str        # ../results
FIGURES_DIR: str        # ../figures
LOG_DIR: str            # ../logs
CACHE_DIR: str          # /tmp/h-e2-cache

# Probe (same as H-E1)
PROBE_C: float          # 1.0
PROBE_MAX_ITER: int     # 1000
PROBE_SOLVER: str       # 'lbfgs'
FEATURE_DIM: int        # 2048

# Stats (same as H-E1)
BONFERRONI_N: int       # 6
GATE_ALPHA: float       # 0.05
GATE_MIN_DIFF: float    # 0.02
```

### RunExperiment (`run_experiment.py`)

**Dependencies**: config, data/celeba_loader, h-e1 model_utils, h-e1 probe_utils, h-e1 stats_utils, h-e1 viz_utils

```python
def setup_logging() -> None: ...
def main(device: str | None = None) -> None: ...

# Orchestration flow:
# 1. get_celeba_loaders() → train_loader, test_dataset
# 2. for each paradigm: get_or_extract_features() [H-E1 model_utils]
# 3. for each seed: get_balanced_celeba_indices() → compute_ratio() [H-E1 probe_utils]
# 4. run_anova(), pairwise_tests(), check_gate() [H-E1 stats_utils]
# 5. plot_ratio_bar(), plot_acc_heatmap(), plot_pvalue_matrix() [H-E1 viz_utils]
# + plot_cross_dataset_bar() — new figure comparing H-E1 vs H-E2 ratios
```

---

## External Dependencies (Base Hypothesis)

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| get_or_extract_features, LOADERS | `sys.path + from model_utils import ...` | `h-e1/code/model_utils.py` |
| compute_ratio | `from probe_utils import compute_ratio` | `h-e1/code/probe_utils.py` |
| run_anova, pairwise_tests, check_gate, export_results | `from stats_utils import ...` | `h-e1/code/stats_utils.py` |
| plot_ratio_bar, plot_acc_heatmap, plot_pvalue_matrix, plot_ratio_violin | `from viz_utils import ...` | `h-e1/code/viz_utils.py` |

**Import mechanism**: `sys.path.insert(0, '<h-e1/code absolute path>')` in `run_experiment.py` before imports — mirrors H-E1's own pattern.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config | H-E2 config.py with CelebA attrs and paths | 4 | 1+1+1+1 |
| A-2 | CelebA Loader | celeba_loader.py: load + balanced sampler | 8 | 2+2+2+2 |
| A-3 | Orchestrator | run_experiment.py wiring H-E1 modules to CelebA | 9 | 2+3+2+2 |
| A-4 | Cross-dataset Figure | plot_cross_dataset_bar() comparing H-E1 vs H-E2 ratios | 6 | 1+2+2+1 |
| A-5 | Validate & Gate | Run experiment, verify gate, write results CSVs | 7 | 1+2+2+2 |

**Distribution**: High(8-10): [A-3], Medium(5-8): [A-2, A-4, A-5], Low(1-4): [A-1]

---

## Notes

- H-E1 feature cache at `/tmp/h-e1-cache` is reusable if paradigm keys match; H-E2 uses `/tmp/h-e2-cache` to avoid collision.
- `get_or_extract_features` in H-E1's `model_utils.py` takes a DataLoader — CelebA loader must yield `(imgs, attrs)` where attrs shape is `(B, 40)`; feature extractor ignores attrs, so no interface change needed.
- CelebA attrs tensor: `dataset.attr[:, 9]` = Blond_Hair, `[:, 20]` = Male — verified against Group DRO paper.
- `plot_cross_dataset_bar` is the only genuinely new viz; all other viz calls are H-E1 functions with H-E2 data.
