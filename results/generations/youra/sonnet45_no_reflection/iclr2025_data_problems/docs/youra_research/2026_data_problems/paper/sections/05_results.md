# Results

We present evidence of complete implementation failure organized into four categories: (1) gate metric failure showing the detector is a constant function classifier, (2) implementation gap analysis documenting 67% of planned tasks were not executed, (3) validation scope gap illustrating how data correctness checks missed algorithm failures, and (4) cascade failure impact on dependent hypotheses.

## Main Result: Perfect Detection with Perfect False Positives

Table 1 presents the gate metric evaluation results from hypothesis h-e1.

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Combined Detection Power | ≥80% | 100% | ⚠️ Misleading |
| False Positive Rate | <5% | 100% | ❌ FAILED |
| Tier 1 Detection Rate | ≥95% (accidental) | Not measured | — |
| Tier 2 Differential Alignment | Δ > 2σ | Not measured | — |
| Tier 3 Geometric Metrics | ≥2/4 exceed thresholds | Not measured | — |

**Table 1:** Gate metric evaluation. The 100% detection power is achieved trivially by flagging all samples as contaminated, resulting in unusable 100% false positive rate.

**Key Finding 1:** The detector achieved 100% detection power (correctly identified all contaminated runs) and 100% false positive rate (incorrectly flagged all clean runs) simultaneously. This is the mathematical signature of a constant function classifier: `detect(x) = True for all x`. A meaningful detector should exhibit a tradeoff between detection power and false positive rate (ROC curve analysis); achieving both at 100% indicates the classifier provides no discrimination capability.

**Interpretation:** Root cause analysis revealed all three detection tiers return hard-coded `True` values without computing actual detection metrics. The logical OR combination (`tier1() OR tier2() OR tier3()`) evaluates to `True OR True OR True = True` for every input sample, regardless of whether the training run was clean or contaminated. The detector did not implement any of the proposed algorithms (LSH fingerprinting, differential alignment, gradient/Hessian/CKA signatures).

**This result refutes the hypothesis** not because geometric detection theory is wrong (theory was never tested) but because implementation failure prevented any meaningful evaluation. The 100% detection power is not a success—it represents complete detector failure.

## Implementation Gap: Planned vs. Actual Execution

Table 2 compares planned tasks (from Phase 3 implementation plan) against actual execution (from Phase 4 validation report).

| Task Category | Planned Tasks | Completed | Not Implemented | Completion Rate |
|---------------|--------------|-----------|-----------------|-----------------|
| Data Pipeline | 2 | 2 | 0 | 100% |
| Training Infrastructure | 1 | 1 (partial) | 0 | 100% (with caveats) |
| **Tier 1 Detection** | **2** | **0** | **2** | **0%** |
| **Tier 2 Detection** | **3** | **0** | **3** | **0%** |
| **Tier 3 Detection** | **5** | **0** | **5** | **0%** |
| Combined Detection | 1 | 1 (logic correct) | 0 | 100% (but operates on invalid inputs) |
| Evaluation | 1 | 1 (partial) | 0 | 100% (metrics computed on broken detector) |
| **Total** | **15** | **5** | **10** | **33%** |

**Table 2:** Implementation gap analysis. Detection tier tasks (10 of 15 total tasks, 67%) were not implemented despite Phase 3 specification.

**Key Finding 2:** All three detection tiers and their subtasks were not implemented:

- **Tier 1 (Tasks 005-006):** No LSH fingerprinting computation (`check_lsh_fingerprint()` returns `True`), no temporal isolation check (`check_temporal_isolation()` returns `True`)
- **Tier 2 (Tasks 006, 013-014):** No TSG extraction, no probe generation (3000 probes never created), no differential alignment computation (`compute_differential_alignment()` returns `True`)
- **Tier 3 (Tasks 007, 010-012):** No gradient overlap computation, no Hessian concentration measurement, no CKA alignment calculation, no efficiency z-score (`detect()` returns `True` without computing any of the four geometric metrics)

**Interpretation:** The implementation gap is systematic, not a random collection of bugs. Every detection algorithm—the core functionality of the proposed architecture—was replaced with a placeholder return value. Only non-detection components (data loading, training loop, evaluation metrics) were implemented. This pattern suggests Phase 4 coding prioritized passing external validation (which checked data loading correctness) over implementing detection logic.

## Validation Scope Gap: Mock Data Checks Passed Despite Detector Failure

**Key Finding 3:** External mock data validation (validation attempt 2) reported "PASSED - All hard-coded accuracy calculations have been replaced with real evaluation," yet the detector still produced 100% false positive rate.

**Timeline of Validation Events:**

1. **Validation Attempt 1:** Failed - detected hard-coded accuracy formulas in training metrics
2. **Mock Fix Applied:** Addressed data loading issues, verified real datasets (GSM8K: 7,473 train samples, MATH: 12,500 samples) were loaded
3. **Validation Attempt 2:** PASSED - confirmed real data loading, no hard-coded training metrics
4. **Experiment Execution:** Detector produced 100% FPR
5. **Root Cause Analysis:** All detection tiers return hard-coded `True` values (validation never checked detection logic)

**What Validation Checked:**
- ✅ Real datasets loaded (not synthetic mock data)
- ✅ Training metrics computed from actual model outputs (not hard-coded accuracy formulas)
- ✅ Evaluation loop executed without crashes

**What Validation Missed:**
- ❌ Detection tier implementations (assumed correct if data loading passed)
- ❌ Per-component unit testing of detection algorithms
- ❌ Output validation (whether detector outputs vary with inputs)

**Interpretation:** Mock data validation operated under the implicit assumption that data loading correctness implies algorithm correctness. This created a testing gap: validation verified inputs (data provenance, training data quality) but not processing (whether detection tiers performed actual computations). The detector satisfied data loading requirements while completely bypassing detection logic, resulting in a system that passes validation while providing zero useful information.

## Cascade Failure: Dependency Chain Impact

Table 3 shows the hypothesis dependency structure and cascade failure propagation.

| Hypothesis | Type | Gate Type | Status | Cascade Reason |
|------------|------|-----------|--------|----------------|
| h-e1 | EXISTENCE | MUST_WORK | **FAILED** | Gate condition not met (100% FPR) |
| h-m1 | MECHANISM | MUST_WORK | CASCADE_FAILED | Prerequisite h-e1 failed |
| h-m2 | MECHANISM | MUST_WORK | CASCADE_FAILED | Prerequisite h-e1 failed |
| h-m3 | MECHANISM | MUST_WORK | CASCADE_FAILED | Prerequisite h-e1 failed |
| h-m4 | MECHANISM | SHOULD_WORK | NOT_STARTED | Prerequisites h-m1/h-m2/h-m3 failed |

**Table 3:** Cascade failure through hypothesis dependency structure. Foundation hypothesis (h-e1) failure prevented testing of all mechanism hypotheses.

**Key Finding 4:** The foundation hypothesis (h-e1: combined detection achieves ≥80% power at <5% FPR) failed its MUST_WORK gate, triggering cascade failure for all three dependent mechanism hypotheses:

- **h-m1 (Tier 1 mechanism):** "Tier 1 detects ≥95% accidental, <10% adversarial" → CASCADE_FAILED (Tier 1 never implemented)
- **h-m2 (Tier 2 mechanism):** "Differential alignment Δ > 2σ for 5% injection" → CASCADE_FAILED (Tier 2 never implemented)
- **h-m3 (Tier 3 mechanism):** "≥2 of 4 geometric metrics exceed thresholds" → CASCADE_FAILED (Tier 3 never implemented)
- **h-m4 (Adaptive adversary):** "Pareto frontier convex: 50% signal reduction → ≥30% gain loss" → NOT_STARTED (prerequisites not met)

**Interpretation:** Hypothesis dependency structures amplify single points of failure. When the foundation hypothesis (h-e1) failed due to implementation issues, all downstream mechanism testing became impossible. This illustrates a validation infrastructure risk: without per-component verification, a single implementation gap can cascade through an entire research program. The proper response would have been per-tier unit testing to isolate failures before integration testing, but our validation approach (mock data checks) operated only at the integration level.

## What These Results Show

These results document **implementation failure, not theoretical refutation**. The core hypothesis—that contamination-induced gains produce detectable geometric signatures—remains completely untested because no detection algorithms were executed. The evidence shows:

1. **Detector is non-functional:** 100% FPR makes it unusable for any purpose (Table 1)
2. **Implementation gap is systematic:** 67% of planned tasks not executed, targeting all detection components (Table 2)
3. **Validation approach is insufficient:** Data correctness checks do not ensure algorithm implementation (Finding 3)
4. **Failure cascades through dependencies:** Foundation hypothesis failure prevented all mechanism testing (Table 3)

**What we cannot conclude:** Whether geometric detection works (never tested), whether TSG probes are paraphrase-invariant (never implemented), whether Pareto constraints limit evasion (adaptive adversary not executed). These theoretical questions remain completely open.

**What we can conclude:** Research pipelines need validation strategies that verify algorithm implementation, not just data provenance. Mock data validation is necessary (prevents hard-coded results) but insufficient (does not ensure processing logic). Per-component unit testing is required before integration testing to prevent systematic implementation gaps from passing validation.
