# Related Work

## KV Cache Compression for Transformers

The quadratic memory growth of transformer KV caches has motivated extensive work on compression methods. **H2O** (Zhang et al., 2023) introduces heavy-hitter oracle eviction, tracking accumulated attention scores across layers to identify tokens that contribute most to attention computations. By retaining a small fraction (20%) of heavy-hitter tokens plus recent tokens, H2O achieves 29× throughput improvement on OPT-6.7B with minimal accuracy loss. However, H2O's uniform attention-based policy treats all tokens identically regardless of structural properties (query boundaries, retrieval provenance).

**StreamingLLM** (Xiao et al., 2024) preserves initial attention sink tokens plus a sliding window of recent context, enabling infinite-length streaming with constant memory. While effective for conversational systems, StreamingLLM's fixed window discards distant but semantically relevant retrieved passages—problematic for multi-hop QA requiring evidence synthesis across documents.

**DynamicKV** (Liu et al., 2024) extends H2O with per-layer budget allocation, observing that different transformer layers exhibit distinct attention patterns (early layers focus on local syntax, late layers on global semantics). Per-layer eviction improves efficiency by 2-3% over global budgets. Our work is complementary—ProvenanceCache could apply per-layer budgets to provenance-aware tiers for additional gains.

A key limitation shared by these methods: they operate on attention scores computed from the original context, requiring expensive prefill passes before eviction. ProvenanceCache uses retrieval metadata available at preprocessing time, enabling eviction **before** the first generation token—eliminating redundant computation for passages destined for eviction.

## Dense Retrieval for RAG Systems

Dense retrieval methods encode queries and passages into shared embedding spaces, ranking by semantic similarity rather than lexical overlap. **DPR** (Karpukhin et al., 2020) trains dual BERT encoders on question-passage pairs, achieving state-of-the-art open-domain QA results by retrieving relevant contexts for reader models. **Contriever** (Izacard et al., 2021) extends DPR to unsupervised learning via contrastive pretraining, eliminating dependence on labeled retrieval pairs.

These retrieval systems produce relevance scores (dot-product similarities) and passage boundaries as byproducts of retrieval. However, downstream generation models (reader LLMs) typically discard this metadata after concatenating retrieved passages into a single context string. Our work demonstrates that retrieval scores **generalize** from passage ranking (retrieval task) to attention prediction (generation task), with Contriever showing ρ=0.612 Spearman correlation—57% stronger than lexical BM25 (ρ=0.391).

## Diversity in Information Retrieval

Diversity-aware ranking prevents redundant results in search systems. **Maximal Marginal Relevance (MMR)** (Carbonell & Goldstein, 1998) balances relevance and novelty via a weighted combination: λ × relevance + (1-λ) × diversity (embedding cosine distance from already-selected documents). MMR with λ=0.5 produces diverse result sets without excessive relevance sacrifice.

Coverage-based ranking (Clarke et al., 2008) models query intent as a distribution over subtopics, rewarding documents that cover under-represented aspects. These methods target retrieval ranking (top-k selection from large candidate pools). ProvenanceCache extends diversity principles to **cache eviction**—memory-constrained retention where all passages are initially in cache, and we must select which to preserve.

Our work shows diversity matters asymmetrically by task type: +14.71% F1 gain on multi-hop QA (bridging distant facts across dissimilar passages) versus +6.16% on single-hop factoid QA (top-k relevance ranking sufficient). This finding validates that multi-hop reasoning is a **coverage problem** (maximize diverse evidence span), not a **ranking problem** (maximize top-k scores).

## Multi-Hop Question Answering

Multi-hop QA requires synthesizing evidence across multiple documents. **HotpotQA** (Yang et al., 2018) introduced the bridge entity task: answering "What nationality is the director of film X?" requires retrieving (1) "X was directed by Y" and (2) "Y has nationality Z." Both passages are semantically relevant to the query, but neither alone suffices—diversity preserves both rather than overweighting the first high-relevance hit.

**MuSiQue** (Trivedi et al., 2022) extends multi-hop reasoning to disconnected reasoning chains requiring 2-4 hops across compositional questions. These datasets motivate our diversity-aware eviction policy: naïve top-k retention by relevance over-allocates cache budget to redundant passages about Entity A, evicting critical bridging facts about Entity B.

Our experiments on LongBench multi-doc QA (subset of HotpotQA + narrativeqa + triviaqa) demonstrate that MMR diversity scoring prevents this failure mode, achieving 2.4× larger gains on multi-hop questions than single-hop factoid QA.

## Relationship to Prior Work

ProvenanceCache differs from prior KV cache compression in three ways:

1. **Metadata source**: Uses retrieval provenance (passage boundaries, Contriever scores) rather than runtime attention (H2O, DynamicKV) or positional heuristics (StreamingLLM).

2. **Eviction timing**: Applies provenance-based eviction **before** first generation token (at preprocessing), not after accumulated attention tracking.

3. **Task-aware diversity**: Incorporates MMR diversity metric to prevent redundant high-relevance passage retention on multi-hop tasks.

To our knowledge, this is the first work to condition KV cache eviction on retrieval metadata and empirically validate that retrieval scores predict attention patterns during generation (ρ=0.612 correlation).
