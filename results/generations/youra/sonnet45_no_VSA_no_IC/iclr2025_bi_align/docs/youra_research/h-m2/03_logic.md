# Logic Design: Multi-Layer Validation Detection (h-m2)

**Hypothesis ID:** h-m2  
**Phase:** 3 - Logic Design  
**Date:** 2026-08-20  
**Implementation Tier:** Tier 0 (Proof-of-Concept)

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase  
**Status:** API signatures verified from actual validation code  
**Analyzed Path:** `src/validation/*.py`  
**Relevant Symbols:**
- `Phase2AOutput` (schema layer)
- `Phase2AOutputWithPatterns` (pattern layer)
- `Phase2AOutputWithContracts` (contract layer)
- `STANDARD_DATASETS`, `EXISTING_BENCHMARKS` (whitelists)

**Applied:** Standard Python test runner pattern

---

## Core Components

### 1. Test Case Generator Extension

**Function:** Extend existing 20-case suite to 30 cases

```python
def generate_test_suite(output_path: str) -> None:
    """Generate 30 test cases: 10 schema, 10 pattern, 5 contract, 5 valid."""
    cases = []
    
    # Schema violations (10): type errors, missing fields, invalid literals
    cases.extend(_gen_schema_violations(count=10))
    
    # Pattern violations (10): keyword blacklist hits
    cases.extend(_gen_pattern_violations(count=10))
    
    # Contract violations (5): cross-field, state-based
    cases.extend(_gen_contract_violations(count=5))
    
    # Valid cases (5): pass all layers
    cases.extend(_gen_valid_cases(count=5))
    
    with open(output_path, 'w') as f:
        yaml.dump({"test_cases": cases}, f)
```

**Distribution Logic:**
```
Schema violations (10):
  - 3 type errors (int instead of str)
  - 3 missing required fields
  - 2 invalid Literal values
  - 2 constraint violations (min_length)

Pattern violations (10):
  - 3 C1 violations (synthetic keywords in dataset_name)
  - 3 C2 violations (human keywords in evaluation_method)
  - 2 C1 edge cases (synonyms: "artificially generated")
  - 2 C2 edge cases (synonyms: "rater", "labeler")

Contract violations (5):
  - 2 C3 violations (unknown standard dataset)
  - 3 C4 violations (new benchmark names)

Valid cases (5):
  - Minimal valid case
  - Custom dataset (bypasses C3)
  - Programmatic API dataset
  - Standard dataset (MNIST)
  - Automated evaluation (no benchmark keyword)
```

---

## 2. Validation Runners

### Baseline Runner (Schema-Only)

```python
from typing import Dict, Any
from pydantic import ValidationError
from src.validation.schemas import Phase2AOutput

def run_schema_only(test_case: Dict[str, Any]) -> Dict[str, Any]:
    """Run schema-only validation (baseline condition).
    
    Returns: {"detected": bool, "layer": None, "error": str|None}
    """
    try:
        Phase2AOutput(**test_case["phase2a_output"])
        return {"detected": False, "layer": None, "error": None}
    except ValidationError as e:
        return {"detected": True, "layer": None, "error": str(e)}
```

**Expected behavior:**
- Detects: structural violations (schema layer only)
- Misses: pattern violations (C1/C2), contract violations (C3/C4)
- Detection rate: 10/25 = 40%

---

### Three-Layer Runner

```python
from pydantic import ValidationError
from icontract import ViolationError
from src.validation.schemas import Phase2AOutput
from src.validation.patterns import Phase2AOutputWithPatterns
from src.validation.contracts import Phase2AOutputWithContracts

def run_three_layer(test_case: Dict[str, Any]) -> Dict[str, Any]:
    """Run three-layer validation (proposed condition).
    
    Fail-fast: stop at first violation.
    Returns: {"detected": bool, "layer": str|None, "error": str|None}
    """
    phase2a_data = test_case["phase2a_output"]
    
    # Layer 1: Schema
    try:
        Phase2AOutput(**phase2a_data)
    except ValidationError as e:
        return {"detected": True, "layer": "schema", "error": str(e)}
    
    # Layer 2: Pattern
    try:
        Phase2AOutputWithPatterns(**phase2a_data)
    except ValidationError as e:
        return {"detected": True, "layer": "pattern", "error": str(e)}
    
    # Layer 3: Contract
    try:
        Phase2AOutputWithContracts(**phase2a_data)
    except (ValidationError, ViolationError) as e:
        return {"detected": True, "layer": "contract", "error": str(e)}
    
    # All layers passed
    return {"detected": False, "layer": None, "error": None}
```

**Expected behavior:**
- Layer 1: catches schema violations (10/10)
- Layer 2: catches pattern violations (10/10)
- Layer 3: catches contract violations (5/5)
- Detection rate: 25/25 = 100%

---

## 3. Detection Rate Calculation

### Per-Condition Metrics

```python
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class DetectionMetrics:
    """Detection rate metrics."""
    total_violations: int
    detected: int
    detection_rate: float  # percentage
    
    # Per-layer breakdown (three-layer only)
    schema_detected: int = 0
    pattern_detected: int = 0
    contract_detected: int = 0
    
    # Per-constraint breakdown
    c1_detected: int = 0  # Pattern layer
    c2_detected: int = 0  # Pattern layer
    c3_detected: int = 0  # Contract layer
    c4_detected: int = 0  # Contract layer

def calculate_detection_rate(results: List[Dict], test_cases: List[Dict]) -> DetectionMetrics:
    """Calculate detection metrics from results.
    
    Args:
        results: List of {"detected": bool, "layer": str|None, ...}
        test_cases: List of test case metadata (violation_type, constraint)
    
    Returns: DetectionMetrics with rates per layer and constraint
    """
    violations = [tc for tc in test_cases if tc["violation_type"] != "none"]
    total_violations = len(violations)
    detected = sum(1 for r in results if r["detected"])
    
    metrics = DetectionMetrics(
        total_violations=total_violations,
        detected=detected,
        detection_rate=100.0 * detected / total_violations if total_violations > 0 else 0.0
    )
    
    # Per-layer breakdown (if three-layer results)
    for i, result in enumerate(results):
        if not result["detected"]:
            continue
        layer = result.get("layer")
        if layer == "schema":
            metrics.schema_detected += 1
        elif layer == "pattern":
            metrics.pattern_detected += 1
        elif layer == "contract":
            metrics.contract_detected += 1
    
    # Per-constraint breakdown
    for i, tc in enumerate(violations):
        if not results[i]["detected"]:
            continue
        constraint = tc.get("constraint_violated")
        if constraint == "C1":
            metrics.c1_detected += 1
        elif constraint == "C2":
            metrics.c2_detected += 1
        elif constraint == "C3":
            metrics.c3_detected += 1
        elif constraint == "C4":
            metrics.c4_detected += 1
    
    return metrics
```

**Formulas:**
- Detection rate: `detected / total_violations × 100%`
- Detection gap: `three_layer_rate - schema_only_rate` (percentage points)
- Per-layer rate: `layer_detected / total_violations × 100%`
- Per-constraint rate: `constraint_detected / constraint_violations × 100%`

---

### False Positive Rate

```python
def calculate_false_positive_rate(results: List[Dict], test_cases: List[Dict]) -> float:
    """Calculate false positive rate on valid cases.
    
    Returns: percentage of valid cases incorrectly rejected
    """
    valid_cases = [tc for tc in test_cases if tc["violation_type"] == "none"]
    valid_results = [results[i] for i, tc in enumerate(test_cases) 
                     if tc["violation_type"] == "none"]
    
    total_valid = len(valid_cases)
    false_positives = sum(1 for r in valid_results if r["detected"])
    
    return 100.0 * false_positives / total_valid if total_valid > 0 else 0.0
```

**Target:** 0% (all valid cases pass all layers)

---

## 4. Experiment Runner

### Main Execution Flow

```python
import yaml
from pathlib import Path
from typing import Dict, List

def run_experiment(test_suite_path: str) -> Dict[str, Any]:
    """Run h-m2 multi-layer validation experiment.
    
    Returns: {
        "baseline": DetectionMetrics,
        "three_layer": DetectionMetrics,
        "gap": float,
        "false_positive_rate": float,
        "verdict": str
    }
    """
    # Load test cases
    with open(test_suite_path) as f:
        data = yaml.safe_load(f)
    test_cases = data["test_cases"]
    
    # Baseline condition (schema-only)
    baseline_results = [run_schema_only(tc) for tc in test_cases]
    baseline_metrics = calculate_detection_rate(baseline_results, test_cases)
    
    # Three-layer condition
    three_layer_results = [run_three_layer(tc) for tc in test_cases]
    three_layer_metrics = calculate_detection_rate(three_layer_results, test_cases)
    
    # Calculate gap
    gap = three_layer_metrics.detection_rate - baseline_metrics.detection_rate
    
    # False positive rate
    fpr = calculate_false_positive_rate(three_layer_results, test_cases)
    
    # Gate verdict
    verdict = _compute_verdict(gap, three_layer_metrics, fpr)
    
    return {
        "baseline": baseline_metrics,
        "three_layer": three_layer_metrics,
        "gap": gap,
        "false_positive_rate": fpr,
        "verdict": verdict
    }
```

**Pseudo-code:**
```
1. Load 30 test cases from YAML
2. For each test case:
   a. Run schema-only validation → record detection
   b. Run three-layer validation → record detection + layer
3. Calculate baseline detection rate (expected: 40%)
4. Calculate three-layer detection rate (expected: 100%)
5. Calculate gap (expected: 60pp)
6. Calculate false positive rate (expected: 0%)
7. Check gate criteria → emit verdict
```

---

### Gate Verdict Logic

```python
def _compute_verdict(gap: float, metrics: DetectionMetrics, fpr: float) -> str:
    """Compute gate verdict based on success criteria.
    
    Primary: gap >= 40pp
    Secondary: pattern layer >= 80% on C1/C2
    """
    primary_pass = gap >= 40.0
    
    # Secondary: pattern layer performance on C1/C2
    c1_c2_total = 6  # 3 C1 + 3 C2 violations (from distribution)
    c1_c2_detected = metrics.c1_detected + metrics.c2_detected
    pattern_rate = 100.0 * c1_c2_detected / c1_c2_total if c1_c2_total > 0 else 0.0
    secondary_pass = pattern_rate >= 80.0
    
    if primary_pass and secondary_pass and fpr == 0.0:
        return "PASS"
    elif primary_pass and pattern_rate >= 60.0:
        return "PARTIAL_PASS"
    else:
        return "FAIL"
```

**Criteria:**
- PASS: gap ≥ 40pp AND pattern layer ≥ 80% on C1/C2 AND fpr = 0%
- PARTIAL_PASS: gap ≥ 40pp AND pattern layer ≥ 60%
- FAIL: gap < 40pp

---

## 5. Edge Case Handling

### Empty Test Suite

```python
if not test_cases:
    raise ValueError("Empty test suite - cannot compute metrics")
```

### All Valid Cases (No Violations)

```python
if total_violations == 0:
    # Cannot compute detection rate without violations
    return DetectionMetrics(total_violations=0, detected=0, detection_rate=0.0)
```

### Mixed Exception Types

```python
# Layer 2: Pattern (Pydantic ValidationError)
except ValidationError as e:
    return {"detected": True, "layer": "pattern", "error": str(e)}

# Layer 3: Contract (icontract ViolationError OR Pydantic ValidationError)
except (ValidationError, ViolationError) as e:
    return {"detected": True, "layer": "contract", "error": str(e)}
```

**Rationale:** `Phase2AOutputWithContracts` inherits from Pydantic, so can raise either exception type.

---

### Test Case Schema Mismatch

```python
# Validate test case structure before running
required_keys = ["phase2a_output", "violation_type", "constraint_violated", "expected_detection"]
for tc in test_cases:
    if not all(k in tc for k in required_keys):
        raise ValueError(f"Invalid test case: {tc['id']} missing required keys")
```

---

## 6. Results Reporting

### Report Structure

```python
def generate_report(results: Dict[str, Any]) -> str:
    """Generate markdown report for 04_validation.md.
    
    Sections:
    1. Detection rate table (baseline vs three-layer)
    2. Per-layer analysis (schema/pattern/contract)
    3. Per-constraint analysis (C1/C2/C3/C4)
    4. Gate verdict
    """
    report = []
    
    # Detection rate table
    report.append("## Detection Rates\n")
    report.append(f"| Condition | Detection Rate | Detected/Total |\n")
    report.append(f"|-----------|----------------|----------------|\n")
    report.append(f"| Schema-only | {results['baseline'].detection_rate:.1f}% | "
                  f"{results['baseline'].detected}/{results['baseline'].total_violations} |\n")
    report.append(f"| Three-layer | {results['three_layer'].detection_rate:.1f}% | "
                  f"{results['three_layer'].detected}/{results['three_layer'].total_violations} |\n")
    report.append(f"| **Gap** | **{results['gap']:.1f}pp** | - |\n\n")
    
    # Per-layer analysis
    report.append("## Per-Layer Detection\n")
    m = results['three_layer']
    report.append(f"- Schema: {m.schema_detected} violations\n")
    report.append(f"- Pattern: {m.pattern_detected} violations\n")
    report.append(f"- Contract: {m.contract_detected} violations\n\n")
    
    # Per-constraint analysis
    report.append("## Per-Constraint Detection\n")
    report.append(f"- C1 (synthetic data): {m.c1_detected}/3\n")
    report.append(f"- C2 (human eval): {m.c2_detected}/3\n")
    report.append(f"- C3 (standard dataset): {m.c3_detected}/2\n")
    report.append(f"- C4 (new benchmark): {m.c4_detected}/3\n\n")
    
    # Gate verdict
    report.append(f"## Gate Verdict: {results['verdict']}\n")
    
    return "".join(report)
```

---

## 7. Data Structures

### Test Case Format

```yaml
id: tc-16
name: Unknown standard dataset (C3 violation)
violation_type: contract  # "schema"|"pattern"|"contract"|"none"
constraint_violated: C3   # "C1"|"C2"|"C3"|"C4"|"none"
phase2a_output:
  research_question: "Can cross-field validation catch mismatches?"
  detailed_question: "Test cross-field constraints in validation"
  reference_papers: []
  hypotheses: [{"h1": "test"}]
  causal_mechanism: {"mechanism": "test"}
  predictions: [{"p1": "test"}]
  dataset_type: standard
  dataset_name: UnknownDataset123  # Not in STANDARD_DATASETS
  model_approach: "test model"
  evaluation_method: automated
expected_detection:
  schema: true      # Passes type/structure checks
  pattern: true     # No keyword violations
  contract: false   # Cross-field logic fails
```

### Results Format

```python
# Per test case result
{
    "detected": bool,       # Was violation caught?
    "layer": str|None,      # "schema"|"pattern"|"contract"|None
    "error": str|None       # Exception message if detected
}

# Aggregated metrics
DetectionMetrics(
    total_violations=25,
    detected=25,
    detection_rate=100.0,
    schema_detected=10,
    pattern_detected=10,
    contract_detected=5,
    c1_detected=3,
    c2_detected=3,
    c3_detected=2,
    c4_detected=3
)
```

---

## 8. Existing Validation Infrastructure (h-m1)

### API Signatures (From Actual Code)

**Schema Layer:**
```python
# src/validation/schemas.py
class Phase2AOutput(BaseModel):
    research_question: str
    detailed_question: str
    reference_papers: List[Dict]
    hypotheses: List[Dict]
    causal_mechanism: Dict
    predictions: List[Dict]
    dataset_type: Literal["standard", "custom", "programmatic-api"]
    dataset_name: str
    model_approach: str
    evaluation_method: str
```

**Pattern Layer:**
```python
# src/validation/patterns.py
class Phase2AOutputWithPatterns(Phase2AOutput):
    @field_validator("dataset_name")
    @classmethod
    def validate_no_synthetic(cls, v: str) -> str:
        """C1: No synthetic data."""
        if re.search(r"synthetic|simulated|generated", v, re.IGNORECASE):
            raise ValueError("C1 violation: synthetic data forbidden")
        return v
    
    @field_validator("evaluation_method")
    @classmethod
    def validate_no_human_eval(cls, v: str) -> str:
        """C2: No human evaluation."""
        forbidden = ["human", "manual", "annotator", "labeler"]
        if any(kw in v.lower() for kw in forbidden):
            raise ValueError("C2 violation: human evaluation forbidden")
        return v
```

**Contract Layer:**
```python
# src/validation/contracts.py
class Phase2AOutputWithContracts(Phase2AOutputWithPatterns):
    @ensure(lambda self: self.dataset_type != "standard" or self.dataset_name in STANDARD_DATASETS,
            "C3 violation: unknown standard dataset")
    def model_post_init(self, __context) -> None:
        """Enforce contracts after initialization."""
        super().model_post_init(__context)
        self._validate_no_new_benchmarks()
    
    def _validate_no_new_benchmarks(self) -> None:
        """C4: Benchmark name must be in existing list."""
        if "benchmark" in self.evaluation_method.lower():
            benchmark_mentioned = any(
                b.lower() in self.evaluation_method.lower()
                for b in EXISTING_BENCHMARKS
            )
            if not benchmark_mentioned:
                raise ViolationError("C4 violation: new benchmark not allowed")
```

**Constants:**
```python
# src/validation/constants.py
STANDARD_DATASETS = ["MNIST", "CIFAR-10", "CIFAR-100", "ImageNet", "COCO", ...]
EXISTING_BENCHMARKS = ["GLUE", "SuperGLUE", "SQuAD", "COCO", "ImageNet"]
```

---

## 9. Implementation Tasks

### Task Breakdown

**Total Budget:** Tier 0 (~100 LOC)

| ID | Task | LOC | Description |
|----|------|-----|-------------|
| L-1 | Test case generator | 30 | Extend to 30 cases with 10/10/5/5 distribution |
| L-2 | Schema-only runner | 10 | Baseline validation (schema layer only) |
| L-3 | Three-layer runner | 20 | Fail-fast validation across all layers |
| L-4 | Metrics calculation | 25 | Detection rate, gap, FPR, per-layer/constraint |
| L-5 | Experiment runner | 15 | Main loop, load YAML, run conditions, report |

**Total:** 100 LOC

---

## 10. Expected Performance

### Baseline (Schema-Only)

| Violation Type | Count | Detected | Rate |
|----------------|-------|----------|------|
| Schema | 10 | 10 | 100% |
| Pattern | 10 | 0 | 0% |
| Contract | 5 | 0 | 0% |
| **Total** | **25** | **10** | **40%** |

### Three-Layer

| Layer | Violations Caught | Cumulative Rate |
|-------|-------------------|-----------------|
| Schema | 10 | 40% |
| Pattern | 10 | 80% |
| Contract | 5 | 100% |

### Detection Gap

```
Gap = 100% - 40% = 60 percentage points
Target: >= 40pp
Result: PASS (60pp > 40pp)
```

---

## Document Metadata

**Implementation Complexity:** Tier 0 (reuse h-m1 infrastructure)  
**Estimated Effort:** 2-3 hours  
**Risk Level:** LOW  
**Dependencies:** h-m1 validation layers (validated)  
**Next Phase:** Implementation (Phase 4)

---

**Status:** Complete  
**Ready for Implementation:** Yes
