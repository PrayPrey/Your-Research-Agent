# Product Requirements Document: H-M1 Feature-Ranking Correlation Analysis

**Date:** 2026-07-13
**Author:** Anonymous
**Hypothesis:** H-M1 - Dataset characteristics (sample size, dimensionality, signal properties) determine which method families have structural advantages.
**Type:** MECHANISM
**Gate:** SHOULD_WORK (ρ > 0.3, p < 0.05)

---

## Executive Summary

### Problem Statement
Test whether dataset characteristics correlate with method family performance rankings. This validates the causal mechanism underlying meta-method selection: if no correlation exists, the meta-classifier cannot learn meaningful patterns.

### Solution Overview
Compute Tier 1+2 dataset features for 63 benchmarks (from H-E1) and measure Spearman correlation with method family rankings. Success requires ≥3 significant correlations (ρ > 0.3, p < 0.05).

### Success Criteria
- **Primary Gate (SHOULD_WORK):** Feature-ranking correlation ρ > 0.3, p < 0.05 for ≥3 feature-method pairs
- **Secondary:** No significant inverse correlations (ρ < -0.3)
- **Validation:** Statistical significance p < 0.05 for all reported correlations

---

## Functional Requirements

### FR1: Dataset Feature Computation
**Priority:** P0 (Critical Path)

**Description:** Compute Tier 1 (universal) and Tier 2 (domain-specific) features for all 63 benchmarks from H-E1 collection.

**Tier 1 Features (Universal):**
- `sample_size`: Total number of samples in dataset
- `dimensionality`: Feature count (tabular) or input dimensions (images/sequences)
- `num_classes`: Number of target classes
- `class_imbalance`: Gini coefficient of class distribution

**Tier 2 Features (Domain-Specific):**
- **Vision:** `image_resolution`, `channel_count`
- **NLP:** `sequence_length`, `vocabulary_size`
- **Tabular:** `feature_variance`, `categorical_ratio`
- **Graph:** `edge_density`, `avg_degree`

**Inputs:** `./data/h-e1/collected_benchmarks.json` (63 benchmarks with metadata)

**Outputs:** `features_df` (63 × ~10 features, pandas DataFrame)

**Acceptance Criteria:**
- All 63 benchmarks have complete Tier 1 features
- Domain-specific Tier 2 features computed for matching benchmarks
- Feature computation completes in <1 minute per benchmark
- No missing values in output DataFrame

---

### FR2: Method Rankings Extraction
**Priority:** P0 (Critical Path)

**Description:** Extract method family rankings from H-E1 benchmark collection and convert to percentile format.

**Method Families:**
- Linear/Polynomial methods
- RNN-based methods
- Augmentation-based methods
- Ensemble methods

**Inputs:** `./data/h-e1/collected_benchmarks.json`

**Outputs:** `rankings_df` (63 × 4 method families, percentile values 0-100)

**Acceptance Criteria:**
- All 63 benchmarks have rankings for ≥3 method families
- Rankings are percentile-normalized (0 = worst, 100 = best)
- Missing methods handled gracefully (NaN or exclusion)

---

### FR3: Spearman Correlation Analysis
**Priority:** P0 (Critical Path)

**Description:** Compute Spearman correlation coefficient (ρ) and p-value for all (feature, method_family) pairs.

**Algorithm:**
```python
from scipy.stats import spearmanr

for feature in features_df.columns:
    for method in rankings_df.columns:
        rho, p_value = spearmanr(features_df[feature], rankings_df[method])
        significant = (abs(rho) > 0.3) and (p_value < 0.05)
```

**Inputs:**
- `features_df`: (63, ~10) feature matrix
- `rankings_df`: (63, 4) method ranking matrix

**Outputs:** `correlations_dict` with structure:
```python
{
    "feature_vs_method": {
        "rho": float,
        "p_value": float,
        "significant": bool
    }
}
```

**Acceptance Criteria:**
- All valid (feature, method) pairs analyzed
- Spearman ρ reported with 3 decimal precision
- p-values computed using two-tailed test
- Significant pairs flagged (ρ > 0.3 AND p < 0.05)

---

### FR4: Result Aggregation and Reporting
**Priority:** P0 (Critical Path)

**Description:** Count significant correlations, identify strongest pairs, and check for inverse correlations.

**Outputs:**
- Total significant pairs count
- Top 5 strongest positive correlations (sorted by |ρ|)
- List of inverse correlations (ρ < -0.3, p < 0.05) if any
- Summary statistics (mean ρ, median p-value)

**Gate Decision Logic:**
```python
significant_count = sum(1 for r in results.values() if r['significant'])

if significant_count >= 3:
    gate_result = "PASS"
elif significant_count >= 1:
    gate_result = "PARTIAL"  # Some correlation, but weak
else:
    gate_result = "FAIL"  # No correlation found
```

**Acceptance Criteria:**
- Gate decision automatically determined
- All results saved to `04_validation.md`
- Inverse correlations flagged as warnings

---

### FR5: Visualization Generation
**Priority:** P1 (Required for validation report)

**Description:** Generate 4 figures for validation report.

**Figure 1 (Mandatory):** Gate Metrics Comparison
- Bar chart: correlation strength (ρ) vs threshold (0.3)
- Shows top 5 feature-method pairs
- Threshold line at ρ = 0.3

**Figure 2:** Feature-Method Correlation Heatmap
- Rows: Features
- Columns: Method families
- Color: ρ value (-1 to +1)

**Figure 3:** Significance Plot
- Bar chart of p-values for top 10 pairs
- Threshold line at p = 0.05

**Figure 4:** Top 3 Scatter Plots
- X-axis: Feature values
- Y-axis: Method ranking percentile
- Regression line with Spearman ρ annotation

**Outputs:** All figures saved to `./docs/youra_research/h-m1/figures/`

**Acceptance Criteria:**
- All figures use consistent styling
- Axes labeled with units
- Legends included where needed
- High resolution (300 DPI) PNG format

---

## Non-Functional Requirements

### NFR1: Performance
- Feature computation: <1 min per benchmark (total ~63 min)
- Correlation analysis: <5 seconds for all pairs
- Total execution time: <90 minutes

### NFR2: Reproducibility
- All random seeds fixed (not applicable - deterministic correlation)
- Feature computation order deterministic (alphabetical by benchmark ID)
- Results bit-exact across runs

### NFR3: Data Quality
- Feature values validated (no NaN, no infinite values)
- Rankings validated (0-100 range, no negatives)
- Correlation results checked for numerical stability

### NFR4: Logging
- Feature computation progress logged per benchmark
- Correlation computation progress logged per feature
- All significant pairs logged with details

---

## Data Specifications

### Input Data

**File:** `./data/h-e1/collected_benchmarks.json`

**Format:**
```json
{
    "benchmarks": [
        {
            "id": "benchmark_001",
            "name": "CIFAR-10",
            "domain": "Vision",
            "sample_size": 60000,
            "dimensionality": [32, 32, 3],
            "num_classes": 10,
            "method_rankings": {
                "Linear": 45,
                "RNN": 78,
                "Augmentation": 92,
                "Ensemble": 88
            }
        }
    ]
}
```

**Validation Rules:**
- `sample_size` > 0
- `num_classes` ≥ 2
- `method_rankings` values in [0, 100]

### Output Data

**File 1:** `features.csv`
- Rows: 63 benchmarks
- Columns: ~10 features (Tier 1 + Tier 2)
- Format: CSV with header

**File 2:** `correlations.json`
- Structure: `{feature_vs_method: {rho, p_value, significant}}`
- Format: JSON with 3 decimal precision

**File 3:** `04_validation.md`
- Structured validation report (see FR4)
- Includes gate decision, figures, summary statistics

---

## Dependencies

### External Libraries
- **scipy** (>=1.7.0): `spearmanr` correlation computation
- **pandas** (>=1.3.0): DataFrame operations, feature storage
- **numpy** (>=1.21.0): Numerical computations
- **matplotlib** (>=3.4.0): Figure generation
- **seaborn** (>=0.11.0): Heatmap visualization

### Internal Dependencies
- **H-E1 Output:** `./data/h-e1/collected_benchmarks.json` (MUST exist)
- **Verification State:** Read `verification_state.yaml` for H-E1 completion status

### Environment Requirements
- Python 3.8+
- 8GB RAM (for full dataset in memory)
- No GPU required (CPU-only correlation analysis)

---

## Evaluation Metrics

### Primary Metrics
1. **Feature-Ranking Correlation (ρ):** Spearman correlation coefficient
   - Target: ≥3 pairs with ρ > 0.3
   - Range: [-1, 1]
   - Interpretation: 0.3+ = moderate correlation, 0.5+ = strong

2. **Statistical Significance (p):** Two-tailed p-value
   - Target: p < 0.05 for all reported pairs
   - Interpretation: p < 0.05 = statistically significant

3. **Significant Pair Count:** Number of (feature, method) pairs passing both thresholds
   - Target: ≥3 pairs
   - Gate: PASS if ≥3, PARTIAL if 1-2, FAIL if 0

### Secondary Metrics
4. **Mean Absolute Correlation:** Average |ρ| across all pairs
   - Diagnostic: Overall correlation strength
   - Expected: >0.15 for meaningful patterns

5. **Inverse Correlation Count:** Pairs with ρ < -0.3, p < 0.05
   - Target: 0 (inverse correlations suggest mechanism failure)
   - Action: If >0, investigate feature computation errors

---

## Success Criteria

### Gate Condition (SHOULD_WORK)
✅ **PASS:** ≥3 significant correlations (ρ > 0.3, p < 0.05)
⚠️ **PARTIAL:** 1-2 significant correlations → Explore Tier 3 features or simpler model
❌ **FAIL:** 0 significant correlations → Mechanism hypothesis invalid

### Quality Checks
- No significant inverse correlations (ρ < -0.3)
- Mean |ρ| > 0.15 across all pairs
- Feature computation completes without errors
- All 63 benchmarks successfully analyzed

### Validation Report Requirements
- Gate decision clearly stated
- All significant pairs listed with (feature, method, ρ, p)
- Figures show visual evidence of correlations
- Summary statistics table included

---

## Risk Assessment

### Technical Risks
1. **Insufficient correlation strength:** ρ values may be below 0.3
   - Mitigation: PARTIAL gate allows exploration of Tier 3 features
   - Fallback: Re-run H-M1 with expanded feature set

2. **Domain-specific features incomplete:** Some benchmarks may lack Tier 2 data
   - Mitigation: Use only Tier 1 features for incomplete benchmarks
   - Impact: May reduce correlation strength for those benchmarks

3. **Sparse method rankings:** Some benchmarks may have <3 method families
   - Mitigation: Exclude pairs with insufficient data
   - Impact: Reduces total pairs analyzed

### Methodological Risks
1. **Spurious correlations:** Random chance may produce false positives
   - Mitigation: p < 0.05 threshold controls false positive rate
   - Validation: Bonferroni correction if >30 pairs tested

2. **Non-linear relationships:** Spearman may miss non-monotonic patterns
   - Mitigation: SHOULD_WORK gate allows alternative approaches
   - Future: Consider Kendall τ or mutual information (H-M2)

---

## Appendix: Traceability

### Phase 2C Mapping
| Phase 2C Section | PRD Section |
|------------------|-------------|
| Dataset Specification | FR1: Feature Computation |
| Models (Baseline + Proposed) | FR3: Correlation Analysis |
| Evaluation Metrics | Evaluation Metrics section |
| Success Criteria | Gate Condition |
| Visualization Requirements | FR5: Visualization |

### Hypothesis Chain
- **H-E1 (COMPLETED):** Collected 63 benchmarks → Used as input for H-M1
- **H-M1 (CURRENT):** Test correlation → Enables H-M2 (meta-classifier training)
- **H-M2 (FUTURE):** Train Random Forest → Uses H-M1 validated features

---

**Document Status:** COMPLETE
**Next Phase:** Phase 3 Step 3 - Architecture Design
