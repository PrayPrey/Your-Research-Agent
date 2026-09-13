# Methodology

## Overview

ProvenanceCache is a retrieval-aware KV cache eviction policy for long-context RAG systems. Given a query $q$ and a set of retrieved passages $\{p_1, \ldots, p_n\}$ with relevance scores $\{s_1, \ldots, s_n\}$ from a dense retriever (Contriever), ProvenanceCache allocates cache budget across three tiers based on retrieval provenance, then applies diversity-aware selection within each tier to prevent redundant passage retention.

## Provenance-Aware Tiered Eviction

We partition the concatenated context into three tiers based on retrieval metadata:

**Tier 0 (Query Tokens)**: All tokens from the original query $q$ receive highest retention priority. Query tokens serve as attention anchors during generation—particularly for queries explicitly mentioned in answer spans ("Who directed X?" → answer contains "X was directed by..."). Tier 0 receives 10% of total cache budget $B$.

**Tier 1 (High-Relevance Passages)**: Passages with retrieval scores above median: $P_{\text{high}} = \{p_i : s_i \geq \text{median}(s_1, \ldots, s_n)\}$. These passages contain semantically relevant evidence identified by the retriever. Tier 1 receives 60% of budget $B$.

**Tier 2 (Low-Relevance Passages)**: Passages with below-median scores: $P_{\text{low}} = \{p_i : s_i < \text{median}(s_1, \ldots, s_n)\}$. While individually less relevant, these passages preserve contrastive evidence and negative examples needed for multi-hop reasoning ("Entity A is *not* related to Entity B"). Tier 2 receives 30% of budget $B$.

The tier allocation (10/60/30) was validated empirically via grid search over {5%, 10%, 15%} for Tier 0 and {50%, 60%, 70%} for Tier 1, with Tier 2 absorbing the remainder. The selected configuration balanced query-token preservation with passage diversity.

## Diversity-Aware Selection via MMR

Within each passage tier (Tiers 1 and 2), we apply Maximal Marginal Relevance (MMR) selection to prevent redundant passage retention. Given a passage set $P$, current selected set $S$, and remaining budget $k$, we iteratively select:

$$
p^* = \arg\max_{p \in P \setminus S} \left[ \lambda \cdot s_p - (1-\lambda) \cdot \max_{p' \in S} \text{sim}(p, p') \right]
$$

where:
- $s_p$ is the Contriever relevance score (dot-product similarity between query and passage embeddings)
- $\text{sim}(p, p')$ is the cosine similarity between passage embeddings (Contriever 768-dim vectors)
- $\lambda = 0.5$ balances relevance and diversity

The diversity term $\max_{p' \in S} \text{sim}(p, p')$ penalizes passages semantically similar to already-selected passages, spreading cache budget across complementary evidence sources rather than redundant restatements of the same fact.

We use $\lambda = 0.5$ (equal weighting) based on prior MMR literature showing this value balances exploration and exploitation. Ablations in Section 5.3 validate that diversity-aware selection outperforms pure relevance ranking by +14.71% F1 on multi-hop QA.

## Integration with Llama-2-7B

ProvenanceCache integrates with Llama-2-7B via the following pipeline:

**1. Preprocessing**: After retrieving passages via Contriever, we extract:
- Passage boundaries (start/end token positions in concatenated context)
- Contriever relevance scores (query-passage dot products)
- Contriever passage embeddings (for diversity computation)

**2. Tier Assignment**: Map each token position to its tier (0/1/2) based on whether the token belongs to the query, a high-relevance passage, or a low-relevance passage.

**3. MMR Selection**: Within Tiers 1 and 2, apply MMR to select diverse passage subsets that fit within tier budgets. Evict tokens from non-selected passages.

**4. Prefill + Generation**: Run standard Llama-2-7B inference with the reduced KV cache. The eviction is applied **before** the first generation token, so attention computations never see evicted tokens.

**Computational Overhead**: MMR diversity computation requires $O(n^2)$ passage similarity computations, where $n$ is the number of retrieved passages (typically 5-10). For $n=10$, this adds ~5-10ms overhead per query on CPU. Passage embeddings are cached from retrieval preprocessing, so no additional encoder passes are needed.

## Baseline: H2O Heavy-Hitter Oracle

We compare against H2O (Zhang et al., 2023), a state-of-the-art uniform eviction baseline. H2O tracks accumulated attention scores across all layers during prefill:

$$
\text{score}_i = \sum_{\ell=1}^{L} \sum_{j=1}^{N} \text{Attn}_\ell(i, j)
$$

where $\text{Attn}_\ell(i, j)$ is the attention weight from position $j$ to position $i$ at layer $\ell$. After prefill, H2O retains the top-$k$ tokens by accumulated score (heavy hitters) plus a sliding window of recent tokens.

**Key Difference**: H2O requires a full prefill pass to compute attention scores before eviction. ProvenanceCache evicts based on retrieval metadata **before** generation, avoiding redundant computation for passages destined for eviction. This reduces prefill latency by up to 15% for queries where 75% of passages are evicted.

## Theoretical Motivation

ProvenanceCache rests on two hypotheses validated in Section 5:

**H1 (Retrieval-Attention Alignment)**: Dense retrieval scores correlate moderately (Spearman $\rho > 0.3$) with attention weights during generation. We validate this by computing correlations between Contriever scores and per-passage mean attention across layers, finding $\rho = 0.612$ (95% CI [0.601, 0.624]).

**H2 (Diversity for Multi-Hop Reasoning)**: Multi-hop QA requires bridging distant facts across semantically dissimilar passages. Diversity-aware eviction preserves contrastive evidence that pure relevance ranking would discard (e.g., retaining both "Entity A → Bridge Fact" and "Bridge Fact → Entity B" rather than three redundant passages about Entity A).

These hypotheses are tested in controlled ablation studies (Section 5.3) that isolate the contributions of tiered eviction versus diversity-aware selection.
