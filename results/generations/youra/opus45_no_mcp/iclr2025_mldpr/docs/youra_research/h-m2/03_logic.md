# Logic: H-M2 (Texture Bias Measurement)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No reusable model/training/AdaIN code found (h-m1 bibliometric-only, h-e1 raw data only). New implementation from scratch.
**Analyzed Path**: N/A (green-field, per architecture doc)
**Relevant Symbols**: None - new implementation

---

## A-1: Config + project scaffold [Complexity: 4, Budget: 4]

**Applied**: Standard PyTorch config module

### API Signatures

```python
# config.py - module-level constants only, no functions
DATA_DIR: str
DTD_DIR: str
CHECKPOINT_DIR: str
RESULTS_DIR: str
FIGURES_DIR: str
BATCH_SIZE: int = 128
EPOCHS: int = 200
LR_INIT: float = 0.1
LR_MIN: float = 0.001
MOMENTUM: float = 0.9
WEIGHT_DECAY: float = 5e-4
SEED: int = 42
EFFECT_SIZE_THRESHOLD: float = 0.05

def ensure_dirs() -> None:
    """Create CHECKPOINT_DIR, RESULTS_DIR, FIGURES_DIR if missing."""
    ...

def check_dtd_present(dtd_dir: str) -> bool:
    """Return True if dtd_dir exists and is non-empty."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Constants | Define all config values above |
| L-1-2 | ensure_dirs | mkdir -p for checkpoint/results/figures dirs |
| L-1-3 | check_dtd_present | Verify manual DTD download, raise informative error if missing |
| L-1-4 | Dependency check | Verify torch/torchvision importable, print versions |

---

## A-2: AdaIN style transfer module [Complexity: 6, Budget: 6]

**Applied**: Adaptive Instance Normalization (Huang & Belongie 2017)

### API Signatures

```python
def adain_style_transfer(content: Tensor, style: Tensor, alpha: float = 1.0) -> Tensor:
    """AdaIN: transfer style's channel-wise mean/std onto content. [B,3,32,32] -> [B,3,32,32]"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| content | [B, 3, 32, 32] | CIFAR-10 batch |
| style | [B, 3, 32, 32] | DTD batch, resized to match |
| content_mean/std | [B, 3, 1, 1] | per-channel stats over H,W |
| out | [B, 3, 32, 32] | stylized, clamp to [0,1] after blend |

### Pseudo-code

```
1. content_mean, content_std = mean/std(content, dim=[2,3], keepdim=True)  # [B,3,1,1]
2. style_mean, style_std = mean/std(style, dim=[2,3], keepdim=True)
3. normalized = (content - content_mean) / (content_std + eps)
4. stylized = normalized * style_std + style_mean
5. out = alpha * stylized + (1 - alpha) * content
6. out = out.clamp(0, 1)
```

### Subtasks [4/6 used - 2 reserve for tuning]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Stats computation | mean/std over spatial dims, eps guard |
| L-2-2 | Blend + clamp | alpha interpolation, output range fix |

---

## A-3: Data pipeline [Complexity: 12, Budget: 12]

**Applied**: torchvision Dataset/DataLoader pattern

### API Signatures

```python
def get_cifar10_loaders(batch_size: int) -> tuple[DataLoader, DataLoader]:
    """train_loader (augmented: RandomCrop(32,pad=4)+HFlip), test_loader (plain). Auto-downloads."""
    ...

def load_dtd_images(dtd_dir: str) -> list[Tensor]:
    """Load all DTD images, resize to [3,32,32], return list of tensors in [0,1]."""
    ...

class StylizedCIFAR10(Dataset):
    def __init__(self, cifar_test: Dataset, dtd_images: list[Tensor], seed: int):
        """Pre-generates stylized images at init using adain_style_transfer."""
        ...
    def __getitem__(self, idx: int) -> tuple[Tensor, int, int]:
        """Returns (stylized_image [3,32,32], shape_label, texture_label)."""
        ...
    def __len__(self) -> int: ...

def build_stylized_cifar10(cifar_test: Dataset, dtd_images: list[Tensor], seed: int) -> Dataset:
    """Factory wrapper: return StylizedCIFAR10(cifar_test, dtd_images, seed)."""
    ...

def get_conflict_loader(stylized_dataset: Dataset, batch_size: int) -> DataLoader:
    """shuffle=False, for deterministic evaluation."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| cifar image | [3, 32, 32] | float in [0,1] |
| dtd image (resized) | [3, 32, 32] | resize + center-crop from variable source size |
| stylized image | [3, 32, 32] | AdaIN(content=cifar, style=dtd, alpha=1.0) |
| conflict batch | ([B,3,32,32], [B], [B]) | image, shape_label, texture_label |

### Pseudo-code (Stylized-CIFAR-10 generation)

```
1. rng = Random(seed)
2. texture_labels = []  # need 47 texture categories from DTD folder names; if flat list, use running index mod 47 or per-image assigned class
3. for i, (img, shape_label) in enumerate(cifar_test):
4.     dtd_img = rng.choice(dtd_images)  # random texture per image, deterministic via seed
5.     texture_label = dtd_img.category_index  # tracked alongside dtd_images
6.     stylized = adain_style_transfer(img.unsqueeze(0), dtd_img.unsqueeze(0), alpha=1.0).squeeze(0)
7.     store (stylized, shape_label, texture_label)
```

**Note**: `load_dtd_images` must also return/track per-image category index (from DTD subfolder name) for `texture_label`; extend return to `list[tuple[Tensor, int]]` (image, category_idx) internally used by `build_stylized_cifar10`.

### Subtasks [12/12 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | get_cifar10_loaders | torchvision CIFAR10 train/test + augmentation transforms |
| L-3-2 | load_dtd_images | Walk DTD dir, resize, track category label per image |
| L-3-3 | StylizedCIFAR10.__init__ | Seeded random pairing + AdaIN generation loop |
| L-3-4 | get_conflict_loader | DataLoader wrapper, shuffle=False |

---

## A-4: Model implementations [Complexity: 8, Budget: 8]

**Applied**: torchvision.models base, CIFAR-adapted classifier head

### API Signatures

```python
def build_vgg11_cifar(num_classes: int = 10) -> nn.Module:
    """torchvision vgg11(weights=None), avgpool->AdaptiveAvgPool2d((1,1)), classifier->Linear(512,256)->ReLU->Dropout(0.5)->Linear(256,num_classes)."""
    ...

def build_resnet18_cifar(num_classes: int = 10) -> nn.Module:
    """torchvision resnet18(weights=None), conv1->3x3 stride1 (CIFAR-adapt), maxpool->Identity(), fc->Linear(512,num_classes)."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input | [B, 3, 32, 32] | |
| vgg11 output | [B, 10] | logits |
| resnet18 output | [B, 10] | logits |

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | build_vgg11_cifar | Load base, replace avgpool+classifier |
| L-4-2 | build_resnet18_cifar | Load base, replace conv1 (3x3,stride1,pad1), maxpool=Identity, fc |
| L-4-3 | Shape sanity check | Forward dummy [2,3,32,32] through both, assert output [2,10] |

---

## A-5: Training pipeline [Complexity: 14, Budget: 14]

**Applied**: SGD + CosineAnnealingLR (standard CIFAR recipe)

### API Signatures

```python
def train_model(model: nn.Module, train_loader: DataLoader, test_loader: DataLoader,
                 epochs: int, checkpoint_path: str) -> dict:
    """SGD(lr=0.1,momentum=0.9,wd=5e-4) + CosineAnnealingLR(T_max=epochs,eta_min=0.001).
    Returns {"train_acc_curve": list[float], "test_acc_curve": list[float], "final_test_acc": float}."""
    ...

def save_checkpoint(model: nn.Module, path: str) -> None: ...

def load_checkpoint(model: nn.Module, path: str) -> nn.Module:
    """Loads state_dict via torch.load, model.load_state_dict, returns model."""
    ...
```

### Pseudo-code

```
1. optimizer = SGD(model.parameters(), lr=LR_INIT, momentum=MOMENTUM, weight_decay=WEIGHT_DECAY)
2. scheduler = CosineAnnealingLR(optimizer, T_max=epochs, eta_min=LR_MIN)
3. for epoch in range(epochs):
4.     model.train(); for x, y in train_loader: forward, CE loss, backward, step
5.     scheduler.step()
6.     train_acc = evaluate_standard_accuracy(model, train_loader)  # or track running acc
7.     test_acc = evaluate_standard_accuracy(model, test_loader)
8.     append to curves
9. save_checkpoint(model, checkpoint_path)
10. return {"train_acc_curve", "test_acc_curve", "final_test_acc": test_acc_curve[-1]}
```

### Subtasks [8/14 used - 6 reserve for 200-epoch runtime debugging]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Optimizer+scheduler setup | SGD + CosineAnnealingLR per config |
| L-5-2 | Train loop | Forward/backward/step per batch, CE loss |
| L-5-3 | Per-epoch eval | Compute train/test acc, append curves |
| L-5-4 | Checkpoint save/load | torch.save/load state_dict |

---

## A-6: Texture bias evaluation [Complexity: 8, Budget: 8]

**Applied**: Geirhos et al. (2019) texture-bias metric

### API Signatures

```python
def measure_texture_bias(model: nn.Module, conflict_loader: DataLoader) -> dict:
    """Returns {"texture_bias_ratio": float, "texture_accuracy": float, "shape_accuracy": float, "neither": float}."""
    ...

def evaluate_standard_accuracy(model: nn.Module, test_loader: DataLoader) -> float:
    """Standard top-1 accuracy on (image, label) loader."""
    ...
```

### Pseudo-code

```
model.eval()
texture_correct = shape_correct = total = 0
with no_grad():
    for images, shape_labels, texture_labels in conflict_loader:
        preds = model(images).argmax(dim=1)
        texture_correct += (preds == texture_labels).sum().item()
        shape_correct += (preds == shape_labels).sum().item()
        total += images.size(0)
texture_bias_ratio = texture_correct / (texture_correct + shape_correct + 1e-8)
return {
    "texture_bias_ratio": texture_bias_ratio,
    "texture_accuracy": texture_correct / total,
    "shape_accuracy": shape_correct / total,
    "neither": 1 - (texture_correct + shape_correct) / total,
}
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | measure_texture_bias | Full conflict-loader loop per pseudo-code |
| L-6-2 | evaluate_standard_accuracy | Plain top-1 accuracy loop |
| L-6-3 | Per-model results assembly | Run both metrics for ResNet-18 and VGG-11, package as dict |

---

## A-7: Gate evaluation [Complexity: 4, Budget: 4]

**Applied**: Direction + effect-size threshold gate

### API Signatures

```python
def evaluate_gate(resnet_bias: dict, vgg_bias: dict) -> dict:
    """Returns {"pass_gate": bool, "diff": float, "resnet_ratio": float, "vgg_ratio": float}."""
    ...

def write_gate_report(gate_result: dict, path: str) -> None:
    """Write gate_result as JSON to path."""
    ...
```

### Pseudo-code

```
diff = resnet_bias["texture_bias_ratio"] - vgg_bias["texture_bias_ratio"]
pass_gate = (diff > EFFECT_SIZE_THRESHOLD)  # direction (diff>0) implied by threshold>0
return {"pass_gate": pass_gate, "diff": diff,
        "resnet_ratio": resnet_bias["texture_bias_ratio"],
        "vgg_ratio": vgg_bias["texture_bias_ratio"]}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | evaluate_gate | Diff + threshold check |
| L-7-2 | write_gate_report | JSON dump to results/ |

---

## A-8: Visualization + orchestration [Complexity: 10, Budget: 10]

**Applied**: matplotlib standard plotting, script orchestration

### API Signatures

```python
def plot_gate_comparison(gate_result: dict, out_path: str) -> None:
    """Bar chart: VGG-11 vs ResNet-18 texture_bias_ratio, threshold line at 0.5. REQUIRED figure."""
    ...

def plot_confusion_shape_texture(bias_result: dict, out_path: str) -> None:
    """Bar/heatmap of texture_correct/shape_correct/neither counts."""
    ...

def plot_training_curves(resnet_history: dict, vgg_history: dict, out_path: str) -> None:
    """Line plot: test_acc_curve for both models vs epoch."""
    ...

def plot_per_class_texture_bias(bias_result: dict, out_path: str) -> None:
    """Per-class breakdown if per-class stats tracked; else skip gracefully."""
    ...

def main() -> None:
    """Full pipeline: data -> models -> train x2 -> evaluate x2 -> gate -> figures."""
    ...
```

### Pseudo-code (run.py main)

```
1. config.ensure_dirs(); config.check_dtd_present(DTD_DIR)
2. train_loader, test_loader = get_cifar10_loaders(BATCH_SIZE)
3. dtd_images = load_dtd_images(DTD_DIR)
4. stylized = build_stylized_cifar10(test_loader.dataset, dtd_images, SEED)
5. conflict_loader = get_conflict_loader(stylized, BATCH_SIZE)
6. vgg = build_vgg11_cifar(); resnet = build_resnet18_cifar()
7. vgg_hist = train_model(vgg, train_loader, test_loader, EPOCHS, "checkpoints/vgg11.pt")
8. resnet_hist = train_model(resnet, train_loader, test_loader, EPOCHS, "checkpoints/resnet18.pt")
9. vgg_bias = measure_texture_bias(vgg, conflict_loader)
10. resnet_bias = measure_texture_bias(resnet, conflict_loader)
11. gate = evaluate_gate(resnet_bias, vgg_bias); write_gate_report(gate, "results/gate.json")
12. plot_gate_comparison(gate, "figures/gate_comparison.png")
13. plot_confusion_shape_texture / plot_training_curves / plot_per_class_texture_bias (best-effort, try/except)
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | plot_gate_comparison | Required bar chart w/ threshold line |
| L-8-2 | plot_confusion_shape_texture | Confusion-style visualization |
| L-8-3 | plot_training_curves + plot_per_class_texture_bias | Remaining two figures |
| L-8-4 | run.py main() wiring | Full pipeline + logging/error handling (try/except around each stage) |

---

## External Dependencies (Base Hypothesis)

None. Green-field implementation, no prior hypothesis code reused.
