# Logic Design: H-M2 (NFN Data Efficiency vs MLP)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1 provides data pipeline + NFN model)
**Status**: Serena project not pre-activated for `TEST_wsl` path (`No active project` error on `get_symbols_overview`) — direct `Read` used as mandatory equivalent analysis of `docs/youra_research/h-m1/code/{data,nfn_model,train,config}.py`, matching h-m2 architecture doc's precedent.
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Relevant Symbols**: `ResNet20`, `generate_model_zoo`, `download_model_zoo`, `load_checkpoints`, `split_test_set` (data.py); `NFNAccuracyPredictor`, `extract_weight_tensors`, `collate_weights` (nfn_model.py); `train_nfn`, `evaluate_nfn`, `set_seed` (train.py); `Config`/`DataConfig`/`TrainConfig` (config.py)

**Critical finding — spec vs actual code mismatch**: PRD/brief specify the official `nfn` PyPI library (`WeightSpaceFeatures`, `NPLinear`, `HNPPool`, `network_spec_from_wsfeat`). H-M1's *actual code* implements a custom DeepSets-style equivariant model operating on `List[Tensor]`, with `NFNAccuracyPredictor(hidden_dim=128, num_layers=3)` (no `network_spec` arg) and `collate_weights(items) -> (List[Tensor], Tensor)`, not `WeightSpaceFeatures`. This logic doc follows **actual code**, not the PRD's official-library assumption — do NOT `pip install nfn`.

---

## External Dependencies (Base Hypothesis)

Verified from `docs/youra_research/h-m1/code/` (actual implementation):

```python
# data.py
class ResNet20(nn.Module):
    def __init__(self, num_classes: int = 10): ...
    def forward(self, x: Tensor) -> Tensor: ...  # [B,3,32,32] -> [B,10]

def generate_model_zoo(n_models: int = 6000, dest_dir: str = "data/model_zoo") -> str: ...  # returns cache_file path, idempotent
def download_model_zoo(dest_dir: str = "data/model_zoo") -> str: ...  # calls generate_model_zoo(n_models=6000, ...)
def load_checkpoints(zoo_path: str) -> List[Tuple[dict, float]]: ...  # [(state_dict, accuracy), ...]
def split_test_set(items: List[Tuple[dict, float]], test_size: int = 500, seed: int = 42) -> Tuple[list, list]: ...  # (train_pool, test)

# nfn_model.py
class NFNAccuracyPredictor(nn.Module):
    def __init__(self, hidden_dim: int = 128, num_layers: int = 3): ...  # NOTE: no network_spec param (custom impl, not official nfn lib)
    def forward(self, weight_tensors: List[Tensor]) -> Tensor: ...  # -> [B] predicted accuracy
    def get_invariant_repr(self, weight_tensors: List[Tensor]) -> Tensor: ...  # -> [B, hidden_dim]

def extract_weight_tensors(state_dict: dict) -> List[Tensor]: ...  # per-layer 2D+ weight matrices, each [1, out, in(, h, w)]
def collate_weights(items: List[Tuple[dict, float]]) -> Tuple[List[Tensor], Tensor]: ...  # (n_layers x [B,out,in(,h,w)], [B] accs)

# train.py
def set_seed(seed: int) -> None: ...
def train_nfn(model, train_items: list, val_items: list, cfg: config.Config = config.CONFIG, device: str = "cuda"|"cpu") -> Dict[str, List[float]]: ...
def evaluate_nfn(model, test_items: list, device: str) -> Dict[str, float]: ...  # {"r2","mae","y_true","y_pred"}
```

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation, not h-m1's or h-m2's spec docs). H-m2's own `mlp_model.py`/`train_common.py`/`sweep.py` are new code (below); `data.py`/`nfn_model.py` are copied verbatim into `h-m2/code/`.

---

## A-1..A-2: Bootstrap + Data Pool [Complexity: Low, Budget: 8]

**Applied**: Standard PyTorch file copy + reuse (no new pattern; direct copy per architecture doc's Note)

### API Signatures

```python
# h-m2/code/data.py, nfn_model.py — copied verbatim from h-m1/code/ (see External Dependencies)

# h-m2/code/config.py — new, extends h-m1 style
@dataclass
class Config:
    data: DataConfig      # n_pool_models=6000, n_test=500, split_seed=42
    nfn: NFNConfig         # hidden_dim=128, num_layers=3
    mlp: MLPConfig          # hidden_dim=256, num_hidden_layers=2
    train: TrainConfig       # lr=1e-3, batch_size=32, epochs=50, seeds=list(range(10))

N_VALUES = [100, 250, 500, 1000, 2500, 5000]
PRIMARY_N = 500
R2_DELTA_TARGET = 0.1
ALPHA = 0.05
CONFIG = Config()
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Copy data.py, nfn_model.py | Verbatim from h-m1, adjust imports |
| L-1-2 | config.py | Dataclass config w/ N_VALUES, PRIMARY_N, ALPHA |
| L-1-3 | Zoo generation | `download_model_zoo(dest_dir)` -> 6000 models, cached |
| L-1-4 | Fixed split | `split_test_set(items, test_size=500, seed=42)` -> `(train_pool[5500], test[500])` |

---

## A-3: MLP Baseline Model [Complexity: Medium, Budget: 6]

**Applied**: Standard PyTorch `nn.Sequential` (matches PRD FR-2 exactly)

### API Signatures

```python
class MLPBaseline(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 256):
        """2-layer MLP, ReLU, scalar output."""
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim), nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim), nn.ReLU(),
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, x: Tensor) -> Tensor:
        """x: [B, D] -> [B] (squeezed)."""
        return self.net(x).squeeze(-1)


def flatten_state_dict(state_dict: dict) -> Tensor:
    """Concat all param tensors (same set as extract_weight_tensors uses) into 1D vector, ~270K dims."""
    ...

def infer_input_dim(sample_state_dict: dict) -> int:
    """len(flatten_state_dict(sample_state_dict))."""
    ...

def collate_flat(items: List[Tuple[dict, float]]) -> Tuple[Tensor, Tensor]:
    """items -> (X [B,D], y [B]). Stack flatten_state_dict per item."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| X (flat) | [B, ~270000] | full state_dict flattened (conv+bn+fc), not just `extract_weight_tensors` subset |
| y | [B] | accuracy 0-1 |

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | MLPBaseline | 2-layer, hidden=256, ReLU |
| L-3-2 | flatten_state_dict | torch.cat of all param.flatten() in fixed key order |
| L-3-3 | infer_input_dim | compute D once from one sample |
| L-3-4 | collate_flat | batch flatten + stack |

---

## A-4: Generic Train/Eval Loop [Complexity: Medium, Budget: 7]

**Applied**: Standard PyTorch loop (simplified from h-m1's `train_nfn` — no early-stop val carve since N can be 100)

### API Signatures

```python
def train_model(
    model: nn.Module,
    train_items: List[Tuple[dict, float]],
    collate_fn: Callable[[list], Tuple[Any, Tensor]],
    cfg: config.Config = config.CONFIG,
    device: str = "cpu",
) -> Dict[str, List[float]]:
    """Full cfg.train.epochs, no val split/early stop. Returns {"train_loss": [...]}."""
    ...

def evaluate_model(
    model: nn.Module,
    test_items: List[Tuple[dict, float]],
    collate_fn: Callable,
    device: str = "cpu",
) -> Dict[str, Any]:
    """Returns {"r2": float, "mae": float, "y_true": ndarray, "y_pred": ndarray}."""
    ...
```

### Pseudo-code (train_model)

```
optimizer = Adam(model.parameters(), lr=cfg.train.lr)
for epoch in range(cfg.train.epochs):
    model.train()
    for batch_idx in minibatches(shuffle(train_items), cfg.train.batch_size):
        x, y = collate_fn(batch_idx)                # model-specific: List[Tensor] for NFN, Tensor for MLP
        pred = model(x)                              # [B]
        loss = mse_loss(pred, y)
        loss.backward(); optimizer.step(); optimizer.zero_grad()
        assert not torch.isnan(loss)
return history
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | train_model | Generic loop, no val split, works both collate_fns |
| L-4-2 | evaluate_model | sklearn r2_score/mean_absolute_error |
| L-4-3 | NaN guard | Same assert pattern as h-m1's `train_nfn` |
| L-4-4 | batch iterator helper | Shared minibatch index generator |

---

## A-5: Per-Run Trainer [Complexity: Low, Budget: 8]

**Applied**: Paired-comparison sweep pattern (same-subset train for both models, per architecture doc header)

### API Signatures

```python
def run_single(
    n: int, seed: int,
    train_pool: List[Tuple[dict, float]], test_items: List[Tuple[dict, float]],
    cfg: config.Config = config.CONFIG,
) -> Dict[str, float]:
    """Seeded N-sample draw from train_pool, train NFN+MLP on same subset, eval both on test_items."""
    ...
```

### Pseudo-code

```
1. set_seed(seed)
2. idx = random.Random(seed).sample(range(len(train_pool)), n)
3. subset = [train_pool[i] for i in idx]
4. input_dim = infer_input_dim(subset[0][0])
5. nfn = NFNAccuracyPredictor(hidden_dim=cfg.nfn.hidden_dim, num_layers=cfg.nfn.num_layers)
6. mlp = MLPBaseline(input_dim=input_dim, hidden_dim=cfg.mlp.hidden_dim)
7. train_model(nfn, subset, collate_weights, cfg)
8. train_model(mlp, subset, collate_flat, cfg)
9. r2_nfn = evaluate_model(nfn, test_items, collate_weights)["r2"]
10. r2_mlp = evaluate_model(mlp, test_items, collate_flat)["r2"]
11. return {"n": n, "seed": seed, "r2_nfn": r2_nfn, "r2_mlp": r2_mlp}
```

### Subtasks [4/8 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | run_single | Seeded subset draw + dual train + dual eval |
| L-5-2 | model instantiation | NFN/MLP built fresh per run (no shared state across seeds) |

---

## A-6: Sweep Orchestration [Complexity: Low, Budget: 8]

### API Signatures

```python
def run_sweep(
    train_pool: list, test_items: list,
    n_values: list = config.N_VALUES,
    seeds: list = config.CONFIG.train.seeds,
) -> List[Dict[str, float]]:
    """N x seed grid (default 6x10=60 run_single calls = 120 trainings). Logs elapsed time per run."""
    ...
```

### Pseudo-code

```
results = []
for n in n_values:
    for seed in seeds:
        t0 = time.time()
        r = run_single(n, seed, train_pool, test_items)
        r["elapsed_sec"] = time.time() - t0
        results.append(r)
        log(f"N={n} seed={seed} r2_nfn={r['r2_nfn']:.3f} r2_mlp={r['r2_mlp']:.3f} ({r['elapsed_sec']:.0f}s)")
return results
```

Note: gate check only needs N=500 (10 seeds x 2 models = 20 runs). Full 6-value sweep is for optional learning curve; `run_sweep` can be called with `n_values=[500]` if runtime constrained.

### Subtasks [4/8 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | run_sweep | Nested loop, per-run timing log |
| L-6-2 | partial-sweep support | Allow n_values subset (e.g. `[500]` only) for time-constrained runs |

---

## A-7: Statistical Testing [Complexity: Low, Budget: 7]

**Applied**: `scipy.stats.ttest_rel` paired t-test (standard, per PRD FR-5.2)

### API Signatures

```python
def paired_ttest(r2_nfn_scores: List[float], r2_mlp_scores: List[float]) -> Tuple[float, float]:
    """Returns (t_stat, p_value) via scipy.stats.ttest_rel."""
    ...

def summarize_n(results: List[dict], n: int) -> Dict[str, Any]:
    """Filter results to given n; returns {"mean_delta","std_delta","p_value","pass": bool}."""
    ...

def summarize_all(results: List[dict]) -> Dict[int, Dict[str, Any]]:
    """summarize_n for every distinct n in results, keyed by n."""
    ...
```

### Pseudo-code (summarize_n)

```
rows = [r for r in results if r["n"] == n]
nfn_scores = [r["r2_nfn"] for r in rows]
mlp_scores = [r["r2_mlp"] for r in rows]
deltas = [a - b for a, b in zip(nfn_scores, mlp_scores)]
t_stat, p_value = paired_ttest(nfn_scores, mlp_scores)
return {
    "mean_delta": mean(deltas), "std_delta": std(deltas), "p_value": p_value,
    "pass": mean(deltas) >= config.R2_DELTA_TARGET and p_value < config.ALPHA,
}
```

### Subtasks [4/7 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | paired_ttest | scipy.stats.ttest_rel wrapper |
| L-7-2 | summarize_n | Gate check logic (delta >=0.1 & p<0.05) |
| L-7-3 | summarize_all | Per-N dict for learning curve figure |

---

## A-8: Figures [Complexity: Low, Budget: 6]

### API Signatures

```python
def plot_gate_comparison(results: list, n: int, out_path: str) -> None: ...  # bar: NFN vs MLP mean R2 +/- std, at n
def plot_learning_curve(results: list, n_values: list, out_path: str) -> None: ...  # x=N (log scale), y=mean R2, both lines
def plot_seed_scatter(results: list, n: int, out_path: str) -> None: ...  # x=r2_mlp, y=r2_nfn per seed, identity line
def plot_box_distribution(results: list, n: int, out_path: str) -> None: ...  # boxplot [r2_nfn scores, r2_mlp scores] at n
```

### Subtasks [4/6 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | plot_gate_comparison | Mandatory gate figure (FR-6.1) |
| L-8-2 | plot_learning_curve | R2 vs N, both methods (FR-6.2) |
| L-8-3 | plot_seed_scatter | Per-seed scatter (FR-6.3) |
| L-8-4 | plot_box_distribution | N=500 distribution box plot (FR-6.4) |

---

## A-9: Orchestration + Results [Complexity: Low, Budget: 5]

### API Signatures

```python
def main(n_values: list = config.N_VALUES, seeds: list = config.CONFIG.train.seeds) -> dict:
    """Load/split data -> run_sweep -> summarize_all -> figures -> save results.json. Returns final summary dict."""
    ...
```

### Pseudo-code

```
1. zoo_path = download_model_zoo(cfg.data.zoo_dir)
2. items = load_checkpoints(zoo_path)
3. train_pool, test_items = split_test_set(items, cfg.data.n_test, cfg.data.split_seed)
4. results = run_sweep(train_pool, test_items, n_values, seeds)
5. summary = summarize_all(results)
6. gate = summary[config.PRIMARY_N]
7. plot_gate_comparison(results, config.PRIMARY_N, f"{cfg.figures_dir}/gate_comparison.png")
8. plot_learning_curve(results, n_values, f"{cfg.figures_dir}/learning_curve.png")
9. plot_seed_scatter(results, config.PRIMARY_N, f"{cfg.figures_dir}/seed_scatter.png")
10. plot_box_distribution(results, config.PRIMARY_N, f"{cfg.figures_dir}/box_distribution.png")
11. save_json({"results": results, "summary": summary, "gate_pass": gate["pass"]}, f"{cfg.results_dir}/results.json")
12. return summary
```

### Subtasks [4/5 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-9-1 | main | End-to-end orchestration |
| L-9-2 | results.json save | All N/seed R2s + stats + pass/fail |
| L-9-3 | runtime budget log | Sum elapsed_sec, warn if > NFR-1 budget (30min/seed/N) |

---

## Self-Validation

- No ASCII diagrams: pass
- Docstrings <=2 lines: pass
- Tensor shapes in comments/tables only where non-obvious: pass
- Subtask counts within architecture doc budgets: pass (A-1/2 combined 4/8, A-3 6/6, A-4 7/7, A-5 4/8, A-6 4/8, A-7 4/7, A-8 4/6, A-9 4/5)
- Codebase Analysis (Serena) section included: pass
- Archon KB searched ("MLP baseline comparison paired t-test") — no relevant results, patterns marked "Standard PyTorch"/"scipy.stats.ttest_rel"
