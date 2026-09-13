# Introduction

Language models that achieve state-of-the-art accuracy on benchmarks can simultaneously produce confidence scores that are fundamentally unreliable for distinguishing correct from incorrect predictions. This reliability gap emerges not because models are poorly calibrated in the traditional sense, but because Reinforcement Learning from Human Feedback (RLHF) corrupts the discriminative relationship between confidence and correctness through a mechanism we characterize as *geometric distortion*.

Reliable confidence signals are essential for safe deployment of AI systems. Selective prediction systems must identify when to abstain; human-AI collaboration requires knowing when to trust model outputs; uncertainty-aware decision making depends on confidence scores that actually reflect probability of correctness. Prior work has documented that RLHF-tuned models exhibit systematic overconfidence compared to their base model counterparts [Tian et al., 2023], and the standard remedy is post-hoc temperature scaling [Guo et al., 2017], which can reduce Expected Calibration Error (ECE) by 15-55% [Khanmohammadi et al., 2025]. However, this approach assumes that RLHF-induced miscalibration is a scalar shift—analogous to a miscalibrated thermometer that reads consistently high—that can be corrected by rescaling.

We challenge this assumption. Our central observation is that RLHF does not merely shift the scale of confidence scores; it fundamentally reshapes the probability landscape in ways that degrade the model's ability to discriminate correct from incorrect predictions. This distinction matters critically: temperature scaling can repair scalar shifts but cannot undo geometric distortions. A medical diagnosis system using an RLHF-tuned model might express high confidence in incorrect diagnoses at rates 3-17 times higher than its base model counterpart, and no amount of post-hoc rescaling can restore the lost discriminative signal.

## The Deeper Problem

The calibration literature has primarily focused on Expected Calibration Error (ECE) as the diagnostic metric for miscalibration [Guo et al., 2017; Naeini et al., 2015]. ECE measures whether predicted probabilities match observed frequencies across confidence bins—a model is well-calibrated if 80% of predictions at 80% confidence are correct. However, ECE can be improved by temperature scaling even when the model's ability to rank predictions by correctness probability degrades. This creates a dangerous scenario: practitioners may observe improved calibration metrics while deploying systems with fundamentally broken confidence signals.

The deeper problem is that RLHF's preference optimization mechanism—which underlies instruction-tuned models from major providers—rewards decisive responses regardless of correctness. The Bradley-Terry model used in RLHF training penalizes hedging and rewards confident-sounding outputs [Ouyang et al., 2022]. This creates selection pressure that inflates logit margins uniformly, including for incorrect predictions. When margins inflate disproportionately for errors, high confidence no longer reliably indicates high probability of being right.

## Our Insight and Approach

Our key insight is that RLHF-induced confidence distortion can be characterized as *geometric* rather than *scalar*. Scalar distortion (like temperature miscalibration) changes the magnitude of confidence scores but preserves their relative ordering—the most confident predictions remain most likely to be correct. Geometric distortion changes the shape of the confidence-correctness relationship itself, degrading discriminative ability in ways that persist even after scale normalization.

To test this hypothesis, we measure discriminative quality using AUROC (Area Under the Receiver Operating Characteristic curve) for margin-based correctness prediction. Unlike ECE, AUROC directly measures how well confidence scores distinguish correct from incorrect predictions. We further introduce percentile-normalized logistic regression to separate scale effects from shape effects: if the slope of the confidence-correctness relationship (β_percentile) attenuates after percentile normalization, the distortion is geometric, not scalar.

Building on this insight, we make the following contributions:

1. **Novel discriminative degradation metric.** We demonstrate that AUROC for margin-based correctness prediction drops 2-4 percentage points in instruction-tuned models compared to their base counterparts across the Qwen and Mistral families—a statistically significant effect with practical implications for deployment.

2. **Mechanism identification.** We identify the mechanism underlying this degradation: RLHF inflates expected margins for incorrect predictions by 3-17x across model families (Cohen's d = 1.01-1.85), explaining why confidence scores become less informative about correctness.

3. **Geometric distortion characterization.** Using percentile-normalized monotonicity analysis and Murphy's Brier score decomposition, we demonstrate that the distortion is geometric rather than scalar—the refinement component (discrimination) degrades by 2-5 percentage points, confirming that RLHF reshapes the probability landscape rather than merely rescaling it.

4. **Cross-family validation.** We validate these findings across two major model families (Qwen2.5-7B and Mistral-7B), showing consistent effects that suggest RLHF training procedures—not vendor-specific implementation details—are the root cause.

These findings have direct implications for practitioners: temperature scaling alone cannot repair RLHF-induced discriminative degradation. For applications where confidence-based decision making matters—selective prediction, uncertainty quantification, human-AI collaboration—new approaches that preserve discrimination during RLHF training are needed.

The remainder of this paper is organized as follows. Section 2 reviews related work on LLM calibration and RLHF training dynamics. Section 3 describes our methodology for measuring and characterizing discriminative degradation. Section 4 presents our experimental setup. Section 5 reports results across four complementary experiments. Section 6 discusses implications and limitations, and Section 7 concludes with future directions.
