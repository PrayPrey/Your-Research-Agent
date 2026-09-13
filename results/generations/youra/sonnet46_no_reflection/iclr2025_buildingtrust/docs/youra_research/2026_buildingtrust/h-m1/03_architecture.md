# Architecture: H-M1 — RI → ECE Mechanism Verification

**Applied: modular-statistical-pipeline (single-responsibility modules, CSV/YAML outputs)**
**Applied: incremental-hypothesis-extension (reuse base code via import, add new modules only)**

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Patterns found from actual h-e1 code (Serena project resolution used direct file reads due to project selection requirement)
**Analyzed Path**: `docs/youra_research/20260512_buildingtrust/h-e1/code/`
**Findings**: DataAssembler class in `data_assembly.py` with `load_trustllm_scores()`, `load_lmeval_scores()`, `merge_matrix()`, `validate_matrix()` methods; RIComputer class in `compute_ri.py` with `compute_pc1()`, `fit_ols()`, `check_vif()`, `compute()` methods; `config.py` exports SEED=42, N_BOOTSTRAP=10000, CAP_COLS, VIF_THRESHOLD=5.0; outputs land in `outputs/` directory as `model_matrix.csv` and `ri_scores.csv`.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| DataAssembler | `sys.path.insert(0, "../h-e1/code"); from data_assembly import DataAssembler` | `h-e1/code/data_assembly.py` |
| RIComputer | `sys.path.insert(0, "../h-e1/code"); from compute_ri import RIComputer` | `h-e1/code/compute_ri.py` |
| assemble_matrix | `from data_assembly import assemble_matrix` | `h-e1/code/data_assembly.py` |
| compute_residual_instability | `from compute_ri import compute_residual_instability` | `h-e1/code/compute_ri.py` |

**Verified from**: `h-e1/code/data_assembly.py`, `h-e1/code/compute_ri.py` (actual implementation)

**H-E1 Output Paths (read-only):**
- `../h-e1/code/outputs/model_matrix.csv` — 30 models × PC1, mean_confidence, advglue_drop, family, scale, regime
- `../h-e1/code/outputs/ri_scores.csv` — 30 models × RI score

---

## File Organization

```
h-m1/
├── code/
│   ├── run_experiment.py       # Entry point (FR-7)
│   ├── data_loader.py          # FR-1: Load H-E1 outputs + merge ECE
│   ├── ece_computer.py         # FR-2: ECE computation per model
│   ├── partial_corr.py         # FR-3: Spearman partial correlation + Holm
│   ├── evaluate.py             # FR-4: Secondary tests + gate evaluation
│   ├── visualize.py            # FR-5: 6 figures
│   ├── config.py               # Fixed constants for H-M1
│   └── requirements.txt
├── figures/
├── results/
└── tests/
    ├── test_data_loader.py
    ├── test_ece_computer.py
    ├── test_partial_corr.py
    └── test_evaluate.py
```

---

## Module Interfaces

### Config (`code/config.py`)

**Dependencies**: none

```python
SEED: int = 42
N_BOOTSTRAP: int = 10000
VIF_THRESHOLD: float = 5.0
RHO_THRESHOLD: float = 0.4
P_THRESHOLD: float = 0.05
FAMILY_SIGN_THRESHOLD: int = 2
TARGET_FAMILIES: list[str] = ["LLaMA", "Mistral", "Qwen"]
MIN_FAMILY_SIZE: int = 5
H_E1_OUTPUTS_DIR: str = "../h-e1/code/outputs"
RESULTS_DIR: str = "results"
FIGURES_DIR: str = "figures"
```

---

### DataLoader (`code/data_loader.py`)

**Dependencies**: Config, h-e1 outputs (CSV files)

```python
import pandas as pd

class DataLoader:
    def __init__(self, h_e1_outputs_dir: str = config.H_E1_OUTPUTS_DIR) -> None: ...

    def load_model_matrix(self) -> pd.DataFrame:
        """Load h-e1/code/outputs/model_matrix.csv.
        Returns DataFrame (30, ≥7): model_id, model_family, scale,
        training_regime, PC1, mean_confidence, advglue_drop.
        """
        ...

    def load_ri_scores(self) -> pd.DataFrame:
        """Load h-e1/code/outputs/ri_scores.csv.
        Returns DataFrame (30, 2): model_id, RI.
        """
        ...

    def merge_with_ece(self, ece_series: pd.Series) -> pd.DataFrame:
        """Merge model_matrix + RI scores + ECE column.
        Args:
            ece_series: pd.Series {model_id: ECE_scalar}
        Returns DataFrame (30, 8+) with ECE column, no NaN.
        """
        ...

    def validate(self, df: pd.DataFrame) -> bool:
        """Assert shape (30, 8+), no NaN in [RI, ECE, PC1, mean_confidence],
        ECE in [0, 1], all 30 H-E1 models present.
        """
        ...


def load_experiment_data(ece_series: pd.Series) -> pd.DataFrame:
    """Top-level entry point. Returns validated merged DataFrame."""
    ...
```

---

### ECEComputer (`code/ece_computer.py`)

**Dependencies**: Config, uncertainty-calibration (`pip install uncertainty-calibration`)

```python
import numpy as np
import pandas as pd
import calibration as cal

class ECEComputer:
    def __init__(self, seed: int = config.SEED, n_bootstrap: int = config.N_BOOTSTRAP) -> None: ...

    def compute_ece(self, probs: np.ndarray, labels: np.ndarray) -> float:
        """Compute ECE scalar via cal.get_ece(probs, labels).
        Args:
            probs: shape (N,) predicted probabilities in [0,1]
            labels: shape (N,) ground-truth binary labels
        Returns: ECE scalar in [0, 1]
        """
        ...

    def compute_ece_ci(self, probs: np.ndarray, labels: np.ndarray) -> tuple[float, float]:
        """Bootstrap 95% CI on ECE (10K resamples).
        Returns: (lower, upper) tuple
        """
        ...

    def compute_per_model(
        self,
        model_probs_dict: dict[str, np.ndarray],
        labels_dict: dict[str, np.ndarray],
    ) -> pd.DataFrame:
        """Compute ECE + CI for all 30 models.
        Returns DataFrame (30, 3): model_id, ECE, ECE_ci_lower, ECE_ci_upper.
        """
        ...

    def load_or_compute(
        self,
        model_ids: list[str],
        cache_path: str = "results/ece_scores.csv",
    ) -> pd.DataFrame:
        """Load cached ECE or compute from lm-eval logits.
        Fallback: mock ECE from Gaussian calibrated to literature (ECE~0.05-0.25).
        Returns DataFrame (30, 3): model_id, ECE, ECE_ci_lower, ECE_ci_upper.
        """
        ...


def compute_ece_scores(model_ids: list[str]) -> pd.DataFrame:
    """Top-level entry point."""
    ...
```

---

### PartialCorrAnalyzer (`code/partial_corr.py`)

**Dependencies**: Config, pingouin==0.6.1, statsmodels

```python
import pandas as pd
import numpy as np
import pingouin as pg
from statsmodels.stats.multitest import multipletests

class PartialCorrAnalyzer:
    def __init__(
        self,
        target_families: list[str] = config.TARGET_FAMILIES,
        min_family_size: int = config.MIN_FAMILY_SIZE,
        n_bootstrap: int = config.N_BOOTSTRAP,
        seed: int = config.SEED,
    ) -> None: ...

    def full_partial_corr(self, df: pd.DataFrame) -> dict:
        """Spearman partial ρ(RI, ECE | PC1, mean_confidence) on full N=30.
        Uses pg.partial_corr(data=df, x="RI", y="ECE",
                             covar=["PC1","mean_confidence"], method="spearman").
        Returns dict: {rho: float, p_val: float, ci95: tuple, n: int}
        """
        ...

    def family_partial_corr(self, df: pd.DataFrame) -> dict[str, dict]:
        """Per-family Spearman partial correlation.
        Subsets df by model_family for each family in target_families.
        Returns {family: {rho: float, p_val: float, n: int}} for families with n≥5.
        """
        ...

    def holm_correction(self, p_values: list[float]) -> np.ndarray:
        """Apply Holm correction via statsmodels.multipletests.
        Returns array of Holm-corrected p-values.
        """
        ...

    def bootstrap_rho_ci(self, df: pd.DataFrame) -> tuple[float, float]:
        """Bootstrap 95% CI on full Spearman partial ρ (10K resamples).
        Returns: (lower, upper)
        """
        ...

    def run(self, df: pd.DataFrame) -> dict:
        """Full analysis pipeline: full + family + Holm + bootstrap CI.
        Returns complete results dict matching partial_corr_results.yaml schema.
        """
        ...


def run_partial_correlation_analysis(df: pd.DataFrame) -> dict:
    """Top-level entry point."""
    ...
```

---

### GateEvaluator (`code/evaluate.py`)

**Dependencies**: Config, PartialCorrAnalyzer results, pingouin, statsmodels, scipy

```python
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.outliers_influence import variance_inflation_factor

class GateEvaluator:
    def __init__(
        self,
        rho_threshold: float = config.RHO_THRESHOLD,
        p_threshold: float = config.P_THRESHOLD,
        family_sign_threshold: int = config.FAMILY_SIGN_THRESHOLD,
        vif_threshold: float = config.VIF_THRESHOLD,
    ) -> None: ...

    def baseline_corr(self, df: pd.DataFrame) -> dict:
        """Spearman ρ(PC1, ECE) — capability-only null model.
        Returns dict: {rho: float, p_val: float}
        """
        ...

    def check_vif(self, df: pd.DataFrame) -> dict[str, float]:
        """VIF for [RI, PC1, mean_confidence]. Must be < 5.0.
        Returns {RI: float, PC1: float, mean_confidence: float}
        """
        ...

    def cooks_distance(self, df: pd.DataFrame) -> dict:
        """Compute Cook's distance, flag models with D > 4/n.
        Returns {flagged_models: list[str], d_values: dict[str, float]}
        """
        ...

    def fisher_z_test(self, df: pd.DataFrame) -> dict:
        """Fisher z-test: ρ_high_PC1 vs ρ_low_PC1 split.
        Returns {z_stat: float, p_val: float, rho_high: float, rho_low: float}
        """
        ...

    def evaluate_gate(self, partial_corr_results: dict) -> dict:
        """Evaluate PASS/PARTIAL/FAIL gate from partial correlation results.
        PASS: rho≥0.4 AND p<0.05 AND consistent_positive≥2
        PARTIAL: rho≥0.3 AND p<0.10 (document, FAIL gate)
        FAIL: rho<0.2 or sign_reversal>1 family
        Returns gate_results dict matching gate_results.yaml schema.
        """
        ...

    def run_all_secondary(self, df: pd.DataFrame) -> dict:
        """Run all secondary tests: baseline_corr + vif + cooks + fisher_z.
        Returns consolidated secondary_results dict.
        """
        ...


def evaluate_experiment(
    df: pd.DataFrame,
    partial_corr_results: dict,
) -> tuple[dict, dict]:
    """Top-level entry point.
    Returns (gate_results, secondary_results).
    """
    ...
```

---

### Visualizer (`code/visualize.py`)

**Dependencies**: Config, matplotlib, seaborn, DataLoader results

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

class Visualizer:
    def __init__(self, figures_dir: str = config.FIGURES_DIR, dpi: int = 300) -> None: ...

    def fig1_partial_regression_scatter(
        self, df: pd.DataFrame, rho: float, p_val: float
    ) -> Path:
        """Scatter RI vs ECE with partial regression line + 95% CI band.
        Annotates ρ and p-value. Saves fig1_ri_ece_scatter.png.
        """
        ...

    def fig2_residuals_scatter(self, df: pd.DataFrame) -> Path:
        """RI_residual vs ECE_residual (after removing PC1, mean_confidence).
        Saves fig2_residuals_scatter.png.
        """
        ...

    def fig3_family_subplots(
        self, df: pd.DataFrame, family_results: dict[str, dict]
    ) -> Path:
        """3-panel subplot: LLaMA / Mistral / Qwen with per-family ρ annotation.
        Saves fig3_family_subplots.png.
        """
        ...

    def fig4_reliability_diagram(self, df: pd.DataFrame, ece_df: pd.DataFrame) -> Path:
        """Reliability diagram: confidence bins vs accuracy, sorted by RI quartile.
        Saves fig4_reliability_diagram.png.
        """
        ...

    def fig5_rho_comparison_bar(
        self, rho_baseline: float, rho_partial: float,
        ci_baseline: tuple, ci_partial: tuple
    ) -> Path:
        """Bar: ρ(PC1, ECE) vs ρ(RI, ECE | PC1) with bootstrap CI error bars.
        Saves fig5_rho_comparison_bar.png.
        """
        ...

    def fig6_gate_summary(
        self, rho_actual: float, rho_target: float, ci: tuple
    ) -> Path:
        """Gate summary: target ρ=0.40 vs actual ρ with CI.
        Saves fig6_gate_summary.png.
        """
        ...

    def generate_all(
        self,
        df: pd.DataFrame,
        ece_df: pd.DataFrame,
        partial_corr_results: dict,
        secondary_results: dict,
    ) -> list[Path]:
        """Generate all 6 figures. Returns list of saved paths."""
        ...
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies**: All modules above

```python
import argparse
import sys

def parse_args() -> argparse.Namespace:
    """--data-dir, --output-dir, --figures-dir, --seed, --no-compute-ece"""
    ...

def main() -> int:
    """Orchestrates: ECEComputer → DataLoader → PartialCorrAnalyzer
    → GateEvaluator → Visualizer → export results.
    Exit code 0 on PASS gate; exit code 1 on FAIL/PARTIAL gate.
    """
    ...

if __name__ == "__main__":
    sys.exit(main())
```

---

## Data Flow

- ECEComputer → `ece_scores.csv` (model_id, ECE, CI bounds)
- DataLoader: loads `model_matrix.csv` + `ri_scores.csv` + ECE → merged DataFrame (30, 8+)
- PartialCorrAnalyzer: merged DataFrame → `partial_corr_results.yaml`
- GateEvaluator: partial_corr_results + merged DataFrame → `gate_results.yaml` + secondary stats
- Visualizer: merged DataFrame + results → 6 PNG figures
- RunExperiment: saves `model_matrix_m1.csv`, `ece_scores.csv`, `partial_corr_results.yaml`, `gate_results.yaml`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Config | Project scaffold, config.py, requirements.txt, conda env extension | 5 | 1+1+1+2 |
| A-2 | DataLoader | Load H-E1 CSVs, merge RI + ECE, validate (30, 8+) shape | 8 | 2+2+2+2 |
| A-3 | ECEComputer | ECE per model via uncertainty-calibration, bootstrap CIs, mock fallback | 14 | 3+3+4+4 |
| A-4 | PartialCorrAnalyzer | Full + family Spearman partial ρ, Holm correction, bootstrap CI on ρ | 15 | 3+3+5+4 |
| A-5 | GateEvaluator | Baseline ρ, VIF, Cook's distance, Fisher z-test, PASS/PARTIAL/FAIL logic | 13 | 3+3+4+3 |
| A-6 | Visualizer | 6 figures: partial regression, residuals, family subplots, reliability, bar, gate | 12 | 3+2+4+3 |
| A-7 | Results Export | YAML/CSV export for partial_corr_results, ece_scores, model_matrix_m1, gate_results | 7 | 2+2+1+2 |
| A-8 | RunExperiment | CLI entry point, orchestration, exit code gate, end-to-end test | 9 | 2+3+2+2 |
| A-9 | Test Suite | Unit tests for DataLoader, ECEComputer, PartialCorrAnalyzer, GateEvaluator (≥80% coverage) | 10 | 2+2+3+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3, A-4], Medium(9-13): [A-5, A-6, A-8, A-9], Low(4-8): [A-1, A-2, A-7]
