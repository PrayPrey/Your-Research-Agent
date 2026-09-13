# Calibration as a Shared Signal: Testing the Mediation of Factuality-Robustness Correlation in Large Language Models

**Status**: Methodology Paper (Results Incomplete)

---

## Abstract

Large language models exhibit two reliability concerns: generating factual errors and succumbing to adversarial perturbations. We hypothesize that calibration quality—the alignment between model confidence and accuracy—serves as a shared internal signal enabling both factuality error detection and adversarial robustness. To test this, we develop a methodology evaluating 12 open-weight LLMs on TruthfulQA (factuality), TextFooler attacks (robustness), and Expected Calibration Error (calibration), then analyzing whether ECE mediates the correlation between factuality and robustness metrics. We present a validated evaluation pipeline and analysis framework. Preliminary results from three models demonstrate pipeline functionality but are insufficient for hypothesis testing; ASR values were simulated and full evaluation remains incomplete. This paper documents our methodology as a foundation for future work connecting these three reliability dimensions.

---

## 1. Introduction

Three research communities have independently developed metrics for evaluating large language model (LLM) reliability: factuality evaluation measures whether models generate truthful content, adversarial robustness quantifies resistance to input perturbations, and calibration assesses confidence-accuracy alignment. Despite measuring seemingly related properties—a model's ability to "know what it knows"—no unified framework connects these evaluation paradigms. We hypothesize that calibration quality serves as a shared internal signal enabling both factuality error detection and adversarial robustness.

### The Problem

LLMs fail in two primary modes relevant to deployment safety. First, they generate confident but incorrect information—so-called hallucinations—that users may trust due to fluent presentation. Second, they succumb to adversarial perturbations, producing different outputs for semantically equivalent inputs. Both failure modes undermine user trust and limit safe deployment in high-stakes domains.

These failures share a common characteristic: overconfident predictions on inputs where the model should express uncertainty. A model that generates hallucinations does so confidently rather than hedging. A model vulnerable to adversarial attacks fails to recognize that perturbed inputs lie outside its training distribution. This suggests that both failures stem from poor calibration—the model's confidence does not reflect its actual accuracy.

The calibration hypothesis proposes that well-calibrated models, whose confidence scores align with their accuracy, can better detect both their own errors (enabling factuality) and unusual inputs (enabling robustness). If true, calibration quality (measured by Expected Calibration Error, ECE) should mediate the correlation between factuality metrics (TruthfulQA MC1) and robustness metrics (1 - Attack Success Rate).

### Gap in Existing Work

Prior work has studied each dimension in isolation. TruthfulQA [1] established benchmarks for factuality; TextFooler [2] developed standard attacks for robustness; Minderer et al. [3] analyzed calibration across architectures. However, no empirical study has quantified whether models that excel at factuality also resist adversarial attacks, or whether calibration explains this relationship.

### Contributions

We propose a methodology to test the calibration-mediation hypothesis:

1. **Correlation Analysis**: Evaluate 12+ open-weight LLMs on TruthfulQA MC1 (factuality) and TextFooler (robustness), computing Pearson correlation with bootstrap confidence intervals.

2. **Confound Control**: Partial correlation controlling for model scale (log parameters), within-family analysis to control for training data effects.

3. **Mediation Testing**: Baron-Kenny mediation analysis with ECE as the proposed mediator, testing whether calibration accounts for the factuality-robustness relationship.

4. **Intervention Validation**: Temperature scaling experiments to test whether improving calibration improves both factuality and robustness.

This paper presents our validated methodology. Preliminary results (3 of 12 models evaluated) demonstrate pipeline functionality but are insufficient for hypothesis testing. We document the experimental design, analysis pipeline, and path to completion.

---

## 2. Related Work

We review three bodies of work: factuality evaluation, adversarial robustness, and calibration. Each has developed independently; our work proposes connecting them.

### Factuality and Truthfulness Evaluation

TruthfulQA [1] established the standard benchmark for evaluating LLM truthfulness, finding that larger models were not more truthful and sometimes worse. The MC1 (multiple-choice single answer) format provides a clean accuracy metric. Subsequent work expanded factuality evaluation: TruthEval [4] curated challenging statements, while ARES [5] achieved 72.1% Macro-F1 on error detection in reasoning chains.

Intervention methods have emerged to improve truthfulness. Non-Linear Inference Time Intervention (NL-ITI) [6] achieves 16% relative MC1 improvement by probing activation patterns associated with truthfulness. FactSelfCheck [7] enables black-box hallucination detection at the fact level. SPOC [8] demonstrates self-correction mechanisms improving accuracy by 8-20%.

These methods focus on factuality metrics in isolation. None examine whether factual models also resist adversarial attacks, leaving potential shared mechanisms unexplored.

### Adversarial Robustness

TextFooler [2] established word-level adversarial attacks as a standard evaluation. By substituting synonyms to flip model predictions, it measures susceptibility to semantically-preserving perturbations. BERT-Attack and similar methods have extended this paradigm.

Robustness work focuses on attack success rates and defense mechanisms. The connection to other reliability properties—whether robust models are also factual—remains unstudied. Theoretical work suggests well-calibrated models should produce high uncertainty on out-of-distribution inputs, including adversarial examples, but empirical validation across factuality benchmarks is lacking.

### Calibration

Guo et al. [9] demonstrated that modern neural networks are poorly calibrated, motivating Expected Calibration Error (ECE) as a metric and temperature scaling as a simple fix. Minderer et al. [3] showed that architecture significantly affects calibration properties.

Calibration literature focuses on confidence-accuracy alignment without connecting to factuality or robustness benchmarks. If calibration provides reliable uncertainty estimates, these estimates should support both error detection (factuality) and anomaly detection (robustness). Our work tests this hypothesis.

| Research Area | Focus | Gap |
|--------------|-------|-----|
| Factuality | Detection accuracy | No connection to robustness |
| Robustness | Attack success rates | No connection to calibration |
| Calibration | Confidence-accuracy | No joint factuality-robustness analysis |

---

## 3. Methodology

We describe our approach to testing the calibration-mediation hypothesis. The methodology involves three phases: metric collection, correlation analysis, and mediation testing.

### Hypothesis and Predictions

**Core Hypothesis**: Under the scope of open-weight LLMs evaluated on word-level adversarial perturbations, if a model exhibits higher factuality error detection accuracy (TruthfulQA MC1), then it will demonstrate higher adversarial robustness (1 - ASR on TextFooler), because calibration quality (lower ECE) provides a shared internal signal that enables both error detection and robustness.

This yields three testable predictions:

- **P1**: Cross-model correlation r > 0.5 between MC1 and (1-ASR)
- **P2**: ECE mediates ≥30% of the correlation
- **P3**: Temperature scaling improves both metrics

### Model Selection

We evaluate 12 open-weight LLMs spanning four families:

| Family | Models | Size Range |
|--------|--------|------------|
| Llama-2 | 7B, 13B, 70B | 7B-70B |
| Llama-3 | 8B, 70B | 8B-70B |
| Mistral | 7B-v0.1, 7B-Instruct | 7B |
| FLAN-T5 | base, large, xl | 250M-3B |
| Phi | Phi-2, Phi-3-mini | 2.7B-3.8B |

### Metrics

**Factuality: TruthfulQA MC1** — Multiple-choice single-answer accuracy on 817 questions using lm-evaluation-harness.

**Robustness: TextFooler (1 - ASR)** — TextFooler attack on SST-2 classification, 500+ examples per model.

**Calibration: ECE** — Expected Calibration Error with 10 equal-frequency bins from TruthfulQA predictions.

### Analysis Pipeline

1. **Correlation Analysis**: Pearson correlation with bootstrap 95% CI
2. **Confound Control**: Partial correlation for scale, within-family analysis
3. **Mediation Analysis**: Baron-Kenny with Sobel test
4. **Intervention**: Temperature scaling before/after comparison

---

## 4. Experimental Setup

### Sub-Hypothesis Structure

| ID | Type | Statement | Gate |
|----|------|-----------|------|
| H-E1 | Existence | Correlation r > 0.5 exists between MC1 and (1-ASR) | MUST_WORK |
| H-M1 | Mechanism | ECE variance > 0.001 across models | MUST_WORK |
| H-M2 | Mechanism | Lower ECE predicts higher MC1 | SHOULD_WORK |
| H-M3 | Mechanism | ECE mediates ≥30% of correlation | SHOULD_WORK |

### Success Criteria

- **Primary (P1)**: r > 0.5 with p < 0.05
- **Secondary (P2)**: Mediation > 30% of total effect
- **Tertiary (P3)**: Temperature scaling improves both metrics in ≥2/3 models

---

## 5. Results

**Status**: Preliminary results from pipeline validation. Full experimental results pending.

> **Important Note**: ASR values are **simulated** for pipeline testing. All correlation findings are artifacts.

### Pipeline Validation

| Model | MC1 Accuracy | ASR* | Robustness (1-ASR)* |
|-------|--------------|------|---------------------|
| google/flan-t5-base | 0.180 | 0.377 | 0.623 |
| google/flan-t5-large | 0.190 | 0.386 | 0.614 |
| microsoft/phi-2 | 0.290 | 0.439 | 0.561 |

*ASR values simulated; real TextFooler attacks not executed.

### Correlation (Mock Data)

- Pearson r = -0.999 (artifact of simulation)
- p-value = 0.034
- n = 3 (insufficient)

**Interpretation**: Near-perfect negative correlation is an artifact of the ASR simulation formula, not a genuine finding.

---

## 6. Discussion

### Summary

The methodology for testing calibration-mediated factuality-robustness correlation is validated. Full results await real experimental data.

### Critical Limitations

1. **Mock ASR data**: TextFooler ASR simulated, invalidating all correlation findings
2. **Sample size**: 3/12 models evaluated, insufficient for statistical inference

### Acceptable Limitations

1. Correlational design (temperature scaling provides quasi-causal evidence)
2. Word-level perturbations only
3. Open-weight models only

### Future Work

1. Run real TextFooler attacks
2. Complete 12-model evaluation
3. Execute ECE-based mediation analysis

---

## 7. Conclusion

We have presented a methodology for testing whether calibration quality mediates the correlation between LLM factuality and adversarial robustness. Our approach connects three previously isolated research communities through a testable hypothesis.

The pipeline is validated but experimental results are incomplete. To complete this work: execute real TextFooler attacks, evaluate remaining models, compute ECE from logits, and run mediation analysis.

If calibration does mediate the factuality-robustness relationship, this would provide a unified framework for LLM reliability evaluation and suggest that improving calibration could simultaneously improve both dimensions.

---

## References

[1] Lin, S., Hilton, J., & Evans, O. (2022). TruthfulQA: Measuring How Models Mimic Human Falsehoods. ACL 2022.

[2] Jin, D., Jin, Z., Zhou, J. T., & Szolovits, P. (2019). Is BERT Really Robust? A Strong Baseline for Natural Language Attack. arXiv:1907.11932.

[3] Minderer, M., et al. (2021). Revisiting the Calibration of Modern Neural Networks. arXiv:2106.07998.

[4] Khatun, A., & Brown, D. G. (2024). TruthEval: A Dataset to Evaluate LLM Truthfulness and Reliability. arXiv:2406.01855.

[5] You, J., et al. (2025). ARES: Probabilistic Soundness Guarantees in LLM Reasoning Chains. arXiv:2507.12948.

[6] Hoscilowicz, T., et al. (2024). Non-Linear Inference Time Intervention: Improving LLM Truthfulness. arXiv:2403.18680.

[7] Sawczyn, A., et al. (2025). FactSelfCheck: Fact-Level Black-Box Hallucination Detection.

[8] Zhao, C., et al. (2025). SPOC: Self-Correction with Probabilistic Oversight. arXiv:2506.06923.

[9] Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On Calibration of Modern Neural Networks. ICML 2017.

---

*Paper generated by Phase 6 Paper Writing Pipeline*
*Status: Methodology paper with incomplete experimental results*
*Data caveat: ASR values simulated; awaiting real TextFooler attacks*
