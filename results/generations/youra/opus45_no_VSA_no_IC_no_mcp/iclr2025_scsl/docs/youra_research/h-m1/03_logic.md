# Logic: H-M1 (MECHANISM)

**Applied**: gradient-hook regional norm tracking (pytorch-grad-cam forward/backward hook pattern)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-3: GradientNormTracker [Complexity: 12, Budget: 3+3+4+2]

**Applied**: forward/backward hook activation-gradient capture (pytorch-grad-cam Activations-Gradients pattern)

### API Signatures

```python
class GradientNormTracker:
    def __init__(self, model: nn.Module, target_layer: nn.Module):
        """Register fwd/bwd hooks on target_layer. Stores activation, gradient."""
        self.activations: Optional[Tensor] = None  # [B, C, H', W']
        self.gradients: Optional[Tensor] = None     # [B, C, H', W']
        self._fwd_handle = target_layer.register_forward_hook(self._save_activation)
        self._bwd_handle = target_layer.register_full_backward_hook(self._save_gradient)

    def _save_activation(self, module: nn.Module, input: tuple, output: Tensor) -> None:
        """output: [B, C, H', W'] -> store detached."""
        ...

    def _save_gradient(self, module: nn.Module, grad_input: tuple, grad_output: tuple) -> None:
        """grad_output[0]: [B, C, H', W'] -> store detached."""
        ...

    def compute_regional_gradient_norms(
        self, bird_mask: Tensor, background_mask: Tensor
    ) -> tuple[float, float]:
        """masks: [B, H, W] binary in {0,1}. Resized (nearest) to [H', W'].
        Returns: (core_norm, spurious_norm) -- batch-mean L2 norm of gradient
        elements within each mask region."""
        ...

    def remove_hooks(self) -> None:
        """Call self._fwd_handle.remove(); self._bwd_handle.remove()."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| activations/gradients | [B, 2048, 7, 7] | layer4 output for ResNet-50, input 224x224 |
| bird_mask, background_mask | [B, 224, 224] | resized via F.interpolate(mode="nearest") to [B,7,7] |
| masked_grad | [B, C, H', W'] | gradients * mask.unsqueeze(1) |

### Pseudo-code (regional norm computation)

```
1. grad = self.gradients                       # [B, C, H', W']
2. mask_r = F.interpolate(mask[:,None].float(), size=(H',W'), mode="nearest")  # [B,1,H',W']
3. region_grad = grad * mask_r                  # zero out non-region elements
4. norm_per_sample = region_grad.flatten(1).norm(dim=1)  # [B]
5. return norm_per_sample.mean().item()
   (compute once with bird_mask -> core_norm, once with background_mask -> spurious_norm)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A3-1 | Hook registration | `__init__`, `_save_activation`, `_save_gradient`, `remove_hooks` |
| L-A3-2 | Mask resize utility | Nearest-neighbor resize [B,H,W] -> [B,H',W'] via F.interpolate |
| L-A3-3 | Regional norm compute | `compute_regional_gradient_norms` core logic (mask, flatten, L2 norm) |
| L-A3-4 | Edge cases | Empty-mask guard (region sum==0 -> norm=0.0), dtype/device alignment |

---

## A-4: Training Loop [Complexity: 10, Budget: 2+3+3+2]

**Applied**: standard PyTorch SGD training loop + per-batch hook-based metric aggregation

### API Signatures

```python
def train_one_epoch(
    model: nn.Module,
    tracker: GradientNormTracker,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    device: torch.device,
) -> tuple[float, float, float]:
    """One epoch. Returns (avg_loss, mean_core_norm, mean_spurious_norm)."""
    ...

def run_training(config: Config, seed: int) -> list[dict]:
    """Full run for one seed. Returns per-epoch records:
    [{"epoch": int, "core_norm": float, "spurious_norm": float, "ratio": float}, ...]"""
    ...

def main() -> None:
    """Loop seeds in config.seeds, call run_training, save via evaluate.save_metrics."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| image | [B, 3, 224, 224] | ImageNet-normalized |
| label | [B] | long, {0,1} |
| bird_mask, background_mask | [B, 224, 224] | float/binary |
| logits | [B, 2] | model output |

### Pseudo-code (train_one_epoch)

```
1. model.train()
2. for image, label, bird_mask, bg_mask in loader:
3.     optimizer.zero_grad()
4.     logits = model(image)                       # [B, 2]
5.     loss = criterion(logits, label)
6.     loss.backward()                              # triggers tracker hooks
7.     core_norm, spurious_norm = tracker.compute_regional_gradient_norms(bird_mask, bg_mask)
8.     optimizer.step()
9.     accumulate loss.item(), core_norm, spurious_norm (running means)
10. return avg_loss, mean_core_norm, mean_spurious_norm
```

### Pseudo-code (run_training)

```
1. set_seed(seed); tracker = GradientNormTracker(model, model.layer4[-1])
2. optimizer = SGD(model.parameters(), lr, momentum, weight_decay)
3. scheduler = MultiStepLR(optimizer, milestones=step_sizes, gamma)
4. records = []
5. for epoch in range(1, config.epochs+1):
6.     loss, core, spur = train_one_epoch(...)
7.     ratio = spur / core if core > 0 else float("inf")
8.     records.append({"epoch": epoch, "core_norm": core, "spurious_norm": spur, "ratio": ratio})
9.     scheduler.step()
10. tracker.remove_hooks()
11. return records
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A4-1 | train_one_epoch | Batch loop, loss backward, running-mean aggregation of norms |
| L-A4-2 | run_training | Seed set, optimizer/scheduler setup, epoch loop, record collection |
| L-A4-3 | main + I/O | Multi-seed orchestration, checkpoint/record persistence to output_dir |
</content>
