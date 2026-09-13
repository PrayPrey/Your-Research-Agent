# Logic Design: Combined Contract Validation Framework

**Hypothesis ID:** h-c1  
**Document Type:** Logic Specification  
**Date:** 2026-07-11  
**Tier:** LIGHT (reuse h-m1/h-m2 validators)

**Applied:** ThreadPoolExecutor patterns, scipy.stats.mcnemar, bootstrap resampling

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (h-m1, h-m2, h-e1)  
**Status:** API signatures verified from actual code  
**Analyzed Paths:**
- `docs/youra_research/h-m1/code/contracts/validator.py`
- `docs/youra_research/h-m2/code/contracts/metamorphic.py`
- `docs/youra_research/h-e1/data/defect_corpus.csv`

**Relevant Symbols:**
- `validate_structural` (decorator, h-m1)
- `validate_metamorphic` (decorator, h-m2)
- `MetamorphicValidator` (static methods, h-m2)
- `ContractViolationError`, `ShapeViolation`, `DtypeViolation`, `DeviceViolation` (h-m1)
- `MetamorphicViolation`, `SoftmaxSumViolation`, `DropoutIdentityViolation` (h-m2)

---

## External Dependencies (Base Hypotheses)

### API Signatures (From Actual Code)

The following APIs are called from base hypotheses. Signatures verified from actual implementation:

```python
# From: docs/youra_research/h-m1/code/contracts/validator.py (ACTUAL CODE)
def validate_structural(
    input_shapes: Dict[str, Tuple[int, ...]] = None,
    output_shape: Tuple[int, ...] = None,
    device: str = None,
    dtype: torch.dtype = None
) -> Callable:
    """Decorator for structural contract validation. Returns decorator function."""
    ...

class ContractViolationError(Exception):
    """Base exception for contract violations"""
    pass

class ShapeViolation(ContractViolationError):
    """Raised when tensor shape doesn't match specification"""
    pass

class DeviceViolation(ContractViolationError):
    """Raised when tensor device doesn't match specification"""
    pass

class DtypeViolation(ContractViolationError):
    """Raised when tensor dtype doesn't match specification"""
    pass

# From: docs/youra_research/h-m2/code/contracts/metamorphic.py (ACTUAL CODE)
class MetamorphicValidator:
    @staticmethod
    def validate_softmax(
        func: Callable,
        probe_input: torch.Tensor,
        dim: int = -1,
        rtol: float = 1e-5,
        atol: float = 1e-7
    ) -> bool:
        """Validate softmax sum=1.0 property. Raises SoftmaxSumViolation if violated."""
        ...

    @staticmethod
    def validate_dropout_identity(
        module: torch.nn.Module,
        probe_input: torch.Tensor,
        eval_mode: bool = True
    ) -> bool:
        """Validate dropout identity in eval mode. Raises DropoutIdentityViolation if violated."""
        ...

class MetamorphicViolation(ContractViolationError):
    """Base exception for metamorphic property violations"""
    pass

class SoftmaxSumViolation(MetamorphicViolation):
    """Raised when softmax sum property violated"""
    def __init__(self, message: str, actual_sum: float, tolerance: Dict[str, float]):
        ...

class DropoutIdentityViolation(MetamorphicViolation):
    """Raised when dropout identity property violated"""
    pass

def validate_metamorphic(
    softmax: bool = False,
    dropout_identity: bool = False,
    dim: int = -1,
    rtol: float = 1e-5,
    atol: float = 1e-7,
    probe_size: int = 100
) -> Callable:
    """Decorator for metamorphic property validation. Returns decorator function."""
    ...
```

**Verified from:** Actual implementations in h-m1/h-m2 code directories (NOT specs)

**Integration Strategy:**
- Import validators as-is via decorators
- Wrap defect code snippets in test functions
- Catch exception types to detect violations
- No modifications to base validators

---

## C-1: Corpus Loader [Complexity: 4, Budget: 4]

**Applied:** pandas CSV reader, stratified sampling

### API Signatures

```python
from dataclasses import dataclass
from typing import List, Dict
import pandas as pd

@dataclass
class DefectRecord:
    """Single defect from corpus."""
    defect_id: str
    defect_type: str  # "structural" | "behavioral" | "mixed" | "composition"
    description: str
    api_name: str
    source_project: str
    stage: str
    invariant: str
    structural_detectable: bool  # Inferred from type if missing
    metamorphic_detectable: bool  # Inferred from type if missing

class CorpusLoader:
    def __init__(self, corpus_path: str):
        """Load corpus CSV."""
        ...

    def load(self, stratify_by: str = "defect_type") -> List[DefectRecord]:
        """Load and stratify corpus. Returns: List of DefectRecord."""
        ...

    def get_stratification_summary(self) -> Dict[str, int]:
        """Get defect counts by type. Returns: {type: count}."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| defects | [348] | List of DefectRecord objects |
| stratification | {str: int} | Dict of type counts |

### Pseudo-code

```
1. Read CSV: df = pd.read_csv(corpus_path)
2. Validate schema: assert columns include [defect_id, type, description, api_name]
3. Infer ground truth if missing:
   - structural_detectable = True if type in {"structural", "mixed"}
   - metamorphic_detectable = True if type in {"behavioral", "mixed"}
4. Convert to DefectRecord objects
5. Sort by defect_type for stratification
6. Return records
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | CSV Reader | Load CSV with pandas, validate schema |
| L-1-2 | Ground Truth Inference | Infer detectability from type column |
| L-1-3 | Stratification | Group by defect_type, return summary |
| L-1-4 | Unit Tests | Test stratification logic, schema validation |

---

## C-2: Ensemble Validator [Complexity: 8, Budget: 8]

**Applied:** ThreadPoolExecutor timeout patterns, deep copy for state isolation

### API Signatures

```python
from concurrent.futures import ThreadPoolExecutor, TimeoutError, Future
from typing import Callable, List, Optional
import copy
import time

@dataclass
class Violation:
    """Validation violation result."""
    source: str  # "structural" | "metamorphic" | "both"
    message: str
    timestamp: float
    defect_id: str

class EnsembleValidator:
    def __init__(
        self,
        structural_validator: Callable,
        metamorphic_validator: Callable,
        timeout: float = 10.0,
        workers: int = 4
    ):
        """Initialize ensemble validator."""
        ...

    def validate_combined(
        self,
        defect_code: str,
        defect_id: str
    ) -> List[Violation]:
        """
        Run both validators in parallel.
        
        Args:
            defect_code: Python code with defect
            defect_id: Defect identifier
        
        Returns: List of violations (deduplicated)
        """
        ...

    def _run_validator(
        self,
        validator_func: Callable,
        defect_code: str,
        defect_id: str
    ) -> List[Violation]:
        """Execute single validator. Returns: violations or [] if timeout."""
        ...

    def _deduplicate_violations(
        self,
        structural: List[Violation],
        metamorphic: List[Violation]
    ) -> List[Violation]:
        """Merge violations by message similarity. Returns: deduplicated list."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| structural_violations | [K1] | List of Violation objects |
| metamorphic_violations | [K2] | List of Violation objects |
| combined_violations | [≤K1+K2] | Deduplicated violations |

### Pseudo-code

```
validate_combined(defect_code, defect_id):
    1. Initialize executor = ThreadPoolExecutor(max_workers=2)
    2. Submit parallel tasks:
       - future_s = executor.submit(_run_validator, structural_validator, defect_code, defect_id)
       - future_m = executor.submit(_run_validator, metamorphic_validator, defect_code, defect_id)
    3. Wait with timeout:
       - Try: violations_s = future_s.result(timeout=10.0)
       - Catch TimeoutError: violations_s = []
       - Try: violations_m = future_m.result(timeout=10.0)
       - Catch TimeoutError: violations_m = []
    4. Deduplicate: combined = _deduplicate_violations(violations_s, violations_m)
    5. Return combined

_run_validator(validator_func, defect_code, defect_id):
    1. Wrap defect code in test function
    2. Try:
       - exec(defect_code_with_validator)
       - return []  # No violation
    3. Catch ContractViolationError as e:
       - return [Violation(source=validator_type, message=str(e), timestamp=time.time(), defect_id=defect_id)]
    4. Catch Exception:
       - return []  # Not a contract violation

_deduplicate_violations(structural, metamorphic):
    1. Build hash map: {message_hash: Violation}
    2. For v in structural:
       - hash = v.message[:50]  # First 50 chars
       - map[hash] = v
    3. For v in metamorphic:
       - hash = v.message[:50]
       - If hash in map:
           - map[hash].source = "both"  # Mark as detected by both
       - Else:
           - map[hash] = v
    4. Return list(map.values())
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | ThreadPool Setup | Configure executor with timeout |
| L-2-2 | Validator Wrapper | Wrap defect code execution |
| L-2-3 | Timeout Handling | Catch TimeoutError, return empty list |
| L-2-4 | Exception Catching | Detect ContractViolationError types |
| L-2-5 | Deduplication Logic | Hash-based message matching |
| L-2-6 | Source Labeling | Mark violations as structural/metamorphic/both |
| L-2-7 | Integration Test | Test parallel execution with known defects |
| L-2-8 | Timeout Test | Verify timeout enforcement with slow validator |

---

## C-3: Experiment Runner [Complexity: 7, Budget: 7]

**Applied:** Three-strategy loop pattern, CSV output with pandas

### API Signatures

```python
from typing import Dict, List
import pandas as pd
import time

@dataclass
class StrategyResults:
    """Results for single strategy."""
    strategy: str
    fnr: float
    detection_rate: float
    execution_time_mean: float
    per_defect_results: List[Dict]

class ExperimentRunner:
    def __init__(
        self,
        corpus_loader: CorpusLoader,
        ensemble_validator: EnsembleValidator,
        timeout: float = 10.0
    ):
        """Initialize experiment runner."""
        ...

    def run_three_strategy(
        self,
        strategies: List[str] = ["structural", "metamorphic", "combined"]
    ) -> Dict[str, StrategyResults]:
        """
        Run experiment for all three strategies.
        
        Returns: {strategy_name: StrategyResults}
        """
        ...

    def _run_single_strategy(
        self,
        strategy: str,
        defects: List[DefectRecord]
    ) -> StrategyResults:
        """Execute single strategy. Returns: StrategyResults object."""
        ...

    def save_results(self, output_path: str) -> None:
        """Save results to CSV. Schema: defect_id, strategy, detected, execution_time."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| defects | [348] | List of DefectRecord |
| results | [1044] | 348 defects × 3 strategies |
| per_strategy | [348] | Results for one strategy |

### Pseudo-code

```
run_three_strategy(strategies):
    1. Load defects: defects = corpus_loader.load()
    2. Initialize results: results = {}
    3. For strategy in strategies:
       - results[strategy] = _run_single_strategy(strategy, defects)
    4. Return results

_run_single_strategy(strategy, defects):
    1. Initialize: per_defect_results = []
    2. For defect in defects:
       - start_time = time.time()
       - If strategy == "structural":
           - violations = _run_structural_only(defect)
       - Elif strategy == "metamorphic":
           - violations = _run_metamorphic_only(defect)
       - Elif strategy == "combined":
           - violations = ensemble_validator.validate_combined(defect.code, defect.defect_id)
       - execution_time = time.time() - start_time
       - detected = len(violations) > 0
       - per_defect_results.append({
           "defect_id": defect.defect_id,
           "strategy": strategy,
           "detected": detected,
           "execution_time": execution_time,
           "violation_source": violations[0].source if violations else None
         })
    3. Compute FNR: See C-4 logic
    4. Return StrategyResults(...)

save_results(output_path):
    1. Flatten per_defect_results from all strategies
    2. Create DataFrame: df = pd.DataFrame(all_results)
    3. Write: df.to_csv(output_path, index=False)
```

### Subtasks [7/7 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Strategy Loop | Iterate over three strategies |
| L-3-2 | Structural-Only Runner | Wrap h-m1 validator for standalone execution |
| L-3-3 | Metamorphic-Only Runner | Wrap h-m2 validator for standalone execution |
| L-3-4 | Combined Runner | Call ensemble validator |
| L-3-5 | Result Recording | Build per-defect result dictionaries |
| L-3-6 | CSV Output | Save results with pandas |
| L-3-7 | Integration Test | Run on 10-defect subset, verify schema |

---

## C-4: Statistical Analyzer [Complexity: 6, Budget: 6]

**Applied:** scipy.stats.mcnemar, bootstrap resampling

### API Signatures

```python
from scipy.stats import mcnemar
import numpy as np
from typing import Tuple, List, Set

class StatisticalAnalyzer:
    @staticmethod
    def calculate_fnr(
        detected: Set[str],
        ground_truth_detectable: Set[str]
    ) -> Tuple[float, Tuple[float, float]]:
        """
        Calculate FNR with bootstrap 95% CI.
        
        Args:
            detected: Set of defect IDs detected
            ground_truth_detectable: Set of defect IDs that should be detected
        
        Returns: (fnr, (ci_lower, ci_upper))
        """
        ...

    @staticmethod
    def bootstrap_ci(
        data: List[bool],
        n_iterations: int = 1000,
        seed: int = 42
    ) -> Tuple[float, float]:
        """Bootstrap confidence interval for proportion. Returns: (ci_lower, ci_upper)."""
        ...

    @staticmethod
    def mcnemar_test(
        strategy_a_results: List[bool],
        strategy_b_results: List[bool]
    ) -> Tuple[float, bool]:
        """
        McNemar test for paired proportions.
        
        Args:
            strategy_a_results: Detection results (True/False) for strategy A
            strategy_b_results: Detection results (True/False) for strategy B
        
        Returns: (p_value, is_significant)
        """
        ...

    @staticmethod
    def calculate_reduction(
        baseline_fnr: float,
        combined_fnr: float
    ) -> float:
        """Calculate FNR reduction percentage. Returns: (baseline - combined) / baseline."""
        ...
```

### Pseudo-code

```
calculate_fnr(detected, ground_truth_detectable):
    1. missed = ground_truth_detectable - detected
    2. fnr = len(missed) / len(ground_truth_detectable)
    3. If len(ground_truth_detectable) == 0: return (NaN, (NaN, NaN))
    4. Create binary array: results = [d in detected for d in ground_truth_detectable]
    5. ci = bootstrap_ci(results, n_iterations=1000, seed=42)
    6. Return (fnr, ci)

bootstrap_ci(data, n_iterations, seed):
    1. np.random.seed(seed)
    2. n = len(data)
    3. fnr_samples = []
    4. For i in range(n_iterations):
       - sample = np.random.choice(data, size=n, replace=True)
       - fnr_sample = 1 - sum(sample) / n  # FNR = 1 - detection_rate
       - fnr_samples.append(fnr_sample)
    5. ci_lower = np.percentile(fnr_samples, 2.5)
    6. ci_upper = np.percentile(fnr_samples, 97.5)
    7. Return (ci_lower, ci_upper)

mcnemar_test(strategy_a_results, strategy_b_results):
    1. Build contingency table:
       - b = sum(a=True, b=False)  # A detects, B misses
       - c = sum(a=False, b=True)  # A misses, B detects
    2. If b + c < 25: use exact McNemar test
    3. result = mcnemar([[0, b], [c, 0]], exact=(b+c < 25))
    4. p_value = result.pvalue
    5. is_significant = p_value < 0.05
    6. Return (p_value, is_significant)

calculate_reduction(baseline_fnr, combined_fnr):
    1. If baseline_fnr == 0: return NaN
    2. reduction = (baseline_fnr - combined_fnr) / baseline_fnr
    3. Return reduction
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | FNR Calculation | Implement formula: missed / detectable |
| L-4-2 | Bootstrap CI | Resample and compute percentiles |
| L-4-3 | McNemar Test | scipy.stats.mcnemar wrapper |
| L-4-4 | Reduction Calculation | Percentage reduction formula |
| L-4-5 | Edge Cases | Handle zero division, empty sets |
| L-4-6 | Unit Tests | Verify formulas with known data |

---

## C-5: Visualizer [Complexity: 5, Budget: 5]

**Applied:** matplotlib bar charts, error bars for CI

### API Signatures

```python
import matplotlib.pyplot as plt
from typing import Dict

class Visualizer:
    def __init__(self, output_dir: str):
        """Initialize visualizer with output directory."""
        ...

    def plot_fnr_comparison(
        self,
        results: Dict[str, StrategyResults],
        threshold: float = 0.30
    ) -> str:
        """
        Bar chart of FNR by strategy with 95% CI error bars.
        
        Returns: Path to saved PNG
        """
        ...

    def plot_coverage_by_type(
        self,
        results: Dict[str, StrategyResults],
        defects: List[DefectRecord]
    ) -> str:
        """
        Stacked bar chart: Detection rate by defect type.
        
        Returns: Path to saved PNG
        """
        ...

    def plot_execution_time(
        self,
        results: Dict[str, StrategyResults]
    ) -> str:
        """
        Box plot: Execution time distribution by strategy.
        
        Returns: Path to saved PNG
        """
        ...
```

### Pseudo-code

```
plot_fnr_comparison(results, threshold):
    1. Extract FNR and CI for each strategy
    2. Create bar chart: plt.bar(strategies, fnr_values, yerr=ci_widths)
    3. Add horizontal line at threshold: plt.axhline(y=threshold, linestyle='--', label='30% threshold')
    4. Set labels: xlabel='Strategy', ylabel='False Negative Rate'
    5. Save: plt.savefig(f'{output_dir}/fnr_comparison.png', dpi=300)
    6. Return file path

plot_coverage_by_type(results, defects):
    1. Group defects by type: {structural: [...], behavioral: [...], mixed: [...], composition: [...]}
    2. For each strategy:
       - Compute detection rate per type
    3. Create stacked bar chart: plt.bar(strategies, detection_rates_by_type, stacked=True)
    4. Legend: defect types
    5. Save: plt.savefig(f'{output_dir}/coverage_by_type.png', dpi=300)
    6. Return file path

plot_execution_time(results):
    1. Extract execution times per strategy
    2. Create box plot: plt.boxplot([times_structural, times_metamorphic, times_combined])
    3. Set labels: strategies
    4. Add horizontal line at 10s timeout
    5. Save: plt.savefig(f'{output_dir}/execution_time.png', dpi=300)
    6. Return file path
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | FNR Bar Chart | Bar chart with error bars |
| L-5-2 | Coverage Stacked Bar | Detection rate by defect type |
| L-5-3 | Execution Time Box Plot | Distribution of execution times |
| L-5-4 | Styling | Consistent colors, labels, DPI=300 |
| L-5-5 | File Output | Save as PNG to output_dir |

---

## C-6: Integration Script [Complexity: 5, Budget: 5]

**Applied:** YAML config parsing, logging

### API Signatures

```python
import yaml
import logging
from pathlib import Path

def load_config(config_path: str) -> Dict:
    """Load config.yaml. Returns: config dict."""
    ...

def setup_logging(log_level: str = "INFO") -> None:
    """Configure logging to console and file."""
    ...

def main() -> None:
    """Main orchestrator for experiment."""
    ...
```

### Pseudo-code

```
main():
    1. Load config: config = load_config("config.yaml")
    2. Setup logging: setup_logging(config["logging"]["level"])
    3. Load corpus:
       - loader = CorpusLoader(config["corpus"]["path"])
       - defects = loader.load(stratify_by=config["corpus"]["stratify_by"])
    4. Setup validators:
       - ensemble = EnsembleValidator(
           structural_validator=validate_structural,
           metamorphic_validator=validate_metamorphic,
           timeout=config["validation"]["timeout"],
           workers=config["validation"]["parallel_workers"]
         )
    5. Run experiment:
       - runner = ExperimentRunner(loader, ensemble, timeout=config["validation"]["timeout"])
       - results = runner.run_three_strategy(config["experiment"]["strategies"])
       - runner.save_results(config["experiment"]["output_path"])
    6. Analyze:
       - analyzer = StatisticalAnalyzer()
       - For each strategy:
           - fnr, ci = analyzer.calculate_fnr(...)
           - Log results
       - p_value_s = analyzer.mcnemar_test(combined_results, structural_results)
       - p_value_m = analyzer.mcnemar_test(combined_results, metamorphic_results)
       - reduction = analyzer.calculate_reduction(better_baseline_fnr, combined_fnr)
    7. Visualize:
       - viz = Visualizer(config["visualization"]["output_dir"])
       - viz.plot_fnr_comparison(results, threshold=config["visualization"]["fnr_threshold"])
       - viz.plot_coverage_by_type(results, defects)
       - viz.plot_execution_time(results)
    8. Report gate verdict:
       - If reduction >= 0.30 and p_value < 0.05:
           - print("GATE: PASS")
       - Else:
           - print("GATE: FAIL")
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Config Loading | YAML parsing with PyYAML |
| L-6-2 | Logging Setup | Console and file logger |
| L-6-3 | Module Wiring | Instantiate all components |
| L-6-4 | Error Handling | Try/catch with informative messages |
| L-6-5 | Gate Verdict | Print PASS/FAIL based on criteria |

---

## C-7: Validation Report Generation [Complexity: 9, Budget: 9]

**Applied:** Markdown generation, statistical reporting

### API Signatures

```python
from typing import Dict, List

class ValidationReportGenerator:
    def __init__(
        self,
        results: Dict[str, StrategyResults],
        defects: List[DefectRecord],
        output_path: str = "04_validation.md"
    ):
        """Initialize report generator."""
        ...

    def generate_report(self) -> None:
        """Generate 04_validation.md with all sections."""
        ...

    def _write_executive_summary(self) -> str:
        """Executive summary with gate verdict."""
        ...

    def _write_fnr_results(self) -> str:
        """FNR reduction table with 95% CI."""
        ...

    def _write_statistical_tests(self) -> str:
        """McNemar test results."""
        ...

    def _write_coverage_breakdown(self) -> str:
        """Detection rate by defect type."""
        ...

    def _write_execution_time_analysis(self) -> str:
        """Execution time statistics."""
        ...

    def _embed_visualizations(self) -> str:
        """Embed PNG plots in markdown."""
        ...
```

### Pseudo-code

```
generate_report():
    1. Open file: f = open(output_path, 'w')
    2. Write header: "# Validation Report: h-c1"
    3. Write executive summary: f.write(_write_executive_summary())
    4. Write FNR results: f.write(_write_fnr_results())
    5. Write statistical tests: f.write(_write_statistical_tests())
    6. Write coverage breakdown: f.write(_write_coverage_breakdown())
    7. Write execution time: f.write(_write_execution_time_analysis())
    8. Embed visualizations: f.write(_embed_visualizations())
    9. Close file

_write_executive_summary():
    1. Extract reduction percentage
    2. Extract p-value
    3. Determine gate verdict: PASS if reduction >= 30% and p < 0.05
    4. Return markdown section:
       """
       ## Executive Summary
       - **FNR Reduction:** {reduction:.1%}
       - **Statistical Significance:** p={p_value:.4f}
       - **Gate Verdict:** {verdict}
       """

_write_fnr_results():
    1. Build markdown table:
       | Strategy | FNR | 95% CI | Detection Rate |
       |----------|-----|--------|----------------|
       | Structural | {fnr_s:.3f} | [{ci_s_low:.3f}, {ci_s_high:.3f}] | {dr_s:.1%} |
       | Metamorphic | {fnr_m:.3f} | [{ci_m_low:.3f}, {ci_m_high:.3f}] | {dr_m:.1%} |
       | Combined | {fnr_c:.3f} | [{ci_c_low:.3f}, {ci_c_high:.3f}] | {dr_c:.1%} |
    2. Return markdown section

_write_statistical_tests():
    1. Build markdown table:
       | Comparison | p-value | Significant? |
       |------------|---------|--------------|
       | Combined vs Structural | {p_s:.4f} | {sig_s} |
       | Combined vs Metamorphic | {p_m:.4f} | {sig_m} |
    2. Return markdown section

_write_coverage_breakdown():
    1. Compute detection rate by defect type for each strategy
    2. Build markdown table:
       | Defect Type | Structural | Metamorphic | Combined |
       |-------------|------------|-------------|----------|
       | Structural-only | {rate_s_s:.1%} | {rate_s_m:.1%} | {rate_s_c:.1%} |
       | Behavioral-only | {rate_b_s:.1%} | {rate_b_m:.1%} | {rate_b_c:.1%} |
       | Mixed | {rate_m_s:.1%} | {rate_m_m:.1%} | {rate_m_c:.1%} |
       | Composition | {rate_c_s:.1%} | {rate_c_m:.1%} | {rate_c_c:.1%} |
    3. Return markdown section

_write_execution_time_analysis():
    1. Compute mean, median, 99th percentile for each strategy
    2. Build markdown table:
       | Strategy | Mean (s) | Median (s) | 99th %ile (s) |
       |----------|----------|------------|---------------|
       | Structural | {mean_s:.2f} | {med_s:.2f} | {p99_s:.2f} |
       | Metamorphic | {mean_m:.2f} | {med_m:.2f} | {p99_m:.2f} |
       | Combined | {mean_c:.2f} | {med_c:.2f} | {p99_c:.2f} |
    3. Return markdown section

_embed_visualizations():
    1. Return markdown image embeds:
       ![FNR Comparison](visualizations/fnr_comparison.png)
       ![Coverage by Type](visualizations/coverage_by_type.png)
       ![Execution Time](visualizations/execution_time.png)
```

### Subtasks [9/9 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Report Structure | Define markdown sections |
| L-7-2 | Executive Summary | Gate verdict, reduction percentage |
| L-7-3 | FNR Table | Build results table with CI |
| L-7-4 | Statistical Tests | McNemar test p-values |
| L-7-5 | Coverage Breakdown | Detection rate by defect type |
| L-7-6 | Execution Time Table | Mean, median, percentiles |
| L-7-7 | Visualization Embed | Markdown image links |
| L-7-8 | Markdown Generation | Write to 04_validation.md |
| L-7-9 | Documentation | Code docstrings for report functions |

---

## Edge Case Handling

### Timeout Scenarios

**Case 1: Validator hangs**
- Detection: ThreadPoolExecutor.result(timeout=10.0) raises TimeoutError
- Handling: Return empty violations list, record execution_time=10.0
- Recording: Flag defect as TIMEOUT in results CSV

**Case 2: All validators timeout**
- Detection: Both futures raise TimeoutError
- Handling: Return empty violations list for combined strategy
- Impact: FNR calculation excludes timeout defects (logged separately)

### Ground Truth Missing

**Case 1: Detectability columns missing in CSV**
- Detection: KeyError on column access
- Handling: Infer from defect type:
  - structural_detectable = type in {"structural", "mixed"}
  - metamorphic_detectable = type in {"behavioral", "mixed"}

**Case 2: Invalid defect type**
- Detection: Type not in {structural, behavioral, mixed, composition}
- Handling: Skip defect, log warning, continue experiment

### Statistical Edge Cases

**Case 1: Zero detectable defects**
- Detection: len(ground_truth_detectable) == 0
- Handling: Return FNR=NaN, CI=(NaN, NaN), log warning

**Case 2: McNemar test prerequisites not met**
- Detection: b + c < 10 (too few discordant pairs)
- Handling: Use exact=True parameter, report if still invalid

**Case 3: Perfect detection (FNR=0)**
- Detection: All defects detected
- Handling: FNR=0.0, CI=(0.0, 0.0), reduction may be undefined if baseline also 0

### Deduplication Edge Cases

**Case 1: Same message from both validators**
- Detection: Hash collision in first 50 chars
- Handling: Mark source="both", keep single violation

**Case 2: Similar but not identical messages**
- Detection: Different hashes
- Handling: Keep both violations (false negative acceptable for LIGHT tier)

---

## Validation Logic Flow

### Experiment Execution Flow

```
1. Load Phase
   ├─ Read defect_corpus.csv (348 rows)
   ├─ Infer ground truth labels if missing
   └─ Stratify by defect_type

2. Validation Phase (Per Strategy)
   For strategy in [structural, metamorphic, combined]:
     For defect in defects:
       ├─ Start timer
       ├─ Execute validator(s)
       │  ├─ If structural: Run h-m1 decorator
       │  ├─ If metamorphic: Run h-m2 decorator
       │  └─ If combined: ThreadPoolExecutor with both
       ├─ Catch ContractViolationError → detected=True
       ├─ Catch TimeoutError → detected=False, flag=TIMEOUT
       ├─ Record result: {defect_id, strategy, detected, execution_time}
       └─ Stop timer

3. Analysis Phase
   ├─ Compute FNR per strategy
   ├─ Bootstrap 95% CI (1000 iterations)
   ├─ McNemar test: Combined vs Structural
   ├─ McNemar test: Combined vs Metamorphic
   └─ Calculate reduction: (baseline_fnr - combined_fnr) / baseline_fnr

4. Visualization Phase
   ├─ FNR bar chart with error bars
   ├─ Coverage stacked bar by defect type
   └─ Execution time box plot

5. Reporting Phase
   ├─ Generate 04_validation.md
   ├─ Embed visualizations
   └─ Print gate verdict
```

### Validator Wrapper Logic

```
Structural-Only Execution:
    1. Import validate_structural from h-m1
    2. Wrap defect code:
       @validate_structural(input_shapes={'x': ('B', 3, 32, 32)}, output_shape=('B', 10))
       def defect_function(x):
           {defect_code}
           return x
    3. Execute: defect_function(torch.randn(1, 3, 32, 32))
    4. If ShapeViolation/DeviceViolation/DtypeViolation → detected=True
    5. Else → detected=False

Metamorphic-Only Execution:
    1. Import MetamorphicValidator from h-m2
    2. Parse defect code to identify operation (softmax, dropout, etc.)
    3. If softmax operation:
       - MetamorphicValidator.validate_softmax(func, probe_input)
    4. If dropout operation:
       - MetamorphicValidator.validate_dropout_identity(module, probe_input)
    5. If SoftmaxSumViolation/DropoutIdentityViolation → detected=True
    6. Else → detected=False

Combined Execution:
    1. ThreadPoolExecutor(max_workers=2)
    2. Future 1: Structural-only execution
    3. Future 2: Metamorphic-only execution
    4. Wait for both with timeout=10.0
    5. Aggregate violations from both
    6. Deduplicate by message hash
    7. Return combined violations
```

---

## Summary of Budget Allocation

| Task ID | Task Name | Complexity | Budget Used |
|---------|-----------|------------|-------------|
| C-1 | Corpus Loader | 4 | 4 |
| C-2 | Ensemble Validator | 8 | 8 |
| C-3 | Experiment Runner | 7 | 7 |
| C-4 | Statistical Analyzer | 6 | 6 |
| C-5 | Visualizer | 5 | 5 |
| C-6 | Integration Script | 5 | 5 |
| C-7 | Validation Report | 9 | 9 |
| **Total** | | **44** | **44** |

**Budget Status:** 44/44 used (100%)

---

**End of Logic Design**
