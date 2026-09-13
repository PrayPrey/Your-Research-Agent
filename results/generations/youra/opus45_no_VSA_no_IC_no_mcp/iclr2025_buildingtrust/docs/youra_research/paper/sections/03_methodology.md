# Methodology

Building on the observation that truthfulness and robustness may share underlying mechanisms, we design a cross-benchmark correlation study with explicit mechanism testing. Our approach addresses three questions: (1) Does a significant correlation exist after controlling for model size? (2) Does calibration correlate with either metric? (3) Does calibration moderate the correlation strength?

## Overview

We evaluate decoder-only LLMs on three benchmarks: TruthfulQA MC1 (truthfulness), AdvGLUE (robustness), and MMLU (calibration reference). We compute partial correlations controlling for model size (log-transformed parameter count) and test whether Expected Calibration Error (ECE) explains the relationship.

## Benchmark Selection

**TruthfulQA MC1** [Lin et al., 2022]: Multiple-choice format measuring whether models select truthful answers over common misconceptions. We use MC1 (single correct answer) for cleaner accuracy measurement.

*Rationale:* TruthfulQA specifically measures factual accuracy under adversarial questioning designed to elicit falsehoods, making it complementary to AdvGLUE's perturbation-based robustness.

**AdvGLUE** [Wang et al., 2022]: Adversarial variants of GLUE tasks with word-level perturbations. We report average accuracy across subtasks.

*Rationale:* AdvGLUE tests robustness to input perturbations that preserve semantics but fool models, representing a different trust dimension from truthfulness.

**MMLU** [Hendrycks et al., 2021]: Multi-task academic benchmark. Used only for ECE computation on a neutral task.

*Rationale:* Computing ECE on TruthfulQA or AdvGLUE would conflate calibration measurement with the metrics being correlated. MMLU provides a neutral reference.

## Model Selection

We evaluate models from four families to avoid family-specific artifacts:

| Family | Models | Size Range |
|--------|--------|------------|
| Pythia | 70M, 160M, 410M, 1B, 1.4B, 2.8B, 6.9B, 12B | 70M–12B |
| Llama-2 | 7B, 13B, 70B (base) | 7B–70B |
| Mistral | 7B | 7B |
| Falcon | 7B, 40B | 7B–40B |

*Rationale:* Multiple families across a range of scales (70M–70B) ensure correlations are not artifacts of specific architectures or training procedures.

## Statistical Methods

### Partial Correlation

We compute Pearson partial correlation between TruthfulQA MC1 and AdvGLUE accuracy, controlling for log(parameters):

$$r_{xy \cdot z} = \frac{r_{xy} - r_{xz} \cdot r_{yz}}{\sqrt{(1 - r_{xz}^2)(1 - r_{yz}^2)}}$$

*Rationale:* Larger models tend to perform better on both metrics. Without controlling for size, we might observe a spurious correlation driven by scale alone.

### Bootstrap Confidence Intervals

We compute 95% confidence intervals via 1000 bootstrap iterations, resampling models with replacement and recomputing partial correlation.

*Rationale:* With N=14 models, asymptotic confidence intervals may be unreliable. Bootstrap provides nonparametric uncertainty quantification.

### Expected Calibration Error (ECE)

For each model, we compute 15-bin ECE on MMLU:

$$\text{ECE} = \sum_{b=1}^{B} \frac{|B_b|}{N} |acc(B_b) - conf(B_b)|$$

where bins are formed by predicted probability and we measure the gap between accuracy and confidence.

*Rationale:* ECE is the standard calibration metric. 15 bins balance granularity with stability given sample sizes.

### Mechanism Testing

**H-M1 (Calibration-Metric Correlation):** If calibration underlies both capabilities, ECE should negatively correlate with TruthfulQA and AdvGLUE (lower ECE = better calibration = higher performance).

**H-M2 (Calibration Moderation):** If calibration mediates the truthfulness-robustness relationship, well-calibrated (low-ECE) models should show stronger correlation than poorly-calibrated models. We test via Fisher's z-test comparing correlation coefficients across ECE tertiles.

## Hypothesis Structure

Our analysis follows a hierarchical verification plan:

| ID | Type | Test | Gate |
|----|------|------|------|
| h-e1 | Existence | Partial r > 0.3, p < 0.05 | MUST_WORK |
| h-m1 | Mechanism | ECE-metric r < -0.2 | SHOULD_WORK |
| h-m2 | Mechanism | Low-ECE r > High-ECE r | SHOULD_WORK |
| h-c1 | Condition | Pattern holds for base and IT separately | SHOULD_WORK |

*Rationale:* The MUST_WORK gate (h-e1) determines whether the core correlation exists. SHOULD_WORK gates test the calibration mechanism; failure redirects to alternative explanations rather than rejecting the main finding.

## Evaluation Protocol

All evaluations use lm-evaluation-harness [Gao et al., 2023] with consistent settings:
- Batch size: auto (determined by model size)
- Prompt format: default harness templates
- Sampling: greedy decoding for reproducibility

We prioritize reproducibility and fair comparison over optimizing individual model performance.
