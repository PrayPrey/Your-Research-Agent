# Product Requirements Document: h-e1

**Hypothesis:** Pairwise failure correlations across TrustfulQA, AdvBench, and BOLD benchmarks exceed random chance with statistical significance (Spearman r > 0.3, p < 0.01 after Bonferroni correction)

**Type:** EXISTENCE (PoC validation)
**Gate:** MUST_WORK (failure = ABANDON)
**Date:** 2026-08-28

---

## 1. Product Vision

### 1.1 Purpose
Validate foundation hypothesis that multi-dimensional trustworthiness failures show statistically significant correlations across benchmarks. Success enables investigation of shared failure mechanisms (H-M1-M4).

### 1.2 Success Metric
- Primary: ≥2 of 3 benchmark pairs show Spearman r > 0.3 AND p < 0.01 after Bonferroni correction
- Secondary: Correlations remain significant across all 3 size strata (small/medium/large)

### 1.3 Non-Goals
- Model training or fine-tuning (meta-analysis only)
- Causal mechanism investigation (deferred to H-M* hypotheses)
- New benchmark development (uses existing leaderboard data)

---

## 2. Functional Requirements

### 2.1 Data Collection Module
**Priority:** P0 (blocks all analysis)

**Requirements:**
- [FR-1] Collect benchmark scores for ≥15 models across 3 size strata:
  - Small (<1B): Phi-1.5, TinyLlama, Pythia-410M, GPT-2, OPT-350M
  - Medium (1-10B): LLaMA-7B, Mistral-7B, GPT-3.5-Turbo, Claude-Instant, Vicuna-7B
  - Large (>10B): GPT-4, Claude-2, LLaMA-70B, PaLM-2, Mixtral-8x7B
- [FR-2] Data sources:
  - TrustfulQA: Official leaderboard (github.com/sylinrl/TruthfulQA) + published papers
  - AdvBench: Model cards, safety reports, adversarial robustness papers
  - BOLD: BOLD benchmark publications and supplementary materials
- [FR-3] Output: CSV with columns [model_name, size_stratum, params_billions, truthfulqa_score, advbench_score, bold_score]
- [FR-4] Save to `./data/h-e1/benchmark_scores.csv`

**Validation:**
- Minimum 15 models (5 per stratum)
- All 3 benchmark scores present for each model
- Scores in [0,1] range after normalization

### 2.2 Preprocessing Module
**Priority:** P0 (blocks correlation analysis)

**Requirements:**
- [FR-5] Normalize all benchmark scores to [0,1] scale
- [FR-6] Handle missing values via listwise deletion
- [FR-7] Stratify models by parameter count (<1B, 1-10B, >10B)
- [FR-8] Validate data integrity (no NaN values post-cleaning)

**Output:**
- Cleaned DataFrame ready for correlation analysis
- Data quality report (missing value counts, final sample size per stratum)

### 2.3 Correlation Analysis Module
**Priority:** P0 (core hypothesis test)

**Requirements:**
- [FR-9] Compute pairwise Spearman correlations for 3 benchmark pairs:
  - TrustfulQA ↔ AdvBench
  - TrustfulQA ↔ BOLD
  - AdvBench ↔ BOLD
- [FR-10] Calculate p-values for each correlation
- [FR-11] Apply Bonferroni correction for 3 comparisons (α = 0.01 → α_corrected = 0.0033)
- [FR-12] Report effect sizes (Spearman r values) for significant pairs

**Implementation:**
```python
from scipy.stats import spearmanr
from statsmodels.stats.multitest import multipletests

# Core analysis logic
correlations = {}
for bench1, bench2 in benchmark_pairs:
    r, p = spearmanr(df[bench1], df[bench2])
    correlations[(bench1, bench2)] = (r, p)

# Bonferroni correction
reject, pvals_corrected, _, _ = multipletests(pvals, method='bonferroni')
```

**Validation:**
- All 3 pairs computed
- Bonferroni correction applied correctly
- Results logged to `./results/h-e1/correlation_results.json`

### 2.4 Stratified Analysis Module
**Priority:** P1 (validates scale invariance)

**Requirements:**
- [FR-13] Repeat correlation analysis within each size stratum
- [FR-14] Compare correlation strengths across strata
- [FR-15] Test whether correlations generalize beyond single scale

**Output:**
- Per-stratum correlation matrices
- Cross-stratum comparison report

### 2.5 Visualization Module
**Priority:** P1 (required for interpretation)

**Requirements:**
- [FR-16] Correlation matrix heatmap (3×3, annotated with r and p-values)
- [FR-17] Scatter plots for each benchmark pair with fitted regression lines
- [FR-18] Stratified correlation comparison bar chart
- [FR-19] Gate metrics comparison chart (target vs actual)
- [FR-20] Save all figures to `./figures/h-e1/`

**Acceptance Criteria:**
- All visualizations generated without errors
- Figures use consistent color scheme
- Annotations include statistical significance markers (* for p < 0.01)

---

## 3. Non-Functional Requirements

### 3.1 Performance
- [NFR-1] Data collection: ≤2 days manual effort
- [NFR-2] Analysis runtime: ≤5 minutes on standard laptop
- [NFR-3] Memory footprint: <100MB (small dataset)

### 3.2 Reproducibility
- [NFR-4] All code deterministic (no randomness in Spearman correlation)
- [NFR-5] Results reproducible given same input CSV
- [NFR-6] Version all dependencies (scipy, statsmodels, pandas)

### 3.3 Robustness
- [NFR-7] Handle missing benchmark scores gracefully (listwise deletion + warning)
- [NFR-8] Validate input data schema before analysis
- [NFR-9] Log all intermediate outputs for debugging

### 3.4 Maintainability
- [NFR-10] Modular code structure (separate modules for data, analysis, viz)
- [NFR-11] Type hints for all public functions
- [NFR-12] Inline comments for statistical formulas

---

## 4. Implementation Constraints

### 4.1 Data Constraints
- No synthetic data (violates 02_roadmap.md synthetic data policy)
- Must use publicly available benchmark results only
- Cannot run new benchmark evaluations (resource constraint)

### 4.2 Technical Constraints
- Python 3.8+ with scipy, statsmodels, pandas, matplotlib, seaborn
- No proprietary tools or APIs
- Must run on single CPU (no GPU required)

### 4.3 Time Constraints
- Total effort: ≤1 week including data collection
- Data collection: 1-2 days
- Implementation + analysis: 2-3 days
- Visualization + reporting: 1-2 days

---

## 5. Acceptance Criteria

### 5.1 PoC Pass Criteria
1. ✅ Code runs without errors
2. ✅ At least 1 benchmark pair shows Spearman r > 0.3 AND p < 0.01 after Bonferroni

### 5.2 Full Success Criteria
1. ✅ At least 2 of 3 benchmark pairs meet significance threshold
2. ✅ Correlations remain significant in at least 2 of 3 size strata
3. ✅ All required visualizations generated
4. ✅ Results documented in `04_validation.md`

### 5.3 Gate Decision
- **PASS**: Success criteria met → Continue to H-M1-M4 mechanism hypotheses
- **FAIL**: Abandon hypothesis chain (core assumption violated)

---

## 6. Deliverables

### 6.1 Code Artifacts
- `data_collection.py`: Benchmark aggregation script
- `preprocessing.py`: Data cleaning and normalization
- `correlation_analysis.py`: Core statistical analysis
- `visualizations.py`: Figure generation
- `benchmark_scores.csv`: Raw data (./data/h-e1/)
- `requirements.txt`: Python dependencies

### 6.2 Output Artifacts
- `correlation_results.json`: Numerical results (./results/h-e1/)
- `figures/`: All visualizations (./figures/h-e1/)
- `04_validation.md`: Final validation report

### 6.3 Documentation
- README.md: Usage instructions
- Data provenance log: Sources for each benchmark score

---

## 7. Risks and Mitigations

### 7.1 Data Availability Risk
**Risk:** Insufficient public benchmark results (<15 models)
**Mitigation:** Expand search to ArXiv preprints, model cards, leaderboards
**Contingency:** Lower sample size to 12 models (4 per stratum) with reduced power

### 7.2 Missing Data Risk
**Risk:** Models missing scores for 1+ benchmarks
**Mitigation:** Listwise deletion + expand candidate pool to 25+ models
**Contingency:** Accept 10 complete models if 15 unattainable

### 7.3 Statistical Power Risk
**Risk:** Small sample size → insufficient power to detect r = 0.3
**Mitigation:** Power analysis suggests n=15 adequate for r=0.3, α=0.01, power=0.80
**Contingency:** Report confidence intervals, acknowledge low-power limitation

---

## 8. Open Questions

### 8.1 Resolved
- Q: Use Pearson or Spearman correlation?
  - A: Spearman (handles non-linear monotonic relationships, robust to outliers)
- Q: Permutation test or parametric test?
  - A: Spearman's built-in p-value (asymptotic) sufficient for n≥15
- Q: Multiple comparison correction method?
  - A: Bonferroni (conservative, appropriate for 3 comparisons)

### 8.2 Pending Resolution in Phase 4
- Q: Exact model list (depends on data availability during collection)
- Q: Fallback if <15 models found (accept lower power or abandon?)

---

## 9. Dependencies

### 9.1 External Dependencies
- Python libraries: scipy, statsmodels, pandas, matplotlib, seaborn
- Public benchmark leaderboards: TrustfulQA, AdvBench, BOLD
- Published papers for supplementary benchmark data

### 9.2 Internal Dependencies
- Phase 2C experiment brief (02c_experiment_brief.md) → defines specification
- verification_state.yaml → tracks gate status

---

## 10. Appendix

### 10.1 Reference Materials
- Experiment Brief: `./02c_experiment_brief.md`
- Hypothesis Context: `./02b_context.md`
- Verification Plan: `../02b_verification_plan.md`

### 10.2 Glossary
- **Spearman r**: Rank correlation coefficient, measures monotonic relationship strength
- **Bonferroni correction**: Conservative multiple comparison adjustment (α_corrected = α / n_tests)
- **Listwise deletion**: Remove entire row if any value missing
- **Effect size**: r > 0.3 considered "medium" by Cohen's conventions

---

*Generated by Phase 3 PRD Agent*
*Next: Architecture Design (03_architecture.md)*
