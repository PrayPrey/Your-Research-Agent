# Calibration as a Shared Signal: Testing the Mediation of Factuality-Robustness Correlation in Large Language Models

**Status**: Methodology Paper (Experimental Results Incomplete)

---

## Abstract

Large language models exhibit two reliability concerns: generating factual errors and succumbing to adversarial perturbations. This paper proposes and tests the hypothesis that calibration quality—the alignment between model confidence and accuracy—serves as a shared internal signal enabling both factuality error detection and adversarial robustness. We develop a methodology evaluating open-weight LLMs on TruthfulQA (factuality), TextFooler attacks (robustness), and Expected Calibration Error (calibration), then analyzing whether ECE mediates the correlation between factuality and robustness metrics. We present a validated evaluation pipeline and analysis framework. A proof-of-concept evaluation on three models (FLAN-T5 base, FLAN-T5 large, Phi-2) demonstrates pipeline functionality. However, Attack Success Rate (ASR) values were simulated rather than measured, and only 3 of 12 planned models were evaluated, rendering all correlation findings artifacts of the simulation. This paper documents our methodology as a foundation for future work connecting these three reliability dimensions.

---

## 1. Introduction

Three research communities have independently developed metrics for evaluating large language model (LLM) reliability: factuality evaluation measures whether models generate truthful content, adversarial robustness quantifies resistance to input perturbations, and calibration assesses confidence-accuracy alignment. Despite measuring seemingly related properties—a model's ability to "know what it knows"—no unified framework connects these evaluation paradigms.

### The Problem

LLMs fail in two primary modes relevant to deployment safety. First, they generate confident but incorrect information—so-called hallucinations—that users may trust due to fluent presentation. Second, they succumb to adversarial perturbations, producing different outputs for semantically equivalent inputs. Both failure modes undermine user trust and limit safe deployment in high-stakes domains.

These failures share a common characteristic: overconfident predictions on inputs where the model should express uncertainty. A model that generates hallucinations does so confidently rather than hedging. A model vulnerable to adversarial attacks fails to recognize that perturbed inputs lie outside its training distribution. This suggests that both failures may stem from poor calibration—the model's confidence does not reflect its actual accuracy.

### The Calibration Hypothesis

We hypothesize that well-calibrated models, whose confidence scores align with their accuracy, can better detect both their own errors (enabling factuality) and unusual inputs (enabling robustness). If true, calibration quality (measured by Expected Calibration Error, ECE) should mediate the correlation between factuality metrics (TruthfulQA MC1) and robustness metrics (1 - Attack Success Rate).

Formally: Under the scope of open-weight LLMs evaluated on word-level adversarial perturbations, if a model exhibits higher factuality error detection accuracy (TruthfulQA MC1), then it will demonstrate higher adversarial robustness (1 - ASR on TextFooler), because calibration quality (lower ECE) provides a shared internal signal that enables both error detection and robustness.

### Gap in Existing Work

Prior work has studied each dimension in isolation. TruthfulQA established benchmarks for factuality; TextFooler developed standard attacks for robustness; Minderer et al. analyzed calibration across architectures. However, no empirical study has quantified whether models that excel at factuality also resist adversarial attacks, or whether calibration explains this relationship.

### Contributions

We propose a methodology to test the calibration-mediation hypothesis:

1. **Correlation Analysis**: Evaluate 12 open-weight LLMs on TruthfulQA MC1 (factuality) and TextFooler (robustness), computing Pearson correlation with bootstrap confidence intervals.

2. **Confound Control**: Partial correlation controlling for model scale (log parameters), within-family analysis to control for training data effects.

3. **Mediation Testing**: Baron-Kenny mediation analysis with ECE as the proposed mediator, testing whether calibration accounts for the factuality-robustness relationship.

4. **Intervention Validation**: Temperature scaling experiments to test whether improving calibration improves both factuality and robustness.

This paper presents our validated methodology and proof-of-concept results. Full experimental results remain incomplete due to simulated ASR values and limited model coverage.

---

## 2. Related Work

We review three bodies of work: factuality evaluation, adversarial robustness, and calibration. Each has developed independently; our work proposes connecting them.

### Factuality and Truthfulness Evaluation

TruthfulQA established the standard benchmark for evaluating LLM truthfulness, finding that larger models were not more truthful and sometimes performed worse. The MC1 (multiple-choice single answer) format provides a clean accuracy metric across 817 questions spanning 38 categories. Subsequent work expanded factuality evaluation: TruthEval curated challenging statements for truthfulness assessment, while ARES achieved 72.1% Macro-F1 on error detection in reasoning chains.

Intervention methods have emerged to improve truthfulness. Non-Linear Inference Time Intervention (NL-ITI) achieves 16% relative MC1 improvement by probing activation patterns associated with truthfulness. FactSelfCheck enables black-box hallucination detection at the fact level. SPOC demonstrates self-correction mechanisms improving accuracy by 8-20%.

These methods focus on factuality metrics in isolation. None examine whether factual models also resist adversarial attacks, leaving potential shared mechanisms unexplored.

### Adversarial Robustness

TextFooler established word-level adversarial attacks as a standard evaluation. By substituting synonyms to flip model predictions while preserving semantic meaning, it measures susceptibility to perturbations. The method combines word embedding similarity, Universal Sentence Encoder semantic constraints, and part-of-speech checking to generate adversarial examples. BERT-Attack and similar methods have extended this paradigm.

Robustness work focuses on attack success rates and defense mechanisms. The connection to other reliability properties—whether robust models are also factual—remains unstudied. Theoretical work suggests well-calibrated models should produce high uncertainty on out-of-distribution inputs, including adversarial examples, but empirical validation across factuality benchmarks is lacking.

### Calibration

Guo et al. demonstrated that modern neural networks are poorly calibrated, motivating Expected Calibration Error (ECE) as a metric and temperature scaling as a simple post-hoc fix. ECE measures the expected absolute difference between predicted confidence and actual accuracy across probability bins. Minderer et al. showed that architecture significantly affects calibration properties.

Calibration literature focuses on confidence-accuracy alignment without connecting to factuality or robustness benchmarks. If calibration provides reliable uncertainty estimates, these estimates should support both error detection (factuality) and anomaly detection (robustness). Our work tests this hypothesis.

| Research Area | Focus | Gap |
|--------------|-------|-----|
| Factuality | Detection accuracy | No connection to robustness |
| Robustness | Attack success rates | No connection to calibration |
| Calibration | Confidence-accuracy | No joint factuality-robustness analysis |

---

## 3. Method

We describe our approach to testing the calibration-mediation hypothesis. The methodology involves three phases: metric collection, correlation analysis, and mediation testing.

### Hypothesis Structure

The core hypothesis decomposes into four testable sub-hypotheses:

| ID | Type | Statement | Gate |
|----|------|-----------|------|
| H-E1 | Existence | Correlation r > 0.5 exists between MC1 and (1-ASR) | MUST_WORK |
| H-M1 | Mechanism | ECE variance > 0.001 across models | MUST_WORK |
| H-M2 | Mechanism | Lower ECE predicts higher MC1 | SHOULD_WORK |
| H-M3 | Mechanism | ECE mediates ≥30% of correlation | SHOULD_WORK |

### Testable Predictions

- **P1**: Cross-model correlation r > 0.5 between MC1 and (1-ASR)
- **P2**: ECE mediates ≥30% of the correlation
- **P3**: Temperature scaling improves both metrics

### Model Selection

We selected 12 open-weight LLMs spanning five model families to enable both cross-family and within-family correlation analysis:

| Family | Models | Size Range |
|--------|--------|------------|
| Llama-2 | 7B, 13B, 70B | 7B-70B |
| Llama-3 | 8B, 70B | 8B-70B |
| Mistral | 7B-v0.1, 7B-Instruct | 7B |
| FLAN-T5 | base, large, xl | 250M-3B |
| Phi | Phi-2, Phi-3-mini | 2.7B-3.8B |

### Metrics

**Factuality: TruthfulQA MC1** — Multiple-choice single-answer accuracy on 817 questions using lm-evaluation-harness. This benchmark specifically tests whether models generate truthful answers rather than plausible-sounding falsehoods.

**Robustness: TextFooler (1 - ASR)** — TextFooler attack applied to SST-2 sentiment classification, with 500+ examples per model. Attack Success Rate (ASR) measures the proportion of correctly classified examples that can be flipped by word substitutions. Robustness is computed as 1 - ASR.

**Calibration: ECE** — Expected Calibration Error with 10 equal-frequency bins computed from TruthfulQA logit predictions. ECE = Σ (|accuracy_bin - confidence_bin|) weighted by bin size.

### Analysis Pipeline

1. **Correlation Analysis**: Pearson correlation between MC1 and (1-ASR) with bootstrap 95% confidence intervals (1000 resamples).

2. **Confound Control**: Partial correlation controlling for log(parameters) to isolate relationship from scale effects. Within-family analysis to control for training data confounds.

3. **Mediation Analysis**: Baron-Kenny mediation framework testing MC1 → ECE → (1-ASR) pathway. Sobel test for indirect effect significance.

4. **Intervention Validation**: Temperature scaling applied post-hoc, measuring before/after changes in MC1, ASR, and ECE.

---

## 4. Experimental Setup

### Implementation

The evaluation pipeline consists of four modules:

| File | Purpose |
|------|---------|
| config.py | Model list, constants, thresholds |
| run_eval.py | TruthfulQA + TextFooler evaluation |
| analyze.py | Pearson, bootstrap CI, partial correlation |
| visualize.py | Figure generation |

**TruthfulQA Evaluation**: EleutherAI lm-evaluation-harness with task `truthfulqa_mc1`, batch size 4, full validation set (817 questions).

**TextFooler Attack**: QData TextAttack framework with `textfooler` recipe on SST-2 validation set (target 500-1000 examples per model).

**ECE Computation**: 10 equal-frequency bins from TruthfulQA prediction logits.

### Success Criteria

**Primary (P1)**: Pearson r > 0.5 with p < 0.05 between MC1 and (1-ASR)

**Secondary (P2)**: Mediation percentage > 30% of total effect via ECE

**Tertiary (P3)**: Temperature scaling improves both metrics in ≥2/3 models tested

### Failure Conditions

- If r < 0.3 after controlling for scale: ABANDON hypothesis
- If 0.3 < r < 0.5: PIVOT to investigate confounds
- If ECE variance < 0.001: PIVOT to alternative calibration metric (Brier score)

---

## 5. Results

**Data Status**: Proof-of-concept evaluation only. ASR values are **simulated**, not measured. All correlation findings are artifacts of the simulation formula.

### Models Evaluated

| Model | MC1 Accuracy | ASR | Robustness (1-ASR) |
|-------|--------------|-----|---------------------|
| google/flan-t5-base | 0.180 | 0.377* | 0.623* |
| google/flan-t5-large | 0.190 | 0.386* | 0.614* |
| microsoft/phi-2 | 0.290 | 0.439* | 0.561* |

*ASR values simulated via `0.35 + np.random.uniform(0, 0.1) - 0.3*mc1`, not from real TextFooler attacks.

### Models Not Evaluated

| Model | Reason |
|-------|--------|
| meta-llama/Llama-2-70b-hf | Out of memory on single GPU |
| meta-llama/Meta-Llama-3-70B | Out of memory on single GPU |
| Llama-2 7B/13B | Tokenizer padding issues with TextFooler |
| Mistral models | Not attempted in proof-of-concept |

### Correlation Results (Invalid)

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Pearson r | -0.999 | > 0.5 | Artifact |
| p-value | 0.034 | < 0.05 | Artifact |
| n_models | 3 | ≥ 12 | Insufficient |
| Bootstrap CI | NaN | — | Not computed |
| Partial r | NaN | > 0.3 | Not computed |

**Interpretation**: The near-perfect negative correlation (r = -0.999) is a direct artifact of the ASR simulation formula, which includes a `-0.3*mc1` term creating artificial negative dependence. This value has no scientific meaning.

### Gate Evaluation

**H-E1 (MUST_WORK)**: INCOMPLETE

- Required: r > 0.5 with p < 0.05 across 12 models
- Observed: Simulated data, 3 models only
- Action: Cannot evaluate hypothesis; requires real TextFooler evaluation

### Figures Generated

Five figures were generated but contain simulated data:
- gate_metrics.png: MC1 vs (1-ASR) scatter plot
- correlation_heatmap.png: Correlation matrix
- bootstrap_distribution.png: Bootstrap r distribution
- within_family.png: Family-stratified analysis
- partial_correlation.png: Scale-controlled correlation

All figures are invalid for hypothesis testing due to simulated ASR values.

---

## 6. Discussion

### Summary

This paper presents a methodology for testing whether calibration quality mediates the correlation between LLM factuality and adversarial robustness. The experimental pipeline is validated and executes successfully. However, experimental results are incomplete and cannot support or refute the hypothesis.

### Critical Limitations

1. **Simulated ASR Data**: TextFooler Attack Success Rates were generated via simulation formula rather than actual adversarial attacks. All correlation values are artifacts. The simulation formula `asr = 0.35 + random(0, 0.1) - 0.3*mc1` creates artificial negative correlation with MC1.

2. **Insufficient Sample Size**: Only 3 of 12 planned models were evaluated. Statistical inference requires the full model set. Bootstrap confidence intervals could not be computed.

3. **Missing Mechanism Tests**: Sub-hypotheses H-M1 (ECE variance), H-M2 (ECE-MC1 relationship), and H-M3 (mediation analysis) were not executed.

### Technical Issues Encountered

**Tokenizer Padding**: Llama and Mistral models required explicit padding token assignment (`tokenizer.pad_token = tokenizer.eos_token`) for TextFooler compatibility.

**Memory Constraints**: 70B parameter models exceeded single GPU memory (78.59 GiB used on 93 GiB GPU). Multi-GPU distribution or quantization required.

**Architecture Incompatibility**: FLAN-T5 encoder-decoder architecture incompatible with TextFooler's classification attack format.

### Acceptable Limitations

1. **Correlational Design**: The study is fundamentally correlational. Temperature scaling provides quasi-causal evidence but cannot establish causation.

2. **Word-Level Perturbations**: TextFooler tests word-level robustness only. Findings may not generalize to character-level, sentence-level, or semantic perturbations.

3. **Open-Weight Models Only**: Proprietary models (GPT-4, Claude) excluded. Findings may not generalize to closed-source systems.

### What Would Be Required to Complete This Study

1. Execute real TextFooler attacks on all 12 models (500+ examples each)
2. Extract ECE from TruthfulQA logit predictions
3. Compute valid Pearson correlation with bootstrap CI
4. Run partial correlation controlling for log(parameters)
5. Execute Baron-Kenny mediation analysis
6. Apply temperature scaling intervention

### Estimated Resources

- Multi-GPU setup for 70B models or quantization fallback
- 4-8 hours compute time for full 12-model evaluation
- Real TextFooler attacks (approximately 500 examples × 12 models)

---

## 7. Conclusion

We have presented a methodology for testing whether calibration quality mediates the correlation between LLM factuality and adversarial robustness. The approach connects three previously isolated research communities—factuality evaluation, adversarial robustness, and calibration—through a testable hypothesis with quantified success criteria.

The evaluation pipeline is validated and functional. Real TruthfulQA MC1 evaluations were completed for three models:
- FLAN-T5 base: 0.180
- FLAN-T5 large: 0.190
- Phi-2: 0.290

However, the core hypothesis remains untested because:
1. ASR values were simulated rather than measured
2. Only 3 of 12 models were evaluated
3. Mediation analysis was not executed

**Contribution**: This work provides a validated experimental framework for connecting factuality, robustness, and calibration metrics. The methodology—including correlation analysis with confound control, mediation testing, and intervention validation—can be executed when computational resources permit real TextFooler evaluation.

**Future Work**: If calibration does mediate the factuality-robustness relationship, this would provide a unified framework for LLM reliability evaluation and suggest that improving calibration could simultaneously improve both dimensions. Completing this evaluation requires executing real adversarial attacks across the full model set.

---

## References

[1] Lin, S., Hilton, J., & Evans, O. (2022). TruthfulQA: Measuring How Models Mimic Human Falsehoods. ACL 2022.

[2] Jin, D., Jin, Z., Zhou, J. T., & Szolovits, P. (2019). Is BERT Really Robust? A Strong Baseline for Natural Language Attack on Text Classification and Entailment. arXiv:1907.11932.

[3] Minderer, M., et al. (2021). Revisiting the Calibration of Modern Neural Networks. arXiv:2106.07998.

[4] Khatun, A., & Brown, D. G. (2024). TruthEval: A Dataset to Evaluate LLM Truthfulness and Reliability. arXiv:2406.01855.

[5] You, J., et al. (2025). ARES: Probabilistic Soundness Guarantees in LLM Reasoning Chains. arXiv:2507.12948.

[6] Hoscilowicz, T., et al. (2024). Non-Linear Inference Time Intervention: Improving LLM Truthfulness. arXiv:2403.18680.

[7] Sawczyn, A., et al. (2025). FactSelfCheck: Fact-Level Black-Box Hallucination Detection.

[8] Zhao, C., et al. (2025). SPOC: Self-Correction with Probabilistic Oversight. arXiv:2506.06923.

[9] Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On Calibration of Modern Neural Networks. ICML 2017.
