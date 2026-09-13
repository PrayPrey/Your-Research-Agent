# Architecture: H-M3 (MECHANISM)

**Hypothesis:** Untrained MLP shows no permutation invariance (correlation < 0.3)
**Type:** MECHANISM — negative-control counterpart to H-M1/H-M2, reuses H-M1 permutation infra with new untrained MLP.

Applied: No MLP-permutation-variance KB pattern found (KB returned unrelated diffusion-model docs, same as H-M2); reused H-M1's validated permutation-generation + eval-mode inference pattern instead.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1) — H-M2/code/ does not exist on disk (only referenced in its own architecture doc), so H-M3 depends directly on H-M1's actual code, not H-M2's.
**Status**: H-M1 code analyzed directly; function signatures confirmed.
**Analyzed Path**: `docs/youra_research/h-m1/code/{test_data.py, permute.py, metrics.py, test_invariance.py}`
**Findings**:
- `generate_test_mlp(hidden_dims=(32,32), input_dim=32, output_dim=10, seed=42)` — default `input_dim=32` (matches PRD FR-1, NOT H-E1/H-M2's 3072; H-M3 doesn't load NFN/H-E1 checkpoint so the small default applies unchanged).
- `generate_permutations(hidden_dims=(32,32), base_seed=0) -> List[Tensor]` and `permute_state_dict(state_dict, n_hidden_layers=2, perms=...) -> Dict` — both reusable as-is.
- `test_invariance.py::plot_predictions_bar(predictions, out_path)` and `plot_prediction_histogram(predictions, out_path)` are generic (list of floats + path) — directly reusable for H-M3's variance plots, no modification needed.
- `metrics.py::compute_invariance_metrics` / `gate_passed` are invariance-oriented (low deviation = pass); H-M3 needs opposite polarity (high variance = pass) — NOT reused, new small `compute_variance_metrics`/gate logic in H-M3's own script per PRD FR-4/FR-5.
- No MLPMatched or model.py exists in H-M1 — new file required.

**Correction applied**: 02c brief's pseudo-code passes `generate_permutations` and constructs `perm_sd` inline per-permutation-seed inside the loop (matches actual `permute_state_dict` signature `n_hidden_layers=2`) — brief's code is already aligned with actual H-M1 signatures, no fix needed.

---

## File Structure

```
h-m3/code/
  mlp_model.py       # MLPMatched class (new)
  test_variance.py   # main script: generate data, run MLP, compute variance, gate, save/plot
h-m3/figures/
h-m3/results.json
```

Two new files; `test_data.py`/`permute.py` imported directly from `h-m1/code/`.

---

## External Dependencies (H-M1)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| generate_test_mlp | `from test_data import generate_test_mlp` (add h-m1/code to sys.path) | `h-m1/code/test_data.py` |
| generate_permutations, permute_state_dict | `from permute import generate_permutations, permute_state_dict` | `h-m1/code/permute.py` |
| plot_predictions_bar, plot_prediction_histogram | `from test_invariance import plot_predictions_bar, plot_prediction_histogram` | `h-m1/code/test_invariance.py` |

**Verified from**: `h-m1/code/` (actual implementation). `metrics.py::compute_invariance_metrics`/`gate_passed` intentionally NOT imported — wrong polarity for variance test.

---

## Modules

### mlp_model.py (`h-m3/code/mlp_model.py`)

**Dependencies**: torch only

```python
class MLPMatched(nn.Module):
    def __init__(self, input_dim: int): ...
    def forward(self, x: Tensor) -> Tensor: ...
    # Sequential: Linear(input_dim,256) -> ReLU -> Linear(256,128) -> ReLU -> Linear(128,1)
    # Kaiming-uniform default init, no custom reset_parameters
```

### test_variance.py (`h-m3/code/test_variance.py`)

**Dependencies**: mlp_model.py, h-m1/code/{test_data.py, permute.py, test_invariance.py}

```python
H_M1_CODE_DIR = "../../h-m1/code"

def flatten_state_dict(state_dict: dict) -> torch.Tensor: ...
    # torch.cat([v.flatten() for v in state_dict.values()])

def run_mlp_variance_test(mlp: nn.Module, base_state_dict: dict, hidden_dims: tuple,
                           n_hidden_layers: int = 2, n_perms: int = 10) -> dict:
    # original pred + n_perms permuted preds (each perm_seed 0..9 via generate_permutations)
    # -> {"predictions": list[float]}

def compute_variance_metrics(predictions: list[float]) -> dict:
    # mean, std, cv = std/(|mean|+1e-12), max_deviation, correlation proxy
    # -> {"mean","std","coefficient_of_variation","max_deviation"}

def gate_passed(metrics: dict) -> bool:
    # metrics["coefficient_of_variation"] > 0.1 or metrics["max_deviation"] > 0.01

def plot_nfn_vs_mlp_comparison(mlp_predictions: list[float], out_path: str,
                                nfn_predictions: list[float] | None = None) -> None:
    # side-by-side scatter/bar; if h-m2/results.json predictions unavailable, MLP-only panel

def main() -> None: ...
    # generate_test_mlp(seed=42) -> MLPMatched(input_dim, seed=1042) -> run_mlp_variance_test
    # -> compute_variance_metrics -> gate_passed -> plot_predictions_bar (h-m1 reuse)
    # -> plot_prediction_histogram (h-m1 reuse) -> plot_nfn_vs_mlp_comparison (new)
    # -> write results.json
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| Q-1 | sys.path + imports setup | Wire H_M1_CODE_DIR constant, import generate_test_mlp/generate_permutations/permute_state_dict/plot funcs | 3 | 1+1+0+1 |
| Q-2 | MLPMatched model | New nn.Module: input_dim->256->128->1, default Kaiming init, seed=1042 | 4 | 2+0+1+1 |
| Q-3 | Test data + flatten | generate_test_mlp(seed=42), flatten_state_dict helper for MLP input format | 3 | 1+1+1+0 |
| Q-4 | Variance test loop | run_mlp_variance_test: original + 10 permuted forward passes via permute_state_dict | 6 | 2+2+1+1 |
| Q-5 | Variance metrics + gate | compute_variance_metrics (cv, max_deviation, std) + gate_passed (opposite polarity of H-M1) | 4 | 1+1+1+1 |
| Q-6 | Visualization (reused) | Call h-m1's plot_predictions_bar + plot_prediction_histogram, save to h-m3/figures/ | 3 | 1+2+0+0 |
| Q-7 | NFN vs MLP comparison plot | New plot_nfn_vs_mlp_comparison; load h-m2/results.json predictions if present, else MLP-only | 5 | 2+2+1+0 |
| Q-8 | Orchestration (main) | Wire Q-2..Q-7 into main(), results.json write, error handling | 3 | 1+1+0+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [Q-1, Q-2, Q-3, Q-4, Q-5, Q-6, Q-7, Q-8]

---

## Notes

- `metrics.py::compute_invariance_metrics`/`gate_passed` from H-M1 deliberately not reused — inverted success polarity (high variance = pass) requires distinct logic (PRD NFR-1 already specifies new `test_variance.py`, not a metrics.py modification).
- Seeds per PRD: test data seed=42, MLP init seed=1042, permutation seeds=0-9 — all deterministic.
- Runtime target < 1s per PRD NFR-3 — single MLP, 11 forward passes, no training.
- Q-7's NFN comparison is best-effort: gracefully degrades to MLP-only plot if `h-m2/results.json` absent (H-M2/code/ was not found on disk during this analysis).
