# Architecture Design: H-C4 Version-Stable Contract Validation System

**Hypothesis ID:** h-c4  
**Document Type:** Architecture  
**Phase:** 3 - Implementation Planning  
**Status:** DRAFT  
**Generated:** 2026-07-11

**Applied Patterns:** Multi-version environment isolation, contract stability tracking, false positive categorization

---

## Codebase Analysis (Serena)

**Project Type**: condition_hypothesis  
**Status**: Extends h-m1 (structural) and h-m2 (metamorphic) contracts  
**Analyzed Paths**: 
- docs/youra_research/h-m1/code/ (validator.py with @validate_structural)
- docs/youra_research/h-m2/code/ (validator.py with @validate_metamorphic)
**Findings**: Reusable decorator patterns, exception hierarchies (ShapeViolation, DtypeViolation), probe-based validation

---

## 1. System Overview

### 1.1 Architecture Principle
Version-stable contract validation system that tests h-m1/h-m2 contracts across ±2 minor library versions. Measures false positive rate (<5% target) and identifies version-sensitive contract patterns. Uses isolated environments to prevent version contamination.

### 1.2 Core Components

* **version_adapter/** - Multi-version environment manager (conda/virtualenv)
* **contract_injector/** - Decorator-based contract injection into test scripts
* **false_positive_tracker/** - FP detection, logging, categorization
* **stability_analyzer/** - Root cause analysis (API deprecation, behavioral change, numerical drift)
* **test_corpus/** - PyTorch Hub, HuggingFace examples, GitHub scripts
* **run_version_transition_benchmark.py** - Main experiment harness

### 1.3 Technology Stack

| Component | Technology |
|-----------|-----------|
| Environment Isolation | Conda 23.0+, Python 3.10 |
| Libraries Under Test | PyTorch 2.1-2.3, HF Transformers 4.35-4.38, NumPy 1.24-1.26 |
| Contract Framework | From h-m1/h-m2 (decorator-based validators) |
| Parallel Execution | concurrent.futures.ProcessPoolExecutor |
| Analysis | pandas, matplotlib (FPR heatmaps) |

---

## 2. Module Specifications

### 2.1 Version Adapter

#### `version_adapter/environment_manager.py`

**Dependencies**: subprocess, pathlib, json

```python
class Environment:
    name: str
    library: str
    version: str
    python_path: str
    conda_prefix: Path
    
    def run_script(self, script_path: Path, timeout: float = 30.0) -> ExecutionResult: ...
    def install_package(self, package: str): ...
    def export_spec(self) -> dict: ...

class EnvironmentManager:
    def __init__(self, base_path: Path = Path('.envs')): ...
    
    def create_environment(self, library: str, version: str) -> Environment:
        """
        Create isolated conda environment.
        
        Args:
            library: "pytorch" | "transformers" | "numpy"
            version: "2.1.0" | "4.35.0" | "1.24.0"
        
        Returns:
            Environment with isolated library installation
        
        Implementation:
            1. conda create -n {library}-{version} python=3.10
            2. conda activate {library}-{version}
            3. pip install {library}=={version}
            4. Export environment.yml for reproducibility
        """
    
    def get_environment(self, library: str, version: str) -> Environment: ...
    def list_environments(self) -> List[Environment]: ...
    def cleanup_environment(self, env: Environment): ...
```

#### `version_adapter/execution_runner.py`

**Dependencies**: subprocess, multiprocessing

```python
class ExecutionResult:
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float
    contract_violations: List[str]
    
class ExecutionRunner:
    def __init__(self, timeout: float = 30.0): ...
    
    def run_in_environment(
        self,
        env: Environment,
        script: str,
        contracts: List[str]
    ) -> ExecutionResult:
        """
        Execute script with contracts in isolated environment.
        
        Args:
            env: Target environment
            script: Python script path or code string
            contracts: Contract decorators to inject
        
        Returns:
            ExecutionResult with contract violation logs
        
        Implementation:
            1. Inject contract decorators into script
            2. subprocess.run([env.python_path, script])
            3. Parse stdout/stderr for contract violations
            4. Categorize outcome: pass, fail, error
        """
    
    def run_parallel(
        self,
        tasks: List[Tuple[Environment, str, List[str]]]
    ) -> List[ExecutionResult]: ...
```

### 2.2 Contract Injector

#### `contract_injector/decorator_injector.py`

**Dependencies**: ast, astor

```python
class ContractInjectionPoint:
    function_name: str
    class_name: str | None
    line_number: int
    contract_type: str  # "structural" | "metamorphic"

class DecoratorInjector:
    def __init__(self): ...
    
    def find_injection_points(self, script: str) -> List[ContractInjectionPoint]:
        """
        Identify functions/methods for contract injection.
        
        Implementation:
            1. ast.parse(script)
            2. Find nn.Module.forward(), model.forward()
            3. Find functions with tensor operations (matmul, softmax)
            4. Return injection points with line numbers
        """
    
    def inject_contracts(
        self,
        script: str,
        injection_points: List[ContractInjectionPoint],
        contract_type: str
    ) -> str:
        """
        Inject contract decorators without modifying semantics.
        
        Args:
            script: Original Python source
            injection_points: Functions to decorate
            contract_type: "structural" | "metamorphic"
        
        Returns:
            Modified source with @validate_structural/@validate_metamorphic
        
        Implementation:
            1. ast.parse(script)
            2. For each injection point:
                - Add import: from contracts.validator import validate_structural
                - Add decorator to AST node
            3. astor.to_source(modified_ast)
        """
    
    def inject_structural_contracts(self, script: str) -> str: ...
    def inject_metamorphic_contracts(self, script: str) -> str: ...
```

### 2.3 False Positive Tracker

#### `false_positive_tracker/fp_detector.py`

**Dependencies**: None

```python
class FalsePositive:
    script_id: str
    contract_id: str
    source_version: str
    target_version: str
    violation_message: str
    breakage_type: str  # "api_deprecation" | "behavioral_change" | "numerical_drift" | "unknown"
    timestamp: datetime

class FalsePositiveDetector:
    def __init__(self): ...
    
    def detect_false_positive(
        self,
        baseline_result: ExecutionResult,
        target_result: ExecutionResult,
        script_id: str,
        source_version: str,
        target_version: str
    ) -> Optional[FalsePositive]:
        """
        Detect false positive: baseline passes, target fails on valid code.
        
        Logic:
            if baseline_result.success and not target_result.success:
                if "contract violation" in target_result.stderr:
                    return FalsePositive(...)
            return None
        """
    
    def categorize_breakage(self, fp: FalsePositive) -> str:
        """
        Categorize FP root cause via heuristics.
        
        Rules:
            - "DeprecationWarning" in violation_message → "api_deprecation"
            - "dtype" or "shape" in violation_message → "behavioral_change"
            - "tolerance" or "rtol" in violation_message → "numerical_drift"
            - else → "unknown"
        """
```

#### `false_positive_tracker/fpr_calculator.py`

**Dependencies**: numpy, scipy

```python
class FPRMetrics:
    overall_fpr: float
    fpr_by_contract_type: Dict[str, float]
    fpr_by_library: Dict[str, float]
    fpr_by_version_distance: Dict[int, float]
    confidence_interval_95: Tuple[float, float]

class FPRCalculator:
    def __init__(self): ...
    
    def compute_fpr(
        self,
        results: List[Tuple[ExecutionResult, ExecutionResult]],
        metadata: List[dict]
    ) -> FPRMetrics:
        """
        Compute false positive rate.
        
        FPR = (False Positives) / (True Negatives + False Positives)
        
        Args:
            results: List of (baseline_result, target_result) pairs
            metadata: Script info (contract_type, library, version_distance)
        
        Returns:
            FPRMetrics with stratified FPR + 95% CI
        
        Implementation:
            1. Identify FPs: baseline pass, target fail
            2. Identify TNs: baseline pass, target pass
            3. Compute FPR overall
            4. Stratify by contract_type, library, version_distance
            5. Wilson score interval for 95% CI
        """
    
    def compute_confidence_interval(self, fpr: float, n: int) -> Tuple[float, float]: ...
    def stratify_fpr(self, fps: List[FalsePositive], metadata: List[dict]) -> Dict: ...
```

### 2.4 Stability Analyzer

#### `stability_analyzer/root_cause_analyzer.py`

**Dependencies**: requests (for release notes), re

```python
class BreakageAnalysis:
    root_cause: str
    release_note_url: str | None
    api_changed: str | None
    fix_recommendation: str

class RootCauseAnalyzer:
    def __init__(self, release_notes_cache: Path = Path('.release_notes')): ...
    
    def analyze_breakage(self, fp: FalsePositive) -> BreakageAnalysis:
        """
        Cross-reference FP with library release notes.
        
        Implementation:
            1. Fetch release notes for version transition
               - PyTorch: https://pytorch.org/docs/{version}/notes/
               - HF: https://github.com/huggingface/transformers/releases/tag/v{version}
            2. Search for API mentioned in violation_message
            3. Extract deprecation notices, behavioral changes
            4. Generate fix recommendation (e.g., "Update contract tolerance to 1e-5")
        """
    
    def fetch_release_notes(self, library: str, source_version: str, target_version: str) -> str: ...
    def extract_api_changes(self, release_notes: str, api_name: str) -> List[str]: ...
    def generate_fix_recommendation(self, fp: FalsePositive, changes: List[str]) -> str: ...
```

#### `stability_analyzer/pattern_extractor.py`

**Dependencies**: collections

```python
class ContractPattern:
    pattern_name: str
    stability_score: float  # % of contracts with this pattern that remain stable
    examples: List[str]

class PatternExtractor:
    def __init__(self): ...
    
    def extract_patterns(
        self,
        stable_contracts: List[str],
        unstable_contracts: List[str]
    ) -> Tuple[List[ContractPattern], List[ContractPattern]]:
        """
        Identify high-stability and anti-patterns.
        
        High-stability patterns (≥95% stability):
            - Abstract invariants (e.g., softmax sum=1)
            - Tolerance bands (rtol=1e-5)
            - Public API only (no _buffers access)
        
        Anti-patterns (<80% stability):
            - Exact numerical equality (==)
            - Internal state inspection (_modules, _buffers)
            - Deprecated API usage
        
        Returns:
            (high_stability_patterns, anti_patterns)
        """
    
    def analyze_contract_ast(self, contract_code: str) -> Dict[str, bool]: ...
    def compute_pattern_stability(self, pattern: str, all_contracts: List) -> float: ...
```

### 2.5 Experimental Harness

#### `run_version_transition_benchmark.py`

**Dependencies**: version_adapter, contract_injector, false_positive_tracker

```python
class BenchmarkConfig:
    libraries: List[Tuple[str, List[str]]]  # [("pytorch", ["2.1.0", "2.2.0", "2.3.0"]), ...]
    corpus_path: Path
    contract_types: List[str]
    parallel_workers: int

class VersionTransitionBenchmark:
    def __init__(self, config: BenchmarkConfig): ...
    
    def run(self) -> BenchmarkResults:
        """
        Main experiment loop.
        
        Workflow:
            1. Setup: Create all environments (13 total)
            2. Corpus: Load 1000 test scripts
            3. Injection: Annotate contracts (3000 contract instances)
            4. Baseline: Run on source versions (1000 scripts × 13 versions)
            5. Transition: Run on target versions (1000 scripts × 12 version pairs)
            6. Detection: Identify false positives (baseline pass, target fail)
            7. Analysis: Compute FPR, categorize breakages
            8. Reporting: Generate validation report
        
        Returns:
            BenchmarkResults(
                fpr_metrics: FPRMetrics,
                false_positives: List[FalsePositive],
                stability_matrix: pd.DataFrame,
                execution_time: float
            )
        """
    
    def setup_environments(self): ...
    def load_corpus(self) -> List[Tuple[str, str]]: ...
    def inject_contracts_batch(self, scripts: List[str]) -> List[str]: ...
    def run_baseline_phase(self) -> Dict[str, ExecutionResult]: ...
    def run_transition_phase(self) -> Dict[str, ExecutionResult]: ...
    def detect_false_positives(self) -> List[FalsePositive]: ...
    def analyze_results(self) -> BenchmarkResults: ...
```

---

## 3. Data Flow

### 3.1 Experiment Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Environment Setup                                        │
│    EnvironmentManager.create_environment() × 13 versions    │
│    → .envs/pytorch-2.1.0/, .envs/pytorch-2.2.0/, ...       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Corpus Collection                                        │
│    Load PyTorch Hub (200), HF examples (300), GitHub (500)  │
│    → test_corpus/pytorch_hub/*.py                           │
│    → test_corpus/huggingface_examples/*.py                  │
│    → test_corpus/github_scripts/*.py                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Contract Injection                                       │
│    DecoratorInjector.inject_contracts() × 1000 scripts      │
│    → annotated_corpus/script_001_structural.py              │
│    → annotated_corpus/script_002_metamorphic.py             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Baseline Phase (Source Versions)                        │
│    ExecutionRunner.run_in_environment()                     │
│    → baseline_results.json                                  │
│    → {script_id: {version: ExecutionResult}}                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Transition Phase (Target Versions)                      │
│    ExecutionRunner.run_in_environment() × 12 version pairs  │
│    → transition_results.json                                │
│    → {script_id: {version_pair: ExecutionResult}}           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. False Positive Detection                                 │
│    FalsePositiveDetector.detect_false_positive()            │
│    if baseline.success and not transition.success:          │
│        → false_positives.csv                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. FPR Calculation                                          │
│    FPRCalculator.compute_fpr()                              │
│    → fpr_results.json                                       │
│    → {overall: 3.2%, structural: 1.8%, metamorphic: 5.5%}  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 8. Root Cause Analysis                                      │
│    RootCauseAnalyzer.analyze_breakage() for each FP         │
│    → breakage_analysis.json                                 │
│    → {fp_id: {root_cause, release_note_url, fix}}          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 9. Validation Report                                        │
│    Generate 04_validation.md                                │
│    → FPR metrics, stability heatmap, contract patterns      │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Key Data Structures

**baseline_results.json**:
```json
{
  "script_001": {
    "pytorch-2.1.0": {
      "success": true,
      "contract_violations": [],
      "execution_time": 0.45
    },
    "pytorch-2.2.0": {...}
  }
}
```

**transition_results.json**:
```json
{
  "script_001": {
    "pytorch-2.1.0→2.2.0": {
      "success": false,
      "contract_violations": ["Shape mismatch: expected (1, 1000), got (1, 999)"],
      "execution_time": 0.52
    }
  }
}
```

**false_positives.csv**:
```csv
script_id,contract_id,source_version,target_version,violation_message,breakage_type
script_042,structural_shape,pytorch-2.1.0,pytorch-2.2.0,"Output shape mismatch",api_deprecation
script_089,metamorphic_softmax,transformers-4.35.0,transformers-4.36.0,"Softmax sum 0.9999998",numerical_drift
```

---

## 4. Error Handling

### 4.1 Environment Isolation Failures

**Scenario:** Conda environment creation fails (network, disk space)

**Handling:**
```python
try:
    env = manager.create_environment("pytorch", "2.1.0")
except EnvironmentCreationError as e:
    logger.error(f"Failed to create environment: {e}")
    # Fallback: Try virtualenv instead of conda
    env = manager.create_virtualenv("pytorch", "2.1.0")
```

### 4.2 Script Execution Timeouts

**Scenario:** Script hangs (infinite loop, deadlock)

**Handling:**
```python
result = runner.run_in_environment(env, script, timeout=30.0)
if result.exit_code == -1:  # Timeout
    logger.warning(f"Script {script_id} timed out in {env.name}")
    # Mark as SKIP, do not count toward FPR
```

### 4.3 Contract Injection Failures

**Scenario:** AST parsing fails (syntax errors, unsupported Python version)

**Handling:**
```python
try:
    annotated = injector.inject_contracts(script, injection_points, "structural")
except ast.SyntaxError:
    logger.warning(f"Could not parse {script_id}, skipping")
    # Exclude from corpus (reduce N, but maintain validity)
```

---

## 5. Performance Optimizations

### 5.1 Parallel Execution

**Strategy:** ProcessPoolExecutor for version pairs

```python
with ProcessPoolExecutor(max_workers=8) as executor:
    futures = []
    for (script, env, contracts) in tasks:
        future = executor.submit(runner.run_in_environment, env, script, contracts)
        futures.append(future)
    
    results = [f.result() for f in futures]
```

**Expected Speedup:** 8× on 8-core machine (48h → 6h)

### 5.2 Environment Caching

**Strategy:** Reuse environments across scripts

```python
env_cache = {}  # {(library, version): Environment}

for script in corpus:
    env = env_cache.get(("pytorch", "2.1.0"))
    if not env:
        env = manager.create_environment("pytorch", "2.1.0")
        env_cache[("pytorch", "2.1.0")] = env
    
    result = runner.run_in_environment(env, script)
```

**Benefit:** Avoid repeated environment creation (5s → 0s per script)

### 5.3 Incremental Results

**Strategy:** Save results after each version pair

```python
for version_pair in version_pairs:
    results = run_transition_phase(version_pair)
    save_checkpoint(f"results_{version_pair}.json", results)
    # If interrupted, resume from checkpoint
```

---

## 6. Testing Strategy

### 6.1 Unit Tests

**Module:** version_adapter/environment_manager.py
- Test environment creation (mock conda commands)
- Test environment isolation (verify no cross-contamination)
- Test cleanup (environment deletion)

**Module:** contract_injector/decorator_injector.py
- Test AST parsing (valid/invalid scripts)
- Test injection correctness (decorators added, semantics preserved)
- Test injection point detection (nn.Module.forward identified)

**Module:** false_positive_tracker/fp_detector.py
- Test FP detection logic (baseline pass, target fail)
- Test breakage categorization (heuristic accuracy)

### 6.2 Integration Tests

**End-to-End Test:** Mini benchmark (10 scripts, 2 version pairs)
- Expected: Completes in <5 minutes
- Validates full workflow (setup → injection → execution → FP detection)

---

## 7. File Structure

```
h-c4/code/
├── version_adapter/
│   ├── __init__.py
│   ├── environment_manager.py       # Conda/virtualenv wrapper
│   └── execution_runner.py          # Script execution in isolated envs
├── contract_injector/
│   ├── __init__.py
│   └── decorator_injector.py        # AST-based contract injection
├── false_positive_tracker/
│   ├── __init__.py
│   ├── fp_detector.py               # FP detection logic
│   └── fpr_calculator.py            # FPR metrics + confidence intervals
├── stability_analyzer/
│   ├── __init__.py
│   ├── root_cause_analyzer.py       # Release note cross-reference
│   └── pattern_extractor.py         # High-stability pattern mining
├── test_corpus/
│   ├── pytorch_hub/                 # 200 PyTorch Hub scripts
│   ├── huggingface_examples/        # 300 HF examples
│   └── github_scripts/              # 500 curated GitHub scripts
├── run_version_transition_benchmark.py  # Main experiment harness
├── requirements.txt
└── README.md
```

---

## 8. Dependencies

**Core:**
- Python 3.10
- conda 23.0+ (environment isolation)
- subprocess, multiprocessing, concurrent.futures

**Libraries Under Test:**
- PyTorch: 2.1.0, 2.1.2, 2.2.0, 2.2.2, 2.3.0, 2.3.1
- HuggingFace Transformers: 4.35.0, 4.36.0, 4.37.0, 4.38.0
- NumPy: 1.24.0, 1.25.0, 1.26.0

**Contract Framework (from h-m1/h-m2):**
- contracts/validator.py (@validate_structural, @validate_metamorphic)

**Analysis:**
- pandas (FPR stratification)
- matplotlib (stability heatmaps)
- scipy (confidence intervals)

**Utilities:**
- ast, astor (contract injection)
- requests (release notes fetching)

---

## 9. Non-Functional Requirements

### 9.1 Reproducibility

- Conda environment.yml exports for each version
- Fixed random seeds (if any randomness)
- Versioned dependencies (requirements.txt with ==)

### 9.2 Extensibility

- Plugin interface for new libraries (EnvironmentManager.register_library())
- Contract type registry (support h-m3 composition contracts in future)

### 9.3 Maintainability

- Type hints throughout (mypy compliance)
- Docstrings for all public APIs
- Logging at INFO level (progress) and DEBUG level (detailed traces)

---

**Architecture Status:** APPROVED  
**Next Document:** Logic Design (03_logic.md)  
**Implementation Estimate:** 1 week (48h runtime + 8h analysis)
