# Phase 2B: Verification Plan
## Metadata Completeness Predicts Reproducibility Variance

**Generated:** 2026-08-09T04:40:00Z  
**Main Hypothesis:** H-MetadataReproducibility-v1  
**Source:** 03_refinement.yaml  

---

## 1. Executive Summary

This verification plan decomposes the main hypothesis into 4 sub-hypotheses organized by verification type. The plan follows a dependency-aware execution order where MUST_WORK gates block downstream hypotheses.

**Main Claim:** Under OpenML benchmark datasets with ≥10 matched runs (2019-2024), if metadata completeness score increases, then reproducibility variance (IQR) decreases by ≥20%, because richer documentation constrains preprocessing degrees of freedom.

---

## 2. Sub-Hypothesis Decomposition

### 2.1 h-e1: Existence Test (MUST_WORK)

| Field | Value |
|-------|-------|
| **ID** | h-e1 |
| **Type** | EXISTENCE |
| **Gate** | MUST_WORK |
| **Statement** | Metadata completeness score correlates negatively with reproducibility variance (IQR) after controlling for intrinsic stability, popularity, algorithm family, and infrastructure factors. |
| **Prediction** | P1: Top-quartile metadata completeness predicts ≥20% reduction in IQR vs bottom quartile |
| **Success Criterion** | 95% CI excludes <10% relative reduction; effect size ≥20% |
| **Falsification** | Effect <10% or CI includes zero |
| **Dependencies** | None (entry point) |
| **Blocked By** | None |

**Verification Protocol:**
1. Collect OpenML datasets with ≥10 matched runs (same flow, same hyperparameters)
2. Compute metadata completeness score (5-field checklist)
3. Compute reproducibility variance (IQR) per dataset
4. Run mixed-effects regression with controls
5. Test whether top-quartile M shows ≥20% IQR reduction vs bottom-quartile

---

### 2.2 h-m1: Mechanism Test (MUST_WORK)

| Field | Value |
|-------|-------|
| **ID** | h-m1 |
| **Type** | MECHANISM |
| **Gate** | MUST_WORK |
| **Statement** | Preprocessing entropy mediates the relationship between metadata completeness and reproducibility variance. |
| **Prediction** | P2: Preprocessing entropy mediates ≥30% of the metadata → variance effect |
| **Success Criterion** | Indirect effect accounts for ≥30%, p<0.05 (Sobel test, bootstrap CIs) |
| **Falsification** | Indirect effect <15% or p>0.10 |
| **Dependencies** | h-e1 must pass (existence established before mechanism testing) |
| **Blocked By** | h-e1 |

**Verification Protocol:**
1. Prerequisite: h-e1 confirms existence of metadata → variance relationship
2. Extract preprocessing components from OpenML flows
3. Compute preprocessing entropy (Shannon entropy of component families)
4. Run mediation analysis: M → Entropy → Variance
5. Sobel test + bootstrap CIs for indirect effect

**Sub-predictions:**
- P2a: High-M datasets show ≥30% lower preprocessing entropy
- P2b: High-M datasets show NO significant difference in model hyperparameter entropy

---

### 2.3 h-c1: Robustness Check (SHOULD_WORK)

| Field | Value |
|-------|-------|
| **ID** | h-c1 |
| **Type** | COMPARISON |
| **Gate** | SHOULD_WORK |
| **Statement** | The metadata → variance effect persists across robustness checks (early-run test, single-algorithm family, temporal holdout). |
| **Predictions** | P3 (early-run), P4 (RF-only), P5 (temporal holdout) |
| **Success Criterion** | Effect persists in ≥2 of 3 robustness tests |
| **Falsification** | Effect fails in ≥2 of 3 tests |
| **Dependencies** | h-e1 must pass |
| **Blocked By** | h-e1 |

**Verification Protocol:**
1. P3: Restrict to first-50-runs (within 90 days of upload); effect persists
2. P4: Restrict to RandomForest flows; effect persists
3. P5: Train on pre-2022, test on post-2022; R² degradation <25%

---

### 2.4 h-c2: Permutation Control (SHOULD_WORK)

| Field | Value |
|-------|-------|
| **ID** | h-c2 |
| **Type** | COMPARISON |
| **Gate** | SHOULD_WORK |
| **Statement** | Shuffled metadata completeness scores produce negligible effect (ruling out spurious correlation). |
| **Prediction** | P6: Permuted effect <5% of observed effect |
| **Success Criterion** | 1000 permutations yield effect <5% of true effect |
| **Falsification** | Shuffled effect ≥20% of observed |
| **Dependencies** | h-e1 must pass |
| **Blocked By** | h-e1 |

**Verification Protocol:**
1. Run 1000 permutations of metadata completeness scores
2. For each permutation, compute regression coefficient
3. Compare permutation distribution to true effect
4. True effect should be >95th percentile of permutation distribution

---

## 3. Execution Order (Dependency Graph)

```
┌─────────────────────────────────────────────────────────────┐
│                    PHASE 2C-4 EXECUTION                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Stage 1: h-e1 (EXISTENCE, MUST_WORK)                     │
│            ↓                                                │
│            Gate Check: If FAIL → Pipeline BLOCKED           │
│            ↓                                                │
│   Stage 2: h-m1 (MECHANISM, MUST_WORK)                     │
│            ↓                                                │
│            Gate Check: If FAIL → Pipeline BLOCKED           │
│            ↓                                                │
│   Stage 3: [PARALLEL]                                       │
│            ├── h-c1 (ROBUSTNESS, SHOULD_WORK)              │
│            └── h-c2 (PERMUTATION, SHOULD_WORK)             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Execution Rules:**
- MUST_WORK gates: Pipeline halts if any fails
- SHOULD_WORK gates: Pipeline continues with warnings if fail
- h-c1 and h-c2 can run in parallel after h-m1 passes

---

## 4. Resource Requirements

| Sub-Hypothesis | Compute | Data | Statistical Tests |
|----------------|---------|------|-------------------|
| h-e1 | Low | OpenML API, ~200 datasets | Mixed-effects regression |
| h-m1 | Medium | Flow parsing, entropy computation | Sobel mediation, bootstrap |
| h-c1 | Medium | Temporal splits, RF subset | Regression × 3 subsets |
| h-c2 | High | 1000 permutations | Permutation testing |

**Total Estimated Time:** 8-12 hours compute time

---

## 5. Assumptions to Monitor

| ID | Assumption | Monitoring Strategy |
|----|------------|---------------------|
| A1 | OpenML seed logging complete | Check coverage in pilot |
| A2 | Preprocessing taxonomy standardizable | Measure flow parsing success rate |
| A3 | Metadata time-invariant | Version-1 restriction |
| A4 | Metadata ≠ popularity proxy | Stratified analysis |
| A5 | 200+ datasets meet criteria | Count in data collection |

---

## 6. Phase 2C Entry Point

**Next Action:** Begin Phase 2C experiment design for h-e1 (EXISTENCE, MUST_WORK, status=READY)

**Phase 2C will produce:**
- Detailed experiment specification for h-e1
- Data collection pipeline design
- Statistical analysis plan with code templates

---

## Appendix: Prediction-to-Hypothesis Mapping

| Prediction | Hypothesis | Priority |
|------------|------------|----------|
| P1 | h-e1 | Primary |
| P2, P2a, P2b | h-m1 | Primary |
| P3, P4, P5 | h-c1 | Secondary |
| P6 | h-c2 | Secondary |
