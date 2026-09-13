# Introduction

Tools for assessing machine learning reproducibility—statistical evaluators, LLM-based pipeline screeners, end-to-end verifiers—share a fundamental limitation: they operate after experiments have already run. A researcher selecting a benchmark dataset receives no signal about whether their chosen dataset will yield reproducible results until they have invested substantial computational resources and development time. This reactive paradigm persists despite widespread recognition that reproducibility failures trace to upstream causes, particularly ambiguous dataset specifications that permit divergent preprocessing implementations.

We demonstrate that dataset metadata completeness predicts reproducibility variance *before* any experiment executes. Analyzing OpenML benchmark datasets with matched experimental configurations (identical flows and hyperparameters), we find that top-quartile metadata completeness predicts a 42.1% reduction in interquartile range (IQR) of performance outcomes compared to bottom-quartile datasets (95% CI: 39.1–51.7%). The effect substantially exceeds our pre-registered 20% threshold, suggesting metadata quality matters more than previously understood.

## The Problem of Post-Hoc Assessment

The machine learning reproducibility crisis is well-documented. Kapoor and Narayanan (2022) identified eight types of data leakage affecting 329 papers across 17 scientific fields, establishing the scope and severity of the problem. The research community responded with valuable assessment infrastructure: rliable (Agarwal et al., 2021) provides statistical tools for reliable benchmark evaluation; Reproscreener (Bhaskar & Stodden, 2024) uses language models to assess pipeline reproducibility; paper-replay enables end-to-end verification with cryptographic attestation. These tools share a common characteristic: they verify reproducibility *post-hoc*, after experiments complete.

Yet reproducibility variance originates upstream—in the ambiguities that dataset documentation leaves unresolved. When metadata omits preprocessing specifications, missing value handling, or train/test split definitions, researchers facing these ambiguous datasets make divergent implementation choices. This implementation heterogeneity propagates through the experimental pipeline, manifesting as variance in reported results.

## Dataset Metadata as an Upstream Predictor

We propose a conceptual reframing: reproducibility is not merely a binary property of individual papers but a continuous property of datasets, predictable from metadata characteristics before any experiment runs. The mechanism is epistemic entropy reduction—complete documentation constrains the degrees of freedom available to implementing researchers, reducing the space of valid preprocessing pipelines and thereby reducing outcome variance.

Our mediation analysis confirms this mechanism: preprocessing entropy mediates 64.7% of the metadata-to-variance effect (Sobel Z = 16.02, p < 0.0001). Datasets with rich metadata exhibit lower Shannon entropy in preprocessing component distributions (imputation methods, scaling approaches, encoding strategies). This lower entropy directly corresponds to reduced performance variance across matched runs.

## Contributions

Building on this insight, we make three contributions:

First, we establish that metadata completeness predicts reproducibility variance with substantial effect size. Our 5-field metadata checklist—train/test split specification, preprocessing enumeration, missing value handling documentation, feature semantics provision, and versioning presence—explains significant variance in IQR even after controlling for intrinsic dataset stability, popularity, algorithm family, and infrastructure factors.

Second, we identify preprocessing entropy as the dominant causal pathway. The 64.7% mediation proportion exceeds our 30% threshold, demonstrating that documentation completeness operates primarily by constraining preprocessing choices rather than through alternative mechanisms such as researcher self-selection.

Third, we demonstrate robustness across multiple checks. The effect persists in early-run subsamples (90.7% preservation, ruling out reverse causality from community convergence), within single algorithm families (p < 0.001 for RandomForest-only analysis, ruling out algorithm-mix confounds), and against permutation controls (observed effect exceeds 95th percentile of null distribution).

We organize the paper as follows: Section 2 reviews related work in reproducibility assessment and positions our predictive approach against existing post-hoc tools. Section 3 presents our methodology including the metadata scoring scheme, variance operationalization, and mediation framework. Sections 4–5 detail our experimental setup and results. Section 6 discusses implications and limitations, and Section 7 concludes with directions for proactive reproducibility guidance.
