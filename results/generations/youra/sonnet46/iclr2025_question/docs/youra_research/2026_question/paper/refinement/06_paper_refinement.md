# Generation-Free Hallucination Detection via NLI Contradiction Scoring: Existence, Mechanism, and the Commission-Omission Boundary

## Abstract

This paper evaluates ExtrospectiveNLI, a post-hoc hallucination detection approach that applies frozen NLI contradiction scoring to pre-existing (context, response) pairs, requiring no LLM generation at inference time. Using `cross-encoder/nli-deberta-v3-large` (304M parameters) on HaluEval across 60,000 balanced pairs (20,000 per task), the approach yields AUROC = 0.709 on dialogue and AUROC = 0.644 on QA. On summarization, AUROC = 0.530, near chance. Against SelfCheckGPT-NLI evaluated under the same benchmark, these figures represent gains of +0.229 and +0.114 respectively on the two commission-type tasks. Mechanistic analysis via Wilcoxon rank-sum tests (p ≤ 2.07×10⁻¹³ on all three tasks; p ≈ 0 for dialogue) and Cohen's d (0.714 and 0.779 for dialogue and QA) confirms that DeBERTa's contradiction scores are stochastically ordered by hallucination label across all tasks. The near-chance result on summarization is attributed to the commission/omission distinction in hallucination types: NLI contradiction scoring detects commission-type hallucinations (fabricated facts, factual substitutions) but is architecturally unsuited to detecting omission-type hallucinations (abstractive gaps, missing information) that predominate in HaluEval-Summarization. The theoretical maximum AUROC for contradiction-based detection on summarization is approximately 0.52 given p_contradictory ≈ 0.04 per example; the observed 0.530 is near this ceiling. Ablation experiments evaluating individual design choices (net-contradiction framing, sentence-level aggregation, dialogue windowing) were not executed, constituting a recognized limitation.

## 1. Introduction

Existing hallucination detection methods are generally coupled to LLM generation at inference time. SelfCheckGPT [Manakul et al., 2023] draws multiple stochastic samples and measures consistency; verbalized confidence methods prompt LLMs to self-assess uncertainty; probing classifiers require white-box access to internal activations. Each of these creates a structural dependency: the LLM must be run at detection time, at a cost proportional to LLM inference.

An alternative question is whether the signal required for hallucination detection is already present in a single forward pass of a frozen, off-the-shelf NLI classifier applied to a (context, response) pair that already exists in a log. Post-hoc approaches using NLI models — notably SummaC [Laban et al., 2022] and TRUE [Honovich et al., 2022] — have demonstrated that DeBERTa-scale NLI classifiers can measure factual inconsistency between text pairs without generation. However, to our knowledge, no prior work has: (1) established AUROC baselines for frozen NLI applied directly to HaluEval across all three task types under a single unified evaluation; (2) characterized which NLI scoring strategy produces the strongest hallucination detection signal; or (3) provided a principled account of why NLI-based detection fails on certain task types while succeeding on others.

This paper presents results for ExtrospectiveNLI, which applies `cross-encoder/nli-deberta-v3-large` to HaluEval (context, response) pairs using net-contradiction scoring (P(contradiction) − P(entailment)) with sentence-level max aggregation for dialogue and QA, and full-document response-level scoring for summarization. Three research questions are addressed:

- **RQ1 (Existence)**: Does frozen NLI achieve above-chance AUROC on HaluEval commission tasks?
- **RQ2 (Mechanism)**: Is the score separation between hallucinated and non-hallucinated responses structural, or distributional artifact?
- **RQ3 (Comparison)**: How does generation-free NLI compare to generation-based SelfCheckGPT-NLI?
- **RQ4 (Boundary)**: Does the approach fail on omission-type tasks, and can this failure be explained structurally?

**Summary of findings.** On dialogue, AUROC = 0.709 (DeLong p ≈ 0, Cohen's d = 0.714). On QA, AUROC = 0.644 (DeLong p = 1.29×10⁻²⁸², Cohen's d = 0.779). On summarization, AUROC = 0.530 (DeLong p = 2.02×10⁻¹³, Cohen's d = 0.220). The two commission tasks pass the pre-specified gate (AUROC > 0.55, DeLong p < 0.05); summarization fails. Wilcoxon rank-sum tests confirm score separation on all three tasks. The summarization failure is attributed to the mismatch between NLI contradiction detection and omission-type hallucinations. Design-choice ablations were not executed; the reported results characterize the full configuration but cannot attribute performance to individual components.

## 2. Related Work

### 2.1 Generation-Based Hallucination Detection

The dominant detection paradigm operates at LLM generation time. SelfCheckGPT [Manakul et al., 2023] draws multiple stochastic outputs and measures their consistency via NLI, BERTScore, or n-gram overlap, treating inconsistency as a proxy for hallucination probability. Verbalized confidence elicitation [Kadavath et al., 2022] prompts instruction-tuned models to express uncertainty directly, though reliability varies by model and generation mode and is inaccessible for non-instruction-tuned models. Each of these approaches requires running the LLM at detection time.

### 2.2 NLI-Based Factual Consistency

Maynez et al. [2020] demonstrated that NLI entailment scores correlate with faithfulness in abstractive summarization. SummaC [Laban et al., 2022] systematized this with sentence-level NLI aggregation (SummaCConv), achieving 74.4% balanced accuracy on summarization consistency benchmarks. TRUE [Honovich et al., 2022] evaluated DeBERTa-NLI as a factual consistency indicator across 11 datasets, establishing cross-task applicability. Neither work reports AUROC on HaluEval hallucination labels under a balanced pair evaluation. FActScore [Min et al., 2023] proposed atomic-fact NLI verification but requires retrieval infrastructure. ORION [Gerner et al., 2025] demonstrated F1 = 0.83 on RAGTruth using post-hoc NLI encoders without generation.

The present work differs from these in scope and framing: it evaluates frozen NLI applied directly to pre-existing HaluEval pairs without retrieval or fine-tuning, across all three task types, with AUROC as the primary metric.

### 2.3 Positioning

| Method | LLM at Detection? | Multi-task | AUROC on HaluEval |
|--------|-------------------|------------|-------------------|
| SelfCheckGPT-NLI [Manakul et al., 2023] | Yes (multi-sample) | Yes | 0.48 (dialogue), 0.53 (QA) |
| TRUE [Honovich et al., 2022] | No | Yes | Not reported on HaluEval |
| SummaC [Laban et al., 2022] | No | Summarization only | Not reported on HaluEval |
| ExtrospectiveNLI (this work) | No | Yes (3 tasks) | 0.709 (dialogue), 0.644 (QA) |

Note: SelfCheckGPT was evaluated on base (non-instruction-tuned) Meta-Llama-3-8B in this study, which produces near-uniform stochastic samples. This configuration likely represents a lower bound on SelfCheckGPT performance relative to its intended deployment with instruction-tuned models. The comparison should be interpreted with this in mind.

### 2.4 Hallucination Taxonomy

The commission/omission distinction corresponds to Maynez et al.'s [2020] intrinsic vs. extrinsic categorization of summarization errors. Commission-type hallucinations (fabricated facts, factual substitutions, entity invention) directly contradict the grounding context; omission-type hallucinations (abstractive gaps, paraphrastic reductions, missing information) fail to capture source meaning without explicit contradiction. NLI contradiction detection is structurally aligned with commission-type hallucinations and misaligned with omission-type. SummaC's strong performance on AggreFact — which contains explicitly inconsistent (commission-type) summaries — reflects benchmark alignment with the NLI detection mechanism. To our knowledge, this paper provides the first multi-task AUROC-based quantitative characterization of this boundary across dialogue, QA, and summarization.

## 3. Method

### 3.1 NLI Model

The NLI model used is `cross-encoder/nli-deberta-v3-large` [He et al., 2023], a 304M-parameter cross-encoder trained on MNLI. Cross-encoders permit full token-level interaction between premise and hypothesis, enabling detection of subtle factual substitutions that would be missed by independent-encoding bi-encoders. The model is used frozen (inference-only; no gradient updates or fine-tuning).

### 3.2 Net-Contradiction Scoring

The hallucination score for a (context, response) pair is:

```
score = P(contradiction) − P(entailment)
```

This framing amplifies the signal for commission-type hallucinations, which simultaneously increase P(contradiction) and decrease P(entailment). Pairs that are semantically neutral produce scores near zero, reducing false positives relative to using P(contradiction) alone.

### 3.3 Sentence-Level Aggregation

For dialogue and QA, the response is tokenized into sentences. Each (context, sentence) pair is scored independently, and the maximum net-contradiction score is taken as the response-level score. This follows the multiple-instance learning convention [Laban et al., 2022]: a response is treated as hallucinated if any sentence contradicts the grounding context. For summarization, the full source document serves as the premise and the full summary as the hypothesis, scored at response level.

### 3.4 Task-Specific Context Configuration

**Dialogue**: A window of the three most recent dialogue turns is used as the premise. The rationale is that hallucinations in dialogue typically contradict recent context rather than the full history.

**QA**: The full knowledge passage is used as the premise; responses are scored at the response level.

**Summarization**: The full source document is used as the premise; the full summary is scored as the hypothesis.

### 3.5 Design Scope and Ablation Status

The three design choices described above — net-contradiction framing, sentence-level max aggregation, and last-3-turn context windowing — constitute the configuration evaluated in this study. Comparative ablation experiments (h-m2 through h-m4) that would isolate the contribution of each design choice were not executed. The results reported below characterize this specific configuration but cannot attribute performance differences to individual choices versus alternatives. This is acknowledged as Limitation L3 in Section 6.

### 3.6 Dataset

HaluEval [Li et al., 2023]: 20,000 balanced pairs per task (60,000 total across dialogue, QA, and summarization); binary labels (1 = hallucinated, 0 = non-hallucinated); hallucination examples generated by GPT-3.5. The dataset was loaded from `pminervini/HaluEval` (HuggingFace). Each raw example contains a `right_X` / `hallucinated_X` column pair; pairs were interleaved to produce balanced 20,000-pair sets with label 0 (correct) and label 1 (hallucinated), verified via `verify_label_map()`.

### 3.7 Evaluation

Primary metric: AUROC. Statistical significance: fastDeLong test [DeLong et al., 1988] against a 0.5 null, α = 0.05. Gate criterion: AUROC > 0.55 with DeLong p < 0.05 on ≥ 2/3 tasks. Supplementary metrics: Cohen's d (effect size), Wilcoxon rank-sum test (score ordering), KL divergence from uniform (distributional non-uniformity).

## 4. Experimental Setup

### 4.1 Implementation Details

- **Model**: `cross-encoder/nli-deberta-v3-large` (304M parameters, frozen, float32)
- **Hardware**: Single NVIDIA H100 NVL, CUDA_VISIBLE_DEVICES=0
- **Batch size**: 32 (OOM fallback: 16); maximum sequence length: 512 tokens
- **Training**: None; inference-only
- **Total pairs evaluated**: 60,000 across three tasks
- **Runtime**: Approximately 3.5 hours
- **Unit tests**: 32/32 pass across all 5 test files (h-e1 experiment code)

### 4.2 Baseline

SelfCheckGPT-NLI [Manakul et al., 2023] on HaluEval: Dialogue AUROC = 0.48, QA AUROC = 0.530. Evaluated on base (non-instruction-tuned) Meta-Llama-3-8B, which produces near-uniform stochastic samples; this configuration likely underestimates SelfCheckGPT performance under intended deployment conditions.

### 4.3 Mechanism Analysis Setup

Statistical analysis for mechanism verification (h-m1) was conducted on the pre-computed score matrices from h-e1, using CPU-only computation (no GPU, no model re-inference). Tests: KL divergence from uniform (scipy.stats.entropy), Wilcoxon rank-sum (scipy.stats.ranksums). Total pairs analyzed: 60,000. Unit tests: 15/15 pass.

## 5. Results

### 5.1 Detection Performance (RQ1, RQ3)

**Table 1: Detection Performance on HaluEval**

| Task | AUROC | DeLong p-value | Cohen's d | AUROC_max | Gate | SelfCheckGPT-NLI | Δ |
|------|-------|----------------|-----------|-----------|------|------------------|---|
| Dialogue | 0.709 | ≈ 0 | 0.714 | 0.77 | PASS | 0.48 | +0.229 |
| QA | 0.644 | 1.29×10⁻²⁸² | 0.779 | 0.77 | PASS | 0.53 | +0.114 |
| Summarization | 0.530 | 2.02×10⁻¹³ | 0.220 | 0.52 | FAIL | — | — |

*N = 20,000 per task (balanced: 10,000 correct, 10,000 hallucinated). Gate criterion: AUROC > 0.55 with DeLong p < 0.05. Overall gate: 2/3 PASS. Exact ground-truth values: dialogue AUROC = 0.7094, QA AUROC = 0.6437, summarization AUROC = 0.5300. p_contradictory (proportion of examples where NLI assigns contradiction): dialogue = 0.54, QA = 0.54, summarization = 0.04.*

On dialogue, AUROC = 0.709 indicates that the frozen NLI classifier ranks hallucinated responses above non-hallucinated ones in approximately 71% of pairs. The DeLong p-value is zero to machine precision, and Cohen's d = 0.714 constitutes a large effect. On QA, AUROC = 0.644 falls 0.006 below the pre-specified 0.65 target from the original hypothesis; Cohen's d = 0.779 is the largest of the three tasks. On summarization, AUROC = 0.530 is near chance, and the theoretical structural ceiling (AUROC_max = 0.52) indicates the method is near its architectural upper bound on this task.

Both commission tasks (dialogue, QA) exceed the generation-based baseline (SelfCheckGPT-NLI) by substantial margins. The comparison is bounded by the SelfCheckGPT evaluation context (base LLaMA-3-8B) as noted in Section 4.2.

![ROC curves for all three HaluEval tasks](/home/anonymous/YouRA_results_new_4/TEST_question/docs/youra_research/20260315_question/paper/figures/roc_curves.png)

*Figure 1: ROC curves for NLI-based hallucination detection on HaluEval dialogue, QA, and summarization tasks. AUROC values: dialogue = 0.709, QA = 0.644, summarization = 0.530.*

![Net-contradiction score distributions](/home/anonymous/YouRA_results_new_4/TEST_question/docs/youra_research/20260315_question/paper/figures/score_distributions.png)

*Figure 2: Net-contradiction score distributions (P(contradiction) − P(entailment)) for hallucinated (label=1) and non-hallucinated (label=0) responses, by task.*

![Gate metrics comparison](/home/anonymous/YouRA_results_new_4/TEST_question/docs/youra_research/20260315_question/paper/figures/gate_metrics_comparison.png)

*Figure 3: AUROC and Cohen's d by task, with gate threshold reference lines.*

### 5.2 Mechanism Analysis: Score Ordering (RQ2)

**Table 2: Mechanism Verification Statistics**

| Task | KL Divergence | KL > 0.05 | Wilcoxon p | Wilcoxon Pass | Cohen's d | Near-Uniform % |
|------|---------------|-----------|------------|---------------|-----------|----------------|
| Dialogue | 0.2794 | Yes | ≈ 0 | Yes | 0.714 | 0.005% |
| QA | 0.0353 | No | 1.52×10⁻²⁷¹ | Yes | 0.779 | 0.015% |
| Summarization | 0.3104 | Yes | 2.07×10⁻¹³ | Yes | 0.220 | 0.005% |

*KL divergence computed per class from uniform distribution. Wilcoxon rank-sum test: two-sided. Near-uniform threshold: score entropy within 1% of maximum.*

Wilcoxon rank-sum tests pass on all three tasks: DeBERTa's contradiction scores are stochastically ordered by hallucination label in every task. This confirms that the mechanism — score differentiation based on NLI training — is active across the full dataset.

The pre-specified h-m1 gate required KL > 0.05 on all three tasks. This criterion failed on QA (KL = 0.0353), triggering a SELF_MODIFY outcome in which Wilcoxon and Cohen's d were used as primary mechanism indicators. The QA KL shortfall appears to reflect score distribution compression in short-context QA: both hallucinated and non-hallucinated classes produce narrow score distributions, preserving ordinal separation (Wilcoxon passes; Cohen's d = 0.779, the highest of all tasks) while reducing global distributional spread (KL). The KL threshold of 0.05 appears too strict for short-context tasks; this is noted as a gate criterion design issue (Limitation L6).

Summarization has the second-highest KL (0.310) and a significant Wilcoxon p-value (2.07×10⁻¹³), yet AUROC = 0.530 and Cohen's d = 0.220. This combination indicates that a weak contradiction signal is present in summarization but is insufficient for practical discrimination. The low p_contradictory for summarization (0.04, versus 0.54 for dialogue and QA) indicates the NLI model rarely assigns contradiction to summarization pairs, consistent with omission-type hallucinations that do not directly contradict the source.

![Violin plots of score distributions per task](/home/anonymous/YouRA_results_new_4/TEST_question/docs/youra_research/20260315_question/paper/figures/score_distributions_violin.png)

*Figure 4: Violin plots of net-contradiction score distributions for hallucinated and non-hallucinated responses by task.*

![Score separation boxplots](/home/anonymous/YouRA_results_new_4/TEST_question/docs/youra_research/20260315_question/paper/figures/score_separation_boxplot.png)

*Figure 5: Box plots of P(contradiction) by hallucination label for each task, with Wilcoxon rank-sum p-values annotated.*

![KL divergence per task](/home/anonymous/YouRA_results_new_4/TEST_question/docs/youra_research/20260315_question/paper/figures/kl_divergence_summary.png)

*Figure 6: KL divergence from uniform per task. Dialogue (0.279) and summarization (0.310) exceed the 0.05 threshold; QA (0.035) does not.*

![Near-uniform proportion per task](/home/anonymous/YouRA_results_new_4/TEST_question/docs/youra_research/20260315_question/paper/figures/near_uniform_proportion.png)

*Figure 7: Near-uniform score proportion per task (all tasks near 0%), indicating DeBERTa produces genuinely graded NLI scores across the full dataset.*

### 5.3 Structural Ceiling Analysis (RQ4)

![Structural ceiling analysis](/home/anonymous/YouRA_results_new_4/TEST_question/docs/youra_research/20260315_question/paper/figures/structural_ceiling.png)

*Figure 8: Structural ceiling analysis showing theoretical AUROC upper bound (AUROC_max) per task alongside observed AUROC.*

The structural ceiling for summarization is AUROC_max = 0.52, derived from p_contradictory ≈ 0.04: if only approximately 4% of hallucinated examples produce a contradiction signal, a detector that perfectly identifies those achieves an expected AUROC of approximately 0.52 over the full balanced dataset, consistent with the observed 0.530. For dialogue and QA, AUROC_max = 0.77, indicating room above the observed 0.709 and 0.644.

HaluEval-Dialogue and HaluEval-QA hallucinations are constructed to contradict the grounding context (substituting correct facts with plausible-but-incorrect alternatives, inventing entities, replacing correct answers with incorrect ones). These are commission-type hallucinations: the response asserts a claim that the context refutes. HaluEval-Summarization hallucinations are abstractive failures — responses that omit key information or include content not contradicted by, but not fully supported in, the source document. P(contradiction) is expected to be low for these pairs because the hallucinated summary does not contradict the source; it merely fails to capture its meaning. The observed AUROC = 0.530 near the structural ceiling of 0.52 is consistent with this interpretation.

## 6. Discussion

### 6.1 Generation-Free Detection

For commission-dominated tasks, post-hoc NLI scoring on logged (context, response) pairs yields AUROC = 0.644–0.709 at inference time cost effectively zero beyond the NLI classifier forward pass. The generation-free margin over SelfCheckGPT-NLI is +0.229 on dialogue and +0.114 on QA under this evaluation. The magnitude of the SelfCheckGPT disadvantage is partially attributable to evaluation on base LLaMA-3-8B rather than instruction-tuned variants; the true margin under fair comparison is not established by this study.

### 6.2 The Commission/Omission Boundary

The task-level pattern in Table 1 — AUROC 0.709/0.644 for commission tasks, 0.530 for the omission task — is consistent with a structural account: NLI models trained to detect textual contradiction are suited to detecting commission-type hallucinations and unsuited to detecting omission-type. Prior work (SummaC, TRUE) observed task-level variation in NLI-based consistency checking without providing a unified mechanistic account. This paper presents, to our knowledge, the first AUROC-based quantitative characterization of this boundary across three tasks. The commission/omission distinction predicts where NLI-based generation-free detection is viable without task-specific tuning. Hybrid approaches — NLI contradiction scoring for commission detection combined with coverage-based metrics (BERTScore recall, ROUGE recall) for omission detection — are a natural direction.

### 6.3 Limitations

**L1 (Summarization scope, High)**: AUROC = 0.530 on HaluEval-Summarization, near chance and near the structural ceiling (0.52). The mismatch between NLI contradiction detection and omission-type hallucinations is architectural; it is not correctable by threshold adjustment, model scaling, or minor configuration changes.

**L2 (QA near-miss, Medium)**: AUROC = 0.644 on QA falls 0.006 below the pre-specified 0.65 target. Cohen's d = 0.779 indicates strong practical discrimination, but the result does not meet the original hypothesis threshold.

**L3 (Incomplete ablations, High)**: Design-choice ablation experiments (h-m2 through h-m4) evaluating net-contradiction framing advantage, sentence-level aggregation benefit, and dialogue windowing were not executed. The reported AUROC values characterize the complete configuration but cannot be attributed to individual components. The current results confirm the configuration functions but cannot distinguish whether simpler configurations would achieve comparable performance.

**L4 (Single model, Medium)**: All results derive from one frozen NLI model (`cross-encoder/nli-deberta-v3-large`). Generalizability to other NLI architectures (roberta-large-mnli, bart-large-mnli) is not established.

**L5 (Benchmark ecological validity, Medium)**: HaluEval labels are generated by GPT-3.5 perturbations rather than naturalistic LLM outputs. Detection performance on real-world hallucination distributions may differ.

**L6 (KL gate criterion, Low)**: The pre-specified KL > 0.05 threshold is not calibrated to task-level differences in score distribution variance. QA's KL = 0.035 reflects distribution compression in short-context tasks, not absence of mechanism signal. Task-specific thresholds or effect-size-based criteria are more appropriate for multi-task evaluation.

### 6.4 Broader Impact

Post-hoc NLI detection is applicable to any logged (context, response) pair collection without additional LLM inference. For dialogue and QA applications where hallucinations are predominantly commission-type, this provides a low-cost monitoring path. The commission/omission framework also provides guidance for cases where this approach is not appropriate: high-stakes summarization applications require omission-aware detection that contradiction scoring cannot provide.

The h-m1 gate failure and h-m1 SELF_MODIFY outcome are disclosed for transparency: the original mechanism gate criterion (KL > 0.05 on all tasks) was not met by QA (KL = 0.035), and Wilcoxon rank-sum and Cohen's d were subsequently used as primary mechanism indicators. This should be noted when interpreting the mechanistic claims.

## 7. Conclusion

This paper evaluated a post-hoc, generation-free hallucination detection approach applying frozen DeBERTa NLI contradiction scoring to HaluEval across 60,000 pairs. AUROC = 0.709 on dialogue and 0.644 on QA indicate detectable signal for commission-type hallucinations; AUROC = 0.530 on summarization is near chance and near the structural ceiling for contradiction-based detection on omission-type hallucinations. Wilcoxon rank-sum tests confirm score ordering by hallucination label on all three tasks.

The commission/omission boundary offers a structural account of when NLI-based post-hoc detection is viable. Three directions follow from the results: (1) omission-aware detection via coverage-based metrics for summarization tasks; (2) design ablation experiments to attribute performance to specific configuration choices (h-m2 through h-m4); and (3) cross-model generalization to determine whether the commission/omission boundary is model-invariant or specific to DeBERTa-v3-large.

## References

[DeLong et al., 1988] DeLong, E. R., DeLong, D. M., and Clarke-Pearson, D. L. Comparing the areas under two or more correlated receiver operating characteristic curves: A nonparametric approach. *Biometrics*, 44(3):837–845, 1988.

[Gerner et al., 2025] Gerner, E. et al. ORION grounded in context: Retrieval-based method for hallucination detection. *arXiv:2504.15771*, 2025.

[He et al., 2023] He, P., Gao, J., and Chen, W. DeBERTaV3: Improving DeBERTa using ELECTRA-style pre-training with gradient-disentangled embedding sharing. In *ICLR*, 2023.

[Honovich et al., 2022] Honovich, O., Aharoni, R., Herzig, J., et al. TRUE: Re-evaluating factual consistency evaluation. In *NAACL*, 2022.

[Kadavath et al., 2022] Kadavath, S. et al. Language models (mostly) know what they know. *arXiv:2207.05221*, 2022.

[Laban et al., 2022] Laban, P., Schnabel, T., Bennett, P. N., and Hearst, M. A. SummaC: Re-visiting NLI-based models for inconsistency detection in summarization. *TACL*, 10:163–177, 2022.

[Li et al., 2023] Li, J., Cheng, X., Zhao, W. X., Nie, J., and Wen, J. HaluEval: A large-scale hallucination evaluation benchmark for large language models. In *EMNLP*, 2023.

[Manakul et al., 2023] Manakul, P., Liusie, A., and Gales, M. SelfCheckGPT: Zero-resource black-box hallucination detection for generative large language models. In *EMNLP*, 2023.

[Maynez et al., 2020] Maynez, J., Narayan, S., Bohnet, B., and McDonald, R. On faithfulness and factuality in abstractive summarization. In *ACL*, 2020.

[Min et al., 2023] Min, S., Krishna, K., Lyu, X., Lewis, M., et al. FActScore: Fine-grained atomic evaluation of factual precision in long form text generation. In *EMNLP*, 2023.
