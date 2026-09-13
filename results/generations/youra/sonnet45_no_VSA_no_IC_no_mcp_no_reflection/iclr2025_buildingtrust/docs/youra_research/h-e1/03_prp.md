# Phase 4 Requirement Package: h-e1

**Hypothesis:** Pairwise failure correlations across TrustfulQA, AdvBench, and BOLD benchmarks exceed random chance with statistical significance (Spearman r > 0.3, p < 0.01 after Bonferroni correction)

**Implementation Tier:** Tier 1 (20-40 subtasks, ≤10 epics, minimal-medium complexity)
**Total Complexity:** 30
**Date:** 2026-08-28

---

## Epic Breakdown

### Epic E1: Data Collection (Complexity 8)
**Objective:** Manually aggregate benchmark scores for ≥15 models across 3 size strata

**Subtasks:**
- E1.1: Setup data directory structure (`./data/h-e1/`)
- E1.2: Scrape TrustfulQA benchmark scores (5 models per stratum)
- E1.3: Aggregate AdvBench scores from model cards and safety reports
- E1.4: Collect BOLD bias metrics from publications
- E1.5: Validate CSV schema (6 columns, ≥15 rows, no empty cells)

**Validation:** CSV with columns [model_name, size_stratum, params_billions, truthfulqa_score, advbench_score, bold_score]

---

### Epic E2: Preprocessing Pipeline (Complexity 6)
**Objective:** Normalize scores, handle missing values, stratify by model size

**Subtasks:**
- E2.1: Implement score normalization to [0,1] range
- E2.2: Handle missing values via listwise deletion
- E2.3: Stratify models by parameter count (<1B, 1-10B, >10B)
- E2.4: Validate preprocessed data integrity (no NaN, all scores in [0,1])

**Validation:** Cleaned DataFrame ready for correlation analysis

---

### Epic E3: Correlation Analysis (Complexity 9)
**Objective:** Compute Spearman correlations with Bonferroni correction

**Subtasks:**
- E3.1: Implement FailureCorrelationAnalyzer class (03_logic.md API)
- E3.2: Compute pairwise Spearman correlations for 3 benchmark pairs
- E3.3: Apply Bonferroni correction (α = 0.01 → α_corrected = 0.0033)
- E3.4: Implement stratified analysis (per size stratum)
- E3.5: Save correlation results to JSON (`./results/h-e1/correlation_results.json`)

**Validation:** 3 correlation pairs computed, Bonferroni applied, results logged

---

### Epic E4: Visualization (Complexity 7)
**Objective:** Generate 4 required figures for interpretation

**Subtasks:**
- E4.1: Generate correlation matrix heatmap (3×3, annotated with r and p-values)
- E4.2: Create scatter plots for each benchmark pair (3 plots with regression lines)
- E4.3: Plot stratified correlation comparison (bar chart across size strata)
- E4.4: Generate gate metrics comparison (target vs actual)
- E4.5: Validate all figures saved to `./figures/h-e1/`

**Validation:** 4 PNG files generated without errors

---

## Infrastructure Tasks

### I1: Dependency Management
- Create `requirements.txt` with scipy, statsmodels, pandas, matplotlib, seaborn
- Specify minimum versions (scipy>=1.7.0, statsmodels>=0.13.0, etc.)

### I2: Orchestration
- Implement `main.py` to coordinate:
  1. Load data from CSV
  2. Preprocess
  3. Analyze correlations
  4. Generate visualizations
  5. Save results

### I3: Documentation
- Write README.md with:
  - Data collection instructions
  - Usage: `python main.py`
  - Output file locations
  - Interpretation of results

---

## Task Summary

| Epic | Subtasks | Complexity | Status |
|------|----------|------------|--------|
| E1: Data Collection | 5 | 8 | Pending |
| E2: Preprocessing | 4 | 6 | Pending |
| E3: Correlation Analysis | 5 | 9 | Pending |
| E4: Visualization | 5 | 7 | Pending |
| Infrastructure | 3 | - | Pending |
| **TOTAL** | **22** | **30** | **0% Complete** |

---

## Critical Path

1. **E1 (Data Collection)** → Blocks all downstream tasks
2. **E2 (Preprocessing)** → Depends on E1
3. **E3 (Correlation Analysis)** → Depends on E2
4. **E4 (Visualization)** → Depends on E3
5. **Infrastructure** → Can run in parallel with epics

**Estimated Timeline:** 5-7 days
- Data collection: 1-2 days (manual effort)
- Implementation: 2-3 days (coding + debugging)
- Visualization + docs: 1-2 days

---

## File Structure

```
h-e1/
├── code/
│   ├── data_collection.py       # E1 implementation
│   ├── preprocessing.py          # E2 implementation
│   ├── correlation_analysis.py  # E3 implementation
│   ├── visualizations.py         # E4 implementation
│   ├── main.py                   # I2 orchestration
│   ├── requirements.txt          # I1 dependencies
│   └── README.md                 # I3 documentation
├── data/
│   └── benchmark_scores.csv      # E1 output
├── results/
│   └── correlation_results.json  # E3 output
└── figures/                      # E4 outputs
    ├── correlation_matrix.png
    ├── scatter_pairs.png
    ├── stratified_comparison.png
    └── gate_metrics.png
```

---

## Success Criteria (from 03_prd.md)

### PoC Pass
1. ✅ Code runs without errors
2. ✅ At least 1 benchmark pair shows r > 0.3 AND p < 0.01 after Bonferroni

### Full Success
1. ✅ At least 2 of 3 benchmark pairs meet significance threshold
2. ✅ Correlations remain significant in ≥2 of 3 size strata
3. ✅ All 4 required visualizations generated
4. ✅ Results documented in `04_validation.md`

---

## Key Dependencies (from 03_architecture.md)

**External:**
- scipy >= 1.7.0
- statsmodels >= 0.13.0
- pandas >= 1.3.0
- matplotlib >= 3.4.0
- seaborn >= 0.11.0

**Internal:** None (green-field project)

---

## Phase 4 Handoff

**What Coder Agent Receives:**
1. PRD: `03_prd.md` (functional requirements)
2. Architecture: `03_architecture.md` (module structure, epic tasks)
3. Logic: `03_logic.md` (API signatures, data schemas)
4. Config: `03_config.md` (hyperparameters, paths)
5. PRP: This file (task breakdown, acceptance criteria)

**What Coder Agent Delivers:**
1. Working code implementing all 22 subtasks
2. Output artifacts (CSV, JSON, figures)
3. Validation report (`04_validation.md`) documenting:
   - PoC pass status
   - Correlation results (r values, p-values)
   - Gate decision (PASS/FAIL)

---

*Generated by Phase 3 Implementation Planning*
*Next: Phase 4 Coding (Coder-Validator loop)*
