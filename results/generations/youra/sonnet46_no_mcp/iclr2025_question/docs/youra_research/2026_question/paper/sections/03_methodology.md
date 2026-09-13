# Methodology

## Overview

Our methodology is designed around a single principle: controlled comparison. Each prior evaluation of semantic entropy, SelfCheckGPT, and token entropy uses different datasets, models, and evaluation protocols — making cross-method conclusions unreliable. We remove these confounds by applying all three methods to the same examples, with the same LLM, using the same evaluation pipeline.

Beyond the comparative design, we treat the NLI clustering mechanism of semantic entropy as an empirical question rather than an assumption. Prior work implicitly assumes that NLI-based clustering produces meaningful semantic aggregation on any QA benchmark. We test this assumption directly by measuring NLI aggregation behavior (H-M2) before attributing AUROC differences to method quality. This mechanism-first approach converts what could be a generic null result into a precise, actionable diagnosis.

## Dataset

We evaluate on the QA subset of HaluEval [Li et al., 2023], stratified to 2,000 examples (1,000 hallucinated, 1,000 factual) using a fixed random seed (seed=42). HaluEval-QA provides binary labels: each example consists of a question, a factual reference answer, and a ChatGPT-generated hallucinated answer. The hallucinated answers are designed to be confident-sounding and plausible — an important characteristic that distinguishes HaluEval-QA from human-annotated benchmarks.

**Rationale for HaluEval-QA:** (1) Explicit binary hallucination labels make AUROC a natural evaluation metric. (2) The QA task format with short responses (typically 1–15 words) represents a deployment scenario distinct from the long-form generation settings (TriviaQA, WikiBio) where semantic entropy and SelfCheckGPT were originally validated. (3) The 2,000-example balanced sample provides sufficient statistical power for bootstrap CI estimation (N=1000 resamples) while remaining computationally tractable with a fixed inference budget.

The data is loaded from HuggingFace (pminervini/HaluEval, QA subset) and persisted to disk for reproducibility across sub-hypothesis experiments.

## Model

We use **LLaMA-2-7B-chat** (meta-llama/Llama-2-7b-chat-hf) in float16 precision on a single NVIDIA H100 NVL GPU. The chat variant is used because it is instruction-tuned and produces coherent short answers for the QA task. Inference parameters are fixed across all methods:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `greedy_temperature` | 0.0 | Deterministic reference response for SelfCheckGPT |
| `stochastic_temperature` | 1.0 | Standard stochastic sampling for SE and SCG |
| `max_new_tokens` | 256 | Sufficient for short QA answers; prevents truncation |
| `n_stochastic_samples` | 5 | Fixed budget; minimum validated by Manakul et al. (2023) |

All three UQ methods share the same greedy and stochastic inference outputs — greedy logits are computed once (for token entropy), and five stochastic samples are generated once (for semantic entropy and SelfCheckGPT). This ensures that method differences reflect signal extraction, not inference variance.

## UQ Signal Pipelines

### Token Entropy (Baseline)

Token entropy is computed as the mean Shannon entropy over per-token output distributions from the greedy inference pass:

$$H_{\text{token}}(x) = \frac{1}{T} \sum_{t=1}^{T} H(p_t)$$

where $H(p_t) = -\sum_v p_t(v) \log p_t(v)$ is the entropy of the token distribution at position $t$, and $T$ is the response length. Logits are cast to float32 before softmax to avoid fp16 precision artifacts on the H100 NVL.

**Rationale:** Token entropy is the simplest possible UQ signal — no additional inference beyond the greedy pass. It serves as the floor baseline: if semantic entropy's NLI mechanism works, it should strictly outperform token entropy by filtering surface-form noise.

### Semantic Entropy

Semantic entropy [Kuhn et al., 2023] is computed over NLI-based semantic equivalence clusters of the N=5 stochastic samples:

1. **NLI pairwise classification:** For each pair of stochastic responses $(r_i, r_j)$, bidirectional NLI entailment is checked using deberta-large-mnli (microsoft/deberta-large-mnli). Two responses are considered semantically equivalent if they mutually entail each other.

2. **Union-find clustering:** Pairs classified as semantically equivalent are merged into clusters using a union-find algorithm [Kuhn et al., 2023]. This ensures transitivity: if $r_1 \equiv r_2$ and $r_2 \equiv r_3$, then $r_1$, $r_2$, $r_3$ are in the same cluster.

3. **Cluster entropy computation:** Given cluster assignment probabilities $p_c = |C_c| / N$ for each cluster $C_c$:

$$H_{\text{semantic}}(x) = -\sum_c p_c \log p_c$$

**The critical mechanism step** is step (1): if deberta-large-mnli fails to classify semantically equivalent responses as entailing each other, nearly all responses land in singleton clusters, and $H_{\text{semantic}}$ approaches its maximum value for all examples — collapsing to a constant signal. We measure whether this mechanism operates correctly using the NLI aggregation rate (Section 3.5).

### SelfCheckGPT-BERTScore

SelfCheckGPT [Manakul et al., 2023] measures how consistently the model generates the greedy response when prompted stochastically:

$$\text{SCG}(x) = 1 - \frac{1}{N} \sum_{i=1}^{N} \text{BERTScore}(r_{\text{greedy}}, r_i)$$

where BERTScore computes token-level F1 between greedy and stochastic response embeddings (using bert-base-uncased). Higher SCG score = more inconsistent = predicted hallucination.

**Key assumption:** Hallucinated responses are inconsistently generated (the model "doesn't know" the answer). This assumption holds on benchmarks where hallucinations arise from genuine model uncertainty. On HaluEval-QA, where hallucinations are designed to be confident-sounding, this assumption may invert.

## Evaluation Protocol

All methods are evaluated on the same 2,000-example stratified sample using binary AUROC against HaluEval-QA hallucination labels. AUROC is estimated with 95% bootstrap confidence intervals (N=1000 resamples, seed=42).

Pairwise method comparisons use a significance criterion of Δ AUROC ≥ 0.05 with non-overlapping 95% bootstrap CIs, Bonferroni-corrected for 3 comparisons (corrected α = 0.0167). This criterion is adopted from the sub-hypothesis gate conditions (H-E1) and is more conservative than standard significance testing — requiring both a minimum effect size and non-overlapping CIs.

## Mechanism Verification Sub-Hypotheses

Beyond the main AUROC comparison (H-E1), we formulate and test two mechanism sub-hypotheses that trace the causal chain from NLI clustering to AUROC outcomes:

**H-M1 (Token-Semantic Divergence):** If semantic entropy's NLI filtering is effective, its scores should diverge from token entropy (Pearson r < 0.9 with non-overlapping CI upper bound). If NLI clustering fails, semantic entropy will be constant and the correlation will be undefined.

**H-M2 (NLI Aggregation):** We define the *NLI aggregation rate* as the fraction of examples where the cluster count is strictly less than N=5 (meaning at least two responses were grouped into the same semantic cluster). A rate ≥ 0.50 indicates that NLI clustering is non-trivially aggregating responses; a rate below 0.50 indicates that most responses are assigned to singleton clusters — the mechanism failure condition.

$$\text{aggregation\_rate} = \frac{|\{x : \text{cluster\_count}(x) < N\}|}{|D|}$$

This metric is not reported in the original semantic entropy paper [Kuhn et al., 2023] but is critical for diagnosing degenerate outputs. We report it with 95% bootstrap confidence intervals and compare against the 0.50 threshold.

**Execution order:** H-E1 (main AUROC comparison) → H-M1 (TE-SE correlation diagnosis) → H-M2 (NLI aggregation measurement). Results propagate: H-E1's degenerate SE diagnosis informs H-M1's interpretation; H-M1's cluster distribution data feeds H-M2's aggregation rate computation.

## Reproducibility

All experiments use fixed random seeds (seed=42 for data stratification and bootstrap resampling). Inference results are checkpointed to disk (greedy logits as .pt files, stochastic samples as JSONL, SelfCheckGPT scores as JSON) enabling resume from any failure point. The complete experimental code (data.py, inference.py, uq\_signals.py, evaluate.py, visualize.py) is released with the paper.

The NLI model (deberta-large-mnli) is loaded from HuggingFace and its weights are not modified. The semantic entropy implementation follows lorenzkuhn/semantic\_uncertainty exactly, using the same bidirectional entailment threshold and union-find clustering algorithm as the original paper.
