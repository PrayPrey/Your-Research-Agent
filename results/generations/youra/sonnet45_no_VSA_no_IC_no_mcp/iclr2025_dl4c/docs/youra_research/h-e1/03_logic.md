# Logic Specification: h-e1

**Date:** 2026-08-25
**Author:** Phase 3 Logic Agent
**Hypothesis:** h-e1 (EXISTENCE - Correlation Infrastructure)
**PRD:** 03_prd.md

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - designing new APIs
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Dataset Loading [Complexity: 2, Budget: 8]

**Applied**: Standard HuggingFace datasets API + sampling

### API Signatures

```python
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass

@dataclass
class Problem:
    """Single problem instance."""
    id: str
    prompt: str
    tests: List[str]
    dataset: str

def load_humaneval(n_samples: int = 100) -> List[Problem]:
    """Load HumanEval problems. Returns first n_samples."""
    ...

def load_mbpp(n_samples: int = 100, seed: int = 42) -> List[Problem]:
    """Load MBPP problems. Random sample n_samples."""
    ...

def load_swe_bench(n_samples: int = 100, seed: int = 42) -> List[Problem]:
    """Load SWE-bench problems. Random sample n_samples."""
    ...

def load_all_datasets(n_samples: int = 100) -> Dict[str, List[Problem]]:
    """Load all three datasets. Returns dict keyed by dataset name."""
    ...
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | HuggingFace API wrapper | Load from `openai_humaneval`, `mbpp` datasets |
| L-1-2 | SWE-bench loader | Custom loader from GitHub or HF cache |
| L-1-3 | Sampling logic | First-n for HumanEval, random for others |
| L-1-4 | Format standardization | Convert to `Problem` dataclass |
| L-1-5 | Test case extraction | Parse test format per dataset |
| L-1-6 | Error handling | Retry on download failure |
| L-1-7 | Caching | Save loaded datasets locally |
| L-1-8 | Validation | Check n_samples loaded correctly |

---

## A-2: Code Generation [Complexity: 2, Budget: 6]

**Applied**: HuggingFace Transformers autoregressive generation

### API Signatures

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class CodeGenModel:
    """Wrapper for CodeGen-16B-mono."""
    
    def __init__(self, model_name: str = "Salesforce/codegen-16B-mono"):
        """Load model and tokenizer."""
        self.model: AutoModelForCausalLM
        self.tokenizer: AutoTokenizer
        self.device: str
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.8,
        top_p: float = 0.95,
        max_tokens: int = 512
    ) -> str:
        """Generate single code sample. Returns code string."""
        ...
    
    def batch_generate(
        self,
        prompts: List[str],
        batch_size: int = 8,
        **kwargs
    ) -> List[str]:
        """Generate code for batch of prompts. Returns list of code strings."""
        ...
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Model loading | Load checkpoint with device placement |
| L-2-2 | Tokenization | Encode prompts to input_ids |
| L-2-3 | Generation loop | Autoregressive sampling with temperature |
| L-2-4 | Decoding | Convert tokens to string, strip special tokens |
| L-2-5 | Batching | Batch prompts for efficiency |
| L-2-6 | Fallback | If OOM, fallback to CodeGen-2B-mono |

---

## A-3: Execution Feedback Collection [Complexity: 3, Budget: 10]

**Applied**: Subprocess execution with timeout + error handling

### API Signatures

```python
from typing import Optional
import subprocess

def execute_code(code: str, tests: List[str], timeout: int = 5) -> bool:
    """
    Execute code against test cases.
    
    Args:
        code: Generated Python code
        tests: List of test assertions (e.g., "assert func(1) == 2")
        timeout: Execution timeout in seconds
    
    Returns:
        True if all tests pass, False otherwise
    """
    ...

def collect_execution_feedback(
    problems: List[Problem],
    generated_codes: List[str]
) -> List[int]:
    """
    Collect binary execution results.
    
    Args:
        problems: List of Problem instances
        generated_codes: Corresponding generated code strings
    
    Returns:
        List of 0/1 values (0=fail, 1=pass). Shape: [N]
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| generated_codes | [N] | N=100 per dataset |
| execution_results | [N] | Binary 0/1 array |

### Pseudo-code

```
For each (code, tests) pair:
  1. Create temp file with code + tests
  2. Run `python temp_file.py` in subprocess
  3. Capture stdout/stderr
  4. If timeout or error: result = 0
  5. If all tests pass: result = 1
  6. Return result
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Temp file creation | Write code + tests to temp .py file |
| L-3-2 | Subprocess execution | Run with timeout |
| L-3-3 | Timeout handling | Kill process after timeout |
| L-3-4 | Error parsing | Detect syntax/runtime errors |
| L-3-5 | Test assertion parsing | Combine code with test assertions |
| L-3-6 | Result aggregation | AND logic across all tests |
| L-3-7 | Logging | Log errors for debugging |
| L-3-8 | Cleanup | Remove temp files |
| L-3-9 | Parallel execution | Use multiprocessing for speed |
| L-3-10 | Safety | Restrict file I/O, network access |

---

## A-4: AI Feedback Collection [Complexity: 2, Budget: 6]

**Applied**: OpenAI API as reward model (GPT-3.5-turbo as judge)

### API Signatures

```python
from openai import OpenAI

class AIRewardModel:
    """LLM-as-judge reward model."""
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        """Initialize OpenAI client."""
        self.client: OpenAI
        self.model: str
    
    def score(self, prompt: str, code: str) -> float:
        """
        Score code quality for given prompt.
        
        Args:
            prompt: Original problem prompt
            code: Generated code
        
        Returns:
            Score in [0, 1] range
        """
        ...
    
    def batch_score(
        self,
        prompts: List[str],
        codes: List[str],
        batch_size: int = 10
    ) -> List[float]:
        """Score multiple (prompt, code) pairs. Returns scores in [0, 1]."""
        ...
```

### Pseudo-code

```
For each (prompt, code) pair:
  1. Construct judge prompt:
     "Rate the following code solution for correctness and quality (0-10):
      Problem: {prompt}
      Code: {code}
      Score:"
  2. Call GPT-3.5-turbo with max_tokens=10
  3. Parse numeric score from response
  4. Normalize to [0, 1] by dividing by 10
  5. Handle parse errors: default score = 0.5
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | OpenAI client setup | API key from env var |
| L-4-2 | Judge prompt template | Design scoring prompt |
| L-4-3 | API call | Send request, handle rate limits |
| L-4-4 | Response parsing | Extract numeric score |
| L-4-5 | Normalization | Scale to [0, 1] |
| L-4-6 | Batching | Batch requests for efficiency |

---

## A-5: Human Feedback Simulation [Complexity: 2, Budget: 6]

**Applied**: Execution-based heuristic + uniform noise

### API Signatures

```python
import numpy as np

def simulate_human_ratings(
    code: str,
    execution_result: int,
    num_raters: int = 3,
    noise_level: float = 0.2,
    seed: Optional[int] = None
) -> List[float]:
    """
    Simulate human ratings for single code sample.
    
    Args:
        code: Generated code (unused in PoC, for API compatibility)
        execution_result: Binary pass/fail (0 or 1)
        num_raters: Number of simulated raters
        noise_level: Noise magnitude (±noise_level uniform)
        seed: Random seed for reproducibility
    
    Returns:
        List of ratings in [0, 1]. Shape: [num_raters]
    """
    ...

def collect_human_feedback(
    problems: List[Problem],
    generated_codes: List[str],
    execution_results: List[int],
    num_raters: int = 3
) -> Tuple[List[float], float]:
    """
    Collect simulated human ratings and compute inter-rater reliability.
    
    Args:
        problems: List of Problem instances
        generated_codes: Generated code strings
        execution_results: Binary execution results
        num_raters: Number of simulated raters per sample
    
    Returns:
        Tuple of (mean_ratings, cohen_kappa)
        - mean_ratings: [N] averaged ratings per sample
        - cohen_kappa: Inter-rater reliability score
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| execution_results | [N] | Input binary results |
| ratings_per_sample | [N, R] | R=3 raters per sample |
| mean_ratings | [N] | Averaged across raters |

### Pseudo-code

```
For each sample:
  1. base_score = execution_result (0 or 1)
  2. For each rater:
       noise = uniform(-0.2, 0.2)
       rating = clip(base_score + noise, 0, 1)
  3. Store [rating_1, rating_2, rating_3]
  4. mean_rating = mean(ratings)

Compute Cohen's kappa:
  1. Discretize ratings to binary: threshold at 0.5
  2. Compute pairwise kappa for all rater pairs
  3. Return average kappa across pairs
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Base score generation | Use execution result as base |
| L-5-2 | Noise sampling | Uniform noise per rater |
| L-5-3 | Clipping | Ensure [0, 1] bounds |
| L-5-4 | Rating aggregation | Mean across raters |
| L-5-5 | Cohen's kappa computation | sklearn.metrics implementation |
| L-5-6 | Seed management | Reproducible randomness |

---

## A-6: Correlation Analysis [Complexity: 3, Budget: 10]

**Applied**: Scipy Pearson r + bootstrap resampling

### API Signatures

```python
from scipy.stats import pearsonr
from typing import Dict, Tuple

@dataclass
class CorrelationResult:
    """Correlation statistics."""
    r: float
    p_value: float
    ci_lower: float
    ci_upper: float

def compute_correlations(
    exec_feedback: List[int],
    ai_feedback: List[float],
    human_feedback: List[float]
) -> Dict[str, CorrelationResult]:
    """
    Compute all pairwise correlations with bootstrap CIs.
    
    Args:
        exec_feedback: Binary execution results [N]
        ai_feedback: AI reward scores [N]
        human_feedback: Human ratings [N]
    
    Returns:
        Dict with keys: 'exec_human', 'ai_human', 'exec_ai'
    """
    ...

def bootstrap_ci(
    data1: np.ndarray,
    data2: np.ndarray,
    n_iterations: int = 1000,
    ci_level: float = 0.95,
    seed: int = 42
) -> Tuple[float, float]:
    """
    Compute bootstrap confidence interval for correlation.
    
    Args:
        data1: First variable [N]
        data2: Second variable [N]
        n_iterations: Number of bootstrap samples
        ci_level: Confidence level (0.95 for 95% CI)
        seed: Random seed
    
    Returns:
        (ci_lower, ci_upper)
    """
    ...

def analyze_dataset(
    problems: List[Problem],
    exec_feedback: List[int],
    ai_feedback: List[float],
    human_feedback: List[float]
) -> Dict[str, Any]:
    """
    Full correlation analysis for single dataset.
    
    Returns:
        {
            'correlations': {pair: CorrelationResult},
            'sample_size': int,
            'cohen_kappa': float
        }
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| exec_feedback | [N] | Binary 0/1 |
| ai_feedback | [N] | Continuous [0, 1] |
| human_feedback | [N] | Continuous [0, 1] |
| bootstrap_samples | [B, N] | B=1000 iterations |
| bootstrap_rs | [B] | r values per iteration |

### Pseudo-code

```
compute_correlations(exec, ai, human):
  1. pairs = [('exec', exec, 'human', human),
              ('ai', ai, 'human', human),
              ('exec', exec, 'ai', ai)]
  2. For each pair:
       r, p = pearsonr(data1, data2)
       ci_lower, ci_upper = bootstrap_ci(data1, data2)
       store CorrelationResult(r, p, ci_lower, ci_upper)
  3. Return dict of results

bootstrap_ci(data1, data2, n_iter):
  1. rs = []
  2. For i in range(n_iter):
       indices = random.choice(N, size=N, replace=True)
       sampled_r, _ = pearsonr(data1[indices], data2[indices])
       rs.append(sampled_r)
  3. ci_lower = percentile(rs, 2.5)
  4. ci_upper = percentile(rs, 97.5)
  5. Return (ci_lower, ci_upper)
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Pearson r computation | scipy.stats.pearsonr wrapper |
| L-6-2 | P-value extraction | Extract from scipy output |
| L-6-3 | Bootstrap sampling | Random resampling with replacement |
| L-6-4 | CI percentile computation | 2.5th and 97.5th percentiles |
| L-6-5 | Pairwise iteration | Loop over 3 feedback pairs |
| L-6-6 | Result aggregation | Collect into dict |
| L-6-7 | Input validation | Check equal lengths, no NaN |
| L-6-8 | Seed management | Reproducible bootstrap |
| L-6-9 | Correlation matrix construction | 3x3 matrix for visualization |
| L-6-10 | Statistical summary | Mean, std, min, max per feedback type |

---

## A-7: Gate Evaluation [Complexity: 1, Budget: 4]

**Applied**: Simple threshold checks

### API Signatures

```python
@dataclass
class GateResult:
    """Gate evaluation result."""
    passed: bool
    correlations_significant: bool
    kappa_sufficient: bool
    details: Dict[str, Any]

def evaluate_gate(
    results: Dict[str, Dict[str, Any]],
    alpha: float = 0.05,
    kappa_threshold: float = 0.6
) -> GateResult:
    """
    Evaluate MUST_WORK gate criteria.
    
    Args:
        results: Analysis results for all datasets
        alpha: P-value threshold for significance
        kappa_threshold: Minimum inter-rater reliability
    
    Returns:
        GateResult with pass/fail and details
    """
    ...

def write_validation_report(
    gate_result: GateResult,
    results: Dict[str, Dict[str, Any]],
    output_path: str
) -> None:
    """Write 04_validation.md with gate evaluation results."""
    ...
```

### Pseudo-code

```
evaluate_gate(results):
  1. all_p_significant = True
  2. For each dataset in results:
       For each pair in dataset['correlations']:
         if pair.p_value >= alpha:
           all_p_significant = False
  
  3. all_kappa_good = True
  4. For each dataset in results:
       if dataset['cohen_kappa'] <= kappa_threshold:
         all_kappa_good = False
  
  5. passed = all_p_significant AND all_kappa_good
  6. Return GateResult(passed, all_p_significant, all_kappa_good, details)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | P-value checks | Verify all p < 0.05 |
| L-7-2 | Kappa checks | Verify all kappa > 0.6 |
| L-7-3 | Gate logic | AND all conditions |
| L-7-4 | Report writing | Format markdown output |

---

## A-8: Visualization [Complexity: 2, Budget: 6]

**Applied**: Matplotlib + Seaborn heatmaps

### API Signatures

```python
import matplotlib.pyplot as plt
import seaborn as sns

def plot_correlation_matrix(
    corr_matrix: np.ndarray,
    labels: List[str],
    title: str,
    output_path: str
) -> None:
    """
    Plot correlation matrix heatmap.
    
    Args:
        corr_matrix: 3x3 correlation matrix
        labels: ['Execution', 'AI', 'Human']
        title: Plot title (e.g., 'HumanEval Correlations')
        output_path: PNG file path
    """
    ...

def plot_scatter(
    x: np.ndarray,
    y: np.ndarray,
    x_label: str,
    y_label: str,
    title: str,
    output_path: str,
    show_regression: bool = True
) -> None:
    """
    Plot scatter with optional regression line.
    
    Args:
        x: X-axis data [N]
        y: Y-axis data [N]
        x_label: X-axis label
        y_label: Y-axis label
        title: Plot title
        output_path: PNG file path
        show_regression: If True, add regression line + 95% CI
    """
    ...

def plot_bootstrap_ci(
    correlations: Dict[str, CorrelationResult],
    dataset_name: str,
    output_path: str
) -> None:
    """
    Plot bar chart with error bars (bootstrap CI).
    
    Args:
        correlations: Dict of correlation results
        dataset_name: Dataset name for title
        output_path: PNG file path
    """
    ...

def plot_distributions(
    exec_feedback: List[int],
    ai_feedback: List[float],
    human_feedback: List[float],
    dataset_name: str,
    output_path: str
) -> None:
    """
    Plot distribution comparison (histograms + boxplots).
    
    Args:
        exec_feedback: Execution results [N]
        ai_feedback: AI scores [N]
        human_feedback: Human ratings [N]
        dataset_name: Dataset name for title
        output_path: PNG file path
    """
    ...
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | Heatmap plotting | Seaborn heatmap with annotations |
| L-8-2 | Scatter plotting | Matplotlib scatter + regression |
| L-8-3 | CI bar chart | Error bars from bootstrap CIs |
| L-8-4 | Distribution plots | Histograms and boxplots |
| L-8-5 | Figure styling | Labels, legends, font sizes |
| L-8-6 | File I/O | Save to PNG with dpi=300 |

---

## Main Orchestration

**Applied**: Sequential pipeline execution

### API Signatures

```python
def run_experiment(
    n_samples: int = 100,
    output_dir: str = "docs/youra_research/h-e1",
    seed: int = 42
) -> GateResult:
    """
    Run full correlation experiment pipeline.
    
    Pipeline:
      1. Load datasets (3 datasets)
      2. Generate code samples (300 total)
      3. Collect execution feedback (300 binary values)
      4. Collect AI feedback (300 scores)
      5. Simulate human feedback (300 ratings + kappa)
      6. Analyze correlations per dataset (9 total correlations)
      7. Evaluate gate (pass/fail)
      8. Generate visualizations (18 PNG files)
      9. Write validation report
    
    Args:
        n_samples: Samples per dataset
        output_dir: Output directory for results
        seed: Random seed for reproducibility
    
    Returns:
        GateResult with final pass/fail status
    """
    ...
```

### Pseudo-code

```
run_experiment():
  1. datasets = load_all_datasets(n=100)
     # Returns: {'humaneval': [Problem], 'mbpp': [Problem], 'swe_bench': [Problem]}
  
  2. model = CodeGenModel()
  
  3. all_results = {}
  4. For dataset_name, problems in datasets.items():
       # Generate code
       codes = model.batch_generate([p.prompt for p in problems])
       
       # Collect feedback
       exec_fb = collect_execution_feedback(problems, codes)
       ai_fb = model_ai.batch_score([p.prompt for p in problems], codes)
       human_fb, kappa = collect_human_feedback(problems, codes, exec_fb)
       
       # Analyze
       results = analyze_dataset(problems, exec_fb, ai_fb, human_fb)
       results['cohen_kappa'] = kappa
       all_results[dataset_name] = results
       
       # Visualize
       plot_correlation_matrix(results['corr_matrix'], dataset_name)
       plot_scatter(exec_fb, human_fb, dataset_name)
       # ... (18 total plots)
  
  5. gate = evaluate_gate(all_results)
  
  6. write_validation_report(gate, all_results, output_dir)
  
  7. Return gate
```

---

## Statistical Computation Details

### Pearson Correlation

```python
from scipy.stats import pearsonr

# Standard implementation
r, p = pearsonr(data1, data2)

# Formula (for reference):
# r = cov(X, Y) / (std(X) * std(Y))
# H0: r = 0 (no correlation)
# p-value from t-distribution with df = N-2
```

### Bootstrap Confidence Interval

```python
import numpy as np

def bootstrap_ci(data1, data2, n_iter=1000):
    rs = []
    for _ in range(n_iter):
        idx = np.random.choice(len(data1), len(data1), replace=True)
        r, _ = pearsonr(data1[idx], data2[idx])
        rs.append(r)
    return np.percentile(rs, [2.5, 97.5])

# Theory:
# - Nonparametric method (no distribution assumption)
# - 95% CI = [2.5th percentile, 97.5th percentile] of bootstrap rs
# - Captures sampling uncertainty
```

### Cohen's Kappa (Inter-rater Reliability)

```python
from sklearn.metrics import cohen_kappa_score

# For pairwise raters:
kappa = cohen_kappa_score(rater1, rater2)

# For multiple raters (average pairwise):
kappas = []
for i in range(num_raters):
    for j in range(i+1, num_raters):
        kappas.append(cohen_kappa_score(rater_i, rater_j))
avg_kappa = np.mean(kappas)

# Interpretation:
# < 0.0: No agreement
# 0.0-0.2: Slight
# 0.2-0.4: Fair
# 0.4-0.6: Moderate
# 0.6-0.8: Substantial
# 0.8-1.0: Almost perfect
# Threshold: >0.6 for acceptable reliability
```

---

## Error Handling Strategy

### Dataset Loading Errors
```python
try:
    dataset = load_dataset("openai_humaneval")
except Exception as e:
    logger.error(f"Failed to load dataset: {e}")
    # Retry with exponential backoff
    for attempt in range(3):
        time.sleep(2 ** attempt)
        dataset = load_dataset("openai_humaneval")
```

### Code Execution Errors
```python
try:
    result = subprocess.run(
        ["python", temp_file],
        timeout=5,
        capture_output=True
    )
    return result.returncode == 0
except subprocess.TimeoutExpired:
    return False  # Timeout counts as fail
except Exception as e:
    logger.warning(f"Execution error: {e}")
    return False
```

### Model OOM Errors
```python
try:
    model = AutoModelForCausalLM.from_pretrained("Salesforce/codegen-16B-mono")
except RuntimeError as e:
    if "out of memory" in str(e).lower():
        logger.warning("OOM on 16B, falling back to 2B")
        model = AutoModelForCausalLM.from_pretrained("Salesforce/codegen-2B-mono")
    else:
        raise
```

---

## Data Caching Strategy

### Generated Code Caching
```python
import json

def cache_generated_samples(problems, codes, output_path):
    """Save generated samples for reproducibility."""
    data = [
        {
            'problem_id': p.id,
            'prompt': p.prompt,
            'code': c,
            'dataset': p.dataset
        }
        for p, c in zip(problems, codes)
    ]
    with open(output_path, 'w') as f:
        for item in data:
            f.write(json.dumps(item) + '\n')

def load_cached_samples(input_path):
    """Load cached samples to skip generation."""
    with open(input_path) as f:
        return [json.loads(line) for line in f]
```

### Feedback Results Caching
```python
def cache_feedback_results(exec_fb, ai_fb, human_fb, output_path):
    """Save all feedback for later analysis."""
    data = {
        'execution': exec_fb,
        'ai': ai_fb,
        'human': human_fb,
        'timestamp': datetime.now().isoformat()
    }
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
```

---

## Total Budget Usage

| Task | Complexity | Budget | Used |
|------|------------|--------|------|
| A-1: Dataset Loading | 2 | 8 | 8 |
| A-2: Code Generation | 2 | 6 | 6 |
| A-3: Execution Feedback | 3 | 10 | 10 |
| A-4: AI Feedback | 2 | 6 | 6 |
| A-5: Human Feedback Simulation | 2 | 6 | 6 |
| A-6: Correlation Analysis | 3 | 10 | 10 |
| A-7: Gate Evaluation | 1 | 4 | 4 |
| A-8: Visualization | 2 | 6 | 6 |
| **TOTAL** | **17** | **56** | **56** |

---

**Document Version:** 1.0
**Next Phase:** Phase 4 Implementation
