# Hypothesis Context: H-E1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-08-27
**Main Hypothesis:** Prefill-Observation vs. Cumulative-Attention KV Eviction Metric Comparison
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement

Under long-context QA inference using LLaMA-2-7B-chat at 50% KV retention on LongBench 4-task QA subset (NarrativeQA, HotpotQA, 2WikiMQA, MuSiQue), if we apply prefill-observation importance scoring (SnapKV-style, W=16 query tokens) versus cumulative-attention-at-prefill scoring (H2O-style, both applied at prefill timing to eliminate timing confound), then prefill-observation achieves ≥2.0 macro-average F1 higher than cumulative-attention-at-prefill, because query-conditioned observation windows selectively retain answer-relevant KV entries.

### Type

EXISTENCE (PoC)

### Rationale

No prior controlled ablation separates metric type (query-conditioned vs. cumulative) from eviction timing under identical conditions. H-E1 is the foundational gate: if prefill-observation does not outperform at 50% retention, the hypothesis chain is invalidated.

---

## Verification Protocol

### Conceptual Test

Implement both score_fn variants (M1: prefill-observation, M2: cumulative-at-prefill) in unified HuggingFace codebase using past_key_values API. Run LLaMA-2-7B-chat-hf on 100 examples each from NarrativeQA, HotpotQA, 2WikiMQA, MuSiQue at 50% KV retention. Apply M1 (mean attention from last W=16 query tokens at prefill end) and M2 (cumulative sum of attention weights at prefill end) as eviction criterion. Compute per-task F1 and macro-average. Bootstrap 95% CI (1000 resamples). Compare macro-average F1 difference.

### Success Criteria

- prefixobs_F1_QA − cumulative_at_prefill_F1_QA ≥ 2.0 F1 points
- 95% bootstrap CI lower bound > 0 (non-overlapping with zero)

### Variables

- **Independent Variable:** Importance metric type (M1: prefill-observation vs. M2: cumulative-attention-at-prefill)
- **Dependent Variable:** LongBench macro-average F1 on 4-task QA subset (100 examples per task = 400 total)
- **Controlled Variables:** Model (LLaMA-2-7B-chat-hf), KV retention (50%), hardware (A100 40GB FP16), seed (42), unified codebase, eviction timing (both at prefill end)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset

- **Name:** LongBench v1
- **Type:** standard
- **Source:** HuggingFace Hub — THUDM/LongBench
- **Path:** auto (HuggingFace: THUDM/LongBench)
- **Hypothesis Fit:** LongBench contains the exact QA tasks (NarrativeQA, HotpotQA, 2WikiMQA, MuSiQue) and summarization contrast tasks (GovReport, QMSum) needed to test the task-conditional prediction. Standard automated metrics (F1, ROUGE-L) — no human evaluation required.

### Selected Model

- **Name:** LLaMA-2-7B-chat-hf
- **Type:** decoder-only, instruction-tuned
- **Source:** HuggingFace Hub — meta-llama/Llama-2-7b-chat-hf
- **Hypothesis Fit:** Instruction-tuned variant avoids base-model KV collapse issues. 7B fits on single A100 40GB at FP16. SnapKV reports stable performance at 40-60% KV retention on this model.

---

## Baseline & Comparison Targets

### Baseline Methods

| Method | Timing | Score Function |
|--------|--------|----------------|
| M1: Prefill-Observation (SnapKV-style) | prefill | mean attention from last W=16 query tokens at prefill end |
| M2: Cumulative-Attention-at-Prefill (H2O-at-prefill) | prefill | cumulative sum of attention weights at prefill end |
| M6: StreamingLLM (static baseline) | N/A | attention sinks (first 4 tokens) + sliding window |

### Baseline Performance

| Method | Performance | Dataset |
|--------|-------------|---------|
| H2O (cumulative, decode-timed) | ~1 PPL degradation at 20% KV budget | WikiText-2, MT-Bench |
| SnapKV (prefill observation) | ~1-2% F1 degradation at 40% KV retention | LongBench, RULER |
| StreamingLLM (static) | Stable PPL; poor on extractive QA | WikiText-2, PassKey |

### Gap Analysis

Controlled M1 vs. M2 comparison at matched prefill timing has not been reported. SnapKV vs. H2O comparisons conflate metric type with eviction timing — this experiment isolates metric type as the only IV.

---

## Dependencies and Gate Conditions

### Prerequisites

None (H-E1 is the root hypothesis)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow

**Consequence if Fails:** Hypothesis invalidated — query-conditioning mechanism not supported at this scale; trigger reflection and route to Phase 2A-Dialogue for redesign

**Phase Assignment:** Phase 1 (root gate)

**Estimated Duration:** 3-4 days

---

## Dependency Context

### Relationship to Other Hypotheses

H-E1 is the root MUST_WORK gate. H-M1 and H-M2 both depend on H-E1 passing (they reuse M1 and M2 runs from H-E1). H-C1 depends on H-M1 and H-M2. All downstream hypotheses are blocked if H-E1 fails.

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation
3. Dependency information for controlled experiments
4. Success criteria for evaluation design

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap
2. Search for implementation patterns (Archon, Exa MCP)
3. Design concrete experiment specification (Level 1.5)
4. Output: h-e1/02c_experiment_brief.md

---

*Optimized for single-hypothesis experiment design*
