# Logic: H-E1 (EXISTENCE PoC)

**Date:** 2026-08-29
**Scope:** High-complexity tasks only (A-3, A-5). Budget: 4 subtasks.

Applied: gradient-accumulation-incremental-SVD (torch.svd_lowrank streaming buffer pattern).

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze, Serena skipped (no base_hypothesis or src/ present)
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-3: Gradient Subspace Accumulator [Complexity: 12, Budget: 4]

**Applied**: incremental SVD via buffered flat-grad matrix + `torch.linalg.svd`

### API Signatures

```python
class GradientSubspaceAccumulator:
    def __init__(self, num_params: int, rank_k: int = 50, accumulation_epochs: int = 10):
        """Buffers flat grads per epoch. buffer: [accumulation_epochs, num_params]."""
        ...

    def accumulate(self, model: nn.Module, epoch: int) -> None:
        """Call once per epoch (after backward, before optimizer.step aggregation).
        Stores get_flat_grad(model) into buffer[epoch - 1]."""
        ...

    def compute_subspace(self) -> Tensor:
        """SVD on buffer -> top-k left singular vectors.
        Returns S: [num_params, rank_k]."""
        ...

    def measure_alignment(self, direction_vec: Tensor) -> float:
        """direction_vec: [num_params]. Returns scalar in [0,1]:
        sum_i cos_sim(S[:,i], direction_vec)^2 (projection energy)."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| buffer | [10, num_params] | one row per epoch grad (num_params ~25.6M for resnet50 fc-only or full net) |
| U | [10, 10] | left singular vectors (economy SVD, rank <= 10) |
| S_vals | [10] | singular values |
| Vt | [10, num_params] | right singular vectors, rows = principal grad directions |
| S (subspace) | [num_params, rank_k] | rank_k = min(50, 10) columns from Vt.T |
| direction_vec | [num_params] | from compute_direction() |

### Pseudo-code

```
# accumulate(): epoch in 1..10
buffer[epoch-1] = get_flat_grad(model).detach().cpu()

# compute_subspace(): after epoch 10
# buffer: [10, num_params] -> economy SVD (num_params >> 10, so SVD on buffer.T not needed;
# use buffer @ buffer.T trick or torch.linalg.svd(buffer, full_matrices=False))
U, S_vals, Vt = torch.linalg.svd(buffer, full_matrices=False)  # Vt: [10, num_params]
k = min(rank_k, Vt.shape[0])
S = Vt[:k].T  # [num_params, k], orthonormal columns = top-k grad directions
return S

# measure_alignment(direction_vec):
d = direction_vec / direction_vec.norm()
proj_energy = sum((S[:, i] @ d) ** 2 for i in range(S.shape[1]))
return proj_energy.item()  # in [0,1], fraction of direction captured by subspace
```

### Subtasks [2/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-A3-1 | Buffer + accumulate | Init buffer tensor, get_flat_grad hook, per-epoch store |
| L-A3-2 | SVD + alignment | compute_subspace via torch.linalg.svd, measure_alignment projection-energy calc |

---

## A-5: Training Loop Integration [Complexity: 13, Budget: 2]

**Applied**: standard ERM SGD loop with StepLR, hooks for accumulator + direction calc

### API Signatures

```python
def train_loop() -> dict[int, dict[str, float]]:
    """Full ERM training, epochs 1..NUM_EPOCHS.
    Returns {epoch: {"spurious_alignment": float, "core_alignment": float}} for epoch in LOG_EPOCHS."""
    ...

def save_checkpoint(model: nn.Module, path: str) -> None:
    """torch.save(model.state_dict(), path)"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| img | [B, 3, 224, 224] | B=BATCH_SIZE=128 |
| label | [B] | binary class |
| group | [B] | group id for pair sampling |
| logits | [B, 2] | model output |
| grad_vec | [num_params] | per get_flat_grad |
| spurious_dir, core_dir | [num_params] | from compute_direction |
| S | [num_params, 50] | from accumulator.compute_subspace() |

### Pseudo-code

```
train_loop():
    model = build_resnet50(2).cuda()
    opt = SGD(model.parameters(), lr=LR, momentum=MOMENTUM, weight_decay=WEIGHT_DECAY)
    sched = StepLR(opt, milestones=STEP_MILESTONES, gamma=GAMMA)
    train_loader, val_loader, test_loader = get_dataloaders(DATA_ROOT, BATCH_SIZE)
    spurious_pairs, core_pairs = get_direction_pairs(train_loader.dataset)
    accumulator = GradientSubspaceAccumulator(num_params, SUBSPACE_RANK, ACCUMULATION_EPOCHS)
    results = {}
    S = None

    for epoch in 1..NUM_EPOCHS:
        for img, label, group in train_loader:
            opt.zero_grad()
            loss = CrossEntropyLoss()(model(img.cuda()), label.cuda())
            loss.backward()
            opt.step()
        sched.step()

        if epoch <= ACCUMULATION_EPOCHS:
            accumulator.accumulate(model, epoch)
        if epoch == ACCUMULATION_EPOCHS:
            S = accumulator.compute_subspace()
            save_checkpoint(model, f"checkpoint_epoch{epoch}.pt")

        if epoch in LOG_EPOCHS:
            spurious_dir = compute_direction(model, train_loader, spurious_pairs)
            core_dir = compute_direction(model, train_loader, core_pairs)
            results[epoch] = {
                "spurious_alignment": accumulator.measure_alignment(spurious_dir),
                "core_alignment": accumulator.measure_alignment(core_dir),
            }
            log to console + CSV

    return results
```

### Subtasks [2/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-A5-1 | Loop skeleton | Model/opt/sched/loader init, standard train step, StepLR |
| L-A5-2 | Hook wiring | accumulate/compute_subspace calls, LOG_EPOCHS alignment calc + checkpoint save |

---

## Subtask Budget Summary

| Task | Budget | Used |
|------|--------|------|
| A-3 | 2 | 2 |
| A-5 | 2 | 2 |
| **Total** | **4** | **4** |
