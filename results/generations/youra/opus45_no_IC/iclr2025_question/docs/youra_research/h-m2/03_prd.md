# Product Requirements Document: H-M2

**Hypothesis:** Benchmarks testing similar error processes exhibit similar uncertainty distributions (JS-divergence < 0.15)

**Date:** 2026-08-10
**Type:** MECHANISM
**Tier:** FULL

---

## 1. Executive Summary

H-M2 validates that the clustering structure observed in H-E1 aligns with intuited error families. We test whether benchmarks expected to test similar error processes (based on task semantics) actually produce similar uncertainty distributions, measured via Jensen-Shannon divergence.

---

## 2. Problem Statement

H-E1 showed data-driven clustering (silhouette=0.8245, k=2), but this was unsupervised. H-M2 tests the hypothesis that benchmarks we *expect* to share error processes (Factual Recall vs Entity/Claim families) have lower JS-divergence within families than across families.

---

## 3. Functional Requirements

### FR-1: Load H-E1 JS-Divergence Matrix
- **Input**: `h-e1/results/js_divergence_matrix.npy`
- **Fallback**: Recompute from entropy distributions if artifact unavailable
- **Output**: 6×6 symmetric matrix

### FR-2: Define Error Family Categories
- **Factual Recall Family**: TriviaQA, NaturalQuestions, SQuAD
- **Entity/Claim Family**: PopQA, HaluEval-QA, FEVER

### FR-3: Extract Same-Family vs Cross-Family Pairs
- **Same-family pairs**: 6 (3 within Factual + 3 within Entity/Claim)
- **Cross-family pairs**: 9

### FR-4: Statistical Hypothesis Test
- **Test**: Mann-Whitney U (one-sided, same < cross)
- **Effect size**: Cliff's delta

### FR-5: Generate Visualization
- Box plot comparing same-family vs cross-family distributions
- JS-divergence heatmap with family boundaries

---

## 4. Non-Functional Requirements

### NFR-1: No Training Required
- Pure statistical analysis of pre-computed values

### NFR-2: Reproducibility
- Deterministic results from fixed JS-divergence matrix

---

## 5. Success Criteria

| Metric | Target | Priority |
|--------|--------|----------|
| Mann-Whitney U p-value | < 0.05 | PRIMARY |
| Same-family mean JS-div | < 0.15 | SECONDARY |
| Effect size (Cliff's d) | < -0.5 (large) | TERTIARY |

---

## 6. Data Specifications

### Input Data
- **Source**: H-E1 experiment output
- **File**: `js_divergence_matrix.npy`
- **Benchmarks**: trivia_qa, natural_questions, squad, pop_qa, halueval_qa, fever

### Expected Values (from H-E1)
- Same-family: [0.056, 0.041, 0.072, 0.142, 0.139, 0.043] → mean ≈ 0.082
- Cross-family: mean ≈ 0.481

---

## 7. Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| H-E1 Validation | PASS | JS-divergence matrix available |
| H-M1 Validation | PASS | Semantic entropy mechanism confirmed |

---

## 8. Out of Scope

- New model training
- Additional benchmark datasets
- Threshold optimization
