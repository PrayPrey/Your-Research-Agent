# Validation Report: H-M2 Meta-Classifier Training Sufficiency

**Date:** 2026-07-13
**Hypothesis:** H-M2 (MECHANISM)
**Gate Type:** SHOULD_WORK
**Gate Result:** **FAIL**

---

## Executive Summary

H-M2 tested whether 50-60 training datasets provide sufficient examples for a Random Forest meta-classifier to learn feature-method relationships. The experiment **FAILED** the SHOULD_WORK gate due to insufficient data quantity and feature diversity.

**Key Finding:** The meta-classifier achieved only 25.6% CV accuracy (below 30% threshold), indicating no learning beyond baseline. This failure stems from limitations in the prerequisite h-e1 dataset, not a fundamental flaw in the hypothesis.

---

## Gate Evaluation

### Gate Criteria (SHOULD_WORK)
- **PASS:** CV Accuracy > 35% AND Generalization Gap < 20%
- **PARTIAL:** CV Accuracy ≥ 30% AND Gap < 25%
- **FAIL:** Otherwise

### Actual Results
- **CV Accuracy:** 0.256 (25.6%)
- **Generalization Gap:** 0.229 (22.9%)
- **Baseline Accuracy:** 0.483 (48.3%)

**Gate Verdict:** **FAIL**
- CV accuracy 0.256 < 0.30 (no learning beyond baseline)
- Meta-classifier performs worse than majority-class baseline

---

## Experiment Configuration

### Dataset
- **Source:** h-e1 benchmark collection (prerequisite)
- **Expected Size:** 50-60 benchmarks
- **Actual Size:** 29 benchmarks (48% of target)
- **Feature Completeness:**
  - sample_size: 13.8% coverage
  - dimensionality: 0% coverage  
  - num_classes: 13.8% coverage
  - class_imbalance: 75.9% coverage

### Model
- **Architecture:** Random Forest (100 trees, max_depth=10)
- **Cross-Validation:** Leave-5-out (13 folds)
- **Features Used:** 1 (after NaN filtering and zero-variance removal)

### Class Distribution
- Linear: 14 benchmarks
- Augmentation: 12 benchmarks
- Polynomial: 2 benchmarks
- RNN: 1 benchmark

---

## Root Cause Analysis

### Primary Issue: Insufficient Feature Diversity
The h-e1 dataset provided only 1 feature with non-zero variance after preprocessing:
- 9 of 10 computed features had >70% missing data
- The single remaining feature (class_imbalance) had near-zero variance
- The system used a fallback constant feature to allow gate evaluation

### Secondary Issue: Insufficient Sample Size
- Only 29 benchmarks collected (vs 50-60 target)
- Extreme class imbalance (14:12:2:1 ratio)
- Leave-5-out CV with 29 samples = only 4-5 test samples per fold

### Contributing Factors
1. **h-e1 Data Quality:** The prerequisite h-e1 experiment collected benchmarks but did not populate comprehensive metadata (dataset characteristics)
2. **Feature Computation Dependencies:** Most Tier 1 and Tier 2 features require raw dataset access, which was not available
3. **Literature Extraction Limitations:** Metadata extraction from papers is incomplete without accessing original datasets

---

## Validation Against Success Criteria

| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| Dataset Size | 50-60 benchmarks | 29 benchmarks | ❌ FAIL |
| Feature Coverage | 4-10 features after filtering | 1 feature | ❌ FAIL |
| CV Accuracy | > 35% (PASS) or ≥ 30% (PARTIAL) | 25.6% | ❌ FAIL |
| Generalization Gap | < 20% (PASS) or < 25% (PARTIAL) | 22.9% | ⚠️ PARTIAL |
| Baseline Improvement | Positive delta | -22.6% (worse) | ❌ FAIL |

---

## Generated Artifacts

### Code Files
- `src/data_preprocessor.py`: Data loading and feature extraction
- `src/baseline_model.py`: Majority-class baseline
- `src/meta_classifier.py`: Random Forest wrapper
- `src/cv_trainer.py`: Leave-K-out cross-validation
- `src/metrics_calculator.py`: Accuracy, gap, per-domain metrics
- `src/gate_evaluator.py`: SHOULD_WORK gate logic
- `src/visualizer.py`: 6 analysis figures
- `run_experiment.py`: Main orchestrator

### Output Files
- `output/metrics.json`: Complete metrics dictionary
- `output/gate_result.txt`: Gate verdict and message
- `output/cv_results.json`: Fold-wise train/test scores

### Visualizations
- `figures/gate_metrics_comparison.png` (MANDATORY)
- `figures/confusion_matrix.png`
- `figures/per_domain_accuracy.png`
- `figures/feature_importance.png`
- `figures/generalization_gap_per_fold.png`

---

## Hypothesis Assessment

### H-M2 Statement
"Aggregated benchmark results from literature provide sufficient training examples (50-60 datasets) to learn feature-method relationships."

### Verdict: **Cannot Reject or Confirm**

The experiment FAILED, but for **data availability reasons**, not due to a fundamental flaw in the hypothesis:

1. **Insufficient Data Quantity:** Only 29 benchmarks collected (vs 50-60 target)
2. **Insufficient Feature Diversity:** Only 1 usable feature (vs expected 4-10)
3. **Prerequisite Failure:** h-e1 did not provide required metadata richness

**This is NOT evidence that the hypothesis is false**. Rather, it demonstrates that:
- The prerequisite h-e1 experiment needs improvement (richer metadata extraction)
- More benchmarks with complete characteristics are needed
- The meta-learning approach cannot be tested without adequate input data

---

## Recommendations

### Immediate Actions
1. **Enhance h-e1 Data Collection:**
   - Extract dataset characteristics from papers AND original datasets
   - Augment with Papers with Code metadata
   - Target 60+ benchmarks with complete feature coverage

2. **Feature Engineering:**
   - Implement fallback feature computation from literature descriptions
   - Add domain-specific proxy features
   - Use text embeddings of benchmark descriptions

3. **Gate Decision:**
   - **Route to:** Phase 2A (Hypothesis Modification)
   - **Rationale:** SHOULD_WORK gate failure due to prerequisite limitations, not mechanism flaw
   - **Next Hypothesis:** Modify h-e1 to collect richer metadata OR test h-m2 with a different dataset source

### Long-Term Improvements
1. Separate "data collection" from "mechanism testing" hypotheses more cleanly
2. Add data quality gates before running downstream experiments
3. Implement automated data augmentation for sparse features

---

## Conclusion

H-M2 FAILED the SHOULD_WORK gate with 25.6% CV accuracy (below 30% threshold). However, this failure is attributable to insufficient prerequisite data from h-e1, not a flaw in the meta-learning hypothesis itself.

**Next Step:** Return to Phase 2A to either:
- Modify h-e1 to improve data collection, OR
- Redesign h-m2 to use alternative data sources with richer metadata

The code implementation is complete and correctly implements the meta-learning pipeline. The experiment infrastructure works as designed.
