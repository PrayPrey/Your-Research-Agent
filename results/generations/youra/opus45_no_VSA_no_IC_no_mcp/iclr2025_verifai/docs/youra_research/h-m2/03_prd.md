# Product Requirements Document: H-M2
## Representational Alignment Mechanism Validation

**Hypothesis ID:** H-M2
**Type:** MECHANISM
**Date:** 2026-08-28
**Author:** Anonymous
**Phase:** 3 - Implementation Planning

---

## Executive Summary

This PRD defines requirements for validating the representational alignment mechanism hypothesis: that structured error format organization (section ordering) causally improves LLM self-repair beyond information content alone. The experiment compares identical error information presented in structured vs scrambled section order, isolating the effect of representational alignment.

**Success Metric:** Structured format achieves significantly higher repair success rate than scrambled format (p < 0.05, McNemar's test).

---

## Problem Statement

### Background
H-M1 validated that information is preserved across format transformations. H-M2 tests whether the STRUCTURE of that information (how sections are ordered) causally affects repair performance.

### Research Question
Does representational alignment (consistent section ordering) improve self-repair success independent of information content?

### Hypothesis
Structured format outperforms scrambled format with p < 0.05, indicating representational alignment drives improvement.

---

## Functional Requirements

### FR-1: Dataset Preparation
- **FR-1.1:** Load EvalPlus (HumanEval+ and MBPP+) benchmarks via evalplus package
- **FR-1.2:** Generate initial code with CodeLlama-7B on full benchmark
- **FR-1.3:** Collect minimum 500 failed samples with static analysis errors
- **FR-1.4:** Apply H-M1 structured error formatting to all failed samples

### FR-2: Scrambling Implementation
- **FR-2.1:** Parse structured error format into sections (PROBLEM, LOCATION, CONTEXT, ROOT_CAUSE)
- **FR-2.2:** Implement reproducible scrambling with per-sample random seeds
- **FR-2.3:** Generate scrambled variants preserving identical content, only reordering sections
- **FR-2.4:** Validate information equivalence between structured and scrambled pairs

### FR-3: Self-Repair Execution
- **FR-3.1:** Implement repair prompt injection for both conditions
- **FR-3.2:** Execute CodeLlama-7B repair with temperature=0.8, top_p=0.95
- **FR-3.3:** Run paired evaluation: same sample, both format conditions
- **FR-3.4:** Collect binary pass/fail outcomes for each repair attempt

### FR-4: Statistical Analysis
- **FR-4.1:** Compute repair success rates for both conditions
- **FR-4.2:** Implement McNemar's test for paired binary outcomes
- **FR-4.3:** Calculate bootstrap confidence intervals (10,000 replicas)
- **FR-4.4:** Report discordant pair counts (structured wins vs scrambled wins)

### FR-5: Visualization
- **FR-5.1:** Generate bar chart comparing repair success rates with 95% CI error bars
- **FR-5.2:** Create discordant pair analysis visualization
- **FR-5.3:** Save all figures to {hypothesis_folder}/figures/

---

## Non-Functional Requirements

### NFR-1: Statistical Validity
- Minimum 500 paired samples for adequate statistical power
- Reproducible scrambling with documented random seeds
- BCa bootstrap for robust confidence intervals

### NFR-2: Computational Efficiency
- Batch inference for throughput optimization
- Single GPU (A100 40GB) sufficient
- Estimated runtime: 4-6 hours

### NFR-3: Reproducibility
- All random seeds documented
- Exact model versions specified (codellama/CodeLlama-7b-Instruct-hf)
- EvalPlus version pinned (v0.3.1)

---

## Data Requirements

### Input Data
| Data | Source | Format |
|------|--------|--------|
| HumanEval+ | evalplus package | 164 code problems |
| MBPP+ | evalplus package | 378 code problems |

### Generated Data
| Data | Description | Count |
|------|-------------|-------|
| Failed samples | Code with static errors | ≥500 |
| Structured errors | H-M1 format applied | ≥500 |
| Scrambled errors | Random section order | ≥500 |
| Repair results | Binary pass/fail pairs | ≥500 |

---

## Evaluation Metrics

### Primary Gate Metric
- **Repair Success Rate Delta:** structured_rate - scrambled_rate > 0
- **Statistical Significance:** p < 0.05 (McNemar's test)

### Secondary Metrics
- Cohen's d effect size (target: d > 0.2)
- 95% CI excludes zero
- Discordant pair ratio

---

## Dependencies

### Prerequisites
- H-M1: VALIDATED (information preservation confirmed)
- H-E1: VALIDATED (structured format improves repair)

### External Dependencies
- evalplus v0.3.1
- transformers (HuggingFace)
- CodeLlama-7B-Instruct model weights
- scipy, numpy for statistical analysis

### Infrastructure
- 1x A100 40GB GPU
- ~10GB storage for model weights + results

---

## Success Criteria

### Gate Pass Conditions
1. ✅ Structured success rate > Scrambled success rate
2. ✅ McNemar's test p < 0.05
3. ✅ 95% bootstrap CI excludes zero

### Gate Fail Implications
- **No difference:** Information content alone sufficient; revise theoretical model
- **Scrambled better:** Unexpected; investigate confounds

---

## Timeline & Phases

| Phase | Description | Deliverable |
|-------|-------------|-------------|
| Data Prep | Load EvalPlus, generate failures | 500+ error pairs |
| Scrambling | Implement section scrambling | Validated scrambled dataset |
| Evaluation | Run paired repair experiments | Binary outcome matrix |
| Analysis | Statistical tests + visualization | Gate determination |

---

## Appendix

### Related Documents
- 02c_experiment_brief.md: Detailed experiment specification
- H-M1 validation results: Information preservation baseline
- theoxo/self-repair: Reference implementation framework

### Reference Papers
- "Is Self-Repair a Silver Bullet?" (ICLR 2024)
- "RoToR: Order-Invariant Inputs" (arXiv:2502.08662)
