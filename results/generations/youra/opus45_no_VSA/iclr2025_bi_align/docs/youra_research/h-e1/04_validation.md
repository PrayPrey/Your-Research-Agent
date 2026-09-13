# Validation Report: H-E1

**Date:** 2026-08-08
**Hypothesis:** H-E1 (EXISTENCE)
**Gate:** MUST_WORK
**Result:** PASS

---

## Summary

Four agency proxies (clarifying questions, option enumeration, epistemic hedging, explicit deferral) successfully extracted from HH-RLHF and RewardBench responses with **mean AUROC = 0.9836** (target: ≥0.8).

---

## Results

| Proxy Type | AUROC | Status |
|------------|-------|--------|
| Clarifying Question | 0.9949 | PASS |
| Option Enumeration | 0.9840 | PASS |
| Epistemic Hedging | 0.9880 | PASS |
| Explicit Deferral | 0.9676 | PASS |
| **Mean** | **0.9836** | **PASS** |

---

## Gate Criteria

| Criterion | Target | Result | Status |
|-----------|--------|--------|--------|
| All proxies > baseline (0.5) | 4/4 | 4/4 | PASS |
| ≥3 proxies ≥ 0.7 | 3/4 | 4/4 | PASS |
| Mean AUROC ≥ 0.8 | ≥0.8 | 0.9836 | PASS |

---

## Dataset Statistics

- **Total samples:** 41,896 responses
- **HH-RLHF:** 40,688 responses (test split)
- **RewardBench Safety:** 1,208 responses
- **Train/Test split:** 33,516 / 8,380 (80/20)

### Proxy Distribution (Test Set)

| Proxy | Positive | Percentage |
|-------|----------|------------|
| Clarifying Question | 166 | 2.0% |
| Option Enumeration | 215 | 2.6% |
| Epistemic Hedging | 980 | 11.7% |
| Explicit Deferral | 23 | 0.3% |

---

## Method

1. **Data Loading:** HH-RLHF (Anthropic) test split + RewardBench Safety subset
2. **Label Generation:** Regex pattern matching per proxy type (ground truth)
3. **Model:** TF-IDF (ngram 1-2, max 5000 features) + LogisticRegression (C=1.0)
4. **Evaluation:** AUROC on held-out test set (20%)

---

## Figures

- `figures/auroc_bar.png` - AUROC per proxy with target line
- `figures/roc_curves.png` - ROC curves for all 4 proxies

---

## Conclusion

**GATE SATISFIED.** Agency proxy extraction achieves substantially above-target performance. Hypothesis H-E1 passes. Downstream hypotheses H-M1, H-M2 are unblocked.

---

## Artifacts

- Code: `h-e1/code/`
- Results: `h-e1/results.json`
- Figures: `h-e1/figures/`
