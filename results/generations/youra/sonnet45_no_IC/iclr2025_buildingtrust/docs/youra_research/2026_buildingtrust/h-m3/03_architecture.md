# System Architecture: h-m3

**Date:** 2026-07-12
**Hypothesis:** h-m3 (MECHANISM - Stratified Correlation Comparison)
**Type:** MECHANISM
**Author:** Architecture Agent

---

## Applied Patterns

**Archon KB:**
- Applied: Statistical hypothesis testing workflow (scipy.stats)

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Patterns found from h-m1 base code
**Analyzed Path:** `docs/youra_research/h-m1/code/`
**Findings:** H-M1 already computed stratified correlations and saved to `outputs/results.csv`. H-M3 will load these cached results and apply Fisher z-test for comparison.

---

## System Overview

This MECHANISM hypothesis tests whether reliability-robustness correlation strength differs significantly across prompt types (factual vs. misinformation). The architecture is a pure statistical analysis workflow that reuses 100% of cached data from H-M1.

**Core Validation:** Fisher z-test p < 0.05 AND |r_factual - r_misinfo| ≥ 0.1

**Key Difference from H-M1:** H-M1 computed correlations per stratum. H-M3 tests if those correlations differ significantly.

---

## Module Structure

### DataLoader (`src/data_loader.py`)

**Dependencies:** pandas, pathlib

```python
class CachedResultsLoader:
    def __init__(self, h_m1_output_path: str): ...
    def load_correlation_results(self) -> pd.DataFrame: ...
    def validate_cached_data(self, df: pd.DataFrame) -> bool: ...
    def get_factual_correlation(self, df: pd.DataFrame) -> dict: ...
    def get_misinfo_correlation(self, df: pd.DataFrame) -> dict: ...
```

### FisherZTest (`src/fisher_z_test.py`)

**Dependencies:** scipy, numpy

```python
class FisherZTest:
    def __init__(self, alpha: float = 0.05): ...
    def compare_correlations(self, r1: float, n1: int, r2: float, n2: int) -> dict: ...
    def compute_z_statistic(self, r1: float, r2: float, n1: int, n2: int) -> tuple[float, float]: ...
    def compute_confidence_intervals(self, r: float, n: int, confidence: float = 0.95) -> tuple[float, float]: ...
    def compute_effect_size(self, r1: float, r2: float) -> dict: ...
```

### GateValidator (`src/gate_validator.py`)

**Dependencies:** FisherZTest

```python
class MechanismGateValidator:
    def __init__(self, p_threshold: float = 0.05, delta_r_threshold: float = 0.1): ...
    def validate_primary_criterion(self, fisher_result: dict) -> bool: ...
    def validate_secondary_criterion(self, r_factual: float, r_misinfo: float) -> bool: ...
    def validate_tertiary_criterion(self, r_factual: float, r_misinfo: float) -> bool: ...
    def evaluate_gate(self, fisher_result: dict, r_factual: float, r_misinfo: float) -> dict: ...
```

### Visualizer (`src/visualizer.py`)

**Dependencies:** matplotlib, seaborn, numpy

```python
class ComparisonVisualizer:
    def __init__(self, output_dir: str): ...
    def plot_gate_metrics_comparison(self, fisher_result: dict, target_p: float = 0.05) -> None: ...
    def plot_forest_plot(self, r_factual: float, r_misinfo: float, ci_factual: tuple, ci_misinfo: tuple, n_factual: int, n_misinfo: int) -> None: ...
    def plot_scatter_comparison(self, results_df: pd.DataFrame) -> None: ...
    def generate_all_figures(self, results: dict) -> None: ...
```

### ReportGenerator (`src/report_generator.py`)

**Dependencies:** GateValidator, pathlib

```python
class ValidationReportGenerator:
    def __init__(self, output_path: str): ...
    def generate_report(self, fisher_result: dict, gate_result: dict, correlations: dict) -> None: ...
    def format_statistics_table(self, fisher_result: dict) -> str: ...
    def format_gate_evaluation(self, gate_result: dict) -> str: ...
    def save_results_json(self, results: dict, output_path: str) -> None: ...
```

### Configuration (`src/config.py`)

**Dependencies:** dataclasses

```python
@dataclass
class FisherTestConfig:
    alpha: float = 0.05
    confidence_level: float = 0.95
    p_threshold: float = 0.05
    delta_r_threshold: float = 0.1

@dataclass
class GateConfig:
    factual_r_threshold: float = 0.4
    misinfo_r_threshold: float = 0.3

@dataclass
class ExperimentConfig:
    h_m1_output_path: str
    output_dir: str
    figures_dir: str
    fisher: FisherTestConfig
    gate: GateConfig

def load_config() -> ExperimentConfig: ...
```

### Main Orchestrator (`run_experiment.py`)

**Dependencies:** All modules

```python
def main():
    config = load_config()
    
    # Load cached correlation results from H-M1
    loader = CachedResultsLoader(config.h_m1_output_path)
    results_df = loader.load_correlation_results()
    
    # Extract per-stratum correlations
    factual_corr = loader.get_factual_correlation(results_df)
    misinfo_corr = loader.get_misinfo_correlation(results_df)
    
    # Fisher z-test comparison
    fisher_test = FisherZTest(alpha=config.fisher.alpha)
    fisher_result = fisher_test.compare_correlations(
        r1=factual_corr["r"],
        n1=factual_corr["n"],
        r2=misinfo_corr["r"],
        n2=misinfo_corr["n"]
    )
    
    # Compute confidence intervals
    ci_factual = fisher_test.compute_confidence_intervals(factual_corr["r"], factual_corr["n"])
    ci_misinfo = fisher_test.compute_confidence_intervals(misinfo_corr["r"], misinfo_corr["n"])
    
    # Compute effect size
    effect_size = fisher_test.compute_effect_size(factual_corr["r"], misinfo_corr["r"])
    
    # Gate validation
    validator = MechanismGateValidator(
        p_threshold=config.fisher.p_threshold,
        delta_r_threshold=config.fisher.delta_r_threshold
    )
    gate_result = validator.evaluate_gate(fisher_result, factual_corr["r"], misinfo_corr["r"])
    
    # Visualization
    visualizer = ComparisonVisualizer(config.figures_dir)
    visualizer.generate_all_figures({
        "fisher": fisher_result,
        "factual": {**factual_corr, "ci": ci_factual},
        "misinfo": {**misinfo_corr, "ci": ci_misinfo},
        "effect_size": effect_size,
        "gate": gate_result
    })
    
    # Generate validation report
    report_gen = ValidationReportGenerator(
        os.path.join(config.output_dir, "04_validation.md")
    )
    report_gen.generate_report(fisher_result, gate_result, {
        "factual": factual_corr,
        "misinfo": misinfo_corr
    })
    
    # Save results
    report_gen.save_results_json({
        "fisher_test": fisher_result,
        "correlations": {"factual": factual_corr, "misinfo": misinfo_corr},
        "effect_size": effect_size,
        "gate": gate_result
    }, os.path.join(config.output_dir, "fisher_test_results.json"))
    
    return 0 if gate_result["passed"] else 1
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From h-m1 Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| Cached Results | Direct file load | `h-m1/code/outputs/results.csv` |
| Config Pattern | Reuse config structure | `h-m1/code/src/config.py` |

**Verified from:** `docs/youra_research/h-m1/code/` (actual implementation)

**Critical Data Reuse:**
- H-M1 `outputs/results.csv` contains stratified correlation results
- Format: `stratum,r,p_value,ci_lower,ci_upper,n`
- No new model inference or scoring needed

---

## File Organization

```
h-m3/
├── code/
│   ├── src/
│   │   ├── data_loader.py
│   │   ├── fisher_z_test.py
│   │   ├── gate_validator.py
│   │   ├── visualizer.py
│   │   ├── report_generator.py
│   │   └── config.py
│   ├── run_experiment.py
│   ├── requirements.txt
│   └── README.md
├── outputs/
│   ├── correlation_results.json
│   ├── fisher_test_results.json
│   └── 04_validation.md
└── figures/
    ├── gate_metrics_comparison.png (MANDATORY)
    ├── forest_plot.png
    └── scatter_comparison.png
```

---

## Data Flow

1. **DataLoader** loads cached correlation results from h-m1/code/outputs/results.csv
2. **FisherZTest** applies Fisher z-transformation and computes test statistic
3. **FisherZTest** computes confidence intervals using Fisher z back-transform
4. **FisherZTest** computes Cohen's q effect size
5. **GateValidator** evaluates SHOULD_WORK gate criteria
6. **Visualizer** generates 3 figures including mandatory gate metrics
7. **ReportGenerator** writes 04_validation.md and saves JSON results

**Expected Runtime:** < 2 minutes (pure statistical computation, no model inference)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| C-1 | Cached Data Loading | Load and validate h-m1 correlation results from CSV | 6 | Module(1) + Dependencies(1) + Algorithm(2) + Integration(2) |
| C-2 | Fisher z-Test Implementation | Implement Fisher z-transformation, test statistic, p-value computation | 14 | Module(3) + Dependencies(2) + Algorithm(5) + Integration(4) |
| C-3 | Confidence Interval Computation | Compute 95% CI using Fisher z back-transform for both strata | 9 | Module(2) + Dependencies(2) + Algorithm(3) + Integration(2) |
| C-4 | Effect Size Calculation | Compute Cohen's q and classify effect magnitude | 7 | Module(2) + Dependencies(1) + Algorithm(2) + Integration(2) |
| C-5 | Gate Validation Logic | Validate SHOULD_WORK criteria (p<0.05, delta_r≥0.1, directional pattern) | 10 | Module(2) + Dependencies(2) + Algorithm(3) + Integration(3) |
| C-6 | Visualization Suite | Generate forest plot, scatter comparison, gate metrics chart | 13 | Module(3) + Dependencies(2) + Algorithm(4) + Integration(4) |
| C-7 | Validation Report Generation | Generate 04_validation.md with gate evaluation and statistics | 8 | Module(2) + Dependencies(1) + Algorithm(3) + Integration(2) |

**Total Complexity:** 67 (distributed across 7 tasks)

**Distribution:**
- Very High (18-20): []
- High (14-17): [C-2]
- Medium (9-13): [C-3, C-5, C-6]
- Low (4-8): [C-1, C-4, C-7]

---

## Complexity Analysis

### High-Complexity Components

**C-2: Fisher z-Test Implementation (14)**
- Fisher z-transformation: `z = 0.5 * ln((1+r)/(1-r))`
- Standard error: `se_diff = sqrt(1/(n1-3) + 1/(n2-3))`
- Test statistic: `z_stat = (z1 - z2) / se_diff`
- Two-tailed p-value from standard normal distribution
- Integration with scipy.stats for CDF computation

### Moderate-Complexity Components

**C-6: Visualization Suite (13)**
- Forest plot with error bars and annotations
- Side-by-side scatter plots with regression lines
- Gate metrics comparison bar chart
- Coordinate multiple data sources

**C-5: Gate Validation Logic (10)**
- Primary: Fisher p < 0.05
- Secondary: |delta_r| ≥ 0.1
- Tertiary: r_factual > 0.4 AND r_misinfo < 0.3
- Aggregate gate result

**C-3: Confidence Interval Computation (9)**
- Fisher z-transform: CI in z-space
- Back-transform to correlation space: `r = tanh(z)`
- Apply to both strata

### Low-Complexity Components

**C-7: Validation Report Generation (8)**
- Format statistics table
- Write markdown report
- Save JSON results

**C-4: Effect Size Calculation (7)**
- Cohen's q: `q = z1 - z2`
- Effect magnitude classification

**C-1: Cached Data Loading (6)**
- Read CSV from h-m1 outputs
- Validate stratum labels and sample sizes
- Extract correlation values

---

## Critical Dependencies

### External Libraries
- `scipy >= 1.10.0` (Fisher z-test, stats.norm)
- `numpy >= 1.24.0` (arctanh, tanh transformations)
- `pandas >= 2.0.0` (CSV loading)
- `matplotlib >= 3.7.0`, `seaborn >= 0.12.0` (visualization)

### Internal Dependencies
- **H-M1 outputs:** `h-m1/code/outputs/results.csv` (cached correlation results)
- **TruthfulQA metadata:** Not needed (already in h-m1 results)

### MCP Services
- **Archon:** Project and task management
- **Serena:** Not required (minimal codebase, statistical analysis only)

---

## Validation Strategy

### SHOULD_WORK Gate Validation
```python
def validate_should_work_gate(fisher_result: dict, r_factual: float, r_misinfo: float) -> bool:
    """
    Validate SHOULD_WORK gate:
    - Primary: Fisher z-test p < 0.05
    - Secondary: |r_factual - r_misinfo| ≥ 0.1
    - Tertiary: r_factual > 0.4 AND r_misinfo < 0.3
    """
    primary = fisher_result["p_value"] < 0.05
    secondary = abs(r_factual - r_misinfo) >= 0.1
    tertiary = (r_factual > 0.4) and (r_misinfo < 0.3)
    
    return primary and secondary and tertiary
```

### Secondary Validation
- **Confidence interval non-overlap:** 95% CIs for factual and misinfo do not overlap
- **Effect size:** Cohen's q ≥ 0.3 (large effect)

---

## Risk Mitigation

### H-M1 Results Not Available
- **Strategy:** Verify h-m1/code/outputs/results.csv exists before running
- **Fallback:** Fail fast with clear error message if file missing

### Insignificant Correlation Difference
- **Strategy:** Report PARTIAL if p < 0.10 (marginal significance)
- **Fallback:** FAIL gate and recommend independence hypothesis

### Invalid Cached Data
- **Strategy:** Validate sample sizes (n_factual ≥ 10, n_misinfo ≥ 10)
- **Fallback:** Fail with validation error if data corrupted

---

## Expected Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Cached Data Loading (C-1) | 0.1 days | H-M1 outputs |
| Fisher z-Test (C-2) | 0.3 days | C-1 |
| Confidence Intervals (C-3) | 0.2 days | C-2 |
| Effect Size (C-4) | 0.1 days | C-2 |
| Gate Validation (C-5) | 0.2 days | C-2, C-3, C-4 |
| Visualization (C-6) | 0.3 days | C-2, C-3, C-5 |
| Report Generation (C-7) | 0.2 days | C-5, C-6 |

**Total:** 1 day (sequential execution)

**Critical Path:** C-1 → C-2 → C-3 → C-5 → C-6 → C-7

---

## Success Criteria

### Primary (SHOULD_WORK Gate)
- **Fisher z-test p < 0.05** (significant correlation difference)
- **|r_factual - r_misinfo| ≥ 0.1** (meaningful effect magnitude)
- **r_factual > 0.4 AND r_misinfo < 0.3** (directional pattern matches theory)

### Secondary
- Confidence intervals do not overlap (95% CI)
- Cohen's q ≥ 0.3 (large effect size)

### Deliverables
- `correlation_results.json` with per-stratum correlations and CIs
- `fisher_test_results.json` with test statistic, p-value, effect size
- `figures/gate_metrics_comparison.png` - Mandatory gate visualization
- `figures/forest_plot.png` - Correlation comparison with error bars
- `figures/scatter_comparison.png` - Side-by-side reliability vs. robustness
- `04_validation.md` - Gate evaluation report with results summary

---

**Document Status:** FINAL
**Last Updated:** 2026-07-12
**Next Phase:** Phase 4 - Implementation (Coder Agent)
