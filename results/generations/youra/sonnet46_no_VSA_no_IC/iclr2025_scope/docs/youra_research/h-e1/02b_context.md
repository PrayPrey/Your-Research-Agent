# Phase 2B Context: h-e1
# H-EntropySWA-v1 — Entropy Criterion Stability
# Generated: 2026-08-22 (JIT from 02b_verification_plan.md)

---

## Hypothesis Info

- **ID:** h-e1
- **Type:** EXISTENCE
- **Gate:** MUST_WORK
- **Statement:** Per-layer attention entropy in Llama-2-7B produces a stable layer ranking (Spearman ρ ≥ 0.8) across 3 independent 100-sequence calibration subsets from WikiText-103 validation split.
- **Success Criterion:** Spearman ρ ≥ 0.8 for top-8 layer rankings across 3 non-overlapping 100-seq calibration subsets
- **Falsification:** ρ < 0.7 → entropy ranking is noise; criterion invalid

## Experimental Setup

**Dataset:**
- Name: WikiText-103
- Type: standard
- Source: HuggingFace datasets ("wikitext", "wikitext-103-raw-v1")
- Split: validation split for calibration (3 × 100-seq non-overlapping subsets)
- Cache path: auto (HuggingFace cache)
- Hypothesis fit: WikiText-103 is the standard calibration dataset for LLM efficiency papers (GPTQ, AWQ); validation split avoids test contamination; 300 sequences total covers full subset requirement

**Model:**
- Name: Llama-2-7B
- Pretrained: meta-llama/Llama-2-7b-hf
- Type: causal decoder transformer, 32 attention layers
- Cache path: HuggingFace model cache
- Hypothesis fit: 32 layers provides sufficient granularity for entropy-based layer ranking; same model as SWAA [2025] and SWARR [Liu et al., 2026] baselines

## Baseline & Comparison Targets

- No SWA conversion in h-e1 (entropy scoring only)
- Comparison: cross-subset Spearman ρ of top-8 ranked layers across 3 seeds
- Mitigation if fails: increase calibration to 300 sequences per subset

## Dependencies & Gate

- Prerequisites: none
- h-e1 must pass before h-e2 can run
- Estimated runtime: ~15 min on 1× H100 (CPU-feasible for entropy scoring)
