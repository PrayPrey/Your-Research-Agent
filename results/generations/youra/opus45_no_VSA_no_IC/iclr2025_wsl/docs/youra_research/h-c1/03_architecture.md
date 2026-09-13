# Architecture: H-C1 (Convergence at N=5000: Statistics vs MLP vs NFN)

**Type**: CONDITION | **Applied**: paired multi-method comparison at fixed large N (extends H-M2's N-sweep pattern to a 3-way gate check)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M2 provides data pipeline, NFN, MLP, train/eval, stats scaffolding)
**Status**: Serena has no active project registered for this path; direct `Read` used as equivalent MANDATORY analysis of `docs/youra_research/h-m2/code/`, consistent with H-M2's own precedent (Serena unavailable there too).
**Analyzed Path**: `docs/youra_research/h-m2/code/`
**Findings**:
- **CRITICAL DEVIATION** (inherited from H-M2, still true here): the brief assumes the official `nfn` PyPI library (`NPLinear`/`HNPPool`/`WeightSpaceFeatures`). H-M2's *actual* `nfn_model.py` is a custom DeepSets-style equivariant model operating on `List[Tensor]` via `extract_weight_tensors`/`collate_weights` — no `nfn` install. H-C1 reuses this actual code, not the brief's snippet.
- H-M2 has NFN + MLP but **no Statistics baseline** — new module needed (`stats_model.py`, ridge/linear regression on layer-wise weight stats, consistent with H-E1 naming per brief).
- `config.py` already defines `N_VALUES` including 5000 and `data.n_pool_models=6000`, `n_test=500` — sufficient pool, no re-generation needed.
- `train_common.py::train_model/evaluate_model` are model-agnostic (parametrized by `collate_fn`) — reusable unchanged for Statistics too, given a `collate_stats` function.
- `stats.py` (H-M2) only does pairwise NFN-vs-MLP paired t-test; H-C1 needs 3-way pairwise |ΔR²| ≤ 0.03 gate — extend, not replace.
- `data.py::split_test_set(seed=42)` — reuse identical split for parity across all H-M hypotheses.

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| ResNet20, generate_model_zoo, load_checkpoints, split_test_set | copy into `h-c1/code/data.py` | `docs/youra_research/h-m2/code/data.py` |
| NFNAccuracyPredictor, extract_weight_tensors, collate_weights | copy into `h-c1/code/nfn_model.py` | `docs/youra_research/h-m2/code/nfn_model.py` |
| MLPBaseline, flatten_state_dict, collate_flat, infer_input_dim | copy into `h-c1/code/mlp_model.py` | `docs/youra_research/h-m2/code/mlp_model.py` |
| train_model, evaluate_model | copy into `h-c1/code/train_common.py` | `docs/youra_research/h-m2/code/train_common.py` |
| Config dataclasses (data/nfn/mlp/train) | copy + extend into `h-c1/code/config.py` | `docs/youra_research/h-m2/code/config.py` |

**Verified from**: `docs/youra_research/h-m2/code/` (actual implementation, matching H-M2's own precedent of copying small self-contained files rather than cross-folder imports).

---

## Directory Structure

```
docs/youra_research/h-c1/code/
  config.py           # copied from h-m2 + StatsConfig + PAIRWISE_DELTA_TARGET=0.03
  data.py              # copied verbatim from h-m2
  nfn_model.py          # copied verbatim from h-m2
  mlp_model.py           # copied verbatim from h-m2
  stats_model.py           # NEW: StatisticsBaseline (ridge/linear on layer stats) + feature extraction
  train_common.py         # copied verbatim from h-m2 (already model-agnostic)
  run_n5000.py              # NEW: single-N (5000) x 10-seed run for all 3 methods
  stats.py                    # extended from h-m2: 3-way pairwise |delta| gate check
  evaluate.py                   # extended from h-m2: bar chart (3 methods) + pairwise heatmap
  run_experiment.py               # orchestration entrypoint, saves results.json
```

---

## Module Interfaces

### config.py (`code/config.py`)

**Dependencies**: none

```python
# DataConfig, NFNConfig, MLPConfig, TrainConfig — copied unchanged from h-m2

@dataclass
class StatsConfig:
    feature_stats: List[str] = field(default_factory=lambda: ["mean", "std", "min", "max"])
    ridge_alpha: float = 1.0   # or None for plain LinearRegression

N_FOCUS = 5000               # this hypothesis's fixed N
PAIRWISE_DELTA_TARGET = 0.03  # gate threshold (not 0.1 as in h-m2)

@dataclass
class Config:
    data: DataConfig = field(default_factory=DataConfig)
    nfn: NFNConfig = field(default_factory=NFNConfig)
    mlp: MLPConfig = field(default_factory=MLPConfig)
    stats_model: StatsConfig = field(default_factory=StatsConfig)
    train: TrainConfig = field(default_factory=TrainConfig)
    figures_dir: str = "figures"
    results_dir: str = "results"

CONFIG = Config()
```

### data.py, nfn_model.py, mlp_model.py, train_common.py

Copied verbatim from H-M2 (see External Dependencies table).

### stats_model.py (`code/stats_model.py`)

**Dependencies**: sklearn.linear_model, numpy

```python
def extract_layer_stats(state_dict: dict, stats: list[str] = None) -> np.ndarray: ...  # [mean,std,min,max] per layer, flat vector
def collate_stats(items: list[tuple[dict, float]]) -> tuple[np.ndarray, np.ndarray]: ...  # (N, D_stats), (N,)

class StatisticsBaseline:
    def __init__(self, alpha: float = 1.0): ...  # wraps sklearn Ridge
    def fit(self, X: np.ndarray, y: np.ndarray) -> "StatisticsBaseline": ...
    def predict(self, X: np.ndarray) -> np.ndarray: ...
```

### run_n5000.py (`code/run_n5000.py`)

**Dependencies**: nfn_model, mlp_model, stats_model, train_common, config, data

```python
def run_single(seed: int, train_pool: list, test_items: list, cfg=config.CONFIG) -> dict:
    ...  # seeded 5000-sample draw; train NFN+MLP (torch loop) + Statistics (sklearn fit);
    ...  # eval all 3 on fixed test set; returns {"seed": seed, "r2_nfn": float, "r2_mlp": float, "r2_stats": float}

def run_all_seeds(train_pool: list, test_items: list, seeds: list = config.CONFIG.train.seeds) -> list[dict]:
    ...  # 10 runs (one per seed) at fixed N=5000
```

### stats.py (`code/stats.py`)

**Dependencies**: scipy.stats, numpy, itertools

```python
def pairwise_deltas(results: list[dict], methods: list[str] = ("nfn", "mlp", "stats")) -> dict:
    ...  # {"nfn_vs_mlp": mean_abs_delta, "nfn_vs_stats": ..., "mlp_vs_stats": ...}

def summarize(results: list[dict]) -> dict:
    ...  # per-method mean/std R2 across seeds + pairwise_deltas + gate "pass": bool
    ...  # pass = max(pairwise_deltas.values()) <= config.PAIRWISE_DELTA_TARGET
```

### evaluate.py (`code/evaluate.py`)

**Dependencies**: matplotlib, stats

```python
def plot_gate_comparison(results: list[dict], out_path: str) -> None: ...  # bar chart, 3 methods, error bars (10 seeds)
def plot_pairwise_heatmap(summary: dict, out_path: str) -> None: ...  # |R2_i - R2_j| heatmap, 3x3
def plot_convergence_curve(all_n_results: list[dict] | None, out_path: str) -> None: ...  # optional, if H-M2 sweep results reused
```

### run_experiment.py (`code/run_experiment.py`)

**Dependencies**: all above

```python
def main(seeds: list = config.CONFIG.train.seeds) -> dict:
    ...  # load pool -> split test -> run_all_seeds(N=5000) -> stats.summarize -> figures -> save results.json
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Bootstrap module | Copy data.py, nfn_model.py, mlp_model.py, train_common.py, config.py from h-m2; extend config with StatsConfig/N_FOCUS/PAIRWISE_DELTA_TARGET | 5 | 1+1+2+1 |
| A-2 | Data pool prep | Load/generate 6000-model pool (reuse h-m2 cache if present), fixed 500-test split (seed=42), verify N=5000 train slice available | 4 | 1+1+1+1 |
| A-3 | Statistics baseline | stats_model.py: extract_layer_stats, collate_stats, StatisticsBaseline (Ridge wrapper) | 5 | 1+1+2+1 |
| A-4 | Single-run trainer | run_n5000.py::run_single: seeded 5000-sample draw, train NFN+MLP+Statistics, eval all 3 on fixed test | 8 | 2+2+2+2 |
| A-5 | Seed loop | run_n5000.py::run_all_seeds: 10 seeds x 3 methods = 30 fits, progress logging, runtime tracking | 6 | 2+1+2+1 |
| A-6 | 3-way statistical gate | stats.py: pairwise_deltas across all method pairs, summarize with pass/fail against 0.03 threshold | 6 | 2+1+2+1 |
| A-7 | Figures | evaluate.py: 3-method bar chart w/ error bars, pairwise delta heatmap, optional convergence curve | 5 | 2+1+1+1 |
| A-8 | Orchestration + results | run_experiment.py: end-to-end run, results.json (per-seed R2s + pairwise summary + gate pass/fail) | 4 | 1+1+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1, A-2, A-3, A-4, A-5, A-6, A-7, A-8]

**Note**: Single N (5000) x 10 seeds x 3 methods = 30 fits total (vs H-M2's 120 across full sweep) — substantially lighter runtime. NFN/MLP dominate cost (torch training loops); Statistics (sklearn Ridge) is near-instant. A-4/A-5 should log elapsed time per method per seed.
