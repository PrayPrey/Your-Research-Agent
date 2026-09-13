# Logic Design: h-m3

**Date:** 2026-07-12
**Hypothesis:** h-m3 (MECHANISM - Stratified Correlation Comparison)
**Type:** MECHANISM
**Author:** Logic Agent

---

## Applied Patterns

**Archon KB:**
- Applied: scipy.stats statistical analysis for correlation comparison
- Applied: Fisher z-transformation for correlation inference

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** API signatures verified from h-m1 actual implementation
**Analyzed Path:** `/workspace/TEST_buildingtrust/docs/youra_research/h-m1/code/`
**Relevant Symbols:**
- `load_dataset()` - Returns (factual_data, misinfo_data) dicts with keys: questions, answers, category
- `compute_correlation_with_ci()` - Returns dict with r, p_value, ci_lower, ci_upper, n
- `save_results()` - Saves results.csv with format: stratum,r,p_value,ci_lower,ci_upper,n
- `validate_mechanism_gate()` - Returns dict with gate_result, gate_checks, all_passed

---

## External Dependencies API (From h-m1 Actual Code)

The following APIs are called from base hypothesis h-m1. Signatures verified from actual implementation:

```python
# From: h-m1/code/run_experiment.py (ACTUAL CODE, lines 33-88, 223-256, 312-344)

def load_dataset(max_samples_per_stratum=None) -> tuple[dict, dict]:
    """Load TruthfulQA dataset and stratify into factual/misinformation strata.
    
    Returns:
        (factual_data, misinfo_data) where each dict has keys:
        - questions: List[str]
        - answers: List[str]
        - category: List[str]
    """
    ...

def compute_correlation_with_ci(
    reliability: np.ndarray,
    robustness: np.ndarray,
    stratum_name: str
) -> dict:
    """Compute Pearson correlation with 95% CI via Fisher z-transform.
    
    Args:
        reliability: [N] scores
        robustness: [N] scores
        stratum_name: Name of the stratum (for logging)
    
    Returns:
        {
            "r": float,
            "p_value": float,
            "ci_lower": float,
            "ci_upper": float,
            "n": int
        }
    """
    ...

def save_results(
    factual_result: dict,
    misinfo_result: dict,
    gate_stats: dict,
    output_dir: str = "outputs"
) -> None:
    """Save correlation results and statistics.
    
    File format (results.csv):
        stratum,r,p_value,ci_lower,ci_upper,n
        factual,0.7233,0.000001,0.6854,0.7612,400
        misinformation,0.2798,0.012345,0.1523,0.4073,417
    """
    ...
```

**Verified from:** `/workspace/TEST_buildingtrust/docs/youra_research/h-m1/code/run_experiment.py`

**Critical Data Format:**
- H-M1 outputs cached in: `h-m1/code/outputs/results.csv`
- CSV columns: stratum,r,p_value,ci_lower,ci_upper,n
- Two rows: factual stratum and misinformation stratum

---

## C-2: Fisher z-Test Implementation [Complexity: 14, Budget: 5]

**Applied:** scipy.stats Fisher z-transformation

### API Signatures

```python
class FisherZTest:
    def __init__(self, alpha: float = 0.05):
        """Initialize Fisher z-test analyzer."""
        self.alpha = alpha
    
    def fisher_z_transform(self, r: float) -> float:
        """Apply Fisher z-transformation. r: [-1, 1] -> z: (-inf, inf)"""
        ...
    
    def compute_z_statistic(
        self,
        r1: float,
        n1: int,
        r2: float,
        n2: int
    ) -> tuple[float, float]:
        """Compute test statistic and standard error.
        
        Returns:
            (z_stat, se_diff)
        """
        ...
    
    def compare_correlations(
        self,
        r1: float,
        n1: int,
        r2: float,
        n2: int
    ) -> dict:
        """Compare two independent correlations using Fisher z-test.
        
        Args:
            r1: Correlation coefficient for group 1 (factual)
            n1: Sample size for group 1
            r2: Correlation coefficient for group 2 (misinformation)
            n2: Sample size for group 2
        
        Returns:
            {
                "z_stat": float,
                "p_value": float,
                "se_diff": float,
                "z1": float,
                "z2": float,
                "significant": bool
            }
        """
        ...
```

### Pseudo-code

```
1. fisher_z_transform(r):
   a. return np.arctanh(r)  # 0.5 * ln((1+r)/(1-r))

2. compute_z_statistic(r1, n1, r2, n2):
   a. z1 = np.arctanh(r1)
   b. z2 = np.arctanh(r2)
   c. se_diff = sqrt(1/(n1-3) + 1/(n2-3))
   d. z_stat = (z1 - z2) / se_diff
   e. return (z_stat, se_diff)

3. compare_correlations(r1, n1, r2, n2):
   a. z_stat, se_diff = compute_z_statistic(r1, n1, r2, n2)
   b. from scipy.stats import norm
   c. p_value = 2 * (1 - norm.cdf(abs(z_stat)))  # Two-tailed
   d. significant = p_value < self.alpha
   e. return {
        "z_stat": z_stat,
        "p_value": p_value,
        "se_diff": se_diff,
        "z1": np.arctanh(r1),
        "z2": np.arctanh(r2),
        "significant": significant
      }
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Fisher Transform | Implement arctanh transformation |
| L-2-2 | Standard Error | Compute SE for correlation difference |
| L-2-3 | Test Statistic | Calculate z-statistic |
| L-2-4 | P-value Computation | Two-tailed p-value from standard normal |
| L-2-5 | Result Aggregation | Package results into dict |

---

## C-3: Confidence Interval Computation [Complexity: 9, Budget: 3]

**Applied:** Fisher z back-transformation

### API Signatures

```python
class ConfidenceIntervalCalculator:
    def __init__(self, confidence: float = 0.95):
        """Initialize CI calculator."""
        self.confidence = confidence
        self.z_critical = 1.96  # For 95% CI
    
    def compute_ci_fisher_z(
        self,
        r: float,
        n: int,
        confidence: float = None
    ) -> tuple[float, float]:
        """Compute CI using Fisher z-transformation.
        
        Args:
            r: Correlation coefficient
            n: Sample size
            confidence: Confidence level (default: self.confidence)
        
        Returns:
            (ci_lower, ci_upper) in correlation space
        """
        ...
    
    def back_transform_ci(self, z_ci_lower: float, z_ci_upper: float) -> tuple[float, float]:
        """Back-transform CI from z-space to correlation space.
        
        Returns:
            (r_ci_lower, r_ci_upper)
        """
        ...
```

### Pseudo-code

```
1. compute_ci_fisher_z(r, n, confidence):
   a. z = np.arctanh(r)
   b. se = 1 / sqrt(n - 3)
   c. z_crit = 1.96 if confidence == 0.95 else norm.ppf((1 + confidence) / 2)
   d. z_ci_lower = z - z_crit * se
   e. z_ci_upper = z + z_crit * se
   f. r_ci_lower = np.tanh(z_ci_lower)
   g. r_ci_upper = np.tanh(z_ci_upper)
   h. return (r_ci_lower, r_ci_upper)

2. back_transform_ci(z_ci_lower, z_ci_upper):
   a. return (np.tanh(z_ci_lower), np.tanh(z_ci_upper))
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Z-space CI | Compute CI in Fisher z-space |
| L-3-2 | Back-transform | Apply tanh to get correlation CI |
| L-3-3 | Dual Stratum | Apply to both factual and misinfo |

---

## C-5: Gate Validation Logic [Complexity: 10, Budget: 4]

**Applied:** SHOULD_WORK gate criteria validation

### API Signatures

```python
class MechanismGateValidator:
    def __init__(
        self,
        p_threshold: float = 0.05,
        delta_r_threshold: float = 0.1
    ):
        """Initialize gate validator."""
        self.p_threshold = p_threshold
        self.delta_r_threshold = delta_r_threshold
    
    def validate_primary_criterion(self, fisher_result: dict) -> bool:
        """Fisher z-test p < 0.05. Returns: True if passed"""
        ...
    
    def validate_secondary_criterion(self, r_factual: float, r_misinfo: float) -> bool:
        """|r_factual - r_misinfo| >= 0.1. Returns: True if passed"""
        ...
    
    def validate_tertiary_criterion(self, r_factual: float, r_misinfo: float) -> bool:
        """r_factual > 0.4 AND r_misinfo < 0.3. Returns: True if passed"""
        ...
    
    def evaluate_gate(
        self,
        fisher_result: dict,
        r_factual: float,
        r_misinfo: float
    ) -> dict:
        """Evaluate SHOULD_WORK gate.
        
        Returns:
            {
                "passed": bool,
                "gate_type": "SHOULD_WORK",
                "primary": bool,
                "secondary": bool,
                "tertiary": bool,
                "p_value": float,
                "delta_r": float
            }
        """
        ...
```

### Pseudo-code

```
1. validate_primary_criterion(fisher_result):
   a. return fisher_result["p_value"] < self.p_threshold

2. validate_secondary_criterion(r_factual, r_misinfo):
   a. delta_r = abs(r_factual - r_misinfo)
   b. return delta_r >= self.delta_r_threshold

3. validate_tertiary_criterion(r_factual, r_misinfo):
   a. return (r_factual > 0.4) and (r_misinfo < 0.3)

4. evaluate_gate(fisher_result, r_factual, r_misinfo):
   a. primary = validate_primary_criterion(fisher_result)
   b. secondary = validate_secondary_criterion(r_factual, r_misinfo)
   c. tertiary = validate_tertiary_criterion(r_factual, r_misinfo)
   d. passed = primary and secondary and tertiary
   e. return {
        "passed": passed,
        "gate_type": "SHOULD_WORK",
        "primary": primary,
        "secondary": secondary,
        "tertiary": tertiary,
        "p_value": fisher_result["p_value"],
        "delta_r": abs(r_factual - r_misinfo)
      }
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Primary Check | Fisher p < 0.05 validation |
| L-5-2 | Secondary Check | Delta r >= 0.1 validation |
| L-5-3 | Tertiary Check | Directional pattern validation |
| L-5-4 | Gate Aggregation | Combine all criteria |

---

## C-6: Visualization Suite [Complexity: 13, Budget: 3]

**Applied:** matplotlib/seaborn publication-quality figures

### API Signatures

```python
class ComparisonVisualizer:
    def __init__(self, output_dir: str):
        """Initialize visualizer."""
        self.output_dir = output_dir
    
    def plot_gate_metrics_comparison(
        self,
        fisher_result: dict,
        target_p: float = 0.05
    ) -> None:
        """MANDATORY: Bar chart comparing observed p-value vs threshold."""
        ...
    
    def plot_forest_plot(
        self,
        r_factual: float,
        r_misinfo: float,
        ci_factual: tuple[float, float],
        ci_misinfo: tuple[float, float],
        n_factual: int,
        n_misinfo: int
    ) -> None:
        """Forest plot with correlation coefficients and 95% CI error bars."""
        ...
    
    def plot_scatter_comparison(self, results_df: pd.DataFrame) -> None:
        """Side-by-side scatter plots of reliability vs robustness per stratum.
        
        Args:
            results_df: DataFrame with columns [stratum, reliability, robustness]
        """
        ...
    
    def generate_all_figures(self, results: dict) -> None:
        """Generate all 3 figures.
        
        Args:
            results: {
                "fisher": dict,
                "factual": {"r": float, "ci": tuple, "n": int},
                "misinfo": {"r": float, "ci": tuple, "n": int},
                "gate": dict
            }
        """
        ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Gate Metrics Chart | Bar chart with p-value vs threshold |
| L-6-2 | Forest Plot | Correlation comparison with CI error bars |
| L-6-3 | Scatter Plots | Side-by-side reliability vs robustness |

---

## Configuration Schema

```python
from dataclasses import dataclass, field

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
    h_m1_output_path: str = field(default_factory=lambda: 
        "docs/youra_research/h-m1/code/outputs/results.csv"
    )
    output_dir: str = "outputs"
    figures_dir: str = "figures"
    fisher: FisherTestConfig = field(default_factory=FisherTestConfig)
    gate: GateConfig = field(default_factory=GateConfig)

def load_config() -> ExperimentConfig:
    """Load configuration from environment or defaults."""
    config = ExperimentConfig()
    os.makedirs(config.output_dir, exist_ok=True)
    os.makedirs(config.figures_dir, exist_ok=True)
    return config
```

---

## Main Orchestration Logic

```python
def main():
    """Main experiment execution for h-m3."""
    print("H-M3: Stratified Correlation Comparison")
    print("="*80)
    
    config = load_config()
    
    # Load cached correlation results from H-M1
    loader = CachedResultsLoader(config.h_m1_output_path)
    results_df = loader.load_correlation_results()
    
    # Verify data format
    if not loader.validate_cached_data(results_df):
        raise ValueError("Invalid H-M1 cached data format")
    
    # Extract per-stratum correlations
    factual_corr = loader.get_factual_correlation(results_df)
    misinfo_corr = loader.get_misinfo_correlation(results_df)
    
    print(f"\nFactual stratum: r={factual_corr['r']:.4f}, n={factual_corr['n']}")
    print(f"Misinfo stratum: r={misinfo_corr['r']:.4f}, n={misinfo_corr['n']}")
    
    # Fisher z-test comparison
    fisher_test = FisherZTest(alpha=config.fisher.alpha)
    fisher_result = fisher_test.compare_correlations(
        r1=factual_corr["r"],
        n1=factual_corr["n"],
        r2=misinfo_corr["r"],
        n2=misinfo_corr["n"]
    )
    
    print(f"\nFisher z-test:")
    print(f"  z-statistic: {fisher_result['z_stat']:.4f}")
    print(f"  p-value: {fisher_result['p_value']:.6f}")
    print(f"  Significant: {fisher_result['significant']}")
    
    # Compute confidence intervals
    ci_calc = ConfidenceIntervalCalculator(confidence=config.fisher.confidence_level)
    ci_factual = ci_calc.compute_ci_fisher_z(factual_corr["r"], factual_corr["n"])
    ci_misinfo = ci_calc.compute_ci_fisher_z(misinfo_corr["r"], misinfo_corr["n"])
    
    print(f"\n95% Confidence Intervals:")
    print(f"  Factual: [{ci_factual[0]:.4f}, {ci_factual[1]:.4f}]")
    print(f"  Misinfo: [{ci_misinfo[0]:.4f}, {ci_misinfo[1]:.4f}]")
    
    # Compute effect size
    effect_size = fisher_test.compute_effect_size(factual_corr["r"], misinfo_corr["r"])
    print(f"\nEffect size (Cohen's q): {effect_size['cohens_q']:.4f}")
    
    # Gate validation
    validator = MechanismGateValidator(
        p_threshold=config.fisher.p_threshold,
        delta_r_threshold=config.fisher.delta_r_threshold
    )
    gate_result = validator.evaluate_gate(
        fisher_result,
        factual_corr["r"],
        misinfo_corr["r"]
    )
    
    print("\n" + "="*80)
    print("SHOULD_WORK GATE EVALUATION")
    print("="*80)
    print(f"Primary (p < 0.05): {gate_result['primary']}")
    print(f"Secondary (|Δr| >= 0.1): {gate_result['secondary']}")
    print(f"Tertiary (directional): {gate_result['tertiary']}")
    print(f"Gate result: {'PASS' if gate_result['passed'] else 'FAIL'}")
    print("="*80)
    
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

## Data Loading Module

```python
class CachedResultsLoader:
    def __init__(self, h_m1_output_path: str):
        """Initialize cached results loader.
        
        Args:
            h_m1_output_path: Path to h-m1/code/outputs/results.csv
        """
        self.output_path = Path(h_m1_output_path)
    
    def load_correlation_results(self) -> pd.DataFrame:
        """Load cached correlation results from H-M1.
        
        Returns:
            DataFrame with columns [stratum, r, p_value, ci_lower, ci_upper, n]
        """
        ...
    
    def validate_cached_data(self, df: pd.DataFrame) -> bool:
        """Validate cached data format and contents.
        
        Returns:
            True if data has 2 rows (factual, misinformation) with valid columns
        """
        ...
    
    def get_factual_correlation(self, df: pd.DataFrame) -> dict:
        """Extract factual stratum correlation.
        
        Returns:
            {"r": float, "p_value": float, "ci_lower": float, "ci_upper": float, "n": int}
        """
        ...
    
    def get_misinfo_correlation(self, df: pd.DataFrame) -> dict:
        """Extract misinformation stratum correlation.
        
        Returns:
            {"r": float, "p_value": float, "ci_lower": float, "ci_upper": float, "n": int}
        """
        ...
```

---

## Effect Size Calculation

```python
class EffectSizeCalculator:
    def compute_cohens_q(self, r1: float, r2: float) -> dict:
        """Compute Cohen's q effect size for correlation difference.
        
        Args:
            r1: Correlation coefficient 1 (factual)
            r2: Correlation coefficient 2 (misinformation)
        
        Returns:
            {
                "cohens_q": float,
                "z1": float,
                "z2": float,
                "magnitude": str  # "small", "medium", "large"
            }
        """
        # Cohen's q = |z1 - z2|
        z1 = np.arctanh(r1)
        z2 = np.arctanh(r2)
        cohens_q = abs(z1 - z2)
        
        # Effect size classification
        if cohens_q < 0.1:
            magnitude = "small"
        elif cohens_q < 0.3:
            magnitude = "medium"
        else:
            magnitude = "large"
        
        return {
            "cohens_q": float(cohens_q),
            "z1": float(z1),
            "z2": float(z2),
            "magnitude": magnitude
        }
```

---

## Report Generation

```python
class ValidationReportGenerator:
    def __init__(self, output_path: str):
        """Initialize report generator."""
        self.output_path = Path(output_path)
    
    def generate_report(
        self,
        fisher_result: dict,
        gate_result: dict,
        correlations: dict
    ) -> None:
        """Generate 04_validation.md report.
        
        Args:
            fisher_result: Fisher z-test results
            gate_result: Gate evaluation results
            correlations: {"factual": dict, "misinfo": dict}
        """
        ...
    
    def format_statistics_table(self, fisher_result: dict) -> str:
        """Format Fisher z-test statistics as markdown table."""
        ...
    
    def format_gate_evaluation(self, gate_result: dict) -> str:
        """Format gate evaluation as markdown section."""
        ...
    
    def save_results_json(self, results: dict, output_path: str) -> None:
        """Save results to JSON file."""
        ...
```

---

## Implementation Notes

### Critical Success Factors

1. **Load H-M1 cached results correctly**: Verify CSV format matches expected schema
2. **Fisher z-transform accuracy**: Use `np.arctanh()` for transformation, `np.tanh()` for back-transform
3. **Two-tailed p-value**: Use `2 * (1 - norm.cdf(abs(z_stat)))` for significance test
4. **Gate validation**: All three criteria must pass for SHOULD_WORK gate

### Error Handling Priorities

1. **Missing H-M1 results**: Fail fast with clear error message if results.csv not found
2. **Invalid data format**: Validate CSV has exactly 2 rows with correct columns
3. **Edge cases**: Handle r=1 or r=-1 (Fisher z-transform approaches infinity)

### Expected Outputs

- `fisher_test_results.json`: Full Fisher z-test results
- `correlation_results.json`: Per-stratum correlations with CIs
- `04_validation.md`: Gate evaluation report
- `figures/gate_metrics_comparison.png`: MANDATORY gate visualization
- `figures/forest_plot.png`: Correlation comparison with error bars
- `figures/scatter_comparison.png`: Side-by-side reliability vs robustness

---

**Document Status:** FINAL
**Last Updated:** 2026-07-12
**Next Phase:** Phase 4 - Implementation (Coder Agent)
**Subtask Budget Used:** 15/15 (C-2:5, C-3:3, C-5:4, C-6:3)
