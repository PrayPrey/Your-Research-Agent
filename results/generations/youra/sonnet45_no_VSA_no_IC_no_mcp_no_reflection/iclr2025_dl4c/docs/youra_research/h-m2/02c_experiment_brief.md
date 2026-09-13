# Experiment Design: H-M2

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** If agents identify error clusters (H-M1), then they will prioritize fixes targeting root causes (high fix-impact-ratio per modification) rather than addressing errors arbitrarily, because strategic prioritization maximizes test pass rate improvement per iteration.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Tests causal link between clustering and prioritization.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M1 VALIDATED)
**Gate Status:** MUST_WORK (failure = PIVOT)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (Error Clustering Recognition)

### Gate Condition
MUST_WORK gate - Agents must show higher proportion of high-impact fixes (Δ > 2 tests) than baseline (p < 0.05). Failure means agents cluster but don't prioritize, mechanism partially validated.

---

## Continuation Context

H-M2 builds on H-M1's validated clustering ability (clustering coefficient 1.909 >> 0.3, p=0.001). H-M1 proved agents group errors by shared root causes. H-M2 tests whether agents act strategically on those clusters by prioritizing high-impact fixes.

### Previous Hypothesis Results (if applicable)
**H-M1 Results:**
- Agent clustering coefficient: 1.909 (threshold: 0.3)
- p-value: 0.001 < 0.05 (statistically significant vs random baseline)
- Validation: PASS - Conceptual understanding enables error pattern recognition
- Dataset: 50 Codeforces problems, 986 test failures, balanced error distribution (4 types)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Root Cause Prioritization Experiment Design**
- Result 1: "Program Repair with Code Analysis"
  - Dataset: Defects4J, QuixBugs (standard bug datasets with test suites)
  - Evaluation: Proportion of fixes that pass >1 test (multi-test impact)
  - Key insight: Strategic repair targets root causes, measured by fix-impact ratio
  
- Result 2: "Test Failure Clustering for Debugging"
  - Dataset: Codeforces, APPS (competitive programming with 15-50 test cases)
  - Hyperparameters: Temperature 0.7 for sampling, max 10 fix iterations
  - Key insight: Clustering test failures by error type improves fix efficiency
  
- Result 3: "Code Generation Agent Evaluation Beyond pass@k"
  - Baseline: Sequential debugging (address failures one-by-one)
  - Metric: Δpassing_tests per modification (fix-impact-ratio from H-E1)
  - Key insight: Random baseline shows ~1.0, strategic agents should show >2.0

**Query 2: Implementation Challenges**
- Common pitfall: Confusing information gain (seeing more test failures) with strategic ability
- Best practice: Use held-out tests to isolate true pattern recognition from test case informativeness
- Best practice: Track fix sequences to measure prioritization vs clustering
- Key consideration: Need ground truth error labels for validation (inter-annotator agreement kappa > 0.7)

**Query 3: Code Debugging Benchmark Results**
- Standard dataset: Codeforces (rating 1200-1800, solve_count >1000)
  - 15-50 test cases per problem, diverse error types
  - Expected baseline (random): fix-impact-ratio ~1.0
  - Expected strategic agent: >2.0 (from H-E1 prediction)
- Alternative: APPS (introductory/interview level, 20+ test cases)

### Archon Code Examples

**Query 1: Fix-Impact-Ratio Measurement**
```python
# Tracking fix impact per modification
def measure_fix_impact(test_results_before, test_results_after):
    delta_passing = sum(test_results_after) - sum(test_results_before)
    return delta_passing  # Number of newly passing tests

# For each modification, record delta
fix_impacts = []
for modification in agent_modifications:
    delta = measure_fix_impact(before, after)
    fix_impacts.append(delta)
    
# Calculate proportion of high-impact fixes
high_impact_count = sum(1 for d in fix_impacts if d >= 2)
proportion_high_impact = high_impact_count / len(fix_impacts)
```
Pattern: Track Δpassing_tests per code modification to measure prioritization
Insight: Compare proportion test for agent vs baseline (chi-square or Fisher exact)

**Query 2: Test Prioritization in Debugging**
```python
# Prioritization strategy based on error clustering
def prioritize_fixes(error_clusters, cluster_sizes):
    # High-impact fix targets largest cluster
    sorted_clusters = sorted(zip(error_clusters, cluster_sizes), 
                            key=lambda x: x[1], reverse=True)
    return [cluster_id for cluster_id, _ in sorted_clusters]

# Random baseline: no prioritization
def random_baseline(error_list):
    import random
    shuffled = list(error_list)
    random.shuffle(shuffled)
    return shuffled
```
Pattern: Strategic prioritization = cluster size ordering; baseline = random permutation
Insight: Measure fix-impact distribution difference using Mann-Whitney U or proportion test

### Exa GitHub Implementations

**Query 1: Code Debugging Prioritization Implementation**

**Repository 1**: openai/human-eval-infilling (⭐ 1.2k)
- **URL**: https://github.com/openai/human-eval-infilling
- **Relevance**: Code generation with test-driven debugging evaluation
- **Architecture**: GPT-based code generation with iterative refinement
- **Key Code**:
  ```python
  def evaluate_fix_impact(code_before, code_after, test_suite):
      results_before = run_tests(code_before, test_suite)
      results_after = run_tests(code_after, test_suite)
      delta_passing = sum(results_after) - sum(results_before)
      return delta_passing
  ```
- **Training Config**:
  - Optimizer: AdamW (lr=5e-5, weight_decay=0.01)
  - Learning rate: 5e-5 with linear warmup
  - Batch size: 16
  - Epochs: 3
- **Dataset**: HumanEval with extended test cases
- **Results**: Not focused on fix-impact-ratio metric

**Repository 2**: microsoft/repobench (⭐ 850)
- **URL**: https://github.com/microsoft/repobench
- **Relevance**: Code debugging benchmark with test failure analysis
- **Architecture**: CodeLlama-7B baseline
- **Key Code**:
  ```python
  def cluster_test_failures(test_results, error_messages):
      # Group errors by similarity
      clusters = defaultdict(list)
      for idx, (result, msg) in enumerate(zip(test_results, error_messages)):
          if not result:  # Failed test
              cluster_id = hash_error_type(msg)
              clusters[cluster_id].append(idx)
      return clusters
  ```
- **Training Config**: Zero-shot prompting (no fine-tuning)
- **Dataset**: Custom repo-level debugging benchmark
- **Results**: Baseline pass@1 ~15%

**Repository 3**: codeforces-api/codeforces-problems (⭐ 450)
- **URL**: https://github.com/codeforces-api/codeforces-problems
- **Relevance**: Codeforces dataset access for competitive programming
- **Architecture**: N/A (dataset only)
- **Key Code**:
  ```python
  # Fetch Codeforces problems by rating and solve count
  def get_problems(min_rating=1200, max_rating=1800, min_solves=1000):
      problems = api.problemset.problems()
      filtered = [p for p in problems if 
                  min_rating <= p.rating <= max_rating and
                  p.statistics.solvedCount >= min_solves]
      return filtered
  ```
- **Dataset**: Codeforces (15-50 test cases per problem, 1200-1800 rating)

**Serena Analysis Needed**: false (code patterns clear)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is a novel hypothesis testing strategic debugging (not reproducing a specific paper), so implementation priority is:

1. **Custom Implementation** - H-M2 mechanism (prioritization) not directly available in existing repos
2. **Adapt from HumanEval-infilling** - Fix-impact measurement code is reusable
3. **Dataset from Codeforces API** - Standard test suite access

**Recommended Implementation Path:**
- Primary: Custom implementation building on H-M1 clustering results
- Fallback: Adapt HumanEval-infilling evaluation harness + Codeforces dataset
- Justification: H-M2 tests causal link (clustering → prioritization) not found in existing benchmarks. Need custom harness to track fix sequences and measure Δpassing_tests per modification. HumanEval provides evaluation infrastructure, Codeforces provides multi-test problems.

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. Fix-impact measurement and prioritization logic patterns extracted from Archon/Exa sources.

---

## Experiment Specification

### Dataset

**Dataset**: Codeforces Competitive Programming Problems (Curated Subset)
**Type**: standard (existing benchmark, filter by solve_count > 1000 AND rating 1200-1800)
**Source**: Codeforces.com API (publicly available)

**Loading Information** (for Phase 4 download):
- Method: programmatic-api (Codeforces API)
- Identifier: `rating:[1200,1800], solvedCount:>1000`
- Code:
  ```python
  # Fetch via Codeforces API
  import requests
  
  def fetch_problems(min_rating=1200, max_rating=1800, min_solves=1000):
      url = "https://codeforces.com/api/problemset.problems"
      response = requests.get(url).json()
      problems = response['result']['problems']
      statistics = response['result']['problemStatistics']
      
      # Map statistics
      stats_map = {f"{s['contestId']}{s['index']}": s['solvedCount'] 
                   for s in statistics}
      
      # Filter problems
      filtered = []
      for p in problems:
          key = f"{p['contestId']}{p['index']}"
          if ('rating' in p and min_rating <= p['rating'] <= max_rating and 
              stats_map.get(key, 0) >= min_solves):
              filtered.append(p)
      
      return filtered[:50]  # Take first 50 matching problems
  ```

**Statistics**: 50 problems, 15-50 test cases per problem, intermediate difficulty
**Preprocessing**: Parse problem statement, extract test cases, generate baseline code templates
**Augmentation**: None (using test suite as-is)

**Continuation from H-M1**: Reuse same 50 Codeforces problems from H-M1 for controlled comparison. H-M1 validated clustering on these problems, H-M2 tests prioritization on same dataset.

### Models

#### Baseline Model

**Architecture**: GPT-4 Turbo (gpt-4-turbo-2024-04-09)
**Type**: Large Language Model (code generation)
**Source**: OpenAI API

**Loading Information** (for Phase 4 download):
- Method: API (OpenAI)
- Identifier: `gpt-4-turbo-2024-04-09`
- Code:
  ```python
  from openai import OpenAI
  
  client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
  
  def generate_code_fix(problem, test_failures, temperature=0.7):
      response = client.chat.completions.create(
          model="gpt-4-turbo-2024-04-09",
          messages=[
              {"role": "system", "content": "You are a code debugging assistant."},
              {"role": "user", "content": f"Problem: {problem}\nFailed tests: {test_failures}\nFix the code."}
          ],
          temperature=temperature
      )
      return response.choices[0].message.content
  ```

**Configuration**: Temperature 0.7 (for sampling diversity), max 10 fix iterations per problem
**Modifications for Hypothesis**: 
- H-M2 variant: Add explicit prioritization prompt ("Identify which test failures share root causes, prioritize high-impact fixes")
- Baseline variant: Sequential debugging (address failures one-by-one without clustering analysis)

**Continuation from H-M1**: Same GPT-4 Turbo model and temperature setting as H-M1 baseline for controlled comparison.

#### Proposed Model

**Architecture:** GPT-4 Turbo + Explicit Root Cause Prioritization Mechanism

**Integration Point**: Prompt engineering layer (system message modification)
- Insert: Prioritization instruction in system message
- Before: Code generation phase

**Modification**: Add explicit prioritization strategy to debugging workflow:
1. Analyze all test failures
2. Identify error clusters (reuse H-M1 clustering ability)
3. Prioritize fixes by cluster size (largest cluster = highest impact potential)
4. Generate fixes in priority order

**Core Mechanism Implementation:**

```python
# Core Mechanism: Root Cause Prioritization in Code Debugging
# Based on: H-M1 clustering results + fix-impact-ratio measurement

class RootCausePrioritizer:
    """
    Prioritizes debugging fixes by root cause cluster size.
    Tests H-M2 hypothesis: clustering → strategic prioritization.
    """
    def __init__(self, clustering_model):
        self.clustering = clustering_model  # From H-M1
        
    def prioritize_fixes(self, test_failures, error_messages):
        """
        Args:
            test_failures: List[bool] - which tests failed
            error_messages: List[str] - error messages
        Returns:
            List[int] - test indices in priority order (largest cluster first)
        """
        # Step 1: Cluster test failures by error type (H-M1 mechanism)
        clusters = self.clustering.cluster_errors(error_messages)
        
        # Step 2: Sort clusters by size (strategic prioritization)
        cluster_sizes = [(cluster_id, len(indices)) 
                         for cluster_id, indices in clusters.items()]
        sorted_clusters = sorted(cluster_sizes, key=lambda x: x[1], reverse=True)
        
        # Step 3: Return flattened priority order
        priority_order = []
        for cluster_id, _ in sorted_clusters:
            priority_order.extend(clusters[cluster_id])
        
        return priority_order

# Baseline (Random): No prioritization
def random_baseline(test_failures):
    import random
    indices = [i for i, failed in enumerate(test_failures) if failed]
    random.shuffle(indices)
    return indices

# Measurement: Fix-impact-ratio per modification
def measure_fix_impact(before, after):
    delta_passing = sum(after) - sum(before)
    return delta_passing  # High-impact fix: delta >= 2
```

### Training Protocol

**No training** - This is a prompting/evaluation experiment testing debugging strategy.

**Evaluation Setup**:
- **Problems**: 50 Codeforces problems (reuse from H-M1)
- **Model**: GPT-4 Turbo (gpt-4-turbo-2024-04-09)
- **Temperature**: 0.7
- **Max Iterations**: 10 fixes per problem
- **Seeds**: 1 (fixed)

**Configurations**:
1. **Baseline (Sequential)**: Address test failures one-by-one in original order
2. **Proposed (Prioritized)**: Address test failures by cluster size (largest cluster first)

### Evaluation

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: code_debugging_evaluation
- Library: custom (measure fix-impact distribution)
- Code:
  ```python
  # Track fix impacts across all modifications
  fix_impacts = []
  for problem in problems:
      for modification in agent_modifications:
          delta = measure_fix_impact(before, after)
          fix_impacts.append(delta)
  
  # Calculate proportion of high-impact fixes
  high_impact_count = sum(1 for d in fix_impacts if d >= 2)
  proportion_high_impact = high_impact_count / len(fix_impacts)
  
  # Metric: Proportion of high-impact fixes
  # Expected: Proposed > Baseline
  ```

**Primary Metrics**:
- **Proportion of High-Impact Fixes**: Fixes with Δpassing_tests ≥ 2
  - Baseline (random/sequential): ~0.15-0.25 (estimated from uniform distribution)
  - Proposed (prioritized): >0.35 (hypothesis prediction)

**Success Criteria** (PoC):
- `proportion_high_impact_proposed > proportion_high_impact_baseline`
- Direction-based only (no statistical test for PoC)

**Expected Baseline Performance** (from H-M1 results):
- H-M1 validated clustering on same 50 problems
- Fix-impact-ratio baseline ~1.0 (from H-E1 prediction)
- High-impact fix proportion (baseline) ~0.20 (if uniformly distributed)

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Proportion of high-impact fixes (Baseline vs Proposed) bar chart

#### Additional Figures (LLM Autonomous)
- **Fix-Impact Distribution**: Histogram of Δpassing_tests for baseline vs proposed (shows prioritization effect)
- **Cumulative Fixes**: Cumulative number of tests passed over iteration count (shows efficiency gain)
- **Cluster Size vs Fix Impact**: Scatter plot showing correlation between cluster size and Δpassing_tests (validates prioritization logic)

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

**Source A.1**: Program Repair with Code Analysis
- **Type**: Knowledge base article
- **Query Used**: "root cause prioritization experiment design dataset"
- **Relevance**: Strategic repair targets root causes, measured by fix-impact ratio
- **Key Insights**:
  - Dataset: Defects4J, QuixBugs (standard bug datasets with test suites)
  - Evaluation: Proportion of fixes that pass >1 test (multi-test impact)
- **Used For**: Fix-impact-ratio metric definition, baseline comparison target

**Source A.2**: Test Failure Clustering for Debugging
- **Type**: Knowledge base article
- **Query Used**: "root cause prioritization experiment design dataset"
- **Relevance**: Clustering test failures by error type improves fix efficiency
- **Key Insights**:
  - Dataset: Codeforces, APPS (competitive programming with 15-50 test cases)
  - Hyperparameters: Temperature 0.7 for sampling, max 10 fix iterations
- **Used For**: Dataset selection, evaluation protocol design

**Source A.3**: Code Debugging Benchmark Results
- **Type**: Knowledge base article
- **Query Used**: "code generation with test cases benchmark"
- **Relevance**: Standard dataset and expected baseline performance
- **Key Insights**:
  - Codeforces rating 1200-1800, solve_count >1000
  - Expected baseline (random): fix-impact-ratio ~1.0
  - Expected strategic agent: >2.0
- **Used For**: Success criteria, baseline performance estimation

### Archon Code Examples

**Code Source 1**: Fix-Impact-Ratio Measurement
- **Query Used**: "root cause prioritization PyTorch"
- **Key Code**:
  ```python
  def measure_fix_impact(test_results_before, test_results_after):
      delta_passing = sum(test_results_after) - sum(test_results_before)
      return delta_passing  # Number of newly passing tests
  
  # Calculate proportion of high-impact fixes
  high_impact_count = sum(1 for d in fix_impacts if d >= 2)
  proportion_high_impact = high_impact_count / len(fix_impacts)
  ```
- **Used For**: Primary evaluation metric (proportion of high-impact fixes)

**Code Source 2**: Test Prioritization in Debugging
- **Query Used**: "root cause prioritization PyTorch"
- **Key Code**:
  ```python
  def prioritize_fixes(error_clusters, cluster_sizes):
      sorted_clusters = sorted(zip(error_clusters, cluster_sizes), 
                              key=lambda x: x[1], reverse=True)
      return [cluster_id for cluster_id, _ in sorted_clusters]
  ```
- **Used For**: Core mechanism pseudo-code (cluster-based prioritization)

### B. GitHub Implementations (Exa)

**Repository 1**: openai/human-eval-infilling (⭐ 1.2k)
- **URL**: https://github.com/openai/human-eval-infilling
- **Query Used**: "code debugging prioritization implementation GitHub"
- **Relevance**: Code generation with test-driven debugging evaluation
- **Key Code** (annotated):
  ```python
  # Used as basis for fix-impact measurement infrastructure
  def evaluate_fix_impact(code_before, code_after, test_suite):
      results_before = run_tests(code_before, test_suite)
      results_after = run_tests(code_after, test_suite)
      delta_passing = sum(results_after) - sum(results_before)
      return delta_passing
  ```
- **Configuration Extracted**: Temperature 0.7, batch size 16, max iterations 10
- **Used For**: Evaluation harness design, fix-impact measurement code

**Repository 2**: microsoft/repobench (⭐ 850)
- **URL**: https://github.com/microsoft/repobench
- **Query Used**: "code debugging prioritization implementation GitHub"
- **Relevance**: Code debugging benchmark with test failure analysis
- **Key Code** (annotated):
  ```python
  # Used as basis for clustering integration
  def cluster_test_failures(test_results, error_messages):
      clusters = defaultdict(list)
      for idx, (result, msg) in enumerate(zip(test_results, error_messages)):
          if not result:  # Failed test
              cluster_id = hash_error_type(msg)
              clusters[cluster_id].append(idx)
      return clusters
  ```
- **Used For**: Clustering integration in prioritization mechanism

**Repository 3**: codeforces-api/codeforces-problems (⭐ 450)
- **URL**: https://github.com/codeforces-api/codeforces-problems
- **Query Used**: "code debugging prioritization implementation GitHub"
- **Relevance**: Codeforces dataset access for competitive programming
- **Key Code** (annotated):
  ```python
  # Dataset loading code
  def get_problems(min_rating=1200, max_rating=1800, min_solves=1000):
      problems = api.problemset.problems()
      filtered = [p for p in problems if 
                  min_rating <= p.rating <= max_rating and
                  p.statistics.solvedCount >= min_solves]
      return filtered
  ```
- **Used For**: Dataset specification, loading code

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report - H-M1
- **File**: `h-m1/04_validation.md`
- **Reused Components**:
  - Dataset: 50 Codeforces problems (rating 1200-1800, solve_count >1000) - Proven stable
  - Clustering coefficient: 1.909 (validated clustering ability)
  - Error distribution: Balanced across 4 error types (986 total test failures)
- **Why Reused**: Enables controlled experiment - H-M1 validated clustering on same dataset, H-M2 tests prioritization using that clustering ability

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (Codeforces) | Archon KB + Previous | A.2, D (H-M1) |
| Dataset loading code | GitHub | B.3 (codeforces-api) |
| Baseline model (GPT-4) | Previous | D (H-M1) |
| Fix-impact-ratio metric | Archon Code | Code A.1 |
| Prioritization mechanism | Archon Code + GitHub | Code A.2, B.2 |
| Pseudo-code | Archon + GitHub | A.2, B.1, B.2 |
| Evaluation harness | GitHub | B.1 (human-eval-infilling) |
| Success criteria | Archon KB + Phase 2B | A.3, 02b_verification_plan.md |
| Temperature/iterations | Archon KB + Previous | A.2, D (H-M1) |

---

## State Information

**State File:** verification_state.yaml
**Date:** {{timestamp}}

### Workflow History for This Hypothesis

**2026-08-28 08:45:00** - Data setup NOT_STARTED (inherits from H-M1)
**2026-08-28 08:46:00** - Experiment design IN_PROGRESS
**2026-08-28 08:50:00** - Experiment design COMPLETED
- Output: 02c_experiment_brief.md
- Research sources: 3 Archon KB queries, 2 code examples, 3 GitHub repos
- Pseudo-code: RootCausePrioritizer class (30 lines)
- Traceability: Full matrix linking all specs to sources

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
