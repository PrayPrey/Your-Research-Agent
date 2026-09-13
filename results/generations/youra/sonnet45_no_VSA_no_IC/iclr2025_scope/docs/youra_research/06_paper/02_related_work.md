# 2. Related Work

## 2.1 KV Cache Eviction

**H2O (Heavy-Hitter Oracle)** [Zhang et al., 2023] pioneered attention-based KV cache eviction, retaining tokens with highest accumulated attention scores (heavy hitters) plus recent tokens to maintain fluency. At 20% cache retention, H2O achieves 29× throughput improvement with minimal accuracy loss on PG-19 and arXiv summarization tasks. H2O's key insight: attention weights predict token importance during generation.

**Limitation for RAG**: H2O treats all tokens uniformly, accumulating attention scores without distinguishing query tokens (e.g., "What caused the 1929 stock market crash?") from retrieved passage tokens (evidence from retrieved documents). In RAG scenarios, retrieval metadata (passage boundaries, semantic relevance scores from Contriever/DPR) provides orthogonal signal to attention scores — a query token may have low accumulated attention early in generation but remains critical for question grounding throughout.

**StreamingLLM** [Xiao et al., 2024] enables infinite-length inference via fixed sliding window (most recent N tokens) plus attention sinks (initial tokens that accumulate high attention). StreamingLLM achieves constant memory consumption but discards all context outside the window, making it unsuitable for multi-document QA where evidence may appear anywhere in the retrieved passages.

**KVCache-Factory** [Cai et al., 2024] provides unified benchmarking platform for six cache methods (FullKV, StreamingLLM, H2O, SnapKV, Quest, PyramidKV) on LongBench evaluation suite. Factory evaluation shows H2O and SnapKV achieve best accuracy-memory trade-offs on long-context understanding tasks (document summarization, code completion). However, no RAG-specific method tested — all evaluated methods use uniform eviction strategies without retrieval provenance conditioning.

**DynamicKV** [Agarwal et al., 2024] extends H2O with per-layer cache budgets, allocating more memory to early layers (where attention patterns stabilize) and less to later layers. DynamicKV achieves 5-10% additional efficiency over global H2O by exploiting layer-wise attention heterogeneity. Our work is orthogonal: ProvenanceCache could integrate per-layer budgets as future extension.

## 2.2 Retrieval-Augmented Generation (RAG)

**Dense Retrieval**: Contriever [Izacard et al., 2022] and DPR [Karpukhin et al., 2020] encode queries and passages into dense embeddings, ranking passages by cosine similarity. Contriever achieves state-of-the-art zero-shot retrieval (nDCG@10 > 0.5 on BEIR benchmark) via contrastive pre-training on unlabeled corpora. BM25 [Robertson & Zaragoza, 2009] remains competitive baseline using lexical term frequency-inverse document frequency scoring.

**Multi-Hop QA**: HotpotQA [Yang et al., 2018] and MuSiQue [Trivedi et al., 2022] require reasoning over multiple passages to bridge distant facts (e.g., "Entity A born in City X → City X located in Country Y → what is Country Y's capital?"). Multi-hop questions expose limitations of top-k retrieval: ranking passages independently by relevance may select redundant evidence (three passages about Entity A, zero about bridging fact or Entity B).

**Maximal Marginal Relevance (MMR)** [Carbonell & Goldstein, 1998] addresses redundancy by iteratively selecting passages that maximize `λ * relevance(q, p) - (1-λ) * max_similarity(p, selected)` — balancing query relevance and diversity from already-selected passages. MMR λ=0.5 equally weights relevance and diversity. Prior work applied MMR to **retrieval ranking** (top-k diverse results). We extend MMR to **cache eviction** (memory-constrained passage retention).

## 2.3 Long-Context Benchmarks

**LongBench** [Bai et al., 2023] provides standardized evaluation across 21 datasets (6 task categories: single-doc QA, multi-doc QA, summarization, few-shot learning, synthetic tasks, code completion) with average context length 6711 words (English). Multi-doc QA subset (HotpotQA, 2WikiMultihopQA, MuSiQue, NarrativeQA, TriviaQA) requires reasoning over 10-20 retrieved passages — ideal testbed for RAG cache strategies. LongBench reports baseline accuracy (FullKV, no eviction) for Llama-2-7B: ~60% F1 on multi-doc QA, establishing upper bound for cache-constrained methods.

**SCROLLS** [Shaham et al., 2022] evaluates seven long-document understanding tasks (up to 100k tokens per example) including multi-document QA and summarization. SCROLLS focuses on document-level reasoning without explicit retrieval step, making it less suitable for RAG-specific cache analysis but valuable for cross-dataset transfer validation (future work).

## 2.4 Gaps in Prior Work

1. **No RAG-Conditioned Cache Strategies**: All prior KV cache methods (H2O, StreamingLLM, DynamicKV, SnapKV, Quest, PyramidKV) use uniform eviction based on attention scores or recency, ignoring retrieval metadata (passage boundaries, relevance scores, query-passage structure) available in RAG systems.

2. **Diversity Ignored in Cache Eviction**: MMR diversity widely used in retrieval ranking (top-k diverse results) but never applied to cache eviction (memory-constrained retention). Multi-hop QA requires diverse passage coverage — relevance-only eviction over-allocates to redundant high-scoring passages.

3. **Tiered Priority Not Explored**: Query tokens provide question grounding throughout generation, yet H2O/StreamingLLM may evict query tokens if they have low accumulated attention. No prior work establishes tiered priority (query > passages > generated tokens) for RAG scenarios.

**ProvenanceCache** addresses these gaps by: (1) conditioning eviction on retrieval provenance (query/passage tiers, Contriever relevance scores), (2) applying MMR diversity to cache retention (not just retrieval ranking), (3) validating tiered priority (query tokens always preserved) via hypothesis chain (h-e1 → h-m1 → h-m2 → h-m4).
