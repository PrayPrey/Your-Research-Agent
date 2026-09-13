# Architecture: H-M2
## Group-Balanced Gradient Propagates Through All Backbone Layers — Proxy Verification

**Generated:** 2026-08-05
**Hypothesis Type:** MECHANISM (Proxy Verification — no new training)
**Applied:** sequential-checkpoint-analysis pattern (Archon KB: domain mismatch, no relevant results)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Patterns found from H-M1 base code
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Findings**: Flat function structure (no classes); single `run_experiment.py` + `config.py`; WILDS loading via `get_dataset(..., download=False, root_dir=WILDS_CACHE)`; group array = `2*y + bg`; transforms = `Resize(224)+ToTensor+Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])`; results to `BASE_DIR/results.json`, `BASE_DIR/04_validation.md`

---

## File Organization

- `h-m2/code/config.py` — paths and constants
- `h-m2/code/run_experiment.py` — all analysis logic and entry point
- `h-m2/figures/` — output figures (4 plots)
- `h-m2/results.json` — structured results
- `h-m2/04_validation.md` — validation report (auto-generated)

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: none

```python
WILDS_CACHE: str = "/home/PrayPrey/.wilds_cache"
WILDS_DATASET: str = "waterbirds"
CHECKPOINT_ARCHIVE: str = "/home/PrayPrey/YouRA_no_IC_sonnet46/TEST_scsl/docs/youra_research/_archive/20260805T130336_routing_recovery/h-e1/checkpoints"
SEEDS: list = [1, 2, 3]
METHODS: list = ["erm", "groupdro", "sam", "dfr"]
N_GRAD_BATCHES: int = 50
GRAD_BATCH_SIZE: int = 32
N_GROUPS: int = 4
PROBE_C: float = 1e9
PROBE_MAX_ITER: int = 1000
PROBE_RANDOM_STATE: int = 42
BASE_DIR: str  # os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGURES_DIR: str  # BASE_DIR/figures
RESULTS_JSON: str  # BASE_DIR/results.json
VALIDATION_REPORT: str  # BASE_DIR/04_validation.md
IMAGENET_MEAN: list = [0.485, 0.456, 0.406]
IMAGENET_STD: list = [0.229, 0.224, 0.225]
```

---

### Experiment Runner (`code/run_experiment.py`)

**Dependencies**: config, torch, torchvision, wilds, sklearn, scipy, numpy, matplotlib

```python
# -- model loading --
def load_resnet50(ckpt_path: str, device: str = 'cpu') -> torch.nn.Module:
    """Load ResNet-50 checkpoint; handles 'model'/'state_dict' wrapper keys."""
    ...

# -- feature extraction (identical to H-P0 proven protocol) --
def extract_layer4_features(model: torch.nn.Module, loader: DataLoader,
                            device: str = 'cpu') -> tuple[np.ndarray, np.ndarray]:
    """Returns (features [N, 2048], background_labels [N]) from loader."""
    ...

# -- weight difference analysis (FR-1) --
def verify_gradient_propagation(erm_ckpt: str, gdro_ckpt: str,
                                 seed: int) -> dict:
    """
    Computes per-block L2 weight diff (GroupDRO - ERM) for layer4[0,1,2].
    Returns: {layer4_block{i}_diff, head_weight_diff,
              backbone_to_head_ratio, gradient_reached_layer4}
    """
    ...

# -- gradient norm analysis (FR-2) --
def compute_layer4_gradient_norm(model: torch.nn.Module, loader: DataLoader,
                                  loss_type: str,  # 'erm' | 'groupdro'
                                  device: str = 'cpu',
                                  n_batches: int = 50) -> tuple[float, float]:
    """Returns (mean_grad_norm, std_grad_norm) over n_batches at layer4."""
    ...

# -- linear probe (FR-3) --
def linear_probe(train_feats: np.ndarray, train_labels: np.ndarray,
                 test_feats: np.ndarray, test_labels: np.ndarray) -> float:
    """sklearn LogisticRegression(lbfgs, C=1e9, max_iter=1000, rs=42).score(...)"""
    ...

# -- statistical test (FR-4) --
def paired_ttest(erm_accs: list[float],
                 gdro_accs: list[float]) -> tuple[float, float]:
    """Returns (p_value, cohens_d). One-sided: H0 probe_gdro >= probe_erm."""
    ...

# -- WILDS data helpers --
def get_transform() -> torchvision.transforms.Compose:
    """Resize(224)+ToTensor+Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])"""
    ...

def get_loader(split: str, batch_size: int, shuffle: bool = False) -> DataLoader:
    """WILDS waterbirds loader for given split; download=False."""
    ...

# -- visualization (FR-5) --
def save_figures(weight_results: dict, grad_results: dict) -> None:
    """
    Saves 3 required + 1 optional figures to config.FIGURES_DIR:
      layer4_weight_diff.png  — grouped bar chart per seed × block
      gradient_norm_comparison.png — box plot ERM vs GroupDRO 50 batches
      backbone_head_ratio.png — scatter per seed
      layer4_heatmap.png      — optional heatmap
    """
    ...

# -- results + report (FR-6, FR-7) --
def save_results(results: dict) -> None:
    """JSON dump to config.RESULTS_JSON."""
    ...

def generate_validation_report(results: dict) -> None:
    """Writes config.VALIDATION_REPORT (04_validation.md)."""
    ...

# -- orchestration --
def main() -> None:
    """
    Step 1: weight difference analysis — 3 ERM×GroupDRO seed pairs.
    Step 2: gradient norm analysis — seed 1 representative, 50 batches.
    Step 3: linear probe on full test set (5,794 samples) — all 12 checkpoints.
    Step 4: statistical test (paired t-test).
    Step 5: figures + results.json + 04_validation.md.
    Sequential checkpoint loading to avoid OOM (< 4 GB).
    """
    ...

if __name__ == '__main__':
    main()
```

---

## Data Flow

- `main()` calls `get_loader('train', batch_size=32, shuffle=False)` for gradient analysis
- `main()` calls `get_loader('test', batch_size=128, shuffle=False)` for linear probe (full 5,794)
- Checkpoints loaded sequentially: one pair at a time (ERM+GroupDRO), analyzed, then released
- `group_array = metadata[:, 0]`; `background_label = group_array % 2`

---

## External Dependencies (Base Hypothesis)

| Module | Import Pattern | File Location |
|--------|---------------|---------------|
| config constants | `import config` (sys.path insert) | `h-m1/code/config.py` → replicated in `h-m2/code/config.py` |
| WILDS loading | `from wilds import get_dataset` | same pattern as `h-m1/code/run_experiment.py:load_group_distribution` |
| transforms | `torchvision.transforms.Compose` | same Resize/ToTensor/Normalize as h-m1 worker |
| group computation | `group_array = 2*y + bg` | h-m1 pattern — H-M2 uses `bg = group_array % 2` for probe label |

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation)

**Note:** H-M2 does NOT import from h-m1 directly. Pattern is replicated in its own `code/` directory, consistent with h-m1 structure.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project setup | config.py, directory structure, figures dir | 4 | 1+1+1+1 |
| A-2 | Checkpoint loader | `load_resnet50` with key-wrapper handling | 6 | 2+1+2+1 |
| A-3 | WILDS data helpers | `get_transform`, `get_loader` for train+test splits | 6 | 1+2+1+2 |
| A-4 | Weight difference analysis | `verify_gradient_propagation` for 3 seed pairs + DFR control | 9 | 2+2+3+2 |
| A-5 | Gradient norm analysis | `compute_layer4_gradient_norm` ERM+GroupDRO, 50 batches | 10 | 2+2+4+2 |
| A-6 | Feature extraction + linear probe | `extract_layer4_features` full test (5,794) × 12 checkpoints + `linear_probe` | 11 | 3+2+3+3 |
| A-7 | Statistical test | `paired_ttest` one-sided + Cohen's d | 5 | 1+1+2+1 |
| A-8 | Visualization | 3 required + 1 optional figures | 8 | 2+1+3+2 |
| A-9 | Results + report | `save_results` JSON + `generate_validation_report` markdown | 6 | 2+1+1+2 |
| A-10 | Orchestration + integration | `main()` sequential flow, OOM-safe loading, assertions | 9 | 2+2+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4, A-5, A-6, A-10], Low(4-8): [A-1, A-2, A-3, A-7, A-8, A-9]

---

## Implementation Notes

- Load checkpoints one at a time (del model; gc.collect() between pairs) to stay < 4 GB
- `model.train()` only during gradient norm analysis; `model.eval()` + `torch.no_grad()` for feature extraction
- `group_array = metadata[:, 0]` (WILDS convention, same as h-m1); `background_label = group_array % 2`
- DFR-ERM diff should be ~0 (negative control from H-P0 cosine_sim=1.000000)
- Assert `gradient_reached_layer4` for all 3 seeds before proceeding to report
