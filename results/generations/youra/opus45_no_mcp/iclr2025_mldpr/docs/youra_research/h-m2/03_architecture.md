# Architecture: H-M2 (Texture Bias Measurement)

**Applied**: dl-training-eval-pipeline-pattern (dataset+style-transfer generation -> parallel model training -> Geirhos texture-bias evaluation -> gate)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: MCP unavailable this session; h-m1/code/ inspected (bibliometric-only, no DL modules); h-e1/code/ contains only raw CIFAR/CINIC data files. No reusable model/training code found.
**Analyzed Path**: `docs/youra_research/h-m1/code/`, `docs/youra_research/h-e1/code/`
**Findings**: No prior PyTorch model/training/AdaIN code to reuse. New implementation from scratch, following h-m1's config/run.py orchestration pattern.

---

## File Structure

```
h-m2/code/
  config.py
  data.py            # CIFAR-10 + DTD loading, Stylized-CIFAR generation
  adain.py           # AdaIN style transfer
  models.py          # VGG-11 and ResNet-18 (CIFAR-adapted)
  train.py           # SGD + cosine LR training loop
  evaluate.py        # Geirhos texture bias measurement
  gate.py            # pass/fail decision
  visualize.py
  run.py
  data/dtd/          # manual DTD download target
  checkpoints/       # saved model weights
  results/           # metrics JSON
  figures/           # required + optional PNGs
```

---

## Modules

### config.py

**Dependencies**: none

```python
DATA_DIR: str = "data/"
DTD_DIR: str = "data/dtd/"
CHECKPOINT_DIR: str = "checkpoints/"
RESULTS_DIR: str = "results/"
FIGURES_DIR: str = "figures/"

BATCH_SIZE: int = 128
EPOCHS: int = 200
LR_INIT: float = 0.1
LR_MIN: float = 0.001
MOMENTUM: float = 0.9
WEIGHT_DECAY: float = 5e-4
SEED: int = 42
EFFECT_SIZE_THRESHOLD: float = 0.05
```

### adain.py (`h-m2/code/adain.py`)

**Dependencies**: none

```python
def adain_style_transfer(content: "Tensor", style: "Tensor", alpha: float = 1.0) -> "Tensor": ...
```

### data.py (`h-m2/code/data.py`)

**Dependencies**: config, adain

```python
def get_cifar10_loaders(batch_size: int) -> tuple["DataLoader", "DataLoader"]:
    # train_loader (augmented), test_loader
    ...
def load_dtd_images(dtd_dir: str) -> list["Tensor"]: ...
def build_stylized_cifar10(cifar_test: "Dataset", dtd_images: list["Tensor"], seed: int) -> "Dataset":
    # each item: (stylized_image, shape_label, texture_label)
    ...
def get_conflict_loader(stylized_dataset: "Dataset", batch_size: int) -> "DataLoader": ...
```

### models.py (`h-m2/code/models.py`)

**Dependencies**: none

```python
def build_vgg11_cifar(num_classes: int = 10) -> "nn.Module": ...
def build_resnet18_cifar(num_classes: int = 10) -> "nn.Module": ...
```

### train.py (`h-m2/code/train.py`)

**Dependencies**: config, models, data

```python
def train_model(model: "nn.Module", train_loader: "DataLoader", test_loader: "DataLoader",
                 epochs: int, checkpoint_path: str) -> dict:
    # SGD + cosine LR schedule; returns {"train_acc_curve", "test_acc_curve", "final_test_acc"}
    ...
def save_checkpoint(model: "nn.Module", path: str) -> None: ...
def load_checkpoint(model: "nn.Module", path: str) -> "nn.Module": ...
```

### evaluate.py (`h-m2/code/evaluate.py`)

**Dependencies**: config

```python
def measure_texture_bias(model: "nn.Module", conflict_loader: "DataLoader") -> dict:
    # {"texture_bias_ratio", "texture_accuracy", "shape_accuracy", "neither"}
    ...
def evaluate_standard_accuracy(model: "nn.Module", test_loader: "DataLoader") -> float: ...
```

### gate.py (`h-m2/code/gate.py`)

**Dependencies**: evaluate

```python
def evaluate_gate(resnet_bias: dict, vgg_bias: dict) -> dict:
    # {"pass_gate": bool, "diff": float, "resnet_ratio": float, "vgg_ratio": float}
    ...
def write_gate_report(gate_result: dict, path: str) -> None: ...
```

### visualize.py (`h-m2/code/visualize.py`)

**Dependencies**: gate, evaluate

```python
def plot_gate_comparison(gate_result: dict, out_path: str) -> None: ...          # required figure
def plot_confusion_shape_texture(bias_result: dict, out_path: str) -> None: ...
def plot_training_curves(resnet_history: dict, vgg_history: dict, out_path: str) -> None: ...
def plot_per_class_texture_bias(bias_result: dict, out_path: str) -> None: ...
```

### run.py (`h-m2/code/run.py`)

**Dependencies**: all modules above

```python
def main() -> None:
    # 1. get_cifar10_loaders, load_dtd_images -> build_stylized_cifar10 -> get_conflict_loader
    # 2. build_vgg11_cifar, build_resnet18_cifar
    # 3. train_model x2 (identical config) -> save_checkpoint
    # 4. measure_texture_bias x2, evaluate_standard_accuracy x2
    # 5. evaluate_gate -> write_gate_report
    # 6. generate all figures
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config + project scaffold | config.py, dirs, dependency/DTD-presence check | 4 | 1+1+1+1 |
| A-2 | AdaIN style transfer module | mean/std normalization transfer, alpha blend | 6 | 2+1+2+1 |
| A-3 | Data pipeline | CIFAR-10 loaders, DTD loading, Stylized-CIFAR-10 generation, conflict loader | 12 | 3+3+3+3 |
| A-4 | Model implementations | VGG-11 + ResNet-18 CIFAR-adapted (torchvision base) | 8 | 3+1+3+1 |
| A-5 | Training pipeline | SGD+cosine LR loop, augmentation, checkpointing, 200-epoch runs x2 | 14 | 3+3+4+4 |
| A-6 | Texture bias evaluation | Geirhos metric, standard accuracy, per-model results | 8 | 2+2+3+1 |
| A-7 | Gate evaluation | direction + effect-size check, report writer | 4 | 1+1+1+1 |
| A-8 | Visualization + orchestration | 4 figures, run.py wiring, logging/error handling | 10 | 3+2+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-5], Medium(9-13): [A-3, A-8], Low(4-8): [A-1, A-2, A-4, A-6, A-7]

---

## External Dependencies (Base Hypothesis)

None. No prior hypothesis provides reusable DL model/training/style-transfer code. h-m2 implemented from scratch.
