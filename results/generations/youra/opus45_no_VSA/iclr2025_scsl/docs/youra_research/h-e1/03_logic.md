# Logic: H-E1 (EXISTENCE / PoC)

**Hypothesis:** SR₀ ≈ 1.0 at initialization
**Type:** EXISTENCE — measurement-only

**Applied:** No KB match (generic diffusion/cuBLAS results only) — using brief's power-iteration HVP + `torch.autograd.grad(create_graph=True)` pattern.

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - new API design, no existing code to analyze
**Analyzed Path:** N/A
**Relevant Symbols:** None - new implementation

---

## A-1: Dataset setup [Complexity: 8, Budget: 8]

**Applied:** Standard PyTorch Dataset

### API Signatures

```python
class WaterbirdDataset(torch.utils.data.Dataset):
    def __init__(self, root: str, split: str = "train"):
        """Loads metadata.csv, builds group labels (0-3)."""
        ...

    def __len__(self) -> int: ...

    def __getitem__(self, idx: int) -> tuple[Tensor, int, int]:
        """Returns (img [3,224,224], label, group)."""
        ...

def get_group_loader(dataset: WaterbirdDataset, group_id: int, batch_size: int = 32) -> DataLoader:
    """Filters dataset to samples where group == group_id, wraps in DataLoader."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Metadata parsing | Read metadata.csv, derive group = 2*y + place |
| L-1-2 | Transforms | ImageNet norm, resize 224, RandomResizedCrop for train |
| L-1-3 | `__getitem__` | Load image, apply transform, return (img, label, group) |
| L-1-4 | `get_group_loader` | `Subset` by group mask + `DataLoader` |

---

## A-2: Model factory [Complexity: 4, Budget: 4]

**Applied:** Standard torchvision factory + seeding

### API Signatures

```python
def create_random_model(seed: int) -> torch.nn.Module:
    """ResNet-50, pretrained=False, fc -> Linear(2048, 2). Seeds torch before init."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | Seed | `torch.manual_seed(seed)` before construction |
| L-2-2 | Backbone | `torchvision.models.resnet50(weights=None)` |
| L-2-3 | Head replace | `model.fc = nn.Linear(2048, 2)` |
| L-2-4 | Return | `model.double()` if double precision used (see A-3) |

---

## A-3: HVP + power iteration [Complexity: 12, Budget: 2 subtasks]

**Applied:** Double-backward HVP (`torch.autograd.grad` twice, `create_graph=True`) + power iteration, per brief's reference implementation.

### API Signatures

```python
def compute_loss(model: nn.Module, loader: DataLoader) -> Tensor:
    """CrossEntropy loss over all batches in loader. Scalar."""
    ...

def hessian_vector_product(model: nn.Module, loader: DataLoader, v: Tensor) -> Tensor:
    """Hv via double backward. v: [P] flat -> returns [P] flat (P = total param count)."""
    ...

def compute_group_sharpness(model: nn.Module, loader: DataLoader, num_iterations: int = 20) -> float:
    """Power iteration for top Hessian eigenvalue (lambda_max) over loader's data."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| params (flat) | [P] | `torch.cat([p.view(-1) for p in model.parameters()])`, P ≈ 25M for ResNet-50 |
| v | [P] | random unit vector, `dtype=torch.float64` for stability |
| Hv | [P] | Hessian-vector product output |

### Pseudo-code

```
compute_loss(model, loader):
    total = 0; n = 0
    for x, y, _ in loader:
        total += CE(model(x), y) * x.size(0); n += x.size(0)
    return total / n

hessian_vector_product(model, loader, v):
    loss = compute_loss(model, loader)
    grads = autograd.grad(loss, model.parameters(), create_graph=True)
    flat_grads = cat([g.view(-1) for g in grads])
    # dot(flat_grads, v) then differentiate again = Hv
    grad_dot_v = dot(flat_grads, v)
    hvp = autograd.grad(grad_dot_v, model.parameters())
    return cat([h.reshape(-1) for h in hvp]).detach()

compute_group_sharpness(model, loader, num_iterations=20):
    P = sum(p.numel() for p in model.parameters())
    v = randn(P, dtype=float64); v /= norm(v)
    for _ in range(num_iterations):
        Hv = hessian_vector_product(model, loader, v)
        lambda_max = dot(v, Hv)
        v = Hv / (norm(Hv) + 1e-12)
    return lambda_max.item()
```

Note: model params must be `float64` (see A-2 L-2-4) to match NFR-2 double-precision requirement; `v` dtype must match.

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | `compute_loss` + `hessian_vector_product` | Batched loss accumulation, double-backward HVP |
| L-3-2 | `compute_group_sharpness` | Power iteration loop, Rayleigh quotient (lambda_max) |

---

## A-4: SR computation [Complexity: 6, Budget: 6]

**Applied:** Group aggregation over A-3 primitives

### API Signatures

```python
def compute_sharpness_ratio(model: nn.Module, dataset: WaterbirdDataset) -> float:
    """SR = mean(sharpness[minority]) / mean(sharpness[majority]). Groups from config.py."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | Loader per group | `get_group_loader` for each of 4 groups |
| L-4-2 | Minority sharpness | mean over MINORITY_GROUPS of `compute_group_sharpness` |
| L-4-3 | Majority sharpness | mean over MAJORITY_GROUPS of `compute_group_sharpness` |
| L-4-4 | Ratio | `sharpness_minority / sharpness_majority` |

---

## A-5: Multi-seed orchestration [Complexity: 6, Budget: 6]

### API Signatures

```python
def run_seed(seed: int, dataset: WaterbirdDataset) -> float:
    """create_random_model(seed) -> compute_sharpness_ratio -> SR value. Catches/logs per-seed errors."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | `run_seed` | model + SR, try/except with error log |
| L-5-2 | Seed loop | iterate config.SEEDS, collect sr_values list |
| L-5-3 | Skip-on-fail | continue on per-seed exception, warn |
| L-5-4 | Result assembly | pass sr_values to stats stage (A-6) |

---

## A-6: Stats + gate check [Complexity: 5, Budget: 5]

### API Signatures

```python
def compute_stats(sr_values: list[float]) -> dict:
    """Returns {mean, ci_low, ci_high} via scipy.stats.t.interval(0.95, ...)."""
    ...

def check_gate(mean_sr: float, ci: tuple[float, float]) -> bool:
    """0.9 <= mean_sr <= 1.1 and ci_low <= 1.0 <= ci_high. Report only, non-fatal."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | Mean/CI | `np.mean`, `scipy.stats.t.interval(0.95, df=n-1, loc=mean, scale=sem)` |
| L-6-2 | Gate check | boolean per success criteria, print result |
| L-6-3 | JSON write | `results/sr_values.json`: `{seeds, sr_values, mean, ci, gate_pass}` |
| L-6-4 | main() wiring | call after A-5 loop, before A-7 |

---

## A-7: Visualization [Complexity: 4, Budget: 4]

### API Signatures

```python
def plot_sr_comparison(sr_values: list[float], seeds: list[int], mean_sr: float, ci: tuple[float, float], out_path: str) -> None:
    """Scatter/errorbar of SR per seed + horizontal line at SR=1.0. Saves PNG."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | Scatter/errorbar | `plt.errorbar(seeds, sr_values, yerr=ci_halfwidth)` |
| L-7-2 | Reference line | `plt.axhline(1.0, linestyle='--')` |
| L-7-3 | Labels/legend | axis labels, title "SR at Initialization" |
| L-7-4 | Save | `plt.savefig(out_path)`, `figures/sr_comparison.png` |

---

## Total Subtask Budget

| Task | Budget | Used |
|------|--------|------|
| A-1 | 8 | 4 |
| A-2 | 4 | 4 |
| A-3 | 2 | 2 |
| A-4 | 6 | 4 |
| A-5 | 6 | 4 |
| A-6 | 5 | 4 |
| A-7 | 4 | 4 |
