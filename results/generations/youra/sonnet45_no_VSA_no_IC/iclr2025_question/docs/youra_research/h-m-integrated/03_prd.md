# Product Requirements Document: h-m-integrated

**Date:** 2026-08-20
**Author:** Anonymous
**Hypothesis:** h-m-integrated
**Status:** Draft
**Version:** 1.0

---

## Executive Summary

Implement UQ mechanism validation pipeline for Llama-3.1-8B-Instruct on TruthfulQA. Validate that uncertainty quantification methods (temperature scaling, conformal prediction, Monte Carlo dropout variants) produce scores that correlate positively with prediction incorrectness (Spearman ρ > 0.2, AUROC > 0.55). Test cross-dataset calibration transfer from HaluEval to TruthfulQA.

**Success Criteria:** All non-degenerate UQ methods (5 of 6, excluding MC k=1) pass gate threshold on either Spearman or AUROC. Coverage transfer maintains Δ ≤ 0.10 from target.

**Prerequisite:** h-e1 PASSED (AUROC ≥ 0.70 achieved). Reuses generated answers and uncertainty scores.

---

## Problem Statement

### Background

H-E1 validated single-method existence (AUROC ≥ 0.70 achievable). H-M-integrated validates the full UQ mechanism pipeline:
1. Method selection → uncertainty score generation → correctness prediction
2. Positive correlation between uncertainty and incorrectness
3. Cross-dataset calibration transfer (HaluEval → TruthfulQA)

Gate type: MUST_WORK. If mechanism fails at 8B scale, stop verification.

### User Need

Researchers need confidence that UQ pipeline works end-to-end across multiple methods, not just one successful method. Validates mechanism generality before scaling to larger experiments.

### Constraints

- Reuse h-e1 artifacts (answers, uncertainty scores, calibration params)
- 6 UQ methods tested: temp_scaling, conformal, mc_k1, mc_k3, mc_k5, mc_k10
- MC k=1 is degenerate baseline (excluded from gate check)
- TruthfulQA: 817 questions (40% calib, 60% eval)
- HaluEval: ~10k samples (QA split only)
- Llama-3.1-8B-Instruct frozen (no fine-tuning)

---

## Functional Requirements

### FR-1: Data Management

**FR-1.1 TruthfulQA Data Reuse**
- Load h-e1 generated answers from cache
- Load h-e1 uncertainty scores (6 methods × 817 questions)
- Load h-e1 calibration artifacts (temperature T, conformal threshold)
- Verify splits match (40% calib / 60% eval)

**FR-1.2 HaluEval Dataset Loading**
- Download HaluEval from HuggingFace `pminervini/HaluEval`
- Use QA split (~10k samples)
- Extract (question, answer, label) triples
- Generate answers using Llama-3.1-8B-Instruct (same config as h-e1)

**FR-1.3 Data Format**
- TruthfulQA: {question: str, generated_answer: str, label: int (0/1), uq_scores: dict[method_name, float]}
- HaluEval: {question: str, generated_answer: str, label: int (0/1)}

### FR-2: UQ Mechanism Validation

**FR-2.1 Spearman Correlation**
- Compute Spearman ρ between uncertainty scores and incorrectness (binary: 0 if correct, 1 if wrong)
- One ρ per UQ method (6 total)
- Gate threshold: ρ > 0.2

**FR-2.2 AUROC**
- Compute AUROC treating uncertainty as positive class score, incorrectness as ground truth
- One AUROC per UQ method (6 total)
- Gate threshold: AUROC > 0.55

**FR-2.3 AUSE (Robust Metric)**
- Compute Area Under Sparsification Error curve
- Sort samples by uncertainty (descending), remove top-k%, measure error on remaining samples
- One AUSE per UQ method (6 total)
- Lower is better (no gate threshold, comparison only)

**FR-2.4 Gate Check**
- For each non-degenerate method (exclude mc_k1):
  - PASS if Spearman ρ > 0.2 OR AUROC > 0.55
  - FAIL if both ρ ≤ 0.2 AND AUROC ≤ 0.55
- Experiment PASSES if ≥4 of 5 non-degenerate methods pass
- Experiment FAILS if ≥2 of 5 non-degenerate methods fail both metrics

### FR-3: Cross-Dataset Calibration Transfer

**FR-3.1 Conformal Prediction Calibration on HaluEval**
- Fit conformal prediction on HaluEval calibration set (80% of QA split)
- Target coverage: 1 - α = 0.90 (α = 0.10)
- Compute quantile threshold q = (1-α) quantile of nonconformity scores
- Measure achieved coverage on HaluEval test set (20% of QA split)

**FR-3.2 Transfer to TruthfulQA**
- Apply HaluEval-calibrated threshold to TruthfulQA test set
- Measure achieved coverage on TruthfulQA
- Compute transfer gap: |coverage_TruthfulQA - coverage_HaluEval|
- Gate threshold: Δ ≤ 0.10

**FR-3.3 AUROC Transfer**
- Compute AUROC on HaluEval test set
- Compute AUROC on TruthfulQA test set
- Report gap (informational, no gate threshold)

### FR-4: Visualization

**FR-4.1 Gate Metrics Scatter (Mandatory)**
- X-axis: Spearman ρ
- Y-axis: AUROC
- Points: 6 UQ methods (mc_k1 gray, others colored)
- Lines: Vertical at ρ=0.2, Horizontal at AUROC=0.55
- Quadrants labeled: Pass gate (top-right)
- Save: `{hypothesis_folder}/figures/gate_metrics_scatter.png`

**FR-4.2 Spearman Comparison (Bar Chart)**
- X-axis: 6 UQ methods
- Y-axis: Spearman ρ (-1.0 to 1.0)
- Horizontal line: threshold 0.2
- Error bars: SE if multiple seeds exist
- Save: `{hypothesis_folder}/figures/spearman_comparison.png`

**FR-4.3 AUSE vs AUROC (Scatter)**
- X-axis: AUSE (lower better)
- Y-axis: AUROC (higher better)
- Points: 6 methods
- Save: `{hypothesis_folder}/figures/ause_vs_auroc.png`

**FR-4.4 Sparsification Curves (6 subplots)**
- One subplot per method
- X-axis: Fraction removed (0 to 1)
- Y-axis: Error on remaining samples (0 to 1)
- Two lines: Oracle (sorted by true error) vs Method (sorted by uncertainty)
- Save: `{hypothesis_folder}/figures/sparsification_curves.png`

**FR-4.5 Cross-Dataset Calibration (2-panel)**
- Panel A: Coverage comparison (HaluEval vs TruthfulQA bars, target line at 0.90)
- Panel B: AUROC transfer gap (two bars: source, target)
- Save: `{hypothesis_folder}/figures/cross_dataset_calibration.png`

### FR-5: Results Reporting

**FR-5.1 Validation Report**
- Output file: `{hypothesis_folder}/04_validation.md`
- Sections:
  - Gate Results (table: method, Spearman ρ, AUROC, AUSE, PASS/FAIL)
  - Cross-Dataset Transfer Results (table: coverage_HaluEval, coverage_TruthfulQA, Δ)
  - Figure References (links to 5 figures)
  - Gate Decision: PASSED / FAILED
  - Reflection: Which methods passed, why failures occurred (if any)

**FR-5.2 Experiment Logs**
- Save raw results to `{hypothesis_folder}/results/metrics.json`
- Format: `{method_name: {spearman: float, auroc: float, ause: float}}`
- Save sparsification data to `{hypothesis_folder}/results/sparsification.json`
- Save cross-dataset data to `{hypothesis_folder}/results/cross_dataset.json`

---

## Non-Functional Requirements

### NFR-1: Performance

- Total runtime: < 30 minutes (reusing h-e1 artifacts, only computing metrics)
- HaluEval inference: ~1 hour (10k samples @ 8 samples/sec = 1250 batches)
- Metric computation: < 5 minutes (vectorized NumPy operations)

### NFR-2: Reproducibility

- Fixed random seed for HaluEval split (80/20 calib/test)
- Reuse h-e1 random seed for TruthfulQA consistency
- Save all intermediate artifacts (uncertainty scores, predictions)

### NFR-3: Code Quality

- Modular design: separate classes for UQMechanismValidator, CrossDatasetCalibrator
- Type hints for all functions
- Unit tests for Spearman, AUROC, AUSE computation
- Integration test: end-to-end pipeline on 10-sample subset

### NFR-4: Documentation

- README in experiment folder with usage instructions
- Inline comments for non-obvious metric formulas (e.g., AUSE integral)
- Docstrings for all public functions

---

## Dependencies

### Internal Dependencies

- h-e1 (prerequisite): Generated answers, uncertainty scores, calibration artifacts
- Llama-3.1-8B-Instruct model checkpoint (shared with h-e1)

### External Dependencies

**Datasets:**
- TruthfulQA: HuggingFace `truthfulqa/truthful_qa` (generation split)
- HaluEval: HuggingFace `pminervini/HaluEval` (QA split)

**Libraries:**
- numpy: Metric computation
- scipy: spearmanr, rankdata
- sklearn: roc_auc_score, roc_curve
- matplotlib: Figure generation
- transformers: Llama model inference (for HaluEval only)
- datasets: HuggingFace dataset loading

---

## Success Criteria

### Gate Success Criteria

1. **Mechanism Validation:** ≥4 of 5 non-degenerate methods pass gate (Spearman > 0.2 OR AUROC > 0.55)
2. **Cross-Dataset Transfer:** Coverage transfer Δ ≤ 0.10 from target (0.90)

### Quality Criteria

- All 5 figures generated and saved
- 04_validation.md exists with complete results table
- metrics.json saved with all method results
- No runtime errors during metric computation

### Failure Criteria (STOP)

- ≥2 non-degenerate methods fail both Spearman ≤ 0.2 AND AUROC ≤ 0.55
- Conformal coverage on TruthfulQA < 0.70 (critical transfer failure)

---

## Timeline & Milestones

**Phase 4 Implementation:** ~2 hours
- Data loading (h-e1 reuse + HaluEval): 30 min
- Metric computation implementation: 30 min
- Figure generation: 30 min
- Validation report generation: 30 min

**Phase 4 Execution:** ~1.5 hours
- HaluEval inference: 1 hour
- Metric computation: 5 min
- Figure generation: 5 min
- Gate check + report: 5 min

**Total:** ~3.5 hours (implementation + execution)

---

## Open Questions

1. **HaluEval Split Size:** Use full 10k or subsample for speed? (Recommend: subsample to 2k for calibration if coverage converges)
2. **MC Dropout Seeds:** Reuse h-e1 dropout masks or regenerate? (Recommend: reuse for consistency)
3. **AUSE Integration:** Trapezoidal vs Simpson's rule? (Recommend: trapezoidal, standard in literature)

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base

No relevant sources (KB indexed for vision models, not NLP UQ).

### B. GitHub Implementations (Exa)

1. **deeplearning-wisc/agentuq**: AUROC + Spearman + AUARC for UQ evaluation
2. **dionysus/uncertainty_metrics.py**: Production-quality Spearman, AUROC, AUSE classes
3. **Novartis/UNIQUE**: UQ benchmarking framework (multi-method evaluation)
4. **BetaConform (OpenReview)**: Cross-dataset conformal transfer via text similarity
5. **foadnamjoo/truthfulqa-audit**: Domain-conditional calibration (FEVER, BoolQ, HaluEval → TruthfulQA)
6. **arxiv/2512.15068**: Conformal prediction for RAG hallucination (HaluEval calibration protocol)

---

**Generated by:** Phase 3 Implementation Planning
**Next Step:** Architecture Design (03_architecture.md)
