# Architecture: H-M2

**Hypothesis:** Different attention structures create different Hessian curvature patterns (block-diagonal vs dense)
**Type:** MECHANISM | **Tier:** FULL

Applied: hessian-eigenthings HessianOperator/GGNOperator + Lanczos pattern for HF transformer curvature analysis

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-M1)
**Status:** Serena had no active project registered for this workspace; fell back to direct file read of `h-m1/code/` (functionally equivalent inspection of actual implementation, per "trust the actual code" rule).
**Analyzed Path:** `docs/youra_research/h-m1/code/`
**Findings:** H-M1 loads `AutoModel` (no classification head, `output_attentions=True`) purely for attention-matrix extraction — models are NOT fine-tuned. H-M2 requires `AutoModelForSequenceClassification` fine-tuned 3 epochs on SST-2 (FR-1.3), so `models.py` and training must be reimplemented, not reused. `data_loader.py` pattern (glue/sst2 via `load_dataset`) is reusable; H-M2 additionally needs the train split (67,349 samples) and a `Dataset`/`DataLoader` wrapper for Hessian batches. `config.py` dataclass + `GATE_CONFIG`/`FIGURE_FILES` pattern is reused directly.

---

## Module Structure

### config (`config.py`)

**Dependencies:** none

```python
@dataclass
class ExperimentConfig:
    dataset_name: str = "glue"; dataset_config: str = "sst2"
    max_length: int = 128; train_batch_size: int = 32
    hessian_batch_size: int = 256
    epochs: int = 3; lr: float = 2e-5
    lanczos_k: int = 20; lanczos_steps: int = 50; trace_matvecs: int = 100
    bert_model_id: str = "bert-base-uncased"; gpt2_model_id: str = "gpt2"
    seeds: list[int] = (42, 43)
    gate_threshold: float = 0.10
    output_dir: str = "."; figures_dir: str = "../figures"
    checkpoints_dir: str = "./checkpoints"

GATE_CONFIG = {"min_relative_diff": 0.10}
FIGURE_FILES = {"gate_comparison": "gate_comparison.png", "eigenvalue_spectrum": "eigenvalue_spectrum.png",
                 "spectral_density": "spectral_density.png", "condition_by_layer": "condition_by_layer.png"}
```

### data_loader (`data_loader.py`)

**Dependencies:** datasets, torch

```python
def load_sst2_splits() -> tuple[list, list, list, list]: ...  # train_texts, train_labels, val_texts, val_labels
def build_dataloader(tokenizer, texts: list[str], labels: list[int], batch_size: int, max_length: int = 128) -> DataLoader: ...
```

### models (`models.py`)

**Dependencies:** transformers, torch

```python
def load_bert_classifier() -> tuple[AutoModelForSequenceClassification, AutoTokenizer]: ...  # bert-base-uncased, num_labels=2
def load_gpt2_classifier() -> tuple[GPT2ForSequenceClassification, GPT2Tokenizer]: ...  # pad_token=eos, num_labels=2
```

### finetune (`finetune.py`)

**Dependencies:** models, data_loader, torch

```python
def finetune(model, tokenizer, train_loader: DataLoader, epochs: int, lr: float, device: str) -> nn.Module: ...
def save_checkpoint(model, path: str) -> None: ...
def load_checkpoint(model, path: str) -> nn.Module: ...
```

### hessian_analysis (`hessian_analysis.py`)

**Dependencies:** hessian-eigenthings (fallback: pyhessian), torch, numpy

```python
def compute_hessian_metrics(model, dataloader, loss_fn, device: str, k: int = 20,
                             lanczos_steps: int = 50, trace_matvecs: int = 100, seed: int = 42) -> dict:
    """top_eigenvalue, eigenvalue_ratio, trace, top_k_eigenvalues, spectral_norm."""
    ...
def compute_spectral_density(model, dataloader, loss_fn, device: str, num_runs: int = 8,
                              lanczos_steps: int = 40, seed: int = 0) -> tuple: ...  # (density, grid)
```

### kronecker_analysis (`kronecker_analysis.py`)

**Dependencies:** hessian-eigenthings (GGNOperator), torch, numpy

```python
def compute_kronecker_fit(model, dataloader, loss_fn, layer_names: list[str], device: str) -> dict:
    """Per-layer ||G_layer - A⊗S||_F / ||G_layer||_F -> {layer_name: fit_error}."""
    ...
def aggregate_kronecker_fit(per_layer_errors: dict) -> dict: ...  # mean/std across layers
```

### ablations (`ablations.py`)

**Dependencies:** hessian_analysis, data_loader

```python
def run_seed_ablation(model, dataloader, loss_fn, device: str, seeds: list[int]) -> list[dict]: ...
def run_batch_size_ablation(model, tokenizer, texts, labels, loss_fn, device: str, batch_sizes: list[int]) -> list[dict]: ...
def run_param_subset_ablation(model, dataloader, loss_fn, device: str, subset: str) -> dict: ...  # "attention"|"mlp"|"full"
```

### verify (`verify.py`)

**Dependencies:** none

```python
def verify_hessian_gate(bert_metrics: dict, gpt2_metrics: dict, threshold: float = 0.10) -> dict:
    """Relative diff per metric (top_eigenvalue, eigenvalue_ratio, trace); pass if any > threshold."""
    ...
```

### visualize (`visualize.py`)

**Dependencies:** matplotlib, numpy

```python
def plot_gate_comparison(bert_metrics: dict, gpt2_metrics: dict, out_path: str) -> None: ...  # required
def plot_eigenvalue_spectrum(bert_eigs: list[float], gpt2_eigs: list[float], out_path: str) -> None: ...
def plot_spectral_density(bert_density: tuple, gpt2_density: tuple, out_path: str) -> None: ...
def plot_condition_by_layer(bert_layer_ratios: list[float], gpt2_layer_ratios: list[float], out_path: str) -> None: ...
```

### run_experiment (`run_experiment.py`)

**Dependencies:** all modules above

```python
def main() -> None:
    """Load data -> load+finetune BERT & GPT-2 -> save checkpoints ->
    compute Hessian metrics (both) -> compute Kronecker fit (both) ->
    run ablations -> verify gate -> generate figures -> save results.yaml + eigenvalues.npz"""
    ...
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location | Reuse Status |
|--------|-------------|----------------|---------------|
| SST-2 loader pattern | n/a (pattern only) | `h-m1/code/data_loader.py` | Pattern reused, reimplemented for train+val splits |
| Config dataclass pattern | n/a (pattern only) | `h-m1/code/config.py` | Pattern reused, reimplemented for H-M2 fields |

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation). No H-M1 module is directly importable — H-M1 models lack classification heads and were never fine-tuned, so `models.py`/`data_loader.py` are rewritten fresh for H-M2 rather than imported.

---

## File Organization

```
h-m2/code/
  config.py
  data_loader.py
  models.py
  finetune.py
  hessian_analysis.py
  kronecker_analysis.py
  ablations.py
  verify.py
  visualize.py
  run_experiment.py
  checkpoints/
    bert_sst2.pt
    gpt2_sst2.pt
  results.yaml
  eigenvalues.npz
figures/
  gate_comparison.png
  eigenvalue_spectrum.png
  spectral_density.png
  condition_by_layer.png
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loading | SST-2 train+val via HF datasets, DataLoader builder | 6 | 2+1+1+2 |
| A-2 | Model loading | BERT + GPT-2 classification heads, tokenizer setup | 5 | 1+1+1+2 |
| A-3 | Fine-tuning pipeline | 3-epoch AdamW loop, checkpoint save/load for both models | 10 | 3+2+2+3 |
| A-4 | Hessian metrics core | HessianOperator + Lanczos top-20, trace estimate, fallback to PyHessian | 14 | 4+4+4+2 |
| A-5 | Spectral density | Stochastic Lanczos Quadrature density estimate | 8 | 3+2+2+1 |
| A-6 | Kronecker fit analysis | GGNOperator per-layer, Frobenius fit error computation | 13 | 4+3+4+2 |
| A-7 | Ablation studies | Seed (2x), batch size (256/512), attention-only vs MLP-only subsets | 11 | 3+3+3+2 |
| A-8 | Gate verification | Relative-diff thresholding across 3 primary metrics | 5 | 1+1+2+1 |
| A-9 | Required + spectral visualizations | Gate bar chart, eigenvalue spectrum, spectral density plots | 8 | 3+1+2+2 |
| A-10 | Layer-wise visualization | Per-layer condition number / Kronecker fit plot | 5 | 2+1+1+1 |
| A-11 | Results reporting | YAML metrics + NPZ eigenvalue arrays + validation report | 6 | 2+1+1+2 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [A-4], Medium(9-13): [A-6, A-7], Low(4-8): [A-1, A-2, A-3, A-5, A-8, A-9, A-10, A-11]
