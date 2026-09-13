# Logic Design: H-C1 (Statistics/MLP/NFN Convergence at N=5000)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M2 provides data pipeline, NFN, MLP, train/eval loop)
**Status**: Serena project not activated for this path; direct `Read` used as mandatory equivalent analysis of `docs/youra_research/h-m2/code/{data,nfn_model,mlp_model,train_common,config,stats}.py`.
**Analyzed Path**: `docs/youra_research/h-m2/code/`
**Relevant Symbols**: `download_model_zoo`, `load_checkpoints`, `split_test_set` (data.py); `NFNAccuracyPredictor`, `collate_weights` (nfn_model.py); `MLPBaseline`, `flatten_state_dict`, `infer_input_dim`, `collate_flat` (mlp_model.py); `train_model`, `evaluate_model` (train_common.py); `Config`/`DataConfig`/`TrainConfig` (config.py)

**Critical finding — PRD assumes official `nfn` PyPI library; actual H-M2 code uses custom DeepSets-style `NFNAccuracyPredictor(hidden_dim, num_layers)` operating on `List[Tensor]`, not `WeightSpaceFeatures`/`NPLinear`.** This doc follows actual H-M2 code. Do NOT `pip install nfn`.

**Zoo size check**: `generate_model_zoo` produces 6000 models total. `split_test_set(test_size=500)` leaves 5500 in `train_pool`. N=5000 draw is valid (margin=500), unlike H-M2 which only needed up to N=2500 reliably at N_VALUES sweep — confirm zoo cache file is `synthetic_zoo_6000.pt` (already generated, present at `h-m2/code/data/model_zoo/`).

**No Statistics baseline exists in H-M2** — new component required for H-C1 (below).

---

## External Dependencies (Base Hypothesis)

Verified from `docs/youra_research/h-m2/code/` (actual implementation):

```python
# data.py — reuse verbatim (or point at h-m2/code/data/model_zoo/ cache)
def download_model_zoo(dest_dir: str = "data/model_zoo") -> str: ...
def load_checkpoints(zoo_path: str) -> List[Tuple[dict, float]]: ...
def split_test_set(items: List[Tuple[dict,float]], test_size: int = 500, seed: int = 42) -> Tuple[list, list]: ...

# nfn_model.py — reuse verbatim
class NFNAccuracyPredictor(nn.Module):
    def __init__(self, hidden_dim: int = 128, num_layers: int = 3): ...
    def forward(self, weight_tensors: List[Tensor]) -> Tensor: ...  # -> [B]
def collate_weights(items: List[Tuple[dict,float]]) -> Tuple[List[Tensor], Tensor]: ...

# mlp_model.py — reuse verbatim
class MLPBaseline(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 256): ...
    def forward(self, x: Tensor) -> Tensor: ...  # [B,D] -> [B]
def flatten_state_dict(state_dict: dict) -> Tensor: ...
def infer_input_dim(sample_state_dict: dict) -> int: ...
def collate_flat(items: List[Tuple[dict,float]]) -> Tuple[Tensor, Tensor]: ...

# train_common.py — reuse verbatim
def train_model(model, train_items, collate_fn, cfg=config.CONFIG, device="cpu") -> Dict[str, List[float]]: ...
def evaluate_model(model, test_items, collate_fn, device="cpu") -> Dict[str, Any]: ...  # {"r2","mae","y_true","y_pred"}
```

**Verified from**: `docs/youra_research/h-m2/code/` (actual implementation). `data.py`, `nfn_model.py`, `mlp_model.py`, `train_common.py` copied verbatim into `h-c1/code/`. New code: `stats_model.py` (Statistics baseline), `config.py` (N=5000 override), `run_experiment.py`, `convergence.py` (3-way gate).

---

## A-1: Bootstrap [Complexity: Low, Budget: 4]

**Applied**: Standard PyTorch file copy + reuse

### API Signatures

```python
# h-c1/code/config.py — extends h-m2 style, single-N focus
@dataclass
class Config:
    data: DataConfig       # n_pool_models=6000, n_test=500, split_seed=42
    stats: StatsConfig      # (no hyperparams; sklearn LinearRegression)
    mlp: MLPConfig            # hidden_dim=256
    nfn: NFNConfig             # hidden_dim=128, num_layers=3
    train: TrainConfig          # lr=1e-3, batch_size=32, epochs=100, seeds=list(range(10))

N_GATE = 5000
R2_PAIR_DELTA_MAX = 0.03
R2_SANITY_MIN = 0.5
CONFIG = Config()
```

### Subtasks [2/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Copy data.py, nfn_model.py, mlp_model.py, train_common.py | Verbatim from h-m2 |
| L-1-2 | config.py | N_GATE=5000, R2_PAIR_DELTA_MAX=0.03, epochs=100 (per PRD) |

---

## A-2: Statistics Baseline [Complexity: Medium, Budget: 8]

**Applied**: Standard sklearn `LinearRegression` (matches PRD Section 5 exactly)

### API Signatures

```python
def extract_layer_stats(state_dict: dict) -> np.ndarray:
    """Per-tensor [mean, std, min, max] concat across all state_dict entries. -> [4*L]"""
    ...

def infer_stats_dim(sample_state_dict: dict) -> int:
    """len(extract_layer_stats(sample_state_dict))."""
    ...

def collate_stats(items: List[Tuple[dict, float]]) -> Tuple[np.ndarray, np.ndarray]:
    """items -> (X [B, 4L], y [B]). Stack extract_layer_stats per item."""
    ...

class StatisticsBaseline:
    """sklearn LinearRegression wrapper matching train_model/evaluate_model interface."""
    def __init__(self):
        self.model = LinearRegression()

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        self.model.fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict(X)


def train_stats_model(train_items: List[Tuple[dict, float]]) -> StatisticsBaseline:
    """collate_stats(train_items) -> fit -> return fitted model."""
    ...

def evaluate_stats_model(model: StatisticsBaseline, test_items: List[Tuple[dict, float]]) -> Dict[str, Any]:
    """Returns {"r2": float, "mae": float, "y_true": ndarray, "y_pred": ndarray} (same shape as evaluate_model)."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| X (stats) | [B, 4*L] | L = num state_dict tensors (conv/bn/fc), 4 stats each |
| y | [B] | accuracy 0-1 |

### Pseudo-code (extract_layer_stats)

```
feats = []
for name, param in state_dict.items():
    t = param.flatten()
    feats += [t.mean(), t.std(), t.min(), t.max()]
return np.array(feats)  # [4L]
```

### Subtasks [4/8 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | extract_layer_stats | mean/std/min/max per tensor, fixed key order |
| L-2-2 | collate_stats | batch extract + stack (numpy, not torch — sklearn native) |
| L-2-3 | StatisticsBaseline + train/evaluate_stats_model | LinearRegression fit/predict, r2_score/mean_absolute_error via sklearn.metrics |
| L-2-4 | interface parity | evaluate_stats_model returns same dict keys as evaluate_model (for shared convergence.py logic) |

---

## A-3: Per-Seed 3-Way Runner [Complexity: Medium, Budget: 8]

**Applied**: Paired-comparison sweep pattern from H-M2 A-5, extended to 3 methods

### API Signatures

```python
def run_single(
    seed: int,
    train_pool: List[Tuple[dict, float]], test_items: List[Tuple[dict, float]],
    cfg: config.Config = config.CONFIG,
) -> Dict[str, float]:
    """Seeded N=5000 draw from train_pool, train Stats+MLP+NFN on same subset, eval all three on test_items."""
    ...
```

### Pseudo-code

```
1. set_seed(seed)
2. idx = random.Random(seed).sample(range(len(train_pool)), config.N_GATE)  # N=5000
3. subset = [train_pool[i] for i in idx]
4. input_dim = infer_input_dim(subset[0][0])           # for MLP
5. stats_model = train_stats_model(subset)
6. mlp = MLPBaseline(input_dim=input_dim, hidden_dim=cfg.mlp.hidden_dim)
7. nfn = NFNAccuracyPredictor(hidden_dim=cfg.nfn.hidden_dim, num_layers=cfg.nfn.num_layers)
8. train_model(mlp, subset, collate_flat, cfg)
9. train_model(nfn, subset, collate_weights, cfg)
10. r2_stats = evaluate_stats_model(stats_model, test_items)["r2"]
11. r2_mlp   = evaluate_model(mlp, test_items, collate_flat)["r2"]
12. r2_nfn   = evaluate_model(nfn, test_items, collate_weights)["r2"]
13. return {"seed": seed, "n": config.N_GATE, "r2_stats": r2_stats, "r2_mlp": r2_mlp, "r2_nfn": r2_nfn}
```

### Subtasks [2/8 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | run_single | Seeded N=5000 subset draw + triple train + triple eval |
| L-3-2 | model instantiation | Stats/MLP/NFN built fresh per seed (no shared state) |

---

## A-4: Sweep Orchestration [Complexity: Low, Budget: 6]

### API Signatures

```python
def run_sweep(
    train_pool: list, test_items: list,
    seeds: list = config.CONFIG.train.seeds,
) -> List[Dict[str, float]]:
    """10 seeds x run_single (N=5000 fixed). Logs elapsed time per seed."""
    ...
```

### Pseudo-code

```
results = []
for seed in seeds:
    t0 = time.time()
    r = run_single(seed, train_pool, test_items)
    r["elapsed_sec"] = time.time() - t0
    results.append(r)
    log(f"seed={seed} r2_stats={r['r2_stats']:.3f} r2_mlp={r['r2_mlp']:.3f} r2_nfn={r['r2_nfn']:.3f} ({r['elapsed_sec']:.0f}s)")
return results
```

### Subtasks [1/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | run_sweep | 10-seed loop, per-run timing log |

---

## A-5: Pairwise Convergence Gate [Complexity: Medium, Budget: 8]

**Applied**: Pairwise |mean R² delta| gate (novel to H-C1; not in H-M2 which used single-pair t-test)

### API Signatures

```python
PAIRS = [("stats", "mlp"), ("stats", "nfn"), ("mlp", "nfn")]

def summarize_gate(results: List[Dict]) -> Dict[str, Any]:
    """Mean/std R2 per method across 10 seeds, pairwise |delta| for all 3 pairs, sanity + gate pass flags."""
    ...

def pairwise_deltas(means: Dict[str, float]) -> Dict[str, float]:
    """{"stats_mlp": |a-b|, "stats_nfn": |a-c|, "mlp_nfn": |b-c|}."""
    ...
```

### Pseudo-code (summarize_gate)

```
methods = ["stats", "mlp", "nfn"]
means = {m: mean([r[f"r2_{m}"] for r in results]) for m in methods}
stds  = {m: std([r[f"r2_{m}"] for r in results]) for m in methods}

deltas = {}
for (a, b) in PAIRS:
    deltas[f"{a}_{b}"] = abs(means[a] - means[b])

max_delta = max(deltas.values())
sanity_pass = all(means[m] > config.R2_SANITY_MIN for m in methods)
gate_pass = sanity_pass and max_delta <= config.R2_PAIR_DELTA_MAX

return {
    "means": means, "stds": stds, "pairwise_deltas": deltas,
    "max_delta": max_delta, "sanity_pass": sanity_pass, "gate_pass": gate_pass,
}
```

### Subtasks [3/8 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | summarize_gate | Per-method mean/std, all 3 pairwise deltas, max_delta, gate_pass |
| L-5-2 | pairwise_deltas | Helper — 3-combination abs diff of means |
| L-5-3 | sanity_pass check | R² > 0.5 per method (PoC sanity, independent of gate) |

---

## A-6: Figures [Complexity: Low, Budget: 6]

### API Signatures

```python
def plot_r2_comparison(results: list, out_path: str) -> None: ...  # bar: Stats/MLP/NFN mean R2 +/- std (mandatory)
def plot_pairwise_heatmap(deltas: dict, out_path: str) -> None: ...  # 3x3 heatmap |R2_i - R2_j|
```

### Subtasks [2/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | plot_r2_comparison | Mandatory gate figure — 3-bar chart with error bars, threshold line at ±0.03 band |
| L-6-2 | plot_pairwise_heatmap | Optional — 3x3 |Δ| matrix visualization |

---

## A-7: Orchestration + Results [Complexity: Low, Budget: 5]

### API Signatures

```python
def main(seeds: list = config.CONFIG.train.seeds) -> dict:
    """Load/split data (reuse h-m2 cache) -> run_sweep -> summarize_gate -> figures -> save results.json."""
    ...
```

### Pseudo-code

```
1. zoo_path = download_model_zoo(cfg.data.zoo_dir)          # reuses cached synthetic_zoo_6000.pt
2. items = load_checkpoints(zoo_path)
3. train_pool, test_items = split_test_set(items, cfg.data.n_test, cfg.data.split_seed)  # 5500 / 500
4. assert len(train_pool) >= config.N_GATE                  # 5500 >= 5000
5. results = run_sweep(train_pool, test_items, seeds)
6. gate = summarize_gate(results)
7. plot_r2_comparison(results, f"{cfg.figures_dir}/r2_comparison_N5000.png")
8. plot_pairwise_heatmap(gate["pairwise_deltas"], f"{cfg.figures_dir}/pairwise_heatmap.png")
9. save_json({"results": results, "gate": gate}, f"{cfg.results_dir}/metrics.json")
10. log(f"GATE PASS: {gate['gate_pass']} (max_delta={gate['max_delta']:.4f}, threshold={config.R2_PAIR_DELTA_MAX})")
11. return gate
```

### Subtasks [2/5 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | main | End-to-end orchestration, reuses h-m2 zoo cache path directly |
| L-7-2 | metrics.json save | Per-seed R2 (3 methods) + gate summary + pass/fail |

---

## Self-Validation

- No ASCII diagrams: pass
- Docstrings <=2 lines: pass
- Tensor shapes in comments/tables only where non-obvious: pass
- Subtask counts within budgets: pass (A-1 2/4, A-2 4/8, A-3 2/8, A-4 1/6, A-5 3/8, A-6 2/6, A-7 2/5)
- Codebase Analysis (Serena) section included: pass
- Archon KB searched ("linear regression baseline R2 sklearn") — standard pattern, marked "Standard PyTorch/sklearn"
