# Overconfident Misalignment: Quantifying Reward Model Failures on Human Disagreement

## Abstract

Reward models guide RLHF training, yet aggregate evaluation metrics conceal systematic failure patterns. This paper introduces a 2×2 mode decomposition that classifies preference battles by human vote entropy (high/low) crossed with reward model variance (high/low), yielding four alignment modes. Analysis of 57,477 Chatbot Arena battles reveals that 23.7% fall into Mode 3 (Misaligned-Confident): samples where human voters disagree while the reward model expresses high confidence (95% CI: 23.4–24.0%, p < 0.001 against a 10% threshold). Two mechanistic hypotheses were tested: (1) that Mode 3 arises from semantic divergence between responses, and (2) that Mode 3 concentrates in subjective prompt types. Both hypotheses are unsupported: Mode 3 pairs exhibit higher semantic similarity than aligned pairs (Cohen's d = −0.049, opposite to prediction), and Mode 3 rates are nearly identical across subjective and objective tasks (ratio = 1.07, below the 1.5 threshold). The contributions are: (a) the first empirical quantification of overconfident reward model misalignment in large-scale preference data, (b) a mode decomposition framework as an alignment diagnostic, and (c) negative results ruling out two candidate mechanisms.

## 1. Introduction

Reinforcement Learning from Human Feedback (RLHF) has become the dominant paradigm for aligning large language models with human preferences. Reward models trained to predict human judgments are evaluated on benchmarks such as RewardBench, which report aggregate accuracy metrics often exceeding 85%. However, aggregate metrics do not reveal the structure of failures. When a reward model scores 85% accuracy, what distinguishes the successful 85% from the failed 15%? More critically, within the successful majority, how many cases reflect genuine alignment versus confident misalignment—the model certain while humans disagree?

This paper introduces a decomposition framework that reveals patterns hidden by aggregate evaluation. Preference battles are classified along two orthogonal dimensions: human vote entropy (high when voters disagree, low when consensus) and reward model variance (high when uncertain, low when confident). Crossing these dimensions yields four alignment modes:

- **Mode 1 (Aligned-Confident)**: Low entropy, low variance—humans agree, reward model agrees
- **Mode 2 (Aligned-Uncertain)**: Low entropy, high variance—humans agree, reward model uncertain
- **Mode 3 (Misaligned-Confident)**: High entropy, low variance—humans disagree, reward model confident
- **Mode 4 (Misaligned-Uncertain)**: High entropy, high variance—both uncertain

Mode 3 is the critical failure pattern. Reward models express high confidence on samples where human preferences diverge. If prevalent, this mode represents a systematic blind spot in RLHF training signal.

Analysis of 57,477 battles from the LMSYS Chatbot Arena finds Mode 3 constitutes 23.7% of samples (95% CI: 23.4–24.0%, p < 0.001 against a 10% threshold). This is not a fringe phenomenon but a substantial pattern affecting approximately one quarter of preference data.

Two mechanistic hypotheses were tested. First, the hypothesis that Mode 3 arises when responses are semantically divergent. The data falsifies this: Mode 3 response pairs show higher semantic similarity than Mode 1 pairs (Cohen's d = −0.049), the opposite direction predicted. Second, the hypothesis that Mode 3 concentrates in subjective prompt types. The data shows negligible enrichment (ratio = 1.07 vs. predicted 1.5); Mode 3 pervades all task types.

**Contributions.** (1) The first empirical quantification of overconfident reward model misalignment in large-scale preference data, demonstrating that approximately 24% of battles exhibit this failure pattern. (2) A 2×2 mode decomposition (entropy × variance) as a diagnostic framework revealing patterns aggregate metrics miss. (3) Negative results ruling out semantic divergence and prompt subjectivity as explanatory mechanisms.

## 2. Related Work

### Reward Model Evaluation

RewardBench (Lambert et al., 2024) established the first standardized benchmark for evaluating reward models, measuring accuracy across chat, safety, and reasoning categories. Top models achieve 80–85% aggregate accuracy. This aggregate view treats all errors equally and provides no decomposition of where failures occur. The present work complements RewardBench by introducing mode-based decomposition that stratifies performance by human-RM agreement patterns.

The Alignment Ceiling (Lambert & Calandra, 2023) identified objective mismatch in RLHF: reward models overoptimize proxy objectives that diverge from true human intent. This work demonstrated that reward model training contains systematic biases but did not quantify the prevalence of overconfident misalignment in preference data. The present work operationalizes "overconfident misalignment" as Mode 3 and measures its proportion.

### LLM-as-Judge Evaluation

Wei et al. (2024) systematically evaluated LLM judges for alignment tasks, finding that prompt templates and judge models significantly affect reliability. The present work differs by examining reward model confidence rather than LLM judge outputs, and by conditioning analysis on human disagreement rather than treating human labels as ground truth.

### Bidirectional Alignment Frameworks

Shen et al. (2024) proposed the Bidirectional Human-AI Alignment framework, systematically reviewing over 400 papers spanning ML, HCI, and NLP. The present work contributes to AI-to-human alignment measurement by revealing that reward models exhibit systematic overconfidence on human-disagreement samples.

## 3. Method

### 3.1 Dataset

The LMSYS Chatbot Arena dataset (57,477 pairwise battles) is used. Each battle includes a prompt, two model responses, and human preference votes aggregated at the model-pair level.

### 3.2 Human Vote Entropy

For each model pair, Shannon entropy is computed over the vote distribution:

$$H = -\sum_{i \in \{A, B, \text{tie}\}} p_i \log_2 p_i$$

Entropy is binarized using median split: above median indicates high entropy (disagreement).

### 3.3 Reward Model Variance Proxy

The OpenAssistant reward model is used. Variance is proxied by absolute score difference:

$$\text{variance\_proxy} = |RM(A) - RM(B)|$$

Low difference indicates high variance (uncertainty); high difference indicates low variance (confidence). Binarization uses median split.

Note: A single reward model is used as a proxy rather than a multi-model ensemble. Full validation with multiple models (OpenAssistant, PairRM, ArmoRM) remains pending.

### 3.4 Mode Classification

| Mode | Entropy | Variance | Interpretation |
|------|---------|----------|----------------|
| 1 | Low | Low | Aligned-Confident |
| 2 | Low | High | Aligned-Uncertain |
| 3 | High | Low | Misaligned-Confident |
| 4 | High | High | Misaligned-Uncertain |

### 3.5 Hypothesis Tests

Three hypotheses were tested:

- **H-E1 (Existence)**: Mode 3 > 10% of samples (one-sided binomial test)
- **H-M1 (Mechanism)**: Mode 3 semantic similarity < Mode 1 (Welch's t-test, Cohen's d > 0.3)
- **H-C1 (Condition)**: Subjective/Objective Mode 3 ratio > 1.5 (two-proportion z-test)

## 4. Experimental Setup

### 4.1 Experiment 1: Mode 3 Existence (H-E1)

**Objective**: Determine whether Mode 3 constitutes a substantial proportion of preference battles.

**Setup**: 57,477 battles processed. Entropy and variance computed per battle. Median-split classification applied to both dimensions.

**Success Criterion**: Mode 3 proportion statistically greater than 10% (p < 0.05).

### 4.2 Experiment 2: Semantic Similarity (H-M1)

**Objective**: Test whether Mode 3 arises from semantic divergence between response pairs.

**Setup**: Sentence embeddings computed using all-MiniLM-L6-v2. Cosine similarity calculated between response_a and response_b for each battle. Mode 1 (n = 15,107) and Mode 3 (n = 13,632) compared.

**Prediction**: Mode 3 similarity lower than Mode 1, Cohen's d > 0.3.

### 4.3 Experiment 3: Prompt Type (H-C1)

**Objective**: Test whether Mode 3 concentrates in subjective tasks.

**Setup**: Keyword-based prompt classification. Subjective keywords: "story", "creative", "write", "poem", "essay". Objective keywords: "code", "math", "calculate", "solve", "algorithm". Battles not matching either category (75%) excluded.

**Prediction**: Subjective/Objective Mode 3 ratio > 1.5.

## 5. Results

### 5.1 H-E1: Mode 3 Existence — CONFIRMED

| Mode | Count | Proportion |
|------|-------|------------|
| 1 (Aligned-Confident) | 15,107 | 26.3% |
| 2 (Aligned-Uncertain) | 13,714 | 23.9% |
| 3 (Misaligned-Confident) | 13,632 | 23.7% |
| 4 (Misaligned-Uncertain) | 15,024 | 26.1% |

Mode 3 proportion: 23.7% (95% CI: 23.4–24.0%, p < 0.001 against H₀: p ≤ 0.10).

The 95% confidence interval lower bound (23.4%) substantially exceeds the 10% threshold. The distribution across modes is near-uniform (23.7%–26.3%), suggesting entropy and variance are approximately orthogonal dimensions in this dataset.

### 5.2 H-M1: Semantic Similarity — FALSIFIED

| Mode | n | Mean Similarity | Std |
|------|---|-----------------|-----|
| 1 (Aligned-Confident) | 15,107 | 0.7031 | 0.1926 |
| 3 (Misaligned-Confident) | 13,632 | 0.7125 | 0.1945 |

Cohen's d = −0.049 (95% CI: −0.073 to −0.026)
Welch's t = −4.12, p = 3.79 × 10⁻⁵

The effect is statistically significant but negligible in magnitude (|d| < 0.1) and in the opposite direction predicted. Mode 3 response pairs exhibit slightly higher semantic similarity than Mode 1 pairs, contradicting the hypothesis that misalignment arises from semantic divergence.

### 5.3 H-C1: Prompt Type — INCONCLUSIVE

| Category | Mode 3 Count | Total | Proportion |
|----------|--------------|-------|------------|
| Subjective | 2,184 | 9,839 | 22.2% |
| Objective | 901 | 4,349 | 20.7% |

Ratio = 1.07 (95% CI: 1.00–1.15)
Cohen's h = 0.036, z = 1.97, p = 0.024

The direction is as predicted (subjective > objective) but the magnitude is far below the 1.5 threshold. The effect size is negligible (h = 0.036). Mode 3 is pervasive across prompt types, not concentrated in subjective tasks.

Note: 75% of battles were classified as ambiguous and excluded. Results reflect only the 25% with clear keyword matches.

### 5.4 Summary

| Hypothesis | Prediction | Observed | Verdict |
|------------|------------|----------|---------|
| H-E1 | Mode 3 > 10% | 23.7% | **CONFIRMED** |
| H-M1 | d > 0.3 | d = −0.049 | **FALSIFIED** |
| H-C1 | ratio > 1.5 | ratio = 1.07 | **INCONCLUSIVE** |

## 6. Discussion

### 6.1 What Mode 3 Reveals

The finding that 24% of preference battles exhibit overconfident misalignment has implications for RLHF training. In approximately one quarter of cases, reward models express high confidence on samples where humans disagree. These samples contribute training signal as if they were unambiguous, potentially reinforcing arbitrary preferences.

### 6.2 What Mode 3 Does Not Reveal

The mechanism driving overconfident misalignment remains unknown. Semantic divergence is falsified: Mode 3 pairs are slightly more similar than Mode 1 pairs. Prompt subjectivity is unsupported: Mode 3 pervades all task types with negligible enrichment in subjective tasks.

### 6.3 Competing Explanations

Several alternative mechanisms warrant investigation:

- **Style/tone differences**: Response pairs may be semantically similar but differ in presentation style, formatting, or tone. Sentence embeddings may not capture these distinctions.
- **Feature sensitivity mismatch**: Reward models may attend to features (length, structure, specific phrases) that humans weight differently.
- **Embedding model limitations**: all-MiniLM-L6-v2 is a lightweight embedding model. Larger or style-aware embeddings may reveal distinctions.

### 6.4 Limitations

**Methodological limitations**:
1. Single reward model used as variance proxy. Full multi-model ensemble (OpenAssistant + PairRM + ArmoRM) validation is pending.
2. Human entropy aggregated at model-pair level, not per-battle.
3. Median-split thresholding is arbitrary; alternative clustering methods may produce different mode boundaries.
4. Embedding model (all-MiniLM-L6-v2) may miss stylistic and tonal features.
5. Keyword-based prompt classification excluded 75% of battles as ambiguous.

**Scope limitations**:
1. Results are specific to Chatbot Arena. Generalization to other preference datasets (HH-RLHF, SHP, Anthropic HH) is unknown.
2. Analysis is correlational. No causal claims can be made about whether reducing Mode 3 would improve downstream alignment.

**Threats to validity**:
- The near-uniform mode distribution (23.7%–26.3%) may partly reflect the methodological choice of median splits rather than genuine structure in the data.

## 7. Conclusion

Analysis of 57,477 Chatbot Arena battles reveals that Mode 3 (overconfident misalignment) constitutes 23.7% of samples: reward models confident where humans disagree. Two candidate mechanisms—semantic divergence and prompt subjectivity—are not supported by the data.

**Contributions**: (1) First quantification of overconfident reward model misalignment at scale. (2) Mode decomposition framework (entropy × variance) as alignment diagnostic. (3) Negative results constraining the hypothesis space for future mechanistic investigation.

**Future work**: Full ensemble validation with multiple reward models; style-aware embedding analysis; cross-dataset replication; human annotation studies to identify features driving disagreement.

## References

1. Lambert, N., Pyatkin, V., Morrison, J., et al. (2024). RewardBench: Evaluating Reward Models for Language Modeling. arXiv:2403.13787.

2. Lambert, N., & Calandra, R. (2023). The Alignment Ceiling: Objective Mismatch in Reinforcement Learning from Human Feedback. arXiv:2311.00168.

3. Shen, H., et al. (2024). Towards Bidirectional Human-AI Alignment: A Systematic Review for Clarifications, Framework, and Future Directions. arXiv:2406.09264.

4. Wei, H., et al. (2024). Systematic Evaluation of LLM-as-a-Judge in LLM Alignment Tasks. arXiv:2408.13006.

5. Zheng, L., Chiang, W.-L., Sheng, Y., et al. (2024). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. NeurIPS.

6. Gal, Y., & Ghahramani, Z. (2016). Dropout as a Bayesian Approximation: Representing Model Uncertainty in Deep Learning. ICML.

7. LMSYS Org. (2024). LMSYS Chatbot Arena Dataset. HuggingFace. https://huggingface.co/datasets/lmsys/lmsys-arena-human-preference-55k

8. Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. arXiv:1908.10084.
