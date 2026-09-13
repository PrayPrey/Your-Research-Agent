# H-E1 Validation Report

**Hypothesis:** H-E1 (EXISTENCE)
**Date:** 2026-08-19
**Status:** PASS

---

## Executive Summary

H-E1 validates that token entropy and semantic consistency metrics CAN be computed for LLM-generated responses. This existence test confirms the foundational capability required for subsequent hypotheses.

**Gate Result:** PASS - All criteria met.

---

## Experiment Configuration

| Parameter | Value |
|-----------|-------|
| Model | meta-llama/Llama-2-7b-chat-hf |
| Dataset | TriviaQA rc.nocontext validation |
| Questions Processed | 20 (PoC subset) |
| Samples per Question | 10 |
| Temperature | 0.7 |
| Top-p | 0.9 |
| Max New Tokens | 128 |

---

## Results

### Success Rate

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Success Rate | ≥99% | 100.0% | ✓ PASS |
| Entropy Variance | >0 | 0.00156 | ✓ PASS |
| Consistency Variance | >0 | 0.00559 | ✓ PASS |

### Entropy Statistics

| Statistic | Value |
|-----------|-------|
| Mean | 0.1224 |
| Std Dev | 0.0395 |
| Min | 0.0256 |
| Max | 0.1824 |

### Consistency Statistics

| Statistic | Value |
|-----------|-------|
| Mean | 0.8693 |
| Std Dev | 0.0748 |
| Min | 0.7210 |
| Max | 0.9858 |

---

## Gate Decision

**MUST_WORK Gate: PASS**

All success criteria satisfied:
1. ✓ Code executes without errors (100% success rate)
2. ✓ Entropy values computed with meaningful variance (std=0.0395)
3. ✓ Consistency values computed with meaningful variance (std=0.0748)
4. ✓ Both metrics show reasonable ranges for QA task

**Next Step:** Proceed to H-M1 (entropy correlation with uncertainty)

---

## Code Validation

Validator agent confirmed:
- All 8 required modules present
- Entropy formula correctly implements Shannon entropy
- Consistency uses SentenceTransformer + pairwise cosine similarity
- Tests pass for entropy and consistency modules

---

## Appendix: Sample Results

| Question ID | Entropy | Consistency |
|-------------|---------|-------------|
| sfq_178 | 0.0928 | 0.7210 |
| sfq_11822 | 0.0726 | 0.9269 |
| sfq_17752 | 0.1322 | 0.8248 |
| qb_2689 | 0.1510 | 0.7553 |
| qb_7436 | 0.0256 | 0.9858 |
