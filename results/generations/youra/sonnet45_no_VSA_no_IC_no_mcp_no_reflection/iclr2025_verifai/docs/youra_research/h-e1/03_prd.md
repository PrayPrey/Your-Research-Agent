# Product Requirements Document: h-e1 SMT Constraint Extraction

**Date:** 2026-08-28
**Hypothesis ID:** h-e1
**Type:** EXISTENCE (PoC)
**Author:** Phase 3 Implementation Planning

---

## Executive Summary

Validate that static analyzers can extract SMT constraints from LLM-generated typed Python code at ≥90% success rate. This foundation hypothesis tests whether type annotations in LLM code provide sufficient structure for formal verification toolchains.

**Success Metric:** Extraction success rate ≥ 90% on 100 HumanEval programs
**Gate:** MUST_WORK (pivot to neural extraction if failed)

---

## 1. Objective

### Primary Goal
Demonstrate that Pyre static analyzer can extract non-empty SMT constraints from LLM-generated typed Python code with Pydantic annotations.

### Success Criteria
1. **Extraction Success Rate ≥ 90%**: At least 90 out of 100 programs yield extractable constraints
2. **Constraint Semantic Quality > 80%**: Extracted constraints are satisfiable (non-trivial)
3. **Code Executes Without Error**: Full pipeline runs end-to-end

### Gate Condition
MUST_WORK gate: If extraction success < 90%, PIVOT to neural constraint extraction (future H2 work).

---

## 2. Functional Requirements

### FR-1: Dataset Preparation
**Priority:** P0 (Critical)

**Description:** Extend OpenAI HumanEval benchmark with Pydantic type annotations.

**Acceptance Criteria:**
- Load 164 HumanEval problems from HuggingFace datasets
- Select subset of 100 problems for PoC validation
- Augment each problem prompt with Pydantic BaseModel + @validator requirements
- Convert canonical solutions to use Pydantic validators for preconditions
- Save extended dataset to `data/humaneval_pydantic/`

**Input:** HuggingFace `openai_humaneval` dataset
**Output:** Extended dataset with Pydantic annotations (100 problems)

**Example Transformation:**
```python
# Original HumanEval prompt
"from typing import List\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n    \"\"\" Check if in given list of numbers, are any two numbers closer to each other than\n    given threshold.\"\"\""

# Extended prompt (Pydantic)
"from pydantic import BaseModel, validator\nfrom typing import List\n\nclass InputContract(BaseModel):\n    numbers: List[float]\n    threshold: float\n    \n    @validator('threshold')\n    def check_positive(cls, v):\n        assert v > 0, 'threshold must be positive'\n        return v\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n    \"\"\" Check if in given list of numbers, are any two numbers closer to each other than\n    given threshold.\"\"\""
```

**Dependencies:** None

---

### FR-2: LLM Code Generation
**Priority:** P0 (Critical)

**Description:** Generate typed Python implementations using Claude Sonnet 3.5 API.

**Acceptance Criteria:**
- API client configured with `claude-sonnet-3-5-20240620` model
- Temperature: 0.2 (deterministic)
- Max tokens: 512 (sufficient for 10-50 LOC)
- System prompt enforces Pydantic types + bans eval/exec/metaprogramming
- Generate 100 implementations (1 per extended HumanEval problem)
- Save generated code to `outputs/generated_code/`

**System Prompt Template:**
```
Generate typed Python code using Pydantic BaseModel. Include @validator decorators for preconditions. Do not use eval, exec, or metaprogramming. Follow the provided type contract strictly.
```

**Input:** Extended HumanEval prompts (100 problems)
**Output:** 100 LLM-generated Python files with Pydantic annotations

**API Configuration:**
- Model: `claude-sonnet-3-5-20240620`
- Temperature: 0.2
- Max tokens: 512
- Stop sequences: None

**Error Handling:**
- Retry on API timeout (max 3 retries)
- Log failed generations
- Continue with remaining problems

**Dependencies:** FR-1 (Dataset Preparation)

---

### FR-3: Constraint Extraction
**Priority:** P0 (Critical)

**Description:** Extract SMT constraints using Pyre static analyzer.

**Acceptance Criteria:**
- Pyre installed (`pip install pyre-check`)
- Run `pyre analyze --output-format json` on each generated file
- Parse JSON output to extract type constraints
- Count programs with non-empty constraint lists
- Save extraction results to `outputs/constraints/`

**Extraction Logic:**
```python
from pyre_check import analyze_file

def extract_constraints(python_file: str) -> list:
    """
    Extract SMT constraints from typed Python code.
    
    Returns:
        constraints: List of dicts with preconditions/postconditions
                    Empty list if extraction failed
    """
    try:
        analysis = analyze_file(python_file)
        constraints = []
        
        # Extract from Pydantic validators
        for validator in analysis.validators:
            constraint = {
                "type": "precondition",
                "predicate": validator.assertion,
                "field": validator.field_name
            }
            constraints.append(constraint)
        
        # Extract from function signatures
        for func in analysis.functions:
            constraint = {
                "type": "contract",
                "precondition": func.args_types,
                "postcondition": func.return_type
            }
            constraints.append(constraint)
        
        return constraints
    except Exception as e:
        print(f"Extraction failed: {e}")
        return []
```

**Input:** 100 LLM-generated Python files
**Output:** Constraint extraction results (JSON per file)

**Dependencies:** FR-2 (LLM Code Generation)

---

### FR-4: Constraint Quality Verification
**Priority:** P1 (High)

**Description:** Verify extracted constraints are semantically meaningful using Z3 solver.

**Acceptance Criteria:**
- Z3 installed (`pip install z3-solver`)
- Check satisfiability for each extracted constraint
- Count non-trivial constraints (satisfiable, not tautologies)
- Compute constraint quality rate: (non_trivial / total_extracted) × 100

**Quality Check Logic:**
```python
from z3 import Solver, sat, Int, Real

def check_constraint_quality(constraint: dict) -> bool:
    """
    Verify constraint is semantically meaningful.
    
    Returns:
        True if satisfiable (non-trivial), False otherwise
    """
    solver = Solver()
    
    # Convert constraint to Z3 format
    if constraint["type"] == "precondition":
        # Example: threshold > 0
        var = Real(constraint["field"])
        solver.add(var > 0)
    
    result = solver.check()
    return result == sat
```

**Input:** Extracted constraints (from FR-3)
**Output:** Constraint quality rate (%)

**Dependencies:** FR-3 (Constraint Extraction)

---

### FR-5: Metrics Computation
**Priority:** P0 (Critical)

**Description:** Compute primary and secondary metrics.

**Acceptance Criteria:**
- **Primary Metric:** Extraction Success Rate = (programs_with_constraints / 100) × 100
  - Target: ≥ 90%
- **Secondary Metric:** Constraint Semantic Quality = (non_trivial_constraints / total_extracted) × 100
  - Target: > 80%
- Save metrics to `outputs/metrics.json`

**Metrics Output Format:**
```json
{
  "extraction_success_rate": 92.0,
  "programs_with_constraints": 92,
  "total_programs": 100,
  "constraint_quality_rate": 85.3,
  "non_trivial_constraints": 243,
  "total_extracted_constraints": 285,
  "gate_result": "PASS"
}
```

**Gate Evaluation:**
- PASS: `extraction_success_rate >= 90.0`
- FAIL: `extraction_success_rate < 90.0` → Trigger PIVOT

**Dependencies:** FR-3, FR-4

---

### FR-6: Visualization
**Priority:** P1 (High)

**Description:** Generate figures per experiment brief requirements.

**Acceptance Criteria:**

1. **Gate Metrics Comparison** (bar chart) - **MANDATORY**
   - X-axis: Metric names (Extraction Rate, Quality Rate)
   - Y-axis: Percentage
   - Bars: Target (90%, 80%) vs Actual
   - Save to `figures/gate_metrics.png`

2. **Extraction Success by Complexity** (bar chart)
   - X-axis: LOC bins (10-20, 20-30, 30-50)
   - Y-axis: Success rate %
   - Save to `figures/success_by_complexity.png`

3. **Constraint Type Distribution** (pie chart)
   - Categories: Preconditions, Postconditions, Type Contracts
   - Save to `figures/constraint_types.png`

4. **Failure Mode Analysis** (table)
   - Columns: Program ID, Failure Reason
   - Save to `figures/failure_modes.png` (rendered table)

**Dependencies:** FR-5 (Metrics)

---

## 3. Non-Functional Requirements

### NFR-1: Performance
- Total execution time: < 1 hour (100 programs × 15s API + 3s Pyre)
- API rate limiting: 10 requests/minute (Anthropic limits)

### NFR-2: Reproducibility
- Fixed seed for API temperature (0.2)
- Deterministic Pyre analysis
- All outputs timestamped and versioned

### NFR-3: Error Handling
- Graceful API failures (retry + log)
- Pyre analysis errors logged (continue pipeline)
- Constraint extraction failures counted in metrics

### NFR-4: Data Management
- All outputs saved with timestamps
- Directory structure:
  ```
  h-e1/
    data/humaneval_pydantic/         # FR-1 output
    outputs/generated_code/          # FR-2 output
    outputs/constraints/             # FR-3 output
    outputs/metrics.json             # FR-5 output
    figures/                         # FR-6 output
  ```

---

## 4. Technical Constraints

### TC-1: Dependencies
- Python 3.9+
- Pyre static analyzer (`pyre-check`)
- Z3 SMT solver (`z3-solver`)
- Anthropic API (`anthropic`)
- HuggingFace datasets (`datasets`)

### TC-2: API Limits
- Anthropic API key required (environment variable `ANTHROPIC_API_KEY`)
- Rate limit: 10 requests/minute
- Token limit: 512 tokens per generation

### TC-3: Compute Resources
- No GPU required (CPU-only static analysis)
- Estimated RAM: 4GB (Pyre analysis)
- Disk space: 500MB (100 programs + outputs)

---

## 5. Acceptance Criteria Summary

**PoC Pass Conditions:**
1. ✅ Code executes without fatal errors
2. ✅ Extraction success rate ≥ 90%
3. ✅ Constraint quality rate > 80%
4. ✅ All mandatory figures generated

**Gate Evaluation:**
- **PASS:** `extraction_success_rate >= 90.0` → Proceed to H-M1
- **FAIL:** `extraction_success_rate < 90.0` → PIVOT to neural extraction

---

## 6. Out of Scope

- Model training (this is static analysis experiment, not ML training)
- Multi-language support (Python only for PoC)
- Real-world codebase evaluation (HumanEval only)
- Performance optimization (PoC focus on correctness)

---

## 7. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM generates code with eval/exec | Blocks static analysis | System prompt bans metaprogramming; pre-filter code |
| Pyre fails on dynamic Python features | Low extraction rate | Strict Pydantic type requirements in prompts |
| API rate limiting delays execution | Timeout | Batch requests with 6s intervals (10/min limit) |
| HumanEval problems too simple | Overly optimistic results | Include complexity breakdown in analysis |

---

## 8. Phase 4 Implementation Notes

**Entry Conditions:**
- Phase 3 architecture/logic/config documents approved
- Archon task breakdown complete

**Implementation Order:**
1. FR-1: Dataset preparation (no dependencies)
2. FR-2: LLM code generation (depends on FR-1)
3. FR-3: Constraint extraction (depends on FR-2)
4. FR-4: Constraint quality check (depends on FR-3)
5. FR-5: Metrics computation (depends on FR-3, FR-4)
6. FR-6: Visualization (depends on FR-5)

**Validation Checkpoints:**
- After FR-1: Verify 100 Pydantic-extended prompts
- After FR-2: Verify 100 generated files exist
- After FR-3: Verify extraction results JSON files
- After FR-5: Verify metrics.json exists + gate result

**Output Artifacts:**
- Extended HumanEval dataset (100 problems)
- LLM-generated code (100 files)
- Constraint extraction results (100 JSON files)
- Metrics report (metrics.json)
- Figures (4 visualizations)

---

## Appendix: Traceability

| Requirement | Source | Phase 2C Reference |
|-------------|--------|-------------------|
| FR-1 Dataset | Experiment Brief | Dataset section |
| FR-2 LLM Generation | Experiment Brief | Baseline Model section |
| FR-3 Constraint Extraction | Experiment Brief | Proposed Model / Core Mechanism |
| FR-4 Quality Verification | Experiment Brief | Secondary Metrics |
| FR-5 Metrics | Experiment Brief | Evaluation section |
| FR-6 Visualization | Experiment Brief | Visualization Requirements |

All requirements trace back to 02c_experiment_brief.md specifications.
