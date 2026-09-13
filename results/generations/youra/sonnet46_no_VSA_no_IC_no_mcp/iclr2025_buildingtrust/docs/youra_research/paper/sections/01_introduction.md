# Introduction

When we evaluated an open-weight language model on the ANLI R1 benchmark — a dataset specifically constructed so that human annotators could fool state-of-the-art NLP models — we found that the model's Expected Calibration Error *decreased* relative to its performance on clean MultiNLI. The adversarial benchmark, designed to expose model failures, made the model appear *better calibrated*. This result was not an error. It reveals a fundamental property of how adversarial construction methods interact with model confidence: in a model-in-the-loop adversarial benchmark, the examples are selected precisely because the model fails on them — and a model that fails with appropriately low confidence is, by definition, well-calibrated.

This observation motivates the central question of our work: **does adversarial perturbation of NLP benchmarks actually degrade LLM calibration, and if so, under what conditions?**

## The Problem

Calibration — the alignment between predicted confidence and observed accuracy — is a critical reliability property for deployed language models. A model that assigns 90% confidence to its predictions should be correct 90% of the time; deviations from this correspondence make model confidence unreliable as a safety signal. The field has developed robust measurement tools, most notably Expected Calibration Error (ECE) [Guo et al., 2017], and has documented that modern neural networks systematically overconfident under distribution shift [Minderer et al., 2021].

At the same time, adversarial NLP benchmarks — AdvGLUE [Wang et al., 2021] and ANLI [Nie et al., 2020] — have become standard for evaluating LLM robustness under distribution shift, typically reporting accuracy degradation. But accuracy degradation alone does not characterize the reliability of model confidence under adversarial conditions. A model that becomes *less* accurate but *proportionally less confident* may be better calibrated than one that maintains confidence while failing more often.

The deeper problem is that adversarial benchmarks are not a single category. AdvGLUE uses *human adversaries* who craft perturbations to fool existing models; ANLI uses a *model-in-the-loop* construction where examples are selected by human annotators specifically when they cause model errors. These construction methods produce qualitatively different distributions of model behavior — and consequently, different calibration effects. Yet prior calibration studies treat adversarial perturbation as a monolithic distribution shift, analogous to the vision-domain corruptions studied by Minderer et al. [2021]. Whether this analogy holds in NLP, and whether RLHF alignment moderates the effect, has not been tested.

**The gap:** No published work measures logit-based ECE on adversarial NLP benchmark splits (AdvGLUE, ANLI) for open-weight LLMs, or examines how adversarial construction method and RLHF alignment jointly determine calibration outcomes under adversarial conditions.

## Key Insight

Our central finding is that adversarial calibration degradation in LLMs is **task-type and construction-method conditional**, not universal. Human-adversarial NLI examples (AdvGLUE MNLI) produce reliable calibration degradation: ΔECE = +0.071, a 7.1 percentage-point increase in Expected Calibration Error relative to clean MultiNLI. Model-in-the-loop adversarial NLI examples (ANLI R1/R2) produce calibration *improvement*: ΔECE = −0.041 for R1. Binary classification tasks (QQP, SST-2) show reversed ΔECE regardless of adversarial method. And RLHF alignment conditionally moderates these effects — helping for model-in-loop adversarial (100% moderation rate across ANLI rounds) but exacerbating calibration degradation for static human-adversarial benchmarks (ΔΔECE = −0.026, chat worse than base on AdvGLUE).

The resolution to the opening paradox follows directly: in model-in-the-loop adversarial benchmarks, examples are selected to cause errors; a model that fails with appropriately moderate confidence on such examples is demonstrating calibration, not miscalibration. Human-adversarial examples, by contrast, exploit surface features to trigger high confidence on wrong answers — the classic miscalibration mechanism.

## Contributions

Our investigation of adversarial LLM calibration yields four contributions that build from existence to mechanism to conditionality:

**(1) First measurement of logit-based ECE on adversarial NLP benchmarks.** We measure ECE directly on AdvGLUE and ANLI benchmark splits for Llama-2-7b-hf, establishing ΔECE as a measurable, meaningful quantity for adversarial calibration stress testing. This fills the gap between adversarial robustness evaluation (accuracy-only) and calibration measurement (clean-data-only).

**(2) Evidence that calibration degradation is task-type and construction-method conditional.** Human-adversarial NLI examples (AdvGLUE MNLI) produce calibration degradation (ΔECE = +0.071); model-in-the-loop adversarial examples (ANLI R1/R2) produce calibration improvement; and the ANLI difficulty gradient (R1 → R2 → R3) shows a smooth transition from improvement to degradation as adversarial difficulty increases. Binary classification tasks consistently show reversed ΔECE. This nuances the vision-domain finding that distribution shift uniformly degrades calibration.

**(3) Evidence that RLHF alignment conditionally moderates adversarial calibration degradation.** We compare Llama-2-7b-hf (base) and Llama-2-7b-chat across ANLI and AdvGLUE conditions. RLHF moderation is confirmed for model-in-loop adversarial (100% of ANLI rounds show ΔΔECE > 0.01 favoring chat), but reversed for static human-adversarial benchmarks (AdvGLUE: chat shows larger ΔECE than base by 2.6 percentage points). This is the first documented benchmark-type × RLHF calibration interaction.

**(4) Methodological contribution: JSONL cache reuse for efficient post-hoc calibration analysis.** Our JSONL logit caching strategy (introduced in H-E1) enables multiple downstream calibration analyses (label preservation, confidence-accuracy decoupling, per-cell ΔECE, RLHF comparison) from a single inference pass — making multi-cell adversarial calibration analysis computationally feasible without repeated model inference.

Together, these contributions establish adversarial calibration measurement as a distinct research problem from adversarial accuracy robustness, and provide a conditional framework (construction method × task type × RLHF alignment) for predicting when and how adversarial perturbation will degrade LLM reliability signals.

We organize the paper as follows. Section 2 discusses calibration measurement, adversarial NLP benchmarks, and RLHF calibration — three bodies of work whose intersection we occupy. Section 3 describes our measurement methodology. Section 4 presents our experimental design. Section 5 reports results across the four research questions. Section 6 interprets findings and discusses limitations. Section 7 concludes.
