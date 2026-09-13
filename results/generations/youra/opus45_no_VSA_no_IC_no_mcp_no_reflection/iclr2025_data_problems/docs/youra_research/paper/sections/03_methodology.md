# Methodology

Building on the observation that embedding similarity correlates with transfer performance in domain adaptation contexts, we design EDMP to predict domain utility for LLM pretraining using only frozen embedder inference.

## Overview

EDMP scores each pretraining domain by computing the average cosine similarity between domain sample embeddings and downstream task exemplar embeddings. The intuition is straightforward: domains whose content is semantically closer to task exemplars in embedding space may contribute more to downstream performance. By using a frozen embedder rather than training proxy models, EDMP eliminates the computational overhead of existing optimization methods.

**Scoring Function:**

$$\text{EDMP}(d) = \frac{1}{|S_d|} \sum_{s \in S_d} \frac{1}{|T|} \sum_{t \in T} \cos(E(s), E(t))$$

where $S_d$ is the set of samples from domain $d$, $T$ is the set of task exemplars, and $E(\cdot)$ is the embedding function.

## Embedding Model Selection

**Design Choice:** We select E5-large-v2 [Wang et al., 2022] as the embedder.

**Rationale:** E5-large is a well-validated sentence transformer that produces semantically meaningful embeddings across diverse text domains. Unlike task-specific embedders, E5 was trained on a broad mixture of retrieval tasks, making it suitable for cross-domain similarity computation. The 1024-dimensional embedding space provides sufficient capacity to capture semantic distinctions between domains.

**Alternative Considered:** BGE-large and OpenAI embeddings were considered but not tested in this work. E5-large was chosen for reproducibility (open weights) and established performance on retrieval benchmarks.

## Task Exemplar Selection

**Design Choice:** We use the MMLU validation set as task exemplars.

**Rationale:** MMLU [Hendrycks et al., 2021] spans 57 subjects across STEM, humanities, social sciences, and other domains, providing broad coverage of downstream task types. The validation set contains approximately 1,500 questions, sufficient to represent the task distribution while remaining computationally tractable for embedding.

**Format:** Each exemplar is formatted as:
```
"{question} A: {choice_A} B: {choice_B} C: {choice_C} D: {choice_D}"
```

This format includes both the question and answer choices, capturing the full context that models must process during evaluation.

## Domain Sample Processing

**Design Choice:** We sample 1,000 texts per domain, truncated to 512 tokens.

**Rationale:** Preliminary experiments suggested diminishing returns beyond 1,000 samples for score stability. The 512-token truncation matches E5-large's maximum context length while capturing sufficient domain-specific vocabulary.

**Embedding Prefixes:** Following E5 conventions, domain samples are prefixed with "passage: " and task exemplars with "query: ". This asymmetric prefixing aligns with E5's training regime for retrieval tasks.

## Scoring Pipeline

The EDMP scoring pipeline executes as follows:

1. **Domain Embedding:** Embed all domain samples using E5-large with "passage: " prefix. Normalize embeddings to unit length.

2. **Task Embedding:** Embed all task exemplars using E5-large with "query: " prefix. Normalize embeddings to unit length.

3. **Similarity Computation:** Compute the cosine similarity matrix between domain embeddings and task embeddings.

4. **Aggregation:** For each domain, compute the mean similarity across all its samples and all task exemplars.

5. **Ranking:** Rank domains by EDMP score in descending order.

**Algorithm 1: EDMP Scoring**

```
Input: Domains D = {d_1, ..., d_n}, Task exemplars T
Output: Domain scores {score(d_i)}

for each domain d in D:
    samples = sample(d, n=1000)
    domain_emb = E5("passage: " + samples)  # [1000, 1024]
    domain_emb = normalize(domain_emb)

task_emb = E5("query: " + T)  # [|T|, 1024]
task_emb = normalize(task_emb)

for each domain d in D:
    sim_matrix = domain_emb[d] @ task_emb.T  # [1000, |T|]
    score(d) = mean(sim_matrix)

return sorted(scores, descending=True)
```

**Computational Complexity:** Embedding 8 domains × 1,000 samples requires approximately 8,000 forward passes through E5-large. On a single A100 GPU, this completes in under 30 minutes—substantially faster than training a proxy model.

## Validation Criteria

To validate that EDMP produces meaningful signals, we define the following criteria:

1. **Score Computability:** All domains must produce valid similarity scores without numerical issues.

2. **Non-Trivial Variance:** Cross-domain score variance must exceed a threshold (std > 0.05) to enable discrimination between domains.

3. **Statistical Significance:** Domain scores must be statistically distinguishable (ANOVA p < 0.05).

4. **Reproducibility:** Scores must be consistent across random seeds (variance < 0.05).

These criteria validate the existence of a domain scoring mechanism before testing its predictive power for downstream performance.
