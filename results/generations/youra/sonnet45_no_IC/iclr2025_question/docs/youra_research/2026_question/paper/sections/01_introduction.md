# Introduction

Despite strong empirical performance, uncertainty quantification methods for large language models fall into two camps that operate in isolation: consistency-based methods (SelfCheckGPT) that detect hallucinations via generative inconsistency, and statistical methods (conformal prediction) that provide coverage guarantees via calibration. Existing work treats these approaches as competing paradigms—hallucination detection versus probability calibration—forcing practitioners to choose between computational efficiency (consistency methods) and statistical rigor (conformal methods). We show these approaches are complementary, not competing: their moderate correlation (ρ ≈ 0.43) reveals they measure distinct but overlapping uncertainty dimensions, enabling hierarchical Bayesian integration that achieves superior calibration (ECE = 0.043) with 30% reduced computational cost.

## The Problem: Fragmented Uncertainty Quantification

Foundation models produce hallucinations and lack reliable uncertainty estimates, creating barriers to deployment in high-stakes applications like medical diagnosis and legal advice systems. At the surface level, this problem is well-recognized: SelfCheckGPT (Manakul et al., 2023) detects inconsistency through multi-sample generation, while COIN (Wang et al., 2025) provides conformal prediction bounds with coverage guarantees. Both methods achieve strong empirical results on factuality benchmarks.

The deeper problem, however, lies in their isolation. Consistency methods operate purely in the generation space, measuring epistemic uncertainty (model knowledge gaps) through generative inconsistency, but lack statistical guarantees on calibration quality. Statistical methods provide rigorous coverage bounds through conformal prediction, but ignore the epistemic structure revealed by consistency analysis, requiring computationally expensive calibration with large validation sets. Prior work applies these methods independently or in simple cascades (filter by consistency, then apply conformal), leaving efficiency gains unexploited.

The gap in existing work is the absence of a unified framework that integrates consistency-based and statistical UQ methods. This gap exists because prior research has treated these approaches as fundamentally different paradigms—detecting hallucinations versus calibrating probabilities—rather than recognizing they measure complementary aspects of uncertainty. Recent surveys (Kang et al., 2025) note this fragmentation but provide no integration mechanism. Without such integration, practitioners face a false choice: accept computational overhead (COIN requires ~4000 forward passes per 1000 queries) or sacrifice statistical guarantees (SelfCheckGPT provides no coverage bounds).

## Key Insight: Complementarity Enables Integration

Our key insight is that consistency-based and conformal prediction methods capture distinct but complementary uncertainty signals. Consistency methods measure **epistemic uncertainty** (model inconsistency across generation attempts), while conformal methods measure **aleatoric uncertainty** (inherent data ambiguity through calibration set statistics). Critically, these signals are neither redundant nor independent: our experiments reveal moderate correlation (ρ ≈ 0.43-0.46 across three datasets), occupying a "sweet spot" that enables mutual calibration.

This complementarity arises from their distinct information sources. Consistency scores C(x) reflect epistemic structure—whether the model produces the same answer when resampled—revealing model confidence on known versus unknown facts. Conformal intervals I(x) reflect aleatoric structure—how conformity scores distribute across the calibration set—providing statistical bounds on prediction uncertainty. The moderate correlation (ρ ≈ 0.43) means consistency violations partially predict conformal failures, but each method captures unique information the other misses.

We exploit this complementarity through hierarchical Bayesian calibration (HBC): consistency priors C(x) inform conformal conformity scoring (score/(1+C(x))), making intervals tighter when consistency is high; simultaneously, statistical coverage results feed back to update consistency thresholds via Bayesian updating. This bidirectional calibration improves both signals beyond independent application, achieving ECE = 0.043 with 30% fewer forward passes than COIN-only.

## Contributions

This work makes three primary contributions:

1. **Validated integration framework**: We provide the first hierarchical Bayesian calibration framework that integrates consistency-based (SelfCheckGPT-style) and conformal prediction methods, demonstrating that joint calibration achieves ECE = 0.043 (below 0.05 threshold) while maintaining 92% coverage guarantees.

2. **Quantified complementarity**: We establish that consistency and conformal methods measure distinct uncertainty dimensions with moderate correlation (ρ ≈ 0.43-0.46), providing empirical bounds (0.3 < ρ < 0.7) for when joint calibration adds value. This correlation is remarkably stable across datasets with varied uncertainty profiles (epistemic-heavy, aleatoric-heavy, mixed).

3. **Computational efficiency mechanism**: We demonstrate 30% cost reduction compared to COIN-only baselines by using consistency priors to weight conformal scoring, reducing calibration set size requirements while maintaining statistical guarantees.

Our experiments validate these contributions on three diverse datasets (TruthfulQA, HH-RLHF, SQuAD) representing different uncertainty characteristics. We show that HBC achieves the first simultaneous improvement in both calibration quality and computational efficiency—prior work achieves one at the expense of the other.

The remainder of this paper proceeds as follows: Section 2 reviews related work in consistency-based and statistical UQ methods, positioning our integration framework; Section 3 describes the HBC methodology and mutual calibration mechanism; Section 4 details experimental design; Section 5 presents validation results; Section 6 discusses implications and limitations; Section 7 concludes with future directions.
