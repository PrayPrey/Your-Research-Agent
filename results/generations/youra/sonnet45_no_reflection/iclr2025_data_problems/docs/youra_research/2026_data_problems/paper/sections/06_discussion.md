# Discussion

We interpret our results as documenting a systematic failure mode in research pipeline execution: validation strategies focused on data provenance (checking for hard-coded results, verifying real datasets) are insufficient without per-component algorithm verification. Our three-tier contamination detection architecture passed mock data validation while completely failing to implement detection logic, producing a constant function classifier with 100% false positive rate.

## Key Findings and Interpretation

**Finding 1: Data Validation ≠ Algorithm Validation**

Mock data validation verified that real datasets (GSM8K with 7,473 training samples, MATH with 12,500 problems) were loaded correctly and training metrics were computed from actual model outputs rather than hard-coded formulas. However, this validation did not check whether detection algorithms were implemented. All three detection tiers returned hard-coded `True` values without performing actual computations (LSH fingerprinting, differential alignment, gradient/Hessian/CKA analysis).

**Implication:** Data loading correctness and algorithm implementation correctness are orthogonal concerns requiring independent validation. A research pipeline can satisfy input validation (correct data provenance) while completely failing output validation (meaningful processing). The consequence is wasted research resources: our experiment consumed computational budget and researcher time testing a detector that never actually performed detection.

**Why This Matters:** Mock data validation has become a standard practice in machine learning research to prevent hard-coded results and ensure experiments use real data. Our experience shows this practice is necessary but insufficient. Validation scope must extend beyond "are inputs correct?" to "does processing produce meaningful outputs?" Without per-component verification, implementation gaps can pass integration-level validation.

**Finding 2: Systematic Implementation Gap, Not Random Bug**

Implementation gap analysis (Table 2) revealed 10 of 15 planned tasks (67%) were not executed, systematically targeting all detection components:
- Tier 1: 0% completion (2 of 2 tasks not implemented)
- Tier 2: 0% completion (3 of 3 tasks not implemented)
- Tier 3: 0% completion (5 of 5 tasks not implemented)

This is not a collection of random bugs but a systematic pattern: only non-detection components (data loading, training loop) were implemented. The implementation satisfied external validation requirements (data loading correctness) while bypassing the core research contribution (detection algorithms).

**Interpretation:** The pattern suggests Phase 4 implementation prioritized passing validation over implementing functionality. When validation checks operate at the integration level (end-to-end testing) without component-level verification, implementation can satisfy validation by implementing only the validated paths (data loading) while skipping unvalidated components (detection logic).

**Broader Implication:** This failure mode may be more common than currently recognized in computational research. How many experiments pass validation by implementing only the input pipeline (data loading, preprocessing) while leaving core algorithms unimplemented or incorrectly implemented? Without per-component unit testing, such failures remain undetectable until integration testing reveals anomalous behavior (in our case, 100% FPR).

**Finding 3: The Original Hypothesis Remains Untested**

Our results do **not** refute the theoretical claims that: (1) contamination-induced gains produce detectable geometric signatures, (2) Task Signature Graphs provide paraphrase-invariant task representations, or (3) geometric inevitability (Pareto constraint) limits adversarial evasion. These claims remain speculative because no detection algorithms were executed. The failure was in implementation execution, not in theoretical design.

**What This Means for the Field:** The motivation for geometric detection remains valid: Fu et al. (2024) established that MIA fails in pretraining (AUC≈50%), and Dekoninck et al. (2024) showed EAL-style paraphrasing evades semantic detection (TPR<2% at 1% FPR). These limitations create a genuine research gap. However, our work has not filled this gap—we have only documented an implementation failure mode. Prior work (Fu et al., Dekoninck et al.) remains the state-of-the-art; we have not advanced contamination detection theory.

## Limitations

We organize limitations by severity and addressability.

### L1: Complete Implementation Failure (FUNDAMENTAL - Cannot Be Fixed Post-Hoc)

**Limitation:** All three detection tiers (Tier 1: data-layer filters, Tier 2: TSG probes, Tier 3: geometric metrics) were not implemented. Detection algorithms returned hard-coded `True` values, producing a constant function classifier with zero discrimination capability.

**Why This Matters:** The theoretical hypothesis ("contamination produces detectable geometric signatures") was never actually evaluated. We cannot conclude whether the hypothesis is true or false—only that the experiment failed to test it. All claims about detection power, tier-specific performance, geometric inevitability, and Pareto constraints are invalidated.

**Why NOT Acceptable:** This is a fundamental failure that eliminates all research contributions. The only salvageable contribution is documenting the failure mode itself as a methodological lesson for the community. This limitation cannot be addressed through post-hoc analysis or additional experiments on the existing implementation—the code must be completely reimplemented with per-tier unit testing before any hypothesis claims can be evaluated.

**Impact on Future Work:** Before retrying this hypothesis, three prerequisite validation experiments are required (identified in Phase 4.5 future work analysis):
1. TSG paraphrase-invariance validation (Phase 0 proof-of-concept)
2. Gradient correlation validation on known-contaminated models
3. Per-tier unit testing infrastructure before integration

### L2: Detection Thresholds Never Calibrated Empirically (HIGH - Addressable but Not Reached)

**Limitation:** All detection thresholds (2σ for differential alignment, +0.10 for gradient overlap, 1.5× for Hessian concentration, ≥0.15 for CKA, ≥2.5 for efficiency z-score) were specified theoretically in Phase 2A hypothesis generation. These thresholds were never validated on actual clean baseline data to achieve the target <5% false positive rate.

**Why This Matters:** Even if detection algorithms had been correctly implemented (which they weren't), the specified thresholds might not achieve the <5% FPR requirement. Proper calibration requires training N=20 clean baseline runs and setting thresholds at the 95th percentile of clean distribution.

**Why This Is Addressable:** Threshold calibration is a standard statistical procedure. Once detection algorithms are correctly implemented, calibration is straightforward.

**Current Status:** Moot due to L1 (implementation failure at an earlier stage), but remains a required step for future attempts.

### L3: Task Signature Graph (TSG) Paraphrase-Invariance Unvalidated (HIGH - Prerequisite Experiment Needed)

**Limitation:** The core novelty claim—that TSG invariants extracted from math problems remain stable under GPT-4-level paraphrasing—was never tested. TSG extraction was not implemented (Task 013 in implementation plan).

**Why This Matters:** TSG paraphrase-invariance is the mechanism by which Tier 2 detection resists EAL-style attacks. If TSGs are not actually paraphrase-invariant, Tier 2 detection collapses to instance-level similarity, which EAL evades (TPR<2% @ 1% FPR per Dekoninck et al. 2024).

**Why NOT Acceptable for Novel Contribution:** Claiming TSG-based detection as a contribution requires demonstrating that TSG extraction preserves task structure under paraphrasing with ≥80% fidelity. This should be a Phase 0 proof-of-concept experiment before building a full detection architecture around it.

**Recommended Validation Experiment (From Phase 4.5 Analysis):**
1. Implement TSG extraction for 100 GSM8K problems
2. Apply GPT-4 paraphrasing to create variants
3. Measure TSG preservation rate (Jaccard similarity on constraint sets)
4. Success criterion: ≥80% preservation → TSG approach viable; <60% → approach not viable

### L4: Geometric Inevitability Theorem Untested (HIGH - Dependent on L1)

**Limitation:** The theoretical claim that suppressing geometric detection signals forces adversaries to sacrifice performance gains (convex Pareto frontier) was never tested. Adaptive adversary experiments (hypothesis h-m4) were not executed due to h-e1 gate failure.

**Why This Matters:** Geometric inevitability is the theoretical contribution distinguishing this work from prior detection methods. The claim is that evasion is fundamentally limited by the Pareto constraint: maximizing benchmark accuracy while minimizing detection signals creates a convex tradeoff, preventing "flat regions" (high gain + low signal).

**Why NOT Acceptable:** Without testing varying λ ∈ {0, 0.1, 0.5, 1.0, 2.0} in the adversarial objective `max(BenchmarkAcc - λ·DetectionSignal)`, we cannot verify whether the Pareto frontier is convex (as predicted) or flat (evasion possible). This eliminates a major theoretical contribution.

**Dependency:** This experiment requires h-e1 (foundation hypothesis) to pass its MUST_WORK gate. Since h-e1 failed due to implementation issues, h-m4 was never reached.

### L5: Single-Dataset Validation (MEDIUM - Acceptable for Proof-of-Concept)

**Limitation:** Experiment design scoped validation to GSM8K math reasoning only. Phase 2A hypothesis claimed generalization to structured domains (HumanEval code, MATH competition problems) with prediction P3 (≥80% detection on code/math, 50-60% on open-NLP).

**Why This Matters:** Detection mechanisms might be specific to GSM8K's particular problem structure. Generalization to other structured domains (code, formal proofs) or open-ended NLP tasks is unknown.

**Why Acceptable:** This is standard practice for EXISTENCE hypotheses: establish "does it work at all?" on a single dataset before testing domain generalization. Domain generalization would be tested in subsequent mechanism hypotheses (h-m1, h-m2, h-m3), but those were never reached due to h-e1 failure.

### L6: Statistical Power Insufficient (MEDIUM - Correct Decision Given Systematic Failure)

**Limitation:** Phase 2A specified N=20 independent runs per condition (60 total) for statistical power. Actual experiment executed N=1 run before detection failure was discovered.

**Why This Matters:** Single-run results have high variance and cannot establish statistical significance.

**Why Aborting Was Correct:** Continuing to N=20 would not fix hard-coded `True` returns. Aborting after detecting systematic failure (not random variance) was the correct decision to avoid wasting additional compute resources.

## Broader Impact

**Methodological Impact:** This work documents a validation gap in computational research: mock data validation checking dataset correctness is insufficient to ensure algorithm implementation. We recommend:

1. **Per-component unit testing before integration:** Each detection tier should have independent validation (e.g., test that Tier 1 LSH produces different outputs for duplicate vs. non-duplicate samples) before combined system testing.

2. **Validation scope expansion:** Validation strategies should check both data correctness (input validation) and algorithm correctness (output validation). A detector that produces identical outputs regardless of inputs is broken, even if it loads data correctly.

3. **Cascade failure awareness:** Hypothesis dependency structures amplify validation gaps. When foundation hypotheses fail, all dependent mechanism testing becomes impossible. Early-stage validation (Phase 0 proof-of-concept for core assumptions) reduces cascade failure risk.

**Impact on Contamination Detection Research:** Our work does not advance contamination detection theory. The research gap identified by Fu et al. (MIA fails in pretraining) and Dekoninck et al. (EAL evades semantic detection) remains open. Future work attempting geometric detection should:

1. Validate TSG paraphrase-invariance as Phase 0 experiment (before full architecture)
2. Validate gradient correlation assumption on known-contaminated models
3. Implement per-tier unit tests before integration
4. Calibrate detection thresholds empirically on clean baselines

**Positive Contribution:** While we failed to validate contamination detection theory, we provide a documented example of validation methodology failure that may help other researchers avoid similar pitfalls. The lesson: validation must verify algorithm implementation, not just data provenance.

## Limitations of This Discussion

This Discussion section interprets implementation failure as a methodological lesson. However, we acknowledge:

1. **Limited Generalizability:** This is a single case study. We do not know how common this failure mode is across computational research. Further study of validation practices and failure patterns would strengthen the methodological contribution.

2. **No Positive Alternative Demonstrated:** We identify validation gaps but do not implement and validate a solution (per-component unit testing infrastructure). Our recommendations are based on post-hoc failure analysis, not proactive validation success.

3. **Negative Results May Have Publication Bias:** Venues may reject negative results papers, limiting dissemination of methodological lessons. This paper is best suited for workshops on reproducibility, negative results tracks, or methodology-focused venues rather than main conference tracks expecting algorithmic contributions.
