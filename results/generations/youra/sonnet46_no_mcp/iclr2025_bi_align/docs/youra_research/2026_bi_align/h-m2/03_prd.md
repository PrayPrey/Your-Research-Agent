# Product Requirements Document (PRD)
# H-M2: Round-Stratified Label-Distribution Coefficient Shift

**Generated:** 2026-05-03
**Phase:** 3 - Implementation Planning
**Hypothesis:** H-M2 (MECHANISM / INCREMENTAL / SHOULD_WORK)
**Tier:** FULL (max 30 tasks)
**Author:** Anonymous
**Base Hypothesis:** H-M1 (COMPLETED, MUST_WORK gate PASSED; β_exposure=0.041, p=2.05e-05)

stepsCompleted: [step-01, step-02, step-03, step-04, step-05]

---

## 1. Executive Summary

This PRD specifies implementation requirements for H-M2, the second mechanism test in the Human→AI Annotation Drift pipeline. H-M2 tests whether preference labels from later annotation rounds encode systematically stronger stylistic biases — measured as larger logistic regression coefficients (β_L, β_H, β_S) — compared to coefficients from early-round-trained predictors on identical held-out prompt sets. H-M2 introduces one novel component over H-E1: `coefficient_comparison.py`, which implements round-stratified model fitting + bootstrap CI comparison for directional coefficient shift detection. All other components are reused from H-E1's validated pipeline.

**Core Question:** Do later-round HH-RLHF preference labels encode systematically stronger stylistic weights (β_L, β_H, β_S) than early-round labels, after controlling for semantic quality (Q_early)?

**Gate:** SHOULD_WORK — ≥ 2/3 stylistic coefficients (β_L, β_H, β_S) are directionally larger in the late-round model vs. early-round model with non-overlapping 95% bootstrap CIs. Failure action: PIVOT to narrower claim (document which specific features shift); continue to H-M3 with reduced scope.

**Failure Response:** n_directional < 2 → PIVOT: document partial results; narrow H-M3 scope to features with confirmed directional shift.

---

## 2. Problem Statement

### 2.1 Research Gap

H-M1 confirmed exposure-dependent norm internalization at the behavioral level (β_exposure=0.041, p=2.05e-05 in WebGPT panel regression). H-M2 tests the label-distribution implication: if annotators internalize AI-typicality norms over time, later-round preference labels should encode systematically stronger stylistic biases. This is a distinct signal from H-E1's null result (which tested round×ambiguity interaction, not aggregate coefficient magnitude comparison across separately-trained models).

### 2.2 Hypothesis

Under conditions of verified exposure-dependent norm internalization (H-M1 passed), if preference labels from later annotation rounds are used to train a logistic regression preference predictor, then the learned stylistic coefficients (β_L, β_H, β_S) will be systematically and directionally larger than coefficients from early-round-trained predictors on identical held-out prompt sets, because internalized AI-typicality norms are reflected in annotation decisions and thus encoded in the label distribution of later rounds.

### 2.3 Gate Condition

SHOULD_WORK: ≥ 2 of 3 stylistic coefficients (β_L, β_H, β_S) are directionally larger in the late-round preference predictor vs. early-round predictor on identical held-out prompt sets, with non-overlapping 95% bootstrap confidence intervals. Scientific magnitude not required at PoC stage — direction + statistical separation is sufficient.

---

## 3. Scope

### 3.1 In Scope

- Round-stratified HH-RLHF loading: early-round (~56K rows, round-1) and late-round (~56K rows, round-3) subsets via equal-partition index (reused from H-E1 `data_loader.py`)
- 25% stratified held-out cross-round test set before any model fitting (~14K per round = ~28K total)
- Topic distribution balance check: chi-square test on prompt topic distribution between early and late training sets
- Early-round preference predictor: `LogisticRegression(C=1.0, solver='lbfgs')` trained on ~42K round-1 samples
- Late-round preference predictor: identical architecture trained on ~42K round-3 samples
- StandardScaler fit on round-1 training data only; applied to all subsets for coefficient comparability
- Q_early covariate: reused from H-E1 `q_early.py` (round-1 trained, Platt-calibrated for round-3)
- Bootstrap CI computation: 2000 resamples per round model; 95% CI for [β_L, β_H, β_S]
- Directional comparison: non-overlapping CI test; n_directional count
- Sign consistency check: all 3 stylistic deltas positive
- β_Q stability check: Q_early coefficient stable across models
- Cross-round held-out validation: late model prefers longer/more structured responses on high-ambiguity prompts
- 5 figures: coefficient comparison bar chart, bootstrap distribution overlapping histograms, feature importance stability, cross-round held-out prediction scatter, topic balance chi-square residual plot
- Gate metrics bar chart (mandatory)

### 3.2 Out of Scope

- Neural network fine-tuning (H-M3/H-M4 scope)
- Reward model training (H-M3 scope)
- RLHF PPO training (H-M4 scope)
- WebGPT dataset (H-M1 scope; H-M2 uses HH-RLHF only — sufficient round structure, ~56K per round)
- Per-annotator worker-ID panel regression (H-M1 scope; H-M2 tests aggregate label distribution, not individual exposure)
- New geometric projection encoder (H-M1 scope; H-M2 uses standard logistic regression coefficients)

---

## 4. Data Specification

### 4.1 Primary Dataset: Anthropic HH-RLHF (Round-Stratified)

| Field | Value |
|-------|-------|
| Name | Anthropic HH-RLHF (Human Feedback) |
| Source | HuggingFace Hub: `Anthropic/hh-rlhf` |
| Scale | ~169,000 pairwise preference comparisons (3 rounds, ~56,333 each) |
| Fields | `chosen` (preferred response), `rejected` (dispreferred response) |
| Download | `load_dataset("Anthropic/hh-rlhf")` — **auto-download** (already cached from H-E1) |
| Cache | `~/.cache/huggingface/datasets/` |
| Round Split | Equal-partition by index: round-1=[0, 56333), round-3=[112666, 169000) |
| Hold-out | 25% stratified from each round before fitting → ~14,083 per round = ~28,166 total test set |
| Training | ~42,250 early-round + ~42,250 late-round training samples |

**Note:** HH-RLHF auto-downloads via HuggingFace — no manual download task required.

**Round-2 usage:** Round-2 (~56K mid-round rows) excluded from main analysis. May be used for Q_early Platt-calibration recalibration and intermediate monotonicity check only.

### 4.2 No Additional Datasets Required

H-M2 uses only HH-RLHF. No new encoder model downloads. No WebGPT. All feature extraction uses H-E1 `features.py` (numpy operations, no model downloads).

---

## 5. Functional Requirements

### FR-1: HH-RLHF Round-Stratified Loading (REUSED + EXTENDED)

- FR-1.1: Reuse `h-e1/code/data_loader.py::load_hh_rlhf()` and `stratify_rounds()` for dataset loading and equal-partition round split
- FR-1.2: Extend stratification to extract early-round (round-1) and late-round (round-3) subsets: `early_df = df.iloc[0:round_size]`, `late_df = df.iloc[2*round_size:]`
- FR-1.3: Perform 25% stratified hold-out from each round before any model fitting: `train_test_split(stratify=y, test_size=0.25, random_state=42)` on each round separately
- FR-1.4: Topic distribution balance check: chi-square test comparing early vs. late prompt topic distributions; warn if p < 0.05
- FR-1.5: Round size check: assert `round_size >= 40000`, warn if < 40,000

### FR-2: Feature Extraction (REUSED from H-E1)

- FR-2.1: Reuse `h-e1/code/features.py::build_feature_matrix()` — extract [length_ratio, hedging_count_normalized, structure_marker_count] for all subsets
- FR-2.2: Reuse `h-e1/code/q_early.py::QEarlyModel` — load or retrain Q_early on round-1 training data; Platt-calibrate for round-3
- FR-2.3: Apply StandardScaler fit ONLY on round-1 training data; use same scaler for round-3 features (ensures coefficient scale comparability)

### FR-3: Round-Stratified Preference Predictor Fitting (NEW — coefficient_comparison.py)

- FR-3.1: Fit early-round predictor: `LogisticRegression(C=1.0, solver='lbfgs', max_iter=1000, random_state=42)` on round-1 training set with feature vector [X_scaled_3, q_early_score] → shape (N_early, 4)
- FR-3.2: Fit late-round predictor: identical `LogisticRegression` config on round-3 training set; use same StandardScaler (fit on round-1) for X_scaled; use same Q_early model (Platt-calibrated) for q_early_score
- FR-3.3: Extract stylistic coefficients: `early_coefs = early_clf.coef_[0][:3]` → [β_L_early, β_H_early, β_S_early]; analogously for late
- FR-3.4: Compute coefficient deltas: `deltas = late_coefs - early_coefs` for each of [β_L, β_H, β_S]
- FR-3.5: β_Q stability check: `assert abs(late_clf.coef_[0][3] - early_clf.coef_[0][3]) < 0.2`, warn if violated (Q_early coefficient should be stable across rounds)

### FR-4: Bootstrap CI Computation (NEW — coefficient_comparison.py)

- FR-4.1: Bootstrap 95% CI for early-round model coefficients: 2000 stratified resamples from round-1 training set; `ci_early: shape (2, 3)` = [low/high, [β_L, β_H, β_S]]
- FR-4.2: Bootstrap 95% CI for late-round model coefficients: 2000 stratified resamples from round-3 training set; `ci_late: shape (2, 3)`
- FR-4.3: Non-overlap test: `n_directional = sum(late_ci[0, i] > early_ci[1, i] for i in [0,1,2])` — count of features where late strictly above early at 95% CI level
- FR-4.4: Sign consistency check: warn if any `delta[i] < 0` for stylistic features

### FR-5: Cross-Round Held-Out Validation (NEW — coefficient_comparison.py)

- FR-5.1: Evaluate both models on shared held-out test set (~28K total: ~14K early + ~14K late)
- FR-5.2: Compute AUC for early and late models on shared test set: `roc_auc_score(y_test, clf.predict_proba(X_test)[:,1])`
- FR-5.3: Ambiguity proxy for held-out test: score magnitude proxy `|score_0 - score_1|` < threshold → high ambiguity (consistent with H-M1 methodology)
- FR-5.4: On high-ambiguity held-out prompts: verify late-round model assigns higher preference probability to longer/more structured responses (≥ 10% longer responses preferred more often by late model)

### FR-6: Evaluation Metrics

- FR-6.1: **n_directional**: count of {β_L, β_H, β_S} where `late_ci[0] > early_ci[1]` (non-overlapping, late strictly above early); gate target: ≥ 2/3
- FR-6.2: **β_L_delta, β_H_delta, β_S_delta**: point estimates of coefficient shift (late - early); target: all > 0
- FR-6.3: **β_Q_stability**: |late_β_Q - early_β_Q|; target: < 0.2 (validates Q_early isolates quality)
- FR-6.4: **Cross-round AUC**: late model AUC vs. early model AUC on shared test set; informational
- FR-6.5: **Topic balance p-value**: chi-square p-value for topic distribution balance; target: > 0.05
- FR-6.6: **Sign consistency**: boolean — all 3 stylistic deltas positive; inconsistency triggers PIVOT

### FR-7: Visualizations (6 figures)

- FR-7.1: **Coefficient Comparison Bar Chart** (MANDATORY — gate metric): side-by-side bar chart [β_L, β_H, β_S, β_quality] for early vs. late models with 95% bootstrap CI error bars; highlight non-overlapping pairs; horizontal reference line at 0
- FR-7.2: **Bootstrap Distribution Overlapping Histograms**: overlapping histograms of bootstrap coefficient distributions for early vs. late per feature (β_L, β_H, β_S); demonstrates CI separation or overlap
- FR-7.3: **Feature Importance Stability Plot**: coefficient magnitudes across rounds 1, 2, 3 (fit auxiliary round-2 model or use interpolation); shows monotonic trend
- FR-7.4: **Cross-Round Held-Out Prediction Scatter**: scatter of early-round model preference score vs. late-round model preference score on same held-out prompts; divergence from diagonal = systematic shift
- FR-7.5: **Topic Distribution Balance**: chi-square residual bar chart comparing prompt topic distributions between early and late training sets
- FR-7.6: **Gate Metrics Summary Bar Chart**: target vs. actual n_directional, β_L_delta, β_H_delta, β_S_delta vs. thresholds
- All figures saved to `h-m2/figures/`

### FR-8: Pipeline Integration

- FR-8.1: Main entry point `run_experiment.py::main()` orchestrates full pipeline
- FR-8.2: Gate logic: SHOULD_WORK gate PASSES if n_directional ≥ 2 AND non-overlapping CIs; PARTIAL if n_directional = 1; FAIL if n_directional = 0 or sign inconsistency
- FR-8.3: Results serialized to `h-m2/results/results.yaml` with all metrics
- FR-8.4: Mechanism log message: `"Coefficient comparison: β_L=[{early:.4f},{late:.4f}] δ={delta:.4f}; β_H=[{early:.4f},{late:.4f}] δ={delta:.4f}; β_S=[{early:.4f},{late:.4f}] δ={delta:.4f}; n_directional={n}/3"`

---

## 6. Non-Functional Requirements

### 6.1 Performance

- Wall-clock estimate: ~5–15 minutes (feature extraction over ~169K samples + 2×2000 bootstrap iterations on ~42K samples each; no GPU needed)
- No encoder model (unlike H-M1); all operations are numpy/sklearn — fast CPU execution
- Single GPU: not required for H-M2; set `CUDA_VISIBLE_DEVICES` if available but experiment is CPU-bound

### 6.2 Reproducibility

- Fixed random seed: `random_state=42` everywhere
- Bootstrap seed: `np.random.RandomState(42)` for all resampling

### 6.3 Reusability (H-E1 Components)

| Component | File | Usage in H-M2 |
|-----------|------|---------------|
| HH-RLHF loader | `h-e1/code/data_loader.py` | Import `load_hh_rlhf`, `stratify_rounds` |
| Feature extraction | `h-e1/code/features.py` | Import `build_feature_matrix` |
| Q_early model | `h-e1/code/q_early.py` | Import `QEarlyModel`; reuse/retrain on round-1 |
| Bootstrap CI | `h-e1/code/analysis.py` | Import `bootstrap_coefficient_ci` pattern |
| Visualization utilities | `h-e1/code/visualize.py` | Extend for coefficient comparison plots |

**Import paths (verified from actual H-M1 code using same convention):**
```python
import sys
sys.path.insert(0, "../h-e1/code")
from data_loader import load_hh_rlhf, stratify_rounds
from features import build_feature_matrix
from q_early import QEarlyModel
from analysis import bootstrap_coefficient_ci
```

---

## 7. Dependencies

### 7.1 Python Packages

**All inherited from H-E1 (already installed — no new packages needed):**

| Package | Version | Usage |
|---------|---------|-------|
| `scikit-learn` | ≥1.3.0 | `LogisticRegression`, `StandardScaler`, `train_test_split`, `roc_auc_score` |
| `numpy` | ≥1.24.0 | Bootstrap resampling, coefficient arrays |
| `scipy` | ≥1.10.0 | `chi2_contingency` for topic balance test |
| `pandas` | ≥2.0.0 | DataFrame operations for round stratification |
| `matplotlib` | ≥3.7.0 | Figure generation |
| `seaborn` | ≥0.12.0 | Distribution plots |
| `datasets` (HuggingFace) | ≥2.14.0 | HH-RLHF loading (already cached) |
| `pyyaml` | ≥6.0 | Results serialization |
| `tqdm` | ≥4.65.0 | Progress tracking |

**H-M2 requires NO new package installations.** All packages present from H-E1 + H-M1 environment.

### 7.2 External Repositories (Reference Only)

| Repository | Usage |
|-----------|-------|
| `Anthropic/hh-rlhf` (HuggingFace) | Primary dataset (already cached from H-E1) |
| `h-e1/code/` (local) | Reused pipeline modules |

---

## 8. Success Criteria

### 8.1 SHOULD_WORK Gate (PoC)

| Criterion | Requirement |
|-----------|-------------|
| Code executes end-to-end | No uncaught exceptions |
| Both models fit successfully | `early_clf.coef_` and `late_clf.coef_` are finite float arrays |
| Bootstrap CIs computed | `ci_early` and `ci_late` both shape (2, 3) with finite values |
| n_directional measurable | Integer in [0, 1, 2, 3] |
| **n_directional ≥ 2** | **Gate PASS: ≥ 2/3 coefficients have late > early with non-overlapping 95% CI** |

### 8.2 Scientific Success (PoC direction-based)

| Criterion | Target |
|-----------|--------|
| n_directional | ≥ 2 (PASS) / = 1 (PARTIAL / PIVOT) / = 0 (FAIL) |
| β_L_delta | > 0 (most likely signal, based on H-E1 β_L Bonferroni p=0.000) |
| β_H_delta, β_S_delta | > 0 (directional prediction) |
| Sign consistency | All 3 stylistic deltas positive |
| β_Q stability | |late_β_Q - early_β_Q| < 0.2 |
| Topic balance | Chi-square p > 0.05 |

### 8.3 Failure Response

| Condition | Action |
|-----------|--------|
| n_directional = 0 | PIVOT: sign inconsistency analysis; narrow H-M3 scope |
| n_directional = 1 | PARTIAL: document which feature shifts; continue to H-M3 with reduced scope |
| β_Q unstable (> 0.2 shift) | WARN: A2 assumption may be violated; document |
| Topic imbalance (p < 0.05) | WARN: coefficient differences may be topic-confounded |
| Round size < 40,000 | WARN: verify equal-partition logic |

---

## 9. File Structure

```
docs/youra_research/20260503_bi_align/h-m2/
├── code/
│   ├── config.py                 # H-M2 hyperparameters, paths, round stratification settings
│   ├── coefficient_comparison.py # NEW: round-stratified fitting, bootstrap CI, directional check
│   ├── run_experiment.py         # Main pipeline entry point
│   └── tests/
│       └── test_coefficient_comparison.py  # Unit tests for new module
├── figures/                      # 6 saved figures
├── results/
│   └── results.yaml              # Serialized experiment results
├── 02c_experiment_brief.md
├── 03_prd.md                     # This file
├── 03_architecture.md            # To be generated
├── 03_logic.md                   # To be generated
├── 03_config.md                  # To be generated
└── 03_tasks.yaml                 # To be generated
```

---

## 10. Ablation Variants

| Variant | Description | Implementation |
|---------|-------------|----------------|
| **Round-2 auxiliary model** | Fit round-2 model to check monotonic β trend (rounds 1→2→3) | `coefficient_comparison.py::fit_round_predictor(round_2_data)` |
| **Ordinal regression fallback** | If round stratification lacks signal, use ordinal regression with continuous round score | `coefficient_comparison.py::run_ordinal_regression()` |
| **Feature-specific pivot** | If n_directional < 2, report individual feature results; narrow H-M3 to features with confirmed shift | `coefficient_comparison.py::report_feature_pivot()` |
| **Shared scaler baseline** | Sensitivity check: refit with per-round scalers (vs. shared round-1 scaler) to assess scale normalization impact | `coefficient_comparison.py::run_per_round_scaler_check()` |
