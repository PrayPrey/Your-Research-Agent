# Logic: H-M5 (MECHANISM)

**Hypothesis:** At N=50K, MLP probe invariance > 0.8 (learned from data diversity)

Applied: No MLP-scale/probe-invariance KB pattern found (query "PyTorch CosineAnnealingLR R2 score regression" returned generic install/docs pages, same null result as H-M4) — standard PyTorch AdamW+CosineAnnealingLR loop, sklearn.metrics.r2_score, from first principles.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M4)
**Status**: API signatures verified from actual code.
**Analyzed Path**: `h-m4/code/{data_gen.py, probe_invariance.py}` (via h-m4/03_logic.md, itself verified against actual code), `h-m3/code/mlp_model.py` (re-verified directly).
**Relevant Symbols**: `MLPMatched.__init__/forward` (h-m3/code/mlp_model.py, re-read directly — confirms `input_dim -> 256 -> 128 -> 1`), `load_model_zoo_population`, `split_train_test`, `to_dataset` (h-m4/code/data_gen.py), `compute_probe_invariance`, `evaluate_population_invariance` (h-m4/code/probe_invariance.py). No R² computation exists in any base hypothesis — new for H-M5.

---

## External Dependencies API

```python
# From: h-m4/code/data_gen.py (ACTUAL CODE, per h-m4/03_architecture.md Codebase Analysis)
def load_model_zoo_population(data_path: str = MODELZOO_DATA_PATH, max_models: Optional[int] = None) -> List[Dict]:
    """torch.load(data_path) -> list of model dicts (state_dict, accuracy). max_models=None -> all ~42547."""
    ...

def split_train_test(population: List[Dict], n_train: int, n_test: int, seed: int) -> Tuple[List[Dict], List[Dict]]:
    """random.Random(seed).shuffle then slice [0:n_train], [n_train:n_train+n_test]."""
    ...

def to_dataset(population: List[Dict]) -> torch.utils.data.TensorDataset:
    """flatten_state_dict per model -> stack [N, D]; accuracy -> [N, 1]."""
    ...

# From: h-m4/code/probe_invariance.py (ACTUAL CODE)
def evaluate_population_invariance(
    model: nn.Module, test_population: List[Dict],
    hidden_dims: Tuple[int, ...] = (32, 32), num_permutations: int = 10,
) -> Dict:
    """-> {"mean_invariance": float, "std_invariance": float, "mean_cv": float,
    "invariance_scores": List[float]}. Methodology identical to H-M4 (FR-4 parity)."""
    ...
```

**Note**: `hidden_dims` param is for the *permutation structure* of the CNN weight layout (unrelated to H-M5's MLP probe hidden dims [512,256]) — pass through unmodified, do not confuse with `MLPMatchedWide`'s own architecture.

**MODELZOO_DATA_PATH** hardcoded in `h-m4/code/data_gen.py` points to a path under a different repo root (`YouRA_no_VSA_sonnet46`). Verify reachability; if unreachable pass `data_path=` explicitly.

---

## S-1/S-4: sys.path + data loading (reuse `h-m4/code/data_gen.py` unmodified)

**Applied**: sys.path injection pattern, matches H-M4's own reuse of h-m3/h-m1 code dirs.

```python
H_M4_CODE_DIR = "../../h-m4/code"
# sys.path.insert(0, H_M4_CODE_DIR)
# from data_gen import load_model_zoo_population, split_train_test, to_dataset
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| X (train) | [~40547, ~50000] | flattened CNN weights, full scale |
| X (test) | [2000, ~50000] | held out for invariance |
| y | [N, 1] | test_acc target |

Memory note: batch loading required for ~50K-dim x 42K-row float32 (~8.4GB) — use `DataLoader`, do not materialize full dense tensor eagerly if avoidable (S-4 budget covers this).

---

## S-2: mlp_model_wide.py (`h-m5/code/mlp_model_wide.py`)

**Applied**: Direct variant of h-m3's `MLPMatched`, widened per PRD FR-2.2.

```python
class MLPMatchedWide(nn.Module):
    def __init__(self, input_dim: int):
        """input_dim -> 512 -> 256 -> 1, ReLU activations, default init."""
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 512), nn.ReLU(),
            nn.Linear(512, 256), nn.ReLU(),
            nn.Linear(256, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: [B, input_dim] -> [B, 1]"""
        return self.net(x)
```

---

## S-3: train_mlp_scheduled.py (`h-m5/code/train_mlp_scheduled.py`)

**Applied**: Standard AdamW+MSELoss loop (h-m4 pattern) + CosineAnnealingLR scheduler (new, PRD FR-3.2).

```python
def train_mlp_on_subset(
    train_dataset: torch.utils.data.TensorDataset,
    input_dim: int,
    seed: int,
    epochs: int = 50,
    batch_size: int = 64,
    lr: float = 1e-3,
    weight_decay: float = 1e-4,
    device: str = "cpu",
) -> nn.Module:
    """torch.manual_seed(seed) -> MLPMatchedWide(input_dim).to(device) ->
    AdamW(lr, weight_decay) -> CosineAnnealingLR(T_max=epochs) -> MSELoss ->
    DataLoader(shuffle=True) -> epochs loop, scheduler.step() per epoch.
    Returns model.eval()."""
    ...
```

### Pseudo-code

```
1. torch.manual_seed(seed)
2. model = MLPMatchedWide(input_dim).to(device)
3. opt = AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
4. scheduler = CosineAnnealingLR(opt, T_max=epochs)
5. loss_fn = MSELoss()
6. loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
7. for epoch in range(epochs):
     for x_batch, y_batch in loader:      # x_batch: [B, input_dim], y_batch: [B, 1]
         opt.zero_grad()
         pred = model(x_batch.to(device))  # [B, 1]
         loss = loss_fn(pred, y_batch.to(device))
         loss.backward(); opt.step()
     scheduler.step()
8. return model.eval()
```

---

## S-5: metrics.py (`h-m5/code/metrics.py`)

**Applied**: sklearn.metrics.r2_score, plain dict-based comparison/gate functions.

```python
def compute_r2(
    model: nn.Module, test_dataset: torch.utils.data.TensorDataset, device: str = "cpu",
) -> float:
    """Batch-predict over DataLoader(test_dataset), collect y_true/y_pred ->
    sklearn.metrics.r2_score(y_true, y_pred)."""
    ...

def compare_with_baseline(
    hm5_r2: float, hm5_invariance: float,
    hm4_r2: float = 0.0036, hm4_invariance: float = 0.9193,
) -> Dict:
    """-> {"r2_delta": hm5_r2 - hm4_r2, "invariance_delta": hm5_invariance - hm4_invariance,
    "hm4": {"r2": hm4_r2, "invariance": hm4_invariance},
    "hm5": {"r2": hm5_r2, "invariance": hm5_invariance}}"""
    ...

def gate_logic(test_r2: float, mean_invariance: float) -> str:
    """PRD gate table, in order:
    if test_r2 < 0.1: return "INCONCLUSIVE - MLP didn't learn"
    elif mean_invariance > 0.8: return "PASS - MLP learned invariance from data"
    else: return "FAIL - MLP learns but NOT invariance" """
    ...
```

---

## S-6/S-7: run_experiment.py — orchestration (`h-m5/code/run_experiment.py`)

**Applied**: Multi-seed loop mirrors h-m4's `run_seed`/`aggregate_seeds`, extended with R².

```python
def run_seed(
    seed: int, train_pop: List[Dict], test_pop: List[Dict], input_dim: int, device: str = "cpu",
) -> Dict:
    """to_dataset(train_pop) -> train_mlp_on_subset(..., seed, device=device) ->
    compute_r2(model, to_dataset(test_pop), device) ->
    evaluate_population_invariance(model, test_pop) ->
    {"seed": int, "test_r2": float, "mean_invariance": float, "std_invariance": float}"""
    ...

def aggregate_seeds(seed_results: List[Dict]) -> Dict:
    """mean/std/95%-CI of test_r2 and mean_invariance across seeds ->
    {"r2_mean": float, "r2_std": float, "invariance_mean": float, "invariance_std": float,
    "invariance_ci_low": float, "invariance_ci_high": float,
    "gate_status": metrics.gate_logic(r2_mean, invariance_mean)}"""
    ...
```

---

## S-8: Visualization suite (`h-m5/code/run_experiment.py`)

**Applied**: matplotlib bar/scatter/hist, mirrors h-m4's plotting pattern (best-effort, non-blocking).

```python
def plot_gate_comparison_bar(hm4_inv: float, hm5_inv: float, out_path: str) -> None:
    """2-bar chart: N=1K invariance vs N=50K invariance, dashed line at 0.8 threshold."""
    ...

def plot_r2_vs_scale(hm4_r2: float, hm5_r2: float, out_path: str) -> None:
    """2-point line/bar: R² at N=1K vs N=50K, dashed line at 0.1 threshold."""
    ...

def plot_invariance_histogram(invariance_scores: List[float], out_path: str) -> None: ...
def plot_prediction_scatter(orig_preds: List[float], perm_preds: List[float], out_path: str) -> None: ...
```

---

## S-9: main() orchestration + results.json

```python
def main() -> None:
    ...
```

### Pseudo-code

```
1. sys.path.insert(0, H_M4_CODE_DIR)
2. from data_gen import load_model_zoo_population, split_train_test, to_dataset
   from probe_invariance import evaluate_population_invariance

3. population = load_model_zoo_population(max_models=None)   # ~42547 models
4. n_test = 2000; n_train = len(population) - n_test
5. train_pop, test_pop = split_train_test(population, n_train, n_test, seed=42)
6. input_dim = flattened weight dim (~50000, inferred from population[0])

7. seed_results = [run_seed(s, train_pop, test_pop, input_dim, device) for s in range(10)]
8. agg = aggregate_seeds(seed_results)

9. cmp = metrics.compare_with_baseline(agg["r2_mean"], agg["invariance_mean"])

10. plot_gate_comparison_bar(0.9193, agg["invariance_mean"], "h-m5/figures/gate_comparison_bar.png")
11. plot_r2_vs_scale(0.0036, agg["r2_mean"], "h-m5/figures/r2_vs_scale.png")
12. plot_invariance_histogram(seed_results[-1]["invariance_scores"], "h-m5/figures/invariance_histogram.png")
13. plot_prediction_scatter(orig_preds, perm_preds, "h-m5/figures/prediction_scatter.png")
    # pulled from one representative compute_probe_invariance call, seed=0

14. json.dump({"seed_results": seed_results, "aggregate": agg, "comparison": cmp,
               "gate_status": agg["gate_status"]}, "h-m5/results.json")
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| train_dataset X | [~40547, ~50000] | full-scale flattened weights |
| test_dataset X | [2000, ~50000] | held out |
| model batch pred | [64, 1] | training batch_size=64 |

---

## Subtasks

None — all Epic tasks (S-1..S-9) are Low complexity (4-8) per architecture doc's distribution table. Budget: 0 subtasks per allocation.
