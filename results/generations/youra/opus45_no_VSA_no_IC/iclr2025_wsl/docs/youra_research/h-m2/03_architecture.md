# Architecture: H-M2 (NFN Data Efficiency vs MLP)

**Type**: MECHANISM | **Applied**: paired-comparison sweep pattern (train N models, eval fixed test set, repeat per seed)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1 provides data pipeline + NFN model to reuse)
**Status**: Serena project not pre-activated for this path (`No active project` error) — direct Read used as equivalent MANDATORY analysis of `docs/youra_research/h-m1/code/`, per H-M1 precedent.
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Findings**:
- **CRITICAL DEVIATION**: H-M2 PRD/brief assume the official `nfn` PyPI library (`NPLinear`/`HNPPool`/`WeightSpaceFeatures`). H-M1's *actual* code does **not** use that library — it implements a custom DeepSets-style equivariant model (`nfn_model.py::NFNAccuracyPredictor`) operating on `List[Tensor]` weight matrices (via `extract_weight_tensors`/`collate_weights`), not `WeightSpaceFeatures`. Trusting actual code over spec: H-M2 reuses this custom NFN, not the official lib.
- H-M1 has **no MLP baseline** — only `baseline_model.py::fit_ridge` (RidgeCV on 147-dim stats). H-M2 FR-2 requires a real 2-layer MLP on flattened weights; this is new code (`mlp_model.py`).
- `data.py` zoo is **synthetic** (`generate_model_zoo`, cached `.pt`, 6000 models default in `download_model_zoo` but H-M1's config used `n_train=2000`). H-M2 needs the full pool + must generate/load enough models to support N up to 5000 train + 500 test → request `n_models=6000` (matches `download_model_zoo` default).
- `data.py::split_test_set(items, test_size=500, seed=42)` — fixed test split, reuse identical seed for parity with H-M1 test set.
- `config.py` uses `@dataclass` nested config (not flat constants as H-M1's own doc claimed) — follow same style, extend with `n_values` sweep list.
- `train.py::train_nfn` takes `train_items, val_items` — H-M2 needs a variant without early-stopping val-set carve-out complexity for small N (N=100 too small to further split); reuse as-is by passing a slice of train_pool as pseudo-val, or skip early stopping for small N.
- `collate_weights` flattens per-layer weight tensors directly — reusable unchanged for both N-sweep and seed loop.

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| ResNet20, generate_model_zoo, load_checkpoints, split_test_set | `from h_m1.data import ResNet20, generate_model_zoo, load_checkpoints, split_test_set` | `docs/youra_research/h-m1/code/data.py` |
| NFNAccuracyPredictor, extract_weight_tensors, collate_weights | `from h_m1.nfn_model import NFNAccuracyPredictor, collate_weights` | `docs/youra_research/h-m1/code/nfn_model.py` |
| train_nfn, evaluate_nfn, set_seed | `from h_m1.train import train_nfn, evaluate_nfn, set_seed` | `docs/youra_research/h-m1/code/train.py` |

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation, not h-m1's own 03_architecture.md spec, and NOT h-m2's PRD which incorrectly assumes official `nfn` lib)

**Note**: Copy `data.py`, `nfn_model.py`, `train.py`, `config.py` style into `h-m2/code/` (small files, self-contained per H-M1 precedent) rather than cross-folder imports. Epic A-1 handles this. Do NOT `pip install nfn` — not needed, H-M1's custom equivariant model already satisfies the mechanism (architectural permutation equivariance vs. non-equivariant MLP).

---

## Directory Structure

```
docs/youra_research/h-m2/code/
  config.py           # dataclass config + N_VALUES sweep + SEEDS (10)
  data.py              # copied from h-m1 (ResNet20, zoo gen/load/split)
  nfn_model.py          # copied from h-m1 (NFNAccuracyPredictor, collate_weights)
  mlp_model.py           # NEW: MLPBaseline (flattened weights -> scalar)
  train_common.py         # generic train/eval loop parametrized by model+collate fn
  sweep.py                  # for each N in N_VALUES, for each seed: sample train_pool[:N], train both models, eval on fixed test
  stats.py                    # paired t-test, R2 delta aggregation across seeds
  evaluate.py                   # figures: gate bar chart, learning curve, per-seed scatter, box plot
  run_experiment.py               # orchestration entrypoint, saves results.json
```

---

## Module Interfaces

### config.py (`code/config.py`)

**Dependencies**: none

```python
@dataclass
class DataConfig:
    zoo_dir: str = "data/model_zoo"
    n_pool_models: int = 6000   # covers max N=5000 train + 500 test
    n_test: int = 500
    split_seed: int = 42

@dataclass
class NFNConfig:
    hidden_dim: int = 128
    num_layers: int = 3   # matches H-M1 defaults

@dataclass
class MLPConfig:
    hidden_dim: int = 256
    num_hidden_layers: int = 2

@dataclass
class TrainConfig:
    lr: float = 1e-3
    batch_size: int = 32
    epochs: int = 50
    seeds: List[int] = field(default_factory=lambda: list(range(10)))

N_VALUES = [100, 250, 500, 1000, 2500, 5000]
PRIMARY_N = 500
R2_DELTA_TARGET = 0.1
ALPHA = 0.05

@dataclass
class Config:
    data: DataConfig = field(default_factory=DataConfig)
    nfn: NFNConfig = field(default_factory=NFNConfig)
    mlp: MLPConfig = field(default_factory=MLPConfig)
    train: TrainConfig = field(default_factory=TrainConfig)
    figures_dir: str = "figures"
    results_dir: str = "results"

CONFIG = Config()
```

### data.py, nfn_model.py

Copied verbatim from H-M1 (see External Dependencies table).

### mlp_model.py (`code/mlp_model.py`)

**Dependencies**: torch, nfn_model.extract_weight_tensors (for consistent flattening)

```python
class MLPBaseline(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 256): ...
    def forward(self, x: torch.Tensor) -> torch.Tensor: ...  # (B,) prediction

def flatten_state_dict(state_dict: dict) -> torch.Tensor: ...  # 1D flat weight vector (~270K dims)
def collate_flat(items: list[tuple[dict, float]]) -> tuple[torch.Tensor, torch.Tensor]: ...  # (B, D), (B,)
def infer_input_dim(sample_state_dict: dict) -> int: ...
```

### train_common.py (`code/train_common.py`)

**Dependencies**: config, sklearn.metrics

```python
def train_model(
    model: nn.Module, train_items: list, collate_fn: Callable,
    cfg: config.Config = config.CONFIG, device: str = "cpu",
) -> dict: ...  # no early-stop val split (N can be as low as 100); trains fixed cfg.train.epochs, returns {"train_loss": [...]}

def evaluate_model(
    model: nn.Module, test_items: list, collate_fn: Callable, device: str = "cpu",
) -> dict: ...  # {"r2": float, "mae": float, "y_true": ndarray, "y_pred": ndarray}
```

### sweep.py (`code/sweep.py`)

**Dependencies**: nfn_model, mlp_model, train_common, config, data

```python
def run_single(n: int, seed: int, train_pool: list, test_items: list, cfg=config.CONFIG) -> dict:
    ...  # trains NFN + MLP on same N-sample subset (seeded), returns {"n": n, "seed": seed, "r2_nfn": float, "r2_mlp": float}

def run_sweep(train_pool: list, test_items: list, n_values: list = config.N_VALUES,
              seeds: list = config.CONFIG.train.seeds) -> list[dict]:
    ...  # full N x seed grid, returns list of run_single results
```

### stats.py (`code/stats.py`)

**Dependencies**: scipy.stats, numpy

```python
def paired_ttest(r2_nfn_scores: list[float], r2_mlp_scores: list[float]) -> tuple[float, float]: ...  # (t_stat, p_value)
def summarize_n(results: list[dict], n: int) -> dict: ...  # {"mean_delta", "std_delta", "p_value", "pass": bool}
def summarize_all(results: list[dict]) -> dict: ...  # per-N summary dict, keyed by n
```

### evaluate.py (`code/evaluate.py`)

**Dependencies**: matplotlib, stats

```python
def plot_gate_comparison(results: list[dict], n: int, out_path: str) -> None: ...  # bar chart w/ error bars at N=500
def plot_learning_curve(results: list[dict], n_values: list, out_path: str) -> None: ...  # R2 vs N, both methods
def plot_seed_scatter(results: list[dict], n: int, out_path: str) -> None: ...  # NFN R2 vs MLP R2, identity line
def plot_box_distribution(results: list[dict], n: int, out_path: str) -> None: ...  # box plot at N=500
```

### run_experiment.py (`code/run_experiment.py`)

**Dependencies**: all above

```python
def main(n_values: list = config.N_VALUES, seeds: list = config.CONFIG.train.seeds) -> dict:
    ...  # load/split data -> run_sweep -> stats summary -> figures -> save results.json
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Bootstrap module | Copy H-M1 data.py, nfn_model.py, config.py style into h-m2/code, extend config with N_VALUES/seeds | 4 | 1+1+1+1 |
| A-2 | Data pool prep | Generate/load 6000-model synthetic zoo, fixed 500-test split (seed=42), verify pool covers N=5000 | 4 | 1+1+1+1 |
| A-3 | MLP baseline model | mlp_model.py: MLPBaseline, flatten_state_dict (~270K dims), collate_flat | 6 | 2+1+2+1 |
| A-4 | Generic train/eval loop | train_common.py: parametrized by model+collate_fn, no early-stop val carve (works for N=100..5000) | 7 | 2+2+2+1 |
| A-5 | Per-run trainer | sweep.py::run_single: seeded N-sample draw, train NFN+MLP, eval both on fixed test set | 8 | 2+2+2+2 |
| A-6 | Sweep orchestration | sweep.py::run_sweep: N x seed grid (6 N-values x 10 seeds = 60 runs x 2 models), progress logging | 8 | 2+2+2+2 |
| A-7 | Statistical testing | stats.py: paired t-test across 10 seeds at N=500, per-N summary, pass/fail against R2 delta >=0.1 & p<0.05 | 7 | 2+2+2+1 |
| A-8 | Figures | evaluate.py: gate bar chart, learning curve, per-seed scatter, box plot (4 required figures) | 6 | 2+2+1+1 |
| A-9 | Orchestration + results | run_experiment.py: end-to-end run, results.json (all N/seed R2s + stats + pass/fail), runtime budget check | 5 | 2+1+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1, A-2, A-3, A-4, A-5, A-6, A-7, A-8, A-9]

**Note**: Full sweep is 6 N-values x 10 seeds x 2 models = 120 training runs; at N=5000/50 epochs this dominates runtime. NFR-1 budget (30 min/seed/N) applies per model per (N,seed) pair — A-6 should log elapsed time per run and allow resuming/partial N-subset runs if Phase 4 execution time is constrained. Primary gate check only requires N=500 (10 seeds x 2 models = 20 runs); full sweep is for the optional learning-curve figure and can be deprioritized if runtime is tight.
