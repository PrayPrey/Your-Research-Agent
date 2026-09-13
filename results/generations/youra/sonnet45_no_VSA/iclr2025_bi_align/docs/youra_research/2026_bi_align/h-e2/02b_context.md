# Hypothesis Context: H-E2

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-07-10
**Main Hypothesis:** Dual-Axis Dataset Accessibility Profiler
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
GPU-normalized SAT (P95/Median batch time × GPU utilization fraction) causally predicts ≥15% epoch-time degradation with ≥80% precision when GPU utilization <90%.

### Type
EXISTENCE

### Rationale
High batch time variance under high GPU utilization indicates data loading bottlenecks (GPU idle). Low utilization indicates non-accessibility system noise. GPU normalization isolates accessibility-related variance.

---

## Verification Protocol

### Conceptual Test
Measure batch time distribution (P95/Median) across training iterations, normalize by GPU utilization, and validate causal relationship by: (1) correlating SAT with epoch-time degradation in natural workloads, (2) synthetic jitter falsification—injecting dataloader sleep() should increase SAT only when GPU utilization drops.

### Success Criteria
- Precision ≥80% for predicting ≥15% epoch-time degradation
- Recall ≥70% (acceptable false negatives for conservative prediction)
- Synthetic jitter falsification: injecting dataloader sleep() increases SAT only when GPU utilization drops (validates causal link)

### Variables
- **Independent Variable:** GPU-normalized SAT (P95/Median batch time × GPU utilization fraction)
- **Dependent Variable:** Epoch-time degradation (≥15% threshold)
- **Controlled Variables:** Model architecture, dataset distribution, hardware configuration, batch size

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Natural workload suite (48 configs: 16 models × 5 optimizers × 3 datasets)
- **Type:** programmatic-api (diverse workloads with varying length distributions)
- **Source:** Standard datasets (CNNs: CIFAR-10, ImageNet; Transformers: WildChat, PersonaChat, mixed-length synthetic)
- **Path:** To be determined in Phase 2C (use standard splits)
- **Hypothesis Fit:** Natural workloads with varying batch time distributions required to validate causal prediction; synthetic jitter experiments validate causality

### Selected Model
- **Name:** 16 diverse architectures (8 CNNs + 8 Transformers)
- **Type:** Mixed (CNNs: ResNet-18/50, VGG-16, EfficientNet-B0; Transformers: GPT-2, BERT-base, T5-small, Llama-7B)
- **Source:** Standard model zoos (torchvision, HuggingFace transformers)
- **Hypothesis Fit:** Diversity across architectures validates SAT generalization; GPU utilization patterns vary by architecture

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
- Epoch-time extrapolation from 20-batch timing (current VeritasEst baseline for throughput risk)
- Assumes uniform batch time distribution (no variance modeling)

### Baseline Performance
Not specified in Phase 2B (H-E2 is EXISTENCE validation, not comparison)

### Gap Analysis
Current baseline does not model batch time variance or isolate data loading vs system noise. SAT aims to provide causal predictor for accessibility-specific throughput degradation.

---

## Dependencies and Gate Conditions

### Prerequisites
None (can run parallel with H-E1)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** If high SAT (>1.5) does not predict degradation with ≥80% precision, SAT is contaminated by non-accessibility variance → Multi-source decomposition needed. Workflow stops pending decomposition implementation.

**Phase Assignment:** Wave 1 (Week 1-2, parallel with H-E1)

**Estimated Duration:** 2 weeks (Tier 2 complexity)

---

## Dependency Context

### Relationship to Other Hypotheses
- **H-E1 (Parallel)**: Validates MSI (memory axis); H-E2 validates SAT (throughput axis). Both must succeed for H-M1 orthogonality test.
- **H-M1 (Dependent)**: Requires validated SAT from H-E2 to compute correlation with MSI
- **H-M2 (Transitive)**: Requires H-M1 (orthogonality) which depends on H-E2

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS (Phase 2C experiment design)
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation
3. Dependency information for controlled experiments
4. Success criteria for evaluation design
5. **Baseline comparison targets (CRITICAL for H-CP* hypotheses)**

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Use baseline metrics to set comparison targets
4. Design concrete experiment specification (Level 1.5)
5. Output: docs/youra_research/h-e2/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Optimized for single-hypothesis experiment design*
