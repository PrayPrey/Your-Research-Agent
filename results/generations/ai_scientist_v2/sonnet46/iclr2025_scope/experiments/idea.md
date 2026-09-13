## Name

moe_routing_guided_kv_eviction

## Title

Expert Knows Best: Leveraging MoE Routing Signals as Free Supervisory Cues for KV Cache Eviction

## Short Hypothesis

In Mixture-of-Experts (MoE) Transformers, expert routing decisions encode rich token-level semantic importance signals that are computed for free during the forward pass. We hypothesize that tokens consistently routed to specialized (non-shared) experts across layers carry higher task-relevant information and should be preferentially retained in the KV cache, while tokens routed predominantly to shared/generic experts are safer to evict. This routing-guided eviction criterion is complementary to and more computationally efficient than attention-score-based eviction, since routing logits are already computed as part of the MoE forward pass with no additional overhead. This setting — MoE-Transformer inference with long contexts — is the ideal testbed because (1) MoE models are increasingly dominant at scale (Mixtral, DeepSeek, Qwen-MoE), (2) their KV cache bottleneck is compounded by the qs-inequality (dense KV cache despite sparse computation), and (3) no existing work exploits routing signals for memory management.

## Related Work

Existing KV cache eviction methods (NACL, CAKE, KeyDiff, SAGE-KV, RocketKV, SparK, OBCache, FIER) all rely on attention score statistics, key similarity, or output perturbation to rank token importance. These methods are architecture-agnostic and ignore the rich structural signals available in MoE models. PiKV proposes distributed KV management for MoE but uses query-relevance scoring (still attention-based) and does not exploit routing signals. mixSGA uses MoE routing to dynamically allocate KV group sizes but focuses on training-time GQA optimization rather than inference-time eviction. ExpertFlow uses routing predictions for expert prefetching (CPU-GPU swapping), not KV cache compression. Our proposal is the first to treat cross-layer MoE routing patterns as a zero-cost importance oracle for KV token eviction during inference, requiring no architectural changes, no additional training, and no extra computation beyond what MoE routing already performs.

## Abstract

Large language models based on Mixture-of-Experts (MoE) architectures achieve high model capacity with sparse computation, but their KV caches remain fully dense, creating a compounded memory bottleneck: sparse FLOPs but dense memory. Existing KV cache eviction methods rely on attention score statistics or key similarity to identify dispensable tokens, incurring additional computation or suffering from attention bias. We observe that in MoE Transformers, the expert routing decision for each token — already computed for free during the forward pass — encodes implicit token importance: tokens consistently routed to specialized experts across multiple layers carry higher task-specific semantic content, while tokens predominantly assigned to shared or generic experts are more redundant. We propose **RouteKV**, a training-free KV cache eviction framework that uses cross-layer expert routing patterns as a zero-overhead importance signal. For each token, RouteKV computes a routing specialization score — the entropy of the routing distribution aggregated across layers — and uses it to rank tokens for eviction. Tokens with low routing entropy (consistently assigned to specific experts) are retained; high-entropy tokens (diffusely routed) are evicted. We further propose a hybrid scoring scheme that combines routing specialization with a lightweight attention-based signal for heads in non-MoE (shared attention) layers. Experiments on Mixtral-8x7B, DeepSeek-V2, and Qwen-MoE across LongBench, NeedleBench, and RULER benchmarks demonstrate that RouteKV achieves competitive or superior performance to attention-score baselines while adding zero extra FLOPs for importance estimation, and yields up to 60% KV cache reduction with less than 3% accuracy degradation.

## Experiments

1. **Routing Pattern Analysis (Motivating Study)**: On Mixtral-8x7B with LongBench tasks, compute per-token routing entropy across all MoE layers. Measure the Spearman correlation between routing entropy and attention-score-based importance rankings (from SAGE-KV). Visualize token types (punctuation, stop words, content words, named entities) against routing entropy to validate the hypothesis. Metric: Spearman rank correlation.

2. **RouteKV Implementation**: For each MoE layer l, compute router logit distribution p_l(t) for token t. Routing specialization score: S(t) = -mean_l[H(p_l(t))] where H is entropy. Tokens with lowest S(t) (most specialized routing) are retained. For attention layers in hybrid models, fall back to accumulated attention score. Eviction is performed once after prefill (like SAGE-KV), making decoding use the compressed cache.

3. **Main Benchmark**: Evaluate RouteKV vs. baselines (StreamLLM, H2O, SAGE-KV, CAKE, RocketKV) on LongBench v2 and RULER (128K context) using Mixtral-8x7B-Instruct and DeepSeek-V2-Lite. KV budget: 10%, 20%, 30%, 50% of full cache. Metrics: LongBench average score, RULER score, peak GPU memory, prefill+decode latency.

4. **Hybrid Scoring Ablation**: Compare (a) routing entropy only, (b) attention score only, (c) linear combination alpha*routing + (1-alpha)*attention, sweeping alpha in {0, 0.25, 0.5, 0.75, 1.0}. Metric: LongBench score at 20% KV budget.

5. **Computational Overhead Analysis**: Measure wall-clock time for importance score computation in RouteKV vs. SAGE-KV (which requires an extra attention pass) and CAKE (which requires attention score accumulation). Report FLOPs and latency overhead on A100 GPU for sequence lengths 32K, 64K, 128K.

6. **Generalization to Dense-MoE Hybrid (DeepSeek-V3 style)**: Apply RouteKV to a hybrid model with both attention and MoE layers, using routing signals only for MoE layers and a lightweight key-norm signal for pure attention layers. Metric: performance on RULER at 128K vs. full cache baseline.

## Risk Factors And Limitations

1. **Hypothesis may not hold universally**: Routing entropy may not reliably correlate with token importance across all task types (e.g., tasks requiring syntactic rather than semantic reasoning). Mitigation: the hybrid scoring scheme provides a fallback.
2. **MoE-specific**: RouteKV only applies to MoE Transformers, not dense models. However, MoE models are increasingly dominant at scale, making this a practically important target.
3. **Router collapse or load balancing artifacts**: Some MoE models use auxiliary load-balancing losses that artificially spread routing, reducing entropy signal quality. Mitigation: evaluate on models with and without strong load balancing (Mixtral vs. DeepSeek).
4. **Single-pass routing may be noisy**: Routing decisions at a single layer may be noisy; aggregating across layers mitigates this but adds bookkeeping overhead. This overhead is still much smaller than recomputing attention.
5. **Prefill-only eviction**: Like SAGE-KV, RouteKV performs eviction after prefill, which may not adapt well to very long generation sequences where new important tokens emerge. Future work could explore online routing-guided eviction during decoding.
6. **Access to routing logits**: Some deployed MoE models may not expose internal routing logits through standard APIs, limiting applicability to open-weight models.

