# Validation Report: H-M1

**Generated:** 2026-04-30T13:57:56Z
**Hypothesis:** Capability-Independent Calibration-Hallucination Mechanistic Link
**Gate Type:** MUST_WORK
**Overall Gate Result:** **PASS ✓**

---

## Primary Gate Result

| Criterion | Threshold | Observed | CI (BCa 95%) | Pass/Fail |
|-----------|-----------|----------|--------------|-----------|
| partial ρ(ECE, TruthfulQA% \| MMLU) | ≥ 0.40 | -0.758 | [-0.903, -0.494] | PASS ✓ |

---

## All Criteria

| Criterion | Threshold | Observed | Pass/Fail |
|-----------|-----------|----------|-----------|
| Primary gate: \|partial ρ(ECE, TruthfulQA%\|MMLU)\| ≥ 0.40 AND CI excludes zero | ≥ 0.40 | -0.758 | PASS ✓ |
| Construct validity: ρ(ECE, Brier) | ≥ 0.30 | 0.775 | PASS ✓ |
| Confound magnitude: survival fraction (partial/raw ρ) | ≥ 0.50 | 0.943 | PASS ✓ |
| Discriminant validity: \|partial ρ(ECE, HumanEval\|MMLU)\| | < 0.20 | -0.082 | PASS ✓ |
| Decoding invariance: \|partial ρ_T07\| | ≥ 0.30 | N/A | SKIP |

---

## Key Findings

- **Primary mechanism confirmed:** partial ρ(ECE, TruthfulQA% | MMLU) = -0.758 (BCa 95% CI: [-0.903, -0.494])
- **Calibration construct valid:** ρ(ECE, Brier) = 0.775 (threshold ≥ 0.30)
- **Confound magnitude:** MMLU explains 0.1% of raw correlation (survival fraction = 0.943)
- **Discriminant validity:** partial ρ(ECE, HumanEval | MMLU) = -0.082 (threshold < 0.20)
- **Decoding invariance:** Skipped (T=0.7 data unavailable)

---

## MUST_WORK Gate Interpretation

The calibration-hallucination mechanistic link is **capability-independent**: partial ρ(ECE, TruthfulQA%|MMLU) survives MMLU control and the BCa 95% CI excludes zero. H-M1 MUST_WORK gate: **PASS**. Proceed to Phase 5.
