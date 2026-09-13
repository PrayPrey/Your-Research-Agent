# Phase 4 Failure Record: h-e1 (Run 3)

**Date:** 2026-07-09T23:18:19Z
**Hypothesis:** h-e1
**Run:** 3
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| Δρ_j | -0.0250 | >0.15 (threshold) | -0.1750 (-116.7%) |
| ρ_j (creative) | 0.0103 | expected: 0.75-0.85 | -0.7397 (-87.8%) |
| ρ_j (factual) | 0.0354 | expected: 0.75-0.85 | -0.7646 (-90.1%) |

## Root Cause Analysis

- NLI model (DeBERTa-v3-base) predominantly assigns probability mass to "neutral" class, resulting in extremely low ρ_j values (0.01-0.04 vs expected 0.75-0.85)
- Δρ_j has wrong direction: negative (-0.025) instead of positive (>0.15) - creative text has LOWER ρ_j than factual text
- Sentence-level claim decomposition (NLTK tokenization) may not capture semantic/logical claims correctly for CCP metric computation
- NLI model trained on SNLI/MNLI may not generalize to creative vs factual text comparison tasks
- Autocorrelation patterns violate expected behavior: factual autocorr (0.264) exceeds threshold (<0.2), creative autocorr (0.046) below threshold (>0.4)

## Lessons Learned

1. NLI model calibration is CRITICAL for CCP ρ_j metric computation - verify NLI output distribution (contradiction/entailment/neutral balance) before using metric
2. Sentence tokenization for claim decomposition may be insufficient - need to validate that extracted "claims" are actually semantic claims
3. DeBERTa-v3-base (trained on SNLI/MNLI) may not be appropriate baseline for creative vs factual text - consider domain-specific NLI fine-tuning
4. Gate criteria passed: 1/6 (only Krippendorff α: 0.75 > 0.7) - reliability is high but mechanism fails
5. This is a **methodological failure** (NLI model/claim extraction), NOT a fundamental hypothesis flaw
6. Sample processing was successful (792 factual + 817 creative samples) - no data loading or infrastructure issues

## Feedback for Next Phase

### Suggested Modifications
- Investigate NLI output distribution on sample data to confirm neutral-class dominance
- Test alternative claim decomposition methods (LLM-based vs sentence tokenization)
- Validate NLI model on known entailment/contradiction examples before using for CCP
- Consider fine-tuning NLI model on creative/factual text or using alternative hallucination detection baseline (e.g., SelfCheckGPT)
- Add sanity checks: verify ρ_j on known good/bad examples first before full experiment

### What NOT To Do
- Do NOT abandon the hypothesis - the core idea (CCP degrades on creative text) is NOT disproven
- Do NOT use sentence tokenization without validating it captures semantic claims
- Do NOT use off-the-shelf NLI models without verifying output distribution on target domain

### What Showed Promise
- Dataset loading and processing pipeline works reliably (817 samples per domain)
- Krippendorff's α (0.75) shows measurement reliability is adequate
- Code infrastructure (NLI inference, metrics, visualization) is robust
- Experiment completed successfully without runtime errors

---
*For cross-phase reference*
*Written at: 2026-07-09T23:18:19Z*
