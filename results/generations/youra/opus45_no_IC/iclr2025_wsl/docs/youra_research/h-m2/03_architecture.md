# Architecture: H-M2 (MECHANISM)

**Hypothesis:** NFN predictions identical under weight permutation (diff < 1e-5)
**Type:** MECHANISM — extends H-M1's layer-invariance test to final scalar prediction, full code reuse.

Applied: No NFN-specific KB pattern found (KB returned unrelated diffusion-model docs); reused H-M1's validated eval-mode inference + permutation-test pattern instead.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: Actual H-M1 code analyzed — confirms function names differ slightly from 02c brief's pseudo-code.
**Analyzed Path**: `docs/youra_research/h-m1/code/{test_data.py, permute.py, metrics.py, test_invariance.py}`
**Findings**:
- `test_invariance.py` actual functions: `load_nfn_model`, `state_dict_to_wsfeat`, `run_predictions` (brief calls this `run_invariance_test` / `test_prediction_invariance` — does not exist under that name), `plot_predictions_bar`, `plot_deviation_heatmap`, `plot_prediction_histogram`, `main`.
- Uses module-level constants `H_M1_CODE_DIR`, `H_E1_CODE_DIR` for `sys.path` injection — H-M2 must follow the same pattern to import `h-e1/code/model.py` and `h-e1/code/data.py`.
- `permute.py`: `generate_permutations(hidden_sizes, seed)`, `permute_state_dict(state_dict, hidden_layer_keys, perms)` — signature takes `hidden_layer_keys`, not just `len(hidden_dims)` as brief pseudo-code implied.
- `test_data.py::generate_test_mlp(hidden_sizes=[64,64], input_dim=3072, output_dim=10, seed=42)` — input_dim is 3072 (CIFAR-10 flat), confirmed correction from H-M1, brief's "32-32-32-10" architecture note in PRD is stale/wrong; trust H-M1 code.
- `metrics.py::compute_invariance_metrics` already computes `max_deviation`; H-M2 just needs a stricter threshold (1e-5, same as H-M1's `dev_threshold` default) applied to prediction-level (not layer-level) deviations — no new metrics module needed.

**Correction applied**: PRD's "32-32-32-10" architecture references are incorrect; actual shape (from H-M1/H-E1 code) is input_dim=3072, hidden=[64,64], output=10. H-M2 reuses H-M1's `generate_test_mlp` defaults unchanged.

---

## File Structure

```
h-m2/code/
  test_predictions.py   # main script: load NFN, run original+permuted predictions, gate, save/plot
h-m2/figures/
h-m2/results.json
```

Only one new file needed — everything else is direct import reuse from `h-m1/code/`.

---

## External Dependencies (H-M1 + H-E1)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| generate_test_mlp | `from test_data import generate_test_mlp` (add h-m1/code to sys.path) | `h-m1/code/test_data.py` |
| generate_permutations, permute_state_dict | `from permute import generate_permutations, permute_state_dict` | `h-m1/code/permute.py` |
| compute_invariance_metrics, gate_passed | `from metrics import compute_invariance_metrics, gate_passed` | `h-m1/code/metrics.py` |
| load_nfn_model, state_dict_to_wsfeat | `from test_invariance import load_nfn_model, state_dict_to_wsfeat` | `h-m1/code/test_invariance.py` |
| NFNRegressor | `from model import NFNRegressor` (add h-e1/code to sys.path) | `h-e1/code/model.py` |
| get_network_spec_from_sample | `from data import get_network_spec_from_sample` | `h-e1/code/data.py` |
| Checkpoint | N/A (torch.load) | `h-e1/checkpoints/nfn_model.pt` |

**Verified from**: `h-m1/code/` and `h-e1/code/` (actual implementation).

---

## Modules

### test_predictions.py (`h-m2/code/test_predictions.py`)

**Dependencies**: h-m1/code/{test_data.py, permute.py, metrics.py, test_invariance.py}, h-e1/code/{model.py, data.py}

```python
H_M1_CODE_DIR = "../../h-m1/code"
H_E1_CODE_DIR = "../../h-e1/code"

def run_prediction_invariance_test(nfn_model, base_state_dict: dict, hidden_sizes: list[int],
                                    network_spec, n_perms: int = 10) -> dict:
    # original pred + n_perms permuted preds -> {predictions, metrics, gate_passed}
    # reuses state_dict_to_wsfeat (h-m1) + compute_invariance_metrics (h-m1, threshold=1e-5)

def main() -> None: ...  # load H-E1 checkpoint -> generate_test_mlp -> run test -> gate -> plots -> results.json
```

No new plotting/metrics functions — reuses `plot_predictions_bar`, `plot_deviation_heatmap`, `plot_prediction_histogram` from `h-m1/code/test_invariance.py` directly (imported, called with H-M2's predictions list and `h-m2/figures/` output path).

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| P-1 | sys.path + imports setup | Wire H_M1_CODE_DIR/H_E1_CODE_DIR constants, import reused functions | 3 | 1+2+0+0 |
| P-2 | Load NFN + network_spec | Reuse `load_nfn_model`, `get_network_spec_from_sample`, checkpoint from H-E1 | 4 | 1+2+0+1 |
| P-3 | Test MLP generation | Call `generate_test_mlp(seed=42)`, reuse H-M1 defaults unchanged | 2 | 1+1+0+0 |
| P-4 | Prediction invariance loop | `run_prediction_invariance_test`: original + 10 permuted predictions via `state_dict_to_wsfeat` + NFN forward | 6 | 2+2+1+1 |
| P-5 | Gate evaluation | Apply `gate_passed(metrics, dev_threshold=1e-5)`, write results.json | 3 | 1+1+0+1 |
| P-6 | Visualization | Call reused `plot_predictions_bar` + `plot_deviation_heatmap` + `plot_prediction_histogram`, save to h-m2/figures/ | 3 | 1+2+0+0 |
| P-7 | Orchestration (main) | Wire P-2..P-6 into single `main()` entrypoint, error handling | 3 | 1+1+0+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [P-1, P-2, P-4, P-6]

---

## Notes

- No new metrics/permutation/model code — pure orchestration script calling H-M1 functions with different gate threshold context (same 1e-5 default already in `metrics.py::gate_passed`).
- Runtime target < 1s per PRD NFR-3 — single MLP, 11 forward passes, no training.
