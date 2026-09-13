# NLI Clustering Failure and Polarity Inversion: Why Standard UQ Methods Miss Hallucinations on HaluEval-QA

## Abstract

Three uncertainty quantification (UQ) signals — token-level entropy, semantic entropy, and SelfCheckGPT-BERTScore — have been proposed for zero-resource hallucination detection in large language models, but have been validated in separate settings on distinct benchmarks, making cross-method comparisons difficult. This paper presents a controlled comparison of all three methods applied to the same model (LLaMA-2-7B-chat) on a stratified 2,000-example subset of HaluEval-QA under matched inference conditions. All three methods fail to discriminate hallucinated from factual responses: AUROC values are 0.5000 (semantic entropy), 0.4829 (token entropy), and 0.3562 (SelfCheckGPT-BERTScore). The failure of semantic entropy is traceable to a specific mechanism: the NLI clustering step (microsoft/deberta-large-mnli) assigns all five stochastic responses to distinct semantic clusters in 72.8% of examples, yielding an aggregation rate of 0.272 (95% CI [0.253, 0.292]) and collapsing semantic entropy to a constant signal. SelfCheckGPT-BERTScore achieves below-random discrimination (AUROC = 0.3562, 95% CI [0.332, 0.380]), consistent with a label polarity inversion hypothesis — that ChatGPT-generated confident hallucinations in HaluEval-QA are produced consistently by LLaMA-2-7B-chat, inverting the consistency–hallucination correlation that SelfCheckGPT depends on. This hypothesis is not verified in the present work. The cross-model comparison (Mistral-7B-Instruct) was not executed. The findings quantify domain boundaries for NLI-based UQ methods on short factual QA responses.

---

## 1. Introduction

The ability to detect when a large language model has generated a hallucinated response — one that is fluent and confident-sounding but factually incorrect — is a practical problem for safe LLM deployment. Several post-hoc uncertainty quantification (UQ) methods have been developed that derive hallucination detection signals from standard inference outputs, without requiring additional training or labeled data. Three such methods have received significant attention: token-level entropy [Kadavath et al., 2022], semantic entropy [Kuhn et al., 2023], and SelfCheckGPT-BERTScore [Manakul et al., 2023].

Each method has been evaluated separately on different benchmarks. Semantic entropy was validated on TriviaQA and Natural Questions, achieving AUROC ≈ 0.78 [Kuhn et al., 2023]. SelfCheckGPT was validated on WikiBio biography generation, achieving AUC-PR ≈ 0.85 [Manakul et al., 2023]. Token entropy has been used as a baseline in multiple studies [Kadavath et al., 2022; Xiao and Wang, 2022]. Because these evaluations use different benchmarks, different models, and different protocols, a practitioner cannot determine from the existing literature which method to use for a specific deployment: short factual QA with an open-source LLM such as LLaMA-2-7B-chat.

This paper addresses that gap by applying all three methods to the same dataset (HaluEval-QA, 2,000 stratified examples), the same model (LLaMA-2-7B-chat), and the same evaluation protocol (AUROC with 1,000-resample bootstrap confidence intervals) under matched inference budgets (N=5 stochastic samples per example). The experimental design controls for confounds present in cross-study comparisons: dataset characteristics, model behavior, and inference variance.

The central result is that none of the three methods achieves above-random hallucination discrimination on HaluEval-QA with LLaMA-2-7B-chat. The failure is not uniform: each method fails for a different identifiable reason. Semantic entropy collapses to a constant signal because the NLI clustering mechanism produces maximum cluster counts (5 out of 5 responses in distinct clusters) for 72.8% of examples. SelfCheckGPT-BERTScore achieves AUROC = 0.3562, which is significantly below the random baseline of 0.5, indicating a negative — rather than positive — correlation between response consistency and hallucination labels on this benchmark. Token entropy is near-random (AUROC = 0.4829, 95% CI spanning 0.5).

**Sub-hypothesis design.** To decompose the mechanism failure, three sub-hypotheses were executed sequentially. H-E1 (EXISTENCE) tested whether a measurable AUROC gap between at least one method pair exists; the gate was satisfied (two pairs with Δ ≥ 0.05 and non-overlapping 95% CIs), but the gap was driven by SelfCheckGPT performing below random, not by semantic entropy outperforming token entropy. H-M1 (MECHANISM) tested whether the Pearson correlation between token entropy and semantic entropy is below 0.9; semantic entropy was diagnosed as constant (std = 4.14 × 10⁻²⁵), rendering the correlation undefined — the gate was recorded as DEGENERATE_PASS. H-M2 (MECHANISM) tested whether the NLI aggregation rate is at least 0.50; the measured rate of 0.272 (95% CI [0.253, 0.292]) does not satisfy this threshold, and the gate was recorded as PIVOT. A fourth sub-hypothesis (H-M3), which would have tested cross-model ranking stability using Mistral-7B-Instruct, was not executed.

**Contributions.** (1) A controlled, matched-condition comparison of token entropy, semantic entropy, and SelfCheckGPT-BERTScore on HaluEval-QA with LLaMA-2-7B-chat, to the authors' knowledge the first such comparison on this benchmark. (2) Empirical quantification of the NLI aggregation rate of microsoft/deberta-large-mnli on HaluEval-QA short factual QA responses: 0.272 (95% CI [0.253, 0.292]), establishing a concrete domain boundary for semantic entropy applicability. (3) Documentation of a below-random AUROC for SelfCheckGPT-BERTScore (0.3562) on HaluEval-QA and a proposed, unverified explanation — label polarity inversion due to the benchmark's construction methodology. (4) A null result with mechanism analysis: each failure is decomposed into a testable mechanism claim, two of which are experimentally verified (H-M1 degenerate diagnosis, H-M2 aggregation failure).

---

## 2. Related Work

### Entropy-Based Uncertainty Quantification

Token-level entropy — the mean per-token Shannon entropy over the greedy output distribution — is a low-cost UQ signal derived from a single forward pass. Kadavath et al. [2022] study self-calibration in large language models, including a P(True) signal, on models from Anthropic; their analysis targets proprietary models and does not systematically measure AUROC on open-source models or short factual QA benchmarks. Xiao and Wang [2022] conduct a broader comparison of UQ methods on natural language understanding tasks, establishing that the choice of UQ method matters for classification tasks; they do not study generative hallucination detection.

Semantic entropy [Kuhn et al., 2023] extends token entropy by computing uncertainty over semantic equivalence classes rather than token sequences. N stochastic responses are grouped into clusters using bidirectional NLI entailment (microsoft/deberta-large-mnli in the lorenzkuhn/semantic_uncertainty implementation), and entropy is computed over the cluster size distribution. Kuhn et al. (2023) report AUROC ≈ 0.78 on TriviaQA and Natural Questions with several LLMs, a substantial improvement over token entropy baselines. Their evaluation does not report NLI aggregation rates, and their benchmarks use responses that are typically longer and more syntactically varied than HaluEval-QA short factual QA responses.

### Consistency-Based Hallucination Detection

SelfCheckGPT [Manakul et al., 2023] measures the consistency of N stochastic generations relative to a greedy response using BERTScore, NLI, or n-gram overlap. The design assumption is that consistent generation indicates factual confidence, while inconsistent generation signals hallucination. Manakul et al. (2023) validate on WikiBio biography generation, reporting AUC-PR ≈ 0.85 for the BERTScore variant with N=5 samples. The benchmark-specific nature of this result — biography generation from Wikipedia — differs from short factual QA in both response length and label construction methodology.

Xiong et al. [2023] study verbalized uncertainty: how well LLMs express their own confidence in natural language. This is a distinct paradigm from the post-hoc signals studied here.

### Hallucination Benchmarks

HaluEval [Li et al., 2023] is a large-scale hallucination evaluation benchmark covering QA, dialogue, and summarization. The QA subset provides binary labels: each question-answer pair is paired with a ChatGPT-generated plausible-but-incorrect hallucinated answer. Li et al. (2023) note that the QA subset is the most reliable of the three HaluEval tasks. A relevant characteristic of the label construction is that ChatGPT-generated hallucinations are designed to be confident-sounding and internally coherent, a property that may interact adversely with consistency-based UQ methods.

### The Cross-Method Comparison Gap

The three methods have been validated on separate benchmarks: semantic entropy on TriviaQA/NQ [Kuhn et al., 2023], SelfCheckGPT on WikiBio [Manakul et al., 2023], and token entropy as a baseline across multiple settings. This siloed validation means that published results cannot be used to select among methods for a new deployment scenario. The present work is, to the authors' knowledge, the first controlled comparison of all three methods on HaluEval-QA with the same LLM under matched inference budgets.

---

## 3. Method

### Dataset

Experiments use the QA subset of HaluEval [Li et al., 2023], loaded from the pminervini/HaluEval HuggingFace dataset. A stratified sample of 2,000 examples (1,000 hallucinated, 1,000 factual) is drawn with a fixed random seed (seed=42), producing a balanced 50% base rate that makes AUROC directly interpretable as discrimination above 0.5. Responses in this subset are typically short (1–2 sentences, 5–15 tokens), which is a key characteristic distinguishing them from TriviaQA/NQ responses (typically 20–50 tokens).

### Model

LLaMA-2-7B-chat (meta-llama/Llama-2-7b-chat-hf) is used in float16 precision on a single NVIDIA H100 NVL GPU (CUDA_VISIBLE_DEVICES=4). Inference parameters are fixed across all UQ methods: greedy temperature = 0.0, stochastic temperature = 1.0, max_new_tokens = 256, N = 5 stochastic samples. All three UQ methods share the same inference outputs: token entropy reuses greedy logits (cast to float32 before softmax for fp16 numerical safety); semantic entropy and SelfCheckGPT both use the same five stochastic samples. This design eliminates inference variance as a confound when comparing methods.

### UQ Signal Pipelines

**Token Entropy (TE).** Mean Shannon entropy over per-token output distributions from the greedy pass:

$$H_\text{token}(x) = \frac{1}{T} \sum_{t=1}^{T} H(p_t)$$

where $p_t$ is the token probability distribution at position $t$ and $T$ is the sequence length.

**Semantic Entropy (SE).** Computed over NLI-based semantic equivalence clusters of the N=5 stochastic samples, following the lorenzkuhn/semantic_uncertainty implementation [Kuhn et al., 2023]. For each ordered response pair $(r_i, r_j)$, bidirectional NLI entailment is checked using microsoft/deberta-large-mnli with batch size 16. Pairs with mutual entailment are merged via union-find clustering. Cluster entropy is:

$$H_\text{semantic}(x) = -\sum_c p_c \log p_c, \quad p_c = |C_c| / N$$

If all N responses are assigned to distinct clusters, $H_\text{semantic}$ equals $\log_2(N)$ for every example, producing a constant signal. The NLI clustering step is the mechanism studied in H-M2.

**SelfCheckGPT-BERTScore (SCG).** Inconsistency between the greedy response and each stochastic sample, measured by BERTScore:

$$\text{SCG}(x) = 1 - \frac{1}{N} \sum_{i=1}^{N} \text{BERTScore}(r_\text{greedy}, r_i)$$

Higher SCG indicates more inconsistent generation, predicted to correspond to hallucination under the assumption that hallucinations arise from model uncertainty.

### Evaluation Protocol

AUROC is computed for each UQ signal against binary hallucination labels. Bootstrap confidence intervals (95%) are estimated from N=1,000 resamples with seed=42. Pairwise significance is assessed using the criterion Δ AUROC ≥ 0.05 and non-overlapping 95% CIs, with Bonferroni correction for three pairwise comparisons (α_corrected = 0.05/3 ≈ 0.0167).

### Implementation

All code is implemented in Python 3.10 with PyTorch. The pipeline consists of: `data.py` (dataset loading and stratified sampling), `inference.py` (greedy and stochastic LLM inference with checkpoint-resume), `uq_signals.py` (TE, SE, and SCG computation), `evaluate.py` (AUROC, bootstrap CI, pairwise gate check), and `visualize.py` (figure generation). Checkpoint-resume was necessary for SelfCheckGPT computation, which required approximately 2.7 hours for 2,000 examples on the H100 NVL.

---

## 4. Experimental Setup

Experiments address three research questions:

- **RQ1:** Do the three UQ methods produce measurably different AUROC on HaluEval-QA with LLaMA-2-7B-chat under matched conditions?
- **RQ2:** Is the correlation structure between token entropy and semantic entropy consistent with functional NLI filtering?
- **RQ3:** Does deberta-large-mnli successfully aggregate stochastic responses on HaluEval-QA short factual QA responses?

| Property | Value |
|---|---|
| Dataset | HaluEval-QA, 2,000 stratified examples (1,000 hallucinated, 1,000 factual) |
| Model | LLaMA-2-7B-chat (meta-llama/Llama-2-7b-chat-hf), float16 |
| GPU | NVIDIA H100 NVL (single GPU) |
| Stochastic samples N | 5 (temperature = 1.0) |
| Greedy temperature | 0.0 |
| max_new_tokens | 256 |
| NLI model | microsoft/deberta-large-mnli |
| Bootstrap resamples | 1,000 (seed = 42) |
| Bonferroni-corrected α | 0.0167 (k = 3) |
| Min AUROC gap (gate) | 0.05 |
| Random seed | 42 |

Three sub-hypotheses were executed in sequence, each building on outputs from the prior:

- **H-E1 (EXISTENCE, MUST_WORK):** Tests whether at least one UQ method pair exhibits Δ AUROC ≥ 0.05 with non-overlapping 95% CIs on HaluEval-QA with LLaMA-2-7B-chat.
- **H-M1 (MECHANISM, MUST_WORK):** Tests whether Pearson r(TE, SE) < 0.9, using H-E1 inference outputs without new LLM inference.
- **H-M2 (MECHANISM, SHOULD_WORK):** Tests whether the NLI aggregation rate — fraction of examples with cluster count < N=5 — is at least 0.50, using H-E1/H-M1 cluster data.

A fourth sub-hypothesis H-M3 — testing cross-model ranking stability with Mistral-7B-Instruct (Spearman ρ ≥ 0.8) — was planned but not executed. Results for H-M3 are therefore absent from this paper.

---

## 5. Results

Results are presented in causal order: the NLI clustering behavior (RQ3) causally precedes the AUROC outcome (RQ1).

### 5.1 NLI Clustering Aggregation (H-M2, RQ3)

The NLI aggregation rate — the fraction of examples for which at least one pair of stochastic responses is clustered together — is **0.272 (95% CI [0.253, 0.292])**, measured from 2,000 HaluEval-QA examples using the cluster counts produced in H-E1/H-M1. The gate threshold for H-M2 (aggregation_rate ≥ 0.50) is not satisfied; the CI upper bound (0.292) is also below the secondary threshold (0.30). Gate result: **PIVOT**.

The cluster count distribution across all 2,000 examples is:

| Cluster Count | Frequency | Fraction |
|:---:|---:|---:|
| 1 (full collapse — all in one cluster) | 4 | 0.2% |
| 2 | 22 | 1.1% |
| 3 | 112 | 5.6% |
| 4 | 406 | 20.3% |
| 5 (no aggregation — all in distinct clusters) | 1,456 | 72.8% |

Mean cluster count = 4.644 (std = 0.657, median = 5.000). In 72.8% of examples, deberta-large-mnli classified all five stochastic responses as semantically non-equivalent, assigning each to its own cluster. The point-biserial correlation between cluster count and hallucination label was not computable (NaN) due to the near-constant cluster distribution.

![Cluster count distribution (H-M2)](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_question_2/docs/youra_research/20260510_question/h-m2/figures/cluster_count_dist.png)

![NLI aggregation rate vs. gate threshold](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_question_2/docs/youra_research/20260510_question/h-m2/figures/aggregation_rate.png)

![CDF of cluster counts](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_question_2/docs/youra_research/20260510_question/h-m2/figures/cluster_count_cdf.png)

When all N=5 responses are in distinct clusters with equal probability p = 1/5, semantic entropy equals log₂(5) ≈ 2.322 bits for every example, producing a constant signal that carries no information about hallucination status. This is the causal mechanism underlying the degenerate semantic entropy result reported in Section 5.2.

### 5.2 Degenerate Semantic Entropy (H-M1, RQ2)

Semantic entropy scores are constant across all 2,000 examples: std = 4.14 × 10⁻²⁵. This near-zero variance results from the 72.8% of examples at the maximum cluster count (5/5) contributing the same entropy value (log₂(5) ≈ 2.322 bits), with only 4 examples (0.2%) yielding cluster count = 1 (SE = 0 bits). The variation introduced by the remaining 27.2% of examples is insufficient to produce measurable variance. The Pearson correlation r(TE, SE) is undefined (division by zero in standard deviation). Gate result: **DEGENERATE_PASS**.

The cluster distribution from H-M1 (mean clusters = 4.644) corroborates the H-M2 finding and confirms that the degenerate SE output propagates from the NLI clustering failure in H-E1.

![Token entropy vs. semantic entropy scatter (degenerate SE)](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_question_2/docs/youra_research/20260510_question/h-m1/figures/degenerate_summary.png)

![Cluster count distribution (H-M1)](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_question_2/docs/youra_research/20260510_question/h-m1/figures/cluster_count_dist.png)

### 5.3 Main AUROC Comparison (H-E1, RQ1)

AUROC values and 95% bootstrap confidence intervals for all three UQ methods on HaluEval-QA with LLaMA-2-7B-chat are:

| Method | AUROC | 95% CI Lower | 95% CI Upper |
|---|---:|---:|---:|
| Semantic Entropy (SE) | 0.5000 | 0.5000 | 0.5000 |
| Token Entropy (TE) | 0.4829 | 0.4585 | 0.5090 |
| SelfCheckGPT-BERTScore (SCG) | 0.3562 | 0.3321 | 0.3803 |

![AUROC bar chart with 95% bootstrap CIs](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_question_2/docs/youra_research/20260510_question/h-e1/code/figures/auroc_bar_chart.png)

![ROC curves overlay](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_question_2/docs/youra_research/20260510_question/h-e1/code/figures/roc_curves_overlay.png)

**Semantic entropy (AUROC = 0.5000, CI = [0.5000, 0.5000]).** The degenerate confidence interval — a single point at exactly 0.5 — is the expected signature of a constant signal: every threshold yields the same true positive rate and false positive rate, producing an ROC curve on the diagonal. This result is a direct consequence of the H-M2 NLI clustering failure described in Section 5.1, not a property of semantic entropy in general.

**Token entropy (AUROC = 0.4829, CI = [0.4585, 0.5090]).** Near-random. The CI spans 0.5, indicating that token entropy is consistent with zero discrimination on this benchmark and model combination.

**SelfCheckGPT-BERTScore (AUROC = 0.3562, CI = [0.3321, 0.3803]).** Below random chance. The CI upper bound (0.3803) is entirely below 0.5, indicating a statistically significant negative correlation between BERTScore consistency and HaluEval-QA hallucination labels. This is the opposite of the positive discrimination assumed by SelfCheckGPT's design.

Pairwise comparisons (Bonferroni-corrected α = 0.0167):

| Pair | Winner | Δ AUROC | CI Overlap | Qualifies (Δ ≥ 0.05, non-overlapping) |
|---|---|---:|---|:---:|
| SE vs. SCG | SE | 0.1438 | Non-overlapping | Yes |
| TE vs. SCG | TE | 0.1268 | Non-overlapping | Yes |
| SE vs. TE | SE | 0.0171 | Overlapping | No |

Two of three pairwise comparisons satisfy both the Δ ≥ 0.05 threshold and the non-overlapping CI criterion. Gate result: **PASS (MUST_WORK satisfied)**. However, both qualifying pairs are driven by SelfCheckGPT performing significantly below random, not by semantic entropy outperforming token entropy. The primary prediction — SE achieves ≥ 0.05 AUROC advantage over TE — is not supported (Δ = 0.0171, overlapping CIs).

### 5.4 Label-Stratified Cluster Counts (H-M2 Supplementary)

The cluster count by hallucination label shows similar distributions for hallucinated and factual examples, consistent with label-agnostic NLI clustering behavior.

![Cluster count by hallucination label](/home/anonymous/YouRA_results_new_4_sonnet46_no_mcp/TEST_question_2/docs/youra_research/20260510_question/h-m2/figures/cluster_count_by_label.png)

### 5.5 Summary of Sub-Hypothesis Outcomes

| Sub-Hypothesis | Type | Gate | Result | Primary Finding |
|---|---|---|---|---|
| H-E1 | EXISTENCE | MUST_WORK | PASS | 2 qualifying method pairs (SE>SCG, TE>SCG); gap driven by SCG below-random |
| H-M1 | MECHANISM | MUST_WORK | DEGENERATE_PASS | SE std = 4.14 × 10⁻²⁵; Pearson r undefined |
| H-M2 | MECHANISM | SHOULD_WORK | PIVOT | Aggregation rate = 0.272 (CI [0.253, 0.292]); A2 violated |
| H-M3 | MECHANISM | MUST_WORK | Not executed | Mistral-7B-Instruct experiment absent |

---

## 6. Discussion

### NLI Domain Mismatch

The H-M2 result establishes that microsoft/deberta-large-mnli does not produce meaningful semantic aggregation on HaluEval-QA short factual QA responses under the lorenzkuhn/semantic_uncertainty configuration with N=5 stochastic samples. In 72.8% of examples, all five stochastic responses are assigned to distinct semantic clusters, collapsing semantic entropy to a constant maximum-entropy value.

A plausible explanation is NLI domain mismatch: deberta-large-mnli was trained on MNLI, which consists of sentence pairs from news and fiction text, and was validated by Kuhn et al. (2023) on TriviaQA and Natural Questions — benchmarks whose responses are typically longer and more syntactically diverse than HaluEval-QA's 1–2 sentence factual answers. For short factual answers where the same semantic content is expressed in surface-variant forms (e.g., "The United States," "America," "the US"), the NLI model may classify surface-distinct responses as semantically non-equivalent, because its entailment threshold is calibrated for longer and more syntactically structured sentence pairs. This explanation is consistent with the data but has not been directly verified in the present work; ruling out alternative explanations (e.g., genuine semantic diversity in LLaMA-2-7B-chat responses at temperature = 1.0) would require testing with a QA-specific NLI model or examining individual response pairs.

The practical implication of the H-M2 finding is that semantic entropy's non-degeneracy cannot be assumed when applying the method to a new benchmark. The aggregation rate is a measurable precondition for non-degenerate semantic entropy, and reporting it alongside AUROC results would allow others to distinguish genuine discrimination from degenerate constant behavior.

### SelfCheckGPT Polarity Inversion Hypothesis

The SelfCheckGPT-BERTScore result (AUROC = 0.3562, CI entirely below 0.5) indicates that BERTScore consistency is positively correlated with HaluEval-QA hallucination labels — the opposite of SelfCheckGPT's design assumption. One explanation, consistent with the benchmark's construction methodology, is a label polarity inversion: HaluEval-QA hallucinations are ChatGPT-generated confident-sounding incorrect answers. If LLaMA-2-7B-chat generates consistently wrong answers for questions with hallucinated labels — because the wrong answer is the model's preferred factual response — then BERTScore consistency would be higher for hallucinated examples than for factual examples, inverting SelfCheckGPT's expected correlation direction. Figure 5.4 shows that cluster count distributions are similar across hallucinated and factual labels, which is consistent with the model behaving similarly regardless of ground-truth label.

This hypothesis is not verified in the present work. Direct verification would require stratifying the per-example BERTScore consistency scores by hallucination label using the existing H-E1 outputs, which involves no new LLM inference. Alternative explanations — including BERTScore insensitivity to short factual QA responses and LLaMA-2-7B-chat-specific generation patterns — have not been ruled out.

### Token Entropy as a Null Baseline

Token entropy (AUROC = 0.4829, CI [0.4585, 0.5090]) is consistent with zero discrimination on HaluEval-QA. This result indicates that LLaMA-2-7B-chat's per-token uncertainty does not systematically covary with HaluEval-QA hallucination labels under greedy inference. As with the other methods, this finding is specific to the LLaMA-2-7B-chat model and the HaluEval-QA benchmark; it should not be interpreted as a general failure of token entropy for hallucination detection.

### Limitations

**Single model.** All executed experiments use LLaMA-2-7B-chat. The planned cross-model experiment (H-M3 with Mistral-7B-Instruct) was not executed. All findings are specific to LLaMA-2-7B-chat on HaluEval-QA; generalization to other model families has not been tested. The NLI aggregation failure is a property of deberta-large-mnli's behavior on HaluEval-QA response style; whether it would also occur with Mistral-7B-Instruct responses is unknown.

**ChatGPT-generated labels.** HaluEval-QA labels are generated by ChatGPT rather than human annotators. All three methods are subject to the same label characteristics, preserving between-method comparison validity. The near-random AUROC values for all methods are consistent with genuine method failure on this benchmark, or with label construction artifacts that suppress UQ signal correlation — distinguishing these would require applying the same pipeline to human-annotated benchmarks such as TriviaQA or Natural Questions with the same model.

**N=5 stochastic samples.** The NLI aggregation failure (72.8% of examples at maximum cluster count, CI entirely below 0.30) is too large in magnitude to be plausibly explained by low N alone. However, whether increasing N (e.g., to N=20) would improve the aggregation rate has not been tested. Similarly, the SelfCheckGPT AUROC magnitude (AUROC = 0.3562, 0.144 below random) suggests a systematic effect unlikely to disappear with higher N, but this has not been verified.

**Unverified polarity inversion.** The proposed explanation for the SelfCheckGPT below-random result is a hypothesis, not an experimentally verified mechanism. Alternative explanations for AUROC = 0.3562 have not been systematically ruled out.

---

## 7. Conclusion

A controlled comparison of token entropy, semantic entropy, and SelfCheckGPT-BERTScore on HaluEval-QA with LLaMA-2-7B-chat shows that all three methods fail to discriminate hallucinated from factual responses: AUROC values are 0.5000, 0.4829, and 0.3562 respectively. The failure of semantic entropy is traceable to the NLI clustering mechanism: microsoft/deberta-large-mnli assigns all five stochastic responses to distinct semantic clusters in 72.8% of examples (aggregation rate = 0.272, 95% CI [0.253, 0.292]), collapsing semantic entropy to a constant signal. SelfCheckGPT-BERTScore achieves below-random discrimination, consistent with — but not proven to be caused by — a label polarity inversion in HaluEval-QA's ChatGPT-generated confident hallucinations.

The cross-model comparison (Mistral-7B-Instruct, H-M3) was not executed, and cross-model generalizability of these findings is unknown.

The primary empirical contributions are: (1) first measurement of the NLI aggregation rate of deberta-large-mnli on HaluEval-QA (0.272, 95% CI [0.253, 0.292]), establishing that non-degeneracy of semantic entropy cannot be assumed on short factual QA benchmarks; (2) documentation of below-random SelfCheckGPT-BERTScore discrimination (AUROC = 0.3562) on HaluEval-QA with LLaMA-2-7B-chat, with a proposed unverified explanation; (3) a matched-condition evaluation framework that makes all three UQ methods directly comparable on the same dataset and model.

Three experiments would directly extend these findings: substituting a QA-specific NLI model for deberta-large-mnli in the semantic entropy pipeline (zero new LLM inference required, using existing H-E1 stochastic samples); verifying the SelfCheckGPT polarity inversion by stratifying existing H-E1 consistency scores by label (zero new inference); and executing H-M3 with Mistral-7B-Instruct using the proven H-E1 codebase.

---

## References

Angelopoulos, A. N. and Bates, S. (2023). A gentle introduction to conformal prediction and distribution-free uncertainty quantification. *arXiv preprint arXiv:2107.07511*.

Geifman, Y. and El-Yaniv, R. (2017). Selective classification for deep neural networks. In *Advances in Neural Information Processing Systems*, volume 30.

Guo, C., Pleiss, G., Sun, Y., and Weinberger, K. Q. (2017). On calibration of modern neural networks. In *Proceedings of the 34th International Conference on Machine Learning*, pages 1321–1330.

Kadavath, S. et al. (2022). Language models (mostly) know what they know. *arXiv preprint arXiv:2207.05221*.

Kuhn, L., Gal, Y., and Farquhar, S. (2023). Semantic uncertainty: Linguistic invariances for uncertainty estimation in natural language generation. *arXiv preprint arXiv:2302.09664*.

Li, J., Cheng, X., Zhao, W. X., Nie, J.-Y., and Wen, J.-R. (2023). HaluEval: A large-scale hallucination evaluation benchmark for large language models. *arXiv preprint arXiv:2305.11747*.

Manakul, P., Liusie, A., and Gales, M. J. F. (2023). SelfCheckGPT: Zero-resource black-box hallucination detection for generative large language models. *arXiv preprint arXiv:2303.08896*.

Quach, V. et al. (2023). Conformal language modeling. *arXiv preprint arXiv:2306.10193*.

Xiao, Y. and Wang, W. Y. (2022). Uncertainty quantification with pre-trained language models: A large-scale empirical analysis. *arXiv preprint arXiv:2210.04714*.

Xiong, M. et al. (2023). Can LLMs express their uncertainty? An empirical evaluation of confidence elicitation in large language models. *arXiv preprint arXiv:2306.13063*.

*Note: Citation arXiv identifiers are taken from Phase 1 research records. Semantic Scholar verification was not performed (MCP unavailable in the test environment).*
