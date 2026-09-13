# Architecture: Early Detection Cost Reduction (h-m3)

**Date:** 2026-08-20  
**Version:** 1.0  
**Type:** MECHANISM  
**Applied patterns:** Validation harness isolation, placeholder corpus generation

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase  
**Status:** Validation framework found at `src/validation/`  
**Analyzed Path:** src/validation/  
**Findings:** Three-layer validation (schemas.py, patterns.py, contracts.py) already implemented from h-m2. Reusable for condition B.

---

## 1. Module Structure

### 1.1 CorpusGenerator (`experiments/h_m3_early_detection/corpus_generator.py`)

**Dependencies:** None

```python
class CorpusGenerator:
    def __init__(self, num_valid: int = 80, num_violations: int = 20, seed: int = 42): ...
    def generate(self) -> List[Dict]: ...
    def _generate_valid_hypothesis(self, hypothesis_id: str) -> Dict: ...
    def _inject_violation(self, hypothesis_id: str, constraint: str) -> Dict: ...
    def save(self, path: str) -> None: ...
```

### 1.2 PipelineRunner (`experiments/h_m3_early_detection/pipeline_runner.py`)

**Dependencies:** FailureTracker

```python
class PipelineRunner:
    def __init__(self, corpus: List[Dict], validator, tracker: FailureTracker): ...
    def run(self) -> Dict: ...
    def _execute_phase2(self, hypothesis: Dict) -> Tuple[Dict, bool]: ...
    def _execute_phase3(self, phase2_output: Dict) -> Tuple[Dict, bool]: ...
    def _execute_phase4(self, phase3_output: Dict) -> Tuple[Dict, bool]: ...
    def _execute_phase5(self, phase4_output: Dict) -> Tuple[Dict, bool]: ...
```

### 1.3 SchemaValidator (`experiments/h_m3_early_detection/validators.py`)

**Dependencies:** src.validation.schemas

```python
class SchemaValidator:
    def validate_phase2_output(self, data: Dict) -> Tuple[bool, Optional[str]]: ...
    def validate_phase3_output(self, data: Dict) -> Tuple[bool, Optional[str]]: ...
    def validate_phase4_output(self, data: Dict) -> Tuple[bool, Optional[str]]: ...
```

### 1.4 ContractValidator (`experiments/h_m3_early_detection/validators.py`)

**Dependencies:** src.validation.contracts

```python
class ContractValidator:
    def validate_phase2_output(self, data: Dict) -> Tuple[bool, Optional[str]]: ...
    def validate_phase3_output(self, data: Dict) -> Tuple[bool, Optional[str]]: ...
    def validate_phase4_output(self, data: Dict) -> Tuple[bool, Optional[str]]: ...
```

### 1.5 FailureTracker (`experiments/h_m3_early_detection/failure_tracker.py`)

**Dependencies:** None

```python
class FailureTracker:
    def __init__(self, output_dir: str): ...
    def log_boundary_validation(self, hypothesis_id: str, phase: int, passed: bool, error: Optional[str]): ...
    def log_phase45_failure(self, hypothesis_id: str, phase: int, constraint: str, message: str, ground_truth: str, detected_at_boundary: bool): ...
    def get_failures(self) -> List[Dict]: ...
    def save_logs(self, condition: str): ...
```

### 1.6 ResultAnalyzer (`experiments/h_m3_early_detection/analyzer.py`)

**Dependencies:** FailureTracker

```python
class ResultAnalyzer:
    def __init__(self, condition_a_log: str, condition_b_log: str, failures_dir: str): ...
    def calculate_failure_rate(self, condition: str) -> float: ...
    def calculate_reduction(self) -> float: ...
    def calculate_detection_rate(self, condition: str) -> float: ...
    def calculate_false_positive_rate(self, condition: str) -> float: ...
    def per_constraint_breakdown(self) -> Dict: ...
    def determine_gate_verdict(self) -> str: ...
    def generate_report(self, output_path: str): ...
```

### 1.7 Orchestrator (`experiments/h_m3_early_detection/main.py`)

**Dependencies:** All modules

```python
def main():
    # 1. Generate corpus
    # 2. Run condition A
    # 3. Run condition B
    # 4. Analyze results
    # 5. Generate report
    ...
```

---

## 2. File Organization

```
experiments/h_m3_early_detection/
├── config.py                    # Constants (paths, violation counts, thresholds)
├── corpus_generator.py          # Generate 100 placeholder hypotheses
├── pipeline_runner.py           # Phase 2→3→4→5 simulation
├── validators.py                # SchemaValidator + ContractValidator
├── failure_tracker.py           # Log validation/failures
├── analyzer.py                  # Calculate metrics, gate verdict
├── main.py                      # Orchestration
└── __init__.py

tests/placeholder_hypotheses/
└── corpus_100.json              # Generated corpus

results/h_m3/
├── condition_a_log.json         # Schema-only execution log
├── condition_b_log.json         # Contract-based execution log
└── phase45_failures/
    ├── cond_a_h-test-015.json
    ├── cond_b_h-test-023.json
    └── ...

docs/youra_research/h-m3/
└── 04_validation.md             # Final report
```

---

## 3. Data Flow

### 3.1 Corpus Generation
```
CorpusGenerator.generate()
  → 80 valid hypotheses (C1/C2/C3/C4 compliant)
  → 20 violated hypotheses (5 each: C1, C2, C3, C4)
  → corpus_100.json
```

### 3.2 Condition A (Schema-only)
```
main.py
  → PipelineRunner(SchemaValidator, FailureTracker)
  → For each hypothesis:
      Phase2 → validate → Phase3 → validate → Phase4 → validate → Phase5
      If violation NOT caught: Phase4/5 fails → FailureTracker logs
  → condition_a_log.json + phase45_failures/cond_a_*.json
```

### 3.3 Condition B (Contract-based)
```
main.py
  → PipelineRunner(ContractValidator, FailureTracker)
  → For each hypothesis:
      Phase2 → validate → Phase3 → validate → Phase4 → validate → Phase5
      If violation caught early: pipeline halts, NO Phase4/5 failure
  → condition_b_log.json + phase45_failures/cond_b_*.json
```

### 3.4 Analysis
```
ResultAnalyzer
  → Load condition_a_log.json, condition_b_log.json, phase45_failures/
  → Calculate: Failure_Rate_A, Failure_Rate_B
  → Reduction = (Failure_Rate_A - Failure_Rate_B) / Failure_Rate_A
  → Per-constraint breakdown
  → Gate verdict (PASS/PIVOT/ROUTE_TO_0)
  → 04_validation.md
```

---

## 4. Validation Integration Points

### 4.1 Phase 2→3 Boundary
**Input:** `hypothesis["phase2_output"]` (verification plan)  
**Schema validator:** Pydantic type checks (dataset_type, evaluation_method)  
**Contract validator:** C1 (no synthetic data), C2 (no human eval), C3 (standard datasets only), C4 (no new benchmarks)  
**Failure impact:** Invalid hypothesis propagates to Phase 3 implementation plan

### 4.2 Phase 3→4 Boundary
**Input:** Phase 3 PRD/Architecture (placeholder)  
**Schema validator:** Field existence checks  
**Contract validator:** Dataset/model specifications consistency with Phase 2  
**Failure impact:** Infeasible implementation plan reaches Phase 4 coding

### 4.3 Phase 4→5 Boundary
**Input:** Phase 4 code artifacts (placeholder)  
**Schema validator:** File structure checks  
**Contract validator:** Baseline compatibility verification  
**Failure impact:** Code runs but fails baseline comparison

---

## 5. Failure Detection & Attribution

### 5.1 Phase 4 Failure Patterns
```python
# C1 violation: Synthetic dataset requirement
if phase2_output["dataset_type"] == "synthetic":
    raise Phase4Error("Cannot generate code for synthetic dataset")

# C2 violation: Human evaluation requirement
if phase2_output["evaluation"]["requires_human"]:
    raise Phase4Error("Cannot automate human evaluation")
```

### 5.2 Phase 5 Failure Patterns
```python
# C3 violation: Non-standard dataset
if phase2_output["dataset_name"] not in STANDARD_DATASETS:
    raise Phase5Error("Baseline not available for custom dataset")

# C4 violation: New benchmark creation
if phase2_output["experiment"]["creates_benchmark"]:
    raise Phase5Error("No baseline for new benchmark")
```

### 5.3 Attribution Logic
```python
def attribute_failure(failure: Dict, corpus_entry: Dict) -> bool:
    """Verify failure traces to injected violation (not infrastructure)."""
    ground_truth = corpus_entry["injected_violation"]["constraint"]
    failure_constraint = failure["constraint_violated"]
    return ground_truth == failure_constraint and ground_truth != "none"
```

---

## 6. Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Corpus generation | Implement CorpusGenerator, generate 100 hypotheses with violations | 9 | 2+2+3+2 (structure+valid+violations+save) |
| A-2 | Pipeline infrastructure | Implement PipelineRunner with Phase 2→3→4→5 simulation | 11 | 3+2+3+3 (runner+phases+validation+tracking) |
| A-3 | Validator implementations | Implement SchemaValidator and ContractValidator | 8 | 3+3+2 (schema+contract+integration) |
| A-4 | Failure tracking | Implement FailureTracker with boundary logging and Phase 4/5 detection | 7 | 2+3+2 (logging+classification+save) |
| A-5 | Condition A execution | Run full corpus with schema-only validation, log failures | 6 | 2+2+2 (setup+execution+verification) |
| A-6 | Condition B execution | Run full corpus with contract validation, log failures | 6 | 2+2+2 (setup+execution+verification) |
| A-7 | Result analysis | Implement ResultAnalyzer, calculate metrics, generate report | 10 | 3+3+2+2 (metrics+breakdown+verdict+report) |
| A-8 | Gate validation | Manual review of failures, verify attribution, finalize verdict | 5 | 2+2+1 (review+verify+finalize) |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-2, A-7], Low(4-8): [A-3, A-4, A-5, A-6, A-8]

---

## 7. External Dependencies

### 7.1 Existing Validation Framework

| Module | Import Path | File Location |
|--------|-------------|---------------|
| Phase2AOutput | `from src.validation.schemas import Phase2AOutput` | `src/validation/schemas.py` |
| Phase2AOutputWithContracts | `from src.validation.contracts import Phase2AOutputWithContracts` | `src/validation/contracts.py` |
| STANDARD_DATASETS | `from src.validation.constants import STANDARD_DATASETS` | `src/validation/constants.py` |
| EXISTING_BENCHMARKS | `from src.validation.constants import EXISTING_BENCHMARKS` | `src/validation/constants.py` |

**Verified from:** Actual codebase at `src/validation/`

---

## 8. Risk Mitigation

### R2: Incomplete Contract Specification
**Detection:** Track violations that pass boundary validation but fail Phase 4/5  
**Mitigation:** If >5 violations (25%) escape, add mutation testing module to find contract gaps  
**Implementation:** Defer mutation testing to PIVOT phase (if needed)

### R5: Validation Overhead Cost
**Detection:** Time validation execution vs Phase 4/5 debugging time  
**Mitigation:** Profile validation in FailureTracker (add timing metrics)  
**Threshold:** Document as limitation if overhead >2× recovery cost

### False Attribution
**Detection:** Manual review task (A-8) verifies all failures trace to injected violations  
**Mitigation:** Exclude failures on valid hypotheses (n=80) from metrics  
**Implementation:** `FailureTracker.log_phase45_failure()` requires ground_truth parameter

---

## 9. Configuration

### 9.1 Constants (`config.py`)

```python
# Corpus parameters
NUM_VALID_HYPOTHESES = 80
NUM_VIOLATIONS = 20
VIOLATION_DISTRIBUTION = {"C1": 5, "C2": 5, "C3": 5, "C4": 5}
RANDOM_SEED = 42

# Paths
CORPUS_PATH = "tests/placeholder_hypotheses/corpus_100.json"
RESULTS_DIR = "results/h_m3"
FAILURES_DIR = "results/h_m3/phase45_failures"
CONDITION_A_LOG = "results/h_m3/condition_a_log.json"
CONDITION_B_LOG = "results/h_m3/condition_b_log.json"
REPORT_PATH = "docs/youra_research/h-m3/04_validation.md"

# Thresholds
FAILURE_REDUCTION_THRESHOLD = 0.80  # 80% reduction for PASS
DETECTION_RATE_THRESHOLD = 0.90     # 90% boundary detection
```

---

## 10. Self-Validation Checklist

- [x] No ASCII diagrams (bulleted data flow)
- [x] No KB search logs (Applied: validation harness, failure tracking)
- [x] Module sections = interface code only
- [x] 8 Epic tasks with complexity (A-1 to A-8)
- [x] Total length <500 lines
- [x] Codebase Analysis section included
- [x] Serena called on existing validation framework
- [x] External Dependencies section with actual file paths
- [x] Import paths verified from src/validation/
