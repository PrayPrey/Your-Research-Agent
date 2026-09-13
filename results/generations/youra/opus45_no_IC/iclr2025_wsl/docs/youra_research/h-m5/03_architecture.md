# Architecture: H-M5 (MECHANISM)

**Hypothesis:** At N=50K, MLP probe invariance > 0.8 (learned from data diversity)
**Type:** MECHANISM — extends H-M4 by scaling N=1K -> N=42K (max available), adding R² computation (missing in H-M4) since PRD requires "must learn" gate check.

Applied: No MLP-scale/probe-invariance KB pattern found (same null result as prior hypotheses) — reused H-M4's full pipeline unmodified except scale params + new R² metric, per PRD FR-5.1.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M4)
**Status**: H-M4 code analyzed directly — all 5 modules read in full (not just h-m4/03_architecture.md spec, which mostly matches actual code here, unlike H-M3->H-M4 case).
**Analyzed Path**: `docs/youra_research/h-m4/code/{data_gen.py, mlp_model.py, train_mlp.py, probe_invariance.py, nfn_control.py, run_experiment.py}`
**Findings**:
- `load_model_zoo_population(data_path, max_models=None)` (`h-m4/code/data_gen.py`) — loads REAL Model Zoo data via `torch.load(MODELZOO_DATA_PATH)`, `MODELZOO_DATA_PATH = "/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_wsl/data/cifar10_gs/dataset_cifar_small_hyp_rand.pt"` (note: hardcoded absolute path from a *different* repo root than current TEST_wsl — must verify this path exists/is reachable, or update constant). Directly reusable — already supports `max_models` param for scaling to N=42K.
- `split_train_test(population, n_train, n_test, seed)` — reusable unmodified, just change `n_train=42547 (or max avail), n_test=2000`.
- `to_dataset(population)` — reusable unmodified (uses `flatten_state_dict` from h-m3).
- `MLPMatched(input_dim)` (`h-m3/code/mlp_model.py`, imported by h-m4) — `Linear(input_dim,256)->ReLU->Linear(256,128)->ReLU->Linear(128,1)`. PRD FR-2.2 specifies hidden dims [512, 256] (different from H-M4's [256,128]) — **new variant required**, cannot reuse H-M4's class as-is.
- `train_mlp_on_subset(train_dataset, input_dim, seed, epochs, batch_size, lr, device)` (`h-m4/code/train_mlp.py`) — AdamW + MSELoss, no LR scheduler. PRD FR-3.2 requires CosineAnnealingLR (new for H-M5) — needs modification, not pure reuse.
- `compute_probe_invariance` / `evaluate_population_invariance` (`h-m4/code/probe_invariance.py`) — flat-vector permutation methodology, CV-based invariance score. **Reusable unmodified** — brief explicitly requires "Keep methodology identical for comparison" (FR-4 same as H-M4).
- No R² computation exists anywhere in H-M4 pipeline — new for H-M5 (PRD FR-5.1, gate logic requirement).
- `nfn_control.py` (optional NFN control) — out of scope for H-M5 (PRD "Out of Scope": no NFN comparison mentioned; H-M5 PRD focuses on H-M4 baseline comparison only, not NFN). Skipped.
- `run_experiment.py` plotting functions (`plot_mlp_vs_nfn_bar`, `plot_prediction_scatter`, `plot_invariance_histogram`) — pattern reusable, but H-M5 needs different comparison (N=1K vs N=50K, not MLP vs NFN) — new plot functions needed per PRD FR-6.

---

## File Structure

```
h-m5/code/
  mlp_model_wide.py     # MLPMatched variant [512,256] hidden dims (new, PRD FR-2.2)
  train_mlp_scheduled.py # train_mlp_on_subset + CosineAnnealingLR (new, PRD FR-3.2)
  metrics.py             # R2 computation + H-M4 baseline comparison (new, PRD FR-5)
  run_experiment.py      # orchestrates data_gen/probe_invariance (h-m4) + above, plots, results.json (new)
h-m5/figures/
h-m5/results.json
```

Three new modules + new orchestrator; reuses `data_gen.py`, `probe_invariance.py` unmodified from `h-m4/code/`.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| load_model_zoo_population, split_train_test, to_dataset | `from data_gen import load_model_zoo_population, split_train_test, to_dataset` (add h-m4/code to sys.path) | `h-m4/code/data_gen.py` |
| compute_probe_invariance, evaluate_population_invariance | `from probe_invariance import compute_probe_invariance, evaluate_population_invariance` (add h-m4/code to sys.path) | `h-m4/code/probe_invariance.py` |
| flatten_state_dict | `from test_variance import flatten_state_dict` (add h-m3/code to sys.path) | `h-m3/code/test_variance.py` |

**Verified from**: `h-m4/code/` (actual implementation, fully read). MODELZOO_DATA_PATH constant in `data_gen.py` points to `/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_wsl/data/cifar10_gs/dataset_cifar_small_hyp_rand.pt` — **verify reachability in current environment before reuse**; if unreachable, override `data_path` param in `load_model_zoo_population(data_path=...)` call.

---

## Modules

### mlp_model_wide.py (`h-m5/code/mlp_model_wide.py`)

**Dependencies**: torch

```python
class MLPMatchedWide(nn.Module):
    def __init__(self, input_dim: int): ...
    # Linear(input_dim,512)->ReLU->Linear(512,256)->ReLU->Linear(256,1), per PRD FR-2.2
    def forward(self, x: torch.Tensor) -> torch.Tensor: ...
```

### train_mlp_scheduled.py (`h-m5/code/train_mlp_scheduled.py`)

**Dependencies**: mlp_model_wide.py

```python
def train_mlp_on_subset(train_dataset: torch.utils.data.TensorDataset, input_dim: int,
                         seed: int, epochs: int = 50, batch_size: int = 64,
                         lr: float = 1e-3, weight_decay: float = 1e-4,
                         device: str = "cpu") -> nn.Module:
    # torch.manual_seed(seed); MLPMatchedWide(input_dim); AdamW(lr, weight_decay)
    # CosineAnnealingLR(optimizer, T_max=epochs); MSELoss; scheduler.step() per epoch
    # returns trained model in eval mode
```

### metrics.py (`h-m5/code/metrics.py`)

**Dependencies**: sklearn.metrics

```python
def compute_r2(model: nn.Module, test_dataset: torch.utils.data.TensorDataset,
                device: str = "cpu") -> float:
    # batch predict, sklearn.metrics.r2_score(y_true, y_pred)

def compare_with_baseline(hm5_r2: float, hm5_invariance: float,
                           hm4_r2: float = 0.0036, hm4_invariance: float = 0.9193) -> dict:
    # -> {"r2_delta", "invariance_delta", "hm4": {...}, "hm5": {...}}

def gate_logic(test_r2: float, mean_invariance: float) -> str:
    # PRD gate: r2<0.1 -> INCONCLUSIVE; invariance>0.8 -> PASS; else FAIL
```

### run_experiment.py (`h-m5/code/run_experiment.py`)

**Dependencies**: all above + h-m4/data_gen.py, h-m4/probe_invariance.py

```python
def run_seed(seed: int, train_pop: list[dict], test_pop: list[dict], input_dim: int) -> dict:
    # to_dataset -> train_mlp_scheduled.train_mlp_on_subset -> metrics.compute_r2
    # -> probe_invariance.evaluate_population_invariance
    # -> {"seed", "test_r2", "mean_invariance", "std_invariance"}

def aggregate_seeds(seed_results: list[dict]) -> dict:
    # mean/std/CI of test_r2 and mean_invariance across 10 seeds
    # gate_status = metrics.gate_logic(mean(test_r2), mean(mean_invariance))

def plot_gate_comparison_bar(hm4_inv: float, hm5_inv: float, out_path: str) -> None: ...
def plot_r2_vs_scale(hm4_r2: float, hm5_r2: float, out_path: str) -> None: ...
def plot_invariance_histogram(invariance_scores: list[float], out_path: str) -> None: ...
def plot_prediction_scatter(predictions: list[float], out_path: str) -> None: ...

def main() -> None:
    # data_gen.load_model_zoo_population(max_models=None) -> ~42547 models
    # split_train_test(n_train=42547-2000, n_test=2000, seed=42)  # or n_train per available
    # for seed in range(10): run_seed(...) -> aggregate_seeds
    # plots + results.json write, includes gate_status string
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| S-1 | sys.path + imports setup | Wire h-m4/h-m3 code dir constants, import data_gen, probe_invariance, flatten_state_dict; verify MODELZOO_DATA_PATH reachable | 4 | 1+2+0+1 |
| S-2 | MLPMatchedWide model | New [512,256] hidden-dim variant per PRD FR-2.2 | 3 | 1+0+1+1 |
| S-3 | Scheduled training loop | train_mlp_on_subset with AdamW(wd=1e-4) + CosineAnnealingLR, batch=64, 50 epochs | 6 | 2+1+2+1 |
| S-4 | Full-scale data loading | load_model_zoo_population(max_models=None) -> ~42547 models, split 40547/2000, memory-safe batching for ~50K-dim vectors | 8 | 3+1+3+1 |
| S-5 | R² metrics module | compute_r2 (sklearn), compare_with_baseline vs H-M4 fixed values, gate_logic per PRD gate table | 5 | 2+1+2+0 |
| S-6 | Probe invariance reuse | Wire h-m4 evaluate_population_invariance over 2000 test models unmodified (methodology parity) | 3 | 1+2+0+0 |
| S-7 | Multi-seed orchestration | run_seed + aggregate_seeds across 10 seeds, R² + invariance CI, gate_status computation | 6 | 2+2+1+1 |
| S-8 | Visualization suite | plot_gate_comparison_bar (N=1K vs N=50K), plot_r2_vs_scale, plot_invariance_histogram, plot_prediction_scatter | 6 | 2+2+1+1 |
| S-9 | Main orchestration + results | Wire S-2..S-8 into main(), results.json with H-M4 comparison, runtime budget (<2hr on ~42K models x 50 epochs x 10 seeds) | 7 | 2+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [S-1, S-2, S-3, S-4, S-5, S-6, S-7, S-8, S-9]

---

## Notes

- H-M4's `MODELZOO_DATA_PATH` hardcodes a path under `YouRA_no_VSA_sonnet46` (different repo root than current `TEST_wsl`) — Phase 4 Coder MUST verify this path exists in execution environment or parameterize `data_path` explicitly; do not assume silent reuse works.
- Runtime risk (NFR-2, <2hr): N=42K x 50 epochs x 10 seeds with ~50K-dim inputs and 512-hidden MLP is far larger than H-M4's N=1K run — Phase 4 Coder should benchmark 1 seed first and consider reducing seeds or epochs if budget exceeded (PRD allows "Use max available" fallback but does not permit reducing seeds/epochs; flag as risk if infeasible).
- NFN control (H-M4's R-6) is explicitly out of scope for H-M5 per PRD "Out of Scope" — not carried forward.
- Gate comparison uses H-M4's published results (R²=0.0036, invariance=0.9193) as fixed baseline constants in `metrics.compare_with_baseline`, not live re-computation.
