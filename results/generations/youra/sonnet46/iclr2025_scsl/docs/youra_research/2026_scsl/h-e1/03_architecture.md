---
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
phase: Phase 3
generated_at: '2026-03-16'
---

# Architecture: H-E1
## Normalized Gradient Norm as Minority Group Proxy (Existence PoC)

**Applied: No domain matches found in Archon KB (similarity 0.32–0.44, diffusion model content only) — standard PyTorch patterns used**

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project — no existing codebase to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. Standard PyTorch ERM + register_forward_hook pattern.

---

## File Organization

```
h-e1/
├── src/
│   ├── dataset.py       # WaterbirdsDataset, get_dataloaders()
│   ├── model.py         # get_model(), GradientNormAnalyzer
│   ├── train.py         # train_epoch(), collect_gradnorms()
│   ├── evaluate.py      # compute_metrics(), gate_check()
│   └── visualize.py     # plot_gate_metrics(), plot_trajectory(), etc.
├── run_experiment.py    # Main CLI entry point
└── outputs/h-e1/
    ├── checkpoints/     # epoch_1.pt, epoch_3.pt, epoch_5.pt, epoch_10.pt
    ├── figures/         # gate_metrics.png, trajectory.png, distribution_epoch5.png,
    │                    # balance_heatmap.png, feature_norms.png
    ├── gradnorm_epoch_1.npz
    ├── gradnorm_epoch_3.npz
    ├── gradnorm_epoch_5.npz
    ├── gradnorm_epoch_10.npz
    ├── train_log.csv
    └── results.json
```

---

## Module Structure

### WaterbirdsDataset (`src/dataset.py`)

**Dependencies**: torch, torchvision, pandas, PIL

```python
class WaterbirdsDataset(Dataset):
    def __init__(self, root: str, split: str = 'train',
                 transform=None): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> tuple[Tensor, int, int]: ...
    # Returns: (image, y_class, place_label)
    # group_id = y * 2 + place  (0=G0,1=G1,2=G2,3=G3)

def get_dataloaders(
    root: str,
    batch_size: int = 128,
    num_workers: int = 4,
) -> dict[str, DataLoader]:
    # Keys: 'train_shuffle' (training), 'train_ordered' (gradnorm collection), 'val'
    ...
```

---

### GradientNormAnalyzer + get_model (`src/model.py`)

**Dependencies**: torch, torchvision

```python
def get_model(device: torch.device) -> nn.Module:
    # ResNet-50 pretrained, model.fc replaced with nn.Linear(2048, 2)
    ...

class GradientNormAnalyzer:
    def __init__(self, model: nn.Module): ...
    def _register_hooks(self) -> None:
        # register_forward_hook on model.fc to capture h(x_i) in R^2048
        ...
    def compute_batch_norms(
        self,
        images: Tensor,    # (B, 3, 224, 224)
        labels: Tensor,    # (B,)
    ) -> tuple[Tensor, Tensor, Tensor]:
        # Uses outer-product decomposition (vectorized, no per-sample backward):
        #   g_tilde_i = ||p_i - y_i_onehot||  (residual norm = g_raw / h_norm)
        #   g_raw_i   = ||p_i - y_i_onehot|| * h_norm_i
        # Returns: g_raw (B,), g_tilde (B,), h_norm (B,)  — all CPU tensors
        ...
    def clear(self) -> None:
        # Clear cached features dict
        ...
```

---

### Training (`src/train.py`)

**Dependencies**: src.model (GradientNormAnalyzer), src.dataset, torch

```python
def set_seed(seed: int = 1) -> None:
    # Sets torch, numpy, random seeds + cudnn deterministic
    ...

def train_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: Optimizer,
    device: torch.device,
) -> dict[str, float]:
    # Standard ERM forward+backward+step
    # Returns: {'loss': float, 'acc': float}
    ...

def collect_gradnorms(
    model: nn.Module,
    analyzer: GradientNormAnalyzer,
    loader: DataLoader,    # train_ordered (shuffle=False)
    device: torch.device,
    epoch: int,
    output_dir: str,
) -> dict[str, np.ndarray]:
    # model.eval() mode — no BN updates during collection
    # Iterates full 4,795-sample train set
    # Returns and saves to outputs/h-e1/gradnorm_epoch_{epoch}.npz:
    #   keys: g_raw, g_tilde, h_norm, sample_indices, group_labels, class_labels
    ...
```

---

### Evaluation (`src/evaluate.py`)

**Dependencies**: numpy, sklearn, src.train (collect_gradnorms output)

```python
def compute_metrics(
    g_tilde: np.ndarray,      # (N,)
    group_labels: np.ndarray, # (N,) values in {0,1,2,3}
    class_labels: np.ndarray, # (N,) values in {0,1}
) -> dict[str, float]:
    # Computes: ratio, auc, balance_deviation
    # Secondary: per_group_mean_gtilde, per_group_mean_hnorm, per_group_mean_graw
    # minority = (group_labels == 1) | (group_labels == 2)
    ...

def gate_check(metrics: dict[str, float]) -> tuple[bool, dict[str, bool]]:
    # Checks: ratio >= 3.0, auc > 0.70, balance_deviation <= 0.10
    # Returns: (all_pass, {criterion: pass_bool})
    ...

def verify_mechanism_activated(
    epoch_results: dict[str, float],
) -> tuple[bool, dict[str, bool]]:
    # Checks: hook_fired, ratio_above_chance > 1.5, auc_above_random > 0.55,
    #         feature_norms_equalized (h_norm_std_ratio < 0.5)
    ...

def save_results(
    per_epoch_metrics: dict[int, dict],
    gate_results: dict,
    secondary_metrics: dict,
    output_path: str,
) -> None:
    # Writes results.json per FR-7.1 schema
    ...
```

---

### Visualization (`src/visualize.py`)

**Dependencies**: matplotlib, seaborn, numpy

```python
def plot_gate_metrics(
    per_epoch_metrics: dict[int, dict],
    output_path: str,  # outputs/h-e1/figures/gate_metrics.png
) -> None:
    # 3-panel bar chart: (a) ratio, (b) AUC, (c) balance_deviation
    # Dashed threshold lines at 3.0, 0.70, 0.10
    ...

def plot_trajectory(
    per_epoch_metrics: dict[int, dict],
    output_path: str,  # outputs/h-e1/figures/trajectory.png
) -> None:
    # Line plot: mean g_tilde per group (G0-G3) across epochs, log-scale y-axis
    ...

def plot_distribution(
    gradnorm_data: dict[str, np.ndarray],  # from gradnorm_epoch_5.npz
    output_path: str,  # outputs/h-e1/figures/distribution_epoch5.png
) -> None:
    # Overlaid KDE: minority (G1+G2) vs majority (G0+G3) g_tilde at T_id=5
    ...

def plot_balance_heatmap(
    gradnorm_data: dict[str, np.ndarray],
    output_path: str,  # outputs/h-e1/figures/balance_heatmap.png
) -> None:
    # 4x2 heatmap: group (G0-G3) x class (0,1) in top-25% vs full train set
    ...

def plot_feature_norms(
    gradnorm_data: dict[str, np.ndarray],
    output_path: str,  # outputs/h-e1/figures/feature_norms.png
) -> None:
    # Box plots: ||h(x_i)|| per group at T_id=5 (BatchNorm equalization check)
    ...
```

---

### Main Entry Point (`run_experiment.py`)

**Dependencies**: all src modules, argparse

```python
def parse_args() -> argparse.Namespace:
    # --data-root: str (default: .data_cache/datasets/waterbirds/)
    # --output-dir: str (default: outputs/h-e1/)
    # --seed: int (default: 1)
    # --smoke-test: flag (10 batches only, verifies hook fires)
    ...

def main(args: argparse.Namespace) -> None:
    # 1. set_seed(args.seed)
    # 2. get_dataloaders() -> loaders
    # 3. get_model() -> model; GradientNormAnalyzer(model) -> analyzer
    # 4. Training loop (epochs 1-10):
    #    a. train_epoch(model, loaders['train_shuffle'], ...)
    #    b. if epoch in {1, 3, 5, 10}: collect_gradnorms(...) -> gradnorm_data
    #       compute_metrics(gradnorm_data) -> epoch_metrics
    #       gate_check(epoch_metrics) -> (pass, details)
    #       print per-epoch gate metric summary (FR-7.2)
    #    c. save CSV log row (epoch, loss, acc, ratio, auc, balance_dev)
    #    d. save checkpoint at epochs 1, 3, 5, 10
    # 5. generate all 5 figures
    # 6. save_results(per_epoch_metrics, gate_results, ...)
    ...
```

---

## Module Dependencies

```
run_experiment.py
  ├── src/dataset.py
  ├── src/model.py
  ├── src/train.py    -> src/model.py
  ├── src/evaluate.py
  └── src/visualize.py
```

---

## Key Algorithmic Note: Outer-Product Decomposition

For CE loss, per-sample gradient norm avoids O(N) backward passes:
```
g_tilde_i = ||p_i - y_i_onehot||    (residual norm — vectorized over batch)
g_raw_i   = g_tilde_i * h_norm_i
```
`p_i` = softmax(logits_i), `y_i_onehot` = one-hot label.
This is computed in `GradientNormAnalyzer.compute_batch_norms()` via a single forward pass.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Dataset Module | WaterbirdsDataset + get_dataloaders(), transforms, metadata.csv parsing | 8 | 2+1+1+4 |
| A-2 | Model + Analyzer | get_model() + GradientNormAnalyzer with FC forward hook + outer-product decomposition | 12 | 3+2+4+3 |
| A-3 | Training Loop | train_epoch(), collect_gradnorms(), seed setup, CSV logging, checkpoint saving | 11 | 3+2+3+3 |
| A-4 | Evaluation + Gate | compute_metrics() (ratio, AUC, balance_dev), gate_check(), save_results() | 9 | 2+2+3+2 |
| A-5 | Visualization | All 5 figures (gate_metrics, trajectory, distribution, heatmap, feature_norms) | 9 | 2+1+3+3 |
| A-6 | Main Script + Integration | run_experiment.py: argparse, end-to-end orchestration, smoke test | 8 | 2+3+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-4, A-5], Low(4-8): [A-1, A-6]

**Total complexity**: 57 | **Task count**: 6 (EXISTENCE PoC range: 4-8)

---

## Data Flow

```
metadata.csv
  -> WaterbirdsDataset (y, place, img_path)
  -> DataLoader (train_shuffle / train_ordered / val)
  -> train_epoch() -> model weights updated
  -> collect_gradnorms() [at epochs 1,3,5,10]
       -> GradientNormAnalyzer.compute_batch_norms()
          -> forward hook captures h(x_i) R^2048
          -> outer-product: g_tilde = ||softmax(logit) - onehot||
       -> gradnorm_epoch_{N}.npz  (g_raw, g_tilde, h_norm, group_labels, class_labels)
  -> compute_metrics() -> {ratio, auc, balance_deviation, secondary_metrics}
  -> gate_check() -> (pass/fail, per-criterion bools)
  -> save_results() -> results.json
  -> plot_*() -> figures/*.png
```

---

## Configuration Constants (inline in run_experiment.py)

| Constant | Value | Source |
|----------|-------|--------|
| COLLECTION_EPOCHS | {1, 3, 5, 10} | FR-4.1 |
| PRIMARY_EPOCH | 5 | FR-5 (T_id) |
| LR | 0.001 | FR-3.1 |
| MOMENTUM | 0.9 | FR-3.1 |
| WEIGHT_DECAY | 1e-4 | FR-3.1 |
| BATCH_SIZE | 128 | FR-1.4 |
| TOTAL_EPOCHS | 10 | FR-3.1 |
| SEED | 1 | FR-3.1 |
| TOP_K_FRACTION | 0.25 | FR-5.3 |
| GATE_RATIO | 3.0 | FR-5.1 |
| GATE_AUC | 0.70 | FR-5.2 |
| GATE_BALANCE | 0.10 | FR-5.3 |
| FC_INPUT_DIM | 2048 | FR-2.2 |
| EPSILON | 1e-8 | FR-4.2 |

---

*Architecture for H-E1 | EXISTENCE PoC | Green-field | 6 Epic Tasks*
