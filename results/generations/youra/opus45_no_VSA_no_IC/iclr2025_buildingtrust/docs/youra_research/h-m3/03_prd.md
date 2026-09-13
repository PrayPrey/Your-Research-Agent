# Product Requirements Document: H-M3

**Hypothesis:** FactScore measures atomic factual precision via retrieval-based verification, a capability distinct from both TruthfulQA and HaluEval

**Date:** 2026-08-24
**Phase:** 3 - Implementation Planning
**Type:** MECHANISM

---

## 1. Executive Summary

This PRD defines implementation requirements for validating that FactScore measures a construct distinct from TruthfulQA and HaluEval. The experiment computes cross-benchmark correlations and uses PCA to assess whether these three truthfulness benchmarks capture different dimensions of model capability.

**Success Criteria:** r(FactScore, TruthfulQA) < 0.7 AND r(FactScore, HaluEval) < 0.7

---

## 2. Problem Statement

### 2.1 Background
H-M2 established that HaluEval (coherence/consistency) is distinct from TruthfulQA (misconception resistance) with r=0.162. H-M3 extends this by testing whether FactScore (atomic factual precision via retrieval) represents a third distinct dimension.

### 2.2 Research Question
Does FactScore measure a capability not captured by TruthfulQA or HaluEval?

### 2.3 Hypothesis Type
MECHANISM - Testing whether FactScore's retrieval-based atomic fact verification measures a distinct construct.

---

## 3. Functional Requirements

### FR-1: Data Collection
- **FR-1.1:** Load model scores from H-M2 analysis (N=50 models with TruthfulQA and HaluEval scores)
- **FR-1.2:** Obtain FactScore results for same model population
- **FR-1.3:** Merge benchmark scores into unified DataFrame

### FR-2: Correlation Analysis
- **FR-2.1:** Compute Spearman correlation r(FactScore, TruthfulQA)
- **FR-2.2:** Compute Spearman correlation r(FactScore, HaluEval)
- **FR-2.3:** Compute reference r(TruthfulQA, HaluEval) to verify H-M2 finding
- **FR-2.4:** Calculate 95% bootstrap confidence intervals for each correlation

### FR-3: PCA Analysis
- **FR-3.1:** Standardize benchmark scores (z-score normalization)
- **FR-3.2:** Fit PCA with 3 components (one per benchmark)
- **FR-3.3:** Calculate explained variance per component
- **FR-3.4:** Determine components needed for 80% variance (expect 2+)
- **FR-3.5:** Extract loading matrix for interpretation

### FR-4: Gate Evaluation
- **FR-4.1:** Evaluate primary condition: r(FS,TQA) < 0.7 AND r(FS,HE) < 0.7
- **FR-4.2:** Evaluate secondary condition: PCA needs 2+ components for 80% variance
- **FR-4.3:** Generate PASS/PARTIAL/FAIL verdict

### FR-5: Visualization
- **FR-5.1:** Generate gate metrics bar chart (correlations vs 0.7 threshold)
- **FR-5.2:** Generate 3x3 correlation heatmap
- **FR-5.3:** Generate PCA biplot with benchmark loadings
- **FR-5.4:** Generate pairwise scatter matrix
- **FR-5.5:** Save all figures to h-m3/figures/

### FR-6: Reporting
- **FR-6.1:** Generate 04_validation.md with results
- **FR-6.2:** Include mechanism verification code output
- **FR-6.3:** Document key findings and gate result

---

## 4. Non-Functional Requirements

### NFR-1: Performance
- Analysis completes in < 5 minutes (CPU-only correlation/PCA)
- If running FactScore evaluation: budget 10-50 GPU-hours

### NFR-2: Reproducibility
- Fixed random seed (42) for bootstrap sampling
- All intermediate results saved to CSV

### NFR-3: Compatibility
- Python 3.8+
- Dependencies: pandas, numpy, scipy, sklearn, matplotlib, seaborn

---

## 5. Data Specifications

### 5.1 Input Data
| Dataset | Source | Size | Format |
|---------|--------|------|--------|
| Model scores (H-M2) | h-m2/model_scores.csv | N=50 | CSV |
| FactScore results | Published leaderboard or computed | N=50 | CSV |

### 5.2 Output Data
| Output | Path | Format |
|--------|------|--------|
| Merged scores | h-m3/model_scores.csv | CSV |
| Correlation results | h-m3/correlation_results.json | JSON |
| PCA results | h-m3/pca_results.json | JSON |
| Validation report | h-m3/04_validation.md | Markdown |

---

## 6. Evaluation Metrics

### 6.1 Primary Metrics
- **r(FactScore, TruthfulQA):** Spearman correlation, target < 0.7
- **r(FactScore, HaluEval):** Spearman correlation, target < 0.7

### 6.2 Secondary Metrics
- **PCA components for 80% variance:** target >= 2
- **Bootstrap CI width:** quality indicator

### 6.3 Gate Conditions
| Condition | Threshold | Weight |
|-----------|-----------|--------|
| r(FS,TQA) | < 0.7 | Primary |
| r(FS,HE) | < 0.7 | Primary |
| PCA components | >= 2 | Secondary |

---

## 7. Dependencies

### 7.1 Prerequisite Hypotheses
- **H-M2:** VALIDATED (r(HaluEval, TruthfulQA) = 0.162)

### 7.2 External Dependencies
- FactScore benchmark results (leaderboard or computed)
- H-M2 model scores file

### 7.3 Library Dependencies
- scipy.stats (spearmanr)
- sklearn.decomposition (PCA)
- pandas, numpy, matplotlib, seaborn

---

## 8. Success Criteria

| Criterion | Definition | Status |
|-----------|------------|--------|
| **PASS** | Both r < 0.7, PCA shows multi-dimensional structure | Target |
| **PARTIAL** | One r < 0.7, other >= 0.7 | Acceptable |
| **FAIL** | Both r >= 0.7 | Valid finding (overlap) |

---

## 9. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| FactScore data unavailable | High | Use published leaderboard; fallback to subset evaluation |
| Model population mismatch | Medium | Verify model overlap; report N for each correlation |
| High variance in estimates | Medium | Bootstrap CI; report uncertainty |

---

*Generated from Phase 2C experiment brief: 02c_experiment_brief.md*
