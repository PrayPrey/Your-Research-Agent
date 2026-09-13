# Orthogonal Uncertainty Signals for LLM Hallucination Detection

**Anonymous Authors**

---

## Abstract

Large language models generate fluent but factually incorrect text, yet existing uncertainty quantification methods for detecting these hallucinations have been developed and evaluated in isolation. This work presents a systematic comparison of entropy-based and consistency-based uncertainty signals for hallucination detection on the same factuality benchmark. Experiments on TruthfulQA with LLaMA-2-7B reveal that these signals are orthogonal: token entropy and N-sample consistency share only 5.2% of variance (Pearson r = 0.228, p < 10⁻¹⁰). Consistency-based detection achieves a large effect size distinguishing correct from incorrect responses (Cohen's d = 1.068, 95% CI [0.921, 1.215]). On 18.1% of questions where the methods disagree substantially, each achieves AUROC exceeding 0.75 on its winning subset, demonstrating complementary detection capability. These findings establish an empirical foundation for multi-signal hallucination detection approaches.

---

## 1. Introduction

On 18% of factuality questions, token entropy and answer consistency point in opposite directions—and each method is right about its own subset. This observation motivates a systematic investigation of whether existing uncertainty quantification approaches capture fundamentally different hallucination patterns.

Large language models generate fluent text that may be factually incorrect, a phenomenon termed hallucination. Detecting such errors before deployment is relevant for applications in domains where factual accuracy matters. Two approaches have emerged: entropy-based methods that measure uncertainty in the model's token probability distribution, and consistency-based methods that measure agreement across multiple sampled responses.

These approaches have been developed and evaluated independently. Kuhn et al. (2023) introduced semantic entropy for natural language generation tasks, while Manakul et al. (2023) developed SelfCheckGPT for consistency-based detection on biography generation. Neither work directly compared these methods on the same factuality benchmark with the same model. This leaves a gap: it is unknown whether entropy and consistency capture redundant information or complementary signals.

This work presents the first systematic comparison of token entropy and N-sample consistency on TruthfulQA with LLaMA-2-7B. The key finding is that these signals are orthogonal (r = 0.228), sharing only approximately 5% of variance. The contributions are:

1. **Systematic comparison** of entropy and consistency methods on the same factuality benchmark (TruthfulQA) with the same model (LLaMA-2-7B).

2. **Empirical demonstration of orthogonality** (r = 0.228, p < 10⁻¹⁰), showing these methods capture different aspects of model uncertainty.

3. **Complementarity analysis** showing that 18.1% of questions exhibit method disagreement, with each method achieving AUROC > 0.75 on its winning subset.

---

## 2. Related Work

### 2.1 Entropy-Based Uncertainty Quantification

Token-level entropy measures uncertainty in next-token prediction by computing the entropy of the softmax distribution over vocabulary. High entropy indicates the model is uncertain about which token to generate.

Kadavath et al. (2022) demonstrated that LLMs exhibit calibration properties, with confidence scores correlating with correctness on question-answering tasks. Kuhn et al. (2023) introduced semantic entropy, which clusters semantically equivalent answers before computing entropy. Malinin and Gales (2018) provided theoretical foundations for distinguishing epistemic and aleatoric uncertainty in neural networks.

### 2.2 Consistency-Based Detection

An alternative approach measures hallucination through response consistency across multiple generations. Manakul et al. (2023) introduced SelfCheckGPT, which generates multiple responses and computes consistency via embedding similarity. They evaluated on WikiBio biography generation. Wang et al. (2023) explored self-consistency in chain-of-thought reasoning.

### 2.3 The Gap

The two paradigms have evolved independently on different benchmarks:

| Method | Benchmark | Model | Direct Comparison |
|--------|-----------|-------|------------------|
| Semantic Entropy (Kuhn 2023) | NLG tasks | Various | No consistency baseline |
| SelfCheckGPT (Manakul 2023) | WikiBio | GPT-3 | No entropy baseline |
| P(True) (Kadavath 2022) | QA tasks | Proprietary | No consistency baseline |

No prior work has compared both methods on the same factuality benchmark using the same model with analysis of whether signals are redundant or orthogonal.

---

## 3. Method

### 3.1 Overview

Two uncertainty signals are computed for each question-answer pair:

1. **Token Entropy:** Mean entropy over generated tokens, computed from logit distributions during greedy decoding
2. **N-Sample Consistency:** Mean pairwise cosine similarity of response embeddings across multiple sampled generations

### 3.2 Token Entropy Computation

For a generated response with tokens t₁, ..., tₙ, token entropy is computed as:

H(tᵢ) = -∑ᵥ∈V p(v | t<ᵢ) log p(v | t<ᵢ)

where V is the vocabulary and p(v | t<ᵢ) is the softmax probability from the model's logits.

**Aggregation:** Mean entropy over response tokens:

H_response = (1/n) ∑ᵢ₌₁ⁿ H(tᵢ)

**Implementation:** Greedy decoding with output_scores=True to access logits. Numerical stability maintained via clamp(min=1e-10) before log computation. Maximum response length: 100 tokens.

### 3.3 N-Sample Consistency Computation

For N independently sampled responses to the same question:

1. Generate N responses with temperature sampling (T=1.0)
2. Encode each response using a sentence embedding model
3. Compute pairwise cosine similarity
4. Average to obtain consistency score

C = (2 / N(N-1)) ∑ᵢ<ⱼ cos(eᵢ, eⱼ)

where eᵢ is the embedding of response i.

**Parameters:**
- N = 5 samples (following SelfCheckGPT)
- Temperature = 1.0
- Embedding model: sentence-transformers/all-MiniLM-L6-v2

### 3.4 Ground Truth Labels

TruthfulQA's generation split (817 questions) is used with factuality labels derived from BERTScore comparison between model response and reference answers:

- **Correct:** BERTScore F1 ≥ 0.5 with best_answer
- **Incorrect:** BERTScore F1 < 0.5 with best_answer

### 3.5 Orthogonality Analysis

**Correlation Analysis:** Pearson r between entropy and (1-consistency) across all questions. Threshold: r < 0.3 indicates orthogonal signals (< 9% shared variance).

**Discordant Case Analysis:** Questions where entropy rank differs from consistency rank by >50 percentile points. Threshold: >15% discordant cases.

### 3.6 Statistical Validation

- **Effect size:** Cohen's d with pooled standard deviation
- **Significance testing:** Mann-Whitney U test (one-sided) for group comparisons
- **Confidence intervals:** 95% CI via bootstrap (1000 iterations)
- **AUROC:** Area under ROC curve

---

## 4. Experimental Setup

### 4.1 Dataset

**TruthfulQA (Generation Split):** A benchmark designed to evaluate truthfulness in language model responses (Lin et al., 2022).

| Property | Value |
|----------|-------|
| Questions | 817 |
| Format | Open-ended generation |
| Labels | Binary (correct/incorrect via BERTScore) |
| Design | Adversarial (questions crafted to elicit falsehoods) |

### 4.2 Model

**LLaMA-2-7B:** A publicly available decoder-only LLM (Meta, 2023).

| Property | Value |
|----------|-------|
| Parameters | 7 billion |
| Architecture | Decoder-only transformer |
| Precision | float16 |
| HuggingFace ID | meta-llama/Llama-2-7b-hf |

### 4.3 Evaluation Metrics

**Primary Metric:** AUROC for hallucination detection ranking quality.

**Effect Size:** Cohen's d (threshold: d > 0.2).

**Orthogonality:** Pearson r (threshold: r < 0.3).

**Complementarity:** Discordant proportion (threshold: >15%) and subset AUROC (threshold: >0.6).

---

## 5. Results

### 5.1 Main Results: Orthogonality

The correlation between entropy and consistency scores is low:

| Metric | Value | p-value |
|--------|-------|---------|
| Pearson r | 0.228 | 4.11 × 10⁻¹¹ |
| Spearman ρ | 0.241 | 3.18 × 10⁻¹² |

With r = 0.228, entropy and consistency share approximately 5.2% of variance (r² = 0.052).

### 5.2 Consistency Effect Size

Consistency shows a large effect size distinguishing correct from incorrect responses:

| Group | N | Mean | Std |
|-------|---|------|-----|
| Correct | 367 | 0.720 | 0.111 |
| Incorrect | 450 | 0.577 | 0.151 |

| Statistic | Value |
|-----------|-------|
| Cohen's d | 1.068 |
| 95% CI | [0.921, 1.215] |
| t-statistic | 15.19 |
| p-value | 4.64 × 10⁻⁴⁶ |

Correct responses have approximately 24% higher consistency than incorrect responses.

### 5.3 Complementarity Analysis

Questions where entropy and consistency rankings disagree substantially:

| Category | Count | Proportion |
|----------|-------|------------|
| Total questions | 817 | 100% |
| Concordant | 669 | 81.9% |
| Discordant | 148 | 18.1% |

**Discordant Subset Breakdown:**
- High-entropy-only: 76 questions
- High-inconsistency-only: 72 questions

**Subset AUROC:**

| Subset | AUROC | N |
|--------|-------|---|
| High-entropy-only | 0.764 | 76 |
| High-inconsistency-only | 0.797 | 72 |

Both subset AUROCs exceed the 0.6 threshold.

### 5.4 Summary of Results

| Hypothesis | Criterion | Threshold | Result | Status |
|------------|-----------|-----------|--------|--------|
| Orthogonality | Pearson r | < 0.3 | 0.228 | PASS |
| Consistency effect | Cohen's d | > 0.2 | 1.068 | PASS |
| Discordant proportion | % | > 15% | 18.1% | PASS |
| Subset AUROC | AUROC | > 0.6 | 0.764, 0.797 | PASS |

---

## 6. Discussion

### 6.1 Key Findings

**Finding 1:** Orthogonality is confirmed. With approximately 5% shared variance (r = 0.228), entropy and consistency measure different phenomena.

**Finding 2:** Consistency shows large discriminative power. Cohen's d = 1.068 indicates approximately one standard deviation of separation between correct and incorrect responses.

**Finding 3:** Discordant cases exhibit complementary predictive value. On 18.1% of questions where methods disagree, each achieves AUROC > 0.75 on its winning subset.

### 6.2 Mechanistic Interpretation

The results suggest a dual-signal model of LLM uncertainty:

- **Entropy captures epistemic uncertainty:** When the model lacks knowledge, its next-token distribution becomes diffuse.
- **Consistency captures generation stability:** When knowledge is unstable or fabricated, repeated sampling produces divergent outputs.

### 6.3 Limitations

**Single model.** Experiments used only LLaMA-2-7B. Results may not generalize to other architectures or scales.

**Single benchmark.** TruthfulQA's adversarial design may inflate effect sizes compared to naturally-occurring hallucinations.

**Hybrid detector not tested.** While orthogonality and complementarity are demonstrated, a combined detector has not been built or evaluated.

**Fixed parameters.** N=5 samples and temperature=1.0 were used without ablation of alternatives.

### 6.4 Scope Conditions

| Condition | Results Hold | Results May Not Hold |
|-----------|-------------|---------------------|
| Model family | Decoder-only LLMs (LLaMA-2) | Encoder-decoder, other families |
| Model scale | 7B parameters | <1B or >70B parameters |
| QA type | Closed-book factuality QA | Open-domain generation, reasoning |
| Language | English | Non-English |

---

## 7. Conclusion

This work conducted a systematic comparison of entropy-based and consistency-based uncertainty quantification for LLM hallucination detection on TruthfulQA with LLaMA-2-7B.

The main findings are:

1. **Orthogonality:** Entropy and consistency share only 5.2% of variance (r = 0.228).

2. **Large consistency effect:** Cohen's d = 1.068 distinguishes correct from incorrect responses.

3. **Complementarity:** 18.1% of questions exhibit method disagreement, with each method achieving AUROC > 0.75 on its winning subset.

These results suggest that entropy and consistency capture different aspects of model uncertainty, providing a foundation for multi-signal hallucination detection approaches. Future work includes testing on additional models and benchmarks, evaluating hybrid detectors that combine both signals, and ablating consistency parameters (N, temperature).

---

## References

- Chen et al. (2024). Contrastive Decoding Improves Reasoning in Large Language Models.
- Dietterich (2000). Ensemble Methods in Machine Learning.
- Guo et al. (2017). On Calibration of Modern Neural Networks. ICML.
- Kadavath et al. (2022). Language Models (Mostly) Know What They Know.
- Kuhn et al. (2023). Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation in Natural Language Generation. ICLR.
- Lakshminarayanan et al. (2017). Simple and Scalable Predictive Uncertainty Estimation using Deep Ensembles. NeurIPS.
- Lin et al. (2022). TruthfulQA: Measuring How Models Mimic Human Falsehoods. ACL.
- Malinin & Gales (2018). Predictive Uncertainty Estimation via Prior Networks. NeurIPS.
- Manakul et al. (2023). SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models. EMNLP.
- Touvron et al. (2023). Llama 2: Open Foundation and Fine-Tuned Chat Models.
- Wang et al. (2023). Self-Consistency Improves Chain of Thought Reasoning in Language Models. ICLR.
- Xiong et al. (2024). Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs. ICLR.
- Zhang et al. (2020). BERTScore: Evaluating Text Generation with BERT. ICLR.
