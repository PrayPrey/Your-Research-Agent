# Architecture Document: H-M1

**Hypothesis:** Calibration moderates truthfulness-robustness correlation
**Date:** 2026-08-28
**Type:** MECHANISM

---

## 1. System Overview

```
h-m1/code/
├── ece.py           # ECE computation (15-bin)
├── analysis.py      # Correlations + Fisher z-test
├── main.py          # Orchestration
├── config.py        # Settings + model list
└── results/         # Output data
    ├── ece_scores.json
    ├── correlations.json
    └── moderation.json

h-m1/figures/
├── ece_vs_metrics.png
├── calibration_curves.png
└── tertile_comparison.png
```

## 2. Component Design

### 2.1 ECE Module (ece.py)

**Responsibility:** Compute Expected Calibration Error from model outputs

```python
def compute_ece(confidences, predictions, labels, n_bins=15) -> float
def get_model_ece(model_id: str, mmlu_results_path: str) -> float
def compute_all_ece(models: list, results_dir: str) -> dict
```

**Complexity:** Medium (binning logic, file parsing)

### 2.2 Analysis Module (analysis.py)

**Responsibility:** Statistical tests and correlation analysis

```python
# Reuse from h-e1
from h_e1.code.analysis import partial_corr, bootstrap_ci

# New for h-m1
def fisher_z_test(r1, n1, r2, n2) -> tuple[float, float]
def tertile_moderation_test(ece, truthfulqa, advglue) -> dict
def correlate_ece_with_metrics(ece, tqa, adv, log_params) -> dict
```

**Complexity:** Medium (statistical computations)

### 2.3 Main Orchestrator (main.py)

**Responsibility:** Run full analysis pipeline

```python
def main():
    # 1. Load cached h-e1 data
    # 2. Compute ECE for all models
    # 3. Run correlation analysis
    # 4. Run moderation test
    # 5. Generate visualizations
    # 6. Save results
```

**Complexity:** Low (orchestration only)

### 2.4 Config Module (config.py)

**Responsibility:** Centralized configuration

```python
SEED = 42
N_BINS = 15
MODELS = [...]  # Extend from h-e1
THRESHOLDS = {
    "ece_correlation_r": -0.2,
    "ece_correlation_p": 0.10,
    "fisher_p": 0.05
}
```

## 3. Data Flow

```
h-e1/code/results/     →  Load cached scores
        ↓
MMLU logits (HF)       →  Compute ECE per model
        ↓
ece.py                 →  ece_scores.json
        ↓
analysis.py            →  correlations.json + moderation.json
        ↓
visualization          →  figures/
        ↓
04_validation.md       →  Gate evaluation
```

## 4. Epic Tasks

| Epic | Description | Complexity | Subtasks |
|------|-------------|------------|----------|
| E1 | Setup + Config | Low | 2 |
| E2 | ECE Computation | Medium | 3 |
| E3 | Correlation Analysis | Medium | 2 |
| E4 | Moderation Test | Medium | 2 |
| E5 | Visualization | Medium | 2 |
| E6 | Validation | Low | 2 |
| **Total** | | | **13** |

## 5. Dependencies

| Component | Depends On |
|-----------|------------|
| ece.py | numpy, MMLU results |
| analysis.py | scipy, h-e1/analysis.py |
| main.py | ece.py, analysis.py, config.py |
| visualizations | matplotlib, results/ |

## 6. Complexity Assessment

| Factor | Rating | Justification |
|--------|--------|---------------|
| Algorithmic | Medium | ECE binning, Fisher z-test |
| Data | Low | Reuse h-e1 cached data |
| Integration | Low | Extend existing codebase |
| **Overall** | Medium | Standard statistical analysis |

---

*Architecture designed for MECHANISM hypothesis with h-e1 dependencies*
