# Experiment Brief: h-m3 Test Coverage Quality Moderates Feedback Granularity

**Date:** 2026-08-19  
**Hypothesis ID:** h-m3  
**Type:** MECHANISM  
**Gate:** SHOULD_WORK  
**Prerequisites:** h-e1 (VALIDATED), h-m2 (VALIDATED)  

---

## 1. Hypothesis Statement

**Full Statement:**  
Test coverage quality moderates feedback granularity requirements: comprehensive test suites enable binary sufficiency while weak coverage benefits from error-type semantic hints.

**Testable Claim:**  
Under small model capacity constraints (350M-1B parameters), if we measure test coverage quality (branch coverage %) for HumanEval and MBPP problems and correlate with per-problem feedback-type advantage, then test coverage explains ≥60% of variance (Pearson r ≥ 0.77) in feedback-type advantage (error-type gain over binary), because comprehensive test suites enable binary sufficiency while weak coverage benefits from error-type semantic hints.

**Success Criteria (from 02b_verification_plan.md):**
1. **Coverage Correlation:** Pearson r ≥ 0.77 (R² ≥ 0.6) between branch coverage and feedback-type advantage
2. **Coverage Variance:** HumanEval and MBPP differ by ≥10 pp average coverage (sufficient variance to test hypothesis)

---

## 2. Experimental Design

### 2.1 Overview

Measure branch coverage for all HumanEval (164) and MBPP (974) problems using coverage.py, train models with binary and error-type feedback (reusing h-e1 setup), evaluate per-problem pass@1, and correlate coverage with feedback-type advantage.

**Three-Stage Design:**

**Stage 1: Coverage Measurement (Offline)**
- Instrument reference solutions with coverage.py (branch mode)
- Execute reference solutions against test suites
- Extract branch coverage % per problem
- Compute coverage statistics: mean, std, distribution

**Stage 2: Per-Problem Evaluation (Reuse h-e1 models)**
- Load trained models from h-e1 (binary and error-type conditions)
- Evaluate per-problem pass@1 (not aggregated benchmark pass@1)
- Generate N=20 samples per problem (following HumanEval standard)
- Compute pass@1 using unbiased estimator: 1 - C(n-c, k) / C(n, k)

**Stage 3: Correlation Analysis**
- Compute per-problem feedback advantage: Δ = error-type_pass@1 - binary_pass@1
- Correlate branch coverage % with Δ using Pearson correlation
- Robustness checks: control for baseline SFT performance, stratify by benchmark

### 2.2 Dataset & Coverage Measurement

#### Datasets

**Primary: HumanEval**
- Problems: 164 hand-written Python functions
- Source: `openai/human-eval` (github.com/openai/human-eval)
- Type: `standard` (real dataset, established benchmark)
- Cache: `/home/PrayPrey/.cache/huggingface/datasets/openai_humaneval`
- Test suite: Comprehensive unit tests per problem (avg 7.5 tests/problem)
- Hypothesis: High branch coverage → binary feedback sufficient

**Secondary: MBPP**
- Problems: 974 entry-level Python problems
- Source: `google-research-datasets/mbpp` (huggingface.co/datasets/mbpp)
- Type: `standard` (real dataset, Google benchmark)
- Cache: `/home/PrayPrey/.cache/huggingface/datasets/mbpp`
- Test suite: 3 test cases per problem (weaker coverage)
- Hypothesis: Lower branch coverage → error-type feedback advantage

#### Coverage Instrumentation (coverage.py)

**Tool:** coverage.py v7.15+ (branch coverage mode)
- Source: `coveragepy/coveragepy` (github.com/coveragepy/coveragepy, 3393 stars)
- Implementation reference: [VERIFIED - EXA] coverage.readthedocs.io/en/latest/branch.html
- API: Programmatic access via `Coverage` class

**Measurement Protocol:**

```python
from coverage import Coverage
from coverage.data import CoverageData
import tempfile
import os

def measure_branch_coverage(problem_code: str, test_suite: str) -> dict:
    """
    Measure branch coverage for a single problem.
    
    Returns:
        {
            'branch_coverage_pct': float,  # % of branches covered
            'total_branches': int,
            'covered_branches': int,
            'statement_coverage_pct': float,  # Secondary metric
            'problem_id': str
        }
    """
    # Create temp file with problem code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(problem_code)
        f.write('\n\n')
        f.write(test_suite)
        code_file = f.name
    
    try:
        # Initialize coverage with branch mode
        cov = Coverage(branch=True, source=[os.path.dirname(code_file)])
        cov.start()
        
        # Execute code + tests
        exec(compile(open(code_file).read(), code_file, 'exec'), {})
        
        cov.stop()
        cov.save()
        
        # Extract branch statistics
        analysis = cov.analysis2(code_file)
        executed_lines, missing_lines, excluded_lines, missing_branches = analysis
        
        # Compute metrics
        total_branches = cov._analyze(code_file).total_branches()
        covered_branches = total_branches - len(missing_branches)
        branch_coverage_pct = (covered_branches / total_branches * 100) if total_branches > 0 else 100.0
        
        statement_coverage_pct = (len(executed_lines) / (len(executed_lines) + len(missing_lines)) * 100) 
        
        return {
            'branch_coverage_pct': branch_coverage_pct,
            'total_branches': total_branches,
            'covered_branches': covered_branches,
            'statement_coverage_pct': statement_coverage_pct,
            'missing_branches': missing_branches  # For debugging
        }
    finally:
        os.unlink(code_file)
```

**Coverage Dataset Construction:**

For each problem in HumanEval and MBPP:
1. Extract reference solution code
2. Extract test suite (all test cases)
3. Measure branch coverage using protocol above
4. Store results in JSON: `{problem_id: {coverage_metrics}}`
5. Save to: `data/coverage_analysis/humaneval_coverage.json`, `data/coverage_analysis/mbpp_coverage.json`

**Expected Coverage Statistics (Hypothesis):**
- HumanEval: mean coverage 75-85% (comprehensive test suites)
- MBPP: mean coverage 45-60% (3 tests/problem, weaker coverage)
- Coverage difference: ≥10 pp (criterion for sufficient variance)

### 2.3 Per-Problem Evaluation

#### Model Reuse (from h-e1)

**Models:**
- Binary-trained CodeGen-350M (checkpoint from h-e1)
- Error-type-trained CodeGen-350M (checkpoint from h-e1)
- Binary-trained StarCoder-1B (checkpoint from h-e1)
- Error-type-trained StarCoder-1B (checkpoint from h-e1)

**Rationale:** Reuse h-e1 trained models to isolate coverage analysis from training variability. No new training required.

#### Evaluation Protocol

**Per-Problem Pass@1 Estimation:**

```python
import numpy as np
from typing import List

def estimate_pass_at_k(num_samples: int, num_correct: int, k: int = 1) -> float:
    """
    Unbiased estimator for pass@k (from HumanEval paper).
    
    Calculates: 1 - C(n-c, k) / C(n, k)
    where n = num_samples, c = num_correct, k = top-k threshold
    """
    if num_samples - num_correct < k:
        return 1.0
    return 1.0 - np.prod(1.0 - k / np.arange(num_samples - num_correct + 1, num_samples + 1))

def evaluate_per_problem_pass_at_1(model, problems: List[dict], num_samples: int = 20) -> dict:
    """
    Evaluate per-problem pass@1 for a model.
    
    Args:
        model: Trained code generation model
        problems: List of {problem_id, prompt, test_suite}
        num_samples: Generations per problem (default 20, HumanEval standard)
    
    Returns:
        {problem_id: {'pass@1': float, 'num_correct': int, 'num_samples': int}}
    """
    results = {}
    
    for problem in problems:
        num_correct = 0
        
        # Generate N samples
        for _ in range(num_samples):
            generated_code = model.generate(problem['prompt'], max_length=512, temperature=0.8)
            
            # Execute against test suite
            is_correct = execute_tests(generated_code, problem['test_suite'])
            num_correct += int(is_correct)
        
        # Compute pass@1 using unbiased estimator
        pass_at_1 = estimate_pass_at_k(num_samples, num_correct, k=1)
        
        results[problem['problem_id']] = {
            'pass@1': pass_at_1,
            'num_correct': num_correct,
            'num_samples': num_samples
        }
    
    return results
```

**Evaluation Runs:**
1. Binary-CodeGen-350M on HumanEval (164 problems × 20 samples = 3,280 generations)
2. Error-type-CodeGen-350M on HumanEval (164 problems × 20 samples = 3,280 generations)
3. Binary-CodeGen-350M on MBPP (974 problems × 20 samples = 19,480 generations)
4. Error-type-CodeGen-350M on MBPP (974 problems × 20 samples = 19,480 generations)
5. Repeat for StarCoder-1B (4 runs × ~11,000 generations each)

**Total evaluation cost:** ~90,000 code generations (reusing cached models, GPU cost: ~2-3 hours)

### 2.4 Correlation Analysis

#### Feedback-Type Advantage Computation

**Per-Problem Advantage:**

```python
def compute_feedback_advantage(binary_results: dict, error_type_results: dict) -> dict:
    """
    Compute per-problem feedback-type advantage.
    
    Δ_i = error_type_pass@1_i - binary_pass@1_i
    
    Positive Δ: error-type feedback helped
    Negative Δ: binary feedback was better (or tied)
    """
    advantages = {}
    
    for problem_id in binary_results:
        delta = error_type_results[problem_id]['pass@1'] - binary_results[problem_id]['pass@1']
        advantages[problem_id] = {
            'advantage': delta,
            'binary_pass@1': binary_results[problem_id]['pass@1'],
            'error_type_pass@1': error_type_results[problem_id]['pass@1']
        }
    
    return advantages
```

#### Correlation Test

**Primary Analysis:**

```python
from scipy.stats import pearsonr

def test_coverage_correlation(coverage_data: dict, advantage_data: dict) -> dict:
    """
    Test coverage-advantage correlation.
    
    H0: Coverage does not explain feedback advantage (r = 0)
    H1: Coverage explains ≥60% of variance (r ≥ 0.77)
    """
    # Extract matched pairs
    problem_ids = set(coverage_data.keys()) & set(advantage_data.keys())
    
    coverage_values = [coverage_data[pid]['branch_coverage_pct'] for pid in problem_ids]
    advantage_values = [advantage_data[pid]['advantage'] for pid in problem_ids]
    
    # Pearson correlation
    r, p_value = pearsonr(coverage_values, advantage_values)
    
    # Success criterion
    success = (r >= 0.77) and (p_value < 0.05)
    
    return {
        'pearson_r': r,
        'r_squared': r**2,
        'p_value': p_value,
        'n_problems': len(problem_ids),
        'success': success,
        'criterion': 'r ≥ 0.77, p < 0.05'
    }
```

**Expected Correlation Pattern (Hypothesis):**
- **Negative correlation:** Higher coverage → lower feedback advantage
- **Interpretation:** When coverage is high (comprehensive tests), binary feedback suffices (Δ ≈ 0). When coverage is low (weak tests), error-type feedback provides semantic hints (Δ > 0).

#### Robustness Checks

**Control for Problem Difficulty:**

```python
def partial_correlation_difficulty_controlled(coverage, advantage, sft_baseline_perf):
    """
    Partial correlation controlling for baseline SFT performance.
    
    If coverage and difficulty both correlate with advantage, partial
    correlation isolates coverage effect.
    """
    from scipy.stats import spearmanr
    
    # Baseline SFT performance proxy for difficulty
    # (harder problems → lower SFT pass@1)
    
    # Compute residuals after regressing out difficulty
    coverage_residuals = residualize(coverage, sft_baseline_perf)
    advantage_residuals = residualize(advantage, sft_baseline_perf)
    
    # Correlation on residuals
    r_partial, p_partial = pearsonr(coverage_residuals, advantage_residuals)
    
    return r_partial, p_partial
```

**Stratified Analysis:**

```python
def stratify_by_benchmark(coverage_data, advantage_data):
    """
    Test hypothesis separately for HumanEval and MBPP.
    
    Expected:
    - HumanEval: r ≈ -0.6 (high coverage, weak advantage)
    - MBPP: r ≈ -0.8 (wider coverage variance, stronger signal)
    """
    humaneval_ids = [pid for pid in coverage_data if pid.startswith('HumanEval')]
    mbpp_ids = [pid for pid in coverage_data if pid.startswith('MBPP')]
    
    humaneval_r, humaneval_p = test_coverage_correlation(
        {pid: coverage_data[pid] for pid in humaneval_ids},
        {pid: advantage_data[pid] for pid in humaneval_ids}
    )
    
    mbpp_r, mbpp_p = test_coverage_correlation(
        {pid: coverage_data[pid] for pid in mbpp_ids},
        {pid: advantage_data[pid] for pid in mbpp_ids}
    )
    
    return {
        'humaneval': {'r': humaneval_r, 'p': humaneval_p},
        'mbpp': {'r': mbpp_r, 'p': mbpp_p}
    }
```

**Secondary Coverage Metrics:**

Test correlation with:
- Statement coverage % (alternative metric)
- Path coverage % (if computable via coverage.py plugins)
- Test suite size (number of test cases)

If all metrics correlate with advantage, coverage hypothesis strengthened. If not, identifies proxy limitations.

### 2.5 Visualization

**Scatter Plot:**

```python
import matplotlib.pyplot as plt

def plot_coverage_advantage_correlation(coverage_data, advantage_data, r, p):
    """
    Scatter plot: branch coverage (x) vs feedback advantage (y)
    """
    coverage_values = [coverage_data[pid]['branch_coverage_pct'] for pid in coverage_data]
    advantage_values = [advantage_data[pid]['advantage'] for pid in coverage_data]
    
    plt.figure(figsize=(8, 6))
    plt.scatter(coverage_values, advantage_values, alpha=0.6, s=30)
    plt.xlabel('Branch Coverage (%)')
    plt.ylabel('Feedback Advantage (error-type - binary pass@1)')
    plt.title(f'Coverage-Advantage Correlation (r={r:.2f}, p={p:.3f})')
    plt.axhline(y=0, color='gray', linestyle='--', linewidth=1)
    
    # Linear regression line
    from scipy.stats import linregress
    slope, intercept, _, _, _ = linregress(coverage_values, advantage_values)
    x_line = np.linspace(min(coverage_values), max(coverage_values), 100)
    y_line = slope * x_line + intercept
    plt.plot(x_line, y_line, color='red', linewidth=2)
    
    plt.savefig('plots/h-m3_coverage_advantage_correlation.png', dpi=300)
```

**Coverage Distribution:**

```python
def plot_coverage_distributions():
    """
    Histogram comparing HumanEval vs MBPP coverage distributions.
    
    Validates ≥10 pp coverage difference criterion.
    """
    humaneval_coverage = [coverage_data[pid]['branch_coverage_pct'] 
                          for pid in coverage_data if pid.startswith('HumanEval')]
    mbpp_coverage = [coverage_data[pid]['branch_coverage_pct'] 
                     for pid in coverage_data if pid.startswith('MBPP')]
    
    plt.figure(figsize=(10, 5))
    plt.hist(humaneval_coverage, bins=20, alpha=0.7, label='HumanEval', color='blue')
    plt.hist(mbpp_coverage, bins=20, alpha=0.7, label='MBPP', color='orange')
    plt.xlabel('Branch Coverage (%)')
    plt.ylabel('Frequency')
    plt.title('Coverage Distribution: HumanEval vs MBPP')
    plt.legend()
    plt.savefig('plots/h-m3_coverage_distributions.png', dpi=300)
```

---

## 3. Implementation Plan

### 3.1 Epic Tasks

**Epic 1: Coverage Measurement Infrastructure**
- Load HumanEval and MBPP datasets
- Extract reference solutions and test suites
- Instrument coverage.py in branch mode
- Execute reference solutions, collect coverage metrics
- Save coverage datasets (JSON)

**Epic 2: Per-Problem Evaluation Pipeline**
- Load h-e1 trained models (binary, error-type, 2 model sizes)
- Implement per-problem pass@1 evaluation (20 samples/problem)
- Run evaluation on HumanEval and MBPP (4 model-feedback combinations)
- Save per-problem pass@1 results (JSON)

**Epic 3: Correlation Analysis**
- Compute per-problem feedback advantage
- Test Pearson correlation (coverage vs advantage)
- Robustness checks: difficulty control, stratified analysis
- Generate visualizations (scatter plot, distributions)
- Write results report

### 3.2 Subtasks

**Epic 1 Subtasks:**
1.1. Install coverage.py (v7.15+)
1.2. Load HumanEval dataset (164 problems)
1.3. Load MBPP dataset (974 problems)
1.4. Extract reference solutions (parse `canonical_solution` field)
1.5. Extract test suites (parse `test` field)
1.6. Implement `measure_branch_coverage()` function
1.7. Run coverage measurement on HumanEval (164 problems)
1.8. Run coverage measurement on MBPP (974 problems)
1.9. Compute coverage statistics (mean, std, distribution)
1.10. Validate ≥10 pp coverage difference criterion
1.11. Save coverage datasets to JSON

**Epic 2 Subtasks:**
2.1. Load binary-trained CodeGen-350M from h-e1
2.2. Load error-type-trained CodeGen-350M from h-e1
2.3. Load binary-trained StarCoder-1B from h-e1
2.4. Load error-type-trained StarCoder-1B from h-e1
2.5. Implement `evaluate_per_problem_pass_at_1()` function
2.6. Implement `estimate_pass_at_k()` estimator
2.7. Run evaluation: Binary-CodeGen on HumanEval
2.8. Run evaluation: Error-type-CodeGen on HumanEval
2.9. Run evaluation: Binary-CodeGen on MBPP
2.10. Run evaluation: Error-type-CodeGen on MBPP
2.11. Run evaluation: Binary-StarCoder on HumanEval
2.12. Run evaluation: Error-type-StarCoder on HumanEval
2.13. Run evaluation: Binary-StarCoder on MBPP
2.14. Run evaluation: Error-type-StarCoder on MBPP
2.15. Save per-problem results to JSON

**Epic 3 Subtasks:**
3.1. Implement `compute_feedback_advantage()` function
3.2. Compute advantage for CodeGen-350M (HumanEval + MBPP)
3.3. Compute advantage for StarCoder-1B (HumanEval + MBPP)
3.4. Implement `test_coverage_correlation()` function
3.5. Test correlation on CodeGen-350M results
3.6. Test correlation on StarCoder-1B results
3.7. Implement difficulty-controlled partial correlation
3.8. Implement stratified analysis (HumanEval vs MBPP)
3.9. Test secondary metrics (statement coverage, test suite size)
3.10. Generate scatter plot visualization
3.11. Generate coverage distribution plot
3.12. Write results summary (correlation stats, plots, interpretation)

### 3.3 Time Estimate

| Epic | Duration | Dependencies |
|------|----------|--------------|
| Epic 1: Coverage Measurement | 4 hours | None (standalone) |
| Epic 2: Per-Problem Evaluation | 8 hours | h-e1 models (available) |
| Epic 3: Correlation Analysis | 4 hours | Epic 1, Epic 2 |
| **Total** | **16 hours** | h-e1 (VALIDATED) |

**Justification:**
- Coverage measurement: Offline, parallelizable (CPU-bound)
- Per-problem evaluation: Reuses h-e1 models (GPU-bound, ~2-3 hours runtime)
- Correlation analysis: CPU-bound statistical tests (fast)

---

## 4. Success Metrics & Gate Evaluation

### 4.1 Primary Metrics

**Metric 1: Coverage Correlation**
- **Target:** Pearson r ≥ 0.77 (R² ≥ 0.6)
- **Test:** Two-tailed Pearson correlation test, α = 0.05
- **Interpretation:** Coverage explains ≥60% of variance in feedback advantage

**Metric 2: Coverage Variance**
- **Target:** HumanEval and MBPP differ by ≥10 pp average coverage
- **Test:** Two-sample t-test (HumanEval coverage vs MBPP coverage)
- **Interpretation:** Sufficient variance to test moderation hypothesis

### 4.2 Gate Evaluation (SHOULD_WORK)

**Pass Condition:**
- Pearson r ≥ 0.77 AND p < 0.05
- Coverage difference ≥10 pp AND statistically significant

**If PASS:**
- Coverage moderation hypothesis VALIDATED
- Confirms: Test suite quality moderates feedback requirements
- Implication: Lightweight feedback design should consider benchmark coverage

**If FAIL:**
- Coverage moderation hypothesis INVALID (not blocking)
- Does NOT fail main hypothesis (SHOULD_WORK gate)
- Alternative moderators: Problem difficulty, solution complexity, error distribution
- Action: Report null result, explore alternative moderators in discussion

### 4.3 Robustness Indicators

**Strong Evidence (r ≥ 0.77):**
- Difficulty-controlled partial correlation r ≥ 0.7
- Stratified analysis: both HumanEval and MBPP show negative correlation
- Secondary metrics (statement coverage) also correlate

**Weak Evidence (0.5 < r < 0.77):**
- Marginal correlation, coverage explains 25-60% variance
- Difficulty confound likely (partial correlation drops)
- Hypothesis partially supported but not decisive

**Null Evidence (r < 0.5):**
- Coverage does not explain feedback advantage
- Other factors dominate (difficulty, error types, model capacity)
- Hypothesis refuted, report null result

---

## 5. Implementation Resources

### 5.1 Exa Search Results

**MCP Server Used:** Exa Search (`mcp__exa__web_search_exa`, `mcp__exa__get_code_context_exa`)  
**Total Queries:** 4 queries across 3 priorities  
**Results Found:** 8 GitHub repos + 3 tutorials + 1 code context  

#### Coverage.py Implementation

1. **[VERIFIED - EXA]** coveragepy/coveragepy
   - URL: https://github.com/coveragepy/coveragepy
   - Stars: 3393
   - Language: Python
   - Search Query: "coverage.py branch coverage measurement Python implementation github"
   - Priority Level: Priority 1
   - Relevance: Official implementation of branch coverage measurement
   - Key Features: Branch coverage tracking, arc-based measurement, programmatic API
   - Adaptability: Direct integration via `Coverage` class
   - Last Updated: 2025-03 (active development)
   - Retrieved via: `mcp__exa__web_search_exa(query="coverage.py branch coverage measurement Python implementation github", numResults=8)`

2. **[VERIFIED - EXA - CODE_CONTEXT]** Coverage API Documentation
   - Retrieved via: `mcp__exa__get_code_context_exa(query="coverage.py branch coverage API Python code analysis", tokensNum=5000)`
   - API Pattern:
     ```python
     from coverage import Coverage
     cov = Coverage(branch=True)
     cov.start()
     # Execute code
     cov.stop()
     analysis = cov.analysis2(filename)
     # Returns: (executed_lines, missing_lines, excluded_lines, missing_branches)
     ```
   - Branch Statistics: `cov._analyze(filename).total_branches()`
   - Arc Measurement: Tracks (source_line, dest_line) transitions

#### Code Generation Evaluation Harnesses

3. **[VERIFIED - EXA]** openai/human-eval
   - URL: https://github.com/openai/human-eval
   - Stars: 3345
   - Language: Python
   - Search Query: "code generation test suite quality analysis per-problem pass@1 github"
   - Priority Level: Priority 1
   - Relevance: Standard HumanEval evaluation harness with pass@k estimator
   - Key Features: Unbiased pass@k estimator, execution sandbox
   - Integration: Reuse `estimate_pass_at_k()` function
   - Retrieved via: `mcp__exa__web_search_exa(query="code generation test suite quality analysis per-problem pass@1 github", numResults=8)`

4. **[VERIFIED - EXA]** bigcode-project/bigcode-evaluation-harness
   - URL: https://github.com/bigcode-project/bigcode-evaluation-harness
   - Stars: 500+ (estimated)
   - Language: Python
   - Search Query: "code generation test suite quality analysis per-problem pass@1 github"
   - Relevance: Multi-benchmark evaluation (HumanEval, MBPP, MultiPL-E)
   - Key Features: Per-problem metrics, execution runner, timeout handling
   - Integration: Use execution wrapper for sandbox isolation
   - Retrieved via: `mcp__exa__web_search_exa(query="code generation test suite quality analysis per-problem pass@1 github", numResults=8)`

5. **[VERIFIED - EXA]** microsoft/coverage-eval
   - URL: https://github.com/microsoft/coverage-eval
   - Stars: 25
   - Language: Python
   - Search Query: "HumanEval MBPP test coverage correlation feedback analysis"
   - Priority Level: Priority 1
   - Relevance: HumanEval augmented with coverage annotations (related work)
   - Key Features: Per-problem coverage annotations, coverage prediction task
   - Adaptability: Reference for coverage annotation format
   - Last Updated: 2023 (archived but usable)
   - Retrieved via: `mcp__exa__web_search_exa(query="HumanEval MBPP test coverage correlation feedback analysis", numResults=8)`

#### Tutorial Resources

6. **[VERIFIED - EXA - TUTORIAL]** "Branch coverage measurement — Coverage.py 7.15.3 documentation"
   - Source: Official Docs
   - URL: https://coverage.readthedocs.io/en/latest/branch.html
   - Search Query: "coverage.py branch coverage measurement Python implementation github"
   - Priority Level: Priority 3
   - Relevance: Explains branch coverage measurement, partial branches, pragmas
   - Key Insights: 
     - Branch coverage = actual transitions / possible transitions
     - Partial branches flagged in yellow (HTML report)
     - `# pragma: no branch` to suppress warnings
   - Retrieved via: `mcp__exa__web_search_exa(query="coverage.py branch coverage measurement Python implementation github", numResults=8)`

7. **[VERIFIED - EXA - TUTORIAL]** "Do Code Language Models Use Tests?" (arXiv:2607.26244)
   - Source: arXiv preprint
   - URL: https://arxiv.org/html/2607.26244v1
   - Search Query: "HumanEval MBPP test coverage correlation feedback analysis"
   - Relevance: Behavioral study of test-driven code generation (related research)
   - Key Insights: Tests as executable specifications, models react to test context
   - Retrieved via: `mcp__exa__web_search_exa(query="HumanEval MBPP test coverage correlation feedback analysis", numResults=8)`

### 5.2 Framework Analysis

**Coverage Measurement:**
- Primary tool: coverage.py (Python standard)
- Alternative: pytest-cov (pytest plugin wrapper)
- Chosen: coverage.py (programmatic API, branch mode, arc tracking)

**Code Execution:**
- Primary tool: BigCode evaluation harness (execution sandbox)
- Alternative: HumanEval execution.py (simpler, direct)
- Chosen: BigCode harness (timeout handling, multi-benchmark support)

**Statistical Analysis:**
- scipy.stats (Pearson correlation, t-tests, linear regression)
- matplotlib (scatter plots, histograms)

---

## 6. Expected Outcomes & Interpretation

### 6.1 Hypothesis-Confirming Results

**Strong Confirmation (r ≥ 0.77):**
- Coverage explains ≥60% of variance in feedback advantage
- Negative correlation: high coverage → low advantage (binary suffices)
- Stratified analysis: both HumanEval (high coverage) and MBPP (low coverage) show pattern
- Implication: Test suite quality IS a design factor for feedback granularity

**Example Result:**
```
Pearson r = -0.82, p < 0.001, R² = 0.67
HumanEval: mean coverage 78%, mean advantage -0.02 (binary ≈ error-type)
MBPP: mean coverage 52%, mean advantage +0.08 (error-type > binary)
```

### 6.2 Hypothesis-Refuting Results

**Null Result (r < 0.5):**
- Coverage does not explain feedback advantage
- Feedback advantage driven by other factors (difficulty, error types, model capacity)
- SHOULD_WORK gate allows null result (not blocking)

**Alternative Explanations:**
- Problem difficulty confound (harder problems → lower coverage AND lower pass@1)
- Error distribution skew (TypeError-dominated errors make error-type feedback redundant)
- Model capacity saturation (models can't exploit error-type hints regardless of coverage)

**Action if Null:**
- Report null result transparently
- Explore alternative moderators: solution complexity, error type distribution, problem difficulty
- Acknowledge coverage proxy limitations in discussion

### 6.3 Partial Confirmation (0.5 < r < 0.77)

**Moderate Evidence:**
- Coverage explains 25-60% of variance (marginal support)
- Other factors contribute (partial correlation drops after difficulty control)
- Coverage is A moderator, not THE moderator

**Interpretation:**
- Test suite quality matters but is not sole determinant
- Multi-factor model needed (coverage + difficulty + error types)
- Hypothesis partially supported, refinement needed

---

## 7. Limitations & Risks

### 7.1 Coverage Proxy Validity

**Risk:** Branch coverage % is a proxy for test quality, not a complete measure.

**Limitation:**
- Branch coverage does not capture semantic test quality (assertion diversity, edge case detection)
- High coverage with weak assertions (e.g., `assert result is not None`) provides false confidence
- Mutation testing (killing mutants) is a stronger proxy but computationally expensive

**Mitigation:**
- Report multiple coverage types (branch, statement, path)
- Acknowledge proxy limits in discussion
- If all metrics correlate, proxy validity strengthened

### 7.2 Problem Difficulty Confound

**Risk:** Coverage and difficulty may both correlate with feedback advantage, creating spurious correlation.

**Confound Path:**
- Harder problems → weaker reference solutions → lower coverage (incomplete edge cases)
- Harder problems → lower baseline pass@1 → larger room for feedback improvement

**Mitigation:**
- Difficulty-controlled partial correlation (regress out SFT baseline performance)
- If partial correlation remains strong, coverage effect is real
- If partial correlation drops, difficulty is confound

### 7.3 Small Sample Size (HumanEval)

**Risk:** HumanEval has only 164 problems (smaller than MBPP's 974).

**Impact:**
- Correlation test on HumanEval alone may lack statistical power
- Stratified analysis may be underpowered for HumanEval

**Mitigation:**
- Pooled analysis (HumanEval + MBPP combined, n=1138) for primary test
- Stratified analysis as robustness check (acknowledge power limits)
- If MBPP shows strong correlation but HumanEval is null, attribute to sample size

### 7.4 Model Reuse from h-e1

**Risk:** Models trained on HumanEval (h-e1) may overfit to HumanEval problems.

**Impact:**
- Per-problem pass@1 on HumanEval may be inflated
- Correlation test may conflate coverage with training set membership

**Mitigation:**
- Primary analysis on MBPP (held-out benchmark, not used in h-e1 training)
- HumanEval analysis as secondary check (acknowledge training set overlap)
- If MBPP correlation is strong, hypothesis holds regardless of HumanEval confound

---

## 8. Deliverables

### 8.1 Code Artifacts

1. `src/h-m3/coverage_measurement.py` - Coverage instrumentation script
2. `src/h-m3/per_problem_eval.py` - Per-problem pass@1 evaluation
3. `src/h-m3/correlation_analysis.py` - Statistical tests and visualization
4. `data/coverage_analysis/humaneval_coverage.json` - HumanEval coverage dataset
5. `data/coverage_analysis/mbpp_coverage.json` - MBPP coverage dataset
6. `data/h-m3/per_problem_results.json` - Per-problem pass@1 results (8 model-feedback combos)

### 8.2 Plots

1. `plots/h-m3_coverage_advantage_correlation.png` - Scatter plot (coverage vs advantage)
2. `plots/h-m3_coverage_distributions.png` - Coverage distribution (HumanEval vs MBPP)
3. `plots/h-m3_stratified_correlation.png` - Separate correlations per benchmark

### 8.3 Report

`docs/youra_research/h-m3/04_validation.md` - Includes:
- Coverage measurement results (mean, std, distribution)
- Per-problem evaluation results (pass@1 per model-feedback combo)
- Correlation test results (r, p-value, R²)
- Robustness checks (difficulty control, stratified analysis)
- Visualizations (embedded plots)
- Gate evaluation (PASS/FAIL for SHOULD_WORK gate)
- Interpretation and limitations

---

## 9. Archon Project Metadata

**Archon Document IDs:** (To be created in Phase 3)
- PRD: Not applicable (analysis task, not implementation)
- Architecture: Not applicable
- Logic: Not applicable
- Configuration: Not applicable

**Note:** h-m3 is primarily a data analysis task (correlation study), not a model implementation task. No new model training or architecture design required. Archon KB is used for reference patterns only, not for PRD/Architecture generation.

---

**End of Experiment Brief**
