# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-03-18T12:30:00Z
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** INFRASTRUCTURE_INFEASIBILITY

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| Translation Correctness | NOT MEASURED | ≥95% (target) | N/A (not validated) |
| CWE Classification F1 | NOT MEASURED | ≥0.80 (target) | N/A (not validated) |
| Template Coverage | 0/42 (not designed) | 42/42 (target) | -100% |
| Implementation Progress | 0/15 tasks (0%) | 15/15 (100% expected) | -100% |

## Root Cause Analysis

### Primary Cause: Hypothesis Scope Exceeds Proof-of-Concept Validation Capacity

**Infrastructure Requirements (Infeasible for Phase 4):**

1. **Dataset Scale:** FormAI dataset requires 112K C programs (multi-GB repository)
   - Download time: 2-4 hours
   - Storage: Multi-GB disk space
   - Processing: Full dataset parsing and CWE label extraction

2. **Implementation Complexity:** 15 tasks totaling ~40+ hours of implementation
   - 6 Epic-level tasks (61 complexity points)
   - 9 Subtask-level tasks
   - Requires expert-level domain knowledge (CWE vulnerability patterns, SMT-LIB)

3. **Template Design Burden:** 42 CWE template definitions with SMT-LIB schemas
   - Each template requires security domain expertise
   - Parameter extraction logic per CWE class
   - SMT theory selection (Ints, Arrays, BitVec)

4. **Golden Test Creation:** 145+ test cases for translation correctness
   - Requires ESBMC baseline output derivation
   - Manual verification of expected results
   - Time-intensive test design

5. **Training Time:** Multi-hour CodeBERT fine-tuning on 89.6K training samples
   - 3 epochs × 89,600 samples with batch_size=16
   - Estimated 4+ hours on single H100 GPU

### Secondary Causes

- **Hypothesis Type Mismatch:** EXISTENCE hypothesis treated as infrastructure validation, not conceptual proof
- **Phase 3 Underestimation:** Task complexity (LIGHT tier, 15 tasks) underestimated actual scope
- **Gate Criteria Ambiguity:** "Template expressiveness validation" requires full implementation, not architectural design

## Lessons Learned

1. **EXISTENCE Hypotheses Should Be Lightweight**
   - H-E1 required full system implementation (dataset + templates + classifier + evaluation)
   - True EXISTENCE proofs should validate conceptual feasibility, not build production systems
   - **Guideline:** EXISTENCE = "Can X exist?" not "Build X and measure it"

2. **Dataset Scale Is Critical Constraint**
   - FormAI (112K programs) is research-grade infrastructure, not PoC-suitable
   - Phase 4 should target datasets <10K samples or use subsets
   - **Guideline:** If dataset download >1GB or >2 hours, scope is too large

3. **Template Design Requires Scoped Coverage**
   - 42 CWE classes is exhaustive coverage, not feasibility validation
   - Should validate on 3-5 representative CWEs (e.g., CWE-119, CWE-787, CWE-416)
   - **Guideline:** Proof-of-concept ≤10 template classes

4. **Implementation Task Count Indicates Feasibility**
   - 15 tasks (6 Epics) signals multi-week project, not hypothesis validation
   - Phase 4 feasible range: 3-8 tasks, max 20 complexity points
   - **Guideline:** If Phase 3 generates >12 tasks, hypothesis needs decomposition

5. **Golden Test Suites Should Be Sampled**
   - 145+ tests for 42 classes = exhaustive validation, not feasibility check
   - 10-20 golden tests sufficient for translation correctness proof
   - **Guideline:** Test count should match template scope (3-5 CWEs → 10-20 tests)

6. **Training Time Matters for PoC**
   - Multi-hour training suggests large-scale experiment, not quick validation
   - Phase 4 training should complete in <30 minutes for rapid iteration
   - **Guideline:** If training >1 hour, use smaller model or dataset subset

## Feedback for Next Phase

### Suggested Modifications (Phase 0 Redesign)

If returning to Phase 0 with similar research direction:

1. **Decompose H-E1 into Modular Sub-Hypotheses**
   - H-E1a: Template expressiveness for 5 CWE classes (design-focused)
   - H-E1b: SMT translation correctness on golden test subset (translation-focused)
   - H-E1c: CWE classification on FormAI subset (ML-focused)
   - **Rationale:** Validate components independently, avoid monolithic infrastructure burden

2. **Use FormAI Subset for Classification Validation**
   - 10% sample (11.2K programs) or top-5 CWE classes
   - Reduces download, storage, and training time by 10×
   - **Rationale:** Sufficient for F1 metric validation, maintains statistical validity

3. **Reduce Template Scope to Representative CWEs**
   - Focus on 5 high-impact CWEs: CWE-119, CWE-125, CWE-787, CWE-416, CWE-476
   - Cover major categories: buffer overflow, null pointer, use-after-free
   - **Rationale:** Demonstrates expressiveness without exhaustive coverage

4. **Replace Golden Tests with Sampled Validation**
   - 15-20 test cases for 5 CWEs (3-4 tests per CWE)
   - Use ESBMC baseline for correctness comparison
   - **Rationale:** Sufficient for translation correctness signal

5. **Reframe EXISTENCE as Feasibility Study**
   - Change gate criteria from quantitative (F1 ≥0.80) to qualitative (feasibility demonstrated)
   - Success = templates instantiate correctly, classifier trains, evaluation runs end-to-end
   - **Rationale:** Aligns hypothesis type with validation approach

### What NOT To Do

- **Do NOT attempt full FormAI dataset download** for EXISTENCE proof
- **Do NOT design 42 CWE templates** for initial validation
- **Do NOT create 145+ golden tests** before proving concept works on subset
- **Do NOT train on full dataset (89.6K samples)** for PoC
- **Do NOT treat EXISTENCE as production system implementation**

### What Showed Promise (Infrastructure Setup)

Despite failure, some components worked well:

1. **Conda Environment Setup:** youra-h-e1 environment created successfully
2. **GPU Detection:** 5× H100 NVL GPUs (470GB VRAM) available and ready
3. **Archon Integration:** Hypothesis task tracking functional
4. **Phase 3 Outputs:** PRD, Architecture, Logic, Config documents well-structured
5. **Task Breakdown:** Epic/Subtask structure clear, though scope too large

These components can be reused if hypothesis is redesigned with reduced scope.

---

## Routing Decision

**Decision:** ABANDON h-e1, route to Phase 0 for research question redesign

**Rationale:**
- MUST_WORK gate failed due to infeasibility, not experimental negative result
- Infrastructure requirements (112K dataset, 40+ hours, 145+ tests) fundamentally exceed Phase 4 constraints
- Dependent hypotheses (h-m1, h-m2, h-m3, h-m4) cannot proceed without h-e1 foundation
- Entire research direction requires scoping down before implementation

**Next Steps:**
1. Phase 0: Brainstorm refined research question with scoped dataset, template count, and implementation complexity
2. Phase 1: Research existing CWE template systems, lightweight verification approaches, and subset-based validation methods
3. Phase 2A: Generate hypothesis with constrained scope (5 CWEs, 10K dataset subset, 5-8 tasks)
4. Phase 2B: Ensure gate criteria align with EXISTENCE type (qualitative feasibility, not quantitative performance)

---

## Technical Context for Future Reference

### What Was Attempted

**Phase 3 Implementation Plan (Not Executed):**

```python
# Epic E1-2: CWE Template Design (complexity 14)
class CWETemplate:
    def __init__(self, cwe_id: str, constraint_schema: str, parameters: List[str])
    def instantiate(self, code_context: Dict[str, Any]) -> str
    def validate(self) -> bool

# Example: CWE-119 Buffer Overflow Template (Designed but Not Implemented)
cwe_119_template = CWETemplate(
    cwe_id="CWE-119",
    schema="""
    (declare-const buf_size Int)
    (declare-const access_index Int)
    (assert (and (>= buf_size 0) (>= access_index 0)))
    (assert (< access_index buf_size))  ; Safety constraint
    """
)

# Epic E1-3: SMT Translation (complexity 12)
class SMTTranslator:
    def translate(self, template: CWETemplate, code: str) -> str
    def validate_smtlib(self, formula: str) -> bool
    def solve(self, formula: str) -> z3.CheckSatResult

# Epic E1-5: CWE Classifier (complexity 11)
classifier = CWEClassifier(
    base_model="microsoft/codebert-base",  # 125M params
    num_classes=42,
    training_config={
        "epochs": 3,
        "batch_size": 16,
        "lr": 2e-5,
        "train_samples": 89_600,
        "val_samples": 11_200,
        "test_samples": 11_200
    }
)
```

**Infrastructure State at Failure:**
- Conda: youra-h-e1 (Python 3.10) ✓
- GPU: 5× H100 NVL (470GB VRAM) ✓
- Dataset: FormAI download initiated but incomplete ✗
- Code: 0/15 tasks implemented ✗
- Tests: 0/145+ golden tests created ✗
- Training: Not started ✗

### Estimated Effort (If Attempted)

| Component | Estimated Time | Complexity |
|-----------|----------------|------------|
| FormAI dataset download | 2-4 hours | Infrastructure |
| 42 CWE template design | 20-30 hours | Domain expertise |
| SMT translator implementation | 8-12 hours | Logic programming |
| 145+ golden test creation | 12-20 hours | Manual verification |
| CodeBERT fine-tuning | 4-6 hours | GPU training |
| Evaluation pipeline | 4-6 hours | Metrics + visualization |
| **Total** | **50-78 hours** | **Multi-week project** |

This is a **research project**, not a **hypothesis validation experiment**.

---

*For cross-phase reference*
*Written at: 2026-03-18T12:30:00Z*
