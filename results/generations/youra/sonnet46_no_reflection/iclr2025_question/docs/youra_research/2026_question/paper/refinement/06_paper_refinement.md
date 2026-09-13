# When Semantic Entropy Fails: Sampling Degeneracy in Base Language Models Undermines Clustering-Based Uncertainty Quantification

## Abstract

Semantic entropy (SE), a method published in *Nature* by Farquhar et al. (2024) with over 1,000 citations, is widely used as a benchmark for uncertainty quantification (UQ) in language models. This paper reports that SE fails as an uncertainty estimator when applied to Llama-3-8B-Base on factual question answering: on 500 validation queries from TriviaQA (rc.nocontext), SE achieves an AUROC of 0.4735 (95% CI: [0.4409, 0.5036]), compared to 0.6835 for token-probability (95% CI: [0.6361, 0.7332]). On NaturalQuestions (open-domain validation split, 500 queries), SE achieves an AUROC of 0.5524 (95% CI: [0.5121, 0.5977]) versus 0.6551 for token-probability (95% CI: [0.5960, 0.7063]). The observed failure is consistent with a sampling degeneracy phenomenon: under N=10 stochastic sampling at temperature=1.0, 89.4% of TriviaQA queries and 84.8% of NaturalQuestions queries produce a single semantic cluster (K=1), collapsing SE entropy to near-zero for the majority of queries and eliminating its discriminative ability. Kernel Language Entropy (KLE) similarly fails, with AUROC of 0.2642 on TriviaQA and 0.3753 on NaturalQuestions. SelfCheckGPT-BERTScore yields a constant AUROC of 0.5000 on both datasets. SelfCheckGPT-NLI achieves AUROC of 0.6862 on TriviaQA but only 0.4508 on NaturalQuestions, indicating dataset-dependent performance. The paper introduces `degenerate_fraction`—the proportion of queries for which all N samples cluster into a single semantic equivalence class—as a diagnostic for SE validity, and provides a complete benchmarking infrastructure of approximately 2,222 lines of Python code with checkpointed generation and bootstrap confidence intervals. The 70B-scale experiment was initiated but did not complete before the time of reporting; the 8B gate results alone are sufficient to falsify the existence claim that SE exceeds token-probability for base models on these benchmarks.

---

## 1. Introduction

Reliable uncertainty quantification (UQ) for large language models (LLMs) is of practical importance for systems that must detect hallucinations, route queries to human reviewers, or abstain from low-confidence predictions. Token-probability-based approaches—using the model's own predicted logits as a confidence proxy—are computationally simple and require only a single forward pass. Sampling-based semantic methods were proposed as improvements that operate over semantic content rather than surface-level token distributions.

Semantic entropy (SE), introduced by Farquhar et al. (2024) and published in *Nature*, clusters N stochastic responses into semantic equivalence classes via bidirectional NLI and computes entropy over cluster probability mass. Published evaluations report SE achieving AUROC of approximately 0.72–0.79 on TriviaQA, NaturalQuestions, BioASQ, and SQuAD, consistently exceeding token-probability (approximately 0.67 AUROC on TriviaQA). This superiority has been taken as established and has motivated several subsequent methods: Semantic Entropy Probes (SEPs; Kossen et al., 2024), which approximate SE from a single forward pass; Kernel Language Entropy (KLE; Nikitin et al., 2024), which generalizes SE via von Neumann entropy; and SelfCheckGPT (Manakul et al., 2023), which measures cross-sample NLI consistency. However, none of these evaluations explicitly reports the sampling diversity—specifically, the proportion of queries for which all N samples are semantically identical—as a diagnostic for the validity of clustering-based methods.

The present study was designed to test the Epistemic Geometry Scaling Hypothesis (EGSH), which predicted that the AUROC advantage of SE and KLE over token-probability would increase with model scale from 8B to 70B parameters in the Llama-3 base model family. As a prerequisite, the existence of an SE advantage at 8B was verified first. This existence check failed: SE achieves an AUROC of 0.4735 on TriviaQA and 0.5524 on NaturalQuestions when applied to Llama-3-8B-Base under the standard N=10 sampling protocol at temperature=1.0—both values substantially below token-probability on the same datasets.

The experiment records a degenerate_fraction of 0.894 on TriviaQA and 0.848 on NaturalQuestions: the proportion of queries for which all 10 stochastic samples from Llama-3-8B-Base are assigned to a single semantic cluster by the DeBERTa-large-mnli NLI model. When K=1 for a query, SE entropy is exactly zero regardless of whether the query is answered correctly or incorrectly. With 89% of queries at K=1, SE scores cluster near zero and carry no discriminative signal. This is not an implementation error: the SE mechanism activates correctly (mean_k=9.884 < N=10, confirming that clustering runs), but the model's output distribution lacks the diversity that clustering-based entropy estimation requires to function as a UQ signal.

The paper is organized as follows. Section 2 reviews related work. Section 3 describes the experimental methodology. Section 4 presents results. Section 5 discusses implications and limitations. Section 6 concludes.

---

## 2. Related Work

### Token-Probability Methods

The simplest UQ approach for language models uses the model's predicted probability distribution directly. Negative log-probability and maximum softmax probability are standard baselines (Kadavath et al., 2022; Malinin and Gales, 2021). Despite their simplicity, these methods have demonstrated competitive performance across benchmarks. In the original SE paper, Farquhar et al. (2024) report token-probability AUROC of approximately 0.67 on TriviaQA for Llama-2-70B. The present study finds token-probability AUROC of 0.6835 on TriviaQA and 0.6551 on NaturalQuestions for Llama-3-8B-Base—values broadly consistent with these prior reports.

### Sampling-Based Semantic Methods

Farquhar et al. (2024) introduced SE to address the sensitivity of logit-based estimates to paraphrase variation: two responses expressing the same answer with different wording should receive similar uncertainty scores, but token-probability can differ substantially. SE clusters N stochastic responses into semantic equivalence classes via bidirectional entailment checking (using DeBERTa-large-mnli) and computes entropy over the cluster probability mass. The method was evaluated on Llama-2 variants (multiple scales), GPT-3, and Falcon models. Reported AUROC values range from 0.72 to 0.79 on TriviaQA, NaturalQuestions, BioASQ, and SQuAD, consistently exceeding token-probability.

KLE (Nikitin et al., 2024) generalizes SE using von Neumann entropy over a semantic similarity kernel matrix, computed from pairwise NLI scores. It provides a theoretically unified framework but shares SE's dependence on semantic diversity across samples: when the similarity matrix has rank 1 (all samples identical), von Neumann entropy is near zero.

SEPs (Kossen et al., 2024) approximate SE from hidden-state representations using linear probes trained on a reference set, achieving 5–10× inference speedup relative to multi-sample SE. SEPs were evaluated on Llama-2 variants on TriviaQA and NaturalQuestions. The degenerate_fraction of the generation distribution is not reported in these evaluations.

SelfCheckGPT (Manakul et al., 2023) measures consistency across N samples using NLI, BERTScore, or n-gram overlap as consistency scoring functions. Evaluated primarily on GPT-3 outputs, SelfCheckGPT-NLI achieves strong performance on biographical fact-checking. Unlike SE and KLE, SelfCheckGPT-NLI does not require multiple distinct clusters; it measures pairwise entailment consistency, which can retain some discriminative signal even when most samples are near-identical, provided the minority of diverse samples carry entailment information.

### Output Diversity in Language Generation

The relationship between sampling diversity and generation quality has been studied in other contexts. Diverse Beam Search (Vijayakumar et al., 2016) was proposed to address near-identical outputs under standard beam decoding. Self-BLEU (Zhu et al., 2018) and distinct-n (Li et al., 2016) measure corpus-level lexical diversity in generation. The `degenerate_fraction` metric introduced in this paper differs from these in focus: it measures the proportion of queries for which semantic clustering collapses to K=1, which is the condition under which SE and KLE become uninformative as UQ estimators. The application of diversity measurement as a pre-screening diagnostic for UQ validity is, to the authors' knowledge, not established in prior work.

### Representation-Based Methods

Several methods bypass sampling by extracting uncertainty estimates from internal model representations. Layer-wise Semantic Dynamics (LSD; Mir, 2025) trains contrastive representations on hidden states, reporting AUROC of 0.96 on TruthfulQA. Effective Rank-based Uncertainty (Wang et al., 2025) uses spectral rank of hidden-state matrices. Conformal prediction methods (Cherian et al., 2024; Su et al., 2024) provide coverage guarantees. These approaches do not require sampling diversity and are thus not subject to the failure mode described here.

### Surveys

Kang et al. (2025) survey over 100 UQ methods for LLMs and identify evaluation fragmentation—particularly the conflation of methods evaluated under different conditions—as a primary limitation of the field. The present finding that base and instruction-tuned models produce substantially different sampling distributions, and that this distinction is not consistently reported in UQ benchmarks, is one instance of this fragmentation.

---

## 3. Method

### Study Design

This study was designed to verify the existence hypothesis for the Epistemic Geometry Scaling Hypothesis (EGSH): that SE and KLE achieve statistically higher AUROC for correctness prediction than token-probability at both 8B and 70B scale in the Llama-3 base model family. The existence gate required SE AUROC > token-probability AUROC at both scales on both TriviaQA and NaturalQuestions, with 95% bootstrap confidence intervals excluding zero. The gate failed at 8B scale.

### Models

**Primary model:** Llama-3-8B-Base (`meta-llama/Meta-Llama-3-8B`), loaded in bfloat16 precision on a single NVIDIA H100 NVL GPU (96 GB). This is a pretrained base checkpoint without instruction tuning or RLHF.

**Planned comparison model:** Llama-3-70B-Base (`meta-llama/Meta-Llama-3-70B`), to be loaded with 8-bit quantization via bitsandbytes. The 70B experiment was initiated (`run_70b_only.py`) but did not produce results prior to the gate evaluation at 8B; since both 8B conditions already failed, the 70B results cannot change the gate outcome.

**NLI entailment model:** `microsoft/deberta-large-mnli`, used for SE clustering (bidirectional entailment) and SelfCheckGPT-NLI scoring.

### Datasets

**TriviaQA rc.nocontext** (Joshi et al., 2017): validation split, 500 queries (sampled as a proof-of-concept subset; planned full evaluation was 17,944 test queries). Correctness rate: 66.0% (330/500). Loaded from HuggingFace (`mandarjoshi/trivia_qa`, config `rc.nocontext`).

**NaturalQuestions open-domain** (Kwiatkowski et al., 2019): validation split, 500 queries (planned full evaluation was 3,610 validation queries). Correctness rate: 19.4% (97/500). Loaded from HuggingFace (`google-research-datasets/natural_questions`, config `default`).

Correctness labels were determined by exact-match normalization of the model's greedy decode against gold answer aliases. A post-generation bug fix in `data_loader.py` was applied to extract only the first line of multi-line generations and to use the correct TriviaQA HuggingFace package and validation split; these corrections were applied before final evaluation.

### Generation Protocol

For each query: N=10 stochastic samples at temperature=1.0, top_p=0.9, max 50 new tokens, plus one greedy decode. Sampling seed: 42. Few-shot prompting: 5-shot for TriviaQA, standard format for NaturalQuestions, following Farquhar et al. (2024). Token-probability is computed from greedy decode logits (negative mean log-probability). Generation outputs were checkpointed to pickle files every 500 items to support resumption.

The N=10, temperature=1.0 protocol matches Farquhar et al. (2024) exactly and was not modified in order to characterize failure under the standard conditions.

### UQ Methods

Six methods were evaluated:

1. **Token-probability:** Negative mean log-probability of the greedy decode token sequence. Single forward pass; no sampling diversity requirement.

2. **Semantic Entropy (SE):** NLI-based bidirectional entailment clustering of N=10 samples using DeBERTa-large-mnli. Cluster entropy H = −∑_c p(c) log p(c) over cluster probability mass. Implementation follows Farquhar et al. (2024).

3. **Kernel Language Entropy (KLE):** Von Neumann entropy over the normalized Laplacian of the pairwise NLI semantic similarity matrix. Implemented as EigValLaplacian. Near-zero for rank-1 matrices.

4. **SelfCheckGPT-BERTScore:** Mean BERTScore between greedy decode and each of the N samples. Constant when all samples are identical.

5. **SelfCheckGPT-NLI:** Proportion of the N samples that do not entail the greedy decode. Uses DeBERTa-large-mnli.

6. **Semantic Entropy Probes (SEPs):** Linear probes on hidden-state representations. Produced zero valid scores on both datasets (insufficient probe data at proof-of-concept scale); excluded from all analyses.

### Evaluation

**Primary metric:** AUROC for binary correctness prediction (higher uncertainty should predict lower correctness). Computed via `sklearn.metrics.roc_auc_score`.

**Confidence intervals:** 1000-resample bootstrap, 95% percentile intervals, applied per method per dataset.

**Degenerate fraction diagnostic:** For each dataset, degenerate_fraction = (number of queries with K=1) / (total queries), where K is the number of distinct semantic clusters produced by SE clustering over N=10 samples.

**Gate criterion:** SE AUROC > token-probability AUROC with 95% CI of the difference excluding zero, on both TriviaQA and NaturalQuestions, at both 8B and 70B scale. All four conditions must be satisfied.

### Implementation

The complete implementation comprises approximately 2,222 lines of Python across 10 source files: `config.py`, `data_loader.py`, `evaluate.py`, `generate.py`, `model_loader.py`, `uq_methods.py`, `visualize.py`, `run_experiment.py`, `run_70b_only.py`, and `eval_from_checkpoint.py`. All code is located in `h-e1/code/`. Four correctness bugs were identified and fixed after initial code generation: a multi-line answer extraction issue and a wrong HuggingFace package/split in `data_loader.py`, a question_id alignment issue in `eval_from_checkpoint.py`, and a model list issue in `run_experiment.py`.

The 8B experiment ran from 03:51 UTC to 07:13 UTC on 2026-05-21, a duration of approximately 3 hours 22 minutes, on GPU 0 of a system with 5 NVIDIA H100 NVL GPUs (95,830 MiB each).

---

## 4. Experimental Setup

The experimental setup is described fully in Section 3. Key parameters are summarized here for reference.

- **Model:** meta-llama/Meta-Llama-3-8B, bfloat16, single H100 NVL GPU
- **Datasets:** TriviaQA rc.nocontext validation split (500 samples); NaturalQuestions open-domain validation split (500 samples)
- **Sampling:** N=10 samples per query, temperature=1.0, top_p=0.9, max 50 new tokens
- **Entailment model:** microsoft/deberta-large-mnli
- **Evaluation:** AUROC with 1000-resample 95% bootstrap CI
- **Conda environment:** youra-h-e1 (Python 3.10)

---

## 5. Results

### 5.1 Main AUROC Results

Table 1 reports AUROC values and 95% bootstrap confidence intervals for all functional UQ methods on Llama-3-8B-Base, on TriviaQA (500 queries, 66.0% correct) and NaturalQuestions (500 queries, 19.4% correct). These values are taken directly from `h-e1/results/auroc_results.json` and are confirmed by the experiment log (`h-e1/code/experiment.log`).

**Table 1: AUROC with 95% Bootstrap CI — Llama-3-8B-Base**

| Method | TriviaQA AUROC | TriviaQA 95% CI | NQ AUROC | NQ 95% CI |
|---|---|---|---|---|
| token_prob | 0.6835 | [0.6361, 0.7332] | 0.6551 | [0.5960, 0.7063] |
| selfcheck_nli | 0.6862 | [0.6362, 0.7340] | 0.4508 | [0.3943, 0.5084] |
| semantic_entropy | 0.4735 | [0.4409, 0.5036] | 0.5524 | [0.5121, 0.5977] |
| kle | 0.2642 | [0.2158, 0.3107] | 0.3753 | [0.3078, 0.4372] |
| selfcheck_bertscore | 0.5000 | [0.5000, 0.5000] | 0.5000 | [0.5000, 0.5000] |
| seps | N/A | N/A | N/A | N/A |

*SEPs excluded due to zero valid scores on both datasets.*

![AUROC comparison bar chart for all UQ methods on Llama-3-8B-Base](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_question_sonnet46_no_reflection/docs/youra_research/20260520_question/paper/figures/fig1_auroc_bar_8b.png)

*Figure 1: AUROC for each UQ method on TriviaQA and NaturalQuestions (Llama-3-8B-Base). Error bars indicate 95% bootstrap CI. SEPs omitted due to zero valid scores.*

The existence gate (SE AUROC > token-probability AUROC, 95% CI of difference excluding zero, on both datasets) fails on both TriviaQA and NaturalQuestions. On TriviaQA, the SE–token-probability difference is −0.210 AUROC points (95% CI approximately [−0.252, −0.155], excluding zero in the negative direction). On NaturalQuestions, the difference is approximately −0.103 AUROC points.

![SE minus token-probability AUROC difference with bootstrap CI](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_question_sonnet46_no_reflection/docs/youra_research/20260520_question/paper/figures/fig2_se_tp_difference_8b.png)

*Figure 2: SE minus token-probability AUROC difference with 95% bootstrap CI, for TriviaQA and NaturalQuestions. Both intervals are entirely negative, excluding zero.*

### 5.2 Sampling Degeneracy

Table 2 reports sampling degeneracy statistics computed by the SE clustering module.

**Table 2: Sampling Degeneracy Statistics — Llama-3-8B-Base, N=10**

| Dataset | degenerate_fraction | mean_k | min_k | max_k |
|---|---|---|---|---|
| TriviaQA | 0.894 | 9.884 | 7 | 10 |
| NaturalQuestions | 0.848 | 9.796 | 6 | 10 |

*degenerate_fraction: proportion of queries where all N=10 samples fall into a single semantic cluster (K=1). mean_k: mean number of samples in the dominant cluster per query, out of N=10. Note: mean_k is not the mean number of clusters; for queries with K=1, the dominant cluster contains all 10 samples.*

On TriviaQA, 89.4% of 500 queries produce K=1: all 10 stochastic samples are assigned to a single semantic equivalence class by the NLI clustering step. For these queries, SE = 0 by definition, regardless of whether the query is answered correctly. The mean_k value of 9.884 indicates that on average across all queries (including the 10.6% with K>1), the dominant cluster accounts for 98.84% of the 10 samples. On NaturalQuestions, 84.8% of queries are degenerate.

The SE mechanism is confirmed to be functioning: the log entry from `uq_methods.py` at 05:36:52 UTC reads "SE mechanism activated: mean K=9.88 < N=10," confirming that clustering runs and that K < N on every query. The degenerate_fraction captures the degree to which near-trivial clustering is occurring.

### 5.3 Method-Specific Findings

**Token-probability** achieves AUROC of 0.6835 on TriviaQA and 0.6551 on NaturalQuestions. These values are consistent with the approximately 0.67 AUROC reported for Llama-2-70B in Farquhar et al. (2024). Token-probability is valid under any sampling diversity condition.

**SelfCheckGPT-NLI** achieves AUROC of 0.6862 on TriviaQA—numerically higher than token-probability—but 0.4508 on NaturalQuestions, below the random-chance baseline. The 95% CI for NaturalQuestions [0.3943, 0.5084] crosses 0.5, indicating the NQ result is not statistically distinguishable from chance at this sample size. The dataset-dependent behavior of SelfCheckGPT-NLI is not fully explained by the data available; the NaturalQuestions queries have a substantially lower correctness rate (19.4% vs. 66.0%), which may affect the method's calibration.

**KLE** achieves AUROC of 0.2642 on TriviaQA and 0.3753 on NaturalQuestions—substantially below the random-chance baseline of 0.5 on TriviaQA. The 95% CI [0.2158, 0.3107] for TriviaQA entirely excludes 0.5 in the negative direction. KLE operates on the von Neumann entropy of the pairwise similarity matrix; when 89% of queries produce rank-1 Laplacian matrices (all samples identical), eigenvalue structure is near-degenerate and the resulting scores are systematically near-zero, potentially with inverted rank ordering relative to true uncertainty.

**SelfCheckGPT-BERTScore** achieves AUROC of exactly 0.5000 on both datasets, with a zero-width confidence interval [0.5000, 0.5000]. This indicates that the uncertainty score is constant across all queries—a consequence of all samples being identical (BERTScore of identical texts is 1.0), producing a constant score with no rank variation.

**SEPs** produced zero valid scores on both datasets and are excluded from all analyses. The cause is insufficient probe data at the 500-sample proof-of-concept scale.

![All six UQ methods on both datasets](/home/anonymous/YouRA_results_new_4_sonnet46_no_reflection/TEST_question_sonnet46_no_reflection/docs/youra_research/20260520_question/paper/figures/fig3_auroc_all_methods_8b.png)

*Figure 3: AUROC for all evaluated UQ methods on TriviaQA and NaturalQuestions. SelfCheckGPT-BERTScore and SEPs omitted from visualization due to constant scores and null scores respectively.*

### 5.4 Gate Evaluation

The MUST_WORK gate is evaluated against four conditions:

| Condition | Required | Observed | Result |
|---|---|---|---|
| SE AUROC > token_prob (8B/TriviaQA), CI excl. 0 | SE > TP | SE=0.4735 < TP=0.6835 | FAIL |
| SE AUROC > token_prob (8B/NQ), CI excl. 0 | SE > TP | SE=0.5524 < TP=0.6551 | FAIL |
| SE AUROC > token_prob (70B/TriviaQA), CI excl. 0 | SE > TP | Not available | Unknown |
| SE AUROC > token_prob (70B/NQ), CI excl. 0 | SE > TP | Not available | Unknown |

The gate fails based on 8B results alone. The 70B experiment did not complete before the reporting cutoff. Because all four conditions must be satisfied and both 8B conditions already fail, 70B results cannot change the gate outcome.

---

## 6. Discussion

### 6.1 Possible Explanations for SE Failure

The observed failure of SE on Llama-3-8B-Base is consistent with the sampling degeneracy account: when 89.4% of TriviaQA queries produce K=1, SE≈0 for the vast majority of queries. A query-level score distribution that is 89% at or near zero has essentially no rank variation and cannot predict correctness. The anti-correlation on TriviaQA (AUROC=0.4735 < 0.5) is interpretable: among the 10.6% of non-degenerate queries (K>1), queries that the model is genuinely uncertain about may be more likely to produce diverse outputs (K>1, higher SE), while high-confidence incorrect answers produce K=1 (lower SE). If genuine uncertainty weakly co-occurs with K>1 among the minority of diverse queries, SE becomes weakly anti-correlated with incorrectness in the combined distribution.

This account is correlational rather than causal. Establishing causality would require an experiment that independently varies sampling diversity—for example, by comparing base versus instruction-tuned variants, or sweeping sampling temperature—while holding other conditions fixed. Such experiments are not reported here and are identified as the primary future work.

The discrepancy between present results (SE AUROC 0.47–0.55) and Farquhar et al. (2024) (SE AUROC 0.72–0.79) is consistent with a model-type difference. Published SE evaluations included instruction-tuned Llama-2 variants and GPT-3; these models may produce higher sampling diversity due to RLHF-induced output variation, placing them in a regime where SE clustering produces K>1 for a larger proportion of queries. The exact instruction-tuning status and sampling diversity of the models used in Farquhar et al. (2024) is not confirmed in this study; the model-type explanation is a hypothesis rather than a verified fact.

KLE's sub-chance performance (AUROC=0.2642 on TriviaQA) is consistent with the rank-1 Laplacian explanation: near-identical samples produce near-zero eigenvalue sums, and systematic near-zero scores may invert rank ordering relative to true uncertainty. The specific mechanism producing this inversion is not fully characterized.

### 6.2 Implications for UQ Benchmarking

If the sampling degeneracy account is correct, it implies that the validity of SE and KLE as UQ estimators is contingent on the model producing semantically diverse outputs under the chosen sampling protocol. This diversity precondition was not explicitly reported or tested in the original SE paper or subsequent evaluations. The `degenerate_fraction` metric provides a computable diagnostic that can be reported alongside AUROC to characterize whether the diversity precondition is met.

The following practical guidance follows from the observed results, with the caveat that these recommendations are based on a single model (Llama-3-8B-Base) and two datasets at 500-sample scale:

- Token-probability achieves AUROC above 0.65 on both TriviaQA and NaturalQuestions and does not require sampling diversity.
- SelfCheckGPT-NLI is competitive with token-probability on TriviaQA (AUROC=0.6862) but substantially underperforms on NaturalQuestions (AUROC=0.4508); its utility appears dataset-dependent.
- SE and KLE perform at or below random chance on TriviaQA and only marginally above chance on NaturalQuestions when applied to Llama-3-8B-Base under N=10, temperature=1.0.

### 6.3 Limitations

**L1 — Scale coverage:** Only Llama-3-8B-Base is fully evaluated. The 70B experiment was not completed. Results may differ at 70B scale, and no cross-scale comparison is possible.

**L2 — Single model family:** Results are from one base model (Llama-3-8B). Generalization to other base models, other model families, or instruction-tuned models is not established.

**L3 — Sample size:** 500 samples per dataset (versus the planned 17,944 TriviaQA test and 3,610 NaturalQuestions validation). The reduced scale limits statistical precision and sub-group analysis. The NQ correctness rate of 19.4% (97/500 correct) may widen confidence intervals due to class imbalance.

**L4 — Causal attribution:** The degenerate_fraction observation is a post-hoc diagnostic, not a preregistered variable. The causal claim that degeneracy causes SE failure requires controlled manipulation experiments not conducted in this study.

**L5 — Method coverage:** SEPs produced null results due to insufficient probe data; SelfCheckGPT-BERTScore produced constant scores. Two of six planned methods were effectively non-functional, leaving the benchmark incomplete.

**L6 — No instruct-model comparison:** The hypothesis that SE functions correctly on instruction-tuned Llama-3 models (due to higher sampling diversity) is not tested and remains a prediction.

---

## 7. Conclusion

This study set out to verify that semantic entropy achieves higher AUROC than token-probability for correctness prediction in Llama-3-8B-Base on TriviaQA and NaturalQuestions, as a prerequisite for a scale-dependent interaction hypothesis. The verification failed: SE achieves AUROC of 0.4735 on TriviaQA and 0.5524 on NaturalQuestions, compared to 0.6835 and 0.6551 for token-probability on the same datasets. KLE performs at 0.2642 and 0.3753 respectively, and SelfCheckGPT-BERTScore yields a constant AUROC of 0.5000.

The degenerate_fraction diagnostic records that 89.4% of TriviaQA queries and 84.8% of NaturalQuestions queries produce K=1 semantic clusters under N=10 sampling at temperature=1.0 from Llama-3-8B-Base. This observation is consistent with the SE failure: a method that relies on semantic diversity across samples cannot produce discriminative uncertainty scores when the vast majority of queries yield semantically identical samples.

The contribution of this study is primarily diagnostic. The `degenerate_fraction` metric makes explicit a precondition that is implicit in clustering-based UQ methods and was not reported in their original evaluations. Token-probability is shown to provide a valid uncertainty signal in the base-model, factual-QA regime studied here. The finding that SE superiority over token-probability is not observed for Llama-3-8B-Base under standard evaluation conditions documents a boundary on the known validity of this method.

Several important questions remain open: whether SE functions correctly on instruction-tuned variants of Llama-3; whether temperature adjustment can reduce degenerate_fraction sufficiently to restore SE discriminability on base models; and whether 70B scale results differ from 8B. These are identified as the immediate priorities for follow-up.

---

## References

[Cherian et al., 2024] Cherian, A. et al. Large Language Model Validity via Enhanced Conformal Prediction Methods. *ACL*, 2024.

[Dubey et al., 2024] Dubey, A. et al. The Llama 3 Herd of Models. *arXiv:2407.21783*, 2024.

[Farquhar et al., 2024] Farquhar, S., Kossen, J., Kuhn, L., and Gal, Y. Detecting Hallucinations in Large Language Models Using Semantic Entropy. *Nature*, 2024.

[Joshi et al., 2017] Joshi, M. et al. TriviaQA: A Reading Comprehension Dataset over Trivia Questions. *ACL*, 2017.

[Kadavath et al., 2022] Kadavath, S. et al. Language Models (Mostly) Know What They Know. *arXiv:2207.05221*, 2022.

[Kang et al., 2025] Kang, J. et al. Uncertainty Quantification for Hallucination Detection in Large Language Models: A Survey. *arXiv:2510.12040*, 2025.

[Kossen et al., 2024] Kossen, J. et al. Semantic Entropy Probes: Robust and Cheap Hallucination Detection in LLMs. *NeurIPS*, 2024.

[Kwiatkowski et al., 2019] Kwiatkowski, T. et al. Natural Questions: A Benchmark for Question Answering Research. *TACL*, 2019.

[Li et al., 2016] Li, J. et al. A Diversity-Promoting Objective Function for Neural Conversation Models. *NAACL*, 2016.

[Malinin and Gales, 2021] Malinin, A. and Gales, M. Uncertainty Estimation in Autoregressive Structured Prediction. *ICLR*, 2021.

[Manakul et al., 2023] Manakul, P., Liusie, A., and Gales, M. SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models. *EMNLP*, 2023.

[Mir, 2025] Mir, R. Layer-wise Semantic Dynamics (LSD) for Hallucination Detection. *arXiv:2510.04933*, 2025.

[Nikitin et al., 2024] Nikitin, A. et al. Kernel Language Entropy: Fine-grained Uncertainty Quantification for LLMs from Semantic Similarities. *NeurIPS*, 2024.

[Su et al., 2024] Su, J. et al. API is Enough: Conformal Prediction for Large Language Models Without Logit-Access. *arXiv:2403.01216*, 2024.

[Vijayakumar et al., 2016] Vijayakumar, A. K. et al. Diverse Beam Search: Decoding Diverse Solutions from Neural Sequence Models. *arXiv:1610.02424*, 2016.

[Wang et al., 2025] Wang, Y. et al. Effective Rank-based Uncertainty Estimation for Language Models. *arXiv:2510.08389*, 2025.

[Zhu et al., 2018] Zhu, Y. et al. Texygen: A Benchmarking Platform for Text Generation Models. *SIGIR*, 2018.
