# SnapKV: LLM Knows What You are Looking for Before Generation
**arXiv:** 2404.14469 | **Authors:** Li et al., 2024 | **Citations:** ~150

---

### Abstract & Motivation
SnapKV observes that during the prefill phase, attention patterns already reveal which tokens the model will attend to during generation. By computing a query-aware importance score during prefill — before any decode step — SnapKV selects and retains the most relevant KV cache entries upfront, enabling one-shot compression without per-step eviction overhead.

### Methodology
- **Importance metric (prefill-observation):** For each KV position i, compute importance = mean attention weight received from the last W query tokens in the prompt (observation window, default W=16 or 32). This is query-aware: tokens the model attends to from the recent query window are retained.
- **Eviction timing:** PREFILL-PHASE only — compress once before generation starts; no per-decode-step decisions.
- **Implementation:** No retraining. Plug-in to HuggingFace generate(). Requires knowing prompt structure (observation window applied to final query tokens).
- **Cluster pooling:** Optional: use max-pooling over nearby positions to avoid fragmentation artifacts.

### Experiments & Results
- **Models tested:** LLaMA-2-7B-chat, LLaMA-2-13B-chat, LLaMA-3-8B-instruct (INSTRUCT models)
- **Benchmarks:** LongBench (16 tasks), RULER (long-context synthetic), NarrativeQA, Qasper
- **KV budget:** 20% retention (80% eviction) AND 40% retention (60% eviction)
- **Key result:** SnapKV matches full-KV on LongBench at 40% retention; minor degradation at 20%; significantly outperforms H2O and StreamingLLM at matched budgets on LongBench
- **Claimed advantage over H2O:** Query-aware (uses query context) vs. query-agnostic (cumulative over all decode steps); prefill-phase compression avoids per-step overhead
- **Limitations:** Only tested on instruct models — no base model results; no ablation comparing prefill-observation to entropy-based or gradient-based metrics; LLaMA-2/3 only; no Mistral or Falcon evaluation

### Key Innovation vs. Baselines
| Method | Metric Type | Query-Aware | Timing |
|--------|-------------|-------------|--------|
| StreamingLLM | Static window | No | N/A |
| H2O | Cumulative attn | Partially (all decode steps) | Per-step |
| SnapKV | Prefill observation | Yes (query window) | Prefill only |

### What's Missing (Gap 1 Relevance)
SnapKV claims superiority over H2O but the comparison conflates metric type AND timing AND model type (SnapKV tests instruct, H2O tests base). No controlled ablation: same model, same benchmark, same budget, varying only the importance metric. Gap 1 is precisely this missing controlled comparison.
