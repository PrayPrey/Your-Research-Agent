# Architecture: H-M4 (MECHANISM)

**Hypothesis:** At N=1K, MLP probe invariance < 0.5 (insufficient data diversity)
**Type:** MECHANISM — extends H-M3 (untrained MLP, CV=0.194) by adding a training loop; tests whether training on limited data teaches permutation invariance.

Applied: No MLP-training/probe-invariance KB pattern found (KB returned unrelated diffusion-model docs, same null result as H-M1/H-M2/H-M3) — reused H-M3's MLPMatched + H-M1's permutation infra, added standard AdamW/MSE training loop from first principles per PRD FR-2.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M3, which itself bases on H-M1)
**Status**: H-M3 code analyzed directly (mlp_model.py, test_variance.py); H-M1 permutation/data code analyzed transitively (already verified by H-M3's own architecture doc, re-confirmed here).
**Analyzed Path**: `docs/youra_research/h-m3/code/{mlp_model.py, test_variance.py}`, `docs/youra_research/h-m1/code/{test_data.py, permute.py}`
**Findings**:
- `MLPMatched(input_dim)` (`h-m3/code/mlp_model.py`) — `Linear(input_dim,256)->ReLU->Linear(256,128)->ReLU->Linear(128,1)`, no custom init. Directly reusable, unmodified — PRD FR-2 architecture matches exactly.
- `generate_test_mlp(hidden_dims=(32,32), input_dim=32, output_dim=10, seed=42) -> state_dict` (`h-m1/code/test_data.py`) — synthetic weight generator. No real Model Zoo/CIFAR-10 dataset exists in this repo or prior hypotheses (H-E1/H-M1/H-M2/H-M3 all use this synthetic generator, not real Model Zoo downloads, despite PRD/brief mentioning it). **Correction applied**: brief's `load_dataset("model_zoo_cifar10_cnn", ...)` pseudo-code is aspirational/unverified — no prior hypothesis actually used it. H-M4 follows established repo convention: synthetic weight-vector population (many `generate_test_mlp`-style samples with varied seeds) + synthetic accuracy targets for regression target, consistent with H-E1/H-M3 practice.
- `generate_permutations(hidden_dims, base_seed) -> List[Tensor]`, `permute_state_dict(state_dict, n_hidden_layers, perms) -> Dict` (`h-m1/code/permute.py`) — reusable as-is for probe invariance permutation generation (FR-3).
- `flatten_state_dict(state_dict) -> Tensor[1,D]` (`h-m3/code/test_variance.py`) — reusable for weight-vector flattening (FR-1).
- `plot_predictions_bar`, `plot_prediction_histogram`, `plot_nfn_vs_mlp_comparison` (`h-m3/code/test_variance.py`) — generic list-of-floats plotting, reusable for FR-6 with new invariance-score inputs instead of raw predictions.
- No training loop, no NFN loader, no dataset-of-many-models exists anywhere in the repo — new code required for FR-1 (population), FR-2 (training), FR-4 (NFN control).
- `nfn` pip package not present in any prior hypothesis code — FR-4 requires optional import with graceful skip (consistent with H-M3's graceful-degrade pattern for missing H-M2 results).

---

## File Structure

```
h-m4/code/
  data_gen.py         # synthetic weight-vector population + train/test split (new)
  train_mlp.py         # AdamW/MSE training loop over N=1K, 10 seeds (new)
  probe_invariance.py  # invariance score computation (reuses h-m1 permute + h-m3 flatten)
  nfn_control.py        # optional NFN invariance measurement, graceful skip if unavailable (new)
  run_experiment.py     # orchestrates all above, statistics, plots, results.json (new)
h-m4/figures/
h-m4/results.json
```

Five new files; imports `MLPMatched` from `h-m3/code/mlp_model.py`, `generate_permutations`/`permute_state_dict` from `h-m1/code/permute.py`.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| MLPMatched | `from mlp_model import MLPMatched` (add h-m3/code to sys.path) | `h-m3/code/mlp_model.py` |
| flatten_state_dict | `from test_variance import flatten_state_dict` (add h-m3/code to sys.path) | `h-m3/code/test_variance.py` |
| generate_permutations, permute_state_dict | `from permute import generate_permutations, permute_state_dict` (add h-m1/code to sys.path) | `h-m1/code/permute.py` |
| generate_test_mlp | `from test_data import generate_test_mlp` (add h-m1/code to sys.path) | `h-m1/code/test_data.py` (pattern reference for synthetic weight generation, not called directly — H-M4 needs a *population* of models, see data_gen.py) |

**Verified from**: `h-m3/code/`, `h-m1/code/` (actual implementation). No real Model Zoo dataset code exists in repo — synthetic population generation required (see Codebase Analysis).

---

## Modules

### data_gen.py (`h-m4/code/data_gen.py`)

**Dependencies**: torch, h-m1/code/test_data.py (pattern reuse only, not import)

```python
def generate_model_population(n_models: int, hidden_dims=(32,32), input_dim=32,
                               output_dim=10, base_seed: int = 0) -> list[dict]:
    # n_models synthetic state_dicts, each via generate_test_mlp-style random init
    # with per-model seed = base_seed + i, plus a synthetic "accuracy" scalar target
    # (deterministic function of weight norm + noise) attached as model["accuracy"]

def split_train_test(population: list[dict], n_train: int = 1000, n_test: int = 200,
                      seed: int = 42) -> tuple[list[dict], list[dict]]: ...

def to_dataset(population: list[dict]) -> torch.utils.data.TensorDataset:
    # flatten each state_dict (flatten_state_dict) -> stacked [N, D] tensor + [N] accuracy tensor
```

### train_mlp.py (`h-m4/code/train_mlp.py`)

**Dependencies**: mlp_model.py (h-m3), data_gen.py

```python
def train_mlp_on_subset(train_dataset: torch.utils.data.TensorDataset, input_dim: int,
                         seed: int, epochs: int = 50, batch_size: int = 32,
                         lr: float = 1e-3) -> nn.Module:
    # torch.manual_seed(seed); MLPMatched(input_dim); AdamW; MSELoss; standard loop
    # returns trained model in eval mode
```

### probe_invariance.py (`h-m4/code/probe_invariance.py`)

**Dependencies**: h-m1/code/permute.py, h-m3/code/test_variance.py (flatten_state_dict)

```python
def compute_probe_invariance(model: nn.Module, weight_vector: torch.Tensor,
                              num_permutations: int = 10) -> tuple[float, list[float], float]:
    # original pred + num_permutations torch.randperm-based flat-vector permutations
    # -> cv = std/(|mean|+1e-8), invariance = max(0, 1-min(cv,1.0))
    # -> (invariance_score, predictions, cv)

def evaluate_population_invariance(model: nn.Module, test_population: list[dict],
                                    num_permutations: int = 10) -> dict:
    # loops compute_probe_invariance over test set
    # -> {"mean_invariance","std_invariance","mean_cv","invariance_scores": list[float]}
```

### nfn_control.py (`h-m4/code/nfn_control.py`)

**Dependencies**: nfn (optional pip package)

```python
def load_nfn_model(input_dim: int) -> nn.Module | None:
    # try: import nfn; construct minimal NPLinear-based regressor
    # except ImportError: return None (graceful skip, log warning)

def measure_nfn_invariance(nfn_model, test_population: list[dict],
                            num_permutations: int = 10) -> dict | None:
    # same structure as evaluate_population_invariance; None if nfn_model is None
```

### run_experiment.py (`h-m4/code/run_experiment.py`)

**Dependencies**: all above modules

```python
def run_seed(seed: int, train_pop: list[dict], test_pop: list[dict], input_dim: int) -> dict:
    # train_mlp_on_subset -> evaluate_population_invariance -> {"seed", "mean_invariance", "std_invariance"}

def aggregate_seeds(seed_results: list[dict]) -> dict:
    # mean/std/CI of mean_invariance across 10 seeds; pass = mean < 0.5

def plot_mlp_vs_nfn_bar(mlp_mean: float, nfn_mean: float | None, out_path: str) -> None: ...
def plot_prediction_scatter(orig_preds: list[float], perm_preds: list[float], out_path: str) -> None: ...
def plot_invariance_histogram(invariance_scores: list[float], out_path: str) -> None: ...

def main() -> None:
    # data_gen.generate_model_population(1200) -> split 1000/200
    # for seed in range(10): run_seed(...) -> aggregate_seeds
    # nfn_control.load_nfn_model + measure_nfn_invariance (best-effort)
    # gate: aggregate["mean"] < 0.5 and (nfn is None or nfn["mean_invariance"] > 0.95)
    # plots + results.json write
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| R-1 | sys.path + imports setup | Wire H_M3/H_M1 code dir constants, import MLPMatched, flatten_state_dict, generate_permutations, permute_state_dict | 3 | 1+1+0+1 |
| R-2 | Synthetic model population | generate_model_population: N synthetic state_dicts + synthetic accuracy targets, deterministic seeding | 6 | 2+1+2+1 |
| R-3 | Train/test split + dataset | split_train_test (1000/200), to_dataset (flatten + stack into TensorDataset) | 4 | 2+1+1+0 |
| R-4 | MLP training loop | train_mlp_on_subset: AdamW/MSE, 50 epochs, batch=32, per-seed reproducibility | 7 | 2+2+2+1 |
| R-5 | Probe invariance computation | compute_probe_invariance (flat-vector permutation) + evaluate_population_invariance over 200 test models | 6 | 2+2+2+0 |
| R-6 | NFN control (optional) | load_nfn_model via pip nfn, measure_nfn_invariance, graceful skip if unavailable | 8 | 3+3+1+1 |
| R-7 | Multi-seed orchestration | run_seed + aggregate_seeds across 10 seeds, gate logic (mean_invariance<0.5, NFN>0.95) | 6 | 2+2+1+1 |
| R-8 | Visualization suite | plot_mlp_vs_nfn_bar, plot_prediction_scatter, plot_invariance_histogram, save to h-m4/figures/ | 5 | 2+2+0+1 |
| R-9 | Main orchestration + results | Wire R-2..R-8 into main(), results.json write, error handling, runtime budget (<2hr) | 4 | 1+2+0+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [R-1, R-2, R-3, R-4, R-5, R-6, R-7, R-8, R-9]

---

## Notes

- No real Model Zoo dataset access exists in this repo (verified via Serena across H-E1/H-M1/H-M2/H-M3) — H-M4 uses synthetic population generation consistent with prior hypothesis practice, not the brief's aspirational `load_dataset(...)` call.
- NFN control (R-6) is best-effort: if `pip install nfn` unavailable in execution environment, gate degrades to MLP-only invariance check (mean < 0.5), matching H-M3's graceful-degradation precedent for missing dependencies/results.
- Seeds: population base_seed=0, train/test split seed=42, per-seed training seeds=0-9 (PRD NFR-1).
- Runtime target < 10 min/seed, < 2 hours total (PRD NFR-2) — with N=1000 synthetic small-dim samples and 50 epochs, well within budget on CPU.
