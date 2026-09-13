# Phase 2B Context: H-E1 (Proxy Measurement Reliability)

**Generated**: 2026-07-09  
**Hypothesis ID**: h-e1  
**Type**: EXISTENCE  
**Gate**: MUST_WORK

---

## Hypothesis Information

### Statement
Proxy metrics (CodeBLEU, normalized runtime ratio, learned PR-style score) demonstrate measurement reliability sufficient for optimization.

### Success Criteria
- Intra-implementation coefficient of variation (CV) ≤ 5%
- Inter-complexity-class separability: Cohen's d ≥ 0.8 (e.g., O(n) vs O(n²))
- Cross-hardware rank correlation: Spearman ρ ≥ 0.8

### Rationale
This hypothesis establishes the foundational measurement quality required for all subsequent stages. Without reliable proxies, optimization would chase noise rather than signal. The three criteria (precision, discriminative power, robustness) form the minimum bar for using metrics in RL reward functions.

---

## Experimental Setup (from Phase 2B Section 1.3)

### Dataset
**Benchmark**: HumanEval  
**Calibration Study**: 50 HumanEval problems, 10 solutions × 5 runs each  
**Controlled Asymptotic Tasks**: 50 synthetic problems with known optimal complexity classes  
**Cross-hardware Validation**: AWS g4dn.xlarge vs local GPU

### Model
**Base Model**: CodeLlama-7B-Instruct (meta-llama/CodeLlama-7b-Instruct-hf)  
**Purpose**: Generate diverse solutions for measurement calibration

### Experimental Method
1. **CV Study**: Measure each metric 5 times per solution (500 total solutions) to quantify noise
2. **Complexity Separation**: Controlled tasks with labeled O(n) vs O(n²) solutions to test discriminative power
3. **Hardware Comparison**: Same solutions evaluated on two platforms to test robustness

---

## Baseline & Comparison Targets

**Baseline**: No direct baseline (measurement validation study)  
**Success Threshold**: Each proxy must independently pass all three criteria OR be dropped

**Falsification Trigger**: If efficiency metric fails CV ≤5% threshold OR complexity class separation fails Cohen's d ≥0.8, drop efficiency from optimization and continue with remaining proxies (CodeBLEU + PR-style score).

---

## Dependencies and Gate Conditions

### Prerequisites
None (READY to start)

### Gate Logic
**MUST_WORK**: This is a foundational hypothesis. Failure does NOT block the pipeline — instead, it scopes which proxies proceed to H-E2.

**Outcomes**:
- **Pass**: All three proxies validated → Proceed to H-E2 with full proxy set
- **Partial Pass**: 1-2 proxies validated → Proceed to H-E2 with reduced proxy set
- **Fail**: Zero proxies validated → Route to Phase 0 (fundamental measurement failure)

---

## Controlled Variables (Experimental Hygiene)

- **Hardware**: Containerized execution with deterministic seeds, fixed GPU/CPU allocation
- **Benchmark Splits**: Fixed HumanEval test splits
- **Measurement Protocol**: Standardized timing procedures (5 warmup runs, median of 5 measured runs)
- **Baseline Model**: Same CodeLlama-7B-Instruct checkpoint across all measurements

---

## Continuation Context

**Position in DAG**: Root node (no prerequisites)  
**Dependent Hypotheses**: H-E2 (awaits proxy selection from this stage)  
**Critical Path**: H-E1 → H-E2 → H-M1 → H-M2 → H-C2

**Timeline**: 2 weeks  
**Compute**: ~100 GPU hours (calibration + controlled tasks)

---

**Context Status**: Generated from Phase 2B Verification Plan  
**Next Step**: Phase 2C Experiment Design
