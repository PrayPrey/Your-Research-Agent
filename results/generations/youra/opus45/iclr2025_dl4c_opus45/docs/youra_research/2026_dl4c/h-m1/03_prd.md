# Product Requirements Document: H-M1

**Hypothesis:** Zero-Reward Basin Mechanism in RL Code Generation
**Date:** 2026-03-24
**Author:** Phase 3 Implementation Planning
**Status:** Draft
**Version:** 1.0

---

## Executive Summary

This PRD defines the implementation requirements for hypothesis H-M1, which tests the MECHANISM behind the error type divergence observed in H-E1. Specifically, H-M1 investigates whether RL's binary execution reward creates a "flat zero-reward basin" over all non-executable programs, concentrating RL failures in assertion errors (code that runs but produces wrong output).

**Core Hypothesis Statement:**
> RL binary execution reward creates flat zero-reward basin over all non-executable programs, concentrating RL failures in assertion errors (code runs but wrong output)

**Key Insight from H-E1:**
- RL assertion proportion: 2.1% (5/235 failures)
- DPO assertion proportion: 0.0% (0/530 failures)
- H-M1 tests if this difference is statistically significant with one-sided Fisher's exact test

**Success Gate:** MUST_WORK
- Primary: Fisher's exact test p-value < 0.05 (one-sided)
- Secondary: P(assertion | failure, RL) > P(assertion | failure, DPO) (direction)

---

## Problem Statement

### Research Gap
H-E1 established that RL-aligned and DPO-aligned code generation models produce systematically different error type distributions. H-M1 tests the **causal mechanism**: that RL's binary execution reward creates a zero-reward basin where all non-executable programs receive identical zero reward, creating optimization pressure to first achieve execution before optimizing semantics.

### Mechanism Description
- **Binary Reward Structure**: CodeRL uses unit test pass/fail as binary reward signal
- **Zero-Reward Basin**: All execution failures (syntax, runtime) receive ZERO reward
- **Optimization Pressure**: Model learns to first escape the zero-reward basin (achieve execution)
- **Concentration Effect**: RL failures concentrate in assertion errors (code runs but wrong output)

### Target Users
- Deep learning researchers studying code generation alignment mechanisms
- Alignment research community investigating RL reward topology effects
- Error analysis practitioners studying causal mechanisms

### Research Value
- Tests specific causal mechanism behind H-E1's existence finding
- Validates reward topology theory in code generation
- Provides foundation for subsequent mechanism hypotheses (H-M2, H-M3)

---

## Functional Requirements

### FR-1: Data Reuse from H-E1

**FR-1.1: Load H-E1 Execution Results**
- Load pre-computed error classifications from H-E1 outputs
- File paths:
  - `../h-e1/code/outputs/experiment_results.json` - Full execution results
  - `../h-e1/code/outputs/metrics.json` - Summary metrics with error counts
- Verify file existence and data integrity
- Priority: P0 (Critical)

**FR-1.2: Extract Error Classifications**
- Parse execution results to extract error types per model
- Error categories: syntax, runtime, assertion, pass
- Count failures only (exclude passes) for proportion analysis
- Priority: P0 (Critical)

**FR-1.3: Validate Data Consistency**
- Verify expected sample counts match H-E1 validation report:
  - RL failures: ~235 (out of 542 problems)
  - DPO failures: ~530 (out of 542 problems)
- If data inconsistent, log warning and proceed with available data
- Priority: P1 (Important)

### FR-2: Statistical Analysis

**FR-2.1: Assertion Proportion Calculation**
- Compute P(assertion | failure) for each model:
  - `rl_assertion_prop = rl_assertion_count / rl_total_failures`
  - `dpo_assertion_prop = dpo_assertion_count / dpo_total_failures`
- Handle zero denominators gracefully
- Priority: P0 (Critical)

**FR-2.2: Contingency Table Construction**
- Build 2×2 contingency table:
  - Rows: Model (RL, DPO)
  - Columns: Error category (assertion, non-assertion)
- Cell values: Count of failures
- Priority: P0 (Critical)

**FR-2.3: Fisher's Exact Test (One-Sided)**
- Use `scipy.stats.fisher_exact` with `alternative='greater'`
- Hypothesis: P(assertion | failure, RL) > P(assertion | failure, DPO)
- Report odds ratio and p-value
- Success threshold: p < 0.05
- Priority: P0 (Critical)

**FR-2.4: Effect Size Calculation**
- Calculate odds ratio from Fisher's exact test
- Report 95% confidence interval if available
- Document effect magnitude interpretation
- Priority: P1 (Important)

### FR-3: Mechanism Documentation

**FR-3.1: Reward Topology Analysis**
- Document CodeRL's binary reward structure from official paper
- Explain zero-reward basin concept
- Link mechanism to observed assertion concentration
- Priority: P1 (Important)

**FR-3.2: Causal Chain Documentation**
- Step 1: Binary pass/fail reward signal
- Step 2: Zero reward for ALL non-passing programs
- Step 3: Optimization pressure to achieve execution first
- Step 4: Assertion errors (code runs, wrong output) as escape from basin
- Priority: P1 (Important)

### FR-4: Visualization

**FR-4.1: Gate Metrics Comparison (Required)**
- Bar chart showing target vs actual metrics
- Target: p-value = 0.05
- Actual: Computed Fisher's exact p-value
- Save to figures/gate_metrics.png
- Priority: P0 (Critical)

**FR-4.2: Assertion Proportion Comparison**
- Bar chart comparing P(assertion | failure) for RL vs DPO
- Include error bars if bootstrap CI available
- Save to figures/assertion_proportion.png
- Priority: P1 (Important)

**FR-4.3: Error Type Distribution**
- Stacked bar chart showing full error breakdown (syntax/runtime/assertion)
- Grouped by model (RL vs DPO)
- Highlights assertion concentration in RL
- Save to figures/error_distribution.png
- Priority: P1 (Important)

**FR-4.4: Contingency Table Heatmap**
- Heatmap of 2×2 Fisher's exact test table
- Cell values: Count
- Color scale showing relative magnitudes
- Save to figures/contingency_table.png
- Priority: P2 (Nice to have)

**FR-4.5: Reward Topology Diagram (Conceptual)**
- Visualization of binary reward structure
- Shows zero-reward basin over non-executable programs
- Optional: LLM-generated conceptual diagram
- Save to figures/reward_topology.png
- Priority: P2 (Nice to have)

### FR-5: Output Generation

**FR-5.1: Metrics JSON**
- Save all computed metrics to outputs/metrics.json:
  - rl_assertion_count, rl_total_failures, rl_assertion_prop
  - dpo_assertion_count, dpo_total_failures, dpo_assertion_prop
  - odds_ratio, p_value, gate_pass
- Priority: P0 (Critical)

**FR-5.2: Experiment Results JSON**
- Save full analysis results to outputs/experiment_results.json
- Include contingency table, proportions, test statistics
- Priority: P0 (Critical)

**FR-5.3: Summary Report**
- Generate human-readable summary of mechanism analysis
- Include key findings and interpretation
- Priority: P1 (Important)

---

## Non-Functional Requirements

### NFR-1: Performance
- Analysis should complete within 1 minute (pure statistical computation)
- No GPU required
- Memory usage under 1 GB

### NFR-2: Reproducibility
- Load exact H-E1 results (no re-computation)
- Fixed random seed if any sampling involved
- All intermediate values logged

### NFR-3: Code Quality
- Type hints for all functions
- Docstrings for public APIs
- Error handling for missing/corrupt H-E1 data
- Logging for analysis steps

### NFR-4: Data Integrity
- Verify H-E1 data files exist before analysis
- Validate data format and expected fields
- Report any data quality issues

---

## Success Criteria

### Primary Success Criteria (MUST_WORK Gate)

| Metric | Target | Interpretation |
|--------|--------|----------------|
| Fisher's exact p-value (one-sided) | < 0.05 | RL assertion proportion significantly greater than DPO |
| Direction | P(assertion\|failure, RL) > P(assertion\|failure, DPO) | Matches mechanism prediction |

### Secondary Success Criteria
- H-E1 data successfully loaded and validated
- Non-zero assertion count for RL model (mechanism activation indicator)
- Clear documentation of reward topology mechanism

### Failure Criteria
- Fisher's exact p >= 0.05 → Not statistically significant → MUST_WORK gate FAIL
- RL assertion count = 0 → Mechanism not active → MUST_WORK gate FAIL
- H-E1 data files missing/corrupt → Cannot proceed → ERROR

### Expected Outcome (from H-E1 results)
- RL assertion proportion: ~2.1% (5/235)
- DPO assertion proportion: ~0.0% (0/530)
- Expected: PASS (direction clearly consistent, Fisher's test for formal significance)

---

## Dependencies

### External Dependencies
- **scipy**: Fisher's exact test (`pip install scipy`)
- **numpy**: Array operations
- **matplotlib/seaborn**: Visualization
- **json**: Data loading/saving

### Internal Dependencies
- **H-E1 Outputs (REQUIRED)**:
  - `h-e1/code/outputs/experiment_results.json`
  - `h-e1/code/outputs/metrics.json`
- Phase 2C experiment brief: `h-m1/02c_experiment_brief.md`
- verification_state.yaml for status tracking

### Reference Implementations
- salesforce/CodeRL (558 stars) - Binary reward documentation
- scipy.stats.fisher_exact - Statistical test API
- H-E1 validation report - Error classification counts

---

## Data Specifications

### Input Data (Reused from H-E1)
| Data | Source | Format |
|------|--------|--------|
| RL Execution Results | h-e1/code/outputs/ | JSON (error classifications) |
| DPO Execution Results | h-e1/code/outputs/ | JSON (error classifications) |
| H-E1 Metrics | h-e1/code/outputs/metrics.json | JSON summary |

### Output Data
| Data | Location | Format |
|------|----------|--------|
| Metrics | outputs/metrics.json | JSON (p-value, odds_ratio, proportions) |
| Experiment Results | outputs/experiment_results.json | JSON (full analysis) |
| Contingency Table | outputs/contingency_table.csv | CSV |
| Figures | figures/ | PNG images |

---

## Risk Assessment

### Technical Risks
- **R1**: H-E1 output files may be missing or corrupted
  - Mitigation: Validate file existence and format before analysis
  - Fallback: Re-run H-E1 if needed (documented in 02c_experiment_brief.md)
- **R2**: Zero DPO assertion count may cause division issues
  - Mitigation: Handle zero denominators, use Fisher's exact (handles zeros gracefully)

### Research Risks
- **R3**: Effect may exist but not reach significance with small assertion counts
  - Mitigation: Fisher's exact is appropriate for small expected frequencies
- **R4**: One-sided test may be questioned
  - Mitigation: Document hypothesis-driven direction from reward topology theory

---

## Task Budget

### Tier: FULL (MECHANISM Hypothesis)
- Maximum tasks: 30
- Epic range: 6-12
- Infrastructure: Standard

### Expected Task Distribution
| Category | Count |
|----------|-------|
| Data Preparation | 1 (load H-E1 results) |
| Environment Setup | 1 |
| Epic Tasks | 6-8 |
| Subtasks | 4-6 |
| Failsafe | 1 |
| **Total** | 13-17 |

---

## Phase Sequence

1. **Phase 2C**: Experiment Design ✓ (completed)
2. **Phase 3**: Implementation Planning (current) - PRD, Architecture, Logic, Config
3. **Phase 4**: Coding & PoC Validation - Statistical analysis, mechanism documentation
4. **Phase 4.5**: Synthesis - Evidence integration
5. **Phase 6**: Paper Writing - Academic publication

---

*Generated by Phase 3 PRD Workflow | Anonymous Research Pipeline*
*Input: h-m1/02c_experiment_brief.md*
*Gate: MUST_WORK | Type: MECHANISM*
*Base Hypothesis: H-E1 (COMPLETED - PASS)*
