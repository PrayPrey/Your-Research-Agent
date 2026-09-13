# Phase 2B Context: h-e1

**Hypothesis ID:** h-e1
**Type:** EXISTENCE
**Status:** IN_PROGRESS (Phase 2C completed)
**Generated:** 2026-08-24 (JIT from 02b_verification_plan.md)

---

## Hypothesis Statement

Under foundation model training (pre-training → fine-tuning → RLHF), if low-level quality filters (deduplication, perplexity-based outlier removal) are applied across stages, then they will transfer robustly with ≤1% performance delta compared to stage-tuned thresholds, because these operations address universal data hygiene properties independent of stage objectives.

---

## Experimental Setup

*From Phase 2A Dialogue (via Phase 2B verification plan)*

### Dataset

**Selected:** Alpaca-52k (instruction fine-tuning dataset)
- **Type:** standard (publicly available)
- **Source:** Stanford Alpaca (tatsu-lab/stanford_alpaca)
- **Path:** HuggingFace `tatsu-lab/alpaca`
- **Hypothesis Fit:** Tests transfer of pre-training curation filters (dedup, perplexity) to instruction fine-tuning stage

### Model

**Selected:** LLaMA-2-7B (Causal Language Model)
- **Type:** standard (publicly available pre-trained model)
- **Source:** Meta AI (HuggingFace checkpoint `meta-llama/Llama-2-7b-hf`)
- **Hypothesis Fit:** Mid-size model balances feasibility with meaningful performance measurement

---

## Variables

**Independent Variable (IV):** Curation Strategy Source
- Levels: Transferred (C4 thresholds), Stage-Tuned (Alpaca-optimized), Baseline (no curation)

**Dependent Variable (DV):** Downstream Task Performance
- Metrics: MMLU accuracy, HellaSwag accuracy, validation perplexity

**Controlled Variables:**
- Model architecture: LLaMA-2-7B (same across all variants)
- Training hyperparameters: AdamW, lr=2e-5, 3 epochs
- Pre-training checkpoint: meta-llama/Llama-2-7b-hf

---

## Success Criteria (PoC - Direction-based)

**Primary:** `|acc_transferred - acc_stage_tuned| ≤ 1%` (validates transfer robustness)

**Secondary:** `acc_transferred > acc_baseline + 2%` AND `acc_stage_tuned > acc_baseline + 2%` (validates curation benefit)

---

## Gate Condition

**Type:** MUST_WORK
**Pass Condition:** Transfer-stable category exists with ≤1% performance delta
**Fail Action:** PIVOT to partial-stability model

---

## Prerequisites

**None** - This is the foundation hypothesis (h-e1) in the verification chain.

---

## Dependencies

**Blocked Hypotheses (depend on h-e1):**
- h-m1: Low-Level Operations Address Universal Data Hygiene
- h-m2: Transfer Stability Correlates with Objective-Independence
- h-m3: Transferred Low-Level Thresholds Match Stage-Tuned Performance

**If h-e1 MUST_WORK gate fails:** All dependent hypotheses blocked, PIVOT required.

---

## Verification Protocol Summary

1. Extract pre-training curation thresholds (C4: dedup 0.8, perplexity 100)
2. Apply three curation variants to Alpaca-52k:
   - Baseline: No curation
   - Transferred: C4 thresholds
   - Stage-Tuned: Optimized on Alpaca validation perplexity
3. Fine-tune LLaMA-2-7B on each variant (identical hyperparameters)
4. Evaluate on MMLU, HellaSwag benchmarks
5. Measure performance delta: `|transferred - stage_tuned|`

---

## Phase 2B Planning Notes

- **Scope:** Single-stage transfer test (pre-training → fine-tuning)
- **Simplification:** PoC does NOT test full pipeline (pre-training → fine-tuning → RLHF)
- **Risk:** Distribution shift between C4 and Alpaca may affect filter transfer
- **Mitigation:** Use standard datasets with established curation pipelines

---

**Source:** Extracted from `02b_verification_plan.md` Section 2.2 (Hypothesis h-e1)
**Next Phase:** Phase 2C (Experiment Design) → Phase 3 (Implementation Planning)
