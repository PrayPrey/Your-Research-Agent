# Phase 2B Context: H-M2

**Generated:** 2026-05-20 (JIT from 02b_verification_plan.md by Phase 2C step-01)
**Hypothesis ID:** H-M2
**Type:** MECHANISM
**Gate:** MUST_WORK

---

## Hypothesis Statement

Joint end-to-end training of LoRA adapter parameters and Locret retaining head parameters in a single backward pass via task classification loss converges stably (no loss divergence or NaN across 3 seeds) and achieves >= B3 accuracy on LongBench-QA at 50% KV budget, because LoRA A/B matrices and Locret head weights are disjoint parameter sets with independent gradient paths.

---

## Experimental Setup

**Dataset:**
- Name: GLUE training splits + LongBench-QA test sets
- Type: standard
- Source: HuggingFace datasets (`nyu-mll/glue`); THUDM/LongBench
- Path: `glue` (HuggingFace), https://github.com/THUDM/LongBench
- Hypothesis Fit: GLUE provides task CE loss for joint training; LongBench-QA tests KV compression at 50% budget

**Model:**
- Name: LLaMA-3.1-8B (meta-llama/Meta-Llama-3.1-8B)
- Type: Decoder-only transformer LLM with KV cache
- Source: HuggingFace Model Hub
- Hypothesis Fit: Locret and PEFT/LoRA fully supported; tractable for single-GPU fine-tuning

---

## Baselines

- B3: LoRA → sequential Locret fine-tune (primary comparison — hardest baseline)
- Vanilla LoRA (100% KV budget) — reference ceiling

---

## Gate Conditions

- Prerequisites: H-E1 (COMPLETED ✅ — mean ρ=0.3662, misalignment confirmed)
- Gate Type: MUST_WORK
- Gate Logic: Training must converge stably (zero NaN/divergence across 3 seeds) AND achieve >= B3 accuracy on LongBench-QA

---

## Controlled Variables

- Model: LLaMA-3.1-8B
- LoRA: r=16, alpha=32, target_modules=[Q, K, V]
- KV budget ratio: 0.5
- Seeds: 42, 123, 456
- Optimizer: AdamW (LoRA LR=1e-4, Locret LR=5e-4)

---

## Success Criteria

- Primary: Zero NaN/divergence events across all 3 seeds
- Primary: JointLoRA-KV LongBench-QA mean F1 >= B3 LongBench-QA mean F1 at 50% KV budget
- Secondary: Gradient norms for LoRA and Locret groups remain independent (no interference)

---

## Source

Phase 2B verification plan: 02b_verification_plan.md — Section 2.2 (H-M2 specification)
