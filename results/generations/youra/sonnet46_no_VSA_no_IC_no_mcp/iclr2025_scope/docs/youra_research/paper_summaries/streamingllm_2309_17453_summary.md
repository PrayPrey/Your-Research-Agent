# Efficient Streaming Language Models with Attention Sinks
**arXiv:** 2309.17453 | **Authors:** Xiao et al., 2023 | **Citations:** ~800

---

### Abstract & Motivation
StreamingLLM identifies "attention sinks" — a small set of initial tokens (typically positions 0-3) that receive disproportionately high attention regardless of content. By always retaining these sinks plus a sliding window of recent tokens, StreamingLLM enables streaming inference over infinite-length sequences without full KV cache recomputation, at the cost of losing distant context.

### Methodology
- **Eviction policy:** STATIC — no importance scoring. Retain: (a) first 4 tokens (attention sinks) + (b) sliding window of most recent W tokens. All other tokens evicted.
- **No query-awareness, no importance metric.** Pure positional heuristic.
- **Key insight:** Without attention sinks, softmax attention collapses when initial tokens are evicted (numerical instability). Sinks are necessary anchors.
- **Implementation:** HuggingFace compatible; tested on LLaMA-2-7B/13B, Mistral-7B, Falcon-7B/40B.

### Experiments & Results
- **Models tested:** LLaMA-2-7B/13B/70B, Mistral-7B, Falcon-7B/40B (base models)
- **Benchmarks:** WikiText-2 perplexity (streaming), PassKey retrieval (long-context)
- **Window size:** 256-2048 tokens
- **Key result:** StreamingLLM maintains stable PPL over 4M-token streams; H2O without attention-sink fix degrades (PPL spikes) at long sequences
- **Cross-architecture note:** Tests LLaMA + Mistral + Falcon, establishing multi-arch baseline — but only for static eviction. No cross-arch test for query-aware metrics.
- **Limitations:** Cannot retrieve long-range information (anything outside the window is gone); purely positional — loses all query-aware selectivity; evaluated on base models; perplexity only (no LongBench/SCROLLS QA tasks)

### Role as Baseline
StreamingLLM is the canonical STATIC baseline for all query-aware eviction methods. Gap 1 hypothesis needs StreamingLLM as the lower-bound baseline in the metric comparison.

### What's Missing (Gap 1 Relevance)
StreamingLLM is the baseline all query-aware methods must beat. It establishes that positional eviction is insufficient for long-context QA. Gap 1 uses it as baseline and compares cumulative attention (H2O), prefill observation (SnapKV), warm-up attention (ScissorHands), and attention entropy against it.
