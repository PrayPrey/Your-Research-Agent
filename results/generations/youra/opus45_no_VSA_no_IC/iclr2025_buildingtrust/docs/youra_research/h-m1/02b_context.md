# Phase 2B Context: H-M1

**Date:** 2026-08-24
**Hypothesis ID:** H-M1

---

## Hypothesis Information

**Statement:** TruthfulQA specifically measures resistance to popular misconceptions (imitative falsehoods), a capability distinct from general knowledge retrieval measured by MMLU.

**Type:** MECHANISM
**Rationale:** If TruthfulQA correlates perfectly with MMLU, it measures general knowledge, not misconception resistance. The benchmark was designed to elicit imitative falsehoods that appear correct but are false.

**Success Criteria:**
- Primary: r(TruthfulQA, MMLU) < r(MMLU subtasks internal)
- Secondary: Models exist with high MMLU but low TruthfulQA (divergent profiles)

---

## Gate Condition

**Type:** MUST_WORK
**If Fail:** TruthfulQA may not measure unique construct

---

## Variables

- **IV:** Benchmark (TruthfulQA vs MMLU)
- **DV:** Correlation coefficient between TruthfulQA and MMLU
- **CV:** Model population diversity

---

## Verification Protocol

1. Compute r(TruthfulQA, MMLU) across model population
2. Identify models with divergent profiles (high MMLU, low TruthfulQA)
3. Analyze error patterns on TruthfulQA for these models
4. Confirm misconception-type errors dominate

---

## Prerequisites

**Depends on:** H-E1 (VALIDATED - PASS)
**H-E1 Key Findings:**
- N=50 models analyzed (7 architectures, 4 scales, 4 variants)
- Cross-benchmark correlations: TruthfulQA-HaluEval r=0.58, TruthfulQA-FactScore r=0.42, HaluEval-FactScore r=0.44
- Baseline correlation (MMLU-Physics vs HaluEval): r=0.10
- All correlations satisfy gate condition: 0.10 < r < 0.70
- All p-values significant after Bonferroni correction (p < 0.0167)

---

## Experimental Setup

**Dataset:**
- Source: TruthfulQA (sylinrl/TruthfulQA), MMLU (cais/mmlu)
- Type: standard (established public benchmarks)
- Purpose: Correlation analysis between misconception-testing and general knowledge

**Model:**
- Source: Open LLM Leaderboard model population
- Type: Decoder-only transformers
- Requirement: Same N≥50 models from H-E1 for consistency

---

## Previous Results to Build On

From H-E1:
- Model population already assembled and scored
- TruthfulQA scores already computed
- Baseline reference established (r=0.10)
- Correlation analysis pipeline ready
