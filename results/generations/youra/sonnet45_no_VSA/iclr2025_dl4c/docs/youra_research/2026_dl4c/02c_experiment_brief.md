# Phase 2C: Experiment Design Brief
## H-E1: Proxy Measurement Reliability

**Generated**: 2026-07-09  
**Hypothesis ID**: h-e1  
**Type**: EXISTENCE  
**Gate**: MUST_WORK  
**Prerequisites**: None (READY)  
**Archon Task ID**: af62f509-0467-4742-b644-62e460ed8f16

---

## Executive Summary

This experiment validates the **measurement reliability** of three proxy metrics (CodeBLEU, normalized runtime ratio, learned PR-style score) for code generation quality assessment. The validation follows a three-pronged approach: (1) intra-implementation reproducibility (CV ≤5%), (2) inter-complexity-class separability (Cohen's d ≥0.8), and (3) cross-hardware rank consistency (Spearman ρ ≥0.8).

**Critical Success Criteria**:
- At least **one proxy** passes all three validation tests
- If efficiency metric fails CV threshold, drop it and continue with CodeBLEU + style
- Gate advancement requires: ≥1 validated proxy

**Timeline**: 2 weeks  
**Compute Budget**: ~50 GPU hours (primarily for PR-style model inference)

---

## 1. Research Context & Implementation Insights

### 1.1 CodeBLEU Implementation
**Source**: k4black/codebleu (PyPI package, supports Python/C++/Java/JavaScript)

**Key Findings**:
- Weighted combination of 4 sub-metrics: n-gram match (BLEU), weighted n-gram match, AST match, dataflow match
- Default weights: (0.25, 0.25, 0.25, 0.25)
- Requires tree-sitter compilation (platform-dependent, available for Linux/macOS/Windows)
- Output range: [0, 1] per metric component

**Implementation Pattern**:
```python
from codebleu import calc_codebleu

result = calc_codebleu(
    references=[reference_code],  # list[str] or list[list[str]]
    predictions=[predicted_code],  # list[str]
    lang="python",
    weights=(0.25, 0.25, 0.25, 0.25)
)
# Returns: {'codebleu': float, 'ngram_match_score': float, 
#           'weighted_ngram_match_score': float, 
#           'syntax_match_score': float, 'dataflow_match_score': float}
```

### 1.2 Runtime Measurement Best Practices
**Source**: Python timeit, pyperf, pytest-benchmark, microbench

**Key Insights**:
1. **Timer Selection**: Use `time.perf_counter()` (default, wall-clock) for realistic latency; avoid `time.process_time()` (CPU-only) as it misses I/O and GPU wait times
2. **Repetition Strategy**: 
   - Run 5+ repetitions per measurement
   - Report **minimum time** (not mean) as lower bound of machine capability
   - Higher values = external interference, not Python variability
3. **Calibration**: Auto-calibrate to achieve ≥0.2s total runtime (pyperf approach)
4. **Isolation**: Disable GC during measurement, warm up interpreter before timing
5. **Metadata Capture**: Record Python version, hardware specs, environment variables for reproducibility (microbench pattern)

**Implementation Pattern** (pytest-benchmark style):
```python
import time
import gc

def measure_runtime(func, args, n_runs=5, warmup=2):
    # Warm up
    for _ in range(warmup):
        func(*args)
    
    # Disable GC, measure
    gc.disable()
    times = []
    for _ in range(n_runs):
        start = time.perf_counter()
        func(*args)
        end = time.perf_counter()
        times.append(end - start)
    gc.enable()
    
    return min(times)  # Lower bound of capability
```

### 1.3 Statistical Validation Patterns
**Cohen's d Calculation** (Effect Size):
```python
import numpy as np

def cohens_d(group1, group2):
    """Effect size for complexity class separation"""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    return (np.mean(group1) - np.mean(group2)) / pooled_std
```

**Coefficient of Variation** (Reproducibility):
```python
def coefficient_of_variation(values):
    """CV = std / mean, measures relative variability"""
    return np.std(values, ddof=1) / np.mean(values)
```

**Spearman Rank Correlation** (Cross-Hardware Consistency):
```python
from scipy.stats import spearmanr

rho, p_value = spearmanr(hardware1_ranks, hardware2_ranks)
# rho ≥ 0.8 required, p < 0.01
```

---

## 2. Dataset Specification

### 2.1 Primary Dataset: HumanEval
**Type**: standard  
**Source**: openai/human-eval (GitHub)  
**Size**: 164 hand-written programming problems with test suites

**Rationale**:
- Standard benchmark with established test coverage
- Each problem has canonical solution + test suite
- Enables controlled generation of complexity variants

**Usage Strategy**:
1. **Calibration Study** (Test 1): Sample **50 problems** from full 164
2. **Complexity Study** (Test 2): Select **50 problems** amenable to algorithmic variants
3. **Cross-Hardware Study** (Test 3): Reuse same 50 problems from Test 1

**Data Split**: No train/test split needed (metric validation, not model training)

### 2.2 Solution Generation Strategy
**Source of Reference Solutions**: HumanEval canonical solutions  
**Source of Predicted Solutions**: 
- For Test 1: Generate 10 solutions per problem using **CodeLlama-7B-Instruct** (greedy decoding, temperature=0.8 for diversity)
- For Test 2: Hand-craft or semi-automatically generate complexity variants:
  - Variant A: O(n) solution (optimal)
  - Variant B: O(n²) solution (naive)
  - Variant C: O(n log n) solution (intermediate)

**Total Solutions Generated**:
- Test 1: 50 problems × 10 solutions × 5 runs = 2,500 metric computations
- Test 2: 50 problems × 3 variants = 150 solutions
- Test 3: 50 problems × 10 solutions (reuse from Test 1)

### 2.3 Synthetic Complexity Problems (OPTIONAL FALLBACK)
**CRITICAL**: Only use if HumanEval proves insufficient for complexity variants.

**Type**: programmatic-api (generated from known templates, NOT simulated)  
**Source**: LeetCode API or Codeforces API (real problems with known complexity classes)  
**Selection Criteria**: Problems with multiple known solutions at different complexity classes

**Justification**: Real algorithmic problems with verified complexity boundaries, not synthetic/simulated data.

---

## 3. Experimental Design

### 3.1 Test 1: Intra-Implementation Reproducibility (CV ≤ 5%)

**Objective**: Verify metrics produce consistent measurements on identical inputs.

**Protocol**:
1. For each of 50 HumanEval problems:
   - Generate 10 diverse solutions using CodeLlama-7B-Instruct
   - For each solution:
     - Compute CodeBLEU **5 times** (identical inputs)
     - Compute runtime efficiency **5 times** (same execution environment)
     - Compute PR-style score **5 times** (same model checkpoint)
2. Calculate CV for each metric across 5 runs
3. Aggregate: Report % of solutions with CV ≤ 5%

**Success Criteria**:
- **CodeBLEU**: CV ≤ 5% for ≥95% of solutions (deterministic metric, should be near-perfect)
- **Runtime Efficiency**: CV ≤ 5% for ≥80% of solutions (allows for system noise)
- **PR-Style Score**: CV ≤ 5% for ≥90% of solutions (neural model, greedy decoding should be deterministic)

**Statistical Test**: None (descriptive statistics only)

**Environment Control**:
- Same GPU/CPU allocation across runs (use `taskset` to pin cores)
- Disable Turbo Boost, fix CPU frequency
- Use Docker container for isolation
- Warm up interpreter/GPU before measurements

**Implementation Notes**:
- CodeBLEU: No randomness expected, CV should be ~0
- Runtime: Capture minimum of 5 runs (pyperf pattern), calculate CV on all 5
- PR-Style: Use deterministic inference (greedy decoding, fixed seed)

**Failure Handling**: If efficiency CV > 5% for >20% of solutions, **drop efficiency proxy** and continue with CodeBLEU + style.

---

### 3.2 Test 2: Inter-Complexity-Class Separability (Cohen's d ≥ 0.8)

**Objective**: Verify runtime efficiency metric distinguishes algorithmic complexity classes.

**Protocol**:
1. Select 50 HumanEval problems amenable to complexity variants
2. For each problem, generate 3 solutions:
   - O(n) solution (optimal complexity)
   - O(n²) solution (naive nested loops)
   - O(n log n) solution (divide-and-conquer or heap-based)
3. Measure runtime efficiency on **controlled input sizes**:
   - Small input: n=100
   - Medium input: n=1000
   - Large input: n=5000
4. Calculate Cohen's d between each pair:
   - d(O(n), O(n²))
   - d(O(n), O(n log n))
   - d(O(n log n), O(n²))

**Success Criteria**:
- Cohen's d ≥ 0.8 between O(n) vs O(n²) for ≥80% of problems
- Cohen's d ≥ 0.5 between O(n) vs O(n log n) for ≥70% of problems
- Large input (n=5000) shows stronger separation than small input (n=100)

**Statistical Test**:
- Welch's t-test (unequal variances) for mean runtime difference (p < 0.01)
- Report Cohen's d as primary metric (standardized effect size)

**Input Size Selection Rationale**:
- n=100: Too small, may not show asymptotic behavior (overhead dominates)
- n=1000: Sweet spot for detecting O(n) vs O(n²) differences
- n=5000: Confirms asymptotic trend (quadratic should be 25× slower than linear)

**Normalization Strategy**:
```python
normalized_runtime_ratio = (runtime - baseline_O_n) / baseline_O_n
# baseline_O_n = optimal solution runtime for same problem
```

**Complexity Variant Generation**:
- **Manual**: For 10 high-priority problems, hand-craft variants
- **Semi-Automatic**: Use CodeLlama-7B-Instruct with prompts like:
  - "Solve using nested loops (O(n²))"
  - "Solve using optimal O(n) approach"
- **Validation**: Verify generated code matches intended complexity via code review

**Failure Handling**: If d < 0.8 for >20% of problems, investigate:
1. Input sizes too small → Increase to n=10,000
2. Overhead dominates signal → Use pure algorithmic tasks (no I/O)
3. If still failing after 1 modification attempt → Drop efficiency proxy

---

### 3.3 Test 3: Cross-Hardware Rank Correlation (Spearman ρ ≥ 0.8)

**Objective**: Verify runtime rankings remain consistent across hardware platforms.

**Protocol**:
1. Reuse 50 problems × 10 solutions from Test 1 (500 total solutions)
2. Measure runtime efficiency on **two platforms**:
   - **Platform A**: AWS g4dn.xlarge (NVIDIA T4 GPU, 4 vCPU, 16 GB RAM)
   - **Platform B**: Local workstation (user-specified GPU, document specs)
3. For each platform, rank all 500 solutions by runtime efficiency
4. Compute Spearman rank correlation between Platform A and Platform B rankings

**Success Criteria**:
- Spearman ρ ≥ 0.8 (strong rank agreement)
- p-value < 0.01 (statistically significant)

**Statistical Test**:
- Spearman's rank correlation (non-parametric, robust to outliers)
- Bootstrap 95% CI around ρ estimate (1000 resamples)

**Platform Selection Rationale**:
- AWS g4dn.xlarge: Standard ML instance, reproducible
- Local workstation: Represents researcher's actual environment
- Both platforms run same containerized code (Docker image)

**Implementation Notes**:
- Normalize within-platform (Z-score normalization) before ranking
- Use **relative rankings**, not absolute times (different hardware speeds expected)
- Control: Same problem should rank similarly on both platforms (e.g., if problem X's solution A is faster than solution B on Platform A, same should hold on Platform B)

**Failure Handling**: If ρ < 0.8:
1. Investigate platform-specific optimizations (e.g., GPU memory bandwidth differences)
2. Restrict to CPU-only timing (remove GPU variability)
3. If still failing → Acknowledge hardware-dependent efficiency, scope claims to specific hardware profile

---

### 3.4 PR-Style Score Model Specification

**Model Type**: Learned proxy (fine-tuned BERT-style model or retrieval-based similarity)

**Training Data**: GitHub PR diffs with acceptance labels (from SWE-bench or custom corpus)

**Architecture Options** (select one):
1. **CodeBERT** fine-tuned on PR acceptance classification
2. **GraphCodeBERT** (AST-aware, better code understanding)
3. **Cosine similarity** to accepted PR embeddings (retrieval baseline)

**For Phase 2C (Experiment Design)**: 
- **Assume**: Pre-trained CodeBERT checkpoint available (e.g., microsoft/codebert-base)
- **Defer training**: Phase 3 will specify fine-tuning protocol if needed
- **Test 1 usage**: Inference only (greedy decoding, deterministic)

**Input Format**:
```python
# Tokenize code pair (reference, prediction)
inputs = tokenizer(
    reference_code, 
    predicted_code, 
    padding=True, 
    truncation=True, 
    max_length=512, 
    return_tensors="pt"
)
score = model(**inputs).logits.softmax(dim=-1)[:, 1]  # Prob(accepted)
```

**CV Test**: Should be ≤5% if using greedy decoding (no dropout during inference)

---

## 4. Metrics & Statistical Analysis

### 4.1 Primary Metrics

| Metric | Formula | Threshold | Interpretation |
|--------|---------|-----------|----------------|
| **Coefficient of Variation (CV)** | σ / μ | ≤ 5% | Lower = more reproducible |
| **Cohen's d** | (μ₁ - μ₂) / σ_pooled | ≥ 0.8 | Higher = better separation |
| **Spearman ρ** | Rank correlation | ≥ 0.8 | Higher = more consistent |

### 4.2 Statistical Tests

| Test | Purpose | Significance Level |
|------|---------|-------------------|
| **Descriptive Stats** | CV distribution across solutions | N/A (report percentiles) |
| **Welch's t-test** | Complexity class mean differences | p < 0.01 |
| **Spearman correlation** | Cross-hardware rank agreement | p < 0.01 |
| **Bootstrap CI** | ρ confidence interval | 95% CI |

### 4.3 Reporting Standards

**Test 1 Output**:
```
Metric             | % Solutions with CV ≤ 5% | Median CV | 95th Percentile CV
-------------------|---------------------------|-----------|-------------------
CodeBLEU           | 99.2%                    | 0.001     | 0.012
Runtime Efficiency | 82.4%                    | 0.038     | 0.067
PR-Style Score     | 94.6%                    | 0.021     | 0.048
```

**Test 2 Output**:
```
Complexity Pair    | % Problems with d ≥ 0.8 | Median d | Min d | Max d
-------------------|-------------------------|----------|-------|-------
O(n) vs O(n²)      | 86%                    | 1.24     | 0.52  | 2.83
O(n) vs O(n log n) | 72%                    | 0.68     | 0.31  | 1.45
```

**Test 3 Output**:
```
Hardware Pair        | Spearman ρ | 95% CI       | p-value
---------------------|------------|--------------|----------
AWS vs Local         | 0.847      | [0.812, 0.879] | < 0.001
```

---

## 5. Implementation Plan

### 5.1 Environment Setup

**Base Image**: Ubuntu 22.04 + Python 3.10  
**Key Dependencies**:
```
codebleu==0.7.0
transformers==4.36.0
scipy==1.11.0
numpy==1.24.0
pytest-benchmark==4.0.0
pyperf==2.6.0
docker==6.1.0
```

**Hardware Requirements**:
- **Platform A**: AWS g4dn.xlarge (rent on-demand, ~$0.50/hr × 40 hrs = $20)
- **Platform B**: Local GPU (user-provided, document specs)
- **Storage**: ~10 GB for HumanEval dataset + generated solutions

**Docker Container**:
- Pin CPU cores: `docker run --cpuset-cpus="0-3" ...`
- Fix GPU allocation: `--gpus device=0`
- Disable Turbo Boost: `echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo`

### 5.2 Code Structure

```
h-e1-proxy-reliability/
├── data/
│   ├── humaneval/           # HumanEval benchmark (164 problems)
│   ├── generated_solutions/ # CodeLlama-7B outputs
│   └── complexity_variants/ # Hand-crafted O(n) vs O(n²) solutions
├── src/
│   ├── metrics/
│   │   ├── codebleu_wrapper.py       # CodeBLEU computation
│   │   ├── runtime_profiler.py       # pyperf-based timing
│   │   └── pr_style_scorer.py        # CodeBERT inference
│   ├── experiments/
│   │   ├── test1_reproducibility.py  # CV measurements
│   │   ├── test2_separability.py     # Cohen's d analysis
│   │   └── test3_cross_hardware.py   # Spearman correlation
│   └── utils/
│       ├── solution_generator.py     # CodeLlama inference
│       └── statistical_tests.py      # CV, Cohen's d, Spearman
├── configs/
│   ├── test1_config.yaml
│   ├── test2_config.yaml
│   └── test3_config.yaml
├── outputs/
│   ├── test1_cv_results.csv
│   ├── test2_cohens_d_results.csv
│   └── test3_spearman_results.csv
└── README.md
```

### 5.3 Execution Timeline

**Week 1**:
- **Day 1-2**: Environment setup, install dependencies, download HumanEval
- **Day 3-4**: Generate 500 solutions (50 problems × 10 solutions) using CodeLlama-7B
- **Day 5**: Run Test 1 (CV measurements) on local platform
- **Day 6-7**: Hand-craft complexity variants for Test 2 (20 problems manually, 30 semi-auto)

**Week 2**:
- **Day 8-9**: Run Test 2 (Cohen's d separability) with controlled inputs
- **Day 10-11**: Provision AWS g4dn.xlarge, run Test 3 (cross-hardware)
- **Day 12**: Statistical analysis, generate reports
- **Day 13**: Interpret results, update verification_state.yaml
- **Day 14**: Buffer for debugging or re-runs

### 5.4 Compute Cost Estimate

| Resource | Hours | Cost |
|----------|-------|------|
| Local GPU (solution generation) | 10 hrs | $0 (existing) |
| AWS g4dn.xlarge (cross-hardware test) | 20 hrs | $10 |
| Local GPU (all tests) | 20 hrs | $0 (existing) |
| **Total** | **50 hrs** | **~$10** |

---

## 6. Success Criteria & Gate Logic

### 6.1 MUST_WORK Gate Requirements

**Minimum Viable Outcome**: At least **one proxy** passes all three tests.

**Full Success** (all proxies pass):
- CodeBLEU: CV ≤5% ✓, d ≥0.8 N/A (not a runtime metric), ρ ≥0.8 N/A
- Runtime Efficiency: CV ≤5% ✓, d ≥0.8 ✓, ρ ≥0.8 ✓
- PR-Style Score: CV ≤5% ✓, d ≥0.8 N/A, ρ ≥0.8 N/A
- **Action**: Proceed to H-E2 with all three proxies

**Partial Success** (efficiency fails CV or ρ):
- Drop runtime efficiency proxy
- Continue with CodeBLEU + PR-Style score
- **Action**: Update verification plan, proceed to H-E2 with 2 proxies

**MUST_WORK PARTIAL** (only CodeBLEU passes):
- PR-Style score fails CV (model too stochastic)
- Runtime efficiency fails CV or ρ
- **Action**: 1 modification attempt:
  - Try deterministic PR-Style model (remove dropout)
  - Try CPU-only runtime timing (remove GPU variability)
  - If still failing → Proceed with CodeBLEU only, document limitations

**MUST_WORK FAIL** (all proxies fail):
- CodeBLEU fails CV (impossible, deterministic metric)
- This scenario indicates fundamental implementation error
- **Action**: Debug metric implementations, route to Phase 2A-Dialogue if unfixable

### 6.2 Modification Attempt Protocol

**If Test 1 (CV) fails for ≥2 proxies**:
1. **Attempt 1**: Increase repetitions from 5 to 20 (reduce noise)
2. **Attempt 2**: Use stricter environment isolation (disable hyperthreading)
3. **Limit**: 1 modification attempt total before downgrading to PARTIAL

**If Test 2 (Cohen's d) fails for runtime efficiency**:
1. **Attempt 1**: Increase input size from n=5000 to n=10,000
2. **Attempt 2**: Use pure algorithmic tasks (no I/O, no imports)
3. **Limit**: 1 modification attempt before dropping efficiency

**If Test 3 (Spearman ρ) fails**:
1. **Attempt 1**: Switch to CPU-only timing (remove GPU variability)
2. **Limit**: 1 modification attempt before scoping to single-hardware claims

---

## 7. Risk Analysis & Mitigation

### R1: Runtime Efficiency Too Noisy (CV > 5%)
**Likelihood**: Medium  
**Impact**: Medium (efficiency proxy dropped, continue with 2 proxies)  
**Mitigation**:
- Use pyperf calibration to auto-tune repetitions
- Pin CPU cores, disable Turbo Boost
- Report minimum time (not mean) to reduce noise
- **Fallback**: Drop efficiency, proceed with CodeBLEU + PR-style

### R2: Complexity Variants Hard to Generate
**Likelihood**: Medium  
**Impact**: Low (manually craft for subset of problems)  
**Mitigation**:
- Focus on 20 high-quality manual variants rather than 50 semi-auto
- Use well-known problems (e.g., sorting, search) with obvious O(n) vs O(n²) solutions
- **Fallback**: Use real LeetCode/Codeforces problems with verified complexity labels

### R3: Cross-Hardware Correlation Low (ρ < 0.8)
**Likelihood**: Low  
**Impact**: Medium (efficiency proxy scoped to specific hardware)  
**Mitigation**:
- Use relative rankings (not absolute times)
- Normalize within-platform before correlation
- **Fallback**: Acknowledge hardware-dependent efficiency, limit claims to AWS g4dn platform

### R4: PR-Style Model Stochastic (CV > 5%)
**Likelihood**: Low  
**Impact**: Low (use greedy decoding, fixed seed)  
**Mitigation**:
- Disable dropout during inference
- Use temperature=0 (deterministic)
- **Fallback**: Switch to retrieval-based similarity (cosine to reference embeddings)

---

## 8. Expected Outputs

### 8.1 Deliverables

1. **Data Artifacts**:
   - `generated_solutions.jsonl`: 500 CodeLlama-7B solutions
   - `complexity_variants.jsonl`: 150 hand-crafted O(n)/O(n²)/O(n log n) solutions
   - `test1_cv_raw.csv`: 2,500 metric measurements (500 solutions × 5 runs)
   - `test2_runtimes.csv`: 450 runtime measurements (150 solutions × 3 input sizes)
   - `test3_cross_hardware.csv`: 1,000 runtime measurements (500 solutions × 2 platforms)

2. **Analysis Reports**:
   - `test1_reproducibility_report.md`: CV statistics, pass/fail per proxy
   - `test2_separability_report.md`: Cohen's d distribution, t-test results
   - `test3_cross_hardware_report.md`: Spearman ρ, bootstrap CI

3. **Visualizations**:
   - `cv_distribution.png`: Histogram of CV values per proxy
   - `cohens_d_scatter.png`: O(n) vs O(n²) runtime scatter with effect size
   - `rank_correlation_plot.png`: AWS vs Local rankings with ρ annotation

4. **Updated State**:
   - `verification_state.yaml`: h-e1 status = COMPLETED, validated_proxies = [list]
   - `04_checkpoint.yaml`: experiment_design.status = COMPLETED

### 8.2 Checkpoint Update Schema

```yaml
experiment_design:
  status: COMPLETED
  file: docs/youra_research/02c_experiment_brief.md
  completed_at: 2026-07-09

validation:
  status: NOT_STARTED  # Will be updated in Phase 4
  result: null
  key_findings: []

validated_proxies:  # Updated after Phase 4 validation
  - name: CodeBLEU
    cv_pass: true
    separability_pass: N/A
    cross_hardware_pass: N/A
  - name: runtime_efficiency
    cv_pass: null  # To be determined
    separability_pass: null
    cross_hardware_pass: null
  - name: pr_style_score
    cv_pass: null
    separability_pass: N/A
    cross_hardware_pass: N/A
```

---

## 9. Phase 3 Handoff Notes

**For Implementation Planning** (Phase 3):
1. **Dataset Access**: HumanEval available via `datasets` library: `load_dataset("openai_humaneval")`
2. **CodeLlama-7B**: Use `meta-llama/CodeLlama-7b-Instruct-hf` from HuggingFace (requires access request)
3. **AWS Provisioning**: Use `g4dn.xlarge` spot instances to reduce cost ($0.35/hr vs $0.526/hr on-demand)
4. **Containerization**: Provide Dockerfile with pinned dependencies
5. **Validation Scripts**: Pytest-based test suite for each experiment (test1/test2/test3)

**Critical Assumptions to Validate**:
- HumanEval solutions are diverse enough to show CV variance (if all solutions identical, CV meaningless)
- Complexity variants are implementable for ≥80% of selected problems
- AWS g4dn.xlarge provides sufficient performance (fallback: g5.xlarge with A10G GPU)

**Phase 4 Validation Trigger**:
- When implementation complete, run `pytest tests/test_h_e1_*.py --benchmark-autosave`
- Review outputs in `outputs/` directory
- Update `verification_state.yaml` with pass/fail status per proxy

---

## 10. Alignment with Verification Plan (02b)

**From 02b_verification_plan.md** (H-E1 section):

| Requirement (02b) | Addressed in 02c | Location |
|-------------------|------------------|----------|
| CV ≤ 5% | Test 1, Section 3.1 | ✓ |
| Cohen's d ≥ 0.8 | Test 2, Section 3.2 | ✓ |
| Spearman ρ ≥ 0.8 | Test 3, Section 3.3 | ✓ |
| 50 HumanEval problems | Dataset Spec, Section 2.1 | ✓ |
| 10 solutions × 5 runs | Test 1 Protocol, Section 3.1 | ✓ |
| Controlled asymptotic tasks | Complexity variants, Section 3.2 | ✓ |
| Cross-hardware: AWS g4dn.xlarge vs local | Test 3 Protocol, Section 3.3 | ✓ |
| Falsification: drop efficiency if CV fails | Gate Logic, Section 6.1 | ✓ |
| Timeline: 2 weeks | Execution Timeline, Section 5.3 | ✓ |

**Deviations from 02b**: None. All requirements fully specified.

---

## 11. Experiment Design Checklist

- [x] **Dataset selected**: HumanEval (standard, 164 problems)
- [x] **Sample size justified**: 50 problems (30% of full benchmark, sufficient for statistical power)
- [x] **Metrics operationalized**: CodeBLEU (k4black/codebleu), Runtime (pyperf pattern), PR-Style (CodeBERT)
- [x] **Statistical tests specified**: CV (descriptive), Cohen's d (Welch's t-test), Spearman ρ (non-parametric)
- [x] **Success criteria quantified**: CV ≤5%, d ≥0.8, ρ ≥0.8
- [x] **Environment controlled**: Docker containers, CPU pinning, Turbo Boost disabled
- [x] **Failure modes addressed**: Drop efficiency if noisy, 1 modification attempt protocol
- [x] **Compute budget estimated**: ~50 GPU hours, $10 AWS cost
- [x] **Timeline realistic**: 2 weeks with daily breakdown
- [x] **Handoff to Phase 3 clear**: Code structure, dependencies, critical assumptions documented

---

**Document Status**: Phase 2C Complete (H-E1 Experiment Design)  
**Next Workflow**: Phase 3 Implementation Planning (PRD + Architecture + Tasks)  
**Estimated Phase 3 Start**: Upon approval of this experiment design
