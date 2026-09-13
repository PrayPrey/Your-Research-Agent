# Product Requirements Document: h-m3 Coverage-Advantage Correlation Study

**Hypothesis ID:** h-m3  
**Type:** MECHANISM  
**Gate:** SHOULD_WORK  
**Date:** 2026-08-19

---

## 1. Executive Summary

**Objective:** Test whether test coverage quality (branch coverage %) moderates feedback granularity requirements by correlating coverage with per-problem feedback-type advantage (error-type gain over binary).

**Approach:** Three-stage offline analysis:
1. Measure branch coverage for HumanEval (164) and MBPP (974) using coverage.py
2. Evaluate per-problem pass@1 using h-e1 trained models (binary vs error-type)
3. Correlate coverage with feedback advantage (Pearson correlation)

**Success Criteria:**
- Pearson r ≥ 0.77 (R² ≥ 0.6, coverage explains ≥60% variance)
- Coverage difference HumanEval vs MBPP ≥10 pp

**Key Constraint:** Analysis-only task (no model training). Reuse h-e1 models.

---

## 2. Functional Requirements

### FR-1: Coverage Measurement Module

**Capability:** Measure branch coverage for reference solutions.

**Inputs:**
- HumanEval dataset (164 problems, `openai/human-eval`)
- MBPP dataset (974 problems, `mbpp`)
- Reference solutions (`canonical_solution` field)
- Test suites (`test` field)

**Outputs:**
- `data/coverage_analysis/humaneval_coverage.json`: `{problem_id: {branch_coverage_pct, total_branches, covered_branches, statement_coverage_pct}}`
- `data/coverage_analysis/mbpp_coverage.json`: (same schema)

**Coverage Tool:**
- coverage.py v7.15+ (branch mode)
- API: `Coverage(branch=True)` → `analysis2(filename)` → extract branch stats

**Processing:**
1. Load datasets (HuggingFace `datasets` library)
2. For each problem:
   - Write reference solution + test suite to temp file
   - Initialize `Coverage(branch=True)`
   - Execute code under coverage
   - Extract branch statistics
   - Save metrics
3. Compute statistics: mean, std, distribution per benchmark

**Validation:**
- Verify ≥10 pp coverage difference (HumanEval > MBPP)
- Check coverage distribution variance (sufficient to test correlation)

### FR-2: Per-Problem Evaluation Module

**Capability:** Evaluate per-problem pass@1 for h-e1 models.

**Inputs:**
- Trained models from h-e1:
  - Binary-trained CodeGen-350M
  - Error-type-trained CodeGen-350M
  - Binary-trained StarCoder-1B
  - Error-type-trained StarCoder-1B
- Datasets: HumanEval (164), MBPP (974)
- Evaluation protocol: 20 samples/problem, pass@1 estimator

**Outputs:**
- `data/h-m3/per_problem_results.json`:
  ```json
  {
    "model": "CodeGen-350M-binary",
    "benchmark": "HumanEval",
    "results": {
      "HumanEval/0": {"pass@1": 0.85, "num_correct": 18, "num_samples": 20},
      ...
    }
  }
  ```
- 8 result files (2 models × 2 feedback types × 2 benchmarks)

**Pass@k Estimator:**
- Function: `estimate_pass_at_k(num_samples, num_correct, k=1)`
- Formula: `1 - C(n-c, k) / C(n, k)` (unbiased, from HumanEval paper)

**Execution:**
- Code generation: Temperature 0.8, max_length 512
- Test execution: Sandbox isolation (timeout 5s/test)
- Error handling: Catch syntax errors, runtime errors

**Validation:**
- Check total generations: 164 problems × 20 samples = 3,280/benchmark
- Verify pass@1 range: [0, 1]

### FR-3: Correlation Analysis Module

**Capability:** Test coverage-advantage correlation.

**Inputs:**
- Coverage data (`humaneval_coverage.json`, `mbpp_coverage.json`)
- Per-problem results (`per_problem_results.json` × 8 files)

**Outputs:**
- `docs/youra_research/h-m3/04_validation.md`: Results report
- Plots:
  - `plots/h-m3_coverage_advantage_correlation.png`: Scatter plot (coverage vs advantage)
  - `plots/h-m3_coverage_distributions.png`: Histogram (HumanEval vs MBPP)
  - `plots/h-m3_stratified_correlation.png`: Separate correlations per benchmark

**Analysis Steps:**

1. **Compute Feedback Advantage:**
   - Per problem: `Δ = error-type_pass@1 - binary_pass@1`
   - Store: `{problem_id: {advantage, binary_pass@1, error_type_pass@1}}`

2. **Pearson Correlation Test:**
   - Extract: `(coverage_pct, advantage)` pairs
   - Compute: `scipy.stats.pearsonr(coverage, advantage)`
   - Report: r, p-value, R²

3. **Robustness Checks:**
   - **Difficulty control:** Partial correlation controlling for SFT baseline performance
   - **Stratified analysis:** Separate correlations for HumanEval and MBPP
   - **Secondary metrics:** Correlation with statement coverage, test suite size

**Success Criteria:**
- Primary: r ≥ 0.77, p < 0.05
- Expected pattern: Negative correlation (high coverage → low advantage)

**Gate Evaluation:**
- PASS: r ≥ 0.77 AND p < 0.05 → Coverage moderation validated
- FAIL: r < 0.5 → Null result (not blocking, SHOULD_WORK gate)

---

## 3. Non-Functional Requirements

### NFR-1: Performance
- Coverage measurement: Parallelize over CPU cores (974 MBPP problems, ~2-4 hours)
- Per-problem evaluation: GPU-accelerated (reuse h-e1 models, ~2-3 hours)
- Correlation analysis: CPU-bound (fast, <5 minutes)

### NFR-2: Reproducibility
- Random seed control for code generation (temperature 0.8, fixed seed)
- Cache coverage results (JSON) to enable reanalysis
- Save raw per-problem results (no aggregation yet)

### NFR-3: Data Integrity
- Validate coverage measurement: Check total_branches > 0
- Validate pass@1: Range [0, 1], no NaN values
- Match problem IDs across coverage and evaluation datasets

---

## 4. Data Flow

```
[HumanEval/MBPP datasets]
         ↓
    [FR-1: Coverage Measurement]
         ↓
    [coverage_analysis/*.json]
         ↓
    [FR-3: Correlation Analysis] ← [per_problem_results.json]
         ↑
    [FR-2: Per-Problem Evaluation]
         ↑
    [h-e1 trained models]
```

---

## 5. Out of Scope

- **No new model training:** Reuse h-e1 models (binary, error-type)
- **No dataset creation:** Use standard HumanEval and MBPP
- **No architecture design:** Data analysis only
- **No Archon KB tasks:** Analysis task, not implementation

---

## 6. Dependencies

**External Libraries:**
- `coverage` v7.15+ (branch coverage measurement)
- `datasets` (HuggingFace, for HumanEval/MBPP)
- `transformers` (model loading)
- `scipy` (Pearson correlation, t-tests)
- `matplotlib` (visualization)
- `numpy` (pass@k estimator)

**Data Dependencies:**
- h-e1 trained models (prerequisite: h-e1 VALIDATED)
- HumanEval reference solutions (from dataset)
- MBPP reference solutions (from dataset)

---

## 7. Success Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| Coverage correlation (r) | ≥ 0.77 | Pearson test, p < 0.05 |
| Coverage difference (HumanEval - MBPP) | ≥ 10 pp | Two-sample t-test |
| Per-problem evaluations | 1138 problems × 8 models | Count total |
| Coverage measurements | 1138 problems | Check JSON file size |

**Gate Verdict:**
- PASS: r ≥ 0.77, p < 0.05
- FAIL: r < 0.5 (null result, not blocking)

---

## 8. Deliverables

1. **Code:**
   - `src/h-m3/coverage_measurement.py`
   - `src/h-m3/per_problem_eval.py`
   - `src/h-m3/correlation_analysis.py`

2. **Data:**
   - `data/coverage_analysis/humaneval_coverage.json`
   - `data/coverage_analysis/mbpp_coverage.json`
   - `data/h-m3/per_problem_results.json` (8 files)

3. **Plots:**
   - `plots/h-m3_coverage_advantage_correlation.png`
   - `plots/h-m3_coverage_distributions.png`
   - `plots/h-m3_stratified_correlation.png`

4. **Report:**
   - `docs/youra_research/h-m3/04_validation.md`

---

**End of PRD**
