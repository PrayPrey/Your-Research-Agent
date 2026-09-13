# Architecture: h-m-integrated - Mechanism Validation Pipeline

**Date:** 2026-08-20
**Hypothesis:** MECHANISM
**Status:** Full validation pipeline

Applied: Modular DL experiment pattern (diffusers training structure)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** h-e1 implementation found - reuse data loader, UQ methods, base metrics
**Analyzed Path:** docs/youra_research/h-e1/code/
**Findings:** TruthfulQALoader, 6 UQ methods (temp_scaling, conformal, mc_k1/3/5/10), AUROC+Spearman metrics exist. Extend with AUSE, cross-dataset calibration, expanded visualization.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From h-e1 Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| TruthfulQALoader | `from h_e1.data.loader import TruthfulQALoader` | `h-e1/code/data/loader.py` |
| TemperatureScaling | `from h_e1.uq.methods import TemperatureScaling` | `h-e1/code/uq/methods.py` |
| ConformalPrediction | `from h_e1.uq.methods import ConformalPrediction` | `h-e1/code/uq/methods.py` |
| MCDropout | `from h_e1.uq.methods import MCDropout` | `h-e1/code/uq/methods.py` |
| compute_auroc | `from h_e1.eval.metrics import compute_auroc` | `h-e1/code/eval/metrics.py` |
| compute_spearman | `from h_e1.eval.metrics import compute_spearman` | `h-e1/code/eval/metrics.py` |

**Verified from:** docs/youra_research/h-e1/code/ (actual implementation)

---

## Module Structure

### DataManager (`data/manager.py`)

**Dependencies:** h_e1.data.loader, HuggingFace datasets

```python
class DataManager:
    def __init__(self, h_e1_cache_dir: str, seed: int = 42): ...
    def load_h_e1_artifacts(self) -> dict: ...  # {answers, uq_scores, calibration_params}
    def load_halueval(self, split: str = "qa", cache_dir: str = None) -> tuple[list, list]: ...  # (calib, test)
    def verify_splits(self, h_e1_data: dict) -> bool: ...  # Check 40/60 split consistency
```

### UQMechanismValidator (`eval/mechanism_validator.py`)

**Dependencies:** h_e1.eval.metrics, scipy, sklearn, numpy

```python
class UQMechanismValidator:
    def __init__(self, uq_scores: dict, predictions: list, labels: list): ...
    def compute_spearman(self, method_name: str) -> tuple[float, float]: ...  # (rho, p_value)
    def compute_auroc(self, method_name: str) -> float: ...
    def compute_ause(self, method_name: str, n_bins: int = 10) -> float: ...
    def validate_all_methods(self) -> dict: ...  # {method: {spearman, auroc, ause, pass_gate}}
    def check_gate(self, results: dict) -> tuple[bool, str]: ...  # (passed, reason)
```

### CrossDatasetCalibrator (`eval/cross_dataset.py`)

**Dependencies:** h_e1.uq.methods, numpy

```python
class CrossDatasetCalibrator:
    def __init__(self, source_data: list, target_data: list, alpha: float = 0.1): ...
    def calibrate_on_source(self, method: str = "conformal") -> float: ...  # Returns threshold
    def test_transfer_to_target(self, threshold: float) -> dict: ...  # {coverage, auroc_target, transfer_success}
    def compute_coverage_gap(self, coverage: float) -> float: ...  # |coverage - (1-alpha)|
```

### Visualizer (`visualize.py`)

**Dependencies:** matplotlib, numpy

```python
def plot_gate_metrics_scatter(results: dict, save_path: str): ...
def plot_spearman_comparison(results: dict, save_path: str): ...
def plot_ause_vs_auroc(results: dict, save_path: str): ...
def plot_sparsification_curves(validator: UQMechanismValidator, save_path: str): ...
def plot_cross_dataset_calibration(calibrator: CrossDatasetCalibrator, save_path: str): ...
```

### ReportGenerator (`report.py`)

**Dependencies:** UQMechanismValidator, CrossDatasetCalibrator, json

```python
class ReportGenerator:
    def __init__(self, output_dir: str): ...
    def generate_validation_report(self, results: dict, figures: list[str]) -> str: ...  # Returns markdown
    def save_metrics_json(self, results: dict, path: str): ...
    def save_sparsification_data(self, data: dict, path: str): ...
```

### Runner (`run_experiment.py`)

**Dependencies:** All above modules

```python
def main():
    # 1. Load h-e1 artifacts + HaluEval
    # 2. Validate mechanism (Spearman, AUROC, AUSE)
    # 3. Test cross-dataset calibration
    # 4. Generate visualizations
    # 5. Generate validation report
    # 6. Check gate conditions
```

---

## File Organization

```
experiments/h-m-integrated/
├── data/
│   └── manager.py              # h-e1 artifact loading + HaluEval loader
├── eval/
│   ├── mechanism_validator.py  # Spearman, AUROC, AUSE computation + gate check
│   └── cross_dataset.py        # Conformal calibration transfer (HaluEval → TruthfulQA)
├── visualize.py                # 5 plots (gate scatter, Spearman bar, AUSE vs AUROC, sparsification, transfer)
├── report.py                   # Validation report generator (04_validation.md)
├── run_experiment.py           # Main runner
└── config.py                   # Paths, thresholds, method names
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | Load h-e1 artifacts + HaluEval QA split | 8 | 2+2+2+2 |
| A-2 | Mechanism validator | Spearman, AUROC, AUSE + gate check | 12 | 3+3+3+3 |
| A-3 | Cross-dataset calibration | Conformal transfer HaluEval → TruthfulQA | 11 | 3+2+3+3 |
| A-4 | HaluEval inference | Generate answers + uncertainty scores on 10k samples | 14 | 4+3+4+3 |
| A-5 | Visualization suite | 5 plots (gate scatter, Spearman, AUSE, sparsification, transfer) | 13 | 3+3+4+3 |
| A-6 | Report generation | 04_validation.md + metrics.json + gate decision | 9 | 2+2+3+2 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [A-4], Medium(9-13): [A-2, A-3, A-5, A-6], Low(4-8): [A-1]

---

## Implementation Notes

### Reused from h-e1

1. TruthfulQALoader - no changes needed
2. UQ method implementations (TemperatureScaling, ConformalPrediction, MCDropout)
3. compute_auroc, compute_spearman - extend with AUSE
4. Generated answers + uncertainty scores (6 methods × 817 questions)

### New Components

1. **AUSE metric** - sparsification curve computation
2. **HaluEval data loader** - ~10k QA samples, 80/20 split
3. **Cross-dataset calibrator** - conformal threshold transfer
4. **Extended visualization** - 5 plots vs 3 in h-e1
5. **Gate check logic** - non-degenerate methods (5/6), dual metric (Spearman OR AUROC)

### Gate Conditions

```python
# Non-degenerate methods: All except mc_k1
non_degenerate = [m for m in methods if m != "mc_k1"]

# Each method passes if: Spearman > 0.2 OR AUROC > 0.55
passed = sum(1 for m in non_degenerate if results[m]["spearman_rho"] > 0.2 or results[m]["auroc"] > 0.55)

# Experiment passes if: >= 4 of 5 non-degenerate methods pass
gate_passed = passed >= 4

# Cross-dataset transfer passes if: |coverage - 0.90| <= 0.10
transfer_passed = abs(coverage - 0.90) <= 0.10
```

---

## Dependencies

```python
# From h-e1
torch>=2.0.0
transformers>=4.36.0
datasets>=2.14.0

# Shared
sklearn>=1.3.0
numpy>=1.24.0
scipy>=1.11.0

# Visualization
matplotlib>=3.7.0
pandas>=2.0.0  # For result tables
```

---

## Success Validation

**Primary Gate Conditions:**
1. At least 4 of 5 non-degenerate methods pass (Spearman > 0.2 OR AUROC > 0.55)
2. Conformal coverage transfer Δ ≤ 0.10 from target (0.90)

**Failure Conditions (STOP):**
1. If ≥2 non-degenerate methods fail both Spearman AND AUROC → mechanism broken
2. If conformal coverage on TruthfulQA < 0.70 → critical transfer failure

**Quality Checks:**
1. All 5 figures generated and saved
2. 04_validation.md exists with complete results table
3. metrics.json contains all method results
4. No runtime errors during metric computation
