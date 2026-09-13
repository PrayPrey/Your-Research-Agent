# Phase 2B: Verification Plan
**Main Hypothesis:** H-DNSI-v1
**Generated:** 2026-08-28

## Main Hypothesis Statement
Under standard ML benchmarks with dense SOTA histories (>50 entries over >3 years), DNSI = observed improvement entropy / expected entropy based on difficulty proxy correlates negatively with generalization gap (R > 0.4), because saturated benchmarks exhibit systematic overfitting to test set characteristics.

## Sub-Hypotheses

### H-E1 (Existence) — MUST_WORK
**Statement:** DNSI can be reliably computed from PapersWithCode SOTA histories using 6-month windowing and difficulty normalization (class count proxy)
- **Prerequisites:** None
- **Status:** READY
- **Falsification:** DNSI computation fails or produces undefined values for >50% of target benchmarks

### H-M1 (Mechanism) — MUST_WORK
**Statement:** DNSI correlates negatively with generalization gap (R > 0.4) across 4 benchmarks with ground truth (ImageNet-V2, CIFAR-10.2, ObjectNet, HANS)
- **Prerequisites:** h-e1
- **Status:** NOT_STARTED
- **Falsification:** R < 0.2 or positive correlation

### H-M2 (Mechanism - Temporal) — SHOULD_WORK
**Statement:** Pre-2019 DNSI (computed on 2009-2018 SOTA data) predicts post-2019 generalization gap measurements with R² > 0.3
- **Prerequisites:** h-e1
- **Status:** NOT_STARTED
- **Falsification:** R² < 0.1

### H-C1 (Condition - Cross-domain) — SHOULD_WORK
**Statement:** DNSI-gap correlation holds across domains: R > 0.3 in vision (ImageNet, CIFAR, ObjectNet) AND R > 0.3 in NLP (HANS/GLUE)
- **Prerequisites:** h-m1
- **Status:** NOT_STARTED
- **Falsification:** Correlation positive in one domain, negative in other

## Dependency Graph (DAG)
```
h-e1 ──┬──► h-m1 ──► h-c1
       │
       └──► h-m2
```

## Risk Analysis
| Risk | Severity | Mitigation |
|------|----------|------------|
| Small sample (n=4) | HIGH | Bayesian analysis, bootstrap CI, frame as pilot |
| Difficulty proxy choice | MODERATE | Sensitivity analysis across proxies |
| PapersWithCode publication bias | LOW | 6-month windowing smooths conference clustering |
| Data availability | LOW | All data public (PWC API + papers) |

## Timeline Estimate
- Phase 2C: 2 days (experiment designs for 4 sub-hypotheses)
- Phase 3: 2 days (implementation planning)
- Phase 4: 3-5 days (data collection + statistical analysis)
- Phase 5: 2 days (baseline comparison)
- **Total:** ~1-2 weeks

## Dialectical Analysis

**Thesis:** DNSI captures true benchmark saturation via entropy normalization, providing predictive indicator for generalization gaps.

**Antithesis:** Saturation and benchmark difficulty may be confounded by third factor (benchmark design quality). Sample size n=4 insufficient for robust correlation claims.

**Synthesis:** Frame as pilot study. Use Bayesian methods for small n. Report sensitivity analysis across difficulty proxy choices. Acknowledge correlational limitation but note predictive utility.

## Baselines for Comparison
1. Raw Entropy (no difficulty normalization)
2. Improvement Rate (mean accuracy gain/year)
3. Time Since Last Improvement (days since last SOTA)

## Success Criteria
- P1: Lowest DNSI quartile shows >10% generalization gap (p < 0.05)
- P2: Temporal prediction R² > 0.3 for ImageNet
- P3: Cross-domain R > 0.3 in both vision and NLP separately
