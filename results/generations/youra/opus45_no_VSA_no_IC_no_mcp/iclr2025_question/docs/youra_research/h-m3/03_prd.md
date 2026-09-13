# PRD: H-M3 Orthogonal Signals Enable Complementary Detection

**Hypothesis ID:** H-M3
**Type:** MECHANISM
**Gate:** MUST_WORK
**Generated:** 2026-08-28

---

## 1. Executive Summary

Verify that token entropy (H-M1) and N-sample consistency (H-M2) capture orthogonal failure modes. If correlation is low (r < 0.3) and discordant cases show differential predictive value, the signals are complementary and suitable for fusion.

---

## 2. Problem Statement

**Research Question:** Do entropy and consistency measure the same underlying uncertainty, or different failure modes?

**Why This Matters:** If signals are redundant (high correlation), fusion adds no value. If orthogonal, each captures unique information about hallucination.

---

## 3. Functional Requirements

### FR-1: Score Loading
- Load entropy scores from H-M1 results (817 values)
- Load consistency scores from H-M2 results (817 values)
- Load ground truth labels from TruthfulQA

### FR-2: Correlation Analysis
- Compute Pearson r between entropy and (1 - consistency)
- Compute Spearman ρ for robustness
- Primary criterion: r < 0.3

### FR-3: Rank Normalization
- Convert both signals to percentile ranks [0, 1]
- Invert consistency ranks (low consistency = high rank)

### FR-4: Discordant Case Identification
- Define discordant: |rank_diff| > 0.5
- Categorize into high-entropy-only and high-inconsistency-only subsets
- Secondary criterion: discordant proportion > 0.15

### FR-5: Subset AUROC Analysis
- Compute AUROC for entropy on high-entropy-only subset
- Compute AUROC for consistency on high-inconsistency-only subset
- Secondary criterion: both AUROCs > 0.6

### FR-6: Visualization
- Scatter plot: entropy vs (1 - consistency) colored by correctness
- Quadrant analysis plot

---

## 4. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seed for any stochastic operations
- Version-pinned dependencies

### NFR-2: Performance
- CPU-only computation (no GPU required)
- Complete analysis in < 1 minute

---

## 5. Dependencies

### Required from H-M1:
- `h-m1/results/entropy_scores.json` with 817 entropy values

### Required from H-M2:
- `h-m2/results/consistency_scores.json` with 817 consistency values

---

## 6. Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| Pearson r | < 0.3 | Primary |
| Discordant proportion | > 0.15 | Secondary |
| Entropy subset AUROC | > 0.6 | Secondary |
| Consistency subset AUROC | > 0.6 | Secondary |

---

## 7. Out of Scope

- New model inference (reuses H-M1/H-M2 outputs)
- Dataset loading (reuses cached results)
- Hyperparameter tuning

---

**Phase 3 PRD Complete for H-M3**
