# Logic: H-M2 (MECHANISM)

**Hypothesis:** NFN predictions identical under weight permutation (diff < 1e-5)

Applied: No NFN-specific KB pattern found (Archon search "PyTorch permutation invariance test" returned only low-similarity general PyTorch/diffusers docs, not used); reused H-M1's validated eval-mode inference + permutation-test pattern instead.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: API signatures verified from actual H-M1 code (`docs/youra_research/h-m1/code/`), confirmed via 03_architecture.md's prior Serena analysis — function names differ from 02c brief's pseudo-code (e.g. `run_predictions` not `test_prediction_invariance`).
**Analyzed Path**: `docs/youra_research/h-m1/code/{test_data.py, permute.py, metrics.py, test_invariance.py}`
**Relevant Symbols**: `generate_test_mlp`, `generate_permutations`, `permute_state_dict`, `load_nfn_model`, `state_dict_to_wsfeat`, `run_predictions`, `compute_invariance_metrics`, `gate_passed`, `plot_predictions_bar`, `plot_deviation_heatmap`, `plot_prediction_histogram`

**Note**: H-M2 needs zero new logic modules — it is a thin orchestration script that reuses H-M1's `run_predictions` directly (already does exactly what's needed: original + N permuted predictions). Architecture doc's proposed `run_prediction_invariance_test` wrapper is unnecessary — call `run_predictions` + `compute_invariance_metrics` + `gate_passed` directly in `main()`.

---

## External Dependencies API

```python
# From: h-m1/code/test_data.py (ACTUAL CODE)
def generate_test_mlp(
    hidden_dims: Tuple[int, ...] = (64, 64),
    input_dim: int = 3072,
    output_dim: int = 10,
    seed: int = 42,
) -> Dict[str, torch.Tensor]:
    """Random MLP state_dict, layer{i}.weight/bias keys. Matches SimpleCNN shape."""
    ...

# From: h-m1/code/permute.py (ACTUAL CODE)
def generate_permutations(hidden_dims: Tuple[int, ...] = (64, 64), base_seed: int = 0) -> List[torch.Tensor]:
    """One randperm(h) per hidden layer -> [perm_0, perm_1]"""
    ...

def permute_state_dict(
    state_dict: Dict[str, torch.Tensor],
    n_hidden_layers: int = 2,
    perms: List[torch.Tensor] = None,
) -> Dict[str, torch.Tensor]:
    """Apply neuron perms[i] to layer{i}, propagate to layer{i+1} inputs."""
    ...

# From: h-m1/code/test_invariance.py (ACTUAL CODE)
def load_nfn_model(checkpoint_path: str, network_spec: Any, nfn_channels: int = 32) -> "NFNRegressor":
    """Instantiate NFNRegressor(network_spec, nfn_channels), load_state_dict, .eval()."""
    ...

def state_dict_to_wsfeat(state_dict: Dict[str, torch.Tensor], network_spec: Any) -> Any:
    """Single state_dict -> batched WeightSpaceFeatures [B=1, ...]."""
    ...

def run_predictions(
    nfn_model: nn.Module,
    base_state_dict: Dict[str, torch.Tensor],
    hidden_dims: Tuple[int, ...],
    network_spec: Any,
    n_perms: int = 10,
) -> List[float]:
    """[pred_original] + [pred_perm_i for i in 0..n_perms-1], len = n_perms + 1."""
    ...

def plot_predictions_bar(predictions: List[float], out_path: str) -> None: ...
def plot_deviation_heatmap(predictions: List[float], out_path: str) -> None: ...
def plot_prediction_histogram(predictions: List[float], out_path: str) -> None: ...

# From: h-m1/code/metrics.py (ACTUAL CODE)
def compute_invariance_metrics(predictions: List[float]) -> Dict[str, float]:
    """{mean, std, max_deviation, invariance_score, invariance_correlation}"""
    ...

def gate_passed(metrics: Dict[str, float], dev_threshold: float = 1e-5, corr_threshold: float = 0.99) -> bool:
    """(max_deviation < dev_threshold) or (invariance_correlation > corr_threshold)"""
    ...

# From: h-e1/code/data.py (ACTUAL CODE)
def get_network_spec_from_sample(models: List[Dict]) -> Any:
    """models[0]['state_dict'] must use layer{i}.weight/bias keys."""
    ...
```

**Verified from**: `h-m1/code/` and `h-e1/code/` (actual implementation, not 02c brief pseudo-code — note brief's `test_prediction_invariance(base_seed=...)` signature does not exist; use `run_predictions` above).

**Correction vs PRD**: PRD's "32-32-32-10" architecture is stale; actual shape is `input_dim=3072, hidden_dims=(64,64), output_dim=10` per H-M1's `generate_test_mlp` defaults — do not override.

---

## P-*: test_predictions.py (h-m2/code/test_predictions.py)

**Applied**: Standard PyTorch orchestration script, `sys.path` injection pattern (matches H-M1's `H_E1_CODE_DIR` convention).

### API

```python
H_M1_CODE_DIR = "../../h-m1/code"
H_E1_CODE_DIR = "../../h-e1/code"
H_E1_CHECKPOINT = "../../h-e1/checkpoints/nfn_model.pt"

def main() -> None:
    """load H-E1 checkpoint -> generate_test_mlp -> run_predictions -> metrics -> gate -> plots -> results.json"""
    ...
```

### Pseudo-code

```
1. sys.path.insert(0, H_M1_CODE_DIR); sys.path.insert(0, H_E1_CODE_DIR)
2. from test_data import generate_test_mlp
   from permute import generate_permutations, permute_state_dict
   from metrics import compute_invariance_metrics, gate_passed
   from test_invariance import load_nfn_model, state_dict_to_wsfeat, run_predictions,
       plot_predictions_bar, plot_deviation_heatmap, plot_prediction_histogram
   from data import get_network_spec_from_sample

3. base_sd = generate_test_mlp(seed=42)   # hidden_dims=(64,64), input_dim=3072, output_dim=10
4. network_spec = get_network_spec_from_sample([{"state_dict": base_sd}])
5. nfn_model = load_nfn_model(H_E1_CHECKPOINT, network_spec, nfn_channels=32)
6. predictions = run_predictions(nfn_model, base_sd, hidden_dims=(64,64),
                                  network_spec=network_spec, n_perms=10)
7. metrics = compute_invariance_metrics(predictions)
8. passed = gate_passed(metrics, dev_threshold=1e-5)
9. plot_predictions_bar(predictions, "h-m2/figures/predictions_bar.png")
10. plot_deviation_heatmap(predictions, "h-m2/figures/deviation_heatmap.png")
11. plot_prediction_histogram(predictions, "h-m2/figures/prediction_histogram.png")
12. json.dump({"predictions": predictions, "metrics": metrics, "gate_passed": passed},
               "h-m2/results.json")
```

No new tensor shapes beyond H-M1 (reused unchanged): `layer0.weight [64,3072]`, `layer1.weight [64,64]`, `layer2.weight [10,64]`, prediction scalar per forward call.

---

## Subtasks

None — all Epic tasks (P-1..P-7) are Low complexity (4-8), pure orchestration calling H-M1/H-E1 functions verbatim. Budget: 0 subtasks per allocation.
