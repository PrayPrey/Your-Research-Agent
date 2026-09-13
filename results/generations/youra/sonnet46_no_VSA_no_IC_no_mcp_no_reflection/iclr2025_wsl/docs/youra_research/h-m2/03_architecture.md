# Architecture: h-m2
# Differential Advantage of Permutation-Equivariant Encoders (gap vs. test_acc)

**Date:** 2026-08-31
**Author:** yoon303@etri.re.kr
**Type:** MECHANISM (INCREMENTAL — extends h-m1)

Applied: Dual-target controlled comparison pattern (train same encoder on two targets, compute differential)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Patterns found from base code
**Analyzed Path**: `h-m1/code/run_analysis.py`
**Findings**: H-M1 is a single `run_analysis.py` bridging to h-e1/code via sys.path. All encoders, data loading, and training live in `h-e1/code/`. H-M2 follows identical bridge pattern, adding `target="test_acc"` training and Δ computation.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code — h-m1/code/run_analysis.py lines 16-29)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| ExperimentConfig | `from config import ExperimentConfig, ENCODER_CONFIGS` | `h-e1/code/config.py` |
| load_zoo | `from data.loader import load_zoo, ZooData, make_loader` | `h-e1/code/data/loader.py` |
| compute_split | `from data.audit import compute_split` | `h-e1/code/data/audit.py` |
| FlatMLP | `from encoders.flat_mlp import FlatMLP` | `h-e1/code/encoders/flat_mlp.py` |
| DWSNet | `from encoders.dwsnet import DWSNet` | `h-e1/code/encoders/dwsnet.py` |
| NFT | `from encoders.nft import NFT` | `h-e1/code/encoders/nft.py` |
| GNN | `from encoders.gnn import GNN` | `h-e1/code/encoders/gnn.py` |
| random_search | `from training.train import random_search, train_encoder` | `h-e1/code/training/train.py` |
| eval_spearman | `from evaluation.evaluate import eval_spearman` | `h-e1/code/evaluation/evaluate.py` |

**Bridge pattern (from h-m1 actual code):**
```python
H_E1_CODE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../h-e1/code"))
sys.path.insert(0, H_E1_CODE)
os.chdir(H_E1_CODE)
```

**Verified from**: `h-m1/code/run_analysis.py` (actual implementation, lines 16–19)

---

## File Organization

```
h-m2/
  code/
    run_experiment.py      # main entry point: train test_acc, compute Δ, P3, gate
    compute_delta.py       # Δ formula, bootstrap CI, gate check
    metrics.py             # partial_spearman (P3), bootstrap helpers
    visualize.py           # 5 figures → h-m2/figures/
  checkpoints/
    flat_mlp_testacc_best.pt
    dws_net_testacc_best.pt
    nft_testacc_best.pt
    gnn_testacc_best.pt
  figures/
    fig1_gate_delta.png
    fig2_dual_target_spearman.png
    fig3_delta_decomposition.png
    fig4_partial_corr_scatter.png
    fig5_bootstrap_ci.png
  04_results.json
```

---

## Module Structure

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: h-e1 bridge (load_zoo, encoders, random_search, eval_spearman), compute_delta, metrics, visualize

```python
H_E1_CODE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../h-e1/code"))
sys.path.insert(0, H_E1_CODE)
os.chdir(H_E1_CODE)

SHAPES_2D = [(3*3*3,4),(4*3*3,8),(8*8*8,64),(64,10)]
CHECKPOINT_DIR: str  # h-m2/checkpoints/
FIGURES_DIR: str     # h-m2/figures/
RESULTS_PATH: str    # h-m2/04_results.json
SEED: int = 42
BOOTSTRAP_N: int = 1000

H_M1_GAP_RESULTS: dict = {
    "FlatMLP": 0.5330, "DWSNet": 0.4881, "NFT": 0.5752, "GNN": 0.3747
}

def build_encoder(name: str, input_dim: int) -> torch.nn.Module: ...
def train_testacc(name: str, zoo: ZooData, device: str) -> tuple[float, dict]: ...
    # 3-trial random_search on target="test_acc", returns (best_r, best_state)
def evaluate_testacc(name: str, model: torch.nn.Module, zoo: ZooData) -> np.ndarray: ...
    # returns predictions array for bootstrap + Spearman
def verify_mechanism(gap_results: dict, testacc_results: dict, delta: dict) -> bool: ...
def save_results(testacc_results: dict, delta: dict, p3: dict, gate: bool) -> None: ...
def main() -> None: ...
```

---

### ComputeDelta (`code/compute_delta.py`)

**Dependencies**: numpy, scipy.stats

```python
H_M1_GAP: dict[str, float]  # hardcoded from h-m1/04_results.json

def compute_delta(gap_results: dict[str, float],
                  testacc_results: dict[str, float]) -> dict[str, float]:
    # Δ(enc) = (gap[enc]-gap[FlatMLP]) - (acc[enc]-acc[FlatMLP])
    ...

def gate_check(delta: dict[str, float], threshold: float = 0.02) -> tuple[int, bool]:
    # returns (n_pass, passed) where n_pass >= 2 → True
    ...

def bootstrap_delta_ci(gap_preds: dict[str, np.ndarray],
                       testacc_preds: dict[str, np.ndarray],
                       true_gap: np.ndarray,
                       true_testacc: np.ndarray,
                       n_boot: int = 1000,
                       seed: int = 42) -> dict[str, tuple[float, float]]:
    # returns {enc: (ci_low, ci_high)} 95% CI on Δ
    ...
```

---

### Metrics (`code/metrics.py`)

**Dependencies**: numpy, scipy.stats, sklearn.linear_model

```python
def partial_spearman(pred_gap: np.ndarray,
                     true_gap: np.ndarray,
                     true_testacc: np.ndarray) -> tuple[float, float]:
    # Spearman(pred_gap_resid, true_gap_resid | rank(true_testacc))
    # returns (r, p_value)
    ...

def bootstrap_spearman_ci(preds: np.ndarray,
                          targets: np.ndarray,
                          n_boot: int = 1000,
                          seed: int = 42) -> tuple[float, float]:
    # 95% CI on Spearman r
    ...
```

---

### Visualize (`code/visualize.py`)

**Dependencies**: matplotlib, numpy

```python
def fig1_gate_delta(delta: dict[str, float],
                    ci: dict[str, tuple],
                    threshold: float,
                    out_path: str) -> None:
    # Bar chart: Δ per equivariant encoder + threshold line at 0.02
    ...

def fig2_dual_target_spearman(gap_results: dict,
                               testacc_results: dict,
                               out_path: str) -> None:
    # Side-by-side bars: 4 encoders × 2 targets
    ...

def fig3_delta_decomposition(gap_results: dict,
                              testacc_results: dict,
                              out_path: str) -> None:
    # Stacked bar: gap_improvement + acc_improvement components per encoder
    ...

def fig4_partial_corr_scatter(pred_gap_resid: np.ndarray,
                               true_gap_resid: np.ndarray,
                               r: float, p: float,
                               out_path: str) -> None:
    # Scatter of residuals for NFT P3 check
    ...

def fig5_bootstrap_ci(delta: dict,
                      ci: dict,
                      out_path: str) -> None:
    # Error bar plot: Δ ± 95% CI for 3 equivariant encoders
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment & Bridge Setup | Verify h-e1 bridge path, checkpoints dir, figures dir; smoke-test imports | 5 | 1+1+1+2 |
| A-2 | Data Loading (dual-target) | Extend load_zoo call to return both gap and test_acc labels; verify split identity to H-M1 | 6 | 1+2+1+2 |
| A-3 | Train FlatMLP on test_acc | 3-trial random search on test_acc target; save checkpoint; eval Spearman with CI | 8 | 2+2+2+2 |
| A-4 | Train DWSNet/NFT/GNN on test_acc | Same protocol as A-3 for 3 equivariant encoders; save checkpoints; eval Spearman | 12 | 3+3+3+3 |
| A-5 | Δ Computation & Gate Check | compute_delta.py: Δ formula, gate check (≥2 of 3), bootstrap CI on Δ | 10 | 2+2+4+2 |
| A-6 | Partial Spearman P3 | metrics.py: rank-based residual regression, Spearman on residuals, report r+p | 9 | 2+2+3+2 |
| A-7 | Mechanism Verification | verify_mechanism(): sanity checks (testacc range, NFT gap consistency, Δ non-null) | 6 | 1+2+2+1 |
| A-8 | Visualization (5 figures) | visualize.py: fig1–fig5 as specified; save to h-m2/figures/ | 10 | 2+2+3+3 |
| A-9 | Results Export | save_results(): 04_results.json with all Spearman, Δ, CI, gate, P3 values | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4, A-5, A-6, A-8], Low(4-8): [A-1, A-2, A-3, A-7, A-9]

---

## Data Flow

- `run_experiment.py` → loads zoo (both targets) via h-e1 `load_zoo`
- Trains 4 encoders on `test_acc` → saves checkpoints → collects `testacc_results`
- `compute_delta.py` → uses hardcoded `H_M1_GAP_RESULTS` + `testacc_results` → Δ, gate, CI
- `metrics.py` → NFT gap predictions + true labels → P3 (r, p)
- `visualize.py` → all results → 5 figures
- `save_results()` → `04_results.json`

## Key Constants (From h-m1 actual code)

```python
SHAPES_2D = [(3*3*3,4), (4*3*3,8), (8*8*8,64), (64,10)]
INPUT_DIM = 33890
SEED = 42
N_TRIALS = 3
LR_RANGE = (5e-4, 2e-3)
BATCH_SIZE = 64
EPOCHS = 100
H_M1_GAP_RESULTS = {"FlatMLP": 0.5330, "DWSNet": 0.4881, "NFT": 0.5752, "GNN": 0.3747}
GATE_THRESHOLD = 0.02
GATE_MIN_PASS = 2
```
