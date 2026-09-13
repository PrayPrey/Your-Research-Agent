# Product Requirements Document: H-M3

**Hypothesis:** Within-cluster benchmark pairs show successful threshold transfer (AUROC degradation ≤ 0.08)

**Date:** 2026-08-10
**Type:** MECHANISM
**Tier:** FULL

---

## 1. Executive Summary

H-M3 validates that cluster membership (from H-E1) predicts successful threshold transfer. When a semantic entropy threshold is calibrated on one benchmark, it should transfer effectively to other benchmarks within the same cluster, with minimal AUROC degradation (≤0.08). This validates the practical utility of the clustering structure for transfer learning.

---

## 2. Problem Statement

H-E1 established clustering (silhouette=0.8245, k=2) and H-M2 validated that same-family benchmarks have similar uncertainty distributions (JS-div=0.0823). H-M3 tests whether this similarity translates to practical threshold transferability: can we calibrate a hallucination detection threshold on one benchmark and apply it successfully to another within the same cluster?

---

## 3. Functional Requirements

### FR-1: Load H-M1 Semantic Entropy Computation Pipeline
- **Input**: Llama-2-7B model, tokenizer
- **Components**: 
  - Generation sampling (N=10, temperature=1.0)
  - Bidirectional entailment clustering (DeBERTa-v3-large)
  - Semantic entropy calculation
- **Reuse**: Core pipeline from H-M1 validation

### FR-2: Multi-Benchmark Data Loading
- **Benchmarks** (6 total):
  - Cluster 1 (Factual Recall): TriviaQA, Natural Questions, SQuAD
  - Cluster 2 (Entity/Claim): PopQA, HaluEval-QA, FEVER
- **Sample size**: 1000 queries per benchmark
- **Split**: 70% calibration (700), 30% evaluation (300)

### FR-3: Within-Cluster Pair Definition
- **Cluster 1 pairs**: TriviaQA↔NQ, TriviaQA↔SQuAD, NQ↔SQuAD (3 pairs)
- **Cluster 2 pairs**: PopQA↔HaluEval, PopQA↔FEVER, HaluEval↔FEVER (3 pairs)
- **Total**: 6 within-cluster pairs (bidirectional = 12 transfer experiments)

### FR-4: Threshold Calibration Protocol
- **Method**: Find threshold at target FPR (0.1) on source benchmark calibration split
- **Function**: `calibrate_threshold(entropies, labels, target_fpr=0.1)`
- **Output**: Scalar threshold value per source benchmark

### FR-5: Cross-Benchmark Threshold Transfer
- For each within-cluster pair (source, target):
  1. Compute semantic entropy on target benchmark
  2. Apply source-calibrated threshold
  3. Compute AUROC on target
  4. Calculate degradation = AUROC_source - AUROC_target

### FR-6: Statistical Analysis
- **Primary**: Mean AUROC degradation across 6 pairs
- **Secondary**: 95% CI via bootstrap (1000 samples)
- **Threshold**: Mean ≤ 0.08, CI upper bound < 0.12

### FR-7: Visualization
- **Required**: Bar chart of AUROC degradation per pair with 0.08 threshold line
- **Optional**: Transfer matrix heatmap (6×6), cluster scatter with transfer arrows

---

## 4. Non-Functional Requirements

### NFR-1: Computational Efficiency
- Semantic entropy computation: ~3-5 min per 1000 queries
- Total runtime estimate: 6 benchmarks × ~4 min = 24-30 minutes

### NFR-2: Reproducibility
- Fixed seed (42) for all random operations
- Deterministic data splits

### NFR-3: Memory Requirements
- Peak: ~16GB GPU memory (Llama-2-7B + DeBERTa)

---

## 5. Success Criteria

| Metric | Target | Priority |
|--------|--------|----------|
| Mean within-cluster AUROC degradation | ≤ 0.08 | PRIMARY |
| 95% CI upper bound | < 0.12 | SECONDARY |
| All pairs degradation | ≤ 0.15 | TERTIARY |

**Gate Type:** SHOULD_WORK
**Fail Action:** EXPLORE tighter cluster criteria

---

## 6. Data Specifications

### Input Data

| Benchmark | Source | Split | Sample Size |
|-----------|--------|-------|-------------|
| TriviaQA | HF: trivia_qa (rc) | validation | 1000 |
| Natural Questions | HF: natural_questions | validation | 1000 |
| SQuAD | HF: squad | validation | 1000 |
| PopQA | HF: akariasai/PopQA | test | 1000 |
| HaluEval-QA | HF: pminervini/HaluEval (qa_samples) | data | 1000 |
| FEVER | HF: fever (v1.0) | paper_dev | 1000 |

### Pre-computed Data (from H-M1/H-E1)
- Cluster assignments from H-E1: {TriviaQA, NQ, SQuAD} = Cluster 1, {PopQA, HaluEval, FEVER} = Cluster 2
- Expected baseline AUROC: ~0.79 (Kuhn et al. 2024)

### Output Data
- Per-benchmark semantic entropy distributions
- Per-pair AUROC scores (source, target)
- Per-pair degradation values
- Aggregated statistics (mean, CI)

---

## 7. Dependencies

### 7.1 Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| transformers | ≥4.35.0 | Llama-2-7B, DeBERTa |
| torch | ≥2.0.0 | Model inference |
| datasets | ≥2.14.0 | HuggingFace datasets |
| scikit-learn | ≥1.3.0 | AUROC, ROC curve |
| numpy | ≥1.24.0 | Array operations |
| scipy | ≥1.10.0 | Bootstrap statistics |
| matplotlib | ≥3.7.0 | Visualization |

### 7.2 External Models
- `meta-llama/Llama-2-7b-hf` (HuggingFace, requires license)
- `microsoft/deberta-v3-large` (HuggingFace)

### 7.3 Hypothesis Dependencies

| Dependency | Status | Required Artifact |
|------------|--------|-------------------|
| H-E1 | PASS | Cluster assignments |
| H-M1 | PASS | Semantic entropy pipeline |
| H-M2 | PASS | JS-divergence validation |

---

## 8. Out of Scope

- Cross-cluster transfer (that's H-M4)
- Multiple model evaluation (Llama-2-7B only)
- Threshold optimization methods beyond FPR targeting
- Ablation of entailment model choice

---

## 9. Ablation Studies

### AB-1: FPR Target Sensitivity
- Test FPR targets: [0.05, 0.10, 0.15, 0.20]
- Report mean degradation for each

### AB-2: Calibration Split Size
- Test splits: [50/50, 60/40, 70/30, 80/20]
- Report mean degradation for each

---

## 10. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Degradation > 0.08 | Medium | Hypothesis fails | EXPLORE tighter cluster criteria |
| High variance across pairs | Medium | Inconclusive | Bootstrap CI provides bounds |
| Computational timeout | Low | Delayed results | Use cached entropy values |

---

*Generated from Phase 2C experiment brief (02c_experiment_brief.md)*
*Phase 3 Implementation Planning - PRD Step*
