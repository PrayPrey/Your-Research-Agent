# Product Requirements Document: H-E1

**Hypothesis:** AS Components Are Measurable
**Date:** 2026-08-19
**Author:** Anonymous
**Phase:** 3 - Implementation Planning
**Type:** EXISTENCE (Proof of Concept)

---

## Executive Summary

This PRD specifies the implementation requirements for validating that Actionable Specificity (AS) components—AS_loc, AS_state, and AS_causal—can be independently computed from verification signals using deterministic extraction rules.

**Success Criteria:** AS components extractable from ≥95% of verification signals.

---

## Problem Statement

### Background
Current LLM-based code repair systems receive verification signals (error messages, tracebacks) without quantifying how much actionable information each signal provides. This makes it impossible to study the relationship between signal informativeness and repair success.

### Goal
Demonstrate that AS components can be reliably extracted from standard Python verification signals, enabling quantitative analysis of signal informativeness.

---

## Functional Requirements

### FR-1: Dataset Preparation
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | Load HumanEval dataset (164 problems) from openai/openai_humaneval | P0 |
| FR-1.2 | Load MBPP dataset (500 problems) from mbpp | P0 |
| FR-1.3 | Generate buggy code for each problem using LLM (temp=0.7) | P0 |
| FR-1.4 | Execute pytest to identify failing test cases | P0 |
| FR-1.5 | Sample 100+ failing cases stratified by error type | P0 |

### FR-2: Signal Generation (6 Conditions)
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | C1: Generate full trace output (highest AS) | P0 |
| FR-2.2 | C2: Generate truncated trace (max 3 frames) | P0 |
| FR-2.3 | C3: Generate value-masked trace | P0 |
| FR-2.4 | C4: Generate error message only | P0 |
| FR-2.5 | C5: Generate static analysis output (AS_loc=1 only) | P1 |
| FR-2.6 | C6: Generate syntax error output | P1 |

### FR-3: AS Component Extraction
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | Extract AS_loc (binary: file:line presence) via regex | P0 |
| FR-3.2 | Extract AS_state (count of variable=value pairs) via regex | P0 |
| FR-3.3 | Extract AS_causal (trace depth / frame count) via regex | P0 |
| FR-3.4 | Handle edge cases: multi-file traces, nested exceptions | P1 |
| FR-3.5 | Return ASComponents dataclass with validity check | P0 |

### FR-4: Evaluation Pipeline
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1 | Apply extractors to all signals (100 samples × 6 conditions = 600) | P0 |
| FR-4.2 | Calculate extraction rate per component | P0 |
| FR-4.3 | Verify AS ordering: mean(C1) > mean(C2) > mean(C3) > mean(C4) | P0 |
| FR-4.4 | Calculate component independence (correlation matrix) | P1 |

### FR-5: Visualization
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.1 | Generate extraction rate bar chart (mandatory gate metric) | P0 |
| FR-5.2 | Generate AS component distribution boxplots by condition | P1 |
| FR-5.3 | Generate extraction success heatmap | P1 |
| FR-5.4 | Generate component correlation matrix | P1 |

---

## Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1 | Execution time | < 30 minutes for full pipeline |
| NFR-2 | Memory usage | < 8GB RAM |
| NFR-3 | Python version | 3.10+ |
| NFR-4 | No external ML models | Rule-based extraction only |

---

## Data Specifications

### Input Data
- **HumanEval:** 164 Python programming problems with test cases
- **MBPP:** 500 Python programming problems with test cases
- **Format:** JSON/JSONL with problem description, solution template, test cases

### Output Data
- **ASComponents records:** JSON with AS_loc, AS_state, AS_causal per signal
- **Aggregated metrics:** CSV with extraction rates, means, correlations
- **Figures:** PNG files in `{hypothesis_folder}/figures/`

---

## Success Criteria

### Primary (Gate)
- **Extraction Rate ≥ 95%:** At least 570 of 600 signals successfully parsed

### Secondary
- **AS Ordering:** mean(AS_state[C1]) > mean(AS_state[C2]) > mean(AS_state[C3]) > mean(AS_state[C4])
- **Component Independence:** Pearson r < 0.5 between AS_loc, AS_state, AS_causal

---

## Dependencies

### External
- `datasets` (HuggingFace) for data loading
- `pytest` for test execution
- `matplotlib` for visualization
- `numpy` for statistics

### Internal
- None (FOUNDATION hypothesis)

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Regex fails on edge cases | Use stdlib traceback module as fallback |
| Extraction rate < 95% | Expand regex patterns, add error-type-specific handlers |
| AS components correlated | Report as limitation, proceed with caution |

---

## Out of Scope

- LLM repair experiments (future hypotheses)
- Multi-language support (Python only)
- Real-world bug datasets (synthetic bugs only)

---

## Appendix: Phase 2C Traceability

| Phase 2C Item | PRD Location |
|---------------|--------------|
| HumanEval + MBPP dataset | FR-1 |
| 6 signal conditions (C1-C6) | FR-2 |
| AS extraction rules | FR-3 |
| 95% extraction rate | Success Criteria |
| AS ordering validation | FR-4.3 |
| Required visualizations | FR-5 |
