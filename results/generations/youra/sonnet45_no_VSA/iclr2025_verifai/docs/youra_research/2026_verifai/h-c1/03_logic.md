# Logic/API Specification: H-C1 Compute-Matched Control Experiment

**Hypothesis ID:** h-c1  
**Type:** CONTROL CONDITION  
**Date:** 2026-07-11  
**Status:** Phase 3 - Logic Design  
**Prerequisites:** h-m1 (VALIDATED)

---

## Codebase Analysis (Serena)

**Project Type**: Base hypothesis exists (h-m1)  
**Status**: API signatures verified from h-m1 actual code  
**Analyzed Path**: docs/youra_research/h-m1/code/code/src/  
**Relevant Symbols**: IterativeRefinementLoop, SpecificationGenerator, FramaCVerifier, FeedbackExtractor, ACSLSpec, VerificationResult, StructuredFeedback

---

## Applied Patterns

**Applied**: PyTorch/Anthropic API patterns, statistical analysis pipeline

---

## Core Data Structures

### DS-1: ComputeBudget

```python
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class ComputeBudget:
    """Track compute usage per experiment."""
    total_tokens: int  # Prompt + completion tokens
    verifier_time_seconds: float  # Total Frama-C execution time
    llm_api_calls: int  # Number of LLM invocations
    iterations_or_samples: int  # Refinement iterations or N samples
    per_iteration_tokens: List[int]  # Token breakdown
    per_iteration_times: List[float]  # Time breakdown
    
    def utilization_ratio(self, target: 'ComputeBudget') -> Dict[str, float]:
        """Compute budget utilization as ratio of target."""
        return {
            'token_ratio': self.total_tokens / target.total_tokens if target.total_tokens > 0 else 0.0,
            'time_ratio': self.verifier_time_seconds / target.verifier_time_seconds if target.verifier_time_seconds > 0 else 0.0
        }
    
    def within_bounds(self, target: 'ComputeBudget', tolerance: float = 0.10) -> bool:
        """Check if within ±tolerance of target budget."""
        ratios = self.utilization_ratio(target)
        return (0.90 <= ratios['token_ratio'] <= 1.10) and (0.90 <= ratios['time_ratio'] <= 1.10)
```

### DS-2: ExperimentResult

```python
@dataclass
class ExperimentResult:
    """Single program evaluation result."""
    program_id: str
    baseline_name: str  # 'IterativeFeedback' | 'SelfConsistency' | 'Hybrid'
    discharge_rate: float  # 0-100%
    final_spec: str  # ACSL-annotated code
    compute_budget: ComputeBudget
    budget_violation: bool  # True if exceeds 110% target
    convergence_reason: str  # From h-m1 ConvergenceReason
    error_message: Optional[str] = None
```

### DS-3: ProgramMetadata

```python
@dataclass
class ProgramMetadata:
    """Dataset program information."""
    program_id: str
    source_code: str  # Unannotated C code
    gold_spec: str  # Expert ACSL annotations
    complexity: str  # 'simple' | 'medium' | 'complex'
    proof_obligations: int
    description: str
```

### DS-4: FeedbackData (Reuse from h-m1)

```python
# From h-m1: StructuredFeedback dataclass
# Already defined in feedback_parser.py
# Includes: witness, structure, dependency dimensions
```

---

## Algorithm 1: Iterative Feedback Baseline (Reuse from h-m1)

### API Signature

```python
from pathlib import Path
from typing import Tuple
from .h_m1_refinement import IterativeRefinementLoop, RefinementHistory  # Reuse

def iterative_feedback_baseline(
    program: ProgramMetadata,
    budget_tracker: 'ComputeBudgetTracker',
    generator: SpecificationGenerator,
    verifier: FramaCVerifier,
    feedback_extractor: FeedbackExtractor,
    temp_dir: Path,
    max_iterations: int = 10
) -> Tuple[str, float, ComputeBudget]:
    """
    Run iterative feedback refinement (from h-m1).
    
    Args:
        program: Input C program metadata
        budget_tracker: Compute budget tracker
        generator: LLM spec generator (from h-m1)
        verifier: Frama-C verifier (from h-m1)
        feedback_extractor: Feedback parser (from h-m1)
        temp_dir: Working directory
        max_iterations: Max refinement cycles
    
    Returns:
        (final_spec, discharge_rate, compute_budget)
    """
    pass  # Implementation in pseudo-code below
```

### Pseudo-code

```
1. Initialize refinement loop (reuse h-m1 IterativeRefinementLoop)
2. FOR iter in range(max_iterations):
3.     budget_tracker.start_iteration()
4.     
5.     IF iter == 0:
6.         spec = generator.generate_initial_spec(program.source_code)
7.     ELSE:
8.         spec = refine_with_feedback(current_spec, feedback)
9.     
10.    budget_tracker.record_llm_call(prompt_tokens, completion_tokens)
11.    
12.    result = verifier.verify(spec, temp_dir)
13.    budget_tracker.record_verifier_call(execution_time)
14.    
15.    IF result.proof_discharge_rate >= 100.0:
16.        BREAK  # All proved
17.    
18.    feedback = feedback_extractor.extract_feedback(result, spec)
19.    
20.    IF no_improvement_for_N_iterations(result):
21.        BREAK  # Early stopping
22.    
23.    current_spec = spec
24.
25. budget = budget_tracker.finalize()
26. RETURN (current_spec, result.proof_discharge_rate, budget)
```

---

## Algorithm 2: Self-Consistency Baseline (NEW)

### API Signatures

```python
def self_consistency_baseline(
    program: ProgramMetadata,
    N: int,
    budget_tracker: 'ComputeBudgetTracker',
    generator: SpecificationGenerator,
    verifier: FramaCVerifier,
    temp_dir: Path,
    selection_strategy: str = "best_of_n"
) -> Tuple[str, float, ComputeBudget]:
    """
    Generate N independent samples, select best.
    
    Args:
        program: Input program
        N: Number of independent samples (from budget matching)
        budget_tracker: Compute tracker
        generator: LLM client
        verifier: Frama-C verifier
        temp_dir: Working directory
        selection_strategy: 'best_of_n' | 'majority_voting'
    
    Returns:
        (selected_spec, discharge_rate, compute_budget)
    """
    pass
```

### Pseudo-code: Best-of-N Selection

```
1. samples = []
2. results = []
3. 
4. FOR i in range(N):
5.     budget_tracker.start_sample(i)
6.     
7.     # Generate independent sample (temperature=0.7, different seed)
8.     spec = generator.generate_initial_spec(
9.         program.source_code,
10.        temperature=0.7,
11.        seed=42 + program_index * 1000 + i
12.    )
13.    budget_tracker.record_llm_call(prompt_tokens, completion_tokens)
14.    
15.    # Verify sample
16.    result = verifier.verify(spec, temp_dir)
17.    budget_tracker.record_verifier_call(execution_time)
18.    
19.    samples.append(spec)
20.    results.append(result)
21.
22. # Select best by discharge rate
23. best_idx = argmax([r.proof_discharge_rate for r in results])
24. budget = budget_tracker.finalize()
25.
26. RETURN (samples[best_idx], results[best_idx].proof_discharge_rate, budget)
```

### Pseudo-code: Majority Voting Selection

```
1. # Generate N samples (same as best-of-N, lines 1-20)
2. 
3. # Aggregate obligation-level votes
4. obligation_votes = {}  # obligation_id -> List[bool]
5. 
6. FOR result in results:
7.     FOR obligation in result.obligations:
8.         IF obligation.obligation_id NOT IN obligation_votes:
9.             obligation_votes[obligation.obligation_id] = []
10.        obligation_votes[obligation.obligation_id].append(
11.            obligation.status == ProofStatus.VALID
12.        )
13.
14. # Construct consensus spec (merge clauses by majority)
15. consensus_spec = construct_consensus_spec(samples, obligation_votes)
16.
17. # Final verification
18. final_result = verifier.verify(consensus_spec, temp_dir)
19. budget_tracker.record_verifier_call(execution_time)
20.
21. RETURN (consensus_spec, final_result.proof_discharge_rate, budget)
```

---

## Algorithm 3: Hybrid Baseline (Exploratory)

### API Signature

```python
def hybrid_sample_then_refine(
    program: ProgramMetadata,
    target_budget: ComputeBudget,
    budget_tracker: 'ComputeBudgetTracker',
    generator: SpecificationGenerator,
    verifier: FramaCVerifier,
    feedback_extractor: FeedbackExtractor,
    temp_dir: Path,
    K: int = 3
) -> Tuple[str, float, ComputeBudget]:
    """
    Sample K candidates, select best, refine with remaining budget.
    
    Args:
        program: Input program
        target_budget: Budget constraint from validation set
        budget_tracker: Compute tracker
        generator: LLM client
        verifier: Frama-C verifier
        feedback_extractor: Feedback parser
        temp_dir: Working directory
        K: Initial samples (default: 3)
    
    Returns:
        (final_spec, discharge_rate, compute_budget)
    """
    pass
```

### Pseudo-code

```
1. # Phase 1: Initial sampling
2. initial_samples = []
3. initial_results = []
4. 
5. FOR i in range(K):
6.     budget_tracker.start_sample(i)
7.     spec = generator.generate_initial_spec(program.source_code, temperature=0.7, seed=i)
8.     budget_tracker.record_llm_call(tokens)
9.     
10.    result = verifier.verify(spec, temp_dir)
11.    budget_tracker.record_verifier_call(time)
12.    
13.    initial_samples.append(spec)
14.    initial_results.append(result)
15.
16. # Select best initial sample
17. best_idx = argmax([r.proof_discharge_rate for r in initial_results])
18. current_spec = initial_samples[best_idx]
19.
20. # Phase 2: Refine with remaining budget
21. remaining_budget = compute_remaining_budget(budget_tracker, target_budget)
22. max_refinement_iters = estimate_affordable_iterations(remaining_budget)
23.
24. FOR iteration in range(max_refinement_iters):
25.     IF budget_tracker.exceeds_target(target_budget):
26.         BREAK  # Budget exhausted
27.     
28.     result = verifier.verify(current_spec, temp_dir)
29.     budget_tracker.record_verifier_call(time)
30.     
31.     IF result.proof_discharge_rate >= 100.0:
32.         BREAK  # All proved
33.     
34.     feedback = feedback_extractor.extract_feedback(result, current_spec)
35.     current_spec = generator.refine_spec(current_spec, feedback, temperature=0.2)
36.     budget_tracker.record_llm_call(tokens)
37.
38. budget = budget_tracker.finalize()
39. RETURN (current_spec, result.proof_discharge_rate, budget)
```

---

## Algorithm 4: Compute Budget Matching

### API Signature

```python
from typing import List

def compute_matched_sample_count(
    validation_budgets: List[ComputeBudget],
    single_shot_estimate: ComputeBudget
) -> int:
    """
    Calculate N for self-consistency baseline from validation set statistics.
    
    Args:
        validation_budgets: Budgets from iterative feedback on validation set
        single_shot_estimate: Estimated tokens/time for single LLM call
    
    Returns:
        N (number of samples within budget)
    """
    pass
```

### Pseudo-code

```
1. # Calculate average from validation set
2. avg_tokens = mean([b.total_tokens for b in validation_budgets])
3. avg_time = mean([b.verifier_time_seconds for b in validation_budgets])
4. avg_iters = mean([b.iterations_or_samples for b in validation_budgets])
5.
6. # Estimate N from token budget (with 5% margin)
7. N_from_tokens = floor((avg_tokens * 0.95) / single_shot_estimate.total_tokens)
8.
9. # Estimate N from time budget
10. N_from_time = floor((avg_time * 0.95) / single_shot_estimate.verifier_time_seconds)
11.
12. # Conservative estimate (minimum of constraints)
13. N = min(N_from_tokens, N_from_time, avg_iters)
14.
15. # Ensure minimum 3 samples
16. N = max(N, 3)
17.
18. RETURN N
```

---

## Algorithm 5: Statistical Analysis

### API Signatures

```python
from typing import Dict, Any
from scipy import stats

def primary_hypothesis_test(
    baseline1_rates: List[float],
    baseline2_rates: List[float]
) -> Dict[str, Any]:
    """
    Paired t-test for compute-matched comparison.
    
    Args:
        baseline1_rates: Discharge rates from iterative feedback
        baseline2_rates: Discharge rates from self-consistency (paired)
    
    Returns:
        Statistical test results
    """
    pass

def validate_compute_fairness(
    baseline1_budgets: List[ComputeBudget],
    baseline2_budgets: List[ComputeBudget]
) -> Dict[str, Any]:
    """
    Check if compute budgets are matched within 10% tolerance.
    
    Args:
        baseline1_budgets: Budgets from baseline 1
        baseline2_budgets: Budgets from baseline 2 (paired)
    
    Returns:
        Fairness validation results
    """
    pass

def make_gate_decision(
    primary_test: Dict[str, Any],
    fairness_check: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Determine if MUST_WORK gate is satisfied.
    
    Args:
        primary_test: Results from primary_hypothesis_test
        fairness_check: Results from validate_compute_fairness
    
    Returns:
        Gate decision with criteria breakdown
    """
    pass
```

### Pseudo-code: Primary Hypothesis Test

```
1. # Paired t-test
2. t_stat, p_value = scipy.stats.ttest_rel(baseline1_rates, baseline2_rates)
3.
4. # Mean difference
5. mean_diff = mean(baseline1_rates) - mean(baseline2_rates)
6.
7. # Effect size (Cohen's d for paired samples)
8. differences = [b1 - b2 for b1, b2 in zip(baseline1_rates, baseline2_rates)]
9. std_diff = std(differences)
10. cohens_d = mean_diff / std_diff
11.
12. # Check gate criteria
13. gate_satisfied = (
14.     mean_diff >= 10.0 AND
15.     p_value < 0.05 AND
16.     cohens_d >= 0.5
17. )
18.
19. RETURN {
20.     'mean_baseline1': mean(baseline1_rates),
21.     'mean_baseline2': mean(baseline2_rates),
22.     'mean_difference': mean_diff,
23.     't_statistic': t_stat,
24.     'p_value': p_value,
25.     'cohens_d': cohens_d,
26.     'gate_satisfied': gate_satisfied
27. }
```

### Pseudo-code: Compute Fairness Validation

```
1. # Token fairness
2. b1_tokens = mean([b.total_tokens for b in baseline1_budgets])
3. b2_tokens = mean([b.total_tokens for b in baseline2_budgets])
4. token_ratio = b2_tokens / b1_tokens
5.
6. # Time fairness
7. b1_time = mean([b.verifier_time_seconds for b in baseline1_budgets])
8. b2_time = mean([b.verifier_time_seconds for b in baseline2_budgets])
9. time_ratio = b2_time / b1_time
10.
11. # Check within 10% margin
12. token_fair = (0.90 <= token_ratio <= 1.10)
13. time_fair = (0.90 <= time_ratio <= 1.10)
14.
15. RETURN {
16.     'baseline1_avg_tokens': b1_tokens,
17.     'baseline2_avg_tokens': b2_tokens,
18.     'token_ratio': token_ratio,
19.     'token_budget_fair': token_fair,
20.     'baseline1_avg_time': b1_time,
21.     'baseline2_avg_time': b2_time,
22.     'time_ratio': time_ratio,
23.     'time_budget_fair': time_fair,
24.     'overall_fair': token_fair AND time_fair
25. }
```

### Pseudo-code: Gate Decision

```
1. # All 4 criteria must pass
2. criteria = {
3.     'mean_difference_10pp': primary_test['mean_difference'] >= 10.0,
4.     'statistical_significance': primary_test['p_value'] < 0.05,
5.     'medium_effect_size': primary_test['cohens_d'] >= 0.5,
6.     'compute_budget_fair': fairness_check['overall_fair']
7. }
8.
9. gate_satisfied = ALL(criteria.values())
10.
11. RETURN {
12.     'gate_decision': 'SATISFIED' IF gate_satisfied ELSE 'FAILED',
13.     'criteria': criteria,
14.     'failure_reasons': [k for k, v in criteria.items() IF NOT v]
15. }
```

---

## Supporting Classes

### ComputeBudgetTracker

```python
class ComputeBudgetTracker:
    """Track compute usage during experiment execution."""
    
    def __init__(self, target: Optional[ComputeBudget] = None):
        """
        Args:
            target: Target budget for validation (optional)
        """
        self.target = target
        self.total_tokens = 0
        self.verifier_time = 0.0
        self.llm_calls = 0
        self.iterations = 0
        self.token_history = []
        self.time_history = []
    
    def start_iteration(self) -> None:
        """Start tracking new iteration."""
        self.iterations += 1
    
    def record_llm_call(self, prompt_tokens: int, completion_tokens: int) -> None:
        """Record LLM API call. tokens: prompt + completion"""
        tokens = prompt_tokens + completion_tokens
        self.total_tokens += tokens
        self.llm_calls += 1
        self.token_history.append(tokens)
    
    def record_verifier_call(self, execution_time: float) -> None:
        """Record verifier execution. time: seconds"""
        self.verifier_time += execution_time
        self.time_history.append(execution_time)
    
    def exceeds_target(self, tolerance: float = 0.10) -> bool:
        """Check if current usage exceeds target (1 + tolerance)."""
        if self.target is None:
            return False
        
        token_exceeded = self.total_tokens > self.target.total_tokens * (1 + tolerance)
        time_exceeded = self.verifier_time > self.target.verifier_time_seconds * (1 + tolerance)
        
        return token_exceeded or time_exceeded
    
    def finalize(self) -> ComputeBudget:
        """Return final budget object."""
        return ComputeBudget(
            total_tokens=self.total_tokens,
            verifier_time_seconds=self.verifier_time,
            llm_api_calls=self.llm_calls,
            iterations_or_samples=self.iterations,
            per_iteration_tokens=self.token_history,
            per_iteration_times=self.time_history
        )
```

### ExperimentRunner

```python
class ExperimentRunner:
    """Orchestrate multi-baseline evaluation."""
    
    def __init__(
        self,
        generator: SpecificationGenerator,
        verifier: FramaCVerifier,
        feedback_extractor: FeedbackExtractor,
        temp_dir: Path,
        checkpoint_dir: Path
    ):
        """
        Args:
            generator: LLM client (from h-m1)
            verifier: Frama-C verifier (from h-m1)
            feedback_extractor: Feedback parser (from h-m1)
            temp_dir: Working directory
            checkpoint_dir: Checkpoint storage
        """
        self.generator = generator
        self.verifier = verifier
        self.feedback_extractor = feedback_extractor
        self.temp_dir = temp_dir
        self.checkpoint_dir = checkpoint_dir
    
    def calibrate_budgets(
        self,
        validation_set: List[ProgramMetadata]
    ) -> Tuple[ComputeBudget, int]:
        """
        Stage 1: Run baseline 1 on validation set, compute average budget.
        
        Returns:
            (avg_budget, N_for_baseline2)
        """
        pass
    
    def run_test_evaluation(
        self,
        test_set: List[ProgramMetadata],
        avg_budget: ComputeBudget,
        N: int
    ) -> List[Dict[str, ExperimentResult]]:
        """
        Stage 2: Run all baselines on test set.
        
        Args:
            test_set: 50 programs
            avg_budget: From calibration
            N: Sample count for baseline 2
        
        Returns:
            Results for all programs × baselines
        """
        pass
    
    def save_checkpoint(self, results: List[Dict], checkpoint_id: int) -> None:
        """Save results checkpoint every 10 programs."""
        pass
    
    def load_checkpoint(self, checkpoint_id: int) -> List[Dict]:
        """Resume from checkpoint."""
        pass
```

---

## External Dependencies (Base Hypothesis)

### API Signatures (From h-m1 Actual Code)

The following APIs are called from h-m1. Signatures verified from actual implementation:

```python
# From: docs/youra_research/h-m1/code/code/src/refinement_loop.py
class IterativeRefinementLoop:
    def __init__(
        self,
        generator: SpecificationGenerator,
        verifier: FramaCVerifier,
        feedback_extractor: FeedbackExtractor,
        max_iterations: int = 10,
        no_improvement_threshold: int = 3
    ):
        """Initialize refinement loop."""
        pass
    
    def synthesize_specification(
        self,
        c_code: str,
        temp_dir: Path
    ) -> RefinementHistory:
        """Complete synthesis pipeline. c_code: str -> RefinementHistory"""
        pass

# From: docs/youra_research/h-m1/code/code/src/llm_client.py
class SpecificationGenerator:
    def __init__(self, api_key: str, model: str = "claude-opus-4-5"):
        """Initialize LLM client."""
        pass
    
    def generate_initial_spec(
        self,
        c_code: str,
        verification_goal: str = "functional correctness"
    ) -> ACSLSpec:
        """Generate ACSL spec. c_code: str -> ACSLSpec"""
        pass

# From: docs/youra_research/h-m1/code/code/src/verifier.py
class FramaCVerifier:
    def __init__(
        self,
        timeout_per_obligation: int = 10,
        provers: List[str] = None
    ):
        """Initialize verifier."""
        pass
    
    def verify(self, acsl_spec: ACSLSpec, temp_dir: Path) -> VerificationResult:
        """Verify spec. acsl_spec: ACSLSpec -> VerificationResult"""
        pass

# From: docs/youra_research/h-m1/code/code/src/feedback_parser.py
class FeedbackExtractor:
    def extract_feedback(
        self,
        result: VerificationResult,
        acsl_spec: ACSLSpec
    ) -> Optional[StructuredFeedback]:
        """Extract 3D feedback. result: VerificationResult -> StructuredFeedback"""
        pass
```

**Verified from**: docs/youra_research/h-m1/code/code/src/ (actual implementation)

---

## Tensor/Data Shapes

| Variable | Type | Shape/Structure | Notes |
|----------|------|-----------------|-------|
| validation_set | List[ProgramMetadata] | [15] | Budget calibration |
| test_set | List[ProgramMetadata] | [50] | Final evaluation |
| baseline1_rates | List[float] | [50] | Discharge rates 0-100% |
| baseline2_rates | List[float] | [50] | Paired with baseline1 |
| validation_budgets | List[ComputeBudget] | [15] | Per-program budgets |
| per_iteration_tokens | List[int] | [max_iterations] | Token breakdown |
| per_iteration_times | List[float] | [max_iterations] | Time breakdown |

---

## Error Handling

### Retry Logic

```python
def run_with_retry(
    baseline_func: Callable,
    program: ProgramMetadata,
    max_retries: int = 3
) -> Optional[ExperimentResult]:
    """Execute baseline with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return baseline_func(program)
        except LLMAPIError as e:
            if attempt < max_retries - 1:
                sleep(2 ** attempt)  # Exponential backoff
                continue
            else:
                return None  # Failed after all retries
        except VerifierCrashError as e:
            return None  # Verifier error - skip program
```

### Timeout Protection

```python
def run_with_timeout(
    baseline_func: Callable,
    program: ProgramMetadata,
    timeout_minutes: int = 30
) -> Optional[ExperimentResult]:
    """Execute with per-program timeout."""
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError("Program execution exceeded timeout")
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_minutes * 60)
    
    try:
        result = baseline_func(program)
        signal.alarm(0)  # Cancel alarm
        return result
    except TimeoutError:
        return None  # Timeout - mark as failed
```

---

## Complexity Analysis

| Algorithm | Time Complexity | Space Complexity | Notes |
|-----------|-----------------|------------------|-------|
| iterative_feedback_baseline | O(I × T_llm × T_verifier) | O(I × S_spec) | I=iterations (≤10) |
| self_consistency_baseline | O(N × T_llm × T_verifier) | O(N × S_spec) | N=samples (≈7) |
| hybrid_sample_then_refine | O((K + R) × T_llm × T_verifier) | O((K + R) × S_spec) | K=3, R=refinements |
| compute_matched_sample_count | O(V) | O(1) | V=validation set size (15) |
| primary_hypothesis_test | O(n) | O(n) | n=test set size (50) |
| validate_compute_fairness | O(n) | O(1) | Linear scan of budgets |

Where:
- T_llm: LLM API latency (~2-5 sec)
- T_verifier: Frama-C WP time (~10-30 sec)
- S_spec: Specification size (~5KB)
- I, N, K, R: Iteration/sample counts

---

## Configuration Schema

```yaml
experiment:
  hypothesis_id: h-c1
  dataset: h-m1-benchmark
  validation_set_size: 15
  test_set_size: 50

llm:
  model: claude-opus-4-5
  temperature_refinement: 0.2
  temperature_sampling: 0.7
  max_tokens: 4096
  top_p: 0.95

verifier:
  tool: frama-c
  timeout_per_obligation: 10
  provers: [alt-ergo, z3]

baselines:
  iterative_feedback:
    max_iterations: 10
    no_improvement_threshold: 3
  self_consistency:
    selection_strategy: best_of_n
    min_samples: 3
  hybrid:
    initial_samples: 3

compute_budget:
  fairness_tolerance: 0.10
  tracking_precision: 0.001

gate:
  min_gap_pp: 10.0
  alpha: 0.05
  min_effect_size: 0.5
```

---

## Summary

This logic specification defines:
- **5 core algorithms**: Iterative feedback (h-m1 reuse), self-consistency (new), hybrid (new), budget matching (new), statistical analysis (new)
- **4 data structures**: ComputeBudget, ExperimentResult, ProgramMetadata, FeedbackData
- **3 baselines**: Compute-matched comparison with detailed pseudo-code
- **2 supporting classes**: ComputeBudgetTracker, ExperimentRunner
- **Statistical pipeline**: Paired t-test, effect size, fairness validation, gate decision

**Phase 4 Implementation Roadmap:**
1. Week 1: Implement ComputeBudgetTracker + self_consistency_baseline
2. Week 2: Implement hybrid_sample_then_refine + statistical analysis
3. Week 3: Implement ExperimentRunner + checkpoint system
4. Week 4-5: Run calibration + test evaluation
5. Week 6: Generate validation report

**Total**: 6 algorithms, 8 API specifications, 4 data structures, comprehensive statistical pipeline.
