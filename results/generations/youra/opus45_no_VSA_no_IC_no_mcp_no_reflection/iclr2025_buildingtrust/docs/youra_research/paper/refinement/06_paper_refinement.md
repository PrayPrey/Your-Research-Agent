# Benchmark Sensitivity in Hallucination Detection: A Matched-Budget Pilot Study

## Abstract

Uncertainty-based hallucination detection methods report strong performance in isolation, yet practitioners lack guidance on which method works for their specific task. This pilot study compares semantic entropy and self-consistency under matched computational budgets—same model, same sample count, same benchmarks. The key finding is benchmark sensitivity: semantic entropy achieves AUROC 0.551 on HaluEval but 0.289 on TruthfulQA under identical conditions, while self-consistency performs near random on both (AUROC 0.444–0.474). These results suggest that method performance depends on benchmark-specific factors, and published evaluations on different benchmarks may not be directly comparable. The pilot sample size (N=20 per dataset) limits statistical power; confidence intervals are wide and overlapping. This work establishes a controlled comparison framework and identifies benchmark-method alignment as a consideration for hallucination detection evaluation. Full-scale validation is required before drawing definitive conclusions.

## 1. Introduction

Uncertainty-based hallucination detection methods report strong results in isolation—semantic entropy achieves AUROC values in the range 0.75–0.85 on TruthfulQA according to Kuhn et al. (2023), and self-consistency reaches approximately 0.70–0.80 on WikiBio according to Manakul et al. (2023). However, these methods have been evaluated on different benchmarks with different sample counts and different models. This pilot study reveals that these methods can perform at random or below under different conditions: semantic entropy achieved AUROC 0.551 on HaluEval but only 0.289 on TruthfulQA in our experiments. This gap between published performance and observed behavior poses a challenge for practitioners selecting detection methods.

Large language models hallucinate confidently, generating plausible-sounding but factually incorrect outputs (Lin et al., 2022). Multiple uncertainty-based detection methods have emerged. Semantic entropy clusters generated responses by semantic equivalence via natural language inference (NLI), computing entropy over the cluster distribution (Kuhn et al., 2023). Self-consistency measures agreement across multiple generations using surface similarity metrics (Manakul et al., 2023). Contextual calibration adjusts confidence scores using content-free inputs (Zhao et al., 2021).

Each method has been evaluated on different benchmarks with different sample counts and different models. Semantic entropy reports AUROC on TruthfulQA using specific NLI models; SelfCheckGPT reports on WikiBio using BERTScore. No study, to our knowledge, compares these methods head-to-head on the same benchmarks under matched computational budgets. This leaves practitioners unable to make informed choices—published results are not directly comparable.

This pilot study reveals that hallucination detection method effectiveness may be benchmark-sensitive. Under identical conditions (N=10 samples per query, same model, same temperature), semantic entropy achieved AUROC 0.551 on HaluEval but only 0.289 on TruthfulQA—the latter worse than random, with uncertainty scores inverted relative to ground truth labels. Self-consistency performed near random on both datasets. This suggests that benchmark design may affect method evaluation.

This work makes the following contributions:

1. **Matched-Budget Evaluation Framework.** A pilot comparison protocol that tests semantic entropy and self-consistency under identical computational budgets (same sample count, model, and temperature) across multiple benchmarks.

2. **Benchmark Sensitivity Observation.** Empirical evidence that detection method performance varies across benchmarks in this pilot—semantic entropy shows marginal signal on HaluEval but inverted results on TruthfulQA.

3. **Methodological Observations.** Identification of labeling methodology and benchmark design as potential sources of evaluation inconsistency, providing directions for investigation.

## 2. Related Work

### Uncertainty Quantification for Language Models

Uncertainty estimation in neural networks has a rich history (Gal and Ghahramani, 2016), with recent adaptations for large language models. Semantic entropy (Kuhn et al., 2023) extends classical entropy-based uncertainty to account for semantic equivalence—responses that differ in surface form but convey the same meaning are clustered together before computing entropy. The method uses bidirectional NLI to determine semantic equivalence, then computes entropy over the cluster distribution. Higher entropy indicates greater uncertainty and potential hallucination. Follow-up work demonstrated semantic entropy's effectiveness on detecting confabulations in long-form generation (Farquhar et al., 2024).

However, semantic entropy has been evaluated primarily on TruthfulQA and related factual QA tasks. The reliance on NLI-based clustering raises questions about transfer to benchmarks with different hallucination definitions.

### Self-Consistency Methods

SelfCheckGPT (Manakul et al., 2023) measures surface-level agreement across multiple generations. The intuition is that factual knowledge, being reproducible, should yield consistent responses, while hallucinations vary. The method computes pairwise similarity (using BERTScore, n-gram overlap, or NLI-based comparison) and aggregates into a consistency score. SelfCheckGPT was evaluated on WikiBio hallucination detection.

The gap: SelfCheckGPT uses different benchmarks, different sample counts, and different base models than semantic entropy evaluations. Direct comparison of the two methods requires matching these variables.

### Confidence Calibration

Contextual calibration (Zhao et al., 2021) adjusts model confidence using content-free inputs to estimate inherent biases. Temperature scaling and Platt scaling (Guo et al., 2017) post-process confidence scores to improve calibration. While these methods primarily target classification tasks, they provide potential baselines for hallucination detection.

### Hallucination Benchmarks

TruthfulQA (Lin et al., 2022) evaluates model truthfulness on questions designed to elicit common misconceptions. The benchmark labels responses as truthful or not based on "Best Answer" matching. HaluEval (Li et al., 2023) provides hallucinated and correct response pairs across QA, summarization, and dialogue tasks, with explicit hallucination labels. These benchmarks encode different notions of "hallucination."

## 3. Method

We design a matched-budget evaluation framework that enables direct method comparison across benchmarks. The key design principle: hold computational budget constant while varying method and benchmark.

### Overview

We evaluate two sampling-based uncertainty methods—semantic entropy and self-consistency—under identical conditions:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Sample count (N) | 10 | Standard in both original papers |
| Temperature | 0.7 | Enables diverse sampling |
| Max tokens | 256 | Sufficient for QA responses |
| Model | Llama-3-8B-Instruct | Open-weight, reproducible |
| Seed | 42 | Single seed for pilot |
| NLI Model | DeBERTa-large-mnli | For semantic clustering |
| Similarity | BERTScore (roberta-large) | For self-consistency |

### Semantic Entropy

Semantic entropy quantifies uncertainty by clustering generated responses according to semantic equivalence, then computing entropy over the cluster distribution.

**Step 1: Generation.** For each query q, generate N=10 responses {r_1, ..., r_N} using temperature sampling.

**Step 2: Semantic Clustering.** Use DeBERTa-large-mnli to compute bidirectional NLI scores between response pairs. Responses r_i and r_j are considered semantically equivalent if both directions yield entailment probability above threshold τ=0.5.

**Step 3: Entropy Computation.** Let {C_1, ..., C_K} be the resulting clusters. The cluster probability distribution is p_k = |C_k|/N. Semantic entropy is H_SE = -Σ p_k log p_k.

Higher entropy indicates responses fall into many distinct semantic clusters, suggesting uncertainty.

### Self-Consistency

Self-consistency measures agreement across generated responses using surface-level similarity.

**Step 1: Generation.** Identical to semantic entropy—N=10 responses per query.

**Step 2: Pairwise Similarity.** Compute BERTScore F1 between all response pairs: S_ij = BERTScore-F1(r_i, r_j).

**Step 3: Consistency Score.** Self-consistency is the mean off-diagonal similarity: SC = (1/N(N-1)) Σ_{i≠j} S_ij.

Higher consistency indicates similar responses. For hallucination detection, we use 1 - SC as the uncertainty score.

### Evaluation Protocol

**Benchmarks.** TruthfulQA (817 questions total) and HaluEval-QA (10,000 samples total).

**Pilot Mode.** For pipeline validation, N=20 samples per dataset were used.

**Metrics.** Primary metric is AUROC with 95% confidence intervals via bootstrap resampling (1,000 iterations).

**Gate Criterion.** AUROC > 0.55 as threshold for determining whether a method shows above-chance performance on a benchmark.

## 4. Experimental Setup

**Research Questions:**
- RQ1: Do semantic entropy and self-consistency detect hallucinations above random on each benchmark?
- RQ2: Does method ranking differ across benchmarks?
- RQ3: Are observed differences statistically significant given the sample size?

**Datasets:**

| Dataset | Total Size | Pilot Size | Hallucination Definition |
|---------|------------|------------|--------------------------|
| TruthfulQA | 817 | 20 | Deviation from "Best Answer" |
| HaluEval-QA | 10,000 | 20 | Explicit hallucination labels |

**Implementation Details:**
- Generator: Meta-Llama-3-8B-Instruct
- NLI: microsoft/deberta-large-mnli
- BERTScore: roberta-large
- Entailment threshold: 0.5
- Bootstrap iterations: 1,000

**Pilot Scope:** N=20 samples per dataset. This sample size was chosen for pipeline validation (proof-of-concept mode) and is insufficient for statistically powered conclusions.

## 5. Results

The pilot study reveals that hallucination detection method performance varies across benchmarks.

### Main Results

**Table 1: Hallucination Detection AUROC (Pilot Study, N=20 samples per dataset)**

| Method | TruthfulQA | HaluEval |
|--------|------------|----------|
| Semantic Entropy | 0.289 [0.105, 0.526] | 0.551 [0.267, 0.800] |
| Self-Consistency | 0.474 [0.252, 0.687] | 0.444 [0.155, 0.733] |
| Gate Threshold | 0.55 | 0.55 |

Values in brackets are 95% bootstrap confidence intervals.

**Observations:**

1. **One condition meets the gate threshold.** Semantic entropy achieves AUROC 0.551 on HaluEval, marginally exceeding the 0.55 threshold.

2. **TruthfulQA shows inverted results for semantic entropy.** AUROC 0.289 is below random (0.5), indicating high-entropy responses were associated with truthful rather than hallucinated outputs in this pilot.

3. **Self-consistency performs near random on both benchmarks.** AUROC values of 0.444 and 0.474 are statistically indistinguishable from chance given the wide confidence intervals.

4. **Confidence intervals are wide and overlapping.** The small sample size (N=20) prevents statistically powered conclusions.

### Gate Evaluation

**Gate Result:** 1 of 4 conditions pass the AUROC > 0.55 threshold.

| Method | TruthfulQA | HaluEval |
|--------|------------|----------|
| Semantic Entropy | FAIL (0.289) | PASS (0.551) |
| Self-Consistency | FAIL (0.474) | FAIL (0.444) |

### Benchmark Sensitivity

Method ranking differs across benchmarks in this pilot: semantic entropy outperforms self-consistency on HaluEval (0.551 vs 0.444), but the pattern reverses on TruthfulQA (0.289 vs 0.474). However, given the wide confidence intervals, this observation requires validation with larger samples.

![ROC Curves](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/opus45/TEST_buildingtrust/docs/youra_research/h-e1/code/figures/roc_curves.png)
*Figure 1: ROC curves comparing detection methods across benchmarks.*

![Score Distributions](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/opus45/TEST_buildingtrust/docs/youra_research/h-e1/code/figures/score_distributions.png)
*Figure 2: Distribution of uncertainty scores for hallucinated vs truthful responses.*

![Gate Comparison](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/opus45/TEST_buildingtrust/docs/youra_research/h-e1/code/figures/gate_comparison.png)
*Figure 3: AUROC comparison against 0.55 gate threshold.*

## 6. Discussion

### Observations

**Observation 1: Benchmark sensitivity may exist.** Semantic entropy shows marginal detection on HaluEval but inverted results on TruthfulQA under identical conditions. This suggests method performance may depend on benchmark-specific factors, though the small sample size limits conclusions.

**Observation 2: Self-consistency requires investigation.** BERTScore-based consistency performed near random on both datasets. Possible explanations include: (a) surface similarity may not capture hallucination-relevant uncertainty, (b) sample size too small to reveal true signal, or (c) benchmark-method mismatch.

**Observation 3: TruthfulQA inversion requires explanation.** The inverted AUROC (0.289) for semantic entropy on TruthfulQA may stem from: (a) labeling methodology mismatch—"Best Answer" matching may not align with hallucination detection as operationalized by uncertainty methods, (b) model-specific effects, or (c) sample size artifacts.

### Limitations

**L1: Insufficient sample size.** N=20 per dataset yields wide confidence intervals (e.g., [0.105, 0.526]), preventing statistically powered conclusions. Full-scale evaluation with N≥200 samples is required.

**L2: TruthfulQA labeling mismatch hypothesis.** The inverted results may stem from differences between TruthfulQA's "truthfulness" definition and uncertainty-based hallucination detection. This requires investigation.

**L3: Single model family.** Results are from Llama-3-8B-Instruct only. Generalization to other model families is not established.

**L4: Single seed.** Variance across random seeds was not captured.

**L5: BERTScore as consistency metric.** The near-random performance of self-consistency may reflect limitations of BERTScore rather than the self-consistency approach itself. NLI-based consistency metrics were not tested.

### Implications

This pilot study suggests that controlled comparison under matched budgets may reveal performance patterns not visible in isolated evaluations. The observation that semantic entropy performs differently on HaluEval versus TruthfulQA, if confirmed at scale, would have implications for method selection.

The findings should be interpreted as preliminary observations requiring validation, not definitive assessments of method effectiveness.

## 7. Conclusion

This pilot study compared semantic entropy and self-consistency under matched computational budgets across two benchmarks. The key observation is potential benchmark sensitivity: semantic entropy achieved AUROC 0.551 on HaluEval but 0.289 on TruthfulQA, while self-consistency performed near random on both.

**Summary of Findings:**
1. Benchmark sensitivity may exist (SE: 0.551 HaluEval vs 0.289 TruthfulQA)
2. Self-consistency with BERTScore performed near random
3. Controlled comparison revealed patterns not visible in isolated evaluations

**Limitations:**
- Sample size (N=20) insufficient for statistical conclusions
- Single model family (Llama-3-8B)
- Single random seed

**Future Directions:**
- Full-scale evaluation with N≥200 samples per dataset
- Investigation of TruthfulQA labeling methodology alignment
- Testing NLI-based consistency metrics as alternative to BERTScore
- Multi-model evaluation (Mistral-7B, other families)

This work establishes a matched-budget comparison framework and identifies benchmark-method alignment as a consideration for hallucination detection evaluation. The findings require validation at scale before informing method selection decisions.

## References

- Farquhar, S., Kossen, J., Kuhn, L., & Gal, Y. (2024). Detecting Hallucinations in Large Language Models Using Semantic Entropy. Nature.
- Gal, Y., & Ghahramani, Z. (2016). Dropout as a Bayesian Approximation: Representing Model Uncertainty in Deep Learning. ICML.
- Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On Calibration of Modern Neural Networks. ICML.
- He, P., Liu, X., Gao, J., & Chen, W. (2021). DeBERTa: Decoding-enhanced BERT with Disentangled Attention. ICLR.
- Kuhn, L., Gal, Y., & Farquhar, S. (2023). Semantic Uncertainty: Linguistic Invariances for Uncertainty Estimation in Natural Language Generation. ICLR.
- Li, J., Cheng, X., Zhao, W. X., Nie, J. Y., & Wen, J. R. (2023). HaluEval: A Large-Scale Hallucination Evaluation Benchmark for Large Language Models. arXiv preprint.
- Lin, S., Hilton, J., & Evans, O. (2022). TruthfulQA: Measuring How Models Mimic Human Falsehoods. ACL.
- Manakul, P., Liusie, A., & Gales, M. J. (2023). SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models. EMNLP.
- Zhang, T., Kishore, V., Wu, F., Weinberger, K. Q., & Artzi, Y. (2020). BERTScore: Evaluating Text Generation with BERT. ICLR.
- Zhao, Z., Wallace, E., Feng, S., Klein, D., & Singh, S. (2021). Calibrate Before Use: Improving Few-Shot Performance of Language Models. ICML.
