# Configuration Specification: h-m3 Coverage-Advantage Correlation Study

**Hypothesis ID:** h-m3  
**Type:** MECHANISM (Data Analysis)  
**Date:** 2026-08-19

---

## 1. Hyperparameters

### Coverage Measurement

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `coverage_mode` | `branch` | Branch coverage (not just statement coverage) |
| `timeout_per_problem` | 60 seconds | Prevent hanging on infinite loops |
| `parallelism` | `os.cpu_count()` | Max CPU utilization |

### Per-Problem Evaluation

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `num_samples` | 20 | HumanEval standard (pass@1 estimation) |
| `temperature` | 0.8 | Balance diversity and correctness |
| `max_length` | 512 tokens | Sufficient for most solutions |
| `do_sample` | True | Stochastic generation |
| `test_timeout` | 5 seconds | Prevent hanging on infinite loops |
| `device` | `cuda` if available, else `cpu` | GPU acceleration |

### Correlation Analysis

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `alpha` | 0.05 | Significance level (95% confidence) |
| `correlation_method` | `pearson` | Linear correlation (expected pattern) |
| `min_sample_size` | 100 | Warn if n < 100 (underpowered) |

---

## 2. Dataset Configuration

### HumanEval

```yaml
dataset:
  name: openai/human-eval
  source: HuggingFace
  cache_dir: /home/PrayPrey/.cache/huggingface/datasets/openai_humaneval
  num_problems: 164
  fields:
    prompt: prompt
    canonical_solution: canonical_solution
    test: test
    entry_point: entry_point
  expected_coverage: 75-85% (hypothesis)
```

### MBPP

```yaml
dataset:
  name: mbpp
  source: HuggingFace
  cache_dir: /home/PrayPrey/.cache/huggingface/datasets/mbpp
  num_problems: 974
  fields:
    prompt: text
    canonical_solution: code
    test: test_list (join all tests)
    entry_point: (not provided, infer from code)
  expected_coverage: 45-60% (hypothesis)
```

---

## 3. Model Configuration

### Models (Reuse from h-e1)

```yaml
models:
  - name: CodeGen-350M-binary
    checkpoint: /path/to/h-e1/checkpoints/codegen-350M-binary-grpo-step500
    architecture: Salesforce/codegen-350M-mono
    feedback_type: binary
    
  - name: CodeGen-350M-error-type
    checkpoint: /path/to/h-e1/checkpoints/codegen-350M-error-type-grpo-step500
    architecture: Salesforce/codegen-350M-mono
    feedback_type: error-type
    
  - name: StarCoder-1B-binary
    checkpoint: /path/to/h-e1/checkpoints/starcoder-1B-binary-grpo-step500
    architecture: bigcode/starcoderbase-1b
    feedback_type: binary
    
  - name: StarCoder-1B-error-type
    checkpoint: /path/to/h-e1/checkpoints/starcoder-1B-error-type-grpo-step500
    architecture: bigcode/starcoderbase-1b
    feedback_type: error-type
```

**Note:** Exact checkpoint paths to be determined from h-e1 validation results. If h-e1 used different step counts or naming, update accordingly.

---

## 4. File Paths

### Input Data

```yaml
inputs:
  datasets:
    humaneval: /home/PrayPrey/.cache/huggingface/datasets/openai_humaneval
    mbpp: /home/PrayPrey/.cache/huggingface/datasets/mbpp
  models:
    base_dir: /path/to/h-e1/checkpoints  # Update after h-e1 completion
```

### Output Data

```yaml
outputs:
  coverage:
    humaneval: data/coverage_analysis/humaneval_coverage.json
    mbpp: data/coverage_analysis/mbpp_coverage.json
  evaluation:
    base_dir: data/h-m3
    naming: per_problem_results_{model}_{feedback}_{benchmark}.json
    # Example: per_problem_results_CodeGen-350M_binary_HumanEval.json
  plots:
    base_dir: plots
    coverage_correlation: h-m3_coverage_advantage_correlation.png
    coverage_distributions: h-m3_coverage_distributions.png
    stratified_correlation: h-m3_stratified_correlation.png
  report:
    path: docs/youra_research/h-m3/04_validation.md
```

---

## 5. Dependencies & Environment

### Python Packages

```yaml
dependencies:
  - coverage>=7.15
  - datasets>=2.14.0
  - transformers>=4.35.0
  - torch>=2.1.0
  - scipy>=1.11.0
  - matplotlib>=3.8.0
  - numpy>=1.24.0
```

### Hardware Requirements

```yaml
hardware:
  coverage_measurement:
    device: CPU
    cores: all available
    memory: ~8 GB (coverage.py overhead)
  per_problem_evaluation:
    device: GPU (CUDA)
    gpu_memory: ~16 GB (1B model inference)
    fallback: CPU (much slower, ~10x)
  correlation_analysis:
    device: CPU
    memory: ~4 GB
```

---

## 6. Execution Configuration

### Coverage Measurement Script

```yaml
coverage_measurement:
  script: src/h-m3/coverage_measurement.py
  parallelism: max (os.cpu_count())
  timeout_per_problem: 60
  output:
    - data/coverage_analysis/humaneval_coverage.json
    - data/coverage_analysis/mbpp_coverage.json
  runtime: ~2-4 hours
```

### Per-Problem Evaluation Script

```yaml
per_problem_evaluation:
  script: src/h-m3/per_problem_eval.py
  arguments:
    --model: [CodeGen-350M, StarCoder-1B]
    --feedback: [binary, error-type]
    --benchmark: [HumanEval, MBPP]
  runs: 8 (2 models × 2 feedback × 2 benchmarks)
  num_samples_per_problem: 20
  temperature: 0.8
  device: cuda
  output:
    base_dir: data/h-m3
    naming: per_problem_results_{model}_{feedback}_{benchmark}.json
  runtime_per_run: ~20-30 minutes (GPU)
  total_runtime: ~2-3 hours
```

### Correlation Analysis Script

```yaml
correlation_analysis:
  script: src/h-m3/correlation_analysis.py
  inputs:
    coverage:
      - data/coverage_analysis/humaneval_coverage.json
      - data/coverage_analysis/mbpp_coverage.json
    evaluation:
      - data/h-m3/per_problem_results_*.json (8 files)
  tests:
    - pearson_correlation
    - coverage_difference_ttest
    - partial_correlation_difficulty_controlled
    - stratified_analysis
  plots:
    - plots/h-m3_coverage_advantage_correlation.png
    - plots/h-m3_coverage_distributions.png
    - plots/h-m3_stratified_correlation.png
  report:
    output: docs/youra_research/h-m3/04_validation.md
  runtime: <5 minutes
```

---

## 7. Success Criteria Configuration

### Gate Evaluation

```yaml
gate:
  type: SHOULD_WORK
  criteria:
    coverage_correlation:
      metric: pearson_r
      threshold: 0.77
      direction: negative (r < 0)
      p_value: <0.05
    coverage_difference:
      metric: mean_diff
      threshold: 10 (percentage points)
      p_value: <0.05
  verdict:
    PASS: "r ≥ 0.77 AND p < 0.05 AND coverage_diff ≥ 10pp"
    FAIL_NULL: "r < 0.5 (null result, not blocking)"
    FAIL_MARGINAL: "0.5 ≤ r < 0.77 (partial support)"
```

---

## 8. Logging & Monitoring

### Logging Configuration

```yaml
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  outputs:
    - console: True
    - file: logs/h-m3_{script_name}_{timestamp}.log
  per_module:
    coverage_measurement:
      log_skipped_problems: True
      log_zero_branches: True
    per_problem_evaluation:
      log_inference_failures: True
      log_test_timeouts: True
    correlation_analysis:
      log_sample_size_warnings: True
```

### Progress Monitoring

```yaml
progress:
  coverage_measurement:
    report_every: 50 problems
    show_eta: True
  per_problem_evaluation:
    report_every: 10 problems
    show_eta: True
```

---

## 9. Reproducibility Configuration

### Random Seeds

```yaml
random_seeds:
  model_generation: 42  # Fixed seed for reproducibility
  dataset_shuffle: null  # No shuffling (evaluate in dataset order)
  torch_seed: 42
  numpy_seed: 42
```

**Note:** Even with fixed seeds, temperature 0.8 sampling introduces stochasticity. To ensure exact reproducibility, store generated samples (not just pass@1 results).

### Caching

```yaml
caching:
  coverage_results: True  # Save JSON, reuse if already computed
  evaluation_results: True  # Save JSON, reuse if already computed
  generated_code: False  # Do not cache generated samples (large)
```

---

## 10. Error Handling Configuration

### Retry Policy

```yaml
retry:
  coverage_measurement:
    enabled: False  # No retry (offline, deterministic)
  per_problem_evaluation:
    enabled: True
    max_retries: 3
    backoff: exponential (1s, 2s, 4s)
    retry_on:
      - CUDA out of memory
      - Model inference timeout
```

### Graceful Degradation

```yaml
graceful_degradation:
  coverage_measurement:
    skip_on_error: True  # Skip problem, log warning
  per_problem_evaluation:
    fallback_to_cpu: True  # If GPU fails, retry on CPU
```

---

**End of Configuration**
