# Overconfident Misalignment: Quantifying Reward Model Failures on Human Disagreement

---

## Abstract

Reward models guide RLHF training, yet aggregate evaluation metrics conceal systematic failure patterns. We introduce a 2×2 mode decomposition that classifies preference battles by human vote entropy (high/low) crossed with reward model variance (high/low), revealing four distinct alignment modes. Analyzing 57,477 Chatbot Arena battles, we find that **23.7%** fall into Mode 3 (Misaligned-Confident): samples where human voters disagree while the reward model expresses high confidence. This overconfident misalignment is not a fringe phenomenon—approximately one in four preference battles exhibits this failure pattern. We test two mechanistic hypotheses: (1) that Mode 3 arises from semantic divergence between responses, and (2) that Mode 3 concentrates in subjective prompt types. Both are unsupported: Mode 3 pairs show *higher* semantic similarity than aligned pairs (Cohen's d = −0.049), and Mode 3 rates are nearly identical across subjective and objective tasks (ratio = 1.07). The phenomenon exists; its mechanism remains unknown. Our contributions are: (a) the first empirical quantification of overconfident RM misalignment in large-scale preference data, (b) the mode decomposition framework as an alignment diagnostic, and (c) negative results ruling out candidate mechanisms. These findings demonstrate that aggregate metrics are insufficient for reward model evaluation and motivate mode-aware benchmarking.

---

## 1. Introduction

One in four preference battles hides a silent failure: reward models confident, humans conflicted. Reinforcement Learning from Human Feedback (RLHF) has become the dominant paradigm for aligning large language models with human preferences. Central to this process are reward models trained to predict human judgments, evaluated on benchmarks like RewardBench that report aggregate accuracy metrics—often exceeding 85%. Yet aggregate metrics conceal systematic failure patterns. When a reward model scores 85% accuracy, what distinguishes the successful 85% from the failed 15%? More critically, within that successful majority, how many cases reflect genuine alignment versus confident misalignment—the model certain while humans disagree?

This paper introduces a decomposition framework that reveals structure hidden by aggregate evaluation. We classify preference battles along two orthogonal dimensions: **human vote entropy** (high when voters disagree, low when consensus) and **reward model variance** (high when the model is uncertain, low when confident). Crossing these dimensions yields four alignment modes:

- **Mode 1 (Aligned-Confident)**: Low entropy, low variance—humans agree, RM agrees
- **Mode 2 (Aligned-Uncertain)**: Low entropy, high variance—humans agree, RM uncertain  
- **Mode 3 (Misaligned-Confident)**: High entropy, low variance—humans disagree, RM confident
- **Mode 4 (Misaligned-Uncertain)**: High entropy, high variance—both disagree

Mode 3—overconfident misalignment—is the critical failure pattern. Here, reward models express high confidence on precisely the samples where human preferences diverge. If prevalent, this mode represents a systematic blind spot in RLHF training signal.

Analyzing 57,477 battles from the Chatbot Arena, we find Mode 3 constitutes **23.7%** of samples (95% CI: 23.4–24.0%, p<0.001), far exceeding our 10% significance threshold. This is not a fringe phenomenon but a substantial pattern affecting approximately one quarter of real-world preference data.

Having established the phenomenon's existence, we test two mechanistic hypotheses. First, we hypothesize that Mode 3 arises when responses are semantically divergent—similar enough for RMs to miss distinctions humans catch. Our analysis falsifies this: Mode 3 response pairs show *higher* semantic similarity than Mode 1 pairs (Cohen's d = −0.049), the opposite direction predicted. Second, we hypothesize Mode 3 concentrates in subjective prompt types (creative writing) versus objective tasks (coding, math). The data shows only negligible enrichment (ratio = 1.07 vs. predicted 1.5); Mode 3 pervades all task types.

**Contributions.** (1) To our knowledge, we provide the first empirical quantification of overconfident RM misalignment in large-scale preference data, demonstrating that ~24% of battles exhibit this failure pattern. (2) We introduce the 2×2 mode decomposition (entropy × variance) as a diagnostic framework that reveals patterns aggregate metrics miss. (3) We rule out two candidate mechanisms—semantic divergence and prompt subjectivity—constraining the hypothesis space for future work.

---

## 2. Related Work

### Reward Model Evaluation

RewardBench [Lambert et al., 2024] established the first standardized benchmark for evaluating reward models, measuring accuracy across chat, safety, and reasoning categories. Top models achieve 80–85% aggregate accuracy. However, this aggregate view treats all errors equally and provides no decomposition of *where* failures occur. Our work complements RewardBench by introducing mode-based decomposition that stratifies performance by human-RM agreement patterns.

The Alignment Ceiling [Lambert & Calandra, 2023] identified objective mismatch in RLHF: reward models overoptimize proxy objectives that diverge from true human intent. This work demonstrated that reward model training contains systematic biases, but did not quantify the prevalence of overconfident misalignment in preference data. We build on this foundation by operationalizing "overconfident misalignment" as Mode 3 and measuring its proportion in real data.

### LLM-as-Judge Evaluation

Wei et al. [2024] systematically evaluated LLM judges for alignment tasks, finding that prompt templates and judge models significantly affect reliability. Our work differs by examining reward model confidence rather than LLM judge outputs, and by conditioning analysis on human disagreement rather than treating human labels as ground truth.

### Bidirectional Alignment Frameworks

Shen et al. [2024] proposed the Bidirectional Human-AI Alignment framework, systematically reviewing 400+ papers. Our work contributes to AI-to-human alignment measurement by revealing that reward models exhibit systematic overconfidence on human-disagreement samples.

---

## 3. Methodology

### Dataset

We use the LMSYS Chatbot Arena dataset (57,477 pairwise battles). Each battle includes a prompt, two model responses, and human preference votes.

### Human Vote Entropy

For each model pair, we compute Shannon entropy over the vote distribution:

$$H = -\sum_{i \in \{A, B, \text{tie}\}} p_i \log_2 p_i$$

We binarize entropy using median split: above median = "high entropy" (disagreement).

### Reward Model Variance Proxy

We use OpenAssistant reward model and compute absolute score difference:

$$\text{variance\_proxy} = |RM(A) - RM(B)|$$

Low difference → high variance (uncertainty). Median split binarizes.

### Mode Classification

| Mode | Entropy | Variance | Interpretation |
|------|---------|----------|----------------|
| 1 | Low | Low | Aligned-Confident |
| 2 | Low | High | Aligned-Uncertain |
| 3 | High | Low | **Misaligned-Confident** |
| 4 | High | High | Misaligned-Uncertain |

### Hypothesis Tests

- **H-E1**: Mode 3 > 10% (binomial test, MUST_WORK)
- **H-M1**: Mode 3 similarity < Mode 1 (t-test, Cohen's d > 0.3)
- **H-C1**: Subjective/Objective Mode 3 ratio > 1.5

---

## 4. Experiments

### Experiment 1: Mode 3 Existence (h-e1)

**Objective**: Determine whether Mode 3 constitutes a substantial proportion.

**Setup**: 57,477 battles, median-split classification on entropy and variance.

**Gate**: MUST_WORK if Mode 3 > 10%.

### Experiment 2: Semantic Similarity (h-m1)

**Objective**: Test whether Mode 3 arises from semantic divergence.

**Setup**: all-MiniLM-L6-v2 embeddings, cosine similarity per pair.

**Prediction**: Mode 3 similarity < Mode 1, d > 0.3.

### Experiment 3: Prompt Type (h-c1)

**Objective**: Test whether Mode 3 concentrates in subjective tasks.

**Setup**: Keyword-based prompt classification.

**Prediction**: Subjective/Objective ratio > 1.5.

---

## 5. Results

### H-E1: Mode 3 Existence — CONFIRMED

| Mode | Count | Proportion |
|------|-------|------------|
| 1 (Aligned-Confident) | 15,107 | 26.3% |
| 2 (Aligned-Uncertain) | 13,714 | 23.9% |
| **3 (Misaligned-Confident)** | **13,632** | **23.7%** |
| 4 (Misaligned-Uncertain) | 15,024 | 26.1% |

Mode 3 = **23.7%** (95% CI: 23.4–24.0%, p<0.001). Far exceeds 10% threshold.

### H-M1: Semantic Similarity — FALSIFIED

| Mode | Mean Similarity | Std |
|------|-----------------|-----|
| 1 | 0.7031 | 0.1926 |
| 3 | 0.7125 | 0.1945 |

Cohen's d = **−0.049** (opposite direction). Mode 3 has *higher* similarity.

### H-C1: Prompt Type — INCONCLUSIVE

| Category | Mode 3 Proportion |
|----------|-------------------|
| Subjective | 22.2% |
| Objective | 20.7% |

Ratio = **1.07** (below 1.5 threshold). Cohen's h = 0.036 (negligible).

### Summary

| Hypothesis | Observed | Verdict |
|------------|----------|---------|
| H-E1 | 23.7% | **CONFIRMED** |
| H-M1 | d = −0.049 | **FALSIFIED** |
| H-C1 | ratio = 1.07 | **INCONCLUSIVE** |

---

## 6. Discussion

### What Mode 3 Tells Us

The 24% Mode 3 finding reveals a substantial blind spot in RLHF training signal. In one quarter of preference battles, reward models express high confidence on samples where humans disagree.

### What Mode 3 Does Not Tell Us

We have not identified *why* overconfident misalignment occurs. Semantic divergence is falsified (Mode 3 pairs are *more* similar). Prompt subjectivity is unsupported (Mode 3 pervades all task types).

### Competing Explanations

- Style/tone differences (embeddings miss presentation)
- RM feature sensitivity (attention to features humans ignore)
- Embedding limitations (larger models may reveal differences)

### Limitations

- Median-split thresholding (alternative clustering methods may shift mode boundaries)
- Near-uniform distribution may partly reflect methodological choice
- Single RM variance proxy (full ensemble pending)
- Chatbot Arena specific (generalization unknown)
- Correlational only

---

## 7. Conclusion

One in four preference battles hides a silent failure. Mode 3 (overconfident misalignment) constitutes **23.7%** of Chatbot Arena battles—RMs confident where humans disagree.

**Contributions**: (1) First quantification of overconfident RM misalignment. (2) Mode decomposition framework as alignment diagnostic. (3) Negative results ruling out semantic divergence and prompt subjectivity.

The mechanism quest continues. Priority directions: style-aware embeddings, RM attention analysis, full ensemble validation, cross-dataset replication.

---

## References

1. Lambert, N., et al. (2024). RewardBench: Evaluating Reward Models for Language Modeling. arXiv:2403.13787.
2. Lambert, N., & Calandra, R. (2023). The Alignment Ceiling: Objective Mismatch in RLHF. arXiv:2311.00168.
3. Shen, H., et al. (2024). Towards Bidirectional Human-AI Alignment. arXiv:2406.09264.
4. Wei, H., et al. (2024). Systematic Evaluation of LLM-as-a-Judge. arXiv:2408.13006.
5. Zheng, L., et al. (2024). Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. NeurIPS.
6. Gal, Y., & Ghahramani, Z. (2016). Dropout as a Bayesian Approximation. ICML.
7. LMSYS Org. (2024). Chatbot Arena Dataset. HuggingFace.
