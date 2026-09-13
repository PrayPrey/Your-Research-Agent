# ScissorHands: Exploiting the Persistence of Importance Hypothesis for LLM KV Cache Compression at Test Time
**arXiv:** 2305.17118 | **Authors:** Liu et al., 2023 | **Citations:** ~200

---

### Abstract & Motivation
ScissorHands proposes the "Persistence of Importance" hypothesis: tokens that attract high attention in early decode steps remain important throughout generation. This means importance patterns stabilize after a warm-up period, enabling a static eviction schedule (computed once after warm-up) rather than per-step dynamic updates.

### Methodology
- **Importance metric:** Attention scores during a warm-up window (first K decode steps). After warm-up, importance is treated as fixed.
- **Eviction policy:** Compute importance from warm-up window → rank tokens → permanently evict lowest-ranked. Static schedule thereafter.
- **Key claim (Persistence hypothesis):** Spearman rank correlation between importance at step K and importance at step K+20 is >0.85 — importance is stable across decode steps.
- **No retraining required.** Applied post-hoc at inference time.

### Experiments & Results
- **Models tested:** GPT-2, OPT-1.3B, OPT-6.7B (BASE models)
- **Benchmarks:** WikiText-2 perplexity, OpenWebText perplexity, summarization (CNN/DM)
- **KV budget:** 20%-50% retention
- **Key result:** ScissorHands within 0.5 PPL of H2O at 20% budget on WikiText-2; warm-up of 32 steps sufficient for stable importance estimation
- **Ablation:** Persistence holds across model sizes; less stable for very short sequences (<128 tokens)
- **Limitations:** Only base models; smaller models (GPT-2, OPT); no instruct or chat models; no LongBench evaluation; no cross-comparison with attention entropy or gradient-based metrics

### Persistence Hypothesis Evidence
- Pearson correlation between importance at step 32 and step 200: r=0.91 (OPT-6.7B, WikiText-2)
- Implication: dynamic per-step eviction adds overhead without accuracy benefit

### What's Missing (Gap 1 Relevance)
ScissorHands uses yet another metric variant (warm-up attention) and never compares it to cumulative attention (H2O), prefill observation (SnapKV), attention entropy, or gradient-based scores. Evaluated on smaller/older models only. Gap 1 needs this unified comparison on LLaMA-2/3 7B on LongBench.
