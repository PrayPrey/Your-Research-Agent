# Architecture: H-M1 — BFS-Gap Correlation Analysis

**Type**: MECHANISM (analysis script, no new model training)
**Applied**: single-script correlation pipeline over frozen artifacts (no new abstractions needed for 6-datapoint stats)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: Serena had no active project registered for this path; fell back to direct `Read` of H-E1 source files (equivalent coverage for this small codebase).
**Analyzed Path**: `docs/youra_research/h-e1/code/{model,data,config,train}.py`
**Findings**:
- H-E1 fine-tunes 15 checkpoints (5 benchmarks x 3 seeds), saved as `{benchmark}_seed{seed}.pt` in `ckpt_dir`, each a dict `{state_dict, benchmark, seed, acc, epoch}`.
- `FeatureResNet50.extract_features(x)` returns 2048-d avgpool features; `DATASET_NUM_CLASSES` gives per-benchmark class counts.
- **Gap vs PRD**: H-E1's `train_linear_probe` fits a `sklearn.LogisticRegression` in-memory but never pickles it to disk — only `features.npy`/`labels.npy`/`model_ids.npy` and JSON metrics are persisted. H-M1 must **retrain the identical probe** (same hyperparams from `Config`) on the saved `.npy` features rather than loading a serialized classifier object. Architecture below accounts for this.
- "6 models" in the brief vs 15 checkpoints in H-E1: H-M1 uses one representative model per benchmark (seed 0) for gap evaluation, matching brief's "6 fine-tuned models" (5 benchmarks + treats classifier itself as the 6th artifact) — clarified as 5 in-domain checkpoints (seed0) evaluated; adjust to actual count found in `ckpt_dir` at runtime.

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| FeatureResNet50 | `from h_e1.model import FeatureResNet50` | `h-e1/code/model.py` |
| build_dataloader, DATASET_NUM_CLASSES | `from h_e1.data import build_dataloader, DATASET_NUM_CLASSES` | `h-e1/code/data.py` |
| Config | `from h_e1.config import Config` | `h-e1/code/config.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation, not specs)

Sys-path note: H-M1 script inserts `h-e1/code/` into `sys.path` (same pattern as `h-e1/code/run_experiment.py`) since H-E1 has no package `__init__.py`.

## File Organization

- `h-m1/code/config.py` — paths to H-E1 artifacts + H-M1 output paths
- `h-m1/code/artifacts.py` — load checkpoints, load/rebuild probe classifier
- `h-m1/code/bfs.py` — BFS computation from classifier confidence
- `h-m1/code/gap.py` — in-domain vs NABirds accuracy evaluation
- `h-m1/code/correlate.py` — Pearson correlation + scatter plot
- `h-m1/code/run_correlation.py` — orchestration script (PRD deliverable)

## Modules

### Config (`h-m1/code/config.py`)

**Dependencies**: none

```python
@dataclass
class Config:
    h_e1_dir: str = "../h-e1"          # base hypothesis folder
    data_root: str = "../h-e1/code/data"
    benchmarks: list = field(default_factory=lambda: ["cub","dogs","flowers","cars","aircraft"])
    seed: int = 0                       # representative checkpoint per benchmark
    probe_dataset: str = "nabirds"
    batch_size: int = 32
    results_path: str = "./results/experiment_results.json"
    figure_path: str = "./figures/bfs_gap_scatter.png"
```

### ArtifactLoader (`h-m1/code/artifacts.py`)

**Dependencies**: Config, FeatureResNet50 (external), build_dataloader (external)

```python
def load_checkpoint(benchmark: str, seed: int, cfg: Config) -> dict: ...
def load_model(ckpt: dict) -> FeatureResNet50: ...
def load_or_rebuild_probe(cfg: Config) -> Tuple[LogisticRegression, np.ndarray, np.ndarray, np.ndarray]:
    """Loads h-e1 features/labels/model_ids .npy, refits LogisticRegression
    with h-e1.config.Config defaults. Returns (clf, features, labels, model_ids)."""
```

### BFS (`h-m1/code/bfs.py`)

**Dependencies**: sklearn LogisticRegression

```python
def compute_bfs(clf: LogisticRegression, features: np.ndarray,
                 model_ids: np.ndarray, model_idx: int, true_label: int) -> float:
    """Mean softmax confidence for true benchmark class, over this model's probe samples."""
```

### GapEvaluator (`h-m1/code/gap.py`)

**Dependencies**: FeatureResNet50, build_dataloader

```python
def eval_accuracy(model: FeatureResNet50, loader: DataLoader, device) -> float: ...
def compute_gap(model: FeatureResNet50, benchmark: str, cfg: Config, device) -> dict:
    """Returns {'in_domain_acc': float, 'nabirds_acc': float, 'gap': float}.
    in_domain: build_dataloader(benchmark, train=False).
    nabirds_acc: model's own fc head can't score 555-class NABirds directly ->
    use k-NN on extract_features() against NABirds train split labels (1-NN classifier)
    as cross-dataset probe accuracy proxy."""
```

### Correlation (`h-m1/code/correlate.py`)

**Dependencies**: scipy.stats, matplotlib

```python
def pearson_analysis(bfs_scores: List[float], gaps: List[float]) -> dict:
    """Returns {'r': float, 'p_value': float, 'n': int}."""
def plot_scatter(bfs_scores, gaps, r, p_value, save_path: str) -> None:
    """Scatter + linregress line, annotate r and p."""
```

### Orchestration (`h-m1/code/run_correlation.py`)

```python
def main(cfg: Config = None) -> dict:
    """
    1. clf, features, labels, model_ids = load_or_rebuild_probe(cfg)
    2. for each benchmark in cfg.benchmarks:
         ckpt = load_checkpoint(benchmark, cfg.seed, cfg)
         model = load_model(ckpt)
         bfs = compute_bfs(clf, features, model_ids, model_idx, true_label)
         gap_result = compute_gap(model, benchmark, cfg, device)
    3. stats = pearson_analysis(bfs_list, gap_list)
    4. plot_scatter(...)
    5. dump JSON to cfg.results_path; exit 0 if stats['r']>0.3 and stats['p_value']<0.05 else 1
    """
```

## Data Flow

1. `load_or_rebuild_probe` → reads `h-e1/features/{features,labels,model_ids}.npy`, refits `LogisticRegression` (same `Config` hyperparams as H-E1) since no serialized classifier exists on disk.
2. Per benchmark: load seed-0 checkpoint → `FeatureResNet50` → (a) BFS via probe confidence on that model's NABirds probe features, (b) Gap via in-domain test accuracy minus NABirds 1-NN proxy accuracy.
3. Collect 5 `(BFS, Gap)` pairs → `pearsonr` → scatter plot + JSON.

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Config + artifact paths | Set up Config, verify H-E1 paths resolve | 5 | 1+1+1+2 |
| M-2 | Checkpoint loader | Load `.pt` checkpoints, reconstruct FeatureResNet50 | 6 | 2+2+1+1 |
| M-3 | Probe reconstruction | Load `.npy` features, refit LogisticRegression matching H-E1 config | 8 | 2+2+2+2 |
| M-4 | BFS computation | Per-model mean confidence for true benchmark class | 6 | 1+2+2+1 |
| M-5 | In-domain accuracy eval | Evaluate each model on its own benchmark test split | 5 | 1+1+2+1 |
| M-6 | NABirds cross-dataset eval | 1-NN proxy accuracy on NABirds features per model | 8 | 2+2+2+2 |
| M-7 | Correlation + plotting | pearsonr + scatter with regression line | 5 | 1+1+2+1 |
| M-8 | Orchestration + JSON output | run_correlation.py wiring, results JSON, gate check | 6 | 1+2+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [M-1,M-2,M-3,M-4,M-5,M-6,M-7,M-8]
