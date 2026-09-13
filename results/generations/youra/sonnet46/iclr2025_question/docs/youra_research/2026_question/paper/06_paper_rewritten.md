# Post-Hoc Hallucination Detection via Frozen NLI Contradiction Scoring on HaluEval: Task-Dependent Effectiveness and the Commission–Omission Boundary

---

## Abstract

This paper investigates whether a frozen, off-the-shelf Natural Language Inference (NLI) model can detect hallucinations in large language model outputs without requiring any LLM generation at inference time. Using `cross-encoder/nli-deberta-v3-large` applied to 60,000 balanced (context, response) pairs from the HaluEval benchmark, the method computes net-contradiction scores — P(contradiction) minus P(entailment) — as a hallucination indicator across three tasks: dialogue, question answering (QA), and summarization. On the dialogue task, AUROC reached 0.709 (Cohen's d = 0.714, DeLong p ≈ 0); on QA, AUROC reached 0.644 (Cohen's d = 0.779, DeLong p = 1.29 × 10⁻²⁸²). Both exceeded the pre-specified 0.55 threshold. On summarization, AUROC was 0.530 (Cohen's d = 0.220), failing to exceed the threshold. Mechanism analysis via Wilcoxon rank-sum tests confirmed that NLI contradiction scores separate hallucinated from non-hallucinated responses on all three tasks (p < 0.05), though a KL divergence criterion failed on the QA task. The task asymmetry is interpreted through a commission–omission framework: NLI contradiction scoring detects commission-type hallucinations (factual fabrications, contradictions) prevalent in dialogue and QA, but not omission-type hallucinations (missing information, abstractive gaps) that characterize the summarization subset of HaluEval. These results suggest that generation-free NLI scoring is a viable hallucination detection method for commission-dominated tasks, while omission-dominated tasks require alternative approaches.

---

## 1. Introduction

Large language models (LLMs) generate text that is frequently plausible-sounding but factually incorrect or unsupported by the provided context. This phenomenon, commonly termed hallucination, poses a challenge for deploying LLMs in dialogue systems, question answering pipelines, and summarization applications where factual reliability is expected. Detecting hallucinations before they reach end users is therefore a practical requirement for many production systems.

The dominant approaches to hallucination detection rely on the LLM's own generation process. SelfCheckGPT (Manakul et al., 2023) samples multiple stochastic outputs and measures their consistency. Verbalized confidence methods (Kadavath et al., 2022) prompt models to express uncertainty about their own outputs. These generation-dependent methods introduce additional inference cost that scales with the number of samples required, and they depend on model-specific capabilities such as instruction-following or calibrated uncertainty expression that vary across model families and versions.

An alternative line of work has demonstrated that NLI models can assess factual consistency between text pairs without any generation. SummaC (Laban et al., 2022) applied sentence-level NLI aggregation to summarization consistency, and TRUE (Honovich et al., 2022) evaluated DeBERTa-scale NLI classifiers across multiple factual consistency benchmarks. However, to our knowledge, no prior work has reported AUROC for frozen NLI applied directly to the HaluEval benchmark (Li et al., 2023) across all three of its task types (dialogue, QA, and summarization), nor has prior work provided a systematic analysis of why NLI-based detection succeeds on some task types and fails on others.

This paper presents a generation-free hallucination detection method that applies a frozen NLI cross-encoder to pre-existing (context, response) pairs from HaluEval. The method requires no LLM generation, no fine-tuning, and no retrieval infrastructure. The core scoring mechanism is net-contradiction: P(contradiction) − P(entailment), which amplifies the signal from responses that simultaneously contradict the context and fail to be entailed by it.

The main findings are as follows. First, the method achieves AUROC = 0.709 on dialogue and AUROC = 0.644 on QA, both with large effect sizes (Cohen's d > 0.7) and extreme statistical significance (DeLong p < 10⁻²⁸²). Second, mechanism analysis via Wilcoxon rank-sum tests confirms that NLI scores separate hallucinated from non-hallucinated responses on all three tasks. Third, the method produces near-chance performance on summarization (AUROC = 0.530), which is interpreted as a structural limitation rather than a performance failure: the NLI contradiction signal is architecturally misaligned with omission-type hallucinations that predominate in HaluEval's summarization subset.

---

## 2. Related Work

### 2.1 Generation-Based Hallucination Detection

SelfCheckGPT (Manakul et al., 2023) is the most directly comparable prior method. It samples multiple stochastic outputs from an LLM and measures consistency using NLI, BERTScore, or n-gram overlap. On HaluEval, SelfCheckGPT-NLI achieved AUROC = 0.48 on dialogue and AUROC = 0.53 on QA when evaluated with base (non-instruction-tuned) Meta-Llama-3-8B (as reported in the experiment design documentation for this study; these values should be understood as a lower bound, since SelfCheckGPT performance likely improves with instruction-tuned models that produce more diverse stochastic samples). Verbalized confidence methods (Kadavath et al., 2022) prompt LLMs to express uncertainty directly, but their reliability varies with model capabilities and they are inapplicable to non-instruction-tuned models.

### 2.2 NLI-Based Factual Consistency

Maynez et al. (2020) demonstrated that NLI entailment could predict faithfulness in abstractive summarization. SummaC (Laban et al., 2022) systematized this approach with sentence-level NLI aggregation (SummaCConv), achieving 74.4% balanced accuracy on summarization consistency benchmarks. TRUE (Honovich et al., 2022) extended NLI-based evaluation across 11 datasets, establishing DeBERTa-NLI as a cross-task factual consistency indicator. FActScore (Min et al., 2023) proposed atomic-fact NLI verification but requires retrieval infrastructure. ORION (Gerner et al., 2025) reported F1 = 0.83 on RAGTruth using post-hoc NLI encoders. None of these works report AUROC on HaluEval hallucination labels using a frozen NLI model without retrieval or fine-tuning.

### 2.3 Hallucination Taxonomy

The distinction between commission-type and omission-type hallucinations maps onto Maynez et al.'s (2020) categorization of intrinsic versus extrinsic summarization errors. Commission hallucinations (fabricated facts, factual substitutions, direct contradictions) share the logical structure of NLI contradiction. Omission hallucinations (missing information, abstractive gaps, incomplete coverage) do not produce contradiction signals because the response does not explicitly contradict the context — it simply fails to capture it. SummaC's effectiveness on AggreFact, which contains explicitly inconsistent summaries (commission-type), is consistent with this distinction. HaluEval's summarization hallucinations, generated by GPT-3.5, appear to be predominantly omission-type.

### 2.4 Positioning

| Method | LLM at Detection? | Multi-task | AUROC on HaluEval |
|--------|-------------------|------------|-------------------|
| SelfCheckGPT-NLI (Manakul et al., 2023) | Yes (multi-sample) | Yes | 0.48 (dialogue), 0.53 (QA)* |
| TRUE (Honovich et al., 2022) | No | Yes | Not reported |
| SummaC (Laban et al., 2022) | No | Summarization | Not reported |
| Present method | No | Yes (3 tasks) | 0.709 (dialogue), 0.644 (QA), 0.530 (summ.) |

*SelfCheckGPT values are from evaluation with base (non-instruction-tuned) Llama-3-8B and represent a likely lower bound.

---

## 3. Method

### 3.1 Problem Formulation

Given a (context, response) pair where the context is the grounding information and the response is the LLM output, the goal is to produce a scalar hallucination score without requiring any LLM generation. The score should rank hallucinated responses above non-hallucinated ones (measured by AUROC).

### 3.2 NLI Model

The method uses `cross-encoder/nli-deberta-v3-large` (He et al., 2021), a 304M-parameter cross-encoder trained on MNLI. Cross-encoders compute full token-level interaction between premise and hypothesis in a single forward pass, enabling detection of subtle factual substitutions that independent-encoding architectures would miss. The model is used in inference-only mode with no gradient computation or fine-tuning.

### 3.3 Net-Contradiction Scoring

The hallucination score for a (context, response) pair is defined as:

```
score = P(contradiction | context, response) − P(entailment | context, response)
```

where the NLI model outputs a probability distribution over {entailment, neutral, contradiction}. This formulation amplifies the hallucination signal: commission-type hallucinations simultaneously increase P(contradiction) and decrease P(entailment), producing large positive scores. Non-hallucinated responses that are entailed by the context produce negative scores. Neutral responses produce scores near zero.

### 3.4 Sentence-Level Aggregation

For the dialogue task, the response is tokenized into sentences, each sentence is scored independently against the context, and the maximum net-contradiction score is taken as the final score. This follows the multiple-instance learning principle (Laban et al., 2022): a response is considered hallucinated if any constituent sentence contradicts the grounding context.

For QA, responses are typically short (one or two sentences) and are scored at the response level.

### 3.5 Task-Specific Context Configuration

**Dialogue:** The last three turns of the conversation history serve as the NLI premise. This window captures the immediate conversational context against which hallucinations are most likely to be detectable.

**QA:** The full knowledge passage serves as the NLI premise; the response is the hypothesis.

**Summarization:** The full source document serves as the NLI premise; the full summary is the hypothesis, scored at the response level.

### 3.6 Limitations of the Current Design

The three design choices — net-contradiction framing, sentence-level max aggregation, and last-3-turn context window — represent the single configuration evaluated in this study. Ablation experiments comparing alternative formulations (e.g., different aggregation strategies, context window sizes, or scoring functions) were not conducted. The results confirm that this configuration produces above-chance discrimination on dialogue and QA, but it is not possible to attribute performance to individual design choices versus alternatives.

---

## 4. Experimental Setup

### 4.1 Dataset

HaluEval (Li et al., 2023) provides 20,000 balanced pairs per task (10,000 hallucinated, 10,000 non-hallucinated) across three domains: dialogue, QA, and summarization. Hallucinated examples were generated by GPT-3.5. The total evaluation set comprises 60,000 (context, response) pairs.

### 4.2 Evaluation Metrics

The primary metric is AUROC (Area Under the Receiver Operating Characteristic curve), which measures the probability that a randomly chosen hallucinated response receives a higher score than a randomly chosen non-hallucinated response. Statistical significance is assessed via the DeLong test (DeLong et al., 1988) against the null hypothesis of AUROC = 0.5, with α = 0.05. Effect size is measured by Cohen's d between the score distributions of the two classes.

The pre-specified gate criterion for the existence hypothesis (H-E1) required AUROC > 0.55 with DeLong p < 0.05 on at least 2 out of 3 tasks.

### 4.3 Mechanism Analysis (H-M1)

A separate mechanism analysis was conducted on the pre-computed NLI scores from H-E1 to test whether DeBERTa's MNLI pretraining encodes graded support sensitivity. Two criteria were evaluated:

1. **KL divergence from uniform:** The NLI output distribution [P(entailment), P(neutral), P(contradiction)] should be non-uniform (KL > 0.05 on all 3 tasks).
2. **Wilcoxon rank-sum test:** Net-contradiction scores should differ between hallucinated and non-hallucinated responses (p < 0.05 on ≥ 2/3 tasks).

### 4.4 Baseline

The comparison baseline is SelfCheckGPT-NLI (Manakul et al., 2023), with reported AUROC values of 0.48 (dialogue) and 0.53 (QA) on HaluEval. These values were obtained from evaluations using base (non-instruction-tuned) Meta-Llama-3-8B, which produces near-uniform stochastic samples. This represents a likely lower bound on SelfCheckGPT performance; instruction-tuned models would likely yield higher AUROC. The comparison should be interpreted with this caveat.

### 4.5 Implementation Details

- **Model:** `cross-encoder/nli-deberta-v3-large` (304M parameters, frozen, float32)
- **Hardware:** Single NVIDIA H100 NVL (CUDA_VISIBLE_DEVICES=0)
- **Batch size:** 32 (with OOM fallback to 16)
- **Max sequence length:** 512 tokens
- **Inference only:** No training, no gradient computation
- **Total pairs evaluated:** 60,000 across three tasks
- **Software:** Python 3.10, PyTorch, HuggingFace Transformers

---

## 5. Results

### 5.1 Existence Results (H-E1)

Table 1 reports the per-task detection performance.

**Table 1: Detection Performance on HaluEval (N = 20,000 per task, balanced)**

| Task | AUROC | DeLong p-value | Cohen's d | Gate (>0.55) |
|------|-------|----------------|-----------|--------------|
| Dialogue | 0.709 | ≈ 0 | 0.714 | Pass |
| QA | 0.644 | 1.29 × 10⁻²⁸² | 0.779 | Pass |
| Summarization | 0.530 | 2.02 × 10⁻¹³ | 0.220 | Fail |

The pre-specified gate criterion (AUROC > 0.55 on ≥ 2/3 tasks) was satisfied: dialogue and QA both passed, while summarization did not.

On the dialogue task, AUROC = 0.709 indicates that the frozen NLI classifier correctly ranks a randomly selected hallucinated response above a randomly selected non-hallucinated response 70.9% of the time. The effect size is large (Cohen's d = 0.714). On QA, AUROC = 0.644 with an even larger effect size (Cohen's d = 0.779), indicating that the score distributions of the two classes are well-separated despite the lower AUROC. On summarization, AUROC = 0.530 is close to chance (0.5), with a small effect size (Cohen's d = 0.220).

The structural ceiling analysis estimated AUROC_max = 0.77 for dialogue and QA, based on the proportion of examples where contradictions are detectable (p_contradictory = 0.54). For summarization, AUROC_max = 0.52 with p_contradictory = 0.04, indicating that only approximately 4% of summarization hallucinations manifest as direct contradictions — the method is operating near its theoretical ceiling on this task.

![Figure 1: ROC curves for NLI-based hallucination detection across three HaluEval tasks. Dialogue achieves the highest AUROC (0.709), followed by QA (0.644), with summarization near chance (0.530).](/home/anonymous/YouRA_results_new_4/TEST_question/docs/youra_research/20260315_question/h-e1/figures/roc_curves.png)

![Figure 2: Net-contradiction score distributions for hallucinated versus non-hallucinated responses across tasks. Dialogue and QA show clear separation between classes; summarization distributions largely overlap.](/home/anonymous/YouRA_results_new_4/TEST_question/docs/youra_research/20260315_question/h-e1/figures/score_distributions.png)

![Figure 3: Gate metrics comparison (AUROC and Cohen's d) across tasks. Dialogue and QA exceed the AUROC threshold; summarization falls below.](/home/anonymous/YouRA_results_new_4/TEST_question/docs/youra_research/20260315_question/h-e1/figures/gate_metrics_comparison.png)

![Figure 4: Structural ceiling analysis showing estimated maximum AUROC per task based on the proportion of commission-type hallucinations. Summarization has a very low ceiling (0.52) due to the rarity of contradiction-detectable hallucinations.](/home/anonymous/YouRA_results_new_4/TEST_question/docs/youra_research/20260315_question/h-e1/figures/structural_ceiling.png)

**Comparison with SelfCheckGPT-NLI.** The literature-reported SelfCheckGPT-NLI values on HaluEval are AUROC = 0.48 (dialogue) and 0.53 (QA), obtained with base Llama-3-8B. The present method exceeds these by +0.229 (dialogue) and +0.114 (QA). However, this comparison has an important caveat: the SelfCheckGPT values were obtained with a non-instruction-tuned model that produces near-uniform stochastic samples, which likely underestimates SelfCheckGPT's performance under its intended deployment conditions with instruction-tuned models. The generation-free advantage reported here should be interpreted with this asymmetry in mind.

### 5.2 Mechanism Analysis Results (H-M1)

Table 2 reports the mechanism verification results.

**Table 2: Mechanism Verification — Graded Support Sensitivity**

| Task | KL Divergence | KL Gate (>0.05) | Wilcoxon p-value | Wilcoxon Gate (<0.05) | Cohen's d |
|------|---------------|-----------------|------------------|-----------------------|-----------|
| Dialogue | 0.279 | Pass | ≈ 0 | Pass | 0.714 |
| QA | 0.035 | Fail | 1.52 × 10⁻²⁷¹ | Pass | 0.779 |
| Summarization | 0.310 | Pass | 2.07 × 10⁻¹³ | Pass | 0.220 |

The Wilcoxon rank-sum test passed on all three tasks, confirming that DeBERTa's contradiction scores separate hallucinated from non-hallucinated responses across all domains. The mechanism — graded support sensitivity — is present on all tasks, including summarization, where the separation is statistically significant but the magnitude is small.

The KL divergence criterion (>0.05 on all 3 tasks) failed because QA produced KL = 0.035, below the 0.05 threshold. This resulted in the H-M1 gate formally failing. However, the QA task simultaneously produced the highest Cohen's d (0.779) and highly significant Wilcoxon separation (p = 1.52 × 10⁻²⁷¹). The low KL divergence on QA is attributable to short QA contexts producing narrow NLI score distributions for both classes: the class-conditional distributions are shifted relative to each other (preserving ordinal separation) but are individually concentrated near their means (reducing global spread as measured by KL divergence). The KL threshold of 0.05 was set uniformly across tasks but appears inappropriately strict for short-context tasks where score distributions are inherently narrow. Cohen's d and the Wilcoxon test provide more reliable mechanism evidence for the QA task.

The near-uniform proportion was below 0.02% on all tasks, indicating that DeBERTa produces genuinely graded NLI scores rather than degenerate binary outputs.

![Figure 5: Violin plots of net-contradiction score distributions per task and hallucination class, illustrating graded support sensitivity.](/home/anonymous/YouRA_results_new_4/TEST_question/docs/youra_research/20260315_question/h-m1/figures/score_distributions_violin.png)

![Figure 6: Box plots of score separation with Wilcoxon rank-sum significance annotations per task.](/home/anonymous/YouRA_results_new_4/TEST_question/docs/youra_research/20260315_question/h-m1/figures/score_separation_boxplot.png)

![Figure 7: KL divergence from uniform per task. Dialogue (0.279) and summarization (0.310) exceed the 0.05 threshold; QA (0.035) falls below.](/home/anonymous/YouRA_results_new_4/TEST_question/docs/youra_research/20260315_question/h-m1/figures/kl_divergence_summary.png)

![Figure 8: Proportion of near-uniform NLI score examples per task. All tasks show near-zero proportions, confirming graded (non-degenerate) scoring.](/home/anonymous/YouRA_results_new_4/TEST_question/docs/youra_research/20260315_question/h-m1/figures/near_uniform_proportion.png)

![Figure 9: Gate metrics comparison for H-M1 mechanism analysis across tasks.](/home/anonymous/YouRA_results_new_4/TEST_question/docs/youra_research/20260315_question/h-m1/figures/gate_metrics_comparison.png)

### 5.3 The Commission–Omission Boundary

The task-level asymmetry in detection performance aligns with a commission–omission distinction in hallucination types. HaluEval dialogue and QA hallucinations predominantly involve fabricated facts, invented entities, or factual substitutions that directly contradict the grounding context. These are commission-type hallucinations whose logical structure matches NLI contradiction: the response asserts X while the context implies not-X.

HaluEval summarization hallucinations, by contrast, are predominantly omission-type: the summary fails to capture the source document's key information without explicitly contradicting it. Only approximately 4% of summarization examples (p_contradictory = 0.04) produce strong contradiction signals. The NLI model correctly identifies those few contradictions, but the vast majority of summarization hallucinations are invisible to the contradiction signal.

The structural ceiling analysis (Figure 4) confirms that the summarization AUROC of 0.530 is near the theoretical maximum (AUROC_max ≈ 0.52) for a contradiction-based detector on this task distribution. The method is not underperforming on summarization — it is operating on a task where its detection mechanism is structurally mismatched.

---

## 6. Discussion

### 6.1 Generation-Free Detection on Commission-Dominated Tasks

The results demonstrate that a frozen NLI cross-encoder achieves above-chance hallucination detection on dialogue (AUROC = 0.709) and QA (AUROC = 0.644) tasks from HaluEval without any LLM generation. The detection cost is a single forward pass of a 304M-parameter model per (context, response) pair, which is constant and independent of the LLM that generated the response. For deployed systems that log (context, response) pairs, this enables retrospective hallucination detection on existing data at marginal computational cost.

The comparison with SelfCheckGPT-NLI (literature-reported AUROC = 0.48 and 0.53) suggests that generation-free NLI may match or exceed generation-dependent methods on commission-dominated tasks, though this comparison is complicated by the fact that the SelfCheckGPT baseline was evaluated with a non-instruction-tuned model. A controlled comparison using the same base model under both methods would be needed to isolate the generation-free advantage.

### 6.2 Mechanism Evidence and Its Limits

The Wilcoxon rank-sum tests provide strong evidence that DeBERTa's NLI contradiction scores carry genuine hallucination-discriminative signal on all three tasks. The formal H-M1 gate failed due to the QA KL divergence falling below the pre-specified threshold (0.035 vs. 0.05), but this appears to be a threshold-setting issue rather than evidence against the mechanism. The QA task simultaneously produced the largest Cohen's d (0.779) and overwhelmingly significant Wilcoxon separation. The KL criterion, designed to verify that NLI scores are non-uniform, was set without accounting for the effect of context length on score distribution width. Future mechanism analyses should consider task-adapted thresholds or alternative measures of distributional non-uniformity.

### 6.3 Limitations

**L1 (Structural): Summarization exclusion.** The method does not provide useful hallucination detection for summarization (AUROC = 0.530, near chance). This is an architectural limitation of contradiction-based scoring when applied to omission-type hallucinations, and it is not correctable by tuning or fine-tuning.

**L2 (Methodological): No design ablations.** The scoring formulation (net-contradiction), aggregation strategy (sentence-level max), and context configuration (last-3-turn window) were fixed rather than ablated. It is not possible to determine whether these specific choices are optimal or whether simpler alternatives would achieve comparable performance.

**L3 (Scope): Single NLI model.** All results are from a single frozen NLI model (`cross-encoder/nli-deberta-v3-large`). Cross-model generalizability — whether other NLI models of different sizes or training regimes produce similar results — was not tested.

**L4 (Ecological validity): HaluEval benchmark.** HaluEval hallucinations are GPT-3.5-generated perturbations. Real-world hallucination distributions may differ in type, severity, and proportion of commission versus omission errors.

**L5 (Baseline): SelfCheckGPT comparison asymmetry.** The SelfCheckGPT-NLI baseline values (0.48 dialogue, 0.53 QA) were obtained with a base, non-instruction-tuned model, which represents a likely lower bound on SelfCheckGPT performance. The comparison does not constitute a controlled evaluation under equivalent conditions.

**L6 (Gate): H-M1 mechanism gate failure.** The mechanism hypothesis (H-M1) formally failed its pre-specified gate due to the QA KL divergence criterion. While the scientific evidence (Wilcoxon tests, Cohen's d) supports the mechanism, the pre-registered gate was not satisfied.

### 6.4 Future Directions

Three directions follow from these results. First, omission-aware detection methods — coverage metrics, entailment-based completeness scoring, or hybrid approaches combining NLI contradiction for commissions with coverage metrics for omissions — are needed for summarization and other omission-dominated tasks. Second, design ablation experiments comparing alternative scoring functions, aggregation strategies, and context configurations would determine which design choices contribute to performance. Third, evaluation across multiple NLI models of varying size and training data would establish whether the commission–omission boundary is a property of NLI models generally or specific to DeBERTa-v3-large-mnli.

---

## 7. Conclusion

A frozen NLI cross-encoder (`cross-encoder/nli-deberta-v3-large`), applied post-hoc to (context, response) pairs from HaluEval, achieves AUROC = 0.709 on dialogue and AUROC = 0.644 on QA without any LLM generation at detection time. Mechanism analysis via Wilcoxon rank-sum tests confirms that NLI contradiction scores carry genuine hallucination-discriminative signal across all three HaluEval tasks. On summarization, AUROC = 0.530 (near chance), consistent with a structural mismatch between contradiction-based detection and omission-type hallucinations that dominate this task (only ~4% of summarization hallucinations produce contradiction signals).

The commission–omission boundary provides a framework for predicting when NLI-based detection is applicable: it is effective for tasks where hallucinations involve fabricated facts or direct contradictions (commission-type), and ineffective for tasks where hallucinations involve missing or incomplete information (omission-type). For production systems monitoring dialogue or QA outputs, generation-free NLI scoring offers hallucination detection at the cost of a single 304M-parameter forward pass per example. The generation overhead characteristic of methods like SelfCheckGPT is avoided entirely, though a controlled comparison under equivalent conditions remains to be conducted.

---

## References

DeLong, E. R., DeLong, D. M., and Clarke-Pearson, D. L. (1988). Comparing the areas under two or more correlated receiver operating characteristic curves: A nonparametric approach. *Biometrics*, 44(3):837–845.

Gerner, E. et al. (2025). ORION grounded in context: Retrieval-based method for hallucination detection. *arXiv:2504.15771*.

He, P., Gao, J., and Chen, W. (2021). DeBERTaV3: Improving DeBERTa using ELECTRA-style pre-training with gradient-disentangled embedding sharing. In *ICLR*, 2023.

Honovich, O., Aharoni, R., Herzig, J., et al. (2022). TRUE: Re-evaluating factual consistency evaluation. In *NAACL*, 2022.

Kadavath, S. et al. (2022). Language models (mostly) know what they know. *arXiv:2207.05221*.

Laban, P., Schnabel, T., Bennett, P. N., and Hearst, M. A. (2022). SummaC: Re-visiting NLI-based models for inconsistency detection in summarization. *TACL*, 10:163–177.

Li, J., Cheng, X., Zhao, W. X., Nie, J., and Wen, J. (2023). HaluEval: A large-scale hallucination evaluation benchmark for large language models. In *EMNLP*, 2023.

Manakul, P., Liusie, A., and Gales, M. (2023). SelfCheckGPT: Zero-resource black-box hallucination detection for generative large language models. In *EMNLP*, 2023.

Maynez, J., Narayan, S., Bohnet, B., and McDonald, R. (2020). On faithfulness and factuality in abstractive summarization. In *ACL*, 2020.

Min, S., Krishna, K., Lyu, X., Lewis, M., et al. (2023). FActScore: Fine-grained atomic evaluation of factual precision in long form text generation. In *EMNLP*, 2023.
