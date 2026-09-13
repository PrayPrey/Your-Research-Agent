# Logic Design: h-m1

**Date:** 2026-08-25
**Author:** Phase 3 Implementation Planning
**Hypothesis:** h-m1 - MECHANISM hypothesis on specification completeness and test-intent capture
**PRD:** h-m1/03_prd.md

---

## Overview

This document specifies algorithms and data structures for h-m1 disagreement analysis. Reuses h-e1 code generation and feedback collection infrastructure, adds new components for disagreement extraction, qualitative coding, and statistical comparison.

**Design Philosophy (PoC):**
- Reuse h-e1 APIs (generators, feedback collectors, loaders)
- Minimal new code for disagreement analysis
- Manual qualitative coding (no automation for PoC)
- Standard scipy statistical tests

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (extending h-e1)
**Status:** API signatures verified from h-e1 code
**Analyzed Path:** docs/youra_research/h-e1/code/
**Relevant Symbols:**
- `data.loader.load_humaneval(n_samples: int = 100) -> List[Problem]`
- `data.loader.load_mbpp(n_samples: int = 100, seed: int = 42) -> List[Problem]`
- `models.generator.CodeGenModel.generate(prompt: str, temperature: float = 0.8, max_tokens: int = 256) -> str`
- `eval.feedback.execute_code(code: str, tests: List[str], timeout: int = 5) -> int`
- `eval.feedback.ai_score(prompt: str, code: str) -> float`
- `eval.feedback.simulate_human_ratings(code: str, execution_result: int, num_raters: int = 3, seed: int = None) -> List[float]`

---

## External Dependencies (h-e1)

### API Signatures (From Actual Code)

```python
# From: h-e1/code/data/loader.py
@dataclass
class Problem:
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

# From: h-e1/code/models/generator.py
class CodeGenModel:
    def __init__(self, model_name: str = "Salesforce/codegen-350M-mono"):
        """Load model and tokenizer."""
        ...

    def generate(
        self,
        prompt: str,
        temperature: float = 0.8,
        top_p: float = 0.95,
        max_tokens: int = 256
    ) -> str:
        """Generate single code sample."""
        ...

# From: h-e1/code/eval/feedback.py
def execute_code(code: str, tests: List[str], timeout: int = 5) -> int:
    """Execute code against tests. Returns 1 if pass, 0 if fail."""
    ...

def ai_score(prompt: str, code: str) -> float:
    """Score code using heuristic. Returns 0-1."""
    ...

def simulate_human_ratings(
    code: str,
    execution_result: int,
    num_raters: int = 3,
    noise_level: float = 0.2,
    seed: int = None
) -> List[float]:
    """Simulate human ratings. Returns list of ratings."""
    ...
```

**Verified from:** h-e1/code/ actual implementation

---

## A-1: SWE-bench Dataset Loader [Complexity: 3, Budget: 6]

**Applied:** Standard HuggingFace Datasets API

### API Signatures

```python
from dataclasses import dataclass
from typing import List
from datasets import load_dataset

@dataclass
class SWEBenchProblem:
    """SWE-bench problem instance."""
    id: str
    repo: str
    problem_statement: str
    test_patch: str
    dataset: str

def load_swebench(n_samples: int = 100, seed: int = 42) -> List[SWEBenchProblem]:
    """Load SWE-bench Lite samples. Returns n_samples randomly sampled."""
    ds = load_dataset("princeton-nlp/SWE-bench_Lite", split="test")
    ds = ds.shuffle(seed=seed).select(range(min(n_samples, len(ds))))
    
    problems = []
    for item in ds:
        problems.append(SWEBenchProblem(
            id=item["instance_id"],
            repo=item["repo"],
            problem_statement=item["problem_statement"],
            test_patch=item["test_patch"],
            dataset="swebench"
        ))
    return problems
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Load dataset | HuggingFace API call |
| L-1-2 | Sample 100 | Shuffle + select |
| L-1-3 | Parse fields | Extract instance_id, repo, problem_statement, test_patch |
| L-1-4 | Create dataclass | SWEBenchProblem instances |
| L-1-5 | Error handling | Handle missing fields, network errors |
| L-1-6 | Cache setup | HF_DATASETS_CACHE env var |

---

## A-2: Data Standardization [Complexity: 2, Budget: 4]

**Applied:** Simple dict normalization pattern

### API Signatures

```python
@dataclass
class UnifiedSample:
    """Unified sample across all datasets."""
    sample_id: str  # "humaneval_001", "swebench_django_12345"
    task_type: str  # "humaneval" | "mbpp" | "swebench"
    problem: str
    code: str
    exec_result: int  # 0 or 1
    ai_score: float  # 0-1
    human_rating: float  # 0-1 (normalized from rater scores)

def standardize_samples(
    problems: List[Problem],
    codes: List[str],
    exec_results: List[int],
    ai_scores: List[float],
    human_ratings: List[float]
) -> List[UnifiedSample]:
    """Convert to unified format. All lists same length."""
    samples = []
    for prob, code, exec_res, ai, human in zip(problems, codes, exec_results, ai_scores, human_ratings):
        samples.append(UnifiedSample(
            sample_id=f"{prob.dataset}_{prob.id}",
            task_type=prob.dataset,
            problem=prob.prompt,
            code=code,
            exec_result=exec_res,
            ai_score=ai,
            human_rating=human
        ))
    return samples
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Zip data | Combine parallel lists |
| L-2-2 | Create ID | dataset_problemid format |
| L-2-3 | Normalize ratings | human_ratings already 0-1 from h-e1 |
| L-2-4 | Build dataclass | UnifiedSample instances |

---

## A-3: Disagreement Extraction [Complexity: 3, Budget: 6]

**Applied:** Threshold-based filtering pattern

### API Signatures

```python
@dataclass
class Disagreement:
    """Disagreement case."""
    sample_id: str
    task_type: str
    exec_result: int
    human_rating: float
    disagreement_type: str  # "exec_pass_human_low" | "exec_fail_human_high"
    problem: str
    code: str

def extract_disagreements(
    samples: List[UnifiedSample],
    threshold: float = 0.6
) -> List[Disagreement]:
    """
    Extract exec/human disagreements.
    threshold: 0.6 on 0-1 scale (equivalent to 3/5)
    """
    disagreements = []
    
    for s in samples:
        exec_pass = (s.exec_result == 1)
        human_low = (s.human_rating < threshold)
        human_high = (s.human_rating > threshold)
        
        if exec_pass and human_low:
            disagreements.append(Disagreement(
                sample_id=s.sample_id,
                task_type=s.task_type,
                exec_result=1,
                human_rating=s.human_rating,
                disagreement_type="exec_pass_human_low",
                problem=s.problem,
                code=s.code
            ))
        elif not exec_pass and human_high:
            disagreements.append(Disagreement(
                sample_id=s.sample_id,
                task_type=s.task_type,
                exec_result=0,
                human_rating=s.human_rating,
                disagreement_type="exec_fail_human_high",
                problem=s.problem,
                code=s.code
            ))
    
    return disagreements
```

### Pseudo-code

```
1. For each sample:
   a. exec_pass = (exec_result == 1)
   b. human_low = (human_rating < 0.6)
   c. human_high = (human_rating > 0.6)
   
2. If exec_pass AND human_low:
   - Create disagreement: "exec_pass_human_low"
   
3. If NOT exec_pass AND human_high:
   - Create disagreement: "exec_fail_human_high"
   
4. Return list of disagreements
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Iterate samples | Loop over unified samples |
| L-3-2 | Compute flags | exec_pass, human_low, human_high |
| L-3-3 | Check Type A | exec PASS + human LOW |
| L-3-4 | Check Type B | exec FAIL + human HIGH |
| L-3-5 | Create disagreement | Build dataclass |
| L-3-6 | Return list | Collect all cases |

---

## A-4: Qualitative Coding Interface [Complexity: 4, Budget: 8]

**Applied:** Simple CLI prompt-based coding pattern

### API Signatures

```python
INTENT_DIMENSIONS = [
    "correctness",
    "edge_cases",
    "readability",
    "efficiency",
    "maintainability",
    "security"
]

@dataclass
class CodedResult:
    """Coded disagreement case."""
    sample_id: str
    task_type: str
    disagreement_type: str
    missed_dimensions: List[str]
    notes: str

def code_single_disagreement(
    disagreement: Disagreement,
    show_code: bool = True
) -> CodedResult:
    """
    Manual coding for one disagreement.
    Displays code + problem, prompts for dimensions.
    """
    if show_code:
        print(f"\n{'='*60}")
        print(f"Sample ID: {disagreement.sample_id}")
        print(f"Task Type: {disagreement.task_type}")
        print(f"Disagreement: {disagreement.disagreement_type}")
        print(f"Exec: {disagreement.exec_result}, Human: {disagreement.human_rating:.2f}")
        print(f"\nProblem:\n{disagreement.problem[:300]}...")
        print(f"\nCode:\n{disagreement.code[:500]}...")
        print(f"{'='*60}")
    
    print("\nWhich intent dimensions did execution feedback MISS?")
    for i, dim in enumerate(INTENT_DIMENSIONS, 1):
        print(f"{i}. {dim}")
    
    choice = input("Enter numbers (comma-separated) or 0 for none: ").strip()
    
    missed = []
    if choice and choice != "0":
        indices = [int(x.strip()) - 1 for x in choice.split(",")]
        missed = [INTENT_DIMENSIONS[i] for i in indices if 0 <= i < len(INTENT_DIMENSIONS)]
    
    notes = input("Notes (optional): ").strip()
    
    return CodedResult(
        sample_id=disagreement.sample_id,
        task_type=disagreement.task_type,
        disagreement_type=disagreement.disagreement_type,
        missed_dimensions=missed,
        notes=notes
    )

def batch_code_disagreements(
    disagreements: List[Disagreement],
    output_path: str = "coded_results.json"
) -> List[CodedResult]:
    """Code all disagreements and save to JSON."""
    import json
    
    results = []
    for i, d in enumerate(disagreements, 1):
        print(f"\n[{i}/{len(disagreements)}]")
        coded = code_single_disagreement(d)
        results.append(coded)
    
    with open(output_path, 'w') as f:
        json.dump([vars(r) for r in results], f, indent=2)
    
    return results
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Display sample | Print problem + code |
| L-4-2 | Show dimensions | List 6 intent dimensions |
| L-4-3 | Prompt input | Ask for comma-separated choices |
| L-4-4 | Parse input | Split + validate indices |
| L-4-5 | Map to dimensions | Convert indices to dimension names |
| L-4-6 | Collect notes | Optional qualitative notes |
| L-4-7 | Create result | Build CodedResult |
| L-4-8 | Save JSON | Export batch results |

---

## A-5: Chi-Square Test [Complexity: 2, Budget: 4]

**Applied:** scipy.stats.chi2_contingency

### API Signatures

```python
import numpy as np
from scipy.stats import chi2_contingency

def compute_chi_square(coded_results: List[CodedResult]) -> dict:
    """
    Test if missed dimension rates differ by task type.
    
    Contingency table:
                 | Has Missed | No Missed |
    HumanEval    |     a      |     b     |
    MBPP         |     c      |     d     |
    SWE-bench    |     e      |     f     |
    
    Returns: {statistic, p_value, dof, table}
    """
    task_types = ["humaneval", "mbpp", "swebench"]
    table = []
    
    for task_type in task_types:
        task_results = [r for r in coded_results if r.task_type == task_type]
        has_missed = sum(1 for r in task_results if len(r.missed_dimensions) > 0)
        no_missed = len(task_results) - has_missed
        table.append([has_missed, no_missed])
    
    table = np.array(table)
    chi2, p_value, dof, expected = chi2_contingency(table)
    
    return {
        "statistic": chi2,
        "p_value": p_value,
        "dof": dof,
        "observed": table.tolist(),
        "expected": expected.tolist()
    }
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Build table | 3×2 contingency matrix |
| L-5-2 | Filter by task | Group coded_results by task_type |
| L-5-3 | Count categories | has_missed vs no_missed |
| L-5-4 | Run test | scipy chi2_contingency |

---

## A-6: Bootstrap Confidence Intervals [Complexity: 3, Budget: 6]

**Applied:** Percentile bootstrap method

### API Signatures

```python
import numpy as np

def bootstrap_ci(
    coded_results: List[CodedResult],
    task_type: str,
    n_bootstrap: int = 1000,
    alpha: float = 0.05,
    seed: int = 42
) -> tuple:
    """
    Compute 95% CI for missed dimension rate.
    
    Args:
        coded_results: All coded disagreements
        task_type: "humaneval" | "mbpp" | "swebench"
        n_bootstrap: Number of bootstrap samples
        alpha: Significance level (0.05 for 95% CI)
        seed: Random seed
    
    Returns:
        (lower_bound, upper_bound)
    """
    np.random.seed(seed)
    
    task_results = [r for r in coded_results if r.task_type == task_type]
    n = len(task_results)
    
    if n == 0:
        return (0.0, 0.0)
    
    rates = []
    for _ in range(n_bootstrap):
        # Resample with replacement
        indices = np.random.choice(n, size=n, replace=True)
        bootstrap_sample = [task_results[i] for i in indices]
        
        missed_count = sum(1 for r in bootstrap_sample if len(r.missed_dimensions) > 0)
        rate = missed_count / n
        rates.append(rate)
    
    lower = np.percentile(rates, alpha / 2 * 100)
    upper = np.percentile(rates, (1 - alpha / 2) * 100)
    
    return (lower, upper)
```

### Pseudo-code

```
1. Filter coded_results to task_type
2. Set n = number of samples
3. For i = 1 to 1000:
   a. Resample n indices with replacement
   b. Count samples with len(missed_dimensions) > 0
   c. rate = count / n
   d. Store rate
4. Compute 2.5th and 97.5th percentiles
5. Return (lower, upper)
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Filter task | Select task_type samples |
| L-6-2 | Bootstrap loop | Repeat 1000 times |
| L-6-3 | Resample | np.random.choice with replacement |
| L-6-4 | Compute rate | Fraction with missed_dimensions > 0 |
| L-6-5 | Collect rates | Append to list |
| L-6-6 | Percentiles | 2.5th and 97.5th |

---

## A-7: Effect Size Calculation [Complexity: 1, Budget: 2]

**Applied:** Simple ratio calculation

### API Signatures

```python
def compute_effect_size(coded_results: List[CodedResult]) -> dict:
    """
    Compute effect size (SWE-bench rate / HumanEval rate).
    
    Returns:
        {
            "humaneval_rate": float,
            "mbpp_rate": float,
            "swebench_rate": float,
            "swebench_humaneval_ratio": float,
            "swebench_mbpp_ratio": float
        }
    """
    task_types = ["humaneval", "mbpp", "swebench"]
    rates = {}
    
    for task_type in task_types:
        task_results = [r for r in coded_results if r.task_type == task_type]
        if len(task_results) == 0:
            rates[f"{task_type}_rate"] = 0.0
        else:
            missed_count = sum(1 for r in task_results if len(r.missed_dimensions) > 0)
            rates[f"{task_type}_rate"] = missed_count / len(task_results)
    
    humaneval_rate = rates.get("humaneval_rate", 1e-6)
    mbpp_rate = rates.get("mbpp_rate", 1e-6)
    swebench_rate = rates.get("swebench_rate", 0.0)
    
    return {
        **rates,
        "swebench_humaneval_ratio": swebench_rate / humaneval_rate if humaneval_rate > 0 else 0.0,
        "swebench_mbpp_ratio": swebench_rate / mbpp_rate if mbpp_rate > 0 else 0.0
    }
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Compute rates | Missed count / total per task type |
| L-7-2 | Compute ratios | SWE-bench / HumanEval, SWE-bench / MBPP |

---

## A-8: Visualization Logic [Complexity: 4, Budget: 8]

**Applied:** matplotlib bar charts and heatmaps

### API Signatures

```python
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def plot_missed_dimensions_comparison(
    coded_results: List[CodedResult],
    ci_dict: dict,
    output_path: str = "missed_comparison.png"
):
    """
    Bar chart: % disagreement cases with missed dimensions per task type.
    ci_dict: {task_type: (lower, upper)}
    """
    task_types = ["humaneval", "mbpp", "swebench"]
    rates = []
    errors_lower = []
    errors_upper = []
    
    for task_type in task_types:
        task_results = [r for r in coded_results if r.task_type == task_type]
        missed_count = sum(1 for r in task_results if len(r.missed_dimensions) > 0)
        rate = missed_count / len(task_results) if len(task_results) > 0 else 0.0
        rates.append(rate)
        
        lower, upper = ci_dict.get(task_type, (rate, rate))
        errors_lower.append(rate - lower)
        errors_upper.append(upper - rate)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    x = np.arange(len(task_types))
    ax.bar(x, rates, yerr=[errors_lower, errors_upper], capsize=5)
    ax.set_xticks(x)
    ax.set_xticklabels(task_types)
    ax.set_ylabel("% Disagreements with Missed Dimensions")
    ax.set_xlabel("Task Type")
    ax.set_title("Missed Intent Dimensions by Task Type")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

def plot_dimension_heatmap(
    coded_results: List[CodedResult],
    output_path: str = "dimension_heatmap.png"
):
    """
    Heatmap: dimension × task type.
    Cell values: % of disagreements missing this dimension.
    """
    task_types = ["humaneval", "mbpp", "swebench"]
    dimensions = INTENT_DIMENSIONS
    
    matrix = np.zeros((len(dimensions), len(task_types)))
    
    for i, dim in enumerate(dimensions):
        for j, task_type in enumerate(task_types):
            task_results = [r for r in coded_results if r.task_type == task_type]
            if len(task_results) == 0:
                matrix[i, j] = 0.0
            else:
                count = sum(1 for r in task_results if dim in r.missed_dimensions)
                matrix[i, j] = count / len(task_results)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(matrix, annot=True, fmt=".2f", cmap="YlOrRd",
                xticklabels=task_types, yticklabels=dimensions, ax=ax)
    ax.set_title("Intent Dimension Coverage by Task Type")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | Bar chart data | Compute rates per task type |
| L-8-2 | Error bars | Extract CI bounds |
| L-8-3 | Plot bars | matplotlib bar plot |
| L-8-4 | Heatmap matrix | dimension × task type grid |
| L-8-5 | Count occurrences | dim in missed_dimensions |
| L-8-6 | Normalize | Divide by total per task |
| L-8-7 | Plot heatmap | seaborn heatmap |
| L-8-8 | Save figures | PNG output |

---

## Edge Case Handling

### Missing Feedback Cases

```python
def filter_complete_samples(samples: List[UnifiedSample]) -> List[UnifiedSample]:
    """Remove samples with missing feedback (exec/ai/human all required)."""
    return [s for s in samples if s.exec_result is not None 
            and s.ai_score is not None 
            and s.human_rating is not None]
```

### Empty Disagreement Sets

```python
def validate_disagreement_coverage(disagreements: List[Disagreement]) -> dict:
    """Check if each task type has >=10 disagreement cases."""
    coverage = {}
    for task_type in ["humaneval", "mbpp", "swebench"]:
        count = sum(1 for d in disagreements if d.task_type == task_type)
        coverage[task_type] = {
            "count": count,
            "sufficient": count >= 10
        }
    return coverage
```

### Chi-Square Test Assumptions

```python
def validate_chi_square_assumptions(table: np.ndarray) -> dict:
    """Check if expected frequencies >=5 for chi-square test."""
    from scipy.stats import chi2_contingency
    _, _, _, expected = chi2_contingency(table)
    min_expected = expected.min()
    
    return {
        "min_expected": min_expected,
        "valid": min_expected >= 5,
        "warning": "Use Fisher's exact test if min_expected < 5" if min_expected < 5 else None
    }
```

---

## Pipeline Integration

### Main Orchestration

```python
def run_h_m1_experiment(
    n_humaneval: int = 50,
    n_mbpp: int = 50,
    n_swebench: int = 100,
    seed: int = 42
):
    """
    Full h-m1 pipeline.
    
    Steps:
    1. Load h-e1 results (HumanEval, MBPP)
    2. Generate SWE-bench samples
    3. Collect feedback (exec/ai/human)
    4. Standardize data
    5. Extract disagreements
    6. Qualitative coding
    7. Statistical analysis
    8. Visualization
    9. Gate decision
    """
    
    # 1. Load h-e1 data (reuse existing results)
    humaneval_samples = load_h_e1_humaneval_results()  # From h-e1/code/outputs/
    mbpp_samples = load_h_e1_mbpp_results()
    
    # 2. Generate SWE-bench samples
    swebench_problems = load_swebench(n_swebench, seed)
    model = CodeGenModel()
    swebench_codes = [model.generate(p.problem_statement) for p in swebench_problems]
    
    # 3. Collect SWE-bench feedback
    swebench_exec = collect_swebench_execution(swebench_problems, swebench_codes)
    swebench_ai = [ai_score(p.problem_statement, c) for p, c in zip(swebench_problems, swebench_codes)]
    swebench_human = [simulate_human_ratings(c, e, seed=seed)[0] for c, e in zip(swebench_codes, swebench_exec)]
    
    # 4. Standardize all data
    all_samples = (
        standardize_samples(humaneval_samples) +
        standardize_samples(mbpp_samples) +
        standardize_samples(swebench_problems, swebench_codes, swebench_exec, swebench_ai, swebench_human)
    )
    
    # 5. Extract disagreements
    disagreements = extract_disagreements(all_samples, threshold=0.6)
    
    # Validate coverage
    coverage = validate_disagreement_coverage(disagreements)
    print(f"Disagreement coverage: {coverage}")
    
    # 6. Qualitative coding (manual)
    coded_results = batch_code_disagreements(disagreements, "h-m1/coded_results.json")
    
    # 7. Statistical analysis
    chi_square = compute_chi_square(coded_results)
    effect_size = compute_effect_size(coded_results)
    
    # Bootstrap CIs
    ci_dict = {}
    for task_type in ["humaneval", "mbpp", "swebench"]:
        ci_dict[task_type] = bootstrap_ci(coded_results, task_type, seed=seed)
    
    # 8. Visualization
    plot_missed_dimensions_comparison(coded_results, ci_dict, "h-m1/figures/missed_comparison.png")
    plot_dimension_heatmap(coded_results, "h-m1/figures/dimension_heatmap.png")
    
    # 9. Gate decision
    gate_pass = (
        effect_size["swebench_humaneval_ratio"] > 2.0 and
        chi_square["p_value"] < 0.05
    )
    
    return {
        "gate_pass": gate_pass,
        "chi_square": chi_square,
        "effect_size": effect_size,
        "ci": ci_dict,
        "coded_results": coded_results
    }
```

---

## Complexity Analysis

| Component | Time | Space | Notes |
|-----------|------|-------|-------|
| SWE-bench load | O(n) | O(n) | n=100, dataset download |
| Disagreement extract | O(n) | O(k) | k=disagreements (<n) |
| Qualitative coding | O(k×t) | O(k) | t=manual time per case (~2min) |
| Chi-square | O(1) | O(1) | 3×2 table, constant |
| Bootstrap | O(k×B) | O(B) | B=1000 bootstrap samples |
| Visualization | O(k) | O(1) | Bar/heatmap generation |

**Total runtime:** ~3-4 hours (dominated by manual coding)

---

## Summary

**Total Subtasks:** 44/44 allocated

**Reused APIs:**
- h-e1 data loaders (HumanEval, MBPP)
- h-e1 CodeGenModel
- h-e1 feedback collectors (execute_code, ai_score, simulate_human_ratings)

**New Components:**
- SWE-bench loader (A-1)
- Data standardization (A-2)
- Disagreement extraction (A-3)
- Qualitative coding interface (A-4)
- Chi-square test (A-5)
- Bootstrap CI (A-6)
- Effect size calculation (A-7)
- Visualization (A-8)

**Gate Success Conditions:**
- Effect size >2× (SWE-bench / HumanEval)
- Chi-square p<0.05
- Sufficient disagreement cases (>10 per dataset)
