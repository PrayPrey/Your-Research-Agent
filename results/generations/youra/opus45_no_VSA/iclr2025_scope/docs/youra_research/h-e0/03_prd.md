# Product Requirements Document: h-e0

**Date:** 2026-08-09
**Hypothesis:** Instruction prefixes are linearly separable by FLAN task family (macro-F1 ≥0.75 on 10+ families)
**Type:** EXISTENCE (Proof of Concept)
**Phase:** Phase 3 Implementation Planning

---

## Executive Summary

This PRD specifies implementation requirements for validating whether instruction prefixes from FLAN tasks are linearly separable by task family. Success criterion: macro-F1 ≥0.75 using a frozen sentence encoder + linear classifier on 10+ task families.

---

## Problem Statement

**Research Question:** Can instruction prefixes be classified into FLAN task families using a linear probe on sentence embeddings?

**Significance:** If true, instruction semantics carry task-type information extractable via simple linear methods, enabling zero-shot adapter routing based on instruction content.

**Gate:** MUST_WORK - Failure blocks all downstream hypotheses (h-e1, h-m1, h-m2).

---

## Functional Requirements

### FR-1: Data Pipeline
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | Load FLAN collection metadata (task family labels) | P0 |
| FR-1.2 | Filter to families with ≥500 samples | P0 |
| FR-1.3 | Select 10+ task families for classification | P0 |
| FR-1.4 | Extract instruction prefix (first sentence/task prompt) | P0 |
| FR-1.5 | Stratified 80/20 train/test split | P0 |
| FR-1.6 | Truncate to max 128 tokens | P1 |

### FR-2: Baseline Model
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | Implement stratified random classifier (DummyClassifier) | P0 |
| FR-2.2 | Compute baseline macro-F1 and accuracy | P0 |

### FR-3: Proposed Model
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | Load sentence-transformers/all-MiniLM-L6-v2 (frozen) | P0 |
| FR-3.2 | Encode instruction prefixes to 384-dim embeddings | P0 |
| FR-3.3 | Train LogisticRegression (multinomial, L-BFGS, balanced) | P0 |
| FR-3.4 | Predict task family from embeddings | P0 |

### FR-4: Evaluation
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1 | Compute macro-F1 score (primary metric) | P0 |
| FR-4.2 | Compute accuracy (secondary metric) | P0 |
| FR-4.3 | Generate classification report (per-class F1) | P0 |
| FR-4.4 | Gate check: macro-F1 ≥ 0.75 | P0 |

### FR-5: Visualization
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.1 | Gate metrics bar chart (target vs actual) | P0 |
| FR-5.2 | Confusion matrix heatmap | P1 |
| FR-5.3 | t-SNE/UMAP embedding visualization | P1 |
| FR-5.4 | Per-family F1 bar chart | P1 |

### FR-6: Mechanism Verification
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-6.1 | Verify embedding shape (N, 384) | P0 |
| FR-6.2 | Verify classifier fitted with correct classes | P0 |
| FR-6.3 | Verify predictions are valid labels | P0 |

---

## Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-1 | Reproducibility | Fixed random_state=42 for all stochastic operations |
| NFR-2 | Performance | Embedding generation <5 min for 5000 samples |
| NFR-3 | Memory | Peak memory <8GB for embedding + classification |
| NFR-4 | Output | All figures saved to h-e0/figures/ |

---

## Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| **Primary** | macro-F1 ≥ 0.75 | sklearn.metrics.f1_score(average='macro') |
| Direction | proposed > baseline | Compare macro-F1 scores |
| Families | ≥10 task families | Count unique labels in test set |

---

## Data Specifications

### Input
- **Source:** FLAN Collection (Open-Orca/FLAN or google-research/FLAN CSV)
- **Fields:** instruction text, Generic Task Category
- **Volume:** 5,000+ samples (500+ per family × 10+ families)

### Output
- **Primary:** 04_validation.md with gate result
- **Artifacts:** figures/, model checkpoints (optional)

---

## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| sentence-transformers | ≥2.2.0 | MiniLM encoder |
| sklearn | ≥1.0 | LogisticRegression, metrics |
| pandas | ≥1.5 | Data loading |
| matplotlib | ≥3.5 | Visualization |
| numpy | ≥1.21 | Array operations |

---

## Out of Scope

- Hyperparameter tuning (EXISTENCE type: single run)
- Multiple seeds (single seed: 42)
- Non-linear classifiers (linear probe only)
- Full FLAN dataset (subsample to 10+ families)

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Insufficient family separation | Medium | High (blocks pipeline) | Verify 10+ distinct families before classification |
| Class imbalance | Medium | Medium | Use balanced class_weight in LogReg |
| Embedding quality | Low | High | Use established MiniLM model |

---

*Generated from Phase 2C experiment brief*
*Next: Architecture design (Step 3)*
