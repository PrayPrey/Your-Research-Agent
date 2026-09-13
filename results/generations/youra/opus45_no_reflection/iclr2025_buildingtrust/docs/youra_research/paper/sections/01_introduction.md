# Introduction

Three research communities have independently developed metrics for evaluating large language model (LLM) reliability: factuality evaluation measures whether models generate truthful content, adversarial robustness quantifies resistance to input perturbations, and calibration assesses confidence-accuracy alignment. Despite measuring seemingly related properties—a model's ability to "know what it knows"—no unified framework connects these evaluation paradigms. We hypothesize that calibration quality serves as a shared internal signal enabling both factuality error detection and adversarial robustness.

## The Problem

LLMs fail in two primary modes relevant to deployment safety. First, they generate confident but incorrect information—so-called hallucinations—that users may trust due to fluent presentation. Second, they succumb to adversarial perturbations, producing different outputs for semantically equivalent inputs. Both failure modes undermine user trust and limit safe deployment in high-stakes domains.

These failures share a common characteristic: overconfident predictions on inputs where the model should express uncertainty. A model that generates hallucinations does so confidently rather than hedging. A model vulnerable to adversarial attacks fails to recognize that perturbed inputs lie outside its training distribution. This suggests that both failures stem from poor calibration—the model's confidence does not reflect its actual accuracy.

The calibration hypothesis proposes that well-calibrated models, whose confidence scores align with their accuracy, can better detect both their own errors (enabling factuality) and unusual inputs (enabling robustness). If true, calibration quality (measured by Expected Calibration Error, ECE) should mediate the correlation between factuality metrics (TruthfulQA MC1) and robustness metrics (1 - Attack Success Rate).

## Gap in Existing Work

Prior work has studied each dimension in isolation. TruthfulQA \cite{lin2022truthfulqa} established benchmarks for factuality; TextFooler \cite{jin2019textfooler} developed standard attacks for robustness; Minderer et al. \cite{minderer2021revisiting} analyzed calibration across architectures. However, no empirical study has quantified whether models that excel at factuality also resist adversarial attacks, or whether calibration explains this relationship.

## Contributions

We propose a methodology to test the calibration-mediation hypothesis:

1. **Correlation Analysis**: Evaluate 12+ open-weight LLMs on TruthfulQA MC1 (factuality) and TextFooler (robustness), computing Pearson correlation with bootstrap confidence intervals.

2. **Confound Control**: Partial correlation controlling for model scale (log parameters), within-family analysis to control for training data effects.

3. **Mediation Testing**: Baron-Kenny mediation analysis with ECE as the proposed mediator, testing whether calibration accounts for the factuality-robustness relationship.

4. **Intervention Validation**: Temperature scaling experiments to test whether improving calibration improves both factuality and robustness.

This paper presents our validated methodology. Preliminary results (3 of 12 models evaluated) demonstrate pipeline functionality but are insufficient for hypothesis testing. We document the experimental design, analysis pipeline, and path to completion.
