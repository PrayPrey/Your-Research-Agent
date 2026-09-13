# Architecture: H-M2

**hypothesis_id:** h-m2
**hypothesis_type:** MECHANISM
**gate:** SHOULD_WORK
**generated_at:** 2026-03-16
**Applied:** evaluation-continuation pattern (checkpoint reuse, gate extension)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Patterns found from base code (Read tool fallback — Serena project not active)
**Analyzed Path**: `docs/youra_research/20260316_wsl/h-m1/code/src/`
**Findings**: H-M1 implements `evaluate_all_encoders()` (returns 72-row DataFrame, cols: [encoder, seed, severity, rho, delta_rho, ci_lower, ci_upper, p_value]) and `evaluate_gate_condition_v2()` (MUST_WORK gate, 5 boolean indicators). H-M2 adds `evaluate_gate_hm2()` wrapping the SHOULD_WORK three-way ranking logic on top of these reused functions. `build_encoder()` factory and `load_checkpoint()` in `src/train.py` are the loading interface.

---

## File Organization

H-M2 code is placed entirely in `h-m2/code/`. H-M1 source is imported via `sys.path`.

```
h-m2/code/
  src/
    gate_evaluator.py     # SHOULD_WORK gate + bootstrap stats
    visualize_hm2.py      # 5 required figures
  run_experiment_hm2.py   # main entry point
  results/                # hm2_results.json, hm2_eval_df.csv (generated)
  figures/                # 5 .png files (generated)
```

H-M1 source (read-only):
```
h-m1/code/src/
  models.py               # build_encoder(), all 6 encoder classes
  evaluate.py             # evaluate_all_encoders(), evaluate_gate_condition_v2()
  data_loader.py          # load_zoo(), ZooDataset, DataLoader builders
  config.py               # ExperimentConfig, GateConfig, ENCODER_CONFIG
  train.py                # load_checkpoint()
h-m1/code/checkpoints/    # 12 .pt files (4 encoders × 3 seeds)
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| build_encoder | `from src.models import build_encoder` | `h-m1/code/src/models.py` |
| evaluate_all_encoders | `from src.evaluate import evaluate_all_encoders` | `h-m1/code/src/evaluate.py` |
| evaluate_gate_condition_v2 | `from src.evaluate import evaluate_gate_condition_v2` | `h-m1/code/src/evaluate.py` |
| load_checkpoint | `from src.train import load_checkpoint` | `h-m1/code/src/train.py` |
| load_zoo | `from src.data_loader import load_zoo` | `h-m1/code/src/data_loader.py` |
| ExperimentConfig | `from src.config import ExperimentConfig, GateConfig` | `h-m1/code/src/config.py` |

**sys.path setup** (must appear before any src imports):
```python
import sys, os
HM1_SRC = os.path.abspath("docs/youra_research/20260316_wsl/h-m1/code")
sys.path.insert(0, HM1_SRC)
```

**Verified from**: `h-m1/code/src/` actual implementation (Read tool)

---

## Module Structure

### GateEvaluatorHM2 (`h-m2/code/src/gate_evaluator.py`)

**Dependencies**: src.evaluate (H-M1), scipy.stats, numpy, pandas

```python
ENCODERS_HM2 = ["flat-MLP", "flat-MLP+aug", "flat-MLP+canon", "NFT-base"]
AUG_THRESHOLD  = 0.05
CANON_THRESHOLD = 0.03
NFT_THRESHOLD   = 0.02

def evaluate_gate_hm2(eval_df: pd.DataFrame) -> dict: ...
# Returns: {aug_partial, canon_partial, nft_superior, ranking, passed,
#           mean_dr_by_encoder, gate_type}

def run_bootstrap_pairwise(
    preds_a: np.ndarray,
    preds_b: np.ndarray,
    labels: np.ndarray,
    n_bootstrap: int = 10_000,
    seed: int = 42,
) -> dict: ...
# Returns: {delta_rho_mean, p_value, ci_lower, ci_upper, cohens_d}

def holm_correct(p_values: list[float]) -> list[float]: ...

def check_consistency_with_hm1(
    mean_dr_by_encoder: dict,
    tolerance: float = 0.01,
) -> dict: ...
# Checks NFT-base Δρ <= 0.03, flat-MLP+aug Δρ >= 0.21
# Returns: {nft_consistent, aug_consistent, passed}
```

---

### VisualizerHM2 (`h-m2/code/src/visualize_hm2.py`)

**Dependencies**: matplotlib, seaborn, pandas, numpy

```python
def plot_gate_metrics_comparison(
    eval_df: pd.DataFrame,
    gate_result: dict,
    out_path: str = "h-m2/figures/gate_metrics_comparison.png",
) -> None: ...
# Bar chart: mean Δρ at s=1.0 for 4 encoders, 95% CI, threshold lines (0.02, 0.03, 0.05)

def plot_delta_rho_heatmap(
    eval_df: pd.DataFrame,
    out_path: str = "h-m2/figures/delta_rho_heatmap.png",
) -> None: ...
# 4-encoder × 4-severity heatmap (blue=robust, red=degraded)

def plot_rho_degradation_curves(
    eval_df: pd.DataFrame,
    out_path: str = "h-m2/figures/rho_degradation_curves.png",
) -> None: ...
# Line plot: mean Spearman ρ vs severity, seed-level error bands

def plot_threeway_ranking_scatter(
    eval_df: pd.DataFrame,
    out_path: str = "h-m2/figures/threeway_ranking_scatter.png",
) -> None: ...
# Per-seed Δρ scatter at s=1.0 with threshold zones

def plot_bootstrap_distributions(
    bootstrap_results: dict,
    out_path: str = "h-m2/figures/bootstrap_distributions.png",
) -> None: ...
# Overlapping bootstrap Δρ distributions: aug vs NFT-base, canon vs NFT-base
```

---

### RunExperimentHM2 (`h-m2/code/run_experiment_hm2.py`)

**Dependencies**: GateEvaluatorHM2, VisualizerHM2, src.evaluate (H-M1), src.data_loader (H-M1), src.config (H-M1)

```python
HM1_CKPT_ROOT = "docs/youra_research/20260316_wsl/h-m1/code/checkpoints"
DATA_CACHE    = ".data_cache/datasets/unterthiner_mnist_zoo/zoo_enriched.pkl"
RESULTS_DIR   = "docs/youra_research/20260316_wsl/h-m2/results"
FIGURES_DIR   = "docs/youra_research/20260316_wsl/h-m2/figures"

def verify_checkpoints(ckpt_root: str, encoders: list, seeds: list) -> dict: ...
# Checks all 12 .pt files exist and load_state_dict succeeds
# Returns: {all_ok: bool, missing: list, failed: list}

def build_training_results_from_checkpoints(
    ckpt_root: str, encoders: list, seeds: list
) -> list[dict]: ...
# Constructs training_results list compatible with evaluate_all_encoders() signature

def run_pairwise_bootstrap_tests(
    eval_df: pd.DataFrame,
    flat_test_loader,
    device: torch.device,
    flat_input_dim: int,
    layer_fan_ins: list,
) -> dict: ...
# Runs bootstrap for (aug vs NFT) and (canon vs NFT), returns Holm-corrected p-values

def save_results(
    gate_result: dict,
    eval_df: pd.DataFrame,
    bootstrap_results: dict,
    results_dir: str,
) -> None: ...
# Saves hm2_results.json and hm2_eval_df.csv

def main() -> None: ...
# Full pipeline: env setup → checkpoint verify → data load → evaluate → gate → viz → save
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment Setup | sys.path config, dir creation, GPU/seed setup, dependency check | 5 | 1+1+1+2 |
| A-2 | Checkpoint Verification | Verify 12 .pt files exist, load_state_dict all succeed, report missing | 8 | 2+2+2+2 |
| A-3 | Data & Split Setup | Load zoo_enriched.pkl, apply seed=42 split, build flat/NFT loaders | 9 | 2+2+3+2 |
| A-4 | Multi-Severity Evaluation | Call evaluate_all_encoders() on 4 encoders × 4 sev × 3 seeds = 48 rows | 11 | 3+3+3+2 |
| A-5 | Bootstrap Statistical Tests | Paired bootstrap n=10,000 for aug/canon vs NFT; Holm correction; Cohen's d | 14 | 3+3+4+4 |
| A-6 | H-M2 Gate Evaluator | Implement evaluate_gate_hm2(), consistency check vs H-M1 ±0.01 | 12 | 3+3+3+3 |
| A-7 | Visualization Suite | All 5 required figures with threshold annotations | 13 | 3+2+4+4 |
| A-8 | Results Reporting | Save hm2_results.json + hm2_eval_df.csv, print gate report to stdout | 7 | 2+2+1+2 |
| A-9 | Integration Test | End-to-end smoke test: load checkpoints → eval → gate returns valid dict | 9 | 2+3+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-5], Medium(9-13): [A-4, A-6, A-7, A-3], Low(4-8): [A-1, A-2, A-8, A-9]

---

## Data Flow

```
zoo_enriched.pkl
  → load_zoo() [H-M1 data_loader.py]
  → train/test split (seed=42)
  → flat_test_loader, nft_test_loader

h-m1/code/checkpoints/*.pt (12 files)
  → verify_checkpoints()
  → build_training_results_from_checkpoints()
  → evaluate_all_encoders() [H-M1 evaluate.py]
  → eval_df (48 rows: 4 encoders × 3 seeds × 4 severities)

eval_df
  → evaluate_gate_hm2()    → gate_result dict
  → run_bootstrap_tests()  → bootstrap_results dict
  → VisualizerHM2 (5 figs)
  → save_results() → hm2_results.json, hm2_eval_df.csv
```

---

## Key Interfaces

### evaluate_all_encoders() call signature (H-M1 actual)

```python
eval_df = evaluate_all_encoders(
    training_results=training_results,   # list[dict] with checkpoint_path keys
    cfg=cfg,                             # ExperimentConfig (encoder_names filtered to 4)
    flat_test_loader=flat_test_loader,
    nft_test_loader=nft_test_loader,
    flat_input_dim=flat_input_dim,
    layer_fan_ins=layer_fan_ins,
)
# Returns DataFrame columns: [encoder, seed, severity, rho, delta_rho, ci_lower, ci_upper, p_value]
```

### Checkpoint file naming (verified from h-m1/code/checkpoints/)

```
flat-MLP_seed42.pt          flat-MLP_seed123.pt          flat-MLP_seed456.pt
flat-MLPplusaug_seed42.pt   flat-MLPplusaug_seed123.pt   flat-MLPplusaug_seed456.pt
flat-MLPpluscanon_seed42.pt flat-MLPpluscanon_seed123.pt flat-MLPpluscanon_seed456.pt
NFT-base_seed42.pt          NFT-base_seed123.pt          NFT-base_seed456.pt
```

**Note**: The `+` in encoder names maps to `plus` in checkpoint filenames. Verified from 02c_experiment_brief.md Serena findings.

---

*Hypothesis type: MECHANISM | Gate: SHOULD_WORK*
*H-M1 source reused via sys.path — do NOT copy or modify H-M1 files*
