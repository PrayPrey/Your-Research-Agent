# Reflection Report: H-E1

**Date:** 2026-08-31
**Gate Result:** FAIL
**Reflection Outcome:** ROUTED_TO_PHASE_0
**Reflection Type:** MUST_WORK gate failure analysis

---

## Gate Evaluation Summary

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| SMC-NLI AUROC | 0.4933 | > 0.60 | ❌ FAIL |
| SMC-Embed AUROC | 0.4859 | > 0.60 (fallback) | ❌ FAIL |
| SMC-NLI std | 0.3388 | > 0.05 | ✅ PASS |
| Mechanism verification | PASSED | — | ✅ PASS |

Both primary (SMC-NLI) and fallback (SMC-Embed) metrics failed. AUROC ≈ 0.49 indicates random or slightly inverted discrimination.

---

## Root Cause Analysis

### Finding 1: Dataset-Generation Mismatch (Primary)

HaluEval QA provides `right_answer` and `hallucinated_answer` fields, but H-E1 **discards** these and generates fresh Llama-3-8B answers. The hypothesis assumed:
- Correct questions → Llama samples concentrate (high SMC-NLI)
- Hallucinated questions → Llama samples spread (low SMC-NLI)

**Reality:** Both correct and hallucinated HaluEval questions produce consistent Llama-3-8B answers (~0.62–0.63 mean SMC-NLI). The hallucinated questions in HaluEval are factually adjacent to real facts — Llama-3-8B may generate the same plausible-but-wrong answer consistently. High consistency ≠ correctness when the model has a consistent wrong belief.

### Finding 2: Mechanism Assumption Invalid for This Task

SMC-NLI's core assumption is "factually correct questions produce more consistent LLM samples than incorrect ones." This holds on open-ended generation tasks (WikiBio), where hallucinated content contains random fabrications. In factual short-answer QA, Llama may have a stable but incorrect belief → consistent wrong answers = high SMC-NLI despite being hallucinated.

Mean SMC-NLI difference: correct=0.6236, hallucinated=0.6299 (gap=0.006, noise-level).

### Finding 3: SMC-Embed Confirms the Pattern

SMC-Embed AUROC = 0.486 corroborates that semantic consistency (not just NLI agreement) also fails to discriminate. This rules out NLI-specific OOD failure — the fundamental mechanism does not apply.

---

## Lessons Learned

1. SMC-NLI (and SMC-Embed) work on open-ended generation tasks where hallucinated content is random. They fail on factual QA where the model may consistently confabulate the same wrong answer.
2. HaluEval QA's hallucinated answers are crafted plausible alternatives — Llama-3-8B may "know" the same wrong answer consistently, making high SMC-NLI compatible with hallucination.
3. The verification hypothesis (existence of SMC-NLI signal) must be tested on tasks with stochastic hallucination, not deterministic confabulation.

---

## Routing Decision

**Gate type:** MUST_WORK  
**Gate result:** FAIL (both metrics below threshold)  
**Reflection outcome:** ROUTED_TO_PHASE_0  
**Reason:** Fundamental mechanism assumption invalid for short factual QA. Both metrics show AUROC ≈ 0.49 (near-random). No meaningful finding — cannot modify to recover.

**Cascade effects:**
- H-M1, H-M2, H-M3 all depend on H-E1 → CASCADE_FAILED

**Recommended Phase 0 direction:**
- Reframe hypothesis for open-ended generation tasks (WikiBio-style)
- OR: Use SMC-NLI on Llama's own generated answers (not HaluEval labels) for different downstream tasks
- OR: Test semantic entropy (white-box) vs SMC (black-box) tradeoff with logit access

---

## Status Update

- H-E1: FAILED
- H-M1: CASCADE_FAILED (prerequisite failed)
- H-M2: CASCADE_FAILED (prerequisite failed)
- H-M3: CASCADE_FAILED (prerequisite failed)
