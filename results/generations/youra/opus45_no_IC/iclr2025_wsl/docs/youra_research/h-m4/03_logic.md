# Logic: H-M4 (MECHANISM)

**Hypothesis:** At N=1K, MLP probe invariance < 0.5 (insufficient data diversity)

Applied: No MLP-training/probe-invariance KB pattern found (query "probe invariance API tensor shapes" returned unrelated PyTorch dtype docs, same null result as prior H-M hypotheses) — reused H-M3's MLPMatched + H-M1's permutation infra, standard AdamW/MSE training loop from first principles.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M3, which itself bases on H-M1)
**Status**: API signatures verified from actual code — H-M3's own `03_logic.md` already documents verified signatures for `MLPMatched`, `flatten_state_dict` (h-m3/code), and `generate_permutations`/`permute_state_dict` (h-m1/code), cross-checked here.
**Analyzed Path**: `h-m3/code/{mlp_model.py, test_variance.py}`, `h-m1/code/permute.py`
**Relevant Symbols**: `MLPMatched.__init__/forward`, `flatten_state_dict`, `generate_permutations`, `permute_state_dict`. No training loop or population-generation code exists in either base — new for H-M4.

---

## External Dependencies API

```python
# From: h-m3/code/mlp_model.py (ACTUAL CODE)
class MLPMatched(nn.Module):
    def __init__(self, input_dim: int):
        """input_dim -> 256 -> 128 -> 1, ReLU activations, default init."""
        ...
    def forward(self, x: Tensor) -> Tensor:
        """x: [1, input_dim] -> [1, 1]"""
        ...

# From: h-m3/code/test_variance.py (ACTUAL CODE)
def flatten_state_dict(state_dict: Dict[str, torch.Tensor]) -> torch.Tensor:
    """Concat all values flattened -> [1, input_dim]"""
    ...

# From: h-m1/code/permute.py (ACTUAL CODE)
def generate_permutations(hidden_dims: Tuple[int, ...] = (32, 32), base_seed: int = 0) -> List[torch.Tensor]:
    """One randperm(h) per hidden layer -> [perm_0, perm_1]"""
    ...

def permute_state_dict(
    state_dict: Dict[str, torch.Tensor],
    n_hidden_layers: int = 2,
    perms: List[torch.Tensor] = None,
) -> Dict[str, torch.Tensor]:
    """Apply neuron perms[i] to layer{i}, propagate to layer{i+1} inputs."""
    ...
```

**Verified from**: `h-m3/code/`, `h-m1/code/` (actual implementation, via H-M3's own verified `03_logic.md`). No real Model Zoo dataset code exists anywhere in the repo — synthetic population generation required (matches H-M4 architecture doc's Codebase Analysis finding).

---

## R-1/R-2/R-3: data_gen.py (`h-m4/code/data_gen.py`)

**Applied**: Standard PyTorch `TensorDataset` + reused `generate_test_mlp`-style random init (no import, pattern reuse only per architecture doc).

```python
H_M3_CODE_DIR = "../../h-m3/code"
H_M1_CODE_DIR = "../../h-m1/code"

def generate_model_population(
    n_models: int,
    hidden_dims: Tuple[int, ...] = (32, 32),
    input_dim: int = 32,
    output_dim: int = 10,
    base_seed: int = 0,
) -> List[Dict]:
    """n_models synthetic state_dicts (layer{i}.weight/bias), seed=base_seed+i.
    Each dict gets model["state_dict"] and model["accuracy"] (float,
    deterministic fn of weight-norm + small noise, seeded)."""
    ...

def split_train_test(
    population: List[Dict], n_train: int = 1000, n_test: int = 200, seed: int = 42,
) -> Tuple[List[Dict], List[Dict]]:
    """random.Random(seed).shuffle(population) then slice [0:n_train], [n_train:n_train+n_test]"""
    ...

def to_dataset(population: List[Dict]) -> torch.utils.data.TensorDataset:
    """flatten_state_dict per model -> stack [N, D]; accuracy -> [N, 1]. Returns TensorDataset(X, y)."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| X (dataset) | [N, 32] | N=1000 train / 200 test, input_dim=32 default |
| y (dataset) | [N, 1] | synthetic accuracy target |

---

## R-4: train_mlp.py (`h-m4/code/train_mlp.py`)

**Applied**: Standard PyTorch AdamW/MSELoss training loop, per-seed reproducibility via `torch.manual_seed`.

```python
def train_mlp_on_subset(
    train_dataset: torch.utils.data.TensorDataset,
    input_dim: int,
    seed: int,
    epochs: int = 50,
    batch_size: int = 32,
    lr: float = 1e-3,
) -> nn.Module:
    """torch.manual_seed(seed) -> MLPMatched(input_dim) -> AdamW(lr) -> MSELoss
    -> DataLoader(train_dataset, batch_size, shuffle=True) -> epochs loop.
    Returns model.eval()."""
    ...
```

### Pseudo-code (training loop)

```
1. torch.manual_seed(seed)
2. model = MLPMatched(input_dim); opt = AdamW(model.parameters(), lr=1e-3)
3. loss_fn = MSELoss()
4. loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
5. for epoch in range(50):
     for x_batch, y_batch in loader:
         opt.zero_grad()
         pred = model(x_batch)          # [B, 1]
         loss = loss_fn(pred, y_batch)  # [B, 1]
         loss.backward(); opt.step()
6. return model.eval()
```

---

## R-5: probe_invariance.py (`h-m4/code/probe_invariance.py`)

**Applied**: Reuses H-M1's permute infra, mirrors H-M3's variance-loop pattern with invariance polarity per PRD FR-3.

```python
def compute_probe_invariance(
    model: nn.Module,
    state_dict: Dict[str, torch.Tensor],
    hidden_dims: Tuple[int, ...] = (32, 32),
    num_permutations: int = 10,
) -> Tuple[float, List[float], float]:
    """original pred + num_permutations permuted preds (perm_seed 0..n-1 via
    generate_permutations/permute_state_dict) -> cv = std/(|mean|+1e-8)
    -> invariance = max(0, 1 - min(cv, 1.0)). Returns (invariance, predictions, cv)."""
    ...

def evaluate_population_invariance(
    model: nn.Module,
    test_population: List[Dict],
    hidden_dims: Tuple[int, ...] = (32, 32),
    num_permutations: int = 10,
) -> Dict:
    """loops compute_probe_invariance over test_population state_dicts ->
    {"mean_invariance": float, "std_invariance": float, "mean_cv": float,
     "invariance_scores": List[float]}"""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| flattened state_dict | [1, 32] | same as H-M3 default |
| predictions | list[float], len 11 | 1 original + 10 permuted |

---

## R-6: nfn_control.py (`h-m4/code/nfn_control.py`)

**Applied**: Optional-import graceful-skip pattern (matches H-M3's precedent for missing dependencies).

```python
def load_nfn_model(input_dim: int) -> Optional[nn.Module]:
    """try: import nfn; construct minimal NPLinear-based regressor.
    except ImportError: log warning, return None."""
    ...

def measure_nfn_invariance(
    nfn_model: Optional[nn.Module],
    test_population: List[Dict],
    num_permutations: int = 10,
) -> Optional[Dict]:
    """None if nfn_model is None; else same structure as
    evaluate_population_invariance."""
    ...
```

---

## R-7/R-8/R-9: run_experiment.py (`h-m4/code/run_experiment.py`)

**Applied**: Multi-seed orchestration + gate logic per PRD FR-5, plotting mirrors H-M3's `plot_nfn_vs_mlp_comparison` best-effort pattern.

```python
def run_seed(
    seed: int, train_pop: List[Dict], test_pop: List[Dict], input_dim: int,
) -> Dict:
    """train_mlp_on_subset(to_dataset(train_pop), input_dim, seed) ->
    evaluate_population_invariance(model, test_pop) ->
    {"seed": int, "mean_invariance": float, "std_invariance": float}"""
    ...

def aggregate_seeds(seed_results: List[Dict]) -> Dict:
    """mean/std/95%-CI of mean_invariance across 10 seeds ->
    {"mean": float, "std": float, "ci_low": float, "ci_high": float, "pass": mean < 0.5}"""
    ...

def plot_mlp_vs_nfn_bar(mlp_mean: float, nfn_mean: Optional[float], out_path: str) -> None: ...
def plot_prediction_scatter(orig_preds: List[float], perm_preds: List[float], out_path: str) -> None: ...
def plot_invariance_histogram(invariance_scores: List[float], out_path: str) -> None: ...

def main() -> None: ...
```

### Pseudo-code (main orchestration)

```
1. sys.path.insert(0, H_M3_CODE_DIR); sys.path.insert(0, H_M1_CODE_DIR)
2. from mlp_model import MLPMatched
   from test_variance import flatten_state_dict
   from permute import generate_permutations, permute_state_dict

3. population = generate_model_population(1200, base_seed=0)
4. train_pop, test_pop = split_train_test(population, 1000, 200, seed=42)

5. seed_results = [run_seed(s, train_pop, test_pop, input_dim=32) for s in range(10)]
6. agg = aggregate_seeds(seed_results)   # gate: agg["mean"] < 0.5

7. nfn_model = load_nfn_model(input_dim=32)   # None if pip package missing
8. nfn_result = measure_nfn_invariance(nfn_model, test_pop) if nfn_model else None
9. gate_passed = agg["mean"] < 0.5 and (nfn_result is None or nfn_result["mean_invariance"] > 0.95)

10. plot_mlp_vs_nfn_bar(agg["mean"], nfn_result["mean_invariance"] if nfn_result else None,
                         "h-m4/figures/mlp_vs_nfn_bar.png")
11. plot_invariance_histogram(seed_results[-1] invariance_scores, "h-m4/figures/invariance_histogram.png")
12. plot_prediction_scatter(orig_preds, perm_preds, "h-m4/figures/prediction_scatter.png")
    # orig/perm preds pulled from one representative compute_probe_invariance call, seed=0
13. json.dump({"seed_results": seed_results, "aggregate": agg, "nfn": nfn_result,
               "gate_passed": gate_passed}, "h-m4/results.json")
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| train_dataset X | [1000, 32] | flattened weight vectors |
| test_dataset X | [200, 32] | flattened weight vectors |
| model batch pred | [32, 1] | training batch_size=32 |

---

## Subtasks

None — all Epic tasks (R-1..R-9) are Low complexity (4-8). Budget: 0 subtasks per allocation.
