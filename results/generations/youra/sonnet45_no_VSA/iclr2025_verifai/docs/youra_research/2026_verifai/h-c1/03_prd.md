# Product Requirements Document: H-C1 Compute-Matched Control Experiment

**Hypothesis ID:** h-c1  
**Type:** CONTROL CONDITION  
**Date:** 2026-07-11  
**Author:** Anonymous  
**Status:** Phase 3 - Implementation Planning  
**Parent Hypothesis:** h-verifierteacher-v1  
**Prerequisite:** h-m1 (VALIDATED)

---

## Executive Summary

This PRD specifies the implementation requirements for validating the **Compute-Matched Control Hypothesis**: that iterative feedback outperforms single-shot self-consistency sampling by ≥10pp in proof discharge rate when given equal compute budgets (tokens + verifier time).

The system will implement three baseline approaches:
1. **IterativeFeedback** - Reuses h-m1 FullStructured feedback refinement
2. **SelfConsistency-ComputeMatched** - N independent samples with best-of-N selection
3. **Hybrid-SampleThenRefine** - Initial sampling followed by iterative refinement

This is a **critical control experiment**: if self-consistency sampling achieves comparable results with matched compute, it invalidates the claim that feedback content (not just compute budget) drives performance gains.

**Gate Type:** MUST_WORK (If gap <10pp, main hypothesis about "structured feedback enabling synthesis" is weakened)

---

## Problem Statement

### Context

H-M1 (prerequisite) validated the information gradient hypothesis, demonstrating that FullStructured feedback achieves 70.12% discharge rate through iterative refinement. However, this result does not control for compute budget - iterative refinement inherently uses more LLM tokens and verifier time than single-shot synthesis.

**Critical Question:** Is the 70.12% performance due to:
- (A) Structured feedback quality enabling better synthesis ← **Our claim**
- (B) Simply spending more compute budget (tokens + verifier time) ← **Alternative explanation**

### Research Question

Under compute-matched conditions (equal total tokens + verifier time), does iterative feedback with structured verifier feedback outperform self-consistency sampling with N independent attempts by at least 10 percentage points?

### Success Criteria

1. **Primary:** IterativeFeedback discharge rate ≥ SelfConsistency discharge rate + 10pp
2. **Statistical Significance:** Paired t-test p-value < 0.05
3. **Effect Size:** Cohen's d ≥ 0.5 (medium effect)
4. **Compute Matching:** Token and verifier time budgets within 10% between baselines

### Failure Conditions

- Gap between IterativeFeedback and SelfConsistency <10pp
- Not statistically significant (p ≥ 0.05)
- Compute budgets not matched (>10% difference)
- Non-monotonic ordering where SelfConsistency > IterativeFeedback

---

## Functional Requirements

### FR-1: Dataset Management (Reuse from H-M1)

**Priority:** P0 (Critical)

**Description:** Reuse Frama-C verified C programs dataset prepared for h-m1.

**Requirements:**
- FR-1.1: Use same ACSL-by-Example benchmark subset (50 test programs)
- FR-1.2: Validate data consistency with h-m1 results
- FR-1.3: Verify gold standard annotations unchanged
- FR-1.4: Use same train/validation/test split
  - Training/Few-shot: 10 programs
  - Validation: 15 programs  
  - Test: 50 programs

**Input:** H-M1 dataset directory  
**Output:** Validated dataset ready for compute-matched experiments  
**Dependencies:** H-M1 validated dataset

**Acceptance Criteria:**
- All 50 test programs from h-m1 successfully loaded
- Data integrity checks pass
- Gold annotations match h-m1 reference

---

### FR-2: Frama-C Verification Integration (Reuse from H-M1)

**Priority:** P0 (Critical)

**Description:** Reuse Frama-C/WP verification wrapper from h-m1.

**Requirements:**
- FR-2.1: Use same Frama-C configuration as h-m1:
  - Version: Frama-C 32.0 (Germanium)
  - Provers: Alt-Ergo 2.6.2, Z3 4.15.2, CVC5 1.3.3
  - Timeout: 10 seconds per obligation
- FR-2.2: Track verifier execution time for compute budget accounting
- FR-2.3: Parse verification results:
  - Total obligations count
  - Discharged obligations count
  - Failed obligation details (for feedback extraction)
  - Witness/counterexample information
- FR-2.4: Compute discharge rate: (discharged / total) × 100

**Input:** C program + ACSL annotations  
**Output:** Verification result + execution time  
**Dependencies:** H-M1 verifier wrapper module

**Acceptance Criteria:**
- Verifier produces identical results to h-m1 on same inputs
- Execution time accurately measured (±100ms precision)
- All parser functions from h-m1 work correctly

---

### FR-3: LLM Integration for Specification Synthesis (Reuse from H-M1)

**Priority:** P0 (Critical)

**Description:** Reuse LLM client from h-m1 with token tracking enhancement.

**Requirements:**
- FR-3.1: Use same LLM configuration as h-m1:
  - Model: GPT-4 or Claude Opus (match h-m1 choice)
  - Temperature: 0.7 for sampling, 0.2 for refinement
  - Max tokens: 4096 per generation
  - Top-p: 0.95
- FR-3.2: Enhance token tracking:
  - Record prompt tokens per API call
  - Record completion tokens per API call
  - Accumulate total tokens per experiment run
- FR-3.3: Support temperature override for self-consistency sampling
- FR-3.4: Support random seed setting for independent samples

**Input:** C program + feedback (optional)  
**Output:** ACSL annotations + token usage stats  
**Dependencies:** H-M1 LLM client module

**Acceptance Criteria:**
- Token tracking accuracy ±1% (validated against API response)
- Temperature override works for sampling diversity
- Retry logic handles API failures (max 3 retries)

---

### FR-4: Compute Budget Tracking System (NEW - Critical)

**Priority:** P0 (Critical)

**Description:** Implement comprehensive compute budget accounting for fair comparison.

**Requirements:**

**FR-4.1: Budget Definition**
```python
@dataclass
class ComputeBudget:
    total_tokens: int          # Prompt + completion tokens
    verifier_time_seconds: float  # Total Frama-C WP execution time
    llm_api_calls: int         # Number of LLM invocations
    iterations: int            # Refinement iterations or samples
```

**FR-4.2: Budget Tracking Per Experiment**
- Initialize budget tracker at experiment start
- Increment on each LLM API call (add prompt + completion tokens)
- Increment on each verifier invocation (add execution time)
- Store per-iteration/per-sample breakdowns

**FR-4.3: Budget Matching Logic**
- Run Baseline 1 (IterativeFeedback) on validation set (15 programs)
- Calculate average budget: `avg_tokens`, `avg_verifier_time`, `avg_iterations`
- For Baseline 2 (SelfConsistency), set:
  - `N_samples = floor(avg_iterations * 0.95)` (5% margin)
  - Token constraint: `N * single_shot_tokens ≤ avg_tokens * 1.10` (10% margin)
  - Time constraint: `N * single_shot_verifier_time ≤ avg_verifier_time * 1.10`

**FR-4.4: Budget Validation**
- After each test program, verify budgets within 10% tolerance
- Flag violations: Log warning if any budget exceeds 110% of reference
- Aggregate statistics: Mean, std, min, max budget utilization across test set

**Input:** Per-iteration token/time measurements  
**Output:** ComputeBudget object with validation status  
**Dependencies:** FR-2, FR-3

**Acceptance Criteria:**
- Budget tracking overhead <1% of total execution time
- Token counts match LLM API response metadata (±1%)
- Verifier time measured with ≥100ms precision
- Validation flags all budget violations correctly

---

### FR-5: Baseline 1 - Iterative Feedback (Reuse from H-M1)

**Priority:** P0 (Critical)

**Description:** Reuse FullStructured feedback refinement loop from h-m1.

**Requirements:**

**FR-5.1: Configuration**
- Feedback format: FullStructured (Witness + Obligation + Dependency dimensions)
- Max iterations: 10
- Temperature: 0.2 (deterministic refinement)
- Convergence criterion: All obligations discharged OR no spec change for 2 iterations

**FR-5.2: Refinement Loop**
```python
def iterative_feedback_baseline(program, budget_tracker):
    spec = initialize_empty_spec()
    for iteration in range(10):
        budget_tracker.start_iteration()
        
        # Generate/refine specification
        spec = llm_client.generate(program, spec, feedback, temperature=0.2)
        budget_tracker.record_llm_call(tokens)
        
        # Verify
        result = verifier.run_framac_wp(program, spec)
        budget_tracker.record_verifier_call(execution_time)
        
        # Check convergence
        if result.all_discharged:
            break
        
        # Extract FullStructured feedback
        feedback = extract_fullstructured_feedback(result)
        
    return spec, result.discharge_rate, budget_tracker.get_budget()
```

**FR-5.3: Feedback Extraction (from H-M1)**
```python
@dataclass
class FullStructuredFeedback:
    witness_dimension: Dict[str, Any]  # Counterexample values, traces
    obligation_dimension: Dict[str, Any]  # Obligation types, categories
    dependency_dimension: Dict[str, Any]  # Inter-obligation dependencies
```

**Input:** C program  
**Output:** Final specification, discharge rate, compute budget  
**Dependencies:** H-M1 refinement loop module

**Acceptance Criteria:**
- Reproduces h-m1 discharge rate on validation set (within ±2pp)
- All 3 feedback dimensions extracted correctly
- Budget tracking captures all token/time usage

---

### FR-6: Baseline 2 - Self-Consistency Sampling (NEW - Critical)

**Priority:** P0 (Critical)

**Description:** Implement compute-matched self-consistency sampling baseline.

**Requirements:**

**FR-6.1: Sampling Strategy**
- Generate N independent specifications (different random seeds)
- Temperature: 0.7 (diversity over individual quality)
- No cross-contamination: Each sample generated independently
- Prompt: Single-shot with in-context examples (no feedback)

**FR-6.2: Compute Budget Matching**
```python
def compute_matched_sample_count(avg_budget_from_baseline1):
    # From validation set statistics
    avg_iters = avg_budget_from_baseline1.iterations
    avg_tokens = avg_budget_from_baseline1.total_tokens
    avg_time = avg_budget_from_baseline1.verifier_time_seconds
    
    # Estimate single-shot cost
    single_shot_tokens = estimate_single_shot_tokens()  # From validation
    single_shot_time = estimate_single_shot_verifier_time()
    
    # Calculate N within budget
    N_from_tokens = floor((avg_tokens * 0.95) / single_shot_tokens)
    N_from_time = floor((avg_time * 0.95) / single_shot_time)
    
    N = min(N_from_tokens, N_from_time, avg_iters)  # Conservative estimate
    return max(N, 3)  # Minimum 3 samples
```

**FR-6.3: Selection Strategies**

**Strategy A: Best-of-N (Verifier-based)**
```python
def best_of_n_selection(program, N, budget_tracker):
    samples = []
    results = []
    
    for i in range(N):
        # Generate independent sample
        spec = llm_client.generate(program, temperature=0.7, seed=i)
        budget_tracker.record_llm_call(tokens)
        
        # Verify
        result = verifier.run_framac_wp(program, spec)
        budget_tracker.record_verifier_call(execution_time)
        
        samples.append(spec)
        results.append(result)
    
    # Select best by discharge rate
    best_idx = argmax([r.discharge_rate for r in results])
    return samples[best_idx], results[best_idx], budget_tracker.get_budget()
```

**Strategy B: Majority Voting (Obligation-level)**
```python
def majority_voting_selection(program, N, budget_tracker):
    # Generate N samples (same as Strategy A)
    samples, results = generate_n_samples(program, N, budget_tracker)
    
    # Extract obligation-level success/failure from each sample
    obligation_votes = aggregate_obligation_votes(results)
    
    # Select sample with most consensus
    consensus_spec = construct_consensus_spec(samples, obligation_votes)
    
    # Final verification
    final_result = verifier.run_framac_wp(program, consensus_spec)
    budget_tracker.record_verifier_call(execution_time)
    
    return consensus_spec, final_result, budget_tracker.get_budget()
```

**FR-6.4: Implementation**
- Use Strategy A (Best-of-N) as primary method
- Implement Strategy B as optional comparison (exploratory)
- Log all N sample results for post-hoc analysis

**Input:** C program, N (from budget matching)  
**Output:** Selected specification, discharge rate, compute budget  
**Dependencies:** FR-3, FR-4

**Acceptance Criteria:**
- N samples generated independently (verified by random seed variation)
- Total budget within 10% of Baseline 1 average
- Best-of-N selection identifies highest discharge rate sample
- All N samples stored for analysis

---

### FR-7: Baseline 3 - Hybrid Approach (Exploratory)

**Priority:** P1 (High)

**Description:** Combine sampling diversity with iterative refinement.

**Requirements:**

**FR-7.1: Hybrid Strategy**
```python
def hybrid_sample_then_refine(program, budget_tracker, K=3):
    # Phase 1: Generate K initial samples
    initial_samples = []
    initial_results = []
    
    for i in range(K):
        spec = llm_client.generate(program, temperature=0.7, seed=i)
        budget_tracker.record_llm_call(tokens)
        
        result = verifier.run_framac_wp(program, spec)
        budget_tracker.record_verifier_call(execution_time)
        
        initial_samples.append(spec)
        initial_results.append(result)
    
    # Select best initial sample
    best_idx = argmax([r.discharge_rate for r in initial_results])
    current_spec = initial_samples[best_idx]
    
    # Phase 2: Refine with remaining budget
    remaining_budget = compute_remaining_budget(budget_tracker, target_budget)
    max_refinement_iters = estimate_affordable_iterations(remaining_budget)
    
    for iteration in range(max_refinement_iters):
        if budget_tracker.exceeds_target():
            break
        
        result = verifier.run_framac_wp(program, current_spec)
        budget_tracker.record_verifier_call(execution_time)
        
        if result.all_discharged:
            break
        
        feedback = extract_fullstructured_feedback(result)
        current_spec = llm_client.generate(program, current_spec, feedback, temperature=0.2)
        budget_tracker.record_llm_call(tokens)
    
    return current_spec, result.discharge_rate, budget_tracker.get_budget()
```

**FR-7.2: Configuration**
- Initial samples: K = 3 (fixed)
- Refinement: Use FullStructured feedback from h-m1
- Budget allocation: 30% sampling, 70% refinement (approximate)

**Input:** C program, target compute budget  
**Output:** Final specification, discharge rate, compute budget  
**Dependencies:** FR-3, FR-4, FR-5

**Acceptance Criteria:**
- Both phases execute within combined budget target (±10%)
- Refinement phase starts with best initial sample
- All samples and refinement iterations logged

---

### FR-8: Experiment Execution Pipeline (NEW - Critical)

**Priority:** P0 (Critical)

**Description:** Execute controlled comparison across all baselines.

**Requirements:**

**FR-8.1: Two-Stage Execution**

**Stage 1: Validation Set Budget Calibration**
```python
def calibrate_budgets():
    # Run Baseline 1 on validation set (15 programs)
    validation_budgets = []
    
    for program in validation_set:
        spec, discharge_rate, budget = iterative_feedback_baseline(program)
        validation_budgets.append(budget)
    
    # Calculate statistics
    avg_budget = ComputeBudget(
        total_tokens=mean([b.total_tokens for b in validation_budgets]),
        verifier_time_seconds=mean([b.verifier_time_seconds for b in validation_budgets]),
        iterations=mean([b.iterations for b in validation_budgets])
    )
    
    # Determine N for Baseline 2
    N = compute_matched_sample_count(avg_budget)
    
    return avg_budget, N
```

**Stage 2: Test Set Evaluation**
```python
def run_test_set_evaluation(test_set, avg_budget, N):
    results = []
    
    for program in test_set:  # 50 programs
        budget_tracker = ComputeBudgetTracker(target=avg_budget)
        
        # Baseline 1: Iterative Feedback
        spec_b1, rate_b1, budget_b1 = iterative_feedback_baseline(program, budget_tracker.fork())
        
        # Baseline 2: Self-Consistency (Compute-Matched)
        spec_b2, rate_b2, budget_b2 = best_of_n_selection(program, N, budget_tracker.fork())
        
        # Baseline 3: Hybrid (Exploratory)
        spec_b3, rate_b3, budget_b3 = hybrid_sample_then_refine(program, budget_tracker.fork())
        
        # Record results
        results.append({
            'program_id': program.id,
            'baseline1': {'spec': spec_b1, 'discharge_rate': rate_b1, 'budget': budget_b1},
            'baseline2': {'spec': spec_b2, 'discharge_rate': rate_b2, 'budget': budget_b2},
            'baseline3': {'spec': spec_b3, 'discharge_rate': rate_b3, 'budget': budget_b3}
        })
        
        # Checkpoint every 10 programs
        if len(results) % 10 == 0:
            save_checkpoint(results)
    
    return results
```

**FR-8.2: Control Variables**
- Same LLM model across all baselines (match h-m1)
- Same verifier configuration (Frama-C 32.0, same timeouts)
- Same random seed initialization strategy
- Same in-context examples (from training set)

**FR-8.3: Result Storage**
```python
@dataclass
class ExperimentResult:
    program_id: str
    baseline_name: str  # 'IterativeFeedback', 'SelfConsistency', 'Hybrid'
    discharge_rate: float
    final_spec: str
    compute_budget: ComputeBudget
    iterations_or_samples: int
    budget_violation: bool  # True if exceeds 110% of target
```

**Input:** Validation set (15), test set (50), baseline implementations  
**Output:** Results database (50 programs × 3 baselines = 150 trials)  
**Dependencies:** FR-5, FR-6, FR-7

**Acceptance Criteria:**
- All 50 programs evaluated successfully
- No baseline failures (handle errors gracefully)
- Budget tracking complete for all trials
- Checkpoint/resume works correctly

---

### FR-9: Statistical Analysis and Validation (NEW - Critical)

**Priority:** P0 (Critical)

**Description:** Test compute-matched control hypothesis with rigorous statistics.

**Requirements:**

**FR-9.1: Primary Comparison Test**
```python
def primary_hypothesis_test(results):
    # Extract paired discharge rates
    baseline1_rates = [r['baseline1']['discharge_rate'] for r in results]
    baseline2_rates = [r['baseline2']['discharge_rate'] for r in results]
    
    # Paired t-test
    t_stat, p_value = paired_ttest(baseline1_rates, baseline2_rates)
    
    # Mean difference
    mean_diff = mean(baseline1_rates) - mean(baseline2_rates)
    
    # Effect size (Cohen's d for paired samples)
    std_diff = std([b1 - b2 for b1, b2 in zip(baseline1_rates, baseline2_rates)])
    cohens_d = mean_diff / std_diff
    
    return {
        'mean_baseline1': mean(baseline1_rates),
        'mean_baseline2': mean(baseline2_rates),
        'mean_difference': mean_diff,
        't_statistic': t_stat,
        'p_value': p_value,
        'cohens_d': cohens_d,
        'gate_satisfied': mean_diff >= 10.0 and p_value < 0.05 and cohens_d >= 0.5
    }
```

**FR-9.2: Compute Budget Fairness Validation**
```python
def validate_compute_fairness(results):
    b1_budgets = [r['baseline1']['budget'] for r in results]
    b2_budgets = [r['baseline2']['budget'] for r in results]
    
    # Token fairness
    b1_tokens = mean([b.total_tokens for b in b1_budgets])
    b2_tokens = mean([b.total_tokens for b in b2_budgets])
    token_ratio = b2_tokens / b1_tokens
    
    # Time fairness
    b1_time = mean([b.verifier_time_seconds for b in b1_budgets])
    b2_time = mean([b.verifier_time_seconds for b in b2_budgets])
    time_ratio = b2_time / b1_time
    
    # Check within 10% margin
    token_fair = 0.90 <= token_ratio <= 1.10
    time_fair = 0.90 <= time_ratio <= 1.10
    
    return {
        'baseline1_avg_tokens': b1_tokens,
        'baseline2_avg_tokens': b2_tokens,
        'token_ratio': token_ratio,
        'token_budget_fair': token_fair,
        'baseline1_avg_time': b1_time,
        'baseline2_avg_time': b2_time,
        'time_ratio': time_ratio,
        'time_budget_fair': time_fair,
        'overall_fair': token_fair and time_fair
    }
```

**FR-9.3: Exploratory Analysis**
- Compare Baseline 3 (Hybrid) to Baseline 1 and 2
- Identify if hybrid approach outperforms both (>5pp)
- Document hybrid results for future work

**FR-9.4: Per-Program Analysis**
```python
def per_program_analysis(results):
    # For each program, compute gap
    gaps = []
    for r in results:
        gap = r['baseline1']['discharge_rate'] - r['baseline2']['discharge_rate']
        gaps.append({
            'program_id': r['program_id'],
            'gap': gap,
            'baseline1_better': gap > 0,
            'gap_magnitude': abs(gap)
        })
    
    # Aggregate statistics
    return {
        'programs_where_b1_wins': sum(1 for g in gaps if g['baseline1_better']),
        'programs_where_b2_wins': sum(1 for g in gaps if not g['baseline1_better']),
        'mean_gap_when_b1_wins': mean([g['gap'] for g in gaps if g['baseline1_better']]),
        'mean_gap_when_b2_wins': mean([abs(g['gap']) for g in gaps if not g['baseline1_better']])
    }
```

**FR-9.5: Gate Decision Logic**
```python
def make_gate_decision(primary_test, fairness_check, per_program_stats):
    # All criteria must pass
    criteria = {
        'mean_difference_10pp': primary_test['mean_difference'] >= 10.0,
        'statistical_significance': primary_test['p_value'] < 0.05,
        'medium_effect_size': primary_test['cohens_d'] >= 0.5,
        'compute_budget_fair': fairness_check['overall_fair']
    }
    
    gate_satisfied = all(criteria.values())
    
    return {
        'gate_decision': 'SATISFIED' if gate_satisfied else 'FAILED',
        'criteria': criteria,
        'failure_reasons': [k for k, v in criteria.items() if not v]
    }
```

**Input:** Experiment results from FR-8  
**Output:** Statistical report + gate decision  
**Dependencies:** FR-8

**Acceptance Criteria:**
- Paired t-test correctly computed (validated on synthetic data)
- Effect size calculation matches reference implementation
- Gate decision logic handles all edge cases
- All 4 criteria evaluated independently

---

### FR-10: Visualization Generation (NEW)

**Priority:** P1 (High)

**Description:** Generate publication-quality figures for compute-matched comparison.

**Requirements:**

**FR-10.1: Primary Comparison Plot**
```
Bar plot with error bars:
- X-axis: Baselines (IterativeFeedback, SelfConsistency, Hybrid)
- Y-axis: Mean discharge rate (%) with 95% CI
- Annotations: Show gaps above bars
- Reference line: 10pp threshold
```

**FR-10.2: Per-Program Heatmap**
```
Heatmap:
- Rows: 50 programs (sorted by difficulty)
- Columns: 3 baselines
- Color: Discharge rate (0-100%)
- Annotations: Highlight where SelfConsistency ≥ IterativeFeedback (failures)
```

**FR-10.3: Compute Budget Scatter**
```
Scatter plot:
- X-axis: Total tokens used
- Y-axis: Discharge rate (%)
- Points: All 150 trials (50 programs × 3 baselines)
- Color by baseline
- Reference lines: Budget fairness bounds (90%-110%)
```

**FR-10.4: Gap Distribution**
```
Histogram:
- X-axis: Gap (IterativeFeedback - SelfConsistency) in pp
- Y-axis: Frequency (number of programs)
- Overlay: Mean gap, 10pp threshold line
- Show: % programs where gap ≥10pp
```

**FR-10.5: Hybrid Analysis (if exploratory)**
```
Line plot:
- X-axis: Baseline (IterativeFeedback, SelfConsistency, Hybrid)
- Y-axis: Discharge rate (%)
- Lines: Per-program trajectories
- Highlight: Programs where Hybrid is best
```

**Input:** Experiment results, statistical analysis  
**Output:** 5 publication-ready figures (PNG + PDF)  
**Dependencies:** FR-8, FR-9

**Acceptance Criteria:**
- All figures render correctly with publication quality (300 DPI)
- Error bars correctly represent 95% confidence intervals
- Color schemes accessible (colorblind-friendly)
- Annotations and labels readable at journal column width

---

### FR-11: Results Documentation (NEW)

**Priority:** P0 (Critical)

**Description:** Generate comprehensive validation report for h-c1.

**Requirements:**

**FR-11.1: Document Structure**
```markdown
# H-C1 Validation Report

## Executive Summary
- Hypothesis statement
- Gate decision (SATISFIED/FAILED)
- Key findings (1-2 sentences)

## Experimental Setup
- Dataset: 50 test programs from h-m1
- Baselines: IterativeFeedback, SelfConsistency, Hybrid
- LLM model: [GPT-4/Claude Opus]
- Verifier: Frama-C 32.0

## Budget Calibration (Validation Set)
- Average iterations: X
- Average tokens: Y
- Average verifier time: Z seconds
- Computed N for SelfConsistency: N

## Results Summary (Test Set)
- Baseline 1 (IterativeFeedback): X.XX% ± Y.YY%
- Baseline 2 (SelfConsistency): X.XX% ± Y.YY%
- Baseline 3 (Hybrid): X.XX% ± Y.YY%
- Gap (B1 - B2): ±X.XX pp
- Statistical significance: p = X.XXX
- Effect size: Cohen's d = X.XX

## Compute Budget Fairness
- Token ratio (B2/B1): X.XX (target: 0.90-1.10)
- Time ratio (B2/B1): X.XX (target: 0.90-1.10)
- Fairness verdict: PASS/FAIL

## Gate Decision
- Criterion 1 (≥10pp gap): PASS/FAIL
- Criterion 2 (p<0.05): PASS/FAIL
- Criterion 3 (d≥0.5): PASS/FAIL
- Criterion 4 (budget fair): PASS/FAIL
- **OVERALL GATE: SATISFIED/FAILED**

## Per-Program Analysis
- Programs where IterativeFeedback wins: X/50
- Programs where SelfConsistency wins: Y/50
- Mean gap when IterativeFeedback wins: ±X.XX pp

## Failure Analysis (if gate failed)
- Error patterns in failed programs
- Hypothesis for why SelfConsistency performs well
- Implications for main research claim

## Figures
[Include all 5 figures from FR-10]

## Conclusion
- Interpretation of results
- Implications for h-verifierteacher-v1 main hypothesis
- Next steps

## Appendix
- Full results table (50 programs × 3 baselines)
- Budget tracking details
- Configuration parameters
```

**FR-11.2: Metadata Update**
```yaml
# verification_state.yaml update
h-c1:
  status: VALIDATED
  gate:
    type: MUST_WORK
    satisfied: true/false
    decision_date: 2026-07-XX
  validation:
    discharge_rates:
      iterative_feedback: X.XX
      self_consistency: X.XX
      hybrid: X.XX
    gap_pp: X.XX
    statistical_test:
      p_value: X.XXX
      cohens_d: X.XX
    compute_fairness:
      token_ratio: X.XX
      time_ratio: X.XX
```

**FR-11.3: Output Files**
- `04_validation.md` - Comprehensive report
- `validation_results.json` - Machine-readable results
- `verification_state.yaml` - Updated gate status
- `figures/` - All visualization outputs

**Input:** All experimental data, statistical analysis, figures  
**Output:** Complete validation documentation package  
**Dependencies:** FR-8, FR-9, FR-10

**Acceptance Criteria:**
- 04_validation.md follows template structure exactly
- Gate decision clearly justified with evidence
- All figures embedded correctly
- verification_state.yaml valid YAML syntax
- JSON results parseable by downstream tools

---

## Non-Functional Requirements

### NFR-1: Reproducibility

**NFR-1.1: Deterministic Execution**
- Fix random seeds:
  - LLM sampling: seed = 42 + program_index × 1000 + sample_index
  - Numpy/Python: seed = 42
- Version lock all dependencies:
  - Frama-C version, prover versions
  - LLM API version (model snapshot if available)
  - Python packages (requirements.txt)

**NFR-1.2: Configuration Management**
```yaml
# config/h-c1-experiment.yaml
experiment:
  hypothesis_id: h-c1
  dataset: h-m1-benchmark
  validation_set_size: 15
  test_set_size: 50

llm:
  model: gpt-4-0613  # or claude-opus-20240229
  temperature_refinement: 0.2
  temperature_sampling: 0.7
  max_tokens: 4096
  top_p: 0.95

verifier:
  tool: frama-c
  version: 32.0
  timeout_per_obligation: 10
  provers: [alt-ergo-2.6.2, z3-4.15.2, cvc5-1.3.3]

baselines:
  iterative_feedback:
    max_iterations: 10
    convergence_check: 2_iterations_no_change
  self_consistency:
    compute_matched: true
    selection_strategy: best_of_n
    min_samples: 3
  hybrid:
    initial_samples: 3
    budget_allocation: [0.3, 0.7]  # sampling, refinement

compute_budget:
  fairness_tolerance: 0.10  # ±10%
  tracking_precision: 0.001  # seconds

gate:
  min_gap_pp: 10.0
  alpha: 0.05
  min_effect_size: 0.5
```

**NFR-1.3: Logging**
- All LLM API calls: prompt, response, tokens, timestamp
- All verifier invocations: input, output, execution time
- Budget tracking: per-iteration breakdown
- Checkpoint files: every 10 programs

### NFR-2: Robustness

**NFR-2.1: Error Handling**
```python
class RobustExperimentRunner:
    def run_with_retry(self, program, baseline):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return baseline.run(program)
            except LLMAPIError as e:
                if attempt < max_retries - 1:
                    sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    log_error(f"Failed after {max_retries} attempts: {e}")
                    return None
            except VerifierCrashError as e:
                log_error(f"Verifier crashed on {program.id}: {e}")
                return None
```

**NFR-2.2: Checkpoint/Resume**
- Save results after every 10 programs
- Resume detection: Load existing checkpoint, skip completed programs
- Crash recovery: Verify checkpoint integrity before resume

**NFR-2.3: Timeout Protection**
- Per-program timeout: 30 minutes (generous for 10 iterations)
- Global experiment timeout: 24 hours
- Graceful shutdown: Save partial results on timeout

### NFR-3: Performance

**NFR-3.1: Target Runtime**
- Validation set (15 programs × 1 baseline): 1-2 hours
- Test set (50 programs × 3 baselines): 6-12 hours
- Total with analysis: <16 hours

**NFR-3.2: Parallelization**
- Parallelize across programs (independent trials)
- Do NOT parallelize across baselines (budget matching requires sequential)
- Use multiprocessing pool: 4-8 workers (based on API rate limits)

**NFR-3.3: Resource Optimization**
- Cache LLM responses for identical (program, prompt, seed) tuples
- Cache verifier results for identical (code, spec) pairs
- Disk I/O: Stream logs, don't accumulate in memory

### NFR-4: Maintainability

**NFR-4.1: Code Structure**
```
h-c1/code/
├── src/
│   ├── baselines/
│   │   ├── iterative_feedback.py    # Reuse from h-m1
│   │   ├── self_consistency.py      # NEW
│   │   └── hybrid.py                # NEW
│   ├── core/
│   │   ├── compute_budget.py        # NEW - budget tracking
│   │   ├── experiment_runner.py     # NEW - orchestration
│   │   └── checkpoint_manager.py    # NEW
│   ├── analysis/
│   │   ├── statistical_tests.py     # NEW
│   │   ├── visualizer.py            # Extend from h-m1
│   │   └── report_generator.py      # NEW
│   └── utils/
│       ├── llm_client.py            # Reuse from h-m1
│       ├── verifier_wrapper.py      # Reuse from h-m1
│       └── dataset_loader.py        # Reuse from h-m1
├── config/
│   └── h-c1-experiment.yaml
├── main.py                          # Entry point
└── requirements.txt
```

**NFR-4.2: Documentation**
- Docstrings for all public functions (Google style)
- Type hints for all function signatures
- Inline comments for complex logic (budget matching, consensus voting)
- README with setup instructions

**NFR-4.3: Testing**
- Unit tests for compute budget tracking (±1% accuracy)
- Integration test: Synthetic program with known discharge rates
- Smoke test: Run 3 programs × 3 baselines in <10 minutes

---

## Dependencies

### Prerequisite Hypotheses

| Hypothesis | Status | Reuse |
|------------|--------|-------|
| H-M1 (Information Gradient) | VALIDATED | Dataset, verifier wrapper, LLM client, FullStructured feedback, refinement loop |

### External Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Frama-C | 32.0 (Germanium) | Verification engine |
| Alt-Ergo | 2.6.2 | SMT solver |
| Z3 | 4.15.2 | SMT solver |
| CVC5 | 1.3.3 | SMT solver |
| Python | 3.10+ | Implementation language |

### Python Packages

```txt
# requirements.txt
openai==1.3.0  # or anthropic==0.8.0
numpy==1.24.0
scipy==1.11.0
pandas==2.0.0
matplotlib==3.7.0
seaborn==0.12.0
pyyaml==6.0
pydantic==2.0.0
pytest==7.4.0
```

### APIs

| Provider | Model | Rate Limits | Cost Estimate |
|----------|-------|-------------|---------------|
| OpenAI | GPT-4 (gpt-4-0613) | 10K tokens/min | $200-300 for full experiment |
| Anthropic (fallback) | Claude Opus | 5K tokens/min | $250-350 for full experiment |

### Datasets

| Dataset | Source | Scale | Status |
|---------|--------|-------|--------|
| ACSL-by-Example | H-M1 preprocessed | 50 test programs | Available from h-m1 |

---

## Success Criteria

### Phase 4 PoC Success (Interim Gate)

**Criterion 1: Code Runs Without Critical Errors**
- All 3 baselines execute on validation set (15 programs)
- Budget tracking captures all token/time usage
- No crashes or unhandled exceptions

**Criterion 2: Budget Matching Works**
- SelfConsistency budget within 10% of IterativeFeedback on validation set
- N samples correctly computed from validation statistics
- Token and time constraints both satisfied

**Criterion 3: Initial Signal Detected**
- IterativeFeedback discharge rate > SelfConsistency discharge rate on validation set
- Gap suggests potential for ≥10pp on test set

### Final Gate Success (Hypothesis Validation)

**All 4 criteria must pass:**

1. **Mean Gap ≥10pp:** `mean(IterativeFeedback) - mean(SelfConsistency) ≥ 10.0`
2. **Statistical Significance:** `p_value < 0.05` (paired t-test)
3. **Medium Effect Size:** `Cohen's d ≥ 0.5`
4. **Compute Fairness:** Both token and time ratios within 0.90-1.10

**Gate SATISFIED:** All 4 criteria met → Write `gate.satisfied = true`  
**Gate FAILED:** Any criterion fails → Write `gate.satisfied = false`

### Failure Mode Classification

| Failure Mode | Diagnostic | Implication |
|--------------|-----------|-------------|
| Gap <10pp but gap >0pp | Weak effect | Feedback helps but not dramatically |
| Gap ≈0pp | No effect | Self-consistency equivalent to feedback |
| Gap <0pp | Negative effect | Self-consistency better than feedback (!!) |
| Budget violation | Unfair comparison | Experiment invalid, retry with adjusted N |
| p≥0.05 | Underpowered | Increase test set size or reduce variance |

---

## Out of Scope

**Explicitly NOT included in this experiment:**

- Multi-model comparison (GPT-4 vs Claude) - use single model from h-m1
- Temperature sweep for self-consistency (use 0.7 fixed)
- Adaptive N per program (use global N from validation set)
- Human-in-the-loop baseline (no human annotations)
- Fine-tuning or retrieval augmentation (inference-only)
- Other sampling strategies (nucleus sampling, top-k) - use temperature only
- Verifier timeout tuning (use 10s from h-m1)
- Multi-turn voting refinement (single-round voting only)

---

## Risk Analysis & Mitigation

### Risk 1: Compute Matching Imperfect

**Description:** Token/time variance across programs may make "average" budget matching insufficient.

**Likelihood:** High  
**Impact:** Critical (invalidates comparison)

**Mitigation:**
- Use per-program adaptive N based on h-m1 iteration history for that program
- Report results with multiple budget levels (90%, 100%, 110% of target)
- Sensitivity analysis: How do results change if N varies ±1?

### Risk 2: Self-Consistency Exceeds Budget

**Description:** N independent samples use more total tokens than iterative refinement.

**Likelihood:** Medium  
**Impact:** Critical (unfair comparison)

**Mitigation:**
- Pre-compute single-shot token estimates on validation set
- Conservative N selection (5% margin)
- Real-time budget monitoring: abort if exceeding 110% threshold
- Include "budget-capped" variant that stops at exact token limit

### Risk 3: Sampling Temperature Affects Quality

**Description:** Temperature=0.7 for diversity reduces individual sample quality, unfairly handicaps SelfConsistency.

**Likelihood:** Medium  
**Impact:** High (biased comparison)

**Mitigation:**
- Validate temperature choice on validation set
- Test multiple temperatures {0.2, 0.5, 0.7, 1.0}, select optimal
- Report temperature sensitivity analysis
- Alternative: Use temperature=0.2 for all samples (removes diversity bias)

### Risk 4: Best-of-N vs Voting Strategy

**Description:** Selection strategy choice may significantly impact results.

**Likelihood:** Low  
**Impact:** Medium (unclear which is "fair")

**Mitigation:**
- Implement both Best-of-N and Voting strategies
- Report results for both
- Use Best-of-N as primary (simpler, more standard in literature)
- Document Voting as exploratory

### Risk 5: LLM Model Stability (from Liu & Meng 2024)

**Description:** Only certain models (o3-mini, Claude Opus 4.6) are stable in iterative refinement (EIR <0.5%).

**Likelihood:** Low (h-m1 already validated stable model)  
**Impact:** Critical (iterative refinement degrades)

**Mitigation:**
- Reuse same model from h-m1 (already proven stable)
- Measure Error Introduction Rate (EIR) per Liu & Meng framework
- If EIR >0.5%, abort and report instability

### Risk 6: Insufficient Test Set Size

**Description:** n=50 may lack power to detect <10pp differences if variance is high.

**Likelihood:** Low (power analysis shows 99% power for 10pp)  
**Impact:** Medium (inconclusive result)

**Mitigation:**
- Power analysis validated 50 programs sufficient
- If p≥0.05 but gap ≥10pp, consider expanding to full 75 programs
- Report post-hoc power calculation

---

## Timeline & Resource Estimates

### Phase 3 (Implementation Planning): 2 weeks

- Week 1: PRD (this document), Architecture, PRP design
- Week 2: Task breakdown, Archon task creation

### Phase 4 (Implementation & Validation): 6 weeks

**Week 1: Baseline 2 (SelfConsistency) Implementation**
- Implement N-sample generation loop
- Implement Best-of-N selection
- Implement Voting selection (optional)
- Unit tests for sampling diversity

**Week 2: Compute Budget Tracking**
- Implement ComputeBudget dataclass and tracker
- Implement budget matching logic
- Implement validation set calibration
- Integration tests with h-m1 modules

**Week 3: Baseline 3 (Hybrid) + Experiment Runner**
- Implement Hybrid strategy (sample-then-refine)
- Implement experiment orchestration pipeline
- Implement checkpoint/resume system
- Smoke test on 5 programs

**Week 4: Validation Set Calibration**
- Run Baseline 1 on validation set (15 programs)
- Compute average budget statistics
- Determine N for SelfConsistency
- Validate budget fairness on validation set

**Week 5-6: Test Set Evaluation**
- Run all 3 baselines on test set (50 programs)
- Monitor budget compliance in real-time
- Checkpoint every 10 programs
- Total runtime estimate: 8-12 hours

### Week 7: Analysis & Documentation

- Statistical analysis (FR-9)
- Visualization generation (FR-10)
- Report writing (FR-11)
- Gate decision

**Total Time:** 9 weeks (Phase 3 + Phase 4)

### Compute Resources

**LLM API Costs:**
- Validation set calibration (15 programs × avg 7 iters × 8K tokens): ~$17
- Test set - Baseline 1 (50 programs × 7 iters × 8K tokens): ~$56
- Test set - Baseline 2 (50 programs × 7 samples × 8K tokens): ~$56
- Test set - Baseline 3 (50 programs × (3 samples + 4 iters) × 8K tokens): ~$56
- **Total:** ~$185-250 (depending on model)

**Compute Time:**
- Validation set: 1-2 hours
- Test set: 8-12 hours (parallelized across 4-8 workers)
- Analysis: 30 minutes
- **Total wall-clock:** <16 hours

**Storage:**
- Experiment results: ~100 MB (all trials + checkpoints)
- Logs: ~500 MB (verbose LLM/verifier logs)
- Figures: ~10 MB
- **Total:** ~600 MB

---

## User Stories

### Researcher Stories

**Story 1: Fair Compute Comparison**
> As a researcher, I want to compare iterative feedback vs self-consistency sampling under equal compute budgets, so that I can isolate the effect of feedback quality from compute quantity.

**Acceptance Criteria:**
- Budget tracking captures all token and verifier time usage
- SelfConsistency baseline constrained to match IterativeFeedback budget (±10%)
- Budget fairness validation included in report

---

**Story 2: Validate Main Hypothesis Claim**
> As a researcher, I want to test if feedback content (not just compute) drives performance, so that I can defend my main hypothesis against alternative explanations.

**Acceptance Criteria:**
- If IterativeFeedback > SelfConsistency + 10pp: claim validated
- If gap <10pp: claim weakened, must acknowledge compute budget as confound
- Statistical significance tested (p<0.05)

---

**Story 3: Discover Hybrid Potential**
> As a researcher, I want to explore if combining sampling diversity with feedback refinement yields better results, so that I can identify optimal strategies for future work.

**Acceptance Criteria:**
- Hybrid baseline implemented and evaluated
- Results compared to both IterativeFeedback and SelfConsistency
- If Hybrid best, documented for future research directions

---

**Story 4: Reproducible Results**
> As a researcher, I want all experiments to be fully reproducible, so that external reviewers can validate my claims.

**Acceptance Criteria:**
- All random seeds fixed and logged
- Configuration file captures all parameters
- Checkpoint files enable crash recovery
- Results match when re-run (±0.5pp due to API variance)

---

**Story 5: Actionable Failure Analysis**
> As a researcher, if the gate fails, I want detailed diagnostics explaining why, so that I can revise the hypothesis or experimental design.

**Acceptance Criteria:**
- Per-program breakdown shows where IterativeFeedback fails
- Budget violation logs identify unfair trials
- Statistical report explains which criterion failed
- Contingency plan documented in validation report

---

## Appendix A: Compute Budget Example

**Example Program:** `array_max_001` (from h-m1)

### Baseline 1: Iterative Feedback (from h-m1)

```
Iteration 0 (Initial):
  LLM: 2500 prompt + 800 completion = 3300 tokens
  Verifier: 15 seconds
  Discharge: 40%

Iteration 1 (Feedback):
  LLM: 3200 prompt + 900 completion = 4100 tokens
  Verifier: 18 seconds
  Discharge: 65%

Iteration 2 (Feedback):
  LLM: 3500 prompt + 950 completion = 4450 tokens
  Verifier: 20 seconds
  Discharge: 80%

Iteration 3: Converged (no change)

Total Budget:
  Tokens: 3300 + 4100 + 4450 = 11,850 tokens
  Verifier Time: 15 + 18 + 20 = 53 seconds
  Iterations: 3
```

### Baseline 2: Self-Consistency (Compute-Matched)

**Budget Allocation:**
- Target tokens: 11,850 (from Baseline 1)
- Target time: 53 seconds
- Single-shot estimate: 3300 tokens, 15 seconds (from validation)
- N = min(floor(11,850 / 3,300), floor(53 / 15)) = min(3, 3) = 3 samples

**Execution:**
```
Sample 1 (seed=42):
  LLM: 2500 prompt + 800 completion = 3300 tokens
  Verifier: 15 seconds
  Discharge: 45%

Sample 2 (seed=1042):
  LLM: 2500 prompt + 850 completion = 3350 tokens
  Verifier: 14 seconds
  Discharge: 55%

Sample 3 (seed=2042):
  LLM: 2500 prompt + 780 completion = 3280 tokens
  Verifier: 16 seconds
  Discharge: 50%

Best-of-N Selection: Sample 2 (55% discharge)

Total Budget:
  Tokens: 3300 + 3350 + 3280 = 9,930 tokens (84% of target, FAIR)
  Verifier Time: 15 + 14 + 16 = 45 seconds (85% of target, FAIR)
  Samples: 3
```

**Result:**
- IterativeFeedback: 80% discharge
- SelfConsistency: 55% discharge
- Gap: 25pp (exceeds 10pp threshold ✓)
- Budget Fair: Tokens 84%, Time 85% (within 90%-110% ✓)

---

## Appendix B: Statistical Power Analysis

**Hypothesis Test:** Paired t-test (IterativeFeedback vs. SelfConsistency)

**Parameters:**
- Sample size: n = 50 programs
- Significance level: α = 0.05 (two-tailed)
- Target power: 1 - β = 0.80
- Expected difference: Δ = 10pp
- Estimated std of differences: σ_d = 15pp (conservative)

**Effect Size:**
```
Cohen's d = Δ / σ_d = 10 / 15 = 0.67 (medium-large)
```

**Power Calculation:**
```
t_critical = t(α/2, df=49) ≈ 2.01
ncp (non-centrality parameter) = (Δ / σ_d) × sqrt(n) = 0.67 × sqrt(50) ≈ 4.74
Power ≈ 0.995 (>99%)
```

**Interpretation:**
- With n=50, we have >99% power to detect a 10pp difference
- Minimum detectable effect (80% power): ~4.3pp
- Well-powered to test hypothesis

---

## Appendix C: Reference Prior Work

### Self-Consistency in LLMs

**Wang et al., "Self-Consistency Improves Chain of Thought Reasoning in Language Models" (ICLR 2023)**
- Sample diverse reasoning paths, select by majority vote
- Improvements: 3-17pp over greedy decoding on reasoning tasks
- Relevance: Establishes self-consistency as strong baseline

### Iterative Refinement with Feedback

**Chakraborty et al., "On the Role of Feedback in Test-Time Scaling of Agentic AI Workflows" (2024)**
- IAD with high-fidelity feedback: up to 10% absolute over best-of-N
- Domains: Sketch2Code, Text2SQL, Intercode, WebShop
- Relevance: Our hypothesis predicts similar 10pp gap for formal verification

### Compute-Matched Controls

**Snell et al., "Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters" (2024)**
- Compare different compute allocation strategies at fixed budget
- Finding: Adaptive strategies outperform fixed strategies
- Relevance: Motivates our compute-matched experimental design

---

## Appendix D: Contingency Plan (If Gate Fails)

### Scenario 1: Gap <10pp but gap >0pp (Weak Effect)

**Diagnostic:**
- IterativeFeedback helps but not dramatically
- Effect size d < 0.5 (small-to-medium)

**Actions:**
1. Analyze per-program results: Which programs benefit from feedback?
2. Hypothesis: Complex programs benefit more (test with stratification)
3. Update claim: "Feedback helps on hard problems" (not universally)
4. Document as qualified success in Phase 6

### Scenario 2: Gap ≈0pp (No Effect)

**Diagnostic:**
- Self-consistency performs equivalently to iterative feedback
- Compute budget, not feedback quality, drives gains

**Actions:**
1. Deep error analysis: Why doesn't feedback help?
   - Are LLM responses ignoring feedback?
   - Is feedback too noisy to be useful?
2. Measure Error Introduction Rate (EIR) per Liu & Meng 2024
3. Pivot to Hybrid approach (if outperforms both)
4. Revise main hypothesis: "Sampling diversity + feedback" (not feedback alone)
5. Publish negative result: "Compute budget confound in iterative refinement"

### Scenario 3: Gap <0pp (SelfConsistency Better!)

**Diagnostic:**
- Iterative refinement actively harmful (error accumulation)
- EIR > ECR per Liu & Meng stability analysis

**Actions:**
1. **CRITICAL FINDING:** Feedback loop degrades performance
2. Measure EIR: If >0.5%, model is unstable for iterative refinement
3. Document failure mode: "Iterative refinement unstable for formal verification"
4. Recommend: Use self-consistency sampling instead
5. Major hypothesis revision required

### Scenario 4: Budget Violation (Unfair Comparison)

**Diagnostic:**
- SelfConsistency uses >110% of IterativeFeedback budget
- Comparison invalid

**Actions:**
1. Re-run SelfConsistency with reduced N (ensure budget fairness)
2. Use per-program adaptive N (not global average N)
3. Report results with multiple budget levels (80%, 100%, 120%)
4. Plot discharge rate vs. compute budget curve

### Scenario 5: Not Statistically Significant (p≥0.05)

**Diagnostic:**
- High variance, underpowered study
- Gap exists but not reliably detected

**Actions:**
1. Post-hoc power analysis: Calculate achieved power
2. Increase test set size: Use all 75 programs (10 train + 15 val + 50 test → 75 test)
3. Reduce variance: Ensemble methods, multiple runs per program
4. Report as inconclusive, not failed

---

**Approval:** Ready for Phase 3 Architecture Design

**Next Steps:**
1. Architecture Agent: Design system components, module structure, Epic-level tasks
2. Logic Agent: Specify API signatures, algorithms (budget matching, selection strategies)
3. Configuration Agent: Define hyperparameters, YAML schemas, dataclasses
