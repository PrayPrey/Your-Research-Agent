# Product Requirements Document

**Hypothesis ID:** h-m1  
**Hypothesis Type:** MECHANISM  
**Date:** 2026-08-25  
**Author:** Anonymous

---

## Executive Summary

Implement a beam search instrumentation system to validate the hypothesis that beam search maintains k=5 candidate sequences throughout generation, enabling exploration of multiple syntax paths (vs greedy's single committed path).

**Key Components:**
- Beam count logging callback for HuggingFace Transformers
- Diversity measurement system
- Ablation study framework (k ∈ {3, 5, 10})

**Success Criteria:**
- Beam count = k at ALL generation steps (100% maintenance)
- Diversity ratio ≥ 60% (≥3 unique outputs for k=5)
- Computational feasibility (extrapolated <30min for 164 problems)

---

## Problem Statement

### Context

Building on h-e1's validated infrastructure (beam search + AST scoring works), this implementation tests whether beam search **actually maintains** k=5 parallel sequences vs collapsing to greedy-like behavior. The mechanism hypothesis depends on beam diversity — if beams prune early or duplicate, the exploration advantage disappears.

### Objectives

1. **Beam Maintenance Validation:** Verify beam count = k at every generation step
2. **Diversity Measurement:** Quantify unique sequences in final k beams
3. **Ablation Analysis:** Compare k={3,5,10} for trade-off assessment

### Prerequisites

- h-e1 VALIDATED (infrastructure: beam search + AST parsing works)
- CodeLlama-7B cached locally
- HumanEval-164 dataset accessible

---

## Functional Requirements

### FR-1: Beam Count Logging System

**Priority:** P0 (MUST_WORK gate)  
**Description:** Instrument HuggingFace beam search to log active beam count at each generation step.

**Acceptance Criteria:**
- `BeamCountLogger` callback captures beam count per step
- Logs stored as list `[count_step_1, count_step_2, ...]`
- Returns boolean `beam_maintained` (all counts == k)

**Input:** `GenerationConfig(num_beams=k)`, tokenized prompt  
**Output:** `beam_counts: List[int]`, `beam_maintained: bool`

### FR-2: Diversity Measurement

**Priority:** P0 (SHOULD_WORK gate)  
**Description:** Measure uniqueness of final k beams to detect premature convergence.

**Acceptance Criteria:**
- Decode all k beam outputs
- Count unique sequences (set-based deduplication)
- Calculate diversity ratio = unique_count / k

**Input:** `outputs.sequences` (k beams)  
**Output:** `unique_count: int`, `diversity_ratio: float`

### FR-3: Greedy Baseline

**Priority:** P1  
**Description:** Run greedy sampling (k=1) for comparison baseline.

**Acceptance Criteria:**
- CodeLlama-7B with `do_sample=False`, `num_beams=1`
- Beam count logged (expected: constant 1)
- Same 3 HumanEval problems as beam search

**Input:** Same prompts as beam search  
**Output:** Greedy outputs, beam count = [1, 1, 1, ...]

### FR-4: Ablation Study (k Selection)

**Priority:** P1  
**Description:** Test k ∈ {3, 5, 10} to validate k=5 as optimal trade-off.

**Acceptance Criteria:**
- Run same 3 problems with k=3, 5, 10
- Measure (beam maintenance, diversity, compute time) for each k
- Generate comparison bar charts

**Input:** HumanEval problems 0-2  
**Output:** Metrics table per k, 3 comparison figures

### FR-5: Dataset Preparation

**Priority:** P0  
**Description:** Load HumanEval-164 and extract first 3 problems for PoC.

**Acceptance Criteria:**
- Use `datasets` library: `load_dataset("openai_humaneval")`
- Extract `dataset['test'].select(range(3))`
- Format prompts with function signature + docstring

**Input:** HumanEval identifier  
**Output:** 3 problem dicts with `{prompt, test, entry_point}`

### FR-6: Model Loading

**Priority:** P0  
**Description:** Load CodeLlama-7B with local caching.

**Acceptance Criteria:**
- `AutoModelForCausalLM.from_pretrained("meta-llama/CodeLlama-7b-hf")`
- Cache to avoid re-download
- Move to GPU if available (CUDA check)

**Input:** Model identifier  
**Output:** Model, tokenizer ready for generation

### FR-7: Visualization

**Priority:** P1  
**Description:** Generate 3 required figures for hypothesis validation.

**Acceptance Criteria:**
- **Figure 1 (Mandatory):** Beam count over steps (line plot, expected flat at k=5)
- **Figure 2:** Diversity by k (bar chart, k ∈ {3,5,10})
- **Figure 3:** Compute time vs k (bar chart)

**Input:** Logged metrics  
**Output:** 3 PNG files saved to `h-m1/figures/`

---

## Non-Functional Requirements

### NFR-1: Computational Efficiency

- **Target:** Extrapolated runtime <30 min for full 164 problems
- **Measured:** h-e1 achieved 16.1s for 3 problems → 14.7min for 164 (OK)
- **Constraint:** k=10 ablation may exceed budget (acceptable for ablation study)

### NFR-2: Code Quality

- **Modularity:** Separate functions for (logging, diversity, visualization)
- **Reusability:** Beam logger reusable for h-m2 (combined scoring)
- **Documentation:** Docstrings for all public functions

### NFR-3: Reproducibility

- **Determinism:** Beam search is deterministic (no temperature)
- **Seed:** Set random seed for any stochastic operations
- **Logging:** Save all metrics to JSON for Phase 4.5 synthesis

---

## Data Specifications

### Input Data

| Dataset | Type | Size | Source |
|---------|------|------|--------|
| HumanEval-164 | Standard test set | 3 problems (PoC) | `datasets` library |

**Processing:**
- No preprocessing required
- Prompts = function signature + docstring (from HumanEval format)

### Output Data

| Artifact | Format | Content |
|----------|--------|---------|
| Beam counts | JSON | `{problem_id: [counts_per_step]}` |
| Diversity metrics | JSON | `{problem_id: {unique, ratio}}` |
| Figures | PNG | 3 visualization plots |

---

## Dependencies

### External Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| `transformers` | >=4.30.0 | HuggingFace beam search |
| `datasets` | Latest | HumanEval loading |
| `torch` | >=2.0.0 | Model inference |
| `matplotlib` | Latest | Visualization |

### Hardware

- **GPU:** CUDA-capable GPU (optional, CPU fallback OK for 3 problems)
- **RAM:** 16GB+ (7B model loaded)
- **Disk:** 15GB (CodeLlama-7B cache)

### Prerequisite Outputs

From h-e1:
- Validated infrastructure (beam search works)
- CodeLlama-7B cached locally

---

## Success Criteria

### Gate: SHOULD_WORK

**Pass Condition:**
1. Beam count = k at ALL steps for k=5 (100% maintenance)
2. Diversity ratio ≥ 60% for k=5 (≥3 unique outputs)

**Pivot Condition:**
- If beam count drops below k → Adjust beam pruning threshold
- If diversity <60% → Increase k or modify scoring

**Metrics:**
- `beam_maintained: bool` (primary gate)
- `diversity_ratio: float` (secondary gate)
- `compute_time: float` (informational)

---

## Validation Plan

### Unit Tests

- `test_beam_count_logger()`: Verify callback captures counts correctly
- `test_diversity_calculation()`: Check deduplication logic

### Integration Tests

- Run 1 HumanEval problem end-to-end
- Verify all 3 figures generated

### PoC Validation

- Run 3 problems with k=5
- Check gate conditions met
- Visual inspection of beam count plot (should be flat line)

---

## Timeline Constraints

**Phase 4 Validation Deadline:** Within 30min computational budget (already validated in h-e1)

---

## Appendix: Phase 2C Traceability

| Phase 2C Item | PRD Section |
|---------------|-------------|
| Dataset: HumanEval-164 (first 3) | FR-5, Data Specifications |
| Baseline: CodeLlama-7B greedy | FR-3 |
| Proposed: CodeLlama-7B beam k=5 | FR-1, FR-2 |
| Ablation: k ∈ {3,5,10} | FR-4 |
| Metric: Beam count maintenance | FR-1, Success Criteria |
| Metric: Diversity ratio | FR-2, Success Criteria |
| Metric: Compute time | NFR-1 |
| Viz: Beam count over steps | FR-7 (Figure 1) |
| Viz: Diversity by k | FR-7 (Figure 2) |
| Viz: Compute time vs k | FR-7 (Figure 3) |

---

**Document Status:** READY FOR PHASE 3 ARCHITECTURE
