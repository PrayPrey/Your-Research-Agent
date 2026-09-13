# Hypothesis Context: H-E1

**Generated:** 2026-08-02 (JIT from 02b_verification_plan.md)
**Source:** Phase 2B Verification Plan

---

## Hypothesis Information

- **ID:** H-E1
- **Type:** EXISTENCE
- **Status:** IN_PROGRESS
- **Gate:** MUST_WORK

**Statement:**
Under Llama-3.1-8B (temp=0.7, N=5) on TriviaQA dev (2500 prompts), if SE_N5 (bidirectional DeBERTa-MNLI clustering) and min_logprob (greedy decode) are computed, then Pearson |r|(SE, min_logprob) < 0.7 and partial R²(SE) ≥ 0.02 in conditional LR [logit(h=1) ~ min_logprob + SE + L + SE×min_logprob], because SE marginalizes over semantic class masses while min_logprob captures minimum token-level prediction confidence — algebraically distinct measures.

**Rationale:** Foundational test — if SE and min_logprob are not empirically independent, the ensemble hypothesis collapses. H-E1 is scoped to a diagnostic (pre-experiment correlation check + conditional LR), not a full ensemble evaluation. The h-e1 infrastructure (generate.py, compute_signals.py) is directly reusable.

---

## Experimental Setup (from Phase 2A via Phase 2B)

### Dataset
- **Primary:** TriviaQA dev — `mandarjoshi/trivia_qa` (HuggingFace), `rc.nocontext` split, validation set (11,313 prompts; use 2500)
- **Type:** standard
- **Source:** HuggingFace datasets
- **Path:** auto (HuggingFace download)
- **Hypothesis Fit:** TriviaQA dev was benchmark for h-m1 (AUROC=0.825 baseline) and prior h-e1 snapshot (SE validated non-degenerate). Directly comparable. Short-answer QA tests both SE diversity and min_logprob discriminability.

### Model
- **Name:** Llama-3.1-8B (meta-llama/Llama-3.1-8B-Instruct)
- **Type:** Open-weight 7-8B decoder LLM
- **Source:** HuggingFace
- **Hypothesis Fit:** Validated in prior h-m1/h-e1 runs. SE_variance=0.1522, fraction_degenerate=0.000 at temp=0.7 N=5. Cross-model judge: Qwen-2.5-7B or GPT-4o-mini.

---

## Baseline & Comparison Targets

| Method | Performance | Notes |
|--------|-------------|-------|
| min_logprob standalone | AUROC ~0.825 | From h-m1 (300/2500 samples) |
| SE standalone (Kuhn 2023) | AUROC 0.83 | OPT-30B, different protocol |

---

## Dependencies

- **Prerequisites:** None (H-E1 is the root hypothesis)
- **Gate:** MUST_WORK — |r| < 0.7 AND partial R²(SE) ≥ 0.02

---

## Success Criteria

- **Primary:** Pearson |r|(SE, min_logprob) < 0.7 AND partial R²(SE) ≥ 0.02 (LRT p < 0.05)
- **Secondary:** ρ(SE, LM-judge) < 0.4 (circularity check)

## Failure Response

- IF |r| > 0.85: ABANDON — SE is near-monotone reparameterization
- IF 0.7 < |r| < 0.85 OR partial R² < 0.02: EXPLORE — recheck N=10 ablation
