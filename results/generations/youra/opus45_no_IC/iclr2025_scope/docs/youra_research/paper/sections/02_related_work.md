# Related Work

We review KV cache compression methods along two axes: eviction-based approaches that discard tokens, and compression-based approaches that reduce precision. We then position our contribution in task-aware compression selection.

## KV Cache Eviction Methods

**Heavy-hitter eviction.** H2O [Zhang et al., 2023] identifies tokens contributing disproportionately to attention scores and evicts low-importance tokens while retaining recent context. At 20% retention, H2O achieves less than 2% accuracy degradation on perplexity benchmarks. Ada-KV [Feng et al., 2024] extends this with adaptive per-head budget allocation and provides theoretical loss bounds. RocketKV [Behnam et al., 2025] combines coarse eviction with fine-grained sparse attention, claiming up to 400x compression.

**Attention sink methods.** StreamingLLM [Xiao et al., 2023] discovers that initial tokens serve as "attention sinks" regardless of semantic content, and naive window attention fails without retaining these tokens. This enables infinite-length generation with fixed memory by combining sink tokens with recent context.

**Adaptive methods.** EvolKV [Yu & Chai, 2025] uses evolutionary search for layer-wise budget allocation, demonstrating that optimal compression varies across layers. SmallKV [Zhao et al., 2025] employs a small model to assist large model attention under compression.

*Limitation:* These methods optimize *within* a single compression paradigm. H2O selects which tokens to evict but applies the same eviction ratio across all tasks. Ada-KV adapts per-head but not per-task. None systematically addresses whether the *choice* between eviction and quantization should depend on task type.

## Compression-Based Methods

**KV cache quantization.** While weight quantization is well-established, KV cache quantization remains less explored. TurboQuant and similar methods apply INT8/INT4 precision to cached keys and values. Shard [2026] combines PCA-based key compression with vector quantization for values, achieving 10x memory reduction.

**Low-rank methods.** LESS [Dong et al., 2024] synthesizes recurrence with eviction, recovering information for tasks requiring token recollection. Low-rank concepts from LoRA [Hu et al., 2021] have inspired factorization approaches to state compression.

*Limitation:* Quantization and low-rank methods are typically evaluated in isolation from eviction methods, lacking systematic comparison under unified conditions.

## Task-Aware Optimization

**Benchmarks.** LongBench [Bai et al., 2023] provides 21 datasets across 6 task categories (single-doc QA, multi-doc QA, summarization, few-shot, synthetic, code), enabling category-level analysis. RULER and SCROLLS offer complementary evaluation.

**Task-dependent hints.** EvolKV observes that optimal layer budgets vary by task but does not quantify cross-task structure or provide a selection mechanism. No prior work applies gap statistic or clustering analysis to characterize task-compression relationships.

*Gap we address:* Existing methods evaluate aggregate benchmark scores without characterizing per-task behavior. We provide the first rigorous quantification that tasks cluster into distinct compression response groups, and that attention entropy can discriminate these groups—establishing the empirical foundation for task-conditioned compression selection that prior work lacks.

## Our Position

We complement rather than replace existing compression methods. H2O, StreamingLLM, and quantization remain effective compression primitives. Our contribution is demonstrating that *selecting among* these methods should consider task structure, and providing evidence that such structure exists and is detectable. This positions task-conditioned compression as a research direction building on established foundations.
