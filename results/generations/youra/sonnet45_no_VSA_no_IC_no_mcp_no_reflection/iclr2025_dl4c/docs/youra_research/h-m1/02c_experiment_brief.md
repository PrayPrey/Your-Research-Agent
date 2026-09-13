# Experiment Design: h-m1

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Under multi-test failures, if agents identify root causes, then test failures are grouped by shared error sources because conceptual understanding enables pattern recognition.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** - Tests error clustering recognition as causal mechanism

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 (awaiting implementation)
**Gate Status:** MUST_WORK - requires clustering coefficient > 0.3 (p < 0.05)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (Fix-Impact-Ratio Measurement)

### Gate Condition
MUST_WORK gate: At least one architecture shows clustering coefficient > 0.3 AND p < 0.05 vs random. If fails: PIVOT - Agents do not cluster errors, mechanism not validated.

---

## Continuation Context

First MECHANISM hypothesis in verification chain (H-E1 → H-M1 → H-M2 → H-M3). Tests the foundational claim that agents with conceptual understanding can recognize error patterns by clustering same-type fixes together.

### Previous Hypothesis Results (if applicable)
N/A - H-E1 prerequisite not yet implemented

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Error Clustering Experiment Design**
- Standard approach: Manual error type annotation with inter-annotator agreement validation (Cohen's kappa > 0.7)
- Dataset: Codeforces Competitive Programming (curated subset, 1200-1800 rating, solve_count > 1000)
- Typical setup: 50 problems × 15 test cases = 750 error labels with 2-3 annotators
- Metric: Error Clustering Coefficient = observed_consecutive_same_type / expected_random (range 0-1)
- Baseline: Random permutation baseline (~0.0)
- Expected result: Clustering coefficient > 0.3 for conceptual understanding agents

**Query 2: Code Generation Test Failure Patterns**
- Common error types taxonomy: syntax errors, runtime errors, logic errors, edge case failures
- Implementation challenge: Error type taxonomy must be reliable (kappa > 0.7) or metric becomes unmeasurable
- Best practice: Filter problems by community validation (solve_count > 1000 ensures quality test suites)
- Pitfall: Low solve_count problems may have duplicate or low-coverage test cases → noisy fix-impact-ratio

**Query 3: Agent Debugging Benchmarks**
- Standard dataset: HumanEval (doesn't support multi-test clustering analysis)
- Alternative: Codeforces problems provide 15-50 test cases per problem with diverse error types
- Expected baseline: GPT-4 Turbo (temperature=0.7)
- Comparison architectures: GPT-4 + memory module, GPT-4 + error analysis prompt
- Typical performance: Strategic agents show fix-impact-ratio > 2.0 vs baseline ~1.0

### Archon Code Examples

**Example 1: Error Clustering Coefficient Calculation**
```python
# Error clustering coefficient measurement
def clustering_coefficient(error_sequence, error_labels):
    """
    Measure if agent fixes errors in clustered order.
    error_sequence: list of test case IDs in fix order
    error_labels: dict mapping test_id -> error_type
    """
    consecutive_same = 0
    for i in range(len(error_sequence) - 1):
        if error_labels[error_sequence[i]] == error_labels[error_sequence[i+1]]:
            consecutive_same += 1
    
    observed = consecutive_same / (len(error_sequence) - 1)
    expected_random = 1.0 / num_unique_error_types
    
    return observed / expected_random  # >1.0 means clustering
```
**Pattern:** Ratio-based metric comparing observed vs random expectation
**Insight:** Clustering coefficient > 1.0 indicates non-random error grouping

**Example 2: Fix-Impact-Ratio Tracking**
```python
# Track Δpassing_tests per modification
def calculate_fix_impact_ratio(modifications):
    """
    modifications: list of (code_version, passing_test_count) tuples
    """
    impacts = []
    for i in range(1, len(modifications)):
        delta_passing = modifications[i][1] - modifications[i-1][1]
        impacts.append(delta_passing)
    
    return np.mean(impacts)  # avg tests fixed per modification
```
**Pattern:** Delta-based impact measurement across iterations
**Insight:** High-impact fixes (Δ > 2) indicate root cause targeting

### Exa GitHub Implementations

**Query 1: Code Generation Agent Debugging Implementations**

**Repository 1**: openai/human-eval (⭐ 2.1k)
- **URL**: https://github.com/openai/human-eval
- **Relevance**: Standard code generation benchmark, but lacks multi-test clustering support
- **Architecture**: Language model evaluation framework
- **Key Code**:
  ```python
  # Test execution and pass@k evaluation
  def evaluate_functional_correctness(sample_file, k=[1, 10, 100]):
      problems = read_problems()
      samples = [json.loads(x) for x in open(sample_file)]
      
      # Run test cases
      results = []
      for sample in samples:
          result = check_correctness(sample["task_id"], sample["completion"])
          results.append(result)
      
      # Calculate pass@k
      return calculate_pass_at_k(results, k)
  ```
- **Training Config**: N/A (evaluation only)
- **Dataset**: 164 hand-written Python programming problems
- **Results**: GPT-3.5 pass@1 ~48%, GPT-4 ~67%
- **Limitation**: Single test case per problem - cannot measure error clustering

**Repository 2**: Codeforces Multi-Test Framework (custom implementation required)
- **Relevance**: Codeforces problems provide 15-50 test cases per problem for clustering analysis
- **Architecture**: Multi-test debugging evaluation loop
- **Key Code** (custom implementation needed):
  ```python
  # Multi-test debugging loop
  def run_debug_session(agent, problem, test_cases):
      modifications = []
      code = agent.generate_initial_solution(problem)
      
      for iteration in range(max_iterations):
          results = execute_tests(code, test_cases)
          passing = [t for t in results if t.passed]
          failing = [t for t in results if not t.passed]
          
          if len(failing) == 0:
              break
          
          # Track fix impact
          prev_passing = len(passing)
          code = agent.debug_and_fix(code, failing)
          new_passing = count_passing(code, test_cases)
          
          modifications.append({
              'iteration': iteration,
              'delta_passing': new_passing - prev_passing,
              'code_version': code
          })
      
      return modifications
  ```
- **Training Config**:
  - Model: GPT-4 Turbo API
  - Temperature: 0.7
  - Max iterations: 10
- **Dataset**: Codeforces (1200-1800 rating, solve_count > 1000)

**Query 2: Error Clustering Measurement**
- **Approach**: Manual error type annotation with 2-3 annotators
- **Taxonomy**: syntax, runtime, logic, edge case
- **Validation**: Inter-annotator agreement (Cohen's kappa > 0.7)
- **Metric**: Clustering coefficient via permutation test

**Serena Analysis Needed**: false

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

N/A - This is a novel evaluation framework (error clustering measurement), not paper reproduction. Custom implementation required for multi-test debugging evaluation loop.

**Recommended Implementation Path:**
- Primary: Custom Codeforces evaluation framework with GPT-4 API integration
- Fallback: Simplified 10-problem pilot with manual error annotation
- Justification: No existing framework measures error clustering in code generation agents. HumanEval lacks multi-test support. Custom implementation enables precise control over error annotation, clustering measurement, and baseline comparisons.

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. Error clustering implementation patterns are straightforward (annotation + permutation test).

---

## Experiment Specification

### Dataset

**Name:** Codeforces Competitive Programming Problems (Curated Subset)
**Type:** standard
**Source:** Codeforces.com (publicly available)

**Selection Criteria:**
- solve_count > 1000 (ensures quality test suites)
- Rating: 1200-1800 (intermediate difficulty)
- Test cases: 15+ per problem (required for clustering analysis)

**Sample Size:** 50 problems for Phase 1 validation (750 test case error labels with 2-3 annotators)

**Hypothesis Fit:** Multi-test failures (15-50 cases per problem) enable measurement of error clustering coefficient. High solve count ensures non-duplicate, well-coverage test suites critical for reliable fix-impact-ratio.

**Loading Information** (for Phase 4 download):
- Method: Custom curation via Codeforces API
- Identifier: Programmatic filter (solve_count > 1000, rating 1200-1800, min_test_cases 15)
- Code:
  ```python
  # Codeforces problem curation
  import requests
  
  def fetch_codeforces_problems(min_solve_count=1000, min_rating=1200, max_rating=1800, min_test_cases=15):
      response = requests.get('https://codeforces.com/api/problemset.problems')
      problems = response.json()['result']['problems']
      
      curated = [
          p for p in problems
          if p.get('solve_count', 0) >= min_solve_count
          and min_rating <= p.get('rating', 0) <= max_rating
          # Note: test_case_count requires problem scraping
      ]
      return curated[:50]  # Phase 1 validation set
  ```

**Preprocessing:**
- Manual error type annotation (syntax, runtime, logic, edge case)
- Inter-annotator agreement validation (Cohen's kappa > 0.7)
- Test case execution via subprocess isolation

### Models

#### Baseline Model

**Architecture:** GPT-4 Turbo (baseline), GPT-4 + memory module, GPT-4 + error analysis prompt

**Baseline (Control):** GPT-4 Turbo with temperature=0.7, no error feedback context

**Variant 1 (Memory):** GPT-4 + sliding window memory of past errors (last 5 fixes)

**Variant 2 (Prompting):** GPT-4 + explicit "analyze root cause before fixing" prompt

**Hypothesis Fit:** State-of-the-art code generation agent. Memory variant tests if retaining error history improves clustering. Prompt variant tests if explicit root cause analysis is sufficient.

**Loading Information** (for Phase 4 download):
- Method: OpenAI API
- Identifier: `gpt-4-turbo-2024-04-09`
- Code:
  ```python
  from openai import OpenAI
  
  client = OpenAI(api_key="YOUR_API_KEY")
  
  def baseline_agent(problem_description, test_failures):
      response = client.chat.completions.create(
          model="gpt-4-turbo-2024-04-09",
          messages=[
              {"role": "system", "content": "You are a code debugging assistant."},
              {"role": "user", "content": f"Problem: {problem_description}\n\nFailing tests: {test_failures}\n\nFix the code."}
          ],
          temperature=0.7
      )
      return response.choices[0].message.content
  ```

#### Proposed Model

**Architecture:** Baseline + Error Clustering Analysis

**Core Mechanism Implementation:**

```python
# Core Mechanism: Error Clustering Recognition
# Based on: Phase 2B verification plan + clustering analysis patterns

class ErrorClusteringAnalyzer:
    """
    Measure if agent fixes errors in clustered order vs random permutation.
    Tests conceptual understanding via pattern recognition.
    """
    def __init__(self, error_taxonomy=['syntax', 'runtime', 'logic', 'edge_case']):
        self.error_types = error_taxonomy
        
    def measure_clustering(self, fix_sequence, error_labels):
        """
        Args:
            fix_sequence: List[test_id] - order agent addressed failures
            error_labels: Dict[test_id, error_type] - annotated error types
        Returns:
            clustering_coefficient: float - >1.0 indicates clustering
        """
        # Count consecutive same-type fixes
        consecutive_same = 0
        for i in range(len(fix_sequence) - 1):
            if error_labels[fix_sequence[i]] == error_labels[fix_sequence[i+1]]:
                consecutive_same += 1
        
        # Observed vs expected under random ordering
        observed_rate = consecutive_same / (len(fix_sequence) - 1)
        expected_random = 1.0 / len(self.error_types)
        
        return observed_rate / expected_random  # >1.0 = clustering

# Integration: Multi-test debugging evaluation loop
# Annotation: 2-3 human annotators label 750 test failures (50 problems × 15 tests)
# Validation: Cohen's kappa > 0.7 for reliable labels
```

### Training Protocol

**Model**: GPT-4 Turbo API (gpt-4-turbo-2024-04-09)
**Temperature**: 0.7
**Max Iterations**: 10 (debugging loop per problem)
**Seeds**: 1 (fixed)

**Baseline Configuration**:
- No error context memory
- No explicit root cause analysis prompt
- Addresses test failures in presented order

**Proposed Configuration**:
- Error clustering metric applied to fix sequence
- Same API calls, different evaluation metric

**Source**: Phase 2B verification plan Section 2.2 (H-M1 verification protocol)

> ⚠️ **Note**: No training required - evaluation-only experiment measuring agent debugging sequence patterns.

### Evaluation

**Primary Metrics**:
- Error Clustering Coefficient (continuous, 0-∞)
  - Ratio of observed consecutive same-type fixes to random expectation
  - >1.0 indicates non-random clustering
  - Expected baseline: ~0.0 (random permutation)
  - Expected agent: >0.3 (Phase 2B threshold)

**Success Criteria**:
- clustering_coefficient_agent > clustering_coefficient_random
- Preferably > 0.3 for meaningful clustering evidence

**Expected Baseline Performance** (from Phase 2B):
- Random permutation baseline: ~0.0
- Sequential trial-and-error baseline: ~0.0
- Source: Phase 2B Section 1.4 baseline methods

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Code debugging sequence analysis
- Library: Custom implementation (numpy, sklearn for Cohen's kappa)
- Code:
  ```python
  from sklearn.metrics import cohen_kappa_score
  import numpy as np
  
  # Inter-annotator agreement
  kappa = cohen_kappa_score(annotator1_labels, annotator2_labels)
  assert kappa > 0.7, "Error taxonomy unreliable"
  
  # Clustering coefficient
  def clustering_coefficient(fix_sequence, error_labels):
      consecutive_same = sum(
          1 for i in range(len(fix_sequence) - 1)
          if error_labels[fix_sequence[i]] == error_labels[fix_sequence[i+1]]
      )
      observed = consecutive_same / (len(fix_sequence) - 1) if len(fix_sequence) > 1 else 0
      num_types = len(set(error_labels.values()))
      expected_random = 1.0 / num_types
      return observed / expected_random
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Clustering coefficient (agent vs random baseline) bar chart

#### Additional Figures (LLM Autonomous)
- **Error Type Distribution**: Histogram of error types across 750 test failures
- **Fix Sequence Heatmap**: Temporal view of which error types were addressed in what order
- **Inter-Annotator Agreement**: Confusion matrix between annotators (validates kappa > 0.7)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1**: Error Clustering Experiment Design
- **Type**: Knowledge base synthesis (from Phase 2B verification plan)
- **Query Used**: "error clustering experiment design dataset"
- **Relevance**: Standard methodology for measuring agent error grouping behavior
- **Key Insights**:
  - Manual annotation with inter-annotator agreement (Cohen's kappa > 0.7) is required
  - Codeforces problems provide 15-50 test cases needed for clustering analysis
  - Error taxonomy: syntax, runtime, logic, edge case
  - Expected clustering coefficient > 0.3 for conceptual understanding agents
- **Used For**: Dataset selection, metric design, success criteria

**Source 2**: Code Generation Test Failure Patterns
- **Type**: Knowledge base synthesis
- **Query Used**: "code generation test failure implementation challenges"
- **Relevance**: Common pitfalls and best practices for multi-test debugging evaluation
- **Key Insights**:
  - Filter by solve_count > 1000 to ensure quality test suites
  - Low solve_count problems have duplicate/low-coverage test cases → noisy metrics
  - Error type taxonomy must be reliable (kappa > 0.7) or metric becomes unmeasurable
- **Used For**: Dataset filtering criteria, quality validation

**Source 3**: Agent Debugging Benchmarks
- **Type**: Knowledge base synthesis
- **Query Used**: "agent debugging benchmark code generation"
- **Relevance**: Baseline performance expectations and architecture comparisons
- **Key Insights**:
  - HumanEval doesn't support multi-test clustering (single test per problem)
  - GPT-4 Turbo baseline with temperature=0.7
  - Strategic agents show fix-impact-ratio > 2.0 vs baseline ~1.0
- **Used For**: Baseline model selection, expected performance range

### Archon Code Examples

**Code Source 1**: Error Clustering Coefficient Calculation
- **Query Used**: "error clustering measurement code"
- **Key Code**:
  ```python
  # Error clustering coefficient measurement
  def clustering_coefficient(error_sequence, error_labels):
      consecutive_same = 0
      for i in range(len(error_sequence) - 1):
          if error_labels[error_sequence[i]] == error_labels[error_sequence[i+1]]:
              consecutive_same += 1
      
      observed = consecutive_same / (len(error_sequence) - 1)
      expected_random = 1.0 / num_unique_error_types
      
      return observed / expected_random  # >1.0 means clustering
  ```
- **Used For**: Core mechanism pseudo-code, metric implementation

**Code Source 2**: Fix-Impact-Ratio Tracking
- **Query Used**: "fix impact ratio tracking code"
- **Key Code**:
  ```python
  # Track Δpassing_tests per modification
  def calculate_fix_impact_ratio(modifications):
      impacts = []
      for i in range(1, len(modifications)):
          delta_passing = modifications[i][1] - modifications[i-1][1]
          impacts.append(delta_passing)
      
      return np.mean(impacts)  # avg tests fixed per modification
  ```
- **Used For**: Supplementary metric (not primary for h-m1)

### B. GitHub Implementations (Exa)

**Repository 1**: openai/human-eval (⭐ 2.1k)
- **URL**: https://github.com/openai/human-eval
- **Query Used**: "code generation agent debugging implementations"
- **Relevance**: Standard benchmark, but lacks multi-test clustering support
- **Key Code** (annotated):
  ```python
  # Test execution and pass@k evaluation
  def evaluate_functional_correctness(sample_file, k=[1, 10, 100]):
      problems = read_problems()
      samples = [json.loads(x) for x in open(sample_file)]
      
      results = []
      for sample in samples:
          result = check_correctness(sample["task_id"], sample["completion"])
          results.append(result)
      
      return calculate_pass_at_k(results, k)
  ```
  # Limitation: Single test case per problem - cannot measure error clustering
- **Configuration Extracted**: pass@k evaluation methodology
- **Their Results**: GPT-3.5 pass@1 ~48%, GPT-4 ~67%
- **Used For**: Baseline comparison context (not directly used for h-m1)

**Repository 2**: Codeforces Multi-Test Framework (custom implementation required)
- **URL**: N/A (custom implementation)
- **Query Used**: "Codeforces multi-test debugging framework"
- **Relevance**: 15-50 test cases per problem enable clustering analysis
- **Key Code** (custom implementation needed):
  ```python
  # Multi-test debugging loop
  def run_debug_session(agent, problem, test_cases):
      modifications = []
      code = agent.generate_initial_solution(problem)
      
      for iteration in range(max_iterations):
          results = execute_tests(code, test_cases)
          failing = [t for t in results if not t.passed]
          
          if not failing:
              break
          
          prev_passing = sum(1 for t in results if t.passed)
          code = agent.debug_and_fix(code, failing)
          new_passing = sum(1 for t in execute_tests(code, test_cases) if t.passed)
          
          modifications.append({
              'iteration': iteration,
              'delta_passing': new_passing - prev_passing
          })
      
      return modifications
  ```
- **Configuration Extracted**: Multi-test debugging loop structure
- **Used For**: Experiment framework design

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - error clustering patterns were sufficiently clear from Archon/Exa findings. Implementation involves straightforward annotation + permutation test methodology.

### D. Previous Hypothesis Context

**Previous Context**: None - h-m1 is the first MECHANISM hypothesis (prerequisite: h-e1).

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Archon KB + Phase 2B | Source A.1, Phase 2B Section 1.3 |
| Dataset filtering | Archon KB | Source A.2 |
| Error annotation protocol | Archon KB | Source A.1 |
| Baseline model | Archon KB + Phase 2B | Source A.3, Phase 2B Section 1.3 |
| Clustering coefficient metric | Archon Code | Code Source 1 |
| Pseudo-code | Archon Code | Code Source 1 |
| Success criteria | Phase 2B | Section 2.2 (H-M1) |
| Expected performance | Archon KB | Source A.1 |
| Multi-test framework | GitHub (custom) | Repo B.2 |

---

## State Information

**State File:** verification_state.yaml
**Date:** {{timestamp}}

### Workflow History for This Hypothesis
- 2026-08-28: Phase 2C experiment design completed
- Status: experiment_design.status = COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
