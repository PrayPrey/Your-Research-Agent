# Logic: H-E1 (EXISTENCE / PoC)

Applied: GradCAM epoch-wise attribution ratio pattern (pytorch-grad-cam standard usage)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Dataset setup [Complexity: 10, Budget: 1 subtask]

**Applied**: torchvision Dataset + PIL mask loading

### API Signatures

```python
class WaterbirdsDataset(Dataset):
    def __init__(self, root_dir: str, split: str, transform=None):
        """split: 'train' | 'val' | 'test'"""
        ...

    def __len__(self) -> int: ...

    def __getitem__(self, idx: int) -> tuple[Tensor, int, Tensor, Tensor]:
        """Returns (image, label, spurious_mask, core_mask)"""
        ...

def get_dataloaders(root_dir: str, batch_size: int) -> dict[str, DataLoader]: ...
def download_waterbirds(root_dir: str) -> None: ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| image | [3, 224, 224] | ImageNet normalized |
| label | scalar int | 0=landbird, 1=waterbird |
| spurious_mask | [224, 224] | binarized background mask |
| core_mask | [224, 224] | binarized bird mask |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A1-1 | Dataset + loaders | `WaterbirdsDataset.__getitem__` loads image + resizes/binarizes segmentation masks to 224x224 via `PIL.Image.resize` + threshold; `get_dataloaders` wraps train/val/test splits |

---

## A-3: GradCAM tracker [Complexity: 9, Budget: 1 subtask]

**Applied**: pytorch-grad-cam `GradCAM` on `layer4[-1]`

### API Signatures

```python
class AttributionTracker:
    def __init__(self, model: nn.Module, target_layer):
        """target_layer: model.layer4[-1]"""
        ...

    def compute_attribution_ratio(self, dataloader: DataLoader, device: str) -> float:
        """Mean spurious/core ratio over dataloader subset."""
        ...

    def log_epoch(self, epoch: int, dataloader: DataLoader, device: str) -> float:
        """Appends (epoch, ratio) to self.epoch_ratios, returns ratio."""
        ...

    epoch_ratios: list[tuple[int, float]]
```

### Pseudo-code

```
compute_attribution_ratio(loader, device):
  ratios = []
  for image, label, spurious_mask, core_mask in loader:      # [B,3,224,224], [B], [B,224,224], [B,224,224]
      cam = GradCAM(model, target_layer)(image, targets=label)  # [B, 224, 224]
      spurious_attr = sum(cam * spurious_mask, dim=(1,2))        # [B]
      core_attr = sum(cam * core_mask, dim=(1,2)) + 1e-8         # [B]
      ratios.extend((spurious_attr / core_attr).tolist())
  return mean(ratios)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A3-1 | GradCAM ratio computation | `AttributionTracker` wraps `pytorch_grad_cam.GradCAM`; `log_epoch` runs `compute_attribution_ratio` on fixed 500-sample subset each epoch and appends to `epoch_ratios` |
