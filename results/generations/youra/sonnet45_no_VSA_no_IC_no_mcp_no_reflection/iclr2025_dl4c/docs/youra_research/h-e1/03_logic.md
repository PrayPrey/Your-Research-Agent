# Logic Design: Fix-Impact-Ratio Measurement System

**Hypothesis:** h-e1  
**Type:** EXISTENCE (LIGHT tier)  
**Generated:** 2026-08-28  
**Phase:** 3 — Implementation Planning

---

## Codebase Analysis (Serena)

**MCP Status:** Serena MCP not available  
**Analysis Mode:** Green-field (no existing logic to analyze)

**Applied:** Light-tier Logic Pattern (Archon KB) — minimal API surface, focused on core computation

---

## Core API Signatures

### 1. Dataset Module

#### Problem Fetcher
```python
class CodeforcesFetcher:
    """Fetch problems from Codeforces API or CodeContests dataset."""
    
    def fetch_problems(
        self,
        min_rating: int = 1200,
        max_rating: int = 1800,
        min_solve_count: int = 1000,
        min_test_cases: int = 15,
        limit: int = 200
    ) -> List[Problem]:
        """
        Fetch and filter problems matching criteria.
        
        Returns:
            List of Problem objects with test_cases ≥ min_test_cases
        """
        pass
```

#### Ground Truth Validator
```python
def validate_ground_truth(problem: Problem) -> bool:
    """
    Run ground truth solution against all test cases.
    
    Returns:
        True if 100% tests pass, else False
    """
    pass
```

---

### 2. Experiment Runner Interface

#### Base Runner (Abstract)
```python
class ExperimentRunner(ABC):
    """Abstract base for all experiment runners (baselines + agents)."""
    
    @abstractmethod
    def run(self, problem: Problem) -> ExperimentResult:
        """
        Execute experiment on one problem.
        
        Returns:
            ExperimentResult with fix_impact_ratio, iterations, modifications
        """
        pass
    
    def compute_fix_impact_ratio(
        self,
        modifications: List[Modification]
    ) -> float:
        """
        Compute fix-impact-ratio = Σ(Δtests_passing) / len(modifications)
        """
        total_delta = sum(mod.tests_fixed for mod in modifications)
        return total_delta / len(modifications) if modifications else 0.0
```

---

### 3. Agent Logic

#### Agent A: GPT-4 Baseline
```python
class GPT4BaselineAgent(ExperimentRunner):
    """Standard debugging prompt, no explicit clustering."""
    
    def run(self, problem: Problem) -> ExperimentResult:
        """
        1. Generate initial solution
        2. Loop (max 10 iterations):
           - Run tests
           - If failures, pass to prompt
           - Generate fix
           - Track Δtests_passing
        """
        pass
    
    def _generate_fix(self, code: str, failures: List[TestFailure]) -> str:
        """
        Prompt: "Fix the code to pass all test cases."
        """
        pass
```

#### Agent B: GPT-4 + Memory
```python
class GPT4MemoryAgent(ExperimentRunner):
    """Memory module stores past error patterns."""
    
    def __init__(self):
        self.memory: Dict[str, List[FixAttempt]] = {}
    
    def run(self, problem: Problem) -> ExperimentResult:
        """
        1. Generate initial solution
        2. Loop (max 10 iterations):
           - Extract error signatures from failures
           - Query memory for similar errors
           - Pass memory context to prompt
           - Generate fix
           - Update memory
        """
        pass
    
    def _query_memory(self, error_sig: str) -> List[FixAttempt]:
        """Retrieve similar error patterns from memory."""
        pass
```

#### Agent C: GPT-4 + Explicit Prompting
```python
class GPT4ExplicitAgent(ExperimentRunner):
    """Explicit error clustering instruction."""
    
    def run(self, problem: Problem) -> ExperimentResult:
        """
        1. Generate initial solution
        2. Loop (max 10 iterations):
           - Prompt: "Step 1: Cluster errors. Step 2: Prioritize. Step 3: Fix."
           - Parse structured output {clusters: [{root_cause, tests, fix}]}
           - Apply highest-impact fix
           - Track Δtests_passing
        """
        pass
    
    def _parse_clustering(self, response: str) -> List[ErrorCluster]:
        """Parse agent's structured clustering output."""
        pass
```

---

### 4. Metrics Computation

#### Fix-Impact-Ratio
```python
def compute_fix_impact_ratio(modifications: List[Modification]) -> float:
    """
    Primary metric: Σ(Δpassing_tests) / total_modifications
    
    Args:
        modifications: List of code changes with tests_fixed count
    
    Returns:
        Ratio (0 to ∞); baseline ≈ 1.0, strategic ≥ 2.0
    """
    if not modifications:
        return 0.0
    total_delta = sum(mod.tests_fixed for mod in modifications)
    return total_delta / len(modifications)
```

#### Secondary Metrics
```python
def compute_pass_rate(tests_passed: int, total_tests: int) -> float:
    """Final test pass rate (%)."""
    return (tests_passed / total_tests) * 100

def compute_convergence_iteration(pass_rates: List[float]) -> int:
    """First iteration where pass_rate plateaus."""
    for i in range(len(pass_rates) - 1):
        if pass_rates[i] == pass_rates[i+1]:
            return i
    return len(pass_rates) - 1

def compute_high_impact_proportion(modifications: List[Modification]) -> float:
    """Proportion of modifications with Δtests ≥ 2."""
    high_impact = sum(1 for mod in modifications if mod.tests_fixed >= 2)
    return high_impact / len(modifications) if modifications else 0.0
```

---

### 5. Code Execution Sandbox

#### Test Execution
```python
def execute_code(
    code: str,
    test_input: str,
    expected_output: str,
    timeout_seconds: int = 10
) -> TestResult:
    """
    Execute code in sandbox with timeout.
    
    Returns:
        TestResult(passed: bool, actual_output: str, error: Optional[str])
    """
    pass

def run_all_tests(code: str, test_cases: List[TestCase]) -> List[TestResult]:
    """Run code against all test cases, return results."""
    pass
```

---

### 6. Statistical Analysis

#### Mann-Whitney U Test
```python
def mann_whitney_u_test(
    agent_ratios: List[float],
    baseline_ratios: List[float]
) -> Tuple[float, float]:
    """
    One-tailed Mann-Whitney U test.
    
    Returns:
        (u_statistic, p_value)
    """
    from scipy.stats import mannwhitneyu
    return mannwhitneyu(agent_ratios, baseline_ratios, alternative='greater')
```

#### Cohen's d Effect Size
```python
def cohens_d(
    agent_ratios: List[float],
    baseline_ratios: List[float]
) -> float:
    """
    Effect size: (mean_agent - mean_baseline) / pooled_std
    """
    mean_a = np.mean(agent_ratios)
    mean_b = np.mean(baseline_ratios)
    pooled_std = np.sqrt((np.var(agent_ratios) + np.var(baseline_ratios)) / 2)
    return (mean_a - mean_b) / pooled_std if pooled_std > 0 else 0.0
```

#### Pearson Correlation
```python
def pearson_correlation(
    fix_impact_ratios: List[float],
    pass_rates: List[float]
) -> Tuple[float, float]:
    """
    Correlation between fix-impact-ratio and final pass rate.
    
    Returns:
        (correlation_coefficient, p_value)
    """
    from scipy.stats import pearsonr
    return pearsonr(fix_impact_ratios, pass_rates)
```

---

## Tensor Shapes and Data Structures

### Problem Data Model
```python
@dataclass
class TestCase:
    input: str
    expected_output: str

@dataclass
class Problem:
    problem_id: str
    statement: str
    solution: str  # ground truth code
    test_cases: List[TestCase]  # Shape: (15+,)
    metadata: Dict[str, Any]
```

### Experiment Result Data Model
```python
@dataclass
class Modification:
    iteration: int
    tests_fixed: int  # Δpassing_tests
    code_diff: str

@dataclass
class ExperimentResult:
    problem_id: str
    fix_impact_ratio: float
    final_pass_rate: float
    iterations_to_convergence: int
    high_impact_fix_proportion: float
    modifications: List[Modification]  # Shape: (≤10,)
```

### Aggregated Results Data Model
```python
@dataclass
class AggregatedMetrics:
    mean_fix_impact_ratio: float
    std_fix_impact_ratio: float
    median_fix_impact_ratio: float
    mean_pass_rate: float
    mean_iterations: float
    problem_results: List[ExperimentResult]  # Shape: (50,)
```

---

## Algorithmic Pseudo-code

### Agent Debugging Loop
```python
def debugging_loop(problem: Problem, agent: Agent) -> ExperimentResult:
    """
    Standard debugging loop for all agents.
    """
    code = agent.generate_initial_solution(problem.statement)
    modifications = []
    max_iterations = 10
    
    for iteration in range(max_iterations):
        test_results = run_all_tests(code, problem.test_cases)
        passing_tests = sum(1 for r in test_results if r.passed)
        
        if passing_tests == len(problem.test_cases):
            break  # 100% pass, done
        
        failures = [r for r in test_results if not r.passed]
        new_code = agent.generate_fix(code, failures)
        
        # Track delta
        new_test_results = run_all_tests(new_code, problem.test_cases)
        new_passing = sum(1 for r in new_test_results if r.passed)
        delta = new_passing - passing_tests
        
        modifications.append(Modification(
            iteration=iteration,
            tests_fixed=delta,
            code_diff=compute_diff(code, new_code)
        ))
        
        code = new_code
    
    return ExperimentResult(
        problem_id=problem.problem_id,
        fix_impact_ratio=compute_fix_impact_ratio(modifications),
        final_pass_rate=compute_pass_rate(passing_tests, len(problem.test_cases)),
        iterations_to_convergence=iteration,
        high_impact_fix_proportion=compute_high_impact_proportion(modifications),
        modifications=modifications
    )
```

### Statistical Validation Pipeline
```python
def validate_hypothesis(
    agent_results: AggregatedMetrics,
    baseline_results: AggregatedMetrics
) -> GateStatus:
    """
    Verify MUST_WORK gate criteria.
    """
    # Criterion 1: Agent ratio > 2.0
    if agent_results.mean_fix_impact_ratio <= 2.0:
        return GateStatus.FAIL("Agent ratio ≤ 2.0")
    
    # Criterion 2: Baseline ratio ≈ 1.0
    if not (0.8 <= baseline_results.mean_fix_impact_ratio <= 1.2):
        return GateStatus.FAIL("Baseline ratio not ≈ 1.0 (metric insensitive)")
    
    # Criterion 3: Statistical significance
    _, p_value = mann_whitney_u_test(
        [r.fix_impact_ratio for r in agent_results.problem_results],
        [r.fix_impact_ratio for r in baseline_results.problem_results]
    )
    if p_value >= 0.05:
        return GateStatus.FAIL(f"p = {p_value:.3f} ≥ 0.05 (not significant)")
    
    # Criterion 4: Effect size
    d = cohens_d(
        [r.fix_impact_ratio for r in agent_results.problem_results],
        [r.fix_impact_ratio for r in baseline_results.problem_results]
    )
    if d < 0.5:
        return GateStatus.FAIL(f"Cohen's d = {d:.2f} < 0.5 (small effect)")
    
    return GateStatus.PASS(f"All criteria met: ratio={agent_results.mean_fix_impact_ratio:.2f}, p={p_value:.3f}, d={d:.2f}")
```

---

## Applied Patterns Summary

| Pattern | Source | Application |
|---------|--------|-------------|
| Debugging Loop Pattern | Archon KB | All agents share same loop structure |
| Memory Retrieval Pattern | Archon KB | Agent B queries past error patterns |
| Structured Prompting Pattern | Archon KB | Agent C parses clustering output |
| Metrics Aggregation Pattern | Archon KB | Collect per-problem, aggregate to dataset level |
| Hypothesis Testing Pattern | Archon KB | Mann-Whitney U + Cohen's d validation |

---

**End of Logic Design Document**
