# Logic Specification: h-m3 Coverage-Advantage Correlation Study

**Hypothesis ID:** h-m3  
**Type:** MECHANISM (Data Analysis)  
**Date:** 2026-08-19

---

## 1. Core Logic Overview

**Pipeline:**
1. Coverage Measurement: `coverage.py` instrumentation → branch statistics
2. Per-Problem Evaluation: Model inference → test execution → pass@1 estimation
3. Correlation Analysis: Statistical tests → gate verdict

**No training logic.** Reuse h-e1 models.

---

## 2. Module Logic Specifications

### Module 1: Coverage Measurement

**Function:** `measure_branch_coverage(problem_code: str, test_suite: str) -> dict`

**Algorithm:**

```python
from coverage import Coverage
import tempfile
import os

def measure_branch_coverage(problem_code: str, test_suite: str, problem_id: str) -> dict:
    """
    Measure branch coverage for a single problem.
    
    Input:
        problem_code: Reference solution (canonical_solution)
        test_suite: Test cases (test field)
        problem_id: Problem identifier
    
    Output:
        {
            'branch_coverage_pct': float,
            'total_branches': int,
            'covered_branches': int,
            'statement_coverage_pct': float,
            'missing_branches': list
        }
    """
    # Create temp file with problem code + tests
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
        
        statement_coverage_pct = (
            len(executed_lines) / (len(executed_lines) + len(missing_lines)) * 100
        ) if (len(executed_lines) + len(missing_lines)) > 0 else 100.0
        
        return {
            'branch_coverage_pct': branch_coverage_pct,
            'total_branches': total_branches,
            'covered_branches': covered_branches,
            'statement_coverage_pct': statement_coverage_pct,
            'missing_branches': list(missing_branches)
        }
    finally:
        os.unlink(code_file)
```

**Edge Cases:**
- Zero branches (trivial solution): Return 100% coverage
- Syntax error in reference solution: Catch, log, return None
- Timeout (60s): Kill coverage.py, return None

**Parallelization:**
```python
from multiprocessing import Pool

def measure_all_problems(problems: list) -> dict:
    with Pool(processes=os.cpu_count()) as pool:
        results = pool.starmap(
            measure_branch_coverage,
            [(p['canonical_solution'], p['test'], p['problem_id']) for p in problems]
        )
    return {p['problem_id']: r for p, r in zip(problems, results) if r is not None}
```

### Module 2: Per-Problem Evaluation

**Function:** `estimate_pass_at_k(num_samples: int, num_correct: int, k: int = 1) -> float`

**Algorithm (Unbiased Estimator):**

```python
import numpy as np

def estimate_pass_at_k(num_samples: int, num_correct: int, k: int = 1) -> float:
    """
    Unbiased pass@k estimator (HumanEval paper).
    
    Formula: 1 - C(n-c, k) / C(n, k)
    where n = num_samples, c = num_correct
    
    Edge cases:
    - If n - c < k: return 1.0 (all samples correct or near-all)
    - If c = 0: return 0.0 (no correct samples)
    """
    if num_samples - num_correct < k:
        return 1.0
    
    # Compute C(n-c, k) / C(n, k) using log-space for numerical stability
    # C(n, k) = n! / (k! * (n-k)!)
    # Product formula: 1 - prod_{i=1}^{k} (1 - k / (n - c + i))
    return 1.0 - np.prod(1.0 - k / np.arange(num_samples - num_correct + 1, num_samples + 1))
```

**Function:** `evaluate_per_problem_pass_at_1(model, problems: list, num_samples: int = 20) -> dict`

**Algorithm:**

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

def evaluate_per_problem_pass_at_1(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    problems: list,
    num_samples: int = 20
) -> dict:
    """
    Evaluate per-problem pass@1 for a model.
    
    Input:
        model: Trained code generation model
        tokenizer: Model tokenizer
        problems: List of {problem_id, prompt, test_suite}
        num_samples: Generations per problem (default 20)
    
    Output:
        {
            problem_id: {
                'pass@1': float,
                'num_correct': int,
                'num_samples': int
            }
        }
    """
    results = {}
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(device)
    model.eval()
    
    for problem in problems:
        num_correct = 0
        
        # Generate N samples
        for _ in range(num_samples):
            # Tokenize prompt
            inputs = tokenizer(problem['prompt'], return_tensors='pt').to(device)
            
            # Generate code (temperature 0.8, max 512 tokens)
            with torch.no_grad():
                outputs = model.generate(
                    inputs['input_ids'],
                    max_length=512,
                    temperature=0.8,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            generated_code = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
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

**Function:** `execute_tests(generated_code: str, test_suite: str) -> bool`

**Sandbox Execution (Timeout 5s):**

```python
import subprocess
import tempfile
import os

def execute_tests(generated_code: str, test_suite: str) -> bool:
    """
    Execute generated code against test suite in sandbox.
    
    Returns True if all tests pass, False otherwise.
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(generated_code)
        f.write('\n\n')
        f.write(test_suite)
        test_file = f.name
    
    try:
        # Run tests with timeout
        result = subprocess.run(
            ['python', test_file],
            timeout=5,
            capture_output=True,
            text=True
        )
        
        # Check if all tests passed (exit code 0, no errors)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False
    finally:
        os.unlink(test_file)
```

### Module 3: Correlation Analysis

**Function:** `compute_feedback_advantage(binary_results: dict, error_type_results: dict) -> dict`

**Algorithm:**

```python
def compute_feedback_advantage(binary_results: dict, error_type_results: dict) -> dict:
    """
    Compute per-problem feedback-type advantage.
    
    Δ_i = error_type_pass@1_i - binary_pass@1_i
    
    Positive Δ: error-type feedback helped
    Negative Δ: binary feedback was better (or tied)
    Zero Δ: no difference
    """
    advantages = {}
    
    for problem_id in binary_results:
        if problem_id not in error_type_results:
            continue  # Skip if missing in either dataset
        
        delta = error_type_results[problem_id]['pass@1'] - binary_results[problem_id]['pass@1']
        
        advantages[problem_id] = {
            'advantage': delta,
            'binary_pass@1': binary_results[problem_id]['pass@1'],
            'error_type_pass@1': error_type_results[problem_id]['pass@1']
        }
    
    return advantages
```

**Function:** `test_coverage_correlation(coverage_data: dict, advantage_data: dict) -> dict`

**Algorithm:**

```python
from scipy.stats import pearsonr

def test_coverage_correlation(coverage_data: dict, advantage_data: dict) -> dict:
    """
    Test coverage-advantage correlation.
    
    H0: Coverage does not explain feedback advantage (r = 0)
    H1: Coverage explains ≥60% of variance (r ≥ 0.77)
    
    Expected pattern: Negative correlation
    (higher coverage → lower advantage, binary suffices)
    """
    # Extract matched pairs (problems in both datasets)
    problem_ids = set(coverage_data.keys()) & set(advantage_data.keys())
    
    coverage_values = [coverage_data[pid]['branch_coverage_pct'] for pid in problem_ids]
    advantage_values = [advantage_data[pid]['advantage'] for pid in problem_ids]
    
    # Pearson correlation
    r, p_value = pearsonr(coverage_values, advantage_values)
    
    # Success criterion
    success = (abs(r) >= 0.77) and (p_value < 0.05)
    
    # Expected direction: negative (high coverage → low advantage)
    expected_direction = r < 0
    
    return {
        'pearson_r': r,
        'r_squared': r**2,
        'p_value': p_value,
        'n_problems': len(problem_ids),
        'success': success,
        'expected_direction': expected_direction,
        'criterion': 'abs(r) ≥ 0.77, p < 0.05, r < 0 (negative correlation)'
    }
```

**Robustness Check:** Partial Correlation (Difficulty Control)

```python
from scipy.stats import pearsonr
import numpy as np

def partial_correlation_difficulty_controlled(
    coverage: list,
    advantage: list,
    sft_baseline_perf: list
) -> tuple:
    """
    Partial correlation controlling for baseline SFT performance.
    
    Residualize coverage and advantage on SFT baseline, then correlate.
    """
    # Convert to numpy arrays
    coverage = np.array(coverage)
    advantage = np.array(advantage)
    sft_baseline = np.array(sft_baseline_perf)
    
    # Linear regression: coverage ~ sft_baseline
    cov_coef = np.polyfit(sft_baseline, coverage, deg=1)
    coverage_pred = np.polyval(cov_coef, sft_baseline)
    coverage_residuals = coverage - coverage_pred
    
    # Linear regression: advantage ~ sft_baseline
    adv_coef = np.polyfit(sft_baseline, advantage, deg=1)
    advantage_pred = np.polyval(adv_coef, sft_baseline)
    advantage_residuals = advantage - advantage_pred
    
    # Correlation on residuals
    r_partial, p_partial = pearsonr(coverage_residuals, advantage_residuals)
    
    return r_partial, p_partial
```

---

## 3. Statistical Logic

### Pearson Correlation Test

**Null Hypothesis (H0):** Coverage does not explain feedback advantage (r = 0).

**Alternative Hypothesis (H1):** Coverage explains ≥60% variance (|r| ≥ 0.77).

**Test Statistic:**
- Pearson r = cov(X, Y) / (σ_X * σ_Y)
- Where X = coverage_pct, Y = feedback_advantage

**Significance Level:** α = 0.05 (two-tailed)

**Success Criterion:**
- PASS: |r| ≥ 0.77 AND p < 0.05
- Expected direction: r < 0 (negative correlation)

### Coverage Difference Test

**Null Hypothesis (H0):** HumanEval and MBPP have equal mean coverage.

**Alternative Hypothesis (H1):** |mean_HumanEval - mean_MBPP| ≥ 10 pp.

**Test:** Two-sample t-test (unpaired, two-tailed)

**Criterion:** p < 0.05 AND |mean_diff| ≥ 10 pp

---

## 4. Gate Evaluation Logic

**SHOULD_WORK Gate:**

```python
def evaluate_gate(correlation_result: dict, coverage_diff_result: dict) -> str:
    """
    Evaluate SHOULD_WORK gate.
    
    PASS conditions:
    1. Pearson r ≥ 0.77 (R² ≥ 0.6)
    2. p < 0.05 (statistically significant)
    3. Coverage difference ≥ 10 pp (sufficient variance)
    
    FAIL: Null result (r < 0.5) → not blocking (SHOULD_WORK)
    """
    r = abs(correlation_result['pearson_r'])
    p = correlation_result['p_value']
    coverage_diff = abs(coverage_diff_result['mean_diff'])
    
    if r >= 0.77 and p < 0.05 and coverage_diff >= 10:
        return "PASS"
    elif r < 0.5:
        return "FAIL_NULL_RESULT"  # Not blocking
    else:
        return "FAIL_MARGINAL"  # Marginal evidence (0.5 < r < 0.77)
```

**Verdict Interpretation:**
- **PASS:** Coverage moderation validated → test quality IS a design factor
- **FAIL_NULL_RESULT:** Coverage does not explain advantage → explore alternative moderators
- **FAIL_MARGINAL:** Partial support (25-60% variance explained) → multi-factor model needed

---

## 5. Visualization Logic

### Scatter Plot: Coverage vs Advantage

```python
import matplotlib.pyplot as plt
from scipy.stats import linregress

def plot_coverage_advantage_correlation(
    coverage_data: dict,
    advantage_data: dict,
    r: float,
    p: float
) -> None:
    """
    Scatter plot: branch coverage (x) vs feedback advantage (y).
    """
    problem_ids = set(coverage_data.keys()) & set(advantage_data.keys())
    
    coverage_values = [coverage_data[pid]['branch_coverage_pct'] for pid in problem_ids]
    advantage_values = [advantage_data[pid]['advantage'] for pid in problem_ids]
    
    plt.figure(figsize=(8, 6))
    plt.scatter(coverage_values, advantage_values, alpha=0.6, s=30, color='steelblue')
    plt.xlabel('Branch Coverage (%)')
    plt.ylabel('Feedback Advantage (error-type - binary pass@1)')
    plt.title(f'Coverage-Advantage Correlation (r={r:.2f}, p={p:.3f})')
    plt.axhline(y=0, color='gray', linestyle='--', linewidth=1)
    
    # Linear regression line
    slope, intercept, _, _, _ = linregress(coverage_values, advantage_values)
    x_line = np.linspace(min(coverage_values), max(coverage_values), 100)
    y_line = slope * x_line + intercept
    plt.plot(x_line, y_line, color='red', linewidth=2, label=f'y={slope:.3f}x+{intercept:.3f}')
    plt.legend()
    
    plt.savefig('plots/h-m3_coverage_advantage_correlation.png', dpi=300, bbox_inches='tight')
```

### Histogram: Coverage Distributions

```python
def plot_coverage_distributions(humaneval_coverage: list, mbpp_coverage: list) -> None:
    """
    Histogram comparing HumanEval vs MBPP coverage distributions.
    """
    plt.figure(figsize=(10, 5))
    plt.hist(humaneval_coverage, bins=20, alpha=0.7, label='HumanEval', color='blue')
    plt.hist(mbpp_coverage, bins=20, alpha=0.7, label='MBPP', color='orange')
    plt.xlabel('Branch Coverage (%)')
    plt.ylabel('Frequency')
    plt.title('Coverage Distribution: HumanEval vs MBPP')
    plt.legend()
    
    # Annotate means
    mean_he = np.mean(humaneval_coverage)
    mean_mbpp = np.mean(mbpp_coverage)
    plt.axvline(mean_he, color='blue', linestyle='--', linewidth=2, label=f'HumanEval mean={mean_he:.1f}%')
    plt.axvline(mean_mbpp, color='orange', linestyle='--', linewidth=2, label=f'MBPP mean={mean_mbpp:.1f}%')
    plt.legend()
    
    plt.savefig('plots/h-m3_coverage_distributions.png', dpi=300, bbox_inches='tight')
```

---

## 6. Edge Case Handling

**Coverage Measurement:**
- Zero branches (trivial solution): `branch_coverage_pct = 100.0`
- Syntax error: Log warning, skip problem, return `None`
- Infinite loop: Timeout after 60s, return `None`

**Per-Problem Evaluation:**
- Model inference failure: Log error, set `num_correct = 0`
- Test execution timeout (5s): Count as incorrect
- Syntax error in generated code: Count as incorrect

**Correlation Analysis:**
- Mismatched problem IDs: Use intersection only
- NaN values: Filter out before correlation test
- Sample size < 100: Log warning (underpowered)

---

**End of Logic Specification**
