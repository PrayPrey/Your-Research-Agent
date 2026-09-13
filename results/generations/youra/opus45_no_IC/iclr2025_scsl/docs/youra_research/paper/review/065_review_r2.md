# Adversarial Review Round 2
# Date: 2026-08-12

## Summary

Numerical verification round. All metrics cross-checked against Phase 4 validation files.

**Verdict: PASS - All numbers verified**

---

## Numerical Verification

### H-E1 Metrics (from h-e1/04_validation.md)

| Metric | Paper | Source | Status |
|--------|-------|--------|--------|
| Mann-Whitney p | 7.36e-15 | 7.36e-15 | EXACT |
| Mann-Whitney U | 705,391 | 705,391 | EXACT |
| Precision | 0.329 | 0.329 | EXACT |
| Recall | 0.329 | 0.329 | EXACT |
| Minority mean loss | 0.158 | 0.158 | EXACT |
| Majority mean loss | 0.019 | 0.019 | EXACT |
| Loss ratio | 8× (8.3) | ~8× | CORRECT |

### H-M1 Metrics (from h-m1/04_validation.md)

| Metric | Paper | Source | Status |
|--------|-------|--------|--------|
| Spurious acc epoch 5 | 91.20% | 91.20% | EXACT |
| Core acc epoch 5 | 80.50% | 80.50% | EXACT |
| Spurious acc epoch 50 | 91.34% | 91.34% | EXACT |
| Core acc epoch 50 | 82.62% | 82.62% | EXACT |
| Gap epoch 5 | +10.70% | +10.70% | EXACT |

### H-M2 Metrics (from h-m2/04_validation.md)

| Metric | Paper | Source | Status |
|--------|-------|--------|--------|
| Spurious peak epoch | 81 | 81 | EXACT |
| Core peak epoch | 81 | 81 | EXACT |
| Wilcoxon p | 3.88e-18 | 3.88e-18 | EXACT |

---

## Issues Found

### FATAL Issues (0)
None.

### MAJOR Issues (0)
None.

### MINOR Issues (0)
None additional from R1.

---

## Signal-to-Performance Gap Check

Paper correctly characterizes base-rate limitation:
- 5% minority rate → ~33% max precision at matched rate
- Paper states 0.329 precision, acknowledges "base-rate-limited absolute precision"
- No overclaiming detected

---

## Baseline Fairness Check

- Random baseline: 5% precision (correctly stated)
- 6.6× lift calculation: 0.329 / 0.05 = 6.58 → rounded to 6.6 (correct)

---

## Recommendation

**CONVERGED** - All numbers verified against source artifacts. No fabrication detected.
