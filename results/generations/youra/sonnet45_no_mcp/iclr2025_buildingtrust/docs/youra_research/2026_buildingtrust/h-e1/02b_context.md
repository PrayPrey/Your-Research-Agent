# H-E1 Context: Published Benchmark Error Data Existence

**Generated:** 2026-04-14 (JIT from 02b_verification_plan.md)
**Source:** Phase 2B Section 2.2, H-E1 Specification

---

## Hypothesis Information

**ID:** H-E1
**Type:** Existence
**Statement:** Under the scope of major LLM benchmarks (TruthfulQA, MMLU), if we examine published technical reports from multiple model families (GPT, Claude, Llama), then we can extract category-level error rates for ≥3 model families across ≥2 timepoints (baseline vs current), because major labs publish detailed benchmark results as high-stakes performance claims.

**Rationale:** Foundation hypothesis validating data availability. Without published category-level error data, the entire weak supervision approach is infeasible. This tests the BUILD_ON claim that published results contain sufficient granularity.

---

## Experimental Setup (from Phase 2A via Phase 2B)

### Dataset

**Name:** TruthfulQA + MMLU
**Type:** standard
**Source:** 
- TruthfulQA: github.com/sylinrl/TruthfulQA (817 questions)
- MMLU: github.com/hendrycks/test (subject-based evaluation)

**Hypothesis Fit:** Rich metadata, published results available from major labs, enables cross-benchmark validation testing

### Model

**Name:** Published Results Analysis (GPT/Claude/Llama)
**Type:** Published evaluations (no API calls required)
**Source:** Technical reports from OpenAI, Anthropic, Meta

**Model Families:**
- GPT: GPT-3.5 (baseline) → GPT-4 (current)
- Claude: Claude-2 (baseline) → Claude-3 (current)  
- Llama: Llama-2 (baseline) → Llama-3 (current)

**Hypothesis Fit:** Eliminates API dependency (avoiding h-e1 prior failure), enables temporal comparison, tests across independent model families

---

## Variables

**Independent Variables:**
- Model families: GPT, Claude, Llama (3 families)
- Timepoints: Baseline vs Current (2 timepoints per family)

**Dependent Variable:**
- Availability of category-level error rates (binary: available/not available)

**Controlled Variables:**
- Benchmark selection: TruthfulQA and MMLU only
- Source type: Technical reports only (no informal blogs/tweets)

---

## Success Criteria (PoC: Direction-based)

**Primary:** ≥3 model families with category-level data for both timepoints
**Secondary:** Data granularity sufficient (≥10 categories per benchmark)

---

## Gate Condition

**Type:** MUST_WORK
**Condition:** ≥3 model families with category-level data for both timepoints
**If Failed:** ABORT - entire approach infeasible without published data

---

## Dependencies

**Prerequisites:** None (foundation hypothesis)

---

## Baseline & Comparison Targets

**Baseline Methods (for Phase 5):**
- GPT-4 Technical Report aggregate scores (~60% TruthfulQA)
- Manual error analysis (qualitative, small samples)
- Random category assignment
- Category mean baseline

---

*JIT-Generated from 02b_verification_plan.md Section 2.2*
