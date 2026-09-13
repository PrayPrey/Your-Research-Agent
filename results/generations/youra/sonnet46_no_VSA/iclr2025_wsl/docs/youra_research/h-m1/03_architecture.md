# Architecture: H-M1
# Causal Attribution — Encoder Architecture Determines OrbitVar (≥4 OOM)

**Hypothesis ID:** H-M1
**Type:** MECHANISM (Causal Step 1)
**Date:** 2026-08-03
**Base:** H-E1 (INCREMENTAL)

Applied: N/A — Archon KB contains only diffusion model docs (max sim 0.45, below threshold)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-E1)
**Status:** Patterns found from base code
**Analyzed Path:** `docs/youra_research/h-e1/code/`
**Findings:** H-E1 has 6 modules — data_loader, permutation, encoder_c2, encoder_c3, orbit_var, visualization, run_experiment. All reusable via sys.path insert. `orbit_var.save_results` writes to `results/orbit_var_results.json`. `compute_orbit_var_all_models` returns `(per_model_vars, mean_orbitvar, max_orbitvar)` and accepts `encoder_fn: Callable`. `DeepSetsChannelEncoder` has `.phi` attribute (MLP layers). `sample_functional_permutations(channels_per_layer, K, seed=1)` returns list of perm specs.

---

## External Dependencies (H-E1 Verified)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_dataset | `from data_loader import load_dataset, reconstruct_state_dict` | `h-e1/code/data_loader.py` |
| sample_functional_permutations | `from permutation import sample_functional_permutations, apply_permutation` | `h-e1/code/permutation.py` |
| DeepSetsChannelEncoder | `from encoder_c2 import DeepSetsChannelEncoder, build_c2_encoder` | `h-e1/code/encoder_c2.py` |
| NFNEncoder | `from encoder_c3 import NFNEncoder, build_nfn_encoder, encode_nfn` | `h-e1/code/encoder_c3.py` |
| compute_orbit_var_all_models | `from orbit_var import compute_orbit_var_all_models, save_results` | `h-e1/code/orbit_var.py` |

**Import pattern** (add to sys.path before imports):
```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'h-e1', 'code'))
```

**Verified from:** `docs/youra_research/h-e1/code/` (actual implementation)

---

## File Structure

```
h-m1/
  code/
    run_experiment.py     # single entry point — all logic inline (< 80 lines new code)
    encoder_c1.py         # CISEEncoder (C1) — new implementation
    visualize.py          # 3 figures
  results/
    orbit_var_ratios.json
    h_m1_summary.csv
    anti_gate_log.txt
  figures/
    orbitvar_comparison.png
    ratio_histogram.png
    summary_table.png
```

---

## Modules

### CISEEncoder (`code/encoder_c1.py`)

**Dependencies:** torch (stdlib), data_loader (H-E1)

```python
import torch
import torch.nn as nn

class CISEEncoder(nn.Module):
    def __init__(self, embed_dim: int = 64, max_channels: int = 16): ...
    def forward(self, state_dict: dict) -> torch.Tensor: ...
    # Returns: (embed_dim,) float32 tensor
    # Uses sinusoidal PE over channel position index — no sort/argsort/topk
```

### run_experiment (`code/run_experiment.py`)

**Dependencies:** CISEEncoder, all H-E1 imports via sys.path, scipy.stats, json, numpy, matplotlib

```python
def verify_prerequisites(h_e1_results_path: str) -> tuple[np.ndarray, np.ndarray]: ...
# Returns: (orbit_vars_C2, orbit_vars_C3) — asserts means match known values

def measure_cise_orbitvar(
    dataset: list,
    perm_specs: list,
    build_on: bool = True,
    build_on_value: float = 0.010333,
) -> np.ndarray: ...
# Returns: orbit_vars_C1 [N_MODELS] — reuses compute_orbit_var_all_models from H-E1

def compute_ratios(
    orbit_vars_C1: np.ndarray,
    orbit_vars_C2: np.ndarray,
    orbit_vars_C3: np.ndarray,
    eps: float = 1e-30,
) -> dict: ...
# Returns: dict with per-model ratios, mean/median/geomean, log10 OOM values

def run_wilcoxon(
    orbit_vars_C1: np.ndarray,
    orbit_vars_C2: np.ndarray,
    orbit_vars_C3: np.ndarray,
    eps: float = 1e-30,
) -> dict: ...
# Returns: dict with stat_C1C2, p_C1C2, stat_C1C3, p_C1C3

def anti_confound_gate(encoder_c2: nn.Module) -> dict: ...
# Returns: dict with passed: bool, max_diff: float, code_inspection: bool

def gate_check(ratios: dict, wilcoxon: dict, anti_gate: dict) -> bool: ...
# Prints gate table, returns True if all MUST_WORK gates pass; sys.exit(1) on fail

def main() -> None: ...
```

### visualize (`code/visualize.py`)

**Dependencies:** matplotlib, numpy

```python
def plot_orbitvar_violin(
    orbit_vars_C1: np.ndarray,
    orbit_vars_C2: np.ndarray,
    orbit_vars_C3: np.ndarray,
    out_path: str,
) -> None: ...
# Figure 1: violin+scatter log10(OrbitVar) per encoder, annotated mean

def plot_ratio_histogram(
    ratios_C1_C2: np.ndarray,
    ratios_C1_C3: np.ndarray,
    out_path: str,
) -> None: ...
# Figure 2: histogram log10(ratio), vertical line at 4

def plot_summary_table(results: dict, out_path: str) -> None: ...
# Figure 3: matplotlib table — Encoder | Mean OrbitVar | OOM vs C1 | Gate
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Prereq Verification | Verify H-E1 env/results exist; load orbit_vars_C2/C3 from JSON; assert means match known values | 5 | 1+1+1+2 |
| A-2 | CISEEncoder (C1) | Implement sinusoidal PE channel encoder; no order stats; forward(state_dict)->embedding | 10 | 3+2+3+2 |
| A-3 | CISE OrbitVar Measurement | Reuse compute_orbit_var_all_models with CISEEncoder; BUILD_ON gate (reuse 0.010333 if audit confirmed) | 8 | 2+3+2+1 |
| A-4 | Ratio Computation | Per-model C1/C2 and C1/C3 ratios; mean/median/geomean aggregates; log10 OOM | 7 | 2+1+2+2 |
| A-5 | Wilcoxon Tests | Paired Wilcoxon on log10(OrbitVar) for C1>C2 and C1>C3; gate p<0.001 | 6 | 1+2+2+1 |
| A-6 | Anti-Confound Gate | Unit test DeepSetsChannelEncoder channel permutation invariance; inspect .phi source for sort/argsort/topk | 7 | 2+2+2+1 |
| A-7 | Gate Check + Results Save | Print gate table; save orbit_var_ratios.json and h_m1_summary.csv; exit 0/1 | 5 | 1+1+1+2 |
| A-8 | Visualization | 3 figures: violin, ratio histogram, summary table; save to figures/ | 8 | 2+1+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2], Low(4-8): [A-1, A-3, A-4, A-5, A-6, A-7, A-8]

---

## Data Flow

- `h-e1/results/orbit_var_results.json` → `verify_prerequisites` → `orbit_vars_C2`, `orbit_vars_C3`
- `data/dataset_cifar_small_hyp_rand.pt` → `load_dataset` (H-E1) → `measure_cise_orbitvar` → `orbit_vars_C1`
- `orbit_vars_C1/C2/C3` → `compute_ratios` + `run_wilcoxon` + `anti_confound_gate`
- All results → `gate_check` → `save_results` → `visualize`

## H-E1 Results File

Expected key names in `h-e1/results/orbit_var_results.json` (per H-E1 `save_results`):
- `orbit_vars_C2` (list of floats, len=100)
- `orbit_vars_C3` (list of floats, len=100)
- `mean_orbitvar_C2`, `mean_orbitvar_C3`

If keys differ, load by inspection of the JSON before asserting.
