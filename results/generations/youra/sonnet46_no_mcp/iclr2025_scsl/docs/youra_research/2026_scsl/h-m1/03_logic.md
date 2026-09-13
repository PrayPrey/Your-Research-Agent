# Logic: H-M1
# SGD Gradient Structure Analysis — Gradient Dominance Ratio (GDR)

**Hypothesis ID:** H-M1
**Type:** MECHANISM (INCREMENTAL — extends H-E1)
**Date:** 2026-05-04

Applied: DL API design pattern — fc-only backward pass for gradient norm measurement
Applied: incremental extension pattern — verified H-E1 API signatures from actual code

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual H-E1 code
**Analyzed Path**: `h-e1/code/`
**Relevant Symbols**:
- `build_model(num_classes=2, pretrained=True) -> nn.Module` — ResNet-50, fc=Linear(2048,2)
- `train_one_seed(cfg: TrainConfig, seed: int, device: str) -> None` — NOTE: no `analyzer` param in actual code; H-M1 adds it
- `WaterbirdsDataset.__getitem__` returns `{"image": Tensor, "core_label": int, "spurious_label": int}`
- `get_waterbirds_loader(root, split, batch_size, num_workers, augment=False) -> DataLoader`
- `TrainConfig`: `dataset, data_root, checkpoint_dir, epochs, checkpoint_interval=2, batch_size=128, lr=1e-3, momentum=0.9, weight_decay=1e-4, seeds=[1,2,3,4,5], num_workers=4`

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code — h-e1/code/)

```python
# From: h-e1/code/train.py (ACTUAL CODE)
def build_model(num_classes: int = 2, pretrained: bool = True) -> nn.Module:
    """ResNet-50, model.fc = Linear(2048, num_classes)."""
    ...

def train_one_seed(cfg: TrainConfig, seed: int, device: str) -> None:
    # Actual signature: NO analyzer param. H-M1 overrides this with extended version.
    ...

# From: h-e1/code/data/waterbirds.py (ACTUAL CODE)
def get_waterbirds_loader(
    root: str,
    split: str,
    batch_size: int,
    num_workers: int,
    augment: bool = False,
) -> DataLoader:
    # batch items: {"image": Tensor[3,224,224], "core_label": int, "spurious_label": int}
    ...

# From: h-e1/code/config.py (ACTUAL CODE)
@dataclass
class TrainConfig:
    dataset: str
    data_root: str
    checkpoint_dir: str
    epochs: int
    checkpoint_interval: int = 2
    batch_size: int = 128
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    seeds: List[int] = field(default_factory=lambda: [1, 2, 3, 4, 5])
    num_workers: int = 4
```

**Verified from**: `h-e1/code/` (actual implementation)

---

## A-4: GradientAlignmentAnalyzer [Complexity: 14, Budget: 4 subtasks]

**Applied**: PyTorch frozen-backbone gradient instrumentation pattern

### API Signatures

```python
class GradientAlignmentAnalyzer:
    def __init__(self, model: nn.Module, device: str) -> None:
        """Store model + device; init history buffers."""
        # self._spurious_norms: List[float] = []
        # self._core_norms: List[float] = []
        # self._gdr_series: List[float] = []

    def extract_features(
        self,
        loader: DataLoader,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Frozen backbone forward pass.
        Returns (features, core_labels, spurious_labels).
        features: [N, 2048], core_labels: [N,], spurious_labels: [N,]
        """
        # model.eval() + torch.no_grad()
        # collect batch["image"] through model up to avgpool (pre-fc)
        # collect batch["core_label"], batch["spurious_label"]

    def compute_label_gradient_norm(
        self,
        features: torch.Tensor,     # [N, 2048]
        label_tensor: torch.Tensor, # [N,]  (either core or spurious labels)
        criterion: nn.Module,
    ) -> float:
        """Single fc-only backward pass. Returns L2 grad norm of fc.weight."""
        # model.fc.zero_grad()
        # logits = model.fc(features)  # [N, num_classes]
        # loss = criterion(logits, label_tensor)
        # loss.backward()
        # grad_norm = model.fc.weight.grad.norm().item()
        # return grad_norm

    def log_epoch_gradients(
        self,
        loader: DataLoader,
        criterion: nn.Module,
    ) -> Dict[str, float]:
        """Extract features, compute GDR, append to history.
        Returns {'spurious_grad_norm': float, 'core_grad_norm': float, 'gdr': float}
        """
        # features, core_labels, spurious_labels = self.extract_features(loader)
        # spurious_norm = self.compute_label_gradient_norm(features, spurious_labels, criterion)
        # core_norm = self.compute_label_gradient_norm(features, core_labels, criterion)
        # gdr = spurious_norm / (core_norm + 1e-8)
        # append to history buffers
        # return dict

    def get_history(self) -> Dict[str, List[float]]:
        """Returns accumulated history across all log_epoch_gradients calls.
        Keys: 'spurious_grad_norms', 'core_grad_norms', 'gdr_series'
        Lengths: 15 (one per checkpoint at every 2 epochs over 30 epochs)
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| features | [N, 2048] | N=4795 train samples |
| core_labels | [N,] | dtype=torch.long |
| spurious_labels | [N,] | dtype=torch.long |
| logits (fc out) | [N, 2] | num_classes=2 |
| fc.weight.grad | [2, 2048] | grad_norm = .norm().item() |

### Pseudo-code: extract_features

```
model.eval()
features_list, core_list, spurious_list = [], [], []
with torch.no_grad():
    for batch in loader:
        x = batch["image"].to(device)          # [B, 3, 224, 224]
        # forward up to avgpool, skip fc
        feat = backbone_forward(model, x)       # [B, 2048]
        features_list.append(feat.cpu())
        core_list.append(batch["core_label"])
        spurious_list.append(batch["spurious_label"])
return cat(features_list), cat(core_list), cat(spurious_list)

# backbone_forward: use model with hook or run model and extract avgpool output
# Preferred: register forward hook on model.avgpool OR use:
#   feat = model.avgpool(model.layer4(...)).flatten(1)
# Simpler: full forward then access intermediate via hook
```

### Pseudo-code: compute_label_gradient_norm

```
features = features.to(device).requires_grad_(False)
features_detached = features.detach()
model.fc.zero_grad()
logits = model.fc(features_detached)            # [N, 2]
loss = criterion(logits, label_tensor.to(device))
loss.backward()
grad_norm = model.fc.weight.grad.norm(p=2).item()
model.fc.zero_grad()  # cleanup
return grad_norm
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | extract_features | Frozen backbone pass returning (features, core_labels, spurious_labels) |
| L-4-2 | compute_label_gradient_norm | fc-only backward, L2 norm of fc.weight.grad |
| L-4-3 | log_epoch_gradients | Compose extract+2x compute_grad_norm, append history, return GDR dict |
| L-4-4 | get_history | Return accumulated dict of lists, verify length=15 after full training |

---

## A-5: GDR Metric & Wilcoxon [Complexity: 10, Budget: 2 subtasks]

**Applied**: Standard PyTorch + scipy.stats

### API Signatures

```python
def compute_mean_early_gdr(
    gdr_series: List[float],        # length=15, one per checkpoint (epochs 2,4,...,30)
    early_epochs: List[int],        # e.g. [2, 4, 6]
    checkpoint_interval: int,       # 2
) -> float:
    """Mean GDR over early window checkpoints.
    early_epochs=[2,4,6] → indices [0,1,2] in gdr_series.
    Returns mean of gdr_series[0:3].
    """
    # indices = [(e // checkpoint_interval) - 1 for e in early_epochs]  → [0, 1, 2]
    # return np.mean([gdr_series[i] for i in indices])

def run_wilcoxon_test(
    spurious_norms_early: np.ndarray,  # shape (3,) — 3 early checkpoints
    core_norms_early: np.ndarray,      # shape (3,)
) -> Dict[str, float]:
    """One-sided Wilcoxon signed-rank test: spurious > core.
    Returns {'stat': float, 'p_value': float}.
    """
    # from scipy.stats import wilcoxon
    # stat, p = wilcoxon(spurious_norms_early, core_norms_early, alternative='greater')
    # return {'stat': stat, 'p_value': p}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | compute_mean_early_gdr | Index extraction from gdr_series + mean |
| L-5-2 | run_wilcoxon_test | scipy.stats.wilcoxon with alternative='greater' |

---

## A-7: Visualization [Complexity: 10, Budget: 2 subtasks]

**Applied**: Standard matplotlib/seaborn pattern

### API Signatures

```python
def plot_mean_early_gdr_bar(
    analysis: Dict[str, Any],
    # expects: analysis['mean_early_gdr_per_seed']: List[float] length=3
    #          analysis['std_early_gdr']: float
    figures_dir: str,
) -> str:
    """Bar chart: mean Early GDR per seed vs 1.0 threshold line, with error bars.
    Returns absolute path to saved figure (figures_dir/mean_early_gdr_bar.png).
    """
    ...

def plot_gdr_timeline(
    seed_results: Dict[int, Dict[str, Any]],
    # seed_results[seed]['gdr_series']: List[float] length=15
    delta_series: np.ndarray,   # shape (15,) — H-E1 delta(t) values
    figures_dir: str,
) -> str:
    """Line plot: GDR(t) per seed + mean, overlaid with delta(t) from H-E1 on secondary axis.
    Returns absolute path to saved figure (figures_dir/gdr_timeline.png).
    """
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | plot_mean_early_gdr_bar | Bar chart with error bars + threshold line at 1.0 |
| L-7-2 | plot_gdr_timeline | Dual-line with secondary y-axis for delta(t) overlay |

---

## A-9: End-to-End Validation [Complexity: 10, Budget: 2 subtasks]

**Applied**: Standard PyTorch + assertion-based gate pattern

### API Signatures

```python
def check_gate(analysis: Dict[str, Any], cfg: GDRConfig) -> bool:
    """Gate logic: mean_early_GDR > 1.0 in >= min_seeds_pass seeds AND Wilcoxon p < p_threshold.
    Raises AssertionError with details if gate fails (for hard-fail mode).
    Returns True if PASS, False if FAIL.
    """
    # seeds_pass = sum(1 for g in analysis['mean_early_gdr_per_seed'] if g > 1.0)
    # wilcoxon_pass = sum(1 for r in analysis['wilcoxon_results'].values() if r['p_value'] < cfg.p_threshold)
    # gate_pass = (seeds_pass >= cfg.min_seeds_pass) and (wilcoxon_pass >= cfg.min_seeds_pass)
    # assert gate_pass, f"Gate FAILED: seeds_pass={seeds_pass}, wilcoxon_pass={wilcoxon_pass}"
    # return gate_pass
```

### Results Schema (summary.json)

```json
{
  "hypothesis": "H-M1",
  "gate": "PASS",
  "mean_early_gdr": 1.45,
  "std_early_gdr": 0.12,
  "mean_early_gdr_per_seed": {"1": 1.38, "2": 1.52, "3": 1.44},
  "wilcoxon_results": {
    "1": {"stat": 0.0, "p_value": 0.031},
    "2": {"stat": 0.0, "p_value": 0.031},
    "3": {"stat": 0.0, "p_value": 0.031}
  },
  "pearson_correlation": {
    "1": {"r": 0.65, "p_value": 0.008},
    "2": {"r": 0.71, "p_value": 0.003},
    "3": {"r": 0.68, "p_value": 0.005}
  },
  "per_seed": {
    "1": {
      "gdr_series": [1.8, 1.7, 1.5, 1.4, 1.3, 1.2, 1.1, 1.05, 1.02, 1.01, 1.0, 0.99, 0.98, 0.97, 0.96],
      "spurious_grad_norms": [],
      "core_grad_norms": [],
      "mean_early_gdr": 1.67,
      "wilcoxon_stat": 0.0,
      "wilcoxon_p": 0.031
    }
  },
  "figures": ["mean_early_gdr_bar.png", "gdr_timeline.png", "grad_norm_dual_axis.png", "early_late_violin.png"],
  "seeds_passed_gdr": 3,
  "seeds_passed_wilcoxon": 3,
  "gate_criteria": {"min_seeds_pass": 2, "p_threshold": 0.05, "gdr_threshold": 1.0}
}
```

### Gate Assertion Logic

```python
# Hard gate (run_experiment.py):
early_gdr_per_seed = [analysis['mean_early_gdr_per_seed'][s] for s in seeds]
assert np.mean(early_gdr_per_seed) > 1.0, \
    f"GATE FAIL: mean_early_GDR={np.mean(early_gdr_per_seed):.4f} <= 1.0"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | check_gate | Assertion logic with per-seed GDR > 1.0 count + Wilcoxon p count |
| L-9-2 | summary_json | Write full results schema to results/h-m1/summary.json |

---

## H-M1 Train Override (A-3 reference)

The actual H-E1 `train_one_seed` signature is `(cfg, seed, device) -> None`.
H-M1 must override with an extended version:

```python
def train_one_seed(
    cfg: TrainConfig,
    seed: int,
    device: str,
    analyzer: "GradientAlignmentAnalyzer",  # NEW param
) -> Dict[str, Any]:
    """Extended H-E1 trainer with gradient logging at checkpoint epochs.
    At each checkpoint_interval epoch: calls analyzer.log_epoch_gradients(train_loader, criterion).
    Returns: {'seed': int, 'gdr_series': List[float], 'spurious_grad_norms': List[float], 'core_grad_norms': List[float]}
    """
    # ... identical training loop ...
    # if epoch % cfg.checkpoint_interval == 0:
    #     result = analyzer.log_epoch_gradients(train_loader, criterion)
    #     # accumulate
```

**Note**: H-M1 uses batch_size=64 (override from H-E1 default of 128), seeds=[1,2,3] (3 seeds).
