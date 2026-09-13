# Phase 4 Failure Record: H-E1 Content-Token Uncertainty

**Hypothesis ID:** H-E1 (EXISTENCE)
**Gate Type:** MUST_WORK
**Date:** 2026-07-09
**Phase:** Phase 4 (PoC Implementation & Validation)
**Outcome:** GATE FAILED

---

## Hypothesis Statement

Under RAG-based text generation with open LLMs (LLaMA-3, Mistral-7B), if we extract token-level log-probabilities and apply spaCy dependency parsing to identify content tokens (entities, numerics, relational heads), then we can compute claim-level content-token uncertainty measures with relational head sensitivity (Cohen's d ≥ 0.3) while entity tokens remain stable (d < 0.2), because transformer attention integrates retrieval context producing token-level probability distributions causally conditioned on retrieval quality.

---

## Gate Criteria & Results

**MUST_WORK Gate Requirements:**
1. Code runs without error ✓
2. d(relational) ≥ 0.3 ❌
3. d(entity) < 0.2 ✓
4. Directional consistency ≥ 70% ❌

**Measured Results:**

| Model | d(relational) | d(entity) | Directional | Status |
|-------|---------------|-----------|-------------|--------|
| LLaMA-3-8B | 0.093 [-0.105, 0.233] | 0.056 [-0.213, 0.221] | 42.0% | FAIL |
| Mistral-7B | -0.129 [-0.312, 0.076] | 0.080 [-0.136, 0.344] | 43.0% | FAIL |

**Cross-Model Agreement:**
- Pearson r = -0.112 (p = 0.268) — weak negative correlation
- Directional agreement = 57% — barely better than random

---

## Root Causes

### 1. Weak Effect Size (Primary)
The observed effect size for relational heads (d ≈ 0.09) is 3× smaller than the target threshold (d ≥ 0.3). This is not a measurement error — the 95% confidence intervals are tight and cross zero, indicating the effect is indistinguishable from noise.

### 2. Low Directional Consistency
Only 42-43% of minimal pairs showed the predicted direction (gold > adversarial). This is worse than random chance would predict (50%).

### 3. Negative Cross-Model Correlation
LLaMA-3 and Mistral-7B show weakly negative correlation (r = -0.11), meaning they disagree more than they agree.

### 4. Minimal Pair Design May Be Too Subtle
Entity frequency matching produced valid swaps (e.g., "David M." → "Childhood"), but LLMs may not be sensitive enough to detect these subtle context violations.

---

## What Worked

1. ✓ Infrastructure: Token logprob extraction, spaCy parsing, statistical pipeline all functional
2. ✓ Reproducibility: Fixed seed, greedy decoding, deterministic results
3. ✓ Data Quality: 100 minimal pairs constructed successfully with valid entity swaps
4. ✓ Code Quality: Clean implementation, no errors, complete execution
5. ✓ Entity Stability: d(entity) < 0.2 for both models — entities ARE stable as predicted

---

## What Didn't Work

1. ❌ Core Mechanism: Relational heads do NOT show retrieval-conditioned sensitivity at meaningful levels
2. ❌ Directional Consistency: Effect is random, not systematic
3. ❌ Cross-Model Generalization: Models disagree on which tokens are sensitive
4. ❌ Effect Magnitude: 3× below minimum viable threshold

---

## Lessons Learned

**Technical:** Token-level signals are noisy; Content token identification works; Models differ in fine-grained behavior
**Methodological:** Small effect sizes require large samples; PoC gates must test existence not magnitude; Cross-model validation is essential
**Domain:** Relational token uncertainty may not exist as a retrieval-conditioned phenomenon at token level; Sentence-level aggregation may be required; Stronger manipulations needed

---

## Routing Decision

**Route to:** Phase 0 (New Research Question)

**Rationale:** MUST_WORK gate failure indicates fundamental mechanism flaw, not implementation issue. Effect size too small to be meaningful. Cross-model disagreement suggests no generalizable phenomenon exists.

---

## Alternative Directions

1. **Claim-Level Aggregation:** Sentence-level entropy instead of token-level
2. **Stronger Manipulations:** Contradiction or temporal impossibility instead of entity swaps
3. **Different Token Types:** Temporal, numeric, causal tokens instead of entities/relational
4. **Abandon Token-Level:** Shift to dual-NLI ensemble (proven approach)

---

**Memory Type:** PHASE4_FAIL
**Created:** 2026-07-09 16:37:00 UTC
**Next Action:** Route to Phase 0 for new research question
