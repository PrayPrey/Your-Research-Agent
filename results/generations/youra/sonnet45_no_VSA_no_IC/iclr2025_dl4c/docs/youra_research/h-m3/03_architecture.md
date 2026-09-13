# Architecture Document: h-m3 Coverage-Advantage Correlation Study

**Hypothesis ID:** h-m3  
**Type:** MECHANISM (Data Analysis)  
**Date:** 2026-08-19

---

## 1. System Overview

**Nature:** Offline data analysis pipeline (no model training, no runtime system).

**Three-Module Architecture:**
1. Coverage Measurement: Instrument reference solutions, measure branch coverage
2. Per-Problem Evaluation: Reuse h-e1 models, compute per-problem pass@1
3. Correlation Analysis: Statistical tests, visualization

**Key Constraint:** No new components. Reuse h-e1 models, standard datasets, standard libraries.

---

## 2. Module Design

### Module 1: Coverage Measurement (`coverage_measurement.py`)

**Purpose:** Measure branch coverage for HumanEval and MBPP reference solutions.

**Components:**

```
CoverageMeasurer
  ├── load_datasets()          # Load HumanEval, MBPP from HuggingFace
  ├── measure_branch_coverage() # coverage.py instrumentation
  ├── compute_statistics()      # Mean, std, distribution
  └── save_coverage_data()      # JSON output
```

**Data Flow:**
```
[HuggingFace datasets] → [Extract reference solutions + tests]
                      → [coverage.py execution]
                      → [Extract branch stats]
                      → [Save JSON]
```

**Storage:**
- `data/coverage_analysis/humaneval_coverage.json`
- `data/coverage_analysis/mbpp_coverage.json`

**Schema:**
```json
{
  "problem_id": {
    "branch_coverage_pct": float,
    "total_branches": int,
    "covered_branches": int,
    "statement_coverage_pct": float,
    "missing_branches": list
  }
}
```

### Module 2: Per-Problem Evaluation (`per_problem_eval.py`)

**Purpose:** Evaluate per-problem pass@1 for h-e1 models.

**Components:**

```
PerProblemEvaluator
  ├── load_models()              # Load h-e1 checkpoints
  ├── generate_samples()          # 20 samples/problem, temp=0.8
  ├── execute_tests()             # Sandbox execution, timeout 5s
  ├── estimate_pass_at_k()        # Unbiased estimator
  └── save_results()              # JSON output
```

**Model Reuse:**
- Binary-trained CodeGen-350M (from h-e1)
- Error-type-trained CodeGen-350M (from h-e1)
- Binary-trained StarCoder-1B (from h-e1)
- Error-type-trained StarCoder-1B (from h-e1)

**Evaluation Protocol:**
- Samples: 20/problem (HumanEval standard)
- Temperature: 0.8
- Max length: 512 tokens
- Estimator: `1 - C(n-c, k) / C(n, k)` (k=1)

**Storage:**
- `data/h-m3/per_problem_results_{model}_{feedback}_{benchmark}.json` (8 files)

**Schema:**
```json
{
  "model": "CodeGen-350M",
  "feedback_type": "binary",
  "benchmark": "HumanEval",
  "results": {
    "problem_id": {
      "pass@1": float,
      "num_correct": int,
      "num_samples": int
    }
  }
}
```

### Module 3: Correlation Analysis (`correlation_analysis.py`)

**Purpose:** Test coverage-advantage correlation, generate report.

**Components:**

```
CorrelationAnalyzer
  ├── load_coverage_data()            # Load coverage JSONs
  ├── load_evaluation_results()       # Load per-problem results
  ├── compute_feedback_advantage()    # Δ = error-type - binary
  ├── test_pearson_correlation()      # scipy.stats.pearsonr
  ├── robustness_checks()             # Difficulty control, stratification
  ├── generate_visualizations()       # Scatter, histograms
  └── write_report()                  # 04_validation.md
```

**Statistical Tests:**
1. **Primary:** Pearson correlation (coverage vs advantage)
2. **Robustness:** Partial correlation (control for SFT baseline)
3. **Stratified:** Separate correlations (HumanEval, MBPP)

**Visualizations:**
- Scatter plot: coverage (x) vs advantage (y), regression line
- Histogram: HumanEval vs MBPP coverage distributions
- Stratified scatter: Separate plots per benchmark

**Output:**
- `docs/youra_research/h-m3/04_validation.md`
- `plots/h-m3_*.png` (3 plots)

---

## 3. Data Dependencies

**Inputs:**
1. HumanEval dataset (`openai/human-eval`, HuggingFace)
2. MBPP dataset (`mbpp`, HuggingFace)
3. h-e1 trained models (4 checkpoints)

**Outputs:**
1. Coverage data (JSON, 1138 problems)
2. Per-problem results (JSON, 8 files)
3. Correlation report (Markdown + plots)

**Intermediate:**
- Temp files for coverage.py execution (cleaned after measurement)
- Generated code samples (not saved, only execution results)

---

## 4. Execution Plan

**Stage 1: Coverage Measurement (Offline)**
- Run: `python src/h-m3/coverage_measurement.py`
- Duration: ~2-4 hours (CPU-bound, parallelizable)
- Output: 2 JSON files (HumanEval, MBPP)

**Stage 2: Per-Problem Evaluation (Offline)**
- Run: `python src/h-m3/per_problem_eval.py --model <model> --feedback <type> --benchmark <name>`
- Duration: ~2-3 hours total (GPU-bound, 8 runs)
- Output: 8 JSON files

**Stage 3: Correlation Analysis (Offline)**
- Run: `python src/h-m3/correlation_analysis.py`
- Duration: <5 minutes (CPU-bound)
- Output: Report + 3 plots

**Total Duration:** ~8-12 hours (mostly compute, minimal dev)

---

## 5. Error Handling

**Coverage Measurement:**
- Skip problems with zero branches (return 100% coverage)
- Handle syntax errors in reference solutions (log, skip)
- Timeout: 60s/problem (coverage.py can hang on infinite loops)

**Per-Problem Evaluation:**
- Sandbox timeout: 5s/test execution
- Catch syntax errors in generated code (count as incorrect)
- Handle model inference failures (log, skip, mark num_correct=0)

**Correlation Analysis:**
- Validate matching problem IDs across datasets
- Check for NaN values (exclude from correlation)
- Warn if sample size < 100 (underpowered)

---

## 6. Design Decisions

**Why reuse h-e1 models instead of training new ones?**
- Isolate coverage analysis from training variability
- Faster (no 8-12 hour training runs)
- Directly test moderation hypothesis (models are controlled variable)

**Why branch coverage instead of mutation testing?**
- Mutation testing is computationally expensive (10-100× slower)
- Branch coverage is standard proxy in literature
- Limitation acknowledged in report (proxy validity)

**Why 20 samples/problem instead of 1 or 100?**
- HumanEval standard: 20 samples for pass@1 estimation
- 1 sample: too noisy (binary outcome)
- 100 samples: diminishing returns, 5× compute cost

**Why Pearson instead of Spearman?**
- Linear relationship expected (coverage → advantage)
- Pearson more powerful for linear correlations
- Spearman as robustness check (if non-linear pattern)

---

## 7. Limitations

**No real-time system:** Offline analysis only.

**No model training:** Reuse h-e1 models (training set overlap risk for HumanEval).

**Coverage proxy:** Branch coverage ≠ test quality (high coverage with weak assertions still possible).

**Sample size:** HumanEval n=164 may be underpowered for stratified analysis.

---

## 8. Testing Strategy

**Unit Tests:**
- `test_coverage_measurement.py`: Validate coverage.py integration
- `test_pass_at_k.py`: Verify unbiased estimator matches HumanEval paper

**Integration Tests:**
- Run coverage measurement on 5-problem subset (sanity check)
- Run evaluation on 5-problem subset (check model loading, execution)

**Validation:**
- Cross-check coverage results against manual inspection (5 problems)
- Verify pass@1 estimator: edge cases (num_correct=0, num_correct=num_samples)

---

**End of Architecture**
