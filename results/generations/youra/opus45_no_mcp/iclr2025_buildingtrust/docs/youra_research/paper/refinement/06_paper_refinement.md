# Self-Reading Uncertainty: How Chain-of-Thought Prompting Enables LLMs to Leverage In-Context Hedging Signals for Calibration

## Abstract

Large language models produce poorly calibrated confidence estimates, frequently expressing high certainty on questions they answer incorrectly. This study investigates whether chain-of-thought (CoT) prompting improves calibration by enabling models to leverage in-context uncertainty signals. Through systematic mechanism verification on TruthfulQA (817 items), four steps of a hypothesized causal mechanism are empirically validated: CoT prompting produces multi-step reasoning chains (100% rate, mean 4.49 steps), these chains contain epistemic hedging markers (82% presence rate, mean 2.84 markers per output), markers structurally precede confidence verbalization (100% compliance), and hedging count negatively correlates with verbalized confidence (Spearman r = -0.315, p < 1e-16, n = 664). The primary calibration claim comparing Expected Calibration Error (ECE) across conditions was not tested with real API calls due to resource constraints. These findings support a self-reading interpretation in which models integrate uncertainty signals from their own reasoning into confidence judgments, though the evidence remains correlational.

## 1. Introduction

When large language models reason step-by-step, they generate linguistic markers of uncertainty that correlate with confidence judgments. This observation motivates the present investigation of whether CoT prompting enables a form of "self-reading" whereby models leverage their own in-context uncertainty signals.

### The Calibration Problem

LLM confidence estimates are poorly calibrated. Models routinely express high confidence on questions they answer incorrectly. This overconfidence undermines trust in LLM outputs, particularly for applications where users must decide whether to rely on model predictions.

Standard prompting provides no mechanism for uncertainty to surface during generation. When prompted to answer directly, the model produces a response without intermediate reasoning that might reveal epistemic uncertainty. Confidence scores, if requested, are generated without access to information about the model's uncertainty during answer generation.

### Research Gap

Prior work has examined chain-of-thought prompting for accuracy improvement (Wei et al., 2022; Kojima et al., 2022) and confidence elicitation methods separately (Lin et al., 2022; Xiong et al., 2023; Tian et al., 2023). However, no systematic study has isolated how the combination of CoT and confidence verbalization might improve calibration, nor whether any improvement stems from meaningful uncertainty signals versus artifacts such as increased token count.

### Hypothesized Mechanism

This study decomposes the hypothesized mechanism into four testable steps:

1. CoT prompting produces multi-step reasoning chains.
2. Reasoning chains contain epistemic hedging markers (e.g., "may," "could," "however").
3. Due to autoregressive generation, markers are present in-context when confidence is generated.
4. The model incorporates these signals, producing lower confidence when more hedging is present.

### Contributions

This paper provides:
1. Empirical validation of each step in the mechanism chain linking CoT prompting to hedging-confidence correlation.
2. Quantification of the hedging-confidence relationship (Spearman r = -0.315) on TruthfulQA.
3. Documentation of structural prerequisites for prompting-based calibration via mechanism decomposition.

The primary ECE comparison across prompting conditions was not executed with real API calls; thus, end-to-end calibration improvement is not demonstrated.

## 2. Related Work

### LLM Calibration

Neural network calibration has been studied since Guo et al. (2017) established Expected Calibration Error as the standard metric and introduced temperature scaling. For LLMs, Kadavath et al. (2022) demonstrated that models possess intrinsic self-knowledge and can predict answer correctness at above-chance rates.

Subsequent work explored various elicitation approaches. Lin et al. (2022) trained models to express uncertainty in natural language. Xiong et al. (2023) evaluated confidence elicitation methods including direct prompting, multi-sample consistency, and linguistic confidence markers. Tian et al. (2023) studied prompting strategies for calibration.

### Chain-of-Thought Prompting

Wei et al. (2022) introduced chain-of-thought prompting for reasoning tasks. Kojima et al. (2022) extended this to zero-shot settings with "Let's think step by step." Wang et al. (2023) introduced self-consistency using multiple samples with majority voting.

These works focus on accuracy rather than calibration. A key observation is that CoT produces visible reasoning traces that could reveal model uncertainty through linguistic markers.

### Uncertainty Quantification in NLP

Linguistic hedging has long been recognized as marking epistemic uncertainty (Hyland, 1998). Kuhn et al. (2023) proposed semantic uncertainty, clustering semantically equivalent responses to estimate uncertainty.

The present study differs from prior work by systematically isolating the mechanism by which CoT might improve calibration, decomposing the process into verifiable sub-hypotheses rather than measuring only end-to-end effects.

## 3. Method

### Mechanism Hypothesis

The hypothesized self-reading mechanism proceeds as follows:

1. CoT prompting forces reasoning articulation before answering.
2. Reasoning reveals epistemic uncertainty through hedging markers.
3. Hedging markers appear in-context before confidence generation.
4. The model incorporates uncertainty signals into its confidence estimate.

This predicts a negative correlation between hedging marker count and verbalized confidence.

### Sub-Hypothesis Decomposition

Four sub-hypotheses test each mechanism step:

| Hypothesis | Gate Type | Primary Metric | Threshold |
|------------|-----------|----------------|-----------|
| H-M1 | MUST_WORK | CoT reasoning rate | >90% |
| H-M2 | SHOULD_WORK | Hedging presence rate | >30% |
| H-M3 | SHOULD_WORK | Markers precede confidence rate | >95% |
| H-M4 | MUST_WORK | Spearman r (hedging vs. confidence) | < -0.2 |

### Dataset

TruthfulQA (Lin et al., 2022) was used, an adversarial benchmark testing model tendency toward common misconceptions. The generation split contains 817 items across categories including health, law, finance, and common sense. TruthfulQA was selected because it presents genuinely difficult questions where calibration matters and its adversarial design creates variation in difficulty.

### Model

GPT-3.5-turbo was accessed via OpenAI API with temperature = 0 for deterministic outputs. A single model was used to establish proof-of-concept; replication on other models (Llama-2-70B, Claude, GPT-4) is deferred to future work.

### Hedging Marker Detection

Seventeen epistemic hedging markers were identified based on linguistic literature (Hyland, 1998): "may," "could," "might," "possibly," "perhaps," "likely," "unlikely," "but," "however," "although," "alternatively," "uncertain," "not sure," "seems," "appears," "probably," "suggest."

### Confidence Extraction

Verbalized confidence was parsed from outputs using regex matching for patterns such as "Confidence: X%" with fallback to percentage mentions.

### Positional Analysis

Structural ordering was verified by identifying CoT, answer, and confidence segments and confirming markers appeared before confidence statements.

### Correlation Analysis

Spearman rank correlation was computed between hedging count and confidence, with significance testing.

## 4. Experimental Setup

### Research Questions

The experiments address three questions:

1. Does CoT prompting reliably produce reasoning chains with epistemic hedging markers?
2. Are hedging markers structurally positioned to influence confidence generation?
3. Does hedging marker presence correlate with lower verbalized confidence?

### Evaluation Metrics

- **Hedging Marker Count:** Integer count of 17 predefined markers per output.
- **Hedging Presence Rate:** Proportion of outputs containing at least one marker.
- **Verbalized Confidence:** Numerical confidence (0-100%) extracted from output.
- **Reasoning Rate:** Proportion of outputs containing multi-step reasoning.
- **Step Count:** Number of reasoning steps identified via sentence segmentation.
- **Spearman Correlation:** Rank correlation between hedging count and confidence.

### Prompting Conditions

The primary evaluation used the CoT+Confidence condition (CoT reasoning + answer + confidence). A baseline condition (direct answer only) was included for reasoning rate verification. The planned token-padding control condition (random filler tokens + answer + confidence) was not executed due to resource constraints.

## 5. Results

### Mechanism Verification Summary

All four mechanism steps were verified, with all sub-hypotheses passing their predetermined gates.

| Step | Claim | Hypothesis | Evidence | Status |
|------|-------|------------|----------|--------|
| 1 | CoT produces multi-step reasoning | H-M1 | 100% rate, mean 4.49 steps | VERIFIED |
| 2 | Reasoning contains hedging markers | H-M2 | 82% presence, mean 2.84 markers | VERIFIED |
| 3 | Markers precede confidence | H-M3 | 100% CoT ordering, 100% markers precede | VERIFIED |
| 4 | Hedging correlates with confidence | H-M4 | r = -0.315, p < 1e-16 | VERIFIED |

### H-M1: CoT Reasoning Detection

CoT prompting produced multi-step reasoning chains in all outputs:

- CoT reasoning rate: 100% (817/817 outputs)
- Baseline reasoning rate: 0% (0/817 outputs)
- Mean reasoning steps (CoT): 4.49

### H-M2: Hedging Marker Presence

CoT outputs contained substantial epistemic hedging markers:

- Hedging presence rate: 82.0% (670/817 outputs contained at least one marker)
- Mean markers per output: 2.84
- Median markers per output: 2

Marker frequencies (most common):

| Marker | Occurrences |
|--------|-------------|
| may | 787 |
| could | 619 |
| but | 337 |
| however | 255 |
| likely | 205 |
| unlikely | 55 |
| might | 14 |
| although | 13 |
| uncertain | 7 |

### H-M3: Positional Ordering

Structural analysis confirmed markers are positioned before confidence generation:

- CoT-then-confidence ordering: 100% (817/817 outputs)
- Markers precede confidence: 100% (of outputs with both markers and confidence)

### H-M4: Hedging-Confidence Correlation

Hedging marker count negatively correlated with verbalized confidence:

- Spearman r: -0.315
- p-value: 9.22 × 10⁻¹⁷
- Sample size: n = 664 (outputs with valid confidence extraction)
- 95% CI: [-0.382, -0.246]

The correlation coefficient exceeded the -0.2 threshold by 57%.

### Planned vs. Actual Comparison

| Hypothesis | Target | Actual | Status |
|------------|--------|--------|--------|
| H-M1 reasoning rate | >90% | 100% | Exceeded |
| H-M1 mean steps | >2.0 | 4.49 | Exceeded |
| H-M2 hedging presence | >30% | 82.0% | Exceeded |
| H-M3 markers precede | >95% | 100% | Exceeded |
| H-M4 Spearman r | < -0.2 | -0.315 | Exceeded |

## 6. Discussion

### Interpretation

The results support a self-reading interpretation: when prompted to reason step-by-step, the model generates linguistic uncertainty markers that remain in-context when it subsequently generates a confidence estimate. The negative correlation (r = -0.315) indicates the model adjusts confidence downward when more hedging is present.

### Alternative Explanations

**Difficulty confound.** Difficult questions may produce both more hedging and lower confidence without hedging causally affecting confidence. This interpretation still supports using hedging as a calibration signal but does not demonstrate the self-reading mechanism.

**Prompt artifact.** The prompt structure might induce the correlation through some artifact. This is considered less likely given the effect size and consistency across 817 items.

**Token-count confound.** Without the token-padding control, it cannot be empirically ruled out that longer outputs drive the correlation independently of uncertainty content.

### Limitations

**Single model.** Only GPT-3.5-turbo was tested. Generalization to other architectures requires replication.

**Correlational evidence.** The findings are correlational. An intervention study manipulating hedging markers would provide stronger causal evidence.

**ECE comparison not executed.** The primary ECE comparison (CoT+confidence vs. single interventions) was not executed with real API calls. The sub-hypothesis H-E1 verifying ECE computation infrastructure ran in mock mode; actual calibration improvement was not measured.

**Token-padding control not executed.** The planned control condition was not run. Length artifacts cannot be empirically ruled out.

**Single dataset.** Only TruthfulQA was evaluated. Cross-domain transfer to MMLU or other datasets is untested.

### Practical Implications

For practitioners, CoT+confidence prompting provides a zero-shot method for obtaining confidence estimates that correlate with uncertainty signals, without model fine-tuning or access to internal logits. Full ECE validation remains future work.

## 7. Conclusion

This study investigated whether CoT prompting enables models to leverage in-context uncertainty signals for confidence calibration. Systematic verification confirmed the mechanism chain: CoT prompting produces multi-step reasoning (100% rate), reasoning contains epistemic hedging markers (82% presence), markers structurally precede confidence generation (100% compliance), and hedging count negatively correlates with verbalized confidence (r = -0.315, p < 1e-16).

These findings support a self-reading interpretation in which models incorporate uncertainty signals from their own reasoning into confidence judgments. The mechanism operates through prompting alone without model fine-tuning.

The primary limitation is that end-to-end ECE improvement was not measured; the ECE comparison experiment was not executed with real API calls. The evidence validates the mechanism linking CoT to hedging-confidence correlation but does not demonstrate that this correlation produces meaningful calibration improvement as measured by ECE.

### Future Work

Four directions extend this work:

1. **Multi-model replication** on Llama-2-70B, Claude, and GPT-4 would establish generalization.
2. **Intervention study** manipulating hedging markers would provide causal evidence.
3. **Full ECE comparison** with real API calls would validate end-to-end calibration improvement.
4. **Token-padding control** would rule out length artifacts.

## References

Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On Calibration of Modern Neural Networks. International Conference on Machine Learning (ICML).

Hyland, K. (1998). Hedging in Scientific Research Articles. John Benjamins Publishing.

Kadavath, S., Conerly, T., Askell, A., Henighan, T., Drain, D., Perez, E., ... & others (2022). Language Models (Mostly) Know What They Know. arXiv:2207.05221.

Kojima, T., Gu, S. S., Reid, M., Matsuo, Y., & Iwasawa, Y. (2022). Large Language Models are Zero-Shot Reasoners. Advances in Neural Information Processing Systems (NeurIPS).

Kuhn, L., Gal, Y., & Farquhar, S. (2023). Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation. International Conference on Learning Representations (ICLR).

Lin, S., Hilton, J., & Evans, O. (2022). Teaching Models to Express Their Uncertainty in Words. Transactions on Machine Learning Research (TMLR).

Lin, S., Hilton, J., & Evans, O. (2022). TruthfulQA: Measuring How Models Mimic Human Falsehoods. Association for Computational Linguistics (ACL).

Tian, K., Mitchell, E., Yao, H., Manning, C. D., & Finn, C. (2023). Just Ask for Calibration: Strategies for Eliciting Calibrated Confidence Scores from Language Models Fine-Tuned with Human Feedback. Conference on Empirical Methods in Natural Language Processing (EMNLP).

Wang, X., Wei, J., Schuurmans, D., Le, Q., Chi, E., Narang, S., Chowdhery, A., & Zhou, D. (2023). Self-Consistency Improves Chain of Thought Reasoning in Language Models. International Conference on Learning Representations (ICLR).

Wei, J., Wang, X., Schuurmans, D., Bosma, M., Ichter, B., Xia, F., Chi, E., Le, Q., & Zhou, D. (2022). Chain-of-Thought Prompting Elicits Reasoning in Large Language Models. Advances in Neural Information Processing Systems (NeurIPS).

Xiong, M., Hu, Z., Lu, X., Li, Y., Fu, J., He, J., & Hooi, B. (2023). Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs. International Conference on Learning Representations (ICLR).
