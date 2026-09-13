# Architecture: H-M1
# RLHF Proxy-Gold Divergence Mechanism Verification

**Hypothesis ID:** H-M1
**Type:** MECHANISM (PoC — INCREMENTAL from H-E1)
**Tier:** FULL
**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr

Applied: Incremental extension pattern — inherit H-E1 DataLoader; extend with scipy stats pipeline

---

## Codebase Analysis (Serena)

**Project Type:** INCREMENTAL (base: H-E1)
**Status:** Analyzed H-E1 actual code structure
**Analyzed Path:** `docs/youra_research/h-e1/code/`

**Findings from H-E1 code:**
- `src/data/loader.py` — `load_dataset(csv_path, dataset_name) -> pd.DataFrame`; validates required columns + ≥5 non-null rows; reusable as-is
- `src/verification/coexistence.py` — `verify_signal_coexistence(df, dataset_name) -> dict`; H-M1 does NOT reuse this (different verification logic)
- `src/visualization/plots.py` — `plot_dual_axis()`, `plot_comparison()`; H-M1 extends with new plot types but can share dual-axis base
- `src/reporting/reporter.py` — `print_report()`, `save_results()`; reusable pattern
- `main.py` — orchestration pattern; H-M1 replicates structure

**Import Paths Verified from H-E1 code:**
```python
from src.data.loader import load_dataset          # REUSE — exact signature confirmed
from src.reporting.reporter import print_report    # REUSE — pattern identical
```

**New Modules Required:**
- `src/analysis/trajectory.py` — Spearman test + peak-reversal detection + divergence computation
- `src/visualization/plots.py` — 3 new plot types (divergence gap, Spearman scatter, gate bar chart)

Note: Archon MCP unavailable (ablation mode). Architecture grounded from PRD (03_prd.md) and H-E1 code analysis.

---

## File Organization

```
h-m1/
  code/
    main.py                      # entrypoint — orchestrates H-M1 pipeline
    src/
      data/
        loader.py                # REUSE from H-E1 (copy or symlink)
      analysis/
        trajectory.py            # NEW: monotonicity test, peak-reversal, divergence
      visualization/
        plots.py                 # NEW: 5 required figures (extends H-E1 plots pattern)
      reporting/
        reporter.py              # REUSE pattern from H-E1; adapted for H-M1 metrics
    data/                        # gitignored — place digitized CSVs here
      coste_digitized.csv        # PRIMARY (may symlink from H-E1)
      gao_digitized.csv          # SECONDARY
    results/                     # JSON output + divergence curve CSV for H-M2
    config.yaml                  # H-M1 experiment configuration
    requirements.txt
  docs/youra_research/h-m1/
    figures/                     # 5 saved figure outputs
    results/
      h_m1_results.json
      h_m1_divergence_curve.csv  # feed-forward to H-M2
```

---

## Module Structure

### DataLoader (`src/data/loader.py`) — REUSE FROM H-E1

**Dependencies:** pandas

```python
REQUIRED_COLS = ["kl_budget", "rm_score", "gold_preference"]

def load_dataset(csv_path: str, dataset_name: str) -> pd.DataFrame:
    # Raises ValueError if required columns missing or < 5 non-null paired rows
    # Signature VERIFIED from h-e1/code/src/data/loader.py
    ...
```

---

### TrajectoryAnalyzer (`src/analysis/trajectory.py`) — NEW

**Dependencies:** numpy, scipy

```python
def run_rm_monotonicity_test(kl: np.ndarray, rm: np.ndarray) -> dict:
    # Spearman ρ(KL, RM) via scipy.stats.spearmanr
    # Returns: {rho_rm_kl, p_rho, monotone_pass}

def detect_peak_reversal(kl: np.ndarray, gold: np.ndarray) -> dict:
    # np.argmax for peak; reversal_confirmed = gold[peak_idx] > gold[-1]
    # Returns: {peak_idx, peak_kl, reversal_confirmed, peak_kl_valid}

def compute_divergence(rm: np.ndarray, gold: np.ndarray) -> dict:
    # divergence_curve = rm - gold; divergence_final = divergence_curve[-1]
    # Returns: {divergence_final, divergence_curve, divergence_positive}

def run_analysis(df: pd.DataFrame) -> dict:
    # Orchestrates above 3 functions; returns full analysis results dict
    ...
```

---

### Plotter (`src/visualization/plots.py`) — NEW (5 figure types)

**Dependencies:** matplotlib, numpy

```python
def plot_trajectory_dual_axis(df: pd.DataFrame, results: dict, out_dir: str) -> str:
    # Dual-axis: RM (steelblue left) + gold (crimson right) vs KL; peak KL marked with vertical dashed line
    # Returns saved figure path

def plot_divergence_gap(df: pd.DataFrame, divergence_curve: np.ndarray, out_dir: str) -> str:
    # (RM − gold) vs KL budget; horizontal zero line
    # Returns saved figure path

def plot_spearman_scatter(df: pd.DataFrame, rho: float, out_dir: str) -> str:
    # RM score vs KL scatter + trend line + ρ annotation
    # Returns saved figure path

def plot_gao_overlay(gao_df: pd.DataFrame, out_dir: str) -> str:
    # Same dual-axis for Gao data; separate panel; labeled "Preliminary"
    # Returns saved figure path

def plot_gate_metrics(results: dict, out_dir: str) -> str:
    # Bar chart: rho_rm_kl vs 0.8 threshold, reversal_confirmed, divergence_final vs 0
    # Returns saved figure path
```

---

### Reporter (`src/reporting/reporter.py`) — NEW (H-M1 adapted)

**Dependencies:** json, pathlib, pandas

```python
def print_report(results: dict) -> None:
    # Structured stdout: all gate metrics, PASS/FAIL with explanation

def save_results(results: dict, out_path: str) -> None:
    # Save h_m1_results.json with all required fields

def save_divergence_curve(df: pd.DataFrame, divergence_curve: np.ndarray, out_path: str) -> None:
    # Save h_m1_divergence_curve.csv for H-M2 feed-forward
```

---

### Entrypoint (`main.py`) — NEW

**Dependencies:** DataLoader, TrajectoryAnalyzer, Plotter, Reporter, ExperimentConfig

```python
def main() -> None:
    # 1. load_config()
    # 2. load_dataset() for Coste (primary) + Gao (secondary)
    # 3. run_analysis(coste_df) → results
    # 4. 5 plot functions
    # 5. print_report() + save_results() + save_divergence_curve()
    # 6. sys.exit(0 if gate passes else 1)

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Files | Complexity | Breakdown |
|----|------|-------------|-------|------------|-----------|
| E1 | Data Acquisition | Manual: download Coste/Gao PDFs, export Figs 3-4/Fig 2 as 300+ DPI PNG, digitize with WebPlotDigitizer (2× per figure, mean), export CSVs to `code/data/`; OR symlink from H-E1 data if already present | `code/data/coste_digitized.csv`, `code/data/gao_digitized.csv` | 7 | 1+2+1+3=7 Low |
| E2 | Environment Setup | Create `requirements.txt` (pandas, numpy, scipy, matplotlib), verify Python ≥3.9, set up directory structure; extend H-E1 environment with scipy | `requirements.txt`, `code/` dirs | 4 | 1+1+1+1=4 Low |
| E3 | Data Loading & Validation | Copy/import `load_dataset()` from H-E1; verify columns and ≥5 rows for both Coste and Gao CSVs; sort by kl_budget; extract baseline values | `src/data/loader.py` | 7 | 2+1+2+2=7 Low |
| E4 | Trajectory Analysis Module | Implement `run_rm_monotonicity_test()` (Spearman ρ), `detect_peak_reversal()` (np.argmax + reversal check), `compute_divergence()` (divergence_curve + divergence_final), `run_analysis()` orchestrator | `src/analysis/trajectory.py` | 16 | 4+3+5+4=16 High |
| E5 | Visualization | Implement all 5 figures: dual-axis with peak marker, divergence gap curve, Spearman scatter with trend, Gao preliminary overlay, gate metrics bar chart; save to figures/ | `src/visualization/plots.py` | 14 | 3+2+5+4=14 High |
| E6 | Reporting & Feed-forward | Implement stdout report, JSON save (`h_m1_results.json`), divergence CSV save (`h_m1_divergence_curve.csv` for H-M2); wire `main.py`; gate check + exit code | `src/reporting/reporter.py`, `main.py` | 10 | 2+2+4+2=10 Medium |
| E7 | Configuration | Implement `ExperimentConfig` dataclass + `config.yaml` + `load_config()`; extend H-E1 config pattern with new fields: monotonicity_rho_threshold, peak_kl_min/max, divergence_min | `config.yaml`, `src/config.py` | 8 | 2+1+3+2=8 Medium |

**Task Count:** 7 Epic tasks
**Complexity Distribution:** High (14-17): [E4, E5], Medium (9-13): [E6, E7], Low (4-8): [E1, E2, E3]

---

## External Dependencies (from H-E1)

| Module | Source Path | Import | Verified From |
|--------|-------------|--------|---------------|
| `load_dataset` | `h-e1/code/src/data/loader.py` | `from src.data.loader import load_dataset` | H-E1 03_logic.md + architecture |
| `print_report` pattern | `h-e1/code/src/reporting/reporter.py` | Reused structurally (not imported directly) | H-E1 architecture module spec |

**Note:** scipy is the key new dependency vs H-E1. `scipy.stats.spearmanr` is the primary new function.

---

## Notes

- No model training, no GPU, no weights. Pure pandas + scipy + matplotlib pipeline.
- `data/` directory gitignored; CSVs placed manually after WebPlotDigitizer digitization (E1 is human-action task).
- `main.py` exits non-zero on gate failure to signal blocking to downstream hypothesis loop.
- `h_m1_divergence_curve.csv` is a mandatory output — H-M2 reads it directly for gap quantification.
- Figure count: 5 (dual-axis trajectory, divergence gap, Spearman scatter, Gao preliminary, gate bar chart).
- Outputs: figures to `docs/youra_research/h-m1/figures/`, JSON + CSV to `docs/youra_research/h-m1/results/`.
