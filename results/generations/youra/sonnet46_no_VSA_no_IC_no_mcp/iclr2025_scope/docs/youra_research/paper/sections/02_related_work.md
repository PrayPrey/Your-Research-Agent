# 2. Related Work

KV cache eviction has emerged as the dominant approach to managing memory in long-context transformer inference. We organize prior work into three categories: static eviction policies, query-aware dynamic policies, and unified benchmarking efforts. Critically, all existing implementations integrate eviction into the attention forward pass — which is why the DynamicCache failure mode we document in Section 3.4 has not previously been reported.

## 2.1 Static Eviction Policies

StreamingLLM [Xiao et al., 2023] establishes the minimal viable eviction policy: retain a small set of attention sink tokens (typically the first 4 positions, which consistently receive disproportionate attention weight) plus a recent sliding window. No importance scoring is required; eviction is purely positional. StreamingLLM demonstrates that models can generate indefinitely without degradation under this scheme, as long as the positional structure of the window is maintained. Critically, StreamingLLM integrates directly with the model's generation loop — no post-hoc cache manipulation. It serves as the lower-bound baseline for query-aware methods.

## 2.2 Query-Aware Dynamic Policies

**H2O** [Zhang et al., 2023] proposes cumulative attention accumulation as a token importance metric: each token's importance is the sum of attention weights it has received across all generation steps. H2O evicts low-cumulative-attention tokens at each decode step, maintaining a fixed-size KV cache. The implementation modifies the attention module's per-step forward computation, accumulating importance in-place and applying top-k eviction before each layer appends to past_key_values. H2O reports substantial perplexity improvement over StreamingLLM on WikiText-2 and MT-Bench at 20% KV retention, on base models (OPT, LLaMA). It does not compare against prefill-timing or query-conditioned alternatives.

**SnapKV** [Li et al., 2024] introduces prefill-observation importance scoring: instead of accumulating importance during generation, SnapKV examines attention patterns during the prefill phase, specifically averaging attention weights from the last W query tokens to identify positions that the query region consistently attends to. Eviction occurs once, before generation begins, rather than at each decode step. SnapKV's implementation overrides LlamaAttention.forward() directly — the eviction logic runs inside the attention module, modifying the key/value tensors before they are appended to past_key_values. SnapKV reports strong results on LongBench with LLaMA-2/3-chat models at 40-60% KV retention. However, SnapKV conflates metric type (query-conditioned vs. cumulative) with eviction timing (prefill vs. decode), making it impossible to attribute its advantage to either factor independently.

**ScissorHands** [Liu et al., 2023] motivates its design with the "importance persistence hypothesis": attention patterns at decode step K correlate strongly with attention patterns at step K+20 (Spearman r>0.85 on OPT-6.7B). Based on this observation, ScissorHands computes importance during a warmup period (first 32 decode steps), then freezes the eviction schedule for the remainder of generation. Like H2O and SnapKV, ScissorHands integrates its importance computation and eviction directly within the attention forward pass.

**PyramidKV** [Cai et al., 2024] extends per-token eviction to per-layer budgeting, allocating more KV budget to early layers (which attend broadly) and less to later layers (which attend locally). The layer-adaptive allocation is implemented as a modification to each layer's forward computation.

**RazorAttention** [Tang et al., 2024] stratifies attention heads into "retrieval heads" (which attend to specific spans relevant to the query) and "non-retrieval heads" (which attend to fixed structural positions). Eviction is applied differently per head type. Again, the implementation operates within the attention forward pass.

## 2.3 Unified Benchmarking and Infrastructure

**LongCache** [Liu et al., 2024] proposes a comparative evaluation framework for KV eviction methods on NarrativeQA, QuALITY, and SCROLLS. It evaluates multiple methods under a common evaluation protocol. However, it does not control for metric-type vs. timing confounds (H2O is decode-timed, SnapKV is prefill-timed) and uses each method's original implementation rather than a unified codebase.

## 2.4 Why Prior Work Does Not Encounter the DynamicCache Failure

A consistent pattern across all reviewed implementations is that eviction occurs inside the attention module's forward computation. When a layer's forward pass runs, it applies the importance-weighted top-k selection to the current key/value tensors and modifies the layer's portion of past_key_values before adding the new token's KV. The DynamicCache object is never reconstructed from scratch — it is updated incrementally through the standard HuggingFace interface.

Our implementation diverged from this pattern. Following standard API documentation, we attempted to apply eviction to the complete KV cache after the prefill phase, then reconstruct a DynamicCache object from the evicted tensors using the ddp_cache_data parameter. This reconstruction creates an object with correct tensor shapes but incorrect internal state, as transformers 5.x DynamicCache stores additional bookkeeping beyond the raw (key, value) tuples. The library's constructor does not validate this state, and generation proceeds with a silently corrupt cache.

To our knowledge, no paper in the KV eviction literature documents this failure mode, because no paper has used post-hoc reconstruction as the implementation pattern. Our contribution is to make this failure explicit, characterize it with controlled evidence, and point to the correct implementation approach. The affirmative value is concrete: any researcher building a unified KV eviction benchmark — precisely the kind of controlled comparison the field currently lacks — will encounter this silent failure when using the documented HuggingFace API to manipulate past_key_values. Our paper short-circuits that wasted GPU time and points directly to the correct integration pattern.

## 2.5 Relationship to Our Work

Our experimental design targets the metric-type confound that prior work leaves unresolved. By implementing both prefill-observation (M1, SnapKV-style) and cumulative-at-prefill (M2, H2O-style applied at prefill timing) in a unified codebase with pluggable score functions, we can isolate metric-type effects from timing effects. The DynamicCache failure mode we encountered during implementation is a direct consequence of attempting to build this unified codebase using HuggingFace's documented API rather than adapting an existing forward-pass implementation. We document this failure and the corrected approach so that future unified-codebase efforts can proceed directly to the scientific comparison.
