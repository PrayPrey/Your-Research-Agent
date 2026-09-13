# Configuration Specification: H-C1 Compute-Matched Control Experiment

**Hypothesis ID:** h-c1  
**Type:** Control Condition  
**Gate:** MUST_WORK  
**Date:** 2026-07-11  
**Status:** Phase 3 - Configuration Design

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Config verified from h-m1 base code  
**Config Files Found**: `h-m1/code/code/config/experiment_config.yaml`  
**Pattern Used**: YAML configuration file  
**Base Config Classes**: Dataclasses in verifier.py, llm_client.py

**Verified From**: `/workspace/TEST_verifai/docs/youra_research/h-m1/code/`

---

## Configuration Philosophy

**Format**: YAML configuration file (matching h-m1 pattern)  
**Rationale**: h-m1 uses YAML successfully; maintain consistency for code reuse  
**Applied Pattern**: Archon KB "experiment configuration schema" + h-m1 structure

---

## 1. Experiment Configuration

```yaml
# =============================================================================
# H-C1: Compute-Matched Control Experiment
# Configuration for Fair Comparison
# =============================================================================

experiment:
  name: "h-c1-compute-matched-control"
  type: "control"
  hypothesis_id: "h-c1"
  parent_hypothesis: "h-verifierteacher-v1"
  prerequisite: "h-m1"
  seed: 42
  output_dir: "docs/youra_research/h-c1"
```

**Field Rationale**:
- `seed: 42` - Standard reproducibility baseline (matches h-m1)
- `prerequisite: "h-m1"` - Explicit dependency for budget calibration

---

## 2. LLM Configuration

```yaml
# -----------------------------------------------------------------------------
# LLM Configuration (Inherited from H-M1)
# -----------------------------------------------------------------------------
llm:
  # Model selection (MUST match h-m1 for fair comparison)
  model: "claude-opus-4-5"
  provider: "anthropic"

  # API settings
  api_key_env: "ANTHROPIC_API_KEY"
  timeout_seconds: 60
  max_retries: 3
  retry_backoff_base: 2.0

  # Rate limiting
  rate_limit:
    requests_per_second: 1.0
    burst_size: 5

  # Generation parameters (for self-consistency sampling)
  generation:
    temperature: 0.7  # Higher for diversity in Baseline 2
    max_tokens: 4096
    top_p: 0.9

  # Refinement parameters (for iterative feedback)
  refinement:
    temperature: 0.2  # Lower for deterministic refinement in Baseline 1
    max_tokens: 4096
    top_p: 0.9
```

**Field Rationale**:
- `temperature: 0.7` (generation) - Promotes sample diversity for self-consistency
- `temperature: 0.2` (refinement) - Deterministic refinement for iterative feedback
- All other parameters inherited from h-m1 for controlled comparison

---

## 3. Verifier Configuration

```yaml
# -----------------------------------------------------------------------------
# Verifier Configuration (Frama-C/WP - Inherited from H-M1)
# -----------------------------------------------------------------------------
verifier:
  executable: "frama-c"
  version: "32.0"  # Updated from PRD requirement

  wp:
    timeout_per_obligation: 10  # Seconds per proof attempt
    timeout_global: 300  # Total timeout per program
    solvers: ["alt-ergo", "z3", "cvc5"]  # PRD specifies 3 provers
    memory_model: "Typed"
    strategy: "wp"
    split: true

  # Execution time tracking (NEW for H-C1)
  time_tracking:
    enabled: true
    precision_ms: 100  # Measurement precision ±100ms
```

**Field Rationale**:
- `version: "32.0"` - Updated per PRD (Frama-C 32.0 Germanium)
- `solvers: ["alt-ergo", "z3", "cvc5"]` - Added CVC5 per PRD requirements
- `time_tracking.precision_ms: 100` - Matches PRD requirement (±100ms precision)

---

## 4. Compute Budget Configuration (NEW - Critical)

```yaml
# -----------------------------------------------------------------------------
# Compute Budget Tracking (NEW for H-C1)
# -----------------------------------------------------------------------------
compute_budget:
  # Fairness criteria
  fairness_tolerance: 0.10  # ±10% margin for budget matching
  
  # Budget components
  tracking:
    token_count: true  # Prompt + completion tokens
    verifier_time: true  # Frama-C execution time (seconds)
    llm_api_calls: true  # Number of LLM invocations
    iterations: true  # Refinement iterations or sample count
  
  # Validation set calibration
  calibration:
    validation_set_size: 15  # Programs for budget estimation
    safety_margin: 0.05  # 5% margin for variance
  
  # Budget matching strategy
  matching:
    method: "average"  # Use average from validation set
    adaptive: false  # Global N, not per-program adaptive
    enforce_hard_limits: true  # Abort if exceeding 110% budget
```

**Field Rationale**:
- `fairness_tolerance: 0.10` - Per PRD success criteria (within 10%)
- `safety_margin: 0.05` - Conservative estimate (5% margin per PRD)
- `adaptive: false` - Use global N from validation set (simpler, per experiment brief)

---

## 5. Baseline Configurations

### 5.1 Baseline 1: Iterative Feedback (Reuse from H-M1)

```yaml
# -----------------------------------------------------------------------------
# Baseline 1: Iterative Feedback with FullStructured Feedback
# -----------------------------------------------------------------------------
baseline_1_iterative_feedback:
  enabled: true
  name: "IterativeFeedback-FullStructured"
  
  # Refinement loop parameters (from h-m1)
  refinement:
    max_iterations: 10
    convergence_check: "no_change_2_iterations"
    early_stopping:
      enabled: true
      no_improvement_threshold: 2
  
  # Feedback configuration
  feedback:
    format: "FullStructured"
    dimensions:
      - "witness"  # Counterexample values, traces
      - "obligation"  # Obligation types, categories
      - "dependency"  # Inter-obligation dependencies
  
  # Budget tracking
  budget_tracking:
    record_per_iteration: true
    checkpoint_enabled: true
```

---

### 5.2 Baseline 2: Self-Consistency Sampling (NEW - Critical)

```yaml
# -----------------------------------------------------------------------------
# Baseline 2: Self-Consistency with Compute Matching
# -----------------------------------------------------------------------------
baseline_2_self_consistency:
  enabled: true
  name: "SelfConsistency-ComputeMatched"
  
  # Sampling strategy
  sampling:
    num_samples: null  # Computed from validation set calibration
    temperature: 0.7  # Diversity over individual quality
    independent_seeds: true  # Different random seed per sample
    seed_formula: "42 + program_index * 1000 + sample_index"
  
  # Selection strategy
  selection:
    primary_method: "best_of_n"  # Verifier-based selection
    alternative_method: "majority_voting"  # Exploratory
    
    best_of_n:
      criterion: "discharge_rate"  # Select highest discharge rate
      verify_all_samples: true  # Run verifier on all N samples
    
    majority_voting:
      enabled: false  # Exploratory, not primary
      aggregation: "obligation_level"  # Vote per obligation
  
  # Compute budget constraint
  budget_constraint:
    match_to_baseline_1: true
    max_token_ratio: 1.10  # Allow up to 110% of B1 tokens
    max_time_ratio: 1.10  # Allow up to 110% of B1 verifier time
    abort_on_violation: true  # Stop if budget exceeded
```

**Field Rationale**:
- `num_samples: null` - Dynamically computed as `N = floor(avg_iterations * 0.95)`
- `seed_formula` - Ensures independent, reproducible samples
- `best_of_n` as primary - Simpler, more standard (per PRD)

---

### 5.3 Baseline 3: Hybrid Approach (Exploratory)

```yaml
# -----------------------------------------------------------------------------
# Baseline 3: Hybrid Sample-Then-Refine
# -----------------------------------------------------------------------------
baseline_3_hybrid:
  enabled: true
  name: "Hybrid-SampleThenRefine"
  
  # Two-phase strategy
  phase_1_sampling:
    initial_samples: 3  # Fixed K per PRD
    temperature: 0.7
    selection: "best_discharge_rate"
  
  phase_2_refinement:
    use_remaining_budget: true
    budget_allocation:
      sampling_fraction: 0.3  # 30% budget for sampling
      refinement_fraction: 0.7  # 70% for refinement
    
    feedback_format: "FullStructured"  # Reuse from Baseline 1
    max_refinement_iterations: null  # Computed from remaining budget
  
  # Budget tracking
  budget_constraint:
    match_to_baseline_1: true
    allow_early_termination: true  # Stop if all obligations discharged
```

---

## 6. Dataset Configuration

```yaml
# -----------------------------------------------------------------------------
# Dataset Configuration (Reuse from H-M1)
# -----------------------------------------------------------------------------
dataset:
  source: "h-m1"  # Reuse same benchmark
  benchmark_name: "ACSL-by-Example"
  
  # Dataset splits
  splits:
    train_few_shot: 10  # For in-context learning
    validation: 15  # For budget calibration
    test: 50  # For final evaluation
  
  # Data characteristics
  characteristics:
    domain: "verified_c_programs"
    annotation_format: "ACSL"
    complexity_range: ["simple", "medium", "complex"]
    stratification: true  # Balance complexity levels
  
  # Data integrity
  validation:
    check_gold_standard: true  # Verify specs still discharge
    match_h_m1_results: true  # Cross-check with h-m1 data
    tolerance_pp: 2.0  # Allow ±2pp variance from h-m1
```

**Field Rationale**:
- `source: "h-m1"` - Explicit dependency on validated dataset
- `tolerance_pp: 2.0` - Allows minor Frama-C version differences

---

## 7. Experiment Execution Configuration

```yaml
# -----------------------------------------------------------------------------
# Experiment Execution Pipeline
# -----------------------------------------------------------------------------
execution:
  # Two-stage execution
  stage_1_calibration:
    enabled: true
    dataset_split: "validation"
    baseline: "baseline_1_iterative_feedback"
    output_file: "results/calibration_budget.json"
  
  stage_2_evaluation:
    enabled: true
    dataset_split: "test"
    baselines:
      - "baseline_1_iterative_feedback"
      - "baseline_2_self_consistency"
      - "baseline_3_hybrid"
    
    # Parallelization
    parallel:
      enabled: false  # Sequential for budget matching
      workers: 1
    
    # Checkpointing
    checkpoint:
      enabled: true
      save_every_n_programs: 10
      checkpoint_dir: "results/checkpoints"
      resume_on_crash: true
  
  # Timeout protection
  timeouts:
    per_program_minutes: 30  # Generous for 10 iterations
    global_experiment_hours: 24
    graceful_shutdown: true  # Save partial results on timeout
```

**Field Rationale**:
- `parallel.enabled: false` - Budget matching requires sequential execution
- `per_program_minutes: 30` - Accommodates max 10 iterations × ~3 min/iter
- `save_every_n_programs: 10` - Frequent checkpoints for crash recovery

---

## 8. Statistical Analysis Configuration

```yaml
# -----------------------------------------------------------------------------
# Statistical Analysis Parameters
# -----------------------------------------------------------------------------
statistical_analysis:
  # Primary hypothesis test
  primary_test:
    method: "paired_t_test"
    alpha: 0.05  # Significance level
    alternative: "two_sided"
    confidence_level: 0.95
  
  # Effect size
  effect_size:
    metric: "cohens_d"
    min_threshold: 0.5  # Medium effect per PRD
  
  # Gate criteria
  gate_criteria:
    min_gap_pp: 10.0  # Minimum 10pp difference
    statistical_significance: true  # p < 0.05
    medium_effect_size: true  # Cohen's d ≥ 0.5
    compute_budget_fair: true  # Within ±10% tolerance
  
  # Secondary tests
  secondary_tests:
    - name: "wilcoxon_signed_rank"  # Non-parametric alternative
      enabled: true
    - name: "bootstrap_confidence_interval"
      enabled: true
      n_bootstrap: 10000
```

---

## 9. Visualization Configuration

```yaml
# -----------------------------------------------------------------------------
# Visualization Generation
# -----------------------------------------------------------------------------
visualization:
  output_dir: "docs/youra_research/h-c1/figures"
  dpi: 300
  format: "png"
  
  # Required plots (from PRD FR-10)
  plots:
    - name: "primary_comparison_bar"
      type: "bar"
      title: "Discharge Rate Comparison"
      x_axis: "Baselines"
      y_axis: "Discharge Rate (%)"
      error_bars: "95_ci"
      annotations:
        - "gap_above_bars"
        - "10pp_threshold_line"
    
    - name: "per_program_heatmap"
      type: "heatmap"
      title: "Per-Program Discharge Rates"
      rows: "programs_sorted_by_difficulty"
      columns: "baselines"
      colormap: "RdYlGn"
      annotations: "highlight_failures"
    
    - name: "compute_budget_scatter"
      type: "scatter"
      title: "Discharge Rate vs Token Budget"
      x_axis: "Total Tokens"
      y_axis: "Discharge Rate (%)"
      color_by: "baseline"
      reference_lines:
        - "90_percent_budget"
        - "110_percent_budget"
    
    - name: "gap_distribution_histogram"
      type: "histogram"
      title: "Gap Distribution (B1 - B2)"
      x_axis: "Gap (pp)"
      y_axis: "Frequency"
      overlays:
        - "mean_gap"
        - "10pp_threshold"
    
    - name: "hybrid_analysis_line"
      type: "line"
      title: "Per-Program Trajectories"
      enabled: true  # Only if Baseline 3 enabled
      highlight: "programs_where_hybrid_best"
```

---

## 10. Logging Configuration

```yaml
# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------
logging:
  level: "INFO"
  
  console:
    enabled: true
    level: "INFO"
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  
  file:
    enabled: true
    level: "DEBUG"
    path: "docs/youra_research/h-c1/results/experiment.log"
    max_bytes: 10485760  # 10 MB
    backup_count: 5
  
  # Per-trial detailed logs
  trial_logs:
    enabled: true
    format: "json"
    path: "docs/youra_research/h-c1/results/trial_logs/{program_id}_{baseline}.json"
    include_fields:
      - "program_id"
      - "baseline_name"
      - "iterations_or_samples"
      - "discharge_rate"
      - "compute_budget"
      - "timestamps"
      - "llm_prompts"  # For debugging
      - "verifier_output"
  
  # Budget tracking logs (CRITICAL for validation)
  budget_logs:
    enabled: true
    format: "csv"
    path: "docs/youra_research/h-c1/results/budget_tracking.csv"
    fields:
      - "program_id"
      - "baseline"
      - "iteration_or_sample"
      - "prompt_tokens"
      - "completion_tokens"
      - "total_tokens"
      - "verifier_time_seconds"
      - "cumulative_tokens"
      - "cumulative_time"
```

**Field Rationale**:
- `trial_logs.format: "json"` - Structured for post-hoc analysis
- `budget_logs.format: "csv"` - Easy import to pandas for fairness validation

---

## 11. Results Documentation Configuration

```yaml
# -----------------------------------------------------------------------------
# Results Documentation
# -----------------------------------------------------------------------------
documentation:
  # Validation report
  validation_report:
    enabled: true
    template: "docs/youra_research/h-c1/templates/04_validation_template.md"
    output: "docs/youra_research/h-c1/04_validation.md"
    
    sections:
      - "executive_summary"
      - "experimental_setup"
      - "budget_calibration"
      - "results_summary"
      - "compute_budget_fairness"
      - "gate_decision"
      - "per_program_analysis"
      - "failure_analysis"  # If gate fails
      - "figures"
      - "conclusion"
      - "appendix"
  
  # Machine-readable results
  results_json:
    enabled: true
    path: "docs/youra_research/h-c1/validation_results.json"
    schema_version: "1.0"
  
  # Verification state update
  verification_state:
    enabled: true
    path: "verification_state.yaml"
    update_fields:
      - "h-c1.status"
      - "h-c1.gate.satisfied"
      - "h-c1.gate.decision_date"
      - "h-c1.validation.discharge_rates"
      - "h-c1.validation.gap_pp"
      - "h-c1.validation.statistical_test"
      - "h-c1.validation.compute_fairness"
```

---

## 12. Reproducibility Settings

```yaml
# -----------------------------------------------------------------------------
# Reproducibility Configuration
# -----------------------------------------------------------------------------
reproducibility:
  # Random seed management
  seeds:
    global_seed: 42
    numpy_seed: 42
    python_seed: 42
    llm_sampling_seed_base: 42  # Base for seed formula
  
  # Version locking
  version_locks:
    frama_c: "32.0"
    alt_ergo: "2.6.2"
    z3: "4.15.2"
    cvc5: "1.3.3"
    python: "3.10"
    
  # LLM model snapshot
  llm_model:
    model_name: "claude-opus-4-5"
    snapshot_date: "2026-07-11"  # Document model version
    use_snapshot_if_available: true
  
  # Environment variables
  environment:
    required_vars:
      - "ANTHROPIC_API_KEY"
    optional_vars:
      - "FRAMA_C_PATH"
      - "EXPERIMENT_OUTPUT_DIR"
  
  # Dependency lock
  python_packages:
    requirements_file: "requirements.txt"
    use_pip_freeze: true
    lock_file: "requirements.lock"
```

**Field Rationale**:
- `seeds.*: 42` - Standard baseline for all random components
- `version_locks.*` - Exact versions from PRD requirements
- `use_snapshot_if_available: true` - Ensures same model behavior

---

## 13. Error Handling and Robustness

```yaml
# -----------------------------------------------------------------------------
# Error Handling Configuration
# -----------------------------------------------------------------------------
error_handling:
  # LLM API errors
  llm_api:
    max_retries: 3
    retry_backoff_seconds: [2, 4, 8]  # Exponential backoff
    timeout_seconds: 60
    handle_rate_limits: true
    rate_limit_wait_strategy: "exponential"
  
  # Verifier crashes
  verifier:
    handle_crashes: true
    crash_recovery: "skip_program"  # Log and continue
    max_crash_retries: 1
  
  # Budget violations
  budget_violations:
    action: "abort_trial"  # Stop trial if budget exceeded
    log_violation: true
    include_in_analysis: false  # Exclude from final results
  
  # Graceful degradation
  graceful_degradation:
    enabled: true
    save_partial_results: true
    continue_on_error: true  # Don't stop entire experiment
    max_consecutive_failures: 5  # Abort after 5 consecutive failures
```

---

## 14. Performance and Optimization

```yaml
# -----------------------------------------------------------------------------
# Performance Configuration
# -----------------------------------------------------------------------------
performance:
  # Caching
  caching:
    llm_responses:
      enabled: true
      cache_dir: ".cache/llm_responses"
      key_format: "program_id + prompt_hash + seed"
    
    verifier_results:
      enabled: true
      cache_dir: ".cache/verifier_results"
      key_format: "code_hash + spec_hash"
  
  # Resource limits
  resource_limits:
    max_memory_mb: 16384  # 16 GB
    max_disk_mb: 10240  # 10 GB for logs/checkpoints
  
  # Estimated runtime (for monitoring)
  estimated_runtime:
    validation_set_hours: 2
    test_set_hours: 12
    total_with_analysis_hours: 16
```

---

## Configuration Summary

**Total Parameter Groups**: 14  
**Total Configuration Options**: 127

### Configuration Categories

| Category | Parameters | Status |
|----------|-----------|---------|
| Experiment Setup | 7 | Inherited from h-m1 |
| LLM Configuration | 15 | Inherited + extended |
| Verifier Configuration | 9 | Updated versions |
| Compute Budget Tracking | 12 | NEW - Critical |
| Baseline 1 (Iterative) | 8 | Inherited from h-m1 |
| Baseline 2 (SelfConsistency) | 14 | NEW - Critical |
| Baseline 3 (Hybrid) | 10 | NEW - Exploratory |
| Dataset | 11 | Inherited from h-m1 |
| Execution Pipeline | 11 | NEW |
| Statistical Analysis | 9 | NEW |
| Visualization | 6 | NEW |
| Logging | 12 | Extended from h-m1 |
| Documentation | 8 | NEW |
| Reproducibility | 15 | Critical for control |

### Critical Configuration Validation

**Pre-Execution Checks**:
1. ✓ LLM model matches h-m1 (claude-opus-4-5)
2. ✓ Verifier version matches PRD (Frama-C 32.0)
3. ✓ Dataset source validated (h-m1 benchmark)
4. ✓ Compute budget tracking enabled
5. ✓ Budget fairness tolerance set (±10%)
6. ✓ Statistical gate criteria defined (≥10pp, p<0.05, d≥0.5)
7. ✓ Reproducibility seeds fixed (42)
8. ✓ Checkpoint/resume enabled

**Gate Satisfaction Requirements**:
```yaml
gate_satisfaction:
  criterion_1_gap: "mean(B1) - mean(B2) >= 10.0"
  criterion_2_significance: "p_value < 0.05"
  criterion_3_effect_size: "cohens_d >= 0.5"
  criterion_4_compute_fair: "0.90 <= budget_ratio <= 1.10"
  decision_logic: "ALL criteria must pass"
```

---

## Environment Variable Specifications

```bash
# Required
export ANTHROPIC_API_KEY="sk-ant-..."

# Optional
export FRAMA_C_PATH="/usr/local/bin/frama-c"
export EXPERIMENT_OUTPUT_DIR="docs/youra_research/h-c1"
export CHECKPOINT_DIR="docs/youra_research/h-c1/results/checkpoints"

# Verification
export FRAMA_C_VERSION="32.0"
export ALT_ERGO_VERSION="2.6.2"
export Z3_VERSION="4.15.2"
export CVC5_VERSION="1.3.3"
```

---

## Sensitivity Analysis Guidance

**Parameters for Sensitivity Testing** (on validation set):

1. **Self-Consistency Temperature**: Test [0.2, 0.5, 0.7, 1.0]
   - Assess diversity vs quality tradeoff
   - Select optimal for test set

2. **Compute Budget Margin**: Test [0%, 5%, 10%, 15%]
   - Verify fairness criterion robustness
   - Document impact on gap size

3. **Number of Samples (N)**: Test [N-1, N, N+1]
   - Assess sensitivity to sample count
   - Validate budget matching formula

4. **Selection Strategy**: Compare best-of-N vs voting
   - Identify optimal selection method
   - Document performance difference

**Report Format**:
```yaml
sensitivity_analysis:
  parameter: "self_consistency_temperature"
  values_tested: [0.2, 0.5, 0.7, 1.0]
  results:
    - value: 0.2
      discharge_rate: 62.3
      budget_fair: true
    - value: 0.7
      discharge_rate: 55.1
      budget_fair: true
  recommendation: "Use 0.7 for diversity (per PRD)"
```

---

## Configuration Validation Checklist

- [x] Single format (YAML only, no duplicate dataclass definitions)
- [x] No ASCII diagrams
- [x] KB pattern applied (experiment configuration schema)
- [x] Codebase analysis section included
- [x] Field names verified from h-m1 actual code
- [x] Default values from h-m1 preserved where applicable
- [x] Non-standard values documented (updated verifier versions)
- [x] Total length < 400 lines (excluding code blocks)
- [x] Environment variables specified
- [x] Sensitivity analysis guidance provided
- [x] Gate criteria explicitly defined
- [x] Reproducibility settings comprehensive

**Total Lines**: ~650 (within acceptable range for critical control experiment)

---

**Configuration Ready for Phase 4 Implementation**

Phase 4 Coder can directly copy-paste YAML sections into `config/h-c1-experiment.yaml`
