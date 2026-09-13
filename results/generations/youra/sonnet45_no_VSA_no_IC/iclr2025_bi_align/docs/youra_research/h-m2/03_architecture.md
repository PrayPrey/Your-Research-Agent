# Architecture Specification: Multi-Layer Validation Detection (h-m2)

**Hypothesis ID:** h-m2  
**Type:** MECHANISM (Proof-of-Concept)  
**Date:** 2026-08-20  
**Phase:** 3 - Architecture Design

Applied: Reuse h-m1 validation infrastructure (schema/pattern/contract layers)

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase + base_hypothesis (h-m1)  
**Status:** Validation layers implemented and tested in h-m1  
**Analyzed Path:** `src/validation/*`, `tests/phase_boundary_validation/*`  
**Findings:** Three-layer architecture exists, test generator present, no new validators needed.

---

## 1. System Overview

**Mission:** Measure detection rate gap between schema-only and three-layer validation.

**Scope:** Test harness only (no new validation logic).

**Components:**
- Test suite: 30 adversarial cases (extend from existing 20)
- Experiment runner: Two conditions (baseline vs proposed)
- Metrics calculator: Detection rates, gap, per-layer/per-constraint analysis

---

## 2. Module Specifications

### 2.1 Test Suite Generator (`tests/h_m2/generate_test_cases_h_m2.py`)

**Dependencies:** `src/validation/constants.py`

```python
def generate_schema_violations() -> List[Dict]:
    """10 cases: type errors, missing fields, literal enum violations."""
    ...

def generate_pattern_violations() -> List[Dict]:
    """10 cases: C1/C2 keyword violations."""
    ...

def generate_contract_violations() -> List[Dict]:
    """5 cases: C3/C4 cross-field/state violations."""
    ...

def generate_valid_cases() -> List[Dict]:
    """5 cases: should pass all layers."""
    ...

def save_test_suite(cases: List[Dict], path: str) -> None:
    """Write to YAML."""
    ...
```

### 2.2 Experiment Runner (`experiments/h_m2_multilayer_validation.py`)

**Dependencies:** `src/validation/{schemas,patterns,contracts}`, `tests/h_m2/test_cases_h_m2.yaml`

```python
def run_baseline_condition(test_case: Dict) -> Dict:
    """Schema-only validation.
    
    Returns: {detected: bool, layer: None}
    """
    ...

def run_three_layer_condition(test_case: Dict) -> Dict:
    """Schema → Pattern → Contract (fail-fast).
    
    Returns: {detected: bool, layer: "schema"|"pattern"|"contract"|None}
    """
    ...

def calculate_metrics(baseline_results: List[Dict], 
                     three_layer_results: List[Dict],
                     test_cases: List[Dict]) -> Dict:
    """Detection rates, gap, per-layer, per-constraint."""
    ...

def generate_report(metrics: Dict, output_path: str) -> None:
    """04_validation.md with tables and verdict."""
    ...

def main():
    """Load cases → run both conditions → calculate metrics → report."""
    ...
```

### 2.3 Validation Infrastructure (Existing - No Changes)

**From h-m1:**

`src/validation/schemas.py` - Layer 1
```python
class Phase2AOutput(BaseModel):
    research_question: str = Field(min_length=10)
    dataset_type: Literal["standard", "custom", "programmatic-api"]
    dataset_name: str
    evaluation_method: str
    # ... other fields
```

`src/validation/patterns.py` - Layer 2
```python
class Phase2AOutputWithPatterns(Phase2AOutput):
    @field_validator("dataset_name")
    @classmethod
    def validate_no_synthetic(cls, v: str) -> str: ...
    
    @field_validator("evaluation_method")
    @classmethod
    def validate_no_human_eval(cls, v: str) -> str: ...
```

`src/validation/contracts.py` - Layer 3
```python
class Phase2AOutputWithContracts(Phase2AOutputWithPatterns):
    @ensure(lambda self: self.dataset_type != "standard" or 
            self.dataset_name in STANDARD_DATASETS)
    def model_post_init(self, __context) -> None: ...
    
    def _validate_no_new_benchmarks(self) -> None: ...
```

---

## 3. Data Flow

```
Test Generation:
  generate_test_cases_h_m2.py → test_cases_h_m2.yaml (30 cases)
                                    ↓
Experiment Execution:
  Load cases → ┬─→ Baseline Condition (schema-only)
               └─→ Three-Layer Condition (schema→pattern→contract)
                                    ↓
Metrics Calculation:
  Detection rates (baseline, three-layer, gap)
  Per-layer analysis (schema/pattern/contract contributions)
  Per-constraint analysis (C1/C2/C3/C4)
                                    ↓
Report Generation:
  04_validation.md (tables, verdict)
```

---

## 4. File Structure

```
experiments/
├── h_m2_multilayer_validation.py       # Main experiment runner (~150 LOC)

tests/
└── h_m2/
    ├── generate_test_cases_h_m2.py     # Test suite generator (~200 LOC)
    └── test_cases_h_m2.yaml            # 30 adversarial cases (generated)

src/validation/  # (existing, no changes)
├── schemas.py                          # Layer 1: Schema
├── patterns.py                         # Layer 2: Pattern (C1/C2)
├── contracts.py                        # Layer 3: Contract (C3/C4)
└── constants.py                        # STANDARD_DATASETS, EXISTING_BENCHMARKS

docs/youra_research/h-m2/
└── 04_validation.md                    # Results report (generated)
```

---

## 5. Integration Points

### 5.1 With h-m1 Infrastructure

**Reused Components:**
- `src/validation/schemas.py` - Schema layer (unchanged)
- `src/validation/patterns.py` - Pattern validators (unchanged)
- `src/validation/contracts.py` - Contract enforcement (unchanged)
- `src/validation/constants.py` - Constraint definitions (unchanged)

**Import Paths:**
```python
from src.validation.schemas import Phase2AOutput
from src.validation.patterns import Phase2AOutputWithPatterns
from src.validation.contracts import Phase2AOutputWithContracts
from src.validation.constants import STANDARD_DATASETS, EXISTING_BENCHMARKS
```

### 5.2 Test Suite Extension

**Existing:**
- `tests/phase_boundary_validation/generate_test_cases.py` (20 cases)
- `tests/phase_boundary_validation/test_cases.yaml`

**New:**
- `tests/h_m2/generate_test_cases_h_m2.py` (30 cases)
- Distribution: 10 schema, 10 pattern, 5 contract, 5 valid

---

## 6. Validation Logic

### 6.1 Baseline Condition (Schema-Only)

```python
def run_baseline_condition(test_case: Dict) -> Dict:
    try:
        from src.validation.schemas import Phase2AOutput
        Phase2AOutput(**test_case["phase2a_output"])
        return {"detected": True, "layer": None}
    except Exception:
        return {"detected": False, "layer": None}
```

**Expected Detection:**
- Schema violations: 10/10 (100%)
- Pattern violations: 0/10 (0%)
- Contract violations: 0/5 (0%)
- **Overall:** 10/25 = 40%

### 6.2 Three-Layer Condition

```python
def run_three_layer_condition(test_case: Dict) -> Dict:
    data = test_case["phase2a_output"]
    
    # Layer 1: Schema
    try:
        from src.validation.schemas import Phase2AOutput
        Phase2AOutput(**data)
    except Exception:
        return {"detected": False, "layer": "schema"}
    
    # Layer 2: Pattern
    try:
        from src.validation.patterns import Phase2AOutputWithPatterns
        Phase2AOutputWithPatterns(**data)
    except Exception:
        return {"detected": False, "layer": "pattern"}
    
    # Layer 3: Contract
    try:
        from src.validation.contracts import Phase2AOutputWithContracts
        obj = Phase2AOutputWithContracts(**data)
        return {"detected": True, "layer": "contract"}
    except Exception:
        return {"detected": False, "layer": "contract"}
```

**Expected Detection:**
- Schema violations: 10/10 caught at Layer 1
- Pattern violations: 10/10 caught at Layer 2
- Contract violations: 5/5 caught at Layer 3
- **Overall:** 25/25 = 100%

---

## 7. Metrics Specification

### 7.1 Primary Metric

**Detection Gap:**
```
gap = (three_layer_rate - baseline_rate)
    = (25/25 × 100%) - (10/25 × 100%)
    = 100% - 40%
    = 60 percentage points
```

**Success:** gap ≥ 40pp

### 7.2 Secondary Metrics

**Per-Layer Detection:**
```python
schema_rate = schema_caught / total_schema_violations
pattern_rate = pattern_caught / total_pattern_violations
contract_rate = contract_caught / total_contract_violations
```

**Per-Constraint Detection:**
```python
c1_rate = c1_caught / total_c1_violations  # Pattern layer (synthetic data)
c2_rate = c2_caught / total_c2_violations  # Pattern layer (human eval)
c3_rate = c3_caught / total_c3_violations  # Contract layer (dataset membership)
c4_rate = c4_caught / total_c4_violations  # Contract layer (benchmark whitelist)
```

**False Positive Rate:**
```python
fpr = valid_rejected / total_valid_cases
```

Target: 0% (all 5 valid cases must pass)

---

## 8. Report Structure

### 8.1 Output Format (`04_validation.md`)

**Sections:**
1. Executive Summary (verdict, primary metric)
2. Detection Rate Comparison Table
3. Per-Layer Analysis
4. Per-Constraint Analysis
5. False Positive Check
6. Gate Verdict (PASS/PARTIAL/FAIL)

**Example Table:**
```markdown
| Condition      | Detected | Total | Rate  |
|----------------|----------|-------|-------|
| Schema-Only    | 10       | 25    | 40%   |
| Three-Layer    | 25       | 25    | 100%  |
| **Gap**        | +15      | -     | **60pp** |
```

---

## 9. Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Test Suite Extension | Generate 30-case YAML with 10/10/5/5 distribution | 8 | gen(3) + review(2) + verify(3) |
| A-2 | Experiment Runner | Implement baseline + three-layer conditions | 9 | baseline(2) + three-layer(3) + metrics(4) |
| A-3 | Report Generation | Calculate metrics, generate 04_validation.md | 7 | metrics(3) + tables(2) + verdict(2) |

**Distribution:** Medium(9-13): [A-2], Low(4-8): [A-1, A-3]

**Complexity Key:** gen=generation, review=manual check, verify=coverage/balance, metrics=calculation logic, tables=markdown formatting, verdict=gate logic

---

## 10. Risk Mitigation

### 10.1 Technical Risks

**R1: Ground-truth labels incorrect**
- **Impact:** Wrong detection rates
- **Mitigation:** Manual spot-check 5 sample cases, verify layer-by-layer behavior

**R2: Test suite imbalanced**
- **Impact:** Inflated/deflated detection rates
- **Mitigation:** Automated distribution check (assert 10/10/5/5), adversarial review

### 10.2 Implementation Risks

**R3: Import path errors**
- **Impact:** Validation layers not found
- **Mitigation:** Absolute imports (`from src.validation.schemas import ...`)

**R4: False positives on valid cases**
- **Impact:** FPR > 0%, undermines validation framework
- **Mitigation:** Run 5 valid cases first, halt if any rejected

---

## 11. Success Criteria

**Gate Verdict Logic:**

```python
def determine_verdict(metrics: Dict) -> str:
    gap = metrics["detection_gap"]
    pattern_rate = metrics["pattern_layer_rate"]
    contract_rate = metrics["contract_layer_rate"]
    fpr = metrics["false_positive_rate"]
    
    if gap >= 40 and pattern_rate >= 0.8 and contract_rate == 1.0 and fpr == 0:
        return "PASS"
    elif gap >= 40 and pattern_rate >= 0.6:
        return "PARTIAL"
    else:
        return "FAIL"
```

**Expected Outcome:** PASS (60pp gap, 100% pattern/contract, 0% FPR)

---

## 12. Timeline Estimate

**Total:** 3 hours (Tier 0 PoC)

- Test suite generation: 1 hour
- Experiment runner: 1.5 hours
- Execution + report: 0.5 hours

**Justification:** Reuses all h-m1 infrastructure, no new validation logic.

---

## Appendices

### A.1 Test Case Schema

```yaml
id: tc-{nn}
name: {descriptive name}
violation_type: {schema|pattern|contract|none}
constraint_violated: {C1|C2|C3|C4|none}
phase2a_output:
  research_question: {string, min_length=10}
  detailed_question: {string}
  reference_papers: [{title: str, year: int}]
  hypotheses: [{id: str, statement: str}]
  causal_mechanism: {cause: str, effect: str}
  predictions: [{metric: str, value: float}]
  dataset_type: {standard|custom|programmatic-api}
  dataset_name: {string}
  model_approach: {string}
  evaluation_method: {string}
expected_detection:
  schema: {true|false}
  pattern: {true|false}
  contract: {true|false}
```

### A.2 Constraint Enforcement Map

| Constraint | Layer | Mechanism | Field |
|------------|-------|-----------|-------|
| C1 - No Synthetic Data | Pattern | `@field_validator` regex | `dataset_name` |
| C2 - No Human Eval | Pattern | `@field_validator` keyword blacklist | `evaluation_method` |
| C3 - Standard Dataset Membership | Contract | `@ensure` cross-field | `dataset_type` + `dataset_name` |
| C4 - No New Benchmarks | Contract | Method check + whitelist | `evaluation_method` |

### A.3 External Dependencies (h-m1)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| Phase2AOutput | `from src.validation.schemas import Phase2AOutput` | `src/validation/schemas.py` |
| Phase2AOutputWithPatterns | `from src.validation.patterns import Phase2AOutputWithPatterns` | `src/validation/patterns.py` |
| Phase2AOutputWithContracts | `from src.validation.contracts import Phase2AOutputWithContracts` | `src/validation/contracts.py` |
| STANDARD_DATASETS | `from src.validation.constants import STANDARD_DATASETS` | `src/validation/constants.py` |
| EXISTING_BENCHMARKS | `from src.validation.constants import EXISTING_BENCHMARKS` | `src/validation/constants.py` |

**Verified from:** Existing h-m1 implementation (VALIDATED)

---

**Document Status:** Complete  
**Ready for Phase 4:** Yes  
**Next Phase:** Implementation (Coder Agent)
