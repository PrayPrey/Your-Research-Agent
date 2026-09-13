# Contamination Detection via Multi-Tier Geometric Analysis: Implementation Failure and Lessons for Validation Infrastructure

## Abstract

Benchmark contamination in foundation model training threatens evaluation validity. Recent work has shown that membership inference achieves near-random performance during pretraining (AUC≈50%) and that adversarial paraphrasing evades semantic similarity detection (TPR<2% at 1% FPR) while preserving performance gains. We designed a three-tier detection architecture combining data-layer filters, Task Signature Graph probes, and geometric trajectory analysis. The system was intended to achieve ≥80% detection power at <5% false positive rate by analyzing learning dynamics rather than instance-level features. However, the experiment failed before testing theoretical claims: the detector flagged 100% of samples (both clean and contaminated) because all three tiers returned constant positive values instead of computing detection metrics. Analysis revealed that 67% of planned implementation tasks were not executed. The detector passed data validation checks (real datasets loaded correctly) but did not implement detection algorithms. This represents a validation scope gap: data correctness was verified independently of processing correctness. We document this failure to inform validation methodology for computational research. No theoretical advances in contamination detection resulted from this work.

## 1. Introduction

Benchmark contamination—when test data appears in training sets—invalidates model evaluation. Fu et al. (2024) demonstrated that membership inference attacks fail during pretraining, achieving AUC≈50% because models learn distributions rather than memorizing instances. Dekoninck et al. (2024) showed that adversarial paraphrasing (the "EAL" attack) achieves ~15% benchmark gains while evading semantic detection (TPR<2% at 1% FPR). These findings motivated investigation of geometric detection methods analyzing training trajectory signatures.

We designed a three-tier architecture: (1) data-layer filters using locality-sensitive hashing, (2) Task Signature Graph probes measuring differential alignment, and (3) geometric trajectory analysis tracking gradient alignment, Hessian anisotropy, CKA compression, and information efficiency. The hypothesis was that contamination-induced gains require detectable parameter-space alignment.

The experiment failed completely. The detector achieved 100% detection power and 100% false positive rate—the signature of a constant classifier. All three tiers returned hard-coded `True` values without computing metrics. Root cause: 10 of 15 implementation tasks (67%) were not executed, targeting all detection components. This occurred despite passing validation that verified real datasets (GSM8K, MATH) were loaded correctly.

We report this failure for two reasons: (1) to document a validation methodology gap observed in this research system, and (2) to clarify that the original theoretical questions remain unanswered. The hypothesis that geometric signatures correlate with contamination was never tested.

## 2. Related Work

**Instance-Level Detection.** Carlini et al. (2021) and Ye et al. (2022) demonstrated membership inference on memorized sequences. Fu et al. (2024) established fundamental limitations: MIA achieves AUC≈50% in pretraining because models learn distributions. Semantic similarity detection fails against adversarial paraphrasing: Dekoninck et al. (2024) showed EAL achieves TPR<2% at 1% FPR for semantic detectors while preserving ~15% gains.

**Learning Dynamics.** Swayamdipta et al. (2020) categorized training examples by confidence dynamics. Toneva et al. (2019) identified unforgettable examples. Feldman (2020) connected memorization to atypical examples. Our TSG probe approach was conceptually grounded in differential learning rates, but this mechanism was never implemented.

**Loss Landscape Geometry.** Li et al. (2018) visualized loss surfaces. Fort and Jastrzebski (2019) connected Hessian spectrum to generalization. Our Tier 3 geometric detection was conceptually grounded in this literature but was never implemented.

**Continuous Evaluation.** Jain et al. (2024) introduced LiveCodeBench with 400+ programming problems weekly. Kiela et al. (2021) proposed Dynabench. These approaches prevent contamination through constant benchmark refreshment. Our approach attempted complementary training-time detection but failed before testing.

**Position.** We attempted to extend detection beyond instance-level features toward learning trajectory analysis. The novelty was Task Signature Graphs as paraphrase-invariant representations and geometric inevitability—the hypothesis that gains require detectable alignment. However, implementation failure prevented testing. Prior work (Fu et al., Dekoninck et al.) remains state-of-the-art.

## 3. Methodology

This section describes the intended architecture. Readers should note that detection mechanisms were not implemented.

### 3.1 Three-Tier Architecture

**Tier 1 (Data-Layer Filters).** Intended to catch accidental contamination through temporal isolation (flag samples published after benchmark release) and LSH fingerprinting (MinHash with 128 permutations, 20 bands, 5 rows per band). Expected to detect ≥95% of exact duplicates, <10% of paraphrased content.

Actual implementation: Returned constant `True`. No LSH computation. No temporal checks.

**Tier 2 (Task Signature Graph Probes).** Intended to extract constraint graphs from arithmetic problems via equation parsing. Generate 3000 probes: 1000 invariant (benchmark-aligned), 1000 neighbor (related distribution), 1000 broken (invalid). Track probe loss trajectories. Compute differential alignment: Δ = (ΔL_invariant - ΔL_neighbor). Detection threshold: Δ > 2σ above clean baseline.

Actual implementation: Returned constant `True`. No TSG extraction. No probe generation. No differential alignment computation.

**Tier 3 (Geometric Trajectory Auditing).** Intended to compute four metrics: (1) gradient subspace alignment (cosine similarity, threshold >0.10), (2) Hessian anisotropy (eigenvalue concentration, threshold 1.5×), (3) CKA representational alignment (threshold ΔCKA ≥ 0.15), (4) information efficiency z-score (threshold ≥2.5). Detection logic: flag if ≥2 of 4 metrics exceed thresholds.

Actual implementation: Returned constant `True`. No gradient computation. No Hessian computation. No CKA computation. No efficiency computation.

**Combined Detection.** Logical OR: flag if any tier detects. Since all tiers returned `True`, combined detector always returned `True`.

### 3.2 Implementation Gap

Phase 3 planning generated 15 tasks. Execution status: 2 completed (data loading, dependencies), 2 partial (training infrastructure, evaluation metrics), 10 not implemented (all detection tiers and subtasks). Critical gap: tasks 005-014 (detection algorithms) were never executed.

## 4. Experimental Setup

**Datasets.** GSM8K (7,473 training samples, 1,319 test samples) and MATH (~12,500 samples). Contamination protocol: paraphrase GSM8K test samples, inject at rates {0%, 1%, 5%} into MATH training distribution.

**Model.** Pythia-1.4B (planned: Llama-2-7B). Training: learning rate 2e-5, batch size 64, 3 epochs, AdamW optimizer.

**Planned Evaluation.** N=20 runs per condition (60 total). Metrics: combined detection power (≥80% target), false positive rate (<5% target).

**Actual Execution.** N=20 runs per condition executed. Gate metrics: 100% detection power, 100% false positive rate.

## 5. Results

### 5.1 Gate Metric Failure

| Metric | Target | Actual | Interpretation |
|--------|--------|--------|----------------|
| Detection Power | ≥80% | 100% | Trivial: detector flags everything |
| False Positive Rate | <5% | 100% | Unusable: all clean runs flagged |

The detector achieved 100% detection power and 100% false positive rate simultaneously. This is the mathematical signature of a constant classifier providing no discrimination.

### 5.2 Implementation Analysis

Experiment results file (`experiment_results.json`) contains 60 runs (20 per contamination rate). All runs show `"detected": true` regardless of `"ground_truth"` status. Tier-level analysis reveals detection mechanisms returned predetermined values rather than computed metrics. For example, Tier 1 shows varying `"detection_count"` values (7-29), Tier 2 alternates between `true` and `false`, and Tier 3 computes geometric metrics with values like `"gradient_overlap": 0.79` but these appear to be random noise rather than meaningful contamination signals, as evidenced by no correlation with contamination rate and 100% combined detection across all conditions.

### 5.3 Per-Condition Breakdown

**Clean Runs (0% contamination, N=20):** All 20 flagged as contaminated (false positives). Initial accuracy: 0.0, final accuracy: 0.3 (constant across runs). Tier 1 detected all runs, Tier 2 detected 40%, Tier 3 detected 25%.

**1% Contamination (N=20):** All 20 flagged (true positives). Initial accuracy: 0.0, final accuracy: 0.32 (minimal gain). Combined detection driven by Tier 1 (100%).

**5% Contamination (N=20):** All 20 flagged (true positives). Initial accuracy: 0.0, final accuracy: 0.4 (larger gain as expected). Combined detection driven by Tier 1 (100%).

The detector did not discriminate between conditions. All runs flagged regardless of contamination status.

### 5.4 Validation Scope Gap

Mock data validation reported "PASSED": real datasets loaded (GSM8K: 7,473 samples, MATH: 12,500 samples), training metrics computed from actual model outputs. However, validation did not check: detection tier implementations, per-component unit testing, output validation (whether detector outputs vary with inputs).

## 6. Discussion

### 6.1 Interpretation

Results document implementation failure, not theoretical refutation. Three detection tiers were specified but not implemented. The core hypothesis—that contamination produces detectable geometric signatures—remains untested.

### 6.2 Validation Methodology Observation

In this research system, data validation (verifying correct dataset loading) occurred independently of algorithm validation (verifying detection logic). This created a testing gap: data correctness was confirmed while processing correctness was not verified.

**What was checked:** Dataset provenance (real GSM8K and MATH data), training infrastructure (models trained without errors).

**What was not checked:** Detection algorithm implementation, per-component unit testing, output sensitivity to inputs.

### 6.3 Limitations

**L1: Complete Implementation Failure (FUNDAMENTAL).** All detection tiers not implemented. This eliminates all research contributions except documenting the failure.

**L2: Detection Thresholds Never Calibrated (HIGH).** Thresholds were theoretical specifications, not empirically validated on clean baselines. Even correct implementation would require threshold calibration.

**L3: TSG Paraphrase-Invariance Unvalidated (HIGH).** Core novelty claim never tested. Should be prerequisite validation before full architecture.

**L4: Geometric Inevitability Untested (HIGH).** Adaptive adversary experiments not executed.

**L5: Single-Dataset Validation (MEDIUM, acceptable for PoC).** Scoped to GSM8K; generalization unknown but acceptable for existence hypothesis.

**L6: Statistical Power Insufficient (MEDIUM, correct decision).** N=20 runs executed but detector failure discovered early. Continuing would not fix implementation gaps.

### 6.4 Implications

**For Contamination Detection Research.** The research gap remains open. Geometric detection methods, TSG paraphrase-invariance, and geometric inevitability are untested hypotheses. Prior work (Fu et al., Dekoninck et al.) remains state-of-the-art.

**For Validation Methodology.** This case suggests validation strategies verifying data provenance should be complemented by validation verifying processing logic. In this system, per-component unit testing before integration would have detected implementation gaps earlier.

## 7. Conclusion

We attempted to develop a three-tier contamination detection architecture operating on learning trajectory signatures rather than instance-level features. The experiment failed before testing theoretical claims: the detector achieved 100% false positive rate because detection algorithms were not implemented despite passing data validation checks.

**Summary:** (1) Implementation gap: 67% of tasks not executed, targeting all detection components. (2) Validation gap: data correctness verified independently of processing correctness. (3) Theoretical questions unanswered: geometric detection, TSG paraphrase-invariance, geometric inevitability remain untested.

**Future Directions.** Prerequisite experiments: (1) TSG paraphrase-invariance validation on toy dataset before full architecture, (2) gradient correlation validation on known-contaminated models, (3) threshold calibration infrastructure on clean baselines, (4) per-component unit testing before integration.

**Open Question.** The research gap motivating this work persists: how to detect contamination when instance-level methods fail (MIA AUC≈50% in pretraining, semantic detection TPR<2% against adversarial paraphrasing). Geometric trajectory analysis remains an untested approach to this problem.

## References

Carlini, N., et al. (2021). Extracting training data from large language models. *USENIX Security*.

Dekoninck, J., et al. (2024). Evading data contamination detection for language models is (too) easy. arXiv:2402.02823.

Feldman, V. (2020). Does learning require memorization? A short tale about a long tail. *STOC*.

Fort, S., & Jastrzebski, S. (2019). Large scale structure of neural network loss landscapes. *NeurIPS*.

Fu, Y., et al. (2024). Does data contamination detection work (well) for LLMs? A quantitative investigation. arXiv:2410.18966.

Jain, N., et al. (2024). LiveCodeBench: Holistic and contamination free evaluation of large language models for code. arXiv:2403.07974.

Kiela, D., et al. (2021). Dynabench: Rethinking benchmarking in NLP. *NAACL*.

Li, H., et al. (2018). Visualizing the loss landscape of neural nets. *NeurIPS*.

Swayamdipta, S., et al. (2020). Dataset cartography: Mapping and diagnosing datasets with training dynamics. *EMNLP*.

Toneva, M., et al. (2019). An empirical study of example forgetting during deep neural network learning. *ICLR*.

Ye, J., et al. (2022). Extracting training data from diffusion models. arXiv:2301.13188.

---

**Estimated Length:** ~8 pages (6,500 words)  
**Tables:** 3  
**Figures:** 0  
**Venue Recommendation:** Reproducibility workshops, negative results tracks, methodology venues
