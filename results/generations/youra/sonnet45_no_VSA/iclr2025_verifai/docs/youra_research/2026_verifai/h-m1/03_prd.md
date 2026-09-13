# Product Requirements Document: H-M1 Information Gradient Validation

**Hypothesis ID:** h-m1  
**Type:** MECHANISM  
**Date:** 2026-07-11  
**Author:** Anonymous  
**Status:** Phase 3 - Implementation Planning

---

## Executive Summary

This PRD specifies the implementation requirements for validating the **Information Gradient Hypothesis**: that proof discharge rate scales monotonically with feedback richness across four conditions (FullStructured > ObligationSlice > TagOnly > RawError by ≥10pp between adjacent conditions).

The system will implement an ablation study controlling all variables except feedback richness, measuring proof discharge rates across 30-50 verified C programs from the ACSL-by-Example benchmark using Frama-C verification.

**Gate Type:** MUST_WORK (Core mechanism claim - if no gradient exists, theoretical framing is invalid)

---

## Problem Statement

### Context

H-E1 (prerequisite) validated that LLMs can utilize structured verifier feedback for iterative specification refinement, achieving 62.9% mean discharge rate. However, it remains unknown whether feedback structure matters - whether an information gradient exists where richer feedback produces measurably better results.

### Research Question

Does proof discharge rate scale monotonically with feedback information content? Specifically, does FullStructured feedback (all 3 dimensions) outperform ObligationSlice (2 dimensions), which outperforms TagOnly (1 dimension), which outperforms RawError (unstructured), with adjacent gaps ≥10 percentage points?

### Success Criteria

1. **Monotonic Ordering:** FullStructured > ObligationSlice > TagOnly > RawError (strict inequality)
2. **Adjacent Gaps:** Each condition outperforms next by ≥10pp
3. **Statistical Significance:** Regression coefficient > 0, p < 0.05

### Failure Conditions

- Non-monotonic ordering (e.g., ObligationSlice > FullStructured)
- Adjacent gaps ≤5 percentage points
- No significant regression relationship

---

## Functional Requirements

### FR-1: Benchmark Dataset Management

**Priority:** P0 (Critical)

**Description:** Load and preprocess ACSL-by-Example benchmark programs for blind specification synthesis.

**Requirements:**
- FR-1.1: Clone ACSL-by-Example repository (https://github.com/fraunhoferfokus/acsl-by-example)
- FR-1.2: Select 30-50 programs from StandardAlgorithms/ directory matching criteria:
  - Program size: 10-100 lines of C code
  - Proof obligations: 5-20 per program
  - Coverage: Diverse algorithmic patterns (loops, arrays, conditionals)
- FR-1.3: Strip existing ACSL annotations from selected programs (blind synthesis)
- FR-1.4: Store gold standard annotations separately for evaluation
- FR-1.5: Validate each program has verifiable proof obligations via Frama-C

**Input:** Git repository URL  
**Output:** Dataset of stripped C programs + gold annotations  
**Dependencies:** None

---

### FR-2: Frama-C Verification Integration

**Priority:** P0 (Critical)

**Description:** Integrate Frama-C/WP verification tool for proof obligation discharge measurement.

**Requirements:**
- FR-2.1: Install Frama-C 32.0 (Germanium) + WP plugin
- FR-2.2: Configure proof backends: Alt-Ergo 2.6.2, Z3 4.15.2, CVC5 1.3.3
- FR-2.3: Set proof timeout: 10 seconds per obligation
- FR-2.4: Parse Frama-C output to extract:
  - Total proof obligations count
  - Discharged obligations count
  - Failed obligation details (for feedback extraction)
  - Witness information (counterexamples)
  - Obligation dependency structure
- FR-2.5: Compute discharge rate: (discharged / total) × 100

**Input:** C program + ACSL annotations  
**Output:** Verification result with discharge rate and structured feedback  
**Dependencies:** External tool installation

---

### FR-3: LLM Integration for Specification Synthesis

**Priority:** P0 (Critical)

**Description:** Integrate LLM API (GPT-4 or Claude Opus) for ACSL annotation generation.

**Requirements:**
- FR-3.1: Configure LLM API client (OpenAI or Anthropic)
- FR-3.2: Set generation parameters:
  - Temperature: 0.7
  - Max tokens: 2048
  - Top-p: 0.95
- FR-3.3: Format prompts with:
  - System: "You are a formal verification expert. Generate ACSL annotations for C programs."
  - User: [C code] + [Feedback from previous iteration]
- FR-3.4: Parse LLM output to extract ACSL annotations
- FR-3.5: Handle API errors with retry logic (max 3 retries)
- FR-3.6: Track token usage for compute budget fairness

**Input:** C program + structured feedback  
**Output:** ACSL annotation candidates  
**Dependencies:** OpenAI or Anthropic API access

---

### FR-4: Feedback Condition Ablation (Core Mechanism)

**Priority:** P0 (Critical)

**Description:** Implement 4 feedback richness conditions controlling information content.

**Requirements:**
- FR-4.1: **FullStructured (Condition C):** Extract all 3 dimensions
  - Witness: Counterexample values causing proof failures
  - Structure: Obligation categories and proof goal structure
  - Dependency: Inter-obligation dependency relationships
- FR-4.2: **ObligationSlice (Condition B):** Extract Structure + Dependency only
  - Obligation categories and proof goals
  - Dependency relationships
  - NO witness information
- FR-4.3: **TagOnly (Condition A):** Extract Structure only
  - Obligation categories (error tags)
  - NO witness or dependency information
- FR-4.4: **RawError (Baseline):** Provide unstructured Frama-C output
  - Raw verifier console output
  - No structured extraction

**Input:** Frama-C verification result  
**Output:** Condition-specific feedback payload  
**Dependencies:** FR-2 (verification result parsing)

---

### FR-5: Iterative Refinement Loop

**Priority:** P0 (Critical)

**Description:** Implement iterative LLM-verifier refinement loop for each program × condition combination.

**Requirements:**
- FR-5.1: Initialize with empty specification
- FR-5.2: Loop until convergence or max iterations (10):
  1. Combine C code + current specification
  2. Run Frama-C/WP verification
  3. Check if all obligations discharged → terminate with success
  4. Extract feedback based on condition (FR-4)
  5. Generate refined specification via LLM (FR-3)
  6. Track iteration count
- FR-5.3: Record final discharge rate after max iterations if not converged
- FR-5.4: Store per-iteration metrics: discharge rate, obligations discharged/total
- FR-5.5: Track total compute budget: LLM tokens + verifier time

**Input:** (Program, Feedback Condition) pair  
**Output:** Final discharge rate, iteration count, compute budget  
**Dependencies:** FR-2, FR-3, FR-4

---

### FR-6: Ablation Experiment Execution

**Priority:** P0 (Critical)

**Description:** Execute controlled ablation study across all program × condition combinations.

**Requirements:**
- FR-6.1: For each program in benchmark (30-50):
  - For each feedback condition (4):
    - Run iterative refinement loop (FR-5)
    - Record: discharge_rate, iterations, feedback_condition, compute_budget
- FR-6.2: Control variables:
  - Same LLM model across all experiments
  - Same random seed for LLM sampling
  - Same compute budget cap per program
  - Same verifier configuration
- FR-6.3: Store per-trial results: (program_id, condition, discharge_rate, iterations, tokens, verifier_time)
- FR-6.4: Aggregate statistics per condition: mean, std, min, max discharge rates
- FR-6.5: Save intermediate results every 10 trials (crash recovery)

**Input:** Benchmark dataset, 4 feedback conditions  
**Output:** Results table (120-200 trials = 30-50 programs × 4 conditions)  
**Dependencies:** FR-1, FR-5

---

### FR-7: Statistical Analysis and Validation

**Priority:** P0 (Critical)

**Description:** Analyze results to test information gradient hypothesis.

**Requirements:**
- FR-7.1: **Monotonic Ordering Test:**
  - Compute mean discharge rate per condition: μ_Full, μ_Obl, μ_Tag, μ_Raw
  - Check: μ_Full > μ_Obl > μ_Tag > μ_Raw (strict inequality)
  - Report: PASS if all inequalities hold, FAIL otherwise
- FR-7.2: **Adjacent Gap Test:**
  - Compute gaps: Δ1 = μ_Full - μ_Obl, Δ2 = μ_Obl - μ_Tag, Δ3 = μ_Tag - μ_Raw
  - Check: all Δi ≥ 10 percentage points
  - Report: PASS if all gaps ≥10pp, WARN if 5pp ≤ gaps < 10pp, FAIL if any gap < 5pp
- FR-7.3: **Regression Analysis:**
  - Independent variable: Feedback richness (ordinal: 1=Raw, 2=Tag, 3=Obl, 4=Full)
  - Dependent variable: Proof discharge rate
  - Fit: Linear regression with monotonic constraint
  - Test: Coefficient β > 0, p-value < 0.05
  - Report: β, p-value, R²
- FR-7.4: **Compute Budget Fairness Check:**
  - Compare mean tokens and verifier time across conditions
  - Flag: If any condition uses >20% more compute than others
- FR-7.5: **Gate Decision:**
  - SATISFIED: All 3 tests pass (ordering + gaps + regression)
  - FAILED: Any test fails
  - Write result to verification_state.yaml

**Input:** Results table from FR-6  
**Output:** Statistical report + gate decision  
**Dependencies:** FR-6

---

### FR-8: Visualization Generation

**Priority:** P1 (High)

**Description:** Generate publication-quality figures for results.

**Requirements:**
- FR-8.1: **Monotonic Ordering Plot:**
  - Line plot: X-axis = Feedback condition (Raw, Tag, Obl, Full)
  - Y-axis = Mean discharge rate (%) with 95% confidence intervals
  - Show individual program results as scatter overlay
- FR-8.2: **Per-Program Heatmap:**
  - Rows: Programs (30-50)
  - Columns: Conditions (4)
  - Color: Discharge rate (0-100%)
  - Annotations: Show gaps visually
- FR-8.3: **Regression Plot:**
  - X-axis: Feedback richness (ordinal 1-4)
  - Y-axis: Discharge rate (%)
  - Points: All trials (120-200)
  - Line: Fitted regression with confidence bands
  - Annotation: β, p-value, R²
- FR-8.4: **Compute Budget Analysis:**
  - Scatter: Discharge rate vs. total compute (tokens + verifier time)
  - Color by condition
  - Check: No condition systematically uses more compute
- FR-8.5: Save all figures to `{hypothesis_folder}/figures/`

**Input:** Results table, statistical analysis  
**Output:** 4+ publication-ready figures  
**Dependencies:** FR-6, FR-7

---

### FR-9: Results Documentation

**Priority:** P1 (High)

**Description:** Generate comprehensive validation report.

**Requirements:**
- FR-9.1: Document structure:
  - Experiment configuration (dataset, models, conditions)
  - Per-condition statistics (mean, std, min, max)
  - Monotonic ordering test results
  - Adjacent gap test results
  - Regression analysis results
  - Compute budget fairness check
  - Gate decision with reasoning
- FR-9.2: Include all figures from FR-8
- FR-9.3: Save as `{hypothesis_folder}/04_validation.md`
- FR-9.4: Update verification_state.yaml:
  - `validation.status = "COMPLETED"`
  - `gate.satisfied = true/false`
  - `validation.result = {statistics}`

**Input:** All experimental results and analyses  
**Output:** 04_validation.md + updated verification_state.yaml  
**Dependencies:** FR-6, FR-7, FR-8

---

## Non-Functional Requirements

### NFR-1: Reproducibility

- **NFR-1.1:** Fix all random seeds (LLM sampling, program selection)
- **NFR-1.2:** Log all configuration parameters (model version, verifier version, timeouts)
- **NFR-1.3:** Save raw verifier outputs for manual inspection
- **NFR-1.4:** Version control all code and configuration

### NFR-2: Robustness

- **NFR-2.1:** Handle LLM API failures with exponential backoff (max 3 retries)
- **NFR-2.2:** Handle Frama-C crashes gracefully (log and continue to next trial)
- **NFR-2.3:** Checkpoint intermediate results every 10 trials
- **NFR-2.4:** Resume from checkpoint on script restart

### NFR-3: Performance

- **NFR-3.1:** Target runtime: 4-8 hours for full ablation (30-50 programs × 4 conditions × up to 10 iterations)
- **NFR-3.2:** Parallelize across programs (not conditions - conditions must be sequential per program)
- **NFR-3.3:** Cache verifier results for identical (code + spec) pairs

### NFR-4: Maintainability

- **NFR-4.1:** Modular code structure: dataset loader, verifier wrapper, LLM client, refinement loop, analysis
- **NFR-4.2:** Comprehensive logging (DEBUG level for development, INFO for production)
- **NFR-4.3:** Configuration file for all parameters (avoid hardcoding)

---

## Dependencies

### Prerequisite Hypotheses

- **H-E1 (VALIDATED):** LLM + Structured Feedback Refinement
  - Reuse: Same domain (Frama-C verification), same LLM candidates
  - Build on: H-E1 established 62.9% baseline with FullStructured feedback
  - Difference: H-M1 tests mechanism via ablation, H-E1 tested existence

### External Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Frama-C | 32.0 (Germanium) | Verification engine |
| Frama-C WP Plugin | Latest with 32.0 | Weakest precondition calculus |
| Alt-Ergo | 2.6.2 | SMT solver backend |
| Z3 | 4.15.2 | SMT solver backend |
| CVC5 | 1.3.3 | SMT solver backend |
| Why3 | 1.8.2 | Proof infrastructure |

### APIs

| Provider | Model | Purpose |
|----------|-------|---------|
| OpenAI (primary) | GPT-4 | ACSL specification generation |
| Anthropic (fallback) | Claude Opus | ACSL specification generation |

### Datasets

| Dataset | Source | Scale |
|---------|--------|-------|
| ACSL-by-Example | https://github.com/fraunhoferfokus/acsl-by-example | 126 verified programs (use 30-50 subset) |

---

## Success Criteria

### Phase 4 PoC Success (MUST_WORK Gate)

**Condition 1: Code runs without error**
- All FR-1 through FR-9 components execute successfully
- No crashes on benchmark programs
- Valid output files generated

**Condition 2: Proposed metric > Baseline metric**
- Mean discharge rate FullStructured > RawError
- Gap ≥ 10 percentage points
- Demonstrates information gradient exists

### Final Gate Success (Hypothesis Validation)

**All 3 tests pass:**
1. Monotonic ordering: FullStructured > ObligationSlice > TagOnly > RawError
2. Adjacent gaps: All ≥10pp
3. Regression: β > 0, p < 0.05

**Failure triggers:**
- Non-monotonic ordering
- Any gap <5pp
- Non-significant regression

---

## Out of Scope

- Training new LLM models (inference-only experiment)
- Modifying Frama-C verifier internals
- Human-in-the-loop specification refinement
- Multi-model comparison (GPT-4 vs Claude) - use one model only
- Adaptive feedback selection (all 4 conditions predetermined)

---

## Technical Constraints

- **Compute Budget:** Track but do not hard-cap (fairness check only)
- **Time Budget:** 10-iteration cap per program × condition
- **Proof Timeout:** 10 seconds per obligation (Frama-C/WP setting)
- **LLM Token Limit:** 2048 tokens per generation (sufficient for ACSL)
- **Random Seed:** Fixed seed=42 for all LLM sampling

---

## Appendix: Reference Implementations

### A. LORIS (ltcRandomwalk/LORIS)
- **URL:** https://github.com/ltcRandomwalk/LORIS
- **Relevance:** Loop invariant synthesis with Frama-C 27.1
- **Reuse:** Feedback extraction patterns, Frama-C integration

### B. AutoSpec (Xidian-ICTT-GZ/AutoSpec)
- **URL:** https://github.com/Xidian-ICTT-GZ/AutoSpec
- **Relevance:** Iterative repair with verifier feedback
- **Reuse:** Refinement loop structure

### C. Forge Ablation (wrwei/Forge)
- **URL:** https://github.com/wrwei/Forge/tree/main/experiments/convergence/ablation
- **Relevance:** Ablation methodology for verifier feedback
- **Reuse:** Experimental design (control all variables except feedback)

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2026-07-11 | 1.0 | Initial PRD for H-M1 implementation |

---

**Approval:** Ready for Phase 3 Architecture Design

**Next Steps:**
1. Architecture Agent: Design system components and Epic-level task breakdown
2. Logic Agent: Specify API signatures, tensor shapes, algorithmic pseudo-code
3. Configuration Agent: Define hyperparameters, YAML schemas, dataclasses
