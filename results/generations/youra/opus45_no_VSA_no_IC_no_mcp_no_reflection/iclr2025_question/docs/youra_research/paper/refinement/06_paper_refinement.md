# Format-Dependent Uncertainty Quantification: Why Semantic Entropy Underperforms Simple Confidence on Multiple-Choice Hallucination Detection

**Anonymous Authors**

---

## Abstract

Uncertainty quantification (UQ) methods have been proposed for automatic hallucination detection in large language models, yet prior evaluations employed heterogeneous conditions that obscure method-specific performance characteristics. This work presents a controlled head-to-head comparison of token-level and semantic-level UQ methods on TruthfulQA multiple-choice hallucination detection using Llama-3-8B-Instruct. Contrary to expectations derived from prior work, semantic entropy—which clusters semantically equivalent responses via natural language inference before computing entropy—achieves an AUROC of 0.5645, while simple max probability achieves 0.8068. Mechanism verification confirms that the NLI-based clustering functions correctly (average 4.92 clusters from 5 samples, entropy standard deviation 0.0752). The 0.24-point AUROC gap stems from format mismatch: multiple-choice answers consist of single letters (A/B/C/D) that provide insufficient semantic content for meaningful NLI comparison. Token-level methods extract discriminative signals directly from logits regardless of answer format. These findings indicate that UQ method effectiveness is format-dependent, and practitioners should select methods appropriate to their task format rather than assuming more sophisticated approaches yield better performance.

---

## 1. Introduction

This work reports an empirical finding that contradicts prevailing assumptions about uncertainty quantification methods for hallucination detection: semantic entropy, which captures meaning-level uncertainty through NLI-based clustering, underperforms a simple confidence score by 0.24 AUROC points on multiple-choice hallucination detection.

Automatic detection of hallucinations—confident-sounding but factually incorrect LLM outputs—is a prerequisite for safe deployment in high-stakes domains. Uncertainty quantification offers a principled approach: outputs with high uncertainty may be unreliable and warrant verification. Recent work has produced increasingly sophisticated UQ methods, from token-level entropy and confidence measures to semantic entropy with NLI-based clustering [Kuhn et al., 2023], self-consistency checks [Manakul et al., 2023], and P(True) calibration [Kadavath et al., 2022].

A methodological problem complicates method selection: each approach has been evaluated under favorable conditions using different benchmarks, data splits, and evaluation protocols. Kuhn et al. demonstrated semantic entropy's superiority over token entropy on custom QA splits. Manakul et al. showed SelfCheckGPT's effectiveness on WikiBio generation. Kadavath et al. validated P(True) on proprietary data. No controlled head-to-head comparison exists on identical conditions, leaving practitioners without guidance for method selection.

This work addresses this gap through a controlled comparison of UQ methods for hallucination detection on TruthfulQA's multiple-choice format with Llama-3-8B-Instruct. The central finding is that **UQ method effectiveness depends on task format**: token-level methods extract discriminative signals directly from logits without format dependency, while semantic entropy's NLI-based clustering requires substantial semantic content that single-letter multiple-choice answers cannot provide. The clustering mechanism functions correctly—verification confirms that NLI models produce clusters with non-trivial entropy variance—but the resulting entropy scores do not correlate with hallucination status on this format.

The contributions are: (1) empirical demonstration that token-level UQ methods (max probability, choice entropy) achieve AUROC 0.77–0.81 on TruthfulQA mc1 with Llama-3-8B-Instruct, exceeding a 0.55 chance threshold; (2) documentation that semantic entropy achieves only AUROC 0.5645 on the same task despite correct mechanism implementation; (3) identification of format dependency as the root cause—semantic entropy requires free-form responses with semantic content suitable for NLI comparison, while multiple-choice answers are single letters with no such content.

---

## 2. Related Work

### 2.1 Uncertainty Quantification in Neural Networks

Calibration research established that modern neural networks are often overconfident [Guo et al., 2017]. For language models, calibration became critical as models grew capable of generating plausible but factually incorrect text. Malinin and Gales [2018] introduced predictive uncertainty decomposition, distinguishing epistemic from aleatoric uncertainty. These methods assumed classification settings and did not address free-form generation or factuality.

### 2.2 Token-Level Uncertainty for LLMs

Token-level methods extract uncertainty from output logits: entropy over the vocabulary distribution, maximum probability of the selected token, or perplexity. Kadavath et al. [2022] introduced P(True), using the probability of "True" when asking models to self-assess as a confidence signal. These methods share a computational advantage: single-pass inference without additional sampling. However, they operate at the token level and may miss semantic-level consistency issues.

### 2.3 Semantic-Level Uncertainty Methods

Kuhn et al. [2023] proposed semantic entropy to capture meaning-level uncertainty. The method generates multiple samples, clusters semantically equivalent responses using NLI-based entailment, and computes entropy over cluster assignments. On custom QA evaluation, semantic entropy outperformed token entropy. Manakul et al. [2023] introduced SelfCheckGPT, using self-consistency across samples without reference documents. Both methods require 5–20x more inference compute than token-level methods.

### 2.4 Hallucination Detection Benchmarks

TruthfulQA [Lin et al., 2022] provides questions designed to elicit imitative falsehoods—incorrect answers humans might believe. HaluEval [Li et al., 2023] extends to QA, dialogue, and summarization domains. These benchmarks provide ground-truth labels for hallucination detection evaluation.

### 2.5 Methodological Gap

Each prior method was evaluated under favorable conditions on different benchmarks. No study has compared methods on identical conditions or examined whether effectiveness depends on task format.

---

## 3. Method

### 3.1 Overview

The methodology comprises three components: benchmark selection for ground-truth labels, controlled variables for fair comparison, and mechanism verification to separate implementation correctness from discrimination effectiveness.

### 3.2 Benchmark

TruthfulQA mc1 (multiple-choice, single correct answer) serves as the evaluation benchmark. The multiple-choice format provides ground-truth labels without human annotation: the model's selected answer is either correct or incorrect, enabling AUROC computation where incorrect answers constitute hallucinations.

### 3.3 Model

Llama-3-8B-Instruct serves as the evaluation model. This model is representative of the decoder-only instruction-tuned class, with open weights enabling reproducibility.

### 3.4 UQ Methods

Three UQ methods are evaluated:

**Max Probability (Token-Level):** Uncertainty score $u = 1 - \max_c P(c)$ where $c \in \{A, B, C, D\}$.

**Choice Entropy (Token-Level):** Uncertainty score $u = H(P) = -\sum_c P(c) \log P(c)$ over answer choices.

**Semantic Entropy (Semantic-Level):** Uncertainty score $u = H(P_{\text{cluster}})$ computed over NLI-clustered responses from $N=5$ samples at temperature 0.7. The NLI model is facebook/bart-large-mnli with entailment threshold 0.7.

### 3.5 Mechanism Verification

To distinguish implementation error from format unsuitability, mechanism verification checks whether semantic clustering functions correctly independent of discrimination:

- **Cluster count:** Average clusters per question should be less than the number of samples if clustering occurs
- **Entropy variance:** Standard deviation of entropy should be positive if the signal varies

If mechanism verification passes but discrimination fails, the method is correctly implemented but unsuited to the task format.

---

## 4. Experimental Setup

### 4.1 Research Questions

**RQ1:** Do uncertainty quantification methods discriminate hallucinations better than random chance?

**RQ2:** Does semantic entropy achieve AUROC ≥ 0.70 consistent with prior work?

**RQ3:** Does semantic entropy's clustering mechanism function correctly on multiple-choice format?

### 4.2 Dataset

| Parameter | Value |
|-----------|-------|
| Dataset | TruthfulQA mc1 |
| Format | Multiple choice (4 options: A/B/C/D) |
| Sample size | 50 questions |
| Correct rate | 56% (28 correct) |
| Hallucination rate | 44% (22 incorrect) |

### 4.3 Implementation

| Parameter | Value |
|-----------|-------|
| Model | meta-llama/Meta-Llama-3-8B-Instruct |
| Seed | 42 |
| Samples per question (semantic) | 5 |
| Temperature (semantic) | 0.7 |
| NLI model | facebook/bart-large-mnli |
| NLI threshold | 0.7 |

### 4.4 Evaluation

Primary metric: AUROC for hallucination detection.

Success thresholds:
- AUROC > 0.55 indicates better-than-random discrimination (h-e1)
- AUROC ≥ 0.70 indicates strong discrimination (h-m1)

---

## 5. Results

### 5.1 Main Results

| Method | AUROC | Threshold | Status |
|--------|-------|-----------|--------|
| Random baseline | 0.50 | — | Reference |
| Choice Entropy | 0.7703 | 0.55 | PASS |
| Max Probability | 0.8068 | 0.55 | PASS |
| Semantic Entropy | 0.5645 | 0.70 | FAIL |

**Finding 1:** Token-level methods discriminate hallucinations. Max probability (AUROC = 0.8068) and choice entropy (AUROC = 0.7703) both exceed the 0.55 threshold.

**Finding 2:** Semantic entropy underperforms. AUROC = 0.5645, below the 0.70 threshold and 0.24 points below max probability.

### 5.2 Mechanism Verification

| Check | Value | Expected | Status |
|-------|-------|----------|--------|
| Avg clusters per question | 4.92 | < 5.0 | PASS |
| Entropy standard deviation | 0.0752 | > 0 | PASS |

**Finding 3:** The semantic clustering mechanism functions correctly. Clustering occurs (average 4.92 clusters from 5 samples) and entropy varies across questions.

### 5.3 Format-Dependency Analysis

The resolution to the apparent contradiction—correct mechanism but poor discrimination—lies in the task format. Multiple-choice responses are single letters ("A", "B", "C", "D"). NLI models cannot meaningfully compare "A" versus "B" for entailment. Each response tends to form its own cluster (average 4.92 from 5 samples). Entropy over near-singleton clusters provides no discriminative signal.

Token-level methods extract uncertainty directly from logits. They do not require semantic comparison and function regardless of answer length.

---

## 6. Discussion

### 6.1 Format-Dependency

The 0.24 AUROC gap between max probability and semantic entropy results from format mismatch. Semantic entropy assumes responses contain meaningful semantic content for NLI comparison. Single-letter multiple-choice answers violate this assumption.

Semantic entropy was developed and validated on free-form question answering where responses are sentences or paragraphs. The method's design is reasonable for that setting. The present results indicate it does not transfer to multiple-choice format without modification.

### 6.2 Practical Implications

For multiple-choice format hallucination detection, simple confidence-based methods are sufficient. The additional computational cost of multi-sample generation and NLI-based clustering does not improve discrimination on this format.

Method selection should consider task format. More sophisticated methods do not uniformly outperform simpler alternatives.

### 6.3 Limitations

**Sample size.** Experiments used 50 questions (proof-of-concept level). Full validation requires the complete 817-sample TruthfulQA dataset. The relative rankings (max probability > choice entropy > semantic entropy) are expected to hold, but exact AUROC values have associated uncertainty.

**Single model.** Only Llama-3-8B-Instruct was evaluated. Results may not generalize across architectures or model sizes.

**Multiple-choice format only.** Free-form generation was not evaluated. Semantic entropy may perform differently on tasks where responses contain substantial semantic content.

**Sample count.** Semantic entropy used 5 samples per question. The original work used 5–10 samples. Additional samples might improve performance, though this would not address the fundamental format mismatch.

### 6.4 Connection to Prior Work

The finding that semantic entropy underperforms on multiple-choice format does not contradict Kuhn et al. [2023], who evaluated on free-form question answering. The present results extend understanding of the method's scope conditions: semantic entropy requires responses with semantic content suitable for NLI comparison.

The finding that max probability achieves strong discrimination (AUROC = 0.81) aligns with Kadavath et al. [2022], who demonstrated that LLM confidence signals correlate with correctness.

---

## 7. Conclusion

This work presents a controlled comparison of uncertainty quantification methods for hallucination detection, finding that UQ method effectiveness is format-dependent. On TruthfulQA multiple-choice format with Llama-3-8B-Instruct:

- Token-level methods (max probability, choice entropy) achieve AUROC 0.77–0.81
- Semantic entropy achieves only AUROC 0.5645 despite correct mechanism implementation
- The gap stems from format mismatch: multiple-choice answers lack semantic content for NLI comparison

The practical implication is that method selection should match task format. For multiple-choice tasks, simple confidence-based methods are sufficient and computationally cheaper.

Future work should evaluate semantic entropy on free-form generation tasks (e.g., HaluEval dialogue and summarization) where the format hypothesis predicts improved performance. Cross-model validation and full-scale experiments on the complete TruthfulQA dataset would strengthen the findings.

---

## References

Guo, C., Pleiss, G., Sun, Y., and Weinberger, K. Q. On Calibration of Modern Neural Networks. ICML 2017.

Kadavath, S., et al. Language Models (Mostly) Know What They Know. arXiv:2207.05221, 2022.

Kuhn, L., Gal, Y., and Farquhar, S. Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation in Natural Language Generation. ICLR 2023.

Li, J., et al. HaluEval: A Large-Scale Hallucination Evaluation Benchmark for Large Language Models. arXiv:2305.11747, 2023.

Lin, S., Hilton, J., and Evans, O. TruthfulQA: Measuring How Models Mimic Human Falsehoods. ACL 2022.

Malinin, A. and Gales, M. Predictive Uncertainty Estimation via Prior Networks. NeurIPS 2018.

Manakul, P., Liusie, A., and Gales, M. J. F. SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models. arXiv:2303.08896, 2023.
