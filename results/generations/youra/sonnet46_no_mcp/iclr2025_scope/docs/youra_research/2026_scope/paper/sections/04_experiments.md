# 4. Experimental Setup

We design experiments to test the mechanistic claims of Eviction-Aware LoRA in three stages, corresponding to our three sub-hypotheses.

## 4.1 Research Questions

**RQ1 (Existence — H-E1):** Does applying H2O eviction masks during LoRA training produce adapter weight matrices that are statistically different from sequential-baseline adapters trained without eviction constraints?

**RQ2 (Mechanism — H-M1):** Does eviction-aware training restructure the attention patterns of the resulting adapters, and if so, which transformer layers are most affected?

**RQ3 (Dose-Response — H-M2):** Does the accuracy advantage of eviction-aware training increase monotonically as the KV budget tightens (i.e., does a smaller ρ produce a larger accuracy gap)?

RQ1 and RQ2 test the mechanistic preconditions for the primary accuracy claim (P1: ≥2% LongBench accuracy improvement at r=50%). RQ3 tests a secondary dose-response prediction (P2). The primary accuracy evaluation (P1) on LLaMA-2-7B and Mistral-7B-v0.1 constitutes H-M3, which requires gated model access and is planned as the immediate next experiment (see Section 6.1).

## 4.2 Models and Data

**Proxy Model:** GPT-2 (117M parameters, 12 transformer layers, 12 attention heads, 768 hidden dim, 1024-token context window). We use GPT-2 as a mechanism-validation proxy because (a) it does not require gated model access, (b) its transformer architecture is mechanism-equivalent to LLaMA-2/Mistral for gradient-signal analysis (Q/K/V projections through which eviction masks change gradients), and (c) its compact size enables rapid iteration. The proxy validity boundary — GPT-2's 1024-token context window is incompatible with LongBench task requirements of 2,000–10,000 tokens — is documented explicitly as Limitation L3 (Section 6.2).

**Target Models (H-M3, future work):** LLaMA-2-7B (`meta-llama/Llama-2-7b-hf`) and Mistral-7B-v0.1 (`mistralai/Mistral-7B-v0.1`). Both require gated HuggingFace access unavailable during the experiments reported here. The H2O training wrapper has been architecturally validated for both models' layer structure.

**Training Data:** LongAlpaca-12k (Yukang/LongAlpaca, HuggingFace Hub) — a long-context instruction-following dataset containing 12,000 samples with context lengths up to 32K tokens. For proxy experiments, we use 200 samples to reduce compute while preserving the gradient-signal analysis objective.

**Evaluation Data (H-M1):** Five synthetic multi-sentence samples generated to exercise long-range dependency patterns across GPT-2's context window. These are sufficient for attention pattern comparison (the H-M1 gate is statistical, not accuracy-based) but inadequate for LongBench task performance evaluation (see Limitation L3).

## 4.3 Baselines

**Sequential Baseline:** Standard LoRA fine-tuning on LongAlpaca-12k without eviction masks during training. At evaluation, H2O eviction is applied at the same budget ratio ρ as the eviction-aware adapter. This is the primary comparison: same architecture, same training data, same inference-time eviction policy — the only difference is whether eviction masks are present during training.

**Full-Cache Baseline (H-M3 only):** Standard LoRA fine-tuning evaluated with full KV cache (ρ=1.0). This establishes the "no eviction" ceiling and quantifies the accuracy cost of eviction for both adapter types.

We include only the sequential baseline for H-E1 and H-M1 because the mechanistic questions (weight divergence and attention pattern divergence) require only the eviction-aware vs. sequential comparison.

## 4.4 Evaluation Metrics

**H-E1 (Weight Divergence):**
- *Cosine similarity* between corresponding LoRA adapter weight matrices (layer-wise). Computed as cos(vec(W_eviction), vec(W_sequential)) for each LoRA layer's merged weight update.
- **Gate criterion:** At least one layer with cosine similarity < 0.95. A near-1.0 similarity would indicate the eviction mask has no effect on gradient-driven weight specialization.

**H-M1 (Attention Pattern Divergence):**
- *Attention entropy* per layer: H_l = -Σ_i α_{li} log α_{li}, where α_{li} is the attention distribution at layer l averaged over heads and positions.
- *Heavy-hitter concentration* per layer: fraction of attention weight on the top-20% of tokens by attention score.
- Both metrics computed for eviction-aware and sequential adapters on the same 5 evaluation samples with H2O eviction active.
- Statistical test: paired t-test across the 5 samples per layer for each metric. **Gate criterion:** ≥50% of transformer layers (≥6/12) show p < 0.05.

**H-M2 (Dose-Response):**
- Per-category LongBench accuracy gap: Δ_category(ρ) = accuracy_eviction-aware(ρ) − accuracy_sequential(ρ), evaluated at ρ ∈ {0.25, 0.50, 0.75}.
- Spearman rank correlation ρ_s between KV budget ratio ρ and mean accuracy gap across categories. **Gate criterion:** ρ_s < −0.8 (monotonically increasing gap as budget tightens).

## 4.5 Implementation Details

All experiments use HuggingFace `transformers` (≥4.36) and `peft` libraries. H2O mask injection is implemented as a registered forward hook on the attention module, active only during training. A critical implementation detail: `attn_implementation='eager'` must be set for all models when using H2O wrappers, as H2O's cumulative-score indexing is incompatible with PyTorch SDPA kernels for certain model-sequence combinations (see Section 6.3). This introduces a ~15–30% inference overhead compared to SDPA but does not affect training.

Experiments were run on a single GPU (mechanism validation); full-scale H-M3 evaluation is estimated to require ~16 GPU-hours training + ~8 GPU-hours evaluation on A100 hardware.
