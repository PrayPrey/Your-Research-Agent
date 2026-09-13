# Phase 2B Context: h-e2
# H-EntropySWA-v1 — Zero-Shot SWA Conversion Feasibility
# Generated: 2026-08-22 (JIT from 02b_verification_plan.md)

---

## Hypothesis Info

- **ID:** h-e2
- **Type:** EXISTENCE (PoC)
- **Gate:** MUST_WORK
- **Statement:** Entropy-guided k=4 SWA(w=512) conversion of Llama-2-7B zero-shot maintains WikiText-103 perplexity within 2.0 points of the full-attention baseline (Prediction P1).
- **Success Criterion:** Δperplexity(entropy-k4 vs baseline) ≤ 2.0 on WikiText-103 test set
- **Falsification:** Δperplexity > 2.0 → route to Phase 0; Δperplexity > 5.0 → zero-shot selective SWA infeasible

## Experimental Setup

**Dataset:**
- Name: WikiText-103
- Type: standard (real dataset)
- Source: HuggingFace Datasets ("wikitext", "wikitext-103-v1")
- Split: test split (full, ~245K tokens) for evaluation; validation split first 100 sequences for calibration (reused from h-e1)
- Cache path: auto (HuggingFace cache)
- Hypothesis fit: WikiText-103 test set is the standard perplexity benchmark for LLM efficiency papers; calibration set inherited from h-e1 ensures controlled comparison

**Model:**
- Name: Llama-2-7B
- Pretrained: meta-llama/Llama-2-7b-hf
- Type: causal decoder transformer, 32 attention layers, standard MHA (not GQA)
- Precision: bfloat16
- attn_implementation: eager (required for custom mask injection)
- Cache path: HuggingFace model cache
- Hypothesis fit: Same model as h-e1; 32 layers with standard causal attention supports monkey-patch SWA mask injection

## Baseline & Comparison Targets

- **Baseline:** Llama-2-7B full attention (no modification), expected PPL ~5.47 (Touvron et al., 2023)
- **Proposed:** Llama-2-7B with k=4 highest-entropy layers replaced by SWA(w=512) via monkey-patch
- **Key source:** Entropy layer ranking (top-4 indices by mean per-layer entropy) inherited from h-e1 output
- **No fine-tuning:** Zero-shot evaluation only

## Dependencies & Gate

- Prerequisites: h-e1 (VALIDATED — Gini mean=0.6829, Spearman ρ confirmed stable)
- Estimated runtime: ~30 min on 1× H100
- Failure routes: Δperplexity > 2.0 → Phase 0 (both positive and negative results publishable)
- h-e2 must pass before h-m1, h-m2, h-c1 can run
