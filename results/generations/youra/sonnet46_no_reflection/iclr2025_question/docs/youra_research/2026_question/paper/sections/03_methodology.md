# Methodology

## Overview

Our experimental methodology was originally designed to test the Epistemic Geometry Scaling Hypothesis (EGSH): whether semantic-structural UQ methods (SE, KLE) show a larger AUROC advantage over token-probability at 70B scale compared to 8B. The EGSH posits that larger model capacity enables richer semantic equivalence class representations that surface-level token distributions cannot capture, producing a scale-modulated interaction effect.

The experiment's existence check—verifying that SE > token-probability at any scale—revealed sampling degeneracy as the primary phenomenon. We describe the full experimental design, including the degenerate_fraction diagnostic that emerged as the key explanatory variable.

## Models

We evaluate **Llama-3-8B-Base** (`meta-llama/Meta-Llama-3-8B`) loaded in bfloat16 precision on a single H100 NVL 96GB GPU. The 70B counterpart (`meta-llama/Meta-Llama-3-70B`) was loaded in 8-bit quantization via bitsandbytes; 70B experiments were initiated but 8B results were sufficient for gate determination (MUST_WORK gate failed with |SE_AUROC - TP_AUROC| > 0.2 on both datasets).

**Rationale for base (non-instruct) models:** The EGSH hypothesis targets the scaling behavior of semantic representations under controlled conditions. Instruction tuning introduces RLHF alignment as a confounding variable that modulates sampling diversity independently of model scale. Base checkpoints provide the clearest isolation of the scale variable.

## Datasets

We evaluate on two factual short-answer QA benchmarks:

- **TriviaQA rc.nocontext** [Joshi et al., 2017]: 500 questions from the validation split. Correctness is determined by exact-match normalization (case-insensitive, punctuation-stripped) against the gold answer set. Correctness rate: 66.0% (330/500 correct).

- **NaturalQuestions open-domain** [Kwiatkowski et al., 2019]: 500 questions from the validation split. Correctness rate: 19.4% (97/500 correct), reflecting NQ's harder, longer-tail factual queries.

**Rationale for dataset selection:** Both benchmarks have established evaluation protocols, provide binary correctness labels, and were used in the original SE paper [Farquhar et al., 2024]—enabling direct comparison of our results with published values under controlled conditions (same datasets, same protocol, different model type: base vs. instruct).

## Generation Protocol

For each query, we generate **N=10 stochastic samples** plus one greedy decode. Stochastic sampling uses temperature=1.0, top_p=0.9, maximum 512 new tokens. Logits from the greedy decode provide the token-probability signal. Stochastic samples are used for all sampling-based UQ methods.

**Rationale:** N=10 at temperature=1.0 is the standard protocol from Farquhar et al. (2024), ensuring comparability. We deliberately do not deviate from the standard protocol—our goal is to characterize the failure of SE under standard conditions, not under adversarial ones.

## UQ Methods

We implement and evaluate six uncertainty estimation methods:

**1. Token-probability (token_prob):** Negative mean log-probability of greedy decode tokens. Single-pass, no sampling required. Valid under any sampling regime.

**2. Semantic Entropy (SE)** [Farquhar et al., 2024]: NLI-based bidirectional clustering of N=10 stochastic responses into semantic equivalence classes. Entropy H = −∑_c p(c) log p(c) over cluster probability mass p(c) = ∑_{s∈c} P(s) / ∑_s P(s), where P(s) is the sequence log-probability. NLI classifier: DeBERTa-large-mnli.

**3. Kernel Language Entropy (KLE)** [Nikitin et al., 2024]: Von Neumann entropy over the semantic similarity kernel matrix K_{ij} = NLI_similarity(s_i, s_j). Eigenvalue sum of normalized Laplacian provides the uncertainty score. Degenerates to near-zero when K is rank-1 (K=1 cluster).

**4. SelfCheckGPT-BERTScore** [Manakul et al., 2023]: Mean BERTScore between greedy decode and each stochastic sample. Uncertainty = 1 − mean_BERTScore. Produces constant score=1.0 (AUROC=0.5) when all samples are identical.

**5. SelfCheckGPT-NLI** [Manakul et al., 2023]: Proportion of stochastic samples that do not entail the greedy decode according to DeBERTa-large-mnli. Unlike BERTScore, NLI detects semantic entailment and retains discriminative signal under near-identical samples via subtle paraphrase variation.

**6. Semantic Entropy Probes (SEPs)** [Kossen et al., 2024]: Linear probes on hidden states to approximate SE from a single forward pass. In our experiments, SEPs produced null scores due to insufficient probe data at the PoC scale of 500 samples per dataset and were excluded from AUROC analysis.

## Degenerate Fraction Diagnostic

For each query and dataset, we compute:

```
degenerate_fraction = (# queries with K=1) / (total queries)
```

where K is the number of distinct semantic clusters produced by SE clustering of N=10 samples. K=1 means all samples are semantically equivalent. This metric is not preregistered—it emerged as a post-hoc diagnostic to explain the observed SE failure—but it provides a principled operationalization of the sampling diversity precondition.

## Evaluation

**AUROC:** Area under the ROC curve for binary correctness prediction from UQ scores. Computed via `sklearn.metrics.roc_auc_score`. For methods producing uncertainty scores (higher = more uncertain), we negate the score before AUROC computation.

**Bootstrap confidence intervals:** 1000 bootstrap resamples of (UQ score, correctness label) pairs per dataset, with 2.5th and 97.5th percentile CI bounds. CIs reported alongside all AUROC values.

**Gate criterion (MUST_WORK):** SE AUROC > token_prob AUROC with 95% bootstrap CI excluding zero, on both TriviaQA AND NaturalQuestions.

## Implementation Details

The full pipeline is implemented in Python 3.10 with PyTorch 2.x (~2,222 lines across 10 files). Key components: `config.py` (hyperparameter management), `data_loader.py` (TriviaQA, NQ, TruthfulQA loading with exact-match normalization), `model_loader.py` (bfloat16 / 8-bit model loading), `generate.py` (N=10 stochastic sampling + greedy decode with checkpoint), `uq_methods.py` (all six UQ implementations), `evaluate.py` (AUROC + bootstrap CI), `visualize.py` (figure generation). Checkpointed generation enables resumption after interruption. All code is released with the paper.
