# Product Requirements Document (PRD)
# H-E1: Temporal Stylistic Coefficient Drift in RLHF Annotation

**Generated:** 2026-05-03
**Phase:** 3 - Implementation Planning
**Hypothesis:** H-E1 (EXISTENCE / FOUNDATION / MUST_WORK)
**Tier:** LIGHT (max 15 tasks)
**Author:** Anonymous
---

## 1. Executive Summary

This PRD specifies the implementation requirements for H-E1, the foundational existence test of the Human→AI Annotation Drift pipeline. The experiment measures whether stylistic preference coefficients (β_L: verbosity, β_H: hedging, β_S: structured reasoning) exhibit statistically significant directional drift across annotation rounds in the Anthropic HH-RLHF dataset, after controlling for response quality (Q_early covariate). A positive result (MUST_WORK gate) unlocks the downstream mechanism chain H-M1 through H-M4.

**Core Question:** Do RLHF annotators progressively weight AI-typical stylistic features more heavily across annotation rounds, consistent with automation bias?

---

## 2. Problem Statement

### 2.1 Research Gap

No prior work directly measures per-round coefficient drift in RLHF preference datasets. Existing methods (reward model ensembles, LLM-as-judge evaluations) address annotation variance globally but cannot detect directional temporally-structured drift. The Alignment Asymmetry Index (AAI) requires empirical validation of its first component: existence of stylistic drift in annotation labels.

### 2.2 Hypothesis

Under conditions where HH-RLHF annotation rounds represent genuine temporal exposure strata, if stylistic preference coefficients (β_L, β_H, β_S) are estimated per round via logistic regression with Q_early covariate, then the coefficients exhibit statistically significant directional drift across rounds (increasing weights on verbosity, hedging, structured reasoning), particularly in high-annotator-disagreement prompts.

### 2.3 Gate Condition

MUST_WORK: If drift is absent after Q_early recalibration, downstream hypotheses H-M1 through H-M4 are blocked.

---

## 3. Scope

### 3.1 In Scope
- Round stratification of Anthropic HH-RLHF (~169K comparisons into 3 rounds)
- Stylistic feature extraction (verbosity, hedging, structured reasoning) from chosen/rejected response texts
- Q_early logistic regression training on round-1 + affine recalibration for rounds 2-3
- Round-conditioned logistic regression with Q_early covariate and round × ambiguity interaction term
- Fleiss κ computation for high-ambiguity prompt partitioning
- Bootstrap 95% CI on coefficient differences across rounds
- Placebo permutation test (1000 permutations)
- Secondary validation on OpenAI WebGPT Comparisons (within-annotator dose-response)
- Visualization: 5 figures (coefficient drift, ambiguity stratification, Q_early calibration, placebo, feature correlation)

### 3.2 Out of Scope
- Neural network training (H-E1 is statistical analysis only)
- Reward model training (H-M3 scope)
- RLHF fine-tuning (H-M4 scope)
- Causal inference (H-M1/H-M2 scope)

---

## 4. Data Specification

### 4.1 Primary Dataset: Anthropic HH-RLHF

| Field | Value |
|-------|-------|
| Name | Anthropic HH-RLHF (Human Feedback) |
| Source | HuggingFace Hub: `Anthropic/hh-rlhf` |
| Scale | ~169,000 pairwise preference comparisons |
| Round Structure | 3 annotation rounds (round-1 ~56K, round-2 ~56K, round-3 ~57K) |
| Fields | `chosen` (preferred response), `rejected` (non-preferred response) |
| Download | `load_dataset("Anthropic/hh-rlhf")` — **auto-download via HuggingFace** |
| Cache | `~/.cache/huggingface/datasets/` |
| License | Apache 2.0 |

**Round Metadata Note:** Round stratification must be derived from HH-RLHF dataset split structure. Verify metadata field availability before running (pre-condition: ≥ 80% of comparisons have non-null round indicator).

### 4.2 Secondary Dataset: OpenAI WebGPT Comparisons

| Field | Value |
|-------|-------|
| Name | OpenAI WebGPT Comparisons |
| Source | HuggingFace Hub: `openai/webgpt_comparisons` |
| Scale | ~19,578 comparisons |
| Fields | `question`, `answer_0`, `answer_1`, `preferred`, worker metadata |
| Download | `load_dataset("openai/webgpt_comparisons")` — **auto-download via HuggingFace** |
| Cache | `~/.cache/huggingface/datasets/` |
| License | MIT |

**Both datasets auto-download via HuggingFace datasets API. No manual download required.**

### 4.3 Preprocessing Requirements

- Round-1 subset: minimum 10,000 examples for Q_early training
- High-ambiguity subset: minimum 500 examples (κ < 0.4)
- Feature standardization: zero mean, unit variance (StandardScaler per round)
- VIF check: ensure VIF(β_L, β_H, β_S) < 10 before regression

---

## 5. Functional Requirements

### FR-1: Data Loading and Round Stratification
- Load full HH-RLHF dataset via HuggingFace datasets API
- Partition into round-1, round-2, round-3 strata using annotation phase metadata
- Verify round metadata availability (≥ 80% non-null)
- Load WebGPT comparisons for secondary validation

### FR-2: Stylistic Feature Extraction
- Extract three stylistic features per response text:
  - β_L (verbosity): token/word count
  - β_H (hedging): count of hedging phrases (["might", "may", "could", "perhaps", "possibly", "I think"])
  - β_S (structured reasoning): count of structure markers (["\n-", "\n*", "1.", "2.", "##", "**"])
- Apply StandardScaler normalization per round
- Check VIF among features; warn if VIF > 10

### FR-3: Q_early Calibration (Go/No-Go Gate)
- Train logistic regression on round-1 preference labels (Q_early model)
  - Config: `C=1.0, max_iter=1000, solver='lbfgs', class_weight='balanced', random_state=42`
- Apply affine recalibration (Platt scaling via CalibratedClassifierCV) to rounds 2-3
- Compute Brier score for each round; verify difference < 0.02
- **Gate:** If Brier score difference ≥ 0.02, halt experiment and report calibration failure

### FR-4: Round-Conditioned Regression with Interaction Term
- For each round (1, 2, 3): fit logistic regression with:
  - Features: [β_L_z, β_H_z, β_S_z, Q_early_score]
  - Config: `C=1.0, max_iter=1000, solver='lbfgs', random_state=42`
- Extract per-round coefficients [β_L, β_H, β_S] (excluding Q_early coefficient)
- Fit pooled model with round × high_ambiguity interaction term using statsmodels

### FR-5: Fleiss κ Ambiguity Partitioning
- Compute Fleiss κ per prompt using multi-rater labels from HH-RLHF metadata
  - Requires per-prompt annotator counts ≥ 2
  - Library: `statsmodels.stats.inter_rater.fleiss_kappa`
- Partition prompts: high-ambiguity (κ < 0.4) vs. low-ambiguity (κ ≥ 0.4)
- Minimum 500 high-ambiguity samples required

### FR-6: Statistical Testing (Primary Metrics)
- Bootstrap 95% CI on coefficient differences (1000 iterations, scipy.stats.bootstrap)
- Bonferroni correction: α = 0.05 / 3 = 0.0167 for 3 primary tests (β_L, β_H, β_S)
- Test interaction term round × high_ambiguity significance (p < 0.0167)
- Test coefficient direction: β_x_r3 > β_x_r1 for x in {L, H, S}

### FR-7: Placebo Permutation Test
- Permute round labels within matched prompt groups (1000 permutations)
- Verify coefficient drift disappears under permutation (specificity check)
- Report empirical p-value for permutation test

### FR-8: Secondary Validation (WebGPT Dose-Response)
- Use worker IDs and timestamps from WebGPT for within-annotator fixed effects
- Compute cumulative AI-text exposure proxy from timestamps
- Run dose-response regression: preference ~ stylistic_features + exposure_dose

### FR-9: Visualization
| Figure | Description |
|--------|-------------|
| gate_metrics_comparison | Bar chart: interaction p-value vs 0.0167 threshold; Brier diff vs 0.02 gate |
| coefficient_drift | Line plot of β_L, β_H, β_S across rounds 1-2-3 with bootstrap 95% CI bands |
| ambiguity_stratification | Side-by-side coefficient drift for high-ambiguity vs low-ambiguity strata |
| q_early_calibration | Reliability diagrams for rounds 1, 2, 3 (predicted probability vs actual) |
| placebo_distribution | Histogram of permuted-round coefficient differences with observed value marked |
| feature_correlation | VIF / correlation matrix heatmap for β_L, β_H, β_S features |

Save all figures to: `docs/youra_research/20260503_bi_align/h-e1/figures/`

### FR-10: Baseline Comparison (Round-Pooled Model)
- Implement round-pooled logistic regression baseline (all rounds combined, no temporal stratification)
- Compare β coefficients between pooled vs. round-stratified models
- Report accuracy (~65-70% expected for pairwise preference task)

---

## 6. Non-Functional Requirements (NFRs)

### NFR-1: Reproducibility
- Fixed random seeds: `random_state=42` for all sklearn models
- Fixed bootstrap seed: `random_state=42`
- All results reproducible with identical seeds

### NFR-2: Statistical Rigor
- Bootstrap CI with 1000 iterations (not asymptotic approximation)
- Bonferroni correction applied for all 3 primary coefficient tests
- Placebo test for specificity verification

### NFR-3: Performance
- Wall-clock target: ≤ 4 hours on single GPU (CPU-only acceptable; 169K examples)
- Memory: ≤ 16 GB RAM for full dataset processing

### NFR-4: Code Quality
- Python 3.9+
- pytest test coverage for all modules
- Logging via Python logging module (INFO level default)
- Results saved to YAML/JSON for downstream consumption

### NFR-5: Experiment Scale
- Full HH-RLHF dataset (169K) — no arbitrary subsampling
- Full WebGPT dataset (19,578) for secondary validation
- Bootstrap: 1000 iterations minimum

---

## 7. Dependencies

### 7.1 Python Packages

```
# Core
python>=3.9
numpy>=1.24.0
scipy>=1.10.0
pandas>=1.5.0

# Machine Learning
scikit-learn>=1.2.0
statsmodels>=0.14.0

# NLP / Datasets
datasets>=2.14.0  # HuggingFace datasets API
transformers>=4.30.0  # tokenization utilities
sentence-transformers>=2.2.2  # all-MiniLM-L6-v2 for AI-typicality embedding (FR-8)

# Visualization
matplotlib>=3.7.0
seaborn>=0.12.0

# Testing
pytest>=7.3.0
pytest-cov>=4.0.0

# Utilities
pyyaml>=6.0
tqdm>=4.65.0
```

### 7.2 External Repositories (Reference Only)
- `huggingface/trl` — RewardTrainer reference (relevant for H-M3/H-M4 downstream)
- `EleutherAI/lm-evaluation-harness` — benchmark harness (relevant for H-M4)

### 7.3 Hardware
- Single GPU (CUDA_VISIBLE_DEVICES set to lowest-memory GPU)
- Minimum 16 GB RAM
- 50 GB disk space (HH-RLHF + WebGPT cache)

---

## 8. Success Criteria (PoC Gate)

### 8.1 PoC PASS Conditions (ALL required for MUST_WORK gate)
1. Code runs without error (data loads, features extracted, regression fits)
2. Q_early calibration gate passes: Brier score difference < 0.02 across rounds
3. `interaction_p_value < 0.0167` (Bonferroni-corrected α)
4. `β_drift_direction == "positive"` for ≥ 2/3 stylistic features (β_L, β_H, β_S)

### 8.2 PoC FAIL Conditions
- Q_early gate fails (Brier diff ≥ 0.02) → halt, pivot to alternative quality control
- No directional drift (interaction non-significant) → explore WebGPT dose-response before abandoning

### 8.3 Secondary Success Indicators
- Bootstrap 95% CIs non-overlapping between round-1 and round-3 coefficients
- Placebo test shows no significant drift under permuted round labels
- Effect size (Cohen's d) > 0.2 for at least one stylistic coefficient

---

## 9. Evaluation Metrics Summary

| Metric | Target | Type |
|--------|--------|------|
| Interaction term p-value | < 0.0167 | Primary |
| β_drift_direction | positive for ≥ 2/3 | Primary |
| Brier score difference (Q_early gate) | < 0.02 | Go/No-Go |
| Bootstrap 95% CI overlap | Non-overlapping r1 vs r3 | Secondary |
| Placebo permutation p-value | > 0.05 (null holds) | Secondary |
| Cohen's d for coefficient change | > 0.2 | Secondary |
| Round-pooled baseline accuracy | ~65-70% | Baseline |

---

## 10. File Organization

```
docs/youra_research/20260503_bi_align/h-e1/
├── 02b_context.md            # Phase 2B context
├── 02c_experiment_brief.md   # Phase 2C experiment design
├── 03_prd.md                 # This document
├── 03_architecture.md        # Phase 3 architecture
├── 03_logic.md               # Phase 3 API/logic design
├── 03_config.md              # Phase 3 configuration
├── 03_tasks.yaml             # Phase 4 implementation tasks
├── code/                     # Phase 4 implementation
│   ├── data/
│   ├── features/
│   ├── models/
│   ├── analysis/
│   ├── visualization/
│   └── tests/
└── figures/                  # Experiment output figures
```

---

## 11. Traceability

| Requirement | Source |
|-------------|--------|
| Round stratification (FR-1) | 02c_experiment_brief.md §Dataset |
| Feature extraction (FR-2) | 02c_experiment_brief.md §Proposed Model |
| Q_early calibration (FR-3) | 02c_experiment_brief.md §Training Protocol |
| Interaction regression (FR-4) | 02c_experiment_brief.md §Evaluation |
| Fleiss κ (FR-5) | 02b_context.md §Verification Protocol step 4 |
| Statistical testing (FR-6) | 02c_experiment_brief.md §Training Protocol |
| Placebo test (FR-7) | 02b_context.md §Verification Protocol step 5 |
| WebGPT secondary (FR-8) | 02c_experiment_brief.md §Secondary Dataset |
| Figures (FR-9) | 02c_experiment_brief.md §Visualization |
| Baseline comparison (FR-10) | 02b_context.md §Baseline & Comparison Targets |

---

*Generated by Phase 3 Implementation Planning (inline execution, no-MCP TEST environment)*
*Source: 02c_experiment_brief.md + 02b_context.md*
*Next: 03_architecture.md (Architecture Agent)*
