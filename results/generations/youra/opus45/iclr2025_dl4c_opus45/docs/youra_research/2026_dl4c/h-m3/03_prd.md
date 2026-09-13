# Product Requirements Document: H-M3

**Hypothesis:** LlmFix 19-Cause Fine-Grained Error Taxonomy Analysis
**Date:** 2026-03-24
**Author:** Phase 3 Implementation Planning
**Status:** Draft
**Version:** 1.0

---

## Executive Summary

This PRD defines the implementation requirements for hypothesis H-M3, which tests the MECHANISM that DPO preference optimization without execution feedback concentrates failures in execution errors (syntax/runtime), and this effect persists at fine-grained taxonomy (Cramér's V > 0.03 at LlmFix 19-cause level).

**Core Hypothesis Statement:**
> DPO preference optimization without execution feedback concentrates failures in execution errors (syntax/runtime), and this effect persists at fine-grained taxonomy (Cramér's V > 0.03 at LlmFix 19-cause level)

**Key Insight from H-E1/H-M1/H-M2:**
- H-E1 established error type distributions differ significantly (chi-square p < 0.05, V = 0.2147)
- H-M1 confirmed RL concentrates failures in assertion errors (zero-reward basin mechanism)
- H-M2 confirmed RL failures execute 326x deeper than DPO failures (syntactic validity pressure)
- H-M3 tests whether the **complementary DPO mechanism** (preference surface plausibility → execution errors) persists at fine-grained LlmFix 19-cause taxonomy

**Success Gate:** SHOULD_WORK
- Primary: P(syntax+runtime | failure, DPO) > P(syntax+runtime | failure, RL)
- Secondary: Effect persists at fine-grained taxonomy (Cramér's V > 0.03 at LlmFix 19-cause level)
- Tertiary: Chi-square p < 0.05 at fine-grained level

---

## Problem Statement

### Research Gap
H-E1 through H-M2 demonstrated RL's alignment mechanisms. H-M3 addresses the **complementary mechanism for DPO**: Does DPO's preference optimization without execution feedback concentrate failures in execution errors? And critically: does this pattern persist when examined at fine-grained taxonomy (19 causes vs 3 categories)?

### Mechanism Description
- **DPO Preference Surface Plausibility**: DPO optimizes for surface-level code quality without execution feedback
- **Hypothesis**: Without execution filtering, DPO models generate syntactically-plausible but non-executable code
- **Fine-Grained Taxonomy**: LlmFix 19-cause taxonomy enables deeper analysis than 3-tier (syntax/runtime/assertion)
- **Persistence Test**: Effect size (Cramér's V) should remain significant at finer granularity

### Target Users
- Deep learning researchers studying code generation alignment mechanisms
- Alignment research community investigating preference-based optimization
- Error taxonomy researchers analyzing LLM failure patterns

### Research Value
- Completes the DPO mechanism chain started in H-E1
- Tests robustness of effect across taxonomy granularities
- Validates LlmFix taxonomy applicability to alignment research

---

## Functional Requirements

### FR-1: Data Loading and Preparation

**FR-1.1: Load H-E1 Execution Results**
- Load pre-computed error classifications from H-E1 outputs
- File paths:
  - `../h-e1/code/outputs/experiment_results.json` - Full execution results
  - `../h-e1/code/outputs/metrics.json` - Summary metrics
- Extract all failure cases (RL and DPO)
- Priority: P0 (Critical)

**FR-1.2: Extract Error Traces for Classification**
- Parse experiment_results.json to get error traces and messages
- Separate RL failures and DPO failures
- Expected counts (from H-E1):
  - RL failures: ~236 samples
  - DPO failures: ~530 samples
- Priority: P0 (Critical)

**FR-1.3: Load Problem Context (Optional)**
- Load EvalPlus test cases for context-aware classification
- Use evalplus library: `get_human_eval_plus()`, `get_mbpp_plus()`
- Needed for semantic error classification
- Priority: P1 (Important)

### FR-2: LlmFix 19-Cause Taxonomy Classification

**FR-2.1: Define LlmFix Taxonomy Structure**
- Implement 19-cause taxonomy from arXiv 2409.00676:
  - **Syntax-level (3 causes)**: indentation_error, syntax_error, missing_import
  - **Runtime-level (10 causes)**: name_error, type_error, attribute_error, index_error, key_error, value_error, zero_division, recursion_error, timeout, memory_error
  - **Assertion-level (6 causes)**: wrong_output, partial_output, missing_output, wrong_type, off_by_one, boundary_error
- Priority: P0 (Critical)

**FR-2.2: Coarse Classification (3-Tier)**
- Reuse H-E1 classification logic for syntax/runtime/assertion
- Function signature:
  ```python
  def classify_error_coarse(error_trace: str) -> str:
      """Returns: 'syntax' | 'runtime' | 'assertion'"""
  ```
- Priority: P0 (Critical)

**FR-2.3: Fine-Grained Classification (19-Cause)**
- Implement error message parsing for 19-cause classification
- Function signature:
  ```python
  def classify_error_fine(error_trace: str, coarse_category: str) -> str:
      """Returns one of 19 cause categories"""
  ```
- Parsing rules:
  - SyntaxError message → syntax_error
  - IndentationError → indentation_error
  - ImportError → missing_import
  - NameError → name_error
  - TypeError → type_error
  - AttributeError → attribute_error
  - IndexError → index_error
  - KeyError → key_error
  - ValueError → value_error
  - ZeroDivisionError → zero_division
  - RecursionError → recursion_error
  - Timeout → timeout
  - MemoryError → memory_error
  - AssertionError → analyze output patterns for 6 causes
- Priority: P0 (Critical)

**FR-2.4: Dual-Granularity Classification**
- Classify each failure at BOTH levels
- Function signature:
  ```python
  def classify_error_llmfix(error_trace: str, output: str = None) -> Tuple[str, str]:
      """Returns: (coarse_category, fine_cause)"""
  ```
- Priority: P0 (Critical)

### FR-3: Statistical Analysis

**FR-3.1: Build Contingency Tables**
- 3-tier table: 2x3 (model × {syntax, runtime, assertion})
- 19-cause table: 2x19 (model × 19 causes)
- Handle empty cells (add 0.5 pseudocount if needed)
- Priority: P0 (Critical)

**FR-3.2: Chi-Square Test (Coarse Level)**
- Use `scipy.stats.chi2_contingency(coarse_table)`
- Extract: chi2 statistic, p-value, degrees of freedom
- Compare with H-E1 results (V = 0.2147) for validation
- Priority: P0 (Critical)

**FR-3.3: Chi-Square Test (Fine-Grained Level)**
- Use `scipy.stats.chi2_contingency(fine_table)`
- Extract: chi2 statistic, p-value, degrees of freedom
- Success threshold: p < 0.05
- Priority: P0 (Critical)

**FR-3.4: Cramér's V Calculation**
- Compute at both granularity levels:
  ```python
  def cramers_v(contingency_table: np.ndarray) -> float:
      chi2, p, dof, expected = chi2_contingency(contingency_table)
      n = contingency_table.sum()
      min_dim = min(contingency_table.shape) - 1
      return np.sqrt(chi2 / (n * min_dim))
  ```
- Success threshold (fine-grained): V > 0.03
- Priority: P0 (Critical)

**FR-3.5: Direction Verification**
- Calculate P(syntax+runtime | failure, DPO) and P(syntax+runtime | failure, RL)
- Verify: DPO proportion > RL proportion
- Report proportions and difference
- Priority: P0 (Critical)

**FR-3.6: Descriptive Statistics**
- Error type counts for each model
- Proportions per category
- Most common causes for each model
- Priority: P1 (Important)

### FR-4: Visualization

**FR-4.1: Gate Metrics Comparison (Required)**
- Side-by-side comparison:
  - Cramér's V (coarse 3-tier) vs Cramér's V (fine 19-cause)
  - Target threshold line: V = 0.03
  - p-value indicators
- Save to figures/gate_metrics.png
- Priority: P0 (Critical)

**FR-4.2: Error Distribution Heatmap**
- 2x19 heatmap showing RL vs DPO error cause distribution
- Color intensity: proportion within model
- Annotate with counts
- Save to figures/error_heatmap.png
- Priority: P1 (Important)

**FR-4.3: Cramér's V Persistence Plot**
- Bar/line chart showing V values across granularities
- X-axis: taxonomy level (3-tier, 19-cause)
- Y-axis: Cramér's V
- Threshold line at 0.03
- Save to figures/cramers_v_persistence.png
- Priority: P1 (Important)

**FR-4.4: Error Proportion Bar Chart**
- Grouped bar chart: DPO vs RL proportions by error category
- Show syntax+runtime combined for direction verification
- Save to figures/error_proportions.png
- Priority: P1 (Important)

**FR-4.5: Fine-Grained Category Distribution**
- Stacked bar chart showing 19-cause distribution per model
- Grouped by coarse category (syntax, runtime, assertion)
- Save to figures/finegrained_distribution.png
- Priority: P2 (Nice to have)

### FR-5: Output Generation

**FR-5.1: Metrics JSON**
- Save to outputs/metrics.json:
  ```json
  {
    "coarse": {
      "chi2": float, "p_value": float, "cramers_v": float,
      "dof": int, "contingency_table": [[int]]
    },
    "fine": {
      "chi2": float, "p_value": float, "cramers_v": float,
      "dof": int, "contingency_table": [[int]]
    },
    "direction": {
      "dpo_syntax_runtime_prop": float,
      "rl_syntax_runtime_prop": float,
      "direction_satisfied": bool
    },
    "gate_result": {
      "cramers_v_threshold": 0.03,
      "cramers_v_actual": float,
      "p_value_threshold": 0.05,
      "p_value_actual": float,
      "gate_pass": bool
    }
  }
  ```
- Priority: P0 (Critical)

**FR-5.2: Experiment Results JSON**
- Save full analysis to outputs/experiment_results.json:
  - Per-sample classifications (coarse and fine)
  - Category counts by model
  - Statistical test details
- Priority: P0 (Critical)

**FR-5.3: Classification Data CSV**
- Save to outputs/classification_data.csv
- Columns: sample_id, model, problem_id, coarse_category, fine_cause, error_trace_summary
- Priority: P1 (Important)

---

## Non-Functional Requirements

### NFR-1: Performance
- Analysis should complete within 10 minutes
- No GPU required (classification is string parsing)
- Memory usage under 2 GB

### NFR-2: Reproducibility
- Load exact H-E1 results (no re-computation)
- Deterministic classification logic
- Fixed random seed: 42 (if any sampling)
- All intermediate values logged

### NFR-3: Code Quality
- Type hints for all functions
- Docstrings for public APIs
- Error handling for:
  - Missing H-E1 data
  - Unrecognized error patterns
  - Empty contingency cells
- Comprehensive logging

### NFR-4: Robustness
- Handle malformed error traces gracefully
- Default to "unknown" category for unrecognized patterns
- Log classification failures without crashing

---

## Success Criteria

### Primary Success Criteria (SHOULD_WORK Gate)

| Metric | Target | Interpretation |
|--------|--------|----------------|
| Cramér's V (19-cause) | > 0.03 | Effect persists at fine-grained taxonomy |
| Chi-square p-value (19-cause) | < 0.05 | Statistically significant difference |
| Direction | P(syntax+runtime\|DPO) > P(syntax+runtime\|RL) | DPO concentrates in execution errors |

### Secondary Success Criteria
- Cramér's V (3-tier) similar to H-E1 result (~0.21) - validates methodology
- Successful classification for >95% of failure samples
- No category with zero samples (taxonomy coverage)

### Failure Handling (SHOULD_WORK Gate)
- Cramér's V < 0.03 → Effect does not persist → Document limitation, complete verification
- p >= 0.05 → Not statistically significant → Document, complete verification
- Direction reversed → DPO mechanism not supported → Document, continue to synthesis
- >5% classification failures → Log quality issues but proceed

### Expected Outcome
Based on H-E1 results (V = 0.2147 at 3-tier):
- Cramér's V at 19-cause should be smaller but still significant
- Expected range: 0.05-0.15 (effect dilutes with more categories)
- Effect persistence (V > 0.03) validates mechanism robustness

---

## Dependencies

### External Dependencies
- **scipy**: Chi-square test (`scipy.stats.chi2_contingency`)
- **numpy**: Array operations, statistics
- **matplotlib/seaborn**: Visualization
- **pandas**: Data manipulation

### Internal Dependencies
- **H-E1 Outputs (REQUIRED)**:
  - `h-e1/code/outputs/experiment_results.json` (error traces)
  - `h-e1/code/outputs/metrics.json` (sample counts)
- **H-M1/H-M2 Context**:
  - Zero-reward basin mechanism (theoretical foundation)
  - Execution depth analysis (complementary evidence)
- **Phase 2C**: `h-m3/02c_experiment_brief.md`

### Reference Implementations
- LlmFix paper (arXiv 2409.00676) - 19-cause taxonomy definition
- H-E1 analyze.py - Base classification logic
- scipy.stats documentation - Chi-square, Cramér's V

---

## Data Specifications

### Input Data (Reused from H-E1)
| Data | Source | Format |
|------|--------|--------|
| RL Error Traces | h-e1/code/outputs/ | JSON (error strings) |
| DPO Error Traces | h-e1/code/outputs/ | JSON (error strings) |
| Coarse Classifications | h-e1/code/outputs/ | JSON (if available) |

### Output Data
| Data | Location | Format |
|------|----------|--------|
| Metrics | outputs/metrics.json | JSON (statistics, p-values, V) |
| Experiment Results | outputs/experiment_results.json | JSON (full analysis) |
| Classification Data | outputs/classification_data.csv | CSV (per-sample) |
| Figures | figures/ | PNG images |

---

## Risk Assessment

### Technical Risks
- **R1**: Some error messages may not map cleanly to 19 causes
  - Mitigation: Default to closest category, log unmapped patterns
- **R2**: Sparse contingency table (cells with zero counts)
  - Mitigation: Add pseudocount (0.5), use Fisher's exact if needed
- **R3**: LlmFix taxonomy not perfectly applicable to our models
  - Mitigation: Document mapping decisions, fallback to 3-tier

### Research Risks
- **R4**: Effect may be too small at 19-cause level (V < 0.03)
  - Mitigation: SHOULD_WORK gate allows documenting limitations
- **R5**: Taxonomy granularity may introduce noise
  - Mitigation: Report both levels, interpret conservatively

---

## Task Budget

### Tier: FULL (MECHANISM Hypothesis)
- Maximum tasks: 30
- Epic range: 6-12
- Infrastructure: Standard

### Expected Task Distribution
| Category | Count |
|----------|-------|
| Data Preparation | 1 (load H-E1) |
| Environment Setup | 1 |
| Epic Tasks | 7-9 |
| Subtasks | 4-6 |
| Failsafe | 1 |
| **Total** | ~15-18 |

---

## Phase Sequence

1. **Phase 2C**: Experiment Design ✓ (completed)
2. **Phase 3**: Implementation Planning (current) - PRD, Architecture, Logic, Config
3. **Phase 4**: Coding & PoC Validation - LlmFix taxonomy analysis
4. **Phase 4.5**: Synthesis - Evidence integration with H-E1/H-M1/H-M2
5. **Phase 6**: Paper Writing - Academic publication

---

*Generated by Phase 3 PRD Workflow | Anonymous Research Pipeline*
*Input: h-m3/02c_experiment_brief.md*
*Gate: SHOULD_WORK | Type: MECHANISM*
*Prerequisite: H-M2 (COMPLETED - PASS)*
