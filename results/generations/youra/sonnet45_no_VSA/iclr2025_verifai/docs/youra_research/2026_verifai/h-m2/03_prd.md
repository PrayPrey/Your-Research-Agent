# Product Requirements Document: H-M2 Staged Progressive Refinement

**Date:** 2026-07-11  
**Author:** Anonymous  
**Hypothesis:** H-M2  
**Type:** Mechanism (SHOULD_WORK)

---

## Executive Summary

This PRD defines the implementation requirements for testing hypothesis H-M2: "Staged progressive refinement (types→pre→post→inv) converges faster and achieves higher proof discharge than complete upfront specification."

The experiment compares two LLM-driven specification synthesis strategies on a shared benchmark of C programs from the Frama-C ACSL verification suite. The baseline (Complete Strategy) generates all specification components simultaneously, while the proposed approach (Staged Strategy) synthesizes specifications sequentially through four stages: types, preconditions, postconditions, and loop invariants.

**Success Criteria:**
- Staged strategy converges in ≤70% of iterations vs. Complete
- Staged strategy achieves ≥5pp higher final proof discharge rate
- Statistical significance (p < 0.05, paired t-test)

**Failure Acceptable:** This is a SHOULD_WORK gate - neutral/negative results do not invalidate the core approach.

---

## Problem Statement

### Research Question
Does staged progressive refinement (types→pre→post→inv) improve convergence speed and proof discharge rate compared to complete upfront specification synthesis?

### Context from H-E1
The prerequisite hypothesis H-E1 validated that LLMs can use structured verifier feedback to iteratively refine formal specifications, achieving 62.9% proof discharge rate (target: 50%). H-M2 builds on this foundation by testing whether a specific refinement ordering (staged) outperforms the baseline (complete).

### Key Unknowns
1. Does sequential staged refinement reduce the search space effectively?
2. Does backtracking between stages negate the benefits of progressive refinement?
3. Which stages provide the most value in the refinement sequence?

---

## Functional Requirements

### FR-1: Dataset Management
**Priority:** P0 (Critical)

#### FR-1.1: Frama-C ACSL Benchmark Acquisition
- Clone `fraunhoferfokus/acsl-by-example` repository
- Clone `Frama-C/open-source-case-studies` repository
- Extract C programs from StandardAlgorithms directory
- **Acceptance:** 100+ C programs with ACSL annotations available locally

#### FR-1.2: Benchmark Program Selection
- Select 30-50 representative programs covering:
  - Simple loops (counting, searching)
  - Nested structures (2D arrays, multi-loop)
  - Pointer manipulation
  - Array bounds checking
- Filter by verifiable complexity (exclude timeout cases)
- **Acceptance:** 30-50 programs selected, documented in `benchmark_programs.txt`

#### FR-1.3: Gold Standard Annotation Extraction
- Strip existing ACSL annotations from selected programs
- Store gold annotations separately for validation
- Create unannotated baseline versions
- **Acceptance:** Each program has two versions: unannotated (input) and gold-annotated (reference)

### FR-2: Baseline Model Implementation (Complete Strategy)
**Priority:** P0 (Critical)

#### FR-2.1: LLM Client Configuration
- Support GPT-4 (via OpenAI API) or Claude Opus (via Anthropic API)
- Configuration: temperature=0.0, max_tokens=4096, timeout=30s
- Retry logic: 3 retries with exponential backoff
- **Acceptance:** LLM client initializes successfully with API key

#### FR-2.2: Complete Refinement Strategy
- Generate all spec components simultaneously (types + pre + post + inv)
- Iterative refinement of complete specification (max 10 iterations)
- Convergence criterion: 2 consecutive iterations with same discharge rate
- **Acceptance:** `CompleteRefinementStrategy` class implements `synthesize_specification(program_code)` method

#### FR-2.3: Frama-C WP Integration
- Execute Frama-C WP on annotated C files
- Parse proof obligation statistics from output
- Extract: total_obligations, verified_obligations, discharge_rate
- Timeout: 10s per proof obligation (inherited from H-E1)
- **Acceptance:** `evaluate_with_framac(c_file_path)` returns `VerificationResult` dataclass

### FR-3: Proposed Model Implementation (Staged Strategy)
**Priority:** P0 (Critical)

#### FR-3.1: Staged Refinement Strategy
- Implement 4-stage sequential refinement:
  1. **Stage 1 (Types)**: Generate type annotations only (max 3 iterations)
  2. **Stage 2 (Preconditions)**: Add preconditions given types (max 3 iterations)
  3. **Stage 3 (Postconditions)**: Add postconditions given types+pre (max 3 iterations)
  4. **Stage 4 (Invariants)**: Add loop invariants given types+pre+post (max 3 iterations)
- Partial verification after each stage
- Total budget: 12 iterations (3 per stage)
- **Acceptance:** `StagedRefinementStrategy` class with `refine_stage(program, spec_so_far, stage, max_iter)` method

#### FR-3.2: Per-Stage Verification
- Verify partial specifications after each stage
- Track stage-specific discharge rates
- Store stage history: `{stage: VerificationResult}`
- **Acceptance:** `stage_history` dict populated with 4 entries (types, pre, post, inv)

#### FR-3.3: Backtracking Detection
- Detect cases where later stages invalidate earlier specs
- Count backtracking events per program
- Log: stage that caused backtracking, affected previous stage
- **Acceptance:** `backtracking_events` counter increments when discharge rate decreases between stages

### FR-4: Experiment Execution
**Priority:** P0 (Critical)

#### FR-4.1: Experiment Runner
- Command-line interface: `python run_experiment.py --strategy {staged|complete} --programs data/*.c`
- Execute both strategies on same 30-50 programs
- Reproducibility: fixed random seed, deterministic LLM (temperature=0.0)
- Progress tracking: iteration counts, discharge rates per program
- **Acceptance:** Experiment completes for all programs under both strategies

#### FR-4.2: Result Aggregation
- Aggregate results across all programs:
  - Mean discharge rate (Staged vs Complete)
  - Mean iterations to convergence (Staged vs Complete)
  - Per-stage improvements (Staged only)
  - Backtracking event statistics (Staged only)
- **Acceptance:** `results_summary.json` contains aggregated metrics for both strategies

### FR-5: Evaluation Metrics
**Priority:** P0 (Critical)

#### FR-5.1: Primary Metrics
- **Proof Discharge Rate:** `(verified_obligations / total_obligations) × 100`
- **Iterations to Convergence:** Count until 2 consecutive iterations with same discharge rate
- **Target:** Staged ≥ Complete + 5pp discharge, Staged ≤ 0.7 × Complete iterations
- **Acceptance:** Metrics computed for all programs

#### FR-5.2: Secondary Metrics (Staged Only)
- **Per-Stage Improvement:** Discharge rate delta after each stage (types, pre, post, inv)
- **Backtracking Events:** Count of cases where later stages invalidate earlier specs
- **Acceptance:** `staged_analysis.json` contains stage-wise breakdown

#### FR-5.3: Statistical Analysis
- Paired t-test: Staged discharge vs Complete discharge (across 30-50 programs)
- Compute p-value, effect size (Cohen's d)
- Significance threshold: p < 0.05
- **Acceptance:** Statistical test results saved to `statistical_analysis.txt`

### FR-6: Visualization
**Priority:** P1 (High)

#### FR-6.1: Gate Metrics Comparison (Mandatory)
- Bar chart: Target vs Actual for Staged and Complete strategies
- Metrics: Discharge rate, Iterations to convergence
- **Acceptance:** `figures/gate_metrics_comparison.png` created

#### FR-6.2: Convergence Comparison Plot
- Line plot: Iteration number (x-axis) vs Discharge rate (y-axis)
- Two lines: Staged (blue), Complete (orange)
- Vertical dashed lines: Stage boundaries for Staged strategy
- **Acceptance:** `figures/convergence_comparison.png` created

#### FR-6.3: Per-Stage Improvement (Staged Only)
- Bar chart: Stages (x-axis) vs Cumulative discharge rate (y-axis)
- Show improvement after each stage: types, pre, post, inv
- **Acceptance:** `figures/per_stage_improvement.png` created

#### FR-6.4: Iteration Distribution Box Plot
- Box plot: Strategy (x-axis) vs Iterations count (y-axis)
- Show median, quartiles, outliers for both strategies
- **Acceptance:** `figures/iteration_distribution.png` created

#### FR-6.5: Backtracking Analysis Histogram (Staged Only)
- Histogram: Number of backtracking events (x-axis) vs Frequency (y-axis)
- Annotate mean backtracking rate
- **Acceptance:** `figures/backtracking_analysis.png` created

#### FR-6.6: Statistical Test Figure
- Paired difference plot: (Staged - Complete) discharge rate per program
- Annotate p-value and effect size
- **Acceptance:** `figures/statistical_test.png` created

### FR-7: Result Documentation
**Priority:** P0 (Critical)

#### FR-7.1: Validation Report
- Generate `04_validation.md` with:
  - Experiment setup
  - Quantitative results (gate metrics, statistical tests)
  - Gate decision (PASS/FAIL/NEUTRAL)
  - All figures embedded
- **Acceptance:** Report exists with complete sections

---

## Non-Functional Requirements

### NFR-1: Performance
- **Benchmark Completion Time:** All 30-50 programs × 2 strategies in ≤24 hours on single GPU
- **Frama-C Timeout:** 10s per proof obligation (inherited from H-E1)
- **LLM API Latency:** ≤30s per generation call (with retries)

### NFR-2: Reproducibility
- **Deterministic Results:** Fixed random seed, temperature=0.0 for LLM
- **Version Control:** Pin Frama-C version (29.0 Copper), LLM model versions
- **Data Provenance:** Log all API calls, verifier outputs, intermediate specs

### NFR-3: Scalability
- **Program Size:** Support C programs 10-200 lines
- **Iteration Budget:** Max 12 iterations (Staged) or 10 iterations (Complete) per program
- **Memory:** ≤16GB RAM for experiment execution

### NFR-4: Maintainability
- **Code Structure:** Separate classes for `StagedRefinementStrategy` and `CompleteRefinementStrategy`
- **Configuration:** YAML config file for hyperparameters (max_iterations, temperature, timeouts)
- **Logging:** Structured logs with DEBUG/INFO/ERROR levels

---

## Success Criteria

### Primary Success Criteria (Gate Metrics)
1. **Convergence Speed:** Staged converges in ≤70% of iterations vs. Complete
2. **Proof Discharge:** Staged achieves ≥5pp higher final discharge rate than Complete
3. **Statistical Significance:** p < 0.05 (paired t-test across programs)

### Secondary Success Criteria
1. All 30-50 programs processed successfully under both strategies
2. All 6 visualization figures generated and saved
3. Statistical analysis report with p-value and effect size
4. `04_validation.md` report complete with gate decision

### Failure Acceptance
- **Neutral Result:** Complete outperforms Staged → Document "backtracking overhead dominates"
- **Gate Impact:** SHOULD_WORK gate - failure does not block Phase 5
- **Phase 5 Behavior:** Proceed without staged optimization claim

---

## Dependencies

### Internal Dependencies
- **H-E1:** Validated LLM iterative refinement mechanism (62.9% discharge rate)
  - Reuse: LLM configuration, verifier setup, baseline Complete strategy
  - Validated: Iterative refinement with structured feedback works

### External Dependencies
- **Frama-C 29.0 (Copper):** Deductive verification tool with WP plugin
- **SMT Solvers:** Alt-Ergo 2.6.2, Z3 4.15.2
- **LLM APIs:** OpenAI GPT-4 or Anthropic Claude Opus
- **Python Libraries:** `openai` or `anthropic`, `subprocess`, `matplotlib`, `scipy` (for t-test)
- **Dataset Repositories:**
  - `fraunhoferfokus/acsl-by-example` (primary benchmark)
  - `Frama-C/open-source-case-studies` (secondary)

### Platform Requirements
- **OS:** Linux (Ubuntu 22.04 or similar)
- **Python:** 3.10 or 3.11
- **GPU:** Optional (LLMs are API-based, no local inference)
- **Disk:** ≥5GB for datasets and intermediate results

---

## Constraints

### Technical Constraints
1. **API Rate Limits:** OpenAI/Anthropic API quotas may limit parallel execution
2. **Frama-C Timeouts:** Complex programs may not fully verify within 10s timeout
3. **LLM Context Length:** Programs >8K tokens may exceed LLM context window

### Budget Constraints
1. **API Costs:** ~30-50 programs × 2 strategies × ~6 iterations × $0.01-0.05 per call = $20-150 estimated
2. **Compute Time:** Single-threaded experiment execution (API calls sequential)

### Scope Constraints
1. **Benchmark Size:** 30-50 programs (not full 100+ suite) for time/cost efficiency
2. **Specification Scope:** ACSL only (no other formal languages)
3. **Verification Tool:** Frama-C WP only (no other verifiers)

---

## Milestones

### Phase 3: Implementation Planning (Current)
- ✓ PRD created
- → Architecture design
- → Logic/Config design
- → Task breakdown

### Phase 4: Implementation & PoC Validation
- Week 1-2: Dataset acquisition and preprocessing
- Week 2-3: Implement StagedRefinementStrategy and CompleteRefinementStrategy
- Week 3-4: Frama-C WP integration and experiment runner
- Week 4-5: Execute experiment on 30-50 programs
- Week 5-6: Statistical analysis and visualization
- Week 6: Gate decision and 04_validation.md report

### Phase 4.5: Hypothesis Synthesis
- Refine hypothesis claim based on PoC results
- Prepare evidence summary for Phase 6

### Phase 6: Paper Writing
- Experimental setup description
- Results presentation with figures
- Discussion: backtracking vs. progressive benefits

---

## Appendix: Reference Implementations

### AutoSpec+ (Xidian-ICTT-GZ/AutoSpec)
- **Relevance:** Iterative refinement loop with Frama-C WP
- **Reused Concepts:** Bottom-up synthesis, targeted repair mechanism
- **Difference:** H-M2 tests Staged vs Complete within-function strategies

### LORIS (ACM TOPLAS)
- **Relevance:** Formalized feedback mechanism (NL proof → FOL → SMT check)
- **Reused Concepts:** Precise error attribution beyond binary pass/fail
- **Difference:** H-M2 uses standard verifier feedback (not FOL translation)

### H-E1 Baseline
- **Relevance:** Validated iterative refinement with structured feedback
- **Reused:** LLM config (temperature=0.0), verifier setup, baseline Complete strategy
- **Results:** 62.9% discharge rate, 5.7 mean iterations, 100% improvement rate

---

**Document Version:** 1.0  
**Last Updated:** 2026-07-11  
**Status:** Ready for Phase 3 Architecture Design
