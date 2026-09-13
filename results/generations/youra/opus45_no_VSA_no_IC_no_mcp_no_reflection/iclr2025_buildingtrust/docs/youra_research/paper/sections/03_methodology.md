# Methodology

Building on our observation that existing hallucination detection methods lack controlled comparison, we design a matched-budget evaluation framework that enables direct method comparison across benchmarks. Our key design principle: hold computational budget constant while varying method and benchmark, exposing method-benchmark interactions that isolated evaluations cannot reveal.

## Overview

We evaluate two sampling-based uncertainty methods—semantic entropy and self-consistency—under identical conditions:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Sample count (N) | 10 | Standard in both original papers [Kuhn et al., 2023; Manakul et al., 2023] |
| Temperature | 0.7 | Enables diverse sampling without excessive noise |
| Max tokens | 256 | Sufficient for QA responses |
| Model | Llama-3-8B-Instruct | Open-weight, reproducible |
| Seed | 42 | Single seed for PoC mode |

This matched-budget design ensures that any performance differences reflect method characteristics, not confounding factors.

## Semantic Entropy

Semantic entropy quantifies uncertainty by clustering generated responses according to semantic equivalence, then computing entropy over the cluster distribution.

**Step 1: Generation.** For each query $q$, we generate $N=10$ responses $\{r_1, \ldots, r_N\}$ using temperature sampling.

**Step 2: Semantic Clustering.** We use DeBERTa-large-mnli [He et al., 2021] to compute bidirectional NLI scores between response pairs. Responses $r_i$ and $r_j$ are considered semantically equivalent if both directions (premise→hypothesis and hypothesis→premise) yield entailment probability above threshold $\tau=0.5$.

**Step 3: Entropy Computation.** Let $\{C_1, \ldots, C_K\}$ be the resulting clusters. The cluster probability distribution is:
$$p_k = \frac{|C_k|}{N}$$

Semantic entropy is computed as:
$$H_{SE} = -\sum_{k=1}^{K} p_k \log p_k$$

Higher entropy indicates responses fall into many distinct semantic clusters, suggesting the model is uncertain.

**Rationale.** By grouping semantically equivalent responses, semantic entropy avoids penalizing surface variation that does not reflect genuine uncertainty. A model that produces "The capital is Paris" and "Paris is the capital" should not be considered uncertain merely because the phrasings differ.

## Self-Consistency

Self-consistency measures agreement across generated responses using surface-level similarity metrics.

**Step 1: Generation.** Identical to semantic entropy—N=10 responses per query.

**Step 2: Pairwise Similarity.** We compute BERTScore F1 [Zhang et al., 2020] between all response pairs:
$$S_{ij} = \text{BERTScore-F1}(r_i, r_j)$$

**Step 3: Consistency Score.** Self-consistency is the mean off-diagonal similarity:
$$SC = \frac{1}{N(N-1)} \sum_{i \neq j} S_{ij}$$

Higher consistency indicates responses are similar, suggesting confident factual knowledge. For hallucination detection, we use $1 - SC$ as the uncertainty score (low consistency → high uncertainty → likely hallucination).

**Rationale.** Unlike semantic entropy, self-consistency does not attempt semantic grouping. It captures a simpler signal: do the responses look similar? The hypothesis is that factual responses, being grounded in reproducible knowledge, should exhibit higher surface consistency than hallucinations.

## Evaluation Protocol

**Benchmarks.** We evaluate on two hallucination benchmarks:

1. **TruthfulQA** [Lin et al., 2022]: 817 questions designed to elicit common misconceptions. Labels based on "Best Answer" matching.

2. **HaluEval-QA** [Li et al., 2023]: 10,000 QA samples with explicit hallucination labels.

**Pilot Mode.** For pipeline validation, we use PoC mode with N=20 samples per dataset. Full-scale evaluation requires the complete datasets.

**Metrics.** Our primary metric is AUROC (Area Under ROC Curve), which measures discrimination ability independent of threshold selection. We compute 95% confidence intervals via bootstrap resampling (1,000 iterations).

**Gate Criterion.** Following verification plan design, we set AUROC > 0.55 (above random + margin) as the minimum threshold for "method works on this benchmark."

## Design Decisions

Several design choices warrant explicit justification:

**Why matched sample count?** Original papers used different N values (semantic entropy: 10; SelfCheckGPT: 5-20). Setting N=10 for both enables computational budget comparison.

**Why single model?** Multiple models introduce confounds. We start with Llama-3-8B to establish baseline findings before extending to other architectures.

**Why PoC mode (N=20 samples)?** Full evaluation is computationally expensive. PoC mode validates pipeline functionality before committing to full-scale runs.

**Why two benchmarks?** TruthfulQA and HaluEval encode different hallucination definitions. If methods perform differently across benchmarks, this reveals benchmark sensitivity that single-benchmark evaluation would miss.
