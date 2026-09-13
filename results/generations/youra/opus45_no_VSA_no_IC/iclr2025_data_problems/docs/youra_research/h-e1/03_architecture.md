# Architecture: h-e1

**Type**: EXISTENCE (PoC)
**Applied**: Uniform adapter interface per attribution library (no KB pattern match found — standard wrapper approach used)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch

---

## Data Flow

```
CIFAR-10 (torchvision)
      |
      v
 data.py: get_loaders() -> train_loader, test_loader
      |
      v
 model.py: build_model() -> ResNet-18(cifar)
      |
      v
 train.py: train_or_load() -> model + checkpoints[]
      |
      +---------------+---------------+
      v               v               v
  attrib_trak.py  attrib_tracin.py  attrib_kronfluence.py
   (TRAKer)         (TracInCP)        (Analyzer/EKFAC)
      |               |               |
      +-------+-------+-------+-------+
              v
      evaluate.py: compute_method_correlations()
              |
              v
      outputs/correlations.json, outputs/*.pt
              |
              v
      figures.py: heatmap + scatter + histograms -> figures/*.png
```

---

## File Organization

```
h-e1/code/
  data.py
  model.py
  train.py
  attrib_trak.py
  attrib_tracin.py
  attrib_kronfluence.py
  evaluate.py
  figures.py
  run_experiment.py      # orchestrator entrypoint
  config.py
h-e1/outputs/
  scores_trak.pt
  scores_tracin.pt
  scores_kronfluence.pt
  correlations.json
h-e1/figures/
  correlation_heatmap.png
  scatter_*.png
  distributions.png
```

---

## Modules

### data.py

**Dependencies**: torchvision

```python
def get_loaders(batch_size: int = 128, data_root: str = "./data") -> tuple[DataLoader, DataLoader]: ...
def get_test_subset(test_loader: DataLoader, n: int = 1000) -> Dataset: ...
```

### model.py

**Dependencies**: torchvision.models

```python
def build_model(num_classes: int = 10) -> nn.Module: ...  # resnet18 adapted for CIFAR
```

### train.py

**Dependencies**: model.py, data.py

```python
def train_or_load(model: nn.Module, train_loader: DataLoader, ckpt_dir: str,
                   epochs: int = 200, num_checkpoints: int = 3) -> list[str]:
    """Returns list of checkpoint file paths (subset of epochs saved for TracIn)."""
```

### attrib_trak.py

**Dependencies**: traker, model.py

```python
def run_trak(model: nn.Module, train_loader: DataLoader, test_batch,
             checkpoints: list[str], exp_name: str = "test") -> np.ndarray:
    """Returns (num_test, num_train) score matrix."""
```

### attrib_tracin.py

**Dependencies**: captum, model.py

```python
def run_tracin(model: nn.Module, train_dataset: Dataset, test_batch,
                checkpoints: list[str]) -> np.ndarray:
    """Returns (num_test, num_train) score matrix."""
```

### attrib_kronfluence.py

**Dependencies**: kronfluence, model.py

```python
def run_kronfluence(model: nn.Module, train_dataset: Dataset, test_dataset: Dataset,
                     analysis_name: str = "verify") -> np.ndarray:
    """Returns (num_test, num_train) score matrix."""
```

### evaluate.py

**Dependencies**: scipy.stats, numpy

```python
def compute_method_correlations(scores: dict[str, np.ndarray]) -> dict: ...
def verify_mathematical_distinctness(scores: dict[str, np.ndarray], threshold: float = 0.9) -> tuple[bool, dict]: ...
```

### figures.py

**Dependencies**: matplotlib, evaluate.py

```python
def plot_correlation_heatmap(correlations: dict, out_path: str) -> None: ...
def plot_pairwise_scatter(scores: dict[str, np.ndarray], out_dir: str) -> None: ...
def plot_score_distributions(scores: dict[str, np.ndarray], out_path: str) -> None: ...
```

### run_experiment.py

**Dependencies**: all modules above

```python
def main() -> None:
    """data -> model -> train_or_load -> run_trak/tracin/kronfluence -> evaluate -> figures -> save outputs"""
```

### config.py

```python
BATCH_SIZE = 128
EPOCHS = 200
NUM_CHECKPOINTS = 3
NUM_TEST_SAMPLES = 1000
SEED = 42
CORR_THRESHOLD = 0.9
```

---

## Integration Points (TRAK / TracIn / Kronfluence)

- **Shared inputs**: same `model`, same `checkpoints` list (paths saved by `train.py`), same `train_loader.dataset` / `test_batch` (same 1000-sample subset for all three).
- **Shared output contract**: each `attrib_*.py` module returns a `(num_test, num_train)` numpy array — this uniform shape is the sole integration contract consumed by `evaluate.py`. No shared internal state between the three libraries; each manages its own factors/cache directory (`trak_results/`, `kronfluence_analysis/`) to avoid collisions.
- **Isolation**: run each method in sequence (not parallel) to bound GPU memory; each `run_*` function is independently callable/testable.

## Checkpoint Management for TracIn

- `train.py` saves `num_checkpoints` (default 3) model state_dicts at evenly spaced epochs (e.g., epochs 67, 133, 200) to `h-e1/checkpoints/ckpt_{i}.pt`.
- Same checkpoint list reused by TRAK (`traker.load_checkpoint` per ckpt) and TracIn (`checkpoints=` param) — ensures identical model states drive both methods.
- Kronfluence uses only final trained model (EKFAC is single-model factorization); does not consume the checkpoint list.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data + model setup | CIFAR-10 loaders, ResNet-18 build | 5 | 2+1+1+1 |
| A-2 | Training + checkpointing | Train/load model, save 3 checkpoints | 7 | 2+2+2+1 |
| A-3 | TRAK integration | Wrap TRAKer featurize/finalize | 8 | 2+3+2+1 |
| A-4 | TracIn integration | Wrap captum TracInCP | 6 | 2+2+1+1 |
| A-5 | Kronfluence integration | Wrap Analyzer fit_factors/compute_scores | 9 | 3+3+2+1 |
| A-6 | Correlation evaluation | Pearson/Spearman/Kendall across pairs | 5 | 1+2+1+1 |
| A-7 | Figure generation | Heatmap, scatter, distributions | 4 | 1+1+1+1 |
| A-8 | Orchestration + validation | run_experiment.py, save outputs, gate check | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-5], Low(4-8): [A-1,A-2,A-3,A-4,A-6,A-7,A-8]
