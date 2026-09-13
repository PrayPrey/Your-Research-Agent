# Architecture: Contract Expressiveness Validation

**Hypothesis:** h-m1  
**Type:** MECHANISM  
**Tier:** 1 (PoC)  
**Date:** 2026-08-20

Applied: Standard validation framework pattern

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase  
**Status:** Validation framework exists in `src/validation/`  
**Analyzed Path:** `src/validation/`  
**Findings:** Three-layer validation (schemas.py → patterns.py → contracts.py) already implemented. Reuse structure, focus on test suite.

---

## Component Structure

### Constants (`src/validation/constants.py`)

**Status:** EXISTS - reuse as-is

```python
STANDARD_DATASETS: List[str]  # Known datasets for C3
EXISTING_BENCHMARKS: List[str]  # Known benchmarks for C4
```

### Schema-Only Baseline (`src/validation/schemas.py`)

**Status:** EXISTS - minimal extension

```python
class Phase2AOutput(BaseModel):
    research_question: str
    dataset_type: Literal["standard", "custom", "programmatic-api"]
    dataset_name: str  # Cannot check C1 (keyword pattern)
    evaluation_method: str  # Cannot check C2 (keyword blacklist)
```

### Pattern Layer (`src/validation/patterns.py`)

**Status:** EXISTS - skip for experiment (not schema-only)

### Contract Layer (`src/validation/contracts.py`)

**Status:** EXISTS - verify C1-C4 coverage

```python
class Phase2AOutputWithContracts(Phase2AOutputWithPatterns):
    @ensure(lambda self: self.dataset_type != "standard" or self.dataset_name in STANDARD_DATASETS)
    def model_post_init(self, __context) -> None: ...
    
    def _validate_no_new_benchmarks(self) -> None: ...
```

### Test Cases (`tests/h_m1/test_cases.yaml`)

**Status:** NEW - create 5 test cases

```yaml
test_cases:
  - id: TC-M1-01
    constraint_violated: C1
    input: {dataset_name: "SyntheticDataset2024", ...}
    expected: {schema_detects: false, contract_detects: true}
```

### Coverage Experiment (`tests/h_m1/run_coverage_test.py`)

**Status:** NEW

```python
def run_coverage_test() -> dict:
    """Compare schema vs contract detection rates."""
    ...
    return {"schema_coverage": float, "contract_coverage": float, "gap": float}
```

---

## Data Flow

```
Test Cases (YAML)
  ↓
Schema-Only Validator (Phase2AOutput)
  ↓ detection count
Contract Validator (Phase2AOutputWithContracts)  
  ↓ detection count
Coverage Calculation
  ↓
04_validation.md
```

---

## Constraint Mapping

| Constraint | Schema-Only | Pattern Layer | Contract Layer |
|------------|-------------|---------------|----------------|
| C1: No "synthetic" keyword | ❌ | ✅ field_validator | ✅ inherited |
| C2: No "human" keyword | ❌ | ✅ field_validator | ✅ inherited |
| C3: Standard dataset membership | ❌ | ❌ | ✅ @ensure |
| C4: No new benchmarks | ❌ | ❌ | ✅ method |

**Note:** Pattern layer uses `field_validator` (not schema-only). For this experiment:
- **Schema-only baseline:** `Phase2AOutput` alone (0/4 constraints)
- **Contract-based:** `Phase2AOutputWithContracts` (4/4 via patterns + contracts)

---

## File Structure

```
src/validation/
├── __init__.py          [EXISTS]
├── constants.py         [EXISTS - reuse]
├── schemas.py           [EXISTS - reuse]
├── patterns.py          [EXISTS - reuse]
└── contracts.py         [EXISTS - verify]

tests/h_m1/
├── __init__.py          [NEW]
├── test_cases.yaml      [NEW - 5 cases]
└── run_coverage_test.py [NEW - experiment]
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Create test cases | Define TC-M1-01 through TC-M1-05 in YAML | 6 | structure(1)+C1-C4(4)+valid(1) |
| A-2 | Implement coverage runner | Loop test cases, count detections | 8 | load(2)+schema-test(2)+contract-test(2)+report(2) |
| A-3 | Verify constraint coverage | Confirm C1-C4 in contracts.py | 4 | read(1)+C3-check(2)+C4-check(1) |
| A-4 | Generate validation report | 04_validation.md with metrics | 6 | template(2)+metrics(2)+analysis(2) |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2], Low(4-8): [A-1, A-3, A-4]

**Total:** 24 complexity points (4 tasks)

---

## Success Criteria

**Gate Criteria:**
- Contract coverage ≥ 100% (4/4 constraints)
- Schema coverage < 50% (0-1/4 constraints)
- Expressiveness gap ≥ 75pp

**Expected Results:**
- Schema-only: 0/4 (0%)
- Contract-based: 4/4 (100%)
- Gap: 100pp

---

## Dependencies

**Internal:**
- `src/validation/constants.py` → `contracts.py`
- `schemas.py` → `patterns.py` → `contracts.py`

**External:**
- pydantic ≥2.0
- icontract ≥2.0
- pytest ≥7.0
- pyyaml ≥6.0

---

## Risk Mitigation

**R1: Schema unexpectedly expresses constraints**
- Mitigation: Test `Phase2AOutput` directly (not patterns layer)
- Detection: Verify 0 violations caught by schema alone

**R2: Contract coverage <100%**
- Mitigation: Verify C1-C4 in existing contracts.py
- Detection: Run coverage test, trace failures

---

**Document Status:** Complete  
**Next Phase:** Phase 4 Implementation (Coder)
