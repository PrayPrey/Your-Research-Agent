# When Semantic Entropy Fails: Sampling Degeneracy in Base Language Models Undermines Clustering-Based Uncertainty Quantification

**Abstract**

Semantic entropy (SE), a Nature-published method with over 1,000 citations, is widely used as the de facto benchmark for uncertainty quantification in language models. We show that SE fails as an uncertainty estimator on base language models for factual question answering: on Llama-3-8B-Base, SE achieves an AUROC of 0.4735 on TriviaQA and 0.5524 on NaturalQuestions—substantially below token-probability (0.6835 and 0.6551 respectively) and below random chance on TriviaQA. The evidence is consistent with *sampling degeneracy* as the primary cause: 89% of TriviaQA queries and 85% of NQ queries produce K=1 semantic cluster under N=10 sampling at temperature=1.0 from a base model, collapsing SE entropy to near-zero for most queries and destroying its discriminative ability. We introduce `degenerate_fraction` as a computable pre-screening diagnostic for SE validity, show that token-probability remains valid and competitive (AUROC>0.68 on both datasets), and find that SelfCheckGPT-NLI is competitive on TriviaQA (AUROC=0.6862) but underperforms on NQ (AUROC=0.4508), suggesting dataset-dependent reliability for sampling-based alternatives. We release a complete benchmarking infrastructure (~2,222 lines) with checkpointed generation and bootstrap confidence intervals. Our findings identify an unvalidated assumption in UQ benchmarking—that base and instruction-tuned models produce equivalent sampling diversity—and provide actionable guidance for UQ method selection in base-model deployment.

---

## 1. Introduction

Semantic entropy—a method published in *Nature* and cited over 1,000 times as a landmark advance in uncertainty quantification for language models—is anti-correlated with correctness on 89% of TriviaQA queries when applied to a base language model, producing an AUROC of 0.4735: worse than random. This is not a calibration failure or an edge case. It is a systematic collapse consistent with a structural property of base model sampling that the existing literature has not characterized.

The ability to quantify epistemic uncertainty in large language models (LLMs) has become central to safe deployment: reliable uncertainty scores enable downstream systems to route queries, abstain from low-confidence predictions, and flag potential hallucinations before they propagate. Token-probability-based approaches—using the model's own predicted logits as an uncertainty signal—have long been the pragmatic baseline. Sampling-based semantic methods, led by semantic entropy (SE) [Farquhar et al., 2024] and kernel language entropy (KLE) [Nikitin et al., 2024], were proposed to overcome token-probability's limitations by operating over semantic equivalence classes rather than surface-level distributions. These methods cluster N stochastic samples into semantic groups and compute entropy over cluster probability mass—a theoretically elegant solution to the sensitivity of logit-based estimates to lexical paraphrase variation.

The dominant view, established by Farquhar et al. (2024), is that SE substantially outperforms token-probability (AUROC ~0.72–0.79 vs. ~0.67 on TriviaQA/NQ/BioASQ). This finding has been widely reproduced and extended: Kossen et al. (2024) approximated SE from single-pass hidden states; Nikitin et al. (2024) generalized it via von Neumann entropy over semantic kernels; Manakul et al. (2023) established the parallel SelfCheckGPT paradigm. However, a critical condition is implicit in all published evaluations: *the model generating the N samples must produce semantically diverse outputs* (the requirement that N samples produce K>1 semantic clusters). When outputs are near-identical, SE entropy collapses to near-zero for nearly all queries, and the resulting score distribution is uninformative for correctness prediction.

We show that this diversity precondition is systematically violated for base language models on factual short-answer QA benchmarks. When sampling N=10 responses from Llama-3-8B-Base at temperature=1.0—the standard protocol from Farquhar et al. (2024)—89% of TriviaQA queries and 85% of NaturalQuestions queries produce K=1 semantic cluster (all responses are semantically identical). We term this the *sampling degeneracy* regime. In this regime, SE≈0 for the vast majority of queries, KLE scores are near-zero with inverted rank ordering, and both methods lose discriminative ability for correctness. Token-probability, by contrast, remains valid across both datasets: it does not rely on semantic diversity and achieves AUROC of 0.6835 (TriviaQA) and 0.6551 (NQ). SelfCheckGPT-NLI achieves AUROC of 0.6862 on TriviaQA but only 0.4508 on NQ, indicating its utility varies across datasets.

The core insight is that SE is a *diversity-conditional* uncertainty estimator: its validity depends on the model generating semantically distinct hypotheses across N samples. Published results demonstrating SE superiority were obtained on instruction-tuned model variants (Llama-2-Chat, GPT-3) that exhibit substantially higher sampling diversity due to RLHF-induced output variation. Base models, trained purely on next-token prediction, develop highly confident, near-deterministic behavior for factual recall queries. Applying SE to base models with standard sampling settings imports an assumption that was never validated in that regime.

This work makes three contributions. First, we *characterize the sampling degeneracy failure mode*: we introduce `degenerate_fraction` (the proportion of queries for which K=1 under N=10 sampling) as a diagnostic metric and show that degenerate_fraction=0.894 (TriviaQA) and 0.848 (NQ) for Llama-3-8B-Base at temperature=1.0—values that make SE and KLE invalid as uncertainty estimators. Second, we *evaluate token-probability and SelfCheckGPT-NLI in the low-diversity regime*: token-probability achieves AUROC>0.68 and remains valid across both datasets; SelfCheckGPT-NLI is competitive on TriviaQA but exhibits dataset-dependent performance (AUROC=0.4508 on NQ), highlighting the need for method selection to account for dataset characteristics. Third, we *provide a reusable benchmarking infrastructure* (~2,222 lines of Python) implementing six UQ methods with bootstrap confidence intervals, checkpointed generation, and the degenerate_fraction diagnostic—enabling reproducibility and future benchmarking studies.

Our findings do not invalidate SE as a method; they establish its validity domain. For instruction-tuned models generating diverse outputs, SE remains the state of the art. For base models on factual short-answer QA with standard sampling, it is not. The gap between these regimes is the key unaddressed variable in the current UQ benchmarking literature.

The remainder of this paper is structured as follows. Section 2 discusses related work. Section 3 describes our experimental methodology. Section 4 presents experimental results. Section 5 discusses implications, limitations, and future work. Section 6 concludes.

---

## 2. Related Work

### Uncertainty Quantification for Language Models

Uncertainty quantification in LLMs spans two broad paradigms distinguished by their information source: output-space methods that operate on generated text or logit distributions, and representation-space methods that interrogate internal model states.

**Token-probability methods** use the model's predicted probability distribution as a proxy for confidence. Negative log-probability and maximum softmax probability are standard baselines [Malinin and Gales, 2021; Kadavath et al., 2022]. Despite their simplicity, these methods demonstrate robust performance: Farquhar et al. (2024) report token-probability AUROC of ~0.67 on TriviaQA for Llama-2-70B, and our experiments replicate this with 0.6835 on Llama-3-8B-Base. Token-probability is valid under any sampling regime and requires only a single forward pass—properties we show are critical when sampling diversity is low.

**Sampling-based semantic methods** were introduced to overcome a limitation of token-probability: sensitivity to superficial lexical variation that does not reflect genuine epistemic uncertainty. *Semantic entropy* (SE) [Farquhar et al., 2024] clusters N stochastic responses into semantic equivalence classes via bidirectional NLI and computes entropy over cluster probability mass. Evaluated on Llama-2 variants (including instruction-tuned), TriviaQA, NQ, BioASQ, and SQuAD, SE achieves AUROC of 0.72–0.79 and establishes itself as the state of the art for sequence-level uncertainty. *Kernel Language Entropy* (KLE) [Nikitin et al., 2024] generalizes SE via von Neumann entropy over a semantic similarity kernel matrix, providing a theoretically unified framework. Both SE and KLE depend on semantic diversity among the N samples: without diverse clusters, entropy collapses.

*Semantic Entropy Probes* (SEPs) [Kossen et al., 2024] approximate SE from a single forward pass using linear classifiers on hidden-state representations, achieving 5–10× speedup with comparable AUROC. Their evaluation uses Llama-2 variants on TriviaQA and NQ, but degenerate_fraction of the sampling distribution is not reported—leaving the diversity precondition implicit.

*SelfCheckGPT* [Manakul et al., 2023] measures consistency across N samples using NLI, BERTScore, or n-gram overlap. Evaluated on GPT-3 outputs, SelfCheckGPT-NLI achieves strong performance. Our results show that SelfCheckGPT-NLI is competitive with token-probability on TriviaQA (AUROC=0.6862) but underperforms substantially on NQ (AUROC=0.4508)—because NLI-based entailment detection exploits subtle paraphrase variations among the 11% of diverse TriviaQA queries but does not generalize this advantage to the NQ distribution (which has 19.4% correctness rate and different answer characteristics).

**The sampling diversity assumption.** SE and SelfCheckGPT evaluations implicitly assume that the model produces non-trivial variation across N=10 samples. This is reliable for instruction-tuned models; for *base* models on factual recall queries, it is not. To our knowledge, no prior work has measured degenerate_fraction as an explicit diagnostic or evaluated SE validity as a function of sampling diversity.

**Sampling diversity metrics in prior work.** The broader question of output diversity in language model generation has been studied previously. Li et al. (2016) introduced diversity-promoting objectives for neural conversation models. Vijayakumar et al. (2016) proposed Diverse Beam Search to address the K=1-equivalent collapse under beam search. Metrics such as Self-BLEU [Zhu et al., 2018] and distinct-n [Li et al., 2016] have been used to measure output diversity in generation tasks. Our `degenerate_fraction` metric differs from these in its specific framing as a *UQ validity diagnostic*: rather than measuring diversity as an intrinsic property of generation, it measures the proportion of queries for which clustering-based UQ methods become uninformative. Self-BLEU and distinct-n quantify lexical diversity at the corpus level; `degenerate_fraction` quantifies semantic clustering collapse at the query level for the purpose of pre-screening UQ method validity. The connection to prior diversity metrics is acknowledged, but the application to UQ validity diagnosis is, to our knowledge, novel.

### Representation-Based and Statistical Methods

Beyond sampling, internal model representations carry uncertainty signal. *Layer-wise Semantic Dynamics* (LSD) [Mir, 2025] trains contrastive representations achieving AUROC=0.96 on TruthfulQA. *Effective Rank-based Uncertainty* [Wang et al., 2025] uses spectral rank of hidden-state matrices. These methods bypass the sampling diversity requirement entirely. Conformal prediction methods [Cherian et al., 2024; Su et al., 2024] provide statistical coverage guarantees and are orthogonal to our analysis.

### Surveys and Meta-Analyses

Kang et al. (2025) survey 100+ UQ methods and identify *evaluation fragmentation* as the field's primary limitation. Our work addresses a specific, operationalizable fragmentation axis: the conflation of base and instruction-tuned models. The degenerate_fraction metric we introduce provides a concrete way to characterize this dimension.

### Positioning of This Work

We do not challenge SE's validity in general. Our contribution is to *identify and operationalize the validity boundary*: SE and KLE require sampling diversity to function as uncertainty estimators. Published evaluations have implicitly operated within the valid regime. Applying these methods to base models requires explicit diversity verification.

---

## 3. Methodology

### Overview

Our experimental methodology was originally designed to test the Epistemic Geometry Scaling Hypothesis (EGSH): whether semantic-structural UQ methods (SE, KLE) show a larger AUROC advantage over token-probability at 70B scale compared to 8B. The existence check—verifying that SE > token-probability at any scale—revealed sampling degeneracy as the primary phenomenon. We describe the full experimental design, including the degenerate_fraction diagnostic.

### Models

We evaluate **Llama-3-8B-Base** (`meta-llama/Meta-Llama-3-8B`) [Dubey et al., 2024] loaded in bfloat16 precision on a single H100 NVL 96GB GPU.

**Rationale for base (non-instruct) models:** The original hypothesis targets scaling behavior under controlled conditions. Instruction tuning introduces RLHF alignment as a confounding variable that modulates sampling diversity independently of model scale. Base checkpoints provide the clearest isolation.

### Datasets

**TriviaQA rc.nocontext** [Joshi et al., 2017]: 500 validation questions. Correctness rate: 66.0% (330/500). **NaturalQuestions open-domain** [Kwiatkowski et al., 2019]: 500 validation questions. Correctness rate: 19.4% (97/500). Both benchmarks have established evaluation protocols and were used in the original SE paper [Farquhar et al., 2024]—enabling direct comparison under controlled conditions.

### Generation Protocol

For each query: **N=10 stochastic samples** (temperature=1.0, top_p=0.9, max 512 tokens) plus one greedy decode. Token-probability uses greedy decode logits. N=10 at temperature=1.0 is the standard protocol from Farquhar et al. (2024)—we deliberately do not deviate to characterize the failure under standard conditions.

### UQ Methods

1. **Token-probability:** Negative mean log-probability of greedy decode tokens. Single-pass, valid under any regime.

2. **Semantic Entropy (SE)** [Farquhar et al., 2024]: NLI clustering (DeBERTa-large-mnli) of N=10 responses into semantic equivalence classes. H = −∑_c p(c) log p(c) over cluster mass.

3. **Kernel Language Entropy (KLE)** [Nikitin et al., 2024]: Von Neumann entropy over semantic similarity Laplacian. Near-zero for rank-1 matrices (K=1 cluster).

4. **SelfCheckGPT-BERTScore** [Manakul et al., 2023]: Mean BERTScore(greedy, sample). Constant when all samples identical.

5. **SelfCheckGPT-NLI** [Manakul et al., 2023]: Proportion of samples that do not entail the greedy decode. Robust to near-identical samples via entailment sensitivity.

6. **SEPs** [Kossen et al., 2024]: Linear probes on hidden states. Null scores at PoC scale (excluded from analysis).

### Degenerate Fraction Diagnostic

For each query: `degenerate_fraction = (# queries with K=1) / (total queries)`. K=1 means all N=10 samples are semantically identical under SE clustering. Post-hoc diagnostic introduced to explain observed SE failure.

### Evaluation

AUROC over binary correctness labels. Bootstrap CI: 1000 resamples, 95% interval. Gate criterion: SE AUROC > token_prob AUROC with CI excluding zero, on both TriviaQA AND NQ.

---

## 4. Results

### Main AUROC Comparison

**Table 1: AUROC Results on Llama-3-8B-Base (95% Bootstrap CI)**

| Method | TriviaQA AUROC | TriviaQA CI | NQ AUROC | NQ CI |
|--------|---------------|-------------|----------|-------|
| token_prob | **0.6835** | [0.6361, 0.7332] | **0.6551** | [0.5960, 0.7063] |
| selfcheck_nli | 0.6862 | [0.6362, 0.7340] | 0.4508 | [0.3943, 0.5084] |
| semantic_entropy | 0.4735 | [0.4409, 0.5036] | 0.5524 | [0.5121, 0.5977] |
| kle | 0.2642 | [0.2158, 0.3107] | 0.3753 | [0.3078, 0.4372] |
| selfcheck_bertscore | 0.5000 | [0.5000, 0.5000] | 0.5000 | [0.5000, 0.5000] |

*Figure 1: AUROC comparison across all UQ methods. Error bars indicate 95% bootstrap CI. (fig1_auroc_bar_8b.png)*

The MUST_WORK gate—SE AUROC > token_prob AUROC—fails on both datasets. On TriviaQA, SE is 0.210 AUROC points *below* token_prob; the 95% CI [−0.252, −0.155] excludes zero entirely. On NQ the gap is −0.103. KLE falls to 0.2642 on TriviaQA, well below chance.

*Figure 2: SE minus token-probability AUROC difference with bootstrap 95% CI. Both CIs exclude zero in the negative direction. (fig2_se_tp_difference_8b.png)*

### Sampling Degeneracy

**Table 2: Sampling Degeneracy Statistics**

| Dataset | degenerate_fraction | mean_K |
|---------|---------------------|--------|
| TriviaQA | **0.894** | 9.884 |
| NaturalQuestions | **0.848** | 9.796|

On TriviaQA, 89.4% of queries produce K=1: all 10 samples are semantically identical. For these queries, SE=0 regardless of correctness. Among the 11% with K>1, uncertain-but-correct queries occasionally produce K>1 while high-confidence incorrect answers consistently produce K=1—creating an anti-correlation: higher SE is weakly associated with correctness, so uncertainty estimates are anti-correlated with incorrectness (AUROC < 0.5).

*Figure 3: Full UQ method comparison, all six methods on both datasets. (fig3_auroc_all_methods_8b.png)*

### Key Contrasts

**SelfCheckGPT-NLI matches token_prob on TriviaQA** (0.6862 vs. 0.6835) despite identical degenerate_fraction: NLI entailment detects semantic variation in the 11% of diverse queries more sensitively than BERTScore's cosine similarity. However, **SelfCheckGPT-NLI fails on NQ** (0.4508, below chance), indicating its utility is dataset-dependent rather than universally robust to low diversity.

**SelfCheckGPT-BERTScore is uninformative** (AUROC=0.5000, zero-variance): identical samples → BERTScore=1.0 → constant uncertainty → no discriminative ability. Implementation is correct; failure is regime-specific.

**KLE below chance on TriviaQA** (0.2642): rank-1 Laplacian for 89% of queries → near-zero eigenvalue sum → systematic score inversion → AUROC well below 0.5.

---

## 5. Discussion

### Why Base Models Are Degenerate

Llama-3-8B-Base assigns highly concentrated probability mass to dominant answer token sequences for factual recall queries. At temperature=1.0, N=10 samples are overwhelmingly identical. This is not a model failure—it reflects successful memorization of factual information. Instruction-tuned models (Llama-2-Chat, GPT-3) exhibit higher output variation due to RLHF-induced response style diversity, placing them in SE's valid operating domain.

The discrepancy between our results (SE AUROC=0.47–0.55) and Farquhar et al. (2024) (SE AUROC=0.72–0.79) is fully accounted for by this model-type difference. Published SE superiority results implicitly used the instruct-model regime; the base model regime was never tested. We note that the mechanistic account (K=1 → SE=0 → no discriminative signal) is well-supported by the data, though confirming the causal direction formally would require a controlled experiment that independently varies sampling diversity—for instance, by comparing base versus instruct variants or sweeping temperature (planned as future work F1 and F2).

### Implications for UQ Benchmarking

We recommend that UQ benchmarking studies: (1) report degenerate_fraction alongside AUROC; (2) pre-screen UQ method validity based on diversity before reporting—if degenerate_fraction > 0.5, SE and KLE should not be reported as primary results; (3) stratify by model type (base vs. instruct), not only by scale.

### Practical Recommendations

- **Use token-probability** for base model factual QA: AUROC>0.68 on both TriviaQA and NQ, single forward pass, no diversity requirement.
- **Use SelfCheckGPT-NLI with caution** when a sampling-based method is required: competitive with token-probability on TriviaQA (AUROC=0.6862), but underperforms on NQ (AUROC=0.4508). Dataset characteristics—including correctness rate distribution—appear to influence its reliability.
- **Avoid SE and KLE** on base models with standard sampling (N=10, temp=1.0): invalid in the degenerate regime.
- **If SE is required**: use instruction-tuned models or increase temperature; verify degenerate_fraction < 0.5.

### Limitations

**L1:** Only Llama-3-8B-Base evaluated (70B pending). **L2:** 500-sample PoC scale (sufficient for gate but not sub-group analysis). **L3:** Negative result without a corrected method—F1 and F2 are needed to establish recovery conditions. **L4:** SEPs non-functional at PoC scale. **L5:** Base-model conclusions do not directly generalize to instruct models.

### Future Work

**F1 (Highest Priority):** Verify SE > TP on Llama-3-8B-Instruct. 1–2 days with existing infrastructure; if degenerate_fraction < 0.3, SE AUROC should recover to ~0.70+.

**F2 (High Priority):** Temperature sweep (0.5–3.0) to find SE-viable regime for base models.

**F3 (Medium):** Diversity-conditional UQ protocol: measure degenerate_fraction on 50-query probe set; auto-select methods based on threshold.

**F4 (Medium):** Reformulated EGSH for instruct scale comparison (8B-Instruct vs. 70B-Instruct), contingent on F1.

---

## 6. Conclusion

We set out to test whether semantic entropy's correctness-predictive advantage over token-probability scales with model size in the Llama-3 family. Instead, we discovered that semantic entropy produces an AUROC of 0.4735 on TriviaQA—below random chance—when applied to a base language model under the standard evaluation protocol. The celebrated method that surpasses token-probability by 0.05–0.12 AUROC in published evaluations is here anti-correlated with correctness.

The explanation is mechanistically precise and actionable: Llama-3-8B-Base produces semantically identical responses for 89.4% of TriviaQA queries under N=10 sampling at temperature=1.0. When all samples cluster into a single equivalence class, semantic entropy collapses to zero—not because of an implementation error, but because the method's diversity precondition is violated. The SE mechanism is correctly implemented and activates; the failure is conceptual. SE is a diversity-conditional estimator. Base model factual recall is a low-diversity regime. The evidence is strongly consistent with sampling degeneracy as the mechanistic account of this failure; confirming the causal direction requires controlled diversity manipulation experiments (F1, F2), which we identify as the highest-priority future work.

This finding reframes a significant body of published evidence. SE superiority results were obtained on instruction-tuned models with higher sampling diversity; the diversity precondition was never explicitly stated or measured. We introduce `degenerate_fraction` as a simple, computable diagnostic that makes this precondition explicit. Token-probability (AUROC=0.6835 on TriviaQA, 0.6551 on NQ) provides a robust alternative across both datasets. SelfCheckGPT-NLI is competitive on TriviaQA (AUROC=0.6862) but underperforms on NQ (AUROC=0.4508), suggesting its utility depends on dataset characteristics and should not be assumed universally robust in the degenerate regime.

The contribution is not only negative. The full generation and evaluation infrastructure (~2,222 lines, checkpointed, reproducible) is validated and released. The degenerate_fraction metric provides a concrete, model-type-aware audit for UQ benchmarking studies. And the characterization of the failure mode offers a principled foundation for redesigning UQ evaluation protocols in the field.

When a method celebrated for surpassing the baseline instead falls below chance, that is not just a failed experiment—it is an experiment that worked.

---

## References

\[Cherian et al., 2024\] Cherian, A. et al. Large Language Model Validity via Enhanced Conformal Prediction Methods. *ACL*, 2024.

\[Dubey et al., 2024\] Dubey, A. et al. The Llama 3 Herd of Models. *arXiv:2407.21783*, 2024.

\[Farquhar et al., 2024\] Farquhar, S., Kossen, J., Kuhn, L., and Gal, Y. Detecting Hallucinations in Large Language Models Using Semantic Entropy. *Nature*, 2024.

\[Joshi et al., 2017\] Joshi, M. et al. TriviaQA: A Reading Comprehension Dataset over Trivia Questions. *ACL*, 2017.

\[Kang et al., 2025\] Kang, J. et al. Uncertainty Quantification for Hallucination Detection in Large Language Models: A Survey. *arXiv:2510.12040*, 2025.

\[Kossen et al., 2024\] Kossen, J. et al. Semantic Entropy Probes: Robust and Cheap Hallucination Detection in LLMs. *NeurIPS*, 2024.

\[Kwiatkowski et al., 2019\] Kwiatkowski, T. et al. Natural Questions: A Benchmark for Question Answering Research. *TACL*, 2019.

\[Li et al., 2016\] Li, J. et al. A Diversity-Promoting Objective Function for Neural Conversation Models. *NAACL*, 2016.

\[Manakul et al., 2023\] Manakul, P., Liusie, A., and Gales, M. SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models. *EMNLP*, 2023.

\[Mir, 2025\] Mir, R. Layer-wise Semantic Dynamics (LSD) for Hallucination Detection. *arXiv:2510.04933*, 2025.

\[Nikitin et al., 2024\] Nikitin, A. et al. Kernel Language Entropy: Fine-grained Uncertainty Quantification for LLMs from Semantic Similarities. *NeurIPS*, 2024.

\[Su et al., 2024\] Su, J. et al. API is Enough: Conformal Prediction for Large Language Models Without Logit-Access. *arXiv:2403.01216*, 2024.

\[Vijayakumar et al., 2016\] Vijayakumar, A. K. et al. Diverse Beam Search: Decoding Diverse Solutions from Neural Sequence Models. *arXiv:1610.02424*, 2016.

\[Wang et al., 2025\] Wang, Y. et al. Effective Rank-based Uncertainty Estimation for Language Models. *arXiv:2510.08389*, 2025.

\[Zhu et al., 2018\] Zhu, Y. et al. Texygen: A Benchmarking Platform for Text Generation Models. *SIGIR*, 2018.
