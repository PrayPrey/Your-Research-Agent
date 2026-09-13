# Architecture: H-M3

**Hypothesis:** Attribution approximation methods make different assumptions about curvature (EK-FAC: Kronecker, TracIn: gradient-only, TRAK: random projection)
**Type:** MECHANISM | **Tier:** FULL

Applied: unified multi-method influence wrapper pattern (simple-influence `compute_scores_with_loader` interface) for fair cross-method/cross-architecture comparison

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-M2)
**Status:** No active Serena project registered for this workspace (same limitation noted in H-M2); fell back to direct file read of `h-m2/code/` — functionally equivalent per "trust the actual code" rule.
**Analyzed Path:** `docs/youra_research/h-m2/code/`
**Findings:** `data_loader.py` (`load_sst2_splits`, `build_dataloader`, `TextDataset`), `models.py` (`load_bert_classifier`, `load_gpt2_classifier`), `config.py` (`ExperimentConfig` dataclass) are directly importable/reusable as-is — no signature changes needed. `finetune.py` reused but extended: H-M3 needs 5% mislabel injection before training (H-M2 has none) and 3 separate epoch checkpoints (H-M2 saves final only per `finetune()` returning `nn.Module`, checkpoint save is a separate call). `hessian_analysis.py`/`kronecker_analysis.py` not needed for H-M3 (different mechanism — attribution methods, not raw Hessian metrics).

---

## Module Structure

### config (`config.py`)

**Dependencies:** none

```python
@dataclass
class ExperimentConfig:
    dataset_name: str = "glue"; dataset_config: str = "sst2"
    max_length: int = 128; train_batch_size: int = 32
    epochs: int = 3; lr: float = 2e-5
    bert_model_id: str = "bert-base-uncased"; gpt2_model_id: str = "gpt2"
    mislabel_fraction: float = 0.05; seed: int = 42
    ekfac_strategies: list[str] = ("identity", "diagonal", "kfac", "ekfac")
    trak_proj_dims: list[int] = (1024, 2048, 4096)
    trak_seeds: list[int] = (0, 1, 2, 3, 4)
    tracin_checkpoint_epochs: list[int] = (1, 2, 3)
    gate_threshold: float = 0.10
    output_dir: str = "."; figures_dir: str = "../figures"
    checkpoints_dir: str = "./checkpoints"

GATE_CONFIG = {"min_relative_diff": 0.10}
FIGURE_FILES = {"gate_comparison": "gate_comparison.png", "quality_heatmap": "quality_heatmap.png",
                 "score_distributions": "score_distributions.png", "rank_correlation": "rank_correlation.png"}
```

### data_loader (`data_loader.py`) — REUSED FROM H-M2 (unmodified)

**Dependencies:** datasets, torch

```python
def load_sst2_splits() -> tuple[list, list, list, list]: ...
def build_dataloader(tokenizer, texts, labels, batch_size, max_length=128, shuffle=True) -> DataLoader: ...
```

### models (`models.py`) — REUSED FROM H-M2 (unmodified)

**Dependencies:** transformers

```python
def load_bert_classifier(model_id="bert-base-uncased") -> tuple: ...
def load_gpt2_classifier(model_id="gpt2") -> tuple: ...
```

### mislabel (`mislabel.py`)

**Dependencies:** numpy

```python
def inject_mislabels(labels: list[int], fraction: float, seed: int) -> tuple[list[int], list[int]]: ...  # (flipped_labels, mislabeled_indices)
def save_mislabeled_indices(indices: list[int], path: str) -> None: ...
```

### finetune (`finetune.py`) — EXTENDS H-M2 (adds per-epoch checkpointing)

**Dependencies:** models, data_loader, torch

```python
def finetune_with_checkpoints(model, tokenizer, train_loader: DataLoader, epochs: int, lr: float,
                               device: str, ckpt_dir: str, ckpt_prefix: str) -> list[str]: ...  # returns checkpoint paths per epoch
def load_checkpoint(model, path: str) -> nn.Module: ...
```

### ekfac_attribution (`ekfac_attribution.py`)

**Dependencies:** kronfluence, torch

```python
def fit_ekfac_factors(model, task, train_loader: DataLoader, strategy: str = "ekfac") -> object: ...  # kronfluence Analyzer
def compute_ekfac_scores(analyzer, query_loader: DataLoader, train_loader: DataLoader, strategy: str) -> np.ndarray: ...
def run_ekfac_strategy_ablation(model, task, train_loader, query_loader, strategies: list[str]) -> dict: ...  # {strategy: scores}
```

### tracin_attribution (`tracin_attribution.py`)

**Dependencies:** captum, torch

```python
def compute_tracin_scores(model, checkpoint_paths: list[str], query_loader: DataLoader,
                           train_loader: DataLoader, lr: float, device: str) -> np.ndarray: ...
def run_checkpoint_count_ablation(model, checkpoint_paths: list[str], query_loader, train_loader,
                                   lr: float, device: str, counts: list[int]) -> dict: ...  # {n_ckpts: scores}
```

### trak_attribution (`trak_attribution.py`)

**Dependencies:** traker, torch

```python
def compute_trak_scores(model, task: str, train_loader: DataLoader, query_loader: DataLoader,
                         proj_dim: int, seed: int, train_set_size: int) -> np.ndarray: ...
def run_trak_seed_ensemble(model, task, train_loader, query_loader, proj_dim: int,
                            seeds: list[int], train_set_size: int) -> list[np.ndarray]: ...
def run_proj_dim_ablation(model, task, train_loader, query_loader, seeds: list[int],
                           proj_dims: list[int], train_set_size: int) -> dict: ...  # {proj_dim: scores}
```

### metrics (`metrics.py`)

**Dependencies:** scikit-learn, scipy, numpy

```python
def compute_mislabeled_auc(influence_scores: np.ndarray, mislabeled_indices: list[int], n_train: int) -> float: ...
def compute_rank_correlation(score_list: list[np.ndarray]) -> float: ...  # avg pairwise Spearman
def compute_relative_arch_diff(bert_auc: float, gpt2_auc: float) -> float: ...  # |diff| / max
```

### verify (`verify.py`)

**Dependencies:** metrics

```python
def verify_gate(results: dict, threshold: float = 0.10) -> dict:
    """Per-method relative AUC diff (EK-FAC, TracIn, TRAK) across BERT/GPT-2; pass if any > threshold."""
    ...
```

### visualize (`visualize.py`)

**Dependencies:** matplotlib, seaborn, numpy

```python
def plot_gate_comparison(results: dict, out_path: str) -> None: ...  # required: 6-bar AUC chart
def plot_quality_heatmap(results: dict, out_path: str) -> None: ...
def plot_score_distributions(score_dict: dict, out_path: str) -> None: ...  # violin plots
def plot_rank_correlation_matrix(corr_matrix: np.ndarray, method_names: list[str], out_path: str) -> None: ...
```

### run_experiment (`run_experiment.py`)

**Dependencies:** all modules above

```python
def main() -> None:
    """Load SST-2 -> inject 5% mislabels -> load+finetune BERT & GPT-2 with epoch checkpoints ->
    for each arch: run EK-FAC, TracIn, TRAK attribution -> compute mislabeled-detection AUC ->
    run ablations (proj_dim, checkpoint count, EK-FAC strategy) -> verify gate ->
    generate figures -> save results.yaml"""
    ...
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location | Reuse Status |
|--------|-------------|----------------|---------------|
| load_sst2_splits, build_dataloader, TextDataset | `from h_m2.code.data_loader import load_sst2_splits, build_dataloader` | `h-m2/code/data_loader.py` | Direct reuse, unmodified |
| load_bert_classifier, load_gpt2_classifier | `from h_m2.code.models import load_bert_classifier, load_gpt2_classifier` | `h-m2/code/models.py` | Direct reuse, unmodified |
| ExperimentConfig pattern | n/a (pattern only) | `h-m2/code/config.py` | Pattern reused, reimplemented with H-M3-specific fields |

**Verified from**: `docs/youra_research/h-m2/code/` (actual implementation, confirmed by direct file read — `kronecker_analysis.py`/`ablations.py` mentioned in h-m2/03_architecture.md do not exist in actual code, so not referenced here).

---

## File Organization

```
h-m3/code/
  config.py
  data_loader.py          # copied from h-m2/code/, unmodified
  models.py                # copied from h-m2/code/, unmodified
  mislabel.py
  finetune.py
  ekfac_attribution.py
  tracin_attribution.py
  trak_attribution.py
  metrics.py
  verify.py
  visualize.py
  run_experiment.py
  checkpoints/
    bert_sst2_epoch{1,2,3}.pt
    gpt2_sst2_epoch{1,2,3}.pt
  mislabeled_indices.json
  results.yaml
figures/
  gate_comparison.png
  quality_heatmap.png
  score_distributions.png
  rank_correlation.png
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data + mislabel pipeline | SST-2 load (reused), 5% mislabel injection, index persistence | 6 | 2+1+2+1 |
| A-2 | Model + fine-tune with checkpoints | BERT/GPT-2 loaders (reused), 3-epoch training loop with per-epoch checkpoint save | 8 | 2+2+2+2 |
| A-3 | EK-FAC attribution | kronfluence integration, factor fitting (4 strategies), pairwise score computation | 15 | 4+4+4+3 |
| A-4 | TracIn attribution | captum/gradient-checkpoint-based dot-product scoring across 3 checkpoints | 12 | 3+3+3+3 |
| A-5 | TRAK attribution | traker integration, featurize/score/finalize, multi-seed ensemble | 14 | 4+4+3+3 |
| A-6 | Cross-method metrics | Mislabeled-AUC, rank correlation, relative arch-diff computation | 7 | 2+2+2+1 |
| A-7 | Ablation A1 — TRAK proj dim | Run TRAK at proj_dim 1024/2048/4096, compare AUC/variance | 8 | 2+3+2+1 |
| A-8 | Ablation A2 — TracIn checkpoints | Run TracIn with 1/2/3 checkpoints, compare signal/AUC | 7 | 2+2+2+1 |
| A-9 | Ablation A3 — EK-FAC strategy | Compare identity/diagonal/kfac/ekfac strategies | 8 | 2+3+2+1 |
| A-10 | Gate verification | Per-method relative AUC diff across architectures, pass if any >10% | 5 | 1+1+2+1 |
| A-11 | Visualization suite | Gate bar chart (required), heatmap, violin plots, rank correlation matrix | 9 | 3+2+2+2 |
| A-12 | Orchestration + reporting | run_experiment.py pipeline wiring, results.yaml output | 6 | 2+1+1+2 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [A-3, A-5], Medium(9-13): [A-4], Low(4-8): [A-1, A-2, A-6, A-7, A-8, A-9, A-10, A-11, A-12]
