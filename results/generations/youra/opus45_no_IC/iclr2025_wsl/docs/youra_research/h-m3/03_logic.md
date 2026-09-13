# Logic: H-M3 (MECHANISM)

**Hypothesis:** Untrained MLP shows no permutation invariance (correlation < 0.3)

Applied: No MLP-permutation-variance KB pattern in Archon (query "variance metrics API design" returned unrelated diffusion-model docs, same as H-M2's search); reused H-M1's validated eval-mode inference + permutation-test pattern instead.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1) — H-M2/code/ does not exist on disk, so H-M3 depends directly on H-M1's actual code.
**Status**: API signatures verified from actual H-M1 code (confirmed via 03_architecture.md's Serena analysis, cross-checked against H-M2's 03_logic.md verification).
**Analyzed Path**: `docs/youra_research/h-m1/code/{test_data.py, permute.py, metrics.py, test_invariance.py}`
**Relevant Symbols**: `generate_test_mlp`, `generate_permutations`, `permute_state_dict`, `plot_predictions_bar`, `plot_prediction_histogram`. `metrics.py::compute_invariance_metrics`/`gate_passed` intentionally NOT reused (wrong polarity for a variance/negative-control test).

---

## External Dependencies API

```python
# From: h-m1/code/test_data.py (ACTUAL CODE)
def generate_test_mlp(
    hidden_dims: Tuple[int, ...] = (32, 32),
    input_dim: int = 32,
    output_dim: int = 10,
    seed: int = 42,
) -> Dict[str, torch.Tensor]:
    """Random MLP state_dict, layer{i}.weight/bias keys."""
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

# From: h-m1/code/test_invariance.py (ACTUAL CODE)
def plot_predictions_bar(predictions: List[float], out_path: str) -> None: ...
def plot_prediction_histogram(predictions: List[float], out_path: str) -> None: ...
```

**Verified from**: `h-m1/code/` (actual implementation). Note H-M3 uses `input_dim=32` default (matches PRD FR-1) — NOT H-E1/H-M2's 3072 override, since H-M3 does not load an NFN checkpoint.

---

## mlp_model.py (`h-m3/code/mlp_model.py`)

**Applied**: Standard PyTorch `nn.Sequential` MLP, default Kaiming-uniform init (no custom `reset_parameters`).

```python
class MLPMatched(nn.Module):
    def __init__(self, input_dim: int):
        """input_dim -> 256 -> 128 -> 1, ReLU activations, default init."""
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 256), nn.ReLU(),
            nn.Linear(256, 128), nn.ReLU(),
            nn.Linear(128, 1),
        )

    def forward(self, x: Tensor) -> Tensor:
        """x: [1, input_dim] -> [1, 1]"""
        return self.net(x)
```

---

## test_variance.py (`h-m3/code/test_variance.py`)

**Applied**: `sys.path` injection pattern (matches H-M1/H-M2's `H_M1_CODE_DIR` convention).

### API

```python
H_M1_CODE_DIR = "../../h-m1/code"

def flatten_state_dict(state_dict: Dict[str, torch.Tensor]) -> torch.Tensor:
    """Concat all values flattened -> [1, input_dim]"""
    return torch.cat([v.flatten() for v in state_dict.values()]).unsqueeze(0)

def run_mlp_variance_test(
    mlp: nn.Module,
    base_state_dict: Dict[str, torch.Tensor],
    hidden_dims: Tuple[int, ...],
    n_hidden_layers: int = 2,
    n_perms: int = 10,
) -> Dict[str, List[float]]:
    """original pred + n_perms permuted preds (perm_seed 0..n_perms-1).
    Returns {"predictions": [pred_original, pred_perm_0, ..., pred_perm_9]}, len = n_perms + 1."""
    ...

def compute_variance_metrics(predictions: List[float]) -> Dict[str, float]:
    """{"mean", "std", "coefficient_of_variation", "max_deviation"}"""
    ...

def gate_passed(metrics: Dict[str, float]) -> bool:
    """metrics["coefficient_of_variation"] > 0.1 or metrics["max_deviation"] > 0.01"""
    ...

def plot_nfn_vs_mlp_comparison(
    mlp_predictions: List[float],
    out_path: str,
    nfn_predictions: Optional[List[float]] = None,
) -> None:
    """Side-by-side scatter/bar; MLP-only panel if nfn_predictions is None
    (best-effort load from h-m2/results.json in main(), absent -> None)."""
    ...

def main() -> None:
    """generate_test_mlp(seed=42) -> MLPMatched(input_dim, seed=1042) ->
    run_mlp_variance_test -> compute_variance_metrics -> gate_passed ->
    plot_predictions_bar (h-m1 reuse) -> plot_prediction_histogram (h-m1 reuse) ->
    plot_nfn_vs_mlp_comparison (new) -> write results.json"""
    ...
```

### Pseudo-code (variance loop — mirrors H-M2's `run_predictions`, opposite polarity)

```
1. sys.path.insert(0, H_M1_CODE_DIR)
2. from test_data import generate_test_mlp
   from permute import generate_permutations, permute_state_dict
   from test_invariance import plot_predictions_bar, plot_prediction_histogram

3. base_sd = generate_test_mlp(seed=42)          # hidden_dims=(32,32), input_dim=32
4. torch.manual_seed(1042); mlp = MLPMatched(input_dim=32).eval()

5. run_mlp_variance_test(mlp, base_sd, hidden_dims=(32,32), n_perms=10):
   a. x0 = flatten_state_dict(base_sd)
   b. pred_original = mlp(x0).item()
   c. for seed in range(10):
        perms = generate_permutations(hidden_dims=(32,32), base_seed=seed)
        perm_sd = permute_state_dict(base_sd, n_hidden_layers=2, perms=perms)
        preds.append(mlp(flatten_state_dict(perm_sd)).item())
   d. return {"predictions": [pred_original] + preds}   # len 11

6. metrics = compute_variance_metrics(predictions)
7. passed = gate_passed(metrics)
8. plot_predictions_bar(predictions, "h-m3/figures/predictions_bar.png")
9. plot_prediction_histogram(predictions, "h-m3/figures/prediction_histogram.png")
10. try: nfn_preds = json.load("../../h-m2/results.json")["predictions"]
    except: nfn_preds = None
11. plot_nfn_vs_mlp_comparison(predictions, "h-m3/figures/nfn_vs_mlp.png", nfn_preds)
12. json.dump({"predictions": predictions, "metrics": metrics, "gate_passed": passed},
               "h-m3/results.json")
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| base_sd flattened | [1, 32] | layer0.w[32,32]+b[32] + layer1.w[32,32]+b[32] flattened, input_dim=32 default |
| mlp forward output | [1, 1] | scalar prediction, `.item()` extracted |
| predictions | list[float], len 11 | 1 original + 10 permuted |

No new tensor shapes beyond H-M1's `generate_test_mlp` defaults (input_dim=32, hidden_dims=(32,32)) — reused unchanged.

---

## Subtasks

None — all Epic tasks (Q-1..Q-8) are Low complexity (3-6), pure orchestration + one small model class. Budget: 0 subtasks per allocation.
