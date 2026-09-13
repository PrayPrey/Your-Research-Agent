# Product Requirements Document: H-E1

**Hypothesis:** Alignment-Induced Error Type Divergence in Code Generation
**Date:** 2026-03-24
**Author:** Phase 3 Implementation Planning
**Status:** Draft
**Version:** 1.0

---

## Executive Summary

This PRD defines the implementation requirements for hypothesis H-E1, which tests whether RL-aligned and DPO-aligned code generation models produce systematically different error type distributions among failed generations. The experiment compares CodeRL-770M (execution-based RL) vs CodeLlama-7B-DPO (preference-based DPO) on HumanEval+ and MBPP+ (542 problems total) using chi-square statistical testing.

**Core Hypothesis Statement:**
> Under code generation on HumanEval+/MBPP+, if a model is aligned with RL (binary execution reward) vs DPO (pairwise preference), then P(syntax+runtime | failure, RL) < P(syntax+runtime | failure, DPO), because RL's zero-reward basin creates pressure toward syntactic validity first.

**Success Gate:** MUST_WORK
- Primary: Chi-square test p-value < 0.05
- Secondary: Cramér's V > 0.05 (small-medium effect size)
- Tertiary: Effect direction matches prediction (RL lower syntax+runtime proportion)

---

## Problem Statement

### Research Gap
The previous gradient-based h-e1 hypothesis (layer-wise cosine similarity divergence) FAILED because RL and DPO gradients are anti-correlated across ALL transformer layers, not structured divergence. This pivoted approach tests whether the anti-correlated optimization pressures manifest as different ERROR TYPE distributions at the behavioral output level.

### Target Users
- Deep learning researchers studying code generation alignment
- Error analysis practitioners
- Alignment research community investigating RL vs DPO effects

### Research Value
- Tests whether different alignment objectives produce behaviorally observable differences
- Provides foundation for mechanism hypotheses (H-M1, H-M2, H-M3)
- Validates error taxonomy applicability to alignment analysis

---

## Functional Requirements

### FR-1: Dataset Management

**FR-1.1: HumanEval+ Dataset Loading**
- Install evalplus library: `pip install evalplus`
- Load 164 Python programming problems with 80x more tests than original
- Use `evalplus.data.get_human_eval_plus()` API
- Cache dataset locally for reproducibility
- Priority: P0 (Critical)

**FR-1.2: MBPP+ Dataset Loading**
- Load 378 Python programming problems with 35x more tests than original
- Use `evalplus.data.get_mbpp_plus()` API
- Verify problem format compatibility with HumanEval+
- Priority: P0 (Critical)

**FR-1.3: Combined Dataset Preparation**
- Merge HumanEval+ (164) + MBPP+ (378) = 542 problems total
- Store in uniform format: {task_id, prompt, test, entry_point}
- Generate unique task IDs for combined dataset
- Priority: P0 (Critical)

### FR-2: Model Management

**FR-2.1: CodeRL-770M Loading (RL-aligned)**
- Load `Salesforce/codet5-large-ntp-py` from HuggingFace
- Use T5ForConditionalGeneration architecture (770M parameters)
- This is the RL-aligned model with execution-based binary reward
- Verify model loads correctly with test inference
- Priority: P0 (Critical)

**FR-2.2: CodeLlama-7B-DPO Loading (DPO-aligned)**
- Load `codellama/CodeLlama-7b-Instruct-hf` from HuggingFace
- Use AutoModelForCausalLM architecture (7B parameters)
- This is the DPO-aligned model with preference-based training
- May require DPO adapter if using fine-tuned version
- Priority: P0 (Critical)

**FR-2.3: Generation Configuration**
- Temperature: 0.8
- Samples per problem: 10 (n=10)
- Max new tokens: 512
- Top-p (nucleus): 0.95
- Random seed: 42 (fixed for reproducibility)
- Priority: P0 (Critical)

### FR-3: Code Generation Pipeline

**FR-3.1: Batch Code Generation**
- Generate 10 samples per problem for each model
- Total samples: 542 × 10 × 2 = 10,840 samples
- Store all generated samples with task_id and model_id
- Format: JSONL with {task_id, model, sample_idx, completion}
- Priority: P0 (Critical)

**FR-3.2: Code Execution Engine**
- Execute generated code using EvalPlus sandbox
- Capture full error traces from failed executions
- Store execution results: PASS or error_trace string
- Timeout: Standard EvalPlus timeout (3-5 seconds per test)
- Priority: P0 (Critical)

### FR-4: Error Taxonomy Classification

**FR-4.1: ICSE 2025 Taxonomy Implementation**
- **SYNTAX**: Parsing/compilation errors (SyntaxError, IndentationError)
- **RUNTIME**: Execution-time failures before assertion (TypeError, NameError, AttributeError, IndexError, KeyError, ValueError, ZeroDivisionError, RecursionError, Timeout)
- **ASSERTION**: Code runs but wrong output (AssertionError, "expected" in error)
- **PASS**: Code executed successfully and passed all tests
- Priority: P0 (Critical)

**FR-4.2: Error Classification Logic**
```python
def classify_error(error_trace: str) -> str:
    if error_trace is None:
        return "pass"
    error_lower = error_trace.lower()

    # Syntax errors
    if "syntaxerror" in error_lower or "indentationerror" in error_lower:
        return "syntax"

    # Runtime errors
    runtime_errors = ["typeerror", "nameerror", "attributeerror",
                      "indexerror", "keyerror", "valueerror",
                      "zerodivisionerror", "recursionerror", "timeout"]
    if any(err in error_lower for err in runtime_errors):
        return "runtime"

    # Assertion errors
    if "assertionerror" in error_lower or "expected" in error_lower:
        return "assertion"

    return "other"
```
- Priority: P0 (Critical)

### FR-5: Statistical Analysis

**FR-5.1: Contingency Table Construction**
- Rows: Alignment method (RL, DPO)
- Columns: Error categories (syntax, runtime, assertion)
- Cell values: Count of failures in each (method, category) pair
- Exclude PASS samples from contingency table
- Priority: P0 (Critical)

**FR-5.2: Chi-Square Test**
- Compute chi-square statistic using `scipy.stats.chi2_contingency`
- Report chi2, p-value, degrees of freedom, expected frequencies
- Success threshold: p < 0.05
- Priority: P0 (Critical)

**FR-5.3: Cramér's V Computation**
- Formula: V = sqrt(chi2 / (n * min(r-1, c-1)))
- n = total failures, r = 2 (methods), c = 3 (error types)
- Success threshold: V > 0.05
- Priority: P0 (Critical)

**FR-5.4: Effect Direction Verification**
- Compute P(syntax+runtime | failure) for each model
- Verify: RL_prop < DPO_prop (matches prediction)
- Report proportion difference and direction
- Priority: P0 (Critical)

### FR-6: Visualization

**FR-6.1: Gate Metrics Comparison (Required)**
- Bar chart showing target vs actual metrics
- Target: p-value = 0.05, Cramér's V = 0.05
- Actual: Computed values from experiment
- Save to figures/gate_metrics.png
- Priority: P0 (Critical)

**FR-6.2: Error Type Distribution Bar Chart**
- Stacked/grouped bar chart
- X-axis: Error types (syntax, runtime, assertion)
- Y-axis: Proportion P(type | failure)
- Grouped by: RL vs DPO
- Save to figures/error_distribution.png
- Priority: P1 (Important)

**FR-6.3: Contingency Table Heatmap**
- Heatmap of 2×3 error_type × alignment contingency table
- Cell values: Count
- Color scale: Low (light) to high (dark)
- Save to figures/contingency_heatmap.png
- Priority: P1 (Important)

**FR-6.4: Sample Size Sanity Check**
- Bar chart showing number of failures per model
- Confirms statistical power for chi-square test
- Expected: ~7,000 RL failures, ~6,000 DPO failures
- Save to figures/sample_sizes.png
- Priority: P2 (Nice to have)

---

## Non-Functional Requirements

### NFR-1: Performance
- Code generation should complete within 8 hours on single GPU
- All 10,840 samples processed (542 × 10 × 2)
- Memory usage within 24GB VRAM (CodeLlama-7B requirement)

### NFR-2: Reproducibility
- Fixed random seed: 42
- All hyperparameters documented
- Generated samples archived
- Contingency table saved as CSV

### NFR-3: Code Quality
- Type hints for all functions
- Docstrings for public APIs
- Error handling for execution failures
- Logging for progress tracking

---

## Success Criteria

### Primary Success Criteria (MUST_WORK Gate)

| Metric | Target | Interpretation |
|--------|--------|----------------|
| Chi-square p-value | < 0.05 | Statistically significant association |
| Cramér's V | > 0.05 | Small-medium effect size |
| Effect Direction | RL < DPO (syntax+runtime) | Matches prediction |

### Secondary Success Criteria
- All 542 problems successfully processed for both models
- Sufficient failure samples for statistical power (~13,000 total failures)
- Contingency table has non-zero cells in all categories

### Failure Criteria
- Chi-square p >= 0.05 → Not statistically significant → MUST_WORK gate FAIL
- Cramér's V <= 0.05 → Effect too small → MUST_WORK gate FAIL
- **If FAIL**: Dependent hypotheses (H-M1, H-M2, H-M3) BLOCKED

---

## Dependencies

### External Dependencies
- **transformers**: Model loading (pip install transformers)
- **torch**: PyTorch for inference
- **evalplus**: HumanEval+/MBPP+ benchmark (pip install evalplus)
- **scipy**: Chi-square test (pip install scipy)
- **numpy**: Array operations
- **matplotlib/seaborn**: Visualization

### Internal Dependencies
- Phase 2C experiment brief: h-e1/02c_experiment_brief.md
- verification_state.yaml for status tracking

### Reference Implementations
- salesforce/CodeRL (564 stars) - RL-aligned CodeT5 training
- evalplus/evalplus (1700+ stars) - HumanEval+/MBPP+ benchmark
- martin-wey/CodeUltraFeedback - DPO fine-tuning reference

---

## Data Specifications

### Input Data
| Data | Source | Format |
|------|--------|--------|
| HumanEval+ | evalplus library | Dict[task_id → {prompt, test, entry_point}] |
| MBPP+ | evalplus library | Dict[task_id → {prompt, test, entry_point}] |
| CodeRL-770M | Salesforce/codet5-large-ntp-py | HuggingFace checkpoint |
| CodeLlama-7B | codellama/CodeLlama-7b-Instruct-hf | HuggingFace checkpoint |

### Output Data
| Data | Location | Format |
|------|----------|--------|
| Generated Samples | outputs/samples.jsonl | JSONL |
| Execution Results | outputs/execution_results.json | JSON |
| Error Classifications | outputs/error_classifications.json | JSON |
| Contingency Table | outputs/contingency_table.csv | CSV |
| Metrics | outputs/metrics.json | JSON (p, V, direction) |
| Figures | figures/ | PNG images |

---

## Risk Assessment

### Technical Risks
- **R1**: CodeLlama-7B memory requirements (7B params)
  - Mitigation: Use 8-bit quantization if needed, or cloud GPU
- **R2**: EvalPlus execution sandbox stability
  - Mitigation: Test subset first, handle timeouts gracefully
- **R3**: Error classification ambiguity for edge cases
  - Mitigation: "other" category for unclassifiable errors, document edge cases

### Research Risks
- **R4**: Effect may exist but not reach significance threshold
  - Mitigation: Report actual values, interpret effect direction regardless
- **R5**: Unbalanced failure counts between models
  - Mitigation: Use conditional proportions P(type | failure), not raw counts

---

## Task Budget

### Tier: LIGHT (EXISTENCE Hypothesis)
- Maximum tasks: 15
- Epic range: 4-8
- Infrastructure: Minimal

### Expected Task Distribution
| Category | Count |
|----------|-------|
| Data Preparation | 2 |
| Environment Setup | 1 |
| Epic Tasks | 4-6 |
| Subtasks | 4-6 |
| Failsafe | 1 |
| **Total** | 12-15 |

---

## Phase Sequence

1. **Phase 3**: Implementation Planning (current) - PRD, Architecture, Logic, Config
2. **Phase 4**: Coding & PoC Validation - Code generation, execution, statistics
3. **Phase 4.5**: Synthesis - Evidence integration
4. **Phase 6**: Paper Writing - Academic publication

---

*Generated by Phase 3 PRD Workflow | Anonymous Research Pipeline*
*Input: h-e1/02c_experiment_brief.md*
*Gate: MUST_WORK | Type: EXISTENCE*
