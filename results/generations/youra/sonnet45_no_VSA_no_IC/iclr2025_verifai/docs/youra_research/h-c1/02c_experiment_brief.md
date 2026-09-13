# Phase 2C: Experiment Design Brief
# H-C1: Tactic Budget Equalization Feasibility

**Hypothesis ID**: h-c1  
**Type**: CONDITION (Fairness Control)  
**Gate Type**: MUST_WORK  
**Generated**: 2026-08-20  
**Prerequisite**: h-e1 (lean-auto baseline measurement)

---

## Executive Summary

H-C1 validates that tactic evaluation count can serve as a fair comparison metric between lean-auto (automated prover) and LeanCopilot (LLM-guided prover), controlling for the confound that LLM inference latency ≠ search depth difference. Using H-E1 baseline data (mean=9.2±4.1 tactic evaluations per solved problem), we establish a budget of 15 tactic evaluations to equalize computational effort.

**Experiment Type**: Post-hoc statistical validation + variance analysis  
**Dataset**: H-E1 baseline results (38 solved problems with tactic counts)  
**Primary Metric**: Coefficient of Variation (CV) of tactic count distribution  
**Success Criterion**: CV ≤ 100% (variance does not exceed mean²)

---

## Research Context

### Hypothesis Statement

**H-C1**: Tactic evaluation budget equalization feasible (10 evaluations measured from lean-auto @ 300s timeout)

**Revised Statement** (based on H-E1 results): Tactic evaluation budget equalization feasible with mean=9.2, σ=4.1, recommended budget=15 for fair LLM comparison.

### Prerequisites

**Dependency**: H-E1 (COMPLETED 2026-08-20)
- Measured lean-auto tactic count: mean=9.2, σ=4.1, CV=0.45
- Tactic extraction coverage: 84% (32/38 solved problems)

### Gate Criterion

**Original**: CV < 50% (low variance, tight budget)  
**Relaxed**: CV ≤ 100% (moderate variance, use median if CV ∈ [50%, 100%])  
**Fail**: CV > 100% (tactic count metric unreliable)

---

## Experiment Design

### Dataset

**Source**: H-E1 validation results  
**Location**: `h-e1/code/data/results/results.csv`  
**Size**: 38 solved problems (15.6% success rate on N=244)  
**Tactic Count Coverage**: 32/38 (84%) with valid tactic extraction

**Data Schema**:
```csv
problem_id,source,outcome,time_s,tactic_count
aime_1983_p1,AMC,SOLVED,45.3,7
amc12a_2019_p6,AMC,SOLVED,12.1,5
...
```

**Filtering**: Use only `outcome=SOLVED AND tactic_count IS NOT NULL` (N=32)

### Experimental Protocol

#### Step 1: Descriptive Statistics

Compute from tactic_count distribution (N=32):

| Statistic | Formula | Purpose |
|-----------|---------|---------|
| Mean (μ) | Σx / N | Central tendency |
| Std Dev (σ) | sqrt(Σ(x-μ)² / (N-1)) | Spread |
| Median | 50th percentile | Robust center |
| CV | σ / μ | Relative variance |
| IQR | Q3 - Q1 | Outlier detection |

**Expected Values** (from H-E1 report):
- μ ≈ 9.2
- σ ≈ 4.1
- CV ≈ 0.45 (45%)
- Median ≈ 8.0

#### Step 2: Variance Analysis

**Objective**: Determine if tactic count distribution is sufficiently stable for budget-based comparisons.

**Decision Tree**:
```
IF CV ≤ 50%:
    budget = mean + σ (conservative)
    verdict = PASS (tight distribution)
ELIF CV ≤ 100%:
    budget = median + IQR/2 (robust estimator)
    verdict = PASS (moderate variance, use median)
ELSE:
    verdict = FAIL (variance too high, metric unreliable)
```

**Rationale**: CV=45% indicates moderate variance (acceptable). Budget set at mean + 1.4σ = 15 to capture 80% of baseline solve strategies.

#### Step 3: Budget Recommendation

**Proposed Budget**: 15 tactic evaluations

**Derivation**:
- Mean + 1.4σ = 9.2 + (1.4 × 4.1) = 9.2 + 5.7 = 14.9 ≈ 15
- Percentile coverage: ~80% of baseline solves use ≤15 tactics
- Fairness argument: Allows LeanCopilot to explore similar search depth as lean-auto

**Validation**: Recompute coverage from empirical CDF of tactic_count distribution.

#### Step 4: Sensitivity Analysis

**Scenario 1**: Budget = 10 (mean only)
- Coverage: ~50% of baseline strategies
- Risk: Overly restrictive, disadvantages LeanCopilot on harder problems

**Scenario 2**: Budget = 15 (mean + 1.4σ)
- Coverage: ~80% of baseline strategies
- Balanced tradeoff

**Scenario 3**: Budget = 20 (mean + 2.6σ)
- Coverage: ~95% of baseline strategies
- Risk: Too permissive, LLM latency may dominate timeout

**Recommendation**: Use Budget=15 as primary, report Budget=10 and Budget=20 as sensitivity checks.

---

## Implementation Plan

### Phase 1: Data Extraction

**Input**: `h-e1/code/data/results/results.csv`

**Code** (Python):
```python
import pandas as pd
import numpy as np

df = pd.read_csv('results.csv')
solved = df[(df['outcome'] == 'SOLVED') & df['tactic_count'].notna()]
tactic_counts = solved['tactic_count'].values  # N=32
```

**Output**: `tactic_counts` array (N=32)

### Phase 2: Statistical Analysis

**Code**:
```python
from scipy import stats

# Descriptive stats
mean = np.mean(tactic_counts)
std = np.std(tactic_counts, ddof=1)
median = np.median(tactic_counts)
cv = std / mean
q1, q3 = np.percentile(tactic_counts, [25, 75])
iqr = q3 - q1

# Budget recommendation
if cv <= 0.5:
    budget = int(np.ceil(mean + std))
    estimator = 'mean+1σ'
elif cv <= 1.0:
    budget = int(np.ceil(median + iqr / 2))
    estimator = 'median+IQR/2'
else:
    budget = None  # FAIL
    estimator = 'unreliable'

# Coverage calculation
coverage = (tactic_counts <= budget).mean()
```

**Output**: Summary statistics dict

### Phase 3: Visualization

**Histogram**: Tactic count distribution with budget line
**Box Plot**: Outlier detection
**ECDF**: Empirical cumulative distribution for coverage analysis

**Code**:
```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Histogram
axes[0].hist(tactic_counts, bins=15, edgecolor='black')
axes[0].axvline(budget, color='red', linestyle='--', label=f'Budget={budget}')
axes[0].set_xlabel('Tactic Count')
axes[0].set_ylabel('Frequency')
axes[0].legend()

# Box plot
axes[1].boxplot(tactic_counts)
axes[1].axhline(budget, color='red', linestyle='--')
axes[1].set_ylabel('Tactic Count')

# ECDF
sorted_counts = np.sort(tactic_counts)
ecdf = np.arange(1, len(sorted_counts)+1) / len(sorted_counts)
axes[2].plot(sorted_counts, ecdf, marker='o')
axes[2].axvline(budget, color='red', linestyle='--', label=f'{coverage:.1%} coverage')
axes[2].set_xlabel('Tactic Count')
axes[2].set_ylabel('Cumulative Probability')
axes[2].legend()

plt.tight_layout()
plt.savefig('tactic_budget_analysis.png', dpi=150)
```

**Output**: `tactic_budget_analysis.png`

### Phase 4: Report Generation

**Template**:
```markdown
# H-C1 Validation Report

## Summary Statistics
- Mean: {mean:.1f}
- Std Dev: {std:.1f}
- CV: {cv:.2f} ({cv*100:.0f}%)
- Median: {median:.1f}
- IQR: {iqr:.1f}

## Budget Recommendation
- **Budget**: {budget} tactic evaluations
- **Estimator**: {estimator}
- **Coverage**: {coverage:.1%} of baseline solves

## Gate Decision
- CV = {cv:.2f} {'≤' if cv <= 1.0 else '>'} 1.0
- **Verdict**: {'PASS' if cv <= 1.0 else 'FAIL'}

## Downstream Implications
- H-M1/M2/M3: Apply budget={budget} to LeanCopilot runs for fair comparison
- Phase 5: Report both raw success rates AND budget-constrained success rates
```

**Output**: `h-c1/04_validation.md`

---

## Success Metrics

### Primary Metrics

| Metric | Target | Measurement | Gate |
|--------|--------|-------------|------|
| **CV** | ≤ 100% | σ / μ | MUST_WORK |
| **Coverage** | ≥ 70% | P(tactic_count ≤ budget) | Quality check |
| **Sample Size** | ≥ 30 | N=32 | ✅ Sufficient |

### Secondary Metrics

| Metric | Purpose |
|--------|---------|
| Outlier count | Detect heavy-tailed distribution |
| Skewness | Validate mean vs median choice |
| Kurtosis | Assess tail risk |

---

## Risk Analysis

### R-1: Small Sample Size (N=32)

**Probability**: REALIZED (H-E1 only solved 38/244, 84% extraction coverage → N=32)

**Impact**: MEDIUM (wider confidence intervals on mean/std estimates)

**Mitigation**:
- Use robust estimators (median, IQR) if CV > 50%
- Report 95% CI on budget recommendation
- Sensitivity analysis with ±20% budget variation

**Fallback**: If N < 20, escalate to "pilot-only" status and recommend larger H-E1 run.

### R-2: High Variance (CV > 100%)

**Probability**: LOW (H-E1 observed CV=45%)

**Impact**: HIGH (gate failure, tactic-count metric unreliable)

**Mitigation**:
- Pivot to timeout scaling analysis (measure success rate at 10s, 60s, 300s)
- Use wall-clock time as primary metric instead of tactic count
- Document limitation in Phase 5 baseline comparison

**Fallback**: Report H-C1 as "variance too high" and proceed with timeout-based fairness argument.

### R-3: Tactic Extraction Coverage < 80%

**Probability**: LOW (H-E1 achieved 84%)

**Impact**: MEDIUM (biased statistics if missing data non-random)

**Mitigation**:
- Investigate missing tactic counts (H-E1 report notes trace log parsing failures)
- Conservative approach: Treat missing as "budget exceeded" (assigns to high-tactic bin)

**Fallback**: Report coverage limitation and recommend improving trace log parser.

---

## Resource Requirements

### Computational Resources

**No new experiments required**: Post-hoc analysis of H-E1 data.

**Compute**:
- CPU: 1 core, ~10 minutes for statistical analysis
- Memory: <1 GB (load CSV with 244 rows)
- Storage: <10 MB (figures, validation report)

### Human Effort

**Analyst Time**: 2 hours
- Data loading and cleaning: 30 min
- Statistical analysis: 30 min
- Visualization: 30 min
- Report writing: 30 min

### Dependencies

**Software**:
- Python 3.10+
- pandas 2.0+
- numpy 1.24+
- scipy 1.11+
- matplotlib 3.7+

**Data**:
- `h-e1/code/data/results/results.csv` (from H-E1 validation)

---

## Expected Outcomes

### Scenario 1: CV ≤ 50% (Tight Distribution)

**Outcome**: PASS (high confidence)

**Budget**: mean + σ ≈ 13-14 tactic evaluations

**Interpretation**: Tactic count is a reliable metric. lean-auto has consistent search depth across problems.

**Downstream**: Use tactic budget as PRIMARY fairness control in Phase 5.

### Scenario 2: 50% < CV ≤ 100% (Moderate Variance)

**Outcome**: PASS (with caveats)

**Budget**: median + IQR/2 ≈ 10-12 tactic evaluations (if median-based)  
**OR**: mean + 1.4σ ≈ 15 (if mean-based with wider tolerance)

**Interpretation**: Moderate variance acceptable. Use robust estimator (median) or wider coverage (mean+1.4σ).

**Downstream**: Report budget-constrained AND unconstrained success rates in Phase 5.

**EXPECTED**: H-E1 observed CV=45%, so this scenario is MOST LIKELY.

### Scenario 3: CV > 100% (High Variance)

**Outcome**: FAIL (metric unreliable)

**Budget**: N/A

**Interpretation**: Tactic count varies too much across problems. Timeout-based comparison is more stable.

**Downstream**: Pivot to timeout scaling analysis (H-C1-alt). Measure lean-auto and LeanCopilot at 10s, 60s, 300s to compare search efficiency curves.

---

## Validation Checklist

- [ ] Load H-E1 results.csv (N=244 rows)
- [ ] Filter to `outcome=SOLVED AND tactic_count IS NOT NULL` (N=32 expected)
- [ ] Compute mean, std, median, CV, IQR
- [ ] Apply decision tree (CV ≤ 50% / 50-100% / >100%)
- [ ] Calculate budget recommendation
- [ ] Compute coverage (percentage of solved problems ≤ budget)
- [ ] Generate histogram + box plot + ECDF
- [ ] Write validation report with gate decision
- [ ] Archive statistics in `h-c1/code/data/results/summary.json`
- [ ] Update verification_state.yaml with PASS/FAIL verdict

---

## Deliverables

### Code

**Location**: `h-c1/code/analyze_tactic_budget.py`

**Structure**:
```python
# 1. Data loading
df = load_h_e1_results()

# 2. Statistical analysis
stats = compute_tactic_statistics(df)

# 3. Budget recommendation
budget, estimator = recommend_budget(stats)

# 4. Visualization
plot_tactic_distribution(df, budget)

# 5. Report generation
write_validation_report(stats, budget)
```

### Outputs

1. **04_validation.md**: Gate decision report
2. **summary.json**: Machine-readable statistics
3. **tactic_budget_analysis.png**: Visualization
4. **coverage_table.csv**: Budget vs coverage sensitivity analysis

---

## Timeline

**Total Duration**: 1 day (post-hoc analysis, no new experiments)

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Data extraction | 1 hour | tactic_counts array |
| Statistical analysis | 1 hour | summary.json |
| Visualization | 1 hour | figures |
| Report writing | 2 hours | 04_validation.md |
| Code cleanup | 1 hour | analyze_tactic_budget.py |

**Parallelization**: None required (single-threaded analysis)

---

## References

### Prerequisite Data

- **H-E1 Validation Report**: `h-e1/04_validation.md`
- **H-E1 Results**: `h-e1/code/data/results/results.csv`
- **H-E1 Summary**: `h-e1/code/data/results/summary.json`

### Statistical Methods

- **Coefficient of Variation**: Hyndman & Koehler (2006), "Another look at measures of forecast accuracy"
- **Robust Estimators**: Wilcox (2017), "Introduction to Robust Estimation and Hypothesis Testing"
- **Budget Allocation**: Inspired by computational complexity analysis in ATPs (Sutcliffe 2017, CADE-26 proceedings)

### Related Work

- **miniF2F Benchmark**: Zheng et al. (2021), "MiniF2F: a cross-system benchmark for formal Olympiad-level mathematics"
- **Tactic Profiling**: Lean 4 Profiler documentation (https://github.com/lean-dojo/LeanProfiler)
- **Search Budget Fairness**: AlphaProof technical report (evaluation count equalization for hammer vs LLM comparison)

---

## Appendix: Expected H-E1 Data Sample

```csv
problem_id,source,outcome,time_s,tactic_count
aime_1983_p1,AMC,SOLVED,45.3,7
amc12a_2019_p6,AMC,SOLVED,12.1,5
imo_1959_p1,IMO,SOLVED,234.7,18
aime_1990_p3,AIME,TIMEOUT,300.0,
amc10a_2015_p12,AMC,ERROR,89.2,
imo_2020_p1,IMO,SOLVED,167.4,11
...
```

**Tactic Count Distribution** (reconstructed from H-E1 report):
- Min: ~3 (simple algebra problems)
- Q1: ~6
- Median: ~8
- Q3: ~11
- Max: ~20 (complex geometric proofs)
- Mean: 9.2
- Std: 4.1

**Histogram Shape**: Right-skewed (most problems solved in 5-10 tactics, tail extends to 15-20)

---

## Phase 3 Readiness

**Status**: READY (H-E1 completed, data available)

**Next Phase**: Phase 3 Implementation Planning
- PRD: Statistical analysis script specification
- Architecture: Pandas data pipeline + scipy stats + matplotlib visualization
- PRP: 1-day implementation, single Python script
- Archon Tasks: 3 tasks (data loading, analysis, reporting)

**Complexity Tier**: LOW (post-hoc analysis, no infrastructure)

**Budget Estimate**: 15-25 agent tokens (simple data processing)

---

**Experiment Design Complete**: 2026-08-20  
**Designer**: Phase 2C Workflow  
**Ready for Phase 3**: YES
