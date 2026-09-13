# Architecture: H-P0
## DFR Backbone Identity Sanity Check — EXISTENCE PoC

**hypothesis_id:** h-p0
**hypothesis_type:** EXISTENCE
**tier:** LIGHT
**generated_at:** 2026-08-05

Applied: No domain-specific KB pattern (Archon KB is diffusers-indexed; standard PyTorch inference pattern used)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. All patterns sourced from izmailovpavel/spurious_feature_learning reference implementation and standard PyTorch.

---

## File Organization

- `h-p0/code/run_experiment.py` — single entry point: loads data, loads checkpoints, extracts features, computes similarity, evaluates gate, saves outputs
- `h-p0/code/config.py` — fixed constants (paths, thresholds, seeds)
- `h-p0/results.json` — output gate metrics
- `h-p0/figures/` — output plots
- `h-p0/04_validation.md` — output validation report (written by run_experiment.py)

---

## Modules

### Config (`h-p0/code/config.py`)

**Dependencies**: none

```python
WILDS_CACHE = "/home/PrayPrey/.wilds_cache"
HF_REPO = "izmailovpavel/spurious_feature_learning"
SEEDS = [1, 2, 3]
N_IMAGES = 50
DATA_SEED = 42
GATE_MEAN_SIM = 0.9999
GATE_VARIANCE = 1e-6
DEVICE = "cuda"  # falls back to cpu
OUTPUT_DIR = "h-p0"
FIGURES_DIR = "h-p0/figures"
```

### Experiment Runner (`h-p0/code/run_experiment.py`)

**Dependencies**: config, torch, torchvision, wilds, huggingface_hub, sklearn, matplotlib

```python
def get_transform() -> transforms.Compose: ...
def load_test_images(n: int = 50, seed: int = 42) -> tuple[Tensor, Tensor]: ...
    # returns images (50,3,224,224), background_labels (50,)

def download_checkpoint(seed: int, method: str) -> Path: ...
    # hf_hub_download from HF_REPO, returns local path

def load_model(ckpt_path: Path, device: str) -> nn.Module: ...
    # imagenet_resnet50_pretrained(n_classes=2).load_state_dict(...)

def extract_layer4_features(model: nn.Module, images: Tensor, device: str) -> Tensor: ...
    # forward hook on model.layer4 → AdaptiveAvgPool2d(1,1) → flatten → (50, 2048)

def compute_cosine_similarity(feat1: Tensor, feat2: Tensor) -> dict: ...
    # returns {mean: float, variance: float, per_sample: Tensor(50,)}

def run_probe(features: Tensor, labels: Tensor) -> float: ...
    # sklearn LogisticRegression on ERM seed1 features vs background label

def evaluate_gate(results: dict) -> bool: ...
    # all seeds: mean >= GATE_MEAN_SIM and variance < GATE_VARIANCE

def save_figures(results: dict) -> None: ...
    # bar chart (3 seeds, threshold line) + histogram + PCA scatter

def save_results(results: dict, gate_passed: bool, probe_acc: float) -> None: ...
    # writes results.json and 04_validation.md

def main() -> None: ...
    # orchestrates all above functions
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Config | Project structure, config.py, dependency check | 4 | 1+1+1+1 |
| A-2 | Data Loading | WILDS test split, 50-image fixed subset with seed=42 | 6 | 2+1+1+2 |
| A-3 | Checkpoint Loading | HF Hub download, imagenet_resnet50_pretrained load, 6 checkpoints | 8 | 2+2+2+2 |
| A-4 | Feature Extraction | Forward hook on layer4, pool+flatten, shape verification | 7 | 2+2+2+1 |
| A-5 | Similarity + Gate | Cosine similarity per seed pair, gate evaluation, probe validation | 7 | 2+2+2+1 |
| A-6 | Output & Figures | results.json, bar chart, histogram, PCA scatter, 04_validation.md | 6 | 2+1+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1, A-2, A-3, A-4, A-5, A-6]

**Total complexity**: 38 — appropriate for LIGHT/EXISTENCE tier (pure inference, no training)

---

## Notes

- Single file `run_experiment.py` is sufficient. No separate model.py — checkpoint loading is 3 lines using upstream `imagenet_resnet50_pretrained`.
- Load one checkpoint at a time, delete after feature extraction to keep memory minimal.
- `imagenet_resnet50_pretrained` must be cloned/imported from izmailovpavel/spurious_feature_learning or replicated as a thin wrapper around `torchvision.models.resnet50` with a replaced fc layer.
- CPU fallback acceptable: 50-image batch × ResNet-50 forward pass is < 30s on CPU.
