# Hypothesis Context: h-c3

**Generated:** 2026-07-11
**Hypothesis ID:** h-c3 (H-M3)
**Source:** Phase 2B Verification Plan (Section 2.2)

---

## Hypothesis Information

**Type:** MECHANISM (COMPOSITION)
**Statement:** Chains of contracts (e.g., dataset → preprocess → model → output) propagate failures bidirectionally

**Original Phase 2B Statement:**
Under ML reengineering workflows, if cross-library composition-level contracts validate binding assumptions (device placement, tensor layout consistency), then cross-library interaction defects are detected at environment-stage.

**Rationale:** Tests the third causal step. Many API defects arise from cross-library interactions (Torch + CUDA + Transformers version triads), requiring composition-level validation.

---

## Experimental Setup

### Dataset
**Source:** Jiang et al. 348-Defect Corpus (cross-library interaction defects subset)
**Type:** Retrospective defect corpus analysis
**Focus:** Cross-library version triads (PyTorch + CUDA + Transformers combinations)

### Model
**Type:** Composition-level contract validation framework
**Components:**
- Cross-library binding validators (device placement, tensor layout)
- Version compatibility checkers
- Execution environment validators

---

## Variables

**Independent Variable:** Composition-level contract presence (enabled/disabled)
**Dependent Variable:** Cross-library defect detection rate
**Controlled Variables:**
- Library version combinations
- Device configurations (CPU/GPU/multi-GPU)
- Tensor layout conventions

---

## Verification Protocol

1. Implement composition-level contracts for common library triads (PyTorch + CUDA + Transformers)
2. Deploy to test repos with known cross-library interaction failures
3. Measure detection rate for composition-level defects
4. Validate execution time ≤10s for composition checks
5. Test robustness across version combinations

---

## Success Criteria

**Primary:** Composition contracts detect ≥60% of cross-library interaction defects
**Secondary:**
- Execution time ≤10s
- Applicable to ≥3 distinct repos
- Version stability across ±2 minor releases

---

## Gate Condition

**Type:** SHOULD_WORK
**Pass Condition:** Detection rate ≥60% for cross-library composition defects
**Fail Action:** If detection rate <40%, document as manual curation requirement
**Note:** SHOULD_WORK gate allows continuation with documented limitations

---

## Prerequisites

**Direct Prerequisites:** h-m2 (Metamorphic validation working)
**Indirect Prerequisites:** h-e1 (Contractability validated), h-m1 (Structural validation working)

**All Prerequisites Status:** VALIDATED ✅
- h-e1: 74.76% contractability (EXCEEDS 40% threshold)
- h-m1: Structural contracts working
- h-m2: Metamorphic contracts working

---

## Previous Hypothesis Results

### h-e1 (EXISTENCE - Contractability)
**Key Findings:**
- Overall contractability: 74.76% (95% CI: [69.67%, 79.25%])
- Structural contracts: 95.71% contractable (140/146 defects)
- Metamorphic contracts: 95.24% contractable (100/105 defects)
- **Composition contracts: 0.0% contractable (0/62 defects - version instability)**

**Critical Insight for h-c3:**
Composition-level defects showed 0% contractability in h-e1 due to version instability. This is a HIGH-RISK finding for h-c3 success.

### h-m1 (MECHANISM - Structural Validation)
**Key Findings:**
- Structural contracts detect API violations at import/setup time
- Proven effectiveness on return types, tensor shapes, non-null outputs

### h-m2 (MECHANISM - Metamorphic Validation)
**Key Findings:**
- Metamorphic properties (softmax sums, dropout identity) validated via lightweight probes
- Version-stable mathematical invariants confirmed

---

## Risks & Mitigation

**Risk R3 (High Severity):** Version instability for composition-level contracts
- **Evidence:** h-e1 showed 0% contractability for composition defects (62/62 failed version stability)
- **Affected:** h-c3 directly
- **Mitigation:**
  - Version-Transition Benchmark on 20 real PyTorch/HuggingFace version deltas
  - Focus on LTS library versions only
  - If false positive rate >8%, contracts too brittle for adoption

**Risk R2 (High Severity):** Insufficient documentation for cross-library binding assumptions
- **Mitigation:** Hybrid approach (auto-generation + manual curation)
- **Scope:** Focus on well-documented libraries (PyTorch, HuggingFace)

---

## Expected Challenges

1. **Version Instability:** Cross-library version triads create combinatorial complexity
2. **Binding Assumption Documentation:** Device placement and tensor layout rules often implicit
3. **Execution Time Constraint:** Composition checks across multiple libraries must stay ≤10s
4. **False Positive Rate:** Must maintain <5% false positives despite version combinations

---

## Continuation Context

**Position in DAG:** Level 3 (H-E1 → H-M1 → H-M2 → **h-c3** → H-M4)
**Critical Path:** Yes (blocks h-m4 lifecycle shift validation)
**Gate Impact:** SHOULD_WORK gate - failure documents limitation, doesn't stop pipeline

**Next Steps After h-c3:**
- If PASS: Proceed to h-m4 (Lifecycle shift validation)
- If FAIL: Document composition contracts as manual curation requirement, continue to h-m4

---

*This context file provides Phase 2C with focused information for experiment design.*
*Source: Phase 2B Verification Plan (02b_verification_plan.md, lines 179-209)*
