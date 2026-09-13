# Phase 4.5: Validated Hypothesis Synthesis
# Three-Tier Contamination Detection Architecture

**Research Topic:** Real-World Contamination-Aware Training Pipelines  
**Main Hypothesis ID:** H-ContamGeometry-v1  
**Phase 4.5 Version:** 2.0  
**Generated:** 2026-05-11  
**Pipeline:** Phase 0 → 1 → 2A → 2B → (2C → 3 → 4) × N → **4.5** → [5] → 6 → 6.5

---

## 1. Executive Summary

**Original Hypothesis:** Under finetuning conditions with ≤5% targeted benchmark injection (EAL-style paraphrased contamination), if we apply a three-tier detection architecture combining data-layer filters, Task Signature Graph probes, and geometric trajectory auditing, then we achieve ≥80% combined detection power at <5% false positive rate even against adaptive adversaries, because contamination-induced benchmark gains necessarily produce detectable geometric signatures that cannot be suppressed without sacrificing the performance advantage.

**Refined Hypothesis:** The three-tier contamination detection architecture as implemented failed to achieve usable detection capability due to fundamental implementation issues. All three tiers returned hard-coded True values instead of computing actual detection metrics (LSH fingerprinting, differential alignment, gradient/Hessian signatures), resulting in a detector that flags all samples as contaminated with 100% detection power and 100% false positive rate. This represents complete implementation failure rather than hypothesis refutation - the theoretical detection mechanisms were never actually tested.

**Validation Results:**
- **Predictions Supported:** 0/4 predictions tested (P1 REFUTED due to implementation failure, P2-P4 INCONCLUSIVE - not executed)
- **Gate Status:** FAILED (MUST_WORK gate: combined detection power ≥80% at <5% FPR)
- **Actual Results:** 100% detection power, 100% false positive rate (detector has no discrimination capability)
- **Reflection Outcome:** ROUTED_TO_PHASE_0 for fundamental reconceptualization

**Main Theoretical Insight:** NONE VALIDATED - The experiment revealed that passing mock data validation checks does not guarantee actual algorithm implementation. The critical lesson is that data loading correctness is necessary but insufficient for experiment validity; detection logic itself must be independently validated through per-component unit testing.

**Key Limitations:**
1. **Fundamental Implementation Failure:** All detection algorithms were replaced with hard-coded constant return values
2. **No Actual Testing:** The theoretical hypothesis (contamination produces detectable geometric signatures) remains completely untested
3. **Threshold Calibration Never Performed:** Even if correctly implemented, detection thresholds from Phase 2A hypothesis require empirical validation

**Cascade Impact:** All dependent hypotheses (h-m1, h-m2, h-m3) marked CASCADE_FAILED due to prerequisite h-e1 failure and Phase 0 routing.

---

## 2. Prediction-Result Matrix

### 2.1 Predictions Table

| Prediction ID | Statement | Tested By | Key Metric | Result | Status | Confidence | Evidence |
|--------------|-----------|-----------|------------|--------|--------|------------|----------|
| P1-TierSpecific | Tier 1: ≥95% accidental, <10% adversarial; Tier 2: ≥2σ deviation; Tier 3: ≥2/4 metrics exceed thresholds | h-e1 | Combined detection power @ <5% FPR | 100% power, 100% FPR | **REFUTED** | HIGH | h-e1 validation: Detector flags ALL samples as contaminated (clean and contaminated), providing no discrimination capability |
| P2-ParetoFrontier | Adaptive adversary training reveals convex Pareto frontier: 50% signal suppression costs ≥30% gains | NOT TESTED | Benchmark gain vs detection probability | N/A | **INCONCLUSIVE** | N/A | Phase 3 adaptive adversary experiments not executed due to h-e1 gate failure |
| P3-DomainSpecificity | Structured domains (code/math) achieve ≥80% detection; open-ended NLP 50-60% | NOT TESTED | Detection power by domain | N/A | **INCONCLUSIVE** | N/A | Not tested - experiment scope limited to GSM8K only |
| P4-DifferentialAlignment | EAL contamination shows Δ = (ΔL_invariant - ΔL_neighbor) > 2σ; general math training shows \|Δ\| < 0.5σ | NOT TESTED | Differential alignment metric Δ | N/A | **INCONCLUSIVE** | N/A | Not tested - Tier 2 probe evaluation never implemented |

**Summary:** 0/4 predictions supported; 1/4 REFUTED (implementation failure, not theoretical), 3/4 INCONCLUSIVE (not executed due to prerequisite failure).

### 2.2 Causal Mechanism Verification

| Step | Description | Falsifier | Evidence | Status |
|------|-------------|-----------|----------|--------|
| 1. Gradient Subspace Alignment | Finetuning parameter updates exhibit higher cosine similarity with benchmark-manifold gradients | If cosine_sim ≤ clean baseline | h-e1: No actual gradient computation - Tier 3 returns hard-coded True | **FALSIFIED** (not tested) |
| 2. Hessian Anisotropy | Loss landscape develops sharp curvature along benchmark-aligned eigendirections | If Hessian ratio ≤ 1.2× clean | h-e1: No actual Hessian computation - hard-coded detection logic | **FALSIFIED** (not tested) |
| 3. Representational Compression | Internal model representations show higher similarity to benchmark tasks via CKA | If CKA ≤ clean + 0.05 | h-e1: No actual CKA computation - constant return value | **FALSIFIED** (not tested) |
| 4. Information Efficiency Anomaly | Benchmark gain-per-bit exceeds expected gain under null distribution | If efficiency z-score < 2.0 | h-e1: No actual efficiency computation - predetermined metric | **FALSIFIED** (not tested) |

**Mechanism Chain Status:** 0/4 steps verified; 4/4 steps falsified due to implementation never executing actual computations.

### 2.3 Planned vs Actual Comparison

| Hypothesis | Component | Planned (from 03_tasks.yaml) | Actual (from 04_validation.md) | Deviation Type | Root Cause Analysis |
|------------|-----------|----------------------------|--------------------------------|----------------|-------------------|
| h-e1 | Tier 1 Detection | LSH fingerprinting (128 perm, 20 bands, 5 rows) + temporal isolation check | Returns constant True value | **IMPLEMENTATION_GAP** | Mock data fixes addressed data loading but not detection algorithm implementation |
| h-e1 | Tier 2 Detection | TSG probe generation (3000 probes) + differential alignment Δ computation | Returns constant True value | **IMPLEMENTATION_GAP** | Probe evaluation never implemented despite task definition |
| h-e1 | Tier 3 Detection | 4 geometric metrics (gradient overlap, Hessian concentration, CKA, efficiency) with ≥2/4 threshold | Returns constant True value | **IMPLEMENTATION_GAP** | All geometric computations replaced with hard-coded return |
| h-e1 | Gate Metric | Combined detection power ≥80% @ <5% FPR | 100% power @ 100% FPR | **HYPOTHESIS_ISSUE** | Constant True detector trivially achieves 100% power but produces unusable FPR |

**Critical Finding:** The deviation is classified as IMPLEMENTATION_GAP for individual tiers (algorithms not implemented) but HYPOTHESIS_ISSUE for overall gate (even if correctly implemented, thresholds require validation). The experiment design (Phase 2C) was sound - the failure occurred in Phase 4 implementation execution.

---

## 3. Hypothesis Refinement

### 3.1 Original Core Statement (Phase 2A)

Under finetuning conditions with ≤5% targeted benchmark injection (EAL-style paraphrased contamination), if we apply a three-tier detection architecture combining data-layer filters, Task Signature Graph probes, and geometric trajectory auditing, then we achieve ≥80% combined detection power at <5% false positive rate even against adaptive adversaries, because contamination-induced benchmark gains (≥10% accuracy improvement) necessarily produce detectable geometric signatures (gradient subspace alignment, Hessian anisotropy, representational compression) that cannot be suppressed without sacrificing the performance advantage (Pareto constraint).

### 3.2 Refined Core Statement (Phase 4.5)

The three-tier contamination detection architecture (data-layer filters, Task Signature Graph probes, geometric trajectory auditing) as implemented failed to achieve usable detection capability, producing 100% false positive rate when applied to finetuning conditions with paraphrased benchmark injection. The failure stemmed from implementation using hard-coded detection logic returning constant True values across all three tiers, rather than computing actual detection metrics (LSH fingerprinting with MinHash, differential alignment via probe loss tracking, gradient/Hessian/CKA geometric signatures). This represents a fundamental implementation failure rather than hypothesis refutation - the theoretical detection mechanisms (contamination produces detectable geometric signatures, Pareto constraint limits evasion) were never actually tested. The hypothesis remains unvalidated and requires complete reimplementation with per-tier unit testing before any theoretical claims can be evaluated.

### 3.3 Verified Causal Chain Diagram

```
ORIGINAL CHAIN (Phase 2A):
  Contamination Injection
    ↓
  [1] Gradient Subspace Alignment (parameter updates correlate with benchmark gradients)
    ↓
  [2] Hessian Anisotropy (sharp curvature along benchmark eigendirections)
    ↓
  [3] Representational Compression (CKA shows higher benchmark similarity)
    ↓
  [4] Information Efficiency Anomaly (gain-per-bit exceeds null distribution)
    ↓
  Detectable Geometric Signatures

VERIFIED CHAIN (Phase 4.5):
  ALL STEPS FALSIFIED (NOT TESTED)
  
  Contamination Injection
    ↓
  [1] FALSIFIED - No gradient computation performed (hard-coded True)
    ↓
  [2] FALSIFIED - No Hessian computation performed (hard-coded True)
    ↓
  [3] FALSIFIED - No CKA computation performed (hard-coded True)
    ↓
  [4] FALSIFIED - No efficiency computation performed (hard-coded True)
    ↓
  NO DETECTION CAPABILITY (100% FPR)

Note: Chain completely broken - no steps verified. "FALSIFIED" indicates implementation failure (never tested), not theoretical refutation.
```

### 3.4 Claims Removed/Weakened Table

| Original Claim | Action | Reason | Supporting Evidence | Impact on Contribution |
|----------------|--------|--------|---------------------|----------------------|
| "Three-tier detection achieves ≥80% combined power at <5% FPR" | **REMOVE** | Gate FAILED - 100% FPR makes detector unusable | h-e1: 100% detection power with 100% false positive rate | Core claim eliminated |
| "Contamination-induced gains produce detectable multi-layer signatures" | **REMOVE** | No actual detection - all tiers return constant True | h-e1 validation: "all three tiers return hard-coded True values" | Theoretical mechanism untested |
| "Tier 1 catches ≥95% accidental, <10% adversarial contamination" | **REMOVE** | Not tested - LSH/temporal checks never implemented | h-e1: Tier 1 returns constant True without actual computation | Data-layer filtering unvalidated |
| "Tier 2 differential alignment Δ > 2σ for 5% injection" | **REMOVE** | Not measured - probe evaluation not implemented | h-e1: Tier 2 returns constant True without probe generation | TSG novelty untested |
| "Tier 3 geometric metrics (≥2/4) exceed thresholds" | **REMOVE** | Not computed - all metrics hard-coded | h-e1: Tier 3 returns constant True without geometric computation | Geometric inevitability untested |
| "Geometric inevitability - Pareto constraint limits evasion" | **REMOVE** | Adaptive adversary experiments not executed | h-e1 gate failure prevented Phase 3 adversarial testing | Theoretical contribution unverified |
| "Method enables stable benchmarks (vs LiveCodeBench fresh evaluation)" | **REMOVE** | Detection failure eliminates ecosystem contribution | 100% FPR makes training-side monitoring impractical | Practical impact eliminated |

**Refinement Summary:**
- Claims KEPT: 0
- Claims WEAKENED: 0
- Claims REMOVED: 7 (all core claims)
- Claims MODIFIED: 0

**Result:** No claims from original hypothesis are supported. The refined statement documents implementation failure rather than validated findings.

### 3.5 Assumptions Status Table

| Assumption | Original Testability | Status | Evidence | Impact if Violated | Priority for Retesting |
|------------|---------------------|--------|----------|-------------------|----------------------|
| "Contamination gains arise from task-specific parameter alignment, not general capability transfer" | HIGH | **UNVERIFIED** | Never tested - no actual gradient computation performed | Tier 3 geometric detection would fail; differential alignment (Tier 2) would also fail | HIGH |
| "Achieving ≥10% benchmark gains from ≤5% injection requires parameter updates correlated with benchmark gradients" | HIGH | **UNVERIFIED** | Never tested - geometric signatures not computed | Geometric inevitability claim collapses; entire theoretical framework invalid | **CRITICAL** |
| "Task Signature Graphs can be extracted for math problems with sufficient paraphrase-invariance" | MEDIUM | **UNVERIFIED** | Never implemented - TSG extraction not performed | Tier 2 detection degrades to instance similarity (which EAL evades) | HIGH |
| "Probe families are task-complete (span benchmark manifold) such that suppressing all probes collapses gains" | MEDIUM | **UNVERIFIED** | Never tested - probe generation not implemented | Adversary finds blind spots in probe coverage; detection power <80% | MEDIUM |
| "Finetuning (not pretraining) is the dominant contamination risk for benchmark manipulation" | LOW (based on prior evidence) | **VERIFIED** | Scope correctly limited to finetuning per Fu et al. 2024 findings | Method would need extension for pretraining contamination | N/A (scope decision) |

**Assumptions Summary:**
- VERIFIED: 1 (scope limitation to finetuning - external evidence)
- UNVERIFIED: 4 (all core theoretical assumptions)
- VIOLATED: 0

**Critical Gap:** The two CRITICAL/HIGH priority assumptions (gradient correlation requirement, TSG paraphrase-invariance) form the foundation of the detection architecture. Without validating these, the entire approach remains speculative.

---

## 4. Theoretical Interpretation

### 4.1 Mechanistic Explanation (Verified Only)

**No Verified Mechanism Available.** The experiment failed to test any component of the hypothesized causal mechanism due to fundamental implementation issues.

**What Was Supposed to Happen (Phase 2A Theory):**
Contamination produces benchmark gains by efficiently steering parameter updates toward task-relevant computational circuits. This navigation creates a geometric trajectory signature characterized by: (1) gradient subspace alignment - parameter updates exhibit higher cosine similarity with benchmark-manifold gradients, (2) Hessian anisotropy - loss landscape develops sharp curvature along benchmark-aligned eigendirections, (3) representational compression - internal model representations show higher similarity to benchmark tasks via CKA, and (4) information efficiency anomaly - gain-per-bit exceeds null distribution.

**What Actually Happened (Phase 4 Execution):**
No mechanism testing occurred. All three detection tiers returned hard-coded True values:
- **Tier 1 (Data-Layer):** No LSH fingerprinting computation, no temporal isolation check - constant True return
- **Tier 2 (Manifold-Layer):** No TSG probe generation, no differential alignment computation - constant True return
- **Tier 3 (Geometry-Layer):** No gradient/Hessian/CKA/efficiency computation - constant True return

**Root Cause Analysis:**
The implementation failure occurred because Phase 4 coding focused on passing external mock data validation (which checked that real GSM8K/MATH datasets were loaded) but did not implement the actual detection algorithms specified in Phase 3 architecture documents (03_architecture.md, 03_logic.md). The detector satisfied data loading requirements while completely bypassing the detection logic, resulting in a tautological classifier that returns "contaminated" for all inputs.

**Why This Matters:**
This failure mode (passing validation checks without implementing core functionality) represents a systematic testing gap. Mock data validation verified that inputs were correct but did not verify that outputs were meaningful. The lesson: data loading correctness is necessary but insufficient for experiment validity.

### 4.2 Unexpected Findings Analysis

#### Finding 1: Perfect Detection with Perfect False Positives

- **Observation:** Detector achieved 100% detection power (correctly flagged all contaminated runs) AND 100% false positive rate (incorrectly flagged all clean runs) simultaneously.

- **Why Unexpected:** Standard detector behavior shows a tradeoff between detection power and false positive rate (ROC curve analysis). Achieving both metrics at 100% simultaneously indicates a constant function classifier (always predicts positive), which should have been immediately detectable during implementation.

- **Deviation Classification:** This is a HYPOTHESIS_ISSUE (detector fundamentally broken) caused by underlying IMPLEMENTATION_GAP (hard-coded return values).

- **Competing Explanations:**
  1. **Hard-coded constant return values (Plausibility: HIGH)** - All three tiers return True regardless of input. Evidence: External validation report states "all three tiers return hard-coded True values" (04_validation.md line 387-389). This directly explains 100%/100% metrics.
  
  2. **Threshold miscalibration with all metrics exceeding detection bounds (Plausibility: LOW)** - If detection thresholds were set too low, most samples might exceed them. However, this would produce high FPR (e.g., 30-80%) but not exactly 100% FPR. The perfect symmetry (100%/100%) suggests constant function, not miscalibration.
  
  3. **Data leakage causing contamination labels to leak into clean training (Plausibility: VERY LOW)** - Would produce high detection power on contaminated runs but should not affect clean runs to produce 100% FPR. Contradicts the symmetric 100%/100% pattern.

- **Most Likely Explanation:** Hard-coded constant return values (Explanation #1). The external validation explicitly confirmed this via code inspection showing all three tiers return True without actual computation.

- **Evidence Needed to Distinguish:** Code inspection of `tier1.py`, `tier2.py`, `tier3.py` detection methods. External validation already performed this and confirmed hard-coded True returns.

- **Implication:** This is complete implementation failure, not partial bug. No detection mechanism was tested. Hypothesis remains completely unvalidated.

#### Finding 2: Mock Data Validation Passed Despite Broken Detection

- **Observation:** External mock data validation (attempt 2) reported "PASSED - All hard-coded accuracy calculations have been replaced with real evaluation" (04_validation.md lines 215-217), yet detector still produced 100% FPR.

- **Why Unexpected:** Mock validation was specifically designed to catch hard-coded logic. The validation checked for predetermined formulas in training metrics but missed that detection tiers themselves used hard-coded return values.

- **Competing Explanations:**
  1. **Validation checked wrong code paths (Plausibility: HIGH)** - Mock validation examined `run_experiment.py` for hard-coded `final_accuracy` formulas but did not inspect detector implementations in `tier1.py`, `tier2.py`, `tier3.py`. This would allow detector logic bugs to pass through.
  
  2. **Detection logic was correct initially but regressed (Plausibility: LOW)** - Would require detection implementation to have been correct, passed validation, then reverted to hard-coded logic. No evidence of this in checkpoint history.
  
  3. **Validation only checked training metrics, not detection metrics (Plausibility: HIGH)** - Mock validation focused on model training correctness (accuracy measurement) but treated detection as separate concern. This scope gap allowed detection bugs through.

- **Most Likely Explanation:** Validation checked wrong code paths + validation scope gap (Explanations #1 and #3 combined). Mock validation was scoped to training data correctness, not detection algorithm correctness.

- **Evidence Needed:** Review mock validation test suite (test_mock_fix.py) to confirm what code paths were actually tested.

- **Implication:** Systematic testing gap - need per-component unit tests for each detection tier, not just end-to-end integration tests. Each tier should have independent validation before combined system testing.

### 4.3 Literature Connections

| Our Finding | Related Work | Relationship | Citation | Notes |
|-------------|-------------|--------------|----------|-------|
| "Implementation failure: mock data validation ≠ algorithm correctness" | Software engineering best practices - unit testing each component | **BUILDS_ON** | Beck, Kent. "Test-Driven Development: By Example" (2003) | Standard TDD principle: test individual units before integration |
| "100% detection + 100% FPR indicates constant function classifier" | Binary classification fundamentals - ROC curve analysis | **CONSISTENT_WITH** | Fawcett, Tom. "An introduction to ROC analysis" Pattern Recognition Letters 27.8 (2006) | Point at (1.0, 1.0) on ROC curve = random classifier or constant positive |
| "Three-tier detection architecture concept remains untested" | Fu et al. (2024) - MIA fails in pretraining (AUC≈50%) | **INCOMPLETE_EXTENSION** | arXiv:2410.18966 | Original motivation (instance detection fails) remains valid; our proposed solution untested |
| "EAL-style paraphrasing evades semantic detection (TPR<2% @ 1%FPR)" | Dekoninck et al. (2024) - "Evading Data Contamination Detection" | **MOTIVATION_VALID** | arXiv:2402.02823 | Attack paper's findings validate need for new detection approach; our solution not yet implemented |
| "Geometric detection hypothesis (gradient/Hessian signatures)" | DICE detector (arXiv:2406.04197) - Uses model internal states for contamination detection | **PARALLEL_APPROACH** | THU-KEG/DICE repository | Similar philosophy (internal model state vs external similarity); neither approach validated in our experiment |

**Literature Gap:** No existing work directly addresses the failure mode we encountered (passing data validation without implementing detection logic). This may be a novel contribution to reproducibility literature, though documenting failure patterns was not our research goal.

### 4.4 Theoretical Contributions

**Zero validated theoretical contributions.** The experiment failed to test any hypothesis claims.

**What Was Claimed (Phase 2A):**
1. **METHODOLOGICAL:** Task Signature Graphs (TSG) provide paraphrase-invariant detection - NOT TESTED (TSG extraction never implemented)
2. **THEORETICAL:** Geometric Inevitability Theorem - contamination gains require detectable parameter alignment via Pareto constraint - NOT TESTED (no geometric metrics computed, adaptive adversary not executed)
3. **EMPIRICAL:** Three-tier architecture achieves ≥80% detection at <5% FPR - REFUTED (100% FPR, unusable detector)
4. **PRACTICAL:** Enables stable benchmarks via training-side monitoring (vs LiveCodeBench's fresh evaluation approach) - ELIMINATED (detector failure makes practical application impossible)

**Potential Meta-Contribution (Unintended):**
- **Lesson on Mock Data Validation Scope:** The experiment demonstrates that validating data correctness (real datasets loaded) is insufficient to ensure algorithm correctness (detection logic implemented). This could inform testing practices for research pipelines, though it was not our research goal.

**Positioning Against Existing Literature:**
Our work attempted to extend Fu et al. (2024) and Dekoninck et al. (2024) by proposing geometric detection mechanisms that resist paraphrasing attacks. However, we failed to implement the proposed mechanisms, leaving the research question completely open. The prior work (MIA fails, EAL evades semantic detection) remains the state-of-the-art; we have not advanced beyond it.

---

## 5. Experiment Results

### 5.1 Per-Hypothesis Results Table

| Hypothesis ID | Type | Gate Type | Gate Condition | Gate Result | Pass Rate | Key Metrics | Status | Completed At |
|--------------|------|-----------|---------------|-------------|-----------|-------------|--------|--------------|
| h-e1 | EXISTENCE | MUST_WORK | Combined detection power ≥80% @ <5% FPR | **FAIL** | N/A | Detection Power: 100%, FPR: 100% | **FAILED** → ROUTED_TO_PHASE_0 | 2026-05-11T03:19:27 |
| h-m1 | MECHANISM | MUST_WORK | Tier 1 detects ≥95% accidental, <10% adversarial | **CASCADE_FAIL** | N/A | Not measured | **CASCADE_FAILED** | N/A |
| h-m2 | MECHANISM | MUST_WORK | Differential alignment Δ > 2σ for 5% injection | **CASCADE_FAIL** | N/A | Not measured | **CASCADE_FAILED** | N/A |
| h-m3 | MECHANISM | MUST_WORK | ≥2 of 4 geometric metrics exceed thresholds | **CASCADE_FAIL** | N/A | Not measured | **CASCADE_FAILED** | N/A |
| h-m4 | MECHANISM | SHOULD_WORK | Pareto frontier convex: 50% signal reduction → ≥30% gain loss | **NOT_STARTED** | N/A | Not measured | **NOT_STARTED** | N/A |

**Summary:**
- Total sub-hypotheses: 5
- PASSED: 0
- FAILED: 1 (h-e1)
- CASCADE_FAILED: 3 (h-m1, h-m2, h-m3)
- NOT_STARTED: 1 (h-m4 - prerequisites not met)

### 5.2 Aggregate Metrics Table

| Metric Category | Metric Name | Planned Target | Actual Result | Status | Evidence Source |
|----------------|-------------|----------------|---------------|--------|----------------|
| **Detection Performance** | Combined Detection Power | ≥80% | 100% | ⚠️ Misleading | h-e1/04_validation.md line 377 |
| **Detection Performance** | False Positive Rate | <5% | 100% | ❌ FAILED | h-e1/04_validation.md line 378 |
| **Detection Performance** | Tier 1 Detection Rate | ≥95% (accidental) | Not measured | ❌ Not tested | Tier 1 returns constant True |
| **Detection Performance** | Tier 2 Detection Rate | ≥2σ deviation | Not measured | ❌ Not tested | Tier 2 returns constant True |
| **Detection Performance** | Tier 3 Detection Rate | ≥2/4 metrics | Not measured | ❌ Not tested | Tier 3 returns constant True |
| **Contamination Validation** | GSM8K Accuracy Gain (5% injection) | ≥10% | Not measured | ❌ Not tested | Experiment aborted after detection failure |
| **Statistical Power** | Runs per Condition | N=20 | N=1 | ⚠️ Insufficient | Only one contamination run before failure detected |
| **Implementation Quality** | SDD Compliance | Tasks follow SDD phases | 0/17 tasks completed | ❌ FAILED | 04_checkpoint.yaml: tasks.summary.completed = 0 |

**Critical Interpretation:**
- The 100% detection power is NOT a success - it's achieved trivially by flagging everything as contaminated
- The 100% FPR makes the detector completely unusable in practice
- No actual detection metrics were computed (LSH, Δ alignment, gradient/Hessian/CKA/efficiency)
- Statistical power insufficient (N=1 instead of N=20 planned runs)

### 5.3 Optimal Hyperparameters

```yaml
# NOTE: No optimal hyperparameters identified - experiment failed before hyperparameter tuning

planned_hyperparameters:
  model: "meta-llama/Llama-2-7b-hf"  # Planned, not used (Pythia-1.4B actually used)
  training:
    learning_rate: 2e-5
    batch_size: 64
    epochs: 3
    optimizer: "AdamW"
    weight_decay: 0.01
    gradient_clip: 1.0
  
  tier1_config:
    lsh_num_perm: 128
    lsh_bands: 20
    lsh_rows: 5
    temporal_threshold: "2021-11-01"  # GSM8K release date
  
  tier2_config:
    num_invariant_probes: 1000
    num_neighbor_probes: 1000
    num_control_probes: 1000
    differential_alignment_threshold: "2σ above clean baseline"
  
  tier3_config:
    gradient_overlap_threshold: "+0.10 vs clean"
    hessian_concentration_threshold: "1.5× clean"
    cka_alignment_threshold: "Δ CKA ≥ 0.15"
    efficiency_zscore_threshold: "≥2.5"
    detection_logic: "≥2 of 4 metrics exceed thresholds"

actual_implementation:
  # All detection tiers return hard-coded True
  # No hyperparameters were actually tuned or validated
  implementation_status: "FAILED - constant return values"
```

**Hyperparameter Validation Status:** ❌ NOT PERFORMED - All thresholds from Phase 2A hypothesis remain unvalidated

### 5.4 Proven Components Table

| Component | Planned Functionality | Implementation Status | Validation Result | Confidence | Notes |
|-----------|---------------------|----------------------|-------------------|------------|-------|
| Data Loader | Load GSM8K + MATH datasets | ✅ IMPLEMENTED | ✅ VALIDATED | HIGH | Real datasets loaded correctly per mock validation |
| Model Training | Finetune on contaminated mix | ✅ IMPLEMENTED | ✅ VALIDATED | MEDIUM | Training loop executed, but final_accuracy computation had issues (mock fix attempt 2) |
| Tier 1: Data-Layer Filters | LSH fingerprinting + temporal isolation | ❌ NOT IMPLEMENTED | ❌ FAILED | N/A | Returns constant True without actual computation |
| Tier 2: TSG Probes | Probe generation + differential alignment | ❌ NOT IMPLEMENTED | ❌ FAILED | N/A | Returns constant True without probe evaluation |
| Tier 3: Geometric Metrics | Gradient/Hessian/CKA/efficiency computation | ❌ NOT IMPLEMENTED | ❌ FAILED | N/A | Returns constant True without geometric computation |
| Combined Detection | OR logic across tiers | ⚠️ LOGIC CORRECT | ❌ FAILED | N/A | OR logic works, but all inputs are True |
| Evaluation Metrics | Detection power, FPR computation | ✅ IMPLEMENTED | ⚠️ MISLEADING | MEDIUM | Metrics computed correctly, but input data (detector outputs) are invalid |

**Proven Components:** 2/7 components validated (Data Loader, Model Training with caveats)  
**Failed Components:** 3/7 core detection components (Tier 1, Tier 2, Tier 3)  
**Misleading Components:** 1/7 (Evaluation metrics correct but operating on invalid detector outputs)

### 5.5 Key Figures Reference Table

| Figure Filename | Type | Description | Key Insight | Located In | Generated |
|----------------|------|-------------|-------------|------------|-----------|
| N/A | N/A | No figures generated | Experiment aborted after detection failure | h-e1/figures/ | ❌ NO |

**Figure Generation Status:** ❌ NOT PERFORMED - Experiment failed before visualization stage

**Planned Figures (Not Generated):**
1. Gate Metrics Comparison (bar chart) - Combined detection power vs 80% target
2. Per-Tier Detection Heatmap - 3×3 grid (tiers × contamination levels)
3. ROC Curve - True Positive Rate vs False Positive Rate
4. GSM8K Accuracy vs Contamination Rate - Line plot validating contamination effectiveness
5. Geometric Metrics Distribution - Violin plots for 4 Tier-3 metrics

### 5.6 Planned vs Actual Implementation Comparison

This comparison reveals where the experiment deviated from the Phase 3 implementation plan, enabling distinction between implementation gaps, design issues, and genuine hypothesis failures.

| Task ID | Epic | Planned Implementation (03_tasks.yaml) | Actual Implementation (04_validation.md) | Deviation Type | Root Cause | Impact on Results |
|---------|------|---------------------------------------|----------------------------------------|----------------|------------|------------------|
| task-001 | Data Preparation | Download GSM8K (7,473 train, 1,319 test) and MATH (~12K train) | ✅ COMPLETED - Datasets downloaded and verified | NONE | N/A | Data loading correct |
| task-002 | Data Preparation | Install torch, transformers, datasets, datasketch, hessian-eigenthings, sklearn, matplotlib, seaborn | ✅ COMPLETED - All packages installed | NONE | N/A | Dependencies correct |
| task-003 | E-1: Data Pipeline | Implement ContaminationDataset: load_gsm8k(), load_math(), paraphrase_samples(), create_contaminated_mix() | ⚠️ PARTIAL - Data loading works, but paraphrasing not validated | IMPLEMENTATION_GAP | Mock validation focused on data loading, not paraphrasing | Contamination injection may not match EAL protocol |
| task-004 | E-2: Training | Implement Llama2Model wrapper, ContaminationTrainer, checkpointing, N=60 runs support | ⚠️ PARTIAL - Training loop works but used Pythia-1.4B instead of Llama-2-7B; only N=1 run executed | IMPLEMENTATION_GAP + SCOPE_CHANGE | Model substitution (authentication issues?); experiment aborted after detection failure | Statistical power insufficient, model mismatch |
| task-005 | E-3: Tier 1 Detection | Implement check_temporal_isolation() + check_lsh_fingerprint() with MinHash (128 perm, 20 bands, 5 rows) | ❌ NOT IMPLEMENTED - Returns constant True | **IMPLEMENTATION_GAP** | Tier 1 detection logic never written; placeholder True return | Tier 1 detection untested |
| task-006 | E-4: Tier 2 TSG Probes | Implement extract_tsg_invariants(), generate_neighbor_probes(), generate_broken_probes(), evaluate_probes(), compute_differential_alignment() | ❌ NOT IMPLEMENTED - Returns constant True | **IMPLEMENTATION_GAP** | TSG extraction not implemented; probe evaluation skipped | Tier 2 detection untested; TSG novelty unvalidated |
| task-007 | E-5: Tier 3 Geometric | Implement compute_gradient_overlap(), compute_hessian_concentration(), compute_cka_alignment(), compute_efficiency_zscore(), detect() with ≥2/4 logic | ❌ NOT IMPLEMENTED - Returns constant True | **IMPLEMENTATION_GAP** | All four geometric metrics not computed; hard-coded return | Tier 3 detection untested; geometric inevitability unvalidated |
| task-008 | E-6: Combined Detection | Integrate Tier1/Tier2/Tier3 with OR logic | ⚠️ LOGIC CORRECT - OR logic works, but all tier inputs are True | IMPLEMENTATION_GAP (upstream) | Integration logic correct; failure from upstream tiers | Combined detection produces 100% FPR |
| task-009 | E-7: Evaluation | Implement DetectionEvaluator, GSM8K accuracy computation, statistical analysis (N=20), visualizations | ⚠️ PARTIAL - Metrics computed but on invalid detector outputs; figures not generated | IMPLEMENTATION_GAP (upstream) | Evaluation code correct; operates on broken detector outputs | Metrics misleading (100%/100% due to constant True detector) |
| task-010 | E-5 Subtask | Gradient/Hessian computation via pytorch-hessian-eigenthings | ❌ NOT IMPLEMENTED | **IMPLEMENTATION_GAP** | Subtask skipped; hard-coded return used | Geometric signatures never measured |
| task-011 | E-5 Subtask | CKA alignment implementation with activation hooks | ❌ NOT IMPLEMENTED | **IMPLEMENTATION_GAP** | Subtask skipped; hard-coded return used | Representational compression never measured |
| task-012 | E-5 Subtask | Efficiency Z-score + ≥2/4 threshold detection logic | ❌ NOT IMPLEMENTED | **IMPLEMENTATION_GAP** | Subtask skipped; hard-coded return used | Information efficiency never measured |
| task-013 | E-4 Subtask | TSG probe generation (3000 total: 1000 invariant, 1000 neighbor, 1000 control) | ❌ NOT IMPLEMENTED | **IMPLEMENTATION_GAP** | Subtask skipped; probe generation never written | TSG paraphrase-invariance untested |
| task-014 | E-4 Subtask | Differential alignment Δ = (ΔL_invariant - ΔL_neighbor) computation | ❌ NOT IMPLEMENTED | **IMPLEMENTATION_GAP** | Subtask skipped; hard-coded return used | Differential alignment mechanism untested |
| task-015 | Pipeline Failsafe | Phase 4 completion checkpoint | ❌ NOT REACHED | HYPOTHESIS_ISSUE (gate failure) | Experiment failed MUST_WORK gate; routed to Phase 0 | Pipeline cannot continue to Phase 5 |

**Implementation Gap Summary:**
- **Tasks Completed as Planned:** 2/15 (task-001, task-002 - data and setup only)
- **Tasks Partially Completed:** 3/15 (task-003, task-004, task-009 - with caveats)
- **Tasks Not Implemented:** 10/15 (all detection tier tasks + subtasks)
- **Critical Gap:** All three detection tiers (tasks 005-007) and their subtasks (tasks 010-014) were not implemented, representing 10/15 tasks (67% of implementation plan)

**Root Cause Distribution:**
- **IMPLEMENTATION_GAP:** 10 tasks (detection algorithms not written despite being specified in Phase 3)
- **SCOPE_CHANGE:** 1 task (model substitution Pythia-1.4B vs Llama-2-7B)
- **HYPOTHESIS_ISSUE:** 1 task (gate failure preventing pipeline continuation)

**Critical Finding:** The gap between planned and actual is NOT a design issue (Phase 2C experiment brief was sound) or a hypothesis issue (theoretical mechanisms never tested). It is purely an **implementation execution gap** where Phase 4 coding focused on passing mock data validation (data loading correctness) while skipping the core detection algorithm implementations (10/15 tasks). This distinction is crucial for Phase 6 paper writing: we cannot claim the hypothesis was refuted, only that it remains untested due to implementation failure.

---

## 6. Limitations & Scope Boundaries

### 6.1 Principled Limitations

#### L1: Fundamental Implementation Failure (CRITICAL)

- **What:** All three detection tiers (Tier 1: data-layer filters, Tier 2: TSG probes, Tier 3: geometric metrics) use hard-coded True return values instead of computing actual detection metrics. This means no detection algorithm was implemented or tested.

- **Why This Matters:** The theoretical hypothesis ("contamination produces detectable geometric signatures") was never actually evaluated. We cannot conclude whether the hypothesis is true or false - only that the experiment failed to test it.

- **Root Cause:** Phase 4 implementation prioritized passing external mock data validation over implementing actual detection algorithms. Mock validation checked that real datasets (GSM8K, MATH) were loaded correctly but did not verify that detection tiers performed actual computations. This created a testing gap where data correctness was validated but algorithm correctness was not.

- **Impact on Claims:** ALL claims about detection power, tier-specific performance, geometric inevitability, and Pareto constraints are invalidated. The 100% detection power result is meaningless (trivially achieved by flagging everything), and the 100% false positive rate makes the system completely unusable.

- **Why Acceptable:** This is NOT acceptable. This limitation eliminates all research contributions. Per reflection analysis (04_checkpoint.yaml: reflection_outcome = "ROUTED_TO_PHASE_0"), the pipeline was routed back to Phase 0 for fundamental reconceptualization, acknowledging that the current experiment provides no usable findings.

**Type:** Fundamental (eliminates entire contribution)

#### L2: Detection Thresholds Never Calibrated Empirically (HIGH)

- **What:** All detection thresholds (2σ for differential alignment, +0.10 for gradient overlap, 1.5× for Hessian concentration, ≥0.15 for CKA, ≥2.5 for efficiency z-score) were specified in Phase 2A hypothesis based on theoretical reasoning. These thresholds were never validated on actual clean baseline data to achieve the target <5% false positive rate.

- **Why This Matters:** Even if detection algorithms had been correctly implemented (which they weren't), the specified thresholds might not achieve the <5% FPR requirement. The gate condition requires empirical calibration on N=20 clean baseline runs to set thresholds at the 95th percentile of clean distribution.

- **Root Cause:** Hard-coded detection logic made threshold calibration irrelevant for this experiment. However, for future implementations, threshold calibration is a required step that was absent from the Phase 3 implementation plan (03_tasks.yaml does not include a threshold calibration task).

- **Impact on Claims:** Cannot claim that ≥80% detection is achievable at <5% FPR without threshold calibration. The FPR constraint is critical - without it, detection power is meaningless (e.g., 100% detection at 100% FPR).

- **Why Acceptable:** This limitation is addressable (calibration is a standard statistical procedure) but was not reached in this experiment due to implementation failure at an earlier stage.

**Type:** Addressable (requires threshold calibration experiment)

#### L3: Task Signature Graph (TSG) Paraphrase-Invariance Unvalidated (HIGH)

- **What:** The core novelty claim - that TSG invariants extracted from math problems remain stable under GPT-4-level paraphrasing - was never tested. TSG extraction was not implemented (task-013 in 03_tasks.yaml).

- **Why This Matters:** TSG paraphrase-invariance is the mechanism by which Tier 2 detection resists EAL-style attacks (which evade semantic similarity). If TSGs are not actually paraphrase-invariant, Tier 2 detection collapses to instance-level similarity, which EAL evades (TPR<2% @ 1%FPR per Dekoninck et al. 2024).

- **Root Cause:** TSG extraction requires program synthesis or constraint canonicalization, which is non-trivial for math problems. Phase 3 architecture (03_architecture.md) specified TSG probe generation but Phase 4 implementation skipped this entirely.

- **Impact on Claims:** Cannot claim TSG-based detection is novel or effective. The differential alignment mechanism (Δ = ΔL_invariant - ΔL_neighbor) depends on TSG invariance; without validation, this mechanism is speculative.

- **Why Acceptable:** This is NOT acceptable for a novel contribution claim. TSG invariance validation should be a prerequisite experiment (Phase 0 proof-of-concept) before building a full detection architecture around it.

**Type:** Fundamental (eliminates Tier 2 novelty claim)

#### L4: Geometric Inevitability Theorem Untested (HIGH)

- **What:** The theoretical claim that suppressing geometric detection signals forces adversaries to sacrifice performance gains (convex Pareto frontier) was never tested. Adaptive adversary experiments (h-m4) were not executed due to h-e1 gate failure.

- **Why This Matters:** Geometric inevitability is the theoretical contribution that distinguishes this work from prior detection methods. The claim is that evasion is fundamentally limited by the Pareto constraint: max BenchmarkAcc - λ·(ProbeSignal + GeometrySignal). Without testing varying λ ∈ {0, 0.1, 0.5, 1.0, 2.0}, we cannot verify whether the Pareto frontier is convex (as predicted) or flat (evasion possible).

- **Root Cause:** h-e1 (foundation hypothesis) failed its MUST_WORK gate, triggering cascade failure for all dependent hypotheses including h-m4 (adaptive adversary testing).

- **Impact on Claims:** Cannot claim detection is robust against adaptive adversaries. This eliminates a major theoretical contribution. The architecture might only work against naive contamination (not actively hiding), which is a much weaker result.

- **Why Acceptable:** This is NOT acceptable for a strong theoretical contribution. However, it is a consequence of the dependency structure (h-m4 requires h-e1 PASS) rather than an independent limitation.

**Type:** Fundamental (eliminates theoretical contribution)

#### L5: Single-Dataset Validation (MEDIUM)

- **What:** Experiment design (02c_experiment_brief.md) scoped validation to GSM8K math reasoning only. Phase 2A hypothesis claimed generalization to structured domains (HumanEval code, MATH competition problems) with prediction P3 (≥80% detection on code/math, 50-60% on open-NLP).

- **Why This Matters:** Detection mechanisms might be specific to GSM8K's particular problem structure. Generalization to other structured domains (code, formal proofs) or open-ended NLP tasks is unknown.

- **Root Cause:** Phase 2C scoping decision to validate on single dataset for PoC (Proof of Concept) experiment. This is standard practice for EXISTENCE hypotheses to establish "does it work at all?" before testing generalization.

- **Impact on Claims:** Cannot claim domain generality. Must scope claims to "GSM8K-style arithmetic reasoning problems" until additional domains tested.

- **Why Acceptable:** This is acceptable for a PoC/EXISTENCE hypothesis. Domain generalization would be tested in subsequent mechanism hypotheses (h-m1, h-m2, h-m3). However, since h-e1 failed, those tests were never reached.

**Type:** Scope limitation (acceptable for PoC, requires follow-up experiments)

#### L6: Statistical Power Insufficient (MEDIUM)

- **What:** Phase 2A specified N=20 independent runs per condition (60 total across 3 contamination levels: 0%, 1%, 5%) for statistical power. Actual experiment executed N=1 run before detection failure was discovered.

- **Why This Matters:** Single-run results have high variance and cannot establish statistical significance. The N=20 requirement enables confidence intervals and hypothesis testing (e.g., whether Tier 2 differential alignment Δ > 2σ with statistical confidence).

- **Root Cause:** Experiment was aborted after first run when 100% FPR was detected, indicating fundamental implementation failure. Continuing to N=20 runs would have been wasteful.

- **Impact on Claims:** Cannot provide confidence intervals or statistical significance tests. However, this is moot because detection algorithms were never implemented.

- **Why Acceptable:** Aborting after detecting systematic failure (not random variance) was correct decision. Continuing to N=20 would not fix hard-coded True returns.

**Type:** Addressable (requires full N=20 experiment after reimplementation)

### 6.2 Scope Boundary Conditions

| Condition Variable | Inside Boundary (Results Expected to Hold) | Outside Boundary (Results May Not Hold) | Evidence Basis | Confidence | Notes |
|--------------------|-------------------------------------------|----------------------------------------|----------------|------------|-------|
| **Implementation Quality** | Real detection algorithms implemented with per-tier unit tests | Hard-coded return values, skipped algorithm implementation | h-e1 validation: all tiers return constant True | **DEFINITIVE** | Current results invalid everywhere; boundary defines minimum for valid experiment |
| **Detection Tier** | Data loading, model training infrastructure | Tier 1, Tier 2, Tier 3 detection algorithms | 04_checkpoint.yaml: 2/7 components validated (data loader, training), 3/7 failed (detection tiers) | **HIGH** | Only non-detection components validated |
| **Contamination Type** | Real GSM8K dataset loaded | Actual contamination injection, paraphrasing validation | Mock validation passed for data loading; contamination protocol not validated | **MEDIUM** | Uncertain if contamination injection matches EAL protocol |
| **Training Phase** | Finetuning (per scope decision) | Pretraining | Phase 2A established_facts: "Finetuning is dominant contamination risk" (builds on Fu et al. 2024) | **HIGH** | Scope limitation correctly maintained (this is acceptable) |
| **Task Domain** | Arithmetic reasoning (GSM8K) | Code (HumanEval), competition math (MATH), open-NLP | Experiment design (02c): single dataset validation | **HIGH** | Scope limitation for PoC (acceptable; requires extension) |
| **Model Architecture** | Decoder-only transformers (GPT-style) | Encoder-decoder, encoder-only, non-transformer models | Experiment used Pythia-1.4B (GPTNeoX, decoder-only) | **MEDIUM** | Architecture generality untested |
| **Model Scale** | 1-2B parameters (Pythia-1.4B actually used) | 7B+ (Llama-2-7B was planned), <1B, >10B | Experiment substituted Pythia-1.4B for planned Llama-2-7B | **LOW** | Scale generality unknown; deviation from plan |
| **Contamination Rate** | 1%, 5% (planned) | <0.1% (below statistical power), >10% (outside EAL regime) | Phase 2A scope: 1-5% injection per EAL protocol | **MEDIUM** | Planned range not fully tested (experiment aborted) |
| **Detection Threshold Calibration** | Never performed | Required for <5% FPR guarantee | No threshold calibration in experiment | **DEFINITIVE** | Critical gap; thresholds from Phase 2A are theoretical, not empirical |

**Boundary Interpretation:**

- **DEFINITIVE boundaries:** Results definitively invalid (implementation failure) or definitively required (threshold calibration)
- **HIGH confidence boundaries:** Strong evidence from validation reports or design documents
- **MEDIUM confidence boundaries:** Indirect evidence or single-run observations
- **LOW confidence boundaries:** Speculative based on untested assumptions

**Critical Boundaries for Future Work:**
1. **Implementation Quality** (DEFINITIVE) - Must implement actual detection algorithms before any claims are valid
2. **Detection Threshold Calibration** (DEFINITIVE) - Must calibrate thresholds on clean baseline to achieve <5% FPR
3. **TSG Paraphrase-Invariance** (HIGH) - Must validate TSG invariance before claiming Tier 2 novelty

### 6.3 Assumption Violation Impact Assessment

| Assumption | Violation Status | Severity | Affected Claims | Mitigation Strategy | Residual Risk |
|------------|-----------------|----------|-----------------|--------------------|--------------| |
| "Contamination gains arise from task-specific parameter alignment" | **UNVERIFIED** (not VIOLATED - never tested) | **HIGH** | Tier 3 geometric detection, differential alignment (Tier 2), geometric inevitability theorem | Implement gradient computation (task-010), measure actual cosine similarity on contaminated vs clean runs | If violated: entire geometric detection approach collapses; must find alternative detection signals |
| "Achieving ≥10% gains requires parameter updates correlated with benchmark gradients" | **UNVERIFIED** (never tested) | **CRITICAL** | All geometric signatures, Pareto constraint, theoretical contribution | Phase 0 validation experiment: measure gradient correlation on known-contaminated models (e.g., models trained on leaked benchmark data) | If violated: theoretical framework invalid; no geometric inevitability |
| "TSGs can be extracted with paraphrase-invariance" | **UNVERIFIED** (TSG extraction not implemented) | **HIGH** | Tier 2 detection, differential alignment novelty | Implement TSG extraction (task-013), test on paraphrased samples (GPT-4), measure invariant preservation rate | If violated: Tier 2 collapses to instance similarity (which EAL evades); architecture reduces to Tier 1 + Tier 3 |
| "Probe families are task-complete (span benchmark manifold)" | **UNVERIFIED** (probe generation not implemented) | **MEDIUM** | Tier 2 coverage, adversarial robustness | Adaptive adversary experiment (h-m4) with probe access; measure coverage via gain-suppression curves | If violated: adversary finds blind spots; detection power drops below 80% |
| "Finetuning is dominant contamination risk" | **VERIFIED** (scope decision based on Fu et al. 2024) | **LOW** (scope, not validity issue) | Scope of applicability (finetuning only) | Acknowledge pretraining contamination is out-of-scope; cite Fu et al. MIA findings | If violated: method inapplicable to pretraining; requires separate detection approach (acceptable scope limitation) |

**Impact Severity Levels:**
- **CRITICAL:** If assumption violated, entire theoretical framework collapses (no mitigation possible)
- **HIGH:** If assumption violated, major claims eliminated (requires alternative approach)
- **MEDIUM:** If assumption violated, performance degrades but some claims survive (requires adaptation)
- **LOW:** If assumption violated, scope narrows but core contribution remains (acceptable limitation)

**Critical Path for Validation:**
1. Verify "gradient correlation" assumption (CRITICAL) - Without this, geometric detection has no theoretical basis
2. Validate "TSG paraphrase-invariance" assumption (HIGH) - Without this, Tier 2 novelty claim collapses
3. Test "probe task-completeness" assumption (MEDIUM) - Without this, adversarial robustness is uncertain

**Current Status:** All critical assumptions remain UNVERIFIED due to implementation failure. This represents maximum theoretical uncertainty - we cannot distinguish between "hypothesis is wrong" and "hypothesis is correct but untested."

---

## 7. Future Work

All future work directions are grounded in the current experiment results (implementation failure analysis) and unvalidated assumptions. These are NOT speculative extensions - each direction traces back to a specific gap revealed by the experiment.

### 7.1 From Implementation Failure and Unexpected Findings

#### FW1: Per-Tier Unit Testing Before Integration (PRIORITY: REQUIRED)

- **Motivation:** Current experiment demonstrates that passing data validation (mock data checks) does not ensure detection algorithm correctness. All three detection tiers returned hard-coded True values despite passing external validation.

- **Why Not Yet Tested:** Phase 4 workflow emphasized end-to-end integration testing (via mock data validation) without requiring per-tier unit tests. This created a testing gap where data loading was validated but detection logic was not.

- **Proposed Experiment:**
  - **Tier 1 Unit Tests:** Create synthetic dataset pairs (exact duplicates, near-duplicates via text perturbation, paraphrases via GPT-4). Test LSH fingerprinting achieves >95% detection on exact/near-duplicate, <10% detection on paraphrases. Validate temporal filter correctly uses GSM8K release date (2021-11-01).
  - **Tier 2 Unit Tests:** Extract TSG invariants from toy dataset (10-20 arithmetic problems). Apply paraphrasing. Measure invariant preservation rate (target: ≥80%). Test differential alignment Δ computation on synthetic loss trajectories.
  - **Tier 3 Unit Tests:** Use small model (e.g., GPT-2 124M) on toy dataset. Verify gradient overlap, Hessian concentration, CKA alignment, efficiency z-score can be computed (not that they exceed thresholds - just that computation succeeds). Test ≥2/4 threshold logic on synthetic metric values.

- **Expected Outcome:** If unit tests pass, integration should produce valid detector (not 100% FPR). If unit tests fail, reveals which specific tier has implementation bugs.

- **Why This Matters:** Establishes minimum validation bar before claiming detection results. Prevents repetition of current failure mode (passing data checks while skipping algorithm implementation).

- **Feasibility:** HIGH - Standard software engineering practice; requires ~1-2 weeks per tier

- **Priority:** **REQUIRED** - Cannot proceed to hypothesis testing without validated implementation

#### FW2: Root Cause Analysis of Mock Validation Scope Gap (PRIORITY: HIGH)

- **Motivation:** External mock validation (attempt 2) reported "PASSED - All hard-coded accuracy calculations have been replaced with real evaluation" (04_validation.md line 215-217), yet detector still produced 100% FPR. This suggests validation scope was insufficient.

- **Alternative Explanations:**
  1. Validation tested wrong code paths (checked `run_experiment.py` training metrics but not `tier*.py` detection logic)
  2. Validation scope excluded detection algorithms (focused on data loading + model training, treated detection as separate concern)
  3. Detection implementation regressed after passing validation (unlikely - no evidence in version control)

- **Why Not Yet Distinguished:** Current validation report (04_validation.md) documents that mock validation passed but does not include the validation test suite code (`test_mock_fix.py`). We cannot determine what was actually tested.

- **Proposed Investigation:**
  1. Review `test_mock_fix.py` validation script: What code paths were tested? What patterns were searched for?
  2. Check version control history: Was detection logic ever implemented correctly, or was it always hard-coded True?
  3. Expand validation to include per-tier detection calls: Test that each tier's detect() method returns different values for clean vs contaminated inputs

- **Expected Outcome:**
  - If Explanation #1 (wrong code paths): Validation should be extended to cover `tier*.py` detection methods
  - If Explanation #2 (scope exclusion): Validation philosophy needs revision (data + algorithm correctness, not data alone)
  - If Explanation #3 (regression): Version control should reveal when/why regression occurred

- **Why This Matters:** Prevents future pipelines from repeating this failure mode. Generalizes to meta-lesson: "What should mock data validation check?"

- **Feasibility:** HIGH - Code review + git history analysis; ~1 week

- **Priority:** HIGH - Meta-contribution to research pipeline design (though not original research goal)

### 7.2 From Unverified Assumptions (Critical Path to Hypothesis Validation)

#### FW3: Task Signature Graph (TSG) Paraphrase-Invariance Validation (PRIORITY: CRITICAL)

- **Unverified Assumption:** "Task Signature Graphs can be extracted for math problems with sufficient paraphrase-invariance to enable detection that resists EAL-style attacks"

- **Current Status:** UNVERIFIED - TSG extraction was never implemented (task-013 in 03_tasks.yaml skipped)

- **Why This Is Critical:** TSG paraphrase-invariance is the core novelty enabling Tier 2 detection. Without it, Tier 2 collapses to instance-level similarity matching, which EAL evades (TPR<2% @ 1%FPR per Dekoninck et al. 2024). This assumption should have been validated BEFORE building a full detection architecture around it.

- **Proposed Validation Experiment (Phase 0 PoC):**
  - **Step 1:** Implement TSG extraction for arithmetic reasoning
    - Method 1: Constraint canonicalization (extract equation structure: "X + Y = Z" → abstract pattern)
    - Method 2: Program synthesis (convert word problem to executable program, extract computational graph)
  - **Step 2:** Create test set: 100 GSM8K problems + GPT-4-paraphrased variants
  - **Step 3:** Measure preservation rate: For each (original, paraphrase) pair, extract TSGs and compute structural similarity
  - **Success Criterion:** ≥80% of paraphrased problems preserve TSG structure (>= 0.8 Jaccard similarity on constraint sets)
  - **Failure Criterion:** <60% preservation rate → TSG approach not viable for paraphrase-invariant detection

- **Expected Outcomes:**
  - **If Success:** TSG-based Tier 2 detection is feasible; proceed with full implementation (task-013, task-014)
  - **If Failure:** TSG approach not paraphrase-invariant; must redesign Tier 2 or eliminate it (architecture becomes Tier 1 + Tier 3 only)

- **Why This Matters:** Determines whether Tier 2 novelty claim is viable. Validates Phase 2A theoretical assumption before committing to full Phase 3-4 implementation. Should be a prerequisite for future attempts at this hypothesis.

- **Feasibility:** MEDIUM - Requires non-trivial NLP (constraint extraction) or program synthesis; ~2-4 weeks

- **Priority:** **CRITICAL** - Core novelty depends on this; should be Phase 0 validation before re-attempting pipeline

#### FW4: Gradient Correlation Validation on Known-Contaminated Models (PRIORITY: CRITICAL)

- **Unverified Assumption:** "Achieving ≥10% benchmark gains from ≤5% contamination injection requires parameter updates correlated with benchmark gradients (geometric inevitability foundation)"

- **Current Status:** UNVERIFIED - No gradient computation was performed (task-010 skipped); geometric metrics never measured

- **Why This Is Critical:** This assumption is the foundation of the entire geometric detection approach (Tier 3) and the theoretical contribution (Pareto constraint, geometric inevitability theorem). If contamination gains do NOT require gradient alignment, then:
  - All Tier 3 geometric metrics (gradient overlap, Hessian concentration, CKA, efficiency) are invalid detection signals
  - Geometric inevitability theorem collapses (no Pareto constraint)
  - Theoretical contribution is eliminated

- **Proposed Validation Experiment (Phase 0 Proof-of-Concept):**
  - **Setup:** Use models with known contamination (not simulated - actual leaked benchmark data in training)
    - Option A: Public models trained on web-scraped data containing benchmark leaks (e.g., CodeLlama models before benchmark filtering)
    - Option B: Deliberately train contaminated model: Llama-2-7B finetuned on GSM8K train (100% contamination, not paraphrased)
  - **Measurement:** Compute gradient overlap between:
    - Contaminated model's parameter updates during finetuning
    - Gradient direction of benchmark test set (∇θ L(GSM8K_test))
  - **Control:** Clean baseline model finetuned on MATH dataset (no GSM8K)
  - **Success Criterion:** Contaminated model shows cosine similarity ≥ +0.10 vs clean baseline
  - **Failure Criterion:** Contaminated model shows cosine similarity ≈ clean baseline (no detectable difference)

- **Expected Outcomes:**
  - **If Success:** Gradient correlation assumption validated; Tier 3 geometric detection viable; proceed with full implementation
  - **If Failure:** Geometric inevitability assumption false; must abandon Tier 3 or find alternative geometric signals (Hessian? CKA? Efficiency?)

- **Alternative Test (If Gradient Correlation Fails):**
  - Test whether OTHER geometric signals (Hessian anisotropy, CKA compression, information efficiency) correlate with contamination even if gradient overlap does not
  - This would require revising the causal mechanism but might preserve some geometric detection capability

- **Why This Matters:** Determines whether the entire geometric detection approach (Tier 3) and theoretical framework (geometric inevitability) have any validity. This should be a Phase 0 validation experiment, not discovered during Phase 4.

- **Feasibility:** MEDIUM-HIGH - Requires access to models with known contamination + gradient computation; ~2-3 weeks

- **Priority:** **CRITICAL** - Entire theoretical contribution depends on this; should gate any future attempt at this hypothesis

#### FW5: Empirical Threshold Calibration on Clean Baseline (PRIORITY: HIGH)

- **Unverified Assumption:** "Detection thresholds specified in Phase 2A hypothesis (2σ, +0.10, 1.5×, ≥0.15, ≥2.5) will achieve target <5% false positive rate when applied to actual clean training runs"

- **Current Status:** UNVERIFIED - No threshold calibration was performed; thresholds are theoretical (from Phase 2A reasoning), not empirical

- **Why This Is Critical:** The gate condition requires ≥80% detection power AT <5% false positive rate. Without threshold calibration on clean baseline, we cannot guarantee the FPR constraint. Arbitrary thresholds might produce:
  - Too strict thresholds → low detection power (fail gate)
  - Too loose thresholds → high FPR (fail gate, as occurred with 100% FPR in current experiment)

- **Proposed Calibration Experiment:**
  - **Phase 1: Collect Clean Baseline Distribution**
    - Train N=20 clean models (0% contamination) across different random seeds
    - Measure all Tier 3 metrics at each checkpoint:
      - Gradient overlap with GSM8K test set
      - Hessian concentration ratio (top-10 eigenvalues)
      - CKA alignment with GSM8K vs MATH
      - Information efficiency z-score
  - **Phase 2: Set Thresholds at 95th Percentile**
    - For each metric, compute 95th percentile of clean distribution
    - Set detection threshold = 95th percentile (ensures 5% FPR by construction on held-out clean validation set)
  - **Phase 3: Validate on Held-Out Clean Set**
    - Train additional N=10 clean models (held-out from calibration)
    - Measure FPR using calibrated thresholds
    - Success: FPR ≤ 5%; Failure: FPR > 5% (calibration insufficient)

- **Expected Outcome:** Calibrated thresholds should achieve target <5% FPR. If FPR still exceeds 5%, indicates clean distribution has high variance or metric is unstable (requires alternative detection signal).

- **Why This Matters:** Threshold calibration is a standard step in binary classification that was missing from Phase 3 implementation plan (03_tasks.yaml has no calibration task). Without it, cannot make FPR guarantees required by gate condition.

- **Feasibility:** HIGH - Standard statistical procedure; requires N=30 clean training runs (~1-2 weeks compute time on single GPU)

- **Priority:** HIGH - Required before any valid detection power claims can be made

### 7.3 From Scope Extension Opportunities

#### FW6: Domain Generalization Beyond GSM8K Arithmetic (PRIORITY: MEDIUM)

- **Current Scope Boundary:** Results (when correctly implemented) expected to hold for GSM8K-style arithmetic reasoning; may not hold for code (HumanEval), competition math (MATH), or open-ended NLP (TruthfulQA).

- **Evidence for Boundary:** Experiment design (02c_experiment_brief.md) explicitly scoped to GSM8K only for PoC validation. Phase 2A prediction P3 hypothesized ≥80% detection on structured domains (code/math), 50-60% on open-NLP, but this was never tested.

- **Why Extension Matters:** Detection architecture claims to work across structured domains via TSG abstraction. If architecture only works for arithmetic (not code, formal proofs, etc.), contribution is narrow.

- **Feasibility Assessment:**
  - **Code (HumanEval):** TSG extraction likely feasible via abstract syntax trees (AST) and program dependency graphs. Paraphrase-invariance testable via code paraphrasing (variable renaming, control flow restructuring). Expected detection: ≥80% per P3.
  - **Competition Math (MATH):** Similar to GSM8K but harder problems, more formal notation. TSG extraction may require CAS (Computer Algebra System) parsing. Expected detection: ≥80% per P3.
  - **Open-NLP (TruthfulQA):** TSG extraction problematic (no clear constraint structure in open-ended questions). Expected detection: 50-60% per P3 (degradation acknowledged in hypothesis).

- **Proposed Extension Path:**
  1. Validate on Code (HumanEval) - Closest to GSM8K in structure
  2. Validate on Competition Math (MATH) - Tests robustness to problem difficulty
  3. Test on Open-NLP (TruthfulQA) - Establishes boundary of TSG applicability

- **Expected Challenges:**
  - TSG extraction for code requires AST parsing + program synthesis (non-trivial)
  - Open-NLP may not support TSG extraction at all (might need alternative Tier 2 approach for unstructured domains)

- **Required Resources:** ~3-6 months for cross-domain validation (1-2 months per domain)

- **Priority:** MEDIUM - Important for generality claim but not critical for core hypothesis validation. Should follow FW3 (TSG validation) and FW4 (gradient correlation validation).

#### FW7: Model Scale Generalization (1B → 7B → 70B) (PRIORITY: LOW)

- **Current Scope Boundary:** Experiment used Pythia-1.4B (deviated from planned Llama-2-7B). Generalization to larger models (70B+) or smaller models (<1B) untested.

- **Evidence for Boundary:** Single model scale tested. No theoretical reason to expect scale dependence, but no empirical validation either.

- **Why Extension Matters:**
  - Larger models (70B+): Most concerning for contamination risk (deployed in production)
  - Smaller models (<1B): Useful for rapid experimentation

- **Feasibility Assessment:**
  - **Computational Feasibility:**
    - 7B models: Trainable on single H100 (current setup)
    - 70B models: Require multi-GPU (4-8 H100s) + gradient checkpointing
    - Hessian computation: Becomes prohibitive at 70B+ scale (quadratic memory) → may need approximations (power iteration, Lanczos)
  - **Expected Behavior:**
    - Hypothesis assumes geometric signatures are scale-invariant (gradient alignment, Hessian anisotropy should appear at all scales)
    - If scale-dependent, might indicate detection is measuring scale-related artifacts, not contamination

- **Proposed Validation:**
  1. Replicate at 7B scale (Llama-2-7B as originally planned)
  2. Test at 70B scale if 7B results confirm hypothesis
  3. Compare detection metrics across scales: Do thresholds need recalibration?

- **Priority:** LOW - Scale generalization is valuable but not critical for core hypothesis. Larger models increase cost significantly; defer until core hypothesis validated at 1-7B scale.

---

## 8. Implications for Phase 6 Paper Writing

This section provides direct guidance for Phase 6 narrative design, evidence selection, and honest limitation framing. **Phase 6 MUST NOT write a paper claiming successful detection** - the experiment completely failed. Instead, Phase 6 should consider whether to:
1. Write a "Negative Results" paper documenting the failure mode
2. Abort paper writing and route back to Phase 0 for reconceptualization

### 8.1 Recommended Narrative Hook

**DO NOT write a standard paper hook claiming success.** Standard hooks like "contamination is an urgent problem" or "prior detection methods fail" are NOT applicable because our proposed solution also failed (100% FPR).

**Option A: Negative Results Framing (if publishing failure)**

*"We report a fundamental failure mode in research pipeline execution: passing mock data validation checks does not guarantee algorithm implementation correctness. Our three-tier contamination detection architecture achieved 100% detection power with 100% false positive rate because all detection algorithms were replaced with hard-coded True return values during Phase 4 implementation, despite external validation confirming that real datasets (GSM8K, MATH) were loaded correctly. This failure highlights a systematic testing gap in computational research: data loading correctness is necessary but insufficient for experiment validity."*

**Why This Hook Works (For Negative Results):**
- Frames failure as generalizable lesson (testing methodology) not just our incompetence
- Specific and concrete (100%/100% metrics immediately signal something wrong)
- Relevant to broader research community (reproducibility, validation practices)

**Option B: Do Not Write Paper**

Given that:
- Zero theoretical contributions validated
- Zero predictions supported
- Hypothesis routed to Phase 0 for reconceptualization (per reflection outcome)
- No novel findings beyond documenting our own implementation failure

**Recommendation:** **Abort paper writing.** Route back to Phase 0 for fundamental reconceptualization per reflection decision (04_checkpoint.yaml: reflection_outcome = "ROUTED_TO_PHASE_0"). A negative results paper documenting testing methodology gaps is possible but low priority compared to fixing the hypothesis and re-executing correctly.

### 8.2 Key Insight (Experiment-Verified)

**NO positive insights were validated.** The single verified insight is a negative finding about research methodology:

**Verified Insight:** *"Mock data validation that checks dataset loading correctness is insufficient to ensure detection algorithm implementation. In our experiment, all three detection tiers (data-layer filters, TSG probes, geometric metrics) returned hard-coded True values, producing a tautological detector with 100% false positive rate, despite passing external validation that confirmed real datasets (GSM8K, MATH) were loaded correctly. This demonstrates that data loading correctness and algorithm correctness are orthogonal concerns requiring independent validation."*

**Evidence Reference:** h-e1/04_validation.md lines 11-24 (Executive Summary), lines 387-416 (Root Cause Analysis), 04_checkpoint.yaml lines 387-416 (reflection routing)

**Confidence Level:** HIGH (externally validated, clear causal chain from hard-coded logic → 100% FPR)

**Why This Matters:** Generalizable lesson for research pipelines; highlights need for per-component unit testing; relevant to reproducibility literature

**Limitation:** This is a meta-finding about research methodology, not a finding about contamination detection (the original research goal)

### 8.3 Strongest Claims (Paper-Ready)

**IMPORTANT: There are NO strong claims about contamination detection because the experiment failed.** 

If writing a negative results paper, the following methodology claims have evidence:

| Claim | Evidence | Confidence | Suggested Section | Caveat |
|-------|----------|------------|------------------|--------|
| "Mock data validation checking dataset loading is insufficient to ensure algorithm correctness" | h-e1 validation passed mock checks yet produced 100% FPR due to hard-coded detection logic | **HIGH** | Introduction (Problem), Discussion (Lessons) | Meta-claim about testing, not about contamination detection |
| "Constant function detector (always predicts positive) produces 100% detection power and 100% false positive rate" | h-e1: 100% power, 100% FPR | **DEFINITIVE** | Results (Failure Analysis) | Obvious ML fact; included for completeness but not novel |
| "Implementation gap: 10/15 Phase 3 tasks (67%) were not implemented despite being specified" | Planned-vs-actual comparison (Section 5.6) shows all detection tier tasks skipped | **HIGH** | Results (Implementation Analysis) | Documents failure magnitude; relevant for pipeline design |

**ZERO claims about:**
- Detection power (tautological result)
- TSG paraphrase-invariance (never tested)
- Geometric inevitability (never tested)
- Tier-specific detection mechanisms (never implemented)
- Domain generalization (not tested)

**Phase 6 Guidance:** If attempting to write a standard paper claiming contamination detection success, **STOP IMMEDIATELY**. The experiment completely failed. No claims about detection effectiveness are supported.

### 8.4 Honest Limitations (Must Include in Paper)

If writing a negative results paper, these limitations MUST appear prominently (not buried in appendix):

#### L1: Complete Implementation Failure (MUST BE FIRST)

**Framing:** *"Our experiment failed to test the theoretical hypothesis due to fundamental implementation issues. All three detection tiers returned hard-coded True values instead of computing actual detection metrics (LSH fingerprinting, differential alignment, gradient/Hessian/CKA/efficiency signatures). This means the theoretical mechanisms (contamination produces detectable geometric signatures, Pareto constraint limits evasion) were never actually tested. We cannot conclude whether the hypothesis is true or false - only that the experiment failed to evaluate it."*

**Why Acceptable:** This is NOT acceptable for a standard research paper. For a negative results paper documenting research methodology failures, this is the primary finding.

**Section Placement:** Abstract, Introduction (Problem Statement), beginning of Results

#### L2: Zero Validated Contributions

**Framing:** *"No theoretical contributions were validated. The hypothesis remains completely untested: (1) Task Signature Graph paraphrase-invariance was never demonstrated (TSG extraction not implemented), (2) geometric inevitability theorem was never tested (adaptive adversary experiments not executed), (3) combined detection power of ≥80% at <5% FPR was not achieved (100% FPR makes detector unusable)."*

**Why Acceptable:** NOT acceptable for standard paper; acceptable for negative results paper as honest documentation of failure

**Section Placement:** Discussion (Limitations), Conclusion

#### L3: Threshold Calibration Never Performed

**Framing:** *"Even if detection algorithms had been correctly implemented (which they were not), the specified thresholds (2σ, +0.10, 1.5×, ≥0.15, ≥2.5) were never validated empirically on clean baseline data. The <5% false positive rate requirement cannot be guaranteed without threshold calibration on N=20 clean runs to set thresholds at the 95th percentile."*

**Why Acceptable:** Addressable limitation (calibration is standard procedure) but reinforces that experiment had multiple failure points

**Section Placement:** Discussion (Future Work)

#### L4: Statistical Power Insufficient

**Framing:** *"Phase 2A specified N=20 independent runs per condition (60 total) for statistical power. Actual experiment executed N=1 run before detection failure was discovered. Single-run results cannot establish statistical significance or provide confidence intervals. However, continuing to N=20 would not have fixed the hard-coded detection logic."*

**Why Acceptable:** Correct decision to abort after systematic failure detected; not random variance

**Section Placement:** Methods (Experimental Design), Discussion (Limitations)

### 8.5 Evidence Highlights (Most Persuasive)

**For negative results paper documenting research methodology failure:**

#### E1: Perfect Detection with Perfect False Positives (Figure Opportunity)

- **Data:** 100% detection power, 100% false positive rate (h-e1 gate results)
- **So What:** This is mathematically impossible for a meaningful detector - it's the signature of a constant function classifier (always predicts positive). Immediately signals fundamental implementation failure.
- **Suggested Visualization:** 2×2 confusion matrix showing all samples (clean and contaminated) classified as "contaminated"
- **Section Placement:** Results (Failure Analysis), Figure 1

#### E2: Planned vs Actual Implementation Gap (Table Opportunity)

- **Data:** Section 5.6 planned-vs-actual comparison showing 10/15 tasks (67%) not implemented
- **So What:** Demonstrates systematic failure, not isolated bug. All three detection tiers (Tier 1, Tier 2, Tier 3) and their subtasks were skipped despite Phase 3 specification.
- **Suggested Visualization:** Gantt-style chart showing planned tasks (03_tasks.yaml) vs actual implementation (04_validation.md) with color-coding: green=implemented, red=not implemented, yellow=partial
- **Section Placement:** Results (Implementation Analysis), Figure 2 or Table 2

#### E3: Mock Validation Pass Despite Broken Detection (Timeline Opportunity)

- **Data:** External mock validation (attempt 2) reported "PASSED" (04_validation.md lines 215-217), yet detector still produced 100% FPR
- **So What:** Illustrates the validation scope gap - mock validation checked data loading (passed) but not detection logic (failed). Shows orthogonality of data correctness and algorithm correctness.
- **Suggested Visualization:** Timeline showing: (1) Mock validation PASS → (2) Experiment execution → (3) 100% FPR detected → (4) Root cause analysis reveals hard-coded True returns
- **Section Placement:** Discussion (Lessons Learned), Figure 3

#### E4: Zero Mechanism Steps Verified (Causal Chain Diagram Opportunity)

- **Data:** Section 3.3 verified causal chain diagram showing all 4 mechanism steps FALSIFIED (not tested)
- **So What:** Visual demonstration that theoretical hypothesis was completely untested. Original chain (Phase 2A) vs verified chain (Phase 4.5) side-by-side shows 100% gap.
- **Suggested Visualization:** Two flowcharts side-by-side:
  - Left: Original hypothesis (Contamination → Gradient Alignment → Hessian Anisotropy → CKA Compression → Efficiency Anomaly → Detection)
  - Right: Verified chain (Contamination → [FALSIFIED] → [FALSIFIED] → [FALSIFIED] → [FALSIFIED] → NO DETECTION)
- **Section Placement:** Results (Hypothesis Validation), Figure 4

#### E5: Cascade Failure Impact (Dependency Graph Opportunity)

- **Data:** Section 5.1 per-hypothesis results showing h-e1 FAILED → h-m1, h-m2, h-m3 CASCADE_FAILED
- **So What:** Demonstrates how foundation hypothesis failure (h-e1 EXISTENCE gate fail) propagates through entire hypothesis dependency structure, preventing testing of mechanism hypotheses (h-m1, h-m2, h-m3) and adaptive adversary experiment (h-m4).
- **Suggested Visualization:** Dependency graph with nodes for each hypothesis (h-e1, h-m1, h-m2, h-m3, h-m4) color-coded by status: red=FAILED, orange=CASCADE_FAILED, gray=NOT_STARTED. Show prerequisite arrows (h-m1/h-m2/h-m3 → h-e1, h-m4 → h-m1/h-m2/h-m3).
- **Section Placement:** Results (Cascade Impact), Figure 5 or Supplementary

**CRITICAL GUIDANCE FOR PHASE 6:**

If Phase 6 attempts to write a standard research paper claiming contamination detection success based on these results, **Phase 6 has fundamentally misunderstood the experiment outcome**. The evidence above documents FAILURE, not success. The only viable paper from these results is a negative results paper about research methodology, which is low priority compared to fixing the hypothesis and re-executing.

**Recommended Action:** Abort Phase 6 paper writing. Route back to Phase 0 for reconceptualization per reflection decision.

---

**Document Generated:** 2026-05-11  
**Phase 4.5 Version:** 2.0  
**Status:** COMPLETE  
**Reflection Outcome:** ROUTED_TO_PHASE_0 (reconceptualization required)  
**Next Phase:** Phase 0 (Brainstorm) - Fundamental approach reconceptualization  
**Serena Memory:** failure_h-e1_run3.md documented with full failure analysis  
**Pipeline State:** Sub-hypotheses complete (1 FAILED, 3 CASCADE_FAILED, 1 NOT_STARTED); synthesis complete

