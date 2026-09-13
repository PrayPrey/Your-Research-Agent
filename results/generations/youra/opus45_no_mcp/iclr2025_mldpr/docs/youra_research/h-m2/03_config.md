# Config: H-M2 (Texture Bias Measurement)

**Applied**: dl-training-eval-pipeline-pattern (hardcoded module-level config, matches architecture's config.py spec)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No reusable config code found (h-m1 is bibliometric-only; h-e1 has only raw data). Config designed fresh per architecture's config.py spec.
**Config Files Found**: None
**Pattern Used**: Hardcoded dict (module-level constants), per architecture.py spec — no dataclass used elsewhere in project

---

## A-1: Config + project scaffold [Complexity: 4, Budget: 4]

**Applied**: Standard PyTorch CIFAR training defaults (SGD + cosine decay)

### Configuration (Hardcoded dict / module constants)

```python
# config.py

# Paths
DATA_DIR = "data/"
DTD_DIR = "data/dtd/"
CHECKPOINT_DIR = "checkpoints/"
RESULTS_DIR = "results/"
FIGURES_DIR = "figures/"

# Data
BATCH_SIZE = 128
SEED = 42

# Training
EPOCHS = 200
LR_INIT = 0.1
LR_MIN = 0.001          # cosine decay floor
MOMENTUM = 0.9
WEIGHT_DECAY = 5e-4

# Augmentation (used directly in data.py transforms)
CROP_SIZE = 32
CROP_PADDING = 4

# Gate
EFFECT_SIZE_THRESHOLD = 0.05   # min texture_bias_ratio diff (ResNet - VGG)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Define config constants | All values above in config.py |
| C-1-2 | Create directory scaffold | mkdir data/, checkpoints/, results/, figures/ on import/run |
| C-1-3 | DTD-presence check | Raise clear error if `DTD_DIR` empty/missing at startup |
| C-1-4 | Dependency check | Verify torch/torchvision/matplotlib importable, versions per PRD 7.1 |

---

## Notes for Downstream Tasks (A-2 through A-8)

No additional config schemas needed — all modules (`adain.py`, `data.py`, `models.py`, `train.py`, `evaluate.py`, `gate.py`, `visualize.py`, `run.py`) import constants directly from `config.py` above. Function signatures already fixed in `03_architecture.md`; no per-task config variation required (single fixed run, not a sweep).

- `train_model(..., epochs=EPOCHS, ...)` uses `LR_INIT`, `LR_MIN`, `MOMENTUM`, `WEIGHT_DECAY` for `optim.SGD` + `CosineAnnealingLR(T_max=EPOCHS, eta_min=LR_MIN)`.
- `get_cifar10_loaders(BATCH_SIZE)` applies `transforms.RandomCrop(CROP_SIZE, padding=CROP_PADDING)` + `RandomHorizontalFlip()`.
- `evaluate_gate(resnet_bias, vgg_bias)` uses `EFFECT_SIZE_THRESHOLD` for pass/fail: `pass_gate = (resnet_ratio - vgg_ratio) > EFFECT_SIZE_THRESHOLD`.
- `torch.manual_seed(SEED)` set once in `run.py` before data/model construction.
