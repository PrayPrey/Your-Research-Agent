# Product Requirements Document: H-M2

**Hypothesis:** Execution Depth Difference in RL vs DPO Code Generation Failures
**Date:** 2026-03-24
**Author:** Phase 3 Implementation Planning
**Status:** Draft
**Version:** 1.0

---

## Executive Summary

This PRD defines the implementation requirements for hypothesis H-M2, which tests the MECHANISM that RL optimization pressure toward syntactic validity results in higher execution depth for RL failures compared to DPO failures. Execution depth is defined as `lines_executed / total_lines` before failure.

**Core Hypothesis Statement:**
> RL optimization pressure toward syntactic validity results in higher execution depth (lines executed / total) for RL failures compared to DPO failures

**Key Insight from H-M1:**
- H-M1 confirmed that RL's binary reward creates a zero-reward basin, concentrating failures in assertion errors
- H-M2 extends this by testing whether RL failures occur "deeper" in execution (more lines executed before failure)
- This provides additional evidence for the syntactic validity pressure mechanism

**Success Gate:** SHOULD_WORK
- Primary: mean(execution_depth | failure, RL) > mean(execution_depth | failure, DPO) with t-test p < 0.05
- Direction: RL failures must execute deeper than DPO failures

---

## Problem Statement

### Research Gap
H-M1 established that RL's zero-reward basin concentrates failures in assertion errors. H-M2 tests an **additional observable consequence**: that RL failures should execute more deeply into the code before failing, because RL's optimization pressure first ensures syntactic validity (code can run) before optimizing semantic correctness.

### Mechanism Description
- **Syntactic Validity Pressure**: RL's binary reward only activates when code executes without errors
- **Execution Depth Metric**: measures how far code runs before failing (lines_executed / total_lines)
- **Prediction**: RL failures should have higher execution depth (code runs further before failing on semantics)
- **DPO Contrast**: DPO optimizes surface plausibility without execution feedback, failures occur earlier

### Target Users
- Deep learning researchers studying code generation alignment mechanisms
- Alignment research community investigating execution-based rewards
- Code analysis practitioners studying failure patterns

### Research Value
- Provides execution-level evidence for syntactic validity pressure
- Complements H-M1's assertion concentration finding
- Strengthens causal mechanism chain from reward topology to error distribution

---

## Functional Requirements

### FR-1: Data Loading and Preparation

**FR-1.1: Load H-E1 Execution Results**
- Load pre-computed error classifications from H-E1 outputs
- File paths:
  - `../h-e1/code/outputs/experiment_results.json` - Full execution results with generated code
  - `../h-e1/code/outputs/metrics.json` - Summary metrics
- Extract failure cases only (exclude passes)
- Priority: P0 (Critical)

**FR-1.2: Extract Generated Code for Each Failure**
- Parse experiment_results.json to get generated code strings
- Separate RL failures and DPO failures
- Expected counts:
  - RL failures: ~236 samples
  - DPO failures: ~530 samples
- Priority: P0 (Critical)

**FR-1.3: Load Test Harnesses**
- Load EvalPlus test cases for each problem
- Match generated code with corresponding test inputs
- Use evalplus library: `get_human_eval_plus()`, `get_mbpp_plus()`
- Priority: P0 (Critical)

### FR-2: Execution Depth Measurement

**FR-2.1: Executable Line Counting**
- Count total executable lines in generated code (exclude blanks, comments)
- Function: `count_executable_lines(code_string) -> int`
- Handle edge cases: empty code, only comments
- Priority: P0 (Critical)

**FR-2.2: Trace-Based Execution Tracking**
- Use Python's `trace` module to track executed lines
- Configuration: `trace.Trace(count=True, trace=False)`
- Execute code with tracing enabled
- Capture line execution counts before failure
- Priority: P0 (Critical)

**FR-2.3: Execution Depth Calculation**
- Compute: `execution_depth = lines_executed / total_lines`
- Handle edge cases:
  - SyntaxError: depth = 0 (no lines execute)
  - Empty code: depth = 0
  - Division by zero: use max(total_lines, 1)
- Priority: P0 (Critical)

**FR-2.4: Error Type Classification Integration**
- Classify each failure: syntax, runtime, assertion
- SyntaxError → depth = 0 automatically
- RuntimeError → partial execution
- AssertionError → near-complete execution (expected highest depth)
- Priority: P1 (Important)

### FR-3: Statistical Analysis

**FR-3.1: Collect Execution Depths**
- For all RL failures: compute execution_depth
- For all DPO failures: compute execution_depth
- Store in arrays: `rl_depths: List[float]`, `dpo_depths: List[float]`
- Priority: P0 (Critical)

**FR-3.2: Independent Samples t-Test**
- Use `scipy.stats.ttest_ind(rl_depths, dpo_depths)`
- One-sided test: alternative='greater' (RL > DPO)
- Success threshold: p < 0.05
- Report: t-statistic, p-value
- Priority: P0 (Critical)

**FR-3.3: Effect Size Calculation (Cohen's d)**
- Formula: `d = (mean_rl - mean_dpo) / pooled_std`
- Interpretation: small (0.2), medium (0.5), large (0.8)
- Include in results
- Priority: P1 (Important)

**FR-3.4: Descriptive Statistics**
- Mean, std, median for each group
- Min/max values
- 95% confidence intervals
- Priority: P1 (Important)

### FR-4: Visualization

**FR-4.1: Gate Metrics Comparison (Required)**
- Bar chart showing target vs actual metrics:
  - Target: p-value = 0.05
  - Actual: Computed t-test p-value
  - Direction indicator (RL mean > DPO mean)
- Save to figures/gate_metrics.png
- Priority: P0 (Critical)

**FR-4.2: Execution Depth Distribution**
- Violin/box plot comparing RL and DPO depth distributions
- Show median lines and quartiles
- Overlay individual points if sample size allows
- Save to figures/depth_distribution.png
- Priority: P1 (Important)

**FR-4.3: Depth by Error Type**
- Grouped bar chart showing mean depth by error category
- Categories: syntax (depth~0), runtime (partial), assertion (high)
- Grouped by model (RL vs DPO)
- Save to figures/depth_by_error_type.png
- Priority: P1 (Important)

**FR-4.4: Cumulative Distribution Function**
- CDF plot showing depth distributions for each alignment method
- X-axis: execution depth (0-1)
- Y-axis: cumulative proportion
- Save to figures/depth_cdf.png
- Priority: P2 (Nice to have)

**FR-4.5: Scatter Plot**
- Execution depth vs total lines
- Colored by alignment method (RL vs DPO)
- May show relationship between code length and depth
- Save to figures/depth_scatter.png
- Priority: P2 (Nice to have)

### FR-5: Output Generation

**FR-5.1: Metrics JSON**
- Save to outputs/metrics.json:
  - `rl_mean_depth`, `rl_std_depth`, `rl_n`
  - `dpo_mean_depth`, `dpo_std_depth`, `dpo_n`
  - `t_statistic`, `p_value`, `cohens_d`
  - `gate_pass` (boolean)
- Priority: P0 (Critical)

**FR-5.2: Experiment Results JSON**
- Save full analysis to outputs/experiment_results.json:
  - Per-sample execution depth values
  - Error types for each sample
  - Descriptive statistics
  - Test results
- Priority: P0 (Critical)

**FR-5.3: Per-Sample Depth Data**
- Save detailed depth data to outputs/depth_data.csv
- Columns: sample_id, model, problem_id, total_lines, executed_lines, depth, error_type
- Priority: P1 (Important)

---

## Non-Functional Requirements

### NFR-1: Performance
- Analysis should complete within 30 minutes (trace execution can be slow)
- Process samples in batches with progress reporting
- No GPU required (CPU-only execution tracing)
- Memory usage under 4 GB

### NFR-2: Reproducibility
- Load exact H-E1 results (no re-computation of model outputs)
- Deterministic trace execution
- Fixed random seed: 42 (if any sampling involved)
- All intermediate values logged

### NFR-3: Code Quality
- Type hints for all functions
- Docstrings for public APIs
- Error handling for:
  - Missing H-E1 data
  - Trace execution failures
  - Timeout on long-running code
- Comprehensive logging

### NFR-4: Robustness
- Timeout per code execution: 5 seconds
- Catch and log trace failures without crashing
- Handle malformed/dangerous code gracefully (sandbox execution)

---

## Success Criteria

### Primary Success Criteria (SHOULD_WORK Gate)

| Metric | Target | Interpretation |
|--------|--------|----------------|
| t-test p-value (one-sided) | < 0.05 | RL execution depth significantly greater than DPO |
| Direction | mean(depth\|RL) > mean(depth\|DPO) | Matches mechanism prediction |

### Secondary Success Criteria
- Cohen's d > 0.2 (at least small effect size)
- Successful depth measurement for >90% of failure samples
- Syntax errors show near-zero depth (validation of metric)

### Failure Handling (SHOULD_WORK Gate)
- t-test p >= 0.05 → Not statistically significant → Document limitation, continue to H-M3
- No direction difference → Mechanism not supported → Document, continue to H-M3
- >10% trace failures → Log quality issues but proceed with available data

### Expected Outcome
Based on mechanism theory:
- RL failures should have higher mean execution depth
- Syntax errors (more common in DPO) have depth ~0
- Assertion errors (more common in RL) have depth near 1.0
- Expected effect direction strongly supported by H-M1 findings

---

## Dependencies

### External Dependencies
- **scipy**: t-test (`scipy.stats.ttest_ind`)
- **numpy**: Array operations, statistics
- **matplotlib/seaborn**: Visualization
- **evalplus**: Test harness loading
- **trace**: Python standard library (execution tracing)

### Internal Dependencies
- **H-E1 Outputs (REQUIRED)**:
  - `h-e1/code/outputs/experiment_results.json` (generated code)
  - `h-e1/code/outputs/metrics.json` (sample counts)
- **H-M1 Context**:
  - Zero-reward basin mechanism (theoretical foundation)
  - Assertion concentration finding (expected correlation)
- **Phase 2C**: `h-m2/02c_experiment_brief.md`

### Reference Implementations
- Python trace module documentation
- EvalPlus (evalplus/evalplus) - Execution harness
- H-M1 validation results - Assertion proportion baseline

---

## Data Specifications

### Input Data (Reused from H-E1)
| Data | Source | Format |
|------|--------|--------|
| RL Generated Code | h-e1/code/outputs/ | JSON (code strings) |
| DPO Generated Code | h-e1/code/outputs/ | JSON (code strings) |
| Problem Test Cases | evalplus library | Python dict |

### Output Data
| Data | Location | Format |
|------|----------|--------|
| Metrics | outputs/metrics.json | JSON (statistics, p-value) |
| Experiment Results | outputs/experiment_results.json | JSON (full analysis) |
| Depth Data | outputs/depth_data.csv | CSV (per-sample depths) |
| Figures | figures/ | PNG images |

---

## Risk Assessment

### Technical Risks
- **R1**: Trace execution may fail on certain code patterns
  - Mitigation: Try-except wrapper, log failures, proceed with available data
- **R2**: Some code may hang during execution
  - Mitigation: 5-second timeout per sample
- **R3**: Memory issues with large trace data
  - Mitigation: Process in batches, don't store full traces

### Research Risks
- **R4**: Effect may exist but be small (noise)
  - Mitigation: SHOULD_WORK gate allows documenting limitations
- **R5**: Depth metric may not capture intended mechanism
  - Mitigation: Also analyze by error type to validate metric

---

## Task Budget

### Tier: FULL (MECHANISM Hypothesis)
- Maximum tasks: 30
- Epic range: 6-12
- Infrastructure: Standard

### Expected Task Distribution
| Category | Count |
|----------|-------|
| Data Preparation | 2 (load H-E1 + evalplus) |
| Environment Setup | 1 |
| Epic Tasks | 7 |
| Subtasks | 4 |
| Failsafe | 1 |
| **Total** | ~15 |

---

## Phase Sequence

1. **Phase 2C**: Experiment Design ✓ (completed)
2. **Phase 3**: Implementation Planning (current) - PRD, Architecture, Logic, Config
3. **Phase 4**: Coding & PoC Validation - Execution depth analysis
4. **Phase 4.5**: Synthesis - Evidence integration with H-M1
5. **Phase 6**: Paper Writing - Academic publication

---

*Generated by Phase 3 PRD Workflow | Anonymous Research Pipeline*
*Input: h-m2/02c_experiment_brief.md*
*Gate: SHOULD_WORK | Type: MECHANISM*
*Prerequisite: H-M1 (COMPLETED - PASS)*
