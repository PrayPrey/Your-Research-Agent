# Architecture Design: Combined Contract Validation Framework

**Hypothesis ID:** h-c1  
**Document Type:** Architecture Specification  
**Date:** 2026-07-11  
**Tier:** LIGHT (minimal new code, reuse h-m1/h-m2)

**Applied:** Parallel execution patterns, ensemble validation

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (h-m1, h-m2)  
**Status:** Patterns found from base code  
**Analyzed Path:** `docs/youra_research/h-m1/code/`, `docs/youra_research/h-m2/code/`  
**Findings:** Reusable validators in `contracts/validator.py`, exception types defined, decorator-based validation

---

## System Overview

Ensemble framework combining h-m1 (structural) and h-m2 (metamorphic) validators to detect API contract violations across 348-defect corpus.

**Architecture Pattern:** Parallel validator orchestration with defect corpus loader and statistical analyzer.

**Core Components:**
- Defect corpus loader (stratified CSV reader)
- Ensemble validator (parallel execution wrapper)
- Experiment runner (three-strategy comparison)
- Statistical analyzer (FNR calculation, McNemar test)
- Visualization generator (plots)

---

## Module Specifications

### 1. CorpusLoader (`data/corpus_loader.py`)

**Dependencies:** pandas, h-e1 corpus CSV

```python
class CorpusLoader:
    def __init__(self, corpus_path: str): ...
    def load(self, stratify_by: str = "type") -> list[DefectRecord]: ...
    def get_stratification_summary(self) -> dict[str, int]: ...

class DefectRecord:
    defect_id: str
    type: str  # "structural" | "behavioral" | "mixed" | "composition"
    description: str
    api_name: str
    structural_detectable: bool
    metamorphic_detectable: bool
    code_snippet: str
```

### 2. EnsembleValidator (`validators/ensemble.py`)

**Dependencies:** h-m1 validator, h-m2 validator, concurrent.futures

```python
class EnsembleValidator:
    def __init__(
        self, 
        structural_validator: Callable,
        metamorphic_validator: Callable,
        timeout: float = 10.0,
        workers: int = 4
    ): ...
    
    def validate_combined(
        self, 
        model: torch.nn.Module, 
        data: torch.Tensor, 
        config: dict
    ) -> list[Violation]: ...
    
    def _run_parallel(
        self, 
        validators: list[Callable], 
        args: tuple
    ) -> list[list[Violation]]: ...
    
    def _deduplicate_violations(
        self, 
        structural_violations: list[Violation],
        metamorphic_violations: list[Violation]
    ) -> list[Violation]: ...

class Violation:
    source: str  # "structural" | "metamorphic" | "both"
    message: str
    timestamp: float
    defect_id: str
```

### 3. ExperimentRunner (`experiments/runner.py`)

**Dependencies:** EnsembleValidator, CorpusLoader, timeout mechanism

```python
class ExperimentRunner:
    def __init__(
        self,
        corpus_loader: CorpusLoader,
        ensemble_validator: EnsembleValidator,
        timeout: float = 10.0
    ): ...
    
    def run_three_strategy(
        self, 
        strategies: list[str] = ["structural", "metamorphic", "combined"]
    ) -> dict[str, StrategyResults]: ...
    
    def _run_single_strategy(
        self, 
        strategy: str, 
        defects: list[DefectRecord]
    ) -> StrategyResults: ...
    
    def _record_result(
        self, 
        defect: DefectRecord, 
        strategy: str, 
        detected: bool, 
        execution_time: float
    ) -> None: ...
    
    def save_results(self, output_path: str) -> None: ...

class StrategyResults:
    strategy: str
    fnr: float
    detection_rate: float
    execution_time_mean: float
    per_defect_results: list[dict]
```

### 4. StatisticalAnalyzer (`analysis/statistics.py`)

**Dependencies:** scipy.stats, numpy

```python
class StatisticalAnalyzer:
    @staticmethod
    def calculate_fnr(
        detected: set[str], 
        ground_truth_detectable: set[str]
    ) -> tuple[float, tuple[float, float]]: ...
    
    @staticmethod
    def bootstrap_ci(
        data: list[bool], 
        n_iterations: int = 1000, 
        seed: int = 42
    ) -> tuple[float, float]: ...
    
    @staticmethod
    def mcnemar_test(
        strategy_a_results: list[bool],
        strategy_b_results: list[bool]
    ) -> tuple[float, bool]: ...
    
    @staticmethod
    def calculate_reduction(
        baseline_fnr: float, 
        combined_fnr: float
    ) -> float: ...
```

### 5. Visualizer (`analysis/visualizer.py`)

**Dependencies:** matplotlib, pandas

```python
class Visualizer:
    def __init__(self, output_dir: str): ...
    
    def plot_fnr_comparison(
        self, 
        results: dict[str, StrategyResults],
        threshold: float = 0.30
    ) -> str: ...
    
    def plot_coverage_by_type(
        self, 
        results: dict[str, StrategyResults],
        defects: list[DefectRecord]
    ) -> str: ...
    
    def plot_execution_time(
        self, 
        results: dict[str, StrategyResults]
    ) -> str: ...
```

### 6. Main Orchestrator (`run_experiment.py`)

**Dependencies:** All above modules

```python
def main():
    # Load corpus
    loader = CorpusLoader("../h-e1/data/defect_corpus.csv")
    defects = loader.load(stratify_by="type")
    
    # Setup validators
    ensemble = EnsembleValidator(
        structural_validator=validate_structural_from_h_m1,
        metamorphic_validator=validate_metamorphic_from_h_m2,
        timeout=10.0,
        workers=4
    )
    
    # Run experiment
    runner = ExperimentRunner(loader, ensemble, timeout=10.0)
    results = runner.run_three_strategy()
    runner.save_results("data/results.csv")
    
    # Analyze
    analyzer = StatisticalAnalyzer()
    fnr_structural = analyzer.calculate_fnr(...)
    fnr_metamorphic = analyzer.calculate_fnr(...)
    fnr_combined = analyzer.calculate_fnr(...)
    
    p_value_structural = analyzer.mcnemar_test(...)
    p_value_metamorphic = analyzer.mcnemar_test(...)
    
    # Visualize
    viz = Visualizer("visualizations/")
    viz.plot_fnr_comparison(results, threshold=0.30)
    viz.plot_coverage_by_type(results, defects)
    viz.plot_execution_time(results)
    
    # Report
    print(f"FNR Reduction: {analyzer.calculate_reduction(...):.1%}")
    print(f"Gate: {'PASS' if reduction >= 0.30 else 'FAIL'}")
```

---

## External Dependencies (Base Hypotheses)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| validate_structural | `from contracts.validator import validate_structural` | `h-m1/code/contracts/validator.py` |
| ContractViolationError | `from contracts.validator import ContractViolationError` | `h-m1/code/contracts/validator.py` |
| validate_metamorphic | `from contracts.metamorphic import validate_metamorphic` | `h-m2/code/contracts/metamorphic.py` |
| MetamorphicValidator | `from contracts.metamorphic import MetamorphicValidator` | `h-m2/code/contracts/metamorphic.py` |

**Verified from:** Actual implementations in h-m1/h-m2 code directories

**Integration Strategy:**
- Import validators as-is (no modifications)
- Wrap in ensemble orchestration layer
- Pass defect code snippets as input models
- Catch exception types for violation detection

---

## Data Flow

```
1. Load Phase
   defect_corpus.csv → CorpusLoader → DefectRecord[]

2. Validation Phase (Parallel)
   DefectRecord → EnsembleValidator
     ├─ Thread 1: validate_structural(defect_code) → Violation[]
     └─ Thread 2: validate_metamorphic(defect_code) → Violation[]
   → Aggregate → Deduplicated Violation[]

3. Experiment Phase
   For strategy in [structural, metamorphic, combined]:
     DefectRecord[] → _run_single_strategy → StrategyResults
   → results.csv

4. Analysis Phase
   StrategyResults → StatisticalAnalyzer
     ├─ calculate_fnr() → FNR with 95% CI
     ├─ mcnemar_test() → p-value
     └─ calculate_reduction() → reduction %

5. Visualization Phase
   StrategyResults → Visualizer → PNG plots
```

---

## Component Interaction

**EnsembleValidator Workflow:**
1. Deep copy model (avoid mutation)
2. Launch ThreadPoolExecutor with 2 workers
3. Submit tasks: [structural_validator, metamorphic_validator]
4. Wait with timeout=10s per task
5. Aggregate violations from both threads
6. Deduplicate: if same defect flagged by both, mark source="both"
7. Return combined violation list

**Deduplication Logic:**
- Hash violation by defect_id + message substring
- If hash collision → merge, set source="both"
- Otherwise → preserve original source label

**Timeout Handling:**
- ThreadPoolExecutor.submit() → Future object
- Future.result(timeout=10.0) → raises TimeoutError
- Catch TimeoutError → record as TIMEOUT category
- Include in results.csv but exclude from FNR calculation

---

## Error Handling Strategy

**Validation Errors:**
- ContractViolationError → detected=True, violation logged
- TimeoutError → detected=False, execution_time=10.0, flag=TIMEOUT
- RuntimeError (model execution) → detected=False, flag=MODEL_ERROR

**Data Errors:**
- CSV parse error → abort with clear error message
- Missing ground truth label → skip defect, log warning
- Invalid defect_type → skip defect, log warning

**Statistical Errors:**
- Division by zero (FNR) → return NaN, log warning
- McNemar test prerequisites not met → skip test, report N/A

---

## Configuration Specification

**config.yaml:**
```yaml
corpus:
  path: "../h-e1/data/defect_corpus.csv"
  stratify_by: "type"

validation:
  timeout: 10.0
  parallel_workers: 4
  structural_config:
    rtol: 1e-5
    atol: 1e-7
  metamorphic_config:
    softmax_tolerance: 1e-5
    dropout_identity_check: true

experiment:
  strategies: ["structural", "metamorphic", "combined"]
  output_path: "data/results.csv"
  random_seed: 42

analysis:
  bootstrap_iterations: 1000
  confidence_level: 0.95
  significance_alpha: 0.05

visualization:
  output_dir: "visualizations/"
  fnr_threshold: 0.30
  dpi: 300
  format: "png"
```

---

## Integration Points

**h-m1 Integration:**
- Import: `from contracts.validator import validate_structural, ContractViolationError`
- Usage: Wrap defect code snippet in function, apply decorator
- Exception handling: Catch ShapeViolation, DeviceViolation, DtypeViolation

**h-m2 Integration:**
- Import: `from contracts.metamorphic import validate_metamorphic, MetamorphicValidator`
- Usage: Pass defect code as model module, run validator checks
- Exception handling: Catch SoftmaxSumViolation, DropoutIdentityViolation

**h-e1 Integration:**
- Data source: `defect_corpus.csv` from h-e1 validation
- Schema: defect_id, type, description, api_name, source_project, stage, invariant
- Ground truth: Columns structural_detectable, metamorphic_detectable (if present)
- Note: If ground truth missing, infer from defect type (structural=structural_detectable)

---

## Performance Optimization

**Parallel Execution:**
- Use ThreadPoolExecutor (GIL not bottleneck for I/O-bound validation)
- Max workers = 4 (balanced for CPU cores)
- Batch size = 1 defect per task (fine-grained timeout control)

**Caching:**
- Model validation results cached by defect_id
- Avoid redundant validation across strategies
- Cache invalidation on config change

**Timeout Enforcement:**
- Per-validator timeout = 10s
- Total batch timeout = None (allow full corpus completion)
- Future.result(timeout=10.0) for strict enforcement

---

## File Structure

```
h-c1/
├── code/
│   ├── data/
│   │   ├── corpus_loader.py
│   │   └── results.csv
│   ├── validators/
│   │   └── ensemble.py
│   ├── experiments/
│   │   └── runner.py
│   ├── analysis/
│   │   ├── statistics.py
│   │   └── visualizer.py
│   ├── config.yaml
│   └── run_experiment.py
├── visualizations/
│   ├── fnr_comparison.png
│   ├── coverage_by_type.png
│   └── execution_time.png
├── data/
│   └── results.csv
└── 04_validation.md
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| C-1 | Corpus Loader | Implement stratified CSV loader with DefectRecord schema | 4 | 1 (CSV read) + 1 (stratification) + 1 (validation) + 1 (tests) |
| C-2 | Ensemble Validator | Parallel execution wrapper with timeout and deduplication | 8 | 2 (ThreadPoolExecutor) + 2 (timeout handling) + 2 (deduplication) + 2 (integration) |
| C-3 | Experiment Runner | Three-strategy comparison with per-defect recording | 7 | 2 (strategy loop) + 2 (result recording) + 2 (CSV output) + 1 (tests) |
| C-4 | Statistical Analyzer | FNR calculation, bootstrap CI, McNemar test | 6 | 2 (FNR formula) + 2 (bootstrap) + 1 (McNemar) + 1 (tests) |
| C-5 | Visualizer | Three plots (FNR comparison, coverage by type, execution time) | 5 | 2 (FNR plot) + 1 (coverage plot) + 1 (time plot) + 1 (styling) |
| C-6 | Integration Script | Main orchestrator with config loading and reporting | 5 | 2 (config parsing) + 1 (module wiring) + 1 (error handling) + 1 (logging) |
| C-7 | Validation Report | Run experiment, analyze results, document 04_validation.md | 9 | 3 (experiment execution) + 2 (statistical tests) + 2 (gate verdict) + 2 (documentation) |

**Total Complexity:** 44  
**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [C-7], Low(4-8): [C-1, C-2, C-3, C-4, C-5, C-6]

**Complexity Breakdown by Component:**
- Module_Size (1-5): Data structures simple (1-2), logic modules medium (3-4)
- Dependencies (1-5): External deps moderate (pandas, scipy, matplotlib) = 3
- Algorithm (1-5): FNR calculation straightforward (2), McNemar test library call (1), deduplication logic (2)
- Integration (1-5): h-m1/h-m2 integration moderate (3), parallel execution handling (3)

---

## Validation Criteria

**Functional:**
- Ensemble validator executes both validators in parallel within 10s
- Deduplication correctly identifies mixed defects (source="both")
- Three-strategy experiment produces 1044 results (348 × 3)
- FNR calculation matches formula: (missed/detectable)
- McNemar test returns p-value and significance verdict

**Non-Functional:**
- 99th percentile execution time <10s per test
- Parallel overhead <10% vs sequential
- Results CSV schema matches specification
- Configuration-driven (no hardcoded values)

**Gate Criteria:**
- FNR reduction ≥30% vs better baseline (structural or metamorphic)
- Statistical significance p<0.05 (McNemar test)
- False-positive rate <5% on control set (50 valid scenarios)

---

## Risk Mitigation

**Risk 1: Validator Interference (State Mutation)**
- Mitigation: Deep copy model before each validation
- Verification: Unit test with mutable model state

**Risk 2: Defect Corpus Mislabeling**
- Mitigation: Manual review 10% sample (35 defects)
- Verification: Cross-check with h-e1 validation logs

**Risk 3: Parallel Execution Deadlock**
- Mitigation: Timeout enforcement per validator
- Verification: Integration test with intentionally slow validator

**Risk 4: Deduplication False Negatives**
- Mitigation: Hash-based matching with substring tolerance
- Verification: Unit test with known duplicate pairs

---

## Testing Strategy

**Unit Tests:**
- `test_corpus_loader.py`: Stratification, schema validation
- `test_ensemble_validator.py`: Parallel execution, deduplication, timeout
- `test_statistical_analyzer.py`: FNR formula, bootstrap CI, McNemar test
- `test_visualizer.py`: Plot generation (check file exists, not visual)

**Integration Tests:**
- `test_experiment_runner.py`: Run on 10-defect subset, verify result schema
- `test_timeout_handling.py`: Inject slow validator, verify timeout behavior
- `test_control_set.py`: FPR=0% on 50 valid scenarios

**Validation Tests:**
- `test_full_experiment.py`: Run on full 348-defect corpus
- `test_gate_criteria.py`: Verify FNR reduction ≥30%, p<0.05

---

## Dependencies

**Python Packages:**
- torch>=2.0.0 (model execution)
- pandas>=1.5.0 (CSV handling)
- scipy>=1.10.0 (McNemar test)
- matplotlib>=3.5.0 (visualizations)
- numpy>=1.23.0 (numerical operations)

**Internal Dependencies:**
- h-m1 validators (structural contracts)
- h-m2 validators (metamorphic contracts)
- h-e1 defect corpus (348 defects)

**External Dependencies (none):**
- No network access required
- No GPU required (CPU-only)
- No database connections

---

**End of Architecture Document**
