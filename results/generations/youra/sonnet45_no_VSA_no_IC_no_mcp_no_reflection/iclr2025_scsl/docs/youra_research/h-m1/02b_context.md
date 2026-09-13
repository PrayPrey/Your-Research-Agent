# Phase 2B Context: h-m1

**Generated**: 2026-08-28T23:30:00Z  
**Hypothesis ID**: h-m1  
**Type**: MECHANISM  
**Gate**: MUST_WORK

---

## Hypothesis Statement

Temporal gap is driven by feature complexity difference (simpler spurious features converge faster) - validated via layer-neuron consistency test (Test 8)

---

## Rationale

This hypothesis provides the mechanistic explanation for the temporal ordering observed in h-e1. Understanding why spurious features converge faster is critical for designing interventions (h-c1) that can modulate learning rates based on feature complexity.

---

## Prerequisites

- **h-e1**: Temporal Ordering Foundation (MUST_WORK) - **STATUS: VALIDATED ✅**
  - Result: E_spurious=13, E_core=17, Δ=4 epochs (exceeds 2-epoch threshold)
  - PoC validated on CMNIST (seed 0)

---

## Experimental Approach

**Core Test**: Layer-neuron consistency test (Test 8)
- Compute neuron-spurious correlation ρ_j from ablation data
- Test layer-wise consistency: do early layers have higher ρ_j than late layers?
- Statistical validation: Early layers should show higher spurious feature alignment

**Key Insight**: If temporal ordering is driven by feature complexity, neurons in early layers (which extract simpler features) should correlate more strongly with spurious features than neurons in late layers (which extract complex semantic features).

---

## Dataset & Model (from Phase 2A)

**Dataset**: CMNIST (Colored MNIST)
- Type: Spurious correlation benchmark
- Spurious feature: Color (simpler, low-level)
- Core feature: Digit shape (complex, semantic)
- Standard splits available

**Model**: ResNet-18
- Convolutional architecture with clear layer hierarchy
- Suitable for layer-wise feature complexity analysis
- Compatible with h-e1 validation setup

---

## Success Criteria

**Mechanism Validation**:
1. Early layers (conv1, layer1) show higher ρ_j than late layers (layer3, layer4)
2. Gradient pattern aligns with feature complexity hypothesis
3. Cross-validation with R_temporal from h-e3 (if available)

**Gate Condition**: MUST_WORK
- Failure blocks h-c1 intervention design
- Requires solid mechanistic foundation

---

## Baseline & Comparison

**Baseline**: Random layer-neuron correlation (null hypothesis)
**Comparison**: 
- Alternative mechanism: Loss landscape sharpness (if layer-neuron test fails)
- Cross-method validation with GradCAM temporal ratio (h-e3)

---

## Dependencies

**Requires**:
- h-e1 ablation training data (spurious-only, core-only, baseline models)
- Layer-wise gradient access during training
- Neuron activation analysis capability

**Blocks**:
- h-c1: Gradient-aware intervention (SHOULD_WORK) - requires ρ_j values for learning rate modulation

---

## Continuation Context

This is the first MECHANISM hypothesis in the pipeline. Success establishes causal foundation for intervention design. Failure requires pivot to alternative mechanism explanation or redesign intervention without explicit feature complexity modeling.

---

**Next Phase**: Phase 2C - Experiment Design  
**Timeline**: 1 week (from Phase 2B plan)  
**Risk**: HIGH (MUST_WORK gate)
