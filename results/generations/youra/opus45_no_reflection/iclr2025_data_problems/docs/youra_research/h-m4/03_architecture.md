# Architecture: H-M4

**Hypothesis:** Architecture-approximation interaction determines efficiency-accuracy trade-off (EK-FAC favors GPT-2, TracIn favors BERT, TRAK invariant)
**Type:** MECHANISM | **Tier:** FULL

Applied: unified multi-method influence wrapper pattern (from H-M3) extended with compute-budget sweep + Pareto-point collection

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-M3)
**Status:** No active Serena project registered for this workspace (same limitation as H-M3). Attempted direct file read of `h-m3/code/` — directory does not exist (H-M3 Phase 4 implementation not yet materialized on disk; only `03_architecture.md` spec exists). Per "trust the actual code" rule, when no actual code exists, the spec is the only available source of truth.
**Analyzed Path:** `docs/youra_research/h-m3/code/` (not found), `docs/youra_research/h-m3/03_architecture.md` (used instead)
**Findings:** H-M3 spec defines `data_loader.py`, `models.py`, `mislabel.py`, `finetune.py`, `ekfac_attribution.py`, `tracin_attribution.py`, `trak_attribution.py`, `metrics.py` with reusable signatures. H-M4 reimplements these fresh (no importable code exists), following H-M3's interface conventions for consistency, and adds a compute-budget dimension across all three attribution methods plus Pareto-curve/statistical modules.

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
    mislabel_fraction: float = 0.05
    seeds: list[int] = (42, 123, 456)
    compute_budgets: list[int] = (64, 128, 256, 512, 1024)  # proj dims
    tracin_checkpoint_counts: dict[int, int] = None  # budget -> n_checkpoints mapping
    methods: list[str] = ("ekfac", "tracin", "trak")
    architectures: list[str] = ("bert", "gpt2")
    alpha: float = 0.05
    output_dir: str = "."; figures_dir: str = "../figures"
    checkpoints_dir: str = "./checkpoints"
```

### data_loader (`data_loader.py`)

**Dependencies:** datasets, torch

```python
def load_sst2_splits() -> tuple[list, list, list, list]: ...
def build_dataloader(tokenizer, texts, labels, batch_size, max_length=128, shuffle=True) -> DataLoader: ...
```

### models (`models.py`)

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

### finetune (`finetune.py`)

**Dependencies:** models, data_loader, torch

```python
def finetune(model, tokenizer, train_loader: DataLoader, epochs: int, lr: float,
             device: str, ckpt_dir: str, ckpt_prefix: str, seed: int) -> tuple[nn.Module, list[str]]: ...
    # trains model, saves per-epoch checkpoints (needed for TracIn budget levels), returns (final_model, checkpoint_paths)
def load_checkpoint(model, path: str) -> nn.Module: ...
```

### ekfac_attribution (`ekfac_attribution.py`)

**Dependencies:** kronfluence, torch

```python
def compute_ekfac_scores(model, task, train_loader: DataLoader, query_loader: DataLoader,
                          proj_dim: int) -> np.ndarray: ...
def run_ekfac_budget_sweep(model, task, train_loader, query_loader,
                            proj_dims: list[int]) -> dict[int, tuple[np.ndarray, float]]: ...  # {proj_dim: (scores, wall_time_sec)}
```

### tracin_attribution (`tracin_attribution.py`)

**Dependencies:** dattri, torch

```python
def compute_tracin_scores(model, checkpoint_paths: list[str], query_loader: DataLoader,
                           train_loader: DataLoader, lr: float, device: str) -> np.ndarray: ...
def run_tracin_budget_sweep(model, all_checkpoint_paths: list[str], query_loader, train_loader,
                             lr: float, device: str, budget_to_ckpt_count: dict[int, int]) -> dict[int, tuple[np.ndarray, float]]: ...
    # maps 5 compute-budget levels to checkpoint-subset sizes; returns {budget: (scores, wall_time_sec)}
```

### trak_attribution (`trak_attribution.py`)

**Dependencies:** traker, torch

```python
def compute_trak_scores(model, task: str, train_loader: DataLoader, query_loader: DataLoader,
                         proj_dim: int, seed: int, train_set_size: int) -> np.ndarray: ...
def run_trak_budget_sweep(model, task, train_loader, query_loader, seed: int,
                           train_set_size: int, proj_dims: list[int]) -> dict[int, tuple[np.ndarray, float]]: ...
```

### metrics (`metrics.py`)

**Dependencies:** scikit-learn, numpy

```python
def compute_mislabeled_auc(influence_scores: np.ndarray, mislabeled_indices: list[int], n_train: int) -> float: ...
```

### pareto (`pareto.py`)

**Dependencies:** numpy

```python
def build_pareto_points(sweep_results: dict[int, tuple[np.ndarray, float]],
                         mislabeled_indices: list[int], n_train: int) -> list[tuple[float, float]]: ...
    # converts {budget: (scores, time)} -> [(compute_time, auc), ...] sorted by time
def is_dominated(point: tuple[float, float], frontier: list[tuple[float, float]]) -> bool: ...
def compute_dominance_matrix(results: dict) -> dict: ...
    # {(method, arch): dominates_which_others} per compute budget
```

### stats (`stats.py`)

**Dependencies:** scipy, numpy

```python
def paired_ttest_across_seeds(auc_bert: list[float], auc_gpt2: list[float]) -> tuple[float, float]: ...  # (t_stat, p_value)
def aggregate_seed_results(per_seed_results: list[dict]) -> dict: ...  # mean +/- std per (method, arch, budget)
def evaluate_predictions(agg_results: dict, alpha: float = 0.05) -> dict: ...
    # checks P1 (EK-FAC GPT2>BERT), P2 (TracIn BERT>GPT2), P3 (TRAK |diff|<5%) at matched budgets
```

### visualize (`visualize.py`)

**Dependencies:** matplotlib, numpy

```python
def plot_pareto_frontier_grid(results: dict, out_path: str) -> None: ...  # required: 2x3 grid, x=compute time (log), y=AUC
def plot_arch_comparison_per_method(results: dict, out_path: str) -> None: ...  # 3 overlaid BERT-vs-GPT2 plots
def plot_dominance_heatmap(dominance: dict, out_path: str) -> None: ...
def plot_auc_vs_projdim(results: dict, out_path: str) -> None: ...
def plot_auc_bar_fixed_budget(results: dict, budget: int, out_path: str) -> None: ...
```

### run_experiment (`run_experiment.py`)

**Dependencies:** all modules above

```python
def main() -> None:
    """Load SST-2 -> inject 5% mislabels -> for each seed in [42,123,456]: fine-tune BERT & GPT-2 with
    checkpoints -> for each arch: run EK-FAC/TracIn/TRAK budget sweeps (5 levels each) -> build Pareto points ->
    aggregate across seeds -> paired t-test per (method, budget) -> evaluate P1/P2/P3 -> generate figures ->
    save results.yaml"""
    ...
```

---

## File Organization

```
h-m4/code/
  config.py
  data_loader.py
  models.py
  mislabel.py
  finetune.py
  ekfac_attribution.py
  tracin_attribution.py
  trak_attribution.py
  metrics.py
  pareto.py
  stats.py
  visualize.py
  run_experiment.py
  checkpoints/
    bert_sst2_seed{42,123,456}_epoch{1,2,3}.pt
    gpt2_sst2_seed{42,123,456}_epoch{1,2,3}.pt
  mislabeled_indices_seed{42,123,456}.json
  results.yaml
figures/
  pareto_frontier_grid.png
  arch_comparison_ekfac.png
  arch_comparison_tracin.png
  arch_comparison_trak.png
  dominance_heatmap.png
  auc_vs_projdim.png
  auc_bar_fixed_budget.png
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data + mislabel pipeline | SST-2 load, 5% mislabel injection per seed, index persistence | 6 | 2+1+2+1 |
| A-2 | Model fine-tuning across seeds | BERT/GPT-2 loaders, 3-epoch training x 3 seeds with per-epoch checkpoints | 9 | 3+2+2+2 |
| A-3 | EK-FAC budget sweep | kronfluence integration across 5 proj dims, wall-clock timing, both archs | 15 | 4+3+4+4 |
| A-4 | TracIn budget sweep | dattri gradient-checkpoint attribution mapped to 5 compute-budget levels | 14 | 4+3+4+3 |
| A-5 | TRAK budget sweep | traker integration across 5 proj dims, both archs | 14 | 4+3+4+3 |
| A-6 | Mislabel-AUC metric | ROC-AUC computation for self-influence ranking, per (method,arch,budget,seed) | 6 | 2+1+2+1 |
| A-7 | Pareto point construction | (time, AUC) point extraction, dominance computation, frontier logic | 8 | 3+2+2+1 |
| A-8 | Cross-seed statistical analysis | Aggregate mean+-std, paired t-test per (method,budget), P1/P2/P3 evaluation | 9 | 2+3+2+2 |
| A-9 | Visualization suite | Required 2x3 Pareto grid, arch-comparison, dominance heatmap, AUC-vs-dim, bar chart | 10 | 3+2+3+2 |
| A-10 | Orchestration + reporting | run_experiment.py full pipeline (30 runs), results.yaml output | 7 | 3+2+1+1 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [A-3, A-4, A-5], Medium(9-13): [A-2, A-8, A-9], Low(4-8): [A-1, A-6, A-7, A-10]
