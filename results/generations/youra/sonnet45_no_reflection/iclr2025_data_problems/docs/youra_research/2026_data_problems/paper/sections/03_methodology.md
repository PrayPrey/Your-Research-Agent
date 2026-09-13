# Methodology

This section describes the three-tier contamination detection architecture we **intended to implement** but did not. The methodology is documented for completeness and to contextualize the failure analysis in Section 5. Readers should note that none of the detection mechanisms described here were actually executed in our experiment.

## Overview

Building on the observation that instance-level detection methods (MIA, semantic similarity) have fundamental limitations—MIA achieves AUC≈50% in pretraining (Fu et al., 2024) and semantic detection achieves TPR<2% against adversarial paraphrasing (Dekoninck et al., 2024)—we designed a detection architecture operating on learning trajectory signatures rather than individual sample properties. The intuition was that contamination-induced performance gains require models to align parameter updates with benchmark-specific task structures, producing detectable signatures across multiple analytical layers even when instance-level features are obscured by paraphrasing.

The architecture consisted of three tiers designed to provide complementary detection signals:

1. **Tier 1 (Data-Layer Filters):** Catch accidental contamination through exact or near-duplicate detection
2. **Tier 2 (Task Signature Graph Probes):** Detect systematic learning acceleration on benchmark-aligned task structures
3. **Tier 3 (Geometric Trajectory Auditing):** Identify parameter-space alignment patterns toward benchmark-specific manifolds

Detection logic: A training run is flagged if **any tier** exceeds its detection threshold (logical OR). The hypothesis was that contamination necessarily triggers at least one tier, achieving ≥80% combined detection power at <5% false positive rate.

**Implementation Status:** All three tiers returned hard-coded `True` values. No detection metrics were computed. The following subsections describe intended functionality, not actual behavior.

## Tier 1: Data-Layer Filters

**Intended Functionality (Not Implemented):**

Tier 1 was designed to catch accidental contamination (web-scraped exact or near-duplicates) through two mechanisms:

**Temporal Isolation Check:** Flag training samples with publication dates after benchmark release. For GSM8K (released November 2021), any training sample dated post-2021-11-01 should be excluded as potential contamination.

**LSH Fingerprinting:** Compute MinHash signatures (128 permutations, 20 bands, 5 rows per band) for all training samples and benchmark test samples. Samples with Jaccard similarity >0.8 are flagged as near-duplicates. This catches copy-paste contamination but is evaded by paraphrasing (Dekoninck et al., 2024).

**Rationale:** Tier 1 provides a first line of defense against unsophisticated contamination (web scraping artifacts, dataset leakage) while acknowledging that adversarial contamination (EAL-style paraphrasing) will evade this layer. The expected performance was ≥95% detection on accidental contamination, <10% on adversarial contamination.

**Actual Implementation:** Returned constant `True` value. No LSH computation performed. No temporal checks executed.

## Tier 2: Task Signature Graph Probes

**Intended Functionality (Not Implemented):**

Tier 2 was the novel contribution: Task Signature Graphs (TSG) as paraphrase-invariant representations of task structure. The approach:

**TSG Extraction:** For arithmetic reasoning problems (GSM8K), extract constraint graphs via equation parsing or program synthesis. Example: "If Alice has 3 apples and gets 5 more, how many does she have?" → TSG: `{ADD(X:3, Y:5) → Z:8}`. Paraphrasing changes surface text but preserves this constraint structure.

**Probe Generation (3000 probes total):**
- **Invariant Probes (1000):** Samples structurally similar to benchmark (same constraint patterns)
- **Neighbor Probes (1000):** Samples from related distribution but different constraints
- **Broken Control Probes (1000):** Structurally invalid problems (negative control)

**Differential Alignment Metric:** During finetuning, track probe loss trajectories. Compute:
```
Δ = (ΔL_invariant - ΔL_neighbor)
```
where `ΔL_invariant` is the loss reduction on invariant probes and `ΔL_neighbor` is the loss reduction on neighbor probes. If contamination is present, the model should learn invariant probes faster (larger ΔL_invariant), while general math skill transfer would affect both equally. Detection threshold: Δ > 2σ above clean baseline.

**Rationale:** Paraphrasing changes tokens but preserves task structure. If contamination accelerates learning on benchmark-aligned structures (invariant probes) more than on general math (neighbor probes), differential alignment reveals contamination even when individual samples are paraphrased beyond semantic detection thresholds.

**Key Assumption (Unverified):** TSG extraction preserves task structure under GPT-4-level paraphrasing with ≥80% fidelity. This assumption was never tested. If TSGs are not paraphrase-invariant, Tier 2 collapses to instance-level similarity (which EAL evades).

**Actual Implementation:** Returned constant `True` value. No TSG extraction performed. No probe generation implemented. No differential alignment computed.

## Tier 3: Geometric Trajectory Auditing

**Intended Functionality (Not Implemented):**

Tier 3 was designed to detect parameter-space alignment patterns under the hypothesis that achieving task-specific gains from limited contamination (≤5% injection) requires steering parameter updates toward benchmark-aligned manifolds, leaving geometric signatures.

**Four Geometric Metrics:**

1. **Gradient Subspace Alignment:** Cosine similarity between finetuning gradients and benchmark test set gradients. Threshold: +0.10 above clean baseline. Hypothesis: Contamination-induced gains correlate with parameter updates aligned to benchmark gradients.

2. **Hessian Anisotropy:** Ratio of top-10 to bottom-10 Hessian eigenvalues, measuring curvature concentration. Threshold: 1.5× clean baseline. Hypothesis: Benchmark-specific optimization creates sharp curvature along task-aligned directions.

3. **CKA Representational Alignment:** Centered Kernel Alignment between internal representations and benchmark task embeddings. Threshold: ΔCKA ≥ 0.15 vs. clean. Hypothesis: Contamination compresses representations toward benchmark-specific manifolds.

4. **Information Efficiency Z-Score:** Benchmark gain per training bit, normalized by null distribution. Threshold: z ≥ 2.5. Hypothesis: Contamination achieves abnormally high gain-per-bit compared to general learning.

**Detection Logic:** Flag if ≥2 of 4 metrics exceed thresholds. Rationale: Individual metrics may have noise, but multiple concurrent signals indicate systematic alignment.

**Geometric Inevitability Hypothesis:** The theoretical claim was that suppressing geometric detection signals (e.g., via adversarial training with penalty term λ·GeometrySignal) forces a Pareto tradeoff: reducing detection probability requires sacrificing benchmark gains. Specifically, 50% signal reduction should cost ≥30% gain loss, preventing "flat regions" (high gain + low signal).

**Rationale:** If contamination-induced gains arise from task-specific parameter alignment (not general capability transfer), then achieving ≥10% benchmark improvement from ≤5% injection should produce detectable geometric signatures. Adaptive adversaries attempting evasion face a Pareto constraint limiting simultaneous gain maximization and signal suppression.

**Key Assumption (Unverified):** Achieving ≥10% benchmark gains from ≤5% contamination injection requires parameter updates correlated with benchmark gradients (gradient alignment assumption). If gains can occur through mechanisms that do not produce geometric signatures, the entire Tier 3 detection approach fails. This assumption was never tested.

**Actual Implementation:** Returned constant `True` value. No gradient computation performed. No Hessian computation performed. No CKA computation performed. No efficiency computation performed.

## Combined Detection Architecture

**Intended Logic (Not Implemented):**

The three tiers operate independently and report detections via logical OR:
```python
detection = (tier1_detect() OR tier2_detect() OR tier3_detect())
```

**Threshold Calibration (Never Performed):** Detection thresholds (2σ for differential alignment, +0.10 for gradient overlap, etc.) were specified theoretically in Phase 2A hypothesis generation. Proper calibration requires training N=20 clean baseline runs and setting thresholds at the 95th percentile of clean distribution to achieve target <5% false positive rate. This calibration was never executed.

**Actual Behavior:** Since all three `tier*_detect()` functions returned `True`, the combined detector always returned `True`, producing 100% detection power (correctly flagged all contaminated runs) and 100% false positive rate (incorrectly flagged all clean runs). This is the signature of a constant function classifier with no discrimination capability.

## Implementation Gap Analysis

Phase 3 implementation planning generated 15 tasks spanning data pipeline (tasks 001-002), training infrastructure (task 004), three detection tiers (tasks 005-014), and evaluation (task 009). Root cause analysis revealed:

- **Tasks Completed:** 2/15 (tasks 001-002: data loading, dependency installation)
- **Tasks Partially Completed:** 2/15 (task 004: training loop executed but with model substitution; task 009: evaluation metrics computed on invalid detector outputs)
- **Tasks Not Implemented:** 10/15 (67% of implementation plan)

The critical gap: **all detection tier tasks (005-007) and their subtasks (010-014) were not implemented**. Phase 4 coding focused on passing external mock data validation (which verified real datasets were loaded) but skipped the actual detection algorithm implementations. The resulting code satisfied data loading requirements while completely bypassing detection logic.

**Why Methodology Matters Despite Failure:** This section documents what should have been built to contextualize the implementation gap. The failure was not in design (the three-tier architecture concept is sound) but in execution (10 of 15 tasks were never implemented). Understanding the intended functionality clarifies what was missing and what future work must implement to actually test the hypothesis.
